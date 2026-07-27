#!/usr/bin/env python3
"""Build tmp-only native-coordinate merit-badge repair candidates.

The high candidate repositions only three Korean merit badges already present
in the current 4096x1024 PORT1 atlas.  Each repaired high badge is then
independently downsampled 2:1 and placed at the corresponding native position
in the pre-whole-atlas-downsample 2048x512 layout.  No Steam, release, or Git
state is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
MILITARY_WORKSTREAM = REPO / "workstreams" / "steam_jp_military_overlay_v1"
for candidate in (TOOLS, MILITARY_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as codec  # noqa: E402
import build_steam_jp_military_overlay_v1 as military  # noqa: E402


SCHEMA = "nobu16.kr.battle-merit-badges-native-repair.v1"
HIGH_OUTER = 17
LOW_OUTER = 12
RESOURCE_ID = 58
NESTED_SLOT = 0
TEXTURE_INDEX = 0
HIGH_GEOMETRY = (4096, 1024)
LOW_GEOMETRY = (2048, 512)
FORMAT_CODE = 0x5B
LOW_LAYOUT_PAYLOAD_SHA256 = "0E76BA383BF4AC6D50F47F0F5B9571AF9CEB2A872063095749F4A296D3D51FD6"

EXPECTED_INPUTS: Mapping[str, Mapping[str, Any]] = {
    "current_low": {
        "size": 154714237,
        "sha256": "952B97FAE48F5D077E4663EFBE7B2975ADDBC0A521E63F9EDE373D7A77D55600",
    },
    "current_high": {
        "size": 82905500,
        "sha256": "E2B22DFD399E87DF109947F0F98FC58D1BF360B1B54299A6BB4D2051CE53EEA5",
    },
    "stock_high": {
        "size": 79243911,
        "sha256": "00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7",
    },
    "low_layout": {
        "size": 160710999,
        "sha256": "49A78DAD3E796137550A1AE268018E5D54564B47AF0D72844284B266F06ED36D",
    },
}

BADGES: tuple[Mapping[str, Any], ...] = (
    {
        "id": "merit_rank_1",
        "label": "전공 1위",
        "high_source_rect": (2984, 383, 3364, 459),
        "high_target_rect": (2960, 400, 3344, 480),
        "low_target_rect": (1082, 254, 1274, 294),
        "high_search_rect": (2940, 360, 3380, 490),
        "low_search_rect": (1060, 245, 1285, 300),
    },
    {
        "id": "merit_rank_2",
        "label": "전공 2위",
        "high_source_rect": (3002, 485, 3346, 549),
        "high_target_rect": (2982, 500, 3322, 572),
        "low_target_rect": (1297, 256, 1467, 292),
        "high_search_rect": (2960, 475, 3360, 585),
        "low_search_rect": (1280, 245, 1480, 300),
    },
    {
        "id": "merit_rank_3",
        "label": "전공 3위",
        "high_source_rect": (3693, 625, 4029, 688),
        "high_target_rect": (3686, 644, 4026, 716),
        "low_target_rect": (1501, 256, 1671, 292),
        "high_search_rect": (3670, 615, 4040, 725),
        "low_search_rect": (1490, 245, 1685, 300),
    },
)


class RepairError(ValueError):
    """Raised when the narrow merit-badge repair contract is violated."""


@dataclass(frozen=True)
class Route:
    path: Path
    blob: bytes
    outer_index: int
    outer: lz4.LinkArchive
    inner: military.InnerLink
    wrapper: lz4.WrapperHeader
    raw: bytes
    g1t: atlas_codec.G1T
    texture: atlas_codec.Texture
    rgba: bytes


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RepairError(message)


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


def require_spec(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = file_spec(path)
    require(actual == dict(expected), f"{label} pin mismatch: expected={dict(expected)} actual={actual}")
    return actual


def rect_dimensions(rect: Sequence[int]) -> tuple[int, int]:
    left, top, right, bottom = (int(value) for value in rect)
    require(left < right and top < bottom, f"invalid rectangle: {tuple(rect)}")
    return right - left, bottom - top


def rect_union(left: Sequence[int], right: Sequence[int]) -> tuple[int, int, int, int]:
    return (
        min(int(left[0]), int(right[0])),
        min(int(left[1]), int(right[1])),
        max(int(left[2]), int(right[2])),
        max(int(left[3]), int(right[3])),
    )


def rectangles_overlap(left: Sequence[int], right: Sequence[int]) -> bool:
    return not (
        int(left[2]) <= int(right[0])
        or int(right[2]) <= int(left[0])
        or int(left[3]) <= int(right[1])
        or int(right[3]) <= int(left[1])
    )


def rect_contains(outer: Sequence[int], inner: Sequence[int]) -> bool:
    return (
        int(outer[0]) <= int(inner[0])
        and int(outer[1]) <= int(inner[1])
        and int(inner[2]) <= int(outer[2])
        and int(inner[3]) <= int(outer[3])
    )


def rect_blocks(rect: Sequence[int], width: int, height: int) -> set[tuple[int, int]]:
    left, top, right, bottom = (int(value) for value in rect)
    require(0 <= left < right <= width and 0 <= top < bottom <= height, f"rectangle escapes {width}x{height}: {tuple(rect)}")
    return {
        (block_x, block_y)
        for block_y in range(top // 4, (bottom + 3) // 4)
        for block_x in range(left // 4, (right + 3) // 4)
    }


def changed_blocks(before: bytes, after: bytes, width: int, height: int) -> set[tuple[int, int]]:
    require(len(before) == len(after) == width * height, "BC3 payload geometry differs")
    blocks_wide = width // 4
    output: set[tuple[int, int]] = set()
    for index in range(len(before) // 16):
        start = index * 16
        if before[start : start + 16] != after[start : start + 16]:
            output.add((index % blocks_wide, index // blocks_wide))
    return output


def changed_block_bbox(blocks: Iterable[tuple[int, int]]) -> list[int] | None:
    values = list(blocks)
    if not values:
        return None
    xs = [value[0] for value in values]
    ys = [value[1] for value in values]
    return [min(xs), min(ys), max(xs) + 1, max(ys) + 1]


def encode_selected_blocks(
    requested: bytes,
    width: int,
    height: int,
    template: bytes,
    allowed: set[tuple[int, int]],
) -> tuple[bytes, int]:
    require(len(requested) == width * height * 4, "requested RGBA geometry differs")
    require(len(template) == width * height, "template BC3 geometry differs")
    blocks_wide = width // 4
    output = bytearray(template)
    encoded = 0
    for block_x, block_y in sorted(allowed):
        require(0 <= block_x < blocks_wide and 0 <= block_y < height // 4, "allowed block escapes texture")
        index = block_y * blocks_wide + block_x
        start = index * 16
        original = template[start : start + 16]
        rgba = codec.extract_rgba_block(requested, width, height, block_x, block_y)
        if codec.decode_bc3_block(original) == rgba:
            continue
        output[start : start + 16] = codec.encode_bc3_block(rgba)
        encoded += 1
    require(encoded > 0, "selected-block encoder produced no change")
    return bytes(output), encoded


def component_bboxes(
    rgba: bytes,
    width: int,
    height: int,
    search_rect: Sequence[int],
    *,
    threshold: int = 32,
    minimum_pixels: int = 20,
) -> list[tuple[int, int, int, int]]:
    left, top, right, bottom = (int(value) for value in search_rect)
    require(0 <= left < right <= width and 0 <= top < bottom <= height, "component search escapes canvas")
    active = {
        (x, y)
        for y in range(top, bottom)
        for x in range(left, right)
        if rgba[(y * width + x) * 4 + 3] >= threshold
    }
    output: list[tuple[int, int, int, int]] = []
    while active:
        start = active.pop()
        queue: deque[tuple[int, int]] = deque((start,))
        points = [start]
        while queue:
            x, y = queue.popleft()
            for candidate_y in range(max(top, y - 1), min(bottom, y + 2)):
                for candidate_x in range(max(left, x - 1), min(right, x + 2)):
                    candidate = (candidate_x, candidate_y)
                    if candidate in active:
                        active.remove(candidate)
                        queue.append(candidate)
                        points.append(candidate)
        if len(points) >= minimum_pixels:
            output.append(
                (
                    min(point[0] for point in points),
                    min(point[1] for point in points),
                    max(point[0] for point in points) + 1,
                    max(point[1] for point in points) + 1,
                )
            )
    return sorted(output, key=lambda rect: (rect[1], rect[0], rect[3], rect[2]))


def alpha_bbox(rgba: bytes, width: int, height: int, *, threshold: int = 32) -> tuple[int, int, int, int] | None:
    require(len(rgba) == width * height * 4, "alpha bbox RGBA geometry differs")
    xs: list[int] = []
    ys: list[int] = []
    for y in range(height):
        for x in range(width):
            if rgba[(y * width + x) * 4 + 3] >= threshold:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def alpha_pixels_outside(
    rgba: bytes,
    width: int,
    height: int,
    outer_rect: Sequence[int],
    allowed_rect: Sequence[int],
    *,
    threshold: int = 32,
) -> int:
    require(len(rgba) == width * height * 4, "alpha outside RGBA geometry differs")
    left, top, right, bottom = (int(value) for value in outer_rect)
    allowed_left, allowed_top, allowed_right, allowed_bottom = (int(value) for value in allowed_rect)
    count = 0
    for y in range(top, bottom):
        for x in range(left, right):
            if allowed_left <= x < allowed_right and allowed_top <= y < allowed_bottom:
                continue
            if rgba[(y * width + x) * 4 + 3] >= threshold:
                count += 1
    return count


def validate_mapping_contract() -> None:
    require(len(BADGES) == 3, "expected exactly three merit badges")
    ids = [str(row["id"]) for row in BADGES]
    require(len(ids) == len(set(ids)), "badge ids are not unique")
    high_unions: list[tuple[int, int, int, int]] = []
    low_targets: list[tuple[int, int, int, int]] = []
    for row in BADGES:
        source = tuple(row["high_source_rect"])
        high = tuple(row["high_target_rect"])
        low = tuple(row["low_target_rect"])
        source_width, source_height = rect_dimensions(source)
        high_width, high_height = rect_dimensions(high)
        low_width, low_height = rect_dimensions(low)
        require(source_width > 0 and source_height > 0, f"empty high source: {row['id']}")
        require((high_width, high_height) == (low_width * 2, low_height * 2), f"target scale is not 2:1: {row['id']}")
        require(0 <= source[0] < source[2] <= HIGH_GEOMETRY[0] and 0 <= source[1] < source[3] <= HIGH_GEOMETRY[1], f"high source escapes: {row['id']}")
        require(0 <= high[0] < high[2] <= HIGH_GEOMETRY[0] and 0 <= high[1] < high[3] <= HIGH_GEOMETRY[1], f"high target escapes: {row['id']}")
        require(0 <= low[0] < low[2] <= LOW_GEOMETRY[0] and 0 <= low[1] < low[3] <= LOW_GEOMETRY[1], f"low target escapes: {row['id']}")
        high_unions.append(rect_union(source, high))
        low_targets.append(low)
    for index, left in enumerate(high_unions):
        for right in high_unions[index + 1 :]:
            require(not rectangles_overlap(left, right), "high badge repair unions overlap")
    for index, left in enumerate(low_targets):
        for right in low_targets[index + 1 :]:
            require(not rectangles_overlap(left, right), "low badge targets overlap")


def parse_route(path: Path, outer_index: int, geometry: tuple[int, int], label: str) -> Route:
    path = path.resolve()
    require(path.is_file(), f"missing {label}: {path}")
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"{label}: outer LINK identity failed")
    require(0 <= outer_index < len(outer.entries), f"{label}: missing outer /{outer_index}")
    inner = military.parse_inner_link(outer.entries[outer_index].data, f"{label} /{outer_index}")
    require(inner.resource_id == RESOURCE_ID and len(inner.entries) == 1, f"{label}: nested resource contract differs")
    wrapper, raw = lz4.decompress_wrapper(inner.entries[NESTED_SLOT].data)
    g1t = atlas_codec.parse_g1t(raw)
    require(g1t.platform == 0x0A and len(g1t.textures) == 1, f"{label}: G1T topology differs")
    texture = g1t.textures[TEXTURE_INDEX]
    require(
        (texture.width, texture.height, texture.format_code, texture.mip_count)
        == (geometry[0], geometry[1], FORMAT_CODE, 1),
        f"{label}: texture contract differs",
    )
    rgba = atlas_codec.decode_texture(texture)
    require(rgba is not None and len(rgba) == geometry[0] * geometry[1] * 4, f"{label}: texture decode failed")
    return Route(path, blob, outer_index, outer, inner, wrapper, raw, g1t, texture, rgba)


def replace_route_payload(route: Route, payload: bytes) -> bytes:
    texture = route.texture
    require(len(payload) == len(texture.payload), "replacement payload size differs")
    rebuilt_raw = route.raw[: texture.payload_offset] + payload + route.raw[texture.payload_offset + len(texture.payload) :]
    require(len(rebuilt_raw) == len(route.raw), "rebuilt G1T size changed")
    reparsed_g1t = atlas_codec.parse_g1t(rebuilt_raw)
    require(
        rebuilt_raw[: texture.payload_offset] == route.raw[: texture.payload_offset]
        and rebuilt_raw[texture.payload_offset + len(texture.payload) :]
        == route.raw[texture.payload_offset + len(texture.payload) :],
        "G1T non-payload bytes changed",
    )
    require(
        (reparsed_g1t.platform, len(reparsed_g1t.textures))
        == (route.g1t.platform, len(route.g1t.textures)),
        "rebuilt G1T topology changed",
    )
    rebuilt_wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, route.wrapper)
    roundtrip_header, roundtrip_raw = lz4.decompress_wrapper(rebuilt_wrapper)
    require(roundtrip_raw == rebuilt_raw, "rebuilt wrapper round-trip failed")
    require(roundtrip_header.prefix == route.wrapper.prefix, "wrapper prefix changed")
    rebuilt_inner = military.rebuild_inner_link(route.inner, {NESTED_SLOT: rebuilt_wrapper})
    reparsed_inner = military.parse_inner_link(rebuilt_inner, f"rebuilt outer /{route.outer_index}")
    require(reparsed_inner.resource_id == RESOURCE_ID, "rebuilt nested resource id changed")
    require(reparsed_inner.entries[NESTED_SLOT].data == rebuilt_wrapper, "rebuilt nested wrapper differs")
    candidate = lz4.rebuild_link(route.outer, {route.outer_index: rebuilt_inner})
    reparsed_outer = lz4.parse_link(candidate)
    require(lz4.rebuild_link(reparsed_outer) == candidate, "rebuilt outer LINK identity failed")
    for entry in route.outer.entries:
        if entry.index != route.outer_index:
            require(reparsed_outer.entries[entry.index].data == entry.data, f"unrelated outer /{entry.index} changed")
    return candidate


def outer_hashes(archive: lz4.LinkArchive) -> dict[str, str]:
    return {str(entry.index): sha256_bytes(entry.data) for entry in archive.entries}


def crop_rgba(rgba: bytes, width: int, height: int, rect: Sequence[int]) -> bytes:
    return military.crop_rgba(rgba, width, height, tuple(int(value) for value in rect))


def clear_rect(rgba: bytearray, width: int, height: int, rect: Sequence[int]) -> None:
    military.clear_rect_rgba(rgba, width, height, tuple(int(value) for value in rect))


def paste_rect(rgba: bytearray, width: int, rect: Sequence[int], source: bytes) -> None:
    target = tuple(int(value) for value in rect)
    target_width, target_height = rect_dimensions(target)
    military.paste_rgba(rgba, width, target[0], target[1], source, target_width, target_height)


def resize_rgba(source: bytes, source_width: int, source_height: int, target_width: int, target_height: int) -> bytes:
    return military.resize_rgba_lanczos3_premultiplied(source, source_width, source_height, target_width, target_height)


def write_png(
    path: Path,
    rgba: bytes,
    width: int,
    height: int,
    *,
    forbidden: Iterable[Path],
) -> dict[str, Any]:
    png = codec.encode_rgba_png(rgba, width, height)
    military.atomic_write(path, png, forbidden=forbidden)
    return {"path": str(path), "size": len(png), "sha256": sha256_bytes(png), "dimensions": [width, height]}


def add_border(rgba: bytearray, width: int, height: int, color: tuple[int, int, int, int]) -> None:
    pixel = bytes(color)
    for x in range(width):
        rgba[x * 4 : x * 4 + 4] = pixel
        bottom = ((height - 1) * width + x) * 4
        rgba[bottom : bottom + 4] = pixel
    for y in range(height):
        left = y * width * 4
        right = (y * width + width - 1) * 4
        rgba[left : left + 4] = pixel
        rgba[right : right + 4] = pixel


def build_contact_sheet(
    rows: Sequence[Mapping[str, Any]],
    output_root: Path,
    *,
    forbidden: Iterable[Path],
) -> dict[str, Any]:
    gutter = 8
    panel_count = 4
    max_width = max(rect_dimensions(row["high_target_rect"])[0] for row in rows)
    max_height = max(rect_dimensions(row["high_target_rect"])[1] for row in rows)
    canvas_width = gutter + panel_count * (max_width + gutter)
    canvas_height = gutter + len(rows) * (max_height + gutter)
    canvas = bytearray(canvas_width * canvas_height * 4)
    colors = (
        (232, 72, 72, 255),
        (72, 216, 112, 255),
        (232, 200, 64, 255),
        (64, 208, 232, 255),
    )
    report_rows: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows):
        target_width, target_height = rect_dimensions(row["high_target_rect"])
        panels = (
            row["high_current_uv_crop"],
            row["high_candidate_crop"],
            row["low_layout_crop_upscaled"],
            row["low_candidate_crop_upscaled"],
        )
        y = gutter + row_index * (max_height + gutter)
        for panel_index, (panel, color) in enumerate(zip(panels, colors)):
            marked = bytearray(panel)
            add_border(marked, target_width, target_height, color)
            x = gutter + panel_index * (max_width + gutter)
            military.paste_rgba(canvas, canvas_width, x, y, bytes(marked), target_width, target_height)
        report_rows.append(
            {
                "id": row["id"],
                "label": row["label"],
                "panels_left_to_right": [
                    "current_high_native_uv_crop",
                    "repaired_high_native_uv_crop",
                    "low_layout_native_crop_upscaled_2x",
                    "repaired_low_native_crop_upscaled_2x",
                ],
                "panel_dimensions": [target_width, target_height],
            }
        )
    path = output_root / "private" / "merit_badges_contact_sheet.png"
    record = write_png(path, bytes(canvas), canvas_width, canvas_height, forbidden=forbidden)
    record["rows"] = report_rows
    record["legend"] = {
        "red": "current high sampled at native UV",
        "green": "repaired high",
        "yellow": "pre-whole-downsample low layout",
        "cyan": "repaired low",
    }
    return record


def build(args: argparse.Namespace) -> dict[str, Any]:
    validate_mapping_contract()
    current_low_path = args.current_low.resolve()
    current_high_path = args.current_high.resolve()
    stock_high_path = args.stock_high.resolve()
    low_layout_path = args.low_layout.resolve()
    inputs = {
        "current_low": require_spec(current_low_path, EXPECTED_INPUTS["current_low"], "current low integration"),
        "current_high": require_spec(current_high_path, EXPECTED_INPUTS["current_high"], "current high integration"),
        "stock_high": require_spec(stock_high_path, EXPECTED_INPUTS["stock_high"], "stock high geometry reference"),
        "low_layout": require_spec(low_layout_path, EXPECTED_INPUTS["low_layout"], "pre-whole-downsample low layout"),
    }
    forbidden = (current_low_path, current_high_path, stock_high_path, low_layout_path)
    output_root = military.create_fresh_output_root(args.output_root.resolve())

    print("stage=parse_inputs", flush=True)
    current_high = parse_route(current_high_path, HIGH_OUTER, HIGH_GEOMETRY, "current high")
    stock_high = parse_route(stock_high_path, HIGH_OUTER, HIGH_GEOMETRY, "stock high")
    current_low = parse_route(current_low_path, LOW_OUTER, LOW_GEOMETRY, "current low")
    low_layout = parse_route(low_layout_path, LOW_OUTER, LOW_GEOMETRY, "low layout")
    require(sha256_bytes(low_layout.texture.payload) == LOW_LAYOUT_PAYLOAD_SHA256, "low layout /12 payload pin mismatch")
    require(
        current_low.raw[: current_low.texture.payload_offset] == low_layout.raw[: low_layout.texture.payload_offset]
        and current_low.raw[current_low.texture.payload_offset + len(current_low.texture.payload) :]
        == low_layout.raw[low_layout.texture.payload_offset + len(low_layout.texture.payload) :],
        "current and layout low G1T non-payload bytes differ",
    )

    print("stage=validate_components", flush=True)
    for row in BADGES:
        current_components = component_bboxes(
            current_high.rgba,
            *HIGH_GEOMETRY,
            row["high_search_rect"],
        )
        stock_components = component_bboxes(
            stock_high.rgba,
            *HIGH_GEOMETRY,
            row["high_search_rect"],
        )
        low_components = component_bboxes(
            low_layout.rgba,
            *LOW_GEOMETRY,
            row["low_search_rect"],
        )
        require(tuple(row["high_source_rect"]) in current_components, f"current high source component not found: {row['id']}")
        require(tuple(row["high_target_rect"]) in stock_components, f"stock high target component not found: {row['id']}")
        require(
            low_components
            and rect_contains(
                row["low_target_rect"],
                max(
                    low_components,
                    key=lambda rect: (rect[2] - rect[0]) * (rect[3] - rect[1]),
                ),
            ),
            f"low native badge component escaped its target: {row['id']}",
        )

    print("stage=compose_high", flush=True)
    high_requested = bytearray(current_high.rgba)
    high_allowed: set[tuple[int, int]] = set()
    repaired_high_patches: dict[str, bytes] = {}
    badge_rows: list[dict[str, Any]] = []
    for row in BADGES:
        source_rect = tuple(row["high_source_rect"])
        high_target = tuple(row["high_target_rect"])
        low_target = tuple(row["low_target_rect"])
        union = rect_union(source_rect, high_target)
        source_width, source_height = rect_dimensions(source_rect)
        high_width, high_height = rect_dimensions(high_target)
        low_width, low_height = rect_dimensions(low_target)
        source = crop_rgba(current_high.rgba, *HIGH_GEOMETRY, source_rect)
        require(alpha_bbox(source, source_width, source_height) == (0, 0, source_width, source_height), f"source bbox is not exact: {row['id']}")
        repaired_high = resize_rgba(source, source_width, source_height, high_width, high_height)
        require(alpha_bbox(repaired_high, high_width, high_height) == (0, 0, high_width, high_height), f"repaired high bbox is not exact: {row['id']}")
        clear_rect(high_requested, *HIGH_GEOMETRY, union)
        paste_rect(high_requested, HIGH_GEOMETRY[0], high_target, repaired_high)
        blocks = rect_blocks(union, *HIGH_GEOMETRY)
        require(not high_allowed.intersection(blocks), f"high badge block sets overlap: {row['id']}")
        high_allowed.update(blocks)
        repaired_high_patches[str(row["id"])] = repaired_high
        badge_rows.append(
            {
                "id": row["id"],
                "label": row["label"],
                "high_source_rect": list(source_rect),
                "high_target_rect": list(high_target),
                "high_clear_union_rect": list(union),
                "low_target_rect": list(low_target),
                "source_dimensions": [source_width, source_height],
                "repaired_high_dimensions": [high_width, high_height],
                "repaired_low_dimensions": [low_width, low_height],
                "source_rgba_sha256": sha256_bytes(source),
                "repaired_high_rgba_sha256": sha256_bytes(repaired_high),
            }
        )
    high_payload, high_encoded = encode_selected_blocks(
        bytes(high_requested),
        *HIGH_GEOMETRY,
        current_high.texture.payload,
        high_allowed,
    )
    high_changed = changed_blocks(current_high.texture.payload, high_payload, *HIGH_GEOMETRY)
    require(high_changed and high_changed <= high_allowed, "high payload changed outside allowed badge blocks")
    high_candidate_blob = replace_route_payload(current_high, high_payload)
    high_candidate_path = output_root / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port1.bin"
    military.atomic_write(high_candidate_path, high_candidate_blob, forbidden=forbidden)
    high_candidate = parse_route(high_candidate_path, HIGH_OUTER, HIGH_GEOMETRY, "high candidate")

    for row in BADGES:
        union = rect_union(row["high_source_rect"], row["high_target_rect"])
        require(
            alpha_pixels_outside(high_candidate.rgba, *HIGH_GEOMETRY, union, row["high_target_rect"]) == 0,
            f"high candidate retains alpha outside target: {row['id']}",
        )
        target_width, target_height = rect_dimensions(row["high_target_rect"])
        target_crop = crop_rgba(high_candidate.rgba, *HIGH_GEOMETRY, row["high_target_rect"])
        candidate_bbox = alpha_bbox(target_crop, target_width, target_height)
        require(candidate_bbox is not None, f"high candidate target is empty: {row['id']}")
        require(
            candidate_bbox[2] - candidate_bbox[0] >= target_width - 4
            and candidate_bbox[3] - candidate_bbox[1] >= target_height - 4,
            f"high candidate target bbox shrank excessively: {row['id']} {candidate_bbox}",
        )
        matching_row = next(item for item in badge_rows if item["id"] == row["id"])
        matching_row["high_candidate_alpha_bbox"] = [
            candidate_bbox[0] + int(row["high_target_rect"][0]),
            candidate_bbox[1] + int(row["high_target_rect"][1]),
            candidate_bbox[2] + int(row["high_target_rect"][0]),
            candidate_bbox[3] + int(row["high_target_rect"][1]),
        ]

    print("stage=compose_low", flush=True)
    low_requested = bytearray(low_layout.rgba)
    low_allowed: set[tuple[int, int]] = set()
    repaired_low_patches: dict[str, bytes] = {}
    for badge_row, mapping in zip(badge_rows, BADGES):
        high_patch = repaired_high_patches[str(mapping["id"])]
        high_width, high_height = rect_dimensions(mapping["high_target_rect"])
        low_width, low_height = rect_dimensions(mapping["low_target_rect"])
        low_patch = resize_rgba(high_patch, high_width, high_height, low_width, low_height)
        require(alpha_bbox(low_patch, low_width, low_height) == (0, 0, low_width, low_height), f"repaired low bbox is not exact: {mapping['id']}")
        clear_rect(low_requested, *LOW_GEOMETRY, mapping["low_target_rect"])
        paste_rect(low_requested, LOW_GEOMETRY[0], mapping["low_target_rect"], low_patch)
        blocks = rect_blocks(mapping["low_target_rect"], *LOW_GEOMETRY)
        require(not low_allowed.intersection(blocks), f"low badge block sets overlap: {mapping['id']}")
        low_allowed.update(blocks)
        repaired_low_patches[str(mapping["id"])] = low_patch
        badge_row["repaired_low_rgba_sha256"] = sha256_bytes(low_patch)
        badge_row["resampler"] = "deterministic premultiplied-alpha Lanczos3; repaired high sprite to exact 1/2 dimensions"
    low_payload, low_encoded = encode_selected_blocks(
        bytes(low_requested),
        *LOW_GEOMETRY,
        low_layout.texture.payload,
        low_allowed,
    )
    low_changed_from_layout = changed_blocks(low_layout.texture.payload, low_payload, *LOW_GEOMETRY)
    require(low_changed_from_layout and low_changed_from_layout <= low_allowed, "low payload changed outside allowed badge blocks")
    low_candidate_blob = replace_route_payload(current_low, low_payload)
    low_candidate_path = output_root / "candidate" / "RES_JP" / "res_lang.bin"
    military.atomic_write(low_candidate_path, low_candidate_blob, forbidden=forbidden)
    low_candidate = parse_route(low_candidate_path, LOW_OUTER, LOW_GEOMETRY, "low candidate")
    require(low_candidate.texture.payload == low_payload, "low candidate payload differs from requested layout")

    for row in BADGES:
        target_width, target_height = rect_dimensions(row["low_target_rect"])
        target_crop = crop_rgba(low_candidate.rgba, *LOW_GEOMETRY, row["low_target_rect"])
        candidate_bbox = alpha_bbox(target_crop, target_width, target_height)
        require(candidate_bbox is not None, f"low candidate target is empty: {row['id']}")
        require(
            candidate_bbox[2] - candidate_bbox[0] >= target_width - 4
            and candidate_bbox[3] - candidate_bbox[1] >= target_height - 4,
            f"low candidate target bbox shrank excessively: {row['id']} {candidate_bbox}",
        )
        matching_row = next(item for item in badge_rows if item["id"] == row["id"])
        matching_row["low_candidate_alpha_bbox"] = [
            candidate_bbox[0] + int(row["low_target_rect"][0]),
            candidate_bbox[1] + int(row["low_target_rect"][1]),
            candidate_bbox[2] + int(row["low_target_rect"][0]),
            candidate_bbox[3] + int(row["low_target_rect"][1]),
        ]

    print("stage=write_private_qa", flush=True)
    private_root = military.ensure_tmp(output_root / "private", mkdir=True)
    qa_rows: list[dict[str, Any]] = []
    for badge_row, mapping in zip(badge_rows, BADGES):
        high_width, high_height = rect_dimensions(mapping["high_target_rect"])
        low_width, low_height = rect_dimensions(mapping["low_target_rect"])
        high_source = repaired_high_patches[str(mapping["id"])]
        low_source = repaired_low_patches[str(mapping["id"])]
        high_png = write_png(
            private_root / f"{mapping['id']}_high_master.png",
            high_source,
            high_width,
            high_height,
            forbidden=forbidden + (high_candidate_path, low_candidate_path),
        )
        low_png = write_png(
            private_root / f"{mapping['id']}_low_native.png",
            low_source,
            low_width,
            low_height,
            forbidden=forbidden + (high_candidate_path, low_candidate_path),
        )
        badge_row["private_high_master_png"] = high_png
        badge_row["private_low_native_png"] = low_png
        current_high_uv = crop_rgba(current_high.rgba, *HIGH_GEOMETRY, mapping["high_target_rect"])
        repaired_high_uv = crop_rgba(high_candidate.rgba, *HIGH_GEOMETRY, mapping["high_target_rect"])
        low_layout_crop = crop_rgba(low_layout.rgba, *LOW_GEOMETRY, mapping["low_target_rect"])
        low_candidate_crop = crop_rgba(low_candidate.rgba, *LOW_GEOMETRY, mapping["low_target_rect"])
        qa_rows.append(
            {
                "id": mapping["id"],
                "label": mapping["label"],
                "high_target_rect": mapping["high_target_rect"],
                "high_current_uv_crop": current_high_uv,
                "high_candidate_crop": repaired_high_uv,
                "low_layout_crop_upscaled": resize_rgba(low_layout_crop, low_width, low_height, high_width, high_height),
                "low_candidate_crop_upscaled": resize_rgba(low_candidate_crop, low_width, low_height, high_width, high_height),
            }
        )
    contact = build_contact_sheet(
        qa_rows,
        output_root,
        forbidden=forbidden + (high_candidate_path, low_candidate_path),
    )

    print("stage=final_verification", flush=True)
    high_before_outer = outer_hashes(current_high.outer)
    high_after_outer = outer_hashes(high_candidate.outer)
    low_before_outer = outer_hashes(current_low.outer)
    low_after_outer = outer_hashes(low_candidate.outer)
    high_changed_outers = [
        index
        for index in range(len(current_high.outer.entries))
        if high_before_outer[str(index)] != high_after_outer[str(index)]
    ]
    low_changed_outers = [
        index
        for index in range(len(current_low.outer.entries))
        if low_before_outer[str(index)] != low_after_outer[str(index)]
    ]
    require(high_changed_outers == [HIGH_OUTER], f"high changed outer scope differs: {high_changed_outers}")
    require(low_changed_outers == [LOW_OUTER], f"low changed outer scope differs: {low_changed_outers}")
    require(
        all(
            current_high.outer.entries[index].data == high_candidate.outer.entries[index].data
            for index in range(len(current_high.outer.entries))
            if index != HIGH_OUTER
        ),
        "high unrelated outer data changed",
    )
    require(
        all(
            current_low.outer.entries[index].data == low_candidate.outer.entries[index].data
            for index in range(len(current_low.outer.entries))
            if index != LOW_OUTER
        ),
        "low unrelated outer data changed",
    )
    require(
        all(
            current_high.texture.payload[(y * (HIGH_GEOMETRY[0] // 4) + x) * 16 : (y * (HIGH_GEOMETRY[0] // 4) + x) * 16 + 16]
            == high_candidate.texture.payload[(y * (HIGH_GEOMETRY[0] // 4) + x) * 16 : (y * (HIGH_GEOMETRY[0] // 4) + x) * 16 + 16]
            for y in range(HIGH_GEOMETRY[1] // 4)
            for x in range(HIGH_GEOMETRY[0] // 4)
            if (x, y) not in high_allowed
        ),
        "high non-badge BC3 block changed",
    )
    require(
        all(
            low_layout.texture.payload[(y * (LOW_GEOMETRY[0] // 4) + x) * 16 : (y * (LOW_GEOMETRY[0] // 4) + x) * 16 + 16]
            == low_candidate.texture.payload[(y * (LOW_GEOMETRY[0] // 4) + x) * 16 : (y * (LOW_GEOMETRY[0] // 4) + x) * 16 + 16]
            for y in range(LOW_GEOMETRY[1] // 4)
            for x in range(LOW_GEOMETRY[0] // 4)
            if (x, y) not in low_allowed
        ),
        "low non-badge BC3 block differs from layout baseline",
    )
    inputs_after = {
        "current_low": file_spec(current_low_path),
        "current_high": file_spec(current_high_path),
        "stock_high": file_spec(stock_high_path),
        "low_layout": file_spec(low_layout_path),
    }
    require(inputs_after == inputs, "an input changed during build")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "result": "PASS",
        "plan_review": "PASS",
        "file_only": True,
        "game_install_modified": False,
        "release_modified": False,
        "git_commit_or_push_performed": False,
        "runtime_qa": {
            "performed": False,
            "reported_resolution": "1920x1080",
            "full_process_restart_completed": None,
            "reason": "Steam deployment is forbidden for in-progress candidates",
        },
        "inputs": {
            key: {"path": str(path), **inputs[key]}
            for key, path in {
                "current_low": current_low_path,
                "current_high": current_high_path,
                "stock_high": stock_high_path,
                "low_layout": low_layout_path,
            }.items()
        },
        "scope": {
            "high_route": "RES_JP_PK_PORT/res_lang_pk_port1.bin /17/0 texture 0",
            "low_route": "RES_JP/res_lang.bin /12/0 texture 0",
            "badge_count": len(BADGES),
            "preexisting_low_prompt_japanese_tail_fixed": False,
            "preexisting_low_prompt_japanese_tail_out_of_scope": True,
        },
        "badges": badge_rows,
        "high": {
            "candidate": {"path": str(high_candidate_path), **file_spec(high_candidate_path)},
            "before_payload_sha256": sha256_bytes(current_high.texture.payload),
            "after_payload_sha256": sha256_bytes(high_candidate.texture.payload),
            "allowed_bc3_blocks": len(high_allowed),
            "encoded_bc3_blocks": high_encoded,
            "changed_bc3_blocks": len(high_changed),
            "changed_block_bbox": changed_block_bbox(high_changed),
            "changed_outer_entries": high_changed_outers,
            "all_non_17_outer_entries_byte_preserved": True,
            "all_non_badge_blocks_byte_preserved": True,
            "g1t_non_payload_bytes_preserved": True,
        },
        "low": {
            "candidate": {"path": str(low_candidate_path), **file_spec(low_candidate_path)},
            "current_bad_payload_sha256": sha256_bytes(current_low.texture.payload),
            "layout_payload_sha256": sha256_bytes(low_layout.texture.payload),
            "candidate_payload_sha256": sha256_bytes(low_candidate.texture.payload),
            "allowed_badge_bc3_blocks": len(low_allowed),
            "encoded_badge_bc3_blocks": low_encoded,
            "changed_badge_blocks_from_layout": len(low_changed_from_layout),
            "changed_badge_block_bbox": changed_block_bbox(low_changed_from_layout),
            "changed_outer_entries": low_changed_outers,
            "all_non_12_outer_entries_byte_preserved_from_current": True,
            "all_non_badge_blocks_byte_preserved_from_layout": True,
            "g1t_non_payload_bytes_preserved_from_current": True,
            "individual_high_badges_downsampled_exactly_2x": True,
        },
        "private_visual_qa": contact,
        "private_output_policy": {
            "under_ignored_tmp": True,
            "steam_apply_allowed": False,
            "release_upload_allowed": False,
            "git_publish_game_payload_allowed": False,
        },
    }
    report_path = output_root / "build_report.json"
    military.write_json(
        report_path,
        report,
        forbidden=forbidden + (high_candidate_path, low_candidate_path),
    )
    print(
        json.dumps(
            {
                "result": "PASS",
                "high_candidate": report["high"]["candidate"],
                "low_candidate": report["low"]["candidate"],
                "report": str(report_path),
                "contact_sheet": contact["path"],
                "game_install_modified": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )
    return report


def verify(output_root: Path) -> dict[str, Any]:
    output_root = military.ensure_tmp(output_root.resolve())
    report_path = military.ensure_tmp(output_root / "build_report.json")
    require(report_path.is_file(), f"missing build report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA and report.get("result") == "PASS", "report schema/result differs")
    require(report.get("plan_review") == "PASS", "plan review did not pass")
    require(report.get("game_install_modified") is False and report.get("release_modified") is False, "write-scope invariant lost")
    for route_name, outer_index, geometry in (
        ("high", HIGH_OUTER, HIGH_GEOMETRY),
        ("low", LOW_OUTER, LOW_GEOMETRY),
    ):
        candidate_row = report[route_name]["candidate"]
        candidate_path = military.ensure_tmp(Path(candidate_row["path"]))
        require(candidate_path.is_file() and file_spec(candidate_path) == {"size": candidate_row["size"], "sha256": candidate_row["sha256"]}, f"{route_name} candidate hash differs")
        parse_route(candidate_path, outer_index, geometry, f"verified {route_name} candidate")
    visual = report["private_visual_qa"]
    visual_path = military.ensure_tmp(Path(visual["path"]))
    require(visual_path.is_file() and sha256_file(visual_path) == visual["sha256"], "contact sheet hash differs")
    for row in report["badges"]:
        for key in ("private_high_master_png", "private_low_native_png"):
            png = row[key]
            path = military.ensure_tmp(Path(png["path"]))
            require(path.is_file() and sha256_file(path) == png["sha256"], f"private PNG hash differs: {path}")
    require(report["high"]["all_non_badge_blocks_byte_preserved"] is True, "high preservation gate lost")
    require(report["low"]["all_non_badge_blocks_byte_preserved_from_layout"] is True, "low preservation gate lost")
    require(report["low"]["individual_high_badges_downsampled_exactly_2x"] is True, "low 2x mapping gate lost")
    result = {
        "result": "PASS",
        "schema": SCHEMA,
        "high_candidate": report["high"]["candidate"],
        "low_candidate": report["low"]["candidate"],
        "game_install_modified": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build", help="build two tmp-only candidates and private visual QA")
    build_parser.add_argument("--current-low", type=Path, required=True)
    build_parser.add_argument("--current-high", type=Path, required=True)
    build_parser.add_argument("--stock-high", type=Path, required=True)
    build_parser.add_argument("--low-layout", type=Path, required=True)
    build_parser.add_argument("--output-root", type=Path, required=True)
    verify_parser = commands.add_parser("verify", help="verify an existing build output")
    verify_parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        build(args)
    else:
        verify(args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
