#!/usr/bin/env python3
"""Rebuild ``전체승인`` with the approved non-generative B pipeline.

The builder handles both native PK routes.  It derives clean button plates
from pinned JP/EN/SC/TC stock cells (plus the same-atlas compact-label donor),
renders SeoulHangang ExtraBold with the explicit compact/80%-width exception
for this long label, and replaces only BC7 blocks touched by the six verified
cells in each archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
WORKSPACE = REPO.parent.parent
TOOLS = REPO / "tools"
HIGHRES_WS = REPO / "workstreams" / "steam_jp_port_highres_images_v1"
ISSUE117_WS = REPO / "workstreams" / "issue_117_highres_buttons_v1"
PILOT_WS = REPO / "workstreams" / "ordinary_button_layered_render_pilot_v1"
DEFAULT_DEPENDENCY_ROOT = REPO / "tmp" / "issue117_pydeps"
for candidate in (DEFAULT_DEPENDENCY_ROOT, TOOLS, HIGHRES_WS, ISSUE117_WS, PILOT_WS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import build_issue_117_highres_buttons_v1 as issue117  # noqa: E402
import build_ordinary_button_layered_render_pilot_v1 as pilot  # noqa: E402
import build_steam_jp_port_highres_images_v1 as highres  # noqa: E402
import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402

try:
    import cv2  # type: ignore
    import numpy as np
    from PIL import Image
except ImportError as exc:  # pragma: no cover - bundled runtime invariant.
    raise RuntimeError("NumPy, OpenCV and Pillow are required") from exc


SCHEMA = "nobu16.kr.ordinary-button-approve-all-layered.v1"
GENERATION_POLICY = "forbidden-and-not-used"
LABEL = "전체승인"
FONT_PIN = {
    "size": 7_350_712,
    "sha256": "60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1",
}
VARIANT = "approve_all_compact"
ASPECT_SCALE_X = 0.80
ASPECT_CANDIDATES = (0.84, 0.82, ASPECT_SCALE_X)
TRACKING_GRADE = "standard"
TRACKING_EM = pilot.TRACKING_EM
GAP_ALPHA_THRESHOLD = 8
GAP_TOLERANCE_NATIVE_PX = 0.75
STATE_ROLES = ("white", "cyan", "blue", "disabled", "cyan_alt", "disabled_alt")
LOCALES = ("JP", "EN", "SC", "TC")


@dataclass(frozen=True)
class RouteSpec:
    route_id: str
    resolution: str
    relative_path: str
    outer_entry: int
    resource_id: int
    texture_index: int
    dimensions: tuple[int, int]
    cell_size: tuple[int, int]
    typography_route: str
    target_height: int
    oversample: int
    center: tuple[float, float]
    safe_zone: tuple[int, int]
    interior_text_lane: tuple[int, int]
    icon_candidate_x: int
    icon_protect_kernel: int
    cleanup_kernel: int
    target_pin: Mapping[str, Any]
    source_pins: Mapping[str, Mapping[str, Any]]
    primary_rects: Mapping[str, tuple[tuple[int, int, int, int], ...]]
    compact_rects: Mapping[str, tuple[tuple[int, int, int, int], ...]]


LOW_JP_RECTS = (
    (1208, 96, 1400, 184),
    (1400, 96, 1592, 184),
    (1592, 96, 1784, 184),
    (1784, 96, 1976, 184),
    (0, 160, 192, 248),
    (192, 160, 384, 248),
)
LOW_EN_RECTS = (
    (1376, 0, 1568, 88),
    (1568, 0, 1760, 88),
    (1760, 0, 1952, 88),
    (1376, 88, 1568, 176),
    (1568, 88, 1760, 176),
    (1760, 88, 1952, 176),
)
LOW_JP_COMPACT_RECTS = (
    (384, 160, 576, 248),
    (576, 160, 768, 248),
    (768, 160, 960, 248),
    (960, 160, 1152, 248),
    (1152, 184, 1344, 272),
    (1344, 184, 1536, 272),
)
LOW_EN_COMPACT_RECTS = (
    (788, 160, 980, 248),
    (980, 160, 1172, 248),
    (1172, 160, 1364, 248),
    (1364, 176, 1556, 264),
    (1556, 176, 1748, 264),
    (1748, 176, 1940, 264),
)

HIGH_JP_RECTS = (
    (2412, 188, 2780, 348),
    (2788, 188, 3156, 348),
    (3164, 188, 3532, 348),
    (3540, 188, 3908, 348),
    (4, 308, 372, 468),
    (380, 308, 748, 468),
)
HIGH_EN_RECTS = (
    (2812, 4, 3180, 164),
    (3188, 4, 3556, 164),
    (3564, 4, 3932, 164),
    (2748, 172, 3116, 332),
    (3124, 172, 3492, 332),
    (3500, 172, 3868, 332),
)
HIGH_JP_COMPACT_RECTS = (
    (756, 308, 1124, 468),
    (1132, 308, 1500, 468),
    (1508, 308, 1876, 468),
    (1884, 308, 2252, 468),
    (2260, 356, 2628, 516),
    (2636, 356, 3004, 516),
)
HIGH_EN_COMPACT_RECTS = (
    (1404, 308, 1772, 468),
    (1780, 308, 2148, 468),
    (2156, 308, 2524, 468),
    (2532, 340, 2900, 500),
    (2908, 340, 3276, 500),
    (3284, 340, 3652, 500),
)


LOW_SOURCE_PINS: Mapping[str, Mapping[str, Any]] = {
    "JP": {"size": 4_620_368, "sha256": "DF974BB7918E9A242E46A133ED95C674EBFBCD361EFE1F714CA7A61DB1118E33"},
    "EN": {"size": 4_492_610, "sha256": "29C928516E7FD592D1F7C993F3371041FDECA8CE890A0864584BC2B361228A41"},
    "SC": {"size": 3_988_353, "sha256": "53EC345ECB198D3716E483808B438465FFBD8BA627460CCA0994F25D336E4943"},
    "TC": {"size": 4_256_813, "sha256": "37696E555B8282AAAC806B080B695B212900824763F6E85E6D6BFBE05FCD0BD6"},
}
HIGH_SOURCE_PINS: Mapping[str, Mapping[str, Any]] = {
    "JP": {"size": 61_609_467, "sha256": "52A8DE4BA1480E86218AC0CDE50DA946B4BCDFD7053ED85B94B04E663C00B380"},
    "EN": {"size": 23_199_907, "sha256": "C6F012B7482AB4BF7D2266170649199C29A5E0FB6AF13D3D060DA34FA8CCEC57"},
    "SC": {"size": 21_642_351, "sha256": "D7132F8B0CC10C477AD70295A1E948C83D3902AB4DA2A458CFFDA8D2749CDDBC"},
    "TC": {"size": 22_537_924, "sha256": "42C82BEB4524FB0E4FC9ED61AFF1EDB24422F196EC7424A831EB9E687C94EB77"},
}


ROUTES: tuple[RouteSpec, ...] = (
    RouteSpec(
        route_id="pk_low_approve_all",
        resolution="low",
        relative_path="RES_JP_PK/res_lang_exp_pk.bin",
        outer_entry=4,
        resource_id=870,
        texture_index=1,
        dimensions=(2048, 512),
        cell_size=(192, 88),
        typography_route="common_low",
        target_height=26,
        oversample=8,
        center=(117.0, 41.0),
        safe_zone=(78, 184),
        interior_text_lane=(74, 178),
        icon_candidate_x=84,
        icon_protect_kernel=7,
        cleanup_kernel=11,
        target_pin={"size": 4_613_935, "sha256": "BD0B5B8C86BE48210C052D3DDA9DE9D291089D44093DEAD2FCC932BA43B6825E"},
        source_pins=LOW_SOURCE_PINS,
        primary_rects={"JP": LOW_JP_RECTS, "EN": LOW_EN_RECTS, "SC": LOW_JP_RECTS, "TC": LOW_JP_RECTS},
        compact_rects={"JP": LOW_JP_COMPACT_RECTS, "EN": LOW_EN_COMPACT_RECTS, "SC": LOW_JP_COMPACT_RECTS, "TC": LOW_JP_COMPACT_RECTS},
    ),
    RouteSpec(
        route_id="pk_high_approve_all",
        resolution="high",
        relative_path="RES_JP_PK_PORT/res_lang_pk_port2.bin",
        outer_entry=2,
        resource_id=870,
        texture_index=1,
        dimensions=(4096, 1024),
        cell_size=(368, 160),
        typography_route="common_high_standard",
        target_height=52,
        oversample=4,
        center=(227.0, 76.0),
        safe_zone=(140, 352),
        interior_text_lane=(140, 338),
        icon_candidate_x=148,
        icon_protect_kernel=13,
        cleanup_kernel=21,
        target_pin={"size": 67_340_514, "sha256": "47F290F225B3AB50315A4455FD28FA8EF2A33212D35944A2681F1329ECE09B11"},
        source_pins=HIGH_SOURCE_PINS,
        primary_rects={"JP": HIGH_JP_RECTS, "EN": HIGH_EN_RECTS, "SC": HIGH_JP_RECTS, "TC": HIGH_JP_RECTS},
        compact_rects={"JP": HIGH_JP_COMPACT_RECTS, "EN": HIGH_EN_COMPACT_RECTS, "SC": HIGH_JP_COMPACT_RECTS, "TC": HIGH_JP_COMPACT_RECTS},
    ),
)


class BuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "size": path.stat().st_size, "sha256": sha256_file(path)}


def validate_file(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is missing: {path}")
    actual = file_spec(path)
    require(actual["size"] == int(expected["size"]) and actual["sha256"] == str(expected["sha256"]), f"{label} pin differs: {actual}")
    return actual


def canonical_rgba(values: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    return pilot.wheel.canonical_rgba(values)


def bbox(mask: "np.ndarray[Any, Any]") -> list[int] | None:
    return pilot.bbox(mask)


def fresh_output(path: Path) -> Path:
    value = path.resolve()
    tmp = (REPO / "tmp").resolve()
    try:
        value.relative_to(tmp)
    except ValueError as exc:
        raise BuildError(f"output must stay below {tmp}: {value}") from exc
    require(not value.exists(), f"refusing to replace existing output: {value}")
    value.mkdir(parents=True)
    return value


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    require(not temporary.exists(), f"temporary output exists: {temporary}")
    temporary.write_bytes(payload)
    temporary.replace(path)


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def source_paths(args: argparse.Namespace, route: RouteSpec) -> Mapping[str, Path]:
    if route.resolution == "low":
        return {
            "JP": args.jp_source_root / Path(route.relative_path),
            "EN": args.official_root / "RES_EN_PK" / "res_lang_exp_pk.bin",
            "SC": args.official_root / "RES_SC_PK" / "res_lang_exp_pk.bin",
            "TC": args.official_root / "RES_TC_PK" / "res_lang_exp_pk.bin",
        }
    return {
        "JP": args.jp_source_root / Path(route.relative_path),
        "EN": args.official_root / "RES_EN_PK_PORT" / "res_lang_pk_port2.bin",
        "SC": args.official_root / "RES_SC_PK_PORT" / "res_lang_pk_port2.bin",
        "TC": args.tc_high,
    }


def load_atlas(
    path: Path,
    route: RouteSpec,
    decoder: Any,
) -> tuple[Image.Image, dict[str, Any], tuple[bytes, lz4.LinkArchive, highres.NestedLink, lz4.WrapperHeader, bytes, atlas_codec.G1T]]:
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"outer LINK identity failed: {path}")
    require(route.outer_entry < len(outer.entries), f"outer entry absent: {path}")
    nested = highres.parse_nested_link(outer.entries[route.outer_entry].data, expected_resource_id=route.resource_id)
    slot, header, raw, g1t = highres.g1t_wrapper_entry(nested)
    require(slot == 0, f"nested G1T slot differs: {path} {slot}")
    require(route.texture_index < len(g1t.textures), f"texture absent: {path}")
    texture = g1t.textures[route.texture_index]
    require((texture.format_code, texture.width, texture.height) == (0x5F, *route.dimensions), f"texture contract differs: {path}")
    payload = issue117.bc7_texture_payload(raw, texture)
    atlas = issue117.decode_bc7(payload, texture.width, texture.height, decoder)
    return atlas, {
        "outer_entry": route.outer_entry,
        "resource_id": route.resource_id,
        "nested_slot": slot,
        "texture_index": route.texture_index,
        "format": "BC7/0x5F",
        "dimensions": list(route.dimensions),
    }, (blob, outer, nested, header, raw, g1t)


def extract_states(
    atlas: Image.Image,
    rects: Sequence[Sequence[int]],
    expected_size: tuple[int, int],
) -> "np.ndarray[Any, Any]":
    require(len(rects) == 6, "state rectangle coverage differs")
    states: list[np.ndarray[Any, Any]] = []
    for rect in rects:
        left, top, right, bottom = (int(value) for value in rect)
        require((right - left, bottom - top) == expected_size, f"cell size differs: {rect}")
        require(0 <= left < right <= atlas.width and 0 <= top < bottom <= atlas.height, f"cell escaped atlas: {rect}")
        states.append(np.asarray(atlas.crop((left, top, right, bottom)).convert("RGBA"), dtype=np.uint8).copy())
    return np.stack(states)


def icon_and_cleanup_masks(
    source: "np.ndarray[Any, Any]",
    route: RouteSpec,
) -> tuple[
    "np.ndarray[Any, Any]",
    "np.ndarray[Any, Any]",
    "np.ndarray[Any, Any]",
    "np.ndarray[Any, Any]",
    dict[str, Any],
]:
    core = pilot.original_foreground_core(source, route.typography_route)
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(core.astype(np.uint8), 8)
    candidates = [
        index for index in range(1, count)
        if int(stats[index, cv2.CC_STAT_LEFT]) < route.icon_candidate_x
    ]
    require(candidates, f"icon component is absent: {route.route_id}")
    icon_index = max(candidates, key=lambda index: int(stats[index, cv2.CC_STAT_AREA]))
    icon_core = (labels == icon_index).astype(np.uint8)
    protected = pilot.wheel.dilate(icon_core * 255, route.icon_protect_kernel) > 0
    text_core = core.copy()
    text_core[labels == icon_index] = 0
    require(bool(np.any(text_core)), f"source label core is empty: {route.route_id}")
    cleanup = pilot.wheel.dilate(text_core * 255, route.cleanup_kernel) > 0
    require(bool(np.any(cleanup)), f"source cleanup mask is empty: {route.route_id}")
    return cleanup, protected, icon_core > 0, text_core > 0, {
        "method": "six-state-foreground-transition-plus-connected-icon-separation",
        "source_foreground_core_pixels": int(np.count_nonzero(core)),
        "source_foreground_core_bbox": bbox(core),
        "source_label_core_pixels": int(np.count_nonzero(text_core)),
        "source_label_core_bbox": bbox(text_core),
        "cleanup_pixels": int(np.count_nonzero(cleanup)),
        "cleanup_bbox": bbox(cleanup),
        "icon_component_core_pixels": int(np.count_nonzero(icon_core)),
        "icon_component_core_bbox": bbox(icon_core),
        "protected_icon_pixels": int(np.count_nonzero(protected)),
        "protected_icon_bbox": bbox(protected),
        "cleanup_kernel": route.cleanup_kernel,
        "icon_protect_kernel": route.icon_protect_kernel,
    }


def minimum_mask_distance(
    first: "np.ndarray[Any, Any]",
    second: "np.ndarray[Any, Any]",
) -> float:
    require(first.shape == second.shape, "distance mask geometry differs")
    require(bool(np.any(first)) and bool(np.any(second)), "distance mask is empty")
    distance = cv2.distanceTransform(
        (~first.astype(bool)).astype(np.uint8),
        cv2.DIST_L2,
        cv2.DIST_MASK_PRECISE,
    )
    return float(np.min(distance[second.astype(bool)]))


def donor_foreground_mask(states: "np.ndarray[Any, Any]", route: RouteSpec) -> "np.ndarray[Any, Any]":
    core = pilot.original_foreground_core(states, route.typography_route)
    return pilot.wheel.dilate(core * 255, route.cleanup_kernel) > 0


def clean_stock_cells(
    source: "np.ndarray[Any, Any]",
    samples: Sequence["np.ndarray[Any, Any]"],
    donor_masks: Sequence["np.ndarray[Any, Any]"],
    cleanup: "np.ndarray[Any, Any]",
    protected: "np.ndarray[Any, Any]",
    route: RouteSpec,
) -> tuple["np.ndarray[Any, Any]", dict[str, Any]]:
    require(len(samples) == len(donor_masks) == 8, f"donor coverage differs: {route.route_id}")
    # Samples are appended as JP primary, JP compact, EN primary, EN compact,
    # SC primary, SC compact, TC primary, TC compact.  The JP compact-label
    # button is the closest material match and keeps each state internally
    # coherent.  Copy it at the same coordinate whenever its source label does
    # not cover the pixel; for the remaining compact-label pixels, copy the
    # nearest real pixel on the same material row.  No interpolated or
    # synthesized colour is introduced.
    donor = samples[1]
    donor_foreground = donor_masks[1]
    clean = source.copy()
    exact = cleanup & ~donor_foreground
    clean[:, exact] = donor[:, exact]
    remaining = cleanup & donor_foreground
    cleanup_box = bbox(cleanup)
    require(cleanup_box is not None, f"cleanup bbox is empty: {route.route_id}")
    scale = pilot.scale_for_route(route.typography_route)
    left = max(0, cleanup_box[0] - 16 * scale)
    right = min(route.cell_size[0], cleanup_box[2] + 16 * scale)
    nearest_same_row = 0
    for y in np.nonzero(np.any(remaining, axis=1))[0].tolist():
        available = np.nonzero(~donor_foreground[y, left:right])[0] + left
        require(len(available) > 0, f"no same-row donor pixel exists: {route.route_id} y={y}")
        for x in np.nonzero(remaining[y])[0].tolist():
            nearest_x = int(available[int(np.argmin(np.abs(available - x)))])
            clean[:, y, x] = donor[:, y, nearest_x]
            nearest_same_row += 1
    clean[:, protected] = source[:, protected]
    outside = int(np.count_nonzero(np.any(canonical_rgba(clean) != canonical_rgba(source), axis=-1) & ~cleanup[None]))
    protected_difference = int(np.count_nonzero(np.any(canonical_rgba(clean[:, protected]) != canonical_rgba(source[:, protected]), axis=-1)))
    require(outside == 0, f"clean plate escaped cleanup mask: {route.route_id} {outside}")
    require(protected_difference == 0, f"clean plate changed protected icon: {route.route_id} {protected_difference}")
    return clean, {
        "method": "same-atlas-jp-compact-label-exact-pixel-copy-with-nearest-same-row-fallback",
        "official_locales": list(LOCALES),
        "donor_groups": len(samples),
        "primary_groups": len(LOCALES),
        "same_atlas_compact_label_groups": len(LOCALES),
        "selected_material_donor": "JP same-atlas compact-label button",
        "exact_same_coordinate_pixels": int(np.count_nonzero(exact)),
        "nearest_same_row_actual_donor_pixels": nearest_same_row,
        "required_pixels": int(np.count_nonzero(cleanup)),
        "interpolation_used": False,
        "generation_used": False,
        "outside_cleanup_changed_pixels": outside,
        "protected_icon_canonical_rgba_differences": protected_difference,
    }


def compose_cells(
    source: "np.ndarray[Any, Any]",
    clean: "np.ndarray[Any, Any]",
    cleanup: "np.ndarray[Any, Any]",
    protected: "np.ndarray[Any, Any]",
    icon_core: "np.ndarray[Any, Any]",
    source_label_core: "np.ndarray[Any, Any]",
    route: RouteSpec,
    font: Path,
    tracking_em: float = TRACKING_EM,
    aspect_scale_x: float = ASPECT_SCALE_X,
    enforce_gap_contract: bool = True,
) -> tuple["np.ndarray[Any, Any]", "np.ndarray[Any, Any]", dict[str, Any]]:
    layers, typography = pilot.render_layers(
        route_id=route.typography_route,
        text=LABEL,
        variant=VARIANT,
        cell_size=route.cell_size,
        center=route.center,
        safe_zone=route.safe_zone,
        font_path=font,
        tracking_em=tracking_em,
        aspect_scale_x=aspect_scale_x,
        target_height_override=route.target_height,
    )
    require(typography["target_fill_height_native_px"] == route.target_height, f"compact height differs: {route.route_id}")
    require(typography["target_height_override_used"] is True, f"compact override flag differs: {route.route_id}")
    require(typography["oversample"] == route.oversample, f"oversample differs: {route.route_id}")
    require(typography["uniform_fit_scale"] == 1.0, f"label required fit scaling: {route.route_id}")
    require(typography["font_aspect_ratio_changed"] is (aspect_scale_x != 1.0), f"font aspect flag differs: {route.route_id}")
    require(typography["aspect_scale_x"] == aspect_scale_x, f"font aspect value differs: {route.route_id}")
    source_gap = minimum_mask_distance(icon_core, source_label_core)
    rendered_fill = layers[0, ..., 3] > GAP_ALPHA_THRESHOLD
    rendered_gap = minimum_mask_distance(icon_core, rendered_fill)
    gap_delta = rendered_gap - source_gap
    if enforce_gap_contract:
        require(
            abs(gap_delta) <= GAP_TOLERANCE_NATIVE_PX,
            f"check-to-label gap differs from stock: {route.route_id} "
            f"source={source_gap:.6f} rendered={rendered_gap:.6f}",
        )
    for state in typography["states"]:
        layer_box = state["layer_bbox"]
        require(
            layer_box[0] >= route.interior_text_lane[0] and layer_box[2] <= route.interior_text_lane[1],
            f"label escaped interior text lane: {route.route_id} {state['role']} {layer_box}",
        )
    overlap = int(np.count_nonzero((layers[..., 3] > 0) & protected[None]))
    if enforce_gap_contract:
        require(overlap == 0, f"label intersects protected icon: {route.route_id} {overlap}")
    final = np.stack([pilot.wheel.alpha_composite(clean[state], layers[state]) for state in range(6)])
    final[:, protected] = source[:, protected]
    allowed = cleanup[None] | (layers[..., 3] > 0)
    escaped = int(np.count_nonzero(np.any(canonical_rgba(final) != canonical_rgba(source), axis=-1) & ~allowed))
    icon_difference = int(np.count_nonzero(np.any(canonical_rgba(final[:, protected]) != canonical_rgba(source[:, protected]), axis=-1)))
    require(escaped == 0, f"composite escaped cleanup/label union: {route.route_id} {escaped}")
    require(icon_difference == 0, f"composite changed protected icon: {route.route_id} {icon_difference}")
    return final, layers, {
        **typography,
        "label": LABEL,
        "tracking_grade": TRACKING_GRADE if tracking_em == TRACKING_EM else "pilot",
        "interior_text_lane_x": list(route.interior_text_lane),
        "gap_contract": "minimum Euclidean distance from stock check core to visible white-state label fill",
        "gap_alpha_threshold": GAP_ALPHA_THRESHOLD,
        "gap_tolerance_native_px": GAP_TOLERANCE_NATIVE_PX,
        "gap_contract_enforced": enforce_gap_contract,
        "source_check_to_label_min_distance_px": round(source_gap, 6),
        "rendered_check_to_jeon_min_distance_px": round(rendered_gap, 6),
        "gap_delta_px": round(gap_delta, 6),
        "protected_icon_overlap_pixels": overlap,
        "protected_icon_canonical_rgba_differences": icon_difference,
        "outside_cleanup_and_label_changed_pixels": escaped,
    }


def logical_mask(route: RouteSpec) -> "np.ndarray[Any, Any]":
    width, height = route.dimensions
    mask = np.zeros((height, width), dtype=bool)
    for rect in route.primary_rects["JP"]:
        left, top, right, bottom = rect
        require(not bool(np.any(mask[top:bottom, left:right])), f"logical cells overlap: {route.route_id}")
        mask[top:bottom, left:right] = True
    return mask


def block_pixel_mask(width: int, height: int, blocks: set[tuple[int, int]]) -> "np.ndarray[Any, Any]":
    mask = np.zeros((height, width), dtype=bool)
    for block_x, block_y in blocks:
        mask[block_y * 4:block_y * 4 + 4, block_x * 4:block_x * 4 + 4] = True
    return mask


def encode_changed_blocks(
    original: Image.Image,
    requested: Image.Image,
    original_payload: bytes,
    route: RouteSpec,
    ispc: Any,
    decoder: Any,
) -> tuple[bytes, Image.Image, dict[str, Any]]:
    baseline = np.asarray(original.convert("RGBA"), dtype=np.uint8)
    desired = np.asarray(requested.convert("RGBA"), dtype=np.uint8)
    delta = np.any(canonical_rgba(baseline) != canonical_rgba(desired), axis=-1)
    cells = logical_mask(route)
    require(bool(np.any(delta)), f"route has no requested pixel delta: {route.route_id}")
    require(not bool(np.any(delta & ~cells)), f"requested pixels escaped logical cells: {route.route_id}")
    ys, xs = np.nonzero(delta)
    selected = {(int(x) // 4, int(y) // 4) for y, x in zip(ys.tolist(), xs.tolist())}
    settings = ispc.BC7EncSettings.from_profile("alpha_slow")
    output = bytearray(original_payload)
    blocks_wide = route.dimensions[0] // 4
    for block_x, block_y in sorted(selected, key=lambda value: (value[1], value[0])):
        patch = requested.crop((block_x * 4, block_y * 4, block_x * 4 + 4, block_y * 4 + 4)).convert("RGBA")
        encoded = ispc.compress_blocks_bc7(ispc.RGBASurface(patch.tobytes(), 4, 4), settings)
        require(len(encoded) == 16, "single BC7 block size differs")
        offset = (block_y * blocks_wide + block_x) * 16
        output[offset:offset + 16] = encoded
    changed = {
        (index % blocks_wide, index // blocks_wide)
        for index in range(len(original_payload) // 16)
        if original_payload[index * 16:index * 16 + 16] != output[index * 16:index * 16 + 16]
    }
    require(changed and changed <= selected, f"BC7 changes escaped selected blocks: {route.route_id}")
    decoded = issue117.decode_bc7(bytes(output), *route.dimensions, decoder)
    decoded_values = np.asarray(decoded, dtype=np.uint8)
    decoded_delta = np.any(canonical_rgba(decoded_values) != canonical_rgba(baseline), axis=-1)
    changed_pixels = block_pixel_mask(*route.dimensions, changed)
    outside_blocks = int(np.count_nonzero(decoded_delta & ~changed_pixels))
    outside_cells = int(np.count_nonzero(decoded_delta & ~cells))
    require(outside_blocks == 0, f"decoded pixels escaped changed blocks: {route.route_id} {outside_blocks}")
    require(outside_cells == 0, f"decoded pixels escaped logical cells: {route.route_id} {outside_cells}")
    before = np.abs(canonical_rgba(baseline).astype(np.int16) - canonical_rgba(desired).astype(np.int16)).mean(axis=-1)
    after = np.abs(canonical_rgba(decoded_values).astype(np.int16) - canonical_rgba(desired).astype(np.int16)).mean(axis=-1)
    require(float(after[changed_pixels].mean()) < float(before[changed_pixels].mean()), f"BC7 fidelity did not improve: {route.route_id}")
    return bytes(output), decoded, {
        "requested_pixel_delta": int(np.count_nonzero(delta)),
        "selected_bc7_blocks": len(selected),
        "changed_bc7_blocks": len(changed),
        "changed_block_bbox": highres.changed_block_bbox(sorted(changed)),
        "decoded_pixels_outside_changed_blocks": outside_blocks,
        "decoded_pixels_outside_logical_cells": outside_cells,
        "fidelity_mean_before": round(float(before[changed_pixels].mean()), 6),
        "fidelity_mean_after": round(float(after[changed_pixels].mean()), 6),
        "unselected_bc7_blocks_byte_preserved": True,
        "encoder": "ispc_texcomp 1.0.1 alpha_slow",
    }


def contact_sheet(
    matrices: Sequence["np.ndarray[Any, Any]"],
    route: RouteSpec,
) -> Image.Image:
    require(len(matrices) == 4, "contact row coverage differs")
    width, height = route.cell_size
    sheet = Image.new("RGBA", (width * 6, height * 4), (0, 0, 0, 0))
    for row, matrix in enumerate(matrices):
        for state in range(6):
            sheet.alpha_composite(Image.fromarray(matrix[state]), (state * width, row * height))
    if route.resolution == "low":
        sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.Resampling.NEAREST)
    return sheet


def aspect_sheet(
    source: "np.ndarray[Any, Any]",
    clean: "np.ndarray[Any, Any]",
    cleanup: "np.ndarray[Any, Any]",
    protected: "np.ndarray[Any, Any]",
    icon_core: "np.ndarray[Any, Any]",
    source_label_core: "np.ndarray[Any, Any]",
    route: RouteSpec,
    font: Path,
) -> Image.Image:
    rows = [source[1], clean[1]]
    for aspect_scale_x in ASPECT_CANDIDATES:
        final, _layers, _report = compose_cells(
            source,
            clean,
            cleanup,
            protected,
            icon_core,
            source_label_core,
            route,
            font,
            aspect_scale_x=aspect_scale_x,
            enforce_gap_contract=False,
        )
        rows.append(final[1])
    width, height = route.cell_size
    sheet = Image.new("RGBA", (width * len(rows), height), (0, 0, 0, 0))
    for index, values in enumerate(rows):
        sheet.alpha_composite(Image.fromarray(values), (index * width, 0))
    if route.resolution == "low":
        sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.Resampling.NEAREST)
    return sheet


def rebuild_archive(
    route: RouteSpec,
    context: tuple[bytes, lz4.LinkArchive, highres.NestedLink, lz4.WrapperHeader, bytes, atlas_codec.G1T],
    payload: bytes,
) -> bytes:
    blob, outer, nested, header, raw, g1t = context
    texture = g1t.textures[route.texture_index]
    start = texture.payload_offset
    rebuilt_raw_buffer = bytearray(raw)
    rebuilt_raw_buffer[start:start + len(payload)] = payload
    rebuilt_raw = bytes(rebuilt_raw_buffer)
    require(rebuilt_raw[:start] == raw[:start] and rebuilt_raw[start + len(payload):] == raw[start + len(payload):], f"G1T bytes outside selected BC7 payload changed: {route.route_id}")
    wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, header)
    _roundtrip_header, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == rebuilt_raw, f"wrapper roundtrip failed: {route.route_id}")
    rebuilt_nested = highres.rebuild_nested_link(nested, {0: wrapper})
    reparsed_nested = highres.parse_nested_link(rebuilt_nested, expected_resource_id=route.resource_id)
    for entry in nested.entries:
        if entry.index != 0:
            candidate = reparsed_nested.entries[entry.index]
            require(candidate.data == entry.data and candidate.gap_after == entry.gap_after, f"unrelated nested entry changed: {route.route_id} {entry.index}")
    candidate_blob = lz4.rebuild_link(outer, {route.outer_entry: rebuilt_nested})
    candidate_outer = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(candidate_outer) == candidate_blob, f"candidate LINK identity failed: {route.route_id}")
    changed_outer = [entry.index for entry in outer.entries if entry.data != candidate_outer.entries[entry.index].data]
    require(changed_outer == [route.outer_entry], f"changed outer scope differs: {route.route_id} {changed_outer}")
    for entry in outer.entries:
        if entry.index != route.outer_entry:
            candidate = candidate_outer.entries[entry.index]
            require(candidate.data == entry.data and candidate.gap_after == entry.gap_after, f"unrelated outer entry changed: {route.route_id} {entry.index}")
    require(candidate_blob != blob, f"candidate archive is unchanged: {route.route_id}")
    return candidate_blob


def build_route(
    args: argparse.Namespace,
    output: Path,
    route: RouteSpec,
    font: Path,
    ispc: Any,
    decoder: Any,
) -> tuple[dict[str, Any], list[Path]]:
    target_path = args.target_root / Path(route.relative_path)
    target_spec = validate_file(target_path, route.target_pin, f"{route.route_id} v0.94 target")
    target_atlas, target_resource, target_context = load_atlas(target_path, route, decoder)
    paths = source_paths(args, route)
    source_specs: dict[str, Any] = {}
    atlases: dict[str, Image.Image] = {}
    primary: dict[str, np.ndarray[Any, Any]] = {}
    compact: dict[str, np.ndarray[Any, Any]] = {}
    samples: list[np.ndarray[Any, Any]] = []
    donor_masks: list[np.ndarray[Any, Any]] = []
    donor_rows: list[dict[str, Any]] = []
    for locale in LOCALES:
        path = paths[locale].resolve(strict=True)
        source_specs[locale] = validate_file(path, route.source_pins[locale], f"{route.route_id} {locale} stock")
        atlas, resource, _context = load_atlas(path, route, decoder)
        atlases[locale] = atlas
        primary[locale] = extract_states(atlas, route.primary_rects[locale], route.cell_size)
        compact[locale] = extract_states(atlas, route.compact_rects[locale], route.cell_size)
        for family, states in (("approve_all", primary[locale]), ("compact_label", compact[locale])):
            mask = donor_foreground_mask(states, route)
            samples.append(states)
            donor_masks.append(mask)
            donor_rows.append({
                "locale": locale,
                "family": family,
                "rects": [list(rect) for rect in (route.primary_rects if family == "approve_all" else route.compact_rects)[locale]],
                "foreground_exclusion_pixels": int(np.count_nonzero(mask)),
                "foreground_exclusion_bbox": bbox(mask),
                "resource": resource,
            })
    source = primary["JP"]
    cleanup, protected, icon_core, source_label_core, mask_report = icon_and_cleanup_masks(source, route)
    clean, donor_report = clean_stock_cells(source, samples, donor_masks, cleanup, protected, route)
    final, layers, typography = compose_cells(
        source,
        clean,
        cleanup,
        protected,
        icon_core,
        source_label_core,
        route,
        font,
    )

    requested_atlas = target_atlas.copy()
    for state, rect in enumerate(route.primary_rects["JP"]):
        requested_atlas.paste(Image.fromarray(final[state]), rect[:2])
    texture = target_context[-1].textures[route.texture_index]
    original_payload = issue117.bc7_texture_payload(target_context[-2], texture)
    payload, decoded_atlas, compression = encode_changed_blocks(target_atlas, requested_atlas, original_payload, route, ispc, decoder)
    decoded_states = extract_states(decoded_atlas, route.primary_rects["JP"], route.cell_size)
    candidate_blob = rebuild_archive(route, target_context, payload)
    candidate = output / "candidate" / Path(route.relative_path)
    atomic_write(candidate, candidate_blob)

    route_root = output / "preview" / route.route_id
    route_root.mkdir(parents=True, exist_ok=True)
    contact = route_root / "source_clean_desired_decoded.png"
    contact_sheet((source, clean, final, decoded_states), route).save(contact, optimize=False, compress_level=9)
    aspect = route_root / "aspect_source_clean_084_082_080.png"
    aspect_sheet(
        source,
        clean,
        cleanup,
        protected,
        icon_core,
        source_label_core,
        route,
        font,
    ).save(aspect, optimize=False, compress_level=9)
    cleanup_path = route_root / "cleanup_mask.png"
    protected_path = route_root / "protected_icon_mask.png"
    Image.fromarray(cleanup.astype(np.uint8) * 255).save(cleanup_path, optimize=False, compress_level=9)
    Image.fromarray(protected.astype(np.uint8) * 255).save(protected_path, optimize=False, compress_level=9)
    artifacts = [candidate, contact, aspect, cleanup_path, protected_path]
    return {
        "route": route.route_id,
        "resolution": route.resolution,
        "relative_path": route.relative_path,
        "target": target_spec,
        "sources": source_specs,
        "target_resource": target_resource,
        "primary_rects_canonical_state_order": [list(rect) for rect in route.primary_rects["JP"]],
        "canonical_state_roles": list(STATE_ROLES),
        "cell_size": list(route.cell_size),
        "cells": 6,
        "donors": donor_rows,
        "mask": mask_report,
        "clean_plate": donor_report,
        "typography": typography,
        "compression": compression,
        "candidate": file_spec(candidate),
        "previews": {
            "source_clean_desired_decoded": file_spec(contact),
            "aspect_candidates": file_spec(aspect),
            "cleanup_mask": file_spec(cleanup_path),
            "protected_icon_mask": file_spec(protected_path),
        },
    }, artifacts


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = fresh_output(args.output_root)
    args.target_root = args.target_root.resolve(strict=True)
    args.jp_source_root = args.jp_source_root.resolve(strict=True)
    args.official_root = args.official_root.resolve(strict=True)
    args.tc_high = args.tc_high.resolve(strict=True)
    font = args.font.resolve(strict=True)
    font_spec = validate_file(font, FONT_PIN, "SeoulHangang ExtraBold")
    _cv2, ispc, decoder = issue117.load_external(args.dependency_root)
    route_reports: dict[str, Any] = {}
    artifacts: list[Path] = []
    for route in ROUTES:
        print(f"stage={route.route_id}", flush=True)
        report, files = build_route(args, output, route, font, ispc, decoder)
        route_reports[route.route_id] = report
        artifacts.extend(files)
    artifact_table = {
        str(path.relative_to(output)).replace("\\", "/"): {"size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(artifacts)
    }
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "result": "PASS",
        "generation_policy": GENERATION_POLICY,
        "label": {"jp": "全承認", "ko": LABEL, "contains_space": " " in LABEL},
        "font": font_spec,
        "variant": "ApproveAllCompact",
        "aspect": {"scale_x": ASPECT_SCALE_X, "candidate_scale_x": list(ASPECT_CANDIDATES), "explicit_label_exception": True},
        "tracking": {"grade": TRACKING_GRADE, "em": TRACKING_EM},
        "coverage": {"routes": 2, "logical_labels_per_resolution": 1, "states_per_route": 6, "placements": 12, "candidate_archives": 2},
        "routes": route_reports,
        "validation": {
            "stock_body_state_fx_and_icon_preserved_by_layer_contract": True,
            "official_locale_donors_used": list(LOCALES),
            "same_atlas_compact_label_donor_used": True,
            "generation_used": False,
            "inpainting_used": False,
            "font_aspect_ratio_changed": True,
            "aspect_scale_x": ASPECT_SCALE_X,
            "all_uniform_fit_scales": 1.0,
            "native_low_cell_size": [192, 88],
            "native_high_cell_size": [368, 160],
            "low_coordinates_inferred_from_high_by_halving": False,
            "protected_icon_canonical_rgba_differences": 0,
            "stock_check_to_label_gap_matched": True,
            "decoded_pixels_outside_logical_cells": 0,
            "label": LABEL,
        },
        "artifacts": artifact_table,
        "safety": {"outputs_below_repo_tmp": True, "steam_writes": 0, "patcher_writes": 0, "executable_modified": False},
    }
    path = output / "verification.v1.json"
    atomic_write(path, canonical_json(report))
    print(f"status=PASS\nreport={path}", flush=True)
    return report


def verify(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve(strict=True)
    path = root / "verification.v1.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA and report.get("result") == "PASS", "verification report differs")
    require(report.get("label", {}).get("ko") == LABEL and report["label"]["contains_space"] is False, "label contract differs")
    require(report.get("coverage") == {"routes": 2, "logical_labels_per_resolution": 1, "states_per_route": 6, "placements": 12, "candidate_archives": 2}, "coverage differs")
    require(report.get("validation", {}).get("inpainting_used") is False, "inpainting policy differs")
    require(report["validation"]["font_aspect_ratio_changed"] is True, "aspect policy differs")
    require(report["validation"]["aspect_scale_x"] == ASPECT_SCALE_X, "aspect value differs")
    require(report["validation"]["low_coordinates_inferred_from_high_by_halving"] is False, "low coordinate provenance differs")
    for route in ROUTES:
        route_report = report["routes"][route.route_id]
        candidate = root / "candidate" / Path(route.relative_path)
        expected = route_report["candidate"]
        require(candidate.stat().st_size == int(expected["size"]) and sha256_file(candidate) == str(expected["sha256"]), f"candidate differs: {route.route_id}")
        blob = candidate.read_bytes()
        parsed = lz4.parse_link(blob)
        require(lz4.rebuild_link(parsed) == blob, f"candidate LINK identity failed: {route.route_id}")
        require(route_report["compression"]["unselected_bc7_blocks_byte_preserved"] is True, f"BC7 preservation proof differs: {route.route_id}")
    for relative, expected in report["artifacts"].items():
        artifact = root / Path(relative)
        require(artifact.is_file(), f"artifact missing: {relative}")
        require(artifact.stat().st_size == int(expected["size"]) and sha256_file(artifact) == str(expected["sha256"]), f"artifact differs: {relative}")
    print("status=PASS", flush=True)
    return report


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--target-root", type=Path, default=WORKSPACE / "scratch" / "release-v0940-ordinary-buttons-20260820-01" / "resource-input" / "target")
    build_parser.add_argument("--jp-source-root", type=Path, default=WORKSPACE / "scratch" / "release-v0940-ordinary-buttons-20260820-01" / "resource-input" / "source")
    build_parser.add_argument("--official-root", type=Path, default=Path(r"F:\SteamLibrary\steamapps\common\NOBU16"))
    build_parser.add_argument("--tc-high", type=Path, default=Path(r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\tc-pk-wheel-korean-build002-20260727\RES_TC_PK_PORT\res_lang_pk_port2.bin"))
    build_parser.add_argument("--font", type=Path, default=WORKSPACE / "repository" / "KR_PATCH_WORK" / "tmp" / "third_party_fonts" / "SeoulHangangEB.ttf")
    build_parser.add_argument("--dependency-root", type=Path, default=DEFAULT_DEPENDENCY_ROOT)
    build_parser.add_argument("--output-root", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--root", type=Path, required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "build":
        build(args)
    else:
        verify(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, pilot.PilotError, atlas_codec.AtlasError, lz4.LZ4Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
