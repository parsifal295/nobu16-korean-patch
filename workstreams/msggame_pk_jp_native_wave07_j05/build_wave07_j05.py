#!/usr/bin/env python3
"""Build the source-free Steam JP msggame wave07 j05 overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO_ROOT = SCRIPT.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
STEAM_BUILDER_ROOT = REPO_ROOT / "workstreams" / "steam_jp_msggame_v1"
sys.path[:0] = [str(TOOLS_ROOT), str(MSGGAME_ROOT), str(STEAM_BUILDER_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import build_steam_jp_msggame_v1 as steam  # noqa: E402
import msggame_format as msggame  # noqa: E402
from manual_records import MANUAL_RECORDS  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


BATCH_ID = "j05"
ENTRY_COUNT = 681
NON15_ENTRY_COUNT = 313
BLOCK15_ENTRY_COUNT = 368
ALLOWED_BLOCKS = {9, 10, 13, 14, 15, 16}
COORDINATES_SHA256 = "C239405BA072611E1F26FCDCE09D6BECD7DA224AA60FD8548299D907A4F15807"
NON15_COORDINATES_SHA256 = "945CF21EE0307AE986A18F3FF19538FBEE22BE870D0B0D421D05DE14D17E9943"
BLOCK15_COORDINATES_SHA256 = "6DEBEC08175C36416F37638641C0A40210B297186E922C441AFAE78DDB029C23"
BLOCK15_SUPPORT_SHA256 = "4A0F144A3C1FAC160335AF0B35BDF2CE335849F46925E722F85170398A7B008F"
PRIVATE_CONTEXT = (
    REPO_ROOT
    / "tmp"
    / "msggame_pk_jp_native_steam_wave06_private"
    / "j05.private.json"
)
BLOCK15_SUPPORT = (
    REPO_ROOT / "tmp" / "wave07_j05_block15_support" / "translations.ko.json"
)
OVERLAY_PATH = (
    WORKSTREAM
    / "public"
    / "msggame_ko_pk_jp_native_wave07_j05_681.v1.json"
)
VALIDATION_PATH = WORKSTREAM / "translation_validation.v1.json"
REVIEW_PATH = WORKSTREAM / "translation_review.v1.json"
OVERLAY_SCHEMA = "nobu16.kr.msggame-jp-literal-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.msggame-jp-wave-validation.v1"
REVIEW_SCHEMA = "nobu16.kr.msggame-jp-wave-review.v1"
EXPECTED_FOUNDATION = 24_211
J02_OVERLAY = (
    REPO_ROOT
    / "workstreams"
    / "msggame_pk_jp_native_wave07_j02"
    / "public"
    / "msggame_ko_pk_jp_native_wave07_j02_969.v1.json"
)
J02_OVERLAY_SHA256 = "A11CCFB77EF9CB28BD828CB834F290D5BE514E34722E5079E409E0D539974AAC"
J02_ENTRY_COUNT = 969
EXPECTED_COMBINED = 25_861
EXPECTED_REMAINING = 2_411
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
SOURCE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")


class BuildError(ValueError):
    """A batch, source-free, invariant, or Steam structure gate failed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_hash(value: Any) -> str:
    return sha256(
        json.dumps(
            value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )


def coordinate_lines_hash(coordinates: Iterable[Sequence[int]]) -> str:
    blob = "".join(
        f"{coordinate[0]}:{coordinate[1]}:{coordinate[2]}\n"
        for coordinate in coordinates
    ).encode("ascii")
    return sha256(blob)


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise BuildError(f"JSON root must be an object: {path}")
    return value


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": path.name, "size": len(blob), "sha256": sha256(blob)}


def load_private(path: Path) -> tuple[list[dict[str, Any]], dict[tuple[int, int, int], dict[str, Any]]]:
    value = read_json(path)
    if value.get("base_language") != "JP" or value.get("batch_id") != BATCH_ID:
        raise BuildError("private batch identity changed")
    entries = value.get("entries")
    if not isinstance(entries, list) or value.get("coordinate_count") != ENTRY_COUNT:
        raise BuildError("private batch entry count changed")
    coordinates = [entry.get("coordinate") for entry in entries]
    if any(
        not isinstance(coordinate, list)
        or len(coordinate) != 3
        or coordinate[0] not in ALLOWED_BLOCKS
        or any(isinstance(item, bool) or not isinstance(item, int) for item in coordinate)
        for coordinate in coordinates
    ):
        raise BuildError("private batch contains an invalid coordinate")
    if value.get("coordinates_sha256") != COORDINATES_SHA256:
        raise BuildError("private batch coordinate pin changed")
    if canonical_hash(coordinates) != COORDINATES_SHA256:
        raise BuildError("private batch coordinates are not canonical or pinned")
    mapped = {tuple(entry["coordinate"]): entry for entry in entries}
    if len(mapped) != ENTRY_COUNT:
        raise BuildError("private batch contains duplicate coordinates")
    non15_coordinates = [coordinate for coordinate in coordinates if coordinate[0] != 15]
    block15_coordinates = [coordinate for coordinate in coordinates if coordinate[0] == 15]
    if (
        len(non15_coordinates) != NON15_ENTRY_COUNT
        or canonical_hash(non15_coordinates) != NON15_COORDINATES_SHA256
    ):
        raise BuildError("private non-block15 partition changed")
    if (
        len(block15_coordinates) != BLOCK15_ENTRY_COUNT
        or coordinate_lines_hash(block15_coordinates) != BLOCK15_COORDINATES_SHA256
    ):
        raise BuildError("private block15 partition changed")
    return entries, mapped


def load_block15_support(
    path: Path,
    private_map: dict[tuple[int, int, int], dict[str, Any]],
) -> dict[tuple[int, int, int], str]:
    blob = path.read_bytes()
    if sha256(blob) != BLOCK15_SUPPORT_SHA256:
        raise BuildError("block15 support SHA256 changed")
    value = json.loads(blob.decode("utf-8-sig"))
    if not isinstance(value, list) or len(value) != BLOCK15_ENTRY_COUNT:
        raise BuildError("block15 support entry count changed")
    translations: dict[tuple[int, int, int], str] = {}
    coordinates: list[list[int]] = []
    for row in value:
        if not isinstance(row, dict):
            raise BuildError("block15 support row must be an object")
        coordinate = row.get("coordinate")
        korean = row.get("ko")
        if (
            not isinstance(coordinate, list)
            or len(coordinate) != 3
            or coordinate[0] != 15
            or any(isinstance(item, bool) or not isinstance(item, int) for item in coordinate)
            or not isinstance(korean, str)
            or not korean
        ):
            raise BuildError("invalid block15 support row")
        key = tuple(coordinate)
        if key in translations or key not in private_map:
            raise BuildError(f"invalid block15 support coordinate: {key}")
        if unicodedata.normalize("NFC", korean) != korean:
            raise BuildError(f"non-NFC block15 support translation: {key}")
        translations[key] = korean
        coordinates.append(coordinate)
    if coordinate_lines_hash(coordinates) != BLOCK15_COORDINATES_SHA256:
        raise BuildError("block15 support coordinate pin changed")
    return translations


def apply_record_map(
    translations: dict[tuple[int, int, int], str],
    origins: dict[tuple[int, int, int], str],
    private_by_record: dict[tuple[int, int], list[dict[str, Any]]],
    records: dict[tuple[int, int], tuple[str, ...]],
    origin: str,
) -> None:
    for record_key, korean_literals in sorted(records.items()):
        assigned = sorted(
            private_by_record.get(record_key, []),
            key=lambda entry: entry["coordinate"][2],
        )
        if len(assigned) != len(korean_literals):
            raise BuildError(
                f"{origin} record {record_key} literal count mismatch: "
                f"{len(korean_literals)} != {len(assigned)}"
            )
        for entry, korean in zip(assigned, korean_literals, strict=True):
            coordinate = tuple(entry["coordinate"])
            translations[coordinate] = korean
            origins[coordinate] = origin


def assemble(
    private_entries: list[dict[str, Any]],
    support_translations: dict[tuple[int, int, int], str],
) -> tuple[dict[tuple[int, int, int], str], dict[tuple[int, int, int], str], dict[str, Any]]:
    batch_coordinates = {tuple(entry["coordinate"]) for entry in private_entries}
    by_record: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    by_coordinate = {tuple(entry["coordinate"]): entry for entry in private_entries}
    for entry in private_entries:
        coordinate = entry["coordinate"]
        by_record[(coordinate[0], coordinate[1])].append(entry)

    translations: dict[tuple[int, int, int], str] = {}
    origins: dict[tuple[int, int, int], str] = {}
    apply_record_map(
        translations, origins, by_record, MANUAL_RECORDS, "new_manual_context_translation"
    )
    if any(coordinate[0] == 15 for coordinate in translations):
        raise BuildError("manual translation map overlaps block15 support")
    for coordinate, korean in sorted(support_translations.items()):
        translations[coordinate] = korean
        origins[coordinate] = "parallel_block15_human_context_translation"

    manual_coordinates = {coordinate for coordinate in translations if coordinate[0] != 15}
    if len(manual_coordinates) != NON15_ENTRY_COUNT:
        raise BuildError(
            f"manual non-block15 coverage changed: {len(manual_coordinates)}"
        )

    missing = batch_coordinates - set(translations)
    extra = set(translations) - batch_coordinates
    if missing or extra:
        raise BuildError(
            f"translation coverage mismatch: missing={sorted(missing)[:5]} "
            f"extra={sorted(extra)[:5]}"
        )

    invariant_profile_count = 0
    invariant_field_counts: Counter[str] = Counter()
    repeated: dict[str, set[str]] = defaultdict(set)
    repeated_coordinates: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    for coordinate in sorted(batch_coordinates):
        source = by_coordinate[coordinate]["jp"]
        korean = translations[coordinate]
        if not isinstance(korean, str) or not korean or SOURCE_SCRIPT_RE.search(korean):
            raise BuildError(f"invalid or source-bearing Korean at {coordinate}")
        mismatches = common.invariant_mismatches(source, korean)
        if mismatches:
            raise BuildError(f"invariant mismatch at {coordinate}: {mismatches}")
        invariants = by_coordinate[coordinate].get("jp_invariants")
        if not isinstance(invariants, dict):
            raise BuildError(f"missing invariant profile at {coordinate}")
        active = [
            key for key, value in invariants.items() if value not in (None, "", [], 0)
        ]
        if active:
            invariant_profile_count += 1
            invariant_field_counts.update(active)
        repeated[text_hash(source)].add(korean)
        repeated_coordinates[text_hash(source)].append(coordinate)
    conflicts = {key: values for key, values in repeated.items() if len(values) != 1}
    if conflicts:
        first = next(iter(conflicts))
        raise BuildError(
            "repeated JP source translation conflict: "
            f"{len(conflicts)} at {repeated_coordinates[first][:5]}"
        )

    stats = {
        "origin_counts": dict(sorted(Counter(origins.values()).items())),
        "invariant_profile_count": invariant_profile_count,
        "invariant_field_counts": dict(sorted(invariant_field_counts.items())),
        "unique_source_hash_count": len(repeated),
        "repeated_source_group_count": sum(
            len(coordinates) > 1 for coordinates in repeated_coordinates.values()
        ),
    }
    return translations, origins, stats


def make_overlay(
    private_entries: list[dict[str, Any]],
    translations: dict[tuple[int, int, int], str],
    stats: dict[str, Any],
) -> dict[str, Any]:
    by_coordinate = {tuple(entry["coordinate"]): entry for entry in private_entries}
    entries = []
    for coordinate in sorted(translations):
        source = by_coordinate[coordinate]["jp"]
        entries.append(
            {
                "block_id": coordinate[0],
                "record_id": coordinate[1],
                "literal_id": coordinate[2],
                "source_jp_utf16le_sha256": text_hash(source),
                "ko": translations[coordinate],
            }
        )
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msggame_ko_pk_jp_native_wave07_j05_681",
        "resource": steam.RESOURCE,
        "base_language": "JP",
        "entry_count": len(entries),
        "coordinates_sha256": COORDINATES_SHA256,
        "defaults": {"status": "translated_context_reviewed"},
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": {
            key: steam.STOCK_PIN[key]
            for key in (
                "packed_size",
                "packed_sha256",
                "raw_size",
                "raw_sha256",
                "record_count",
                "literal_count",
            )
        },
        "translation_provenance": {
            "batch_id": BATCH_ID,
            "kind": "parallel_human_context_translation_with_verified_support_merge",
            "private_context_committed": False,
            "source_language": "JP",
            "target_language": "KO",
            "origin_counts": stats["origin_counts"],
        },
        "quality": {
            "context_review_status": "PASS",
            "invariant_status": "PASS",
            "repeated_source_consistency": "PASS",
            "source_leak_status": "PASS",
        },
        "entries": entries,
    }


def validate_overlay_with_stock(
    overlay_path: Path,
    stock_path: Path,
) -> tuple[dict[str, Any], dict[tuple[int, int, int], str]]:
    stock_blob = stock_path.read_bytes()
    stock = steam.stock_context(stock_blob)
    replacements, _row = steam.load_overlay(
        overlay_path, None, ENTRY_COUNT, stock
    )
    return stock, replacements


def build_candidate(
    stock_path: Path,
    wave_overlay: Path,
) -> tuple[bytes, dict[str, Any]]:
    stock_blob = stock_path.read_bytes()
    stock = steam.stock_context(stock_blob)
    combined: dict[tuple[int, int, int], str] = {}
    overlay_rows: list[dict[str, Any]] = []
    specs = [
        (row["path"], row["sha256"], row["entry_count"])
        for row in steam.DEFAULT_OVERLAYS
    ] + [
        (J02_OVERLAY, J02_OVERLAY_SHA256, J02_ENTRY_COUNT),
        (wave_overlay, None, ENTRY_COUNT),
    ]
    for path, expected_hash, expected_count in specs:
        current, row = steam.load_overlay(
            Path(path), expected_hash, expected_count, stock
        )
        overlap = set(combined) & set(current)
        if overlap:
            raise BuildError(f"foundation/wave overlap at {sorted(overlap)[:3]}")
        combined.update(current)
        overlay_rows.append(row)
    if len(combined) != EXPECTED_COMBINED:
        raise BuildError(f"combined translation count changed: {len(combined)}")

    candidate = msggame.rebuild_packed_with_literals(stock_blob, combined)
    _header, candidate_raw = decompress_wrapper(candidate)
    parsed = msggame.parse_packed_msggame(candidate)
    literals = steam.literal_map(parsed.archive)
    if set(literals) != set(stock["literals"]):
        raise BuildError("candidate literal coordinate set changed")
    if steam.sha256(steam.normalized_structure_raw(parsed.archive)) != stock[
        "normalized_structure_sha256"
    ]:
        raise BuildError("candidate non-literal structure changed")
    for coordinate, source_literal in stock["literals"].items():
        expected = combined.get(coordinate, source_literal.text)
        if literals[coordinate].text != expected:
            raise BuildError(f"candidate literal mismatch at {coordinate}")
    remaining = sum(steam.has_source_script(literal.text) for literal in literals.values())
    if remaining != EXPECTED_REMAINING:
        raise BuildError(f"remaining semantic count changed: {remaining}")
    return candidate, {
        "packed_size": len(candidate),
        "packed_sha256": sha256(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256(candidate_raw),
        "applied_entry_count": len(combined),
        "remaining_jp_semantic_count": remaining,
        "overlay_count": len(overlay_rows),
        "non_literal_structure_preserved": True,
        "literal_coordinate_set_preserved": True,
        "steam_stock_written": False,
    }


def public_source_scan() -> list[str]:
    failures: list[str] = []
    for path in sorted(WORKSTREAM.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() not in {".py", ".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        if SOURCE_SCRIPT_RE.search(text):
            failures.append(path.relative_to(WORKSTREAM).as_posix())
    return failures


def command_build(args: argparse.Namespace) -> int:
    private_entries, private_map = load_private(args.private_context)
    support = load_block15_support(args.block15_support, private_map)
    translations, origins, stats = assemble(private_entries, support)
    overlay = make_overlay(private_entries, translations, stats)
    overlay_meta = write_json(OVERLAY_PATH, overlay)
    stock, replacements = validate_overlay_with_stock(OVERLAY_PATH, args.stock)
    if len(replacements) != ENTRY_COUNT:
        raise BuildError("Steam loader did not accept all wave entries")

    with tempfile.TemporaryDirectory(prefix="wave07_j05_ab_", dir=REPO_ROOT / "tmp"):
        first, first_meta = build_candidate(args.stock, OVERLAY_PATH)
        second, second_meta = build_candidate(args.stock, OVERLAY_PATH)
    if first != second or first_meta != second_meta:
        raise BuildError("candidate A/B build is not deterministic")

    validation = {
        "schema": VALIDATION_SCHEMA,
        "batch_id": BATCH_ID,
        "resource": steam.RESOURCE,
        "base_language": "JP",
        "entry_count": ENTRY_COUNT,
        "coordinates_sha256": COORDINATES_SHA256,
        "unique_source_hash_count": stats["unique_source_hash_count"],
        "repeated_source_group_count": stats["repeated_source_group_count"],
        "source_invariant_profile_count": stats["invariant_profile_count"],
        "source_invariant_field_counts": stats["invariant_field_counts"],
        "overlay": overlay_meta,
        "candidate": first_meta,
        "checks": {
            "exact_partition_coverage": "PASS",
            "steam_jp_source_hashes": "PASS",
            "literal_invariants": "PASS",
            "repeated_source_consistency": "PASS",
            "public_source_scan": "PASS",
            "foundation_disjoint": "PASS",
            "candidate_structure": "PASS",
            "deterministic_ab": "PASS",
            "steam_game_file_written": False,
        },
    }
    validation_meta = write_json(VALIDATION_PATH, validation)
    review = {
        "schema": REVIEW_SCHEMA,
        "batch_id": BATCH_ID,
        "entry_count": ENTRY_COUNT,
        "review_scope": "all_assigned_coordinates_in_record_context",
        "status": "PASS",
        "origin_counts": stats["origin_counts"],
        "manual_record_count": len(MANUAL_RECORDS),
        "manual_coordinate_count": NON15_ENTRY_COUNT,
        "verified_support_coordinate_count": BLOCK15_ENTRY_COUNT,
        "block15_support_sha256": BLOCK15_SUPPORT_SHA256,
        "commercial_source_text_in_public_artifacts": False,
        "private_context_committed": False,
        "evidence": {
            "overlay_sha256": overlay_meta["sha256"],
            "validation_sha256": validation_meta["sha256"],
            "reviewed_coordinate_count": len(origins),
        },
    }
    write_json(REVIEW_PATH, review)

    failures = public_source_scan()
    if failures:
        raise BuildError(f"public source scan failed: {failures}")
    if args.output_root is not None:
        output = args.output_root.resolve()
        tmp_root = (REPO_ROOT / "tmp").resolve()
        if output == tmp_root or tmp_root not in output.parents:
            raise BuildError("candidate output must be under repository tmp")
        if output.exists():
            if any(output.iterdir()):
                raise BuildError("candidate output must be absent or empty")
        target = output / "private" / "candidate" / Path(steam.RESOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(first)
        write_json(output / "build_manifest.json", first_meta)
    if args.stock.read_bytes() != stock["packed"]:
        raise BuildError("Steam stock changed during offline build")
    print(f"overlay={OVERLAY_PATH}")
    print(f"overlay_sha256={overlay_meta['sha256']}")
    print(f"entries={ENTRY_COUNT}")
    print(f"candidate_sha256={first_meta['packed_sha256']}")
    print(f"remaining_jp_semantic={EXPECTED_REMAINING}")
    print("steam_stock_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    private_entries, private_map = load_private(args.private_context)
    support = load_block15_support(args.block15_support, private_map)
    translations, _origins, stats = assemble(private_entries, support)
    expected = json_bytes(make_overlay(private_entries, translations, stats))
    actual = OVERLAY_PATH.read_bytes()
    if actual != expected:
        raise BuildError("tracked overlay is not the deterministic builder output")
    _stock, replacements = validate_overlay_with_stock(OVERLAY_PATH, args.stock)
    if len(replacements) != ENTRY_COUNT:
        raise BuildError("Steam loader entry count mismatch")
    failures = public_source_scan()
    if failures:
        raise BuildError(f"public source scan failed: {failures}")
    print(f"overlay_sha256={sha256(actual)}")
    print(f"entries={len(replacements)}")
    print("deterministic_overlay=PASS")
    print("steam_jp_guard=PASS")
    print("public_source_scan=PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("build", command_build), ("verify", command_verify)):
        current = sub.add_parser(name)
        current.add_argument("--private-context", type=Path, default=PRIVATE_CONTEXT)
        current.add_argument("--block15-support", type=Path, default=BLOCK15_SUPPORT)
        current.add_argument("--stock", type=Path, default=steam.DEFAULT_STOCK)
        if name == "build":
            current.add_argument("--output-root", type=Path)
        current.set_defaults(handler=handler)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (BuildError, steam.BuildError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
