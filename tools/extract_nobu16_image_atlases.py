#!/usr/bin/env python3
"""Read-only PNG extraction for the NOBU16 PC image-atlas formats.

Supported inputs intentionally cover only formats that have been structurally
verified in this workspace:

* a top-level ``LINK`` language resource (``res_lang.bin`` or
  ``res_lang_pk.bin``), containing nested LINK + raw-LZ4 wrapped ``GT1G0600``
  images; and
* a direct, concatenated ``GT1G0600`` bank such as
  ``STAGE/texture/main_nm_hi_data.bin``.

The extractor is deliberately read-only.  It hashes every source before and
after processing, performs canonical LINK checks, and writes PNGs, previews,
contact sheets, and JSON only below ``KR_PATCH_WORK/tmp``.  Unknown containers
such as the DLC ``.n16`` files are fingerprinted, never guessed or rewritten.

The decoded formats are the PC variants observed in this game:

* ``0x59``: BC1 / DXT1
* ``0x5B``: BC3 / DXT5
* ``0x01``: linear, row-major RGBA8 (the verified boot-warning variant)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
TMP_ROOT = REPO_ROOT / "tmp"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as png_codec  # noqa: E402

try:  # Pillow is available in the bundled workspace Python runtime.
    from PIL import Image
except ImportError:  # Keep a dependency-free fallback for forensic use elsewhere.
    Image = None  # type: ignore[assignment,misc]

try:  # The bundled workspace Python also includes NumPy for bulk BC decode.
    import numpy as np
except ImportError:
    np = None  # type: ignore[assignment]


G1T_MAGIC = b"GT1G0600"
SUPPORTED_FORMATS = {0x01: "RGBA8", 0x59: "BC1/DXT1", 0x5B: "BC3/DXT5"}


class AtlasError(RuntimeError):
    """An input or output escaped the audited atlas-extraction contract."""


@dataclass(frozen=True)
class NestedEntry:
    index: int
    data: bytes


@dataclass(frozen=True)
class Texture:
    index: int
    format_code: int
    width: int
    height: int
    mip_count: int
    extra_version: int
    payload_offset: int
    payload: bytes


@dataclass(frozen=True)
class G1T:
    raw: bytes
    platform: int
    directory_offset: int
    textures: tuple[Texture, ...]


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AtlasError(f"input is not a regular file: {path}")
    return {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}


def private_output_root(value: str | Path) -> Path:
    root = Path(value).resolve()
    tmp = TMP_ROOT.resolve()
    try:
        root.relative_to(tmp)
    except ValueError as exc:
        raise AtlasError(f"output must remain below {tmp}: {root}") from exc
    if root == tmp:
        raise AtlasError("output must be a child of the tmp root")
    return root


def ensure_empty_output_root(root: Path) -> None:
    if root.exists() and any(root.iterdir()):
        raise AtlasError(f"refusing to mix an extraction into non-empty output: {root}")
    root.mkdir(parents=True, exist_ok=True)


def sanitize_component(value: str) -> str:
    clean = "".join(char if char.isalnum() or char in "._-" else "_" for char in value)
    return clean or "unnamed"


def parse_nested_link(blob: bytes) -> tuple[NestedEntry, ...]:
    """Parse the verified 32-byte nested LINK variant without rebuilding it."""

    if len(blob) < 32 or blob[:4] != b"LINK":
        raise AtlasError("nested entry is not a 32-byte LINK")
    count, table_offset, _resource_id, aligned_table_end = struct.unpack_from("<4I", blob, 4)
    if count == 0 or table_offset != 32:
        raise AtlasError("unsupported nested LINK count/table offset")
    table_end = table_offset + count * 8
    expected_aligned_end = (table_end + 31) & -32
    if aligned_table_end != expected_aligned_end or aligned_table_end > len(blob):
        raise AtlasError("nested LINK table alignment is inconsistent")
    pairs = [struct.unpack_from("<II", blob, table_offset + index * 8) for index in range(count)]
    entries: list[NestedEntry] = []
    for index, (offset, stored_size) in enumerate(pairs):
        end = offset + stored_size
        next_offset = pairs[index + 1][0] if index + 1 < count else end
        if offset < aligned_table_end or end > next_offset:
            raise AtlasError(f"nested LINK entry {index} has invalid bounds")
        # A few Switch-derived structures have virtual tail slots.  PC inputs
        # currently do not, but skipping a nominal non-physical slot is safer
        # than treating it as truncated content.
        if offset >= len(blob) or end > len(blob):
            continue
        entries.append(NestedEntry(index=index, data=blob[offset:end]))
    return tuple(entries)


def base_payload_size(format_code: int, width: int, height: int) -> int:
    if format_code == 0x01:
        return width * height * 4
    blocks = ((width + 3) // 4) * ((height + 3) // 4)
    if format_code == 0x59:
        return blocks * 8
    if format_code == 0x5B:
        return blocks * 16
    raise AtlasError(f"unsupported G1T format 0x{format_code:02X}")


def parse_g1t(raw: bytes) -> G1T:
    if len(raw) < 32 or raw[:8] != G1T_MAGIC:
        raise AtlasError("resource is not GT1G0600")
    declared_size, directory_offset, texture_count, platform = struct.unpack_from("<4I", raw, 8)
    if declared_size != len(raw):
        raise AtlasError(f"G1T declared size {declared_size} != actual {len(raw)}")
    if texture_count == 0 or directory_offset < 32:
        raise AtlasError("G1T directory is invalid")
    directory_end = directory_offset + texture_count * 4
    if directory_end > len(raw):
        raise AtlasError("G1T directory exceeds payload")
    rel_offsets = struct.unpack_from("<" + "I" * texture_count, raw, directory_offset)
    starts = [directory_offset + offset for offset in rel_offsets]
    if starts != sorted(starts) or starts[0] < directory_end or starts[-1] >= len(raw):
        raise AtlasError("G1T texture offsets are invalid")
    textures: list[Texture] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(raw)
        if end - start < 8:
            raise AtlasError(f"G1T texture {index} header is truncated")
        packed_info, format_code, packed_dimensions = struct.unpack_from("<BBB", raw, start)
        width = 1 << (packed_dimensions & 0x0F)
        height = 1 << (packed_dimensions >> 4)
        mip_count = packed_info >> 4
        extra_version = raw[start + 7]
        if extra_version:
            if end - start < 12:
                raise AtlasError(f"G1T texture {index} extra header is truncated")
            extra_length = struct.unpack_from("<I", raw, start + 8)[0]
            if extra_length < 4:
                raise AtlasError(f"G1T texture {index} extra header length is invalid")
            payload_offset = start + 8 + extra_length
        else:
            payload_offset = start + 8
        if payload_offset > end:
            raise AtlasError(f"G1T texture {index} payload starts beyond its node")
        if format_code in SUPPORTED_FORMATS:
            payload_size = base_payload_size(format_code, width, height)
            if payload_offset + payload_size > end:
                raise AtlasError(f"G1T texture {index} base mip exceeds its node")
            payload = raw[payload_offset : payload_offset + payload_size]
        else:
            payload = b""
        textures.append(
            Texture(
                index=index,
                format_code=format_code,
                width=width,
                height=height,
                mip_count=mip_count,
                extra_version=extra_version,
                payload_offset=payload_offset,
                payload=payload,
            )
        )
    return G1T(raw=raw, platform=platform, directory_offset=directory_offset, textures=tuple(textures))


def decode_bc1_block(block: bytes) -> bytes:
    if len(block) != 8:
        raise AtlasError("BC1 block must be eight bytes")
    color0, color1, indexes = struct.unpack("<HHI", block)
    first = png_codec.expand_565(color0)
    second = png_codec.expand_565(color1)
    if color0 > color1:
        third = tuple((2 * first[channel] + second[channel] + 1) // 3 for channel in range(3))
        fourth = tuple((first[channel] + 2 * second[channel] + 1) // 3 for channel in range(3))
        palette = ((*first, 255), (*second, 255), (*third, 255), (*fourth, 255))
    else:
        third = tuple((first[channel] + second[channel] + 1) // 2 for channel in range(3))
        palette = ((*first, 255), (*second, 255), (*third, 255), (0, 0, 0, 0))
    result = bytearray(64)
    for pixel in range(16):
        result[pixel * 4 : pixel * 4 + 4] = bytes(palette[(indexes >> (pixel * 2)) & 3])
    return bytes(result)


def decode_bc1_scalar(payload: bytes, width: int, height: int) -> bytes:
    block_width = (width + 3) // 4
    block_height = (height + 3) // 4
    if len(payload) != block_width * block_height * 8:
        raise AtlasError("BC1 payload size is inconsistent")
    result = bytearray(width * height * 4)
    cursor = 0
    for block_y in range(block_height):
        for block_x in range(block_width):
            pixels = decode_bc1_block(payload[cursor : cursor + 8])
            cursor += 8
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
                    result[target : target + 4] = pixels[source : source + 4]
    return bytes(result)


def _expand_565_np(colors: Any) -> Any:
    """Match ``pc_g1t_title_codec.expand_565`` for a NumPy uint16 array."""

    red = ((colors >> 11) & 0x1F).astype(np.uint8)
    green = ((colors >> 5) & 0x3F).astype(np.uint8)
    blue = (colors & 0x1F).astype(np.uint8)
    return np.stack(((red << 3) | (red >> 2), (green << 2) | (green >> 4), (blue << 3) | (blue >> 2)), axis=-1)


def _unblock_rgba(blocks: Any, width: int, height: int) -> bytes:
    rgba = blocks.transpose(0, 2, 1, 3, 4).reshape(blocks.shape[0] * 4, blocks.shape[1] * 4, 4)
    return rgba[:height, :width, :].tobytes()


def decode_bc1(payload: bytes, width: int, height: int) -> bytes:
    """Decode BC1 with a vectorized path, retaining an exact scalar fallback."""

    block_width = (width + 3) // 4
    block_height = (height + 3) // 4
    if len(payload) != block_width * block_height * 8:
        raise AtlasError("BC1 payload size is inconsistent")
    if np is None:
        return decode_bc1_scalar(payload, width, height)
    blocks = np.frombuffer(payload, dtype=np.uint8).reshape(block_height, block_width, 8)
    color0 = blocks[:, :, 0].astype(np.uint16) | (blocks[:, :, 1].astype(np.uint16) << 8)
    color1 = blocks[:, :, 2].astype(np.uint16) | (blocks[:, :, 3].astype(np.uint16) << 8)
    first = _expand_565_np(color0)
    second = _expand_565_np(color1)
    third = ((first.astype(np.uint16) + second.astype(np.uint16) + 1) // 2).astype(np.uint8)
    two_first = ((2 * first.astype(np.uint16) + second.astype(np.uint16) + 1) // 3).astype(np.uint8)
    two_second = ((first.astype(np.uint16) + 2 * second.astype(np.uint16) + 1) // 3).astype(np.uint8)
    # BC1 switches its third/fourth palette entries when color0 <= color1.
    use_four_color = color0 > color1
    color3 = np.where(use_four_color[:, :, None], two_first, third)
    color4 = np.where(use_four_color[:, :, None], two_second, np.zeros_like(two_second))
    alpha3 = np.full((block_height, block_width, 1), 255, dtype=np.uint8)
    alpha4 = np.where(use_four_color[:, :, None], alpha3, np.zeros_like(alpha3))
    palette = np.stack(
        (
            np.concatenate((first, alpha3), axis=-1),
            np.concatenate((second, alpha3), axis=-1),
            np.concatenate((color3, alpha3), axis=-1),
            np.concatenate((color4, alpha4), axis=-1),
        ),
        axis=2,
    )
    indexes = (
        blocks[:, :, 4].astype(np.uint32)
        | (blocks[:, :, 5].astype(np.uint32) << 8)
        | (blocks[:, :, 6].astype(np.uint32) << 16)
        | (blocks[:, :, 7].astype(np.uint32) << 24)
    )
    output = np.empty((block_height, block_width, 4, 4, 4), dtype=np.uint8)
    y_indexes = np.arange(block_height)[:, None]
    x_indexes = np.arange(block_width)[None, :]
    for local_y in range(4):
        for local_x in range(4):
            selected = (indexes >> (2 * (local_y * 4 + local_x))) & 3
            output[:, :, local_y, local_x, :] = palette[y_indexes, x_indexes, selected]
    return _unblock_rgba(output, width, height)


def decode_bc3_scalar(payload: bytes, width: int, height: int) -> bytes:
    """Delegate to the existing audited scalar codec when NumPy is absent."""

    return png_codec.decode_bc3(payload, width, height)


def decode_bc3(payload: bytes, width: int, height: int) -> bytes:
    """Vectorized BC3/DXT5 decoder matching the audited scalar codec exactly."""

    block_width = (width + 3) // 4
    block_height = (height + 3) // 4
    if len(payload) != block_width * block_height * 16:
        raise AtlasError("BC3 payload size is inconsistent")
    if np is None:
        return decode_bc3_scalar(payload, width, height)
    blocks = np.frombuffer(payload, dtype=np.uint8).reshape(block_height, block_width, 16)
    alpha0 = blocks[:, :, 0].astype(np.uint16)
    alpha1 = blocks[:, :, 1].astype(np.uint16)
    alpha_palette = np.empty((block_height, block_width, 8), dtype=np.uint8)
    alpha_palette[:, :, 0] = alpha0
    alpha_palette[:, :, 1] = alpha1
    seven_mode = alpha0 > alpha1
    for step in range(1, 7):
        seven_value = ((7 - step) * alpha0 + step * alpha1 + 3) // 7
        # Only indices 2..5 interpolate in the five-alpha mode.  The final
        # two entries are hard 0/255 as specified by BC3.
        five_value = ((5 - step) * alpha0 + step * alpha1 + 2) // 5 if step <= 4 else np.zeros_like(alpha0)
        alpha_palette[:, :, step + 1] = np.where(seven_mode, seven_value, five_value).astype(np.uint8)
    alpha_palette[:, :, 6] = np.where(seven_mode, alpha_palette[:, :, 6], 0)
    alpha_palette[:, :, 7] = np.where(seven_mode, alpha_palette[:, :, 7], 255)
    alpha_indexes = (
        blocks[:, :, 2].astype(np.uint64)
        | (blocks[:, :, 3].astype(np.uint64) << 8)
        | (blocks[:, :, 4].astype(np.uint64) << 16)
        | (blocks[:, :, 5].astype(np.uint64) << 24)
        | (blocks[:, :, 6].astype(np.uint64) << 32)
        | (blocks[:, :, 7].astype(np.uint64) << 40)
    )
    color0 = blocks[:, :, 8].astype(np.uint16) | (blocks[:, :, 9].astype(np.uint16) << 8)
    color1 = blocks[:, :, 10].astype(np.uint16) | (blocks[:, :, 11].astype(np.uint16) << 8)
    first = _expand_565_np(color0)
    second = _expand_565_np(color1)
    third = ((2 * first.astype(np.uint16) + second.astype(np.uint16) + 1) // 3).astype(np.uint8)
    fourth = ((first.astype(np.uint16) + 2 * second.astype(np.uint16) + 1) // 3).astype(np.uint8)
    color_palette = np.stack((first, second, third, fourth), axis=2)
    color_indexes = (
        blocks[:, :, 12].astype(np.uint32)
        | (blocks[:, :, 13].astype(np.uint32) << 8)
        | (blocks[:, :, 14].astype(np.uint32) << 16)
        | (blocks[:, :, 15].astype(np.uint32) << 24)
    )
    output = np.empty((block_height, block_width, 4, 4, 4), dtype=np.uint8)
    y_indexes = np.arange(block_height)[:, None]
    x_indexes = np.arange(block_width)[None, :]
    for local_y in range(4):
        for local_x in range(4):
            position = local_y * 4 + local_x
            color_choice = (color_indexes >> (2 * position)) & 3
            alpha_choice = (alpha_indexes >> (3 * position)) & 7
            output[:, :, local_y, local_x, :3] = color_palette[y_indexes, x_indexes, color_choice]
            output[:, :, local_y, local_x, 3] = alpha_palette[y_indexes, x_indexes, alpha_choice]
    return _unblock_rgba(output, width, height)


def decode_texture(texture: Texture) -> bytes | None:
    if texture.format_code == 0x01:
        if len(texture.payload) != texture.width * texture.height * 4:
            raise AtlasError("RGBA8 payload size is inconsistent")
        return texture.payload
    if texture.format_code == 0x59:
        return decode_bc1(texture.payload, texture.width, texture.height)
    if texture.format_code == 0x5B:
        return decode_bc3(texture.payload, texture.width, texture.height)
    return None


def nearest_resize(rgba: bytes, width: int, height: int, target_width: int, target_height: int) -> bytes:
    output = bytearray(target_width * target_height * 4)
    for y in range(target_height):
        source_y = min(height - 1, y * height // target_height)
        for x in range(target_width):
            source_x = min(width - 1, x * width // target_width)
            source = (source_y * width + source_x) * 4
            target = (y * target_width + x) * 4
            output[target : target + 4] = rgba[source : source + 4]
    return bytes(output)


def checker_composite(rgba: bytes, width: int, height: int) -> bytes:
    output = bytearray(len(rgba))
    for y in range(height):
        for x in range(width):
            source = (y * width + x) * 4
            alpha = rgba[source + 3]
            background = 64 if ((x // 8) ^ (y // 8)) & 1 else 34
            for channel in range(3):
                output[source + channel] = (rgba[source + channel] * alpha + background * (255 - alpha) + 127) // 255
            output[source + 3] = 255
    return bytes(output)


def write_png(path: Path, rgba: bytes, width: int, height: int) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if Image is not None:
        # Pillow's native PNG encoder avoids spending seconds per large texture
        # in the pure-Python zlib path.  The decoded RGBA pixels remain exactly
        # the same; only the inspection PNG encoding is non-contractual.
        image = Image.frombytes("RGBA", (width, height), rgba)
        image.save(path, format="PNG", compress_level=3)
        image.close()
        size = path.stat().st_size
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest().upper()
    else:
        blob = png_codec.encode_rgba_png(rgba, width, height)
        path.write_bytes(blob)
        size = len(blob)
        digest = sha256_bytes(blob)
    return {"path": str(path), "size": size, "sha256": digest, "dimensions": [width, height]}


def write_raw(path: Path, blob: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": str(path), **spec(blob)}


def preview_rgba(rgba: bytes, width: int, height: int) -> tuple[bytes, int, int]:
    max_width, max_height = 320, 180
    scale = min(max_width / width, max_height / height, 1.0)
    target_width = max(1, round(width * scale))
    target_height = max(1, round(height * scale))
    flattened = checker_composite(rgba, width, height)
    return nearest_resize(flattened, width, height, target_width, target_height), target_width, target_height


def preview_dimensions(width: int, height: int) -> tuple[int, int]:
    scale = min(320 / width, 180 / height, 1.0)
    return max(1, round(width * scale)), max(1, round(height * scale))


def _sample_bc1_preview(texture: Texture, target_width: int, target_height: int) -> bytes:
    """Nearest-sample a BC1 texture without allocating its full RGBA image."""

    blocks_wide = (texture.width + 3) // 4
    blocks_high = (texture.height + 3) // 4
    blocks = np.frombuffer(texture.payload, dtype=np.uint8).reshape(blocks_high, blocks_wide, 8)
    source_y = (np.arange(target_height) * texture.height // target_height).astype(np.intp)
    source_x = (np.arange(target_width) * texture.width // target_width).astype(np.intp)
    block = blocks[source_y[:, None] // 4, source_x[None, :] // 4]
    color0 = block[:, :, 0].astype(np.uint16) | (block[:, :, 1].astype(np.uint16) << 8)
    color1 = block[:, :, 2].astype(np.uint16) | (block[:, :, 3].astype(np.uint16) << 8)
    first = _expand_565_np(color0)
    second = _expand_565_np(color1)
    average = ((first.astype(np.uint16) + second.astype(np.uint16) + 1) // 2).astype(np.uint8)
    two_first = ((2 * first.astype(np.uint16) + second.astype(np.uint16) + 1) // 3).astype(np.uint8)
    two_second = ((first.astype(np.uint16) + 2 * second.astype(np.uint16) + 1) // 3).astype(np.uint8)
    four_color = color0 > color1
    third = np.where(four_color[:, :, None], two_first, average)
    fourth = np.where(four_color[:, :, None], two_second, np.zeros_like(two_second))
    opaque = np.full((target_height, target_width, 1), 255, dtype=np.uint8)
    fourth_alpha = np.where(four_color[:, :, None], opaque, np.zeros_like(opaque))
    palette = np.stack(
        (
            np.concatenate((first, opaque), axis=-1),
            np.concatenate((second, opaque), axis=-1),
            np.concatenate((third, opaque), axis=-1),
            np.concatenate((fourth, fourth_alpha), axis=-1),
        ),
        axis=2,
    )
    indexes = (
        block[:, :, 4].astype(np.uint32)
        | (block[:, :, 5].astype(np.uint32) << 8)
        | (block[:, :, 6].astype(np.uint32) << 16)
        | (block[:, :, 7].astype(np.uint32) << 24)
    )
    positions = ((source_y[:, None] % 4) * 4 + (source_x[None, :] % 4)).astype(np.uint32)
    selected = (indexes >> (2 * positions)) & 3
    return np.take_along_axis(palette, selected[:, :, None, None], axis=2)[:, :, 0, :].tobytes()


def _sample_bc3_preview(texture: Texture, target_width: int, target_height: int) -> bytes:
    """Nearest-sample a BC3 texture without allocating its full RGBA image."""

    blocks_wide = (texture.width + 3) // 4
    blocks_high = (texture.height + 3) // 4
    blocks = np.frombuffer(texture.payload, dtype=np.uint8).reshape(blocks_high, blocks_wide, 16)
    source_y = (np.arange(target_height) * texture.height // target_height).astype(np.intp)
    source_x = (np.arange(target_width) * texture.width // target_width).astype(np.intp)
    block = blocks[source_y[:, None] // 4, source_x[None, :] // 4]
    alpha0 = block[:, :, 0].astype(np.uint16)
    alpha1 = block[:, :, 1].astype(np.uint16)
    alpha_palette = np.empty((target_height, target_width, 8), dtype=np.uint8)
    alpha_palette[:, :, 0] = alpha0
    alpha_palette[:, :, 1] = alpha1
    seven_mode = alpha0 > alpha1
    for step in range(1, 7):
        seven_value = ((7 - step) * alpha0 + step * alpha1 + 3) // 7
        five_value = ((5 - step) * alpha0 + step * alpha1 + 2) // 5 if step <= 4 else np.zeros_like(alpha0)
        alpha_palette[:, :, step + 1] = np.where(seven_mode, seven_value, five_value).astype(np.uint8)
    alpha_palette[:, :, 6] = np.where(seven_mode, alpha_palette[:, :, 6], 0)
    alpha_palette[:, :, 7] = np.where(seven_mode, alpha_palette[:, :, 7], 255)
    alpha_indexes = (
        block[:, :, 2].astype(np.uint64)
        | (block[:, :, 3].astype(np.uint64) << 8)
        | (block[:, :, 4].astype(np.uint64) << 16)
        | (block[:, :, 5].astype(np.uint64) << 24)
        | (block[:, :, 6].astype(np.uint64) << 32)
        | (block[:, :, 7].astype(np.uint64) << 40)
    )
    color0 = block[:, :, 8].astype(np.uint16) | (block[:, :, 9].astype(np.uint16) << 8)
    color1 = block[:, :, 10].astype(np.uint16) | (block[:, :, 11].astype(np.uint16) << 8)
    first = _expand_565_np(color0)
    second = _expand_565_np(color1)
    third = ((2 * first.astype(np.uint16) + second.astype(np.uint16) + 1) // 3).astype(np.uint8)
    fourth = ((first.astype(np.uint16) + 2 * second.astype(np.uint16) + 1) // 3).astype(np.uint8)
    colors = np.stack((first, second, third, fourth), axis=2)
    color_indexes = (
        block[:, :, 12].astype(np.uint32)
        | (block[:, :, 13].astype(np.uint32) << 8)
        | (block[:, :, 14].astype(np.uint32) << 16)
        | (block[:, :, 15].astype(np.uint32) << 24)
    )
    positions = ((source_y[:, None] % 4) * 4 + (source_x[None, :] % 4)).astype(np.uint64)
    color_choice = (color_indexes >> (2 * positions.astype(np.uint32))) & 3
    alpha_choice = (alpha_indexes >> (3 * positions)) & 7
    output = np.empty((target_height, target_width, 4), dtype=np.uint8)
    output[:, :, :3] = np.take_along_axis(colors, color_choice[:, :, None, None], axis=2)[:, :, 0, :]
    output[:, :, 3] = np.take_along_axis(alpha_palette, alpha_choice[:, :, None], axis=2)[:, :, 0]
    return output.tobytes()


def decode_texture_preview(texture: Texture) -> tuple[bytes, int, int] | None:
    """Create a fast exact nearest-sampled preview from a supported texture."""

    target_width, target_height = preview_dimensions(texture.width, texture.height)
    if np is None:
        rgba = decode_texture(texture)
        if rgba is None:
            return None
        return preview_rgba(rgba, texture.width, texture.height)
    if texture.format_code == 0x01:
        source = np.frombuffer(texture.payload, dtype=np.uint8).reshape(texture.height, texture.width, 4)
        source_y = (np.arange(target_height) * texture.height // target_height).astype(np.intp)
        source_x = (np.arange(target_width) * texture.width // target_width).astype(np.intp)
        rgba = source[source_y[:, None], source_x[None, :]].tobytes()
    elif texture.format_code == 0x59:
        rgba = _sample_bc1_preview(texture, target_width, target_height)
    elif texture.format_code == 0x5B:
        rgba = _sample_bc3_preview(texture, target_width, target_height)
    else:
        return None
    return checker_composite(rgba, target_width, target_height), target_width, target_height


def archive_g1ts(blob: bytes, allowed_outers: set[int] | None = None) -> Iterator[tuple[int, int, bytes, G1T]]:
    outer = lz4.parse_link(blob)
    if lz4.rebuild_link(outer) != blob:
        raise AtlasError("top-level LINK identity rebuild failed")
    for outer_entry in outer.entries:
        if allowed_outers is not None and outer_entry.index not in allowed_outers:
            continue
        if outer_entry.data.startswith(b"LINK"):
            inner_entries: Iterable[NestedEntry] = parse_nested_link(outer_entry.data)
        else:
            inner_entries = (NestedEntry(index=0, data=outer_entry.data),)
        for inner_entry in inner_entries:
            try:
                _header, raw = lz4.decompress_wrapper(inner_entry.data)
            except lz4.LZ4Error:
                continue
            if raw[:8] != G1T_MAGIC:
                continue
            yield outer_entry.index, inner_entry.index, raw, parse_g1t(raw)


def record_texture(
    output_root: Path,
    family: str,
    group: str,
    texture: Texture,
    full_resolution: bool,
) -> dict[str, Any]:
    base = output_root / "decoded" / family / group
    row: dict[str, Any] = {
        "texture_index": texture.index,
        "format_code": f"0x{texture.format_code:02X}",
        "format_name": SUPPORTED_FORMATS.get(texture.format_code, "unsupported"),
        "dimensions": [texture.width, texture.height],
        "mip_count": texture.mip_count,
        "extra_version": texture.extra_version,
        "base_payload": spec(texture.payload) if texture.payload else None,
        "decoded": texture.format_code in SUPPORTED_FORMATS,
    }
    if texture.format_code not in SUPPORTED_FORMATS:
        return row
    stem = f"texture_{texture.index:03d}_{texture.width}x{texture.height}_fmt{texture.format_code:02X}"
    if full_resolution:
        rgba = decode_texture(texture)
        if rgba is None:
            raise AtlasError("supported texture did not decode")
        row["png"] = write_png(base / f"{stem}.png", rgba, texture.width, texture.height)
        row["rgba_sha256"] = sha256_bytes(rgba)
        preview, preview_width, preview_height = preview_rgba(rgba, texture.width, texture.height)
    else:
        sampled = decode_texture_preview(texture)
        if sampled is None:
            raise AtlasError("supported texture did not produce preview")
        preview, preview_width, preview_height = sampled
        row["preview_sampling"] = "nearest exact source pixels; full RGBA hash omitted until full-resolution extraction"
    thumbnail = write_png(output_root / "previews" / family / group / f"{stem}.png", preview, preview_width, preview_height)
    row["preview"] = thumbnail
    return row


def extract_link_archive(
    path: Path,
    output_root: Path,
    allowed_outers: set[int] | None,
    full_resolution: bool,
) -> dict[str, Any]:
    before = file_spec(path)
    blob = path.read_bytes()
    if spec(blob)["sha256"] != before["sha256"]:
        raise AtlasError(f"read hash mismatch: {path}")
    outer = lz4.parse_link(blob)
    if lz4.rebuild_link(outer) != blob:
        raise AtlasError(f"LINK identity rebuild failed: {path}")
    family = sanitize_component(f"{path.parent.name}_{path.stem}")
    groups: list[dict[str, Any]] = []
    decoded_texture_count = 0
    all_texture_count = 0
    for outer_index, inner_index, raw, g1t in archive_g1ts(blob, allowed_outers):
        group = f"outer_{outer_index:03d}_slot_{inner_index:03d}"
        raw_record = write_raw(output_root / "raw_g1t" / family / f"{group}.g1t", raw)
        texture_rows: list[dict[str, Any]] = []
        for texture in g1t.textures:
            all_texture_count += 1
            if texture.format_code in SUPPORTED_FORMATS:
                decoded_texture_count += 1
            texture_rows.append(record_texture(output_root, family, group, texture, full_resolution))
        groups.append(
            {
                "outer_index": outer_index,
                "nested_slot": inner_index,
                "g1t": {"raw": raw_record, "platform": g1t.platform, "directory_offset": g1t.directory_offset},
                "textures": texture_rows,
            }
        )
    after = file_spec(path)
    if after != before:
        raise AtlasError(f"source changed while extracting: {path}")
    return {
        "kind": "LINK-res-lang",
        "input": before,
        "outer_entry_count": len(outer.entries),
        "requested_outer_entries": sorted(allowed_outers) if allowed_outers is not None else "all",
        "g1t_container_count": len(groups),
        "texture_count": all_texture_count,
        "decoded_texture_count": decoded_texture_count,
        "groups": groups,
    }


def direct_g1t_records(blob: bytes) -> Iterator[tuple[int, int, bytes, G1T]]:
    offset = 0
    index = 0
    while offset < len(blob):
        if blob[offset : offset + 8] != G1T_MAGIC:
            raise AtlasError(f"G1T bank record {index} at 0x{offset:X} lacks GT1G0600 magic")
        if offset + 32 > len(blob):
            raise AtlasError(f"G1T bank record {index} header is truncated")
        declared_size = struct.unpack_from("<I", blob, offset + 8)[0]
        if declared_size < 32 or offset + declared_size > len(blob):
            raise AtlasError(f"G1T bank record {index} declared size is invalid")
        raw = blob[offset : offset + declared_size]
        yield index, offset, raw, parse_g1t(raw)
        offset += declared_size
        index += 1
    if offset != len(blob):
        raise AtlasError("G1T bank did not end on an exact record boundary")


def extract_g1t_bank(path: Path, output_root: Path, full_resolution: bool) -> dict[str, Any]:
    before = file_spec(path)
    blob = path.read_bytes()
    family = sanitize_component(f"{path.parent.name}_{path.stem}")
    records: list[dict[str, Any]] = []
    texture_count = 0
    decoded_texture_count = 0
    for index, offset, raw, g1t in direct_g1t_records(blob):
        group = f"record_{index:03d}"
        raw_record = write_raw(output_root / "raw_g1t" / family / f"{group}.g1t", raw)
        texture_rows: list[dict[str, Any]] = []
        for texture in g1t.textures:
            texture_count += 1
            if texture.format_code in SUPPORTED_FORMATS:
                decoded_texture_count += 1
            texture_rows.append(record_texture(output_root, family, group, texture, full_resolution))
        records.append(
            {
                "record_index": index,
                "offset": offset,
                "g1t": {"raw": raw_record, "platform": g1t.platform, "directory_offset": g1t.directory_offset},
                "textures": texture_rows,
            }
        )
    after = file_spec(path)
    if after != before:
        raise AtlasError(f"source changed while extracting: {path}")
    return {
        "kind": "direct-concatenated-G1T-bank",
        "input": before,
        "record_count": len(records),
        "texture_count": texture_count,
        "decoded_texture_count": decoded_texture_count,
        "records": records,
    }


def byte_entropy(blob: bytes) -> float:
    if not blob:
        return 0.0
    counts = [0] * 256
    for value in blob:
        counts[value] += 1
    length = len(blob)
    return -sum((count / length) * math.log2(count / length) for count in counts if count)


def probe_opaque_root(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise AtlasError(f"opaque root is not a directory: {root}")
    rows: list[dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        with path.open("rb") as stream:
            prefix = stream.read(65536)
        rows.append(
            {
                "relative_path": path.relative_to(root).as_posix(),
                "size": path.stat().st_size,
                "prefix_hex": prefix[:32].hex().upper(),
                "prefix_ascii": "".join(chr(value) if 32 <= value < 127 else "." for value in prefix[:32]),
                "prefix_entropy_bits_per_byte": round(byte_entropy(prefix), 6),
                "top_level_kind": "LINK" if prefix.startswith(b"LINK") else "GT1G0600" if prefix.startswith(G1T_MAGIC) else "opaque",
                "g1t_magic_in_first_64KiB": prefix.find(G1T_MAGIC),
            }
        )
    return {"root": str(root), "file_count": len(rows), "files": rows}


def paste(canvas: bytearray, canvas_width: int, rgba: bytes, width: int, height: int, x0: int, y0: int) -> None:
    for y in range(height):
        source = y * width * 4
        target = ((y0 + y) * canvas_width + x0) * 4
        canvas[target : target + width * 4] = rgba[source : source + width * 4]


def contact_sheets(output_root: Path) -> list[dict[str, Any]]:
    previews = sorted((output_root / "previews").rglob("*.png"))
    # Each source group gets a compact sheet; the manifest retains exact paths.
    by_group: dict[Path, list[Path]] = {}
    preview_root = output_root / "previews"
    for path in previews:
        by_group.setdefault(path.parent.relative_to(preview_root), []).append(path)
    sheets: list[dict[str, Any]] = []
    columns, cell_width, cell_height = 4, 336, 196
    for group, items in sorted(by_group.items(), key=lambda item: item[0].as_posix()):
        for page in range((len(items) + columns * 3 - 1) // (columns * 3)):
            selected = items[page * columns * 3 : (page + 1) * columns * 3]
            rows = (len(selected) + columns - 1) // columns
            width, height = columns * cell_width, rows * cell_height
            canvas = bytearray(bytes((18, 18, 18, 255)) * (width * height))
            for item_index, path in enumerate(selected):
                rgba, image_width, image_height = png_codec.decode_png(path.read_bytes())
                x = (item_index % columns) * cell_width + (cell_width - image_width) // 2
                y = (item_index // columns) * cell_height + (cell_height - image_height) // 2
                paste(canvas, width, rgba, image_width, image_height, x, y)
            destination = output_root / "contact_sheets" / group / f"page_{page + 1:03d}.png"
            record = write_png(destination, bytes(canvas), width, height)
            record["preview_files"] = [path.relative_to(preview_root).as_posix() for path in selected]
            sheets.append(record)
    return sheets


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, action="append", default=[], help="top-level LINK res_lang archive; repeatable")
    parser.add_argument("--outer", type=int, action="append", default=[], help="limit LINK extraction to these outer entries; repeatable")
    parser.add_argument("--g1t-bank", type=Path, action="append", default=[], help="direct concatenated G1T bank; repeatable")
    parser.add_argument("--opaque-root", type=Path, action="append", default=[], help="unrecognized container directory to fingerprint; repeatable")
    parser.add_argument("--full-resolution", action="store_true", help="also write full-resolution decoded PNGs (use for focused UI groups)")
    parser.add_argument("--output-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.archive and not args.g1t_bank and not args.opaque_root:
        raise AtlasError("at least one archive, G1T bank, or opaque root is required")
    output_root = private_output_root(args.output_root)
    ensure_empty_output_root(output_root)
    allowed_outers = set(args.outer) if args.outer else None
    if allowed_outers is not None and any(outer < 0 for outer in allowed_outers):
        raise AtlasError("outer entries must be non-negative")
    archives = [extract_link_archive(path.resolve(), output_root, allowed_outers, args.full_resolution) for path in args.archive]
    banks = [extract_g1t_bank(path.resolve(), output_root, args.full_resolution) for path in args.g1t_bank]
    opaque = [probe_opaque_root(path.resolve()) for path in args.opaque_root]
    sheets = contact_sheets(output_root)
    report = {
        "schema": "nobu16.pc-image-atlas-extraction.v1",
        "outputs": {"root": str(output_root), "contact_sheet_count": len(sheets), "contact_sheets": sheets},
        "link_archives": archives,
        "g1t_banks": banks,
        "opaque_container_probes": opaque,
        "safety": {
            "source_files_written": False,
            "steam_files_written": False,
            "outputs_private_tmp_only": True,
            "unsupported_containers_rebuilt": False,
        },
    }
    report_path = output_root / "atlas_inventory.json"
    report_path.write_bytes(canonical_json(report))
    print("status=PASS")
    print(f"inventory={report_path}")
    print(f"link_archives={len(archives)}")
    print(f"g1t_banks={len(banks)}")
    print(f"contact_sheets={len(sheets)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AtlasError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
