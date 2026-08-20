#!/usr/bin/env python3
"""Build an AI-free, layered navigation-wheel pilot for the six 入城 states.

The program is intentionally PNG-only.  It never rewrites LINK/G1T archives,
the v0.94 patcher bundle, or a Steam installation.
"""

from __future__ import annotations

import argparse
import hashlib
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
CATALOG_WORKSTREAM = REPO / "workstreams" / "navigation_wheel_atlas_catalog_v1"
TEXT_WORKSTREAM = REPO / "workstreams" / "navigation_wheel_text_candidates_v1"
TOOLS = REPO / "tools"
for import_root in (TOOLS, CATALOG_WORKSTREAM, TEXT_WORKSTREAM):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import build_navigation_wheel_atlas_catalog_v1 as catalog  # noqa: E402
import build_navigation_wheel_text_candidates_v1 as text_candidates  # noqa: E402

try:
    import cv2  # type: ignore
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, __version__ as pillow_version
except ImportError as exc:  # pragma: no cover - user-facing dependency gate.
    raise RuntimeError("NumPy, OpenCV, and Pillow are required for the layered wheel pilot") from exc


SCHEMA = "nobu16.kr.navigation-wheel-layered-pilot.v1"
GENERATION_POLICY = "forbidden-and-not-used"
ROUTE_ID = "base_low"
PILOT_FAMILY = "base_detail"
PILOT_GROUP = 8
PILOT_NAME = "enter_castle"
PILOT_JP = "入城"
PILOT_KO = "입성"
CELL_SIZE = (100, 95)
STATE_COUNT = 6

OVERSAMPLE = 8
TRACKING_EM = -0.035
TARGET_INK_HEIGHT = 21
INK_BOTTOM = 85
SAFE_INK_WIDTH = 88
STROKE_RADIUS = 1.4
OUTER_RADIUS = 3.0
OUTER_SOFTEN = 0.5

LABEL_SCAN_Y = 56
LABEL_COMPONENT_MIN_BOTTOM = 68
DONOR_FALLBACK_KERNEL = 5
DONOR_PRIMARY_KERNEL = 7
CLEANUP_KERNEL = 11
PROTECTED_BODY_END_Y = 58

FONT_SHA256 = "60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1"
UI_FONT_SHA256 = "194018E6B2B293A7964F037B25C0249CE1418BC9AB3C971060A03AA57861E252"

DEFAULT_JP_SOURCE_ROOT = WORKSPACE / "scratch" / "release-v0940-rc-20260819-06" / "resource-input" / "source"
DEFAULT_OFFICIAL_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_FONT = WORKSPACE / "repository" / "KR_PATCH_WORK" / "tmp" / "third_party_fonts" / "SeoulHangangEB.ttf"
DEFAULT_MAPPING = REPO / "workstreams" / "steam_jp_port_highres_images_v1" / "wheel_detail_groups_full_v1.json"
DEFAULT_INPUT_PINS = WORKSTREAM / "official_locale_inputs_v1.json"
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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def validate_file(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is not a file: {path}")
    actual = {"size": path.stat().st_size, "sha256": sha256_file(path)}
    wanted = {"size": int(expected["size"]), "sha256": str(expected["sha256"]).upper()}
    require(actual == wanted, f"{label} pin differs: expected={wanted} actual={actual}")
    return {"path": str(path.resolve()), **actual}


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bbox_from_mask(mask: "np.ndarray[Any, Any]") -> list[int] | None:
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def odd_filter_size(radius_px: float) -> int:
    radius = max(1, round(radius_px * OVERSAMPLE))
    return radius * 2 + 1


@dataclass(frozen=True)
class StatePalette:
    state: int
    role: str
    fill: tuple[int, int, int, int]
    stroke: tuple[int, int, int, int]
    outer: tuple[int, int, int, int]


STATE_PALETTES = (
    StatePalette(1, "normal", (41, 32, 24, 255), (239, 239, 222, 255), (236, 227, 198, 218)),
    StatePalette(2, "selected-blue", (231, 227, 239, 255), (33, 105, 189, 255), (19, 97, 173, 209)),
    StatePalette(3, "selected-navy", (231, 227, 231, 255), (60, 81, 140, 255), (57, 73, 132, 218)),
    StatePalette(4, "disabled", (41, 36, 33, 255), (156, 150, 140, 255), (126, 124, 110, 232)),
    StatePalette(5, "selected-blue-repeat", (231, 227, 239, 255), (33, 105, 189, 255), (19, 97, 173, 209)),
    StatePalette(6, "disabled-repeat", (41, 36, 33, 255), (156, 150, 140, 255), (126, 124, 110, 232)),
)


def route_spec() -> dict[str, Any]:
    matches = [dict(item) for item in catalog.ROUTES if item["id"] == ROUTE_ID]
    require(len(matches) == 1, f"catalog route missing or duplicated: {ROUTE_ID}")
    return matches[0]


def locale_specs(pin_path: Path) -> dict[str, Mapping[str, Any]]:
    pins = json.loads(pin_path.read_text(encoding="utf-8"))
    require(pins.get("schema") == "nobu16.kr.navigation-wheel-official-locale-inputs.v1", "input pin schema differs")
    selected = {
        str(item["locale"]): item
        for item in pins["files"]
        if item["route"] == ROUTE_ID
    }
    require(set(selected) == {"SC", "TC", "EN"}, f"base_low locale pins differ: {sorted(selected)}")
    return selected


def extract_groups(
    path: Path,
    route: Mapping[str, Any],
    mapping: Mapping[str, Any],
) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    loaded = catalog.load_resource(path, route)
    require(loaded.nested_slot == 0, f"nested G1T slot differs: {path}")
    records = catalog.parse_layout(loaded.table_padding, 474)
    placements = catalog.base_placements(route, records, loaded.texture, mapping)
    decoded = catalog.atlas_codec.decode_texture(loaded.texture)
    require(decoded is not None, f"BC3 decode failed: {path}")
    atlas = np.frombuffer(decoded, dtype=np.uint8).reshape(loaded.texture.height, loaded.texture.width, 4)
    groups: list[np.ndarray[Any, Any]] = []
    for group in range(57):
        rows = sorted(
            (
                row for row in placements
                if row["family"] == PILOT_FAMILY and int(row["group"]) == group
            ),
            key=lambda row: int(row["state"]),
        )
        require(len(rows) == STATE_COUNT, f"base detail group {group} does not have six states: {path}")
        cells: list[np.ndarray[Any, Any]] = []
        for row in rows:
            x0, y0, x1, y1 = (int(value) for value in row["atlas_clip_rect"])
            cell = atlas[y0:y1, x0:x1].copy()
            require(cell.shape == (CELL_SIZE[1], CELL_SIZE[0], 4), f"cell geometry differs: {path} group={group}")
            cells.append(cell)
        groups.append(np.stack(cells))
    return np.stack(groups), {
        "nested_slot": loaded.nested_slot,
        "texture_dimensions": [loaded.texture.width, loaded.texture.height],
        "format_code": f"0x{loaded.texture.format_code:02X}",
        "layout_table_sha256": sha256_bytes(loaded.table_padding),
        "layout_record_count": len(records),
    }


def label_core_mask(
    states: "np.ndarray[Any, Any]",
    *,
    require_nonempty: bool = True,
) -> "np.ndarray[Any, Any]":
    require(states.shape == (STATE_COUNT, CELL_SIZE[1], CELL_SIZE[0], 4), f"state cell shape differs: {states.shape}")
    rgb = states[..., :3].astype(np.float32)
    alpha = states[..., 3].astype(np.float32) / 255.0
    luminance_proxy = rgb.mean(axis=3) * alpha
    y_grid = np.arange(CELL_SIZE[1])[:, None]
    core = (
        (y_grid >= LABEL_SCAN_Y)
        & (alpha[0] > 0.08)
        & (luminance_proxy[0] < 160)
        & (luminance_proxy[1] > 135)
        & (luminance_proxy[2] > 125)
        & (luminance_proxy[3] < 135)
        & (luminance_proxy[4] > 135)
        & (luminance_proxy[5] < 135)
        & ((luminance_proxy[1] - luminance_proxy[0]) > 35)
        & ((luminance_proxy[2] - luminance_proxy[3]) > 25)
    )
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(core.astype(np.uint8), 8)
    kept = np.zeros(core.shape, dtype=np.uint8)
    for index in range(1, count):
        _x, y, _width, height, area = (int(value) for value in stats[index])
        if area >= 1 and y >= LABEL_SCAN_Y and y + height >= LABEL_COMPONENT_MIN_BOTTOM:
            kept[labels == index] = 255
    if require_nonempty:
        require(bool(np.any(kept)), "official locale group produced no label core")
    return kept


def dilate(mask: "np.ndarray[Any, Any]", kernel_size: int) -> "np.ndarray[Any, Any]":
    require(kernel_size >= 1 and kernel_size % 2 == 1, f"dilation kernel must be positive and odd: {kernel_size}")
    if kernel_size == 1:
        return mask.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    return cv2.dilate(mask, kernel)


def premultiplied_rgba(rgba: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    values = rgba.astype(np.float32)
    alpha = values[..., 3:4] / 255.0
    return np.concatenate((values[..., :3] * alpha, values[..., 3:4]), axis=-1)


def donor_template(
    samples: "np.ndarray[Any, Any]",
    label_masks: "np.ndarray[Any, Any]",
) -> tuple["np.ndarray[Any, Any]", "np.ndarray[Any, Any]"]:
    require(samples.ndim == 5 and samples.shape[1:] == (STATE_COUNT, CELL_SIZE[1], CELL_SIZE[0], 4), "donor sample shape differs")
    require(label_masks.shape == (samples.shape[0], CELL_SIZE[1], CELL_SIZE[0]), "donor mask shape differs")
    premul = premultiplied_rgba(samples)
    support = (~label_masks).sum(axis=0).astype(np.int16)
    result = np.empty((STATE_COUNT, CELL_SIZE[1], CELL_SIZE[0], 4), dtype=np.float32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for state in range(STATE_COUNT):
            donors = np.where((~label_masks)[..., None], premul[:, state], np.nan)
            result[state] = np.nanmedian(donors, axis=0)
    return result, support


def straight_rgba(premul: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    alpha = np.clip(premul[..., 3:4], 0, 255)
    rgb = np.zeros_like(premul[..., :3])
    nonzero = alpha[..., 0] > 0
    rgb[nonzero] = premul[..., :3][nonzero] / (alpha[nonzero] / 255.0)
    return np.concatenate((np.clip(rgb, 0, 255), alpha), axis=-1).round().astype(np.uint8)


def build_clean_plate(
    locale_groups: Mapping[str, "np.ndarray[Any, Any]"],
) -> tuple["np.ndarray[Any, Any]", "np.ndarray[Any, Any]", dict[str, Any]]:
    samples: list[np.ndarray[Any, Any]] = []
    masks_primary: list[np.ndarray[Any, Any]] = []
    masks_fallback: list[np.ndarray[Any, Any]] = []
    for locale in ("JP", "SC", "TC", "EN"):
        groups = locale_groups[locale]
        require(groups.shape == (57, STATE_COUNT, CELL_SIZE[1], CELL_SIZE[0], 4), f"{locale} group matrix differs")
        for states in groups:
            core = label_core_mask(states)
            samples.append(states)
            masks_primary.append(dilate(core, DONOR_PRIMARY_KERNEL) > 0)
            masks_fallback.append(dilate(core, DONOR_FALLBACK_KERNEL) > 0)

    sample_matrix = np.stack(samples)
    primary, primary_support = donor_template(sample_matrix, np.stack(masks_primary))
    fallback, fallback_support = donor_template(sample_matrix, np.stack(masks_fallback))
    holes = primary_support == 0
    require(bool(np.all(fallback_support[holes] > 0)), "fallback donor mask has unsupported pixels")
    require(bool(np.all(np.isfinite(fallback[:, holes]))), "fallback donor values contain NaN")
    primary[:, holes] = fallback[:, holes]
    require(bool(np.all(np.isfinite(primary))), "clean-plate template contains NaN")
    template = straight_rgba(primary)

    source = locale_groups["JP"][PILOT_GROUP].copy()
    source_core = label_core_mask(source)
    cleanup_mask = dilate(source_core, CLEANUP_KERNEL) > 0
    clean = source.copy()
    clean[:, cleanup_mask, :] = template[:, cleanup_mask, :]

    outside_changed = int(np.count_nonzero(np.any(clean[:, ~cleanup_mask, :] != source[:, ~cleanup_mask, :], axis=-1)))
    protected_changed = int(np.count_nonzero(np.any(clean[:, :PROTECTED_BODY_END_Y, :, :] != source[:, :PROTECTED_BODY_END_Y, :, :], axis=-1)))
    require(outside_changed == 0, f"clean plate changed {outside_changed} pixels outside the Japanese label mask")
    require(protected_changed == 0, f"clean plate changed {protected_changed} protected body/icon pixels")

    clean_core = label_core_mask(clean, require_nonempty=False)
    metrics = {
        "official_samples": int(sample_matrix.shape[0]),
        "official_locales": 4,
        "groups_per_locale": 57,
        "states_per_group": STATE_COUNT,
        "source_core_pixels": int(np.count_nonzero(source_core)),
        "source_core_bbox": bbox_from_mask(source_core),
        "cleanup_mask_pixels": int(np.count_nonzero(cleanup_mask)),
        "cleanup_mask_bbox": bbox_from_mask(cleanup_mask),
        "primary_support_min": int(primary_support.min()),
        "primary_support_max": int(primary_support.max()),
        "primary_unsupported_pixels": int(np.count_nonzero(holes)),
        "fallback_support_min_at_primary_holes": int(fallback_support[holes].min()) if np.any(holes) else None,
        "clean_residual_core_pixels": int(np.count_nonzero(clean_core)),
        "clean_residual_core_bbox": bbox_from_mask(clean_core),
        "outside_cleanup_mask_changed_pixels": outside_changed,
        "protected_body_end_y_exclusive": PROTECTED_BODY_END_Y,
        "protected_body_changed_pixels": protected_changed,
    }
    return source, clean, metrics | {"source_core_mask": source_core, "cleanup_mask": cleanup_mask}


def render_fill_mask(font_path: Path) -> tuple[Image.Image, dict[str, Any]]:
    candidate = text_candidates.Candidate(
        "b_seoul_hangang_eb",
        "B SeoulHangang ExtraBold",
        "selected wheel typography",
        font_path,
        FONT_SHA256,
        None,
        TRACKING_EM,
    )
    target_height = TARGET_INK_HEIGHT * OVERSAMPLE
    low, high = 4 * OVERSAMPLE, 64 * OVERSAMPLE
    best: tuple[int, Image.Image, int] | None = None
    while low <= high:
        size = (low + high) // 2
        font = text_candidates.load_font(candidate, size)
        mask = text_candidates.render_chars(PILOT_KO, font, TRACKING_EM * size)
        delta = abs(mask.height - target_height)
        if best is None or delta < best[0]:
            best = (delta, mask, size)
        if mask.height < target_height:
            low = size + 1
        elif mask.height > target_height:
            high = size - 1
        else:
            break
    require(best is not None, "font-size search failed")
    _delta, mask, font_size = best
    if mask.height != target_height:
        mask = mask.resize((max(1, round(mask.width * target_height / mask.height)), target_height), Image.Resampling.LANCZOS)
    natural_width = mask.width
    maximum_width = SAFE_INK_WIDTH * OVERSAMPLE
    horizontal_scale = min(1.0, maximum_width / natural_width)
    if horizontal_scale < 1.0:
        mask = mask.resize((maximum_width, mask.height), Image.Resampling.LANCZOS)
    require(horizontal_scale >= 0.86, f"Korean label requires excessive horizontal condensation: {horizontal_scale:.4f}")
    return mask, {
        "font_size_oversampled_px": font_size,
        "natural_fill_size_oversampled_px": [natural_width, target_height],
        "final_fill_size_oversampled_px": [mask.width, mask.height],
        "horizontal_fit_scale": round(horizontal_scale, 6),
    }


def colored(mask: Image.Image, rgba: tuple[int, int, int, int]) -> Image.Image:
    result = Image.new("RGBA", mask.size, rgba)
    if rgba[3] == 255:
        result.putalpha(mask)
    else:
        alpha_lut = [round(value * rgba[3] / 255) for value in range(256)]
        result.putalpha(mask.point(alpha_lut))
    return result


def render_text_layers(font_path: Path) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    fill, fill_metrics = render_fill_mask(font_path)
    cell_size = (CELL_SIZE[0] * OVERSAMPLE, CELL_SIZE[1] * OVERSAMPLE)
    fill_cell = Image.new("L", cell_size, 0)
    x = (cell_size[0] - fill.width) // 2
    y = INK_BOTTOM * OVERSAMPLE - fill.height
    fill_cell.paste(fill, (x, y))
    stroke_mask = fill_cell.filter(ImageFilter.MaxFilter(odd_filter_size(STROKE_RADIUS)))
    outer_mask = fill_cell.filter(ImageFilter.MaxFilter(odd_filter_size(OUTER_RADIUS)))
    outer_mask = outer_mask.filter(ImageFilter.GaussianBlur(OUTER_SOFTEN * OVERSAMPLE))

    layers: list[np.ndarray[Any, Any]] = []
    rows: list[dict[str, Any]] = []
    for style in STATE_PALETTES:
        layer = Image.new("RGBA", cell_size, (0, 0, 0, 0))
        layer.alpha_composite(colored(outer_mask, style.outer))
        layer.alpha_composite(colored(stroke_mask, style.stroke))
        layer.alpha_composite(colored(fill_cell, style.fill))
        native = layer.resize(CELL_SIZE, Image.Resampling.LANCZOS)
        values = np.asarray(native).copy()
        alpha_mask = values[..., 3] > 0
        layer_bbox = bbox_from_mask(alpha_mask)
        require(layer_bbox is not None, f"state {style.state} label layer is empty")
        x0, y0, x1, y1 = layer_bbox
        require(x0 >= 4 and x1 <= CELL_SIZE[0] - 4, f"state {style.state} violates horizontal safety margin: {layer_bbox}")
        require(y0 >= PROTECTED_BODY_END_Y and y1 <= CELL_SIZE[1] - 2, f"state {style.state} violates vertical safety margin: {layer_bbox}")
        layers.append(values)
        rows.append({
            "state": style.state,
            "role": style.role,
            "fill": list(style.fill),
            "stroke": list(style.stroke),
            "outer": list(style.outer),
            "layer_bbox": layer_bbox,
            "layer_pixels": int(np.count_nonzero(alpha_mask)),
        })
    return np.stack(layers), fill_metrics | {"states": rows}


def alpha_composite(base: "np.ndarray[Any, Any]", overlay: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    return np.asarray(Image.alpha_composite(Image.fromarray(base), Image.fromarray(overlay))).copy()


def checker(size: tuple[int, int], block: int = 5) -> Image.Image:
    result = Image.new("RGB", size, (57, 60, 66))
    draw = ImageDraw.Draw(result)
    for y in range(0, size[1], block):
        for x in range(0, size[0], block):
            if (x // block + y // block) % 2:
                draw.rectangle((x, y, x + block - 1, y + block - 1), fill=(39, 42, 47))
    return result


def preview(values: "np.ndarray[Any, Any]", zoom: int, *, label_only: bool = False) -> Image.Image:
    image = Image.fromarray(values)
    background = checker(CELL_SIZE) if label_only else Image.new("RGB", CELL_SIZE, (0, 255, 0))
    background.paste(image, (0, 0), image)
    return background.resize((CELL_SIZE[0] * zoom, CELL_SIZE[1] * zoom), Image.Resampling.NEAREST)


def mask_overlay(source: "np.ndarray[Any, Any]", mask: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    result = source.copy()
    rgb = result[..., :3].astype(np.float32)
    rgb[mask] = rgb[mask] * 0.30 + np.asarray((255, 0, 180), dtype=np.float32) * 0.70
    result[..., :3] = np.clip(rgb, 0, 255).round().astype(np.uint8)
    return result


def contact_sheet(
    source: "np.ndarray[Any, Any]",
    cleanup_mask: "np.ndarray[Any, Any]",
    clean: "np.ndarray[Any, Any]",
    layers: "np.ndarray[Any, Any]",
    composites: "np.ndarray[Any, Any]",
    ui_font_path: Path,
) -> Image.Image:
    zoom = 3
    cell_width, cell_height = CELL_SIZE[0] * zoom, CELL_SIZE[1] * zoom
    gap = 16
    left = 190
    top = 46
    rows = (
        ("JP 원본", source, False),
        ("제거 마스크", np.stack([mask_overlay(source[state], cleanup_mask) for state in range(STATE_COUNT)]), False),
        ("글자 제거 플레이트", clean, False),
        ("B 투명 글자 레이어", layers, True),
        ("B 합성", composites, False),
    )
    width = left + STATE_COUNT * (cell_width + gap) + gap
    height = top + len(rows) * (cell_height + gap) + 62
    sheet = Image.new("RGB", (width, height), (25, 27, 31))
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.truetype(str(ui_font_path), 20)
    title_font.set_variation_by_axes([750])
    small_font = ImageFont.truetype(str(ui_font_path), 15)
    small_font.set_variation_by_axes([600])
    for state in range(STATE_COUNT):
        draw.text((left + state * (cell_width + gap) + 112, 12), f"상태 {state + 1}", font=title_font, fill=(238, 239, 241))
    for row_index, (label, matrix, label_only) in enumerate(rows):
        y = top + row_index * (cell_height + gap)
        draw.text((12, y + cell_height // 2 - 11), label, font=title_font, fill=(230, 232, 235))
        for state in range(STATE_COUNT):
            cell = preview(matrix[state], zoom, label_only=label_only)
            x = left + state * (cell_width + gap)
            sheet.paste(cell, (x, y))
            draw.rectangle((x, y, x + cell_width - 1, y + cell_height - 1), outline=(87, 92, 102), width=1)
    draw.text(
        (12, height - 42),
        "공식 JP/SC/TC/EN 교차 대조 · 생성형 처리 없음 · 원본 몸체/아이콘 좌표 유지 · 1px을 3배 정수 확대",
        font=small_font,
        fill=(178, 184, 194),
    )
    return sheet


def save_rgba(path: Path, values: "np.ndarray[Any, Any]") -> None:
    Image.fromarray(values).save(path, optimize=False, compress_level=9)


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output.resolve()
    tmp_root = (REPO / "tmp").resolve()
    try:
        output.relative_to(tmp_root)
    except ValueError as exc:
        raise PilotError(f"output must stay below repo tmp: {output}") from exc
    require(not output.exists(), f"output already exists: {output}")

    route = route_spec()
    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    require(mapping.get("schema") == "nobu16.kr.wheel-detail-groups.v1", "wheel mapping schema differs")
    selected_mapping = [item for item in mapping["groups"] if item["name"] == PILOT_NAME]
    require(len(selected_mapping) == 1 and int(selected_mapping[0]["source_group"]) == PILOT_GROUP, "pilot mapping differs")
    require(selected_mapping[0]["jp"] == PILOT_JP and selected_mapping[0]["ko"] == PILOT_KO, "pilot label mapping differs")

    font_pin = validate_file(args.font, {"size": args.font.stat().st_size if args.font.is_file() else -1, "sha256": FONT_SHA256}, "B font")
    ui_font_pin = validate_file(args.ui_font, {"size": args.ui_font.stat().st_size if args.ui_font.is_file() else -1, "sha256": UI_FONT_SHA256}, "contact-sheet UI font")
    locale_pin_map = locale_specs(args.input_pins)

    input_report: dict[str, Any] = {}
    locale_groups: dict[str, np.ndarray[Any, Any]] = {}
    jp_path = args.jp_source_root / str(route["relative_path"])
    input_report["JP"] = validate_file(jp_path, route["source"], "JP stock source")
    locale_groups["JP"], input_report["JP"]["resource"] = extract_groups(jp_path, route, mapping)
    for locale in ("SC", "TC", "EN"):
        spec = locale_pin_map[locale]
        path = args.official_root / str(spec["relative_path"])
        input_report[locale] = validate_file(path, spec, f"{locale} official source")
        locale_groups[locale], input_report[locale]["resource"] = extract_groups(path, route, mapping)

    source, clean, clean_report = build_clean_plate(locale_groups)
    source_core = clean_report.pop("source_core_mask")
    cleanup_mask = clean_report.pop("cleanup_mask")
    layers, text_report = render_text_layers(args.font)
    composites = np.stack([alpha_composite(clean[state], layers[state]) for state in range(STATE_COUNT)])
    final_protected_changed = int(
        np.count_nonzero(np.any(composites[:, :PROTECTED_BODY_END_Y] != source[:, :PROTECTED_BODY_END_Y], axis=-1))
    )
    require(final_protected_changed == 0, f"B composite changed {final_protected_changed} protected body/icon pixels")

    output.mkdir(parents=True)
    for directory in ("source", "masks", "clean_plate", "text_layers", "composite"):
        (output / directory).mkdir()
    generated: list[Path] = []
    Image.fromarray(source_core).save(output / "masks" / "source_core.png", optimize=False, compress_level=9)
    generated.append(output / "masks" / "source_core.png")
    Image.fromarray((cleanup_mask.astype(np.uint8) * 255)).save(output / "masks" / "cleanup_k11.png", optimize=False, compress_level=9)
    generated.append(output / "masks" / "cleanup_k11.png")
    for state in range(STATE_COUNT):
        for directory, matrix in (
            ("source", source),
            ("clean_plate", clean),
            ("text_layers", layers),
            ("composite", composites),
        ):
            path = output / directory / f"state_{state + 1}.png"
            save_rgba(path, matrix[state])
            generated.append(path)

    sheet = contact_sheet(source, cleanup_mask, clean, layers, composites, args.ui_font)
    sheet_path = output / "navigation_wheel_layered_pilot_v1.png"
    sheet.save(sheet_path, optimize=False, compress_level=9)
    generated.append(sheet_path)

    artifacts = {
        str(path.relative_to(output)).replace("\\", "/"): {
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(generated)
    }
    manifest = {
        "schema": SCHEMA,
        "generation_policy": GENERATION_POLICY,
        "archive_writes": 0,
        "steam_writes": 0,
        "patcher_writes": 0,
        "scope": {
            "route": ROUTE_ID,
            "family": PILOT_FAMILY,
            "group": PILOT_GROUP,
            "name": PILOT_NAME,
            "jp": PILOT_JP,
            "ko": PILOT_KO,
            "states": STATE_COUNT,
            "cell_size_px": list(CELL_SIZE),
        },
        "inputs": {
            "font": font_pin,
            "ui_font": ui_font_pin,
            "mapping": {
                "path": str(args.mapping.resolve()),
                "size": args.mapping.stat().st_size,
                "sha256": sha256_file(args.mapping),
            },
            "locale_pin_table": {
                "path": str(args.input_pins.resolve()),
                "size": args.input_pins.stat().st_size,
                "sha256": sha256_file(args.input_pins),
            },
            "official_sources": input_report,
        },
        "separation": {
            "method": "premultiplied-RGBA median of official-locale donors outside per-group label masks",
            "label_scan_y": LABEL_SCAN_Y,
            "donor_primary_kernel": DONOR_PRIMARY_KERNEL,
            "donor_fallback_kernel": DONOR_FALLBACK_KERNEL,
            "cleanup_kernel": CLEANUP_KERNEL,
            **clean_report,
        },
        "text_rendering": {
            "font": "SeoulHangang ExtraBold",
            "pillow_version": pillow_version,
            "oversample": OVERSAMPLE,
            "tracking_em": TRACKING_EM,
            "target_ink_height_px": TARGET_INK_HEIGHT,
            "ink_bottom_px": INK_BOTTOM,
            "safe_ink_width_px": SAFE_INK_WIDTH,
            "stroke_radius_px": STROKE_RADIUS,
            "outer_radius_px": OUTER_RADIUS,
            "outer_soften_px": OUTER_SOFTEN,
            "font_aspect_ratio_changed": False,
            **text_report,
        },
        "validation": {
            "clean_plate_outside_cleanup_mask_changed_pixels": clean_report["outside_cleanup_mask_changed_pixels"],
            "clean_plate_protected_body_changed_pixels": clean_report["protected_body_changed_pixels"],
            "composite_protected_body_changed_pixels": final_protected_changed,
            "contact_sheet": sheet_path.name,
        },
        "artifacts": artifacts,
    }
    manifest_path = output / "manifest.v1.json"
    write_json(manifest_path, manifest)
    return {
        "output": str(output),
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": sha256_file(sheet_path),
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "primary_unsupported_pixels": clean_report["primary_unsupported_pixels"],
        "clean_residual_core_pixels": clean_report["clean_residual_core_pixels"],
        "protected_body_changed_pixels": final_protected_changed,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--jp-source-root", type=Path, default=DEFAULT_JP_SOURCE_ROOT)
    result.add_argument("--official-root", type=Path, default=DEFAULT_OFFICIAL_ROOT)
    result.add_argument("--font", type=Path, default=DEFAULT_FONT)
    result.add_argument("--ui-font", type=Path, default=DEFAULT_UI_FONT)
    result.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    result.add_argument("--input-pins", type=Path, default=DEFAULT_INPUT_PINS)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
