#!/usr/bin/env python3
"""Privately inventory and decode PC/Switch ``res_lang`` UI textures.

This is a read-only forensic helper for locating rasterized UI labels such as
the bottom ``返回`` button.  It understands the nested container shape used by
NOBU16::

    res_lang.bin (outer LINK)
      /N (32-byte-header LINK bundle)
        /M (raw-LZ4 wrapped G1T)
          texture T

It writes decoded comparison images and JSON only below the repository's
ignored ``tmp`` directory.  It never replaces a game file and does not touch
the process, executable, DLLs, registry, or memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TMP_ROOT = PROJECT_ROOT / "tmp"
STRDATA_WORKSTREAM = PROJECT_ROOT / "workstreams" / "strdata"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(STRDATA_WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(STRDATA_WORKSTREAM))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as image_codec  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


class TraceError(ValueError):
    """Raised when an input is outside the observed res_lang contract."""


@dataclass(frozen=True)
class BundleEntry:
    index: int
    offset: int
    stored_size: int
    data: bytes


@dataclass(frozen=True)
class Bundle:
    resource_id: int
    entries: tuple[BundleEntry, ...]


@dataclass(frozen=True)
class Texture:
    index: int
    start: int
    end: int
    payload_offset: int
    format_code: int
    packed_info: int
    width: int
    height: int
    mip_count: int
    extra_version: int
    base_payload: bytes


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & -alignment


def private_output_root(value: str | Path) -> Path:
    root = Path(value).resolve()
    tmp = TMP_ROOT.resolve()
    try:
        root.relative_to(tmp)
    except ValueError as exc:
        raise TraceError(f"output must stay below {tmp}") from exc
    return root


def parse_bundle(blob: bytes) -> Bundle:
    if len(blob) < 32 or blob[:4] != b"LINK":
        raise TraceError("bundle is not a 32-byte-header LINK")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from(
        "<4I", blob, 4
    )
    if count == 0 or table_offset != 32:
        raise TraceError("unsupported bundle count/table offset")
    if blob[20:32] != b"\0" * 12:
        raise TraceError("unsupported bundle extension words")
    table_end = table_offset + count * 8
    if aligned_table_end != align_up(table_end, 32):
        raise TraceError("bundle aligned table-end field is inconsistent")
    if aligned_table_end > len(blob):
        raise TraceError("bundle table exceeds input")
    pairs = [
        struct.unpack_from("<II", blob, table_offset + index * 8)
        for index in range(count)
    ]
    entries: list[BundleEntry] = []
    for index, (offset, stored_size) in enumerate(pairs):
        end = offset + stored_size
        next_offset = pairs[index + 1][0] if index + 1 < count else end
        if offset < aligned_table_end or end > next_offset:
            raise TraceError(f"bundle entry {index} has invalid bounds")
        # Switch archives retain a few PC-only table slots whose nominal data
        # ranges are beyond the physical EOF (notably /1/4..5 and /3/108..109).
        # They are semantic placeholders, not truncated bytes to decode.
        if offset >= len(blob) or end > len(blob):
            continue
        entries.append(BundleEntry(index, offset, stored_size, blob[offset:end]))
    return Bundle(resource_id=resource_id, entries=tuple(entries))


def bc_payload_size(format_code: int, width: int, height: int) -> int:
    blocks = ((width + 3) // 4) * ((height + 3) // 4)
    if format_code == 0x59:  # NOBU16 PC/Switch alias for BC1/DXT1
        return blocks * 8
    if format_code == 0x5B:  # NOBU16 PC/Switch alias for BC3/DXT5
        return blocks * 16
    raise TraceError(f"unsupported texture format 0x{format_code:02X}")


def parse_g1t(blob: bytes) -> tuple[dict[str, int], tuple[Texture, ...]]:
    if len(blob) < 32 or blob[:8] != b"GT1G0600":
        raise TraceError("resource is not GT1G0600")
    declared_size, directory_offset, texture_count, platform = struct.unpack_from(
        "<4I", blob, 8
    )
    if declared_size != len(blob) or texture_count == 0:
        raise TraceError("G1T declared size/count is invalid")
    directory_end = directory_offset + texture_count * 4
    if directory_offset < 32 or directory_end > len(blob):
        raise TraceError("G1T directory is out of bounds")
    relative_offsets = struct.unpack_from(
        "<" + "I" * texture_count, blob, directory_offset
    )
    starts = [directory_offset + value for value in relative_offsets]
    if starts != sorted(starts) or starts[0] < directory_end or starts[-1] >= len(blob):
        raise TraceError("G1T texture offsets are invalid")

    textures: list[Texture] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < texture_count else len(blob)
        if end - start < 8:
            raise TraceError(f"G1T texture {index} header is truncated")
        packed_info, format_code, packed_dimensions = struct.unpack_from(
            "<BBB", blob, start
        )
        mip_count = packed_info >> 4
        width = 1 << (packed_dimensions & 0x0F)
        height = 1 << (packed_dimensions >> 4)
        extra_version = blob[start + 7]
        if extra_version:
            if end - start < 12:
                raise TraceError(f"G1T texture {index} extra header is truncated")
            extra_length = struct.unpack_from("<I", blob, start + 8)[0]
            if extra_length < 4:
                raise TraceError(f"G1T texture {index} extra length is invalid")
            payload_offset = start + 8 + extra_length
        else:
            payload_offset = start + 8

        base_payload = b""
        if format_code in (0x59, 0x5B):
            expected = bc_payload_size(format_code, width, height)
            payload_end = payload_offset + expected
            if payload_end > end:
                raise TraceError(
                    f"G1T texture {index} base mip exceeds its entry: "
                    f"{width}x{height} format=0x{format_code:02X}"
                )
            base_payload = blob[payload_offset:payload_end]
        textures.append(
            Texture(
                index=index,
                start=start,
                end=end,
                payload_offset=payload_offset,
                format_code=format_code,
                packed_info=packed_info,
                width=width,
                height=height,
                mip_count=mip_count,
                extra_version=extra_version,
                base_payload=base_payload,
            )
        )
    return {
        "declared_size": declared_size,
        "directory_offset": directory_offset,
        "texture_count": texture_count,
        "platform": platform,
    }, tuple(textures)


def decode_bc1_block(block: bytes) -> bytes:
    if len(block) != 8:
        raise TraceError("BC1 block must contain 8 bytes")
    color0, color1, indices = struct.unpack("<HHI", block)
    first = image_codec.expand_565(color0)
    second = image_codec.expand_565(color1)
    if color0 > color1:
        third = tuple((2 * first[i] + second[i] + 1) // 3 for i in range(3))
        fourth = tuple((first[i] + 2 * second[i] + 1) // 3 for i in range(3))
        palette = (
            (*first, 255),
            (*second, 255),
            (*third, 255),
            (*fourth, 255),
        )
    else:
        third = tuple((first[i] + second[i] + 1) // 2 for i in range(3))
        palette = ((*first, 255), (*second, 255), (*third, 255), (0, 0, 0, 0))
    output = bytearray(64)
    for pixel in range(16):
        output[pixel * 4 : pixel * 4 + 4] = bytes(
            palette[(indices >> (pixel * 2)) & 3]
        )
    return bytes(output)


def decode_bc1(data: bytes, width: int, height: int) -> bytes:
    blocks_wide = (width + 3) // 4
    blocks_high = (height + 3) // 4
    if len(data) != blocks_wide * blocks_high * 8:
        raise TraceError("BC1 payload size is inconsistent")
    output = bytearray(width * height * 4)
    offset = 0
    for block_y in range(blocks_high):
        for block_x in range(blocks_wide):
            pixels = decode_bc1_block(data[offset : offset + 8])
            offset += 8
            for local_y in range(4):
                y = block_y * 4 + local_y
                if y >= height:
                    continue
                for local_x in range(4):
                    x = block_x * 4 + local_x
                    if x >= width:
                        continue
                    source = (local_y * 4 + local_x) * 4
                    target = (y * width + x) * 4
                    output[target : target + 4] = pixels[source : source + 4]
    return bytes(output)


def decode_texture(texture: Texture) -> bytes:
    if texture.format_code == 0x59:
        return decode_bc1(texture.base_payload, texture.width, texture.height)
    if texture.format_code == 0x5B:
        return image_codec.decode_bc3(
            texture.base_payload, texture.width, texture.height
        )
    raise TraceError(f"texture format 0x{texture.format_code:02X} is not decodable")


def alpha_bbox(rgba: bytes, width: int, height: int) -> list[int] | None:
    xs: list[int] = []
    ys: list[int] = []
    for y in range(height):
        row = y * width * 4
        for x in range(width):
            if rgba[row + x * 4 + 3]:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def composite_checker(rgba: bytes, width: int, height: int) -> bytes:
    output = bytearray(len(rgba))
    for y in range(height):
        for x in range(width):
            source = (y * width + x) * 4
            alpha = rgba[source + 3]
            background = 42 if ((x // 8) ^ (y // 8)) & 1 else 26
            for channel in range(3):
                value = rgba[source + channel]
                output[source + channel] = (
                    value * alpha + background * (255 - alpha) + 127
                ) // 255
            output[source + 3] = 255
    return bytes(output)


def nearest_resize(
    rgba: bytes, width: int, height: int, target_width: int, target_height: int
) -> bytes:
    output = bytearray(target_width * target_height * 4)
    for y in range(target_height):
        source_y = min(height - 1, y * height // target_height)
        for x in range(target_width):
            source_x = min(width - 1, x * width // target_width)
            source = (source_y * width + source_x) * 4
            target = (y * target_width + x) * 4
            output[target : target + 4] = rgba[source : source + 4]
    return bytes(output)


def fit_image(rgba: bytes, width: int, height: int, box_w: int, box_h: int) -> tuple[bytes, int, int]:
    scale = min(box_w / width, box_h / height, 1.0)
    target_w = max(1, round(width * scale))
    target_h = max(1, round(height * scale))
    return nearest_resize(rgba, width, height, target_w, target_h), target_w, target_h


def paste(
    canvas: bytearray,
    canvas_width: int,
    canvas_height: int,
    rgba: bytes,
    width: int,
    height: int,
    x0: int,
    y0: int,
) -> None:
    for y in range(height):
        if not (0 <= y0 + y < canvas_height):
            continue
        source = y * width * 4
        target = ((y0 + y) * canvas_width + x0) * 4
        canvas[target : target + width * 4] = rgba[source : source + width * 4]


FONT = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "001", "001", "001"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
    "/": ("001", "001", "010", "100", "100"),
    "P": ("110", "101", "110", "100", "100"),
    "S": ("111", "100", "111", "001", "111"),
}


def draw_text(
    canvas: bytearray, canvas_width: int, canvas_height: int, text: str, x0: int, y0: int
) -> None:
    for char_index, char in enumerate(text):
        glyph = FONT.get(char)
        if glyph is None:
            continue
        for y, row in enumerate(glyph):
            for x, bit in enumerate(row):
                if bit == "1" and 0 <= x0 + char_index * 4 + x < canvas_width and 0 <= y0 + y < canvas_height:
                    offset = ((y0 + y) * canvas_width + x0 + char_index * 4 + x) * 4
                    canvas[offset : offset + 4] = b"\xFF\xE0\x50\xFF"


def write_png(path: Path, rgba: bytes, width: int, height: int) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = image_codec.encode_rgba_png(rgba, width, height)
    path.write_bytes(blob)
    return sha256_bytes(blob)


PAIR_NAME_RE = re.compile(r"^o(?P<outer>\d+)_c(?P<container>\d+)_t(?P<texture>\d+)\.png$")


def build_existing_contact_sheets(output_root: Path) -> list[dict[str, object]]:
    """Tile existing pair previews without re-reading either game archive."""
    pair_root = output_root / "private" / "pairs"
    grouped: dict[int, list[Path]] = {}
    for path in sorted(pair_root.glob("*.png")):
        match = PAIR_NAME_RE.match(path.name)
        if match is None:
            continue
        grouped.setdefault(int(match.group("outer")), []).append(path)

    sheets: list[dict[str, object]] = []
    columns = 3
    rows = 4
    per_page = columns * rows
    cell_w = 520
    cell_h = 170
    sheet_root = output_root / "private" / "contact_sheets"
    sheet_root.mkdir(parents=True, exist_ok=True)
    for outer_index, paths in sorted(grouped.items()):
        for page_index in range((len(paths) + per_page - 1) // per_page):
            page = paths[page_index * per_page : (page_index + 1) * per_page]
            width = columns * cell_w
            height = rows * cell_h
            canvas = bytearray(bytes((10, 10, 10, 255)) * (width * height))
            for item_index, path in enumerate(page):
                rgba, item_w, item_h = image_codec.decode_png(path.read_bytes())
                if (item_w, item_h) != (cell_w, cell_h):
                    raise TraceError(f"unexpected pair preview dimensions: {path}")
                x = (item_index % columns) * cell_w
                y = (item_index // columns) * cell_h
                paste(canvas, width, height, rgba, item_w, item_h, x, y)
            output = sheet_root / f"outer_{outer_index:02d}_page_{page_index + 1:02d}.png"
            png_sha = write_png(output, bytes(canvas), width, height)
            sheets.append(
                {
                    "outer_index": outer_index,
                    "page": page_index + 1,
                    "item_files": [path.name for path in page],
                    "path": str(output),
                    "dimensions": [width, height],
                    "sha256": png_sha,
                }
            )
    manifest = output_root / "contact_sheets.json"
    manifest.write_text(json.dumps(sheets, ensure_ascii=False, indent=2), encoding="utf-8")
    return sheets


def load_archive(path: Path) -> tuple[bytes, lz4.LinkArchive]:
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    if lz4.rebuild_link(outer) != blob:
        raise TraceError(f"outer LINK identity gate failed: {path}")
    return blob, outer


BOTTOM_RETURN_COORDINATE = (1, 22)
EXPECTED_BOTTOM_RETURN_HASHES = {
    "pc_sc": "21DB128C982FCC6244FB34C5354D8B0D6002CB9C328EBC13DA08D1796D0D326E",
    "pc_jp": "636AFE6CB2F24E20CE5B400A79702FE46E4D9EA6A9AF973F176FC9437D089036",
    "switch_ko": "D659A2E49F265AC1624F96F585349FD9F2132EEC571CC842B83C0776AE98526A",
}


def trace_strdata_bottom_return(
    pc_sc_path: Path,
    pc_jp_path: Path,
    switch_path: Path,
    output_root: Path,
) -> dict[str, object]:
    """Prove the common-UI string owner and build a private one-slot PC candidate."""
    inputs = {
        "pc_sc": pc_sc_path,
        "pc_jp": pc_jp_path,
        "switch_ko": switch_path,
    }
    packed: dict[str, bytes] = {}
    raw: dict[str, bytes] = {}
    archives: dict[str, object] = {}
    before: dict[str, str] = {}
    for language, path in inputs.items():
        before[language] = sha256_file(path)
        packed[language] = path.read_bytes()
        _, raw[language] = lz4.decompress_wrapper(packed[language])
        archives[language] = parse_raw_strdata(raw[language])
        if rebuild_raw_strdata(archives[language]) != raw[language]:
            raise TraceError(f"strdata identity rebuild failed: {language}")

    coordinate = BOTTOM_RETURN_COORDINATE
    texts = {
        language: coordinate_texts(archive)[coordinate]
        for language, archive in archives.items()
    }
    hashes = {language: text_hash(text) for language, text in texts.items()}
    if hashes != EXPECTED_BOTTOM_RETURN_HASHES:
        raise TraceError(
            f"bottom-return coordinate hashes differ: {hashes}"
        )

    neighborhoods: dict[str, list[dict[str, object]]] = {}
    for language, archive in archives.items():
        block = archive.blocks[coordinate[0]]
        neighborhoods[language] = [
            {
                "slot_id": slot_id,
                "text": block.texts[slot_id],
                "utf16le_sha256": text_hash(block.texts[slot_id]),
            }
            for slot_id in range(20, 27)
        ]

    sc_archive = archives["pc_sc"]
    replacement_blocks = {
        block.block_id: list(block.texts) for block in sc_archive.blocks
    }
    replacement_blocks[coordinate[0]][coordinate[1]] = texts["switch_ko"]
    candidate_raw = rebuild_raw_strdata(sc_archive, replacement_blocks)
    candidate_packed = lz4.recompress_wrapper(candidate_raw, packed["pc_sc"])
    _, candidate_check_raw = lz4.decompress_wrapper(candidate_packed)
    candidate_archive = parse_raw_strdata(candidate_check_raw)
    if candidate_check_raw != candidate_raw:
        raise TraceError("strdata candidate wrapper round-trip failed")

    original_coordinates = coordinate_texts(sc_archive)
    candidate_coordinates = coordinate_texts(candidate_archive)
    changed = sorted(
        [key for key, value in original_coordinates.items() if candidate_coordinates[key] != value]
    )
    if changed != [coordinate]:
        raise TraceError(f"strdata candidate changed unexpected coordinates: {changed}")
    if text_hash(candidate_coordinates[coordinate]) != EXPECTED_BOTTOM_RETURN_HASHES["switch_ko"]:
        raise TraceError("strdata candidate bottom-return text hash differs")

    candidate_path = output_root / "private" / "candidate" / "MSG" / "SC" / "strdata.bin"
    image_codec.atomic_write(candidate_path, candidate_packed, forbidden=inputs.values())
    after = {language: sha256_file(path) for language, path in inputs.items()}
    if after != before:
        raise TraceError("a strdata input changed during the read-only trace")

    report: dict[str, object] = {
        "schema": "nobu16.kr.bottom-return-common-ui-trace.v1",
        "finding": {
            "owner_relative_path": "MSG/SC/strdata.bin",
            "coordinate": {"block_id": coordinate[0], "slot_id": coordinate[1]},
            "classification": "common_base_ui_string_loaded_by_pk",
            "pc_sc_text": texts["pc_sc"],
            "pc_jp_text": texts["pc_jp"],
            "switch_v13_korean_text": texts["switch_ko"],
            "utf16le_sha256": hashes,
            "why_not_msgui": "installed MSG_PK/SC/msgui slot 22 is already Korean; this independent common strdata coordinate exactly matches the visible bottom return action and its neighboring common UI actions",
            "why_not_res_lang": "320 decoded PC/Switch UI comparison pairs, including /3 title labels and all 105 /4 language rasters, contain no matching bottom-return label",
        },
        "inputs": {
            language: {
                "path": str(path),
                "size": len(packed[language]),
                "sha256": before[language],
                "raw_size": len(raw[language]),
                "raw_sha256": sha256_bytes(raw[language]),
                "identity_raw_rebuild": True,
            }
            for language, path in inputs.items()
        },
        "neighborhoods": neighborhoods,
        "candidate": {
            "path": str(candidate_path),
            "size": len(candidate_packed),
            "sha256": sha256_bytes(candidate_packed),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256_bytes(candidate_raw),
            "changed_coordinates": [[coordinate[0], coordinate[1]]],
            "changed_coordinate_count": 1,
            "all_other_coordinates_preserved": True,
            "wrapper_roundtrip_valid": True,
        },
        "safe_rebuild_plan": [
            "start from the exact PC MSG/SC/strdata.bin baseline",
            "replace only block 1 slot 22 with the Switch-v1.3 Korean text after SC/JP/Switch coordinate validation",
            "rebuild raw strdata outer offsets and alignment",
            "recompress with the original PC wrapper prefix",
            "reparse and prove that only coordinate 1:22 changed",
            "install transactionally only while the game is closed and retain the prior file for restoration",
        ],
        "safety": {
            "live_game_files_read_only": True,
            "candidate_private_tmp_only": True,
            "switch_packed_file_not_copied_to_pc": True,
            "executable_memory_dll_registry_untouched": True,
        },
    }
    report_path = output_root / "strdata_trace.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def g1t_containers(outer: lz4.LinkArchive) -> dict[tuple[int, int], tuple[dict[str, int], tuple[Texture, ...], str]]:
    result: dict[tuple[int, int], tuple[dict[str, int], tuple[Texture, ...], str]] = {}
    for outer_index, outer_entry in enumerate(outer.entries):
        wrapped_entries: Iterable[tuple[int, bytes]]
        if outer_entry.data.startswith(b"LINK"):
            bundle = parse_bundle(outer_entry.data)
            wrapped_entries = ((entry.index, entry.data) for entry in bundle.entries)
        else:
            wrapped_entries = ((0, outer_entry.data),)
        for container_index, wrapper in wrapped_entries:
            try:
                _, raw = lz4.decompress_wrapper(wrapper)
            except lz4.LZ4Error:
                continue
            if not raw.startswith(b"GT1G0600"):
                continue
            header, textures = parse_g1t(raw)
            result[(outer_index, container_index)] = (
                header,
                textures,
                sha256_bytes(raw),
            )
    return result


def texture_record(path: str, texture: Texture, rgba: bytes | None) -> dict[str, object]:
    record: dict[str, object] = {
        "path": path,
        "format": f"0x{texture.format_code:02X}",
        "format_name": {0x59: "BC1/DXT1", 0x5B: "BC3/DXT5"}.get(
            texture.format_code, "unsupported"
        ),
        "dimensions": [texture.width, texture.height],
        "mip_count": texture.mip_count,
        "extra_version": texture.extra_version,
        "base_payload_size": len(texture.base_payload),
        "base_payload_sha256": sha256_bytes(texture.base_payload),
    }
    if rgba is not None:
        record.update(
            {
                "rgba_sha256": sha256_bytes(rgba),
                "alpha_bbox": alpha_bbox(rgba, texture.width, texture.height),
            }
        )
    return record


def build_pair_png(
    pc: tuple[Texture, bytes],
    switch: tuple[Texture, bytes],
    label: str,
    output: Path,
) -> dict[str, object]:
    pc_texture, pc_rgba = pc
    switch_texture, switch_rgba = switch
    box_w, box_h, gap, label_h = 256, 160, 8, 10
    width, height = box_w * 2 + gap, box_h + label_h
    canvas = bytearray(bytes((18, 18, 18, 255)) * (width * height))
    pc_flat = composite_checker(pc_rgba, pc_texture.width, pc_texture.height)
    sw_flat = composite_checker(switch_rgba, switch_texture.width, switch_texture.height)
    pc_fit, pc_w, pc_h = fit_image(pc_flat, pc_texture.width, pc_texture.height, box_w, box_h)
    sw_fit, sw_w, sw_h = fit_image(sw_flat, switch_texture.width, switch_texture.height, box_w, box_h)
    paste(canvas, width, height, pc_fit, pc_w, pc_h, (box_w - pc_w) // 2, label_h + (box_h - pc_h) // 2)
    paste(canvas, width, height, sw_fit, sw_w, sw_h, box_w + gap + (box_w - sw_w) // 2, label_h + (box_h - sw_h) // 2)
    draw_text(canvas, width, height, "P" + label, 2, 2)
    draw_text(canvas, width, height, "S" + label, box_w + gap + 2, 2)
    png_sha = write_png(output, bytes(canvas), width, height)
    return {"path": str(output), "sha256": png_sha, "dimensions": [width, height]}


def analyze(
    pc_path: Path,
    switch_path: Path,
    pc_exp_path: Path | None,
    output_root: Path,
) -> dict[str, object]:
    output_root.mkdir(parents=True, exist_ok=True)
    pc_blob, pc_outer = load_archive(pc_path)
    switch_blob, switch_outer = load_archive(switch_path)
    if len(pc_outer.entries) != len(switch_outer.entries):
        raise TraceError("PC/Switch outer LINK counts differ")
    pc_groups = g1t_containers(pc_outer)
    switch_groups = g1t_containers(switch_outer)
    common_groups = sorted(set(pc_groups) & set(switch_groups))

    records: list[dict[str, object]] = []
    pair_images: list[dict[str, object]] = []
    for outer_index, container_index in common_groups:
        pc_header, pc_textures, pc_raw_hash = pc_groups[(outer_index, container_index)]
        sw_header, sw_textures, sw_raw_hash = switch_groups[(outer_index, container_index)]
        if len(pc_textures) != len(sw_textures):
            raise TraceError(
                f"PC/Switch texture count differs at /{outer_index}/{container_index}"
            )
        group_record: dict[str, object] = {
            "outer_index": outer_index,
            "container_index": container_index,
            "pc_platform": pc_header["platform"],
            "switch_platform": sw_header["platform"],
            "texture_count": len(pc_textures),
            "pc_g1t_sha256": pc_raw_hash,
            "switch_g1t_sha256": sw_raw_hash,
            "textures": [],
        }
        texture_rows: list[dict[str, object]] = []
        for texture_index, (pc_texture, sw_texture) in enumerate(
            zip(pc_textures, sw_textures)
        ):
            path_label = f"{outer_index}/{container_index}/{texture_index}"
            comparable_ui_geometry = (
                (
                    pc_texture.width <= 512
                    and pc_texture.height <= 256
                    and sw_texture.width <= 512
                    and sw_texture.height <= 256
                )
                # /4 is a 105-item 1024x256 language-raster family and must
                # be included in this trace even though it exceeds the generic
                # thumbnail threshold.
                or outer_index == 4
            )
            pc_rgba = (
                decode_texture(pc_texture)
                if pc_texture.format_code in (0x59, 0x5B)
                and comparable_ui_geometry
                else None
            )
            sw_rgba = (
                decode_texture(sw_texture)
                if sw_texture.format_code in (0x59, 0x5B)
                and comparable_ui_geometry
                else None
            )
            row = {
                "texture_index": texture_index,
                "pc": texture_record(path_label, pc_texture, pc_rgba),
                "switch": texture_record(path_label, sw_texture, sw_rgba),
            }
            comparable_ui = (
                pc_rgba is not None
                and sw_rgba is not None
                and comparable_ui_geometry
            )
            if comparable_ui:
                filename = f"o{outer_index:02d}_c{container_index:03d}_t{texture_index:03d}.png"
                pair_meta = build_pair_png(
                    (pc_texture, pc_rgba),
                    (sw_texture, sw_rgba),
                    path_label,
                    output_root / "private" / "pairs" / filename,
                )
                row["pair_preview"] = pair_meta
                pair_images.append(
                    {
                        "resource_path": path_label,
                        "pc_dimensions": [pc_texture.width, pc_texture.height],
                        "switch_dimensions": [sw_texture.width, sw_texture.height],
                        **pair_meta,
                    }
                )
            texture_rows.append(row)
        group_record["textures"] = texture_rows
        records.append(group_record)

    exp_record: dict[str, object] | None = None
    if pc_exp_path is not None:
        exp_blob, exp_outer = load_archive(pc_exp_path)
        exp_groups = g1t_containers(exp_outer)
        exp_record = {
            "path": str(pc_exp_path),
            "size": len(exp_blob),
            "sha256": sha256_bytes(exp_blob),
            "outer_count": len(exp_outer.entries),
            "g1t_container_count": len(exp_groups),
            "texture_count": sum(len(item[1]) for item in exp_groups.values()),
            "groups": [
                {
                    "outer_index": outer_index,
                    "container_index": container_index,
                    "platform": value[0]["platform"],
                    "texture_count": len(value[1]),
                    "textures": [
                        {
                            "index": texture.index,
                            "format": f"0x{texture.format_code:02X}",
                            "dimensions": [texture.width, texture.height],
                            "base_payload_sha256": sha256_bytes(texture.base_payload),
                        }
                        for texture in value[1]
                    ],
                }
                for (outer_index, container_index), value in sorted(exp_groups.items())
            ],
        }

    report: dict[str, object] = {
        "schema": "nobu16.kr.bottom-return-texture-trace.v1",
        "inputs": {
            "pc": {
                "path": str(pc_path),
                "size": len(pc_blob),
                "sha256": sha256_bytes(pc_blob),
                "outer_count": len(pc_outer.entries),
            },
            "switch": {
                "path": str(switch_path),
                "size": len(switch_blob),
                "sha256": sha256_bytes(switch_blob),
                "outer_count": len(switch_outer.entries),
            },
            "pc_exp": exp_record,
        },
        "scope": {
            "common_g1t_container_count": len(common_groups),
            "pc_g1t_container_count": len(pc_groups),
            "switch_g1t_container_count": len(switch_groups),
            "pair_preview_count": len(pair_images),
        },
        "pair_previews": pair_images,
        "groups": records,
        "safety": {
            "live_game_files_read_only": True,
            "outputs_private_tmp_only": True,
            "game_process_modified": False,
            "memory_or_executable_modified": False,
        },
    }
    report_path = output_root / "inventory.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pc", required=True)
    parser.add_argument("--switch", required=True)
    parser.add_argument("--pc-exp")
    parser.add_argument("--pc-strdata-sc")
    parser.add_argument("--pc-strdata-jp")
    parser.add_argument("--switch-strdata")
    parser.add_argument(
        "--output-root",
        default=str(TMP_ROOT / "bottom_return_trace"),
    )
    parser.add_argument(
        "--sheets-only",
        action="store_true",
        help="tile already-generated private pair PNGs without reading archives",
    )
    parser.add_argument(
        "--strdata-only",
        action="store_true",
        help="trace and privately rebuild the common bottom-return string only",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_root = private_output_root(args.output_root)
    if args.sheets_only:
        sheets = build_existing_contact_sheets(output_root)
        print(f"contact_sheet_manifest={output_root / 'contact_sheets.json'}")
        print(f"contact_sheets={len(sheets)}")
        return 0
    if args.strdata_only:
        required = {
            "--pc-strdata-sc": args.pc_strdata_sc,
            "--pc-strdata-jp": args.pc_strdata_jp,
            "--switch-strdata": args.switch_strdata,
        }
        missing = [option for option, value in required.items() if not value]
        if missing:
            raise TraceError(f"strdata-only requires: {', '.join(missing)}")
        report = trace_strdata_bottom_return(
            Path(args.pc_strdata_sc).resolve(),
            Path(args.pc_strdata_jp).resolve(),
            Path(args.switch_strdata).resolve(),
            output_root,
        )
        print(f"strdata_trace={output_root / 'strdata_trace.json'}")
        print(f"owner={report['finding']['owner_relative_path']}")
        print("coordinate=1:22")
        print(f"candidate={report['candidate']['path']}")
        return 0
    report = analyze(
        Path(args.pc).resolve(),
        Path(args.switch).resolve(),
        Path(args.pc_exp).resolve() if args.pc_exp else None,
        output_root,
    )
    print(f"inventory={output_root / 'inventory.json'}")
    print(f"common_g1t_containers={report['scope']['common_g1t_container_count']}")
    print(f"pair_previews={report['scope']['pair_preview_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
