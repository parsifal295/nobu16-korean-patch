#!/usr/bin/env python3
"""Rebuild the Steam-JP QHD image routes in PORT1 and PORT3.

The builder is deliberately file-only and writes below ``tmp``.  PORT1 lifts
only the already-audited low-resolution Korean pixel delta into the exact 2x
PC geometry, preserving every unrelated BC3 block and every unrelated LINK
entry.  PORT3 titles are rendered directly from the pinned Korean source PNGs
into the native 1024x256 Japanese title placement boxes.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
TMP = REPO / "tmp"
TITLE_WORKSTREAM = REPO / "workstreams" / "steam_jp_title_images_v1"
WHEEL_WORKSTREAM = REPO / "workstreams" / "steam_jp_wheel_toprows_v1"
MILITARY_WORKSTREAM = REPO / "workstreams" / "steam_jp_military_overlay_v1"
BANNER_WORKSTREAM = REPO / "workstreams" / "steam_jp_battle_banners_v1"
TUTORIAL_WORKSTREAM = REPO / "workstreams" / "steam_jp_tutorial_diagram_v1"
for candidate in (TOOLS, TITLE_WORKSTREAM, WHEEL_WORKSTREAM, MILITARY_WORKSTREAM, BANNER_WORKSTREAM, TUTORIAL_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as codec  # noqa: E402
import build_steam_jp_title_images_v1 as title_v1  # noqa: E402
import build_steam_jp_wheel_toprows_v1 as wheel_v1  # noqa: E402
import build_steam_jp_military_overlay_v1 as military_v1  # noqa: E402
import build_steam_jp_battle_banners_v1 as banner_v1  # noqa: E402
import build_steam_jp_tutorial_diagram_v1 as tutorial_v1  # noqa: E402

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - the bundled runtime has NumPy.
    raise RuntimeError("the bundled NumPy runtime is required") from exc


SCHEMA = "nobu16.kr.steam-jp-port-highres-images.v1"
PORT1_TARGETS: tuple[Mapping[str, Any], ...] = (
    {"name": "command_wheel", "low_outer": 8, "high_outer": 3, "resource_id": 474, "textures": (0,)},
    {"name": "military_overlay", "low_outer": 12, "high_outer": 17, "resource_id": 58, "textures": (0,)},
    {"name": "battle_banners", "low_outer": 13, "high_outer": 21, "resource_id": 79, "textures": tuple(range(48, 57))},
    {"name": "tutorial_diagram", "low_outer": 16, "high_outer": 23, "resource_id": 64, "textures": (0,)},
)
PORT1_OUTERS = tuple(int(row["high_outer"]) for row in PORT1_TARGETS)
PORT3_OUTER = 0
TITLE_TARGETS = tuple(range(108))
TITLE_TAIL = (108, 109)
TITLE_WIDTH = 1024
TITLE_HEIGHT = 256

EXPECTED_INPUTS = {
    "low_stock": {
        "size": 154216023,
        "sha256": "0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0",
    },
    "low_korean": {
        "size": 160095868,
        "sha256": "2F8048EC34B8B86CED54C0DC9A0879522D2717953805A4E4CC5EFF05407A4A45",
    },
    "port1": {
        "size": 79243911,
        "sha256": "00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7",
    },
    "port3": {
        "size": 43460485,
        "sha256": "BE1361E17341D433931EB5740B228EF1842BF6DF2F01D4F582CE790A9A57A154",
    },
}


class HighresError(ValueError):
    """Raised when the narrow high-resolution rebuild contract is violated."""


@dataclass(frozen=True)
class NestedEntry:
    index: int
    data: bytes
    gap_after: bytes


@dataclass(frozen=True)
class NestedLink:
    fixed_header: bytes
    table_padding: bytes
    entries: tuple[NestedEntry, ...]
    resource_id: int
    original_size: int


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HighresError(message)


def sha256_bytes(blob: bytes | bytearray | memoryview) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256_file(path)}


def bytes_spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def require_spec(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = file_spec(path)
    require(actual == dict(expected), f"{label} pin mismatch: expected={dict(expected)} actual={actual}")
    return actual


def ensure_tmp(path: Path, *, create: bool = False) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(TMP.resolve())
    except ValueError as exc:
        raise HighresError(f"output must remain below {TMP.resolve()}: {resolved}") from exc
    require(resolved != TMP.resolve(), "output may not be the tmp root itself")
    if create:
        resolved.mkdir(parents=True, exist_ok=True)
        resolved = resolved.resolve()
        try:
            resolved.relative_to(TMP.resolve())
        except ValueError as exc:
            raise HighresError("created output escaped tmp") from exc
    return resolved


def fresh_output(path: Path) -> Path:
    root = ensure_tmp(path)
    if root.exists():
        require(not any(root.iterdir()), f"refusing to mix output into non-empty directory: {root}")
    return ensure_tmp(root, create=True)


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    target = ensure_tmp(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target = ensure_tmp(target)
    forbidden_resolved = {item.resolve() for item in forbidden}
    require(target not in forbidden_resolved, f"refusing to overwrite input: {target}")
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: Mapping[str, Any], *, forbidden: Iterable[Path] = ()) -> None:
    atomic_write(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        forbidden=forbidden,
    )


def parse_nested_link(blob: bytes, *, expected_resource_id: int | None = None) -> NestedLink:
    require(len(blob) >= 32 and blob[:4] == b"LINK", "resource is not a 32-byte nested LINK")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", blob, 4)
    require(count > 0 and table_offset == 32, "unsupported nested LINK header")
    table_end = table_offset + count * 8
    require(aligned_table_end == (table_end + 31) & -32, "nested LINK table alignment differs")
    require(aligned_table_end <= len(blob), "nested LINK table exceeds resource")
    if expected_resource_id is not None:
        require(resource_id == expected_resource_id, f"nested resource id {resource_id} != {expected_resource_id}")
    pairs = [struct.unpack_from("<II", blob, table_offset + index * 8) for index in range(count)]
    require(pairs[0][0] >= aligned_table_end, "nested LINK data overlaps its table")
    entries: list[NestedEntry] = []
    for index, (offset, size) in enumerate(pairs):
        end = offset + size
        next_offset = pairs[index + 1][0] if index + 1 < count else len(blob)
        require(offset >= aligned_table_end and end <= next_offset <= len(blob), f"nested entry {index} bounds differ")
        entries.append(NestedEntry(index, blob[offset:end], blob[end:next_offset]))
    parsed = NestedLink(blob[:table_offset], blob[table_end:pairs[0][0]], tuple(entries), resource_id, len(blob))
    require(rebuild_nested_link(parsed) == blob, "nested LINK identity gate failed")
    return parsed


def rebuild_nested_link(link: NestedLink, replacements: Mapping[int, bytes] | None = None) -> bytes:
    replacements = replacements or {}
    count = len(link.entries)
    require(len(link.fixed_header) == 32, "nested fixed header size changed")
    output = bytearray(link.fixed_header)
    output.extend(b"\0" * (count * 8))
    output.extend(link.table_padding)
    pairs: list[tuple[int, int]] = []
    for entry in link.entries:
        payload = replacements.get(entry.index, entry.data)
        pairs.append((len(output), len(payload)))
        output.extend(payload)
        output.extend(entry.gap_after)
    for index, (offset, size) in enumerate(pairs):
        struct.pack_into("<II", output, 32 + index * 8, offset, size)
    return bytes(output)


def outer_hashes(archive: lz4.LinkArchive) -> dict[str, str]:
    return {str(entry.index): sha256_bytes(entry.data) for entry in archive.entries}


def g1t_wrapper_entry(link: NestedLink) -> tuple[int, lz4.WrapperHeader, bytes, atlas_codec.G1T]:
    matches: list[tuple[int, lz4.WrapperHeader, bytes, atlas_codec.G1T]] = []
    for entry in link.entries:
        try:
            header, raw = lz4.decompress_wrapper(entry.data)
            g1t = atlas_codec.parse_g1t(raw)
        except (lz4.LZ4Error, atlas_codec.AtlasError):
            continue
        matches.append((entry.index, header, raw, g1t))
    require(len(matches) == 1, f"expected one nested G1T wrapper, found {len(matches)}")
    return matches[0]


def replace_g1t_payloads(raw: bytes, g1t: atlas_codec.G1T, replacements: Mapping[int, bytes]) -> bytes:
    output = bytearray(raw)
    for index, payload in replacements.items():
        require(0 <= index < len(g1t.textures), f"texture index {index} out of range")
        texture = g1t.textures[index]
        require(len(payload) == len(texture.payload), f"texture {index} payload size changed")
        start = texture.payload_offset
        output[start : start + len(texture.payload)] = payload
    return bytes(output)


def changed_block_bbox(blocks: Sequence[tuple[int, int]]) -> list[int] | None:
    if not blocks:
        return None
    xs = [item[0] for item in blocks]
    ys = [item[1] for item in blocks]
    return [min(xs), min(ys), max(xs) + 1, max(ys) + 1]


def lift_bc3_delta_2x(
    *,
    low_before: atlas_codec.Texture,
    low_after: atlas_codec.Texture,
    high_template: atlas_codec.Texture,
) -> tuple[bytes, dict[str, Any]]:
    """Lift changed low pixels into native 2x BC3 blocks.

    A high 4x4 block maps to exactly one low 2x2 pixel group.  Pixels whose
    low before/after values agree retain the decoded native high pixel; only
    proven Korean delta pixels receive a nearest 2x copy.
    """

    require(low_before.format_code == low_after.format_code == high_template.format_code == 0x5B, "delta lift requires BC3")
    require((low_before.width, low_before.height) == (low_after.width, low_after.height), "low texture geometry differs")
    require((high_template.width, high_template.height) == (low_before.width * 2, low_before.height * 2), "high texture is not exact 2x geometry")
    require(low_before.width % 2 == 0 and low_before.height % 2 == 0, "low geometry must be divisible by two")
    before_rgba = np.frombuffer(atlas_codec.decode_texture(low_before), dtype=np.uint8).reshape(low_before.height, low_before.width, 4)
    after_rgba = np.frombuffer(atlas_codec.decode_texture(low_after), dtype=np.uint8).reshape(low_after.height, low_after.width, 4)
    pixel_mask = np.any(before_rgba != after_rgba, axis=2)
    changed_pixels = int(np.count_nonzero(pixel_mask))
    require(changed_pixels > 0, "selected low texture has no Korean pixel delta")
    block_mask = pixel_mask.reshape(low_before.height // 2, 2, low_before.width // 2, 2).any(axis=(1, 3))
    block_y, block_x = np.nonzero(block_mask)
    changed_blocks = [(int(x), int(y)) for y, x in zip(block_y.tolist(), block_x.tolist())]
    output = bytearray(high_template.payload)
    blocks_wide = high_template.width // 4
    encoded = 0
    identical_encoded = 0
    for bx, by in changed_blocks:
        offset = (by * blocks_wide + bx) * 16
        old_bc3 = bytes(output[offset : offset + 16])
        rgba = bytearray(codec.decode_bc3_block(old_bc3))
        for local_y in range(4):
            low_y = by * 2 + local_y // 2
            for local_x in range(4):
                low_x = bx * 2 + local_x // 2
                if not bool(pixel_mask[low_y, low_x]):
                    continue
                source = after_rgba[low_y, low_x].tobytes()
                target = (local_y * 4 + local_x) * 4
                rgba[target : target + 4] = source
        new_bc3 = codec.encode_bc3_block(bytes(rgba))
        if new_bc3 == old_bc3:
            identical_encoded += 1
        else:
            output[offset : offset + 16] = new_bc3
            encoded += 1
    del before_rgba, after_rgba, pixel_mask, block_mask
    return bytes(output), {
        "low_dimensions": [low_before.width, low_before.height],
        "high_dimensions": [high_template.width, high_template.height],
        "changed_low_pixels": changed_pixels,
        "allowed_high_bc3_blocks": len(changed_blocks),
        "changed_high_bc3_blocks": encoded,
        "encoded_but_identical_blocks": identical_encoded,
        "changed_high_block_bbox": changed_block_bbox(changed_blocks),
        "resampler": "nearest_2x_only_where_low_before_differs_from_low_korean",
        "unselected_high_blocks_byte_preserved": True,
    }


def rect_blocks(rect: Sequence[int], width: int, height: int) -> set[tuple[int, int]]:
    left, top, right, bottom = (int(value) for value in rect)
    require(0 <= left < right <= width and 0 <= top < bottom <= height, f"rectangle escapes {width}x{height}: {tuple(rect)}")
    return {
        (block_x, block_y)
        for block_y in range(top // 4, (bottom + 3) // 4)
        for block_x in range(left // 4, (right + 3) // 4)
    }


def encode_selected_blocks(
    requested: bytes,
    width: int,
    height: int,
    template: bytes,
    allowed: set[tuple[int, int]],
) -> tuple[bytes, int]:
    require(len(requested) == width * height * 4, "selected-block RGBA geometry differs")
    require(len(template) == width * height, "selected-block BC3 geometry differs")
    output = bytearray(template)
    blocks_wide = width // 4
    encoded = 0
    for block_x, block_y in sorted(allowed):
        require(0 <= block_x < blocks_wide and 0 <= block_y < height // 4, "selected BC3 block escapes texture")
        index = block_y * blocks_wide + block_x
        old = template[index * 16 : index * 16 + 16]
        rgba = codec.extract_rgba_block(requested, width, height, block_x, block_y)
        if codec.decode_bc3_block(old) == rgba:
            continue
        output[index * 16 : index * 16 + 16] = codec.encode_bc3_block(rgba)
        encoded += 1
    require(encoded > 0, "selected-block composition encoded no BC3 block")
    return bytes(output), encoded


def clear_rect(target: bytearray, width: int, rect: Sequence[int]) -> None:
    left, top, right, bottom = (int(value) for value in rect)
    height = len(target) // (width * 4)
    require(0 <= left < right <= width and 0 <= top < bottom <= height, "clear rectangle escapes canvas")
    empty = b"\0" * ((right - left) * 4)
    for y in range(top, bottom):
        start = (y * width + left) * 4
        target[start : start + len(empty)] = empty


def paste_rect(target: bytearray, width: int, rect: Sequence[int], source: bytes) -> None:
    left, top, right, bottom = (int(value) for value in rect)
    height = len(target) // (width * 4)
    require(0 <= left < right <= width and 0 <= top < bottom <= height, "paste rectangle escapes canvas")
    patch_width, patch_height = right - left, bottom - top
    require(len(source) == patch_width * patch_height * 4, "paste source geometry differs")
    for y in range(patch_height):
        source_start = y * patch_width * 4
        target_start = ((top + y) * width + left) * 4
        target[target_start : target_start + patch_width * 4] = source[source_start : source_start + patch_width * 4]


def compose_wheel_high(
    texture: atlas_codec.Texture,
    switch_jp: bytes,
    switch_ko: bytes,
) -> tuple[bytes, dict[str, Any]]:
    require((texture.width, texture.height, texture.format_code) == (4096, 4096, 0x5B), "high wheel texture contract differs")
    baseline = atlas_codec.decode_texture(texture)
    require(baseline is not None, "high wheel texture cannot decode")
    requested = bytearray(baseline)
    allowed: set[tuple[int, int]] = set()
    rows: list[dict[str, Any]] = []
    for item in wheel_v1.SPRITES:
        source_row, source_col = item["source"]
        target_row, target_col = item["target"]
        source_x, source_y = wheel_v1.cell_origin(wheel_v1.SWITCH_ORIGIN, wheel_v1.SWITCH_CELL, source_row, source_col)
        low_x, low_y = wheel_v1.cell_origin(wheel_v1.PC_ORIGIN, wheel_v1.PC_CELL, target_row, target_col)
        jp_cell = wheel_v1.crop_rgba(switch_jp, 2048, 1024, source_x, source_y, wheel_v1.SWITCH_CELL, wheel_v1.SWITCH_CELL)
        ko_cell = wheel_v1.crop_rgba(switch_ko, 2048, 1024, source_x, source_y, wheel_v1.SWITCH_CELL, wheel_v1.SWITCH_CELL)
        difference = wheel_v1.changed_bbox(jp_cell, ko_cell, wheel_v1.SWITCH_CELL, wheel_v1.SWITCH_CELL)
        require(
            wheel_v1.SOURCE_BAND[0] <= difference[0] <= difference[2] < wheel_v1.SOURCE_BAND[2]
            and wheel_v1.SOURCE_BAND[1] <= difference[1] <= difference[3] < wheel_v1.SOURCE_BAND[3],
            f"wheel source difference escaped text band: {item['label']} {item['state']}",
        )
        source = wheel_v1.crop_rgba(
            ko_cell,
            wheel_v1.SWITCH_CELL,
            wheel_v1.SWITCH_CELL,
            wheel_v1.SOURCE_BAND[0],
            wheel_v1.SOURCE_BAND[1],
            wheel_v1.SOURCE_BAND[2] - wheel_v1.SOURCE_BAND[0],
            wheel_v1.SOURCE_BAND[3] - wheel_v1.SOURCE_BAND[1],
        )
        low_rect = (
            low_x + wheel_v1.TARGET_BAND[0],
            low_y + wheel_v1.TARGET_BAND[1],
            low_x + wheel_v1.TARGET_BAND[2],
            low_y + wheel_v1.TARGET_BAND[3],
        )
        high_rect = tuple(value * 2 for value in low_rect)
        target_width, target_height = high_rect[2] - high_rect[0], high_rect[3] - high_rect[1]
        resized = title_v1.resize_rgba_lanczos3_premultiplied(
            source,
            wheel_v1.SOURCE_BAND[2] - wheel_v1.SOURCE_BAND[0],
            wheel_v1.SOURCE_BAND[3] - wheel_v1.SOURCE_BAND[1],
            target_width,
            target_height,
        )
        paste_rect(requested, texture.width, high_rect, resized)
        blocks = rect_blocks(high_rect, texture.width, texture.height)
        require(not allowed.intersection(blocks), "high wheel label bands overlap in BC3 space")
        allowed.update(blocks)
        rows.append({
            "label": item["label"],
            "state": item["state"],
            "switch_source_grid": [source_row, source_col],
            "high_target_rect": list(high_rect),
            "source_difference_bbox": list(difference),
        })
    payload, encoded = encode_selected_blocks(bytes(requested), texture.width, texture.height, texture.payload, allowed)
    blocks = sorted(allowed)
    return payload, {
        "method": "direct_switch_korean_text_band_to_native_4096_atlas",
        "source_labels": len(rows),
        "allowed_high_bc3_blocks": len(allowed),
        "changed_high_bc3_blocks": encoded,
        "changed_high_block_bbox": changed_block_bbox(blocks),
        "mappings": rows,
        "unselected_high_blocks_byte_preserved": True,
    }


def compose_military_high(
    texture: atlas_codec.Texture,
    switch_jp: bytes,
    switch_ko: bytes,
) -> tuple[bytes, dict[str, Any]]:
    require((texture.width, texture.height, texture.format_code) == (4096, 1024, 0x5B), "high military texture contract differs")
    baseline = atlas_codec.decode_texture(texture)
    require(baseline is not None, "high military texture cannot decode")
    requested = bytearray(baseline)
    allowed: set[tuple[int, int]] = set()
    rows: list[dict[str, Any]] = []
    for item in military_v1.SAFE_MAPPINGS:
        source_rect = tuple(item["source_rect"])
        low_rect = tuple(item["pc_target_rect"])
        high_rect = tuple(value * 2 for value in low_rect)
        source_width, source_height = military_v1.rect_dimensions(source_rect)
        target_width, target_height = high_rect[2] - high_rect[0], high_rect[3] - high_rect[1]
        korean = military_v1.crop_rgba(switch_ko, 2048, 256, source_rect)
        japanese = military_v1.crop_rgba(switch_jp, 2048, 256, source_rect)
        require(korean != japanese, f"military source has no Korean delta: {item['id']}")
        resized = title_v1.resize_rgba_lanczos3_premultiplied(korean, source_width, source_height, target_width, target_height)
        clear_rect(requested, texture.width, high_rect)
        paste_rect(requested, texture.width, high_rect, resized)
        blocks = rect_blocks(high_rect, texture.width, texture.height)
        require(not allowed.intersection(blocks), "high military targets overlap in BC3 space")
        allowed.update(blocks)
        rows.append({
            "id": item["id"],
            "label": item["label"],
            "switch_source_rect": list(source_rect),
            "high_target_rect": list(high_rect),
        })
    payload, encoded = encode_selected_blocks(bytes(requested), texture.width, texture.height, texture.payload, allowed)
    blocks = sorted(allowed)
    return payload, {
        "method": "direct_switch_korean_text_rect_to_native_4096x1024_atlas",
        "source_labels": len(rows),
        "allowed_high_bc3_blocks": len(allowed),
        "changed_high_bc3_blocks": encoded,
        "changed_high_block_bbox": changed_block_bbox(blocks),
        "mappings": rows,
        "unselected_high_blocks_byte_preserved": True,
    }


def compose_banner_high(
    texture: atlas_codec.Texture,
    texture_index: int,
    switch_jp: bytes,
    switch_ko: bytes,
) -> tuple[bytes, dict[str, Any]]:
    require((texture.width, texture.height, texture.format_code) == (4096, 512, 0x5B), f"high banner texture {texture_index} contract differs")
    baseline = atlas_codec.decode_texture(texture)
    require(baseline is not None, f"high banner texture {texture_index} cannot decode")
    difference = banner_v1.changed_bbox(switch_jp, switch_ko, banner_v1.SWITCH_WIDTH, banner_v1.SWITCH_HEIGHT)
    source_patch = banner_v1.expand_rect(difference, banner_v1.SOURCE_PADDING, banner_v1.SWITCH_WIDTH, banner_v1.SWITCH_HEIGHT)
    low_target = banner_v1.source_to_pc_rect(source_patch)
    high_target = tuple(value * 2 for value in low_target)
    source = banner_v1.crop_rgba(switch_ko, banner_v1.SWITCH_WIDTH, source_patch)
    target_width, target_height = high_target[2] - high_target[0], high_target[3] - high_target[1]
    resized = title_v1.resize_rgba_lanczos3_premultiplied(
        source,
        source_patch[2] - source_patch[0],
        source_patch[3] - source_patch[1],
        target_width,
        target_height,
    )
    requested = bytearray(baseline)
    paste_rect(requested, texture.width, high_target, resized)
    allowed = rect_blocks(high_target, texture.width, texture.height)
    payload, encoded = encode_selected_blocks(bytes(requested), texture.width, texture.height, texture.payload, allowed)
    blocks = sorted(allowed)
    return payload, {
        "method": "direct_switch_korean_banner_patch_to_native_4096x512_texture",
        "switch_difference_bbox": list(difference),
        "switch_source_patch": list(source_patch),
        "high_target_rect": list(high_target),
        "allowed_high_bc3_blocks": len(allowed),
        "changed_high_bc3_blocks": encoded,
        "changed_high_block_bbox": changed_block_bbox(blocks),
        "unselected_high_blocks_byte_preserved": True,
    }


def compose_tutorial_high(
    texture: atlas_codec.Texture,
    switch_jp: tutorial_v1.Atlas,
    switch_ko: tutorial_v1.Atlas,
) -> tuple[bytes, dict[str, Any]]:
    require((texture.width, texture.height, texture.format_code) == (4096, 4096, 0x5B), "high tutorial texture contract differs")
    baseline = atlas_codec.decode_texture(texture)
    require(baseline is not None, "high tutorial texture cannot decode")
    requested = bytearray(baseline)
    allowed: set[tuple[int, int]] = set()
    rows: list[dict[str, Any]] = []
    for original in tutorial_v1.PANEL_MAPPINGS:
        mapping = dict(original)
        mapping["pc_rect"] = tuple(value * 2 for value in original["pc_rect"])
        pc_rect = tuple(mapping["pc_rect"])
        source_jp, width, height = tutorial_v1.panel_scaled_rgba(switch_jp, mapping)
        source_ko, ko_width, ko_height = tutorial_v1.panel_scaled_rgba(switch_ko, mapping)
        require((ko_width, ko_height) == (width, height), "high tutorial source geometry differs")
        diff_blocks = tutorial_v1.changed_bc3_blocks(source_jp, source_ko, width, height)
        require(diff_blocks, f"high tutorial panel has no Korean delta: {mapping['name']}")
        panel_blocks: set[tuple[int, int]] = set()
        for local_x, local_y in diff_blocks:
            global_x = pc_rect[0] // 4 + local_x
            global_y = pc_rect[1] // 4 + local_y
            require((global_x, global_y) not in allowed, "high tutorial panel blocks overlap")
            tutorial_v1.overwrite_block(requested, texture.width, global_x, global_y, source_ko, width, local_x, local_y)
            panel_blocks.add((global_x, global_y))
        allowed.update(panel_blocks)
        rows.append({
            "name": mapping["name"],
            "labels": list(mapping["labels"]),
            "switch_rect": list(mapping["switch_rect"]),
            "high_target_rect": list(pc_rect),
            "source_changed_blocks": len(diff_blocks),
            "high_changed_block_bbox": tutorial_v1.block_bbox(panel_blocks),
        })
    payload, encoded = encode_selected_blocks(bytes(requested), texture.width, texture.height, texture.payload, allowed)
    blocks = sorted(allowed)
    return payload, {
        "method": "direct_switch_jp_to_ko_delta_blocks_in_native_4096_tutorial_panels",
        "source_panels": len(rows),
        "allowed_high_bc3_blocks": len(allowed),
        "changed_high_bc3_blocks": encoded,
        "changed_high_block_bbox": changed_block_bbox(blocks),
        "mappings": rows,
        "unselected_high_blocks_byte_preserved": True,
    }


def texture_crop(payload: bytes, width: int, height: int, block_bbox: Sequence[int]) -> tuple[bytes, int, int]:
    left, top, right, bottom = (int(value) for value in block_bbox)
    require(0 <= left < right <= width // 4 and 0 <= top < bottom <= height // 4, "crop block bbox is invalid")
    crop_width, crop_height = (right - left) * 4, (bottom - top) * 4
    output = bytearray(crop_width * crop_height * 4)
    blocks_wide = width // 4
    for by in range(top, bottom):
        for bx in range(left, right):
            offset = (by * blocks_wide + bx) * 16
            block = codec.decode_bc3_block(payload[offset : offset + 16])
            local_bx, local_by = bx - left, by - top
            for y in range(4):
                source = y * 16
                target = ((local_by * 4 + y) * crop_width + local_bx * 4) * 4
                output[target : target + 16] = block[source : source + 16]
    return bytes(output), crop_width, crop_height


def contact_pair(before: bytes, after: bytes, width: int, height: int) -> tuple[bytes, int, int]:
    require(len(before) == len(after) == width * height * 4, "contact pair dimensions differ")
    gap = 8
    output_width = width * 2 + gap
    output = bytearray(bytes((24, 24, 24, 255)) * (output_width * height))
    for y in range(height):
        source = y * width * 4
        first = (y * output_width) * 4
        second = (y * output_width + width + gap) * 4
        output[first : first + width * 4] = before[source : source + width * 4]
        output[second : second + width * 4] = after[source : source + width * 4]
    return bytes(output), output_width, height


def build_port1(
    *,
    low_stock: Path,
    low_korean: Path,
    port1: Path,
    switch_v20: Path,
    switch_v21: Path,
    switch_v22: Path,
    switch_v24: Path,
    output_root: Path,
) -> tuple[Path, dict[str, Any]]:
    low_stock_blob = low_stock.read_bytes()
    low_korean_blob = low_korean.read_bytes()
    port1_blob = port1.read_bytes()
    low_stock_outer = lz4.parse_link(low_stock_blob)
    low_korean_outer = lz4.parse_link(low_korean_blob)
    high_outer = lz4.parse_link(port1_blob)
    require(lz4.rebuild_link(low_stock_outer) == low_stock_blob, "low stock outer LINK identity failed")
    require(lz4.rebuild_link(low_korean_outer) == low_korean_blob, "low Korean outer LINK identity failed")
    require(lz4.rebuild_link(high_outer) == port1_blob, "PORT1 outer LINK identity failed")
    before_hashes = outer_hashes(high_outer)
    outer_replacements: dict[int, bytes] = {}
    target_rows: list[dict[str, Any]] = []
    qa_root = ensure_tmp(output_root / "visual_qa" / "port1", create=True)
    print("stage=port1_sources", flush=True)
    wheel_jp, wheel_jp_meta = wheel_v1.extract_switch_atlas(switch_v20, wheel_v1.SWITCH_V20, "Switch v2.0")
    wheel_ko, wheel_ko_meta = wheel_v1.extract_switch_atlas(switch_v24, wheel_v1.SWITCH_V24, "Switch v2.4")
    military_jp, military_jp_meta = military_v1.extract_switch_atlas(switch_v21, military_v1.SWITCH_V21, "Switch v2.1")
    military_ko, military_ko_meta = military_v1.extract_switch_atlas(switch_v22, military_v1.SWITCH_V22, "Switch v2.2")
    banner_jp, banner_jp_meta = banner_v1.extract_switch_textures(switch_v21, banner_v1.SWITCH_V21, "Switch v2.1")
    banner_ko, banner_ko_meta = banner_v1.extract_switch_textures(switch_v22, banner_v1.SWITCH_V22, "Switch v2.2")
    tutorial_jp_blob, tutorial_jp_meta = tutorial_v1.read_switch_resource("v21", switch_v21)
    tutorial_ko_blob, tutorial_ko_meta = tutorial_v1.read_switch_resource("v22", switch_v22)
    tutorial_jp = tutorial_v1.extract_atlas_from_outer(tutorial_jp_blob, expected_platform=16, label="Switch v2.1")
    tutorial_ko = tutorial_v1.extract_atlas_from_outer(tutorial_ko_blob, expected_platform=16, label="Switch v2.2")

    for mapping in PORT1_TARGETS:
        name = str(mapping["name"])
        low_outer_index = int(mapping["low_outer"])
        high_outer_index = int(mapping["high_outer"])
        resource_id = int(mapping["resource_id"])
        print(f"stage=port1 target={name}", flush=True)
        high_link = parse_nested_link(high_outer.entries[high_outer_index].data, expected_resource_id=resource_id)
        high_slot, high_header, high_raw, high_g1t = g1t_wrapper_entry(high_link)
        payload_replacements: dict[int, bytes] = {}
        texture_rows: list[dict[str, Any]] = []
        for texture_index in tuple(mapping["textures"]):
            high_texture = high_g1t.textures[texture_index]
            if name == "command_wheel":
                payload, row = compose_wheel_high(high_texture, wheel_jp, wheel_ko)
            elif name == "military_overlay":
                payload, row = compose_military_high(high_texture, military_jp, military_ko)
            elif name == "battle_banners":
                payload, row = compose_banner_high(high_texture, texture_index, banner_jp[texture_index], banner_ko[texture_index])
            elif name == "tutorial_diagram":
                payload, row = compose_tutorial_high(high_texture, tutorial_jp, tutorial_ko)
            else:  # pragma: no cover - PORT1_TARGETS is fixed above.
                raise HighresError(f"unsupported PORT1 target {name}")
            require(payload != high_texture.payload, f"{name} texture {texture_index} did not change")
            payload_replacements[texture_index] = payload
            bbox = row["changed_high_block_bbox"]
            require(isinstance(bbox, list), f"{name} has no QA bbox")
            before_crop, crop_width, crop_height = texture_crop(high_texture.payload, high_texture.width, high_texture.height, bbox)
            after_crop, _, _ = texture_crop(payload, high_texture.width, high_texture.height, bbox)
            contact, contact_width, contact_height = contact_pair(before_crop, after_crop, crop_width, crop_height)
            qa_path = qa_root / f"{name}_texture_{texture_index:03d}_before_after.png"
            atomic_write(
                qa_path,
                codec.encode_rgba_png(contact, contact_width, contact_height),
                forbidden=(low_stock, low_korean, port1, switch_v20, switch_v21, switch_v22, switch_v24),
            )
            row.update({
                "texture": texture_index,
                "high_before_bc3_sha256": sha256_bytes(high_texture.payload),
                "high_after_bc3_sha256": sha256_bytes(payload),
                "qa_contact": str(qa_path),
                "qa_contact_sha256": sha256_file(qa_path),
            })
            texture_rows.append(row)
        rebuilt_raw = replace_g1t_payloads(high_raw, high_g1t, payload_replacements)
        require(len(rebuilt_raw) == len(high_raw), f"{name} G1T size changed")
        for index, texture in enumerate(high_g1t.textures):
            if index not in payload_replacements:
                start = texture.payload_offset
                require(rebuilt_raw[start : start + len(texture.payload)] == texture.payload, f"{name} unselected texture {index} changed")
        wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, high_header)
        _, roundtrip = lz4.decompress_wrapper(wrapper)
        require(roundtrip == rebuilt_raw, f"{name} wrapper roundtrip failed")
        rebuilt_link = rebuild_nested_link(high_link, {high_slot: wrapper})
        reparsed_link = parse_nested_link(rebuilt_link, expected_resource_id=resource_id)
        for entry in high_link.entries:
            if entry.index != high_slot:
                require(reparsed_link.entries[entry.index].data == entry.data, f"{name} unrelated nested slot changed")
        outer_replacements[high_outer_index] = rebuilt_link
        target_rows.append({
            "name": name,
            "low_outer": low_outer_index,
            "high_outer": high_outer_index,
            "resource_id": resource_id,
            "nested_g1t_slot": high_slot,
            "texture_count": len(high_g1t.textures),
            "selected_textures": list(mapping["textures"]),
            "textures": texture_rows,
            "g1t_size_preserved": True,
            "unselected_g1t_bytes_preserved": True,
            "unrelated_nested_slots_preserved": True,
        })
        del high_raw, rebuilt_raw
        gc.collect()

    candidate_blob = lz4.rebuild_link(high_outer, outer_replacements)
    candidate_path = output_root / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port1.bin"
    atomic_write(
        candidate_path,
        candidate_blob,
        forbidden=(low_stock, low_korean, port1, switch_v20, switch_v21, switch_v22, switch_v24),
    )
    reparsed = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(reparsed) == candidate_blob, "PORT1 candidate outer identity failed")
    after_hashes = outer_hashes(reparsed)
    changed_outers = [index for index in range(len(reparsed.entries)) if before_hashes[str(index)] != after_hashes[str(index)]]
    require(changed_outers == list(PORT1_OUTERS), f"PORT1 changed outer scope differs: {changed_outers}")
    for index in range(len(reparsed.entries)):
        if index not in PORT1_OUTERS:
            require(reparsed.entries[index].data == high_outer.entries[index].data, f"PORT1 unrelated outer {index} changed")
    return candidate_path, {
        "candidate": {"path": str(candidate_path), **file_spec(candidate_path)},
        "changed_outer_entries": changed_outers,
        "targets": target_rows,
        "outer_before_sha256": before_hashes,
        "outer_after_sha256": after_hashes,
        "unrelated_outer_entries_byte_preserved": True,
        "switch_sources": {
            "wheel_v20": wheel_jp_meta,
            "wheel_v24": wheel_ko_meta,
            "military_v21": military_jp_meta,
            "military_v22": military_ko_meta,
            "banners_v21": banner_jp_meta,
            "banners_v22": banner_ko_meta,
            "tutorial_v21": tutorial_jp_meta,
            "tutorial_v22": tutorial_ko_meta,
        },
    }


def title_wrapper(
    *,
    entry_data: bytes,
    index: int,
    switch_png_root: Path,
    corrected_png_root: Path,
    switch_audit: Sequence[Mapping[str, Any]],
) -> tuple[bytes, dict[str, Any], bytes, bytes]:
    header, raw = lz4.decompress_wrapper(entry_data)
    g1t = atlas_codec.parse_g1t(raw)
    require(len(g1t.textures) == 1, f"PORT3 title {index} texture count differs")
    texture = g1t.textures[0]
    require(texture.format_code == 0x5B and (texture.width, texture.height) == (TITLE_WIDTH, TITLE_HEIGHT), f"PORT3 title {index} geometry differs")
    target_rgba = atlas_codec.decode_texture(texture)
    require(target_rgba is not None, f"PORT3 title {index} cannot decode")
    target_bbox = title_v1.alpha_bbox(target_rgba, TITLE_WIDTH, TITLE_HEIGHT)
    source_rgba, source_width, source_height, source_meta = title_v1.read_validated_source(
        index=index,
        switch_png_root=switch_png_root,
        corrected_png_root=corrected_png_root,
        switch_audit=switch_audit,
    )
    source_bbox = tuple(int(value) for value in source_meta["alpha_bbox"])
    cropped, cropped_width, cropped_height = title_v1.crop_rgba(source_rgba, source_width, source_height, source_bbox)
    target_height = target_bbox[3] - target_bbox[1] + 1
    scale = target_height / cropped_height
    scaled_width = max(1, int(cropped_width * scale + 0.5))
    scaled_height = target_height
    horizontal_room = TITLE_WIDTH - target_bbox[0]
    if scaled_width > horizontal_room:
        scale = horizontal_room / cropped_width
        scaled_width = horizontal_room
        scaled_height = max(1, int(cropped_height * scale + 0.5))
    resized = title_v1.resize_rgba_lanczos3_premultiplied(cropped, cropped_width, cropped_height, scaled_width, scaled_height)
    canvas, clipped = title_v1.paste_clipped(
        resized, scaled_width, scaled_height, TITLE_WIDTH, TITLE_HEIGHT, target_bbox[0], target_bbox[1]
    )
    require(clipped == 0, f"PORT3 title {index} clips Korean pixels")
    canvas_bbox = title_v1.alpha_bbox(canvas, TITLE_WIDTH, TITLE_HEIGHT)
    bc3, preserved, encoded = codec.encode_bc3(canvas, TITLE_WIDTH, TITLE_HEIGHT, template_bc3=texture.payload)
    rebuilt_raw = replace_g1t_payloads(raw, g1t, {0: bc3})
    wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, header)
    _, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == rebuilt_raw, f"PORT3 title {index} wrapper roundtrip failed")
    return wrapper, {
        "target_index": index,
        "source": source_meta,
        "stock_alpha_bbox": list(target_bbox),
        "candidate_alpha_bbox": list(canvas_bbox),
        "placement": {
            "mode": "native_port3_jp_bbox_height_scale_top_left",
            "canvas": [TITLE_WIDTH, TITLE_HEIGHT],
            "scaled_dimensions": [scaled_width, scaled_height],
            "offset": [target_bbox[0], target_bbox[1]],
            "scale": scale,
            "resampler": "premultiplied_alpha_lanczos3",
        },
        "bc3": {
            "total_blocks": len(bc3) // 16,
            "template_blocks_preserved": preserved,
            "blocks_encoded": encoded,
            "before_sha256": sha256_bytes(texture.payload),
            "after_sha256": sha256_bytes(bc3),
        },
        "wrapper_before_sha256": sha256_bytes(entry_data),
        "wrapper_after_sha256": sha256_bytes(wrapper),
    }, target_rgba, canvas


def build_port3(
    *,
    port3: Path,
    switch_png_root: Path,
    corrected_png_root: Path,
    switch_audit_path: Path,
    output_root: Path,
) -> tuple[Path, dict[str, Any]]:
    blob = port3.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, "PORT3 outer LINK identity failed")
    before_hashes = outer_hashes(outer)
    title_link = parse_nested_link(outer.entries[PORT3_OUTER].data)
    require(len(title_link.entries) == 110, f"PORT3 title slot count {len(title_link.entries)} != 110")
    # This archive repeats the 110-slot title count in the third nested-header
    # word.  It is not the outer index and must be retained verbatim.
    require(title_link.resource_id == 110, f"PORT3 title header word {title_link.resource_id} != 110")
    switch_audit = title_v1.load_switch_v13_audit(switch_audit_path)
    replacements: dict[int, bytes] = {}
    rows: list[dict[str, Any]] = []
    qa_indices = {0, 38, 74, 107}
    qa_root = ensure_tmp(output_root / "visual_qa" / "port3_titles", create=True)
    for index in TITLE_TARGETS:
        if index % 12 == 0:
            print(f"stage=port3_titles index={index}", flush=True)
        wrapper, row, before_rgba, after_rgba = title_wrapper(
            entry_data=title_link.entries[index].data,
            index=index,
            switch_png_root=switch_png_root,
            corrected_png_root=corrected_png_root,
            switch_audit=switch_audit,
        )
        require(wrapper != title_link.entries[index].data, f"PORT3 title {index} did not change")
        replacements[index] = wrapper
        if index in qa_indices:
            contact, width, height = contact_pair(before_rgba, after_rgba, TITLE_WIDTH, TITLE_HEIGHT)
            qa_path = qa_root / f"title_{index:03d}_before_after.png"
            atomic_write(qa_path, codec.encode_rgba_png(contact, width, height), forbidden=(port3, switch_audit_path))
            row["qa_contact"] = str(qa_path)
            row["qa_contact_sha256"] = sha256_file(qa_path)
        rows.append(row)
    tail_before = {str(index): sha256_bytes(title_link.entries[index].data) for index in TITLE_TAIL}
    rebuilt_link = rebuild_nested_link(title_link, replacements)
    reparsed_link = parse_nested_link(rebuilt_link)
    require(len(reparsed_link.entries) == 110, "PORT3 rebuilt title slot count changed")
    for index in TITLE_TARGETS:
        require(reparsed_link.entries[index].data == replacements[index], f"PORT3 title {index} replacement drifted")
    for index in TITLE_TAIL:
        require(reparsed_link.entries[index].data == title_link.entries[index].data, f"PORT3 tail title {index} changed")
    candidate_blob = lz4.rebuild_link(outer, {PORT3_OUTER: rebuilt_link})
    candidate_path = output_root / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port3.bin"
    atomic_write(candidate_path, candidate_blob, forbidden=(port3, switch_audit_path))
    reparsed = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(reparsed) == candidate_blob, "PORT3 candidate outer identity failed")
    after_hashes = outer_hashes(reparsed)
    changed_outers = [index for index in range(len(reparsed.entries)) if before_hashes[str(index)] != after_hashes[str(index)]]
    require(changed_outers == [PORT3_OUTER], f"PORT3 changed outer scope differs: {changed_outers}")
    for index in range(1, len(reparsed.entries)):
        require(reparsed.entries[index].data == outer.entries[index].data, f"PORT3 unrelated outer {index} changed")
    final_title_link = parse_nested_link(reparsed.entries[PORT3_OUTER].data)
    tail_after = {str(index): sha256_bytes(final_title_link.entries[index].data) for index in TITLE_TAIL}
    require(tail_before == tail_after, "PORT3 title tail hashes changed")
    return candidate_path, {
        "candidate": {"path": str(candidate_path), **file_spec(candidate_path)},
        "changed_outer_entries": changed_outers,
        "target_slots": list(TITLE_TARGETS),
        "target_slot_count": len(TITLE_TARGETS),
        "preserved_tail_slots": list(TITLE_TAIL),
        "tail_wrapper_sha256": tail_after,
        "entries": rows,
        "outer_before_sha256": before_hashes,
        "outer_after_sha256": after_hashes,
        "unrelated_outer_entries_byte_preserved": True,
        "tail_slots_byte_preserved": True,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "low_stock": args.low_stock.resolve(),
        "low_korean": args.low_korean.resolve(),
        "port1": args.port1.resolve(),
        "port3": args.port3.resolve(),
    }
    inputs = {name: require_spec(path, EXPECTED_INPUTS[name], name) for name, path in paths.items()}
    switch_png_root = args.switch_png_root.resolve()
    corrected_png_root = args.corrected_png_root.resolve()
    switch_audit = args.switch_audit.resolve()
    switch_archives = {
        "v20": args.switch_v20.resolve(),
        "v21": args.switch_v21.resolve(),
        "v22": args.switch_v22.resolve(),
        "v24": args.switch_v24.resolve(),
    }
    require(switch_png_root.is_dir(), f"missing Switch title source: {switch_png_root}")
    require(corrected_png_root.is_dir(), f"missing corrected title source: {corrected_png_root}")
    require(switch_audit.is_file(), f"missing Switch title audit: {switch_audit}")
    for version, path in switch_archives.items():
        require(path.is_file(), f"missing Switch {version} source archive: {path}")
    output_root = fresh_output(args.output_root)
    print("stage=port1_begin", flush=True)
    port1_path, port1_report = build_port1(
        low_stock=paths["low_stock"],
        low_korean=paths["low_korean"],
        port1=paths["port1"],
        switch_v20=switch_archives["v20"],
        switch_v21=switch_archives["v21"],
        switch_v22=switch_archives["v22"],
        switch_v24=switch_archives["v24"],
        output_root=output_root,
    )
    print("stage=port3_begin", flush=True)
    port3_path, port3_report = build_port3(
        port3=paths["port3"],
        switch_png_root=switch_png_root,
        corrected_png_root=corrected_png_root,
        switch_audit_path=switch_audit,
        output_root=output_root,
    )
    inputs_after = {name: file_spec(path) for name, path in paths.items()}
    require(inputs_after == inputs, "an input archive changed during the build")
    report = {
        "schema": SCHEMA,
        "file_only": True,
        "game_install_modified": False,
        "output_under_tmp": True,
        "inputs": {
            name: {"path": str(paths[name]), **inputs[name], "unchanged_after_build": inputs_after[name] == inputs[name]}
            for name in paths
        },
        "title_sources": {
            "switch_png_root": str(switch_png_root),
            "corrected_png_root": str(corrected_png_root),
            "switch_audit": {"path": str(switch_audit), **file_spec(switch_audit)},
        },
        "switch_archives": {
            version: {"path": str(path), **file_spec(path)} for version, path in switch_archives.items()
        },
        "algorithm": {
            "port1": "direct_pinned_switch_korean_source_composition_into_native_high_resolution_port_geometry",
            "port3": "render_pinned_korean_pngs_into_native_1024x256_stock_title_bboxes",
            "imagegen_role": "visual_style_reference_only_not_binary_source",
        },
        "port1": port1_report,
        "port3": port3_report,
        "candidates": {
            "RES_JP_PK_PORT/res_lang_pk_port1.bin": file_spec(port1_path),
            "RES_JP_PK_PORT/res_lang_pk_port3.bin": file_spec(port3_path),
        },
        "private_payload_policy": {
            "contains_complete_game_resources": True,
            "contains_third_party_translation_pixels": True,
            "git_publish_allowed": False,
        },
    }
    write_json(output_root / "build_report.json", report, forbidden=tuple(paths.values()))
    return report


def verify(args: argparse.Namespace) -> dict[str, Any]:
    output_root = ensure_tmp(args.output_root)
    report_path = ensure_tmp(output_root / "build_report.json")
    require(report_path.is_file(), f"missing build report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(isinstance(report, dict) and report.get("schema") == SCHEMA, "build report schema differs")
    port1_path = ensure_tmp(output_root / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port1.bin")
    port3_path = ensure_tmp(output_root / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port3.bin")
    require(file_spec(port1_path) == report["candidates"]["RES_JP_PK_PORT/res_lang_pk_port1.bin"], "PORT1 candidate spec differs")
    require(file_spec(port3_path) == report["candidates"]["RES_JP_PK_PORT/res_lang_pk_port3.bin"], "PORT3 candidate spec differs")

    base1_path = Path(report["inputs"]["port1"]["path"])
    base3_path = Path(report["inputs"]["port3"]["path"])
    require_spec(base1_path, EXPECTED_INPUTS["port1"], "PORT1 verify baseline")
    require_spec(base3_path, EXPECTED_INPUTS["port3"], "PORT3 verify baseline")
    base1 = lz4.parse_link(base1_path.read_bytes())
    candidate1 = lz4.parse_link(port1_path.read_bytes())
    changed1 = [index for index in range(len(base1.entries)) if base1.entries[index].data != candidate1.entries[index].data]
    require(changed1 == list(PORT1_OUTERS), f"verified PORT1 scope differs: {changed1}")
    for mapping in PORT1_TARGETS:
        link = parse_nested_link(candidate1.entries[int(mapping["high_outer"])].data, expected_resource_id=int(mapping["resource_id"]))
        _, _, _, g1t = g1t_wrapper_entry(link)
        for texture_index in tuple(mapping["textures"]):
            texture = g1t.textures[texture_index]
            require(texture.format_code == 0x5B, "verified PORT1 target is not BC3")

    base3 = lz4.parse_link(base3_path.read_bytes())
    candidate3 = lz4.parse_link(port3_path.read_bytes())
    changed3 = [index for index in range(len(base3.entries)) if base3.entries[index].data != candidate3.entries[index].data]
    require(changed3 == [PORT3_OUTER], f"verified PORT3 scope differs: {changed3}")
    base_titles = parse_nested_link(base3.entries[PORT3_OUTER].data)
    candidate_titles = parse_nested_link(candidate3.entries[PORT3_OUTER].data)
    require(len(candidate_titles.entries) == 110, "verified PORT3 title count differs")
    for index in TITLE_TARGETS:
        require(candidate_titles.entries[index].data != base_titles.entries[index].data, f"verified PORT3 title {index} unchanged")
        _, raw = lz4.decompress_wrapper(candidate_titles.entries[index].data)
        g1t = atlas_codec.parse_g1t(raw)
        require(len(g1t.textures) == 1 and (g1t.textures[0].width, g1t.textures[0].height) == (TITLE_WIDTH, TITLE_HEIGHT), f"verified PORT3 title {index} geometry differs")
    for index in TITLE_TAIL:
        require(candidate_titles.entries[index].data == base_titles.entries[index].data, f"verified PORT3 title tail {index} changed")
    return {
        "port1": file_spec(port1_path),
        "port1_changed_outers": changed1,
        "port3": file_spec(port3_path),
        "port3_changed_outers": changed3,
        "port3_target_titles": len(TITLE_TARGETS),
        "port3_tail_titles_preserved": True,
        "verify": "PASS",
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--low-stock", type=Path, required=True)
    build_parser.add_argument("--low-korean", type=Path, required=True)
    build_parser.add_argument("--port1", type=Path, required=True)
    build_parser.add_argument("--port3", type=Path, required=True)
    build_parser.add_argument("--switch-v20", type=Path, required=True)
    build_parser.add_argument("--switch-v21", type=Path, required=True)
    build_parser.add_argument("--switch-v22", type=Path, required=True)
    build_parser.add_argument("--switch-v24", type=Path, required=True)
    build_parser.add_argument("--switch-png-root", type=Path, required=True)
    build_parser.add_argument("--corrected-png-root", type=Path, required=True)
    build_parser.add_argument("--switch-audit", type=Path, required=True)
    build_parser.add_argument("--output-root", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--output-root", type=Path, required=True)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "build":
        result = build(args)
        print(f"port1={result['port1']['candidate']['path']}")
        print(f"port1_sha256={result['port1']['candidate']['sha256']}")
        print(f"port3={result['port3']['candidate']['path']}")
        print(f"port3_sha256={result['port3']['candidate']['sha256']}")
        print("game_install_modified=False")
        return 0
    result = verify(args)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HighresError, lz4.LZ4Error, lz4.LinkError, atlas_codec.AtlasError, codec.CodecError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
