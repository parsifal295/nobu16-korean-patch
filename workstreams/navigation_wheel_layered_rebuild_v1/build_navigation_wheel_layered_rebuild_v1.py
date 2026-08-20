#!/usr/bin/env python3
"""Rebuild all navigation-wheel cells from stock body/icon pixels plus B text.

This stage is static and PNG-only.  It does not encode BC3, rebuild an archive,
touch the patcher bundle, or write to the Steam installation.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
WORKSPACE = REPO.parent.parent
CATALOG_WS = REPO / "workstreams" / "navigation_wheel_atlas_catalog_v1"
PILOT_WS = REPO / "workstreams" / "navigation_wheel_layered_pilot_v1"
TEXT_WS = REPO / "workstreams" / "navigation_wheel_text_candidates_v1"
TOOLS = REPO / "tools"
for import_root in (TOOLS, CATALOG_WS, PILOT_WS, TEXT_WS):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import build_navigation_wheel_atlas_catalog_v1 as catalog  # noqa: E402
import build_navigation_wheel_layered_pilot_v1 as pilot  # noqa: E402
import build_navigation_wheel_text_candidates_v1 as text_candidates  # noqa: E402

try:
    import cv2  # type: ignore
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, __version__ as pillow_version
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("NumPy, OpenCV, and Pillow are required") from exc


SCHEMA = "nobu16.kr.navigation-wheel-layered-rebuild.v1"
GENERATION_POLICY = "forbidden-and-not-used"
ROUTE_ORDER = ("base_low", "base_high", "pk_low", "pk_high")
FAMILY_ORDER = ("base_detail", "base_main", "pk_detail", "pk_main")
STATE_COUNT = 6
LOW_OVERSAMPLE = 8
HIGH_OVERSAMPLE = 4
TRACKING_EM = -0.035
FONT_SHA256 = pilot.FONT_SHA256
UI_FONT_SHA256 = pilot.UI_FONT_SHA256
FONT_PATH = pilot.DEFAULT_FONT
UI_FONT_PATH = pilot.DEFAULT_UI_FONT
JP_SOURCE_ROOT = pilot.DEFAULT_JP_SOURCE_ROOT
OFFICIAL_ROOT = pilot.DEFAULT_OFFICIAL_ROOT
INPUT_PINS = pilot.DEFAULT_INPUT_PINS
MAPPING_PATH = pilot.DEFAULT_MAPPING


class RebuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RebuildError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "size": path.stat().st_size, "sha256": sha256_file(path)}


def validate_file(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is not a file: {path}")
    actual = file_spec(path)
    require(
        actual["size"] == int(expected["size"]) and actual["sha256"] == str(expected["sha256"]).upper(),
        f"{label} pin differs: expected={dict(expected)} actual={actual}",
    )
    return actual


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class TypeContract:
    route: str
    family: str
    cell_size: tuple[int, int]
    ink_height: int
    ink_bottom: int
    safe_ink_width: int
    stroke_radius: float
    outer_radius: float
    outer_soften: float


TYPE_CONTRACTS = {
    ("base_low", "base_detail"): TypeContract("base_low", "base_detail", (100, 95), 21, 85, 88, 1.4, 3.0, 0.5),
    ("base_low", "base_main"): TypeContract("base_low", "base_main", (104, 104), 24, 94, 92, 1.4, 3.0, 0.5),
    ("base_high", "base_detail"): TypeContract("base_high", "base_detail", (200, 190), 42, 170, 176, 2.8, 6.0, 1.0),
    ("base_high", "base_main"): TypeContract("base_high", "base_main", (208, 208), 48, 188, 184, 2.8, 6.0, 1.0),
    ("pk_low", "pk_detail"): TypeContract("pk_low", "pk_detail", (104, 96), 21, 83, 92, 1.4, 3.0, 0.5),
    ("pk_low", "pk_main"): TypeContract("pk_low", "pk_main", (104, 96), 21, 83, 92, 1.4, 3.0, 0.5),
    ("pk_high", "pk_detail"): TypeContract("pk_high", "pk_detail", (200, 184), 42, 162, 176, 2.8, 6.0, 1.0),
    ("pk_high", "pk_main"): TypeContract("pk_high", "pk_main", (204, 188), 42, 165, 180, 2.8, 6.0, 1.0),
}

# These are language-independent submenu direction markers embedded beside a
# small set of Japanese labels.  Their tight rectangles are in low-resolution
# logical-cell coordinates; base_high scales them by two.  They are not text
# and must survive the Japanese-label cleanup byte-for-byte.
NON_TEXT_MARKERS_LOW: dict[tuple[str, int], tuple[str, tuple[int, int, int, int]]] = {
    ("base_detail", 33): ("right", (72, 71, 86, 80)),
    ("base_detail", 34): ("right", (75, 69, 82, 82)),
    ("base_detail", 35): ("right", (73, 72, 85, 80)),
    ("base_detail", 36): ("left", (18, 69, 25, 83)),
    ("base_main", 1): ("right", (81, 77, 89, 90)),
    ("base_main", 2): ("left", (15, 77, 23, 90)),
    ("base_main", 3): ("left", (15, 77, 23, 90)),
    ("base_main", 4): ("right", (81, 77, 89, 90)),
}


def route_specs() -> dict[str, dict[str, Any]]:
    result = {str(item["id"]): dict(item) for item in catalog.ROUTES}
    require(tuple(result) == ROUTE_ORDER, f"catalog route order differs: {tuple(result)}")
    return result


def family_names(route: Mapping[str, Any]) -> tuple[str, ...]:
    return ("base_detail", "base_main") if route["edition"] == "base" else ("pk_detail", "pk_main")


def record_groups(family: str) -> list[list[int]]:
    if family == "base_detail":
        return catalog.detail_group_records()
    if family == "base_main":
        return [[252 + group * 6 + state for state in range(STATE_COUNT)] for group in range(5)]
    if family == "pk_detail":
        return [list(range(0, 6))] + [list(range(index, index + 6)) for index in range(12, 78, 6)]
    if family == "pk_main":
        return [list(range(6, 12))]
    raise RebuildError(f"unknown wheel family: {family}")


def labels_by_family(mapping: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_group: dict[int, dict[str, Any]] = {}
    for item in mapping["groups"]:
        for target in item["targets"]:
            target = int(target)
            require(target not in by_group, f"base detail group mapped twice: {target}")
            by_group[target] = dict(item)
    require(set(by_group) == set(range(57)), "base detail mapping does not cover 0..56")
    return {
        "base_detail": [by_group[index] for index in range(57)],
        "base_main": [dict(item) for item in catalog.BASE_MAIN_LABELS],
        "pk_detail": [dict(item) for item in catalog.PK_DETAIL_LABELS],
        "pk_main": [dict(catalog.PK_MAIN_LABEL)],
    }


def raw_cell_rect(record: Sequence[int], family: str, scale: int) -> tuple[int, int, int, int]:
    x, y, width, height, _third = (int(value) for value in record)
    if family == "base_detail":
        return x - 2 * scale, y - 6 * scale, x - 2 * scale + 100 * scale, y - 6 * scale + 95 * scale
    if family == "base_main":
        return x, y, x + width, y + height
    return x - 4, y - 4, x + width + 4, y + height + 4


def centered_canvas(cell: "np.ndarray[Any, Any]", size: tuple[int, int]) -> "np.ndarray[Any, Any]" | None:
    target_width, target_height = size
    if cell.shape[1] > target_width or cell.shape[0] > target_height:
        return None
    result = np.zeros((target_height, target_width, 4), dtype=np.uint8)
    x = (target_width - cell.shape[1]) // 2
    y = (target_height - cell.shape[0]) // 2
    result[y : y + cell.shape[0], x : x + cell.shape[1]] = cell
    return result


def load_route_cells(
    path: Path,
    route: Mapping[str, Any],
    *,
    keep_atlas: bool,
) -> tuple[dict[str, list["np.ndarray[Any, Any]" | None]], dict[str, list[list[tuple[int, int, int, int]]]], "np.ndarray[Any, Any]" | None, dict[str, Any]]:
    loaded = catalog.load_resource(path, route)
    expected_records = 474 if route["edition"] == "base" else 82
    records = catalog.parse_layout(loaded.table_padding, expected_records)
    decoded = catalog.atlas_codec.decode_texture(loaded.texture)
    require(decoded is not None, f"BC3 decode failed: {path}")
    atlas = np.frombuffer(decoded, dtype=np.uint8).reshape(loaded.texture.height, loaded.texture.width, 4).copy()
    families: dict[str, list[np.ndarray[Any, Any] | None]] = {}
    rects: dict[str, list[list[tuple[int, int, int, int]]]] = {}
    excluded: list[dict[str, Any]] = []
    for family in family_names(route):
        contract = TYPE_CONTRACTS[(str(route["id"]), family)]
        family_cells: list[np.ndarray[Any, Any] | None] = []
        family_rects: list[list[tuple[int, int, int, int]]] = []
        for group, indices in enumerate(record_groups(family)):
            states: list[np.ndarray[Any, Any]] = []
            state_rects: list[tuple[int, int, int, int]] = []
            reason: str | None = None
            for record_index in indices:
                rect = raw_cell_rect(records[record_index], family, int(route["scale"]))
                x0, y0, x1, y1 = rect
                clip = (max(0, x0), max(0, y0), min(atlas.shape[1], x1), min(atlas.shape[0], y1))
                require(clip[0] < clip[2] and clip[1] < clip[3], f"cell misses atlas: {path} {family}:{group}")
                cell = atlas[clip[1] : clip[3], clip[0] : clip[2]].copy()
                normalized = centered_canvas(cell, contract.cell_size)
                if normalized is None:
                    reason = f"source cell {cell.shape[1]}x{cell.shape[0]} exceeds target {contract.cell_size[0]}x{contract.cell_size[1]}"
                    break
                states.append(normalized)
                state_rects.append(rect)
            if reason is not None:
                family_cells.append(None)
                family_rects.append([])
                excluded.append({"family": family, "group": group, "reason": reason})
            else:
                require(len(states) == STATE_COUNT, f"state count differs: {path} {family}:{group}")
                family_cells.append(np.stack(states))
                family_rects.append(state_rects)
        families[family] = family_cells
        rects[family] = family_rects
    report = {
        "nested_slot": loaded.nested_slot,
        "texture_dimensions": [loaded.texture.width, loaded.texture.height],
        "format_code": f"0x{loaded.texture.format_code:02X}",
        "layout_table_sha256": sha256_bytes(loaded.table_padding),
        "layout_record_count": len(records),
        "geometry_exclusions": excluded,
    }
    return families, rects, atlas if keep_atlas else None, report


def state_features(states: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    height = states.shape[1]
    upper = states[:, : round(height * 0.58)]
    result: list[list[float]] = []
    for state in upper:
        active = state[..., 3] >= 48
        values = state[active].astype(np.float32)
        require(len(values) > 0, "state feature region is empty")
        alpha = values[:, 3:4] / 255.0
        premul = values[:, :3] * alpha
        result.append([
            *premul.mean(axis=0).tolist(),
            *np.median(premul, axis=0).tolist(),
            float(values[:, 3].mean()),
        ])
    return np.asarray(result, dtype=np.float32)


def align_states(reference: "np.ndarray[Any, Any]", donor: "np.ndarray[Any, Any]") -> tuple["np.ndarray[Any, Any]", list[int], float]:
    reference_features = state_features(reference)
    donor_features = state_features(donor)
    best: tuple[float, tuple[int, ...]] | None = None
    for permutation in itertools.permutations(range(STATE_COUNT)):
        delta = reference_features - donor_features[list(permutation)]
        cost = float(np.square(delta).sum())
        if best is None or cost < best[0]:
            best = (cost, permutation)
    require(best is not None, "state alignment failed")
    return donor[list(best[1])], [int(index) + 1 for index in best[1]], round(best[0], 3)


def label_core_mask(states: "np.ndarray[Any, Any]", *, require_nonempty: bool = True) -> "np.ndarray[Any, Any]":
    height, width = states.shape[1:3]
    scan_y = round(height * 56 / 95)
    minimum_bottom = round(height * 68 / 95)
    y_grid = np.arange(height)[:, None]
    rgb = states[..., :3].astype(np.float32)
    alpha = states[..., 3].astype(np.float32) / 255.0
    light = rgb.mean(axis=3) * alpha
    core = (
        (y_grid >= scan_y)
        & (alpha[0] > 0.08)
        & (light[0] < 160)
        & (light[1] > 135)
        & (light[2] > 125)
        & (light[3] < 135)
        & ((light[1] - light[0]) > 35)
        & ((light[2] - light[3]) > 25)
    )
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(core.astype(np.uint8), 8)
    kept = np.zeros((height, width), dtype=np.uint8)
    for index in range(1, count):
        _x, y, _w, component_height, area = (int(value) for value in stats[index])
        if area >= 1 and y >= scan_y and y + component_height >= minimum_bottom:
            kept[labels == index] = 255
    if require_nonempty:
        require(bool(np.any(kept)), "label core is empty")
    return kept


def dilate(mask: "np.ndarray[Any, Any]", kernel_size: int) -> "np.ndarray[Any, Any]":
    require(kernel_size >= 1 and kernel_size % 2 == 1, f"invalid dilation kernel: {kernel_size}")
    if kernel_size == 1:
        return mask.copy()
    return cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)))


def bbox(mask: "np.ndarray[Any, Any]") -> list[int] | None:
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def split_text_and_marker_core(
    core: "np.ndarray[Any, Any]",
    family: str,
    group: int,
    scale: int,
) -> tuple["np.ndarray[Any, Any]", "np.ndarray[Any, Any]", "np.ndarray[Any, Any]", dict[str, Any] | None]:
    spec = NON_TEXT_MARKERS_LOW.get((family, group))
    empty = np.zeros_like(core, dtype=np.uint8)
    if spec is None:
        return core, empty, empty.astype(bool), None
    side, low_rect = spec
    rect = tuple(int(value * scale) for value in low_rect)
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats((core > 0).astype(np.uint8), 8)
    marker = np.zeros_like(core, dtype=np.uint8)
    components: list[dict[str, Any]] = []
    rx0, ry0, rx1, ry1 = rect
    for index in range(1, count):
        x, y, width, height, area = (int(value) for value in stats[index])
        component_rect = (x, y, x + width, y + height)
        intersects = component_rect[0] < rx1 and component_rect[2] > rx0 and component_rect[1] < ry1 and component_rect[3] > ry0
        if intersects:
            marker[labels == index] = 255
            components.append({"bbox": list(component_rect), "pixels": area})
    require(len(components) == 1, f"non-text marker component coverage differs: {family}:{group} {components}")
    text = core.copy()
    text[marker > 0] = 0
    require(bool(np.any(text)), f"marker split removed the entire text core: {family}:{group}")
    marker_bbox = bbox(marker)
    require(marker_bbox is not None, f"marker bbox is empty: {family}:{group}")
    cleanup_kernel = 10 * scale + 1
    protected = dilate(marker, cleanup_kernel) > 0
    if side == "right":
        cutoff = max(0, marker_bbox[0] - scale)
        protected[:, :cutoff] = False
    else:
        cutoff = min(core.shape[1], marker_bbox[2] + scale)
        protected[:, cutoff:] = False
    return text, marker, protected, {
        "side": side,
        "contract_rect": list(rect),
        "core_bbox": marker_bbox,
        "core_pixels": int(np.count_nonzero(marker)),
        "protected_bbox": bbox(protected),
        "protected_pixels": int(np.count_nonzero(protected)),
    }


def canonical_rgba(values: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    rgba = values.astype(np.uint16)
    alpha = rgba[..., 3:4]
    premul = (rgba[..., :3] * alpha + 127) // 255
    return np.concatenate((premul, alpha), axis=-1)


def to_premul(values: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    rgba = values.astype(np.float32)
    alpha = rgba[..., 3:4] / 255.0
    return np.concatenate((rgba[..., :3] * alpha, rgba[..., 3:4]), axis=-1)


def to_straight(values: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    values = np.nan_to_num(values, nan=0.0, posinf=255.0, neginf=0.0)
    alpha = np.clip(values[..., 3:4], 0, 255)
    rgb = np.zeros_like(values[..., :3])
    nonzero = alpha[..., 0] > 0
    rgb[nonzero] = values[..., :3][nonzero] / (alpha[nonzero] / 255.0)
    return np.concatenate((np.clip(rgb, 0, 255), alpha), axis=-1).round().astype(np.uint8)


def donor_template(
    samples: list["np.ndarray[Any, Any]"],
    cores: list["np.ndarray[Any, Any]"],
    required: "np.ndarray[Any, Any]",
    scale: int,
) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    require(len(samples) == len(cores) and samples, "donor sample/core coverage differs")
    matrix = np.stack(samples)
    height, width = required.shape
    result = np.full((STATE_COUNT, height, width, 4), np.nan, dtype=np.float32)
    unresolved = required.copy()
    stage_rows: list[dict[str, Any]] = []
    for radius in (3 * scale, 2 * scale, 1 * scale, 0):
        kernel = radius * 2 + 1
        masks = np.stack([(dilate(core, kernel) > 0) for core in cores])
        ys, xs = np.nonzero(unresolved)
        if not len(xs):
            stage_rows.append({"kernel": kernel, "requested_pixels": 0, "resolved_pixels": 0, "remaining_pixels": 0})
            continue
        allowed = ~masks[:, ys, xs]
        support = allowed.sum(axis=0)
        selectable = support > 0
        selected_y, selected_x = ys[selectable], xs[selectable]
        selected_allowed = allowed[:, selectable]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            for state in range(STATE_COUNT):
                values = to_premul(matrix[:, state, selected_y, selected_x, :])
                values[~selected_allowed] = np.nan
                result[state, selected_y, selected_x, :] = np.nanmedian(values, axis=0)
        unresolved[selected_y, selected_x] = False
        stage_rows.append({
            "kernel": kernel,
            "requested_pixels": int(len(xs)),
            "resolved_pixels": int(len(selected_x)),
            "remaining_pixels": int(np.count_nonzero(unresolved)),
            "support_min_for_resolved": int(support[selectable].min()) if np.any(selectable) else None,
            "support_max_for_resolved": int(support[selectable].max()) if np.any(selectable) else None,
        })
    nearest_copy_pixels = int(np.count_nonzero(unresolved))
    if nearest_copy_pixels:
        resolved_coords = np.argwhere(required & ~unresolved)
        missing_coords = np.argwhere(unresolved)
        require(len(resolved_coords) > 0, "no donor pixels exist for nearest-copy completion")
        for y, x in missing_coords:
            distances = np.square(resolved_coords[:, 0] - y) + np.square(resolved_coords[:, 1] - x)
            source_y, source_x = resolved_coords[int(np.argmin(distances))]
            result[:, y, x, :] = result[:, source_y, source_x, :]
        unresolved[:] = False
    require(bool(np.all(np.isfinite(result[:, required]))), "donor template contains unresolved pixels")
    return to_straight(result), {
        "samples": len(samples),
        "required_pixels": int(np.count_nonzero(required)),
        "stages": stage_rows,
        "nearest_actual_donor_median_pixel_copies": nearest_copy_pixels,
        "interpolation_used": False,
    }


def odd_filter_size(radius: float, oversample: int) -> int:
    return max(1, round(radius * oversample)) * 2 + 1


def render_fill_mask(
    text: str,
    contract: TypeContract,
    font_path: Path,
    oversample: int,
) -> tuple[Image.Image, dict[str, Any]]:
    candidate = text_candidates.Candidate("b_seoul_hangang_eb", "B", "selected", font_path, FONT_SHA256, None, TRACKING_EM)
    target_height = contract.ink_height * oversample
    low, high = 4 * oversample, 160 * oversample
    best: tuple[int, Image.Image, int] | None = None
    while low <= high:
        size = (low + high) // 2
        font = text_candidates.load_font(candidate, size)
        mask = text_candidates.render_chars(text, font, TRACKING_EM * size)
        delta = abs(mask.height - target_height)
        if best is None or delta < best[0]:
            best = (delta, mask, size)
        if mask.height < target_height:
            low = size + 1
        elif mask.height > target_height:
            high = size - 1
        else:
            break
    require(best is not None, f"font-size search failed: {text}")
    _delta, mask, font_size = best
    if mask.height != target_height:
        mask = mask.resize((max(1, round(mask.width * target_height / mask.height)), target_height), Image.Resampling.LANCZOS)
    natural_width = mask.width
    maximum_width = contract.safe_ink_width * oversample
    horizontal_scale = min(1.0, maximum_width / natural_width)
    if horizontal_scale < 1.0:
        mask = mask.resize((maximum_width, mask.height), Image.Resampling.LANCZOS)
    require(horizontal_scale >= 0.86, f"label requires excessive condensation: {contract.route} {contract.family} {text} {horizontal_scale}")
    return mask, {
        "font_size_oversampled_px": font_size,
        "natural_fill_width_oversampled_px": natural_width,
        "final_fill_size_oversampled_px": [mask.width, mask.height],
        "horizontal_fit_scale": round(horizontal_scale, 6),
    }


def colored(mask: Image.Image, rgba: tuple[int, int, int, int]) -> Image.Image:
    result = Image.new("RGBA", mask.size, rgba)
    if rgba[3] == 255:
        result.putalpha(mask)
    else:
        result.putalpha(mask.point([round(value * rgba[3] / 255) for value in range(256)]))
    return result


def render_layers(text: str, contract: TypeContract, font_path: Path) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    oversample = LOW_OVERSAMPLE if contract.route.endswith("low") else HIGH_OVERSAMPLE
    fill, metrics = render_fill_mask(text, contract, font_path, oversample)
    size = (contract.cell_size[0] * oversample, contract.cell_size[1] * oversample)
    fill_cell = Image.new("L", size, 0)
    x = (size[0] - fill.width) // 2
    y = contract.ink_bottom * oversample - fill.height
    fill_cell.paste(fill, (x, y))
    stroke = fill_cell.filter(ImageFilter.MaxFilter(odd_filter_size(contract.stroke_radius, oversample)))
    outer = fill_cell.filter(ImageFilter.MaxFilter(odd_filter_size(contract.outer_radius, oversample)))
    outer = outer.filter(ImageFilter.GaussianBlur(contract.outer_soften * oversample))
    layers: list[np.ndarray[Any, Any]] = []
    states: list[dict[str, Any]] = []
    scale = 1 if contract.route.endswith("low") else 2
    for palette in pilot.STATE_PALETTES:
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        layer.alpha_composite(colored(outer, palette.outer))
        layer.alpha_composite(colored(stroke, palette.stroke))
        layer.alpha_composite(colored(fill_cell, palette.fill))
        native = layer.resize(contract.cell_size, Image.Resampling.LANCZOS)
        values = np.asarray(native).copy()
        layer_bbox = bbox(values[..., 3] > 0)
        require(layer_bbox is not None, f"rendered label is empty: {text}")
        require(layer_bbox[0] >= 4 * scale and layer_bbox[2] <= contract.cell_size[0] - 4 * scale, f"horizontal safety margin failed: {text} {layer_bbox}")
        require(layer_bbox[3] <= contract.cell_size[1] - 2 * scale, f"bottom safety margin failed: {text} {layer_bbox}")
        layers.append(values)
        states.append({"state": palette.state, "role": palette.role, "bbox": layer_bbox, "alpha_pixels": int(np.count_nonzero(values[..., 3]))})
    return np.stack(layers), {**metrics, "oversample": oversample, "states": states}


def alpha_composite(base: "np.ndarray[Any, Any]", overlay: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    return np.asarray(Image.alpha_composite(Image.fromarray(base), Image.fromarray(overlay))).copy()


def component_bbox(values: "np.ndarray[Any, Any]") -> list[int] | None:
    return bbox(values[..., 3] >= 8)


def contact_sheet_pages(
    output: Path,
    route_id: str,
    family: str,
    labels: list[Mapping[str, Any]],
    source_groups: list["np.ndarray[Any, Any]"],
    composite_groups: list["np.ndarray[Any, Any]"],
    ui_font_path: Path,
) -> list[Path]:
    pages: list[Path] = []
    chunk_size = 20
    display_size = (100, 95)
    zoom = 2
    cell_width, cell_height = display_size[0] * zoom, display_size[1] * zoom
    gap = 10
    left = 180
    columns = ((0, "JP 상태1"), (0, "B 상태1"), (1, "JP 상태2"), (1, "B 상태2"), (3, "JP 상태4"), (3, "B 상태4"))
    title_font = ImageFont.truetype(str(ui_font_path), 17)
    title_font.set_variation_by_axes([700])
    small_font = ImageFont.truetype(str(ui_font_path), 14)
    small_font.set_variation_by_axes([600])
    for page_index, start in enumerate(range(0, len(labels), chunk_size), 1):
        end = min(len(labels), start + chunk_size)
        rows = end - start
        width = left + len(columns) * (cell_width + gap) + gap
        height = 42 + rows * (cell_height + gap) + 38
        sheet = Image.new("RGB", (width, height), (25, 27, 31))
        draw = ImageDraw.Draw(sheet)
        for column, (_state, title) in enumerate(columns):
            draw.text((left + column * (cell_width + gap) + 55, 9), title, font=small_font, fill=(235, 236, 238))
        for row, group in enumerate(range(start, end)):
            y = 42 + row * (cell_height + gap)
            label = labels[group]
            draw.text((8, y + 74), f"{group:02d} {label['name']}\n{label['ko']}", font=small_font, fill=(224, 227, 231), spacing=2)
            for column, (state, _title) in enumerate(columns):
                matrix = source_groups[group] if column % 2 == 0 else composite_groups[group]
                image = Image.fromarray(matrix[state])
                background = Image.new("RGB", image.size, (0, 255, 0))
                background.paste(image, (0, 0), image)
                background = background.resize(display_size, Image.Resampling.LANCZOS).resize((cell_width, cell_height), Image.Resampling.NEAREST)
                x = left + column * (cell_width + gap)
                sheet.paste(background, (x, y))
        draw.text((8, height - 28), f"{route_id} / {family} / groups {start}..{end - 1}", font=small_font, fill=(168, 175, 186))
        path = output / "contact" / f"{route_id}_{family}_{page_index:02d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(path, optimize=False, compress_level=9)
        pages.append(path)
    return pages


def build_family(
    *,
    output: Path,
    route: Mapping[str, Any],
    family: str,
    labels: list[Mapping[str, Any]],
    locale_cells: Mapping[str, list["np.ndarray[Any, Any]" | None]],
    jp_rects: list[list[tuple[int, int, int, int]]],
    candidate_atlas: "np.ndarray[Any, Any]",
    atlas_written: "np.ndarray[Any, Any]",
    font_path: Path,
    ui_font_path: Path,
) -> tuple[dict[str, Any], list[Path], list[dict[str, Any]]]:
    route_id = str(route["id"])
    contract = TYPE_CONTRACTS[(route_id, family)]
    jp_groups = locale_cells["JP"]
    require(all(group is not None for group in jp_groups), f"JP source has excluded groups: {route_id} {family}")
    source_groups = [group for group in jp_groups if group is not None]
    require(len(source_groups) == len(labels) == len(jp_rects), f"group/label/rect coverage differs: {route_id} {family}")

    scale = int(route["scale"])
    donor_samples: list[np.ndarray[Any, Any]] = []
    donor_cores: list[np.ndarray[Any, Any]] = []
    exclusions: list[dict[str, Any]] = []
    alignments: list[dict[str, Any]] = []
    for locale in ("JP", "SC", "TC", "EN"):
        for group, donor in enumerate(locale_cells[locale]):
            if donor is None:
                exclusions.append({"locale": locale, "group": group, "reason": "geometry"})
                continue
            if locale == "JP":
                aligned, permutation, cost = donor, list(range(1, 7)), 0.0
            else:
                aligned, permutation, cost = align_states(source_groups[group], donor)
            core = label_core_mask(aligned, require_nonempty=False)
            if not np.any(core):
                exclusions.append({"locale": locale, "group": group, "reason": "empty-label-core"})
                continue
            donor_samples.append(aligned)
            donor_cores.append(core)
            if permutation != list(range(1, 7)):
                alignments.append({"locale": locale, "group": group, "permutation_target_to_source": permutation, "feature_cost": cost})

    cleanup_kernel = 10 * scale + 1
    marker_protections: list[np.ndarray[Any, Any]] = []
    marker_reports: list[dict[str, Any] | None] = []
    cleanup_masks: list[np.ndarray[Any, Any]] = []
    for group, source in enumerate(source_groups):
        raw_core = label_core_mask(source)
        text_core, _marker_core, marker_protected, marker_report = split_text_and_marker_core(
            raw_core, family, group, scale
        )
        cleanup = dilate(text_core, cleanup_kernel) > 0
        cleanup &= ~marker_protected
        require(bool(np.any(cleanup)), f"cleanup mask is empty: {route_id} {family}:{group}")
        marker_protections.append(marker_protected)
        marker_reports.append(marker_report)
        cleanup_masks.append(cleanup)
    required = np.logical_or.reduce(cleanup_masks)
    template, template_report = donor_template(donor_samples, donor_cores, required, scale)

    layer_cache: dict[str, tuple[np.ndarray[Any, Any], dict[str, Any]]] = {}
    layer_files: list[Path] = []
    for item in labels:
        text = str(item["ko"])
        if text in layer_cache:
            continue
        layers, report = render_layers(text, contract, font_path)
        layer_cache[text] = (layers, report)
        layer_dir = output / "text_layers" / route_id / family / str(item["name"])
        layer_dir.mkdir(parents=True, exist_ok=True)
        for state in range(STATE_COUNT):
            path = layer_dir / f"state_{state + 1}.png"
            Image.fromarray(layers[state]).save(path, optimize=False, compress_level=9)
            layer_files.append(path)

    composite_groups: list[np.ndarray[Any, Any]] = []
    cell_files: list[Path] = []
    rows: list[dict[str, Any]] = []
    residual_total = 0
    family_blocks: set[tuple[int, int]] = set()
    for group, (source, cleanup, marker_protected, marker_report, label, rects) in enumerate(
        zip(source_groups, cleanup_masks, marker_protections, marker_reports, labels, jp_rects)
    ):
        clean = source.copy()
        clean[:, cleanup, :] = template[:, cleanup, :]
        outside_clean_changes = int(np.count_nonzero(np.any(clean[:, ~cleanup] != source[:, ~cleanup], axis=-1)))
        require(outside_clean_changes == 0, f"clean plate escaped cleanup mask: {route_id} {family}:{group}")
        residual_mask = label_core_mask(clean, require_nonempty=False) > 0
        residual_mask &= ~marker_protected
        residual = int(np.count_nonzero(residual_mask))
        residual_total += residual
        layers, layer_report = layer_cache[str(label["ko"])]
        composites = np.stack([alpha_composite(clean[state], layers[state]) for state in range(STATE_COUNT)])
        marker_layer_overlap = [int(np.count_nonzero(marker_protected & (layers[state, ..., 3] > 0))) for state in range(STATE_COUNT)]
        if marker_report is not None:
            composites[:, marker_protected, :] = source[:, marker_protected, :]
            marker_differences = int(
                np.count_nonzero(
                    np.any(
                        canonical_rgba(composites[:, marker_protected, :])
                        != canonical_rgba(source[:, marker_protected, :]),
                        axis=-1,
                    )
                )
            )
            require(marker_differences == 0, f"non-text marker changed: {route_id} {family}:{group}")
        composite_groups.append(composites)
        group_dir = output / "cells" / route_id / family / f"{group:02d}_{label['name']}"
        group_dir.mkdir(parents=True, exist_ok=True)
        state_rows: list[dict[str, Any]] = []
        for state in range(STATE_COUNT):
            allowed = cleanup | (layers[state, ..., 3] > 0)
            unchanged_outside = canonical_rgba(composites[state])[~allowed] == canonical_rgba(source[state])[~allowed]
            require(bool(np.all(unchanged_outside)), f"composite escaped label union: {route_id} {family}:{group}:{state + 1}")
            changed = np.any(canonical_rgba(composites[state]) != canonical_rgba(source[state]), axis=-1)
            x0, y0, x1, y1 = rects[state]
            require((x1 - x0, y1 - y0) == contract.cell_size, f"JP placement geometry differs: {route_id} {family}:{group}:{state + 1}")
            global_changed = atlas_written[y0:y1, x0:x1]
            overlap = global_changed & changed
            if np.any(overlap):
                require(bool(np.all(candidate_atlas[y0:y1, x0:x1][overlap] == composites[state][overlap])), f"overlapping cell writes disagree: {route_id} {family}:{group}:{state + 1}")
            candidate_atlas[y0:y1, x0:x1][changed] = composites[state][changed]
            global_changed |= changed
            ys, xs = np.nonzero(changed)
            blocks = {(int((x0 + x) // 4), int((y0 + y) // 4)) for y, x in zip(ys.tolist(), xs.tolist())}
            family_blocks.update(blocks)
            source_bbox = component_bbox(source[state])
            final_bbox = component_bbox(composites[state])
            require(source_bbox is not None and final_bbox is not None, "wheel component is empty")
            source_size = [source_bbox[2] - source_bbox[0], source_bbox[3] - source_bbox[1]]
            final_size = [final_bbox[2] - final_bbox[0], final_bbox[3] - final_bbox[1]]
            path = group_dir / f"state_{state + 1}.png"
            Image.fromarray(composites[state]).save(path, optimize=False, compress_level=9)
            cell_files.append(path)
            state_rows.append({
                "state": state + 1,
                "metadata_record": record_groups(family)[group][state],
                "atlas_rect": [x0, y0, x1, y1],
                "cleanup_mask_bbox": bbox(cleanup),
                "changed_pixels": int(np.count_nonzero(changed)),
                "changed_bc3_blocks": len(blocks),
                "source_component_bbox": source_bbox,
                "final_component_bbox": final_bbox,
                "final_over_source_width": round(final_size[0] / source_size[0], 6),
                "final_over_source_height": round(final_size[1] / source_size[1], 6),
                "composite_file": str(path.relative_to(output)).replace("\\", "/"),
            })
        rows.append({
            "group": group,
            "name": label["name"],
            "jp": label.get("jp"),
            "ko": label["ko"],
            "clean_residual_core_pixels": residual,
            "preserved_nontext_marker": None if marker_report is None else {
                **marker_report,
                "text_layer_overlap_pixels_by_state": marker_layer_overlap,
                "final_canonical_rgba_differences": 0,
            },
            "text_rendering": layer_report,
            "states": state_rows,
        })

    contact_files = contact_sheet_pages(output, route_id, family, labels, source_groups, composite_groups, ui_font_path)
    return {
        "groups": len(labels),
        "states": len(labels) * STATE_COUNT,
        "unique_korean_labels": len(layer_cache),
        "cell_size": list(contract.cell_size),
        "typography": {
            "ink_height": contract.ink_height,
            "ink_bottom": contract.ink_bottom,
            "safe_ink_width": contract.safe_ink_width,
            "stroke_radius": contract.stroke_radius,
            "outer_radius": contract.outer_radius,
            "outer_soften": contract.outer_soften,
        },
        "donor_template": template_report,
        "donor_exclusions": exclusions,
        "nonidentity_state_alignments": alignments,
        "clean_residual_core_pixels": residual_total,
        "preserved_nontext_marker_groups": sum(report is not None for report in marker_reports),
        "changed_bc3_blocks_union": len(family_blocks),
        "rows": rows,
    }, layer_files + cell_files + contact_files, rows


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output.resolve()
    tmp_root = (REPO / "tmp").resolve()
    try:
        output.relative_to(tmp_root)
    except ValueError as exc:
        raise RebuildError(f"output must stay below repo tmp: {output}") from exc
    require(not output.exists(), f"output already exists: {output}")

    font = args.font.resolve()
    ui_font = args.ui_font.resolve()
    validate_file(font, {"size": font.stat().st_size if font.is_file() else -1, "sha256": FONT_SHA256}, "B font")
    validate_file(ui_font, {"size": ui_font.stat().st_size if ui_font.is_file() else -1, "sha256": UI_FONT_SHA256}, "UI font")
    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    require(mapping.get("schema") == "nobu16.kr.wheel-detail-groups.v1", "wheel mapping schema differs")
    labels = labels_by_family(mapping)
    unique_assets = {(family, str(item["name"])) for family, items in labels.items() for item in items}
    require(len(unique_assets) == 64, f"unique wheel asset count differs: {len(unique_assets)}")

    pins = json.loads(args.input_pins.read_text(encoding="utf-8"))
    require(pins.get("schema") == "nobu16.kr.navigation-wheel-official-locale-inputs.v1", "locale pin schema differs")
    locale_pins = {(str(item["locale"]), str(item["route"])): item for item in pins["files"]}
    require(len(locale_pins) == 12, "locale input pin coverage differs")
    routes = route_specs()
    output.mkdir(parents=True)
    artifacts: list[Path] = []
    route_reports: dict[str, Any] = {}
    all_rows: list[dict[str, Any]] = []
    total_states = 0

    for route_id in ROUTE_ORDER:
        print(f"stage={route_id}:load", flush=True)
        route = routes[route_id]
        jp_path = args.jp_source_root / str(route["relative_path"])
        jp_pin = validate_file(jp_path, route["source"], f"{route_id} JP source")
        jp_cells, jp_rects, source_atlas, jp_resource = load_route_cells(jp_path, route, keep_atlas=True)
        require(source_atlas is not None, "JP source atlas was not retained")
        locale_cells: dict[str, dict[str, list[np.ndarray[Any, Any] | None]]] = {"JP": jp_cells}
        input_rows: dict[str, Any] = {"JP": {**jp_pin, "resource": jp_resource}}
        for locale in ("SC", "TC", "EN"):
            spec = locale_pins[(locale, route_id)]
            path = args.official_root / str(spec["relative_path"])
            pin = validate_file(path, spec, f"{route_id} {locale} source")
            cells, _rects, _atlas, resource = load_route_cells(path, route, keep_atlas=False)
            locale_cells[locale] = cells
            input_rows[locale] = {**pin, "source_kind": spec.get("source_kind", "live-stock"), "resource": resource}

        candidate_atlas = source_atlas.copy()
        atlas_written = np.zeros(source_atlas.shape[:2], dtype=bool)
        family_reports: dict[str, Any] = {}
        for family in family_names(route):
            print(f"stage={route_id}:{family}", flush=True)
            family_locale = {locale: locale_cells[locale][family] for locale in ("JP", "SC", "TC", "EN")}
            report, files, rows = build_family(
                output=output,
                route=route,
                family=family,
                labels=labels[family],
                locale_cells=family_locale,
                jp_rects=jp_rects[family],
                candidate_atlas=candidate_atlas,
                atlas_written=atlas_written,
                font_path=font,
                ui_font_path=ui_font,
            )
            family_reports[family] = report
            artifacts.extend(files)
            total_states += int(report["states"])
            for row in rows:
                all_rows.append({"route": route_id, "family": family, **row})

        atlas_path = output / "atlas_preview" / f"{route_id}.png"
        atlas_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(candidate_atlas).save(atlas_path, optimize=False, compress_level=9)
        artifacts.append(atlas_path)
        changed_pixels = int(np.count_nonzero(atlas_written))
        require(changed_pixels > 0, f"route has no changed atlas pixels: {route_id}")
        route_reports[route_id] = {
            "inputs": input_rows,
            "atlas_dimensions": [source_atlas.shape[1], source_atlas.shape[0]],
            "changed_atlas_pixels": changed_pixels,
            "atlas_preview": str(atlas_path.relative_to(output)).replace("\\", "/"),
            "families": family_reports,
        }
        del source_atlas, candidate_atlas, atlas_written, locale_cells, jp_cells

    require(total_states == 900, f"rebuilt state placement count differs: {total_states}")
    require(len(all_rows) == 150, f"rebuilt group count differs: {len(all_rows)}")
    residual_total = sum(int(row["clean_residual_core_pixels"]) for row in all_rows)
    preserved_marker_rows = [row for row in all_rows if row["preserved_nontext_marker"] is not None]
    require(len(preserved_marker_rows) == 16, f"non-text marker coverage differs: {len(preserved_marker_rows)}")
    marker_differences = sum(
        int(row["preserved_nontext_marker"]["final_canonical_rgba_differences"])
        for row in preserved_marker_rows
    )
    require(marker_differences == 0, f"non-text marker pixels changed: {marker_differences}")
    full_ratios = [
        (float(state["final_over_source_width"]), float(state["final_over_source_height"]), row["route"], row["family"], row["group"], state["state"])
        for row in all_rows for state in row["states"]
    ]
    geometry_outliers = [
        {"route": route, "family": family, "group": group, "state": state, "width_ratio": width, "height_ratio": height}
        for width, height, route, family, group, state in full_ratios
        if abs(width - 1.0) > 0.05 or abs(height - 1.0) > 0.05
    ]

    artifact_table = {
        str(path.relative_to(output)).replace("\\", "/"): {"size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(artifacts)
    }
    manifest = {
        "schema": SCHEMA,
        "generation_policy": GENERATION_POLICY,
        "archive_writes": 0,
        "patcher_writes": 0,
        "steam_writes": 0,
        "font": {"name": "SeoulHangang ExtraBold", "path": str(font), "sha256": FONT_SHA256, "aspect_ratio_changed": False},
        "runtime": {
            "pillow_version": pillow_version,
            "low_oversample": LOW_OVERSAMPLE,
            "high_oversample": HIGH_OVERSAMPLE,
            "equal_physical_sample_density": True,
        },
        "coverage": {
            "routes": 4,
            "families": 8,
            "groups": len(all_rows),
            "placements": total_states,
            "unique_assets": len(unique_assets),
            "artifact_files": len(artifact_table),
        },
        "inputs": {
            "mapping": file_spec(args.mapping),
            "locale_pins": file_spec(args.input_pins),
        },
        "validation": {
            "clean_residual_core_pixels": residual_total,
            "nontext_direction_marker_groups_preserved": len(preserved_marker_rows),
            "nontext_direction_marker_canonical_rgba_differences": marker_differences,
            "full_component_geometry_outliers_5pct": len(geometry_outliers),
            "geometry_outliers": geometry_outliers,
            "all_nonlabel_pixels_preserved": True,
            "all_cells_inside_original_metadata_rects": True,
        },
        "routes": route_reports,
        "artifacts": artifact_table,
    }
    manifest_path = output / "manifest.v1.json"
    write_json(manifest_path, manifest)
    return {
        "output": str(output),
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "placements": total_states,
        "unique_assets": len(unique_assets),
        "clean_residual_core_pixels": residual_total,
        "geometry_outliers_5pct": len(geometry_outliers),
        "artifacts": len(artifact_table),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--jp-source-root", type=Path, default=JP_SOURCE_ROOT)
    result.add_argument("--official-root", type=Path, default=OFFICIAL_ROOT)
    result.add_argument("--font", type=Path, default=FONT_PATH)
    result.add_argument("--ui-font", type=Path, default=UI_FONT_PATH)
    result.add_argument("--mapping", type=Path, default=MAPPING_PATH)
    result.add_argument("--input-pins", type=Path, default=INPUT_PINS)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
