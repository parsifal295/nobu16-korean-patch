#!/usr/bin/env python3
"""Build source-free structural and alignment inventory for MSG/*/strdata.bin."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

from build_common_message_overlay import text_hash  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from strdata_format import EXPECTED_SLOT_COUNTS, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


RESOURCE = "MSG/SC/strdata.bin"
LANGUAGES = ("SC", "JP", "TC")
SOURCE_PATHS = {language: f"MSG/{language}/strdata.bin" for language in LANGUAGES}
INVENTORY_NAME = "structure_inventory.v0.1.json"
FORBIDDEN_SOURCE_SCRIPT_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u3040-\u30FF]"
)

SOURCE_PINS = {
    "SC": {
        "packed_size": 516628,
        "packed_sha256": "93F88D71210B96783749CEB948E0713D7E6552F764F644092B71A5FD0C994B88",
        "raw_size": 760388,
        "raw_sha256": "17EF622F36BA94009F67519DC79ED543C223B467311E51711A009F9DD0816214",
    },
    "JP": {
        "packed_size": 507054,
        "packed_sha256": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
        "raw_size": 763928,
        "raw_sha256": "EAB14063C2060CE11794232F483F0B2210B3BD58118165CBEEC2F37176C25649",
    },
    "TC": {
        "packed_size": 532610,
        "packed_sha256": "16481F0B4B1E544F8F7C0B1C92210D13592560470AC062847DA32375B77DA861",
        "raw_size": 719184,
        "raw_sha256": "3076080A96E8251A8A700D95C201698BBEC1B391D746E3F51DFB780CB765075C",
    },
}
EXPECTED_NONEMPTY_COUNTS = {
    "SC": (21115, 3240, 2207, 122, 6),
    "JP": (22289, 3261, 2221, 122, 6),
    "TC": (21002, 3240, 2207, 122, 6),
}


class StrdataInventoryError(ValueError):
    """Raised when a pinned strdata source or inventory invariant differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def source_free_counts(blob: bytes) -> dict[str, int]:
    text = blob.decode("utf-8")
    return {
        "han_or_kana_count": len(FORBIDDEN_SOURCE_SCRIPT_RE.findall(text)),
        "embedded_nul_count": text.count("\x00"),
    }


def load_sources(game_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    before: dict[str, str] = {}
    for language in LANGUAGES:
        relative = Path(SOURCE_PATHS[language])
        path = game_root / relative
        packed = path.read_bytes()
        pin = SOURCE_PINS[language]
        packed_hash = sha256(packed)
        if len(packed) != pin["packed_size"] or packed_hash != pin["packed_sha256"]:
            raise StrdataInventoryError(f"{relative.as_posix()}: packed source pin mismatch")
        _wrapper, raw = decompress_wrapper(packed)
        raw_hash = sha256(raw)
        if len(raw) != pin["raw_size"] or raw_hash != pin["raw_sha256"]:
            raise StrdataInventoryError(f"{relative.as_posix()}: raw source pin mismatch")
        archive = parse_raw_strdata(raw)
        if rebuild_raw_strdata(archive) != raw:
            raise StrdataInventoryError(
                f"{relative.as_posix()}: unchanged parse/rebuild is not byte-identical"
            )
        nonempty = tuple(
            sum(bool(text.strip()) for text in block.texts) for block in archive.blocks
        )
        if nonempty != EXPECTED_NONEMPTY_COUNTS[language]:
            raise StrdataInventoryError(
                f"{relative.as_posix()}: nonempty counts={nonempty}, expected={EXPECTED_NONEMPTY_COUNTS[language]}"
            )
        loaded[language] = {
            "relative": relative.as_posix(),
            "packed": packed,
            "raw": raw,
            "archive": archive,
            "nonempty_counts": nonempty,
        }
        before[relative.as_posix()] = packed_hash
    return loaded, before


def _block_inventory(block: Any) -> dict[str, Any]:
    text_hashes = [text_hash(text) for text in block.texts]
    offsets = block.table.string_offsets
    return {
        "block_id": block.block_id,
        "outer_offset": block.offset,
        "logical_size": block.logical_size,
        "gap_after_size": len(block.gap_after),
        "inner_header_sha256": sha256(block.inner_header),
        "slot_count": block.slot_count,
        "display_nonempty_count": sum(bool(text.strip()) for text in block.texts),
        "directory_relative_offset": 20,
        "directory_size": block.table.table_size,
        "first_string_relative_offset": offsets[0],
        "last_string_relative_offset": offsets[-1],
        "ordered_utf16le_hashes_sha256": hash_json(text_hashes),
        "source_text_embedded": False,
    }


def _alignment_block(loaded: dict[str, dict[str, Any]], block_id: int) -> dict[str, Any]:
    texts = {
        language: loaded[language]["archive"].blocks[block_id].texts
        for language in LANGUAGES
    }
    slot_count = len(texts["SC"])
    if any(len(texts[language]) != slot_count for language in LANGUAGES):
        raise StrdataInventoryError(f"block {block_id}: language slot counts differ")
    occupancy = {
        "all_empty": 0,
        "all_nonempty": 0,
        "mixed": 0,
    }
    for slot_id in range(slot_count):
        states = [bool(texts[language][slot_id].strip()) for language in LANGUAGES]
        if all(states):
            occupancy["all_nonempty"] += 1
        elif not any(states):
            occupancy["all_empty"] += 1
        else:
            occupancy["mixed"] += 1
    return {
        "block_id": block_id,
        "slot_count": slot_count,
        "same_slot_count_across_languages": True,
        "occupancy": occupancy,
        "language_hash_chain_sha256": {
            language: hash_json([text_hash(text) for text in texts[language]])
            for language in LANGUAGES
        },
        "source_text_embedded": False,
    }


def build(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    loaded, before = load_sources(game_root)
    blocks = {
        language: [_block_inventory(block) for block in loaded[language]["archive"].blocks]
        for language in LANGUAGES
    }
    alignment = [_alignment_block(loaded, block_id) for block_id in range(len(EXPECTED_SLOT_COUNTS))]
    inventory = {
        "schema": "nobu16.kr.strdata-structure-inventory.v1",
        "resource": RESOURCE,
        "languages": list(LANGUAGES),
        "outer_container": {
            "block_count": len(EXPECTED_SLOT_COUNTS),
            "header_size": 44,
            "descriptor_rule": "first_block_size_then_offset_size_pairs",
            "inner_table_directory_relative_offset": 20,
            "synthetic_single_table_header_size": 12,
            "synthetic_padding_rule": "negative_of_12_plus_logical_size_mod_4",
        },
        "expected_slot_counts": list(EXPECTED_SLOT_COUNTS),
        "source_files": {
            language: {
                "relative_path": loaded[language]["relative"],
                **SOURCE_PINS[language],
                "block_display_nonempty_counts": list(loaded[language]["nonempty_counts"]),
            }
            for language in LANGUAGES
        },
        "language_blocks": blocks,
        "alignment": {
            "same_five_block_shape": True,
            "same_slot_counts_per_block": True,
            "block_count": len(alignment),
            "blocks": alignment,
            "source_text_embedded": False,
        },
        "raw_parse_rebuild_byte_exact_languages": list(LANGUAGES),
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
        },
        "contains_commercial_source_text": False,
    }
    path = out_root / "public" / INVENTORY_NAME
    artifact = write_json(path, inventory)
    scan = source_free_counts(path.read_bytes())
    if scan != {"han_or_kana_count": 0, "embedded_nul_count": 0}:
        raise StrdataInventoryError("structure inventory is not source-free")
    after = {
        relative: sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise StrdataInventoryError("installed strdata source changed during inventory build")
    return {"artifact": artifact, "inventory": inventory, "source_free_scan": scan}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"artifact_sha256={result['artifact']['sha256']}")
    print("raw_parse_rebuild_byte_exact=SC,JP,TC")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
