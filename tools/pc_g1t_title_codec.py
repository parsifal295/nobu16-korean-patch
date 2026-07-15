#!/usr/bin/env python3
"""Private-only codec/rebuilder for the PC PK title-label G1T resources.

The supported path is deliberately narrow and fail-closed::

    RES_SC/res_lang.bin (outer LINK)
      /3                 (32-byte-header LINK variant)
        /0..109          (raw-LZ4 wrapped, one-texture GT1G0600)

The title textures used by NOBU16 PC encode format byte ``0x5B`` as linear
BC3/DXT5.  A decoded image can be written as a deterministic, dependency-free
RGBA PNG.  During rebuild, an unchanged 4x4 block keeps the exact original
16-byte BC3 block.  Only changed blocks go through the deterministic encoder.

All CLI output is restricted to this repository's ignored ``tmp`` directory.
The input archive is opened read-only, SHA-checked before and after the job,
and is never replaced.  This module does not access the game process, registry,
executables, DLLs, or memory.
"""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import os
import struct
import sys
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TMP_ROOT = PROJECT_ROOT / "tmp"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import nobu16_lz4 as LZ4  # noqa: E402


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
G1T_MAGIC_VERSION = b"GT1G0600"
PC_FORMAT_BC3_ALIAS = 0x5B
EXPECTED_WIDTH = 512
EXPECTED_HEIGHT = 128
OUTER_TITLE_INDEX = 3
INNER_LINK_HEADER_SIZE = 0x20
INNER_LINK_ALIGNMENT = 0x20


class CodecError(ValueError):
    """Raised when an input is outside the exact supported format."""


@dataclass(frozen=True)
class InnerLinkEntry:
    index: int
    offset: int
    stored_size: int
    data: bytes
    gap_after: bytes


@dataclass(frozen=True)
class InnerLink32:
    fixed_header: bytes
    table_offset: int
    pre_data: bytes
    entries: tuple[InnerLinkEntry, ...]
    original_size: int
    alignment: int


@dataclass(frozen=True)
class G1TTexture:
    raw: bytes
    directory_offset: int
    texture_offset: int
    payload_offset: int
    payload_end: int
    packed_info: int
    format_code: int
    packed_dimensions: int
    mip_count: int
    width: int
    height: int
    bc3: bytes


@dataclass(frozen=True)
class TextureChain:
    outer_blob: bytes
    outer: LZ4.LinkArchive
    inner_blob: bytes
    inner: InnerLink32
    inner_index: int
    wrapper_blob: bytes
    wrapper_header: LZ4.WrapperHeader
    g1t: G1TTexture


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def align_up(value: int, alignment: int) -> int:
    if alignment <= 0 or alignment & (alignment - 1):
        raise CodecError("alignment must be a positive power of two")
    return (value + alignment - 1) & -alignment


def parse_inner_link32(blob: bytes) -> InnerLink32:
    """Parse the exact 32-byte-header LINK variant used by outer entry /3."""
    if len(blob) < INNER_LINK_HEADER_SIZE or blob[:4] != b"LINK":
        raise CodecError("outer entry /3 is not a LINK archive")
    count, table_offset, duplicate_count, aligned_table_end = struct.unpack_from(
        "<4I", blob, 4
    )
    if table_offset != INNER_LINK_HEADER_SIZE:
        raise CodecError(
            f"unsupported inner LINK table offset 0x{table_offset:X}; expected 0x20"
        )
    if count == 0 or duplicate_count != count:
        raise CodecError("inner LINK count fields disagree or are empty")
    table_end = table_offset + count * 8
    if table_end > len(blob):
        raise CodecError("inner LINK table exceeds file size")
    if aligned_table_end != align_up(table_end, INNER_LINK_ALIGNMENT):
        raise CodecError("inner LINK aligned table-end field is inconsistent")
    # Remaining header words are observed zero in the exact PC PK variant.
    if blob[20:32] != b"\0" * 12:
        raise CodecError("unsupported non-zero inner LINK extension header")

    pairs = [struct.unpack_from("<II", blob, table_offset + i * 8) for i in range(count)]
    first_offset = pairs[0][0]
    if first_offset < aligned_table_end or first_offset > len(blob):
        raise CodecError("inner LINK first entry offset is invalid")
    entries: list[InnerLinkEntry] = []
    for index, (offset, stored_size) in enumerate(pairs):
        if offset % INNER_LINK_ALIGNMENT:
            raise CodecError(f"inner LINK entry {index} is not 0x20-aligned")
        end = offset + stored_size
        next_offset = pairs[index + 1][0] if index + 1 < count else len(blob)
        if end > next_offset or next_offset > len(blob):
            raise CodecError(f"inner LINK entry {index} overlaps or exceeds the archive")
        gap = blob[end:next_offset]
        if index + 1 < count and any(gap):
            raise CodecError(f"inner LINK entry {index} has non-zero alignment padding")
        entries.append(InnerLinkEntry(index, offset, stored_size, blob[offset:end], gap))

    archive = InnerLink32(
        fixed_header=blob[:table_offset],
        table_offset=table_offset,
        pre_data=blob[table_end:first_offset],
        entries=tuple(entries),
        original_size=len(blob),
        alignment=INNER_LINK_ALIGNMENT,
    )
    if rebuild_inner_link32(archive) != blob:
        raise CodecError("inner LINK parse/rebuild identity gate failed")
    return archive


def rebuild_inner_link32(
    archive: InnerLink32, replacements: dict[int, bytes] | None = None
) -> bytes:
    replacements = replacements or {}
    unknown = sorted(set(replacements) - {entry.index for entry in archive.entries})
    if unknown:
        raise CodecError(f"inner LINK replacement indices are invalid: {unknown}")

    count = len(archive.entries)
    table_end = archive.table_offset + count * 8
    output = bytearray(archive.fixed_header)
    output.extend(b"\0" * (count * 8))
    output.extend(archive.pre_data)
    if len(output) != archive.entries[0].offset:
        raise CodecError("inner LINK pre-data region no longer reaches the first entry")

    pairs: list[tuple[int, int]] = []
    for position, entry in enumerate(archive.entries):
        data = replacements.get(entry.index, entry.data)
        if len(output) % archive.alignment:
            raise CodecError("internal inner LINK alignment error")
        offset = len(output)
        pairs.append((offset, len(data)))
        output.extend(data)
        if position + 1 < count:
            # Preserve an identity rebuild byte-for-byte.  Once a size changes,
            # restore the format invariant by computing fresh zero alignment.
            if offset == entry.offset and data == entry.data:
                output.extend(entry.gap_after)
            else:
                output.extend(b"\0" * (align_up(len(output), archive.alignment) - len(output)))

    for index, (offset, stored_size) in enumerate(pairs):
        if offset > 0xFFFFFFFF or stored_size > 0xFFFFFFFF:
            raise CodecError("inner LINK exceeds its 32-bit table fields")
        struct.pack_into("<II", output, archive.table_offset + index * 8, offset, stored_size)
    return bytes(output)


def parse_pc_title_g1t(raw: bytes) -> G1TTexture:
    """Parse one exact PC GT1G0600 single-texture 512x128 0x5B resource."""
    if len(raw) < 56 or raw[:8] != G1T_MAGIC_VERSION:
        raise CodecError("resource is not GT1G0600")
    file_size, directory_offset, texture_count, platform = struct.unpack_from("<4I", raw, 8)
    if file_size != len(raw):
        raise CodecError(f"G1T file-size field {file_size} != actual {len(raw)}")
    if directory_offset != 0x20 or texture_count != 1 or platform != 0x0A:
        raise CodecError(
            "unsupported G1T layout; expected directory=0x20, one texture, platform=0x0A"
        )
    if raw[24:32] != b"\0" * 8:
        raise CodecError("unsupported G1T header extension")
    relative_offset = struct.unpack_from("<I", raw, directory_offset)[0]
    texture_offset = directory_offset + relative_offset
    if texture_offset != 0x24:
        raise CodecError(f"unexpected G1T texture offset 0x{texture_offset:X}")

    packed_info, format_code, packed_dimensions = struct.unpack_from("<BBB", raw, texture_offset)
    mip_count = packed_info >> 4
    width = 1 << (packed_dimensions & 0x0F)
    height = 1 << (packed_dimensions >> 4)
    if format_code != PC_FORMAT_BC3_ALIAS:
        raise CodecError(f"unsupported PC G1T format 0x{format_code:02X}; expected 0x5B")
    if (width, height, mip_count) != (EXPECTED_WIDTH, EXPECTED_HEIGHT, 1):
        raise CodecError(
            f"unsupported texture geometry {width}x{height}, mip_count={mip_count}"
        )
    extra_version = raw[texture_offset + 7]
    extra_length = struct.unpack_from("<I", raw, texture_offset + 8)[0]
    if extra_version != 0x10 or extra_length != 12:
        raise CodecError(
            f"unsupported G1T extra header version=0x{extra_version:02X}, length={extra_length}"
        )
    payload_offset = texture_offset + 8 + extra_length
    expected_bc3_size = ((width + 3) // 4) * ((height + 3) // 4) * 16
    payload_end = payload_offset + expected_bc3_size
    if payload_end != len(raw):
        raise CodecError(
            f"G1T BC3 payload ends at {payload_end}, but file size is {len(raw)}"
        )
    return G1TTexture(
        raw=raw,
        directory_offset=directory_offset,
        texture_offset=texture_offset,
        payload_offset=payload_offset,
        payload_end=payload_end,
        packed_info=packed_info,
        format_code=format_code,
        packed_dimensions=packed_dimensions,
        mip_count=mip_count,
        width=width,
        height=height,
        bc3=raw[payload_offset:payload_end],
    )


def replace_g1t_bc3(texture: G1TTexture, bc3: bytes) -> bytes:
    if len(bc3) != len(texture.bc3):
        raise CodecError("replacement BC3 payload size differs from the exact one-mip layout")
    rebuilt = texture.raw[: texture.payload_offset] + bc3 + texture.raw[texture.payload_end :]
    reparsed = parse_pc_title_g1t(rebuilt)
    if reparsed.bc3 != bc3:
        raise CodecError("rebuilt G1T payload failed re-extraction")
    return rebuilt


def expand_565(value: int) -> tuple[int, int, int]:
    red = (value >> 11) & 0x1F
    green = (value >> 5) & 0x3F
    blue = value & 0x1F
    return ((red << 3) | (red >> 2), (green << 2) | (green >> 4), (blue << 3) | (blue >> 2))


def quantize_565(red: int, green: int, blue: int) -> int:
    r5 = (red * 31 + 127) // 255
    g6 = (green * 63 + 127) // 255
    b5 = (blue * 31 + 127) // 255
    return (r5 << 11) | (g6 << 5) | b5


def bc3_alpha_palette(alpha0: int, alpha1: int) -> tuple[int, ...]:
    if alpha0 > alpha1:
        values = [alpha0, alpha1]
        values.extend(
            ((7 - step) * alpha0 + step * alpha1 + 3) // 7 for step in range(1, 7)
        )
        return tuple(values)
    values = [alpha0, alpha1]
    values.extend(((5 - step) * alpha0 + step * alpha1 + 2) // 5 for step in range(1, 5))
    values.extend((0, 255))
    return tuple(values)


def bc3_color_palette(color0: int, color1: int) -> tuple[tuple[int, int, int], ...]:
    first = expand_565(color0)
    second = expand_565(color1)
    # A BC3 color block always uses four opaque colors, irrespective of endpoint order.
    third = tuple((2 * first[channel] + second[channel] + 1) // 3 for channel in range(3))
    fourth = tuple((first[channel] + 2 * second[channel] + 1) // 3 for channel in range(3))
    return first, second, third, fourth


def decode_bc3_block(block: bytes) -> bytes:
    if len(block) != 16:
        raise CodecError("BC3 block must contain exactly 16 bytes")
    alpha0, alpha1 = block[0], block[1]
    alpha_indices = int.from_bytes(block[2:8], "little")
    color0, color1, color_indices = struct.unpack_from("<HHI", block, 8)
    alphas = bc3_alpha_palette(alpha0, alpha1)
    colors = bc3_color_palette(color0, color1)
    result = bytearray(64)
    for pixel in range(16):
        red, green, blue = colors[(color_indices >> (pixel * 2)) & 3]
        alpha = alphas[(alpha_indices >> (pixel * 3)) & 7]
        result[pixel * 4 : pixel * 4 + 4] = bytes((red, green, blue, alpha))
    return bytes(result)


def decode_bc3(data: bytes, width: int, height: int) -> bytes:
    blocks_wide = (width + 3) // 4
    blocks_high = (height + 3) // 4
    expected = blocks_wide * blocks_high * 16
    if len(data) != expected:
        raise CodecError(f"BC3 size {len(data)} != expected {expected}")
    rgba = bytearray(width * height * 4)
    offset = 0
    for block_y in range(blocks_high):
        for block_x in range(blocks_wide):
            pixels = decode_bc3_block(data[offset : offset + 16])
            offset += 16
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
                    rgba[target : target + 4] = pixels[source : source + 4]
    return bytes(rgba)


def extract_rgba_block(rgba: bytes, width: int, height: int, block_x: int, block_y: int) -> bytes:
    block = bytearray(64)
    for local_y in range(4):
        y = min(block_y * 4 + local_y, height - 1)
        for local_x in range(4):
            x = min(block_x * 4 + local_x, width - 1)
            source = (y * width + x) * 4
            target = (local_y * 4 + local_x) * 4
            block[target : target + 4] = rgba[source : source + 4]
    return bytes(block)


def encode_bc3_alpha(block_rgba: bytes) -> bytes:
    source_alphas = [block_rgba[pixel * 4 + 3] for pixel in range(16)]
    alpha0 = max(source_alphas)
    alpha1 = min(source_alphas)
    if alpha0 == alpha1:
        return bytes((alpha0, alpha1)) + b"\0" * 6
    palette = bc3_alpha_palette(alpha0, alpha1)
    bits = 0
    for pixel, alpha in enumerate(source_alphas):
        index = min(range(8), key=lambda candidate: (abs(alpha - palette[candidate]), candidate))
        bits |= index << (pixel * 3)
    return bytes((alpha0, alpha1)) + bits.to_bytes(6, "little")


def encode_bc3_color(block_rgba: bytes) -> bytes:
    pixels = [tuple(block_rgba[pixel * 4 : pixel * 4 + 4]) for pixel in range(16)]
    candidates = sorted({quantize_565(red, green, blue) for red, green, blue, _ in pixels})
    if not candidates:
        candidates = [0]
    # Endpoint pairs drawn from the block are deterministic and adequate for
    # these small pre-rendered labels.  Alpha-weighted error ignores hidden RGB.
    pairs: list[tuple[int, int]] = []
    for first in candidates:
        for second in candidates:
            if first > second:
                pairs.append((first, second))
    if not pairs:
        pairs.append((candidates[0], candidates[0]))

    best: tuple[int, int, int, int] | None = None
    for color0, color1 in pairs:
        palette = bc3_color_palette(color0, color1)
        bits = 0
        error = 0
        for pixel_index, (red, green, blue, alpha) in enumerate(pixels):
            weight = alpha + 1
            choices = []
            for palette_index, (pr, pg, pb) in enumerate(palette):
                distance = (
                    (red - pr) * (red - pr)
                    + (green - pg) * (green - pg)
                    + (blue - pb) * (blue - pb)
                ) * weight
                choices.append((distance, palette_index))
            distance, palette_index = min(choices)
            error += distance
            bits |= palette_index << (pixel_index * 2)
        candidate = (error, color0, color1, bits)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    _, color0, color1, bits = best
    return struct.pack("<HHI", color0, color1, bits)


def encode_bc3_block(block_rgba: bytes) -> bytes:
    if len(block_rgba) != 64:
        raise CodecError("RGBA block must contain exactly 64 bytes")
    return encode_bc3_alpha(block_rgba) + encode_bc3_color(block_rgba)


def encode_bc3(
    rgba: bytes,
    width: int,
    height: int,
    *,
    template_bc3: bytes | None = None,
) -> tuple[bytes, int, int]:
    if len(rgba) != width * height * 4:
        raise CodecError("RGBA byte length does not match image dimensions")
    blocks_wide = (width + 3) // 4
    blocks_high = (height + 3) // 4
    expected = blocks_wide * blocks_high * 16
    if template_bc3 is not None and len(template_bc3) != expected:
        raise CodecError("template BC3 length does not match image dimensions")

    output = bytearray()
    preserved = 0
    encoded = 0
    block_index = 0
    for block_y in range(blocks_high):
        for block_x in range(blocks_wide):
            rgba_block = extract_rgba_block(rgba, width, height, block_x, block_y)
            template_block = (
                template_bc3[block_index * 16 : block_index * 16 + 16]
                if template_bc3 is not None
                else None
            )
            if template_block is not None and decode_bc3_block(template_block) == rgba_block:
                output.extend(template_block)
                preserved += 1
            else:
                output.extend(encode_bc3_block(rgba_block))
                encoded += 1
            block_index += 1
    return bytes(output), preserved, encoded


def rgba_error_metrics(expected: bytes, actual: bytes) -> dict[str, int | float]:
    if len(expected) != len(actual) or len(expected) % 4:
        raise CodecError("RGBA comparison buffers have incompatible lengths")
    differing_pixels = 0
    squared_error = 0
    maximum = 0
    for pixel in range(len(expected) // 4):
        start = pixel * 4
        left = expected[start : start + 4]
        right = actual[start : start + 4]
        if left != right:
            differing_pixels += 1
        for first, second in zip(left, right):
            difference = abs(first - second)
            maximum = max(maximum, difference)
            squared_error += difference * difference
    return {
        "differing_pixels": differing_pixels,
        "max_channel_error": maximum,
        "mean_squared_channel_error": round(squared_error / len(expected), 6),
    }


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def encode_rgba_png(rgba: bytes, width: int, height: int) -> bytes:
    if len(rgba) != width * height * 4:
        raise CodecError("RGBA byte length does not match PNG dimensions")
    scanlines = bytearray()
    stride = width * 4
    for y in range(height):
        scanlines.append(0)
        scanlines.extend(rgba[y * stride : (y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(bytes(scanlines), level=9))
        + png_chunk(b"IEND", b"")
    )


def paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    dl = abs(estimate - left)
    da = abs(estimate - above)
    du = abs(estimate - upper_left)
    if dl <= da and dl <= du:
        return left
    return above if da <= du else upper_left


def decode_png(blob: bytes) -> tuple[bytes, int, int]:
    if not blob.startswith(PNG_SIGNATURE):
        raise CodecError("input image is not a PNG")
    position = len(PNG_SIGNATURE)
    ihdr: bytes | None = None
    idat = bytearray()
    saw_end = False
    while position < len(blob):
        if position + 12 > len(blob):
            raise CodecError("truncated PNG chunk")
        length = struct.unpack_from(">I", blob, position)[0]
        kind = blob[position + 4 : position + 8]
        payload_start = position + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if crc_end > len(blob):
            raise CodecError("PNG chunk exceeds file size")
        payload = blob[payload_start:payload_end]
        expected_crc = struct.unpack_from(">I", blob, payload_end)[0]
        actual_crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise CodecError(f"PNG {kind!r} CRC mismatch")
        if kind == b"IHDR":
            if ihdr is not None:
                raise CodecError("PNG has multiple IHDR chunks")
            ihdr = payload
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"IEND":
            saw_end = True
            position = crc_end
            break
        position = crc_end
    if ihdr is None or not saw_end or len(ihdr) != 13:
        raise CodecError("PNG is missing a valid IHDR/IEND")
    width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", ihdr
    )
    if bit_depth != 8 or compression != 0 or filtering != 0 or interlace != 0:
        raise CodecError("only non-interlaced 8-bit PNG is supported")
    channels_by_type = {0: 1, 2: 3, 4: 2, 6: 4}
    if color_type not in channels_by_type:
        raise CodecError(f"unsupported PNG color type {color_type}")
    channels = channels_by_type[color_type]
    stride = width * channels
    try:
        filtered = zlib.decompress(bytes(idat))
    except zlib.error as exc:
        raise CodecError(f"invalid PNG IDAT stream: {exc}") from exc
    if len(filtered) != height * (stride + 1):
        raise CodecError("PNG decompressed scanline size is inconsistent")

    rows: list[bytearray] = []
    source = 0
    for _ in range(height):
        filter_type = filtered[source]
        source += 1
        encoded = filtered[source : source + stride]
        source += stride
        previous = rows[-1] if rows else bytearray(stride)
        row = bytearray(stride)
        for index, value in enumerate(encoded):
            left = row[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                decoded = value
            elif filter_type == 1:
                decoded = value + left
            elif filter_type == 2:
                decoded = value + above
            elif filter_type == 3:
                decoded = value + ((left + above) // 2)
            elif filter_type == 4:
                decoded = value + paeth(left, above, upper_left)
            else:
                raise CodecError(f"unsupported PNG filter {filter_type}")
            row[index] = decoded & 0xFF
        rows.append(row)

    rgba = bytearray(width * height * 4)
    target = 0
    for row in rows:
        for x in range(width):
            source_pixel = x * channels
            if color_type == 0:
                gray = row[source_pixel]
                pixel = (gray, gray, gray, 255)
            elif color_type == 2:
                pixel = (*row[source_pixel : source_pixel + 3], 255)
            elif color_type == 4:
                gray, alpha = row[source_pixel : source_pixel + 2]
                pixel = (gray, gray, gray, alpha)
            else:
                pixel = tuple(row[source_pixel : source_pixel + 4])
            rgba[target : target + 4] = bytes(pixel)
            target += 4
    return bytes(rgba), width, height


def load_texture_chain(archive_path: Path, inner_index: int) -> TextureChain:
    outer_blob = archive_path.read_bytes()
    outer = LZ4.parse_link(outer_blob)
    if LZ4.rebuild_link(outer) != outer_blob:
        raise CodecError("outer LINK parse/rebuild identity gate failed")
    if OUTER_TITLE_INDEX >= len(outer.entries):
        raise CodecError("outer LINK has no title-label component /3")
    inner_blob = outer.entries[OUTER_TITLE_INDEX].data
    inner = parse_inner_link32(inner_blob)
    if inner_index < 0 or inner_index >= len(inner.entries):
        raise CodecError(f"inner texture index {inner_index} is out of range")
    wrapper_blob = inner.entries[inner_index].data
    wrapper_header, raw = LZ4.decompress_wrapper(wrapper_blob)
    g1t = parse_pc_title_g1t(raw)
    return TextureChain(
        outer_blob=outer_blob,
        outer=outer,
        inner_blob=inner_blob,
        inner=inner,
        inner_index=inner_index,
        wrapper_blob=wrapper_blob,
        wrapper_header=wrapper_header,
        g1t=g1t,
    )


def rebuild_texture_chain(chain: TextureChain, rgba: bytes) -> tuple[bytes, dict[str, object]]:
    bc3, preserved_blocks, encoded_blocks = encode_bc3(
        rgba,
        chain.g1t.width,
        chain.g1t.height,
        template_bc3=chain.g1t.bc3,
    )
    rebuilt_g1t = replace_g1t_bc3(chain.g1t, bc3)
    if rebuilt_g1t == chain.g1t.raw:
        rebuilt_wrapper = chain.wrapper_blob
    else:
        rebuilt_wrapper = LZ4.recompress_wrapper(rebuilt_g1t, chain.wrapper_header)
        _, roundtrip_g1t = LZ4.decompress_wrapper(rebuilt_wrapper)
        if roundtrip_g1t != rebuilt_g1t:
            raise CodecError("rebuilt LZ4 wrapper failed round-trip")

    selected_index = chain.inner_index
    rebuilt_inner = rebuild_inner_link32(chain.inner, {selected_index: rebuilt_wrapper})
    parsed_inner = parse_inner_link32(rebuilt_inner)
    if parsed_inner.entries[selected_index].data != rebuilt_wrapper:
        raise CodecError("rebuilt inner LINK failed replacement re-extraction")

    rebuilt_outer = LZ4.rebuild_link(chain.outer, {OUTER_TITLE_INDEX: rebuilt_inner})
    parsed_outer = LZ4.parse_link(rebuilt_outer)
    if parsed_outer.entries[OUTER_TITLE_INDEX].data != rebuilt_inner:
        raise CodecError("rebuilt outer LINK failed replacement re-extraction")
    for index, original in enumerate(chain.outer.entries):
        if index != OUTER_TITLE_INDEX and parsed_outer.entries[index].data != original.data:
            raise CodecError(f"unrelated outer LINK entry {index} changed")

    report = {
        "selected_inner_index": selected_index,
        "total_blocks": len(chain.g1t.bc3) // 16,
        "preserved_template_blocks": preserved_blocks,
        "deterministically_encoded_blocks": encoded_blocks,
        "bc3_exact": bc3 == chain.g1t.bc3,
        "g1t_exact": rebuilt_g1t == chain.g1t.raw,
        "wrapper_exact": rebuilt_wrapper == chain.wrapper_blob,
        "inner_link_exact": rebuilt_inner == chain.inner_blob,
        "outer_archive_exact": rebuilt_outer == chain.outer_blob,
        "bc3_sha256": sha256_bytes(bc3),
        "g1t_sha256": sha256_bytes(rebuilt_g1t),
        "wrapper_sha256": sha256_bytes(rebuilt_wrapper),
        "inner_link_sha256": sha256_bytes(rebuilt_inner),
        "outer_archive_sha256": sha256_bytes(rebuilt_outer),
    }
    return rebuilt_outer, report


def private_output_root(requested: str | None, command: str, index: int) -> Path:
    base = Path(requested).resolve() if requested else (TMP_ROOT / "pc_g1t_title_codec").resolve()
    tmp = TMP_ROOT.resolve()
    try:
        base.relative_to(tmp)
    except ValueError as exc:
        raise CodecError(f"output root must remain below {tmp}") from exc
    return base / "private" / command / f"3_{index:03d}"


def atomic_write(path: Path, data: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    resolved = path.resolve()
    for item in forbidden:
        if resolved == item.resolve():
            raise CodecError(f"refusing to overwrite input file: {item}")
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


def write_json(path: Path, value: object, *, forbidden: Iterable[Path] = ()) -> None:
    atomic_write(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        forbidden=forbidden,
    )


def source_metadata(
    archive_path: Path, archive_hash: str, chain: TextureChain, rgba: bytes, index: int
) -> dict[str, object]:
    return {
        "schema": "nobu16.pc-pk-title-g1t.private-probe.v1",
        "file_only": True,
        "game_install_modified": False,
        "source": {
            "path": str(archive_path),
            "size": len(chain.outer_blob),
            "sha256": archive_hash,
            "unchanged": True,
        },
        "chain": {
            "outer_component": OUTER_TITLE_INDEX,
            "inner_index": index,
            "inner_link_count": len(chain.inner.entries),
            "inner_link_header_size": len(chain.inner.fixed_header),
            "inner_link_sha256": sha256_bytes(chain.inner_blob),
            "wrapper_size": len(chain.wrapper_blob),
            "wrapper_sha256": sha256_bytes(chain.wrapper_blob),
            "g1t_size": len(chain.g1t.raw),
            "g1t_sha256": sha256_bytes(chain.g1t.raw),
            "g1t_version": "0600",
            "format_code": "0x5B",
            "decoded_as": "BC3/DXT5 (NOBU16 PC platform alias)",
            "width": chain.g1t.width,
            "height": chain.g1t.height,
            "mip_count": chain.g1t.mip_count,
            "payload_offset": chain.g1t.payload_offset,
            "bc3_size": len(chain.g1t.bc3),
            "bc3_sha256": sha256_bytes(chain.g1t.bc3),
            "rgba_size": len(rgba),
            "rgba_sha256": sha256_bytes(rgba),
        },
        "runtime_patch_features": [],
    }


def cmd_extract(args: argparse.Namespace) -> int:
    archive_path = Path(args.archive).resolve()
    before = sha256_file(archive_path)
    chain = load_texture_chain(archive_path, args.index)
    rgba = decode_bc3(chain.g1t.bc3, chain.g1t.width, chain.g1t.height)
    png = encode_rgba_png(rgba, chain.g1t.width, chain.g1t.height)
    output_root = private_output_root(args.output_root, "extract", args.index)
    png_path = output_root / "title.png"
    rgba_path = output_root / "title.rgba"
    metadata_path = output_root / "metadata.json"
    atomic_write(png_path, png, forbidden=(archive_path,))
    atomic_write(rgba_path, rgba, forbidden=(archive_path,))
    metadata = source_metadata(archive_path, before, chain, rgba, args.index)
    metadata["private_outputs"] = {
        "png": {"path": str(png_path), "size": len(png), "sha256": sha256_bytes(png)},
        "rgba": {"path": str(rgba_path), "size": len(rgba), "sha256": sha256_bytes(rgba)},
    }
    after = sha256_file(archive_path)
    if after != before:
        raise CodecError("input archive changed while extracting")
    write_json(metadata_path, metadata, forbidden=(archive_path,))
    print(f"png={png_path}")
    print(f"png_sha256={sha256_bytes(png)}")
    print(f"rgba_sha256={sha256_bytes(rgba)}")
    print(f"g1t_sha256={sha256_bytes(chain.g1t.raw)}")
    print(f"wrapper_sha256={sha256_bytes(chain.wrapper_blob)}")
    print("input_unchanged=OK")
    print("game_install_modified=False")
    return 0


def cmd_rebuild(args: argparse.Namespace) -> int:
    archive_path = Path(args.archive).resolve()
    image_path = Path(args.png).resolve()
    before = sha256_file(archive_path)
    image_before = sha256_file(image_path)
    chain = load_texture_chain(archive_path, args.index)
    rgba, width, height = decode_png(image_path.read_bytes())
    if (width, height) != (chain.g1t.width, chain.g1t.height):
        raise CodecError(
            f"replacement PNG is {width}x{height}; expected {chain.g1t.width}x{chain.g1t.height}"
        )
    rebuilt, rebuild_report = rebuild_texture_chain(chain, rgba)
    output_root = private_output_root(args.output_root, "rebuild", args.index)
    candidate_path = output_root / "candidate" / "RES_SC" / "res_lang.bin"
    report_path = output_root / "rebuild_report.json"
    atomic_write(candidate_path, rebuilt, forbidden=(archive_path, image_path))
    reparsed = load_texture_chain(candidate_path, args.index)
    rebuilt_rgba = decode_bc3(reparsed.g1t.bc3, width, height)
    preview = encode_rgba_png(rebuilt_rgba, width, height)
    preview_path = output_root / "candidate_preview.png"
    atomic_write(preview_path, preview, forbidden=(archive_path, image_path))
    if rebuilt_rgba != rgba and rebuild_report["deterministically_encoded_blocks"] == 0:
        raise CodecError("unchanged image rebuild did not preserve decoded pixels")
    after = sha256_file(archive_path)
    image_after = sha256_file(image_path)
    if after != before or image_after != image_before:
        raise CodecError("an input changed during rebuild")
    report = source_metadata(archive_path, before, chain, rgba, args.index)
    report.update(
        {
            "schema": "nobu16.pc-pk-title-g1t.private-rebuild.v1",
            "replacement_png": {
                "path": str(image_path),
                "sha256_before": image_before,
                "sha256_after": image_after,
                "unchanged": True,
            },
            "rebuild": rebuild_report,
            "candidate": {
                "path": str(candidate_path),
                "size": len(rebuilt),
                "sha256": sha256_bytes(rebuilt),
                "outer_parse_rebuild_valid": True,
                "inner_parse_rebuild_valid": True,
                "g1t_reextract_valid": True,
            },
            "candidate_preview": {
                "path": str(preview_path),
                "size": len(preview),
                "sha256": sha256_bytes(preview),
                "rgba_sha256": sha256_bytes(rebuilt_rgba),
                "error_against_requested_rgba": rgba_error_metrics(rgba, rebuilt_rgba),
            },
        }
    )
    write_json(report_path, report, forbidden=(archive_path, image_path))
    print(f"candidate={candidate_path}")
    print(f"candidate_sha256={sha256_bytes(rebuilt)}")
    print(f"preserved_blocks={rebuild_report['preserved_template_blocks']}")
    print(f"encoded_blocks={rebuild_report['deterministically_encoded_blocks']}")
    print(f"outer_archive_exact={rebuild_report['outer_archive_exact']}")
    print("input_unchanged=OK")
    print("game_install_modified=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    extract = subparsers.add_parser("extract", help="Decode one PC /3/N title texture privately")
    extract.add_argument("--archive", required=True)
    extract.add_argument("--index", type=int, default=0)
    extract.add_argument("--output-root")
    extract.set_defaults(func=cmd_extract)
    rebuild = subparsers.add_parser(
        "rebuild", help="Encode a PNG and rebuild wrapper, /3 LINK, and outer archive privately"
    )
    rebuild.add_argument("--archive", required=True)
    rebuild.add_argument("--png", required=True)
    rebuild.add_argument("--index", type=int, default=0)
    rebuild.add_argument("--output-root")
    rebuild.set_defaults(func=cmd_rebuild)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, CodecError, LZ4.LZ4Error, LZ4.LinkError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
