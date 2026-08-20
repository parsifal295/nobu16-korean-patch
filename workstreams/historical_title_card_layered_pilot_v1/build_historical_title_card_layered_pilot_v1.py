#!/usr/bin/env python3
"""Build an AI-free layered prototype for the historical title cards.

Only PNG and JSON files below the repository ``tmp`` directory are written.
The input LINK archives are opened read-only and checked before and after use.
No archive, patcher bundle, Steam installation, process, executable or registry
entry is modified.
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
PIL_RUNTIME = (
    WORKSPACE
    / "repository"
    / "KR_PATCH_WORK"
    / "tmp"
    / "toolchain"
    / "atlas_dashboard_runtime"
)
for import_root in (PIL_RUNTIME, TOOLS):
    if import_root.is_dir() and str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError as exc:  # pragma: no cover - dependency error is user-facing.
    raise RuntimeError("Pillow and NumPy are required for the historical title pilot") from exc

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402


SCHEMA = "nobu16.kr.historical-title-card-layered-pilot.v1"
GENERATION_POLICY = "forbidden-and-not-used"
STATE_NAMES = ("normal_gold", "highlight_white_gold", "burst_zoom")
DEFAULT_PINS = WORKSTREAM / "input_pins.v1.json"
DEFAULT_CATALOG = WORKSTREAM / "catalog.prototype.v1.json"
DEFAULT_TARGET = (
    WORKSPACE
    / "scratch"
    / "release-v0940-approve-all-layered-20260820-01"
    / "generator-output-03"
    / "target"
)
DEFAULT_FONT = (
    WORKSPACE
    / "repository"
    / "KR_PATCH_WORK"
    / "tmp"
    / "third_party_fonts"
    / "yeongyang_eumsikdimibang"
    / "Yydimibang.ttf"
)


class PilotError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PilotError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def validate_file(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is missing: {path}")
    actual = file_spec(path)
    require(
        actual["size"] == int(expected["size"])
        and actual["sha256"] == str(expected["sha256"]).upper(),
        f"{label} pin differs: expected={dict(expected)} actual={actual}",
    )
    return actual


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_output_root(raw: str | Path, *, fresh: bool) -> Path:
    root = Path(raw).resolve()
    tmp = (REPO / "tmp").resolve()
    try:
        root.relative_to(tmp)
    except ValueError as exc:
        raise PilotError(f"output root must remain below {tmp}") from exc
    require(root != tmp, "output root may not be the tmp root itself")
    if fresh:
        require(not root.exists() or not any(root.iterdir()), f"output root is not empty: {root}")
        root.mkdir(parents=True, exist_ok=True)
    else:
        require(root.is_dir(), f"output root is missing: {root}")
    return root


def alpha_bbox(mask: "np.ndarray[Any, Any]", threshold: int = 4) -> list[int]:
    require(mask.ndim == 2, f"alpha mask is not 2D: {mask.shape}")
    ys, xs = np.nonzero(mask > threshold)
    require(bool(len(xs)), "alpha mask is empty")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def clip_to_bbox(mask: "np.ndarray[Any, Any]", box: Sequence[int]) -> "np.ndarray[Any, Any]":
    left, top, right, bottom = (int(value) for value in box)
    clipped = np.zeros_like(mask)
    clipped[top:bottom, left:right] = mask[top:bottom, left:right]
    return clipped


def render_text_mask(
    text: str,
    font_path: Path,
    canvas_size: tuple[int, int],
    target_bbox: Sequence[int],
) -> "np.ndarray[Any, Any]":
    """Render a high-detail glyph mask and fit it to an audited source bbox."""

    left, top, right, bottom = (int(value) for value in target_bbox)
    target_width = right - left
    target_height = bottom - top
    require(target_width > 0 and target_height > 0, f"invalid target bbox: {target_bbox}")
    font_size = max(256, target_height * 4)
    font = ImageFont.truetype(str(font_path), font_size)
    probe = Image.new("L", (1, 1), 0)
    draw = ImageDraw.Draw(probe)
    measured = draw.textbbox((0, 0), text, font=font, stroke_width=0)
    pad = max(16, font_size // 8)
    width = measured[2] - measured[0] + pad * 2
    height = measured[3] - measured[1] + pad * 2
    raw = Image.new("L", (width, height), 0)
    ImageDraw.Draw(raw).text(
        (pad - measured[0], pad - measured[1]),
        text,
        font=font,
        fill=255,
    )
    box = raw.getbbox()
    require(box is not None, f"font rendered an empty label: {text}")
    cropped = raw.crop(box)
    fitted = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
    canvas = Image.new("L", canvas_size, 0)
    canvas.paste(fitted, (left, top))
    return np.asarray(canvas, dtype=np.uint8)


def _fallback_color(rgba: "np.ndarray[Any, Any]", support: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    selected = rgba[..., :3][support > 0.08]
    if len(selected):
        return np.median(selected, axis=0).astype(np.float32)
    return np.array([255.0, 255.0, 255.0], dtype=np.float32)


def normalized_color_field(
    rgba: "np.ndarray[Any, Any]",
    support: "np.ndarray[Any, Any]",
    radius: float,
) -> "np.ndarray[Any, Any]":
    """Interpolate the original color layer through normalized convolution."""

    require(rgba.ndim == 3 and rgba.shape[2] == 4, f"RGBA shape differs: {rgba.shape}")
    require(support.shape == rgba.shape[:2], f"support shape differs: {support.shape}")
    support = np.clip(support.astype(np.float32), 0.0, 1.0)
    denominator_image = Image.fromarray(np.rint(support * 255.0).astype(np.uint8))
    denominator = np.asarray(
        denominator_image.filter(ImageFilter.GaussianBlur(radius=max(0.5, radius))),
        dtype=np.float32,
    )
    fallback = _fallback_color(rgba, support)
    field = np.empty(rgba.shape[:2] + (3,), dtype=np.float32)
    for channel in range(3):
        weighted = np.rint(rgba[..., channel].astype(np.float32) * support).astype(np.uint8)
        numerator = np.asarray(
            Image.fromarray(weighted).filter(
                ImageFilter.GaussianBlur(radius=max(0.5, radius))
            ),
            dtype=np.float32,
        )
        raw_estimate = np.full(rgba.shape[:2], fallback[channel], dtype=np.float32)
        valid = denominator >= 2.0
        raw_estimate[valid] = numerator[valid] * 255.0 / denominator[valid]
        # A new Hangul stroke can occupy a hole between the source glyphs.
        # Fade low-support interpolation back to the source median instead of
        # leaking transparent-black RGB into that stroke.
        confidence = np.clip((denominator - 4.0) / 44.0, 0.0, 1.0)
        estimate = fallback[channel] * (1.0 - confidence) + raw_estimate * confidence
        field[..., channel] = np.clip(estimate, 0.0, 255.0)
    return field


def row_color_field(
    rgba: "np.ndarray[Any, Any]",
    support: "np.ndarray[Any, Any]",
) -> "np.ndarray[Any, Any]":
    """Transfer the source's vertical paint gradient without glyph-shaped holes."""

    require(rgba.shape[:2] == support.shape, "row palette support dimensions differ")
    height, width = support.shape
    fallback = _fallback_color(rgba, support)
    rows = np.full((height, 3), np.nan, dtype=np.float32)
    for y in range(height):
        selected = support[y] > 0.45
        if np.any(selected):
            rows[y] = np.median(rgba[y, selected, :3], axis=0)
    positions = np.arange(height, dtype=np.float32)
    for channel in range(3):
        valid = np.isfinite(rows[:, channel])
        if np.any(valid):
            rows[:, channel] = np.interp(
                positions,
                positions[valid],
                rows[valid, channel],
            )
        else:
            rows[:, channel] = fallback[channel]
        rows[:, channel] = np.convolve(
            np.pad(rows[:, channel], (3, 3), mode="edge"),
            np.array([1, 2, 3, 4, 3, 2, 1], dtype=np.float32) / 16.0,
            mode="valid",
        )
    return np.broadcast_to(rows[:, None, :], (height, width, 3)).copy()


def layer_from_mask(
    mask: "np.ndarray[Any, Any]", color_field: "np.ndarray[Any, Any]"
) -> Image.Image:
    require(mask.shape == color_field.shape[:2], "mask/color field dimensions differ")
    rgba = np.empty(mask.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = np.rint(np.clip(color_field, 0.0, 255.0)).astype(np.uint8)
    rgba[..., 3] = mask.astype(np.uint8)
    rgba[mask == 0, :3] = 0
    return Image.fromarray(rgba)


def highlight_core(source: Image.Image) -> "np.ndarray[Any, Any]":
    rgba = np.asarray(source.convert("RGBA"), dtype=np.uint8)
    rgb = rgba[..., :3].astype(np.int16)
    alpha = rgba[..., 3]
    luminance = rgb.mean(axis=2)
    saturation_proxy = rgb.max(axis=2) - rgb.min(axis=2)
    core = (alpha > 32) & (luminance > 180.0) & (saturation_proxy < 85)
    require(bool(np.any(core)), "highlight source produced no white core")
    return core


def normal_gold_core(source: Image.Image) -> "np.ndarray[Any, Any]":
    rgba = np.asarray(source.convert("RGBA"), dtype=np.uint8)
    rgb = rgba[..., :3].astype(np.int16)
    alpha = rgba[..., 3]
    luminance = rgb.mean(axis=2)
    core = (alpha > 32) & (luminance > 60.0)
    require(bool(np.any(core)), "normal source produced no gold core")
    return core


def normal_shadow_mask(
    core_mask: "np.ndarray[Any, Any]",
    full_bbox: Sequence[int],
    scale: float,
) -> "np.ndarray[Any, Any]":
    core_image = Image.fromarray(core_mask)
    dilate_radius = max(2, round(6 * scale))
    dilated = core_image.filter(ImageFilter.MaxFilter(dilate_radius * 2 + 1))
    soft = np.asarray(
        dilated.filter(ImageFilter.GaussianBlur(max(2.0, 9.0 * scale))),
        dtype=np.float32,
    )
    shadow = np.rint(np.clip(soft * 0.84, 0.0, 255.0)).astype(np.uint8)
    return clip_to_bbox(shadow, full_bbox)


def expanded_halo_mask(
    core_mask: "np.ndarray[Any, Any]",
    full_bbox: Sequence[int],
    scale: float,
) -> "np.ndarray[Any, Any]":
    core_image = Image.fromarray(core_mask)
    dilate_radius = max(2, round(7 * scale))
    blur_radius = max(2.0, 9.0 * scale)
    dilated_image = core_image.filter(ImageFilter.MaxFilter(dilate_radius * 2 + 1))
    dilated = np.asarray(
        dilated_image.filter(ImageFilter.GaussianBlur(max(1.0, 2.2 * scale))),
        dtype=np.float32,
    )
    blurred = np.asarray(core_image.filter(ImageFilter.GaussianBlur(blur_radius)), dtype=np.float32)
    halo = np.maximum(dilated * 0.62, blurred * 1.18)
    return clip_to_bbox(np.rint(np.clip(halo, 0.0, 255.0)).astype(np.uint8), full_bbox)


def zoom_burst_mask(
    core_mask: "np.ndarray[Any, Any]",
    core_bbox: Sequence[int],
    final_bbox: Sequence[int],
    scale: float,
    samples: int = 25,
) -> "np.ndarray[Any, Any]":
    """Create the third-state radial streaks from the separated core layer."""

    require(samples >= 3, "zoom burst needs at least three samples")
    cl, ct, cr, cb = (int(value) for value in core_bbox)
    fl, ft, fr, fb = (int(value) for value in final_bbox)
    core_crop = Image.fromarray(core_mask).crop((cl, ct, cr, cb))
    core_width, core_height = core_crop.size
    final_width, final_height = fr - fl, fb - ft
    require(final_width >= core_width and final_height >= core_height, "burst bbox is smaller than core")
    center_x = (fl + fr) / 2.0
    center_y = (ft + fb) / 2.0
    height, width = core_mask.shape
    accumulated = np.zeros((height, width), dtype=np.float32)
    for index in range(samples):
        amount = index / (samples - 1)
        sample_width = max(1, round(core_width + (final_width - core_width) * amount))
        sample_height = max(1, round(core_height + (final_height - core_height) * amount))
        resized = core_crop.resize((sample_width, sample_height), Image.Resampling.BICUBIC)
        canvas = Image.new("L", (width, height), 0)
        x = round(center_x - sample_width / 2.0)
        y = round(center_y - sample_height / 2.0)
        canvas.paste(resized, (x, y))
        weight = 0.10 - 0.04 * amount
        accumulated += np.asarray(canvas, dtype=np.float32) * weight
    accumulated += core_mask.astype(np.float32) * 0.24
    burst = Image.fromarray(np.rint(np.clip(accumulated, 0.0, 255.0)).astype(np.uint8))
    burst = burst.filter(ImageFilter.GaussianBlur(max(0.5, 0.7 * scale)))
    return clip_to_bbox(np.asarray(burst, dtype=np.uint8), final_bbox)


def save_image(path: Path, image: Image.Image) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=False, compress_level=9)
    return {
        "path": str(path),
        "dimensions": list(image.size),
        "mode": image.mode,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def load_source_group(
    archive_path: Path,
    outer_entry: int,
    group_index: int,
    dimensions: tuple[int, int],
) -> tuple[Image.Image, Image.Image, Image.Image]:
    wanted = {group_index * 3 + state for state in range(3)}
    found: dict[int, Image.Image] = {}
    blob = archive_path.read_bytes()
    for outer, slot, _raw, g1t in atlas_codec.archive_g1ts(blob, {outer_entry}):
        if outer != outer_entry or slot not in wanted:
            continue
        require(len(g1t.textures) == 1, f"slot {slot} is not a single-texture G1T")
        texture = g1t.textures[0]
        require(
            (texture.width, texture.height) == dimensions,
            f"slot {slot} dimensions differ: {(texture.width, texture.height)}",
        )
        require(texture.format_code == 0x5B, f"slot {slot} is not BC3: 0x{texture.format_code:02X}")
        decoded = atlas_codec.decode_texture(texture)
        require(decoded is not None, f"slot {slot} did not decode")
        found[slot] = Image.frombytes("RGBA", dimensions, decoded)
        if len(found) == 3:
            break
    require(set(found) == wanted, f"historical title slots are incomplete: wanted={wanted} found={set(found)}")
    return tuple(found[group_index * 3 + state] for state in range(3))  # type: ignore[return-value]


@dataclass(frozen=True)
class RouteResult:
    route_id: str
    sources: tuple[Image.Image, Image.Image, Image.Image]
    candidates: tuple[Image.Image, Image.Image, Image.Image]
    report: Mapping[str, Any]


def build_route(
    route_id: str,
    sources: tuple[Image.Image, Image.Image, Image.Image],
    text: str,
    font_path: Path,
    output_root: Path,
) -> RouteResult:
    width, height = sources[0].size
    require(all(image.size == (width, height) for image in sources), f"{route_id} source dimensions differ")
    scale = width / 1024.0
    source_arrays = [np.asarray(image.convert("RGBA"), dtype=np.uint8) for image in sources]
    source_bboxes = [alpha_bbox(values[..., 3]) for values in source_arrays]

    source_gold_bool = normal_gold_core(sources[0])
    source_gold_alpha = np.where(source_gold_bool, source_arrays[0][..., 3], 0).astype(np.uint8)
    normal_core_bbox = alpha_bbox(source_gold_alpha, threshold=0)
    normal_mask = render_text_mask(text, font_path, (width, height), normal_core_bbox)
    normal_support = source_gold_bool.astype(np.float32) * (
        source_arrays[0][..., 3].astype(np.float32) / 255.0
    )
    normal_field = row_color_field(source_arrays[0], normal_support)
    normal_gold_layer = layer_from_mask(normal_mask, normal_field)
    shadow_mask = normal_shadow_mask(normal_mask, source_bboxes[0], scale)
    source_shadow_support = (~source_gold_bool).astype(np.float32) * (
        source_arrays[0][..., 3].astype(np.float32) / 255.0
    )
    shadow_color = _fallback_color(source_arrays[0], source_shadow_support)
    shadow_field = np.broadcast_to(
        shadow_color[None, None, :], source_arrays[0].shape[:2] + (3,)
    ).copy()
    shadow_layer = layer_from_mask(shadow_mask, shadow_field)
    normal_layer = Image.alpha_composite(shadow_layer, normal_gold_layer)

    source_core_bool = highlight_core(sources[1])
    source_core_alpha = np.where(source_core_bool, source_arrays[1][..., 3], 0).astype(np.uint8)
    core_bbox = alpha_bbox(source_core_alpha, threshold=0)
    highlight_mask = render_text_mask(text, font_path, (width, height), core_bbox)
    core_support = source_core_bool.astype(np.float32) * (source_arrays[1][..., 3].astype(np.float32) / 255.0)
    core_field = normalized_color_field(source_arrays[1], core_support, radius=9.0 * scale)
    core_layer = layer_from_mask(highlight_mask, core_field)

    halo_mask = expanded_halo_mask(highlight_mask, source_bboxes[1], scale)
    halo_support = (
        (~source_core_bool).astype(np.float32)
        * (source_arrays[1][..., 3].astype(np.float32) / 255.0)
    )
    halo_field = row_color_field(source_arrays[1], halo_support)
    halo_layer = layer_from_mask(halo_mask, halo_field)
    highlight_composite = Image.alpha_composite(halo_layer, core_layer)

    burst_mask = zoom_burst_mask(highlight_mask, core_bbox, source_bboxes[2], scale)
    burst_haze = np.asarray(
        Image.fromarray(burst_mask).filter(ImageFilter.GaussianBlur(max(2.0, 6.0 * scale))),
        dtype=np.float32,
    )
    burst_mask = clip_to_bbox(
        np.rint(np.clip(np.maximum(burst_mask.astype(np.float32), burst_haze * 0.58), 0.0, 255.0)).astype(np.uint8),
        source_bboxes[2],
    )
    burst_support = source_arrays[2][..., 3].astype(np.float32) / 255.0
    burst_field = normalized_color_field(source_arrays[2], burst_support, radius=16.0 * scale)
    burst_layer = layer_from_mask(burst_mask, burst_field)

    candidates = (normal_layer, highlight_composite, burst_layer)
    output_rows: list[dict[str, Any]] = []
    for state, (state_name, source, candidate) in enumerate(zip(STATE_NAMES, sources, candidates)):
        source_path = output_root / "source" / route_id / f"state_{state}_{state_name}.png"
        candidate_path = output_root / "candidate" / route_id / f"state_{state}_{state_name}.png"
        source_record = save_image(source_path, source)
        candidate_record = save_image(candidate_path, candidate)
        candidate_alpha = np.asarray(candidate, dtype=np.uint8)[..., 3]
        candidate_bbox = alpha_bbox(candidate_alpha)
        require(candidate_bbox[0] > 0 and candidate_bbox[1] > 0, f"{route_id} state {state} touches top/left")
        require(candidate_bbox[2] < width and candidate_bbox[3] < height, f"{route_id} state {state} touches bottom/right")
        output_rows.append(
            {
                "state": state,
                "name": state_name,
                "source_bbox": source_bboxes[state],
                "candidate_bbox": candidate_bbox,
                "source": source_record,
                "candidate": candidate_record,
            }
        )

    layer_records = {
        "normal_text_mask": save_image(
            output_root / "layers" / route_id / "normal_text_mask.png",
            Image.fromarray(normal_mask),
        ),
        "normal_shadow": save_image(
            output_root / "layers" / route_id / "normal_shadow.png", shadow_layer
        ),
        "highlight_text_mask": save_image(
            output_root / "layers" / route_id / "highlight_text_mask.png",
            Image.fromarray(highlight_mask),
        ),
        "highlight_halo": save_image(
            output_root / "layers" / route_id / "highlight_halo.png", halo_layer
        ),
        "burst_mask": save_image(
            output_root / "layers" / route_id / "burst_mask.png",
            Image.fromarray(burst_mask),
        ),
    }
    return RouteResult(
        route_id=route_id,
        sources=sources,
        candidates=candidates,
        report={
            "route_id": route_id,
            "dimensions": [width, height],
            "scale_from_low": scale,
            "normal_core_bbox": normal_core_bbox,
            "core_bbox": core_bbox,
            "states": output_rows,
            "layers": layer_records,
        },
    )


def checker_composite(image: Image.Image) -> Image.Image:
    width, height = image.size
    tile = max(8, height // 16)
    background = Image.new("RGBA", (width, height), (38, 40, 42, 255))
    draw = ImageDraw.Draw(background)
    for y in range(0, height, tile):
        for x in range(0, width, tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill=(57, 60, 62, 255))
    return Image.alpha_composite(background, image.convert("RGBA")).convert("RGB")


def contact_sheet(low: RouteResult, high: RouteResult, output_path: Path) -> dict[str, Any]:
    panel_size = (1024, 256)
    header = 28
    rows: list[tuple[str, tuple[Image.Image, Image.Image, Image.Image]]] = [
        ("LOW JP source", low.sources),
        ("LOW KO prototype", low.candidates),
        ("HIGH JP source at 50%", high.sources),
        ("HIGH KO prototype at 50%", high.candidates),
    ]
    canvas = Image.new("RGB", (panel_size[0] * 3, (panel_size[1] + header) * len(rows)), (18, 19, 20))
    draw = ImageDraw.Draw(canvas)
    for row_index, (label, images) in enumerate(rows):
        top = row_index * (panel_size[1] + header)
        draw.text((8, top + 7), label, fill=(235, 232, 214))
        for state, image in enumerate(images):
            display = image
            if image.size != panel_size:
                display = image.resize(panel_size, Image.Resampling.LANCZOS)
            panel = checker_composite(display)
            x = state * panel_size[0]
            canvas.paste(panel, (x, top + header))
            draw.text((x + 860, top + 7), STATE_NAMES[state], fill=(178, 181, 176))
    return save_image(output_path, canvas)


def output_manifest(root: Path, report: Mapping[str, Any]) -> list[dict[str, Any]]:
    paths: set[Path] = set()
    for route in report["routes"]:
        for row in route["states"]:
            paths.add(Path(row["source"]["path"]))
            paths.add(Path(row["candidate"]["path"]))
        for layer in route["layers"].values():
            paths.add(Path(layer["path"]))
    paths.add(Path(report["contact_sheet"]["path"]))
    rows = []
    for path in sorted(paths):
        resolved = path.resolve()
        relative = resolved.relative_to(root).as_posix()
        record: dict[str, Any] = {
            "relative_path": relative,
            "size": resolved.stat().st_size,
            "sha256": sha256_file(resolved),
        }
        if resolved.suffix.lower() == ".png":
            with Image.open(resolved) as image:
                record["dimensions"] = list(image.size)
                record["mode"] = image.mode
        rows.append(record)
    return rows


def build(args: argparse.Namespace) -> dict[str, Any]:
    root = ensure_output_root(args.output_root, fresh=True)
    pins = json.loads(Path(args.pins).read_text(encoding="utf-8"))
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    require(pins.get("schema") == "nobu16.kr.historical-title-card-layered-pilot.inputs.v1", "pin schema differs")
    require(catalog.get("schema") == "nobu16.kr.historical-title-card-layered-pilot.catalog.v1", "catalog schema differs")
    entries = [entry for entry in catalog["entries"] if int(entry["group_index"]) == args.group_index]
    require(len(entries) == 1, f"catalog group is missing or duplicated: {args.group_index}")
    entry = entries[0]
    require(entry["slots"] == [args.group_index * 3 + state for state in range(3)], "catalog state slots differ")

    low_path = Path(args.jp_low).resolve()
    high_path = Path(args.jp_high).resolve()
    font_path = Path(args.font).resolve()
    input_specs = {
        "jp_low": validate_file(low_path, pins["files"]["jp_low"], "JP LOW archive"),
        "jp_high": validate_file(high_path, pins["files"]["jp_high"], "JP HIGH archive"),
        "font": validate_file(font_path, pins["font"], "font"),
    }
    before_hashes = {key: value["sha256"] for key, value in input_specs.items()}

    low_sources = load_source_group(
        low_path,
        int(pins["files"]["jp_low"]["outer_entry"]),
        args.group_index,
        tuple(int(value) for value in pins["files"]["jp_low"]["dimensions"]),
    )
    high_sources = load_source_group(
        high_path,
        int(pins["files"]["jp_high"]["outer_entry"]),
        args.group_index,
        tuple(int(value) for value in pins["files"]["jp_high"]["dimensions"]),
    )
    low = build_route("base_low", low_sources, str(entry["ko"]), font_path, root)
    high = build_route("port3_high", high_sources, str(entry["ko"]), font_path, root)
    sheet = contact_sheet(low, high, root / "contact_sheet.png")

    after_hashes = {
        "jp_low": sha256_file(low_path),
        "jp_high": sha256_file(high_path),
        "font": sha256_file(font_path),
    }
    require(before_hashes == after_hashes, "a read-only input changed during the build")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PASS",
        "scope": "PNG-only one-label prototype",
        "generation_policy": GENERATION_POLICY,
        "image_generation_used": False,
        "archive_output_written": False,
        "steam_written": False,
        "entry": entry,
        "input_pins": file_spec(Path(args.pins).resolve()),
        "catalog": file_spec(Path(args.catalog).resolve()),
        "inputs": input_specs,
        "input_hashes_unchanged": True,
        "pipeline": [
            "decode pinned JP BC3 states",
            "measure source alpha and state geometry",
            "separate normal color field, highlight core, halo and burst",
            "render pinned Yydimibang Korean alpha mask",
            "transfer original color fields onto the Korean mask",
            "derive deterministic zoom burst from the separated core",
            "validate clipping, dimensions, hashes and determinism",
        ],
        "routes": [dict(low.report), dict(high.report)],
        "contact_sheet": sheet,
    }
    report["outputs"] = output_manifest(root, report)
    report["output_manifest_sha256"] = sha256_bytes(canonical_json(report["outputs"]))
    write_json(root / "build_report.json", report)
    return report


def verify(args: argparse.Namespace) -> dict[str, Any]:
    root = ensure_output_root(args.output_root, fresh=False)
    report_path = root / "build_report.json"
    require(report_path.is_file(), f"build report is missing: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA, "build report schema differs")
    require(report.get("status") == "PASS", "build report did not pass")
    require(report.get("generation_policy") == GENERATION_POLICY, "generation policy differs")
    require(report.get("image_generation_used") is False, "image generation flag differs")
    require(report.get("archive_output_written") is False, "archive output flag differs")
    require(report.get("steam_written") is False, "Steam output flag differs")
    for row in report["outputs"]:
        path = (root / row["relative_path"]).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise PilotError(f"manifest path escapes output root: {path}") from exc
        require(path.is_file(), f"manifest output is missing: {path}")
        require(path.stat().st_size == int(row["size"]), f"output size differs: {path}")
        require(sha256_file(path) == row["sha256"], f"output hash differs: {path}")
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                require(list(image.size) == row["dimensions"], f"output dimensions differ: {path}")
                require(image.mode == row["mode"], f"output mode differs: {path}")
    require(
        sha256_bytes(canonical_json(report["outputs"])) == report["output_manifest_sha256"],
        "output manifest hash differs",
    )
    return report


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build", help="build a PNG-only layered prototype")
    build_parser.add_argument("--jp-low", default=str(DEFAULT_TARGET / "RES_JP" / "res_lang.bin"))
    build_parser.add_argument(
        "--jp-high",
        default=str(DEFAULT_TARGET / "RES_JP_PK_PORT" / "res_lang_pk_port3.bin"),
    )
    build_parser.add_argument("--font", default=str(DEFAULT_FONT))
    build_parser.add_argument("--pins", default=str(DEFAULT_PINS))
    build_parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    build_parser.add_argument("--group-index", type=int, default=0)
    build_parser.add_argument("--output-root", required=True)
    verify_parser = subparsers.add_parser("verify", help="verify an existing prototype")
    verify_parser.add_argument("--output-root", required=True)
    return value


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    result = build(args) if args.command == "build" else verify(args)
    print("status=PASS")
    print(f"scope={result['scope']}")
    print(f"entry={result['entry']['jp']}->{result['entry']['ko']}")
    print(f"output_manifest_sha256={result['output_manifest_sha256']}")
    print(f"steam_written={str(result['steam_written']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
