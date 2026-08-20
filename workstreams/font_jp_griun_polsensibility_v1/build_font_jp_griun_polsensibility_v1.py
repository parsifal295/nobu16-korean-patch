#!/usr/bin/env python3
"""Replace table-1 mapped Hangul pixels in the v0.94 JP G1N routes.

The archive structure, G1N maps, records, metrics, pointers, palettes, and all
non-Hangul pixels are preserved byte-for-byte.  G1N tables 0 and 2 are also
preserved byte-for-byte.  Only table 1 atlas spans belonging to mapped Hangul
codepoints covered by the pinned Griun PolSensibility TTF are rewritten.  Two
cmap exceptions are deliberately retained from the input:
U+CE4C (unused legacy mapping) and U+D07F (큿, user-approved exception).
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import shutil
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import nobu16_lz4 as lz4  # noqa: E402


class BuildError(RuntimeError):
    pass


SCHEMA = "nobu16.kr.font-jp-griun-polsensibility-v1.validation.v1"
FONT_SCHEMA = "nobu16.kr.font-jp-griun-polsensibility-v1.raster-request.v1"
FONT_RESULT_SCHEMA = "nobu16.kr.font-jp-griun-polsensibility-v1.raster-result.v1"
G1N_MAGIC = b"_N1G0000"
MAP_SIZE = 0x10000 * 2
RECORD_SIZE = 12
HANGUL_START = 0xAC00
HANGUL_END = 0xD7A3
FONT_NAME = "Griun_PolSensibility-Rg.ttf"
FONT_FAMILY = "그리운 경찰감성체"
FONT_SIZE = 1_936_424
FONT_SHA256 = "057472E1B8E4528421A5B30953A33992FFCE06F2BF9546993C364E264CD1887F"
CMAP_EXCEPTIONS = (0xCE4C, 0xD07F)
DEMANDED_EXCEPTION = 0xD07F
TARGET_TABLE = 1


ROUTES: dict[str, dict[str, Any]] = {
    "base": {
        "relative_path": "RES_JP/res_lang.bin",
        "size": 153_501_108,
        "sha256": "B10EF608C4B1A4981C096A29D8B413087EF395696CB8A219B715BDF4C712D07C",
        "entries": (6, 7),
    },
    "pk": {
        "relative_path": "RES_JP_PK/res_lang_pk.bin",
        "size": 141_800_722,
        "sha256": "B4AE45ED32C79144F5C33F49ABCA4779F88AFB3782EA3C4F577E7F20EDBFFB9E",
        "entries": (16, 17),
    },
    "port1": {
        "relative_path": "RES_JP_PK_PORT/res_lang_pk_port1.bin",
        "size": 79_074_833,
        "sha256": "C1B21E2128A74263DCE4598E49477B056E5C64286E156FF046F7C773D3FB56EB",
        "entries": (1,),
    },
    "port2": {
        "relative_path": "RES_JP_PK_PORT/res_lang_pk_port2.bin",
        "size": 67_321_109,
        "sha256": "C3168D91386375C0F40EFCDF6817E0BA4554FC1EB9B857E1B379507BB3D61C94",
        "entries": (0, 1),
    },
}

PROFILE_BY_CELL = {
    32: {"profile": "cell32", "cell": 32, "raster_size": 32},
    48: {"profile": "cell48", "cell": 48, "raster_size": 46},
    64: {"profile": "cell64", "cell": 64, "raster_size": 64},
    96: {"profile": "cell96", "cell": 96, "raster_size": 92},
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_cp(cp: int) -> str:
    return f"U+{cp:04X}"


def codepoint_hash(codepoints: Iterable[int]) -> str:
    text = "\n".join(canonical_cp(cp) for cp in sorted(codepoints)) + "\n"
    return sha256_bytes(text.encode("ascii"))


def strict_json(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"{label}: invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"{label}: JSON root must be an object")
    return value


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _be_u16(data: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise BuildError(f"{label}: truncated big-endian u16")
    return struct.unpack_from(">H", data, offset)[0]


def _be_i16(data: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise BuildError(f"{label}: truncated big-endian i16")
    return struct.unpack_from(">h", data, offset)[0]


def _be_u32(data: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise BuildError(f"{label}: truncated big-endian u32")
    return struct.unpack_from(">I", data, offset)[0]


def parse_unicode_cmap(font: bytes, label: str) -> list[dict[str, Any]]:
    if len(font) < 12 or font[:4] not in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
        raise BuildError(f"{label}: unsupported SFNT")
    table_count = _be_u16(font, 4, label)
    if not 1 <= table_count <= 4096 or 12 + 16 * table_count > len(font):
        raise BuildError(f"{label}: malformed table directory")
    tables: dict[bytes, tuple[int, int]] = {}
    for index in range(table_count):
        record = 12 + 16 * index
        tag = font[record : record + 4]
        offset = _be_u32(font, record + 8, label)
        length = _be_u32(font, record + 12, label)
        if tag in tables or offset + length > len(font):
            raise BuildError(f"{label}: invalid table {tag!r}")
        tables[tag] = (offset, length)
    if b"cmap" not in tables:
        raise BuildError(f"{label}: missing cmap")
    offset, length = tables[b"cmap"]
    cmap = font[offset : offset + length]
    count = _be_u16(cmap, 2, label)
    if _be_u16(cmap, 0, label) != 0 or 4 + 8 * count > len(cmap):
        raise BuildError(f"{label}: malformed cmap header")
    result: list[dict[str, Any]] = []
    for index in range(count):
        record = 4 + 8 * index
        platform = _be_u16(cmap, record, label)
        encoding = _be_u16(cmap, record + 2, label)
        relative = _be_u32(cmap, record + 4, label)
        if not (platform == 0 or (platform == 3 and encoding in (1, 10))):
            continue
        fmt = _be_u16(cmap, relative, label)
        if fmt in (0, 2, 4, 6):
            sub_length = _be_u16(cmap, relative + 2, label)
        elif fmt in (8, 10, 12, 13, 14):
            sub_length = _be_u32(cmap, relative + 4, label)
        else:
            continue
        if sub_length < 4 or relative + sub_length > len(cmap):
            raise BuildError(f"{label}: malformed cmap format {fmt}")
        if fmt in (0, 4, 6, 12, 13):
            result.append({"platform": platform, "encoding": encoding, "format": fmt, "data": cmap[relative : relative + sub_length]})
    if not result:
        raise BuildError(f"{label}: no supported Unicode cmap")
    return result


def cmap_glyph_id(subtable: dict[str, Any], codepoint: int, label: str) -> int:
    data = subtable["data"]
    fmt = int(subtable["format"])
    if fmt == 0:
        return data[6 + codepoint] if len(data) >= 262 and codepoint <= 0xFF else 0
    if fmt == 6:
        if len(data) < 10 or codepoint > 0xFFFF:
            return 0
        first = _be_u16(data, 6, label)
        count = _be_u16(data, 8, label)
        return _be_u16(data, 10 + 2 * (codepoint - first), label) if first <= codepoint < first + count else 0
    if fmt == 4:
        if codepoint > 0xFFFF or len(data) < 16:
            return 0
        count = _be_u16(data, 6, label) // 2
        end_offset = 14
        start_offset = end_offset + 2 * count + 2
        delta_offset = start_offset + 2 * count
        range_offset = delta_offset + 2 * count
        for segment in range(count):
            end = _be_u16(data, end_offset + 2 * segment, label)
            if codepoint > end:
                continue
            start = _be_u16(data, start_offset + 2 * segment, label)
            if codepoint < start:
                return 0
            delta = _be_i16(data, delta_offset + 2 * segment, label)
            word = range_offset + 2 * segment
            distance = _be_u16(data, word, label)
            if distance == 0:
                return (codepoint + delta) & 0xFFFF
            glyph = _be_u16(data, word + distance + 2 * (codepoint - start), label)
            return (glyph + delta) & 0xFFFF if glyph else 0
        return 0
    if fmt in (12, 13):
        groups = _be_u32(data, 12, label)
        low, high = 0, groups
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
                first = _be_u32(data, group + 8, label)
                return first if fmt == 13 else first + codepoint - start
        return 0
    raise BuildError(f"{label}: unsupported cmap format {fmt}")


@dataclass(frozen=True)
class TableLayout:
    table: int
    offset: int
    end: int
    record_count: int
    cell: int


@dataclass(frozen=True)
class G1NLayout:
    header_size: int
    atlas_offset: int
    table_offsets: tuple[int, ...]
    tables: tuple[TableLayout, ...]


def parse_g1n(data: bytes, label: str) -> G1NLayout:
    if len(data) < 0x2C or data[:8] != G1N_MAGIC:
        raise BuildError(f"{label}: not a G1N")
    declared, header_size, _unknown, atlas_offset, palette_count, table_count = struct.unpack_from("<IIIIII", data, 0x08)
    if declared != len(data) or table_count != 3:
        raise BuildError(f"{label}: size or table count mismatch")
    if header_size != 0x20 + 4 * table_count + 0x40 * palette_count:
        raise BuildError(f"{label}: header equation mismatch")
    offsets = tuple(struct.unpack_from(f"<{table_count}I", data, 0x20))
    if offsets[0] != header_size or tuple(sorted(set(offsets))) != offsets or not offsets[-1] < atlas_offset <= len(data):
        raise BuildError(f"{label}: invalid table offsets")
    ends = (*offsets[1:], atlas_offset)
    tables: list[TableLayout] = []
    for table, (offset, end) in enumerate(zip(offsets, ends, strict=True)):
        record_bytes = end - offset - MAP_SIZE
        if record_bytes < RECORD_SIZE or record_bytes % RECORD_SIZE:
            raise BuildError(f"{label}: malformed table {table}")
        record_count = record_bytes // RECORD_SIZE
        largest = max(
            (ordinal for (ordinal,) in struct.iter_unpack("<H", data[offset : offset + MAP_SIZE])),
            default=0,
        )
        if largest >= record_count:
            raise BuildError(f"{label}: mapped ordinal exceeds table {table} record count")
        cells: set[int] = set()
        for ordinal in range(record_count):
            record = offset + MAP_SIZE + ordinal * RECORD_SIZE
            width0, cell1, zero2, cell3, width4, _center5, zero6, cell7 = data[record : record + 8]
            # Current v0.94 inputs preserve JP metric field 4 independently
            # from the width-packed pixel field 0.  It is deliberately not
            # normalized here; only the uniform cell fields and pixel width
            # are structural inputs to this table-1-only replacement.
            if zero2 or zero6 or not 0 <= width0 <= cell1 or cell1 != cell3 or cell1 != cell7:
                raise BuildError(f"{label}: invalid record geometry table={table} ordinal={ordinal}")
            pointer = struct.unpack_from("<I", data, record + 8)[0]
            if pointer + width0 * cell1 // 2 > len(data) - atlas_offset:
                raise BuildError(f"{label}: atlas pointer exceeds payload table={table} ordinal={ordinal}")
            cells.add(cell1)
        if len(cells) != 1 or next(iter(cells)) not in PROFILE_BY_CELL:
            raise BuildError(f"{label}: unsupported cell geometry in table {table}")
        tables.append(TableLayout(table, offset, end, record_count, next(iter(cells))))
    return G1NLayout(header_size, atlas_offset, offsets, tuple(tables))


def mapped_hangul(data: bytes, table: TableLayout) -> list[int]:
    return [cp for cp in range(HANGUL_START, HANGUL_END + 1) if struct.unpack_from("<H", data, table.offset + 2 * cp)[0] != 0]


def extract_g1n(blob: bytes, entry: int, label: str) -> tuple[Any, bytes]:
    archive = lz4.parse_link(blob)
    if lz4.rebuild_link(archive) != blob:
        raise BuildError(f"{label}: LINK roundtrip mismatch")
    wrapper, raw = lz4.decompress_wrapper(archive.entries[entry].data)
    if raw[:8] != G1N_MAGIC:
        raise BuildError(f"{label}: entry {entry} is not G1N")
    return wrapper, raw


def require_input(path: Path, spec: dict[str, Any], label: str) -> bytes:
    if not path.is_file():
        raise BuildError(f"{label}: missing input {path}")
    size = path.stat().st_size
    digest = sha256_file(path)
    if size != spec["size"] or digest != spec["sha256"]:
        raise BuildError(f"{label}: input pin mismatch size={size} sha256={digest}")
    return path.read_bytes()


def validate_font(path: Path) -> tuple[bytes, list[dict[str, Any]]]:
    if not path.is_file() or path.name != FONT_NAME or path.stat().st_size != FONT_SIZE:
        raise BuildError("official Griun PolSensibility TTF path/name/size mismatch")
    raw = path.read_bytes()
    if sha256_bytes(raw) != FONT_SHA256:
        raise BuildError("official Griun PolSensibility TTF SHA-256 mismatch")
    return raw, parse_unicode_cmap(raw, "Griun PolSensibility")


def run_rasterizer(font: Path, codepoints: Sequence[int], output: Path, powershell: str) -> dict[int, bytes]:
    request = {
        "schema": FONT_SCHEMA,
        "font": {"path": str(font), "file_name": FONT_NAME, "family": FONT_FAMILY, "size": FONT_SIZE, "sha256": FONT_SHA256},
        "codepoints": [canonical_cp(cp) for cp in codepoints],
        "profiles": [PROFILE_BY_CELL[cell] for cell in sorted(PROFILE_BY_CELL)],
        "preview_text": "독안룡 오다 노부나가 시마즈 요시히사 아즈치성 큿",
    }
    raster_root = output / "raster"
    raster_root.mkdir(parents=True, exist_ok=True)
    request_path = output / "raster_request.json"
    request_path.write_bytes(encode_json(request))
    command = [powershell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT_DIR / "rasterize_griun_polsensibility_v1.ps1"), "-RequestPathInput", str(request_path), "-OutputDirectory", str(raster_root)]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode:
        raise BuildError(f"rasterizer failed\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}")
    result = strict_json((raster_root / "raster_result.json").read_bytes(), "raster result")
    if result.get("schema") != FONT_RESULT_SCHEMA or result.get("codepoints") != request["codepoints"]:
        raise BuildError("raster result schema/codepoint mismatch")
    rows = result.get("profiles")
    if not isinstance(rows, list) or len(rows) != len(PROFILE_BY_CELL):
        raise BuildError("raster result profile set mismatch")
    payloads: dict[int, bytes] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise BuildError("invalid raster profile descriptor")
        cell = int(row.get("cell", 0))
        profile = PROFILE_BY_CELL.get(cell)
        if profile is None or row.get("profile") != profile["profile"] or row.get("raster_size") != profile["raster_size"]:
            raise BuildError("raster geometry mismatch")
        name = f"glyph_pixels_{profile['profile']}.pixels"
        if row.get("path") != name:
            raise BuildError("raster payload path mismatch")
        payload = (raster_root / name).read_bytes()
        expected = len(codepoints) * (cell // 2) * cell
        if len(payload) != expected or row.get("size") != expected or row.get("sha256") != sha256_bytes(payload):
            raise BuildError("raster payload size/hash mismatch")
        if int(row.get("minimum_margin", 0)) < 1 or int(row.get("blank_glyph_count", -1)) != 0:
            raise BuildError("raster payload has blank or edge-touching glyph")
        payloads[cell] = payload
    if set(payloads) != set(PROFILE_BY_CELL):
        raise BuildError("raster cell coverage mismatch")
    return payloads


def _pixel_nibble(data: bytes, row_width: int, x: int, y: int) -> int:
    value = data[y * (row_width // 2) + x // 2]
    return value >> 4 if x % 2 == 0 else value & 0x0F


def fit_glyph_to_record_width(full_cell: bytes, cell: int, width: int) -> tuple[bytes, dict[str, Any]]:
    """Fit a centered full-cell raster into an existing width-packed record.

    The G1N record and pointer remain byte-exact.  Ink is copied at 1:1 when
    it fits the record with a one-pixel horizontal margin; otherwise only the
    horizontal axis is nearest-neighbour scaled to that clipping-safe width.
    """

    expected = (cell // 2) * cell
    if len(full_cell) != expected or not 0 < width <= cell or width % 2:
        raise BuildError(f"invalid full-cell/record geometry cell={cell} width={width}")
    ink = [
        (x, y)
        for y in range(cell)
        for x in range(cell)
        if _pixel_nibble(full_cell, cell, x, y)
    ]
    if not ink:
        raise BuildError("blank full-cell raster")
    min_x = min(x for x, _y in ink)
    max_x = max(x for x, _y in ink)
    min_y = min(y for _x, y in ink)
    max_y = max(y for _x, y in ink)
    source_width = max_x - min_x + 1
    if min_y < 1 or max_y >= cell - 1:
        raise BuildError("full-cell raster has no vertical safety margin")
    if width == cell:
        return full_cell, {
            "mode": "full_cell",
            "source_ink_width": source_width,
            "target_ink_width": source_width,
            "minimum_horizontal_margin": min(min_x, cell - 1 - max_x),
        }

    target_width = min(source_width, width - 2)
    if target_width < 1:
        raise BuildError(f"record width is too narrow for safe ink: {width}")
    scaled = source_width > target_width
    destination_x = (width - target_width) // 2
    packed = bytearray((width // 2) * cell)
    for y in range(min_y, max_y + 1):
        for dx in range(target_width):
            source_dx = (
                min(source_width - 1, int(((dx + 0.5) * source_width) // target_width))
                if scaled
                else dx
            )
            value = _pixel_nibble(full_cell, cell, min_x + source_dx, y)
            if not value:
                continue
            x = destination_x + dx
            index = y * (width // 2) + x // 2
            if x % 2 == 0:
                packed[index] |= value << 4
            else:
                packed[index] |= value
    if not any(packed):
        raise BuildError("width-fitted raster is blank")
    fitted_ink = [
        (x, y)
        for y in range(cell)
        for x in range(width)
        if _pixel_nibble(packed, width, x, y)
    ]
    fitted_min_x = min(x for x, _y in fitted_ink)
    fitted_max_x = max(x for x, _y in fitted_ink)
    margin = min(fitted_min_x, width - 1 - fitted_max_x)
    if margin < 1:
        raise BuildError("width-fitted raster touches the horizontal edge")
    return bytes(packed), {
        "mode": "horizontal_scale" if scaled else "centered_crop",
        "source_ink_width": source_width,
        "target_ink_width": fitted_max_x - fitted_min_x + 1,
        "minimum_horizontal_margin": margin,
    }


def replace_g1n_pixels(data: bytes, payloads: dict[int, bytes], raster_index: dict[int, int], direct: set[int], exceptions: set[int], label: str) -> tuple[bytes, dict[str, Any]]:
    layout = parse_g1n(data, label)
    output = bytearray(data)
    spans: list[tuple[int, int, int, int]] = []
    table_rows: list[dict[str, Any]] = []
    for table in layout.tables:
        mapped = mapped_hangul(data, table)
        target = sorted(set(mapped) & direct) if table.table == TARGET_TABLE else []
        retained = sorted(set(mapped) & exceptions)
        stride = (table.cell // 2) * table.cell
        payload = payloads[table.cell] if table.table == TARGET_TABLE else b""
        pointers: set[int] = set()
        before_digest = hashlib.sha256()
        after_digest = hashlib.sha256()
        fit_modes: dict[str, int] = {"full_cell": 0, "centered_crop": 0, "horizontal_scale": 0}
        minimum_horizontal_margin = table.cell
        for cp in target:
            ordinal = struct.unpack_from("<H", data, table.offset + 2 * cp)[0]
            if not 0 < ordinal < table.record_count:
                raise BuildError(f"{label}: invalid ordinal for {canonical_cp(cp)}")
            record = table.offset + MAP_SIZE + ordinal * RECORD_SIZE
            width = data[record]
            pointer = struct.unpack_from("<I", data, record + 8)[0]
            start = layout.atlas_offset + pointer
            end = start + width * table.cell // 2
            if start < layout.atlas_offset or end > len(data) or pointer in pointers:
                raise BuildError(f"{label}: invalid or aliased pixel span for {canonical_cp(cp)}")
            pointers.add(pointer)
            index = raster_index[cp]
            full_cell = payload[index * stride : (index + 1) * stride]
            replacement, fit = fit_glyph_to_record_width(full_cell, table.cell, width)
            if len(replacement) != end - start:
                raise BuildError(f"{label}: fitted pixel size mismatch for {canonical_cp(cp)}")
            fit_modes[fit["mode"]] += 1
            minimum_horizontal_margin = min(minimum_horizontal_margin, fit["minimum_horizontal_margin"])
            before_digest.update(data[start:end])
            after_digest.update(replacement)
            output[start:end] = replacement
            spans.append((start, end, table.table, cp))
        table_rows.append({
            "table": table.table,
            "cell": table.cell,
            "mapped_hangul_count": len(mapped),
            "replaced_hangul_count": len(target),
            "replaced_codepoints_sha256": codepoint_hash(target),
            "retained_exception_count": len(retained),
            "retained_exceptions": [canonical_cp(cp) for cp in retained],
            "target_table": table.table == TARGET_TABLE,
            "table_bytes_exact": table.table != TARGET_TABLE,
            "record_geometry_exact": True,
            "width_fit_modes": fit_modes,
            "minimum_horizontal_margin": minimum_horizontal_margin if target else None,
            "pixels_before_sha256": before_digest.hexdigest().upper(),
            "pixels_after_sha256": after_digest.hexdigest().upper(),
        })
    spans.sort()
    for left, right in zip(spans, spans[1:]):
        if left[1] > right[0]:
            raise BuildError(f"{label}: overlapping target spans")
    protected_spans: list[tuple[int, int]] = []
    for table in layout.tables:
        if table.table == TARGET_TABLE:
            continue
        for ordinal in range(table.record_count):
            record = table.offset + MAP_SIZE + ordinal * RECORD_SIZE
            width = data[record]
            if not width:
                continue
            start = layout.atlas_offset + struct.unpack_from("<I", data, record + 8)[0]
            protected_spans.append((start, start + width * table.cell // 2))
    protected_spans.sort()
    protected_starts = [start for start, _end in protected_spans]
    for start, end, _table, cp in spans:
        index = bisect.bisect_right(protected_starts, start)
        if (index and protected_spans[index - 1][1] > start) or (
            index < len(protected_spans) and protected_spans[index][0] < end
        ):
            raise BuildError(f"{label}: table 1 {canonical_cp(cp)} aliases table 0/2 pixels")
    cursor = 0
    for start, end, _table, _cp in spans:
        if output[cursor:start] != data[cursor:start]:
            raise BuildError(f"{label}: byte changed outside target spans")
        cursor = end
    if output[cursor:] != data[cursor:]:
        raise BuildError(f"{label}: trailing byte changed outside target spans")
    candidate = bytes(output)
    if len(candidate) != len(data) or candidate[: layout.atlas_offset] != data[: layout.atlas_offset]:
        raise BuildError(f"{label}: G1N structure changed")
    for cp in exceptions:
        for table in layout.tables:
            ordinal = struct.unpack_from("<H", data, table.offset + 2 * cp)[0]
            if ordinal:
                record = table.offset + MAP_SIZE + ordinal * RECORD_SIZE
                width = data[record]
                pointer = struct.unpack_from("<I", data, record + 8)[0]
                start = layout.atlas_offset + pointer
                size = width * table.cell // 2
                if candidate[start : start + size] != data[start : start + size]:
                    raise BuildError(f"{label}: exception {canonical_cp(cp)} changed")
    return candidate, {
        "input_size": len(data),
        "input_sha256": sha256_bytes(data),
        "output_size": len(candidate),
        "output_sha256": sha256_bytes(candidate),
        "structure_prefix_exact": True,
        "target_table": TARGET_TABLE,
        "tables_0_and_2_exact": True,
        "changes_confined_to_table_1_mapped_hangul_pixel_spans": True,
        "target_span_count": len(spans),
        "tables": table_rows,
    }


def rebuild_archive(blob: bytes, replacements: dict[int, bytes], label: str) -> tuple[bytes, dict[str, Any]]:
    archive = lz4.parse_link(blob)
    wrapped: dict[int, bytes] = {}
    for entry, raw in replacements.items():
        wrapper, _old = lz4.decompress_wrapper(archive.entries[entry].data)
        wrapped[entry] = lz4.recompress_wrapper_greedy(raw, wrapper)
    candidate = lz4.rebuild_link(archive, wrapped)
    check = lz4.parse_link(candidate)
    if lz4.rebuild_link(check) != candidate or len(check.entries) != len(archive.entries):
        raise BuildError(f"{label}: candidate LINK roundtrip failed")
    for index, (before, after) in enumerate(zip(archive.entries, check.entries, strict=True)):
        if index in replacements:
            _wrapper, raw = lz4.decompress_wrapper(after.data)
            if raw != replacements[index]:
                raise BuildError(f"{label}: target entry {index} re-extraction mismatch")
        elif before.data != after.data or before.gap_after != after.gap_after:
            raise BuildError(f"{label}: non-target entry {index} changed")
    return candidate, {"link_entry_count": len(archive.entries), "target_entries": sorted(replacements), "non_target_entries_exact": True, "link_roundtrip_exact": True}


def validate_output_root(output: Path, inputs: Sequence[Path]) -> None:
    resolved = output.resolve()
    if resolved == REPO_ROOT.resolve() or REPO_ROOT.resolve() not in resolved.parents:
        raise BuildError("output root must be below this worktree")
    for source in inputs:
        source = source.resolve()
        if resolved == source or resolved in source.parents or source in resolved.parents:
            raise BuildError("output root overlaps an input")
    if resolved.exists() and any(resolved.iterdir()):
        raise BuildError("output root must be absent or empty")


def build(args: argparse.Namespace) -> int:
    input_root = args.input_root.resolve()
    font = args.font.resolve()
    output = args.output_root.resolve()
    paths = [input_root / spec["relative_path"] for spec in ROUTES.values()]
    validate_output_root(output, [font, *paths])
    output.mkdir(parents=True, exist_ok=True)
    font_raw, cmap = validate_font(font)
    blobs: dict[str, bytes] = {}
    g1n_inputs: dict[tuple[str, int], bytes] = {}
    mapped_union: set[int] = set()
    for route, spec in ROUTES.items():
        blob = require_input(input_root / spec["relative_path"], spec, route)
        blobs[route] = blob
        for entry in spec["entries"]:
            _wrapper, raw = extract_g1n(blob, entry, route)
            g1n_inputs[(route, entry)] = raw
            layout = parse_g1n(raw, f"{route}/{entry}")
            mapped_union.update(mapped_hangul(raw, layout.tables[TARGET_TABLE]))
    covered = {cp for cp in mapped_union if any(cmap_glyph_id(row, cp, "Griun PolSensibility") for row in cmap)}
    missing = mapped_union - covered
    if missing != set(CMAP_EXCEPTIONS):
        raise BuildError(f"unexpected Griun cmap exceptions: {[canonical_cp(cp) for cp in sorted(missing)]}")
    codepoints = sorted(covered)
    raster_index = {cp: index for index, cp in enumerate(codepoints)}
    # System.Drawing's private-font path is the established Windows GDI+
    # runtime used by the existing G1N builders.  Prefer Windows PowerShell;
    # PowerShell 7 needs an environment-specific System.Drawing.Common
    # compiler reference and must not silently change this raster route.
    powershell = args.powershell or shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        raise BuildError("PowerShell runtime not found")
    payloads = run_rasterizer(font, codepoints, output, powershell)

    route_reports: list[dict[str, Any]] = []
    candidate_root = output / "candidate"
    for route, spec in ROUTES.items():
        replacements: dict[int, bytes] = {}
        entry_reports: list[dict[str, Any]] = []
        for entry in spec["entries"]:
            candidate_g1n, report = replace_g1n_pixels(g1n_inputs[(route, entry)], payloads, raster_index, covered, set(CMAP_EXCEPTIONS), f"{route}/{entry}")
            replacements[entry] = candidate_g1n
            report["outer_entry"] = entry
            entry_reports.append(report)
        candidate, archive_report = rebuild_archive(blobs[route], replacements, route)
        destination = candidate_root / spec["relative_path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidate)
        route_reports.append({
            "route": route,
            "relative_path": spec["relative_path"],
            "input_size": len(blobs[route]),
            "input_sha256": sha256_bytes(blobs[route]),
            "candidate_size": len(candidate),
            "candidate_sha256": sha256_bytes(candidate),
            "archive": archive_report,
            "g1n_entries": entry_reports,
        })

    validation = {
        "schema": SCHEMA,
        "passed": True,
        "font": {
            "official_page": "https://www.griun.co.kr/fonts/polsensibility",
            "download_url": "https://d26ciffk7xlrlz.cloudfront.net/free-fonts/polsensibility/Griun_PolSensibility-Rg.ttf",
            "file_name": FONT_NAME,
            "family": FONT_FAMILY,
            "size": len(font_raw),
            "sha256": sha256_bytes(font_raw),
            "font_file_modified": False,
            "font_file_included_in_output": False,
        },
        "coverage": {
            "mapped_hangul_union_count": len(mapped_union),
            "mapped_hangul_union_sha256": codepoint_hash(mapped_union),
            "direct_griun_count": len(covered),
            "direct_griun_sha256": codepoint_hash(covered),
            "retained_exception_count": len(missing),
            "retained_exceptions": [canonical_cp(cp) for cp in sorted(missing)],
            "demanded_exception": canonical_cp(DEMANDED_EXCEPTION),
            "demanded_exception_policy": "retain current G1N glyph by explicit user direction",
            "os_font_fallback_used": False,
        },
        "profiles": [PROFILE_BY_CELL[cell] for cell in sorted(PROFILE_BY_CELL)],
        "target_table": TARGET_TABLE,
        "routes": route_reports,
        "safety": {
            "installed_game_files_modified": False,
            "steam_deployment_performed": False,
            "input_archives_modified": False,
            "non_target_link_entries_exact": True,
            "g1n_maps_records_metrics_pointers_exact": True,
            "g1n_tables_0_and_2_exact": True,
            "changes_confined_to_table_1_direct_griun_hangul_pixel_spans": True,
        },
    }
    (output / "validation.v1.json").write_bytes(encode_json(validation))
    print(json.dumps({"validation": str(output / "validation.v1.json"), "candidates": [{"path": row["relative_path"], "size": row["candidate_size"], "sha256": row["candidate_sha256"]} for row in route_reports]}, ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--input-root", type=Path, required=True)
    result.add_argument("--font", type=Path, required=True)
    result.add_argument("--output-root", type=Path, required=True)
    result.add_argument("--powershell")
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(build(parser().parse_args()))
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
