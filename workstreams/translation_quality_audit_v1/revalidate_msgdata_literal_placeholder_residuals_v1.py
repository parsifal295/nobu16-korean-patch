#!/usr/bin/env python3
"""Classify every remaining PC ``msgdata`` literal-placeholder coordinate.

The prior literal-placeholder review partitioned 377 nonempty Japanese
``msgdata`` coordinates whose live Korean value is either ``dummy`` or an
all-caps localization identifier.  Some of those coordinates are already
covered by the active translation-quality builder.  This audit deliberately
does not create a second proposal for them.

For each of the remaining coordinates, this script rechecks the pristine PC
Japanese source, current PC Korean target, and PC EN/SC/TC tables.  It writes
only an evidence-backed hold record when visibility or a safe display route is
not established.  In particular, it does not treat an EN-only stale string as
proof that a Korean placeholder is rendered in game.

Only PC resources are read.  Switch Korean, historic Korean backups, and game
resource writes are intentionally out of scope.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_ROOT = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
QUEUE = AUDIT_ROOT / "semantic_inventory_v6" / "private_review_queue.jsonl"
PRIOR_HOLDS = AUDIT_ROOT / "semantic" / "msgdata_placeholder_holds.v1.jsonl"
BUILDER = REPO / "workstreams" / "translation_quality_corrections_v1" / "build_translation_quality_corrections_v1.py"
DEFAULT_OUTPUT = AUDIT_ROOT / "semantic" / "msgdata_literal_placeholder_residual_holds_pc_only.v1.jsonl"

PATHS = {
    "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
    "ko": STEAM / "MSG_PK" / "JP" / "msgdata.bin",
    "en": STEAM / "MSG_PK" / "EN" / "msgdata.bin",
    "sc": STEAM / "MSG_PK" / "SC" / "msgdata.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msgdata.bin",
}

# These bind the result to the installed PC text baseline.  If any of them
# changes, the review must be rebased instead of silently being reused.
EXPECTED_FILE_SHA256 = {
    "jp": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
    "ko": "7EAA33BC80C021A028660DF1A7934886591A1DA36DB7BC53146749C3A4AEF040",
    "en": "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033",
    "sc": "A3A0260B74191D4676C43403B587BB4EC676A7D96E56725844F24C8107B1604E",
    "tc": "E266A9C43AAE09BEEA739812AD8E3E8DDDBC4710EF5A81E174A9D215D6B03676",
}
EXPECTED_QUEUE_SHA256 = "1F0A0417ADE90DAD42964BC09BCBFC622CA7FD6DF32D9A8A0DB06E066B533E80"
EXPECTED_PRIOR_HOLDS_SHA256 = "B2E6173A723D103ABC858652FE5CB035598111B9101BCD8D020EE2D2DE355E86"

EXPECTED_REVIEW_COORDINATE_COUNT = 377
EXPECTED_ACTIVE_COORDINATES = {
    21640, 21641, 21642, 21643, 21644, 21645, 21646, 21647, 21648, 21649,
    21650, 21651, 21652, 21653, 21654, 21655, 21656, 21657, 21658, 21659,
    21660, 21661, 21662, 21663, 21664, 21665, 21666, 21667, 21668, 21669,
    21670, 21671, 21672, 21673, 21674, 21675, 23030, 23059, 23079, 23085,
    23088, 23089, 23101, 23106, 26383, 26483, 26533,
}
EXPECTED_RESIDUAL_GROUP_COUNTS = {
    "dummy_source_marker": 95,
    "dummy_ruby_or_reading": 15,
    "dummy_exact_source_alias": 8,
    "dummy_reference_language_but_unproven": 6,
    "dummy_unconfirmed_visible_route": 120,
    "identifier_all_locales_placeholder": 85,
    "identifier_ruby": 1,
}
EXPECTED_RESIDUAL_COUNT = sum(EXPECTED_RESIDUAL_GROUP_COUNTS.values())
PRIOR_VISIBLE_LANDMARK_CANDIDATE = 26383
PARTIAL_REFERENCE_TRAIT_IDS = {15363, 15364, 15367, 15369, 15380, 15394}

DUMMY_RE = re.compile(r"dummy\d*\Z", re.IGNORECASE)
IDENTIFIER_RE = re.compile(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\Z")
KANA_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f]")

sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def load_table(path: Path) -> tuple[str, ...]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def safe_under(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=False)
    allowed = root.resolve(strict=False)
    if resolved != allowed and allowed not in resolved.parents:
        raise ValueError(f"output must remain below {allowed}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"required artifact is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row is not an object: {path}:{line_number}")
        rows.append(value)
    return rows


def parse_id_runs(value: Any) -> set[int]:
    if not isinstance(value, str) or not value:
        raise ValueError("hold group lacks id_runs")
    result: set[int] = set()
    for part in value.split(","):
        if not re.fullmatch(r"\d+(?:-\d+)?", part):
            raise ValueError(f"invalid id run: {part!r}")
        start_text, separator, end_text = part.partition("-")
        start = int(start_text)
        end = int(end_text) if separator else start
        if end < start:
            raise ValueError(f"descending id run: {part!r}")
        result.update(range(start, end + 1))
    return result


def is_identifier(value: str) -> bool:
    return bool(IDENTIFIER_RE.fullmatch(value))


def is_placeholder(value: str) -> bool:
    return not value or bool(DUMMY_RE.fullmatch(value)) or is_identifier(value)


def queue_rows() -> dict[int, dict[str, Any]]:
    if file_hash(QUEUE) != EXPECTED_QUEUE_SHA256:
        raise ValueError("private review queue changed; rebase literal-placeholder review before reuse")
    result: dict[int, dict[str, Any]] = {}
    required_flags = {
        "target_dummy_placeholder_for_nonempty_jp",
        "target_localization_identifier_for_nonempty_jp",
    }
    for line_number, row in enumerate(jsonl_rows(QUEUE), start=1):
        if row.get("resource") != "msgdata":
            continue
        flags = row.get("flags")
        if not isinstance(flags, list) or not required_flags.intersection(flags):
            continue
        try:
            coordinate = int(row.get("coordinate"))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid msgdata queue coordinate: {QUEUE}:{line_number}") from exc
        if coordinate in result:
            raise ValueError(f"duplicate msgdata queue coordinate: {coordinate}")
        result[coordinate] = row
    if len(result) != EXPECTED_REVIEW_COORDINATE_COUNT:
        raise ValueError("msgdata literal-placeholder queue count differs from reviewed 377 coordinates")
    return result


def prior_hold_groups(review_coordinates: set[int]) -> dict[int, dict[str, Any]]:
    if file_hash(PRIOR_HOLDS) != EXPECTED_PRIOR_HOLDS_SHA256:
        raise ValueError("prior msgdata placeholder holds changed; rebase residual classification before reuse")
    rows = jsonl_rows(PRIOR_HOLDS)
    coverage = [row for row in rows if row.get("type") == "coverage"]
    if len(coverage) != 1:
        raise ValueError("prior msgdata placeholder hold artifact lacks one coverage row")
    cover = coverage[0]
    if (
        cover.get("candidate_id") != PRIOR_VISIBLE_LANDMARK_CANDIDATE
        or cover.get("total_partition_count") != EXPECTED_REVIEW_COORDINATE_COUNT
        or cover.get("dummy_candidate_count") != 244
        or cover.get("identifier_candidate_count") != 133
    ):
        raise ValueError("prior msgdata placeholder coverage differs from reviewed partition")

    group_rows = [row for row in rows if row.get("type") != "coverage"]
    mapping: dict[int, dict[str, Any]] = {}
    for row in group_rows:
        group_id = row.get("group_id")
        status = row.get("status")
        rationale = row.get("rationale")
        selection_rule = row.get("selection_rule")
        if not all(isinstance(value, str) and value for value in (group_id, status, rationale, selection_rule)):
            raise ValueError("prior msgdata hold group is malformed")
        coordinates = parse_id_runs(row.get("id_runs"))
        if row.get("count") != len(coordinates):
            raise ValueError(f"prior hold group count mismatch: {group_id}")
        for coordinate in coordinates:
            if coordinate in mapping:
                raise ValueError(f"coordinate in multiple prior hold groups: {coordinate}")
            mapping[coordinate] = row
    if set(mapping).union({PRIOR_VISIBLE_LANDMARK_CANDIDATE}) != review_coordinates:
        raise ValueError("prior msgdata hold groups no longer partition the queue")
    return mapping


def active_builder_coordinates() -> set[int]:
    if not BUILDER.is_file():
        raise ValueError(f"translation-quality builder is absent: {BUILDER}")
    for dependency in (REPO / "tools", REPO / "workstreams" / "strdata", REPO / "workstreams" / "msggame"):
        dependency_text = str(dependency)
        if dependency_text not in sys.path:
            sys.path.insert(0, dependency_text)
    module_name = "_msgdata_placeholder_residual_builder"
    module_spec = importlib.util.spec_from_file_location(module_name, BUILDER)
    if module_spec is None or module_spec.loader is None:
        raise ValueError(f"unable to load translation-quality builder: {BUILDER}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    try:
        spec = next(resource for resource in module.SPECS if resource.name == "msgdata")
        proposals = module.read_proposals(spec)
    finally:
        sys.modules.pop(module_name, None)
    coordinates: set[int] = set()
    for proposal in proposals:
        try:
            coordinate = int(proposal["coordinate"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("builder returned a nonnumeric msgdata coordinate") from exc
        coordinates.add(coordinate)
    return coordinates


def row_route_checks(
    coordinate: int,
    group_id: str,
    source: str,
    current: str,
    references: Mapping[str, str],
    all_japanese: tuple[str, ...],
    all_korean: tuple[str, ...],
) -> dict[str, Any]:
    """Verify the narrow evidence rule behind the inherited hold group."""
    if group_id.startswith("dummy_"):
        if not DUMMY_RE.fullmatch(current):
            raise ValueError(f"dummy hold is no longer dummy at msgdata:{coordinate}")
    elif group_id.startswith("identifier_"):
        if not is_identifier(current):
            raise ValueError(f"identifier hold is no longer an identifier at msgdata:{coordinate}")
    else:
        raise ValueError(f"unknown msgdata hold group: {group_id}")

    reference_values = tuple(references.values())
    if group_id == "dummy_source_marker":
        if "dummy" not in source.casefold() and "\u30c0\u30df\u30fc" not in source:
            raise ValueError(f"source-marker hold lacks source dummy marker at msgdata:{coordinate}")
        reason = "source_itself_is_internal_dummy_marker"
    elif group_id == "dummy_ruby_or_reading":
        if not all(is_placeholder(value) for value in reference_values):
            raise ValueError(f"reading/internal hold unexpectedly has display reference at msgdata:{coordinate}")
        reason = "reading_or_internal_label_without_display_route"
    elif group_id == "dummy_exact_source_alias":
        aliases = [
            index
            for index, value in enumerate(all_japanese)
            if index != coordinate and value == source and not is_placeholder(all_korean[index])
        ]
        if not aliases:
            raise ValueError(f"alias hold lacks a non-placeholder Korean counterpart at msgdata:{coordinate}")
        reason = "alternate_or_alias_route_requires_runtime_confirmation"
    elif group_id == "dummy_reference_language_but_unproven":
        if not any(not is_placeholder(value) for value in reference_values):
            raise ValueError(f"reference-language hold lost its PC reference text at msgdata:{coordinate}")
        if coordinate not in PARTIAL_REFERENCE_TRAIT_IDS:
            raise ValueError(f"unexpected reference-language hold coordinate: {coordinate}")
        reason = "partial_PC_reference_text_does_not_prove_Korean_display_route"
    elif group_id == "dummy_unconfirmed_visible_route":
        if not all(is_placeholder(value) for value in reference_values):
            raise ValueError(f"unconfirmed route now has a display reference at msgdata:{coordinate}")
        reason = "all_PC_references_are_empty_or_placeholder"
    elif group_id == "identifier_all_locales_placeholder":
        if not all(is_identifier(value) for value in reference_values):
            raise ValueError(f"identifier hold has non-identifier PC reference at msgdata:{coordinate}")
        reason = "all_PC_locales_keep_internal_identifier"
    elif group_id == "identifier_ruby":
        if not KANA_RE.search(source):
            raise ValueError(f"landmark reading hold is not a kana reading at msgdata:{coordinate}")
        if current != all_korean[PRIOR_VISIBLE_LANDMARK_CANDIDATE]:
            raise ValueError(f"landmark reading no longer shares the display identifier at msgdata:{coordinate}")
        reason = "phonetic_companion_of_separately_reviewed_visible_landmark_title"
    else:
        raise ValueError(f"unhandled msgdata hold group: {group_id}")
    return {
        "reference_values_are_all_placeholder": all(is_placeholder(value) for value in reference_values),
        "reference_values_have_display_text": any(not is_placeholder(value) for value in reference_values),
        "route_evidence": reason,
    }


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    file_hashes = {language: file_hash(path) for language, path in PATHS.items()}
    if file_hashes != EXPECTED_FILE_SHA256:
        raise ValueError("PC msgdata baseline hash differs; rebase audit before reuse")
    tables = {language: load_table(path) for language, path in PATHS.items()}
    if any(len(table) != len(tables["jp"]) for table in tables.values()):
        raise ValueError("PC msgdata table cardinalities differ")

    queue = queue_rows()
    review_coordinates = set(queue)
    group_by_coordinate = prior_hold_groups(review_coordinates)
    active_coordinates = active_builder_coordinates()
    active_overlap = review_coordinates.intersection(active_coordinates)
    if active_overlap != EXPECTED_ACTIVE_COORDINATES:
        raise ValueError("active msgdata candidate overlap differs; re-review residual partition before reuse")
    residual_coordinates = review_coordinates - active_overlap
    if len(residual_coordinates) != EXPECTED_RESIDUAL_COUNT:
        raise ValueError("residual msgdata literal-placeholder count differs from reviewed 330 coordinates")

    group_counts = Counter(group_by_coordinate[coordinate]["group_id"] for coordinate in residual_coordinates)
    if dict(sorted(group_counts.items())) != dict(sorted(EXPECTED_RESIDUAL_GROUP_COUNTS.items())):
        raise ValueError("residual msgdata hold-group counts differ from reviewed partition")

    rows: list[dict[str, Any]] = []
    for coordinate in sorted(residual_coordinates):
        source = tables["jp"][coordinate]
        current = tables["ko"][coordinate]
        queue_row = queue[coordinate]
        if not source or queue_row.get("jp") != source or queue_row.get("ko") != current:
            raise ValueError(f"queue source/current text differs from PC msgdata at {coordinate}")
        if queue_row.get("jp_utf16le_sha256") != text_hash(source) or queue_row.get("ko_utf16le_sha256") != text_hash(current):
            raise ValueError(f"queue source/current hash differs from PC msgdata at {coordinate}")
        references = {language.upper(): tables[language][coordinate] for language in ("en", "sc", "tc")}
        if queue_row.get("contexts") != references:
            raise ValueError(f"queue PC reference contexts differ at msgdata:{coordinate}")

        group = group_by_coordinate.get(coordinate)
        if group is None:
            raise ValueError(f"residual coordinate has no inherited hold group: {coordinate}")
        group_id = group["group_id"]
        route_evidence = row_route_checks(
            coordinate,
            group_id,
            source,
            current,
            references,
            tables["jp"],
            tables["ko"],
        )
        flags = queue_row.get("flags")
        if not isinstance(flags, list) or not flags:
            raise ValueError(f"queue flags are invalid at msgdata:{coordinate}")
        rows.append(
            {
                "schema": "nobu16.kr.msgdata-literal-placeholder-residual-hold.v1",
                "resource": "msgdata",
                "coordinate": str(coordinate),
                "candidate_disposition": "hold_no_new_candidate",
                "current_ko": current,
                "current_ko_utf16le_sha256": text_hash(current),
                "source_jp": source,
                "source_jp_utf16le_sha256": text_hash(source),
                "reference_contexts": references,
                "queue_flags": flags,
                "hold_group_id": group_id,
                "hold_status": group["status"],
                "hold_rationale": group["rationale"],
                "hold_selection_rule": group["selection_rule"],
                "route_evidence": route_evidence,
                "source_file_sha256": file_hashes["jp"],
                "current_file_sha256": file_hashes["ko"],
                "reference_file_sha256": {language.upper(): file_hashes[language] for language in ("en", "sc", "tc")},
                "audit_scope": {
                    "pristine_pc_japanese": True,
                    "current_pc_korean": True,
                    "pc_en_sc_tc_references": True,
                    "switch_korean_read": False,
                    "historic_korean_read": False,
                    "steam_game_resource_written": False,
                },
            }
        )

    summary = {
        "schema": "nobu16.kr.msgdata-literal-placeholder-residual-summary.v1",
        "review_coordinate_count": len(review_coordinates),
        "active_builder_candidate_count": len(active_overlap),
        "residual_hold_count": len(rows),
        "new_translation_candidate_count": 0,
        "residual_hold_group_counts": dict(sorted(group_counts.items())),
        "partial_reference_trait_hold_count": len(PARTIAL_REFERENCE_TRAIT_IDS),
        "visible_landmark_reading_hold_coordinate": 26433,
    }
    return rows, summary


def payload(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def validate_rows(rows: list[dict[str, Any]], summary: Mapping[str, Any]) -> None:
    if len(rows) != EXPECTED_RESIDUAL_COUNT:
        raise ValueError("wrong residual hold row count")
    coordinates = {int(row["coordinate"]) for row in rows}
    if len(coordinates) != len(rows):
        raise ValueError("duplicate residual hold coordinate")
    if coordinates.intersection(EXPECTED_ACTIVE_COORDINATES):
        raise ValueError("residual hold duplicates an active builder candidate")
    if any("ko" in row or "proposed_ko" in row for row in rows):
        raise ValueError("hold artifact must not contain a Korean replacement field")
    if Counter(row["hold_group_id"] for row in rows) != Counter(EXPECTED_RESIDUAL_GROUP_COUNTS):
        raise ValueError("hold artifact group counts are wrong")
    if {int(row["coordinate"]) for row in rows if row["hold_group_id"] == "dummy_reference_language_but_unproven"} != PARTIAL_REFERENCE_TRAIT_IDS:
        raise ValueError("partial-reference trait hold partition is wrong")
    ruby_rows = [row for row in rows if row["hold_group_id"] == "identifier_ruby"]
    if len(ruby_rows) != 1 or ruby_rows[0]["coordinate"] != "26433":
        raise ValueError("landmark reading hold partition is wrong")
    if summary.get("new_translation_candidate_count") != 0:
        raise ValueError("residual hold audit must not produce speculative candidates")
    if not all(row["audit_scope"]["switch_korean_read"] is False for row in rows):
        raise ValueError("hold artifact incorrectly claims Switch Korean input")
    if not all(row["audit_scope"]["steam_game_resource_written"] is False for row in rows):
        raise ValueError("hold artifact incorrectly claims a Steam resource write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true", help="write the private evidence-only hold JSONL")
    parser.add_argument("--validate", action="store_true", help="validate generated rows and any existing output")
    args = parser.parse_args()

    output = safe_under(args.output, AUDIT_ROOT)
    rows, summary = build_rows()
    validate_rows(rows, summary)
    expected_payload = payload(rows)
    if args.write:
        atomic_write(output, expected_payload)
    if args.validate and output.exists() and output.read_text(encoding="utf-8") != expected_payload:
        raise ValueError("existing residual hold output differs from current deterministic evidence")
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
