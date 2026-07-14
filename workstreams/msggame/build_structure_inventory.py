#!/usr/bin/env python3
"""Build source-free msggame structure and literal-slot evidence.

No commercial string is written.  The output contains only file pins,
structural counts, coordinate hashes, and parser/rebuilder verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
FORMAT_PATH = WORKSTREAM_ROOT / "msggame_format.py"
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

from msggame_format import (  # noqa: E402
    is_visible_translation_candidate,
    iter_literals,
    parse_raw_msggame,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


INVENTORY_NAME = "structure_inventory.v0.1.json"
VALIDATION_NAME = "validation.v0.1.json"
FORBIDDEN_SOURCE_SCRIPT_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u3040-\u30FF]"
)

SOURCE_PINS: dict[str, dict[str, Any]] = {
    "MSG_PK/SC/msggame.bin": {
        "edition": "pk",
        "language": "SC",
        "packed_size": 529419,
        "packed_sha256": "BD7B33FCC7495B855B0828C7FE4E5F7ADB2DE656A9B12E20259750F94EE665D6",
        "raw_size": 1077200,
        "raw_sha256": "1958B2B801D37186D478284EA0E29CA96D8DA2BC087D6BEB74A4139EF01C11CE",
        "record_count": 21581,
    },
    "MSG_PK/JP/msggame.bin": {
        "edition": "pk",
        "language": "JP",
        "packed_size": 709290,
        "packed_sha256": "0FB9EA3B4817D208C65F587AF1F57A5BB82106367314801A13C9A534ECC47CD8",
        "raw_size": 1571384,
        "raw_sha256": "F00C897353C3C0084BFBFC5ED781C467945C82708F28A6D57BA0CC2710976D57",
        "record_count": 21581,
    },
    "MSG_PK/TC/msggame.bin": {
        "edition": "pk",
        "language": "TC",
        "packed_size": 535098,
        "packed_sha256": "73278A4CF06F007E729C37FC6E6409FD77A5A246DB0408CF2879082E88FB0B5D",
        "raw_size": 1120204,
        "raw_sha256": "989D3FD487344C4DAED73C1D13704488F77A0E6B036E491FBB588C1FFFF58AF4",
        "record_count": 21581,
    },
    "MSG_PK/EN/msggame.bin": {
        "edition": "pk",
        "language": "EN",
        "packed_size": 714037,
        "packed_sha256": "14D9A20ECB35F35C91D14947921CF09F5EAF960F8FA4D70F703F2366DB1D13AF",
        "raw_size": 2169852,
        "raw_sha256": "03A1D07A4FFB460F393A47A047EFF596BBCE6BAADAE22EB00B3686E8AF96D39E",
        "record_count": 21581,
    },
    "MSG/SC/msggame.bin": {
        "edition": "base",
        "language": "SC",
        "packed_size": 430720,
        "packed_sha256": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
        "raw_size": 878860,
        "raw_sha256": "A42DF025567DB627274454F97E57AC7B77D593401DEAF4CC6476D81A614CF020",
        "record_count": 19152,
    },
    "MSG/JP/msggame.bin": {
        "edition": "base",
        "language": "JP",
        "packed_size": 610163,
        "packed_sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        "raw_size": 1337548,
        "raw_sha256": "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38",
        "record_count": 19152,
    },
    "MSG/TC/msggame.bin": {
        "edition": "base",
        "language": "TC",
        "packed_size": 433170,
        "packed_sha256": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
        "raw_size": 916148,
        "raw_sha256": "754EAE338FA15594ADA28604C98E40CF2CB1C10EC829CDCCF8FB0F10D01CC0CF",
        "record_count": 19152,
    },
}


class InventoryError(ValueError):
    """Raised when a pinned source or structural invariant differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def coordinate_hash(coordinates: list[tuple[int, int, int]]) -> str:
    return sha256(
        json.dumps(coordinates, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    )


def literal_hash_chain(literals: list[Any]) -> str:
    digest = hashlib.sha256()
    for literal in literals:
        digest.update(literal.block_id.to_bytes(4, "little"))
        digest.update(literal.record_id.to_bytes(4, "little"))
        digest.update(literal.literal_id.to_bytes(4, "little"))
        digest.update(hashlib.sha256(literal.text.encode("utf-16-le")).digest())
    return digest.hexdigest().upper()


def inspect_source(game_root: Path, relative: str, pin: dict[str, Any]) -> dict[str, Any]:
    path = game_root / Path(relative)
    packed = path.read_bytes()
    if len(packed) != pin["packed_size"] or sha256(packed) != pin["packed_sha256"]:
        raise InventoryError(f"{relative}: packed source pin mismatch")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise InventoryError(f"{relative}: decompressed source pin mismatch")

    archive = parse_raw_msggame(raw)
    rebuilt = rebuild_raw_msggame(archive)
    if rebuilt != raw:
        raise InventoryError(f"{relative}: raw parse/rebuild is not byte-exact")
    if archive.record_count != pin["record_count"]:
        raise InventoryError(f"{relative}: record count changed")

    literals = list(iter_literals(archive))
    coordinates = [
        (literal.block_id, literal.record_id, literal.literal_id)
        for literal in literals
    ]
    visible = [
        literal for literal in literals if is_visible_translation_candidate(literal.text)
    ]
    marker_records = {
        (literal.block_id, literal.record_id) for literal in literals
    }
    block_literal_counts = [0] * len(archive.blocks)
    block_visible_counts = [0] * len(archive.blocks)
    for literal in literals:
        block_literal_counts[literal.block_id] += 1
        if is_visible_translation_candidate(literal.text):
            block_visible_counts[literal.block_id] += 1

    return {
        "relative_path": relative,
        "edition": pin["edition"],
        "language": pin["language"],
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "block_count": len(archive.blocks),
        "record_count": archive.record_count,
        "block_record_counts": [len(block.records) for block in archive.blocks],
        "block_sizes": [block.size for block in archive.blocks],
        "literal_marker_record_count": len(marker_records),
        "literal_slot_count": len(literals),
        "literal_empty_count": sum(not literal.text for literal in literals),
        "literal_nonempty_count": sum(bool(literal.text) for literal in literals),
        "literal_stripped_nonempty_count": sum(
            bool(literal.text.strip()) for literal in literals
        ),
        "visible_translation_candidate_count": len(visible),
        "utf16_code_unit_count": sum(
            len(literal.text.encode("utf-16-le")) // 2 for literal in literals
        ),
        "block_literal_counts": block_literal_counts,
        "block_visible_translation_candidate_counts": block_visible_counts,
        "literal_coordinate_sha256": coordinate_hash(coordinates),
        "literal_text_hash_chain_sha256": literal_hash_chain(literals),
        "checks": {
            "lz4_wrapper_decompression": "OK",
            "block_directory": "OK",
            "record_directories": "OK",
            "zero_alignment_padding": "OK",
            "literal_marker_balance": "OK",
            "literal_utf16le_decode": "OK",
            "raw_parse_rebuild_byte_exact": "OK",
        },
        "_coordinate_set": set(coordinates),
    }


def edition_alignment(rows: list[dict[str, Any]], edition: str) -> dict[str, Any]:
    selected = [row for row in rows if row["edition"] == edition]
    if not selected:
        raise InventoryError(f"no rows for edition {edition}")
    if len({tuple(row["block_record_counts"]) for row in selected}) != 1:
        raise InventoryError(f"{edition}: language record directories are not aligned")
    coordinate_sets = [row["_coordinate_set"] for row in selected]
    common = set.intersection(*coordinate_sets)
    union = set.union(*coordinate_sets)
    sc = next(row for row in selected if row["language"] == "SC")
    return {
        "edition": edition,
        "languages": [row["language"] for row in selected],
        "block_count_each": selected[0]["block_count"],
        "record_count_each": selected[0]["record_count"],
        "block_record_coordinates_aligned": True,
        "literal_coordinate_shapes_aligned": len(common) == len(union),
        "literal_coordinate_common_count": len(common),
        "literal_coordinate_union_count": len(union),
        "sc_translation_scope": {
            "base_language": "SC",
            "literal_slot_count": sc["literal_slot_count"],
            "visible_translation_candidate_count": sc[
                "visible_translation_candidate_count"
            ],
            "excluded_empty_or_non_visible_literal_count": sc["literal_slot_count"]
            - sc["visible_translation_candidate_count"],
            "coordinate_key": ["block_id", "record_id", "literal_id"],
        },
    }


def build_payload(game_root: Path) -> dict[str, Any]:
    before = {
        relative: sha256((game_root / Path(relative)).read_bytes())
        for relative in SOURCE_PINS
    }
    rows = [
        inspect_source(game_root, relative, pin)
        for relative, pin in SOURCE_PINS.items()
    ]
    payload_rows: list[dict[str, Any]] = []
    for row in rows:
        payload_rows.append({key: value for key, value in row.items() if not key.startswith("_")})
    after = {
        relative: sha256((game_root / Path(relative)).read_bytes())
        for relative in SOURCE_PINS
    }
    if before != after:
        raise InventoryError("installed source files changed during read-only inspection")

    return {
        "schema": "nobu16.kr.msggame-structure-inventory.v1",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_binary_patch_payload": False,
        },
        "format": {
            "wrapper": "24-byte NOBU16 raw-LZ4 wrapper",
            "raw_directory": "u32 block_count + block_count*(u32 offset,u32 size)",
            "block_directory": "u32 record_count + record_count*u32 relative_offset",
            "record_payload": "opaque bytecode with framed UTF-16LE literals",
            "literal_start_marker_hex": "07 07 01",
            "literal_end_marker_hex": "07 07 02",
            "alignment_bytes": 4,
            "record_terminal_offset_present": False,
        },
        "files": payload_rows,
        "edition_alignment": [
            edition_alignment(rows, "pk"),
            edition_alignment(rows, "base"),
        ],
        "scope_status": {
            "structural_parser": "proved",
            "raw_rebuilder": "byte_exact_noop_and_variable_length_capable",
            "literal_parser": "proved_for_all_pinned_records",
            "literal_overlay_coordinates": "ready",
            "translation_text": "not_included",
            "runtime_game_validation": "not_run",
        },
    }


def source_free(blob: bytes) -> bool:
    text = blob.decode("utf-8")
    return not FORBIDDEN_SOURCE_SCRIPT_RE.search(text) and "\x00" not in text


def build_outputs(game_root: Path, out_root: Path) -> dict[str, Any]:
    first = build_payload(game_root)
    second = build_payload(game_root)
    first_blob = encode_json(first)
    second_blob = encode_json(second)
    if first_blob != second_blob:
        raise InventoryError("two isolated in-memory inventories are not byte-identical")
    if not source_free(first_blob):
        raise InventoryError("inventory contains source script characters or embedded NUL")

    inventory_path = out_root / "public" / INVENTORY_NAME
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_bytes(first_blob)
    validation = {
        "schema": "nobu16.kr.msggame-structure-validation.v1",
        "passed": True,
        "inventory": {
            "relative_path": f"public/{INVENTORY_NAME}",
            "size": len(first_blob),
            "sha256": sha256(first_blob),
            "source_free_scan": "OK",
        },
        "verified_source_count": len(SOURCE_PINS),
        "verified_editions": ["pk", "base"],
        "verified_languages": {"pk": ["SC", "JP", "TC", "EN"], "base": ["SC", "JP", "TC"]},
        "checks": {
            "source_pins": "OK",
            "raw_parse_rebuild_byte_exact_all_sources": "OK",
            "literal_markers_balanced_all_records": "OK",
            "literal_utf16le_decode_all_slots": "OK",
            "deterministic_inventory_two_runs": "OK",
            "installed_game_files_unchanged": "OK",
        },
        "generator": {
            "relative_path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "parser": {
            "relative_path": FORMAT_PATH.name,
            "sha256": sha256(FORMAT_PATH.read_bytes()),
        },
        "safety": {
            "installed_game_files_modified": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
            "root_readme_or_progress_modified": False,
        },
    }
    validation_blob = encode_json(validation)
    if not source_free(validation_blob):
        raise InventoryError("validation contains source script characters or embedded NUL")
    validation_path = out_root / VALIDATION_NAME
    validation_path.write_bytes(validation_blob)
    return {
        "inventory_path": inventory_path,
        "inventory_sha256": sha256(first_blob),
        "validation_path": validation_path,
        "validation_sha256": sha256(validation_blob),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_outputs(args.game_root.resolve(), args.out_root.resolve())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for key, value in result.items():
        print(f"{key}={value}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
