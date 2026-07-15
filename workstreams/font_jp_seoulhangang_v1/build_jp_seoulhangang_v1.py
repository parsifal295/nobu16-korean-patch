#!/usr/bin/env python3
"""Build and verify private JP-base SeoulHangang G1N candidates for NOBU16 PK.

This pipeline builds both JP font routes statically present in the examined
local non-Steam PK executable as a conservative candidate set.  A current
Steam runtime file-open trace has not yet proven that both are required:

* ``RES_JP/res_lang.bin`` outer G1N entries 6 and 7; and
* ``RES_JP_PK/res_lang_pk.bin`` outer G1N entries 16 and 17.

Every target is a three-table JP G1N.  The stock record geometry proves the
real table hierarchy is ``48/48/48`` for entry 6/16 and ``32/48/32`` for
entry 7/17.  Demanded Korean glyphs are therefore rasterized from SHA-pinned
official SeoulHangang EB for every 48-cell table and SeoulHangang B for every
32-cell table.  There is no third, smaller cell tier in these four G1Ns, so
SeoulHangang M is pinned as the unused contingency source rather than being
silently substituted.  A strict TTF cmap gate prevents GDI font fallback.
The two reviewed non-TTF points U+32A4/U+FF65 are copied from each G1N's
same-cell stock table 0 into a new table-2 atlas tail and never pointer-aliased.
Existing mappings, records, palettes, and the complete stock atlas remain
byte-identical.  Every non-target LINK entry remains byte-identical.

The program never overwrites an input or an installed game file.  Private
candidates may only be written below the repository ``tmp`` directory (or an
external directory outside the game tree).  It has no process-memory,
registry, executable-modification, or runtime-injection path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
GAME_ROOT = REPO_ROOT.parent
sys.dont_write_bytecode = True


class JPFontBuildError(ValueError):
    """Raised when a private input or preservation contract fails."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Reuse the reviewed translation-demand loader, official TTF gate, GDI+
# rasterizer, and LINK/LZ4 codec.  The JP three-table append implementation is
# deliberately local to this workstream.
SC_FONT = load_module(
    "nobu16_jp_seoulhangang_v1_demand_and_raster_base",
    REPO_ROOT / "workstreams" / "font_seoulhangang_v1" / "build_seoulhangang_v1.py",
)
LZ4 = SC_FONT.V6.BASE.LZ4
DEMAND_REFRESH = load_module(
    "nobu16_jp_seoulhangang_v1_current_demand",
    REPO_ROOT / "workstreams" / "font_seoulhangang_v1" / "refresh_demand_pin.py",
)


SCHEMA_PLAN = "nobu16.kr.font-jp-seoulhangang-v1-plan.v1"
SCHEMA_BUILD = "nobu16.kr.font-jp-seoulhangang-v1-private-build.v1"
SCHEMA_EVIDENCE = "nobu16.kr.font-jp-seoulhangang-v1-verification.v1"
G1N_MAGIC = b"_N1G0000"
MAP_ENTRIES = 0x10000
MAP_SIZE = MAP_ENTRIES * 2
RECORD_SIZE = 12
PALETTE_SIZE = 0x40
TABLE_COUNT = 3


FONT_PROFILES: dict[str, dict[str, Any]] = {
    "eb48": {
        "source_entry": 6,
        "cell": 48,
        "raster_size": 46,
        "font_key": "entry6_48px_eb",
        "font": "SeoulHangang EB",
    },
    "b32": {
        "source_entry": 7,
        "cell": 32,
        "raster_size": 32,
        "font_key": "entry7_32px_b",
        "font": "SeoulHangang B",
    },
}

# This is an official member of the same SHA-pinned Seoul archive.  It is not
# used because none of the four target G1Ns has a cell smaller than 32 pixels.
SEOUL_HANGANG_M = {
    "file_name": "SeoulHangangM.ttf",
    "size": 7_627_124,
    "sha256": "D27E1B26B55E507BEC1045962C954CF426D79605009C720FAD1C9EF808E312CB",
    "family": "SeoulHangang M",
    "weight": "Medium",
    "used": False,
    "reason": "no target JP G1N table has a cell smaller than 32 pixels",
}

# The five batches are committed before the shared translation-progress row is
# refreshed.  Canonical in-memory insertion makes demand and candidate bytes
# identical before and after those same paths are registered centrally.
PENDING_OVERLAYS: tuple[dict[str, str], ...] = (
    {
        "resource": "MSG_PK/SC/msgdata.bin",
        "path": "workstreams/msgdata_pk_structural_review_b12/public/msgdata_ko_pk_structural_review_b12_500.v1.json",
    },
    {
        "resource": "MSG_PK/SC/msgdata.bin",
        "path": "workstreams/msgdata_pk_structural_review_b13/public/msgdata_ko_pk_structural_review_b13_500.v1.json",
    },
    {
        "resource": "MSG_PK/SC/msgdata.bin",
        "path": "workstreams/msgdata_pk_structural_review_b14/public/msgdata_ko_pk_structural_review_b14_500.v1.json",
    },
    {
        "resource": "MSG_PK/SC/msgdata.bin",
        "path": "workstreams/msgdata_pk_structural_review_b15/public/msgdata_ko_pk_structural_review_b15_final_110.v1.json",
    },
    {
        "resource": "MSG_PK/SC/msggame.bin",
        "path": "workstreams/msggame_pk_ui_priority_b07/public/msggame_ko_pk_ui_priority_b07_300.v1.json",
    },
)

EXPECTED_FONT_RESOURCES = DEMAND_REFRESH.EXPECTED_FONT_RESOURCES

# A stock G1N has one 65,536-codepoint map per table.  Bytes 1, 3, and
# 7 of every 12-byte record independently agree on the cell height.  Entry 7
# is intentionally mixed: table 1 is a 48-cell table between two 32-cell
# tables.  Width variation in byte 0 is glyph advance/storage packing, not a
# separate font tier.
PROFILE_TABLES: dict[int, tuple[str, str, str]] = {
    6: ("eb48", "eb48", "eb48"),
    7: ("b32", "eb48", "b32"),
}


ROUTES: dict[str, dict[str, Any]] = {
    "base": {
        "logical_path": "RES_JP/res_lang.bin",
        "size": 153_198_542,
        "sha256": "D32898C186CBDC7534692269C062E888ACE3B7A58F5DB4FEC8B0C745DADAAE53",
        "candidate_relative_path": "private/candidate/RES_JP/res_lang.bin",
        "targets": (
            {"outer_entry": 6, "profile_entry": 6},
            {"outer_entry": 7, "profile_entry": 7},
        ),
    },
    "pk": {
        "logical_path": "RES_JP_PK/res_lang_pk.bin",
        "size": 140_729_547,
        "sha256": "67CC064ED9D138B85255F8AA6AC5B5E47D7239E06E15A4E5AD68922274300EF5",
        "candidate_relative_path": "private/candidate/RES_JP_PK/res_lang_pk.bin",
        "targets": (
            {"outer_entry": 16, "profile_entry": 6},
            {"outer_entry": 17, "profile_entry": 7},
        ),
    },
}


DEMAND_LOCK: dict[str, Any] = {
    "source_catalog_sha256": "436876571A1ABE251C3756566ACC9D95523000FEABEDFB70C10F6E3332AA8A6F",
    "source_count": 118,
    "source_entry_count": 83_658,
    "codepoint_count": 1_419,
    "codepoints_sha256": "31941A7119F571E227A96ED2B99427D13A379B1623E82EBF703B8D3B5D1A654B",
    "hangul_syllable_count": 1_247,
    "hangul_syllables_sha256": "974C4F799512A3442A28AE94785F6BDD7C9103F54FF0993C223507AD91A9BC2B",
    "non_hangul_count": 172,
    "non_hangul_sha256": "0F5F778AAF5D219483B3F91B3995AD144E236B4563555E3B06BB0D6820F8D42E",
}


APPEND_UNION_LOCK = {
    "codepoint_count": 1_308,
    "codepoints_sha256": "4C8398A11D1512DBFE1B3793E7CD2DCBA8C14001C44663C986B1950EC0F65A34",
}


STOCK_REUSE_CODEPOINTS = (0x32A4, 0xFF65)
STOCK_REUSE_LOCK = {
    "codepoint_count": 2,
    "codepoints_sha256": "56FA9232EA268ED0FE5B776534B5B7A1A09DBCEAAC8D1E8C27A5EE5E68F13BE4",
}


TTF_RASTER_LOCK = {
    "codepoint_count": 1_306,
    "codepoints_sha256": "E056B7630AE5055647421C5F53ABADC7BD49B9FE44E5BA8DF4421503D32888C6",
}


APPEND_LOCK = {
    0: {
        "count": 1_251,
        "codepoints_sha256": "72EE29EA5727A8B8DCA99D088CD99F960902F2406910EC0B48BF1AF2416EA72B",
    },
    1: {
        "count": 1_251,
        "codepoints_sha256": "72EE29EA5727A8B8DCA99D088CD99F960902F2406910EC0B48BF1AF2416EA72B",
    },
    2: {
        "count": 1_308,
        "codepoints_sha256": "4C8398A11D1512DBFE1B3793E7CD2DCBA8C14001C44663C986B1950EC0F65A34",
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_cp(codepoint: int) -> str:
    return f"U+{codepoint:04X}"


def canonical_codepoint_hash(codepoints: Iterable[int]) -> str:
    return sha256_bytes(
        "".join(f"{canonical_cp(codepoint)}\n" for codepoint in sorted(codepoints)).encode("ascii")
    )


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")


def strict_json(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        folded: set[str] = set()
        for key, value in pairs:
            lowered = key.casefold()
            if key in result or lowered in folded:
                raise JPFontBuildError(f"{path}: duplicate/case-colliding JSON key {key!r}")
            result[key] = value
            folded.add(lowered)
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicates,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JPFontBuildError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise JPFontBuildError(f"{path}: top-level JSON must be an object")
    return value


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


def read_u16(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_u32(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _be_u16(data: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise JPFontBuildError(f"{label}: truncated big-endian u16 at 0x{offset:X}")
    return struct.unpack_from(">H", data, offset)[0]


def _be_i16(data: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise JPFontBuildError(f"{label}: truncated big-endian i16 at 0x{offset:X}")
    return struct.unpack_from(">h", data, offset)[0]


def _be_u32(data: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise JPFontBuildError(f"{label}: truncated big-endian u32 at 0x{offset:X}")
    return struct.unpack_from(">I", data, offset)[0]


def parse_unicode_cmap(font: bytes, label: str) -> list[dict[str, Any]]:
    """Parse supported Unicode cmap subtables without invoking OS fallback."""

    if len(font) < 12 or font[:4] not in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
        raise JPFontBuildError(f"{label}: unsupported or truncated SFNT")
    table_count = _be_u16(font, 4, label)
    if not 1 <= table_count <= 4096 or 12 + 16 * table_count > len(font):
        raise JPFontBuildError(f"{label}: malformed SFNT table directory")
    tables: dict[bytes, tuple[int, int]] = {}
    for index in range(table_count):
        record = 12 + 16 * index
        tag = font[record : record + 4]
        offset = _be_u32(font, record + 8, label)
        length = _be_u32(font, record + 12, label)
        if tag in tables or offset + length > len(font):
            raise JPFontBuildError(f"{label}: duplicate or out-of-range SFNT table {tag!r}")
        tables[tag] = (offset, length)
    if b"cmap" not in tables:
        raise JPFontBuildError(f"{label}: missing cmap table")
    cmap_offset, cmap_length = tables[b"cmap"]
    cmap = font[cmap_offset : cmap_offset + cmap_length]
    if len(cmap) < 4 or _be_u16(cmap, 0, label) != 0:
        raise JPFontBuildError(f"{label}: malformed cmap header")
    record_count = _be_u16(cmap, 2, label)
    if 4 + 8 * record_count > len(cmap):
        raise JPFontBuildError(f"{label}: truncated cmap encoding records")
    result: list[dict[str, Any]] = []
    for index in range(record_count):
        record = 4 + 8 * index
        platform = _be_u16(cmap, record, label)
        encoding = _be_u16(cmap, record + 2, label)
        relative = _be_u32(cmap, record + 4, label)
        is_unicode = platform == 0 or (platform == 3 and encoding in (1, 10))
        if not is_unicode:
            continue
        if relative + 2 > len(cmap):
            raise JPFontBuildError(f"{label}: cmap subtable offset is out of range")
        fmt = _be_u16(cmap, relative, label)
        if fmt in (0, 2, 4, 6):
            length = _be_u16(cmap, relative + 2, label)
        elif fmt in (8, 10, 12, 13, 14):
            length = _be_u32(cmap, relative + 4, label)
        else:
            raise JPFontBuildError(f"{label}: unsupported Unicode cmap format {fmt}")
        if length < 4 or relative + length > len(cmap):
            raise JPFontBuildError(f"{label}: malformed Unicode cmap format {fmt}")
        # Only formats with explicit scalar-to-glyph mappings are accepted for
        # the fallback gate.  Format 14 is variation-selector metadata.
        if fmt not in (0, 4, 6, 12, 13):
            continue
        result.append(
            {
                "platform": platform,
                "encoding": encoding,
                "format": fmt,
                "data": cmap[relative : relative + length],
            }
        )
    if not result:
        raise JPFontBuildError(f"{label}: no supported Unicode cmap subtable")
    return result


def cmap_glyph_id(subtable: dict[str, Any], codepoint: int, label: str) -> int:
    data = subtable["data"]
    fmt = int(subtable["format"])
    if fmt == 0:
        if len(data) < 262 or not 0 <= codepoint <= 0xFF:
            return 0
        return data[6 + codepoint]
    if fmt == 6:
        if len(data) < 10 or codepoint > 0xFFFF:
            return 0
        first = _be_u16(data, 6, label)
        count = _be_u16(data, 8, label)
        if 10 + 2 * count > len(data) or not first <= codepoint < first + count:
            return 0
        return _be_u16(data, 10 + 2 * (codepoint - first), label)
    if fmt == 4:
        if codepoint > 0xFFFF or len(data) < 16:
            return 0
        segment_count_x2 = _be_u16(data, 6, label)
        if not segment_count_x2 or segment_count_x2 % 2:
            raise JPFontBuildError(f"{label}: malformed cmap format 4 segment count")
        count = segment_count_x2 // 2
        end_offset = 14
        start_offset = end_offset + 2 * count + 2
        delta_offset = start_offset + 2 * count
        range_offset = delta_offset + 2 * count
        if range_offset + 2 * count > len(data):
            raise JPFontBuildError(f"{label}: truncated cmap format 4 arrays")
        for segment in range(count):
            end = _be_u16(data, end_offset + 2 * segment, label)
            if codepoint > end:
                continue
            start = _be_u16(data, start_offset + 2 * segment, label)
            if codepoint < start:
                return 0
            delta = _be_i16(data, delta_offset + 2 * segment, label)
            range_word = range_offset + 2 * segment
            distance = _be_u16(data, range_word, label)
            if distance == 0:
                return (codepoint + delta) & 0xFFFF
            glyph_offset = range_word + distance + 2 * (codepoint - start)
            glyph = _be_u16(data, glyph_offset, label)
            return (glyph + delta) & 0xFFFF if glyph else 0
        return 0
    if fmt in (12, 13):
        if len(data) < 16:
            raise JPFontBuildError(f"{label}: truncated cmap format {fmt}")
        group_count = _be_u32(data, 12, label)
        if 16 + 12 * group_count > len(data):
            raise JPFontBuildError(f"{label}: truncated cmap format {fmt} groups")
        low, high = 0, group_count
        while low < high:
            middle = (low + high) // 2
            group = 16 + 12 * middle
            start = _be_u32(data, group, label)
            end = _be_u32(data, group + 4, label)
            if codepoint < start:
                high = middle
            elif codepoint > end:
                low = middle + 1
            else:
                first_glyph = _be_u32(data, group + 8, label)
                return first_glyph if fmt == 13 else first_glyph + codepoint - start
        return 0
    raise JPFontBuildError(f"{label}: internal unsupported cmap format {fmt}")


def validate_official_font_cmaps(
    font_paths: dict[str, Path], append_union: Sequence[int]
) -> list[dict[str, Any]]:
    """Require exact cmap coverage and return a source-free coverage report."""

    expected_missing = set(STOCK_REUSE_CODEPOINTS)
    if canonical_codepoint_hash(expected_missing) != STOCK_REUSE_LOCK["codepoints_sha256"]:
        raise JPFontBuildError("internal stock-reuse codepoint lock mismatch")
    reports: list[dict[str, Any]] = []
    for profile_key in ("eb48", "b32"):
        font_key = FONT_PROFILES[profile_key]["font_key"]
        path = font_paths[font_key]
        subtables = parse_unicode_cmap(path.read_bytes(), f"official {font_key}")
        covered = {
            cp
            for cp in append_union
            if any(cmap_glyph_id(row, cp, f"official {font_key}") for row in subtables)
        }
        missing = set(append_union) - covered
        if missing != expected_missing:
            unexpected = sorted(missing - expected_missing)
            unexpectedly_present = sorted(expected_missing - missing)
            raise JPFontBuildError(
                f"official {font_key} cmap mismatch: unexpected missing="
                f"{[canonical_cp(cp) for cp in unexpected]}; expected stock-reuse now present="
                f"{[canonical_cp(cp) for cp in unexpectedly_present]}"
            )
        reports.append(
            {
                "profile": profile_key,
                "font_key": font_key,
                "font_sha256": sha256_file(path),
                "unicode_cmap_records": [
                    {
                        "platform": row["platform"],
                        "encoding": row["encoding"],
                        "format": row["format"],
                    }
                    for row in subtables
                ],
                "append_union_count": len(append_union),
                "cmap_covered_count": len(covered),
                "cmap_covered_sha256": canonical_codepoint_hash(covered),
                "cmap_missing_count": len(missing),
                "cmap_missing_sha256": canonical_codepoint_hash(missing),
                "cmap_missing": [canonical_cp(cp) for cp in sorted(missing)],
                "gdi_fallback_forbidden": True,
            }
        )
    return reports


def parse_layout(data: bytes, label: str) -> dict[str, Any]:
    """Strictly parse the three-table JP G1N layout."""

    if len(data) < 0x2C or data[:8] != G1N_MAGIC:
        raise JPFontBuildError(f"{label}: not a G1N")
    declared_size = read_u32(data, 0x08)
    header_size = read_u32(data, 0x0C)
    unknown = read_u32(data, 0x10)
    atlas_offset = read_u32(data, 0x14)
    palette_count = read_u32(data, 0x18)
    table_count = read_u32(data, 0x1C)
    if declared_size != len(data):
        raise JPFontBuildError(f"{label}: declared size mismatch")
    if table_count != TABLE_COUNT:
        raise JPFontBuildError(
            f"{label}: expected {TABLE_COUNT} JP tables, found {table_count}"
        )
    expected_header_size = 0x20 + 4 * table_count + PALETTE_SIZE * palette_count
    if header_size != expected_header_size:
        raise JPFontBuildError(f"{label}: header/palette equation failed")
    table_offsets = [read_u32(data, 0x20 + 4 * index) for index in range(table_count)]
    if table_offsets[0] != header_size:
        raise JPFontBuildError(f"{label}: table 0 does not start at header end")
    if table_offsets != sorted(set(table_offsets)):
        raise JPFontBuildError(f"{label}: table offsets are not unique and ascending")
    if not table_offsets[-1] < atlas_offset <= len(data):
        raise JPFontBuildError(f"{label}: invalid table/atlas order")

    table_ends = table_offsets[1:] + [atlas_offset]
    record_counts: list[int] = []
    map_hashes: list[str] = []
    record_hashes: list[str] = []
    mapped_counts: list[int] = []
    table_geometry: list[dict[str, Any]] = []
    for table, (offset, end) in enumerate(zip(table_offsets, table_ends, strict=True)):
        record_bytes = end - offset - MAP_SIZE
        if record_bytes < RECORD_SIZE or record_bytes % RECORD_SIZE:
            raise JPFontBuildError(f"{label}: malformed table {table} record region")
        record_count = record_bytes // RECORD_SIZE
        mapping = data[offset : offset + MAP_SIZE]
        largest = max(
            (value for (value,) in struct.iter_unpack("<H", mapping)),
            default=0,
        )
        if largest >= record_count:
            raise JPFontBuildError(
                f"{label}: table {table} ordinal {largest} exceeds record count {record_count}"
            )
        records = [
            data[position : position + RECORD_SIZE]
            for position in range(offset + MAP_SIZE, end, RECORD_SIZE)
        ]
        cell_fields = {
            str(field): sorted({record[field] for record in records})
            for field in (1, 3, 7)
        }
        cell_values = {value for values in cell_fields.values() for value in values}
        if any(len(values) != 1 for values in cell_fields.values()) or len(cell_values) != 1:
            raise JPFontBuildError(f"{label}: table {table} has no uniform record cell")
        cell = next(iter(cell_values))
        if cell not in (32, 48):
            raise JPFontBuildError(f"{label}: table {table} unexpected cell {cell}")
        if any(record[2] != 0 or record[6] != 0 for record in records):
            raise JPFontBuildError(f"{label}: table {table} record zero fields drifted")
        if any(record[0] != record[4] or not 0 < record[0] <= cell for record in records):
            raise JPFontBuildError(f"{label}: table {table} width fields are malformed")
        pointers = [read_u32(record, 8) for record in records]
        if pointers != sorted(pointers) or pointers[-1] >= len(data) - atlas_offset:
            raise JPFontBuildError(f"{label}: table {table} atlas pointers are malformed")
        deltas = [right - left for left, right in zip(pointers, pointers[1:])]
        full_stride = (cell // 2) * cell
        width_packed = bool(deltas) and all(
            delta == records[index][0] * cell // 2
            for index, delta in enumerate(deltas)
        )
        fixed_cell = bool(deltas) and all(delta == full_stride for delta in deltas)
        storage_mode = (
            "width_packed"
            if width_packed
            else "fixed_cell"
            if fixed_cell
            else "mixed_or_appended"
        )
        record_counts.append(record_count)
        map_hashes.append(sha256_bytes(mapping))
        record_hashes.append(sha256_bytes(data[offset + MAP_SIZE : end]))
        mapped_counts.append(sum(value != 0 for (value,) in struct.iter_unpack("<H", mapping)))
        table_geometry.append(
            {
                "table": table,
                "cell": cell,
                "cell_field_offsets": [1, 3, 7],
                "cell_field_values": cell_fields,
                "width_field_offsets": [0, 4],
                "width_min": min(record[0] for record in records),
                "width_max": max(record[0] for record in records),
                "full_cell_atlas_stride": full_stride,
                "adjacent_pointer_delta_values": sorted(set(deltas)),
                "atlas_storage_mode": storage_mode,
                "record_geometry_sha256": sha256_bytes(
                    b"".join(record[:8] for record in records)
                ),
            }
        )

    return {
        "declared_size": declared_size,
        "header_size": header_size,
        "unknown": unknown,
        "palette_count": palette_count,
        "table_count": table_count,
        "table_offsets": table_offsets,
        "table_ends": table_ends,
        "record_counts": record_counts,
        "mapped_counts": mapped_counts,
        "map_hashes": map_hashes,
        "record_hashes": record_hashes,
        "table_geometry": table_geometry,
        "atlas_offset": atlas_offset,
        "atlas_length": len(data) - atlas_offset,
        "palette_sha256": sha256_bytes(data[0x20 + 4 * table_count : header_size]),
        "atlas_sha256": sha256_bytes(data[atlas_offset:]),
    }


def validate_output_root(output_root: Path, protected: Sequence[Path]) -> None:
    resolved = output_root.resolve()
    repository = REPO_ROOT.resolve()
    game = GAME_ROOT.resolve()
    local_tmp = (repository / "tmp").resolve()
    in_workspace_tmp = local_tmp in resolved.parents
    if resolved in (repository, game, SCRIPT_DIR.resolve(), local_tmp):
        raise JPFontBuildError(f"unsafe output root: {resolved}")
    if game in resolved.parents and not in_workspace_tmp:
        raise JPFontBuildError(
            f"output inside the game tree must be below {local_tmp}: {resolved}"
        )
    for source in protected:
        source = source.resolve()
        if resolved == source or source in resolved.parents or resolved in source.parents:
            raise JPFontBuildError(f"output root overlaps an input: {resolved}")
    if resolved.exists() and any(resolved.iterdir()):
        raise JPFontBuildError(f"output root must be absent or empty: {resolved}")


def require_stock(path: Path, route: str) -> bytes:
    lock = ROUTES[route]
    if not path.is_file():
        raise JPFontBuildError(f"missing private {lock['logical_path']}: {path}")
    size = path.stat().st_size
    digest = sha256_file(path)
    if size != lock["size"] or digest != lock["sha256"]:
        raise JPFontBuildError(
            f"{route} JP stock gate failed: expected size={lock['size']} "
            f"sha256={lock['sha256']}; actual size={size} sha256={digest}"
        )
    return path.read_bytes()


def merge_overlay_paths(
    registered: Sequence[str], resource: str
) -> tuple[list[str], int]:
    """Return a canonical path order stable across pending registration.

    Pending paths are removed from wherever they currently occur and appended
    in the reviewed order for their resource.  Thus central registration of
    the exact same batch cannot perturb the source catalog or font bytes.
    """

    if any(not isinstance(value, str) for value in registered):
        raise JPFontBuildError(f"{resource}: overlay_globs must contain only strings")
    pending = [row["path"] for row in PENDING_OVERLAYS if row["resource"] == resource]
    pending_set = set(pending)
    if len(set(registered)) != len(registered):
        raise JPFontBuildError(f"{resource}: duplicate registered overlay path")
    canonical = [value for value in registered if value not in pending_set] + pending
    return canonical, sum(value in set(registered) for value in pending)


def _inside(parent: Path, child: Path) -> bool:
    parent = parent.resolve()
    child = child.resolve()
    return child == parent or parent in child.parents


def collect_latest_overlay_demand() -> dict[str, Any]:
    """Collect strict current demand plus the five not-yet-registered batches."""

    progress_relative = SC_FONT.PROGRESS_CONFIG_RELATIVE
    progress_path = (REPO_ROOT / progress_relative).resolve()
    if not _inside(REPO_ROOT, progress_path):
        raise JPFontBuildError("translation progress resolved outside repository")
    progress_raw = progress_path.read_bytes()
    progress = SC_FONT.loads_json_strict(progress_raw, progress_relative)
    resources = progress.get("resources")
    shared = progress.get("shared_strings")
    if not isinstance(resources, list) or not isinstance(shared, list):
        raise JPFontBuildError("translation progress resource arrays are missing")
    string_rows = [row for row in resources if isinstance(row, dict) and row.get("kind") == "strings"]
    shared_rows = [row for row in shared if isinstance(row, dict) and row.get("kind") == "strings"]
    ordered_rows = string_rows + shared_rows
    if tuple(row.get("path") for row in ordered_rows) != EXPECTED_FONT_RESOURCES:
        raise JPFontBuildError("translation progress font resources are not canonical")
    if len(shared_rows) != len(shared):
        raise JPFontBuildError("translation progress has a non-string shared resource")

    all_codepoints: set[int] = set()
    source_rows: list[dict[str, Any]] = []
    resource_rows: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()
    total_entries = 0
    registered_pending_count = 0
    for resource_row in ordered_rows:
        resource = resource_row.get("path")
        globs = resource_row.get("overlay_globs")
        if not isinstance(resource, str) or not isinstance(globs, list):
            raise JPFontBuildError("font resource path/overlay_globs is malformed")
        logical_paths, registered_count = merge_overlay_paths(globs, resource)
        registered_pending_count += registered_count
        local_sources: list[dict[str, Any]] = []
        local_entries = 0
        for logical_path in logical_paths:
            relative = SC_FONT._safe_project_relative_path(logical_path, resource)
            path = (REPO_ROOT / relative).resolve()
            if not _inside(REPO_ROOT, path) or path in seen_paths or not path.is_file():
                raise JPFontBuildError(f"unsafe, duplicate, or missing overlay: {logical_path}")
            seen_paths.add(path)
            raw = path.read_bytes()
            overlay = SC_FONT.loads_json_strict(raw, logical_path)
            SC_FONT._require_source_free_policy(overlay, logical_path)
            schema = overlay.get("schema")
            if not isinstance(schema, str) or not schema:
                raise JPFontBuildError(f"{logical_path}: missing schema")
            actual_resource = SC_FONT._overlay_resource(overlay, logical_path)
            if actual_resource not in SC_FONT._expected_overlay_resource(resource):
                raise JPFontBuildError(
                    f"{logical_path}: resource {actual_resource!r} does not serve {resource!r}"
                )
            entries = overlay.get("entries")
            if not isinstance(entries, list) or not entries:
                raise JPFontBuildError(f"{logical_path}: entries must be nonempty")
            if overlay.get("entry_count", len(entries)) != len(entries):
                raise JPFontBuildError(f"{logical_path}: entry_count mismatch")
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict) or "ko" not in entry:
                    raise JPFontBuildError(f"{logical_path}: entries[{index}] lacks ko")
                label = f"{logical_path}: entries[{index}]"
                ko = SC_FONT._validate_ko_text(entry["ko"], label)
                all_codepoints.update(SC_FONT.renderable_characters(ko, label))
            source = {
                "path": relative.as_posix(),
                "sha256": sha256_bytes(raw),
                "resource": resource,
                "entry_count": len(entries),
                "schema": schema,
            }
            source_rows.append(source)
            local_sources.append(source)
            local_entries += len(entries)
            total_entries += len(entries)
        resource_rows.append(
            {
                "resource": resource,
                "source_count": len(local_sources),
                "entry_count": local_entries,
                "source_catalog_sha256": SC_FONT.canonical_json_hash(local_sources),
            }
        )

    ordered = sorted(all_codepoints)
    hangul = [cp for cp in ordered if 0xAC00 <= cp <= 0xD7A3]
    hangul_set = set(hangul)
    non_hangul = [cp for cp in ordered if cp not in hangul_set]
    return {
        "translation_progress": {
            "path": progress_relative,
            "observed_sha256": sha256_bytes(progress_raw),
            "pending_overlay_count": len(PENDING_OVERLAYS),
            "pending_already_registered_count": registered_pending_count,
            "registration_normalized": True,
        },
        "source_count": len(source_rows),
        "source_catalog_sha256": SC_FONT.canonical_json_hash(source_rows),
        "resource_catalog": resource_rows,
        "source_entry_count": total_entries,
        "codepoint_count": len(ordered),
        "codepoints_sha256": SC_FONT.canonical_codepoint_hash(ordered),
        "hangul_syllable_count": len(hangul),
        "hangul_syllables_sha256": SC_FONT.canonical_codepoint_hash(hangul),
        "non_hangul_count": len(non_hangul),
        "non_hangul_sha256": SC_FONT.canonical_codepoint_hash(non_hangul),
        "hangul": hangul,
        "non_hangul": non_hangul,
    }


def require_demand() -> dict[str, Any]:
    demand = collect_latest_overlay_demand()
    projection = {
        "source_catalog_sha256": demand["source_catalog_sha256"],
        "source_count": demand["source_count"],
        "source_entry_count": demand["source_entry_count"],
        "codepoint_count": demand["codepoint_count"],
        "codepoints_sha256": demand["codepoints_sha256"],
        "hangul_syllable_count": demand["hangul_syllable_count"],
        "hangul_syllables_sha256": demand["hangul_syllables_sha256"],
        "non_hangul_count": demand["non_hangul_count"],
        "non_hangul_sha256": demand["non_hangul_sha256"],
    }
    if projection != DEMAND_LOCK:
        raise JPFontBuildError(
            "current translation glyph demand drifted from DEMAND_LOCK; review and refresh "
            "the JP font workstream before building"
        )
    return demand


def parse_stock_archive(blob: bytes, label: str) -> Any:
    archive = LZ4.parse_link(blob)
    if LZ4.rebuild_link(archive) != blob:
        raise JPFontBuildError(f"{label}: LINK identity roundtrip failed")
    return archive


def extract_raw_g1n(archive: Any, outer_entry: int, label: str) -> bytes:
    if not 0 <= outer_entry < len(archive.entries):
        raise JPFontBuildError(f"{label}: missing outer entry {outer_entry}")
    try:
        _, raw = LZ4.decompress_wrapper(archive.entries[outer_entry].data)
    except Exception as exc:
        raise JPFontBuildError(f"{label}: outer entry {outer_entry} is not valid LZ4: {exc}") from exc
    parse_layout(raw, f"{label} outer entry {outer_entry}")
    return raw


def extract_stock_reuse_glyph(
    raw: bytes,
    layout: dict[str, Any],
    profile_entry: int,
    codepoint: int,
    label: str,
) -> dict[str, Any]:
    """Read one same-cell table-0 glyph for a new table-2 pixel copy."""

    if codepoint not in STOCK_REUSE_CODEPOINTS:
        raise JPFontBuildError(f"{label}: unreviewed stock-reuse {canonical_cp(codepoint)}")
    table_profiles = PROFILE_TABLES[profile_entry]
    source_table, target_table = 0, 2
    source_profile = table_profiles[source_table]
    target_profile = table_profiles[target_table]
    source_cell = int(FONT_PROFILES[source_profile]["cell"])
    target_cell = int(FONT_PROFILES[target_profile]["cell"])
    if source_cell != target_cell:
        raise JPFontBuildError(
            f"{label}: stock-reuse source/target cells differ for {canonical_cp(codepoint)}"
        )
    source_offset = layout["table_offsets"][source_table]
    target_offset = layout["table_offsets"][target_table]
    source_ordinal = read_u16(raw, source_offset + 2 * codepoint)
    target_ordinal = read_u16(raw, target_offset + 2 * codepoint)
    if source_ordinal == 0 or target_ordinal != 0:
        raise JPFontBuildError(
            f"{label}: {canonical_cp(codepoint)} must be mapped only in source table 0"
        )
    if source_ordinal >= layout["record_counts"][source_table]:
        raise JPFontBuildError(f"{label}: stock-reuse source ordinal out of range")
    record_start = source_offset + MAP_SIZE + RECORD_SIZE * source_ordinal
    record = raw[record_start : record_start + RECORD_SIZE]
    if len(record) != RECORD_SIZE:
        raise JPFontBuildError(f"{label}: truncated stock-reuse record")
    width, cell = record[0], record[1]
    if (
        cell != source_cell
        or record[3] != cell
        or record[7] != cell
        or record[4] != width
        or not 0 < width <= cell
    ):
        raise JPFontBuildError(f"{label}: malformed stock-reuse record metrics")
    pixel_size = width * cell // 2
    pointer = read_u32(record, 8)
    atlas = raw[layout["atlas_offset"] :]
    if pointer + pixel_size > len(atlas):
        raise JPFontBuildError(f"{label}: stock-reuse pixel range exceeds atlas")
    pixels = atlas[pointer : pointer + pixel_size]
    if not pixels or not any(pixels):
        raise JPFontBuildError(f"{label}: stock-reuse pixels are blank")
    return {
        "codepoint": codepoint,
        "source_table": source_table,
        "target_table": target_table,
        "source_ordinal": source_ordinal,
        "source_pointer": pointer,
        "metric": record[:8],
        "metric_sha256": sha256_bytes(record[:8]),
        "width": width,
        "cell": cell,
        "pixel_size": pixel_size,
        "pixels": pixels,
        "pixels_sha256": sha256_bytes(pixels),
    }


def stock_reuse_summary(
    raw: bytes, layout: dict[str, Any], profile_entry: int, label: str
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for codepoint in STOCK_REUSE_CODEPOINTS:
        glyph = extract_stock_reuse_glyph(raw, layout, profile_entry, codepoint, label)
        rows.append(
            {
                key: value
                for key, value in glyph.items()
                if key not in ("metric", "pixels")
            }
            | {"codepoint": canonical_cp(codepoint)}
        )
    return rows


def append_plan_for_g1n(
    raw: bytes,
    hangul: Sequence[int],
    non_hangul: Sequence[int],
    label: str,
) -> tuple[dict[int, list[int]], list[dict[str, Any]]]:
    layout = parse_layout(raw, label)
    plan: dict[int, list[int]] = {}
    summary: list[dict[str, Any]] = []
    for table, offset in enumerate(layout["table_offsets"]):
        already_mapped = [cp for cp in hangul if read_u16(raw, offset + 2 * cp)]
        if already_mapped:
            preview = ", ".join(canonical_cp(cp) for cp in already_mapped[:8])
            raise JPFontBuildError(
                f"{label} table {table}: demanded Hangul already mapped; refusing overwrite: {preview}"
            )
        missing_non_hangul = [
            cp for cp in non_hangul if read_u16(raw, offset + 2 * cp) == 0
        ]
        codepoints = sorted(set(hangul) | set(missing_non_hangul))
        expected = APPEND_LOCK[table]
        actual_hash = canonical_codepoint_hash(codepoints)
        if len(codepoints) != expected["count"] or actual_hash != expected["codepoints_sha256"]:
            raise JPFontBuildError(f"{label} table {table}: append lock drifted")
        plan[table] = codepoints
        summary.append(
            {
                "table": table,
                "hangul_append_count": len(hangul),
                "non_hangul_required_count": len(non_hangul),
                "non_hangul_stock_covered_count": len(non_hangul) - len(missing_non_hangul),
                "non_hangul_append_count": len(missing_non_hangul),
                "append_codepoint_count": len(codepoints),
                "append_codepoints_sha256": actual_hash,
            }
        )
    return plan, summary


def build_plan(base_blob: bytes, pk_blob: bytes, demand: dict[str, Any]) -> dict[str, Any]:
    stock_blobs = {"base": base_blob, "pk": pk_blob}
    route_plans: dict[str, Any] = {}
    reference_by_profile: dict[int, dict[int, list[int]]] = {}
    reference_geometry_by_profile: dict[int, list[dict[str, Any]]] = {}
    raster_union: set[int] = set()
    for route in ("base", "pk"):
        archive = parse_stock_archive(stock_blobs[route], f"JP {route} stock")
        targets: list[dict[str, Any]] = []
        for target in ROUTES[route]["targets"]:
            outer = int(target["outer_entry"])
            profile = int(target["profile_entry"])
            raw = extract_raw_g1n(archive, outer, f"JP {route}")
            append_plan, append_summary = append_plan_for_g1n(
                raw,
                list(demand["hangul"]),
                list(demand["non_hangul"]),
                f"JP {route} outer entry {outer}",
            )
            if profile in reference_by_profile and reference_by_profile[profile] != append_plan:
                raise JPFontBuildError(
                    f"JP base/PK append plan differs for profile entry {profile}"
                )
            reference_by_profile.setdefault(profile, append_plan)
            raster_union.update(cp for values in append_plan.values() for cp in values)
            layout = parse_layout(raw, f"JP {route} outer entry {outer}")
            table_profiles = PROFILE_TABLES[profile]
            expected_cells = [FONT_PROFILES[key]["cell"] for key in table_profiles]
            actual_cells = [row["cell"] for row in layout["table_geometry"]]
            if actual_cells != expected_cells:
                raise JPFontBuildError(
                    f"JP {route} outer entry {outer}: cell hierarchy {actual_cells} "
                    f"does not match reviewed profile {expected_cells}"
                )
            if (
                profile in reference_geometry_by_profile
                and reference_geometry_by_profile[profile] != layout["table_geometry"]
            ):
                raise JPFontBuildError(
                    f"JP base/PK record geometry differs for profile entry {profile}"
                )
            reference_geometry_by_profile.setdefault(profile, layout["table_geometry"])
            reuse_rows = stock_reuse_summary(
                raw, layout, profile, f"JP {route} outer entry {outer}"
            )
            for codepoint in STOCK_REUSE_CODEPOINTS:
                if codepoint in append_plan[0] or codepoint in append_plan[1]:
                    raise JPFontBuildError(
                        f"JP {route} outer entry {outer}: stock-reuse point unexpectedly "
                        "requires table 0/1 append"
                    )
                if codepoint not in append_plan[2]:
                    raise JPFontBuildError(
                        f"JP {route} outer entry {outer}: stock-reuse point absent from table 2"
                    )
            targets.append(
                {
                    **target,
                    "stock_raw_size": len(raw),
                    "stock_raw_sha256": sha256_bytes(raw),
                    "table_count": layout["table_count"],
                    "record_counts": layout["record_counts"],
                    "mapped_counts": layout["mapped_counts"],
                    "map_hashes": layout["map_hashes"],
                    "table_profiles": list(table_profiles),
                    "cell_hierarchy": actual_cells,
                    "table_geometry": layout["table_geometry"],
                    "stock_reuse": reuse_rows,
                    "append_summary": append_summary,
                    "append_plan": {str(k): v for k, v in append_plan.items()},
                }
            )
        route_plans[route] = {
            "stock_archive": {
                "logical_path": ROUTES[route]["logical_path"],
                "size": len(stock_blobs[route]),
                "sha256": sha256_bytes(stock_blobs[route]),
            },
            "targets": targets,
        }

    append_union = sorted(raster_union)
    if (
        len(append_union) != APPEND_UNION_LOCK["codepoint_count"]
        or canonical_codepoint_hash(append_union) != APPEND_UNION_LOCK["codepoints_sha256"]
    ):
        raise JPFontBuildError("JP append union drifted from APPEND_UNION_LOCK")
    stock_reuse = sorted(STOCK_REUSE_CODEPOINTS)
    if (
        len(stock_reuse) != STOCK_REUSE_LOCK["codepoint_count"]
        or canonical_codepoint_hash(stock_reuse) != STOCK_REUSE_LOCK["codepoints_sha256"]
        or not set(stock_reuse).issubset(raster_union)
    ):
        raise JPFontBuildError("JP stock-reuse set drifted from STOCK_REUSE_LOCK")
    raster_codepoints = sorted(raster_union - set(stock_reuse))
    if (
        len(raster_codepoints) != TTF_RASTER_LOCK["codepoint_count"]
        or canonical_codepoint_hash(raster_codepoints) != TTF_RASTER_LOCK["codepoints_sha256"]
    ):
        raise JPFontBuildError("JP TTF raster union drifted from TTF_RASTER_LOCK")
    if not set(demand["hangul"]).issubset(raster_codepoints):
        raise JPFontBuildError("JP TTF raster union lost demanded Hangul")

    return {
        "schema": SCHEMA_PLAN,
        "file_only": True,
        "installed_game_files_modified": False,
        "switch_resource_raw_copy": False,
        "official_ttf_rerasterization": True,
        "process_memory_access": False,
        "registry_access": False,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_extracted_binary_payload": False,
        },
        "demand": DEMAND_LOCK,
        "append_union_codepoint_count": len(append_union),
        "append_union_codepoints_sha256": canonical_codepoint_hash(append_union),
        "stock_reuse_codepoint_count": len(stock_reuse),
        "stock_reuse_codepoints_sha256": canonical_codepoint_hash(stock_reuse),
        "stock_reuse_codepoints": stock_reuse,
        "raster_codepoint_count": len(raster_codepoints),
        "raster_codepoints_sha256": canonical_codepoint_hash(raster_codepoints),
        "raster_codepoints": raster_codepoints,
        "profile_assignment": {
            "entry_6_or_16": ["EB48", "EB48", "EB48"],
            "entry_7_or_17": ["B32", "EB48", "B32"],
            "cell_48": "official SeoulHangang EB",
            "cell_32": "official SeoulHangang B",
            "smaller_than_32_cell_tier_present": False,
            "seoul_hangang_m_used": False,
            "decision_basis": "stock 12-byte record cell fields 1/3/7 and atlas pointer stride",
        },
        "fonts": [
            {
                "key": key,
                **source,
                "official_archive_url": SC_FONT.OFFICIAL_ARCHIVE_URL,
                "official_archive_sha256": SC_FONT.OFFICIAL_ARCHIVE_SHA256,
            }
            for key, source in SC_FONT.FONT_SOURCES.items()
        ]
        + [
            {
                "key": "contingency_small_tier_m",
                **SEOUL_HANGANG_M,
                "official_archive_url": SC_FONT.OFFICIAL_ARCHIVE_URL,
                "official_archive_sha256": SC_FONT.OFFICIAL_ARCHIVE_SHA256,
            }
        ],
        "routes": route_plans,
    }


def prepare_raster_profiles(
    full_pixels: dict[int, bytes], raster_codepoints: Sequence[int]
) -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    """Validate the reviewed EB48/B32 raster output and expose one copy each."""

    pixels: dict[str, bytes] = {}
    result: list[dict[str, Any]] = []
    for key in ("eb48", "b32"):
        profile = FONT_PROFILES[key]
        source_entry = int(profile["source_entry"])
        cell = int(profile["cell"])
        bytes_per_glyph = (cell // 2) * cell
        one_table_size = len(raster_codepoints) * bytes_per_glyph
        payload = full_pixels[source_entry]
        if len(payload) != 2 * one_table_size:
            raise JPFontBuildError(f"raster profile {key}: payload size mismatch")
        first, second = payload[:one_table_size], payload[one_table_size:]
        if first != second:
            raise JPFontBuildError(f"raster profile {key}: duplicate source renders differ")
        if not any(first):
            raise JPFontBuildError(f"raster profile {key}: all pixels are blank")
        pixels[key] = first
        result.append(
            {
                "profile": key,
                "source_entry": source_entry,
                "font_key": profile["font_key"],
                "font": profile["font"],
                "cell": cell,
                "raster_size": profile["raster_size"],
                "one_table_payload_size": one_table_size,
                "one_table_payload_sha256": sha256_bytes(first),
                "duplicate_source_renders_exact": True,
            }
        )
    return pixels, result


def build_g1n_append(
    stock: bytes,
    profile_pixels: dict[str, bytes],
    profile_entry: int,
    raster_codepoints: Sequence[int],
    table_codepoints: dict[int, list[int]],
    label: str,
) -> tuple[bytes, dict[str, Any]]:
    """Append rasterized glyphs to every JP table with strict preservation."""

    layout = parse_layout(stock, f"{label} stock")
    if set(table_codepoints) != set(range(TABLE_COUNT)):
        raise JPFontBuildError(f"{label}: append plan must cover all three tables")
    if profile_entry not in PROFILE_TABLES:
        raise JPFontBuildError(f"{label}: unsupported profile entry {profile_entry}")
    table_profiles = PROFILE_TABLES[profile_entry]
    stock_cells = [row["cell"] for row in layout["table_geometry"]]
    expected_cells = [FONT_PROFILES[key]["cell"] for key in table_profiles]
    if stock_cells != expected_cells:
        raise JPFontBuildError(
            f"{label}: stock cell hierarchy {stock_cells} != {expected_cells}"
        )
    raster_count = len(raster_codepoints)
    for key in set(table_profiles):
        cell = int(FONT_PROFILES[key]["cell"])
        expected_size = raster_count * (cell // 2) * cell
        if len(profile_pixels.get(key, b"")) != expected_size:
            raise JPFontBuildError(f"{label}: raster profile {key} size mismatch")
    raster_index = {cp: index for index, cp in enumerate(raster_codepoints)}
    if list(raster_codepoints) != sorted(raster_index) or len(raster_index) != raster_count:
        raise JPFontBuildError(f"{label}: raster codepoints are not sorted and unique")

    normalized: dict[int, list[int]] = {}
    glyph_appends: dict[int, list[dict[str, Any]]] = {}
    compact_pixels = bytearray()
    table_pixel_offsets: dict[int, int] = {}
    table_pixel_sizes: dict[int, int] = {}
    reuse_seen: list[int] = []
    for table in range(TABLE_COUNT):
        codepoints = list(table_codepoints[table])
        if codepoints != sorted(set(codepoints)):
            raise JPFontBuildError(f"{label} table {table}: append list is not sorted/unique")
        normalized[table] = codepoints
        table_pixel_offsets[table] = len(compact_pixels)
        raster_key = table_profiles[table]
        cell = int(FONT_PROFILES[raster_key]["cell"])
        pixel_size = (cell // 2) * cell
        raster_payload = profile_pixels[raster_key]
        rows: list[dict[str, Any]] = []
        for cp in codepoints:
            tail_offset = len(compact_pixels)
            if cp in raster_index:
                start = raster_index[cp] * pixel_size
                pixels = raster_payload[start : start + pixel_size]
                metric = bytes(
                    (cell, cell, 0, cell, cell, 256 - cell // 2, 0, cell)
                )
                row = {
                    "codepoint": cp,
                    "source": "official_ttf",
                    "metric": metric,
                    "pixels": pixels,
                    "pixel_size": len(pixels),
                    "tail_offset": tail_offset,
                }
            elif cp in STOCK_REUSE_CODEPOINTS:
                if table != 2:
                    raise JPFontBuildError(
                        f"{label}: stock-reuse {canonical_cp(cp)} is only permitted in table 2"
                    )
                glyph = extract_stock_reuse_glyph(
                    stock, layout, profile_entry, cp, label
                )
                row = {
                    "codepoint": cp,
                    "source": "stock_table0_pixel_copy",
                    "metric": glyph["metric"],
                    "pixels": glyph["pixels"],
                    "pixel_size": glyph["pixel_size"],
                    "tail_offset": tail_offset,
                    "source_table": glyph["source_table"],
                    "source_ordinal": glyph["source_ordinal"],
                    "source_pointer": glyph["source_pointer"],
                    "source_pixels_sha256": glyph["pixels_sha256"],
                    "source_metric_sha256": glyph["metric_sha256"],
                }
                reuse_seen.append(cp)
            else:
                raise JPFontBuildError(
                    f"{label} table {table}: {canonical_cp(cp)} is absent from strict TTF cmap"
                )
            if len(row["pixels"]) != row["pixel_size"] or not any(row["pixels"]):
                raise JPFontBuildError(f"{label}: invalid appended pixels for {canonical_cp(cp)}")
            compact_pixels.extend(row["pixels"])
            rows.append(row)
        glyph_appends[table] = rows
        table_pixel_sizes[table] = len(compact_pixels) - table_pixel_offsets[table]
    expected_reuse_seen = [
        cp for cp in STOCK_REUSE_CODEPOINTS if cp in table_codepoints[2]
    ]
    if reuse_seen != expected_reuse_seen:
        raise JPFontBuildError(
            f"{label}: stock-reuse occurrence set/order drifted: "
            f"{[canonical_cp(cp) for cp in reuse_seen]}"
        )
    compact_pixel_bytes = bytes(compact_pixels)

    record_add = {table: RECORD_SIZE * len(normalized[table]) for table in range(TABLE_COUNT)}
    target_offsets: list[int] = []
    prior_growth = 0
    for table in range(TABLE_COUNT):
        target_offsets.append(layout["table_offsets"][table] + prior_growth)
        prior_growth += record_add[table]
    target_atlas_offset = layout["atlas_offset"] + prior_growth
    target_size = len(stock) + prior_growth + len(compact_pixel_bytes)
    for table in range(TABLE_COUNT):
        if layout["record_counts"][table] + len(normalized[table]) > 0xFFFF:
            raise JPFontBuildError(f"{label} table {table}: 16-bit ordinal capacity exceeded")
    if layout["atlas_length"] + len(compact_pixel_bytes) >= 0x10000000:
        raise JPFontBuildError(f"{label}: 28-bit atlas pointer range exceeded")
    if target_size > 0xFFFFFFFF or target_atlas_offset > 0xFFFFFFFF:
        raise JPFontBuildError(f"{label}: 32-bit G1N size range exceeded")

    output = bytearray(target_size)
    output[: layout["header_size"]] = stock[: layout["header_size"]]
    struct.pack_into("<I", output, 0x08, target_size)
    struct.pack_into("<I", output, 0x14, target_atlas_offset)
    for table, offset in enumerate(target_offsets):
        struct.pack_into("<I", output, 0x20 + 4 * table, offset)

    table_rows: list[dict[str, Any]] = []
    for table in range(TABLE_COUNT):
        raster_key = table_profiles[table]
        profile = FONT_PROFILES[raster_key]
        cell = int(profile["cell"])
        pixel_size = (cell // 2) * cell
        source_offset = layout["table_offsets"][table]
        target_offset = target_offsets[table]
        table_map = bytearray(stock[source_offset : source_offset + MAP_SIZE])
        codepoints = normalized[table]
        old_count = layout["record_counts"][table]
        new_records = bytearray(record_add[table])
        for index, (cp, glyph) in enumerate(
            zip(codepoints, glyph_appends[table], strict=True)
        ):
            old_ordinal = read_u16(table_map, 2 * cp)
            if old_ordinal != 0:
                raise JPFontBuildError(
                    f"{label} table {table} {canonical_cp(cp)}: refusing overwrite of {old_ordinal}"
                )
            struct.pack_into("<H", table_map, 2 * cp, old_count + index)
            record_offset = RECORD_SIZE * index
            new_records[record_offset : record_offset + 8] = glyph["metric"]
            pointer = layout["atlas_length"] + glyph["tail_offset"]
            if glyph["source"] == "stock_table0_pixel_copy" and pointer == glyph["source_pointer"]:
                raise JPFontBuildError(f"{label}: direct stock pointer alias is forbidden")
            struct.pack_into("<I", new_records, record_offset + 8, pointer)
        output[target_offset : target_offset + MAP_SIZE] = table_map
        old_records = stock[source_offset + MAP_SIZE : layout["table_ends"][table]]
        record_start = target_offset + MAP_SIZE
        output[record_start : record_start + len(old_records)] = old_records
        append_start = record_start + len(old_records)
        output[append_start : append_start + len(new_records)] = new_records
        table_rows.append(
            {
                "table": table,
                "raster_profile": raster_key,
                "font": profile["font"],
                "cell": cell,
                "source_record_count": old_count,
                "target_record_count": old_count + len(codepoints),
                "append_codepoint_count": len(codepoints),
                "append_codepoints_sha256": canonical_codepoint_hash(codepoints),
                "appended_records_sha256": sha256_bytes(new_records),
                "appended_pixel_size": table_pixel_sizes[table],
                "appended_pixels_sha256": sha256_bytes(
                    compact_pixel_bytes[
                        table_pixel_offsets[table] : table_pixel_offsets[table]
                        + table_pixel_sizes[table]
                    ]
                ),
                "ttf_raster_append_count": sum(
                    row["source"] == "official_ttf" for row in glyph_appends[table]
                ),
                "stock_pixel_copy_append_count": sum(
                    row["source"] == "stock_table0_pixel_copy"
                    for row in glyph_appends[table]
                ),
                "stock_pixel_copies": [
                    {
                        "codepoint": canonical_cp(row["codepoint"]),
                        "source_table": row["source_table"],
                        "source_ordinal": row["source_ordinal"],
                        "source_pointer": row["source_pointer"],
                        "target_pointer": layout["atlas_length"] + row["tail_offset"],
                        "direct_pointer_alias": False,
                        "pixel_size": row["pixel_size"],
                        "metric_sha256": row["source_metric_sha256"],
                        "pixels_sha256": row["source_pixels_sha256"],
                    }
                    for row in glyph_appends[table]
                    if row["source"] == "stock_table0_pixel_copy"
                ],
            }
        )

    stock_atlas = stock[layout["atlas_offset"] :]
    output[target_atlas_offset : target_atlas_offset + len(stock_atlas)] = stock_atlas
    output[target_atlas_offset + len(stock_atlas) :] = compact_pixel_bytes
    candidate = bytes(output)
    target_layout = parse_layout(candidate, f"{label} target")
    if target_layout["table_offsets"] != target_offsets:
        raise JPFontBuildError(f"{label}: target table offsets mismatch")
    if target_layout["atlas_offset"] != target_atlas_offset:
        raise JPFontBuildError(f"{label}: target atlas offset mismatch")

    # Normalize every permitted header field and demand exact byte identity.
    normalized_header = bytearray(candidate[: layout["header_size"]])
    for start in (0x08, 0x14, *[0x20 + 4 * table for table in range(1, TABLE_COUNT)]):
        normalized_header[start : start + 4] = stock[start : start + 4]
    if bytes(normalized_header) != stock[: layout["header_size"]]:
        raise JPFontBuildError(f"{label}: header changed outside permitted offsets")
    if target_layout["palette_sha256"] != layout["palette_sha256"]:
        raise JPFontBuildError(f"{label}: palette changed")
    for table in range(TABLE_COUNT):
        source_offset = layout["table_offsets"][table]
        target_offset = target_offsets[table]
        normalized_map = bytearray(candidate[target_offset : target_offset + MAP_SIZE])
        for cp in normalized[table]:
            normalized_map[2 * cp : 2 * cp + 2] = stock[
                source_offset + 2 * cp : source_offset + 2 * cp + 2
            ]
        if bytes(normalized_map) != stock[source_offset : source_offset + MAP_SIZE]:
            raise JPFontBuildError(f"{label} table {table}: map changed outside append set")
        old_records = stock[source_offset + MAP_SIZE : layout["table_ends"][table]]
        target_old_start = target_offset + MAP_SIZE
        if candidate[target_old_start : target_old_start + len(old_records)] != old_records:
            raise JPFontBuildError(f"{label} table {table}: existing records changed")
    if candidate[target_atlas_offset : target_atlas_offset + len(stock_atlas)] != stock_atlas:
        raise JPFontBuildError(f"{label}: complete stock atlas prefix changed")
    if candidate[target_atlas_offset + len(stock_atlas) :] != compact_pixel_bytes:
        raise JPFontBuildError(f"{label}: appended pixel tail mismatch")

    validation = {
        "profile_entry": profile_entry,
        "stock_size": len(stock),
        "stock_sha256": sha256_bytes(stock),
        "target_size": len(candidate),
        "target_sha256": sha256_bytes(candidate),
        "table_count": TABLE_COUNT,
        "cell_hierarchy": expected_cells,
        "table_profiles": list(table_profiles),
        "header_allowed_changes_only": True,
        "palette_exact": True,
        "maps_exact_outside_append_sets": True,
        "existing_records_exact": True,
        "complete_stock_atlas_exact_prefix": True,
        "appended_pixels_exact": True,
        "tables": table_rows,
    }
    return candidate, validation


def verify_archive_preservation(
    stock_blob: bytes,
    candidate_blob: bytes,
    replacements: dict[int, bytes],
    label: str,
) -> dict[str, Any]:
    stock = parse_stock_archive(stock_blob, f"{label} stock")
    candidate = parse_stock_archive(candidate_blob, f"{label} candidate")
    if len(stock.entries) != len(candidate.entries):
        raise JPFontBuildError(f"{label}: LINK entry count changed")
    for index, (before, after) in enumerate(zip(stock.entries, candidate.entries, strict=True)):
        if index in replacements:
            rebuilt = extract_raw_g1n(candidate, index, f"{label} candidate")
            if rebuilt != replacements[index]:
                raise JPFontBuildError(f"{label}: target entry {index} re-extraction mismatch")
            if before.data[:8] != after.data[:8]:
                raise JPFontBuildError(f"{label}: target entry {index} wrapper prefix changed")
        else:
            if after.data != before.data or after.gap_after != before.gap_after:
                raise JPFontBuildError(f"{label}: non-target LINK entry {index} changed")
    return {
        "link_entry_count": len(stock.entries),
        "target_outer_entries": sorted(replacements),
        "non_target_entry_payloads_exact": True,
        "non_target_entry_gaps_exact": True,
        "all_nested_g1t_in_non_target_entries_exact": True,
        "target_wrapper_prefixes_exact": True,
    }


def rebuild_link_with_g1n_replacements(
    stock_blob: bytes, replacements: dict[int, bytes], label: str
) -> bytes:
    """Recompress arbitrary JP target entries and preserve every other entry."""

    archive = parse_stock_archive(stock_blob, f"{label} stock")
    if not replacements:
        raise JPFontBuildError(f"{label}: no replacements")
    wrapped: dict[int, bytes] = {}
    for index, raw in sorted(replacements.items()):
        if not 0 <= index < len(archive.entries):
            raise JPFontBuildError(f"{label}: replacement index {index} is out of range")
        wrapped[index] = LZ4.recompress_wrapper(raw, archive.entries[index].data)
    candidate = LZ4.rebuild_link(archive, wrapped)
    parsed = parse_stock_archive(candidate, f"{label} candidate")
    for index, raw in replacements.items():
        _header, unpacked = LZ4.decompress_wrapper(parsed.entries[index].data)
        if unpacked != raw:
            raise JPFontBuildError(f"{label}: replacement {index} recompression mismatch")
    return candidate


def build_route(
    route: str,
    stock_blob: bytes,
    plan: dict[str, Any],
    profile_pixels: dict[str, bytes],
) -> tuple[bytes, dict[int, bytes], dict[str, Any]]:
    archive = parse_stock_archive(stock_blob, f"JP {route} stock")
    target_plan_rows = plan["routes"][route]["targets"]
    replacements: dict[int, bytes] = {}
    validations: list[dict[str, Any]] = []
    raster_codepoints = [int(value) for value in plan["raster_codepoints"]]
    for row in target_plan_rows:
        outer = int(row["outer_entry"])
        profile = int(row["profile_entry"])
        stock_raw = extract_raw_g1n(archive, outer, f"JP {route}")
        table_plan = {
            table: [int(value) for value in row["append_plan"][str(table)]]
            for table in range(TABLE_COUNT)
        }
        candidate_raw, validation = build_g1n_append(
            stock_raw,
            profile_pixels,
            profile,
            raster_codepoints,
            table_plan,
            f"JP {route} outer entry {outer}",
        )
        replacements[outer] = candidate_raw
        validations.append({"outer_entry": outer, **validation})
    candidate_blob = rebuild_link_with_g1n_replacements(
        stock_blob, replacements, f"JP {route}"
    )
    preservation = verify_archive_preservation(
        stock_blob,
        candidate_blob,
        replacements,
        f"JP {route}",
    )
    return candidate_blob, replacements, {
        "route": route,
        "logical_path": ROUTES[route]["logical_path"],
        "stock_archive_size": len(stock_blob),
        "stock_archive_sha256": sha256_bytes(stock_blob),
        "candidate_archive_size": len(candidate_blob),
        "candidate_archive_sha256": sha256_bytes(candidate_blob),
        "preservation": preservation,
        "targets": validations,
    }


def expected_output_projection(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "routes": [
            {
                "route": route["route"],
                "logical_path": route["logical_path"],
                "candidate_archive_size": route["candidate_archive_size"],
                "candidate_archive_sha256": route["candidate_archive_sha256"],
                "targets": [
                    {
                        "outer_entry": target["outer_entry"],
                        "target_size": target["target_size"],
                        "target_sha256": target["target_sha256"],
                    }
                    for target in route["targets"]
                ],
            }
            for route in manifest["routes"]
        ],
        "raster_profiles": manifest["raster_profiles"],
        "font_cmap_gate": manifest["font_cmap_gate"],
    }


def load_expected_outputs(evidence_path: Path) -> dict[str, Any]:
    evidence = strict_json(evidence_path)
    if evidence.get("schema") != SCHEMA_EVIDENCE:
        raise JPFontBuildError(f"{evidence_path}: unsupported evidence schema")
    expected = evidence.get("expected_private_outputs")
    if not isinstance(expected, dict):
        raise JPFontBuildError(f"{evidence_path}: missing expected_private_outputs")
    return expected


def private_build(
    base_blob: bytes,
    pk_blob: bytes,
    font_paths: dict[str, Path],
    plan: dict[str, Any],
    output_root: Path,
    powershell: Path,
    expected_outputs: dict[str, Any] | None,
) -> dict[str, Any]:
    SC_FONT.require_official_fonts(font_paths)
    raster_codepoints = [int(value) for value in plan["raster_codepoints"]]
    append_union = sorted(
        set(raster_codepoints)
        | {int(value) for value in plan["stock_reuse_codepoints"]}
    )
    cmap_gate = validate_official_font_cmaps(font_paths, append_union)
    request_path = output_root / "private" / "raster_request.json"
    raster_root = output_root / "private" / "raster"
    atomic_write(request_path, encode_json(SC_FONT.raster_request(font_paths, raster_codepoints)))
    raster_result = SC_FONT.run_rasterizer(powershell, request_path, raster_root)
    full_pixels = SC_FONT.validate_raster_result(
        raster_result,
        raster_root,
        raster_codepoints,
    )
    profile_pixels, raster_profiles = prepare_raster_profiles(
        full_pixels, raster_codepoints
    )

    route_manifests: list[dict[str, Any]] = []
    for route, stock_blob in (("base", base_blob), ("pk", pk_blob)):
        candidate, raw_targets, route_manifest = build_route(
            route,
            stock_blob,
            plan,
            profile_pixels,
        )
        candidate_path = output_root / ROUTES[route]["candidate_relative_path"]
        atomic_write(candidate_path, candidate)
        for outer, raw in raw_targets.items():
            atomic_write(
                output_root / "private" / "candidate" / "raw_g1n" / f"{route}_{outer}.g1n",
                raw,
            )
        route_manifests.append(route_manifest)

    manifest = {
        "schema": SCHEMA_BUILD,
        "file_only": True,
        "installed_game_files_modified": False,
        "switch_resource_raw_copy": False,
        "official_ttf_rerasterization": True,
        "gdi_font_fallback_allowed": False,
        "process_memory_access": False,
        "registry_access": False,
        "distribution": {
            "official_ttf_included": False,
            "raster_payload_publicly_included": False,
            "stock_or_candidate_game_resource_publicly_included": False,
        },
        "plan_sha256": sha256_bytes(encode_json(plan)),
        "fonts": [
            {
                "key": key,
                "file_name": font_paths[key].name,
                "size": font_paths[key].stat().st_size,
                "sha256": sha256_file(font_paths[key]),
                "family": source["family"],
                "weight": source["weight"],
            }
            for key, source in SC_FONT.FONT_SOURCES.items()
        ],
        "raster_result_sha256": sha256_file(raster_root / "raster_result.json"),
        "raster_profiles": raster_profiles,
        "font_cmap_gate": cmap_gate,
        "routes": route_manifests,
    }
    projection = expected_output_projection(manifest)
    if expected_outputs is not None and projection != expected_outputs:
        raise JPFontBuildError(
            "private candidate hashes differ from pinned verification evidence"
        )
    atomic_write(output_root / "private" / "build_manifest.json", encode_json(manifest))
    return manifest


def verify_existing_candidates(
    base_blob: bytes,
    pk_blob: bytes,
    plan: dict[str, Any],
    candidate_root: Path,
    expected_outputs: dict[str, Any],
) -> dict[str, Any]:
    route_manifests: list[dict[str, Any]] = []
    for route, stock_blob in (("base", base_blob), ("pk", pk_blob)):
        relative = Path(*ROUTES[route]["candidate_relative_path"].split("/"))
        # --candidate-root points to the build root, so retain private/candidate.
        candidate_path = candidate_root / relative
        if not candidate_path.is_file():
            raise JPFontBuildError(f"missing candidate: {candidate_path}")
        candidate_blob = candidate_path.read_bytes()
        stock_archive = parse_stock_archive(stock_blob, f"JP {route} stock")
        candidate_archive = parse_stock_archive(candidate_blob, f"JP {route} candidate")
        replacements: dict[int, bytes] = {}
        target_rows: list[dict[str, Any]] = []
        plan_rows = plan["routes"][route]["targets"]
        for row in plan_rows:
            outer = int(row["outer_entry"])
            profile = int(row["profile_entry"])
            stock_raw = extract_raw_g1n(stock_archive, outer, f"JP {route} stock")
            target_raw = extract_raw_g1n(candidate_archive, outer, f"JP {route} candidate")
            table_plan = {
                table: [int(value) for value in row["append_plan"][str(table)]]
                for table in range(TABLE_COUNT)
            }
            validation = verify_g1n_append_without_raster(
                stock_raw,
                target_raw,
                profile,
                table_plan,
                f"JP {route} outer entry {outer}",
            )
            replacements[outer] = target_raw
            target_rows.append({"outer_entry": outer, **validation})
        preservation = verify_archive_preservation(
            stock_blob,
            candidate_blob,
            replacements,
            f"JP {route}",
        )
        route_manifests.append(
            {
                "route": route,
                "logical_path": ROUTES[route]["logical_path"],
                "stock_archive_size": len(stock_blob),
                "stock_archive_sha256": sha256_bytes(stock_blob),
                "candidate_archive_size": len(candidate_blob),
                "candidate_archive_sha256": sha256_bytes(candidate_blob),
                "preservation": preservation,
                "targets": target_rows,
            }
        )
    projection = {
        "routes": [
            {
                "route": row["route"],
                "logical_path": row["logical_path"],
                "candidate_archive_size": row["candidate_archive_size"],
                "candidate_archive_sha256": row["candidate_archive_sha256"],
                "targets": [
                    {
                        "outer_entry": target["outer_entry"],
                        "target_size": target["target_size"],
                        "target_sha256": target["target_sha256"],
                    }
                    for target in row["targets"]
                ],
            }
            for row in route_manifests
        ],
        "raster_profiles": expected_outputs["raster_profiles"],
        "font_cmap_gate": expected_outputs["font_cmap_gate"],
    }
    if projection != expected_outputs:
        raise JPFontBuildError("existing candidates differ from pinned verification evidence")
    return {
        "schema": "nobu16.kr.font-jp-seoulhangang-v1-existing-verify.v1",
        "ok": True,
        "routes": route_manifests,
    }


def verify_g1n_append_without_raster(
    stock: bytes,
    target: bytes,
    profile_entry: int,
    table_codepoints: dict[int, list[int]],
    label: str,
) -> dict[str, Any]:
    """Independently verify an append candidate without needing the TTF."""

    source = parse_layout(stock, f"{label} stock")
    candidate = parse_layout(target, f"{label} target")
    if profile_entry not in PROFILE_TABLES:
        raise JPFontBuildError(f"{label}: invalid profile")
    table_profiles = PROFILE_TABLES[profile_entry]
    expected_cells = [FONT_PROFILES[key]["cell"] for key in table_profiles]
    if [row["cell"] for row in source["table_geometry"]] != expected_cells:
        raise JPFontBuildError(f"{label}: stock cell hierarchy drifted")
    growth = [RECORD_SIZE * len(table_codepoints[table]) for table in range(TABLE_COUNT)]
    expected_offsets: list[int] = []
    cursor = 0
    for table in range(TABLE_COUNT):
        expected_offsets.append(source["table_offsets"][table] + cursor)
        cursor += growth[table]
    expected_atlas = source["atlas_offset"] + cursor
    expected_glyphs: dict[int, list[dict[str, Any]]] = {}
    expected_pixel_tail = 0
    reuse_seen: list[int] = []
    for table in range(TABLE_COUNT):
        raster_key = table_profiles[table]
        cell = int(FONT_PROFILES[raster_key]["cell"])
        default_metric = bytes(
            (cell, cell, 0, cell, cell, 256 - cell // 2, 0, cell)
        )
        rows: list[dict[str, Any]] = []
        for cp in table_codepoints[table]:
            if cp in STOCK_REUSE_CODEPOINTS:
                if table != 2:
                    raise JPFontBuildError(
                        f"{label}: stock-reuse {canonical_cp(cp)} appears outside table 2"
                    )
                glyph = extract_stock_reuse_glyph(
                    stock, source, profile_entry, cp, label
                )
                rows.append(
                    {
                        "codepoint": cp,
                        "source": "stock_table0_pixel_copy",
                        "metric": glyph["metric"],
                        "pixel_size": glyph["pixel_size"],
                        "pixels": glyph["pixels"],
                        "source_pointer": glyph["source_pointer"],
                        "source_ordinal": glyph["source_ordinal"],
                    }
                )
                reuse_seen.append(cp)
            else:
                rows.append(
                    {
                        "codepoint": cp,
                        "source": "official_ttf",
                        "metric": default_metric,
                        "pixel_size": (cell // 2) * cell,
                    }
                )
            expected_pixel_tail += rows[-1]["pixel_size"]
        expected_glyphs[table] = rows
    expected_reuse_seen = [
        cp for cp in STOCK_REUSE_CODEPOINTS if cp in table_codepoints[2]
    ]
    if reuse_seen != expected_reuse_seen:
        raise JPFontBuildError(f"{label}: stock-reuse occurrence set/order mismatch")
    if candidate["table_offsets"] != expected_offsets:
        raise JPFontBuildError(f"{label}: table offsets do not follow append equation")
    if candidate["atlas_offset"] != expected_atlas:
        raise JPFontBuildError(f"{label}: atlas offset does not follow append equation")
    if len(target) != len(stock) + cursor + expected_pixel_tail:
        raise JPFontBuildError(f"{label}: target size does not follow append equation")

    normalized_header = bytearray(target[: source["header_size"]])
    for start in (0x08, 0x14, *[0x20 + 4 * table for table in range(1, TABLE_COUNT)]):
        normalized_header[start : start + 4] = stock[start : start + 4]
    if bytes(normalized_header) != stock[: source["header_size"]]:
        raise JPFontBuildError(f"{label}: header changed outside append fields")
    if candidate["palette_sha256"] != source["palette_sha256"]:
        raise JPFontBuildError(f"{label}: palette changed")

    tail_cursor = 0
    table_rows: list[dict[str, Any]] = []
    reuse_rows: list[dict[str, Any]] = []
    stock_atlas = stock[source["atlas_offset"] :]
    pixel_tail_start = candidate["atlas_offset"] + len(stock_atlas)
    for table in range(TABLE_COUNT):
        raster_key = table_profiles[table]
        profile = FONT_PROFILES[raster_key]
        cell = int(profile["cell"])
        cps = table_codepoints[table]
        source_offset = source["table_offsets"][table]
        target_offset = candidate["table_offsets"][table]
        changed: list[int] = []
        for cp in range(MAP_ENTRIES):
            before = read_u16(stock, source_offset + 2 * cp)
            after = read_u16(target, target_offset + 2 * cp)
            if before != after:
                changed.append(cp)
        if changed != cps:
            raise JPFontBuildError(f"{label} table {table}: map change set mismatch")
        old_count = source["record_counts"][table]
        for index, cp in enumerate(cps):
            if read_u16(stock, source_offset + 2 * cp) != 0:
                raise JPFontBuildError(f"{label} table {table}: overwritten stock mapping")
            if read_u16(target, target_offset + 2 * cp) != old_count + index:
                raise JPFontBuildError(f"{label} table {table}: appended ordinal mismatch")
        old_records = stock[source_offset + MAP_SIZE : source["table_ends"][table]]
        target_record_start = target_offset + MAP_SIZE
        if target[target_record_start : target_record_start + len(old_records)] != old_records:
            raise JPFontBuildError(f"{label} table {table}: existing records changed")
        new_start = target_record_start + len(old_records)
        new_records = target[new_start : new_start + growth[table]]
        for index, glyph in enumerate(expected_glyphs[table]):
            record = new_records[index * RECORD_SIZE : (index + 1) * RECORD_SIZE]
            if record[:8] != glyph["metric"]:
                raise JPFontBuildError(f"{label} table {table}: appended metrics mismatch")
            expected_pointer = source["atlas_length"] + tail_cursor
            if read_u32(record, 8) != expected_pointer:
                raise JPFontBuildError(f"{label} table {table}: appended pointer mismatch")
            copied = target[
                pixel_tail_start + tail_cursor :
                pixel_tail_start + tail_cursor + glyph["pixel_size"]
            ]
            if len(copied) != glyph["pixel_size"] or not any(copied):
                raise JPFontBuildError(f"{label} table {table}: appended pixels are blank/truncated")
            if glyph["source"] == "stock_table0_pixel_copy":
                if copied != glyph["pixels"]:
                    raise JPFontBuildError(
                        f"{label} table {table}: stock-reuse pixels are not an exact copy"
                    )
                if expected_pointer == glyph["source_pointer"]:
                    raise JPFontBuildError(f"{label}: direct stock pointer alias detected")
                reuse_rows.append(
                    {
                        "codepoint": canonical_cp(glyph["codepoint"]),
                        "source_table": 0,
                        "target_table": table,
                        "source_ordinal": glyph["source_ordinal"],
                        "source_pointer": glyph["source_pointer"],
                        "target_pointer": expected_pointer,
                        "direct_pointer_alias": False,
                        "metric_sha256": sha256_bytes(glyph["metric"]),
                        "pixel_size": glyph["pixel_size"],
                        "pixels_sha256": sha256_bytes(copied),
                    }
                )
            tail_cursor += glyph["pixel_size"]
        table_rows.append(
            {
                "table": table,
                "raster_profile": raster_key,
                "font": profile["font"],
                "cell": cell,
                "append_codepoint_count": len(cps),
                "append_codepoints_sha256": canonical_codepoint_hash(cps),
                "ttf_raster_append_count": sum(
                    row["source"] == "official_ttf" for row in expected_glyphs[table]
                ),
                "stock_pixel_copy_append_count": sum(
                    row["source"] == "stock_table0_pixel_copy"
                    for row in expected_glyphs[table]
                ),
            }
        )
    if target[candidate["atlas_offset"] : candidate["atlas_offset"] + len(stock_atlas)] != stock_atlas:
        raise JPFontBuildError(f"{label}: stock atlas prefix changed")
    pixel_tail = target[candidate["atlas_offset"] + len(stock_atlas) :]
    if len(pixel_tail) != expected_pixel_tail or not any(pixel_tail):
        raise JPFontBuildError(f"{label}: appended pixel tail is missing/blank")
    return {
        "profile_entry": profile_entry,
        "stock_size": len(stock),
        "stock_sha256": sha256_bytes(stock),
        "target_size": len(target),
        "target_sha256": sha256_bytes(target),
        "table_count": TABLE_COUNT,
        "cell_hierarchy": expected_cells,
        "table_profiles": list(table_profiles),
        "header_allowed_changes_only": True,
        "palette_exact": True,
        "maps_exact_outside_append_sets": True,
        "existing_records_exact": True,
        "complete_stock_atlas_exact_prefix": True,
        "appended_pixels_nonblank": True,
        "stock_pixel_copies_exact": True,
        "stock_pixel_copies": reuse_rows,
        "tables": table_rows,
    }


def command_plan(args: argparse.Namespace) -> int:
    base_path = Path(args.stock_base).resolve()
    pk_path = Path(args.stock_pk).resolve()
    output_root = Path(args.output_root).resolve()
    validate_output_root(output_root, (base_path, pk_path))
    plan = build_plan(
        require_stock(base_path, "base"),
        require_stock(pk_path, "pk"),
        require_demand(),
    )
    output_root.mkdir(parents=True, exist_ok=True)
    atomic_write(output_root / "plan.json", encode_json(plan))
    print(f"plan={output_root / 'plan.json'}")
    print(f"raster_codepoints={plan['raster_codepoint_count']}")
    return 0


def command_build(args: argparse.Namespace) -> int:
    base_path = Path(args.stock_base).resolve()
    pk_path = Path(args.stock_pk).resolve()
    font_paths = {
        "entry6_48px_eb": Path(args.font_eb).resolve(),
        "entry7_32px_b": Path(args.font_b).resolve(),
    }
    output_root = Path(args.output_root).resolve()
    evidence_path = Path(args.evidence).resolve()
    validate_output_root(output_root, (base_path, pk_path, *font_paths.values()))
    base_blob = require_stock(base_path, "base")
    pk_blob = require_stock(pk_path, "pk")
    plan = build_plan(base_blob, pk_blob, require_demand())
    expected = load_expected_outputs(evidence_path)
    output_root.mkdir(parents=True, exist_ok=True)
    atomic_write(output_root / "plan.json", encode_json(plan))
    manifest = private_build(
        base_blob,
        pk_blob,
        font_paths,
        plan,
        output_root,
        Path(args.powershell).resolve(),
        expected,
    )
    print(f"private_manifest={output_root / 'private' / 'build_manifest.json'}")
    for route in manifest["routes"]:
        print(
            f"{route['route']}_candidate_sha256={route['candidate_archive_sha256']} "
            f"size={route['candidate_archive_size']}"
        )
    return 0


def command_verify(args: argparse.Namespace) -> int:
    base_blob = require_stock(Path(args.stock_base).resolve(), "base")
    pk_blob = require_stock(Path(args.stock_pk).resolve(), "pk")
    plan = build_plan(base_blob, pk_blob, require_demand())
    expected = load_expected_outputs(Path(args.evidence).resolve())
    report = verify_existing_candidates(
        base_blob,
        pk_blob,
        plan,
        Path(args.candidate_root).resolve(),
        expected,
    )
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


def add_stock_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--stock-base", type=Path, required=True)
    parser.add_argument("--stock-pk", type=Path, required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="validate private stocks and emit a source-free plan")
    add_stock_arguments(plan)
    plan.add_argument("--output-root", type=Path, required=True)
    plan.set_defaults(handler=command_plan)

    build = subparsers.add_parser("build", help="rerasterize official TTFs and build both JP routes")
    add_stock_arguments(build)
    build.add_argument("--font-eb", type=Path, required=True)
    build.add_argument("--font-b", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.add_argument(
        "--evidence",
        type=Path,
        default=SCRIPT_DIR / "verification.v1.json",
        help="pinned source-free output evidence (required fail-closed gate)",
    )
    build.add_argument(
        "--powershell",
        type=Path,
        default=Path(os.environ.get("SystemRoot", r"C:\Windows"))
        / "System32"
        / "WindowsPowerShell"
        / "v1.0"
        / "powershell.exe",
    )
    build.set_defaults(handler=command_build)

    verify = subparsers.add_parser("verify", help="read-only verification of an existing private build root")
    add_stock_arguments(verify)
    verify.add_argument("--candidate-root", type=Path, required=True)
    verify.add_argument(
        "--evidence",
        type=Path,
        default=SCRIPT_DIR / "verification.v1.json",
    )
    verify.set_defaults(handler=command_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (JPFontBuildError, SC_FONT.FontBuildError, OSError, ValueError, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
