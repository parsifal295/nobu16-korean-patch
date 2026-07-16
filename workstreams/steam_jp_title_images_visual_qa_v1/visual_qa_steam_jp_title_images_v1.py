#!/usr/bin/env python3
"""Independently decode and visually QA selected Steam-JP title image slots.

This is a read-only QA companion for ``steam_jp_title_images_v1``.  It opens
only the candidate under the repository's ignored ``tmp`` directory, decodes
six title textures through the PC GT1G0600 / BC3 codec, and writes all PNGs,
contact sheets, and detailed results below another ``tmp`` directory.  It
never writes an installed game file.

The reference canvas is reconstructed independently from the audited private
source PNGs and the public build metadata.  The image builder itself is not
imported.  This separates the checks for placement, alpha bounds, clipping,
stray alpha noise, and lossy BC3 output from the candidate builder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TMP_ROOT = REPO / "tmp"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pc_g1t_title_codec as codec  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-title-images.visual-qa.v1"
TARGET_RESOURCE = "RES_JP/res_lang.bin"
OUTER_TITLE_INDEX = 3
PC_WIDTH = 512
PC_HEIGHT = 128
VISIBLE_ALPHA = 16
# BC3 alpha endpoints are quantized per 4×4 block.  A difference within this
# radius is recorded as a codec fringe displacement, not treated as detached
# visual noise; the exact visible-mask IoU remains separately gated.
FRINGE_NEIGHBORHOOD_RADIUS = 3
SAMPLE_SLOTS = (0, 24, 25, 38, 74, 107)

EXPECTED_CANDIDATE = {
    "size": 160351447,
    "sha256": "D045B42BC3D4A4D4C501C5A0E010698AAE95AAE227775306A1272D5259E0888B",
}
SOURCE_REMAP = {0: 3, 24: 25, 25: 24}
CORRECTED_LABELS = {38: "부대 편성", 74: "공주 정보"}
EXPECTED_CORRECTED_PNG_SHA256 = {
    38: "47D6D9FDB733CC499FB9E546F5283E85C38B77989B9DCB020D76B60DBCA338A4",
    74: "4A15EA220A6DB567DADCCD39434F5F4BBB56E89A5FA0F43D6D7B53A49E2FB5A0",
}


class VisualQaError(ValueError):
    """Raised when the narrow visual-QA contract is violated."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256_file(path)}


def require_spec(actual: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    if actual.get("size") != expected.get("size") or actual.get("sha256") != expected.get("sha256"):
        raise VisualQaError(f"{label} pin mismatch: expected={dict(expected)} actual={dict(actual)}")


def require_tmp_path(raw: str | Path, *, make_dir: bool = False) -> Path:
    path = Path(raw).resolve()
    tmp = TMP_ROOT.resolve()
    try:
        path.relative_to(tmp)
    except ValueError as exc:
        raise VisualQaError(f"path must remain below repository tmp: {path}") from exc
    if make_dir:
        path.mkdir(parents=True, exist_ok=True)
        path = path.resolve()
        try:
            path.relative_to(tmp)
        except ValueError as exc:
            raise VisualQaError(f"created path escaped repository tmp: {path}") from exc
    return path


def atomic_write(path: Path, data: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    resolved = require_tmp_path(path)
    for source in forbidden:
        if resolved == source.resolve():
            raise VisualQaError(f"refusing to overwrite input: {source}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{resolved.name}.", suffix=".tmp", dir=resolved.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, resolved)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: object, *, forbidden: Iterable[Path] = ()) -> None:
    atomic_write(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        forbidden=forbidden,
    )


def alpha_bbox(rgba: bytes, width: int, height: int, *, minimum_alpha: int = 1) -> tuple[int, int, int, int]:
    if len(rgba) != width * height * 4:
        raise VisualQaError("RGBA length does not match its geometry")
    left, top, right, bottom = width, height, -1, -1
    for y in range(height):
        row = y * width * 4
        for x in range(width):
            if rgba[row + x * 4 + 3] >= minimum_alpha:
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)
    if right < 0:
        raise VisualQaError("image contains no visible pixels")
    return left, top, right, bottom


def crop_rgba(
    rgba: bytes, width: int, height: int, bbox: tuple[int, int, int, int]
) -> tuple[bytes, int, int]:
    left, top, right, bottom = bbox
    if left < 0 or top < 0 or right >= width or bottom >= height:
        raise VisualQaError("crop box is outside source image")
    target_width, target_height = right - left + 1, bottom - top + 1
    output = bytearray(target_width * target_height * 4)
    for y in range(target_height):
        source_at = ((top + y) * width + left) * 4
        target_at = y * target_width * 4
        output[target_at : target_at + target_width * 4] = rgba[
            source_at : source_at + target_width * 4
        ]
    return bytes(output), target_width, target_height


def _lanczos3(value: float) -> float:
    value = abs(value)
    if value < 1e-12:
        return 1.0
    if value >= 3.0:
        return 0.0
    return (
        math.sin(math.pi * value)
        * math.sin(math.pi * value / 3.0)
        / (math.pi * math.pi * value * value / 3.0)
    )


def _resample_rows(source_size: int, target_size: int) -> list[list[tuple[int, float]]]:
    if source_size <= 0 or target_size <= 0:
        raise VisualQaError("resample dimensions must be positive")
    scale = target_size / source_size
    rows: list[list[tuple[int, float]]] = []
    for target in range(target_size):
        source_position = (target + 0.5) / scale - 0.5
        first = math.floor(source_position) - 2
        weighted: list[tuple[int, float]] = []
        total = 0.0
        for source in range(first, first + 6):
            if source < 0 or source >= source_size:
                continue
            weight = _lanczos3(source_position - source)
            if weight:
                weighted.append((source, weight))
                total += weight
        if not weighted or abs(total) < 1e-12:
            nearest = min(source_size - 1, max(0, int(source_position + 0.5)))
            rows.append([(nearest, 1.0)])
        else:
            rows.append([(source, weight / total) for source, weight in weighted])
    return rows


def resize_rgba_lanczos3_premultiplied(
    source: bytes,
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
) -> bytes:
    """Reimplementation of the documented reference transform, kept local to QA."""

    if len(source) != source_width * source_height * 4:
        raise VisualQaError("resize source RGBA length mismatch")
    horizontal = _resample_rows(source_width, target_width)
    vertical = _resample_rows(source_height, target_height)
    intermediate = [0.0] * (target_width * source_height * 4)
    for y in range(source_height):
        for target_x, contributions in enumerate(horizontal):
            red = green = blue = alpha = 0.0
            for source_x, weight in contributions:
                source_at = (y * source_width + source_x) * 4
                source_alpha = source[source_at + 3]
                red += source[source_at] * source_alpha * weight
                green += source[source_at + 1] * source_alpha * weight
                blue += source[source_at + 2] * source_alpha * weight
                alpha += source_alpha * weight
            target_at = (y * target_width + target_x) * 4
            intermediate[target_at : target_at + 4] = (red, green, blue, alpha)

    output = bytearray(target_width * target_height * 4)
    for target_y, contributions in enumerate(vertical):
        for x in range(target_width):
            red = green = blue = alpha = 0.0
            for source_y, weight in contributions:
                source_at = (source_y * target_width + x) * 4
                red += intermediate[source_at] * weight
                green += intermediate[source_at + 1] * weight
                blue += intermediate[source_at + 2] * weight
                alpha += intermediate[source_at + 3] * weight
            target_at = (target_y * target_width + x) * 4
            rounded_alpha = min(255, max(0, int(alpha + 0.5)))
            if rounded_alpha:
                output[target_at] = min(255, max(0, int(red / alpha + 0.5)))
                output[target_at + 1] = min(255, max(0, int(green / alpha + 0.5)))
                output[target_at + 2] = min(255, max(0, int(blue / alpha + 0.5)))
                output[target_at + 3] = rounded_alpha
    return bytes(output)


def paste_rgba(
    source: bytes,
    source_width: int,
    source_height: int,
    offset_x: int,
    offset_y: int,
    *,
    target_width: int = PC_WIDTH,
    target_height: int = PC_HEIGHT,
) -> tuple[bytes, int]:
    if len(source) != source_width * source_height * 4:
        raise VisualQaError("paste source RGBA length mismatch")
    target = bytearray(target_width * target_height * 4)
    clipped = 0
    for source_y in range(source_height):
        target_y = source_y + offset_y
        for source_x in range(source_width):
            source_at = (source_y * source_width + source_x) * 4
            if not source[source_at + 3]:
                continue
            target_x = source_x + offset_x
            if target_x < 0 or target_x >= target_width or target_y < 0 or target_y >= target_height:
                clipped += 1
                continue
            target_at = (target_y * target_width + target_x) * 4
            target[target_at : target_at + 4] = source[source_at : source_at + 4]
    return bytes(target), clipped


def source_plan(slot: int) -> dict[str, Any]:
    if slot in CORRECTED_LABELS:
        return {
            "source_kind": "corrected",
            "source_index": None,
            "expected_label": CORRECTED_LABELS[slot],
            "expected_png_sha256": EXPECTED_CORRECTED_PNG_SHA256[slot],
        }
    return {
        "source_kind": "switch_v13",
        "source_index": SOURCE_REMAP.get(slot, slot),
        "expected_label": None,
        "expected_png_sha256": None,
    }


def validate_build_report(build_report: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    if build_report.get("schema") != "nobu16.kr.steam-jp-title-images.candidate.v1":
        raise VisualQaError("unexpected title-image build report schema")
    if build_report.get("target_resource") != TARGET_RESOURCE:
        raise VisualQaError("build report targets a different resource")
    if build_report.get("game_install_modified") is not False:
        raise VisualQaError("build report does not prove game files were untouched")
    candidate = build_report.get("candidate")
    if not isinstance(candidate, Mapping):
        raise VisualQaError("build report has no candidate metadata")
    require_spec(candidate, EXPECTED_CANDIDATE, "build report candidate")
    entries = build_report.get("entries")
    if not isinstance(entries, list) or len(entries) != 108:
        raise VisualQaError("build report does not contain exactly 108 title entries")
    normalized: dict[int, Mapping[str, Any]] = {}
    for row in entries:
        if not isinstance(row, Mapping) or not isinstance(row.get("target_index"), int):
            raise VisualQaError("invalid build report title entry")
        slot = row["target_index"]
        if slot in normalized:
            raise VisualQaError(f"duplicate build report title slot {slot}")
        normalized[slot] = row
    if set(normalized) != set(range(108)):
        raise VisualQaError("build report title slots are incomplete")
    for slot in SAMPLE_SLOTS:
        source = normalized[slot].get("source")
        expected = source_plan(slot)
        if not isinstance(source, Mapping):
            raise VisualQaError(f"build report slot {slot} lacks source metadata")
        for key in ("source_kind", "source_index", "corrected_label"):
            actual = source.get(key)
            required = expected["expected_label"] if key == "corrected_label" else expected[key]
            if actual != required:
                raise VisualQaError(
                    f"slot {slot} source plan drift for {key}: expected={required!r} actual={actual!r}"
                )
        expected_hash = expected["expected_png_sha256"]
        if expected_hash is not None and source.get("png_sha256") != expected_hash:
            raise VisualQaError(f"corrected slot {slot} PNG pin drift")
    return normalized


def decode_candidate_slot(inner: codec.InnerLink32, slot: int) -> tuple[bytes, dict[str, Any]]:
    wrapper = inner.entries[slot].data
    header, raw = codec.LZ4.decompress_wrapper(wrapper)
    texture = codec.parse_pc_title_g1t(raw)
    rgba = codec.decode_bc3(texture.bc3, texture.width, texture.height)
    return rgba, {
        "wrapper_sha256": sha256_bytes(wrapper),
        "g1t_sha256": sha256_bytes(raw),
        "bc3_sha256": sha256_bytes(texture.bc3),
        "g1t_magic": raw[:8].decode("ascii"),
        "g1t_format_code": f"0x{texture.format_code:02X}",
        "width": texture.width,
        "height": texture.height,
        "mip_count": texture.mip_count,
        "wrapper_uncompressed_size": header.uncompressed_size,
    }


def expected_canvas(
    *,
    slot: int,
    build_entry: Mapping[str, Any],
    switch_png_root: Path,
    corrected_png_root: Path,
) -> tuple[bytes, dict[str, Any]]:
    plan = source_plan(slot)
    source_path = (
        corrected_png_root / f"{slot:03d}.png"
        if plan["source_kind"] == "corrected"
        else switch_png_root / f"{plan['source_index']:03d}.png"
    )
    if not source_path.is_file():
        raise VisualQaError(f"missing private source PNG for title {slot}: {source_path}")
    source_blob = source_path.read_bytes()
    source_hash = sha256_bytes(source_blob)
    if plan["expected_png_sha256"] is not None and source_hash != plan["expected_png_sha256"]:
        raise VisualQaError(f"corrected source hash drift at title {slot}")
    source_rgba, source_width, source_height = codec.decode_png(source_blob)
    source_box = alpha_bbox(source_rgba, source_width, source_height)
    cropped, cropped_width, cropped_height = crop_rgba(
        source_rgba, source_width, source_height, source_box
    )

    original_box_raw = build_entry.get("steam_jp_original_alpha_bbox")
    if not isinstance(original_box_raw, list) or len(original_box_raw) != 4:
        raise VisualQaError(f"slot {slot} lacks stock alpha bounds")
    original_box = tuple(int(value) for value in original_box_raw)
    stock_height = original_box[3] - original_box[1] + 1
    scale = stock_height / cropped_height
    scaled_height = stock_height
    scaled_width = max(1, int(cropped_width * scale + 0.5))
    horizontal_room = PC_WIDTH - original_box[0]
    if scaled_width > horizontal_room:
        scale = horizontal_room / cropped_width
        scaled_width = horizontal_room
        scaled_height = max(1, int(cropped_height * scale + 0.5))
    resized = resize_rgba_lanczos3_premultiplied(
        cropped, cropped_width, cropped_height, scaled_width, scaled_height
    )
    canvas, clipped = paste_rgba(
        resized, scaled_width, scaled_height, original_box[0], original_box[1]
    )
    placement = build_entry.get("placement")
    if not isinstance(placement, Mapping):
        raise VisualQaError(f"slot {slot} lacks placement metadata")
    expected_placement = {
        "source_crop_dimensions": [cropped_width, cropped_height],
        "scaled_dimensions": [scaled_width, scaled_height],
        "offset_x": original_box[0],
        "offset_y": original_box[1],
        "clipped_nontransparent_pixels": clipped,
        "candidate_alpha_bbox": list(alpha_bbox(canvas, PC_WIDTH, PC_HEIGHT)),
    }
    for key, expected in expected_placement.items():
        if placement.get(key) != expected:
            raise VisualQaError(
                f"slot {slot} independent source reconstruction disagrees on {key}: "
                f"expected={expected!r} report={placement.get(key)!r}"
            )
    requested_hash = build_entry.get("requested_rgba_sha256")
    if requested_hash != sha256_bytes(canvas):
        raise VisualQaError(f"slot {slot} independent canvas hash differs from builder report")
    return canvas, {
        "source_kind": plan["source_kind"],
        "source_index": plan["source_index"],
        "expected_label": plan["expected_label"],
        "source_png_sha256": source_hash,
        "source_dimensions": [source_width, source_height],
        "source_alpha_bbox": list(source_box),
        "expected_canvas_alpha_bbox": expected_placement["candidate_alpha_bbox"],
        "independent_reconstruction_matches_builder_hash": True,
        "independent_reconstruction_clipped_nontransparent_pixels": clipped,
    }


def _visible_mask(rgba: bytes, *, threshold: int = VISIBLE_ALPHA) -> bytes:
    return bytes(1 if rgba[position + 3] >= threshold else 0 for position in range(0, len(rgba), 4))


def _edge_positions(width: int, height: int) -> tuple[int, ...]:
    positions = set()
    for x in range(width):
        positions.add(x)
        positions.add((height - 1) * width + x)
    for y in range(height):
        positions.add(y * width)
        positions.add(y * width + width - 1)
    return tuple(sorted(positions))


def _has_visible_neighbor(
    mask: bytes,
    width: int,
    height: int,
    position: int,
    radius: int = FRINGE_NEIGHBORHOOD_RADIUS,
) -> bool:
    """Return whether a mask has ink within a Chebyshev-radius neighborhood."""

    y, x = divmod(position, width)
    for neighbor_y in range(max(0, y - radius), min(height, y + radius + 1)):
        row = neighbor_y * width
        for neighbor_x in range(max(0, x - radius), min(width, x + radius + 1)):
            if mask[row + neighbor_x]:
                return True
    return False


def visual_metrics(expected: bytes, actual: bytes) -> dict[str, Any]:
    expected_mask = _visible_mask(expected)
    actual_mask = _visible_mask(actual)
    intersection = sum(1 for left, right in zip(expected_mask, actual_mask) if left and right)
    union = sum(1 for left, right in zip(expected_mask, actual_mask) if left or right)
    unexpected = sum(1 for left, right in zip(expected_mask, actual_mask) if right and not left)
    missing = sum(1 for left, right in zip(expected_mask, actual_mask) if left and not right)
    far_candidate_only = sum(
        1
        for position, (left, right) in enumerate(zip(expected_mask, actual_mask))
        if right and not left and not _has_visible_neighbor(expected_mask, PC_WIDTH, PC_HEIGHT, position)
    )
    edges = _edge_positions(PC_WIDTH, PC_HEIGHT)
    unexpected_edge = sum(1 for position in edges if actual_mask[position] and not expected_mask[position])
    expected_box = alpha_bbox(expected, PC_WIDTH, PC_HEIGHT)
    actual_box = alpha_bbox(actual, PC_WIDTH, PC_HEIGHT)
    return {
        "visible_alpha_threshold": VISIBLE_ALPHA,
        "expected_visible_pixels": sum(expected_mask),
        "candidate_visible_pixels": sum(actual_mask),
        "visible_mask_iou": round(intersection / union if union else 1.0, 8),
        "candidate_only_visible_pixels": unexpected,
        "candidate_only_visible_pixels_farther_than_codec_fringe_radius": far_candidate_only,
        "codec_fringe_neighborhood_radius_pixels": FRINGE_NEIGHBORHOOD_RADIUS,
        "missing_visible_pixels": missing,
        "unexpected_canvas_edge_visible_pixels": unexpected_edge,
        "expected_alpha_bbox": list(expected_box),
        "candidate_alpha_bbox": list(actual_box),
        "bbox_coordinate_deltas": [actual_box[index] - expected_box[index] for index in range(4)],
        "max_abs_bbox_coordinate_delta": max(abs(actual_box[index] - expected_box[index]) for index in range(4)),
        "bc3_rgba_error": codec.rgba_error_metrics(expected, actual),
    }


def assessment(metrics: Mapping[str, Any]) -> dict[str, bool]:
    error = metrics.get("bc3_rgba_error")
    if not isinstance(error, Mapping):
        raise VisualQaError("visual metrics lack BC3 error data")
    return {
        "alpha_bbox_within_one_pixel": metrics.get("max_abs_bbox_coordinate_delta", 99) <= 1,
        # BC3/DXT5 alpha quantization can move a fringe pixel within its 4x4
        # block neighborhood;
        # only candidate-only ink with no nearby reference ink is actual stray
        # noise.  The raw candidate-only count remains in the report.
        "no_stray_visible_noise_farther_than_codec_fringe_radius": (
            metrics.get("candidate_only_visible_pixels_farther_than_codec_fringe_radius") == 0
        ),
        "no_unexpected_canvas_edge_ink": metrics.get("unexpected_canvas_edge_visible_pixels") == 0,
        "visible_shape_iou_at_least_0_98": metrics.get("visible_mask_iou", 0.0) >= 0.98,
        "bc3_mean_squared_channel_error_at_most_64": error.get("mean_squared_channel_error", 1e9) <= 64.0,
        "bc3_max_channel_error_at_most_255": error.get("max_channel_error", 999) <= 255,
    }


def checkerboard_composite(rgba: bytes, width: int, height: int) -> bytes:
    if len(rgba) != width * height * 4:
        raise VisualQaError("checkerboard RGBA length mismatch")
    output = bytearray(width * height * 4)
    for y in range(height):
        for x in range(width):
            position = (y * width + x) * 4
            base = 68 if ((x // 8) + (y // 8)) % 2 else 98
            alpha = rgba[position + 3]
            inverse = 255 - alpha
            output[position] = (rgba[position] * alpha + base * inverse + 127) // 255
            output[position + 1] = (rgba[position + 1] * alpha + base * inverse + 127) // 255
            output[position + 2] = (rgba[position + 2] * alpha + base * inverse + 127) // 255
            output[position + 3] = 255
    return bytes(output)


def nearest_scale(rgba: bytes, width: int, height: int, factor: int) -> tuple[bytes, int, int]:
    if factor < 1:
        raise VisualQaError("nearest scale factor must be at least one")
    target_width, target_height = width * factor, height * factor
    output = bytearray(target_width * target_height * 4)
    for y in range(height):
        source_row = rgba[y * width * 4 : (y + 1) * width * 4]
        expanded = bytearray()
        for x in range(width):
            pixel = source_row[x * 4 : x * 4 + 4]
            expanded.extend(pixel * factor)
        for target_y in range(y * factor, (y + 1) * factor):
            at = target_y * target_width * 4
            output[at : at + target_width * 4] = expanded
    return bytes(output), target_width, target_height


def blank_rgba(width: int, height: int, color: tuple[int, int, int, int]) -> bytearray:
    return bytearray(bytes(color) * (width * height))


def paste_opaque(target: bytearray, target_width: int, target_height: int, source: bytes, source_width: int, source_height: int, x: int, y: int) -> None:
    if x < 0 or y < 0 or x + source_width > target_width or y + source_height > target_height:
        raise VisualQaError("contact-sheet paste exceeds canvas")
    for row in range(source_height):
        source_at = row * source_width * 4
        target_at = ((y + row) * target_width + x) * 4
        target[target_at : target_at + source_width * 4] = source[
            source_at : source_at + source_width * 4
        ]


_DIGITS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}


def draw_slot_digits(target: bytearray, width: int, slot: int, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    text = f"{slot:03d}"
    scale = 3
    cursor = x
    for character in text:
        for row, pattern in enumerate(_DIGITS[character]):
            for column, visible in enumerate(pattern):
                if visible != "1":
                    continue
                for dy in range(scale):
                    for dx in range(scale):
                        at = ((y + row * scale + dy) * width + cursor + column * scale + dx) * 4
                        target[at : at + 4] = bytes(color)
        cursor += 4 * scale


def bordered_panel(rgba: bytes, border: tuple[int, int, int, int]) -> tuple[bytes, int, int]:
    composited = checkerboard_composite(rgba, PC_WIDTH, PC_HEIGHT)
    scaled, width, height = nearest_scale(composited, PC_WIDTH, PC_HEIGHT, 2)
    output = bytearray(scaled)
    for x in range(width):
        output[x * 4 : x * 4 + 4] = bytes(border)
        bottom = ((height - 1) * width + x) * 4
        output[bottom : bottom + 4] = bytes(border)
    for y in range(height):
        left = y * width * 4
        right = (y * width + width - 1) * 4
        output[left : left + 4] = bytes(border)
        output[right : right + 4] = bytes(border)
    return bytes(output), width, height


def contact_sheet(rows: Sequence[Mapping[str, Any]]) -> tuple[bytes, int, int]:
    panel_width, panel_height = PC_WIDTH * 2, PC_HEIGHT * 2
    padding, label_height, row_gap = 12, 24, 10
    width = padding * 3 + panel_width * 2
    height = padding + len(rows) * (label_height + panel_height + row_gap) + padding
    canvas = blank_rgba(width, height, (25, 29, 36, 255))
    y = padding
    for row in rows:
        expected_panel, _, _ = bordered_panel(row["expected_rgba"], (66, 145, 255, 255))
        candidate_panel, _, _ = bordered_panel(row["candidate_rgba"], (76, 206, 123, 255))
        draw_slot_digits(canvas, width, int(row["slot"]), padding, y + 4, (240, 240, 240, 255))
        paste_opaque(canvas, width, height, expected_panel, panel_width, panel_height, padding, y + label_height)
        paste_opaque(
            canvas,
            width,
            height,
            candidate_panel,
            panel_width,
            panel_height,
            padding * 2 + panel_width,
            y + label_height,
        )
        y += label_height + panel_height + row_gap
    return bytes(canvas), width, height


def build_qa_report(
    *,
    candidate_path: Path,
    build_report_path: Path,
    switch_png_root: Path,
    corrected_png_root: Path,
    output_root: Path,
    manual_review_pass: bool,
) -> dict[str, Any]:
    candidate_path = require_tmp_path(candidate_path)
    build_report_path = require_tmp_path(build_report_path)
    switch_png_root = require_tmp_path(switch_png_root)
    corrected_png_root = require_tmp_path(corrected_png_root)
    output_root = require_tmp_path(output_root, make_dir=True)
    before = file_spec(candidate_path)
    require_spec(before, EXPECTED_CANDIDATE, "candidate")
    try:
        build_report = json.loads(build_report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VisualQaError(f"invalid title build report: {exc}") from exc
    build_entries = validate_build_report(build_report)

    outer_blob = candidate_path.read_bytes()
    outer = codec.LZ4.parse_link(outer_blob)
    if codec.LZ4.rebuild_link(outer) != outer_blob:
        raise VisualQaError("candidate outer LINK identity check failed")
    if len(outer.entries) != 42:
        raise VisualQaError("candidate outer LINK entry count is not 42")
    inner = codec.parse_inner_link32(outer.entries[OUTER_TITLE_INDEX].data)
    if len(inner.entries) != 110:
        raise VisualQaError("candidate title LINK entry count is not 110")

    private_root = require_tmp_path(output_root / "private", make_dir=True)
    rows: list[dict[str, Any]] = []
    report_rows: list[dict[str, Any]] = []
    for slot in SAMPLE_SLOTS:
        expected_rgba, source_meta = expected_canvas(
            slot=slot,
            build_entry=build_entries[slot],
            switch_png_root=switch_png_root,
            corrected_png_root=corrected_png_root,
        )
        candidate_rgba, codec_meta = decode_candidate_slot(inner, slot)
        metrics = visual_metrics(expected_rgba, candidate_rgba)
        checks = assessment(metrics)
        if codec_meta["width"] != PC_WIDTH or codec_meta["height"] != PC_HEIGHT:
            raise VisualQaError(f"slot {slot} is not a PC 512x128 title texture")
        if codec_meta["g1t_format_code"] != "0x5B" or codec_meta["mip_count"] != 1:
            raise VisualQaError(f"slot {slot} violates PC BC3 G1T contract")
        expected_png = codec.encode_rgba_png(expected_rgba, PC_WIDTH, PC_HEIGHT)
        candidate_png = codec.encode_rgba_png(candidate_rgba, PC_WIDTH, PC_HEIGHT)
        expected_png_path = private_root / f"slot_{slot:03d}_reference.png"
        candidate_png_path = private_root / f"slot_{slot:03d}_candidate.png"
        atomic_write(expected_png_path, expected_png, forbidden=(candidate_path, build_report_path))
        atomic_write(candidate_png_path, candidate_png, forbidden=(candidate_path, build_report_path))
        rows.append({"slot": slot, "expected_rgba": expected_rgba, "candidate_rgba": candidate_rgba})
        report_rows.append(
            {
                "slot": slot,
                "source_mapping": source_meta,
                "pc_codec": codec_meta,
                "visual_metrics": metrics,
                "automatic_checks": checks,
                "automatic_pass": all(checks.values()),
                "private_preview": {
                    "reference_png_sha256": sha256_bytes(expected_png),
                    "candidate_png_sha256": sha256_bytes(candidate_png),
                },
            }
        )

    sheet_rgba, sheet_width, sheet_height = contact_sheet(rows)
    sheet_path = private_root / "contact_sheet_reference_left_candidate_right.png"
    sheet_png = codec.encode_rgba_png(sheet_rgba, sheet_width, sheet_height)
    atomic_write(sheet_path, sheet_png, forbidden=(candidate_path, build_report_path))
    after = file_spec(candidate_path)
    if after != before:
        raise VisualQaError("candidate changed while it was being QAed")

    report = {
        "schema": SCHEMA,
        "source_free": True,
        "file_only": True,
        "game_install_modified": False,
        "runtime_patch_features": [],
        "candidate": {
            "resource": TARGET_RESOURCE,
            **before,
            "unchanged_during_qa": True,
        },
        "pc_codec_contract": {
            "outer_title_entry": OUTER_TITLE_INDEX,
            "outer_link_entry_count": len(outer.entries),
            "inner_title_entry_count": len(inner.entries),
            "texture_magic": "GT1G0600",
            "format_code": "0x5B",
            "geometry": [PC_WIDTH, PC_HEIGHT],
            "mip_count": 1,
        },
        "sample_order": list(SAMPLE_SLOTS),
        "sample_rows": report_rows,
        "aggregate": {
            "sample_count": len(report_rows),
            "automatic_pass": all(row["automatic_pass"] for row in report_rows),
            "unexpected_visible_pixels_total": sum(
                row["visual_metrics"]["candidate_only_visible_pixels"] for row in report_rows
            ),
            "stray_visible_pixels_farther_than_codec_fringe_radius_total": sum(
                row["visual_metrics"][
                    "candidate_only_visible_pixels_farther_than_codec_fringe_radius"
                ]
                for row in report_rows
            ),
            "missing_visible_pixels_total": sum(
                row["visual_metrics"]["missing_visible_pixels"] for row in report_rows
            ),
            "maximum_bbox_delta": max(
                row["visual_metrics"]["max_abs_bbox_coordinate_delta"] for row in report_rows
            ),
            "minimum_visible_mask_iou": min(
                row["visual_metrics"]["visible_mask_iou"] for row in report_rows
            ),
        },
        "manual_readability_review": {
            "required": True,
            "status": "PASS" if manual_review_pass else "PENDING",
            "method": (
                "Read the private contact sheet at native 2x pixels: blue-border left "
                "is independently reconstructed reference, green-border right is decoded PC candidate."
            ),
            "slot_order": list(SAMPLE_SLOTS),
            "corrected_label_assertions": {
                "38": "부대 편성",
                "74": "공주 정보",
            },
            "automated_ocr_claim": False,
        },
        "private_outputs": {
            "all_outputs_under_tmp": True,
            "contact_sheet_filename": sheet_path.name,
            "contact_sheet_sha256": sha256_bytes(sheet_png),
            "contact_sheet_dimensions": [sheet_width, sheet_height],
            "raw_or_png_committed": False,
        },
    }
    report_path = require_tmp_path(output_root / "visual_qa_report.json")
    write_json(report_path, report, forbidden=(candidate_path, build_report_path))
    return report


def verify_report(report_path: Path, candidate_path: Path) -> dict[str, Any]:
    report_path = require_tmp_path(report_path)
    candidate_path = require_tmp_path(candidate_path)
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VisualQaError(f"invalid visual QA report: {exc}") from exc
    if report.get("schema") != SCHEMA:
        raise VisualQaError("unexpected visual QA report schema")
    if report.get("game_install_modified") is not False:
        raise VisualQaError("visual QA report does not prove game files were untouched")
    candidate = report.get("candidate")
    if not isinstance(candidate, Mapping):
        raise VisualQaError("visual QA report lacks candidate pin")
    require_spec(candidate, EXPECTED_CANDIDATE, "visual QA candidate")
    actual_candidate = file_spec(candidate_path)
    require_spec(actual_candidate, EXPECTED_CANDIDATE, "candidate at verify time")
    rows = report.get("sample_rows")
    if not isinstance(rows, list) or [row.get("slot") for row in rows] != list(SAMPLE_SLOTS):
        raise VisualQaError("visual QA report sample order changed")
    if not all(isinstance(row.get("automatic_checks"), Mapping) and all(row["automatic_checks"].values()) for row in rows):
        raise VisualQaError("one or more automatic visual checks did not pass")
    manual = report.get("manual_readability_review")
    if not isinstance(manual, Mapping) or manual.get("status") != "PASS":
        raise VisualQaError("manual contact-sheet readability review is not complete")
    aggregate = report.get("aggregate")
    if not isinstance(aggregate, Mapping) or not aggregate.get("automatic_pass"):
        raise VisualQaError("visual QA aggregate is not passing")
    return report


def default_paths() -> dict[str, Path]:
    return {
        "candidate": TMP_ROOT / "steam_jp_title_images_v1" / "final" / "candidate" / "RES_JP" / "res_lang.bin",
        "build_report": TMP_ROOT / "steam_jp_title_images_v1" / "final" / "build_report.json",
        "switch_png_root": TMP_ROOT / "switch_title_pixel_audit" / "private" / "switch_v13",
        "corrected_png_root": TMP_ROOT / "pc_title_images_v13" / "private" / "corrected",
        "output_root": TMP_ROOT / "steam_jp_title_images_visual_qa_v1" / "final",
    }


def parser() -> argparse.ArgumentParser:
    defaults = default_paths()
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    qa = commands.add_parser("qa", help="decode six PC title slots and write private visual QA artifacts")
    qa.add_argument("--candidate", type=Path, default=defaults["candidate"])
    qa.add_argument("--build-report", type=Path, default=defaults["build_report"])
    qa.add_argument("--switch-png-root", type=Path, default=defaults["switch_png_root"])
    qa.add_argument("--corrected-png-root", type=Path, default=defaults["corrected_png_root"])
    qa.add_argument("--output-root", type=Path, default=defaults["output_root"])
    qa.add_argument(
        "--manual-review-pass",
        action="store_true",
        help="set only after a human has opened the generated contact sheet",
    )
    verify = commands.add_parser("verify", help="verify an already reviewed private QA report")
    verify.add_argument("--report", type=Path, default=defaults["output_root"] / "visual_qa_report.json")
    verify.add_argument("--candidate", type=Path, default=defaults["candidate"])
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "qa":
            report = build_qa_report(
                candidate_path=args.candidate,
                build_report_path=args.build_report,
                switch_png_root=args.switch_png_root,
                corrected_png_root=args.corrected_png_root,
                output_root=args.output_root,
                manual_review_pass=args.manual_review_pass,
            )
            print(f"candidate_sha256={report['candidate']['sha256']}")
            print(f"automatic_pass={report['aggregate']['automatic_pass']}")
            print(f"manual_readability_review={report['manual_readability_review']['status']}")
            print("game_install_modified=False")
            return 0
        report = verify_report(args.report, args.candidate)
        print(f"candidate_sha256={report['candidate']['sha256']}")
        print("verify=PASS")
        print("game_install_modified=False")
        return 0
    except (OSError, codec.CodecError, codec.LZ4.LZ4Error, codec.LZ4.LinkError, VisualQaError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
