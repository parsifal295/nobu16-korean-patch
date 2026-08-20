#!/usr/bin/env python3
"""Build an AI-free B-font rendering pilot for ordinary system buttons.

The pilot verifies four official locale atlases, separates the original button
body and icon layers with same-atlas donor statistics, renders three B
typography sizes, and emits PNG cells/contact sheets only below the repository
tmp directory.  It never writes game archives, patcher inputs, or a Steam
installation.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
WORKSPACE = REPO.parent.parent
CATALOG_WS = REPO / "workstreams" / "ordinary_button_atlas_catalog_v1"
WHEEL_REBUILD_WS = REPO / "workstreams" / "navigation_wheel_layered_rebuild_v1"
TEXT_WS = REPO / "workstreams" / "navigation_wheel_text_candidates_v1"
for candidate in (CATALOG_WS, WHEEL_REBUILD_WS, TEXT_WS, REPO / "tools"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import build_navigation_wheel_layered_rebuild_v1 as wheel  # noqa: E402
import build_navigation_wheel_text_candidates_v1 as text_candidates  # noqa: E402
import build_ordinary_button_atlas_catalog_v1 as atlas_catalog  # noqa: E402

try:
    import cv2  # type: ignore
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, __version__ as pillow_version
except ImportError as exc:  # pragma: no cover - workspace runtime invariant.
    raise RuntimeError("NumPy, OpenCV, and Pillow are required") from exc


SCHEMA = "nobu16.kr.ordinary-button-layered-render-pilot.v1"
GENERATION_POLICY = "forbidden-and-not-used"
ROUTE_ORDER = ("common_low", "common_high_standard")
LOCALES = ("JP", "SC", "TC", "EN")
STATE_COUNT = 6
PILOT_NAMES = (
    "approve",
    "close",
    "back",
    "no",
    "yes",
    "release_all",
    "skip",
    "renegotiate",
)
ICON_NAMES = frozenset((
    "approve", "stop", "close", "deny", "confirm", "reject", "back",
    "renegotiate", "accept", "next",
))
ICON_PROTECT_END: Mapping[str, Mapping[str, int]] = {
    "common_low": {
        "approve": 84, "stop": 84, "close": 76, "deny": 81, "confirm": 84,
        "reject": 81, "back": 81, "renegotiate": 72, "accept": 84,
        "next": 82,
    },
    "common_high_standard": {
        "approve": 164, "stop": 164, "close": 148, "deny": 158, "confirm": 164,
        "reject": 158, "back": 158, "renegotiate": 140, "accept": 164,
        "next": 160,
    },
}
SIZE_VARIANTS: Mapping[str, Mapping[str, int]] = {
    "small": {"common_low": 28, "common_high_standard": 56},
    "medium": {"common_low": 30, "common_high_standard": 60},
    "large": {"common_low": 32, "common_high_standard": 64},
}
NATIVE_VARIANT = "medium"
TRACKING_EM = -0.035
FONT_SHA256 = "60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1"
UI_FONT_SHA256 = "194018E6B2B293A7964F037B25C0249CE1418BC9AB3C971060A03AA57861E252"

DEFAULT_CATALOG = CATALOG_WS / "ordinary_button_catalog_v1.json"
DEFAULT_INPUT_PINS = REPO / "workstreams" / "navigation_wheel_layered_pilot_v1" / "official_locale_inputs_v1.json"
DEFAULT_JP_SOURCE_ROOT = WORKSPACE / "scratch" / "release-v0940-wheel-b-20260819-01" / "resource-input" / "source"
DEFAULT_OFFICIAL_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_FONT = WORKSPACE / "repository" / "KR_PATCH_WORK" / "tmp" / "third_party_fonts" / "SeoulHangangEB.ttf"
DEFAULT_UI_FONT = REPO / "vendor" / "noto" / "NotoSansKR-wght.ttf"


class PilotError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PilotError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


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
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def bbox(mask: "np.ndarray[Any, Any]") -> list[int] | None:
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def scale_for_route(route_id: str) -> int:
    return 1 if route_id == "common_low" else 2


def oversample_for_route(route_id: str) -> int:
    return 8 if route_id == "common_low" else 4


def icon_protect_end(route_id: str, name: str) -> int:
    return int(ICON_PROTECT_END.get(route_id, {}).get(name, 0))


@dataclass(frozen=True)
class StateStyle:
    state: int
    role: str
    fill: tuple[int, int, int, int]
    stroke: tuple[int, int, int, int]
    stroke_px_high: int


STATE_STYLES = (
    StateStyle(1, "white", (139, 117, 82, 255), (139, 117, 82, 255), 0),
    StateStyle(2, "cyan", (255, 255, 255, 255), (55, 76, 112, 255), 4),
    StateStyle(3, "blue", (255, 255, 255, 255), (62, 86, 134, 255), 2),
    StateStyle(4, "disabled", (61, 58, 49, 255), (61, 58, 49, 255), 0),
    StateStyle(5, "cyan-repeat", (255, 255, 255, 255), (55, 76, 112, 255), 4),
    StateStyle(6, "disabled-repeat", (61, 58, 49, 255), (61, 58, 49, 255), 0),
)


def load_font_mask(
    font_path: Path,
    text: str,
    target_height: int,
    oversample: int,
    *,
    tracking_em: float = TRACKING_EM,
) -> tuple[Image.Image, dict[str, Any]]:
    candidate = text_candidates.Candidate(
        "b_seoul_hangang_eb",
        "B",
        "selected",
        font_path,
        FONT_SHA256,
        None,
        tracking_em,
    )
    wanted = target_height * oversample
    low, high = 4 * oversample, 160 * oversample
    best: tuple[int, Image.Image, int] | None = None
    while low <= high:
        size = (low + high) // 2
        font = text_candidates.load_font(candidate, size)
        mask = text_candidates.render_chars(text, font, tracking_em * size)
        delta = abs(mask.height - wanted)
        if best is None or delta < best[0]:
            best = (delta, mask, size)
        if mask.height < wanted:
            low = size + 1
        elif mask.height > wanted:
            high = size - 1
        else:
            break
    require(best is not None, f"font-size search failed: {text}")
    _delta, mask, font_size = best
    if mask.height != wanted:
        mask = mask.resize((max(1, round(mask.width * wanted / mask.height)), wanted), Image.Resampling.LANCZOS)
    return mask, {"font_size_oversampled_px": font_size, "natural_fill_size": [mask.width, mask.height]}


def colored(mask: Image.Image, rgba: tuple[int, int, int, int]) -> Image.Image:
    result = Image.new("RGBA", mask.size, rgba)
    result.putalpha(mask if rgba[3] == 255 else mask.point([round(value * rgba[3] / 255) for value in range(256)]))
    return result


def render_layers(
    *,
    route_id: str,
    text: str,
    variant: str,
    cell_size: tuple[int, int],
    center: tuple[float, float],
    safe_zone: tuple[int, int],
    font_path: Path,
    tracking_em: float = TRACKING_EM,
    aspect_scale_x: float = 1.0,
    target_height_override: int | None = None,
) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    oversample = oversample_for_route(route_id)
    target_height = int(
        target_height_override
        if target_height_override is not None
        else SIZE_VARIANTS[variant][route_id]
    )
    require(target_height > 0, f"invalid target fill height: {target_height}")
    fill, metrics = load_font_mask(
        font_path,
        text,
        target_height,
        oversample,
        tracking_em=tracking_em,
    )
    require(0.5 <= aspect_scale_x <= 1.0, f"invalid horizontal aspect scale: {aspect_scale_x}")
    uncondensed_fill_size = [fill.width, fill.height]
    if aspect_scale_x != 1.0:
        fill = fill.resize(
            (max(1, round(fill.width * aspect_scale_x)), fill.height),
            Image.Resampling.LANCZOS,
        )
    centered_safe_width = 2 * min(center[0] - safe_zone[0], safe_zone[1] - center[0])
    require(centered_safe_width > 0, f"text center escaped safe zone: {center} {safe_zone}")
    safe_width = max(1, round(centered_safe_width * oversample))
    uniform_fit = min(1.0, safe_width / fill.width)
    if uniform_fit < 1.0:
        fill = fill.resize(
            (max(1, round(fill.width * uniform_fit)), max(1, round(fill.height * uniform_fit))),
            Image.Resampling.LANCZOS,
        )
    size = (cell_size[0] * oversample, cell_size[1] * oversample)
    fill_cell = Image.new("L", size, 0)
    x = round(center[0] * oversample - fill.width / 2)
    y = round(center[1] * oversample - fill.height / 2)
    fill_cell.paste(fill, (x, y))
    layers: list[np.ndarray[Any, Any]] = []
    state_rows: list[dict[str, Any]] = []
    for style in STATE_STYLES:
        stroke_native = style.stroke_px_high if route_id == "common_high_standard" else round(style.stroke_px_high / 2)
        if stroke_native:
            radius = stroke_native * oversample
            stroke = fill_cell.filter(ImageFilter.MaxFilter(radius * 2 + 1))
        else:
            stroke = fill_cell
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        if stroke_native:
            layer.alpha_composite(colored(stroke, style.stroke))
        layer.alpha_composite(colored(fill_cell, style.fill))
        native = layer.resize(cell_size, Image.Resampling.LANCZOS)
        values = np.asarray(native).copy()
        layer_bbox = bbox(values[..., 3] > 0)
        require(layer_bbox is not None, f"rendered layer is empty: {route_id} {text} {variant}")
        require(layer_bbox[0] >= 2 and layer_bbox[2] <= cell_size[0] - 2, f"text escaped horizontal canvas: {layer_bbox}")
        require(layer_bbox[1] >= 2 and layer_bbox[3] <= cell_size[1] - 2, f"text escaped vertical canvas: {layer_bbox}")
        layers.append(values)
        state_rows.append(
            {
                "state": style.state,
                "role": style.role,
                "stroke_px": stroke_native,
                "layer_bbox": layer_bbox,
                "alpha_pixels": int(np.count_nonzero(values[..., 3])),
            }
        )
    return np.stack(layers), {
        **metrics,
        "variant": variant,
        "target_height_override_used": target_height_override is not None,
        "target_fill_height_native_px": target_height,
        "uniform_fit_scale": round(uniform_fit, 6),
        "font_aspect_ratio_changed": aspect_scale_x != 1.0,
        "aspect_scale_x": aspect_scale_x,
        "uncondensed_fill_size": uncondensed_fill_size,
        "tracking_em": tracking_em,
        "oversample": oversample,
        "center": [round(center[0], 3), round(center[1], 3)],
        "safe_zone_x": list(safe_zone),
        "states": state_rows,
    }


def route_rows(catalog: Mapping[str, Any], route_id: str) -> list[Mapping[str, Any]]:
    rows = [
        row for row in catalog["placements"]
        if row["route"] == route_id and row["family"] == "standard"
    ]
    require(len(rows) == 120, f"{route_id} standard placement count differs: {len(rows)}")
    return rows


def load_atlas(
    path: Path,
    route: Mapping[str, Any],
    cache: dict[tuple[Path, int, int], atlas_catalog.LoadedG1T],
) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    loaded = atlas_catalog.load_g1t(
        path,
        int(route["outer_entry"]),
        int(route["resource_id"]),
        cache,
    )
    texture_index = int(route["texture_index"])
    require(texture_index < len(loaded.g1t.textures), f"texture {texture_index} absent: {path}")
    texture = loaded.g1t.textures[texture_index]
    require(
        (texture.format_code, texture.width, texture.height)
        == (int(str(route["format_code"]), 16), *route["dimensions"]),
        f"texture contract differs: {path}",
    )
    decoded = atlas_catalog.atlas_codec.decode_texture(texture)
    require(decoded is not None, f"BC3 decode failed: {path}")
    atlas = np.frombuffer(decoded, dtype=np.uint8).reshape(texture.height, texture.width, 4).copy()
    return atlas, {
        "nested_slot": loaded.nested_slot,
        "texture_index": texture_index,
        "format_code": f"0x{texture.format_code:02X}",
        "dimensions": [texture.width, texture.height],
    }


def extract_groups(atlas: "np.ndarray[Any, Any]", rows: Sequence[Mapping[str, Any]]) -> "np.ndarray[Any, Any]":
    grouped: list[np.ndarray[Any, Any]] = []
    for group in range(20):
        selected = sorted((row for row in rows if int(row["group"]) == group), key=lambda row: int(row["state"]))
        require([int(row["state"]) for row in selected] == list(range(1, 7)), f"group state coverage differs: {group}")
        states: list[np.ndarray[Any, Any]] = []
        expected_size: tuple[int, int] | None = None
        for row in selected:
            x0, y0, x1, y1 = (int(value) for value in row["processing_rect"])
            require(0 <= x0 < x1 <= atlas.shape[1] and 0 <= y0 < y1 <= atlas.shape[0], f"standard cell escaped atlas: {group}")
            cell = atlas[y0:y1, x0:x1].copy()
            size = (cell.shape[1], cell.shape[0])
            if expected_size is None:
                expected_size = size
            require(size == expected_size, f"group cell size differs: {group} {size} != {expected_size}")
            states.append(cell)
        grouped.append(np.stack(states))
    return np.stack(grouped)


def align_groups(reference: "np.ndarray[Any, Any]", donor: "np.ndarray[Any, Any]") -> tuple["np.ndarray[Any, Any]", list[dict[str, Any]]]:
    require(reference.shape == donor.shape, f"locale cell geometry differs: {reference.shape} != {donor.shape}")
    aligned: list[np.ndarray[Any, Any]] = []
    reports: list[dict[str, Any]] = []
    for group in range(20):
        values, permutation, cost = wheel.align_states(reference[group], donor[group])
        aligned.append(values)
        reports.append({"group": group, "permutation_target_to_source": permutation, "feature_cost": cost})
    return np.stack(aligned), reports


def original_foreground_core(states: "np.ndarray[Any, Any]", route_id: str) -> "np.ndarray[Any, Any]":
    """Identify the source foreground shared by the six stock button states.

    The white/blue states brighten text and icons while the white/disabled
    states darken them.  The button body itself does not satisfy the complete
    six-state transition, so this separates foreground without OCR or generated
    pixels.
    """

    require(states.shape[0] == STATE_COUNT, "source state coverage differs")
    scale = scale_for_route(route_id)
    height, width = states.shape[1:3]
    rgb = states[..., :3].astype(np.float32)
    alpha = states[..., 3].astype(np.float32) / 255.0
    light = rgb.mean(axis=3) * alpha
    core = (
        (alpha[0] > 0.08)
        & (light[0] < 160)
        & (light[1] > 135)
        & (light[2] > 125)
        & (light[3] < 135)
        & ((light[1] - light[0]) > 35)
        & ((light[2] - light[3]) > 25)
    ).astype(np.uint8)
    interior = np.zeros((height, width), dtype=np.uint8)
    interior[round(height * 0.13) : round(height * 0.82), round(width * 0.04) : round(width * 0.96)] = 1
    core &= interior
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(core, 8)
    kept = np.zeros_like(core)
    minimum_area = 2 * scale * scale
    for index in range(1, count):
        _x, _y, _component_width, component_height, area = (int(value) for value in stats[index])
        if area >= minimum_area and component_height >= 2 * scale:
            kept[labels == index] = 1
    return kept


def label_cleanup_mask(
    source: "np.ndarray[Any, Any]",
    route_id: str,
    name: str,
) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    scale = scale_for_route(route_id)
    height, width = source.shape[1:3]
    foreground = original_foreground_core(source, route_id)
    kept = foreground.copy()
    icon_layout = name in ICON_NAMES
    protected_end = icon_protect_end(route_id, name) if icon_layout else 0
    if protected_end:
        kept[:, :protected_end] = 0
    require(np.any(kept), f"Japanese label foreground is empty: {route_id} {name}")
    cleanup_kernel = scale * 10 + 1
    cleanup = wheel.dilate(kept * 255, cleanup_kernel) > 0
    protected = np.zeros_like(cleanup)
    if protected_end:
        protected[:, :protected_end] = True
        cleanup &= ~protected
    core_box = bbox(kept > 0)
    cleanup_box = bbox(cleanup)
    require(core_box is not None and cleanup_box is not None, f"label cleanup mask is empty: {route_id} {name}")
    cleanup_area = int(np.count_nonzero(cleanup))
    require(cleanup_area < round(width * height * 0.36), f"cleanup mask is implausibly broad: {route_id} {name} {cleanup_area}/{width * height}")
    return cleanup, {
        "core_method": "six_state_original_foreground_transition",
        "core_pixels": int(np.count_nonzero(kept)),
        "core_bbox": core_box,
        "cleanup_pixels": cleanup_area,
        "cleanup_bbox": cleanup_box,
        "icon_layout": bool(icon_layout),
        "protected_icon_region": [0, 0, protected_end, height] if icon_layout else None,
    }


def clean_group(
    source: "np.ndarray[Any, Any]",
    cleanup: "np.ndarray[Any, Any]",
    *,
    donor_samples: Sequence["np.ndarray[Any, Any]"],
    donor_cores: Sequence["np.ndarray[Any, Any]"],
    route_id: str,
) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    template, template_report = wheel.donor_template(
        list(donor_samples),
        [core * 255 for core in donor_cores],
        cleanup,
        scale_for_route(route_id),
    )
    clean = source.copy()
    clean[:, cleanup] = template[:, cleanup]
    scale = scale_for_route(route_id)
    median_kernel = scale * 4 + 1
    speckle_passes: list[dict[str, Any]] = []
    total_repair = np.zeros_like(cleanup)
    for pass_index in range(8):
        median_states = np.stack([cv2.medianBlur(state, median_kernel) for state in clean])
        median_delta = np.max(
            np.abs(clean.astype(np.int16) - median_states.astype(np.int16)),
            axis=-1,
        ).max(axis=0)
        speckle_core = ((median_delta >= 14) & cleanup).astype(np.uint8)
        count, labels, stats, _centroids = cv2.connectedComponentsWithStats(speckle_core, 8)
        accepted = np.zeros_like(speckle_core)
        accepted_components: list[dict[str, Any]] = []
        for index in range(1, count):
            x, y, component_width, component_height, area = (int(value) for value in stats[index])
            if (
                area <= 64 * scale * scale
                and component_width <= 12 * scale
                and component_height <= 12 * scale
            ):
                accepted[labels == index] = 1
                accepted_components.append(
                    {"bbox": [x, y, x + component_width, y + component_height], "pixels": area}
                )
        repair = (wheel.dilate(accepted * 255, scale * 2 + 1) > 0) & cleanup
        speckle_passes.append(
            {
                "pass": pass_index + 1,
                "components": accepted_components,
                "core_pixels": int(np.count_nonzero(accepted)),
                "repaired_pixels": int(np.count_nonzero(repair)),
            }
        )
        if not np.any(repair):
            break
        clean[:, repair] = median_states[:, repair]
        total_repair |= repair
    require(
        speckle_passes[-1]["core_pixels"] == 0,
        f"same-atlas body speckle cleanup did not converge: {route_id} {speckle_passes[-1]}",
    )
    outside = np.count_nonzero(np.any(clean[:, ~cleanup] != source[:, ~cleanup], axis=-1))
    require(int(outside) == 0, f"clean plate escaped cleanup mask: {outside}")
    return clean, {
        "method": "same_atlas_foreground_excluded_premultiplied_median",
        "source_atlas_groups": len(donor_samples),
        **template_report,
        "rank_filter_speckle_cleanup": {
            "threshold": 14,
            "median_kernel": median_kernel,
            "passes": speckle_passes,
            "repaired_union_pixels": int(np.count_nonzero(total_repair)),
        },
        "generation_used": False,
        "outside_cleanup_changed_pixels": int(outside),
    }


def source_label_geometry(
    source: "np.ndarray[Any, Any]",
    clean: "np.ndarray[Any, Any]",
    cleanup: "np.ndarray[Any, Any]",
    *,
    protected_end: int,
) -> dict[str, Any]:
    delta = np.max(
        np.abs(wheel.canonical_rgba(source).astype(np.int32) - wheel.canonical_rgba(clean).astype(np.int32)),
        axis=-1,
    )
    state_boxes: list[list[int]] = []
    for state in range(STATE_COUNT):
        mask = (delta[state] >= 38) & cleanup
        box = bbox(mask)
        if box is not None:
            state_boxes.append(box)
    require(len(state_boxes) >= 4, f"source label geometry has too few states: {state_boxes}")
    centers_x = [(box[0] + box[2]) / 2 for box in state_boxes]
    centers_y = [(box[1] + box[3]) / 2 for box in state_boxes]
    heights = [box[3] - box[1] for box in state_boxes]
    cleanup_box = bbox(cleanup)
    require(cleanup_box is not None, "cleanup bbox is empty")
    center = (float(np.median(centers_x)), float(np.median(centers_y)))
    scale = 1 if source.shape[2] == 192 else 2
    zone = (
        max(2 * scale, cleanup_box[0] - 2 * scale),
        min(source.shape[2] - 2 * scale, cleanup_box[2] + 2 * scale),
    )
    if protected_end:
        # Keep enough room for the selected-state outline and resampling fringe,
        # not only the fill glyph itself.
        zone = (max(zone[0], protected_end + 6 * scale), zone[1])
    require(zone[0] < center[0] < zone[1], f"source label center escaped zone: {center} {zone}")
    return {
        "source_difference_bboxes": state_boxes,
        "source_median_center": [round(center[0], 3), round(center[1], 3)],
        "source_median_difference_height": round(float(np.median(heights)), 3),
        "safe_zone_x": list(zone),
    }


def flatten_cell(values: "np.ndarray[Any, Any]", route_id: str) -> Image.Image:
    image = Image.fromarray(values)
    background = Image.new("RGB", image.size, (0, 255, 32))
    background.paste(image, (0, 0), image)
    if route_id == "common_low":
        background = background.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)
    canvas = Image.new("RGB", (384, 176), (20, 22, 26))
    x = (canvas.width - background.width) // 2
    y = (canvas.height - background.height) // 2
    canvas.paste(background, (x, y))
    return canvas


def contact_native_states(
    output: Path,
    route_id: str,
    labels: Sequence[Mapping[str, Any]],
    source: Mapping[str, "np.ndarray[Any, Any]"],
    clean: Mapping[str, "np.ndarray[Any, Any]"],
    composite: Mapping[str, "np.ndarray[Any, Any]"],
    ui_font_path: Path,
) -> Path:
    columns = (
        (0, "JP 1", "source"), (0, "클린 1", "clean"), (0, "B 1", "final"),
        (1, "JP 2", "source"), (1, "클린 2", "clean"), (1, "B 2", "final"),
        (3, "JP 4", "source"), (3, "클린 4", "clean"), (3, "B 4", "final"),
    )
    cell_width, cell_height = 384, 176
    left, gap, top = 160, 8, 42
    width = left + len(columns) * (cell_width + gap) + gap
    height = top + len(labels) * (cell_height + gap) + 34
    sheet = Image.new("RGB", (width, height), (25, 27, 31))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(ui_font_path), 15)
    font.set_variation_by_axes([650])
    for index, (_state, title, _kind) in enumerate(columns):
        draw.text((left + index * (cell_width + gap) + 145, 12), title, font=font, fill=(235, 236, 238))
    by_name = {str(item["name"]): item for item in labels}
    for row, name in enumerate(PILOT_NAMES):
        label = by_name[name]
        y = top + row * (cell_height + gap)
        draw.text((8, y + 64), f"{name}\n{label['ko']}", font=font, fill=(224, 227, 231), spacing=3)
        for column, (state, _title, kind) in enumerate(columns):
            matrix = source[name] if kind == "source" else clean[name] if kind == "clean" else composite[name]
            sheet.paste(flatten_cell(matrix[state], route_id), (left + column * (cell_width + gap), y))
    draw.text((8, height - 25), f"{route_id} / B medium / source-clean-final / generated image processing not used", font=font, fill=(165, 173, 184))
    path = output / "contact" / f"{route_id}_B_medium_states.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, optimize=False, compress_level=9)
    return path


def contact_size_comparison(
    output: Path,
    labels: Sequence[Mapping[str, Any]],
    composites: Mapping[tuple[str, str, str], "np.ndarray[Any, Any]"],
    ui_font_path: Path,
) -> Path:
    columns = tuple((route, variant) for route in ROUTE_ORDER for variant in SIZE_VARIANTS)
    cell_width, cell_height = 384, 176
    left, gap, top = 160, 8, 48
    width = left + len(columns) * (cell_width + gap) + gap
    height = top + len(labels) * (cell_height + gap) + 34
    sheet = Image.new("RGB", (width, height), (25, 27, 31))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(ui_font_path), 15)
    font.set_variation_by_axes([650])
    for index, (route, variant) in enumerate(columns):
        title = ("저" if route == "common_low" else "고") + f" / {variant}"
        draw.text((left + index * (cell_width + gap) + 125, 14), title, font=font, fill=(235, 236, 238))
    by_name = {str(item["name"]): item for item in labels}
    for row, name in enumerate(PILOT_NAMES):
        label = by_name[name]
        y = top + row * (cell_height + gap)
        draw.text((8, y + 64), f"{name}\n{label['ko']}", font=font, fill=(224, 227, 231), spacing=3)
        for column, (route, variant) in enumerate(columns):
            matrix = composites[(route, variant, name)]
            sheet.paste(flatten_cell(matrix[1], route), (left + column * (cell_width + gap), y))
    draw.text((8, height - 25), "state 2 cyan / SeoulHangang ExtraBold / small-medium-large", font=font, fill=(165, 173, 184))
    path = output / "contact" / "ordinary_button_B_size_comparison.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, optimize=False, compress_level=9)
    return path


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output.resolve()
    tmp_root = (REPO / "tmp").resolve()
    try:
        output.relative_to(tmp_root)
    except ValueError as exc:
        raise PilotError(f"output must stay below {tmp_root}: {output}") from exc
    require(not output.exists(), f"output already exists: {output}")

    catalog_path = args.catalog.resolve(strict=True)
    pins_path = args.input_pins.resolve(strict=True)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    pins = json.loads(pins_path.read_text(encoding="utf-8"))
    require(catalog.get("schema") == atlas_catalog.SCHEMA, "ordinary-button catalog schema differs")
    require(pins.get("schema") == "nobu16.kr.navigation-wheel-official-locale-inputs.v1", "official locale pin schema differs")
    font_path = args.font.resolve(strict=True)
    ui_font_path = args.ui_font.resolve(strict=True)
    validate_file(font_path, {"size": font_path.stat().st_size, "sha256": FONT_SHA256}, "B font")
    validate_file(ui_font_path, {"size": ui_font_path.stat().st_size, "sha256": UI_FONT_SHA256}, "UI font")
    labels = [item for item in catalog["labels"] if item["name"] in PILOT_NAMES]
    require({item["name"] for item in labels} == set(PILOT_NAMES), "pilot label coverage differs")
    labels_by_name = {str(item["name"]): item for item in labels}
    routes = catalog["routes"]
    pin_map = {(str(item["locale"]), str(item["route"])): item for item in pins["files"]}
    route_pin_names = {"common_low": "base_low", "common_high_standard": "base_high"}
    output.mkdir(parents=True)
    cache: dict[tuple[Path, int, int], atlas_catalog.LoadedG1T] = {}
    route_reports: dict[str, Any] = {}
    artifacts: list[Path] = []
    all_size_composites: dict[tuple[str, str, str], np.ndarray[Any, Any]] = {}

    for route_id in ROUTE_ORDER:
        print(f"stage={route_id}:load", flush=True)
        route = routes[route_id]
        rows = route_rows(catalog, route_id)
        archive = str(route["archive"])
        jp_path = args.jp_source_root.resolve(strict=True) / archive
        jp_pin = validate_file(jp_path, route["source"], f"{route_id} JP source")
        locale_groups: dict[str, np.ndarray[Any, Any]] = {}
        input_rows: dict[str, Any] = {}
        jp_atlas, resource = load_atlas(jp_path, route, cache)
        locale_groups["JP"] = extract_groups(jp_atlas, rows)
        input_rows["JP"] = {**jp_pin, "resource": resource}
        for locale in ("SC", "TC", "EN"):
            pin = pin_map[(locale, route_pin_names[route_id])]
            path = args.official_root.resolve(strict=True) / str(pin["relative_path"])
            file_pin = validate_file(path, pin, f"{route_id} {locale} source")
            atlas, locale_resource = load_atlas(path, route, cache)
            extracted = extract_groups(atlas, rows)
            aligned, alignments = align_groups(locale_groups["JP"], extracted)
            locale_groups[locale] = aligned
            input_rows[locale] = {**file_pin, "resource": locale_resource, "state_alignments": alignments}
            del atlas, extracted

        route_dir = output / route_id
        source_selected: dict[str, np.ndarray[Any, Any]] = {}
        clean_selected: dict[str, np.ndarray[Any, Any]] = {}
        medium_selected: dict[str, np.ndarray[Any, Any]] = {}
        group_reports: list[dict[str, Any]] = []
        cell_size = (locale_groups["JP"].shape[3], locale_groups["JP"].shape[2])
        donor_samples = [locale_groups["JP"][group] for group in range(20)]
        donor_cores = [original_foreground_core(sample, route_id) for sample in donor_samples]
        for name in PILOT_NAMES:
            group = next(int(item["group"]) for item in rows if item["name"] == name)
            source = locale_groups["JP"][group]
            cleanup, mask_report = label_cleanup_mask(source, route_id, name)
            clean, donor_report = clean_group(
                source,
                cleanup,
                donor_samples=donor_samples,
                donor_cores=donor_cores,
                route_id=route_id,
            )
            geometry = source_label_geometry(
                source,
                clean,
                cleanup,
                protected_end=icon_protect_end(route_id, name),
            )
            center = tuple(float(value) for value in geometry["source_median_center"])
            safe_zone = tuple(int(value) for value in geometry["safe_zone_x"])

            name_dir = route_dir / f"{group:02d}_{name}"
            (name_dir / "source").mkdir(parents=True)
            (name_dir / "clean").mkdir()
            (name_dir / "mask").mkdir()
            source_selected[name] = source
            clean_selected[name] = clean
            for state in range(STATE_COUNT):
                source_path = name_dir / "source" / f"state_{state + 1}.png"
                clean_path = name_dir / "clean" / f"state_{state + 1}.png"
                Image.fromarray(source[state]).save(source_path, optimize=False, compress_level=9)
                Image.fromarray(clean[state]).save(clean_path, optimize=False, compress_level=9)
                artifacts.extend((source_path, clean_path))
            mask_path = name_dir / "mask" / "cleanup.png"
            Image.fromarray(cleanup.astype(np.uint8) * 255).save(mask_path, optimize=False, compress_level=9)
            artifacts.append(mask_path)

            variant_reports: dict[str, Any] = {}
            for variant in SIZE_VARIANTS:
                layers, type_report = render_layers(
                    route_id=route_id,
                    text=str(labels_by_name[name]["ko"]),
                    variant=variant,
                    cell_size=cell_size,
                    center=center,
                    safe_zone=safe_zone,
                    font_path=font_path,
                )
                composites = np.stack([wheel.alpha_composite(clean[state], layers[state]) for state in range(STATE_COUNT)])
                icon_end = icon_protect_end(route_id, name) if mask_report["icon_layout"] else 0
                if icon_end:
                    require(
                        int(np.count_nonzero(np.any(composites[:, :, :icon_end] != source[:, :, :icon_end], axis=-1))) == 0,
                        f"protected icon region changed: {route_id} {name} {variant}",
                    )
                variant_dir = name_dir / variant
                variant_dir.mkdir()
                state_reports: list[dict[str, Any]] = []
                for state in range(STATE_COUNT):
                    allowed = cleanup | (layers[state, ..., 3] > 0)
                    outside = int(
                        np.count_nonzero(
                            np.any(wheel.canonical_rgba(composites[state])[~allowed] != wheel.canonical_rgba(source[state])[~allowed], axis=-1)
                        )
                    )
                    require(outside == 0, f"composite escaped label union: {route_id} {name} {variant} state {state + 1}")
                    path = variant_dir / f"state_{state + 1}.png"
                    Image.fromarray(composites[state]).save(path, optimize=False, compress_level=9)
                    artifacts.append(path)
                    state_reports.append(
                        {
                            "state": state + 1,
                            "outside_cleanup_and_new_label_changed_pixels": outside,
                            "changed_pixels": int(
                                np.count_nonzero(
                                    np.any(wheel.canonical_rgba(composites[state]) != wheel.canonical_rgba(source[state]), axis=-1)
                                )
                            ),
                            "file": str(path.relative_to(output)).replace("\\", "/"),
                        }
                    )
                all_size_composites[(route_id, variant, name)] = composites
                if variant == NATIVE_VARIANT:
                    medium_selected[name] = composites
                variant_reports[variant] = {"typography": type_report, "states": state_reports}

            group_reports.append(
                {
                    "group": group,
                    "name": name,
                    "jp": labels_by_name[name]["jp"],
                    "ko": labels_by_name[name]["ko"],
                    "mask": mask_report,
                    "donor_reconstruction": donor_report,
                    "source_label_geometry": geometry,
                    "variants": variant_reports,
                }
            )

        contact = contact_native_states(output, route_id, labels, source_selected, clean_selected, medium_selected, ui_font_path)
        artifacts.append(contact)
        route_reports[route_id] = {
            "inputs": input_rows,
            "cell_size": list(cell_size),
            "pilot_groups": len(group_reports),
            "pilot_placements_per_variant": len(group_reports) * STATE_COUNT,
            "groups": group_reports,
            "medium_state_contact": str(contact.relative_to(output)).replace("\\", "/"),
        }
        del jp_atlas, locale_groups

    size_contact = contact_size_comparison(output, labels, all_size_composites, ui_font_path)
    artifacts.append(size_contact)
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
        "font": {
            "candidate": "B",
            "name": "SeoulHangang ExtraBold",
            "path": str(font_path),
            "sha256": FONT_SHA256,
            "aspect_ratio_changed": False,
        },
        "runtime": {"pillow_version": pillow_version, "opencv_version": cv2.__version__, "numpy_version": np.__version__},
        "coverage": {
            "routes": 2,
            "pilot_labels": len(PILOT_NAMES),
            "states_per_label": STATE_COUNT,
            "size_variants": len(SIZE_VARIANTS),
            "composite_cells": len(ROUTE_ORDER) * len(PILOT_NAMES) * STATE_COUNT * len(SIZE_VARIANTS),
        },
        "size_variants": {name: dict(values) for name, values in SIZE_VARIANTS.items()},
        "native_variant": NATIVE_VARIANT,
        "inputs": {"catalog": file_spec(catalog_path), "official_locale_pins": file_spec(pins_path)},
        "validation": {
            "clean_body_derived_only_from_original_same_atlas_groups": True,
            "interpolation_used": False,
            "generation_used": False,
            "all_nonlabel_pixels_preserved": True,
            "protected_icon_region_differences": 0,
        },
        "routes": route_reports,
        "contacts": {
            "size_comparison": str(size_contact.relative_to(output)).replace("\\", "/"),
            "medium_states": {route: route_reports[route]["medium_state_contact"] for route in ROUTE_ORDER},
        },
        "artifacts": artifact_table,
    }
    manifest_path = output / "manifest.v1.json"
    write_json(manifest_path, manifest)
    return {
        "output": str(output),
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "composite_cells": manifest["coverage"]["composite_cells"],
        "artifacts": len(artifact_table),
        "contacts": manifest["contacts"],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    result.add_argument("--input-pins", type=Path, default=DEFAULT_INPUT_PINS)
    result.add_argument("--jp-source-root", type=Path, default=DEFAULT_JP_SOURCE_ROOT)
    result.add_argument("--official-root", type=Path, default=DEFAULT_OFFICIAL_ROOT)
    result.add_argument("--font", type=Path, default=DEFAULT_FONT)
    result.add_argument("--ui-font", type=Path, default=DEFAULT_UI_FONT)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
