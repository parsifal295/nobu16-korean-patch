#!/usr/bin/env python3
"""Catalog every verified ordinary-button atlas placement used by NOBU16.

The catalog is read-only.  It pins the stock/source and v0.94.0 target
archives, validates the five known texture routes, detects the source alpha
components for the BC3 routes, and writes deterministic JSON/CSV/Markdown
position evidence.  The two PK-only BC7 ``approve_all`` routes use independently
verified native rectangles; low-resolution coordinates are never inferred by
halving the high-resolution coordinates.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
HIGHRES_WORKSTREAM = REPO / "workstreams" / "steam_jp_port_highres_images_v1"
for candidate in (TOOLS, HIGHRES_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
from list_alpha_components import components  # noqa: E402

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - workspace runtime invariant.
    raise RuntimeError("NumPy is required to decode and map the button atlases") from exc


SCHEMA = "nobu16.kr.ordinary-button-atlas-catalog.v1"
SNAPSHOT = "v0.94.0 ordinary-button layered target with native low/high 전체승인, release-v0940-approve-all-layered-20260820-01"
LABEL_APPROVE_ALL = "전체승인"


class CatalogError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CatalogError(message)


ARCHIVE_PINS: Mapping[str, Mapping[str, Mapping[str, Any]]] = {
    "RES_JP/res_lang.bin": {
        "source": {
            "size": 153_198_542,
            "sha256": "D32898C186CBDC7534692269C062E888ACE3B7A58F5DB4FEC8B0C745DADAAE53",
        },
        "target": {
            "size": 153_501_108,
            "sha256": "B10EF608C4B1A4981C096A29D8B413087EF395696CB8A219B715BDF4C712D07C",
        },
    },
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": {
        "source": {
            "size": 77_468_728,
            "sha256": "1B44436B542F73B8B155A43F74D897F8D32C1C274D8C64B3CA9F4478BDB86022",
        },
        "target": {
            "size": 79_074_833,
            "sha256": "C1B21E2128A74263DCE4598E49477B056E5C64286E156FF046F7C773D3FB56EB",
        },
    },
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": {
        "source": {
            "size": 61_609_467,
            "sha256": "52A8DE4BA1480E86218AC0CDE50DA946B4BCDFD7053ED85B94B04E663C00B380",
        },
        "target": {
            "size": 67_321_109,
            "sha256": "C3168D91386375C0F40EFCDF6817E0BA4554FC1EB9B857E1B379507BB3D61C94",
        },
    },
    "RES_JP_PK/res_lang_exp_pk.bin": {
        "source": {
            "size": 4_620_368,
            "sha256": "DF974BB7918E9A242E46A133ED95C674EBFBCD361EFE1F714CA7A61DB1118E33",
        },
        "target": {
            "size": 4_597_857,
            "sha256": "DBAE16679E94AF7709786085A18583E3E37F9AA28D3A8FAB9EBE96F89BF3DE2D",
        },
    },
}


ROUTES: tuple[Mapping[str, Any], ...] = (
    {
        "id": "common_low",
        "runtime_scope": "base_and_pk_common",
        "resolution": "low",
        "relative_path": "RES_JP/res_lang.bin",
        "outer_entry": 5,
        "resource_id": 3856,
        "texture_index": 1,
        "format_code": 0x5B,
        "dimensions": (4096, 2048),
        "placement_count": 127,
    },
    {
        "id": "pk_low_approve_all",
        "runtime_scope": "pk_only",
        "resolution": "low",
        "relative_path": "RES_JP_PK/res_lang_exp_pk.bin",
        "outer_entry": 4,
        "resource_id": 870,
        "texture_index": 1,
        "format_code": 0x5F,
        "dimensions": (2048, 512),
        "placement_count": 6,
    },
    {
        "id": "common_high_standard",
        "runtime_scope": "base_and_pk_common",
        "resolution": "high",
        "relative_path": "RES_JP_PK_PORT/res_lang_pk_port1.bin",
        "outer_entry": 2,
        "resource_id": 3860,
        "texture_index": 1,
        "format_code": 0x5B,
        "dimensions": (4096, 4096),
        "placement_count": 120,
    },
    {
        "id": "common_high_battle",
        "runtime_scope": "base_and_pk_common",
        "resolution": "high",
        "relative_path": "RES_JP_PK_PORT/res_lang_pk_port1.bin",
        "outer_entry": 2,
        "resource_id": 3860,
        "texture_index": 2,
        "format_code": 0x5B,
        "dimensions": (4096, 2048),
        "placement_count": 7,
    },
    {
        "id": "pk_high_approve_all",
        "runtime_scope": "pk_only",
        "resolution": "high",
        "relative_path": "RES_JP_PK_PORT/res_lang_pk_port2.bin",
        "outer_entry": 2,
        "resource_id": 870,
        "texture_index": 1,
        "format_code": 0x5F,
        "dimensions": (4096, 1024),
        "placement_count": 6,
    },
)


STANDARD_LABELS: tuple[Mapping[str, Any], ...] = (
    {"name": "approve", "jp": "承認", "ko": "승인", "aliases": []},
    {"name": "stop", "jp": "中止", "ko": "중지", "aliases": []},
    {"name": "close", "jp": "閉じる", "ko": "닫기", "aliases": []},
    {"name": "deny", "jp": "否認", "ko": "부인", "aliases": []},
    {"name": "release_all", "jp": "全解放", "ko": "전부해방", "aliases": []},
    {"name": "confirm", "jp": "決定", "ko": "결정", "aliases": []},
    {"name": "reject", "jp": "拒否", "ko": "거절", "aliases": ["거부"]},
    {"name": "back", "jp": "戻る", "ko": "뒤로", "aliases": []},
    {"name": "no", "jp": "いいえ", "ko": "아니오", "aliases": []},
    {"name": "hime", "jp": "姫", "ko": "공주", "aliases": ["희"]},
    {"name": "command", "jp": "采配する", "ko": "지휘", "aliases": []},
    {"name": "renegotiate", "jp": "再交渉", "ko": "재교섭", "aliases": []},
    {"name": "accept", "jp": "承諾", "ko": "수락", "aliases": ["승낙"]},
    {"name": "dispose", "jp": "処断", "ko": "처단", "aliases": []},
    {"name": "skip", "jp": "スキップ", "ko": "건너뛰기", "aliases": []},
    {"name": "start", "jp": "開始", "ko": "시작", "aliases": ["개시"]},
    {"name": "recruit", "jp": "登用", "ko": "등용", "aliases": []},
    {"name": "warrior", "jp": "武将", "ko": "무장", "aliases": []},
    {"name": "yes", "jp": "はい", "ko": "예", "aliases": []},
    {"name": "next", "jp": "次へ", "ko": "다음", "aliases": []},
)


# These are semantic membership hints into the low atlas's deterministic
# component order.  Visual-state ordering is recovered from the untouched
# background strips below; the tuple order itself is not used as state order.
LOW_COMPONENT_HINTS: Mapping[str, tuple[int, ...]] = {
    "approve": (0, 1, 2, 3, 4, 5),
    "stop": (6, 7, 9, 10, 11, 12),
    "close": (8, 13, 14, 15, 16, 17),
    "deny": (18, 19, 20, 21, 22, 23),
    "release_all": (24, 26, 27, 34, 35, 36),
    "confirm": (28, 29, 30, 31, 32, 33),
    "reject": (25, 37, 38, 39, 40, 41),
    "back": (42, 43, 44, 54, 55, 56),
    "no": (46, 47, 48, 49, 50, 51),
    "hime": (45, 52, 53, 57, 58, 59),
    "command": (60, 61, 62, 63, 64, 65),
    "renegotiate": (67, 68, 69, 75, 76, 77),
    "accept": (66, 70, 71, 72, 73, 74),
    "dispose": (78, 79, 80, 81, 82, 83),
    "skip": (84, 85, 86, 96, 97, 98),
    "start": (88, 89, 90, 91, 92, 93),
    "recruit": (87, 94, 95, 99, 100, 101),
    "warrior": (102, 103, 104, 105, 106, 107),
    "yes": (109, 110, 111, 117, 118, 119),
    "next": (108, 112, 113, 114, 115, 116),
}


HIGH_BATTLE_PROCESSING_RECTS: tuple[tuple[int, int, int, int], ...] = (
    (8, 5, 516, 159),
    (534, 6, 1027, 152),
    (1054, 6, 1547, 152),
    (1574, 6, 2067, 152),
    (2094, 6, 2587, 152),
    (2614, 6, 3107, 152),
    (3134, 6, 3627, 152),
)


APPROVE_ALL_LOW_CELLS: tuple[Mapping[str, Any], ...] = (
    {"variant": "white", "artwork": (1214, 101, 1394, 180), "processing": (1208, 96, 1400, 184)},
    {"variant": "cyan", "artwork": (1406, 101, 1586, 180), "processing": (1400, 96, 1592, 184)},
    {"variant": "blue", "artwork": (1598, 101, 1778, 180), "processing": (1592, 96, 1784, 184)},
    {"variant": "disabled", "artwork": (1790, 101, 1970, 180), "processing": (1784, 96, 1976, 184)},
    {"variant": "cyan_alt", "artwork": (6, 165, 186, 244), "processing": (0, 160, 192, 248)},
    {"variant": "disabled_alt", "artwork": (198, 165, 378, 244), "processing": (192, 160, 384, 248)},
)


APPROVE_ALL_HIGH_CELLS: tuple[Mapping[str, Any], ...] = (
    {"variant": "white", "artwork": (2416, 190, 2776, 348), "processing": (2412, 188, 2780, 348)},
    {"variant": "cyan", "artwork": (2792, 190, 3152, 348), "processing": (2788, 188, 3156, 348)},
    {"variant": "blue", "artwork": (3168, 190, 3528, 348), "processing": (3164, 188, 3532, 348)},
    {"variant": "disabled", "artwork": (3544, 190, 3904, 348), "processing": (3540, 188, 3908, 348)},
    {"variant": "cyan_alt", "artwork": (8, 310, 368, 468), "processing": (4, 308, 372, 468)},
    {"variant": "disabled_alt", "artwork": (384, 310, 744, 468), "processing": (380, 308, 748, 468)},
)


@dataclass(frozen=True)
class LoadedG1T:
    nested_slot: int
    g1t: atlas_codec.G1T


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256_file(path)}


def validate_pin(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is not a file: {path}")
    actual = file_spec(path)
    require(actual == dict(expected), f"{label} pin differs: expected={dict(expected)} actual={actual}")
    return actual


def nested_entries(blob: bytes, expected_resource_id: int) -> tuple[bytes, ...]:
    require(len(blob) >= 32 and blob[:4] == b"LINK", "nested resource is not LINK")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", blob, 4)
    require(count > 0 and table_offset == 32, "nested LINK header differs")
    require(resource_id == expected_resource_id, f"resource id {resource_id} != {expected_resource_id}")
    table_end = table_offset + count * 8
    require(aligned_table_end == (table_end + 31) & -32, "nested LINK alignment differs")
    pairs = [struct.unpack_from("<II", blob, table_offset + index * 8) for index in range(count)]
    require(pairs and pairs[0][0] >= aligned_table_end, "nested LINK data overlaps its table")
    entries: list[bytes] = []
    for index, (offset, size) in enumerate(pairs):
        end = offset + size
        next_offset = pairs[index + 1][0] if index + 1 < count else len(blob)
        require(aligned_table_end <= offset <= end <= next_offset <= len(blob), f"nested slot {index} bounds differ")
        entries.append(blob[offset:end])
    return tuple(entries)


def load_g1t(
    path: Path,
    outer_entry: int,
    resource_id: int,
    cache: dict[tuple[Path, int, int], LoadedG1T],
) -> LoadedG1T:
    key = (path, outer_entry, resource_id)
    if key in cache:
        return cache[key]
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"outer LINK identity failed: {path}")
    require(outer_entry < len(outer.entries), f"outer entry {outer_entry} absent: {path}")
    matches: list[LoadedG1T] = []
    for slot, entry in enumerate(nested_entries(outer.entries[outer_entry].data, resource_id)):
        try:
            _header, raw = lz4.decompress_wrapper(entry)
            parsed = atlas_codec.parse_g1t(raw)
        except (lz4.LZ4Error, atlas_codec.AtlasError):
            continue
        matches.append(LoadedG1T(slot, parsed))
    require(len(matches) == 1, f"expected one G1T wrapper, found {len(matches)}: {path}")
    cache[key] = matches[0]
    return matches[0]


def decode_rgba(texture: atlas_codec.Texture, label: str) -> np.ndarray:
    decoded = atlas_codec.decode_texture(texture)
    require(decoded is not None, f"{label} texture could not decode")
    return np.frombuffer(decoded, dtype=np.uint8).reshape(texture.height, texture.width, 4)


def rect(item: Mapping[str, int]) -> list[int]:
    return [int(item["x0"]), int(item["y0"]), int(item["x1"]), int(item["y1"])]


def rect_size(value: Sequence[int]) -> list[int]:
    return [int(value[2]) - int(value[0]), int(value[3]) - int(value[1])]


def bc_block_rect(value: Sequence[int]) -> list[int]:
    return [int(value[0]) // 4, int(value[1]) // 4, (int(value[2]) + 3) // 4, (int(value[3]) + 3) // 4]


def bc_pixel_rect(value: Sequence[int]) -> list[int]:
    blocks = bc_block_rect(value)
    return [coordinate * 4 for coordinate in blocks]


def centered_rect(artwork_rect: Sequence[int], cell_size: tuple[int, int]) -> list[int]:
    center_x = (int(artwork_rect[0]) + int(artwork_rect[2])) / 2.0
    center_y = (int(artwork_rect[1]) + int(artwork_rect[3])) / 2.0
    left = int(round(center_x - cell_size[0] / 2.0))
    top = int(round(center_y - cell_size[1] / 2.0))
    return [left, top, left + cell_size[0], top + cell_size[1]]


def placement(
    *,
    route: str,
    resolution: str,
    family: str,
    group: int,
    name: str,
    jp: str,
    ko: str,
    aliases: Sequence[str],
    state: int,
    artwork_rect: Sequence[int],
    processing_rect: Sequence[int] | None,
    component_index: int | None,
    provenance: str,
    state_variant: str | None = None,
) -> dict[str, Any]:
    value = [int(item) for item in artwork_rect]
    processing = value if processing_rect is None else [int(item) for item in processing_rect]
    return {
        "route": route,
        "resolution": resolution,
        "family": family,
        "group": group,
        "name": name,
        "jp": jp,
        "ko": ko,
        "aliases": list(aliases),
        "state": state,
        "state_variant": state_variant,
        "component_index": component_index,
        "artwork_rect": value,
        "artwork_size": rect_size(value),
        "artwork_bc_block_rect": bc_block_rect(value),
        "processing_rect": processing,
        "processing_size": rect_size(processing),
        "rect_provenance": provenance,
    }


def standard_components(atlas: np.ndarray, *, resolution: str) -> list[dict[str, int]]:
    detected = components(atlas[:, :, 3], 8)
    if resolution == "low":
        selected = [
            item for item in detected
            if 120 <= item["width"] <= 210 and 40 <= item["height"] <= 100 and item["y0"] < 700
        ]
        selected.sort(key=lambda item: (round(item["y0"] / 88), item["x0"]))
    else:
        selected = [
            item for item in detected
            if 240 <= item["width"] <= 400 and 60 <= item["height"] <= 200 and item["y0"] < 2300
        ]
    require(len(selected) == 120, f"{resolution} standard component count {len(selected)} != 120")
    expected_size = [180, 79] if resolution == "low" else [360, 158]
    require({tuple(rect_size(rect(item))) for item in selected} == {tuple(expected_size)}, f"{resolution} component geometry differs")
    return selected


def low_feature(atlas: np.ndarray, item: Mapping[str, int]) -> np.ndarray:
    x0, y0, x1, y1 = rect(item)
    sprite = atlas[y0:y1, x0:x1, :3].astype(np.float32)
    require(sprite.shape[:2] == (79, 180), f"low standard sprite geometry differs: {sprite.shape[:2]}")
    return np.concatenate((sprite[8:19, 32:160], sprite[60:71, 32:160]), axis=0).reshape(-1)


def low_standard_rows(atlas: np.ndarray) -> list[dict[str, Any]]:
    detected = standard_components(atlas, resolution="low")
    references = [low_feature(atlas, item) for item in detected[:6]]
    rows: list[dict[str, Any]] = []
    used: set[int] = set()
    for group, label in enumerate(STANDARD_LABELS):
        hints = LOW_COMPONENT_HINTS[str(label["name"])]
        buckets: dict[int, list[tuple[int, Mapping[str, int]]]] = {0: [], 1: [], 2: [], 3: []}
        for index in hints:
            used.add(index)
            vector = low_feature(atlas, detected[index])
            visual_class = int(np.argmin([np.linalg.norm(reference - vector) for reference in references]))
            require(visual_class in buckets, f"unexpected low visual class {visual_class}: {label['name']}")
            buckets[visual_class].append((index, detected[index]))
        require({key: len(value) for key, value in buckets.items()} == {0: 1, 1: 2, 2: 1, 3: 2}, f"low state buckets differ: {label['name']}")
        ordered = {
            0: buckets[0][0],
            1: buckets[1][0],
            2: buckets[2][0],
            3: buckets[3][0],
            4: buckets[1][1],
            5: buckets[3][1],
        }
        for state_index in range(6):
            component_index, item = ordered[state_index]
            rows.append(
                placement(
                    route="common_low",
                    resolution="low",
                    family="standard",
                    group=group,
                    name=str(label["name"]),
                    jp=str(label["jp"]),
                    ko=str(label["ko"]),
                    aliases=label["aliases"],
                    state=state_index + 1,
                    artwork_rect=rect(item),
                    processing_rect=centered_rect(rect(item), (192, 88)),
                    component_index=component_index,
                    provenance="detected_stock_alpha_component_plus_background_state_classification",
                )
            )
    require(used == set(range(120)), "low standard semantic mapping does not cover every component")
    return rows


def high_standard_rows(atlas: np.ndarray) -> list[dict[str, Any]]:
    detected = standard_components(atlas, resolution="high")
    rows: list[dict[str, Any]] = []
    for group, label in enumerate(STANDARD_LABELS):
        for state_index, item in enumerate(detected[group * 6 : (group + 1) * 6]):
            rows.append(
                placement(
                    route="common_high_standard",
                    resolution="high",
                    family="standard",
                    group=group,
                    name=str(label["name"]),
                    jp=str(label["jp"]),
                    ko=str(label["ko"]),
                    aliases=label["aliases"],
                    state=state_index + 1,
                    artwork_rect=rect(item),
                    processing_rect=centered_rect(rect(item), (376, 168)),
                    component_index=group * 6 + state_index,
                    provenance="detected_stock_alpha_component_in_verified_six_state_pack_order",
                )
            )
    return rows


def low_battle_rows(atlas: np.ndarray) -> list[dict[str, Any]]:
    selected = [
        item for item in components(atlas[:, :, 3], 8)
        if 240 <= item["width"] <= 260 and 60 <= item["height"] <= 90 and item["y0"] < 100
    ]
    selected.sort(key=lambda item: item["x0"])
    require(len(selected) == 7, f"low battle-start component count {len(selected)} != 7")
    return [
        placement(
            route="common_low",
            resolution="low",
            family="battle_start",
            group=0,
            name="battle_start",
            jp="開戦",
            ko="개전",
            aliases=[],
            state=state + 1,
            artwork_rect=rect(item),
            processing_rect=centered_rect(rect(item), (264, 88)),
            component_index=state,
            provenance="detected_stock_alpha_component_in_left_to_right_state_order",
        )
        for state, item in enumerate(selected)
    ]


def high_battle_rows(atlas: np.ndarray) -> list[dict[str, Any]]:
    selected = [
        item for item in components(atlas[:, :, 3], 8)
        if 450 <= item["width"] <= 530 and 130 <= item["height"] <= 170 and item["y0"] < 200
    ]
    selected.sort(key=lambda item: item["x0"])
    actual = [tuple(rect(item)) for item in selected]
    require(len(actual) == 7, f"high battle-start rectangle count differs: {actual}")
    for artwork, processing in zip(actual, HIGH_BATTLE_PROCESSING_RECTS):
        require(
            processing[0] <= artwork[0] < artwork[2] <= processing[2]
            and processing[1] <= artwork[1] < artwork[3] <= processing[3],
            f"high battle-start artwork escaped processing rectangle: {artwork} vs {processing}",
        )
    return [
        placement(
            route="common_high_battle",
            resolution="high",
            family="battle_start",
            group=0,
            name="battle_start",
            jp="開戦",
            ko="개전",
            aliases=[],
            state=state + 1,
            artwork_rect=actual[state],
            processing_rect=value,
            component_index=state,
            provenance="detected_stock_alpha_component_and_issue117_native_rect_cross_check",
        )
        for state, value in enumerate(HIGH_BATTLE_PROCESSING_RECTS)
    ]


def approve_all_rows(
    *,
    route: str,
    resolution: str,
    cells: Sequence[Mapping[str, Any]],
    provenance: str,
) -> list[dict[str, Any]]:
    return [
        placement(
            route=route,
            resolution=resolution,
            family="approve_all",
            group=0,
            name="approve_all",
            jp="全承認",
            ko=LABEL_APPROVE_ALL,
            aliases=[],
            state=state + 1,
            artwork_rect=item["artwork"],
            processing_rect=item["processing"],
            component_index=None,
            provenance=provenance,
            state_variant=str(item["variant"]),
        )
        for state, item in enumerate(cells)
    ]


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


CSV_FIELDS = (
    "route", "resolution", "family", "group", "name", "jp", "ko", "aliases", "state",
    "state_variant", "component_index", "artwork_rect", "artwork_size", "artwork_bc_block_rect",
    "processing_rect", "processing_size", "atlas_clip_rect", "boundary_clipped", "bc_block_rect", "bc_pixel_rect",
    "rect_provenance",
)


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        flattened: dict[str, Any] = {}
        for key in CSV_FIELDS:
            value = row.get(key)
            if isinstance(value, (list, dict)):
                flattened[key] = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            elif value is None:
                flattened[key] = ""
            else:
                flattened[key] = value
        writer.writerow(flattened)
    path.write_text(buffer.getvalue(), encoding="utf-8-sig", newline="")


def format_rect(value: Sequence[int]) -> str:
    return "[" + ",".join(str(item) for item in value) + "]"


def write_positions(path: Path, routes: Mapping[str, Mapping[str, Any]], rows: Sequence[Mapping[str, Any]]) -> None:
    lines = [
        "# 일반 버튼 전체 위치표 v1",
        "",
        "모든 상태 번호는 1부터 시작한다. 사각형은 `[left,top,right,bottom]`이고 오른쪽·아래쪽은 포함하지 않는다.",
        "BC 블록의 상세 좌표는 `ordinary_button_placements_v1.csv`를 사용한다.",
        "",
    ]
    route_order = [str(route["id"]) for route in ROUTES]
    for route_id in route_order:
        route = routes[route_id]
        route_rows = [row for row in rows if row["route"] == route_id]
        lines.extend(
            [
                f"## {route_id}",
                "",
                f"- 런타임 범위: `{route['runtime_scope']}`; 해상도: `{route['resolution']}`",
                f"- 경로: `{route['archive']}` / 바깥 `{route['outer_entry']}` / 중첩 `{route['nested_slot']}` / "
                f"리소스 `{route['resource_id']}` / 텍스처 `{route['texture_index']}`",
                f"- 텍스처: {route['dimensions'][0]}×{route['dimensions'][1]} {route['format']}; 배치 {route['placement_count']}개",
                "",
                "| 계열 | 그룹 | 이름 | 일본어 | 한국어 | 상태 | 원본 아트워크 사각형 1→N | 처리 사각형 1→N |",
                "|---|---:|---|---|---|---|---|---|",
            ]
        )
        grouped: dict[tuple[str, int], list[Mapping[str, Any]]] = {}
        for row in route_rows:
            grouped.setdefault((str(row["family"]), int(row["group"])), []).append(row)
        family_order = {"standard": 0, "battle_start": 1, "approve_all": 2}
        for key in sorted(grouped, key=lambda item: (family_order[item[0]], item[1])):
            states = sorted(grouped[key], key=lambda item: int(item["state"]))
            first = states[0]
            state_text = ", ".join(
                f"{row['state']}:{row['state_variant']}" if row["state_variant"] else str(row["state"])
                for row in states
            )
            rects = "; ".join(format_rect(row["artwork_rect"]) for row in states)
            processing = "; ".join(format_rect(row["processing_rect"]) for row in states)
            lines.append(
                f"| `{first['family']}` | {first['group']} | `{first['name']}` | {first['jp']} | "
                f"{first['ko']} | {state_text} | {rects} | {processing} |"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_root = args.source_root.resolve(strict=True)
    target_root = args.target_root.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    cache: dict[tuple[Path, int, int], LoadedG1T] = {}
    route_reports: dict[str, dict[str, Any]] = {}
    source_textures: dict[str, atlas_codec.Texture] = {}

    for route in ROUTES:
        route_id = str(route["id"])
        relative = str(route["relative_path"])
        archive_path = Path(relative)
        source_path = source_root / archive_path
        target_path = target_root / archive_path
        source_spec = validate_pin(source_path, ARCHIVE_PINS[relative]["source"], f"{route_id} source")
        target_spec = validate_pin(target_path, ARCHIVE_PINS[relative]["target"], f"{route_id} target")
        source = load_g1t(source_path, int(route["outer_entry"]), int(route["resource_id"]), cache)
        target = load_g1t(target_path, int(route["outer_entry"]), int(route["resource_id"]), cache)
        texture_index = int(route["texture_index"])
        require(texture_index < len(source.g1t.textures) and texture_index < len(target.g1t.textures), f"{route_id} texture absent")
        source_texture = source.g1t.textures[texture_index]
        target_texture = target.g1t.textures[texture_index]
        actual = (source_texture.format_code, source_texture.width, source_texture.height)
        expected = (int(route["format_code"]), *route["dimensions"])
        require(actual == expected, f"{route_id} source texture contract differs: {actual} != {expected}")
        require(
            (target_texture.format_code, target_texture.width, target_texture.height) == actual,
            f"{route_id} source/target texture geometry differs",
        )
        require(source.nested_slot == target.nested_slot == 0, f"{route_id} nested slot differs")
        source_textures[route_id] = source_texture
        route_reports[route_id] = {
            "runtime_scope": route["runtime_scope"],
            "resolution": route["resolution"],
            "archive": relative,
            "outer_entry": route["outer_entry"],
            "nested_slot": source.nested_slot,
            "resource_id": route["resource_id"],
            "texture_index": texture_index,
            "format_code": f"0x{source_texture.format_code:02X}",
            "format": "BC3/DXT5" if source_texture.format_code == 0x5B else "BC7",
            "dimensions": [source_texture.width, source_texture.height],
            "placement_count": route["placement_count"],
            "source": source_spec,
            "target": target_spec,
        }

    low = decode_rgba(source_textures["common_low"], "common_low")
    high_standard = decode_rgba(source_textures["common_high_standard"], "common_high_standard")
    high_battle = decode_rgba(source_textures["common_high_battle"], "common_high_battle")
    rows = (
        low_standard_rows(low)
        + low_battle_rows(low)
        + high_standard_rows(high_standard)
        + high_battle_rows(high_battle)
        + approve_all_rows(
            route="pk_low_approve_all",
            resolution="low",
            cells=APPROVE_ALL_LOW_CELLS,
            provenance="independently_detected_native_low_bc7_cells_cross_locale_verified",
        )
        + approve_all_rows(
            route="pk_high_approve_all",
            resolution="high",
            cells=APPROVE_ALL_HIGH_CELLS,
            provenance="verified_native_high_bc7_cells_cross_locale",
        )
    )
    require(len(rows) == 266, f"placement count {len(rows)} != 266")
    require(
        len({(row["route"], row["family"], row["group"], row["state"]) for row in rows}) == len(rows),
        "placement keys are not unique",
    )
    for route in ROUTES:
        route_rows = [row for row in rows if row["route"] == route["id"]]
        require(len(route_rows) == route["placement_count"], f"{route['id']} placement count differs")
        width, height = route["dimensions"]
        for row in route_rows:
            px0, py0, px1, py1 = row["processing_rect"]
            require(px0 < px1 and py0 < py1, f"{route['id']} processing rectangle is empty")
            clipped = [max(0, px0), max(0, py0), min(width, px1), min(height, py1)]
            require(clipped[0] < clipped[2] and clipped[1] < clipped[3], f"{route['id']} processing rectangle misses atlas")
            row["atlas_clip_rect"] = clipped
            row["boundary_clipped"] = clipped != row["processing_rect"]
            row["bc_block_rect"] = bc_block_rect(clipped)
            row["bc_pixel_rect"] = bc_pixel_rect(clipped)
            for field in ("artwork_rect", "atlas_clip_rect", "bc_pixel_rect"):
                x0, y0, x1, y1 = row[field]
                require(
                    0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height,
                    f"{route['id']} {field} is out of bounds: {row['name']} state {row['state']} {row[field]}",
                )

    catalog = {
        "schema": SCHEMA,
        "snapshot": SNAPSHOT,
        "coverage": {
            "physical_archives": 4,
            "texture_routes": 5,
            "logical_groups": 22,
            "standard_groups": 20,
            "standard_states_each": 6,
            "battle_start_groups": 1,
            "battle_start_states": 7,
            "approve_all_groups": 1,
            "approve_all_routes": 2,
            "approve_all_states_each": 6,
            "approve_all_placements": 12,
            "placements": 266,
        },
        "coordinate_contract": {
            "origin": "zero_based",
            "rect_order": ["left", "top", "right", "bottom"],
            "right_and_bottom_exclusive": True,
            "alpha_threshold": 8,
            "bc_block_size": [4, 4],
            "artwork_rect_meaning": "stock source alpha component, except verified BC7 logical cells",
            "processing_rect_meaning": "verified replacement canvas: centered native cell for standard/low battle, issue117 native target for high battle, logical cell for BC7",
            "atlas_clip_rect_meaning": "processing_rect intersected with the physical atlas bounds",
            "artwork_bc_block_rect_meaning": "block-index rectangle intersecting stock artwork_rect",
            "bc_block_rect_meaning": "block-index rectangle intersecting atlas_clip_rect",
            "bc_pixel_rect_meaning": "pixel rectangle covered by bc_block_rect",
        },
        "route_order": [route["id"] for route in ROUTES],
        "routes": route_reports,
        "labels": [dict(label) for label in STANDARD_LABELS]
        + [
            {"name": "battle_start", "jp": "開戦", "ko": "개전", "aliases": []},
            {"name": "approve_all", "jp": "全承認", "ko": LABEL_APPROVE_ALL, "aliases": []},
        ],
        "placements": rows,
    }
    write_json(output / "ordinary_button_catalog_v1.json", catalog)
    write_csv(output / "ordinary_button_placements_v1.csv", rows)
    write_positions(output / "ORDINARY_BUTTON_POSITIONS_KO.md", route_reports, rows)
    return catalog


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--source-root", type=Path, required=True)
    value.add_argument("--target-root", type=Path, required=True)
    value.add_argument("--output", type=Path, default=WORKSTREAM)
    return value


def main() -> int:
    args = parser().parse_args()
    catalog = build(args)
    print(json.dumps({"schema": catalog["schema"], **catalog["coverage"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
