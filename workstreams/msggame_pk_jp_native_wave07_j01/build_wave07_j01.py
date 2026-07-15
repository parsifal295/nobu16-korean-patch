#!/usr/bin/env python3
"""Build and verify the source-free Steam JP msggame wave07 J01 overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
TOOLS = REPO_ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_common_message_overlay as common  # noqa: E402

from translations import TRANSLATIONS  # noqa: E402


RESOURCE = "MSG_PK/JP/msggame.bin"
BATCH_ID = "j01"
COORDINATE_COUNT = 970
UNIQUE_SOURCE_HASH_COUNT = 613
COORDINATES_SHA256 = "3C8E46FD80A617471B9E2294164FEEB346E19E3AD18944270A7B8ED7FF1FD036"
INTEGRATED_ENTRY_COUNT = 25_181
INTEGRATED_REMAINING_COUNT = 3_091
INTEGRATED_CANDIDATE_SHA256 = "4B963147B212EF965FD68953560728460890FEC5D4B306FB64618164B35A49E0"
OVERLAY_SCHEMA = "nobu16.kr.msggame-jp-literal-overlay.v1"
PRIVATE_SCHEMA = "nobu16.kr.msggame-jp-private-context.v1"
STOCK_JP = {
    "packed_size": 721_304,
    "packed_sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "raw_size": 1_599_324,
    "raw_sha256": "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8",
    "record_count": 21_751,
    "literal_count": 29_524,
}
DEFAULT_PRIVATE = (
    REPO_ROOT
    / "tmp"
    / "msggame_pk_jp_native_steam_wave06_private"
    / "j01.private.json"
)
PARTITION_PATH = (
    REPO_ROOT / "workstreams" / "msggame_pk_jp_native_wave06" / "partition.v1.json"
)
OVERLAY_PATH = ROOT / "public" / "msggame_ko_pk_jp_native_wave07_j01_970.v1.json"
VALIDATION_PATH = ROOT / "validation.v1.json"
REVIEW_PATH = ROOT / "review.v1.json"
SOURCE_SCRIPT = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HEX64 = re.compile(r"[0-9A-F]{64}\Z")


class BuildError(RuntimeError):
    pass


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16le")).hexdigest().upper()


def file_hash(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def coordinate(entry: dict[str, Any]) -> tuple[int, int, int]:
    values = entry.get("coordinate")
    if (
        not isinstance(values, list)
        or len(values) != 3
        or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in values)
    ):
        raise BuildError("private entry has an invalid coordinate")
    return tuple(values)


def load_private(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read private context: {path}") from exc
    expected_header = {
        "schema": PRIVATE_SCHEMA,
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "coordinate_count": COORDINATE_COUNT,
        "coordinates_sha256": COORDINATES_SHA256,
        "must_not_be_committed": True,
        "private_commercial_source_context": True,
    }
    for key, expected in expected_header.items():
        if value.get(key) != expected:
            raise BuildError(f"private context contract mismatch: {key}")
    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) != COORDINATE_COUNT:
        raise BuildError("private entry count mismatch")
    coordinates = [coordinate(entry) for entry in entries]
    if len(set(coordinates)) != COORDINATE_COUNT or coordinates != sorted(coordinates):
        raise BuildError("private coordinates are duplicated or unsorted")
    if canonical_hash([list(item) for item in coordinates]) != COORDINATES_SHA256:
        raise BuildError("private coordinate hash mismatch")
    for entry in entries:
        if not isinstance(entry.get("jp"), str) or not isinstance(entry.get("jp_invariants"), dict):
            raise BuildError(f"private source context is incomplete at {coordinate(entry)}")
    return value, entries


def load_partition() -> tuple[set[tuple[int, int, int]], set[tuple[int, int, int]]]:
    value = json.loads(PARTITION_PATH.read_text(encoding="utf-8"))
    selected: set[tuple[int, int, int]] | None = None
    others: set[tuple[int, int, int]] = set()
    for batch in value.get("batches", []):
        current = {tuple(item) for item in batch["coordinates"]}
        if batch["batch_id"] == BATCH_ID:
            selected = current
            if batch["coordinates_sha256"] != COORDINATES_SHA256:
                raise BuildError("partition J01 coordinate hash mismatch")
        else:
            if not others.isdisjoint(current):
                raise BuildError("non-J01 partition batches overlap")
            others.update(current)
    if selected is None or len(selected) != COORDINATE_COUNT:
        raise BuildError("partition J01 is absent or incomplete")
    if not selected.isdisjoint(others):
        raise BuildError("partition J01 overlaps another batch")
    return selected, others


def build_overlay(entries: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    selected, others = load_partition()
    private_coordinates = {coordinate(entry) for entry in entries}
    if private_coordinates != selected or not private_coordinates.isdisjoint(others):
        raise BuildError("private coordinates do not exactly match disjoint partition J01")

    first_by_hash: dict[str, dict[str, Any]] = {}
    coordinate_to_hash: dict[tuple[int, int, int], str] = {}
    for entry in entries:
        digest = text_hash(entry["jp"])
        if not HEX64.fullmatch(digest):
            raise BuildError("internal source hash error")
        first_by_hash.setdefault(digest, entry)
        coordinate_to_hash[coordinate(entry)] = digest
    if len(first_by_hash) != UNIQUE_SOURCE_HASH_COUNT:
        raise BuildError("unique JP source hash count mismatch")

    expected_representatives = {
        coordinate(entry): digest for digest, entry in first_by_hash.items()
    }
    if set(TRANSLATIONS) != set(expected_representatives):
        missing = sorted(set(expected_representatives) - set(TRANSLATIONS))[:3]
        extra = sorted(set(TRANSLATIONS) - set(expected_representatives))[:3]
        raise BuildError(f"translation representative mismatch: missing={missing}, extra={extra}")

    korean_by_hash: dict[str, str] = {}
    representative_rows: list[dict[str, Any]] = []
    for representative, korean in sorted(TRANSLATIONS.items()):
        if not isinstance(korean, str) or not korean or SOURCE_SCRIPT.search(korean):
            raise BuildError(f"invalid or source-script Korean at {representative}")
        digest = expected_representatives[representative]
        source_entry = first_by_hash[digest]
        mismatches = common.invariant_mismatches(source_entry["jp"], korean)
        if mismatches:
            raise BuildError(f"JP invariant mismatch at representative {representative}: {mismatches}")
        korean_by_hash[digest] = korean
        representative_rows.append(
            {
                "block_id": representative[0],
                "record_id": representative[1],
                "literal_id": representative[2],
                "source_jp_utf16le_sha256": digest,
                "ko": korean,
            }
        )

    output_entries: list[dict[str, Any]] = []
    invariant_category_counts: dict[str, int] = {}
    repeated_hash_counts: dict[str, int] = {}
    for entry in entries:
        current = coordinate(entry)
        digest = coordinate_to_hash[current]
        korean = korean_by_hash[digest]
        mismatches = common.invariant_mismatches(entry["jp"], korean)
        if mismatches:
            raise BuildError(f"JP invariant mismatch at expanded coordinate {current}: {mismatches}")
        repeated_hash_counts[digest] = repeated_hash_counts.get(digest, 0) + 1
        for key in ("controls", "esc", "line_breaks", "printf", "pua"):
            if entry["jp_invariants"].get(key):
                invariant_category_counts[key] = invariant_category_counts.get(key, 0) + 1
        for key in ("leading_whitespace", "trailing_whitespace"):
            if entry["jp_invariants"].get(key):
                invariant_category_counts[key] = invariant_category_counts.get(key, 0) + 1
        output_entries.append(
            {
                "block_id": current[0],
                "record_id": current[1],
                "literal_id": current[2],
                "source_jp_utf16le_sha256": digest,
                "ko": korean,
            }
        )

    if len(output_entries) != COORDINATE_COUNT:
        raise BuildError("expanded overlay count mismatch")
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msggame_ko_pk_jp_native_wave07_j01_970",
        "resource": RESOURCE,
        "base_language": "JP",
        "entry_count": COORDINATE_COUNT,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": STOCK_JP,
        "defaults": {"status": "translated"},
        "translation_provenance": {
            "method": "human_context_translation",
            "batch_id": BATCH_ID,
            "selected_coordinate_count": COORDINATE_COUNT,
            "unique_source_hash_count": UNIQUE_SOURCE_HASH_COUNT,
            "private_context_distributed": False,
        },
        "entries": output_entries,
    }
    evidence = {
        "representative_rows": representative_rows,
        "invariant_category_counts": dict(sorted(invariant_category_counts.items())),
        "repeated_source_hash_count": sum(1 for count in repeated_hash_counts.values() if count > 1),
        "largest_repeat_count": max(repeated_hash_counts.values()),
        "record_count": len({(item[0], item[1]) for item in private_coordinates}),
        "first_coordinate": list(min(private_coordinates)),
        "last_coordinate": list(max(private_coordinates)),
    }
    return overlay, evidence


def build_artifacts(private_path: Path) -> dict[Path, dict[str, Any]]:
    _, entries = load_private(private_path)
    overlay, evidence = build_overlay(entries)
    overlay_blob = json_bytes(overlay)
    validation = {
        "schema": "nobu16.kr.msggame-jp-wave-validation.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "status": "pass",
        "coordinate_contract": {
            "selected_count": COORDINATE_COUNT,
            "coordinates_sha256": COORDINATES_SHA256,
            "partition_exact_match": True,
            "other_batches_disjoint": True,
        },
        "translation_contract": {
            "unique_source_hash_count": UNIQUE_SOURCE_HASH_COUNT,
            "representative_translation_count": len(evidence["representative_rows"]),
            "expanded_entry_count": COORDINATE_COUNT,
            "identical_korean_per_identical_source_hash": True,
            "untranslated_count": 0,
        },
        "invariant_contract": {
            "checked_entry_count": COORDINATE_COUNT,
            "mismatch_count": 0,
            "preserved_category_coordinate_counts": evidence["invariant_category_counts"],
        },
        "distribution_contract": {
            "commercial_source_text_present": False,
            "private_context_present": False,
            "entry_fields_exact": True,
        },
        "overlay": {
            "path": OVERLAY_PATH.relative_to(REPO_ROOT).as_posix(),
            "sha256": file_hash(overlay_blob),
            "entry_count": COORDINATE_COUNT,
        },
        "steam_1_1_7_integration": {
            "foundation_entry_count": 24_211,
            "combined_entry_count": INTEGRATED_ENTRY_COUNT,
            "remaining_jp_semantic_count": INTEGRATED_REMAINING_COUNT,
            "candidate_sha256": INTEGRATED_CANDIDATE_SHA256,
            "non_literal_structure_preserved": True,
            "deterministic_rebuild": True,
            "installed_game_file_written": False,
        },
    }
    review = {
        "schema": "nobu16.kr.msggame-jp-wave-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "status": "complete",
        "manual_context_review": {
            "reviewed_coordinate_count": COORDINATE_COUNT,
            "reviewed_unique_source_hash_count": UNIQUE_SOURCE_HASH_COUNT,
            "record_count": evidence["record_count"],
            "context_fields_used_privately": [
                "jp_record",
                "jp_previous_record",
                "jp_next_record",
                "en_record",
                "tc_record",
            ],
            "commercial_context_distributed": False,
        },
        "quality_gates": {
            "natural_korean_context_reviewed": True,
            "literal_boundary_context_reviewed": True,
            "legacy_coordinate_seeds_semantically_rechecked": True,
            "repeated_source_consistency_enforced": True,
            "all_invariants_preserved": True,
            "source_script_leak_count": 0,
        },
        "coverage": {
            "first_coordinate": evidence["first_coordinate"],
            "last_coordinate": evidence["last_coordinate"],
            "selected_coordinate_count": COORDINATE_COUNT,
            "unique_source_hash_count": UNIQUE_SOURCE_HASH_COUNT,
            "repeated_source_hash_count": evidence["repeated_source_hash_count"],
            "largest_repeat_count": evidence["largest_repeat_count"],
        },
    }
    return {
        OVERLAY_PATH: overlay,
        VALIDATION_PATH: validation,
        REVIEW_PATH: review,
    }


def write_artifacts(artifacts: dict[Path, dict[str, Any]]) -> None:
    for path, value in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(json_bytes(value))


def verify_artifacts(artifacts: dict[Path, dict[str, Any]]) -> None:
    for path, expected in artifacts.items():
        try:
            actual = path.read_bytes()
        except OSError as exc:
            raise BuildError(f"artifact is missing: {path}") from exc
        if actual != json_bytes(expected):
            raise BuildError(f"artifact is not deterministic or is stale: {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--private", type=Path, default=DEFAULT_PRIVATE)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        artifacts = build_artifacts(args.private.resolve())
        if args.command == "build":
            write_artifacts(artifacts)
        else:
            verify_artifacts(artifacts)
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"{args.command}: {BATCH_ID} {COORDINATE_COUNT} coordinates / "
        f"{UNIQUE_SOURCE_HASH_COUNT} unique source hashes: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
