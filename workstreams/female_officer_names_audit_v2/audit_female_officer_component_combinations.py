#!/usr/bin/env python3
"""Read-only static audit of female-officer name component combinations.

The audit never writes below ``--game-root``.  It compares each direct Korean
``msgev`` name with every exact two-component decomposition of its SC source
name in the active ``msgdata`` component range, after applying the approved
component overlay *in memory*.  A source-name decomposition is evidence of a
possible record pairing, not proof that a specific runtime record uses it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


SCHEMA = "nobu16.kr.female-officer-component-combination-audit.v1"
MSGEV_RELATIVE = Path("MSG_PK") / "{language}" / "msgev.bin"
MSGDATA_RELATIVE = Path("MSG_PK") / "{language}" / "msgdata.bin"
OVERLAY_PATH = HERE / "public" / "msgdata_female_officer_component_fix.v1.json"
COMPONENT_MAX_ID = 0x22DB
HISTORICAL_OFFICER_MAX_ID = 2206
EXPECTED_MSGEV_COUNT = 17_916
EXPECTED_MSGDATA_COUNT = 29_218
APPROVED_COMPONENT_IDS: tuple[int, ...] = (287, 376, 386, 434, 773, 791, 2081, 2082, 2083, 2087, 6708)

# The project-defined hime-officer roster plus the four additional historical
# officers proven to consume the common 姫 component in an exact SC pair.
OFFICIAL_ROSTER_IDS: tuple[int, ...] = (
    404, 406, 410, 692, 715, 719, 1016, 1094, 1157, 1170, 1176,
    1179, 1310, 1390, 1391, 1582, 1583, 1827, 1969, 2147, 2177,
)
HIME_COMPONENT_EXTENSION_IDS: tuple[int, ...] = (1171, 1724, 1861, 2007)

# These are not automatic patch instructions.  They state which component
# produces the observed static difference for a row, allowing the audit to
# calculate the historical-name sharing scope before any later edit.
# These are the remaining component concerns after the approved overlay has
# been applied in memory.  They are not automatic patch instructions.
PENDING_COMPONENT_HINTS: dict[int, int] = {
    1157: 204,
    1170: 674,
    1171: 206,
}

# Oichi's SC text is one character, so it has no non-empty two-part source
# decomposition.  The game-side observed defect and the confirmed 62+2083
# reconstruction are retained as a separately labelled, non-decomposition
# validation anchor.
KNOWN_NONDECOMPOSITION_LINKS: dict[int, tuple[int, int]] = {404: (62, 2083)}


class AuditError(RuntimeError):
    """Raised when an input does not satisfy the pinned audit contract."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def read_table(path: Path) -> tuple[tuple[str, ...], dict[str, Any]]:
    packed = path.read_bytes()
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    return table.texts, {
        "relative_path": "/".join(path.parts[-3:]),
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "string_count": table.string_count,
        "wrapper_uncompressed_size": header.uncompressed_size,
    }


def load_overlay() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"cannot read approved component overlay: {exc}") from exc
    if overlay.get("schema") != "nobu16.kr.female-officer-component-fix.v1":
        raise AuditError("component overlay schema differs")
    if overlay.get("resource") != "MSG_PK/JP/msgdata.bin":
        raise AuditError("component overlay targets an unexpected resource")
    entries = overlay.get("entries")
    if not isinstance(entries, list) or tuple(item.get("id") for item in entries) != APPROVED_COMPONENT_IDS:
        raise AuditError("component overlay is not the approved component set")
    for entry in entries:
        if set(entry) != {
            "id", "baseline_ko_utf16le_sha256", "ko", "ko_utf16le_sha256", "affected_msgev_ids",
        }:
            raise AuditError("component overlay entry schema differs")
        if not isinstance(entry["ko"], str) or not entry["ko"]:
            raise AuditError("component overlay contains an invalid replacement")
        if text_hash(entry["ko"]) != entry["ko_utf16le_sha256"]:
            raise AuditError("component overlay replacement hash differs")
    return entries, overlay


def apply_overlay_in_memory(texts: tuple[str, ...], entries: Iterable[dict[str, Any]]) -> list[str]:
    updated = list(texts)
    for entry in entries:
        entry_id = entry["id"]
        if not isinstance(entry_id, int) or not 0 <= entry_id < len(updated):
            raise AuditError("component overlay id is outside msgdata")
        if text_hash(updated[entry_id]) != entry["baseline_ko_utf16le_sha256"]:
            raise AuditError(f"active JP msgdata differs at component id {entry_id}")
        updated[entry_id] = entry["ko"]
    return updated


def component_index(texts: tuple[str, ...]) -> dict[str, tuple[int, ...]]:
    index: dict[str, list[int]] = {}
    for component_id, value in enumerate(texts[: COMPONENT_MAX_ID + 1]):
        if value:
            index.setdefault(value, []).append(component_id)
    return {value: tuple(ids) for value, ids in index.items()}


def exact_pairs(source: str, index: dict[str, tuple[int, ...]]) -> tuple[tuple[int, int], ...]:
    matches: list[tuple[int, int]] = []
    for split_at in range(1, len(source)):
        for left in index.get(source[:split_at], ()):
            for right in index.get(source[split_at:], ()):
                matches.append((left, right))
    return tuple(matches)


def compare(candidate: str, direct: str) -> str:
    if candidate == direct:
        return "EXACT"
    if candidate.replace(" ", "") == direct.replace(" ", ""):
        return "SPACE_ONLY"
    return "MISMATCH"


def classify_pair_results(results: list[dict[str, Any]]) -> str:
    if not results:
        return "UNRESOLVED_NO_EXACT_SC_PAIR"
    outcomes = {str(item["comparison"]) for item in results}
    rendered = {str(item["candidate_ko"]) for item in results}
    if outcomes == {"EXACT"}:
        return "STATIC_ALL_CANDIDATES_EXACT"
    if outcomes == {"SPACE_ONLY"}:
        return "STATIC_ALL_CANDIDATES_SPACE_ONLY"
    if outcomes == {"MISMATCH"}:
        return "STATIC_ALL_CANDIDATES_MISMATCH"
    if len(rendered) == 1:
        return "STATIC_EQUIVALENT_CANDIDATES_MIXED"
    return "STATIC_AMBIGUOUS_CANDIDATES"


def collect_component_scopes(
    source_msgev: tuple[str, ...],
    source_index: dict[str, tuple[int, ...]],
    component_ids: set[int],
) -> list[dict[str, Any]]:
    links: dict[int, set[int]] = {component_id: set() for component_id in component_ids}
    pair_counts: dict[int, int] = {component_id: 0 for component_id in component_ids}
    for officer_id in range(HISTORICAL_OFFICER_MAX_ID + 1):
        for left, right in exact_pairs(source_msgev[officer_id], source_index):
            for component_id in {left, right} & component_ids:
                links[component_id].add(officer_id)
                pair_counts[component_id] += 1
    return [
        {
            "component_id": component_id,
            "historical_msgev_ids": sorted(links[component_id]),
            "historical_officer_count": len(links[component_id]),
            "exact_pair_occurrence_count": pair_counts[component_id],
        }
        for component_id in sorted(component_ids)
    ]


def audit(game_root: Path) -> dict[str, Any]:
    entries, overlay = load_overlay()
    tables: dict[str, tuple[str, ...]] = {}
    input_tables: dict[str, dict[str, Any]] = {}
    for resource_name, relative in (
        ("SC_msgev", MSGEV_RELATIVE),
        ("JP_msgev", MSGEV_RELATIVE),
        ("SC_msgdata", MSGDATA_RELATIVE),
        ("JP_msgdata", MSGDATA_RELATIVE),
    ):
        language = resource_name[:2]
        path = game_root / Path(str(relative).format(language=language))
        texts, info = read_table(path)
        expected_count = EXPECTED_MSGEV_COUNT if resource_name.endswith("msgev") else EXPECTED_MSGDATA_COUNT
        if len(texts) != expected_count:
            raise AuditError(f"{resource_name} string count differs")
        tables[resource_name] = texts
        input_tables[resource_name] = info

    candidate_components = apply_overlay_in_memory(tables["JP_msgdata"], entries)
    source_index = component_index(tables["SC_msgdata"])
    target_ids = tuple(sorted(set(OFFICIAL_ROSTER_IDS + HIME_COMPONENT_EXTENSION_IDS)))
    if any(not 0 <= officer_id <= HISTORICAL_OFFICER_MAX_ID for officer_id in target_ids):
        raise AuditError("target id is outside the historical-officer range")

    rows: list[dict[str, Any]] = []
    for officer_id in target_ids:
        source = tables["SC_msgev"][officer_id]
        direct = tables["JP_msgev"][officer_id]
        pairs = exact_pairs(source, source_index)
        results = [
            {
                "component_ids": [left, right],
                "candidate_ko": candidate_components[left] + candidate_components[right],
                "comparison": compare(candidate_components[left] + candidate_components[right], direct),
            }
            for left, right in pairs
        ]
        classification = classify_pair_results(results)
        row: dict[str, Any] = {
            "msgev_id": officer_id,
            "scope": "official_hime_roster" if officer_id in OFFICIAL_ROSTER_IDS else "hime_component_extension",
            "direct_msgev_ko": direct,
            "source_sc_utf16le_sha256": text_hash(source),
            "exact_sc_pair_count": len(pairs),
            "pair_results": results,
            "classification": classification,
        }
        if officer_id in KNOWN_NONDECOMPOSITION_LINKS:
            left, right = KNOWN_NONDECOMPOSITION_LINKS[officer_id]
            rendered = candidate_components[left] + candidate_components[right]
            row["known_non_decomposition_link"] = {
                "component_ids": [left, right],
                "candidate_ko": rendered,
                "comparison": compare(rendered, direct),
                "evidence": "observed-defect reconstruction; not an exact SC two-part proof",
            }
            if row["known_non_decomposition_link"]["comparison"] == "EXACT":
                row["classification"] = "KNOWN_NONDECOMPOSITION_LINK_FIXED"
        hinted_component = PENDING_COMPONENT_HINTS.get(officer_id)
        if hinted_component is not None:
            row["anomaly_component_hint"] = hinted_component
        rows.append(row)

    classification_counts: dict[str, int] = {}
    for row in rows:
        key = str(row["classification"])
        classification_counts[key] = classification_counts.get(key, 0) + 1
    anomaly_components = set(PENDING_COMPONENT_HINTS.values())
    return {
        "schema": SCHEMA,
        "scope": {
            "official_hime_roster_count": len(OFFICIAL_ROSTER_IDS),
            "hime_component_extension_count": len(HIME_COMPONENT_EXTENSION_IDS),
            "total_unique_officers": len(target_ids),
            "historical_officer_id_range": [0, HISTORICAL_OFFICER_MAX_ID],
            "component_id_range": [0, COMPONENT_MAX_ID],
            "analysis_is_static_only": True,
        },
        "source_text_policy": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "source_text_is_stored_as_hash_only": True,
        },
        "approved_in_memory_overlay": {
            "overlay_id": overlay["overlay_id"],
            "entry_ids": [entry["id"] for entry in entries],
            "installed_game_files_modified": False,
        },
        "input_tables": input_tables,
        "static_method": {
            "name_combiner": "FUN_1405F40D0",
            "text_resolver": "FUN_1409F9BE0",
            "pair_rule": "all exact non-empty SC two-component decompositions in msgdata ID range",
            "runtime_record_mapping_proven": False,
        },
        "rows": rows,
        "anomaly_component_static_sharing": collect_component_scopes(
            tables["SC_msgev"], source_index, anomaly_components
        ),
        "summary": {
            "classification_counts": classification_counts,
            "static_anomaly_hints": len(PENDING_COMPONENT_HINTS),
        },
    }


def ensure_report_is_safe(report: Path, game_root: Path) -> None:
    try:
        report.resolve().relative_to(game_root.resolve())
    except ValueError:
        return
    raise AuditError("report path must be outside the supplied game root")


def atomic_json_write(path: Path, document: dict[str, Any]) -> None:
    payload = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_bytes(payload)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, help="optional source-free JSON report outside the game root")
    args = parser.parse_args(argv)
    try:
        game_root = args.game_root.resolve()
        document = audit(game_root)
        if args.report is not None:
            report = args.report.resolve()
            ensure_report_is_safe(report, game_root)
            atomic_json_write(report, document)
            print(f"report={report}")
        print("audited=" + str(document["scope"]["total_unique_officers"]))
        print("classification_counts=" + json.dumps(document["summary"]["classification_counts"], sort_keys=True))
        print("installed_game_files_modified=False")
        return 0
    except (OSError, ValueError, AuditError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
