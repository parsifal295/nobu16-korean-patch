#!/usr/bin/env python3
"""Build a deterministic, corpus-driven SC G1N font-v3 component.

This is an offline file builder.  It reads SHA-gated stock resources and
glyph-demand inventories, writes only beneath a caller-selected output root,
and never accesses a game process, registry, launcher, or installed file for
mutation.  Full stock-derived G1N/LINK candidates are confined to ``private``;
the ``public`` directory contains only generated Noto pixels, structural
recipe data, validation metadata, and OFL license texts.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import unicodedata
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]
TOOLS_DIR = PROJECT_ROOT / "KR_PATCH_WORK" / "tools"
DEFAULT_DEMAND_ROOT = PROJECT_ROOT / "KR_PATCH_WORK" / "workstreams" / "msgui_full"
DEFAULT_OUTPUT_ROOT = SCRIPT_DIR / "build"
STOCK_ARCHIVE = PROJECT_ROOT / "RES_SC" / "res_lang.bin"
STOCK_ARCHIVE_SHA256 = "916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99"
FONT_LOCKS = {
    "sans": {
        "relative_path": "KR_PATCH_WORK/vendor/noto/NotoSansKR-wght.ttf",
        "sha256": "194018E6B2B293A7964F037B25C0249CE1418BC9AB3C971060A03AA57861E252",
        "license_relative_path": "KR_PATCH_WORK/vendor/noto/OFL-NotoSansKR.txt",
        "license_sha256": "1C05C68C34F9708415AADA51F17E1B0092D2CEA709BF4A94CD38114F9E73D7D9",
    },
    "serif": {
        "relative_path": "KR_PATCH_WORK/vendor/noto/NotoSerifKR-wght.ttf",
        "sha256": "11F8D5DE6F1B79195EFBA3828AAA2EC95C1178F5AE976FB23C8D53250A9938F3",
        "license_relative_path": "KR_PATCH_WORK/vendor/noto/OFL-NotoSerifKR.txt",
        "license_sha256": "5E0DA210FB04058A8C0087985D2D456B931C2579811A49655721D3CF0C36B6D6",
    },
}
PROFILES = (
    {"entry": 6, "table": 0, "family": "Noto Serif KR", "style": "Bold", "raster_size": 46, "cell": 48},
    {"entry": 6, "table": 1, "family": "Noto Sans KR Medium", "style": "Regular", "raster_size": 46, "cell": 48},
    {"entry": 7, "table": 0, "family": "Noto Sans KR SemiBold", "style": "Regular", "raster_size": 32, "cell": 32},
    {"entry": 7, "table": 1, "family": "Noto Sans KR SemiBold", "style": "Regular", "raster_size": 32, "cell": 32},
)
SEED_CODEPOINTS = (
    0xAC00, 0xAC24, 0xAC8C, 0xAE30, 0xB77C, 0xB7EC, 0xB8CC,
    0xB9AC, 0xBB34, 0xBD88, 0xC0C8, 0xC120, 0xC124, 0xC2A4,
    0xC5B4, 0xC624, 0xC774, 0xC784, 0xC7A5, 0xC815, 0xC885,
    0xC9D1, 0xCD94, 0xCE20, 0xCF58, 0xD150, 0xD3B8, 0xD558,
)
SEED_RASTER_V2_PAYLOAD_SHA256 = {
    6: "DF8D50151F648549C39CD355F47EA8ABACD6034BC88BEFBD8F6F03C012F35800",
    7: "3452CB489C9C7D59DDEFD0E0BBCAC75C9B3B498A5E71844ED5227E6A21B7C263",
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module("nobu16_font_v3_file_only_base", TOOLS_DIR / "build_file_only_font_recipe.py")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"{label} SHA mismatch: expected={expected} actual={actual}")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: Any) -> None:
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def canonical_cp(codepoint: int) -> str:
    return f"U+{codepoint:04X}"


def parse_canonical_cp(value: Any, label: str) -> int:
    if not isinstance(value, str) or len(value) != 6 or not value.startswith("U+"):
        raise ValueError(f"{label}: non-canonical codepoint {value!r}")
    try:
        codepoint = int(value[2:], 16)
    except ValueError as exc:
        raise ValueError(f"{label}: non-hex codepoint {value!r}") from exc
    if not (0 <= codepoint <= 0xFFFF) or canonical_cp(codepoint) != value:
        raise ValueError(f"{label}: codepoint must be uppercase four-digit BMP form: {value!r}")
    if 0xD800 <= codepoint <= 0xDFFF:
        raise ValueError(f"{label}: surrogate codepoint is forbidden: {value}")
    return codepoint


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def validate_demand(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read glyph demand {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema") != "nobu16.kr.glyph-demand.v1":
        raise ValueError(f"{path}: unsupported glyph-demand schema")

    characters = require_list(value.get("characters"), f"{path}: characters")
    codepoint_text = require_list(value.get("codepoints"), f"{path}: codepoints")
    if value.get("character_count") != len(characters) or len(characters) != len(codepoint_text):
        raise ValueError(f"{path}: character count/array mismatch")
    codepoints = [parse_canonical_cp(item, f"{path}: codepoints") for item in codepoint_text]
    if codepoints != sorted(set(codepoints)):
        raise ValueError(f"{path}: codepoints must be unique and strictly ascending")
    for character, codepoint in zip(characters, codepoints):
        if not isinstance(character, str) or len(character) != 1:
            raise ValueError(f"{path}: every character must be one BMP scalar: {character!r}")
        if not unicodedata.is_normalized("NFC", character) or unicodedata.normalize("NFC", character) != character:
            raise ValueError(f"{path}: character is not NFC: {character!r}")
        if ord(character) != codepoint:
            raise ValueError(f"{path}: character/codepoint mismatch for {character!r}")

    syllables = require_list(value.get("hangul_syllables"), f"{path}: hangul_syllables")
    syllable_text = require_list(value.get("hangul_syllable_codepoints"), f"{path}: hangul_syllable_codepoints")
    if value.get("hangul_syllable_count") != len(syllables) or len(syllables) != len(syllable_text):
        raise ValueError(f"{path}: Hangul syllable count/array mismatch")
    syllable_codepoints = [parse_canonical_cp(item, f"{path}: hangul_syllable_codepoints") for item in syllable_text]
    expected_syllables = [cp for cp in codepoints if 0xAC00 <= cp <= 0xD7A3]
    if syllable_codepoints != expected_syllables:
        raise ValueError(f"{path}: Hangul syllable subset is not the exact filtered codepoint list")
    if syllables != [chr(cp) for cp in syllable_codepoints]:
        raise ValueError(f"{path}: Hangul syllable character/codepoint mismatch")

    jamo = require_list(value.get("hangul_jamo"), f"{path}: hangul_jamo")
    jamo_text = require_list(value.get("hangul_jamo_codepoints"), f"{path}: hangul_jamo_codepoints")
    if value.get("hangul_jamo_count") != len(jamo) or len(jamo) != len(jamo_text):
        raise ValueError(f"{path}: Hangul jamo count/array mismatch")
    if jamo or jamo_text:
        raise ValueError(f"{path}: decomposed Hangul jamo is unsupported; translation must be NFC syllables")

    try:
        relative = path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"glyph demand must be inside the project root: {path}") from exc
    return {
        "path": relative,
        "sha256": sha256_bytes(raw),
        "source": value.get("source"),
        "character_count": len(codepoints),
        "hangul_syllable_count": len(syllable_codepoints),
        "codepoints": codepoints,
        "hangul_syllable_codepoints": syllable_codepoints,
    }


def demand_union(paths: Iterable[Path]) -> dict[str, Any]:
    unique_paths = sorted({path.resolve() for path in paths}, key=lambda item: item.as_posix())
    if not unique_paths:
        raise ValueError("no glyph_demand.json inputs found")
    sources = [validate_demand(path) for path in unique_paths]
    all_codepoints = sorted({cp for source in sources for cp in source["codepoints"]})
    hangul = sorted({cp for source in sources for cp in source["hangul_syllable_codepoints"]})
    filtered = [cp for cp in all_codepoints if 0xAC00 <= cp <= 0xD7A3]
    if hangul != filtered:
        raise ValueError("union Hangul subset drift")
    non_hangul = [cp for cp in all_codepoints if cp not in set(hangul)]
    canonical_lines = "".join(f"{canonical_cp(cp)}\n" for cp in all_codepoints).encode("ascii")
    hangul_lines = "".join(f"{canonical_cp(cp)}\n" for cp in hangul).encode("ascii")
    return {
        "sources": [{key: source[key] for key in ("path", "sha256", "source", "character_count", "hangul_syllable_count")} for source in sources],
        "codepoints": all_codepoints,
        "hangul": hangul,
        "non_hangul": non_hangul,
        "codepoint_count": len(all_codepoints),
        "hangul_count": len(hangul),
        "non_hangul_count": len(non_hangul),
        "union_sha256": sha256_bytes(canonical_lines),
        "hangul_sha256": sha256_bytes(hangul_lines),
    }


def signed8(value: int) -> int:
    return value - 256 if value >= 128 else value


def mapped_glyph_proof(data: bytes, layout: dict[str, Any], table: int, codepoint: int) -> dict[str, Any]:
    table_offset = layout["table_offsets"][table]
    ordinal = BASE.read_u16(data, table_offset + 2 * codepoint)
    if ordinal == 0:
        raise ValueError(f"U+{codepoint:04X} is unmapped/blank in table {table}")
    if ordinal >= layout["record_counts"][table]:
        raise ValueError(f"U+{codepoint:04X} ordinal {ordinal} is out of range in table {table}")
    record_offset = table_offset + 0x20000 + 12 * ordinal
    record = data[record_offset : record_offset + 12]
    height = record[1]
    stride = abs(signed8(record[5]))
    pointer = BASE.read_u32(record, 8)
    pixel_length = stride * height
    pixel_start = layout["atlas_offset"] + pointer
    pixel_end = pixel_start + pixel_length
    if height == 0 or stride == 0 or pixel_start < layout["atlas_offset"] or pixel_end > len(data):
        raise ValueError(f"U+{codepoint:04X} has invalid stock glyph bounds in table {table}")
    pixels = data[pixel_start:pixel_end]
    if not any(pixels):
        raise ValueError(f"U+{codepoint:04X} stock glyph is blank in table {table}")
    return {
        "codepoint": canonical_cp(codepoint),
        "character": chr(codepoint),
        "ordinal": ordinal,
        "record_sha256": sha256_bytes(record),
        "pixel_sha256": sha256_bytes(pixels),
        "pixel_length": pixel_length,
    }


def preflight_stock(stock_blob: bytes, hangul: list[int], non_hangul: list[int]) -> tuple[dict[int, bytes], list[dict[str, Any]]]:
    archive = BASE.LZ4.parse_link(stock_blob)
    if BASE.LZ4.rebuild_link(archive) != stock_blob:
        raise ValueError("stock SC LINK identity roundtrip failed")
    entries: dict[int, bytes] = {}
    coverage: list[dict[str, Any]] = []
    for entry in (6, 7):
        data = BASE.extract_raw_entry(archive, entry, f"SC stock entry {entry}")
        layout = BASE.parse_layout(data, f"SC stock entry {entry}")
        entries[entry] = data
        for table in (0, 1):
            table_offset = layout["table_offsets"][table]
            nonzero_hangul = [cp for cp in hangul if BASE.read_u16(data, table_offset + 2 * cp) != 0]
            if nonzero_hangul:
                preview = ", ".join(canonical_cp(cp) for cp in nonzero_hangul[:8])
                raise ValueError(f"entry {entry} table {table}: demanded Hangul already mapped; refusing overwrite: {preview}")
            stock_proofs = []
            missing = []
            for cp in non_hangul:
                try:
                    stock_proofs.append(mapped_glyph_proof(data, layout, table, cp))
                except ValueError:
                    missing.append(cp)
            if missing:
                preview = ", ".join(f"{canonical_cp(cp)} {chr(cp)!r}" for cp in missing)
                raise ValueError(
                    f"entry {entry} table {table}: demanded non-Hangul lacks nonblank stock coverage: {preview}. "
                    "Replace the translation character or explicitly revise the non-Hangul raster policy."
                )
            coverage.append({
                "entry": entry,
                "table": table,
                "hangul_expected_unmapped_count": len(hangul),
                "hangul_nonzero_count": 0,
                "non_hangul_required_count": len(non_hangul),
                "non_hangul_missing_count": 0,
                "non_hangul_glyphs": stock_proofs,
            })
    return entries, coverage


def raster_request(codepoints: Iterable[int]) -> dict[str, Any]:
    return {
        "schema": "nobu16.kr.font-v3-raster-request.v1",
        "codepoints": [canonical_cp(cp) for cp in codepoints],
        "fonts": {
            key: {"path": lock["relative_path"], "sha256": lock["sha256"]}
            for key, lock in FONT_LOCKS.items()
        },
        "profiles": list(PROFILES),
    }


def run_rasterizer(powershell: Path, request_path: Path, output_dir: Path) -> dict[str, Any]:
    helper = SCRIPT_DIR / "rasterize_font_v3.ps1"
    command = [
        str(powershell), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
        "-File", str(helper), "-Request", str(request_path), "-OutputDirectory", str(output_dir),
    ]
    completed = subprocess.run(command, cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        raise ValueError(
            "font-v3 rasterizer failed\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    result_path = output_dir / "raster_result.json"
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read raster result: {exc}") from exc
    if result.get("schema") != "nobu16.kr.font-v3-raster-result.v1":
        raise ValueError("rasterizer returned unsupported result schema")
    return result


def validate_raster_result(result: dict[str, Any], root: Path, expected_codepoints: list[int]) -> dict[int, bytes]:
    if result.get("codepoints") != [canonical_cp(cp) for cp in expected_codepoints]:
        raise ValueError("raster result codepoint list mismatch")
    payloads: dict[int, bytes] = {}
    expected_count = len(expected_codepoints)
    for item in result.get("payloads", []):
        entry = int(item["entry"])
        if entry not in (6, 7) or entry in payloads:
            raise ValueError("raster result payload entry set is invalid")
        path = root / item["path"]
        data = path.read_bytes()
        cell = 48 if entry == 6 else 32
        expected_size = 2 * expected_count * (cell // 2) * cell
        if len(data) != expected_size or item.get("size") != expected_size:
            raise ValueError(f"entry {entry} raster payload size mismatch")
        if sha256_bytes(data) != item.get("sha256"):
            raise ValueError(f"entry {entry} raster payload hash mismatch")
        payloads[entry] = data
    if set(payloads) != {6, 7}:
        raise ValueError("raster result is missing an entry payload")
    profiles = result.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 4:
        raise ValueError("raster result profile set is invalid")
    for profile in profiles:
        glyphs = profile.get("glyphs")
        if not isinstance(glyphs, list) or len(glyphs) != expected_count:
            raise ValueError("raster profile glyph count mismatch")
        if min(int(row["minimum_margin"]) for row in glyphs) < 1:
            raise ValueError("raster glyph touches a cell edge")
        if any(int(row["ink_count"]) <= 0 for row in glyphs):
            raise ValueError("raster profile contains a blank glyph")
    return payloads


def extract_seed_blocks(full: bytes, codepoints: list[int], entry: int) -> bytes:
    if not set(SEED_CODEPOINTS).issubset(codepoints):
        raise ValueError("demand union does not contain the raster-v2 seed corpus")
    cell = 48 if entry == 6 else 32
    block_size = (cell // 2) * cell
    count = len(codepoints)
    index_by_cp = {cp: index for index, cp in enumerate(codepoints)}
    output = bytearray()
    for table in (0, 1):
        table_start = table * count * block_size
        for cp in SEED_CODEPOINTS:
            start = table_start + index_by_cp[cp] * block_size
            output += full[start : start + block_size]
    return bytes(output)


def build_entry(stock: bytes, pixels: bytes, entry: int, codepoints: list[int]) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    layout = BASE.parse_layout(stock, f"SC entry {entry} stock")
    count = len(codepoints)
    cell = 48 if entry == 6 else 32
    pixel_size = (cell // 2) * cell
    expected_pixels = 2 * count * pixel_size
    if len(pixels) != expected_pixels:
        raise ValueError(f"entry {entry}: pixel payload size mismatch")
    record_add_per_table = 12 * count
    target_offsets = [layout["table_offsets"][0], layout["table_offsets"][1] + record_add_per_table]
    target_atlas_offset = layout["atlas_offset"] + 2 * record_add_per_table
    target_size = len(stock) + 2 * record_add_per_table + expected_pixels
    if any(layout["record_counts"][table] + count > 0xFFFF for table in (0, 1)):
        raise ValueError(f"entry {entry}: 16-bit G1N ordinal capacity exceeded")
    if layout["atlas_length"] + expected_pixels >= 0x10000000:
        raise ValueError(f"entry {entry}: 28-bit raw-font atlas range exceeded")
    if target_size > 0xFFFFFFFF or target_atlas_offset > 0xFFFFFFFF:
        raise ValueError(f"entry {entry}: 32-bit G1N size/offset capacity exceeded")

    output = bytearray(target_size)
    output[: layout["header_size"]] = stock[: layout["header_size"]]
    struct.pack_into("<I", output, 0x08, target_size)
    struct.pack_into("<I", output, 0x14, target_atlas_offset)
    struct.pack_into("<I", output, 0x20, target_offsets[0])
    struct.pack_into("<I", output, 0x24, target_offsets[1])
    table_recipes = []
    table_validation = []
    record_prefix = bytes((cell, cell, 0, cell, cell, 256 - cell // 2, 0, cell))
    for table in (0, 1):
        source_offset = layout["table_offsets"][table]
        target_offset = target_offsets[table]
        table_map = bytearray(stock[source_offset : source_offset + 0x20000])
        old_count = layout["record_counts"][table]
        new_records = bytearray(record_add_per_table)
        map_changes = []
        table_pixel_offset = table * count * pixel_size
        for index, cp in enumerate(codepoints):
            old_ordinal = BASE.read_u16(table_map, 2 * cp)
            if old_ordinal != 0:
                raise ValueError(f"entry {entry} table {table} U+{cp:04X}: refusing to overwrite ordinal {old_ordinal}")
            new_ordinal = old_count + index
            struct.pack_into("<H", table_map, 2 * cp, new_ordinal)
            record_offset = 12 * index
            new_records[record_offset : record_offset + 8] = record_prefix
            atlas_pointer = layout["atlas_length"] + table_pixel_offset + index * pixel_size
            struct.pack_into("<I", new_records, record_offset + 8, atlas_pointer)
            map_changes.append({
                "codepoint": canonical_cp(cp),
                "expected_old_ordinal": 0,
                "new_ordinal": new_ordinal,
            })
        output[target_offset : target_offset + 0x20000] = table_map
        old_records = stock[source_offset + 0x20000 : layout["table_ends"][table]]
        target_record_start = target_offset + 0x20000
        output[target_record_start : target_record_start + len(old_records)] = old_records
        append_start = target_record_start + len(old_records)
        output[append_start : append_start + len(new_records)] = new_records
        table_recipes.append({
            "table": table,
            "source_offset": source_offset,
            "target_offset": target_offset,
            "source_record_count": old_count,
            "target_record_count": old_count + count,
            "map_changes": map_changes,
            "appended_records_hex": bytes(new_records).hex().upper(),
            "appended_records_sha256": sha256_bytes(new_records),
            "pixel_payload_offset": table_pixel_offset,
            "pixel_payload_length": count * pixel_size,
        })
        table_validation.append({
            "table": table,
            "map_changes_exactly_demanded_codepoints": True,
            "map_change_count": count,
            "existing_records_exact": True,
            "appended_record_count": count,
        })

    stock_atlas = stock[layout["atlas_offset"] :]
    output[target_atlas_offset : target_atlas_offset + len(stock_atlas)] = stock_atlas
    output[target_atlas_offset + len(stock_atlas) :] = pixels
    candidate = bytes(output)
    target_layout = BASE.parse_layout(candidate, f"SC entry {entry} target")
    if target_layout["table_offsets"] != target_offsets or target_layout["atlas_offset"] != target_atlas_offset:
        raise ValueError(f"entry {entry}: target structural reparse mismatch")

    # Normalize the only permitted header and map changes, then demand exact
    # identity for every stock-owned byte region.
    normalized_header = bytearray(candidate[: layout["header_size"]])
    for start, end in ((0x08, 0x0C), (0x14, 0x18), (0x24, 0x28)):
        normalized_header[start:end] = stock[start:end]
    if bytes(normalized_header) != stock[: layout["header_size"]]:
        raise ValueError(f"entry {entry}: header changed outside permitted fields")
    for table in (0, 1):
        source_offset = layout["table_offsets"][table]
        target_offset = target_offsets[table]
        normalized_map = bytearray(candidate[target_offset : target_offset + 0x20000])
        for cp in codepoints:
            normalized_map[2 * cp : 2 * cp + 2] = stock[source_offset + 2 * cp : source_offset + 2 * cp + 2]
        if bytes(normalized_map) != stock[source_offset : source_offset + 0x20000]:
            raise ValueError(f"entry {entry} table {table}: map changed outside demand corpus")
        old_records = stock[source_offset + 0x20000 : layout["table_ends"][table]]
        target_record_start = target_offset + 0x20000
        if candidate[target_record_start : target_record_start + len(old_records)] != old_records:
            raise ValueError(f"entry {entry} table {table}: existing records changed")
    if candidate[target_atlas_offset : target_atlas_offset + len(stock_atlas)] != stock_atlas:
        raise ValueError(f"entry {entry}: stock atlas prefix changed")
    if candidate[target_atlas_offset + len(stock_atlas) :] != pixels:
        raise ValueError(f"entry {entry}: appended pixel tail mismatch")

    recipe = {
        "entry": entry,
        "stock": {
            "size": len(stock),
            "sha256": sha256_bytes(stock),
            "header_size": layout["header_size"],
            "palette_count": layout["palette_count"],
            "table_offsets": layout["table_offsets"],
            "atlas_offset": layout["atlas_offset"],
            "atlas_length": layout["atlas_length"],
        },
        "target": {
            "size": len(candidate),
            "sha256": sha256_bytes(candidate),
            "table_offsets": target_offsets,
            "atlas_offset": target_atlas_offset,
        },
        "tables": table_recipes,
        "pixel_payload": {
            "file": f"payload/glyph_pixels_entry_{entry}.bin",
            "size": len(pixels),
            "sha256": sha256_bytes(pixels),
            "cell": cell,
            "bytes_per_glyph": pixel_size,
            "glyph_count_per_table": count,
            "table_order": [0, 1],
        },
        "preservation_contract": {
            "header_changes_only": ["declared_file_size", "atlas_offset", "table_1_offset"],
            "palette_blob_exact": True,
            "maps_unchanged_outside_demanded_hangul_codepoints": True,
            "existing_records_exact": True,
            "complete_stock_atlas_exact_prefix": True,
        },
    }
    rebuilt = BASE.build_g1n_from_recipe(stock, recipe, pixels, f"font-v3 entry {entry} clean recipe")
    if rebuilt != candidate:
        raise ValueError(f"entry {entry}: existing file-only applier API did not reproduce candidate")
    validation = {
        "entry": entry,
        "stock_sha256": sha256_bytes(stock),
        "target_sha256": sha256_bytes(candidate),
        "stock_size": len(stock),
        "target_size": len(candidate),
        "header_allowed_changes_only": True,
        "palette_exact": True,
        "maps_exact_outside_corpus": True,
        "existing_records_exact": True,
        "stock_atlas_prefix_exact": True,
        "appended_pixels_exact": True,
        "clean_recipe_reproduction_exact": True,
        "tables": table_validation,
    }
    return candidate, recipe, validation


def relative_project_path(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def build(args: argparse.Namespace) -> int:
    demand_root = Path(args.demand_root).resolve()
    if args.demand_file:
        demand_paths = [Path(item).resolve() for item in args.demand_file]
    else:
        demand_paths = list(demand_root.glob("*/glyph_demand.json"))
    union = demand_union(demand_paths)
    if union["hangul_count"] == 0:
        raise ValueError("demand union contains no Hangul syllables")

    stock_path = Path(args.stock_archive).resolve()
    require_hash(stock_path, STOCK_ARCHIVE_SHA256, "stock SC res_lang.bin")
    stock_blob = stock_path.read_bytes()
    stock_hash_before = sha256_bytes(stock_blob)
    for name, lock in FONT_LOCKS.items():
        require_hash(PROJECT_ROOT / lock["relative_path"], lock["sha256"], f"pinned Noto {name}")
        require_hash(PROJECT_ROOT / lock["license_relative_path"], lock["license_sha256"], f"Noto {name} OFL")

    stock_entries, non_hangul_coverage = preflight_stock(stock_blob, union["hangul"], union["non_hangul"])

    output_root = Path(args.output_root).resolve()
    if output_root == PROJECT_ROOT or output_root == stock_path.parent:
        raise ValueError("refusing unsafe output root")
    if output_root.exists() and any(output_root.iterdir()):
        raise ValueError(f"output root must be absent or empty: {output_root}")
    public_root = output_root / "public"
    private_root = output_root / "private"
    raster_full_root = private_root / "raster_full"
    raster_seed_root = private_root / "raster_seed_regression"
    public_payload = public_root / "payload"
    public_licenses = public_root / "licenses"
    public_metrics = public_root / "metrics"
    for path in (raster_full_root, raster_seed_root, public_payload, public_licenses, public_metrics):
        path.mkdir(parents=True, exist_ok=True)

    full_request_path = private_root / "raster_request_full.json"
    seed_request_path = private_root / "raster_request_seed.json"
    write_json(full_request_path, raster_request(union["hangul"]))
    write_json(seed_request_path, raster_request(SEED_CODEPOINTS))
    powershell = Path(args.powershell).resolve()
    if not powershell.is_file():
        raise ValueError(f"PowerShell executable is missing: {powershell}")
    full_result = run_rasterizer(powershell, full_request_path, raster_full_root)
    seed_result = run_rasterizer(powershell, seed_request_path, raster_seed_root)
    full_pixels = validate_raster_result(full_result, raster_full_root, union["hangul"])
    seed_pixels = validate_raster_result(seed_result, raster_seed_root, list(SEED_CODEPOINTS))
    seed_regression = []
    for entry in (6, 7):
        seed_sha = sha256_bytes(seed_pixels[entry])
        if seed_sha != SEED_RASTER_V2_PAYLOAD_SHA256[entry]:
            raise ValueError(
                f"entry {entry}: raster-v2 seed regression drift; "
                f"expected={SEED_RASTER_V2_PAYLOAD_SHA256[entry]} actual={seed_sha}"
            )
        extracted = extract_seed_blocks(full_pixels[entry], union["hangul"], entry)
        if extracted != seed_pixels[entry]:
            raise ValueError(f"entry {entry}: full-corpus raster differs from isolated seed raster")
        seed_regression.append({
            "entry": entry,
            "seed_glyph_count_per_table": len(SEED_CODEPOINTS),
            "expected_raster_v2_payload_sha256": SEED_RASTER_V2_PAYLOAD_SHA256[entry],
            "actual_seed_payload_sha256": seed_sha,
            "exact": True,
            "full_corpus_seed_blocks_exact": True,
        })

    candidates: dict[int, bytes] = {}
    entry_recipes: dict[str, Any] = {}
    entry_validations = []
    for entry in (6, 7):
        candidate, entry_recipe, validation = build_entry(stock_entries[entry], full_pixels[entry], entry, union["hangul"])
        candidates[entry] = candidate
        entry_recipes[str(entry)] = entry_recipe
        entry_validations.append(validation)
        atomic_write(private_root / "candidate" / f"SC_{entry}.font-v3.g1n", candidate)
        atomic_write(public_payload / f"glyph_pixels_entry_{entry}.bin", full_pixels[entry])

    candidate_archive = BASE.build_candidate_archive(stock_blob, candidates)
    parsed_candidate = BASE.LZ4.parse_link(candidate_archive)
    if BASE.LZ4.rebuild_link(parsed_candidate) != candidate_archive:
        raise ValueError("font-v3 candidate LINK identity roundtrip failed")
    stock_archive = BASE.LZ4.parse_link(stock_blob)
    for index, stock_entry in enumerate(stock_archive.entries):
        if index in (6, 7):
            if BASE.extract_raw_entry(parsed_candidate, index, f"candidate entry {index}") != candidates[index]:
                raise ValueError(f"candidate LINK entry {index} re-extraction mismatch")
        elif parsed_candidate.entries[index].data != stock_entry.data:
            raise ValueError(f"candidate LINK untouched entry {index} changed")
    private_archive_path = private_root / "candidate" / "res_lang.SC.font-v3.bin"
    atomic_write(private_archive_path, candidate_archive)

    for key, target_name in (("sans", "OFL-NotoSansKR.txt"), ("serif", "OFL-NotoSerifKR.txt")):
        source = PROJECT_ROOT / FONT_LOCKS[key]["license_relative_path"]
        target = public_licenses / target_name
        shutil.copyfile(source, target)
        require_hash(target, FONT_LOCKS[key]["license_sha256"], f"copied {key} OFL")

    inventory = []
    for path, origin in (
        (public_payload / "glyph_pixels_entry_6.bin", "generated OFL Noto glyph pixels"),
        (public_payload / "glyph_pixels_entry_7.bin", "generated OFL Noto glyph pixels"),
        (public_licenses / "OFL-NotoSansKR.txt", "SIL Open Font License text"),
        (public_licenses / "OFL-NotoSerifKR.txt", "SIL Open Font License text"),
    ):
        inventory.append({
            "path": path.relative_to(public_root).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
            "origin": origin,
        })

    recipe = {
        "schema": "nobu16.file-only-g1n-tail-recipe.v1",
        "file_only": True,
        "runtime_patch_features": [],
        "process_memory_access": False,
        "registry_access": False,
        "installed_game_files_modified": False,
        "release_eligible": False,
        "runtime_direct_lookup_verified": False,
        "release_blocker": "P3 font-v3 candidate requires in-game SC runtime render/exit validation before release eligibility",
        "corpus": {
            "schema": "nobu16.kr.font-v3-corpus-union.v1",
            "sources": union["sources"],
            "character_count": union["codepoint_count"],
            "hangul_syllable_count": union["hangul_count"],
            "non_hangul_stock_covered_count": union["non_hangul_count"],
            "union_codepoints_sha256": union["union_sha256"],
            "hangul_codepoints_sha256": union["hangul_sha256"],
            "raster_codepoints": [canonical_cp(cp) for cp in union["hangul"]],
        },
        "font_provenance": {
            "family": "Noto Sans KR / Noto Serif KR",
            "license": "SIL Open Font License 1.1",
            "repository": "https://github.com/google/fonts",
            "google_fonts_commit": "ec0464b978de222073645d6d3366f3fdf03376d8",
            "source_fonts": {
                Path(lock["relative_path"]).name: {"sha256": lock["sha256"]}
                for lock in FONT_LOCKS.values()
            },
            "profiles": list(PROFILES),
            "raster_method": "raster-v2-compatible 2x scratch GDI+ raster, complete ink extraction, unscaled centered 4bpp copy",
        },
        "payload_policy": {
            "commercial_original_bytes_in_public_payload": False,
            "stock_archive_required_at_apply_time": True,
            "binary_payload_origin": "OFL Noto Korean glyph pixels rasterized from pinned fonts",
            "structural_payload": "demanded Hangul map writes plus generated 12-byte records; stock palettes, old maps, old records, and stock atlas are absent",
            "private_candidates_for_validation_only": True,
        },
        "payload_inventory": inventory,
        "languages": {
            "SC": {
                "stock_archive": {
                    "path": "RES_SC/res_lang.bin",
                    "size": len(stock_blob),
                    "sha256": STOCK_ARCHIVE_SHA256,
                },
                "target_archive": {
                    "relative_path": "private/candidate/res_lang.SC.font-v3.bin",
                    "size": len(candidate_archive),
                    "sha256": sha256_bytes(candidate_archive),
                },
                "entries": entry_recipes,
                "export_archive_self_test": {
                    "rebuilt_sha256": sha256_bytes(candidate_archive),
                    "link_roundtrip_exact": True,
                    "untouched_link_entries_exact": True,
                    "entries_6_7_reextract_exact": True,
                },
            }
        },
    }
    recipe_path = public_root / "recipe.json"
    write_json(recipe_path, recipe)

    # Exercise the existing public file-only loader/apply path, not merely this
    # builder's own reconstruction logic.  All outputs remain private.
    loaded = BASE.load_recipe(recipe_path)
    if loaded["corpus"]["hangul_syllable_count"] != union["hangul_count"]:
        raise ValueError("existing applier recipe loader corpus mismatch")
    applier_root = private_root / "existing_applier_selftest"
    apply_result = BASE.apply_recipe(SimpleNamespace(
        language="SC",
        recipe=str(recipe_path),
        stock_archive=str(stock_path),
        output_dir=str(applier_root),
    ))
    if apply_result != 0:
        raise ValueError("existing file-only applier self-test returned failure")
    applier_archive = applier_root / "res_lang.SC.pinned_noto.recipe.bin"
    if applier_archive.read_bytes() != candidate_archive:
        raise ValueError("existing file-only applier output is not byte-identical to font-v3 candidate")

    metric_lines = []
    for profile in sorted(full_result["profiles"], key=lambda item: (int(item["entry"]), int(item["table"]))):
        for glyph in profile["glyphs"]:
            row = {
                "entry": int(profile["entry"]),
                "table": int(profile["table"]),
                "family": profile["family"],
                "style": profile["style"],
                "raster_size": int(profile["raster_size"]),
                "cell": int(profile["cell"]),
                **glyph,
            }
            metric_lines.append(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    atomic_write(public_metrics / "glyphs.jsonl", ("\n".join(metric_lines) + "\n").encode("utf-8"))

    stock_hash_after = sha256_file(stock_path)
    if stock_hash_after != stock_hash_before:
        raise ValueError("stock archive changed during read-only font-v3 build")
    validation = {
        "schema": "nobu16.kr.font-v3-validation.v1",
        "passed": True,
        "demand_contract": {
            "schema_valid": True,
            "source_order_deterministic": True,
            "nfc": True,
            "unique_sorted_bmp_codepoints": True,
            "source_count": len(union["sources"]),
            "union_character_count": union["codepoint_count"],
            "raster_hangul_count": union["hangul_count"],
        },
        "stock_coverage": {
            "policy": "Hangul must be ordinal 0 before append; every demanded non-Hangul must have a nonzero, nonblank stock glyph in all four entry/table maps",
            "passed": True,
            "tables": non_hangul_coverage,
        },
        "raster": {
            "profiles_exactly_raster_v2": True,
            "minimum_cell_margin": min(
                int(glyph["minimum_margin"])
                for profile in full_result["profiles"] for glyph in profile["glyphs"]
            ),
            "blank_glyph_count": 0,
            "seed_regression": seed_regression,
        },
        "entries": entry_validations,
        "archive": {
            "sha256": sha256_bytes(candidate_archive),
            "link_roundtrip_exact": True,
            "untouched_link_entries_exact": True,
            "entries_6_7_reextract_exact": True,
        },
        "existing_file_only_applier": {
            "recipe_schema_accepted": True,
            "apply_return_code": apply_result,
            "candidate_archive_byte_identical": True,
        },
        "stock_archive_sha256_before": stock_hash_before,
        "stock_archive_sha256_after": stock_hash_after,
        "stock_archive_unchanged": True,
        "installed_game_files_modified": False,
        "process_memory_access": False,
        "registry_access": False,
        "runtime_patch_features": [],
        "commercial_full_resources_in_public_tree": False,
        "private_candidate_distribution_forbidden": True,
        "runtime_verified": False,
        "release_eligible": False,
    }
    validation_path = public_root / "validation.json"
    write_json(validation_path, validation)

    allowed_public = {
        "licenses/OFL-NotoSansKR.txt",
        "licenses/OFL-NotoSerifKR.txt",
        "metrics/glyphs.jsonl",
        "payload/glyph_pixels_entry_6.bin",
        "payload/glyph_pixels_entry_7.bin",
        "recipe.json",
        "validation.json",
    }
    actual_public = {path.relative_to(public_root).as_posix() for path in public_root.rglob("*") if path.is_file()}
    if actual_public != allowed_public:
        raise ValueError(f"public tree allowlist mismatch: {sorted(actual_public ^ allowed_public)}")
    if any(path.suffix.lower() in {".g1n", ".exe", ".dll"} for path in public_root.rglob("*") if path.is_file()):
        raise ValueError("commercial/native binary type escaped into public tree")

    manifest = {
        "schema": "nobu16.kr.font-v3-build-manifest.v1",
        "target_language": "SC",
        "file_only": True,
        "corpus": {
            "sources": union["sources"],
            "character_count": union["codepoint_count"],
            "hangul_syllable_count": union["hangul_count"],
            "non_hangul_stock_covered_count": union["non_hangul_count"],
            "union_codepoints_sha256": union["union_sha256"],
            "hangul_codepoints_sha256": union["hangul_sha256"],
        },
        "inputs": {
            "stock_archive": {"path": "RES_SC/res_lang.bin", "sha256": stock_hash_before},
            "fonts": {key: {"path": lock["relative_path"], "sha256": lock["sha256"]} for key, lock in FONT_LOCKS.items()},
            "builder": {"path": relative_project_path(Path(__file__)), "sha256": sha256_file(Path(__file__))},
            "rasterizer": {"path": relative_project_path(SCRIPT_DIR / "rasterize_font_v3.ps1"), "sha256": sha256_file(SCRIPT_DIR / "rasterize_font_v3.ps1")},
            "existing_file_only_applier": {"path": relative_project_path(TOOLS_DIR / "build_file_only_font_recipe.py"), "sha256": sha256_file(TOOLS_DIR / "build_file_only_font_recipe.py")},
        },
        "outputs": {
            "public_recipe": {"path": "public/recipe.json", "sha256": sha256_file(recipe_path)},
            "public_validation": {"path": "public/validation.json", "sha256": sha256_file(validation_path)},
            "public_metrics": {"path": "public/metrics/glyphs.jsonl", "sha256": sha256_file(public_metrics / "glyphs.jsonl")},
            "public_payload_inventory": inventory,
            "private_candidate_archive": {
                "path": "private/candidate/res_lang.SC.font-v3.bin",
                "sha256": sha256_bytes(candidate_archive),
                "distribution_forbidden": True,
            },
        },
        "determinism": {
            "input_paths_and_hashes_sorted": True,
            "codepoints_unique_sorted": True,
            "raster_v2_seed_hash_regression_exact": True,
            "full_corpus_seed_blocks_exact": True,
            "clean_recipe_reproduction_exact": True,
            "existing_applier_archive_byte_identical": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "process_memory_access": False,
            "registry_access": False,
            "runtime_patch_features": [],
            "commercial_full_resources_in_public_tree": False,
            "private_candidate_distribution_forbidden": True,
        },
        "runtime_verified": False,
        "release_eligible": False,
    }
    manifest_path = output_root / "manifest.json"
    write_json(manifest_path, manifest)

    print(f"output_root={output_root}")
    print(f"demand_sources={len(union['sources'])}")
    print(f"characters={union['codepoint_count']}")
    print(f"hangul_raster_glyphs={union['hangul_count']}")
    print(f"non_hangul_stock_covered={union['non_hangul_count']}")
    print(f"candidate_archive_sha256={sha256_bytes(candidate_archive)}")
    print(f"recipe_sha256={sha256_file(recipe_path)}")
    print("raster_v2_seed_regression=OK")
    print("append_tail_validation=OK")
    print("existing_file_only_applier_roundtrip=OK")
    print("installed_game_files_modified=False")
    print("process_memory_access=False")
    print("registry_access=False")
    print("release_eligible=False")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--demand-root", default=str(DEFAULT_DEMAND_ROOT))
    result.add_argument("--demand-file", action="append", help="Use only these demand files; repeatable. Default scans demand-root/*/glyph_demand.json.")
    result.add_argument("--stock-archive", default=str(STOCK_ARCHIVE))
    result.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    result.add_argument(
        "--powershell",
        default=str(Path(os.environ.get("WINDIR", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"),
    )
    return result


def main() -> int:
    try:
        return build(parser().parse_args())
    except (OSError, ValueError, RuntimeError, BASE.LZ4.LZ4Error, BASE.LZ4.LinkError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
