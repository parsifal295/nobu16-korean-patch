#!/usr/bin/env python3
"""Build a source-free Switch v1.1 Korean-to-PK msggame transfer overlay.

The third-party Switch asset is read directly from its release ZIP and is
never extracted into the repository.  Its decompressed payload is two bytes
short of four-byte alignment only after its final block; the reader appends
those two zero bytes in memory solely to parse the table.  All output
reconstruction targets the PC PK/SC source, never the Switch asset.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path[:0] = [str(MSGGAME_ROOT), str(TOOLS_ROOT)]

from build_common_message_overlay import invariant_mismatches, message_invariants  # noqa: E402
from build_literal_overlay import OVERLAY_SCHEMA, apply_overlay_blob  # noqa: E402
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameArchive,
    MsgGameFormatError,
    MsgGameRecord,
    iter_literals,
    parse_packed_msggame,
    parse_raw_msggame,
    parse_record_literals,
    rebuild_raw_msggame,
    sha256,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


BATCH_ID = "switch_v11_pk_msggame_exact_source_hash.v0.1"
OVERLAY_NAME = "msggame_ko_switch_v11_exact_source_hash.v0.1.json"
EVIDENCE_NAME = "switch_v11_pk_msggame_alignment_evidence.v0.1.json"
REVIEW_NAME = "switch_v11_pk_msggame_review_index.v0.1.json"
VALIDATION_NAME = "switch_v11_pk_msggame_validation.v0.1.json"
RESOURCE = "MSG_PK/SC/msggame.bin"
PROGRESS_RESOURCE = RESOURCE

SWITCH_ZIP_RELATIVE = Path("tmp/third_party_switch_v11/NobunagaShinsei_KoreanPatch_v1.1.zip")
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/msggame.bin"
PROGRESS_RELATIVE = Path("data/public/translation_progress.v0.1.json")
LOCAL_PK_OVERLAY_GLOB = "workstreams/msggame/public/msggame_ko_system_messages_*.json"
# The final catalog deliberately registers this batch so the progress report can
# count it.  It is not a *prior* translation, however: including it while this
# generator selects candidates would make every one of its own coordinates look
# already translated.  Keep the exact registration path pinned and validate it
# separately before excluding it from the prior-existing union.
SELF_OVERLAY_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()

SOURCE_PROVENANCE = {
    "author": "snake7594",
    "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
    "release_tag": "v1.1",
    "release_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1",
    "asset_name": "NobunagaShinsei_KoreanPatch_v1.1.zip",
    "asset_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/download/v1.1/NobunagaShinsei_KoreanPatch_v1.1.zip",
    "zip_sha256": "931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6",
}

SOURCE_PINS = {
    "switch_zip": {
        "size": 73040529,
        "sha256": SOURCE_PROVENANCE["zip_sha256"],
    },
    "switch_member": {
        "packed_size": 487964,
        "packed_sha256": "89CC6412B8548CA5CCADB6A2AB406D0EC4ED3ABCEBB8B703C4E324C0EAAB2F67",
        "raw_size": 0x16DD42,
        "raw_sha256": "759C32FD7EFAABF70C6B82C45E21AB090D6B80CF88827247370AED9F163D6501",
        "padded_raw_size": 0x16DD44,
        "padded_raw_sha256": "63C95026686EC3BBFAED37700209B3440DE6BBAE52925D2C723DBFD64FB34523",
        "block_count": 18,
        "record_count": 19152,
        "literal_slot_count": 24262,
    },
    "base_jp": {
        "logical_path": "MSG/JP/msggame.bin",
        "packed_size": 610163,
        "packed_sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        "raw_size": 1337548,
        "raw_sha256": "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38",
        "block_count": 18,
        "record_count": 19152,
        "literal_slot_count": 24262,
    },
    "pk_jp": {
        "logical_path": "MSG_PK/JP/msggame.bin",
        "packed_size": 709290,
        "packed_sha256": "0FB9EA3B4817D208C65F587AF1F57A5BB82106367314801A13C9A534ECC47CD8",
        "raw_size": 1571384,
        "raw_sha256": "F00C897353C3C0084BFBFC5ED781C467945C82708F28A6D57BA0CC2710976D57",
        "block_count": 18,
        "record_count": 21581,
        "literal_slot_count": 29149,
    },
    "pk_sc": {
        "logical_path": RESOURCE,
        "packed_size": 529419,
        "packed_sha256": "BD7B33FCC7495B855B0828C7FE4E5F7ADB2DE656A9B12E20259750F94EE665D6",
        "raw_size": 1077200,
        "raw_sha256": "1958B2B801D37186D478284EA0E29CA96D8DA2BC087D6BEB74A4139EF01C11CE",
        "block_count": 18,
        "record_count": 21581,
        "literal_slot_count": 25598,
    },
}

# These pins intentionally bind this migration to the current translation
# catalog.  A later catalog change should produce a new migration batch rather
# than silently rewrite this one.
EXPECTED_COUNTS = {
    "existing_overlay_coordinate_union": 3300,
    "global_strict_candidates": 8375,
    "cjk_or_kana_excluded": 154,
    "existing_overlay_overlap": 2204,
    "both_cjk_or_kana_and_existing": 1,
    "selected": 6018,
}


class SwitchTransferError(ValueError):
    """Raised for an unsafe or non-reproducible third-party transfer."""


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.relative_to(path.parents[1]).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def literal_map(archive: MsgGameArchive) -> dict[tuple[int, int, int], Any]:
    return {
        (literal.block_id, literal.record_id, literal.literal_id): literal
        for literal in iter_literals(archive)
    }


def record_map(archive: MsgGameArchive) -> dict[tuple[int, int], MsgGameRecord]:
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def record_skeleton(record: MsgGameRecord) -> bytes:
    """Return opaque record bytecode with literal payloads removed."""

    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        output.extend(record.data[cursor : literal.marker_offset])
        output.extend(LITERAL_START)
        output.extend(LITERAL_END)
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


def is_visible_translation_candidate(text: str) -> bool:
    return any(character.isprintable() and not character.isspace() for character in text)


def has_hangul_syllable(text: str) -> bool:
    return any(0xAC00 <= ord(character) <= 0xD7A3 for character in text)


def has_semantic_text(text: str) -> bool:
    """Require actual visible content in addition to a Korean syllable check."""

    return is_visible_translation_candidate(text)


def script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": sum(
            (0x3400 <= ord(character) <= 0x4DBF)
            or (0x4E00 <= ord(character) <= 0x9FFF)
            or (0xF900 <= ord(character) <= 0xFAFF)
            for character in text
        ),
        "kana_count": sum(
            (0x3040 <= ord(character) <= 0x30FF)
            or (0x31F0 <= ord(character) <= 0x31FF)
            for character in text
        ),
    }


def source_structure(text: str) -> dict[str, Any]:
    invariant = message_invariants(text)
    return {
        "utf16_code_units": len(text.encode("utf-16-le")) // 2,
        "printf_tokens": invariant["printf"],
        "unknown_percent_count": invariant["unknown_percent_count"],
        "escape_sequences": invariant["esc"],
        "control_codepoints": invariant["controls"],
        "line_breaks": invariant["line_breaks"],
        "private_use_codepoints": invariant["pua"],
        "leading_whitespace_utf16le_sha256": text_hash(invariant["leading_whitespace"]),
        "trailing_whitespace_utf16le_sha256": text_hash(invariant["trailing_whitespace"]),
    }


def archive_summary(packed: bytes, raw: bytes, archive: MsgGameArchive) -> dict[str, Any]:
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "block_count": len(archive.blocks),
        "record_count": archive.record_count,
        "literal_slot_count": len(literal_map(archive)),
        "block_record_counts": [len(block.records) for block in archive.blocks],
    }


def require_pin(label: str, actual: dict[str, Any], expected: dict[str, Any]) -> None:
    for key, value in expected.items():
        if key == "logical_path":
            continue
        if actual.get(key) != value:
            raise SwitchTransferError(
                f"{label} pin mismatch for {key}: expected {value!r}, got {actual.get(key)!r}"
            )


def load_standard_source(path: Path, label: str) -> dict[str, Any]:
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    archive = parse_raw_msggame(raw)
    if rebuild_raw_msggame(archive) != raw:
        raise SwitchTransferError(f"{label} raw parse/rebuild is not byte-identical")
    summary = archive_summary(packed, raw, archive)
    require_pin(label, summary, SOURCE_PINS[label])
    return {
        "path": path,
        "packed": packed,
        "raw": raw,
        "archive": archive,
        "summary": summary,
    }


def load_switch_member(zip_path: Path) -> dict[str, Any]:
    zip_before = zip_path.read_bytes()
    zip_summary = {"size": len(zip_before), "sha256": sha256(zip_before)}
    require_pin("switch_zip", zip_summary, SOURCE_PINS["switch_zip"])
    with zipfile.ZipFile(zip_path) as archive:
        matches = [entry for entry in archive.infolist() if entry.filename == SWITCH_MEMBER]
        if len(matches) != 1:
            raise SwitchTransferError(f"Switch ZIP member count for msggame is {len(matches)}, expected 1")
        packed = archive.read(matches[0])

    _header, raw = decompress_wrapper(packed)
    if len(raw) != SOURCE_PINS["switch_member"]["raw_size"]:
        raise SwitchTransferError("Switch decompressed raw size changed")
    try:
        parse_raw_msggame(raw)
    except MsgGameFormatError:
        pass
    else:
        raise SwitchTransferError("Switch raw unexpectedly parsed without its required alignment pad")

    padding_count = (-len(raw)) % 4
    if padding_count != 2:
        raise SwitchTransferError(f"Switch raw needs {padding_count} alignment bytes, expected 2")
    padded_raw = raw + (b"\0" * padding_count)
    parsed = parse_raw_msggame(padded_raw)
    final_end = parsed.blocks[-1].offset + parsed.blocks[-1].size
    if final_end != len(raw) or parsed.blocks[-1].gap_after != b"\0\0":
        raise SwitchTransferError("Switch final block does not end at the unpadded raw boundary")
    if rebuild_raw_msggame(parsed) != padded_raw:
        raise SwitchTransferError("in-memory padded Switch parse/rebuild is not byte-identical")

    summary = archive_summary(packed, raw, parsed)
    summary["padded_raw_size"] = len(padded_raw)
    summary["padded_raw_sha256"] = sha256(padded_raw)
    require_pin("switch_member", summary, SOURCE_PINS["switch_member"])
    if zip_path.read_bytes() != zip_before:
        raise SwitchTransferError("Switch ZIP changed during read-only load")
    return {
        "zip_path": zip_path,
        "packed": packed,
        "raw": raw,
        "padded_raw": padded_raw,
        "archive": parsed,
        "summary": summary,
        "padding_count": padding_count,
        "final_block_end": final_end,
    }


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SwitchTransferError(f"JSON root must be an object: {path}")
    return value


def validate_final_overlay_registration(
    overlay_globs: list[str], progress_paths: list[Path]
) -> dict[str, Any]:
    """Require the final progress catalog to list this output exactly once.

    The resulting overlay is intentionally visible to progress reporting, but
    must be excluded from the source set used for this batch's selection.  This
    guard makes an accidental missing, duplicate, or wildcard self-reference a
    deterministic build failure instead of silently changing the 6,018-entry
    migration result.
    """

    configured_reference_count = sum(pattern == SELF_OVERLAY_RELATIVE for pattern in overlay_globs)
    if configured_reference_count != 1:
        raise SwitchTransferError(
            "final progress catalog must register the Switch msggame overlay exactly once: "
            f"expected {SELF_OVERLAY_RELATIVE!r}, got {configured_reference_count} references"
        )

    expected_path = (REPO_ROOT / SELF_OVERLAY_RELATIVE).resolve()
    resolved_self_paths = [path for path in progress_paths if path.resolve() == expected_path]
    if len(resolved_self_paths) != 1:
        raise SwitchTransferError(
            "final progress catalog self overlay must resolve exactly once: "
            f"expected {SELF_OVERLAY_RELATIVE!r}, got {len(resolved_self_paths)} paths"
        )
    return {
        "expected_relative_path": SELF_OVERLAY_RELATIVE,
        "configured_reference_count": configured_reference_count,
        "resolved_reference_count": len(resolved_self_paths),
        "resolved_paths": [path.relative_to(REPO_ROOT).as_posix() for path in resolved_self_paths],
        "excluded_from_prior_existing_coordinates": True,
    }


def collect_existing_pk_coordinates(progress_path: Path) -> dict[str, Any]:
    progress = read_json(progress_path)
    resources = progress.get("resources")
    if not isinstance(resources, list):
        raise SwitchTransferError("translation progress resources is not an array")
    matches = [item for item in resources if item.get("path") == PROGRESS_RESOURCE]
    if len(matches) != 1:
        raise SwitchTransferError("translation progress does not contain exactly one PK msggame resource")
    overlay_globs = matches[0].get("overlay_globs")
    if not isinstance(overlay_globs, list) or not all(isinstance(item, str) for item in overlay_globs):
        raise SwitchTransferError("PK msggame overlay_globs is invalid")

    progress_paths: list[Path] = []
    for pattern in overlay_globs:
        found = sorted(REPO_ROOT.glob(pattern))
        if len(found) != 1:
            raise SwitchTransferError(
                f"progress glob {pattern!r} resolved to {len(found)} files, expected 1"
            )
        progress_paths.extend(found)

    self_registration = validate_final_overlay_registration(overlay_globs, progress_paths)
    self_path = (REPO_ROOT / SELF_OVERLAY_RELATIVE).resolve()
    prior_progress_paths = [path for path in progress_paths if path.resolve() != self_path]

    # The worktree can contain the immediately completed v0.22 before a global
    # progress refresh.  Include this conservative local union so a transfer
    # cannot race that catalog update.
    local_paths = sorted(REPO_ROOT.glob(LOCAL_PK_OVERLAY_GLOB))
    prior_local_paths = [path for path in local_paths if path.resolve() != self_path]
    all_paths = sorted({*prior_progress_paths, *prior_local_paths})
    coordinates: set[tuple[int, int, int]] = set()
    for path in all_paths:
        overlay = read_json(path)
        if overlay.get("resource") != RESOURCE:
            raise SwitchTransferError(f"existing overlay has unexpected resource: {path}")
        entries = overlay.get("entries")
        if not isinstance(entries, list):
            raise SwitchTransferError(f"existing overlay entries is invalid: {path}")
        for entry in entries:
            if not isinstance(entry, dict):
                raise SwitchTransferError(f"existing overlay entry is invalid: {path}")
            coordinate = (entry.get("block_id"), entry.get("record_id"), entry.get("literal_id"))
            if any(isinstance(value, bool) or not isinstance(value, int) for value in coordinate):
                raise SwitchTransferError(f"existing overlay coordinate is invalid: {path}")
            coordinates.add(coordinate)
    return {
        "coordinates": coordinates,
        "progress_sha256": sha256(progress_path.read_bytes()),
        "progress_overlay_globs": overlay_globs,
        "progress_paths": [path.relative_to(REPO_ROOT).as_posix() for path in progress_paths],
        "prior_progress_paths": [path.relative_to(REPO_ROOT).as_posix() for path in prior_progress_paths],
        "local_discovery_glob": LOCAL_PK_OVERLAY_GLOB,
        "local_paths": [path.relative_to(REPO_ROOT).as_posix() for path in local_paths],
        "prior_local_paths": [path.relative_to(REPO_ROOT).as_posix() for path in prior_local_paths],
        "all_paths": [path.relative_to(REPO_ROOT).as_posix() for path in all_paths],
        "self_overlay_registration": self_registration,
    }


def build_switch_value_map(
    base_literals: dict[tuple[int, int, int], Any],
    switch_literals: dict[tuple[int, int, int], Any],
    base_records: dict[tuple[int, int], MsgGameRecord],
    switch_records: dict[tuple[int, int], MsgGameRecord],
) -> tuple[dict[str, set[str]], dict[str, int]]:
    if set(base_records) != set(switch_records):
        raise SwitchTransferError("base JP and Switch record coordinates differ")
    if set(base_literals) != set(switch_literals):
        raise SwitchTransferError("base JP and Switch literal coordinates differ")
    for coordinate in sorted(base_records):
        if record_skeleton(base_records[coordinate]) != record_skeleton(switch_records[coordinate]):
            raise SwitchTransferError(f"base JP and Switch opaque structure differ at {coordinate}")

    values: dict[str, set[str]] = defaultdict(set)
    occurrences: Counter[str] = Counter()
    for coordinate in sorted(base_literals):
        base_literal = base_literals[coordinate]
        switch_literal = switch_literals[coordinate]
        source_hash = text_hash(base_literal.text)
        values[source_hash].add(switch_literal.text)
        occurrences[source_hash] += 1
    if not values:
        raise SwitchTransferError("Switch source hash map is empty")
    return dict(values), dict(occurrences)


def select_transfers(
    *,
    base_literals: dict[tuple[int, int, int], Any],
    switch_literals: dict[tuple[int, int, int], Any],
    pk_jp_literals: dict[tuple[int, int, int], Any],
    pk_sc_literals: dict[tuple[int, int, int], Any],
    switch_values_by_source_hash: dict[str, set[str]],
    source_occurrences: dict[str, int],
    existing_coordinates: set[tuple[int, int, int]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    counters: Counter[str] = Counter()
    selected: list[dict[str, Any]] = []
    for coordinate in sorted(pk_jp_literals):
        pk_jp = pk_jp_literals[coordinate]
        pk_sc = pk_sc_literals.get(coordinate)
        if pk_sc is None:
            counters["missing_pk_sc_literal"] += 1
            continue
        source_hash = text_hash(pk_jp.text)
        values = switch_values_by_source_hash.get(source_hash)
        if values is None:
            counters["no_base_jp_source_hash"] += 1
            continue
        if len(values) != 1:
            counters["non_unique_switch_ko_source_set"] += 1
            continue
        ko = next(iter(values))
        if ko == pk_jp.text:
            counters["switch_ko_equals_pk_jp"] += 1
            continue
        if not has_semantic_text(ko):
            counters["switch_ko_not_semantic"] += 1
            continue
        if not has_hangul_syllable(ko):
            counters["switch_ko_has_no_hangul"] += 1
            continue
        if not is_visible_translation_candidate(pk_sc.text):
            counters["pk_sc_not_visible"] += 1
            continue
        if invariant_mismatches(pk_sc.text, ko):
            counters["pk_sc_invariant_mismatch"] += 1
            continue

        counters["global_strict_candidates"] += 1
        banned = script_counts(ko)
        existing = coordinate in existing_coordinates
        if banned != {"cjk_unified_count": 0, "kana_count": 0}:
            counters["cjk_or_kana_excluded"] += 1
        if existing:
            counters["existing_overlay_overlap"] += 1
        if existing and banned != {"cjk_unified_count": 0, "kana_count": 0}:
            counters["both_cjk_or_kana_and_existing"] += 1
        if banned != {"cjk_unified_count": 0, "kana_count": 0} or existing:
            continue

        direct = (
            coordinate in base_literals
            and base_literals[coordinate].text == pk_jp.text
            and switch_literals[coordinate].text == ko
        )
        mode = "same_coordinate" if direct else "source_hash_transfer"
        counters[mode] += 1
        selected.append(
            {
                "coordinate": coordinate,
                "ko": ko,
                "pk_jp_source_hash": source_hash,
                "pk_sc_source_hash": text_hash(pk_sc.text),
                "switch_ko_hash": text_hash(ko),
                "switch_source_occurrence_count": source_occurrences[source_hash],
                "transfer_mode": mode,
                "pk_sc_structure": source_structure(pk_sc.text),
            }
        )
    if not selected:
        raise SwitchTransferError("strict Switch transfer selection is empty")
    return selected, dict(counters)


def assert_expected_counts(counters: dict[str, int], existing_coordinates: set[tuple[int, int, int]], selected: list[dict[str, Any]]) -> None:
    actual = {
        "existing_overlay_coordinate_union": len(existing_coordinates),
        "global_strict_candidates": counters.get("global_strict_candidates", 0),
        "cjk_or_kana_excluded": counters.get("cjk_or_kana_excluded", 0),
        "existing_overlay_overlap": counters.get("existing_overlay_overlap", 0),
        "both_cjk_or_kana_and_existing": counters.get("both_cjk_or_kana_and_existing", 0),
        "selected": len(selected),
    }
    if actual != EXPECTED_COUNTS:
        raise SwitchTransferError(
            f"strict transfer selection changed: expected {EXPECTED_COUNTS!r}, got {actual!r}"
        )


def assert_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = script_counts(path.read_text(encoding="utf-8"))
        result[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise SwitchTransferError(f"source script text leaked into public artifact: {path}")
    return result


def build(args: argparse.Namespace) -> dict[str, Any]:
    switch_zip = args.switch_zip.resolve()
    base_jp_path = args.base_jp.resolve()
    pk_jp_path = args.pk_jp.resolve()
    pk_sc_path = args.pk_sc.resolve()
    progress_path = args.progress.resolve()
    sources_before = {
        "switch_zip": sha256(switch_zip.read_bytes()),
        "base_jp": sha256(base_jp_path.read_bytes()),
        "pk_jp": sha256(pk_jp_path.read_bytes()),
        "pk_sc": sha256(pk_sc_path.read_bytes()),
        "progress": sha256(progress_path.read_bytes()),
    }

    switch = load_switch_member(switch_zip)
    base_jp = load_standard_source(base_jp_path, "base_jp")
    pk_jp = load_standard_source(pk_jp_path, "pk_jp")
    pk_sc = load_standard_source(pk_sc_path, "pk_sc")
    existing = collect_existing_pk_coordinates(progress_path)

    base_literals = literal_map(base_jp["archive"])
    switch_literals = literal_map(switch["archive"])
    pk_jp_literals = literal_map(pk_jp["archive"])
    pk_sc_literals = literal_map(pk_sc["archive"])
    base_records = record_map(base_jp["archive"])
    switch_records = record_map(switch["archive"])
    pk_sc_records = record_map(pk_sc["archive"])
    switch_values, source_occurrences = build_switch_value_map(
        base_literals, switch_literals, base_records, switch_records
    )
    selected, counters = select_transfers(
        base_literals=base_literals,
        switch_literals=switch_literals,
        pk_jp_literals=pk_jp_literals,
        pk_sc_literals=pk_sc_literals,
        switch_values_by_source_hash=switch_values,
        source_occurrences=source_occurrences,
        existing_coordinates=existing["coordinates"],
    )
    assert_expected_counts(counters, existing["coordinates"], selected)
    selected_coordinates = [item["coordinate"] for item in selected]
    if len(selected_coordinates) != len(set(selected_coordinates)):
        raise SwitchTransferError("selected transfer coordinates are not unique")
    if set(selected_coordinates) & existing["coordinates"]:
        raise SwitchTransferError("selected transfer overlaps an existing PK msggame overlay")

    overlay_entries = [
        {
            "block_id": coordinate[0],
            "record_id": coordinate[1],
            "literal_id": coordinate[2],
            "source_sc_utf16le_sha256": item["pk_sc_source_hash"],
            "ko": item["ko"],
        }
        for item in selected
        for coordinate in [item["coordinate"]]
    ]
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "migration_provenance": {
            "kind": "third_party_switch_v11_exact_source_hash_transfer",
            "author": SOURCE_PROVENANCE["author"],
            "repository_url": SOURCE_PROVENANCE["repository_url"],
            "release_tag": SOURCE_PROVENANCE["release_tag"],
            "asset_sha256": SOURCE_PROVENANCE["zip_sha256"],
            "source_text_embedded": False,
        },
        "stock_sc": {
            "packed_size": len(pk_sc["packed"]),
            "packed_sha256": sha256(pk_sc["packed"]),
            "raw_size": len(pk_sc["raw"]),
            "raw_sha256": sha256(pk_sc["raw"]),
            "record_count": pk_sc["archive"].record_count,
            "literal_slot_count": len(pk_sc_literals),
        },
        "entries": overlay_entries,
    }

    evidence_entries = []
    review_entries = []
    for item in selected:
        block_id, record_id, literal_id = item["coordinate"]
        source_hash = item["pk_jp_source_hash"]
        evidence_entries.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "literal_id": literal_id,
                "base_jp_utf16le_sha256": source_hash,
                "pk_jp_utf16le_sha256": source_hash,
                "pk_sc_utf16le_sha256": item["pk_sc_source_hash"],
                "switch_ko_utf16le_sha256": item["switch_ko_hash"],
                "switch_source_occurrence_count": item["switch_source_occurrence_count"],
                "switch_source_value_set_count": 1,
                "transfer_mode": item["transfer_mode"],
                "pk_sc_structure": item["pk_sc_structure"],
                "pk_sc_record_literal_count": len(
                    parse_record_literals(pk_sc_records[(block_id, record_id)])
                ),
                "cross_coordinate_source_hash_match": item["transfer_mode"] == "source_hash_transfer",
            }
        )
        flags = ["third_party_source_hash_transfer", "runtime_line_wrap_review"]
        if item["transfer_mode"] == "source_hash_transfer":
            flags.append("cross_coordinate_same_jp_hash_review")
        if evidence_entries[-1]["pk_sc_record_literal_count"] > 1:
            flags.append("runtime_dynamic_join_review")
        review_entries.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "literal_id": literal_id,
                "status": "translated",
                "translation_origin": "third_party_switch_v11_exact_source_hash_transfer",
                "automated_draft": False,
                "human_review_required": True,
                "runtime_reviewed": False,
                "transfer_mode": item["transfer_mode"],
                "uncertainty_flags": flags,
            }
        )

    source_hash_group_counts = {
        "base_jp_unique_source_hashes": len(switch_values),
        "single_switch_ko_value_sets": sum(len(values) == 1 for values in switch_values.values()),
        "ambiguous_switch_ko_value_sets": sum(len(values) != 1 for values in switch_values.values()),
    }
    selection_summary = {
        **EXPECTED_COUNTS,
        "same_coordinate": counters.get("same_coordinate", 0),
        "source_hash_transfer": counters.get("source_hash_transfer", 0),
        "missing_pk_sc_literal": counters.get("missing_pk_sc_literal", 0),
        "no_base_jp_source_hash": counters.get("no_base_jp_source_hash", 0),
        "non_unique_switch_ko_source_set": counters.get("non_unique_switch_ko_source_set", 0),
        "switch_ko_equals_pk_jp": counters.get("switch_ko_equals_pk_jp", 0),
        "switch_ko_not_semantic": counters.get("switch_ko_not_semantic", 0),
        "switch_ko_has_no_hangul": counters.get("switch_ko_has_no_hangul", 0),
        "pk_sc_not_visible": counters.get("pk_sc_not_visible", 0),
        "pk_sc_invariant_mismatch": counters.get("pk_sc_invariant_mismatch", 0),
    }
    evidence = {
        "schema": "nobu16.kr.switch-msggame-v11-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "provenance": SOURCE_PROVENANCE,
        "switch_member": {
            "zip_member": SWITCH_MEMBER,
            **switch["summary"],
            "in_memory_alignment_padding_bytes": switch["padding_count"],
            "unmodified_raw_final_block_end": switch["final_block_end"],
            "source_file_written": False,
        },
        "pc_sources": {
            "base_jp": {"logical_path": SOURCE_PINS["base_jp"]["logical_path"], **base_jp["summary"]},
            "pk_jp": {"logical_path": SOURCE_PINS["pk_jp"]["logical_path"], **pk_jp["summary"]},
            "pk_sc": {"logical_path": SOURCE_PINS["pk_sc"]["logical_path"], **pk_sc["summary"]},
        },
        "base_switch_structure": {
            "record_coordinates_identical": True,
            "literal_coordinates_identical": True,
            "all_record_skeletons_identical": True,
            "raw_padding_is_memory_only": True,
        },
        "exact_source_hash_mapping": {
            "basis": "base_jp_utf16le_sha256_to_complete_switch_ko_value_set",
            "same_coordinate_equality_required_only_for_same_coordinate_mode": True,
            "pk_target_lookup": "pk_jp_utf16le_sha256",
            **source_hash_group_counts,
        },
        "existing_overlay_exclusion": {
            "progress_path": progress_path.relative_to(REPO_ROOT).as_posix(),
            "progress_sha256": existing["progress_sha256"],
            "progress_overlay_globs": existing["progress_overlay_globs"],
            "resolved_progress_paths": existing["progress_paths"],
            "resolved_prior_progress_paths": existing["prior_progress_paths"],
            "local_discovery_glob": existing["local_discovery_glob"],
            "resolved_local_paths": existing["local_paths"],
            "resolved_prior_local_paths": existing["prior_local_paths"],
            "resolved_all_paths": existing["all_paths"],
            "self_overlay_registration": existing["self_overlay_registration"],
        },
        "selection": selection_summary,
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msggame-v11-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "third_party_import_requires_pc_runtime_review",
        "entry_count": len(review_entries),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts = {
        "overlay": write_json(overlay_path, overlay),
        "alignment_evidence": write_json(evidence_path, evidence),
        "review_index": write_json(review_path, review),
    }
    source_free_scan = assert_source_free((overlay_path, evidence_path, review_path))

    rebuilt, binary_manifest = apply_overlay_blob(pk_sc["packed"], overlay)
    _header, target_raw = decompress_wrapper(rebuilt)
    target = parse_packed_msggame(rebuilt)
    target_literals = literal_map(target.archive)
    target_records = record_map(target.archive)
    replacements = {item["coordinate"]: item["ko"] for item in selected}
    for coordinate, replacement in replacements.items():
        if target_literals.get(coordinate) is None or target_literals[coordinate].text != replacement:
            raise SwitchTransferError(f"target literal reconstruction mismatch at {coordinate}")
    if set(target_literals) != set(pk_sc_literals):
        raise SwitchTransferError("target literal coordinates changed after PK reconstruction")
    if set(target_records) != set(pk_sc_records):
        raise SwitchTransferError("target record coordinates changed after PK reconstruction")
    if any(
        record_skeleton(pk_sc_records[key]) != record_skeleton(target_records[key])
        for key in pk_sc_records
    ):
        raise SwitchTransferError("PK reconstruction changed opaque record bytecode")
    if rebuild_raw_msggame(target.archive) != target_raw:
        raise SwitchTransferError("target PK raw parse/rebuild is not byte-identical")

    sources_after = {
        "switch_zip": sha256(switch_zip.read_bytes()),
        "base_jp": sha256(base_jp_path.read_bytes()),
        "pk_jp": sha256(pk_jp_path.read_bytes()),
        "pk_sc": sha256(pk_sc_path.read_bytes()),
        "progress": sha256(progress_path.read_bytes()),
    }
    if sources_before != sources_after:
        raise SwitchTransferError("read-only source changed during transfer build")

    validation = {
        "schema": "nobu16.kr.switch-msggame-v11-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "provenance": SOURCE_PROVENANCE,
        "selection": selection_summary,
        "source_alignment": {
            "base_switch_record_coordinates_identical": True,
            "base_switch_literal_coordinates_identical": True,
            "base_switch_record_skeletons_identical": True,
            "source_hash_value_sets_must_be_unique": True,
            "pk_sc_invariant_checks": len(selected),
            "cross_coordinate_source_hash_transfers": counters.get("source_hash_transfer", 0),
        },
        "switch_padding": {
            "original_raw_size": len(switch["raw"]),
            "original_final_block_end": switch["final_block_end"],
            "required_alignment_padding_bytes": switch["padding_count"],
            "padded_parse_raw_size": len(switch["padded_raw"]),
            "in_memory_only": True,
            "switch_source_written": False,
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "escape_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "literal_coordinate_and_record_structure",
            ],
        },
        "font_compatibility": {
            "forbidden_ranges": ["U+3400-U+4DBF", "U+4E00-U+9FFF", "U+F900-U+FAFF", "U+3040-U+30FF", "U+31F0-U+31FF"],
            "excluded_entry_count": counters.get("cjk_or_kana_excluded", 0),
            "selected_entries_with_forbidden_script": 0,
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": sha256(rebuilt),
            "target_raw_size": len(target_raw),
            "target_raw_sha256": sha256(target_raw),
            "literal_coordinates_preserved": True,
            "record_coordinates_preserved": True,
            "opaque_record_bytecode_preserved": True,
            "raw_parse_rebuild_byte_exact": True,
            "installed_game_file_written": False,
        },
        "source_free_scan": source_free_scan,
        "progress_catalog": {
            "self_overlay_registration": existing["self_overlay_registration"],
            "prior_existing_coordinate_union": len(existing["coordinates"]),
        },
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "byte_identical_pk_reconstruction_required": True,
        },
        "safety": {
            "switch_zip_modified": False,
            "switch_member_extracted_to_repository": False,
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_modified": False,
            "progress_manifest_modified": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    artifacts["generation_validation"] = write_json(validation_path, validation)
    validation_counts = script_counts(validation_path.read_text(encoding="utf-8"))
    if validation_counts != {"cjk_unified_count": 0, "kana_count": 0}:
        raise SwitchTransferError("source script text leaked into validation artifact")
    return {
        "out_root": out_root,
        "entry_count": len(selected),
        "target_packed_sha256": sha256(rebuilt),
        "selection": selection_summary,
        "artifacts": artifacts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--switch-zip", type=Path, default=REPO_ROOT / SWITCH_ZIP_RELATIVE)
    parser.add_argument("--base-jp", type=Path, default=GAME_ROOT / SOURCE_PINS["base_jp"]["logical_path"])
    parser.add_argument("--pk-jp", type=Path, default=GAME_ROOT / SOURCE_PINS["pk_jp"]["logical_path"])
    parser.add_argument("--pk-sc", type=Path, default=GAME_ROOT / SOURCE_PINS["pk_sc"]["logical_path"])
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE)
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"entries={result['entry_count']}")
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for key, value in result["selection"].items():
        print(f"selection_{key}={value}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
