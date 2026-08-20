#!/usr/bin/env python3
"""Catalog every verified navigation-wheel atlas placement and compare geometry.

This is a read-only forensic tool.  It consumes the pinned stock/source and
Korean/target trees used to build the v0.94 resource bundle, validates the
four known wheel routes, decodes only their selected BC3 textures, and writes
deterministic JSON/CSV evidence.

The lower-band metric is intentionally named a *proxy*.  The current wheel
art is flattened icon + label artwork, so a font-only bounding box cannot be
recovered reliably from the final atlas.  Exact typography auditing requires
the layered pipeline documented beside this script.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import struct
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
for candidate in (TOOLS,):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - dependency gate is user-facing.
    raise RuntimeError("NumPy is required to decode and measure the BC3 wheel atlases") from exc


CATALOG_SCHEMA = "nobu16.kr.navigation-wheel-atlas-catalog.v1"
METRICS_SCHEMA = "nobu16.kr.navigation-wheel-geometry-metrics.v1"
LABEL_BAND_START_RATIO = 0.70
ALPHA_THRESHOLD = 8
FULL_SPRITE_OUTLIER_TOLERANCE = 0.05
BODY_PROXY_OUTLIER_TOLERANCE = 0.05
LABEL_PROXY_OUTLIER_TOLERANCE = 0.10
RESOLUTION_SCALE_TARGET = 2.0
RESOLUTION_SCALE_TOLERANCE = 0.05


class CatalogError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CatalogError(message)


ROUTES: tuple[Mapping[str, Any], ...] = (
    {
        "id": "base_low",
        "edition": "base",
        "resolution": "low",
        "scale": 1,
        "relative_path": "RES_JP/res_lang.bin",
        "outer_entry": 8,
        "resource_id": 474,
        "texture_index": 0,
        "source": {
            "size": 153_198_542,
            "sha256": "D32898C186CBDC7534692269C062E888ACE3B7A58F5DB4FEC8B0C745DADAAE53",
        },
        "target": {
            "size": 154_797_772,
            "sha256": "763F3C5CFDC8CDCBC4220E863F34AAFCCF150E709E9C150C3E162DB9F3AA75A6",
        },
    },
    {
        "id": "base_high",
        "edition": "base",
        "resolution": "high",
        "scale": 2,
        "relative_path": "RES_JP_PK_PORT/res_lang_pk_port1.bin",
        "outer_entry": 3,
        "resource_id": 474,
        "texture_index": 0,
        "source": {
            "size": 77_468_728,
            "sha256": "1B44436B542F73B8B155A43F74D897F8D32C1C274D8C64B3CA9F4478BDB86022",
        },
        "target": {
            "size": 83_104_857,
            "sha256": "26D56822815383CCC5CA74EA289AE2E7BEC5756A141C3A5BDCA78379A6F3D11F",
        },
    },
    {
        "id": "pk_low",
        "edition": "pk",
        "resolution": "low",
        "scale": 1,
        "relative_path": "RES_JP_PK/res_lang_pk.bin",
        "outer_entry": 1,
        "resource_id": 81,
        "texture_index": 0,
        "source": {
            "size": 140_729_547,
            "sha256": "67CC064ED9D138B85255F8AA6AC5B5E47D7239E06E15A4E5AD68922274300EF5",
        },
        "target": {
            "size": 141_941_735,
            "sha256": "9DED5FEC1684D7DD5CC8DCC353747CC2097F119F15501D9BFA719C96008616E7",
        },
    },
    {
        "id": "pk_high",
        "edition": "pk",
        "resolution": "high",
        "scale": 2,
        "relative_path": "RES_JP_PK_PORT/res_lang_pk_port2.bin",
        "outer_entry": 3,
        "resource_id": 81,
        "texture_index": 0,
        "source": {
            "size": 61_609_467,
            "sha256": "52A8DE4BA1480E86218AC0CDE50DA946B4BCDFD7053ED85B94B04E663C00B380",
        },
        "target": {
            "size": 67_881_659,
            "sha256": "D8B26D0D514AD886ECAE746B0C2C0245E8DD74E85932260EAB88F2856ECDB330",
        },
    },
)


BASE_MAIN_LABELS: tuple[Mapping[str, str], ...] = (
    {"name": "assessment", "jp": "評定", "ko": "군평정"},
    {"name": "appointment", "jp": "任命", "ko": "임명"},
    {"name": "military", "jp": "軍事", "ko": "군사"},
    {"name": "domestic", "jp": "内政", "ko": "내정"},
    {"name": "diplomacy", "jp": "外交", "ko": "외교"},
)


# The source atlas contains only pixels, not semantic strings.  Japanese PK
# spellings therefore remain null unless a text source is independently pinned.
PK_DETAIL_LABELS: tuple[Mapping[str, str | None], ...] = (
    {"name": "joint_battle", "jp": None, "ko": "공투"},
    {"name": "reinforcement", "jp": None, "ko": "증원"},
    {"name": "standby", "jp": None, "ko": "대기"},
    {"name": "siege_battle", "jp": None, "ko": "공성전"},
    {"name": "castle_role", "jp": None, "ko": "성역할"},
    {"name": "edit_castle_role", "jp": None, "ko": "편집"},
    {"name": "clear_castle_role", "jp": None, "ko": "해제"},
    {"name": "supply_base", "jp": None, "ko": "보급거점"},
    {"name": "clear_supply_base", "jp": None, "ko": "해제"},
    {"name": "defense_base", "jp": None, "ko": "방어거점"},
    {"name": "clear_defense_base", "jp": None, "ko": "해제"},
    {"name": "edit_defense_base", "jp": None, "ko": "편집"},
)
PK_MAIN_LABEL = {"name": "wide_area", "jp": None, "ko": "광역"}


@dataclass(frozen=True)
class LoadedResource:
    table_padding: bytes
    nested_slot: int
    texture: atlas_codec.Texture


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def validate_pin(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is not a file: {path}")
    actual = {"size": path.stat().st_size, "sha256": sha256_file(path)}
    require(actual == dict(expected), f"{label} pin differs: expected={dict(expected)} actual={actual}")
    return actual


def parse_nested(blob: bytes, expected_resource_id: int) -> tuple[bytes, tuple[bytes, ...], int]:
    require(len(blob) >= 32 and blob[:4] == b"LINK", "nested resource is not LINK")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", blob, 4)
    require(count > 0 and table_offset == 32, "nested LINK header differs")
    require(resource_id == expected_resource_id, f"nested resource id {resource_id} != {expected_resource_id}")
    table_end = table_offset + count * 8
    require(aligned_table_end == (table_end + 31) & -32, "nested LINK alignment differs")
    pairs = [struct.unpack_from("<II", blob, table_offset + index * 8) for index in range(count)]
    require(pairs and pairs[0][0] >= aligned_table_end, "nested data overlaps table")
    entries: list[bytes] = []
    for index, (offset, size) in enumerate(pairs):
        end = offset + size
        next_offset = pairs[index + 1][0] if index + 1 < count else len(blob)
        require(aligned_table_end <= offset <= end <= next_offset <= len(blob), f"nested entry {index} bounds differ")
        entries.append(blob[offset:end])
    return blob[table_end : pairs[0][0]], tuple(entries), resource_id


def load_resource(path: Path, route: Mapping[str, Any]) -> LoadedResource:
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"outer LINK identity failed: {path}")
    outer_index = int(route["outer_entry"])
    require(outer_index < len(outer.entries), f"outer entry {outer_index} absent: {path}")
    table_padding, entries, _ = parse_nested(outer.entries[outer_index].data, int(route["resource_id"]))
    matches: list[tuple[int, atlas_codec.G1T]] = []
    for index, entry in enumerate(entries):
        try:
            _header, raw = lz4.decompress_wrapper(entry)
            g1t = atlas_codec.parse_g1t(raw)
        except (lz4.LZ4Error, atlas_codec.AtlasError):
            continue
        matches.append((index, g1t))
    require(len(matches) == 1, f"expected one nested G1T wrapper, found {len(matches)}: {path}")
    nested_slot, g1t = matches[0]
    texture_index = int(route["texture_index"])
    require(texture_index < len(g1t.textures), f"texture {texture_index} absent: {path}")
    texture = g1t.textures[texture_index]
    require(texture.format_code == 0x5B, f"wheel texture is not BC3: 0x{texture.format_code:02X}")
    return LoadedResource(table_padding=table_padding, nested_slot=nested_slot, texture=texture)


def parse_layout(table_padding: bytes, expected_count: int) -> list[tuple[int, int, int, int, int]]:
    require(len(table_padding) >= 32, "layout table is too short")
    layout = table_padding[24:]
    require(len(layout) % 12 == 8, f"layout byte count differs: {len(layout)}")
    records: list[tuple[int, int, int, int, int]] = []
    for index in range((len(layout) - 8) // 12):
        first, second, third = struct.unpack_from("<III", layout, index * 12)
        records.append((first & 0xFFFF, first >> 16, second & 0xFFFF, second >> 16, third))
    require(len(records) == expected_count, f"layout record count {len(records)} != {expected_count}")
    return records


def detail_group_records() -> list[list[int]]:
    groups: list[list[int]] = []
    for start, end in ((18, 251), (282, 389)):
        require((end - start + 1) % 6 == 0, "base detail range is not divisible by six")
        groups.extend([list(range(index, index + 6)) for index in range(start, end + 1, 6)])
    require(len(groups) == 57, f"base detail group count differs: {len(groups)}")
    return groups


def clipped_rect(rect: Sequence[int], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = (int(value) for value in rect)
    clipped = [max(0, x0), max(0, y0), min(width, x1), min(height, y1)]
    require(clipped[0] < clipped[2] and clipped[1] < clipped[3], f"placement misses atlas: {rect}")
    return clipped


def block_rect(rect: Sequence[int]) -> list[int]:
    x0, y0, x1, y1 = (int(value) for value in rect)
    return [x0 // 4, y0 // 4, (x1 + 3) // 4, (y1 + 3) // 4]


def placement_row(
    route: Mapping[str, Any],
    family: str,
    group: int,
    label: Mapping[str, Any],
    state: int,
    record_index: int,
    record: Sequence[int],
    logical_rect: Sequence[int],
    texture: atlas_codec.Texture,
    *,
    canonical_source_group: int | None = None,
) -> dict[str, Any]:
    x, y, width, height, third = (int(value) for value in record)
    rect = [int(value) for value in logical_rect]
    clip = clipped_rect(rect, texture.width, texture.height)
    return {
        "route": route["id"],
        "edition": route["edition"],
        "resolution": route["resolution"],
        "scale": int(route["scale"]),
        "family": family,
        "group": group,
        "canonical_source_group": canonical_source_group,
        "name": label["name"],
        "jp": label.get("jp"),
        "ko": label.get("ko"),
        "state": state,
        "metadata_record": record_index,
        "metadata_rect": [x, y, width, height],
        "metadata_third": third,
        "logical_rect": rect,
        "logical_size": [rect[2] - rect[0], rect[3] - rect[1]],
        "atlas_clip_rect": clip,
        "boundary_clipped": rect != clip,
        "bc3_block_rect": block_rect(clip),
    }


def base_placements(
    route: Mapping[str, Any],
    records: Sequence[Sequence[int]],
    texture: atlas_codec.Texture,
    mapping: Mapping[str, Any],
) -> list[dict[str, Any]]:
    scale = int(route["scale"])
    detail_core = (96 * scale, 88 * scale)
    detail_cell = (100 * scale, 95 * scale)
    detail_padding = (2 * scale, 6 * scale)
    main_core = 104 * scale
    by_group: dict[int, Mapping[str, Any]] = {}
    for item in mapping["groups"]:
        for target in item["targets"]:
            target = int(target)
            require(target not in by_group, f"base group {target} mapped twice")
            by_group[target] = item
    require(set(by_group) == set(range(57)), "base detail mapping does not cover groups 0..56")

    rows: list[dict[str, Any]] = []
    for group, record_indices in enumerate(detail_group_records()):
        label = by_group[group]
        for state_index, record_index in enumerate(record_indices):
            record = records[record_index]
            x, y, width, height, third = record
            require((width, height, third) == (*detail_core, 0), f"base detail record {record_index} geometry differs")
            rect = [
                x - detail_padding[0],
                y - detail_padding[1],
                x - detail_padding[0] + detail_cell[0],
                y - detail_padding[1] + detail_cell[1],
            ]
            rows.append(
                placement_row(
                    route,
                    "base_detail",
                    group,
                    label,
                    state_index + 1,
                    record_index,
                    record,
                    rect,
                    texture,
                    canonical_source_group=int(label["source_group"]),
                )
            )

    for group, label in enumerate(BASE_MAIN_LABELS):
        for state_index in range(6):
            record_index = 252 + group * 6 + state_index
            record = records[record_index]
            x, y, width, height, third = record
            require((width, height, third) == (main_core, main_core, 0), f"base main record {record_index} geometry differs")
            rows.append(
                placement_row(
                    route,
                    "base_main",
                    group,
                    label,
                    state_index + 1,
                    record_index,
                    record,
                    [x, y, x + main_core, y + main_core],
                    texture,
                    canonical_source_group=group,
                )
            )
    require(len(rows) == 372, f"base placement count differs: {len(rows)}")
    return rows


def pk_placements(
    route: Mapping[str, Any], records: Sequence[Sequence[int]], texture: atlas_codec.Texture
) -> list[dict[str, Any]]:
    scale = int(route["scale"])
    group_indices = [list(range(0, 6))] + [list(range(index, index + 6)) for index in range(12, 78, 6)]
    require(len(group_indices) == 12, "PK detail group count differs")
    rows: list[dict[str, Any]] = []
    detail_core = (96, 88) if scale == 1 else (192, 176)
    for group, indices in enumerate(group_indices):
        label = PK_DETAIL_LABELS[group]
        for state_index, record_index in enumerate(indices):
            record = records[record_index]
            x, y, width, height, third = record
            require((width, height, third) == (*detail_core, 0), f"PK detail record {record_index} geometry differs")
            if scale == 1:
                rect = [x - 4, y - 4, x + 100, y + 92]
            else:
                rect = [x - 4, y - 4, x + 196, y + 180]
            rows.append(
                placement_row(
                    route,
                    "pk_detail",
                    group,
                    label,
                    state_index + 1,
                    record_index,
                    record,
                    rect,
                    texture,
                    canonical_source_group=group,
                )
            )

    main_core = (96, 88) if scale == 1 else (196, 180)
    for state_index, record_index in enumerate(range(6, 12)):
        record = records[record_index]
        x, y, width, height, third = record
        require((width, height, third) == (*main_core, 0), f"PK main record {record_index} geometry differs")
        if scale == 1:
            rect = [x - 4, y - 4, x + 100, y + 92]
        else:
            rect = [x - 4, y - 4, x + 200, y + 184]
        rows.append(
            placement_row(
                route,
                "pk_main",
                0,
                PK_MAIN_LABEL,
                state_index + 1,
                record_index,
                record,
                rect,
                texture,
                canonical_source_group=0,
            )
        )
    require(len(rows) == 78, f"PK placement count differs: {len(rows)}")
    return rows


def connected_components(mask: np.ndarray) -> list[tuple[np.ndarray, tuple[int, int, int, int]]]:
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    result: list[tuple[np.ndarray, tuple[int, int, int, int]]] = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        queue: deque[tuple[int, int]] = deque([(int(y0), int(x0))])
        seen[y0, x0] = True
        pixels: list[tuple[int, int]] = []
        min_x = max_x = int(x0)
        min_y = max_y = int(y0)
        while queue:
            y, x = queue.popleft()
            pixels.append((y, x))
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    if mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
        coords = np.asarray(pixels, dtype=np.int16)
        result.append((coords, (min_x, min_y, max_x + 1, max_y + 1)))
    return result


def bbox_from_coords(coords: np.ndarray) -> list[int] | None:
    if coords.size == 0:
        return None
    return [
        int(np.min(coords[:, 1])),
        int(np.min(coords[:, 0])),
        int(np.max(coords[:, 1])) + 1,
        int(np.max(coords[:, 0])) + 1,
    ]


def dominant_component(cell: np.ndarray) -> dict[str, Any]:
    height, width = cell.shape[:2]
    components = connected_components(cell[:, :, 3] >= ALPHA_THRESHOLD)
    require(bool(components), "wheel placement has no alpha foreground")

    def rank(item: tuple[np.ndarray, tuple[int, int, int, int]]) -> tuple[float, int]:
        coords, _bbox = item
        cy = float(np.mean(coords[:, 0]))
        cx = float(np.mean(coords[:, 1]))
        center_penalty = ((cx - width / 2) / (width / 2)) ** 2 + ((cy - height * 0.52) / (height / 2)) ** 2
        return (len(coords) / (1.0 + center_penalty), len(coords))

    coords, bbox = max(components, key=rank)
    band_start = int(math.floor(height * LABEL_BAND_START_RATIO))
    upper_coords = coords[coords[:, 0] < band_start]
    lower_coords = coords[coords[:, 0] >= band_start]
    return {
        "bbox": list(bbox),
        "size": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
        "center": [(bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0],
        "pixels": int(len(coords)),
        "component_count": len(components),
        "label_band_start_y": band_start,
        "body_band_proxy_bbox": bbox_from_coords(upper_coords),
        "label_band_proxy_bbox": bbox_from_coords(lower_coords),
    }


def logical_cell(atlas: np.ndarray, logical_rect: Sequence[int], clip_rect: Sequence[int]) -> np.ndarray:
    x0, y0, x1, y1 = (int(value) for value in logical_rect)
    cx0, cy0, cx1, cy1 = (int(value) for value in clip_rect)
    result = np.zeros((y1 - y0, x1 - x0, 4), dtype=np.uint8)
    result[cy0 - y0 : cy1 - y0, cx0 - x0 : cx1 - x0] = atlas[cy0:cy1, cx0:cx1]
    return result


def bbox_size(bbox: Sequence[int] | None) -> list[int] | None:
    if bbox is None:
        return None
    return [int(bbox[2]) - int(bbox[0]), int(bbox[3]) - int(bbox[1])]


def ratio(numerator: int, denominator: int) -> float:
    require(denominator > 0, "geometry ratio denominator is zero")
    return round(numerator / denominator, 6)


def geometry_metric(row: Mapping[str, Any], source_atlas: np.ndarray, target_atlas: np.ndarray) -> dict[str, Any]:
    source = dominant_component(logical_cell(source_atlas, row["logical_rect"], row["atlas_clip_rect"]))
    target = dominant_component(logical_cell(target_atlas, row["logical_rect"], row["atlas_clip_rect"]))
    width_ratio = ratio(target["size"][0], source["size"][0])
    height_ratio = ratio(target["size"][1], source["size"][1])
    source_body_size = bbox_size(source["body_band_proxy_bbox"])
    target_body_size = bbox_size(target["body_band_proxy_bbox"])
    source_label_size = bbox_size(source["label_band_proxy_bbox"])
    target_label_size = bbox_size(target["label_band_proxy_bbox"])
    body_width_ratio = None
    body_height_ratio = None
    if source_body_size and target_body_size and source_body_size[0] and source_body_size[1]:
        body_width_ratio = ratio(target_body_size[0], source_body_size[0])
        body_height_ratio = ratio(target_body_size[1], source_body_size[1])
    label_width_ratio = None
    label_height_ratio = None
    if source_label_size and target_label_size and source_label_size[0] and source_label_size[1]:
        label_width_ratio = ratio(target_label_size[0], source_label_size[0])
        label_height_ratio = ratio(target_label_size[1], source_label_size[1])
    full_deviation = max(abs(width_ratio - 1.0), abs(height_ratio - 1.0))
    body_deviation = None
    if body_width_ratio is not None and body_height_ratio is not None:
        body_deviation = max(abs(body_width_ratio - 1.0), abs(body_height_ratio - 1.0))
    label_deviation = None
    if label_width_ratio is not None and label_height_ratio is not None:
        label_deviation = max(abs(label_width_ratio - 1.0), abs(label_height_ratio - 1.0))
    return {
        **{key: row[key] for key in ("route", "edition", "resolution", "scale", "family", "group", "name", "jp", "ko", "state", "metadata_record")},
        "source_component": source,
        "target_component": target,
        "target_over_source_width": width_ratio,
        "target_over_source_height": height_ratio,
        "component_center_shift": [
            round(target["center"][0] - source["center"][0], 3),
            round(target["center"][1] - source["center"][1], 3),
        ],
        "full_sprite_deviation": round(full_deviation, 6),
        "full_sprite_outlier_5pct": full_deviation > FULL_SPRITE_OUTLIER_TOLERANCE,
        "body_proxy_source_size": source_body_size,
        "body_proxy_target_size": target_body_size,
        "body_proxy_target_over_source_width": body_width_ratio,
        "body_proxy_target_over_source_height": body_height_ratio,
        "body_proxy_deviation": None if body_deviation is None else round(body_deviation, 6),
        "body_proxy_outlier_5pct": bool(body_deviation is not None and body_deviation > BODY_PROXY_OUTLIER_TOLERANCE),
        "label_proxy_source_size": source_label_size,
        "label_proxy_target_size": target_label_size,
        "label_proxy_target_over_source_width": label_width_ratio,
        "label_proxy_target_over_source_height": label_height_ratio,
        "label_proxy_deviation": None if label_deviation is None else round(label_deviation, 6),
        "label_proxy_outlier_10pct": bool(label_deviation is not None and label_deviation > LABEL_PROXY_OUTLIER_TOLERANCE),
    }


def percentile(values: Sequence[float], quantile: float) -> float | None:
    if not values:
        return None
    return round(float(np.quantile(np.asarray(values, dtype=np.float64), quantile)), 6)


def ratio_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    widths = [float(row["target_over_source_width"]) for row in rows]
    heights = [float(row["target_over_source_height"]) for row in rows]
    body_widths = [float(row["body_proxy_target_over_source_width"]) for row in rows if row["body_proxy_target_over_source_width"] is not None]
    body_heights = [float(row["body_proxy_target_over_source_height"]) for row in rows if row["body_proxy_target_over_source_height"] is not None]
    label_widths = [float(row["label_proxy_target_over_source_width"]) for row in rows if row["label_proxy_target_over_source_width"] is not None]
    label_heights = [float(row["label_proxy_target_over_source_height"]) for row in rows if row["label_proxy_target_over_source_height"] is not None]
    return {
        "count": len(rows),
        "full_sprite_outliers_5pct": sum(bool(row["full_sprite_outlier_5pct"]) for row in rows),
        "body_proxy_outliers_5pct": sum(bool(row["body_proxy_outlier_5pct"]) for row in rows),
        "label_proxy_outliers_10pct": sum(bool(row["label_proxy_outlier_10pct"]) for row in rows),
        "target_over_source_width": {"min": min(widths), "median": percentile(widths, 0.5), "max": max(widths)},
        "target_over_source_height": {"min": min(heights), "median": percentile(heights, 0.5), "max": max(heights)},
        "body_proxy_target_over_source_width": {
            "min": min(body_widths) if body_widths else None,
            "median": percentile(body_widths, 0.5),
            "max": max(body_widths) if body_widths else None,
        },
        "body_proxy_target_over_source_height": {
            "min": min(body_heights) if body_heights else None,
            "median": percentile(body_heights, 0.5),
            "max": max(body_heights) if body_heights else None,
        },
        "label_proxy_target_over_source_width": {
            "min": min(label_widths) if label_widths else None,
            "median": percentile(label_widths, 0.5),
            "max": max(label_widths) if label_widths else None,
        },
        "label_proxy_target_over_source_height": {
            "min": min(label_heights) if label_heights else None,
            "median": percentile(label_heights, 0.5),
            "max": max(label_heights) if label_heights else None,
        },
    }


def scale_metric(low: Mapping[str, Any], high: Mapping[str, Any]) -> dict[str, Any]:
    require((low["edition"], low["family"], low["group"], low["state"]) == (high["edition"], high["family"], high["group"], high["state"]), "low/high metric key differs")
    source_width = ratio(high["source_component"]["size"][0], low["source_component"]["size"][0])
    source_height = ratio(high["source_component"]["size"][1], low["source_component"]["size"][1])
    target_width = ratio(high["target_component"]["size"][0], low["target_component"]["size"][0])
    target_height = ratio(high["target_component"]["size"][1], low["target_component"]["size"][1])
    source_deviation = max(abs(source_width / RESOLUTION_SCALE_TARGET - 1.0), abs(source_height / RESOLUTION_SCALE_TARGET - 1.0))
    target_deviation = max(abs(target_width / RESOLUTION_SCALE_TARGET - 1.0), abs(target_height / RESOLUTION_SCALE_TARGET - 1.0))
    return {
        "edition": low["edition"],
        "family": low["family"],
        "group": low["group"],
        "name": low["name"],
        "ko": low["ko"],
        "state": low["state"],
        "source_high_over_low_width": source_width,
        "source_high_over_low_height": source_height,
        "target_high_over_low_width": target_width,
        "target_high_over_low_height": target_height,
        "source_scale_deviation": round(source_deviation, 6),
        "target_scale_deviation": round(target_deviation, 6),
        "source_scale_outlier_5pct": source_deviation > RESOLUTION_SCALE_TOLERANCE,
        "target_scale_outlier_5pct": target_deviation > RESOLUTION_SCALE_TOLERANCE,
    }


def scale_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    def stats(key: str) -> dict[str, Any]:
        values = [float(row[key]) for row in rows]
        return {"min": min(values), "median": percentile(values, 0.5), "max": max(values)}

    return {
        "count": len(rows),
        "source_scale_outliers_5pct": sum(bool(row["source_scale_outlier_5pct"]) for row in rows),
        "target_scale_outliers_5pct": sum(bool(row["target_scale_outlier_5pct"]) for row in rows),
        "source_high_over_low_width": stats("source_high_over_low_width"),
        "source_high_over_low_height": stats("source_high_over_low_height"),
        "target_high_over_low_width": stats("target_high_over_low_width"),
        "target_high_over_low_height": stats("target_high_over_low_height"),
    }


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        flattened = {}
        for key in fieldnames:
            value = row.get(key)
            if isinstance(value, (list, dict)):
                flattened[key] = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            elif value is None:
                flattened[key] = ""
            else:
                flattened[key] = value
        writer.writerow(flattened)
    path.write_text(buffer.getvalue(), encoding="utf-8-sig", newline="")


def write_positions_markdown(
    path: Path,
    route_reports: Mapping[str, Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
) -> None:
    lines = [
        "# 네비게이션 휠 전체 위치표 v1",
        "",
        "사각형 표기는 `[left,top,right,bottom]`이고 오른쪽·아래쪽은 포함하지 않는다.",
        "각 행의 레코드와 사각형은 상태 1→6 순서다. 더 세밀한 메타데이터·클립·BC3 블록 좌표는",
        "`navigation_wheel_placements_v1.csv`를 사용한다.",
        "",
    ]
    for route_id in ("base_low", "base_high", "pk_low", "pk_high"):
        route = route_reports[route_id]
        route_rows = [row for row in rows if row["route"] == route_id]
        grouped: dict[tuple[str, int], list[Mapping[str, Any]]] = {}
        for row in route_rows:
            grouped.setdefault((str(row["family"]), int(row["group"])), []).append(row)
        lines.extend(
            [
                f"## {route_id}",
                "",
                f"- 경로: `{route['archive']}` / 바깥 `{route['outer_entry']}` / 중첩 `{route['nested_slot']}` / "
                f"리소스 `{route['resource_id']}` / 텍스처 `{route['texture_index']}`",
                f"- 텍스처: {route['dimensions'][0]}×{route['dimensions'][1]} {route['format']}; 배치 {route['placement_count']}개",
                "",
                "| 계열 | 그룹 | 이름 | 일본어 | 한국어 | 메타데이터 레코드 1→6 | 논리 사각형 1→6 |",
                "|---|---:|---|---|---|---|---|",
            ]
        )
        family_order = {"base_detail": 0, "base_main": 1, "pk_detail": 0, "pk_main": 1}
        for key in sorted(grouped, key=lambda item: (family_order[item[0]], item[1])):
            states = sorted(grouped[key], key=lambda row: int(row["state"]))
            require([int(row["state"]) for row in states] == list(range(1, 7)), f"{route_id} {key} state coverage differs")
            first = states[0]
            records = ", ".join(str(row["metadata_record"]) for row in states)
            rects = "; ".join("[" + ",".join(str(value) for value in row["logical_rect"]) + "]" for row in states)
            lines.append(
                f"| `{first['family']}` | {first['group']} | `{first['name']}` | {first['jp'] or '-'} | "
                f"{first['ko'] or '-'} | {records} | {rects} |"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_root = args.source_root.resolve(strict=True)
    target_root = args.target_root.resolve(strict=True)
    mapping_path = args.mapping.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    require(mapping.get("schema") == "nobu16.kr.wheel-detail-groups.v1", "base detail mapping schema differs")

    catalog_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    route_reports: dict[str, Any] = {}

    for route in ROUTES:
        route_id = str(route["id"])
        relative_path = Path(str(route["relative_path"]))
        source_path = source_root / relative_path
        target_path = target_root / relative_path
        source_spec = validate_pin(source_path, route["source"], f"{route_id} source")
        target_spec = validate_pin(target_path, route["target"], f"{route_id} target")
        source = load_resource(source_path, route)
        target = load_resource(target_path, route)
        require(source.nested_slot == target.nested_slot == 0, f"{route_id} nested G1T slot differs")
        require(source.table_padding == target.table_padding, f"{route_id} source/target layout bytes differ")
        require(
            (source.texture.width, source.texture.height, source.texture.format_code)
            == (target.texture.width, target.texture.height, target.texture.format_code),
            f"{route_id} source/target texture geometry differs",
        )
        expected_dimensions = (2048, 2048) if route_id == "base_low" else (4096, 4096) if route_id == "base_high" else (1024, 1024) if route_id == "pk_low" else (2048, 2048)
        require((source.texture.width, source.texture.height) == expected_dimensions, f"{route_id} texture dimensions differ")
        records = parse_layout(source.table_padding, 474 if route["edition"] == "base" else 82)
        rows = (
            base_placements(route, records, source.texture, mapping)
            if route["edition"] == "base"
            else pk_placements(route, records, source.texture)
        )
        source_decoded = atlas_codec.decode_texture(source.texture)
        target_decoded = atlas_codec.decode_texture(target.texture)
        require(source_decoded is not None and target_decoded is not None, f"{route_id} BC3 decode failed")
        source_atlas = np.frombuffer(source_decoded, dtype=np.uint8).reshape(source.texture.height, source.texture.width, 4)
        target_atlas = np.frombuffer(target_decoded, dtype=np.uint8).reshape(target.texture.height, target.texture.width, 4)
        route_metrics = [geometry_metric(row, source_atlas, target_atlas) for row in rows]
        catalog_rows.extend(rows)
        metric_rows.extend(route_metrics)
        route_reports[route_id] = {
            "edition": route["edition"],
            "resolution": route["resolution"],
            "scale": route["scale"],
            "archive": route["relative_path"],
            "outer_entry": route["outer_entry"],
            "nested_slot": source.nested_slot,
            "resource_id": route["resource_id"],
            "texture_index": route["texture_index"],
            "format_code": f"0x{source.texture.format_code:02X}",
            "format": "BC3/DXT5",
            "dimensions": [source.texture.width, source.texture.height],
            "layout_record_count": len(records),
            "layout_table_sha256": sha256_bytes(source.table_padding),
            "placement_count": len(rows),
            "source": source_spec,
            "target": target_spec,
            "metrics": ratio_summary(route_metrics),
        }
        del source_atlas, target_atlas, source_decoded, target_decoded

    require(len(catalog_rows) == 900, f"catalog placement count differs: {len(catalog_rows)}")
    require(len(metric_rows) == 900, f"metric row count differs: {len(metric_rows)}")
    unique_keys = {
        (row["route"], row["family"], row["group"], row["state"], row["metadata_record"])
        for row in catalog_rows
    }
    require(len(unique_keys) == len(catalog_rows), "catalog placement keys are not unique")

    metric_by_key = {
        (row["route"], row["family"], row["group"], row["state"]): row for row in metric_rows
    }
    scale_rows: list[dict[str, Any]] = []
    for edition in ("base", "pk"):
        low_route = f"{edition}_low"
        high_route = f"{edition}_high"
        low_rows = [row for row in metric_rows if row["route"] == low_route]
        for low in low_rows:
            high = metric_by_key[(high_route, low["family"], low["group"], low["state"])]
            scale_rows.append(scale_metric(low, high))
    require(len(scale_rows) == 450, f"resolution-scale row count differs: {len(scale_rows)}")

    structural_scale_contracts = {
        "base_detail": {
            "metadata_core_low": [96, 88],
            "metadata_core_high": [192, 176],
            "logical_cell_low": [100, 95],
            "logical_cell_high": [200, 190],
            "logical_high_over_low": [2.0, 2.0],
        },
        "base_main": {
            "metadata_core_low": [104, 104],
            "metadata_core_high": [208, 208],
            "logical_cell_low": [104, 104],
            "logical_cell_high": [208, 208],
            "logical_high_over_low": [2.0, 2.0],
        },
        "pk_detail": {
            "metadata_core_low": [96, 88],
            "metadata_core_high": [192, 176],
            "logical_cell_low": [104, 96],
            "logical_cell_high": [200, 184],
            "logical_high_over_low": [round(200 / 104, 6), round(184 / 96, 6)],
        },
        "pk_main": {
            "metadata_core_low": [96, 88],
            "metadata_core_high": [196, 180],
            "logical_cell_low": [104, 96],
            "logical_cell_high": [204, 188],
            "logical_high_over_low": [round(204 / 104, 6), round(188 / 96, 6)],
        },
    }

    catalog = {
        "schema": CATALOG_SCHEMA,
        "snapshot": "v0.94.0 resource bundle source/target trees, release-v0940-rc-20260819-06",
        "mapping": {
            "path": str(mapping_path.relative_to(REPO)).replace("\\", "/"),
            "size": mapping_path.stat().st_size,
            "sha256": sha256_file(mapping_path),
        },
        "coverage": {
            "routes": 4,
            "base_detail_unique_labels": len(mapping["groups"]),
            "base_detail_groups_per_route": 57,
            "base_main_groups_per_route": 5,
            "pk_detail_groups_per_route": 12,
            "pk_main_groups_per_route": 1,
            "states_per_group": 6,
            "placements": len(catalog_rows),
        },
        "route_order": [route["id"] for route in ROUTES],
        "routes": route_reports,
        "structural_scale_contracts": structural_scale_contracts,
        "placements": catalog_rows,
    }

    overall_metrics = ratio_summary(metric_rows)
    metrics_by_family = {
        family: ratio_summary([row for row in metric_rows if row["family"] == family])
        for family in ("base_detail", "base_main", "pk_detail", "pk_main")
    }
    largest_full = sorted(metric_rows, key=lambda row: float(row["full_sprite_deviation"]), reverse=True)[:30]
    largest_label = sorted(
        [row for row in metric_rows if row["label_proxy_deviation"] is not None],
        key=lambda row: float(row["label_proxy_deviation"]),
        reverse=True,
    )[:30]
    metrics = {
        "schema": METRICS_SCHEMA,
        "methodology": {
            "alpha_threshold": ALPHA_THRESHOLD,
            "component_selection": "8-connected alpha component ranked by area and proximity to logical-cell center",
            "full_sprite_definition": "selected flattened icon+label component bounding box",
            "body_band_proxy_definition": f"selected component pixels at y < floor(logical_height * {LABEL_BAND_START_RATIO})",
            "label_band_proxy_definition": f"selected component pixels at y >= floor(logical_height * {LABEL_BAND_START_RATIO})",
            "body_band_is_not_body_layer": True,
            "label_band_is_not_font_only": True,
            "full_sprite_outlier_tolerance": FULL_SPRITE_OUTLIER_TOLERANCE,
            "body_proxy_outlier_tolerance": BODY_PROXY_OUTLIER_TOLERANCE,
            "label_proxy_outlier_tolerance": LABEL_PROXY_OUTLIER_TOLERANCE,
            "resolution_scale_target": RESOLUTION_SCALE_TARGET,
            "resolution_scale_outlier_tolerance": RESOLUTION_SCALE_TOLERANCE,
        },
        "summary": {
            "overall": overall_metrics,
            "by_route": {route_id: report["metrics"] for route_id, report in route_reports.items()},
            "by_family": metrics_by_family,
            "resolution_scale": {
                "overall": scale_summary(scale_rows),
                "base": scale_summary([row for row in scale_rows if row["edition"] == "base"]),
                "pk": scale_summary([row for row in scale_rows if row["edition"] == "pk"]),
            },
        },
        "largest_full_sprite_outliers": [
            {key: row[key] for key in ("route", "family", "group", "name", "ko", "state", "target_over_source_width", "target_over_source_height", "full_sprite_deviation")}
            for row in largest_full
        ],
        "largest_label_proxy_outliers": [
            {key: row[key] for key in ("route", "family", "group", "name", "ko", "state", "label_proxy_target_over_source_width", "label_proxy_target_over_source_height", "label_proxy_deviation")}
            for row in largest_label
        ],
        "rows": metric_rows,
        "resolution_scale_rows": scale_rows,
    }

    catalog_path = output / "navigation_wheel_catalog_v1.json"
    placements_path = output / "navigation_wheel_placements_v1.csv"
    metrics_path = output / "wheel_geometry_metrics_v1.json"
    metrics_csv_path = output / "wheel_geometry_metrics_v1.csv"
    scale_csv_path = output / "wheel_resolution_scale_v1.csv"
    positions_markdown_path = output / "NAVIGATION_WHEEL_POSITIONS_KO.md"
    write_json(catalog_path, catalog)
    write_json(metrics_path, metrics)
    write_positions_markdown(positions_markdown_path, route_reports, catalog_rows)
    write_csv(
        placements_path,
        catalog_rows,
        (
            "route", "edition", "resolution", "scale", "family", "group", "canonical_source_group",
            "name", "jp", "ko", "state", "metadata_record", "metadata_rect", "metadata_third",
            "logical_rect", "logical_size", "atlas_clip_rect", "boundary_clipped", "bc3_block_rect",
        ),
    )
    write_csv(
        metrics_csv_path,
        metric_rows,
        (
            "route", "edition", "resolution", "scale", "family", "group", "name", "jp", "ko", "state",
            "metadata_record", "source_component", "target_component", "target_over_source_width",
            "target_over_source_height", "component_center_shift", "full_sprite_deviation", "full_sprite_outlier_5pct",
            "body_proxy_source_size", "body_proxy_target_size", "body_proxy_target_over_source_width",
            "body_proxy_target_over_source_height", "body_proxy_deviation", "body_proxy_outlier_5pct",
            "label_proxy_source_size", "label_proxy_target_size", "label_proxy_target_over_source_width",
            "label_proxy_target_over_source_height", "label_proxy_deviation", "label_proxy_outlier_10pct",
        ),
    )
    write_csv(
        scale_csv_path,
        scale_rows,
        (
            "edition", "family", "group", "name", "ko", "state", "source_high_over_low_width",
            "source_high_over_low_height", "target_high_over_low_width", "target_high_over_low_height",
            "source_scale_deviation", "target_scale_deviation", "source_scale_outlier_5pct", "target_scale_outlier_5pct",
        ),
    )
    return {
        "catalog": str(catalog_path),
        "catalog_sha256": sha256_file(catalog_path),
        "placements": len(catalog_rows),
        "positions_markdown": str(positions_markdown_path),
        "positions_markdown_sha256": sha256_file(positions_markdown_path),
        "metrics": str(metrics_path),
        "metrics_sha256": sha256_file(metrics_path),
        "resolution_scale_rows": len(scale_rows),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--source-root", type=Path, required=True, help="stock/source resource tree")
    result.add_argument("--target-root", type=Path, required=True, help="Korean/target resource tree")
    result.add_argument(
        "--mapping",
        type=Path,
        default=REPO / "workstreams" / "steam_jp_port_highres_images_v1" / "wheel_detail_groups_full_v1.json",
    )
    result.add_argument("--output", type=Path, default=WORKSTREAM)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
