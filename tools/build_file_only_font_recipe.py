#!/usr/bin/env python3
"""Build and apply the file-only pinned-Noto G1N append recipe.

The distributable recipe contains only:

* 28 Unicode-to-new-ordinal map instructions per G1N table;
* 28 newly generated 12-byte records per G1N table; and
* OFL-licensed, pre-rasterized Noto Korean glyph pixels.

No stock G1N, LINK entry, archive range, executable byte, or runtime-modification payload is
written to the recipe.  Applying the recipe requires the user-owned stock
``res_lang.bin`` and is guarded by exact SHA-256 checks.  Output is always a
new file; the input archive is never overwritten.

Only the Python standard library and the adjacent ``nobu16_lz4.py`` source
module are used.  That local source module is loaded by Python; no native
library is loaded.  There is deliberately no running-process or registry
access, resident component, launcher, or runtime-modification code in this
tool.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
# A distributed source-only recipe must not grow an untracked __pycache__ when
# the adjacent LZ4 helper is imported from the package.
sys.dont_write_bytecode = True


def _load_lz4_module() -> Any:
    path = SCRIPT_DIR / "nobu16_lz4.py"
    spec = importlib.util.spec_from_file_location("nobu16_lz4_local", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    # dataclasses expects the defining module to be present during execution.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LZ4 = _load_lz4_module()


CODEPOINTS = (
    0xAC00,
    0xAC24,
    0xAC8C,
    0xAE30,
    0xB77C,
    0xB7EC,
    0xB8CC,
    0xB9AC,
    0xBB34,
    0xBD88,
    0xC0C8,
    0xC120,
    0xC124,
    0xC2A4,
    0xC5B4,
    0xC624,
    0xC774,
    0xC784,
    0xC7A5,
    0xC815,
    0xC885,
    0xC9D1,
    0xCD94,
    0xCE20,
    0xCF58,
    0xD150,
    0xD3B8,
    0xD558,
)


LOCKS: dict[str, dict[str, Any]] = {
    "SC": {
        "stock_archive": {
            "path": "RES_SC/res_lang.bin",
            "sha256": "916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99",
        },
        "target_archive": {
            "relative_path": "SC/res_lang.SC.pinned_noto.bin",
            "sha256": "7FB2E6E7ABE2ADC7C359170ECB92952054C2F7F412933B8F1B339B6ADE661B7E",
        },
        "entries": {
            6: {
                "stock_sha256": "414A8E98DCF0F52633CD039A74E97AE61A97D98A96684D450EBADD4C3C85CAEB",
                "target_sha256": "E4F151238D3B331D73A09785D0B2736709B2B235DD1B308C06F082A83C15ADCA",
                "target_relative_path": "SC/SC_6.pinned_noto.g1n",
            },
            7: {
                "stock_sha256": "DADBE4EEA223FD48CEFA9A93A08EF1F2458B3BD543ADFCEBD6D888B9EE2AFBB0",
                "target_sha256": "CE976A729FBCA8F3B18A7DF5137B78CF08A76E073A25635607500B8BD026CFAD",
                "target_relative_path": "SC/SC_7.pinned_noto.g1n",
            },
        },
    },
    "TC": {
        "stock_archive": {
            "path": "RES_TC/res_lang.bin",
            "sha256": "A286388AC4A8F6E03E3BD5AC5B91069E858805EBBE81F670991B162A813B0B2F",
        },
        "target_archive": {
            "relative_path": "TC/res_lang.TC.pinned_noto.bin",
            "sha256": "5228871705DBF0CDB61B95A704E74B51B8B2CE59539CBA78CF94ACB096B199AF",
        },
        "entries": {
            6: {
                "stock_sha256": "6C3856FA977099C90F74152E57E2D7A34F178FC141DB1CA361E8ECE8252B0E1E",
                "target_sha256": "0E63992235BB1E198BC78DC9A8F7BC97C1DDFC2CDF902832D11D709D340C06AE",
                "target_relative_path": "TC/TC_6.pinned_noto.g1n",
            },
            7: {
                "stock_sha256": "F6F30FB95C991A0F4A1B894B3E1F9C0A82EDCA2CCDDD59B017AC77BF80ACC521",
                "target_sha256": "C1D7B8B02EBCA1A02134DD176A7CFDFCCB6953E3A7CCE552B1800F28BA894E9F",
                "target_relative_path": "TC/TC_7.pinned_noto.g1n",
            },
        },
    },
}


FONT_PROVENANCE = {
    "family": "Noto Sans KR / Noto Serif KR",
    "license": "SIL Open Font License 1.1",
    "google_fonts_commit": "ec0464b978de222073645d6d3366f3fdf03376d8",
    "source_fonts": {
        "NotoSansKR-wght.ttf": "194018E6B2B293A7964F037B25C0249CE1418BC9AB3C971060A03AA57861E252",
        "NotoSerifKR-wght.ttf": "11F8D5DE6F1B79195EFBA3828AAA2EC95C1178F5AE976FB23C8D53250A9938F3",
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_hash(data: bytes, expected: str, label: str) -> None:
    actual = sha256_bytes(data)
    if actual != expected:
        raise ValueError(f"{label} SHA-256 mismatch: expected={expected} actual={actual}")


def read_u16(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_u32(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def parse_layout(data: bytes, label: str) -> dict[str, Any]:
    if len(data) < 0x28 or data[:8] != b"_N1G0000":
        raise ValueError(f"{label}: not a G1N file")
    declared_size = read_u32(data, 0x08)
    header_size = read_u32(data, 0x0C)
    atlas_offset = read_u32(data, 0x14)
    palette_count = read_u32(data, 0x18)
    table_count = read_u32(data, 0x1C)
    if declared_size != len(data):
        raise ValueError(f"{label}: declared size mismatch")
    if table_count != 2:
        raise ValueError(f"{label}: expected exactly two tables, found {table_count}")
    if header_size != 0x20 + 4 * table_count + 0x40 * palette_count:
        raise ValueError(f"{label}: header/palette equation failed")
    table_offsets = [read_u32(data, 0x20 + 4 * index) for index in range(table_count)]
    if table_offsets[0] != header_size:
        raise ValueError(f"{label}: table 0 does not start at header end")
    if not (table_offsets[0] < table_offsets[1] < atlas_offset <= len(data)):
        raise ValueError(f"{label}: invalid table/atlas order")
    record_counts: list[int] = []
    table_ends = [table_offsets[1], atlas_offset]
    for index, (offset, end) in enumerate(zip(table_offsets, table_ends)):
        record_bytes = end - offset - 0x20000
        if record_bytes < 0 or record_bytes % 12:
            raise ValueError(f"{label}: malformed table {index} record region")
        record_counts.append(record_bytes // 12)
    return {
        "declared_size": declared_size,
        "header_size": header_size,
        "atlas_offset": atlas_offset,
        "palette_count": palette_count,
        "table_count": table_count,
        "table_offsets": table_offsets,
        "table_ends": table_ends,
        "record_counts": record_counts,
        "atlas_length": len(data) - atlas_offset,
    }


def extract_raw_entry(archive: Any, index: int, label: str) -> bytes:
    if index < 0 or index >= len(archive.entries):
        raise ValueError(f"{label}: LINK entry {index} is missing")
    _, raw = LZ4.decompress_wrapper(archive.entries[index].data)
    return raw


def assert_header_only_allowed_changes(stock: bytes, target: bytes, header_size: int, label: str) -> None:
    normalized = bytearray(target[:header_size])
    for start, end in ((0x08, 0x0C), (0x14, 0x18), (0x24, 0x28)):
        normalized[start:end] = stock[start:end]
    if bytes(normalized) != stock[:header_size]:
        diffs = [index for index, (a, b) in enumerate(zip(stock[:header_size], normalized)) if a != b]
        preview = ", ".join(f"0x{offset:X}" for offset in diffs[:8])
        raise ValueError(f"{label}: header changed outside allowed fields: {preview}")


def analyze_candidate_entry(stock: bytes, target: bytes, entry: int, label: str) -> tuple[dict[str, Any], bytes]:
    stock_layout = parse_layout(stock, f"{label} stock")
    target_layout = parse_layout(target, f"{label} target")
    additions = len(CODEPOINTS)
    record_add_per_table = additions * 12
    total_record_add = 2 * record_add_per_table
    cell = 48 if entry == 6 else 32
    pixel_size = (cell // 2) * cell
    expected_pixel_tail_size = 2 * additions * pixel_size

    expected_table_offsets = [
        stock_layout["table_offsets"][0],
        stock_layout["table_offsets"][1] + record_add_per_table,
    ]
    expected_atlas_offset = stock_layout["atlas_offset"] + total_record_add
    expected_size = len(stock) + total_record_add + expected_pixel_tail_size
    if target_layout["header_size"] != stock_layout["header_size"]:
        raise ValueError(f"{label}: header size changed")
    if target_layout["palette_count"] != stock_layout["palette_count"]:
        raise ValueError(f"{label}: palette count changed")
    if target_layout["table_offsets"] != expected_table_offsets:
        raise ValueError(f"{label}: unexpected target table offsets")
    if target_layout["atlas_offset"] != expected_atlas_offset:
        raise ValueError(f"{label}: unexpected target atlas offset")
    if len(target) != expected_size:
        raise ValueError(f"{label}: unexpected target size")
    if target_layout["record_counts"] != [count + additions for count in stock_layout["record_counts"]]:
        raise ValueError(f"{label}: target record counts are not +28 per table")

    assert_header_only_allowed_changes(stock, target, stock_layout["header_size"], label)

    stock_palette = stock[0x28 : stock_layout["header_size"]]
    target_palette = target[0x28 : target_layout["header_size"]]
    if stock_palette != target_palette:
        raise ValueError(f"{label}: palette blob changed")

    table_recipes: list[dict[str, Any]] = []
    for table in range(2):
        source_offset = stock_layout["table_offsets"][table]
        target_offset = target_layout["table_offsets"][table]
        old_record_count = stock_layout["record_counts"][table]
        map_changes: list[dict[str, Any]] = []
        allowed = set(CODEPOINTS)
        actual_changes: set[int] = set()
        for codepoint in range(0x10000):
            old_value = read_u16(stock, source_offset + 2 * codepoint)
            new_value = read_u16(target, target_offset + 2 * codepoint)
            if old_value != new_value:
                actual_changes.add(codepoint)
                if codepoint not in allowed:
                    raise ValueError(f"{label}: table {table} map changed at U+{codepoint:04X}")
        if actual_changes != allowed:
            missing = sorted(allowed - actual_changes)
            raise ValueError(f"{label}: table {table} did not change all 28 cells: {missing}")
        for index, codepoint in enumerate(CODEPOINTS):
            old_value = read_u16(stock, source_offset + 2 * codepoint)
            new_value = read_u16(target, target_offset + 2 * codepoint)
            expected_ordinal = old_record_count + index
            if old_value != 0 or new_value != expected_ordinal:
                raise ValueError(
                    f"{label}: table {table} U+{codepoint:04X} expected 0->{expected_ordinal}, "
                    f"found {old_value}->{new_value}"
                )
            map_changes.append(
                {
                    "codepoint": f"U+{codepoint:04X}",
                    "expected_old_ordinal": 0,
                    "new_ordinal": new_value,
                }
            )

        source_records = stock[
            source_offset + 0x20000 : stock_layout["table_ends"][table]
        ]
        target_old_records_start = target_offset + 0x20000
        target_old_records = target[
            target_old_records_start : target_old_records_start + len(source_records)
        ]
        if target_old_records != source_records:
            raise ValueError(f"{label}: table {table} existing records changed")
        new_records_start = target_old_records_start + len(source_records)
        new_records = target[new_records_start : new_records_start + record_add_per_table]
        if len(new_records) != record_add_per_table:
            raise ValueError(f"{label}: table {table} appended records are truncated")

        table_pixel_offset = table * additions * pixel_size
        for index in range(additions):
            record = new_records[index * 12 : (index + 1) * 12]
            expected_prefix = bytes((cell, cell, 0, cell, cell, 256 - cell // 2, 0, cell))
            if record[:8] != expected_prefix:
                raise ValueError(f"{label}: table {table} record {index} metrics changed")
            expected_pointer = stock_layout["atlas_length"] + table_pixel_offset + index * pixel_size
            if read_u32(record, 8) != expected_pointer:
                raise ValueError(f"{label}: table {table} record {index} pointer mismatch")

        table_recipes.append(
            {
                "table": table,
                "source_offset": source_offset,
                "target_offset": target_offset,
                "source_record_count": old_record_count,
                "target_record_count": old_record_count + additions,
                "map_changes": map_changes,
                "appended_records_hex": new_records.hex().upper(),
                "appended_records_sha256": sha256_bytes(new_records),
                "pixel_payload_offset": table_pixel_offset,
                "pixel_payload_length": additions * pixel_size,
            }
        )

    stock_atlas = stock[stock_layout["atlas_offset"] :]
    target_stock_atlas = target[
        target_layout["atlas_offset"] : target_layout["atlas_offset"] + len(stock_atlas)
    ]
    if target_stock_atlas != stock_atlas:
        raise ValueError(f"{label}: complete stock atlas is not an exact target prefix")
    pixel_tail = target[target_layout["atlas_offset"] + len(stock_atlas) :]
    if len(pixel_tail) != expected_pixel_tail_size:
        raise ValueError(f"{label}: candidate-only pixel tail size mismatch")
    for block_index in range(2 * additions):
        block = pixel_tail[block_index * pixel_size : (block_index + 1) * pixel_size]
        if not any(block):
            raise ValueError(f"{label}: appended pixel block {block_index} is blank")

    recipe = {
        "entry": entry,
        "stock": {
            "size": len(stock),
            "sha256": sha256_bytes(stock),
            "header_size": stock_layout["header_size"],
            "palette_count": stock_layout["palette_count"],
            "table_offsets": stock_layout["table_offsets"],
            "atlas_offset": stock_layout["atlas_offset"],
            "atlas_length": stock_layout["atlas_length"],
        },
        "target": {
            "size": len(target),
            "sha256": sha256_bytes(target),
            "table_offsets": target_layout["table_offsets"],
            "atlas_offset": target_layout["atlas_offset"],
        },
        "tables": table_recipes,
        "pixel_payload": {
            "file": f"payload/glyph_pixels_entry_{entry}.bin",
            "size": len(pixel_tail),
            "sha256": sha256_bytes(pixel_tail),
            "cell": cell,
            "bytes_per_glyph": pixel_size,
            "glyph_count_per_table": additions,
            "table_order": [0, 1],
        },
        "preservation_contract": {
            "header_changes_only": ["declared_file_size", "atlas_offset", "table_1_offset"],
            "palette_blob_exact": True,
            "maps_unchanged_outside_28_codepoints": True,
            "existing_records_exact": True,
            "complete_stock_atlas_exact_prefix": True,
        },
    }
    return recipe, pixel_tail


def build_g1n_from_recipe(stock: bytes, entry_recipe: dict[str, Any], pixel_payload: bytes, label: str) -> bytes:
    stock_info = entry_recipe["stock"]
    require_hash(stock, stock_info["sha256"], f"{label} stock entry")
    if len(stock) != stock_info["size"]:
        raise ValueError(f"{label}: stock entry size mismatch")
    layout = parse_layout(stock, f"{label} stock")
    expected_shape = {
        "header_size": stock_info["header_size"],
        "palette_count": stock_info["palette_count"],
        "table_offsets": stock_info["table_offsets"],
        "atlas_offset": stock_info["atlas_offset"],
        "atlas_length": stock_info["atlas_length"],
    }
    for key, expected in expected_shape.items():
        if layout[key] != expected:
            raise ValueError(f"{label}: stock structural gate failed for {key}")

    payload_info = entry_recipe["pixel_payload"]
    require_hash(pixel_payload, payload_info["sha256"], f"{label} pixel payload")
    if len(pixel_payload) != payload_info["size"]:
        raise ValueError(f"{label}: pixel payload size mismatch")

    target = entry_recipe["target"]
    output = bytearray(target["size"])
    header_size = layout["header_size"]
    output[:header_size] = stock[:header_size]
    struct.pack_into("<I", output, 0x08, target["size"])
    struct.pack_into("<I", output, 0x14, target["atlas_offset"])
    for table, offset in enumerate(target["table_offsets"]):
        struct.pack_into("<I", output, 0x20 + 4 * table, offset)

    for table_recipe in entry_recipe["tables"]:
        table = table_recipe["table"]
        source_offset = layout["table_offsets"][table]
        target_offset = target["table_offsets"][table]
        if source_offset != table_recipe["source_offset"] or target_offset != table_recipe["target_offset"]:
            raise ValueError(f"{label}: table {table} offset gate failed")

        table_map = bytearray(stock[source_offset : source_offset + 0x20000])
        for change in table_recipe["map_changes"]:
            codepoint = int(change["codepoint"][2:], 16)
            current = read_u16(table_map, 2 * codepoint)
            if current != change["expected_old_ordinal"]:
                raise ValueError(f"{label}: table {table} U+{codepoint:04X} old ordinal gate failed")
            struct.pack_into("<H", table_map, 2 * codepoint, change["new_ordinal"])
        output[target_offset : target_offset + 0x20000] = table_map

        old_records_start = source_offset + 0x20000
        old_records_end = layout["table_ends"][table]
        old_records = stock[old_records_start:old_records_end]
        target_records_start = target_offset + 0x20000
        output[target_records_start : target_records_start + len(old_records)] = old_records
        appended_records = bytes.fromhex(table_recipe["appended_records_hex"])
        require_hash(
            appended_records,
            table_recipe["appended_records_sha256"],
            f"{label} table {table} appended records",
        )
        appended_start = target_records_start + len(old_records)
        output[appended_start : appended_start + len(appended_records)] = appended_records

    stock_atlas = stock[layout["atlas_offset"] :]
    target_atlas_offset = target["atlas_offset"]
    output[target_atlas_offset : target_atlas_offset + len(stock_atlas)] = stock_atlas
    output[target_atlas_offset + len(stock_atlas) :] = pixel_payload

    result = bytes(output)
    require_hash(result, target["sha256"], f"{label} rebuilt target entry")
    if len(result) != target["size"]:
        raise ValueError(f"{label}: rebuilt target size mismatch")
    return result


def atomic_write(path: Path, data: bytes, forbidden: tuple[Path, ...] = ()) -> None:
    resolved = path.resolve()
    for source in forbidden:
        if resolved == source.resolve():
            raise ValueError(f"refusing to overwrite input file: {source}")
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: Any) -> None:
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def build_candidate_archive(stock_blob: bytes, replacements: dict[int, bytes]) -> bytes:
    """Match the existing two-step repack order: entry 6, then entry 7."""
    archive = LZ4.parse_link(stock_blob)
    entry6_wrapped = LZ4.recompress_wrapper(replacements[6], archive.entries[6].data)
    step1_blob = LZ4.rebuild_link(archive, {6: entry6_wrapped})
    step1 = LZ4.parse_link(step1_blob)
    entry7_wrapped = LZ4.recompress_wrapper(replacements[7], step1.entries[7].data)
    return LZ4.rebuild_link(step1, {7: entry7_wrapped})


def export_recipe(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    candidate_root = Path(args.candidate_root).resolve()
    output_root = Path(args.output_root).resolve()
    allowed_package_files = {
        "AUDIT.json",
        "recipe.json",
        "licenses/OFL-NotoSansKR.txt",
        "licenses/OFL-NotoSerifKR.txt",
        "payload/glyph_pixels_entry_6.bin",
        "payload/glyph_pixels_entry_7.bin",
        "tools/build_file_only_font_recipe.py",
        "tools/nobu16_lz4.py",
    }
    if output_root.exists():
        unexpected = sorted(
            path.relative_to(output_root).as_posix()
            for path in output_root.rglob("*")
            if path.is_file() and path.relative_to(output_root).as_posix() not in allowed_package_files
        )
        if unexpected:
            raise ValueError(
                "refusing to export into a package directory with untracked files: "
                + ", ".join(unexpected)
            )
    payload_dir = output_root / "payload"
    payload_dir.mkdir(parents=True, exist_ok=True)

    recipe: dict[str, Any] = {
        "schema": "nobu16.file-only-g1n-tail-recipe.v1",
        "release_eligible": False,
        "runtime_direct_lookup_verified": False,
        "file_only": True,
        "runtime_patch_features": [],
        "codepoints": [f"U+{codepoint:04X}" for codepoint in CODEPOINTS],
        "font_provenance": FONT_PROVENANCE,
        "payload_policy": {
            "contains_stock_archive": False,
            "contains_stock_g1n": False,
            "contains_stock_atlas_or_records": False,
            "contains_executable_bytes": False,
            "contains_runtime_memory_patch": False,
            "binary_payload_origin": "OFL Noto Korean glyph raster pixels appended by the pinned builder",
            "structural_payload": "28 map writes and 28 new records per table; no pre-existing record is carried",
            "stock_bytes_are_read_only_at_apply_time": True,
        },
        "languages": {},
    }

    shared_pixels: dict[int, bytes] = {}
    export_checks: list[dict[str, Any]] = []
    for language in ("SC", "TC"):
        lock = LOCKS[language]
        stock_archive_path = project_root / lock["stock_archive"]["path"]
        target_archive_path = candidate_root / lock["target_archive"]["relative_path"]
        stock_blob = stock_archive_path.read_bytes()
        target_blob = target_archive_path.read_bytes()
        require_hash(stock_blob, lock["stock_archive"]["sha256"], f"{language} stock archive")
        require_hash(target_blob, lock["target_archive"]["sha256"], f"{language} target archive")
        stock_archive = LZ4.parse_link(stock_blob)
        target_archive = LZ4.parse_link(target_blob)
        if LZ4.rebuild_link(stock_archive) != stock_blob or LZ4.rebuild_link(target_archive) != target_blob:
            raise ValueError(f"{language}: LINK parse/rebuild identity gate failed")

        language_recipe: dict[str, Any] = {
            "stock_archive": {
                "relative_path": lock["stock_archive"]["path"],
                "size": len(stock_blob),
                "sha256": sha256_bytes(stock_blob),
            },
            "target_archive": {
                "size": len(target_blob),
                "sha256": sha256_bytes(target_blob),
            },
            "entries": {},
        }
        rebuilt_entries: dict[int, bytes] = {}
        for entry in (6, 7):
            entry_lock = lock["entries"][entry]
            stock_g1n = extract_raw_entry(stock_archive, entry, f"{language} stock")
            target_g1n = extract_raw_entry(target_archive, entry, f"{language} target")
            require_hash(stock_g1n, entry_lock["stock_sha256"], f"{language} entry {entry} stock")
            require_hash(target_g1n, entry_lock["target_sha256"], f"{language} entry {entry} target")

            standalone_target_path = candidate_root / entry_lock["target_relative_path"]
            standalone_target = standalone_target_path.read_bytes()
            if standalone_target != target_g1n:
                raise ValueError(f"{language} entry {entry}: candidate archive differs from standalone G1N")

            entry_recipe, pixels = analyze_candidate_entry(
                stock_g1n, target_g1n, entry, f"{language} entry {entry}"
            )
            if entry in shared_pixels and shared_pixels[entry] != pixels:
                raise ValueError(f"entry {entry}: SC and TC appended Noto pixel payloads differ")
            shared_pixels.setdefault(entry, pixels)
            rebuilt = build_g1n_from_recipe(
                stock_g1n, entry_recipe, pixels, f"{language} entry {entry} export self-test"
            )
            if rebuilt != target_g1n:
                raise ValueError(f"{language} entry {entry}: recipe self-test was not byte-identical")
            rebuilt_entries[entry] = rebuilt
            language_recipe["entries"][str(entry)] = entry_recipe
            export_checks.append(
                {
                    "language": language,
                    "entry": entry,
                    "stock_sha256": sha256_bytes(stock_g1n),
                    "target_sha256": sha256_bytes(target_g1n),
                    "rebuilt_sha256": sha256_bytes(rebuilt),
                    "byte_identical": rebuilt == target_g1n,
                }
            )

        rebuilt_archive = build_candidate_archive(stock_blob, rebuilt_entries)
        if rebuilt_archive != target_blob:
            raise ValueError(f"{language}: recipe archive is not byte-identical to pinned candidate")
        language_recipe["export_archive_self_test"] = {
            "rebuilt_sha256": sha256_bytes(rebuilt_archive),
            "byte_identical_to_pinned_candidate": True,
            "link_roundtrip_exact": LZ4.rebuild_link(LZ4.parse_link(rebuilt_archive)) == rebuilt_archive,
        }
        recipe["languages"][language] = language_recipe

    payload_inventory: list[dict[str, Any]] = []
    for entry in (6, 7):
        path = payload_dir / f"glyph_pixels_entry_{entry}.bin"
        atomic_write(path, shared_pixels[entry])
        payload_inventory.append(
            {
                "path": path.relative_to(output_root).as_posix(),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
                "origin": "candidate-only appended OFL Noto glyph pixel tail",
            }
        )

    licenses_dir = output_root / "licenses"
    licenses_dir.mkdir(parents=True, exist_ok=True)
    for name in ("OFL-NotoSansKR.txt", "OFL-NotoSerifKR.txt"):
        source = project_root / "KR_PATCH_WORK" / "vendor" / "noto" / name
        destination = licenses_dir / name
        shutil.copyfile(source, destination)
        payload_inventory.append(
            {
                "path": destination.relative_to(output_root).as_posix(),
                "size": destination.stat().st_size,
                "sha256": sha256_file(destination),
                "origin": "SIL Open Font License text",
            }
        )

    # Make the exported recipe self-contained.  These are source-code tools,
    # not publisher resources; the copied applier imports the copied LZ4
    # module from the same directory.
    tools_dir = output_root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    for source in (Path(__file__).resolve(), SCRIPT_DIR / "nobu16_lz4.py"):
        destination = tools_dir / source.name
        shutil.copyfile(source, destination)
        payload_inventory.append(
            {
                "path": destination.relative_to(output_root).as_posix(),
                "size": destination.stat().st_size,
                "sha256": sha256_file(destination),
                "origin": "file-only standard-library patch source code",
            }
        )

    recipe["payload_inventory"] = payload_inventory
    recipe["export_self_tests"] = export_checks
    recipe_path = output_root / "recipe.json"
    write_json(recipe_path, recipe)
    recipe_hash = sha256_file(recipe_path)
    audit = {
        "schema": "nobu16.file-only-g1n-tail-recipe.audit.v1",
        "recipe": {
            "path": recipe_path.name,
            "size": recipe_path.stat().st_size,
            "sha256": recipe_hash,
        },
        "payload_inventory": payload_inventory,
        "payload_bytes_total_excluding_license_text_and_json": sum(
            item["size"] for item in payload_inventory if item["path"].endswith(".bin")
        ),
        "commercial_original_bytes_in_payload": False,
        "proof_by_construction": [
            "Binary payloads are sliced only from each candidate's appended atlas tail after the exact stock-atlas prefix.",
            "JSON carries only hashes, dimensions, offsets, 28 map writes, and candidate-only appended record bytes.",
            "No stock header, palette, map, old record, atlas, LINK entry, archive, or executable range is written.",
            "The user's stock archive is required and SHA-gated when applying the recipe.",
        ],
        "runtime_access_contract": {
            "process_memory_access": False,
            "external_process_control": False,
            "native_dynamic_library_loading": False,
            "local_python_source_module_loaded": True,
            "arbitrary_plugin_loading": False,
            "persistent_runtime_component": False,
            "registry_access": False,
            "process_access": False,
        },
        "release_eligible": False,
        "reason": "in-game direct Hangul lookup/rendering has not yet passed the runtime gate",
    }
    write_json(output_root / "AUDIT.json", audit)
    print(f"recipe={recipe_path}")
    print(f"recipe_sha256={recipe_hash}")
    print(f"binary_payload_bytes={audit['payload_bytes_total_excluding_license_text_and_json']}")
    print("commercial_original_bytes_in_payload=False")
    print("SC_export_roundtrip=OK")
    print("TC_export_roundtrip=OK")
    print("release_eligible=False")
    return 0


def load_recipe(path: Path) -> dict[str, Any]:
    recipe = json.loads(path.read_text(encoding="utf-8"))
    if recipe.get("schema") != "nobu16.file-only-g1n-tail-recipe.v1":
        raise ValueError("unsupported recipe schema")
    if recipe.get("file_only") is not True or recipe.get("runtime_patch_features") != []:
        raise ValueError("recipe is not marked as file-only")
    release_eligible = recipe.get("release_eligible")
    runtime_verified = recipe.get("runtime_direct_lookup_verified")
    if not isinstance(release_eligible, bool) or not isinstance(runtime_verified, bool):
        raise ValueError("recipe runtime gates must be booleans")
    if release_eligible != runtime_verified:
        raise ValueError("release eligibility and runtime verification gates disagree")
    if release_eligible:
        evidence = recipe.get("runtime_verification")
        if not isinstance(evidence, dict):
            raise ValueError("release-eligible recipe is missing runtime verification evidence")
        language = evidence.get("language")
        if language not in recipe.get("languages", {}):
            raise ValueError("runtime verification language is absent from recipe")
        target_hash = recipe["languages"][language]["target_archive"]["sha256"]
        if evidence.get("candidate_archive_sha256") != target_hash:
            raise ValueError("runtime verification candidate hash does not match recipe target")
        required_true = (
            "main_menu_booted",
            "all_tested_hangul_labels_nonblank",
            "normal_exit",
        )
        if any(evidence.get(field) is not True for field in required_true):
            raise ValueError("runtime verification evidence is incomplete")
        if evidence.get("startup_error_9001_observed") is not False:
            raise ValueError("runtime verification did not clear startup error 9001")
        if not isinstance(evidence.get("tested_labels"), list) or not evidence["tested_labels"]:
            raise ValueError("runtime verification has no tested label list")
    return recipe


def apply_recipe(args: argparse.Namespace) -> int:
    language = args.language.upper()
    if language not in ("SC", "TC"):
        raise ValueError("language must be SC or TC")
    recipe_path = Path(args.recipe).resolve()
    recipe_root = recipe_path.parent
    stock_path = Path(args.stock_archive).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_archive = output_dir / f"res_lang.{language}.pinned_noto.recipe.bin"
    if output_archive.resolve() == stock_path:
        raise ValueError("refusing to overwrite stock archive")

    recipe = load_recipe(recipe_path)
    language_recipe = recipe["languages"][language]
    stock_blob = stock_path.read_bytes()
    require_hash(stock_blob, language_recipe["stock_archive"]["sha256"], f"{language} stock archive")
    input_hash_before = sha256_bytes(stock_blob)
    stock_archive = LZ4.parse_link(stock_blob)
    if LZ4.rebuild_link(stock_archive) != stock_blob:
        raise ValueError(f"{language}: stock LINK parse/rebuild identity gate failed")

    replacements: dict[int, bytes] = {}
    entry_results: list[dict[str, Any]] = []
    for entry in (6, 7):
        entry_recipe = language_recipe["entries"][str(entry)]
        payload_path = recipe_root / entry_recipe["pixel_payload"]["file"]
        pixels = payload_path.read_bytes()
        stock_g1n = extract_raw_entry(stock_archive, entry, f"{language} stock")
        rebuilt = build_g1n_from_recipe(stock_g1n, entry_recipe, pixels, f"{language} entry {entry}")
        replacements[entry] = rebuilt
        standalone = output_dir / f"{language}_{entry}.recipe.g1n"
        atomic_write(standalone, rebuilt)
        entry_results.append(
            {
                "entry": entry,
                "stock_sha256": sha256_bytes(stock_g1n),
                "output_path": str(standalone),
                "output_size": len(rebuilt),
                "output_sha256": sha256_bytes(rebuilt),
                "target_sha256": entry_recipe["target"]["sha256"],
                "exact": sha256_bytes(rebuilt) == entry_recipe["target"]["sha256"],
            }
        )

    rebuilt_archive = build_candidate_archive(stock_blob, replacements)
    target_archive_hash = language_recipe["target_archive"]["sha256"]
    require_hash(rebuilt_archive, target_archive_hash, f"{language} rebuilt archive")
    parsed_output = LZ4.parse_link(rebuilt_archive)
    if LZ4.rebuild_link(parsed_output) != rebuilt_archive:
        raise ValueError(f"{language}: rebuilt LINK parse/rebuild roundtrip failed")
    for index, old_entry in enumerate(stock_archive.entries):
        if index not in replacements and parsed_output.entries[index].data != old_entry.data:
            raise ValueError(f"{language}: untouched LINK entry {index} changed")
    for entry in (6, 7):
        reextracted = extract_raw_entry(parsed_output, entry, f"{language} rebuilt")
        if reextracted != replacements[entry]:
            raise ValueError(f"{language}: entry {entry} re-extraction mismatch")

    atomic_write(output_archive, rebuilt_archive, forbidden=(stock_path,))
    input_hash_after = sha256_file(stock_path)
    if input_hash_after != input_hash_before:
        raise ValueError(f"{language}: input archive changed during read-only application")
    report = {
        "schema": "nobu16.file-only-g1n-tail-recipe.apply-report.v1",
        "language": language,
        "recipe_path": str(recipe_path),
        "stock_archive": {
            "path": str(stock_path),
            "sha256_before": input_hash_before,
            "sha256_after": input_hash_after,
            "unchanged": True,
        },
        "output_archive": {
            "path": str(output_archive),
            "size": len(rebuilt_archive),
            "sha256": sha256_bytes(rebuilt_archive),
            "target_sha256": target_archive_hash,
            "exact": True,
            "link_parse_rebuild_roundtrip": True,
            "entries_6_7_reextract_exact": True,
            "all_other_entry_payloads_exact": True,
        },
        "entries": entry_results,
        "runtime_patch_used": False,
        "installed_game_file_modified": False,
        "runtime_direct_lookup_verified": recipe["runtime_direct_lookup_verified"],
        "release_eligible": recipe["release_eligible"],
        "runtime_verification": recipe.get("runtime_verification"),
    }
    if not recipe["release_eligible"]:
        report["release_blocker"] = "in-game direct Hangul lookup/rendering remains unverified"
    report_path = output_dir / "apply_report.json"
    write_json(report_path, report)
    print(f"language={language}")
    print(f"output={output_archive}")
    print(f"sha256={sha256_bytes(rebuilt_archive)}")
    print("standalone_entries_exact=OK")
    print("link_roundtrip=OK")
    print("reextract_roundtrip=OK")
    print("stock_input_unchanged=OK")
    print("runtime_patch_used=False")
    print(f"release_eligible={recipe['release_eligible']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    export = subparsers.add_parser("export", help="Export the tiny, original-free recipe from pinned candidates")
    export.add_argument("--project-root", default=str(PROJECT_ROOT))
    export.add_argument(
        "--candidate-root",
        default=str(PROJECT_ROOT / "KR_PATCH_WORK" / "tmp" / "sc_tc_pinned_noto_raw"),
    )
    export.add_argument(
        "--output-root",
        default=str(
            PROJECT_ROOT / "KR_PATCH_WORK" / "tmp" / "file_only_font_recipe" / "release_payload"
        ),
    )
    export.set_defaults(func=export_recipe)

    apply = subparsers.add_parser("apply", help="Apply the recipe to a SHA-gated stock archive")
    apply.add_argument("--recipe", required=True)
    apply.add_argument("--language", required=True, choices=("SC", "TC", "sc", "tc"))
    apply.add_argument("--stock-archive", required=True)
    apply.add_argument("--output-dir", required=True)
    apply.set_defaults(func=apply_recipe)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, LZ4.LZ4Error, LZ4.LinkError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
