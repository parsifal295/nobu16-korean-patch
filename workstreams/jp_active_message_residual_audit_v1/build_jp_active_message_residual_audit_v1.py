#!/usr/bin/env python3
"""Read-only residual audit for the active Steam JP message route.

This tool parses only the JP resources that are active when the Steam PK
executable is run.  It does not rebuild a message table, copy a game file, or
touch an installation file.  Its two outputs contain coordinate and SHA-256
metadata only; they deliberately never serialize a game string.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Literal


WORKSTREAM = Path(__file__).resolve().parent
REPOSITORY = WORKSTREAM.parent.parent
TOOLS = REPOSITORY / "tools"
MSGGAME_TOOLS = REPOSITORY / "workstreams" / "msggame"
STRDATA_TOOLS = REPOSITORY / "workstreams" / "strdata"

for tool_dir in (TOOLS, MSGGAME_TOOLS, STRDATA_TOOLS):
    if str(tool_dir) not in sys.path:
        sys.path.insert(0, str(tool_dir))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402
from msggame_format import iter_literals, parse_packed_msggame  # noqa: E402
from strdata_format import parse_raw_strdata  # noqa: E402


ResourceKind = Literal["common", "msggame", "strdata"]

RESOURCE_SPECS: tuple[tuple[str, ResourceKind], ...] = (
    ("MSG/JP/msggame.bin", "msggame"),
    ("MSG/JP/strdata.bin", "strdata"),
    ("MSG/JP/ev_strdata.bin", "common"),
    ("MSG_PK/JP/msgbre.bin", "common"),
    ("MSG_PK/JP/msgdata.bin", "common"),
    ("MSG_PK/JP/msgev.bin", "common"),
    ("MSG_PK/JP/msggame.bin", "msggame"),
    ("MSG_PK/JP/msgire.bin", "common"),
    ("MSG_PK/JP/msgstf.bin", "common"),
    ("MSG_PK/JP/msgui.bin", "common"),
)

RESOURCE_KIND = dict(RESOURCE_SPECS)

KANA = re.compile(r"[\u3040-\u30ff\uff66-\uff9f]")
HANGUL = re.compile(r"[\uac00-\ud7a3]")
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

TUTORIAL_RESOURCE = "MSG/JP/msggame.bin"
TUTORIAL_COORDINATE = (13, 217, 0)
TUTORIAL_SOURCE_SHA256 = "279D8D1246B6C655F8E6FEC0DA1CAA7848AAA1E0EB58C1AA13370EBF5E84BC5B"
TUTORIAL_KO_SHA256 = "0EA8FAF9225A94AF8A10296E06FC1AF873806B8C5CE10C53A2997836A7B42067"

TRACKED_CATEGORIES = (
    "japanese_kana_no_hangul",
    "hanja_only_no_hangul_review",
    "mixed_hangul_kana_review",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_sha256(value: object) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def classify_text(value: str) -> str:
    """Classify without treating CJK-only strings as definitely Japanese.

    Kanji/Hanja overlaps across Japanese, Korean, and Chinese.  A kana-bearing
    string with no Hangul is therefore the only high-confidence remaining
    Japanese bucket.  Hanja-only and mixed Hangul/kana strings are preserved as
    explicit review buckets rather than inflated into a translation count.
    """

    visible = any(character.isprintable() and not character.isspace() for character in value)
    if not visible:
        return "nonvisible"
    has_hangul = bool(HANGUL.search(value))
    has_kana = bool(KANA.search(value))
    has_cjk = bool(CJK.search(value))
    if has_kana and not has_hangul:
        return "japanese_kana_no_hangul"
    if has_kana and has_hangul:
        return "mixed_hangul_kana_review"
    if has_cjk and not has_hangul:
        return "hanja_only_no_hangul_review"
    if has_hangul:
        return "hangul_or_other"
    return "other"


def coordinate_object(kind: ResourceKind, coordinate: tuple[int, ...]) -> dict[str, int]:
    if kind == "common":
        return {"id": coordinate[0]}
    if kind == "strdata":
        return {"block_id": coordinate[0], "slot_id": coordinate[1]}
    return {"block_id": coordinate[0], "record_id": coordinate[1], "literal_id": coordinate[2]}


def coordinate_key(kind: ResourceKind, entry: dict[str, Any]) -> tuple[int, ...] | None:
    try:
        if kind == "common":
            return (int(entry["id"]),)
        if kind == "strdata":
            return (int(entry["block_id"]), int(entry["slot_id"]))
        return (int(entry["block_id"]), int(entry["record_id"]), int(entry["literal_id"]))
    except (KeyError, TypeError, ValueError):
        return None


def parse_resource(game_root: Path, logical_path: str, kind: ResourceKind) -> tuple[list[tuple[tuple[int, ...], str]], dict[str, int | str]]:
    path = game_root / logical_path
    packed = path.read_bytes()
    file_metadata: dict[str, int | str] = {
        "relative_path": logical_path,
        "packed_sha256": sha256_bytes(packed),
        "packed_size": len(packed),
    }

    if kind == "common":
        _, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
        file_metadata.update({"raw_size": len(raw), "entries": table.string_count})
        return [((entry_id,), text) for entry_id, text in enumerate(table.texts)], file_metadata

    if kind == "strdata":
        _, raw = decompress_wrapper(packed)
        archive = parse_raw_strdata(raw)
        rows = [
            ((block.block_id, slot_id), text)
            for block in archive.blocks
            for slot_id, text in enumerate(block.texts)
        ]
        file_metadata.update({"raw_size": len(raw), "blocks": len(archive.blocks), "slots": len(rows)})
        return rows, file_metadata

    parsed = parse_packed_msggame(packed)
    literals = list(iter_literals(parsed.archive))
    rows = [
        ((literal.block_id, literal.record_id, literal.literal_id), literal.text)
        for literal in literals
    ]
    file_metadata.update(
        {
            "raw_size": parsed.archive.raw_size,
            "blocks": len(parsed.archive.blocks),
            "records": sum(len(block.records) for block in parsed.archive.blocks),
            "literals": len(rows),
        }
    )
    return rows, file_metadata


def first_hash(entry: dict[str, Any], candidates: Iterable[str]) -> str | None:
    for key in candidates:
        value = entry.get(key)
        if isinstance(value, str) and re.fullmatch(r"[0-9A-Fa-f]{64}", value):
            return value.upper()
    return None


def native_catalog_index() -> tuple[dict[str, dict[tuple[int, ...], list[dict[str, str]]]], dict[str, int]]:
    """Index only explicitly JP-targeted public catalogs.

    Older SC catalogs are intentionally ignored: a matching coordinate in an
    SC-targeted file is not proof that it safely applies to the active JP route.
    """

    index: dict[str, dict[tuple[int, ...], list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    metadata = Counter()
    for path in sorted((REPOSITORY / "workstreams").rglob("*.json")):
        if "public" not in path.parts:
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            metadata["unreadable_or_non_json_public_files"] += 1
            continue
        if not isinstance(document, dict):
            continue
        logical_path = document.get("resource")
        entries = document.get("entries")
        if logical_path not in RESOURCE_KIND or not isinstance(entries, list):
            continue
        kind = RESOURCE_KIND[logical_path]
        relative_catalog = path.relative_to(REPOSITORY).as_posix()
        metadata["jp_catalog_files"] += 1
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("ko"), str):
                continue
            coordinate = coordinate_key(kind, entry)
            if coordinate is None:
                metadata["invalid_catalog_entries"] += 1
                continue
            ko_hash = first_hash(entry, ("ko_utf16le_sha256",)) or text_sha256(entry["ko"])
            source_hash = first_hash(
                entry,
                (
                    "source_jp_utf16le_sha256",
                    "stock_jp_utf16le_sha256",
                    "legacy_source_jp_utf16le_sha256",
                ),
            )
            contract = {
                "catalog": relative_catalog,
                "ko_utf16le_sha256": ko_hash,
            }
            if source_hash is not None:
                contract["source_jp_utf16le_sha256"] = source_hash
            index[logical_path][coordinate].append(contract)
            metadata["jp_catalog_entries"] += 1
    metadata["jp_catalog_effective_coordinates"] = sum(
        len(coordinates) for coordinates in index.values()
    )
    return index, dict(sorted(metadata.items()))


def catalog_status(contracts: list[dict[str, str]], active_hash: str) -> tuple[str, list[str]]:
    catalogs = sorted({contract["catalog"] for contract in contracts})
    if any(contract["ko_utf16le_sha256"] == active_hash for contract in contracts):
        return "active_matches_known_ko", catalogs
    if any(contract.get("source_jp_utf16le_sha256") == active_hash for contract in contracts):
        return "known_ko_but_jp_source_active", catalogs
    if contracts:
        return "catalog_coordinate_present_but_hash_changed", catalogs
    return "not_covered_by_jp_catalog", catalogs


def chunked(values: list[dict[str, Any]], chunk_size: int) -> Iterable[list[dict[str, Any]]]:
    for start in range(0, len(values), chunk_size):
        yield values[start : start + chunk_size]


def coordinate_digest(entries: list[dict[str, Any]]) -> str:
    return canonical_sha256([entry["coordinate"] for entry in entries])


def planned_bundles(contracts: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Create source-free, exact coordinate batches for the next workers."""

    plan = (
        ("MSG_PK/JP/msgui.bin", "japanese_kana_no_hangul", "P0", "screen_ui", 125),
        ("MSG/JP/strdata.bin", "japanese_kana_no_hangul", "P0", "name_and_label_review", 350),
        ("MSG_PK/JP/msgev.bin", "japanese_kana_no_hangul", "P1", "event_dialogue", 185),
        ("MSG_PK/JP/msgdata.bin", "japanese_kana_no_hangul", "P1", "data_and_readings", 175),
        ("MSG/JP/msggame.bin", "japanese_kana_no_hangul", "P2", "base_tutorial_and_system_tail", 100),
        ("MSG/JP/ev_strdata.bin", "japanese_kana_no_hangul", "P2", "base_event_tail", 100),
        ("MSG_PK/JP/msgbre.bin", "japanese_kana_no_hangul", "P2", "biography_tail", 100),
        ("MSG_PK/JP/msgstf.bin", "japanese_kana_no_hangul", "P2", "small_table_tail", 100),
    )
    bundles: list[dict[str, Any]] = []
    for resource, classification, priority, lane, chunk_size in plan:
        selected = [
            entry
            for entry in contracts.get(resource, [])
            if entry["classification"] == classification
        ]
        for index, group in enumerate(chunked(selected, chunk_size), start=1):
            bundles.append(
                {
                    "bundle_id": f"{priority.lower()}-{resource.replace('/', '_').replace('.bin', '')}-{index:02d}",
                    "priority": priority,
                    "translation_lane": lane,
                    "resource": resource,
                    "format": RESOURCE_KIND[resource],
                    "classification": classification,
                    "coordinate_count": len(group),
                    "coordinate_sha256": coordinate_digest(group),
                    "first_coordinate": group[0]["coordinate"],
                    "last_coordinate": group[-1]["coordinate"],
                    "coordinates": [entry["coordinate"] for entry in group],
                    "safe_application_route": {
                        "target": resource,
                        "basis": "active Steam JP file hash in validation.active_steam.v1.json",
                        "gate": "each source_jp_utf16le_sha256 must equal the staged JP text before rebuild",
                        "write_target": "staging candidate only; never the Steam installation during audit",
                    },
                }
            )
    return bundles


def tutorial_trace(rows: dict[str, dict[tuple[int, ...], str]]) -> dict[str, Any]:
    active_text = rows[TUTORIAL_RESOURCE].get(TUTORIAL_COORDINATE)
    if active_text is None:
        status = "coordinate_missing"
        active_hash = None
    else:
        active_hash = text_sha256(active_text)
        if active_hash == TUTORIAL_KO_SHA256:
            status = "ko_applied"
        elif active_hash == TUTORIAL_SOURCE_SHA256:
            status = "jp_source_still_active"
        else:
            status = "other_text_at_coordinate"
    return {
        "resource": TUTORIAL_RESOURCE,
        "coordinate": coordinate_object("msggame", TUTORIAL_COORDINATE),
        "active_utf16le_sha256": active_hash,
        "historical_jp_source_utf16le_sha256": TUTORIAL_SOURCE_SHA256,
        "expected_ko_utf16le_sha256": TUTORIAL_KO_SHA256,
        "status": status,
        "runtime_route_evidence": "workstreams/tutorial_dialogue_trace_msggame_v1/README_KO.md",
        "runtime_route": "base MSG/JP/msggame.bin remains referenced during PK execution",
    }


def assert_safe_output_dir(output_dir: Path, steam_root: Path) -> Path:
    resolved_output = output_dir.resolve()
    resolved_workstream = WORKSTREAM.resolve()
    resolved_steam = steam_root.resolve()
    if not resolved_output.is_relative_to(resolved_workstream):
        raise ValueError(f"output directory must stay under this audit workstream: {resolved_workstream}")
    if resolved_output.is_relative_to(resolved_steam):
        raise ValueError("refusing to write inside the Steam installation")
    return resolved_output


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_audit(steam_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if not steam_root.is_dir():
        raise ValueError(f"Steam root does not exist: {steam_root}")
    for logical_path, _ in RESOURCE_SPECS:
        if not (steam_root / logical_path).is_file():
            raise ValueError(f"missing active JP resource: {steam_root / logical_path}")

    catalog_index, catalog_metadata = native_catalog_index()
    live_rows: dict[str, dict[tuple[int, ...], str]] = {}
    resources: dict[str, Any] = {}
    source_free_entries: dict[str, list[dict[str, Any]]] = {}
    global_categories = Counter()
    global_catalog_status = Counter()

    for logical_path, kind in RESOURCE_SPECS:
        parsed_rows, file_metadata = parse_resource(steam_root, logical_path, kind)
        if len({coordinate for coordinate, _ in parsed_rows}) != len(parsed_rows):
            raise ValueError(f"duplicate coordinate in active resource: {logical_path}")
        by_coordinate = dict(parsed_rows)
        live_rows[logical_path] = by_coordinate
        categories = Counter()
        status_counts = Counter()
        tracked_entries: list[dict[str, Any]] = []
        for coordinate, text in parsed_rows:
            classification = classify_text(text)
            active_hash = text_sha256(text)
            categories[classification] += 1
            contracts = catalog_index.get(logical_path, {}).get(coordinate, [])
            status, catalogs = catalog_status(contracts, active_hash)
            status_counts[status] += 1
            if classification in TRACKED_CATEGORIES:
                tracked_entries.append(
                    {
                        "coordinate": coordinate_object(kind, coordinate),
                        "classification": classification,
                        "active_utf16le_sha256": active_hash,
                        "jp_catalog_status": status,
                        "jp_catalogs": catalogs,
                    }
                )
                global_categories[classification] += 1
                global_catalog_status[status] += 1
        tracked_entries.sort(key=lambda entry: tuple(entry["coordinate"].values()))
        source_free_entries[logical_path] = tracked_entries
        resources[logical_path] = {
            "format": kind,
            "active_file": file_metadata,
            "classification_counts": dict(sorted(categories.items())),
            "jp_catalog_status_counts_all_entries": dict(sorted(status_counts.items())),
            "tracked_review_coordinate_count": len(tracked_entries),
            "tracked_review_coordinate_sha256": coordinate_digest(tracked_entries),
        }

    bundles = planned_bundles(source_free_entries)
    high_confidence_total = global_categories["japanese_kana_no_hangul"]
    review_total = high_confidence_total + global_categories["hanja_only_no_hangul_review"] + global_categories["mixed_hangul_kana_review"]
    validation: dict[str, Any] = {
        "schema": "nobu16.kr.jp-active-message-residual-audit.v1",
        "purpose": "read-only active Steam JP residual audit; no game installation, release, or GitHub write",
        "scope": {
            "steam_root": str(steam_root),
            "resources": [logical_path for logical_path, _ in RESOURCE_SPECS],
            "excluded_catalog_routes": "all MSG/SC and MSG_PK/SC public catalogs",
            "live_game_file_written": False,
            "candidate_game_file_built": False,
            "release_asset_written": False,
            "github_written": False,
        },
        "native_jp_catalog_scan": catalog_metadata,
        "resources": resources,
        "remaining_summary": {
            "high_confidence_japanese_kana_no_hangul": high_confidence_total,
            "hanja_only_no_hangul_review": global_categories["hanja_only_no_hangul_review"],
            "mixed_hangul_kana_review": global_categories["mixed_hangul_kana_review"],
            "all_tracked_review_coordinates": review_total,
            "tracked_jp_catalog_status_counts": dict(sorted(global_catalog_status.items())),
        },
        "tutorial_dialogue_trace": tutorial_trace(live_rows),
        "recommended_parallel_bundles": bundles,
        "safe_next_step": {
            "translation": "translate only source-free contract coordinates against a pinned staged JP copy",
            "integration": "require per-coordinate JP source hash gates, parser roundtrip, and unchanged-coordinate checks",
            "prohibited_in_this_workstream": ["Steam installation write", "release upload", "GitHub write"],
        },
    }
    public_contract: dict[str, Any] = {
        "schema": "nobu16.kr.jp-active-message-residual-coordinate-contract.v1",
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "basis": {
            "active_steam_file_sha256": {
                logical_path: resources[logical_path]["active_file"]["packed_sha256"]
                for logical_path, _ in RESOURCE_SPECS
            },
            "excluded_catalog_routes": "all MSG/SC and MSG_PK/SC public catalogs",
        },
        "entries_by_resource": source_free_entries,
        "recommended_parallel_bundles": bundles,
    }
    return validation, public_contract


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, required=True, help="Steam NOBU16 root to read")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=WORKSTREAM,
        help="audit-only output directory; must remain under this workstream",
    )
    args = parser.parse_args()
    steam_root = args.steam_root.resolve()
    out_dir = assert_safe_output_dir(args.out_dir, steam_root)
    validation, public_contract = build_audit(steam_root)
    write_json(out_dir / "validation.active_steam.v1.json", validation)
    write_json(out_dir / "public" / "active_jp_remaining_coordinates.v1.json", public_contract)
    print(
        json.dumps(
            {
                "high_confidence_japanese_kana_no_hangul": validation["remaining_summary"]["high_confidence_japanese_kana_no_hangul"],
                "tutorial_dialogue_status": validation["tutorial_dialogue_trace"]["status"],
                "validation": str(out_dir / "validation.active_steam.v1.json"),
                "public_contract": str(out_dir / "public" / "active_jp_remaining_coordinates.v1.json"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
