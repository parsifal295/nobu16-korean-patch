#!/usr/bin/env python3
"""Build a pinned Steam-JP title-image candidate under ``tmp`` only.

The supported input is the Steam 1.1.7 Japanese-route ``RES_JP/res_lang.bin``
after the currently released Korean glyph/font layer has been applied.  This
builder replaces only outer LINK entry ``/3`` and its title slots ``/3/0..107``
with locally decoded Switch v1.3 Korean title pixels, rebuilt through the PC
BC3/G1T/LZ4/LINK codecs.  It never copies a foreign LINK/G1T payload and it
never writes to a game installation.

The two semantic corrections are local PNG inputs for indices 038 and 074.
All other title pixels come from the audited local Switch-v1.3 PNG set.  The
input and output archive hashes are deliberately pinned so a changed font
baseline or a changed rebuild cannot be mistaken for this candidate.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pc_g1t_title_codec as codec  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-title-images.candidate.v1"
TARGET_RESOURCE = "RES_JP/res_lang.bin"
OUTER_TITLE_INDEX = 3
TARGET_COUNT = 108
TAIL_INDICES = (108, 109)
PC_WIDTH = 512
PC_HEIGHT = 128

# Meaning-audited mapping from the Switch title atlas to the Steam-PC title
# slots.  The two corrected labels below intentionally override same-index
# Switch source pixels, not the archive structure.
SOURCE_REMAP = {0: 3, 24: 25, 25: 24}
CORRECTED_LABELS = {38: "부대 편성", 74: "공주 정보"}

# The released Steam-JP v0.8.0 and v0.9.0 font baseline: both releases retain
# this exact RES_JP hash while v0.9 changes only the two base dialogue files.
# A pristine 1.1.7 archive must not be silently accepted because this
# workstream is intentionally an additive title-image candidate.
EXPECTED_JP_STOCK = {
    "size": 154216023,
    "sha256": "0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0",
}

# Independently generated from the pinned input and validated through a second
# parse of the written candidate.  The normal builder rejects any drift.
EXPECTED_JP_CANDIDATE = {
    "size": 160351447,
    "sha256": "D045B42BC3D4A4D4C501C5A0E010698AAE95AAE227775306A1272D5259E0888B",
}

EXPECTED_SWITCH_AUDIT_SHA256 = (
    "224DFA3F3F538FA7559977A9927BC30E9B9A0CE7BF697E9FE9DE942F014103D7"
)
EXPECTED_CORRECTED_PNG_SHA256 = {
    38: "47D6D9FDB733CC499FB9E546F5283E85C38B77989B9DCB020D76B60DBCA338A4",
    74: "4A15EA220A6DB567DADCCD39434F5F4BBB56E89A5FA0F43D6D7B53A49E2FB5A0",
}


class TitleCandidateError(ValueError):
    """Raised when the narrow JP title-image candidate contract is violated."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json_hash(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(payload)


def file_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256_file(path)}


def bytes_spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def require_exact_spec(actual: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    if not isinstance(expected.get("size"), int) or expected["size"] < 0:
        raise TitleCandidateError(f"{label} pin has no valid size")
    expected_hash = expected.get("sha256")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        raise TitleCandidateError(f"{label} pin has no valid SHA-256")
    if actual.get("size") != expected["size"] or actual.get("sha256") != expected_hash:
        raise TitleCandidateError(
            f"{label} pin mismatch: expected={dict(expected)} actual={dict(actual)}"
        )


def ensure_tmp_output_path(raw: str | Path) -> Path:
    """Resolve an output path and reject any escape from ``tmp``.

    Resolving the final child path, not merely the caller-supplied root, closes
    the normal Windows junction/symlink escape route before a writer is handed
    the path. Every output file uses this guard immediately before writing or
    reading it back.
    """

    root = Path(raw).resolve()
    tmp = TMP_ROOT.resolve()
    try:
        root.relative_to(tmp)
    except ValueError as exc:
        raise TitleCandidateError(f"output path must remain below {tmp}") from exc
    return root


def ensure_tmp_output_root(raw: str | Path) -> Path:
    root = ensure_tmp_output_path(raw)
    tmp = TMP_ROOT.resolve()
    if root == tmp:
        raise TitleCandidateError("output root may not be the tmp root itself")
    root.mkdir(parents=True, exist_ok=True)
    return ensure_tmp_output_path(root)


def alpha_bbox(rgba: bytes, width: int, height: int) -> tuple[int, int, int, int]:
    if len(rgba) != width * height * 4:
        raise TitleCandidateError("RGBA byte length does not match dimensions")
    left, top, right, bottom = width, height, -1, -1
    for y in range(height):
        row = y * width * 4
        for x in range(width):
            if rgba[row + x * 4 + 3]:
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)
    if right < 0:
        raise TitleCandidateError("title image has no non-transparent pixels")
    return left, top, right, bottom


def crop_rgba(
    rgba: bytes, width: int, height: int, bbox: tuple[int, int, int, int]
) -> tuple[bytes, int, int]:
    left, top, right, bottom = bbox
    if left < 0 or top < 0 or right >= width or bottom >= height:
        raise TitleCandidateError("crop bbox is outside source RGBA")
    crop_width = right - left + 1
    crop_height = bottom - top + 1
    output = bytearray(crop_width * crop_height * 4)
    for y in range(crop_height):
        source_start = ((top + y) * width + left) * 4
        target_start = y * crop_width * 4
        output[target_start : target_start + crop_width * 4] = rgba[
            source_start : source_start + crop_width * 4
        ]
    return bytes(output), crop_width, crop_height


def paste_clipped(
    source: bytes,
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
    offset_x: int,
    offset_y: int,
) -> tuple[bytes, int]:
    if len(source) != source_width * source_height * 4:
        raise TitleCandidateError("paste source RGBA length mismatch")
    target = bytearray(target_width * target_height * 4)
    clipped_nontransparent = 0
    for source_y in range(source_height):
        target_y = source_y + offset_y
        for source_x in range(source_width):
            source_pos = (source_y * source_width + source_x) * 4
            if not source[source_pos + 3]:
                continue
            target_x = source_x + offset_x
            if target_x < 0 or target_x >= target_width or target_y < 0 or target_y >= target_height:
                clipped_nontransparent += 1
                continue
            target_pos = (target_y * target_width + target_x) * 4
            target[target_pos : target_pos + 4] = source[source_pos : source_pos + 4]
    return bytes(target), clipped_nontransparent


def _lanczos(value: float, radius: int = 3) -> float:
    value = abs(value)
    if value < 1e-12:
        return 1.0
    if value >= radius:
        return 0.0
    return (
        math.sin(math.pi * value)
        * math.sin(math.pi * value / radius)
        / (math.pi * math.pi * value * value / radius)
    )


def _resample_contributions(source_size: int, target_size: int) -> list[list[tuple[int, float]]]:
    if source_size <= 0 or target_size <= 0:
        raise TitleCandidateError("resample dimensions must be positive")
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
            weight = _lanczos(source_position - source)
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
    """Deterministically resize in premultiplied-alpha space."""

    if len(source) != source_width * source_height * 4:
        raise TitleCandidateError("resize source RGBA length mismatch")
    horizontal = _resample_contributions(source_width, target_width)
    vertical = _resample_contributions(source_height, target_height)
    intermediate = [0.0] * (target_width * source_height * 4)
    for y in range(source_height):
        for target_x, contributions in enumerate(horizontal):
            red = green = blue = alpha = 0.0
            for source_x, weight in contributions:
                pos = (y * source_width + source_x) * 4
                source_alpha = source[pos + 3]
                red += source[pos] * source_alpha * weight
                green += source[pos + 1] * source_alpha * weight
                blue += source[pos + 2] * source_alpha * weight
                alpha += source_alpha * weight
            pos = (y * target_width + target_x) * 4
            intermediate[pos : pos + 4] = [red, green, blue, alpha]

    output = bytearray(target_width * target_height * 4)
    for target_y, contributions in enumerate(vertical):
        for x in range(target_width):
            red = green = blue = alpha = 0.0
            for source_y, weight in contributions:
                pos = (source_y * target_width + x) * 4
                red += intermediate[pos] * weight
                green += intermediate[pos + 1] * weight
                blue += intermediate[pos + 2] * weight
                alpha += intermediate[pos + 3] * weight
            rounded_alpha = min(255, max(0, int(alpha + 0.5)))
            pos = (target_y * target_width + x) * 4
            if rounded_alpha:
                output[pos] = min(255, max(0, int(red / alpha + 0.5)))
                output[pos + 1] = min(255, max(0, int(green / alpha + 0.5)))
                output[pos + 2] = min(255, max(0, int(blue / alpha + 0.5)))
                output[pos + 3] = rounded_alpha
    return bytes(output)


def wrapper_for_rgba(entry_data: bytes, rgba: bytes) -> tuple[bytes, dict[str, Any]]:
    header, raw = codec.LZ4.decompress_wrapper(entry_data)
    texture = codec.parse_pc_title_g1t(raw)
    bc3, preserved, encoded = codec.encode_bc3(
        rgba, texture.width, texture.height, template_bc3=texture.bc3
    )
    rebuilt_g1t = codec.replace_g1t_bc3(texture, bc3)
    if rebuilt_g1t == raw:
        rebuilt_wrapper = entry_data
    else:
        rebuilt_wrapper = codec.LZ4.recompress_wrapper(rebuilt_g1t, header)
        _, roundtrip = codec.LZ4.decompress_wrapper(rebuilt_wrapper)
        if roundtrip != rebuilt_g1t:
            raise TitleCandidateError("rebuilt title wrapper fails raw-LZ4 round trip")
    return rebuilt_wrapper, {
        "total_blocks": len(texture.bc3) // 16,
        "preserved_template_blocks": preserved,
        "deterministically_encoded_blocks": encoded,
        "bc3_sha256": sha256_bytes(bc3),
        "g1t_sha256": sha256_bytes(rebuilt_g1t),
        "wrapper_sha256": sha256_bytes(rebuilt_wrapper),
    }


def load_switch_v13_audit(path: Path) -> list[dict[str, Any]]:
    if sha256_file(path) != EXPECTED_SWITCH_AUDIT_SHA256:
        raise TitleCandidateError("Switch v1.3 audit SHA-256 pin mismatch")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TitleCandidateError(f"invalid Switch v1.3 audit JSON: {exc}") from exc
    rows = value.get("switch_v13") if isinstance(value, dict) else None
    if not isinstance(rows, list) or len(rows) != TARGET_COUNT:
        raise TitleCandidateError("Switch v1.3 audit does not contain exactly 108 titles")
    normalized: list[dict[str, Any]] = []
    for expected_index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise TitleCandidateError(f"invalid Switch v1.3 row {expected_index}")
        if row.get("source") != "switch_v13" or row.get("index") != expected_index:
            raise TitleCandidateError("Switch v1.3 source/index ordering changed")
        if (row.get("width"), row.get("height")) not in {(512, 64), (512, 128)}:
            raise TitleCandidateError(f"unsupported Switch title geometry at {expected_index}")
        rgba_hash = row.get("rgba_sha256")
        if not isinstance(rgba_hash, str) or len(rgba_hash) != 64:
            raise TitleCandidateError(f"Switch title has no RGBA hash at {expected_index}")
        normalized.append(row)
    return normalized


def select_source(index: int) -> tuple[str, int | None]:
    if index < 0 or index >= TARGET_COUNT:
        raise TitleCandidateError(f"invalid target index {index}")
    if index in CORRECTED_LABELS:
        return "corrected", None
    return "switch_v13", SOURCE_REMAP.get(index, index)


def read_validated_source(
    *,
    index: int,
    switch_png_root: Path,
    corrected_png_root: Path,
    switch_audit: Sequence[Mapping[str, Any]],
) -> tuple[bytes, int, int, dict[str, Any]]:
    kind, source_index = select_source(index)
    if kind == "corrected":
        image_path = corrected_png_root / f"{index:03d}.png"
        expected_png_hash = EXPECTED_CORRECTED_PNG_SHA256[index]
    else:
        assert source_index is not None
        image_path = switch_png_root / f"{source_index:03d}.png"
        expected_png_hash = None
    if not image_path.is_file():
        raise TitleCandidateError(f"missing title PNG: {image_path}")
    blob = image_path.read_bytes()
    png_hash = sha256_bytes(blob)
    if expected_png_hash is not None and png_hash != expected_png_hash:
        raise TitleCandidateError(f"corrected PNG SHA-256 mismatch at title {index}")
    rgba, width, height = codec.decode_png(blob)
    if (width, height) not in {(512, 64), (512, 128)}:
        raise TitleCandidateError(f"unsupported source title geometry at {index}: {width}x{height}")
    source_bbox = alpha_bbox(rgba, width, height)
    if kind == "switch_v13":
        assert source_index is not None
        audited = switch_audit[source_index]
        if (width, height) != (audited["width"], audited["height"]):
            raise TitleCandidateError(f"Switch v1.3 dimensions mismatch at source {source_index}")
        if sha256_bytes(rgba) != audited["rgba_sha256"]:
            raise TitleCandidateError(f"Switch v1.3 decoded RGBA mismatch at source {source_index}")
    return rgba, width, height, {
        "source_kind": kind,
        "source_index": source_index,
        "corrected_label": CORRECTED_LABELS.get(index),
        "png_sha256": png_hash,
        "rgba_sha256": sha256_bytes(rgba),
        "width": width,
        "height": height,
        "alpha_bbox": list(source_bbox),
    }


def build_candidate(
    *,
    archive_path: Path,
    switch_png_root: Path,
    corrected_png_root: Path,
    switch_audit_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Build and write the exact candidate resource below ``tmp``.

    The archive input is always opened read-only.  All validation occurs before
    the atomic candidate write, and the archive/source PNG hashes are checked
    again before the report is committed.
    """

    archive_path = archive_path.resolve()
    switch_png_root = switch_png_root.resolve()
    corrected_png_root = corrected_png_root.resolve()
    switch_audit_path = switch_audit_path.resolve()
    output_root = ensure_tmp_output_root(output_root)

    archive_before = file_spec(archive_path)
    require_exact_spec(archive_before, EXPECTED_JP_STOCK, "Steam JP font baseline")
    audit_before = sha256_file(switch_audit_path)
    switch_audit = load_switch_v13_audit(switch_audit_path)

    outer_blob = archive_path.read_bytes()
    outer = codec.LZ4.parse_link(outer_blob)
    if codec.LZ4.rebuild_link(outer) != outer_blob:
        raise TitleCandidateError("JP outer LINK identity gate failed")
    del outer_blob
    if len(outer.entries) <= OUTER_TITLE_INDEX:
        raise TitleCandidateError("JP resource has no outer title entry /3")
    outer_non_title_hashes = {
        str(index): sha256_bytes(entry.data)
        for index, entry in enumerate(outer.entries)
        if index != OUTER_TITLE_INDEX
    }
    original_inner = codec.parse_inner_link32(outer.entries[OUTER_TITLE_INDEX].data)
    if len(original_inner.entries) != TARGET_COUNT + len(TAIL_INDICES):
        raise TitleCandidateError("JP title LINK does not contain slots 0..109")
    original_tail_hashes = {
        str(index): sha256_bytes(original_inner.entries[index].data) for index in TAIL_INDICES
    }
    original_title_hashes = {
        str(index): sha256_bytes(original_inner.entries[index].data)
        for index in range(TARGET_COUNT)
    }

    replacements: dict[int, bytes] = {}
    rows: list[dict[str, Any]] = []
    source_file_hashes: dict[str, str] = {}
    for index in range(TARGET_COUNT):
        entry = original_inner.entries[index]
        _, target_raw = codec.LZ4.decompress_wrapper(entry.data)
        target_texture = codec.parse_pc_title_g1t(target_raw)
        target_rgba = codec.decode_bc3(
            target_texture.bc3, target_texture.width, target_texture.height
        )
        target_bbox = alpha_bbox(target_rgba, PC_WIDTH, PC_HEIGHT)

        source_rgba, source_width, source_height, source_meta = read_validated_source(
            index=index,
            switch_png_root=switch_png_root,
            corrected_png_root=corrected_png_root,
            switch_audit=switch_audit,
        )
        source_path = (
            corrected_png_root / f"{index:03d}.png"
            if source_meta["source_kind"] == "corrected"
            else switch_png_root / f"{source_meta['source_index']:03d}.png"
        )
        source_file_hashes[str(source_path)] = source_meta["png_sha256"]
        source_bbox = tuple(source_meta["alpha_bbox"])
        cropped, cropped_width, cropped_height = crop_rgba(
            source_rgba, source_width, source_height, source_bbox
        )

        target_height = target_bbox[3] - target_bbox[1] + 1
        scale = target_height / cropped_height
        scaled_height = target_height
        scaled_width = max(1, int(cropped_width * scale + 0.5))
        horizontal_room = PC_WIDTH - target_bbox[0]
        if scaled_width > horizontal_room:
            scale = horizontal_room / cropped_width
            scaled_width = horizontal_room
            scaled_height = max(1, int(cropped_height * scale + 0.5))
        resized = resize_rgba_lanczos3_premultiplied(
            cropped, cropped_width, cropped_height, scaled_width, scaled_height
        )
        canvas, clipped = paste_clipped(
            resized,
            scaled_width,
            scaled_height,
            PC_WIDTH,
            PC_HEIGHT,
            target_bbox[0],
            target_bbox[1],
        )
        if clipped:
            raise TitleCandidateError(
                f"title {index} placement clips {clipped} non-transparent pixels"
            )
        canvas_bbox = alpha_bbox(canvas, PC_WIDTH, PC_HEIGHT)
        if abs(canvas_bbox[0] - target_bbox[0]) > 1 or abs(canvas_bbox[1] - target_bbox[1]) > 1:
            raise TitleCandidateError(f"title {index} loses its target ink origin")
        wrapper, encode_meta = wrapper_for_rgba(entry.data, canvas)
        replacements[index] = wrapper
        rows.append(
            {
                "target_index": index,
                "stock_wrapper_sha256": original_title_hashes[str(index)],
                "source": source_meta,
                "steam_jp_original_alpha_bbox": list(target_bbox),
                "placement": {
                    "mode": "jp_bbox_height_scale_top_left",
                    "resampler": "fixed_separable_premultiplied_alpha_lanczos3",
                    "source_crop_dimensions": [cropped_width, cropped_height],
                    "scale": scale,
                    "scaled_dimensions": [scaled_width, scaled_height],
                    "offset_x": target_bbox[0],
                    "offset_y": target_bbox[1],
                    "clipped_nontransparent_pixels": clipped,
                    "candidate_alpha_bbox": list(canvas_bbox),
                },
                "requested_rgba_sha256": sha256_bytes(canvas),
                "encode": encode_meta,
            }
        )

    rebuilt_inner = codec.rebuild_inner_link32(original_inner, replacements)
    reparsed_inner = codec.parse_inner_link32(rebuilt_inner)
    if len(reparsed_inner.entries) != len(original_inner.entries):
        raise TitleCandidateError("candidate JP title LINK count changed")
    for index in range(TARGET_COUNT):
        if reparsed_inner.entries[index].data != replacements[index]:
            raise TitleCandidateError(f"candidate JP title replacement mismatch at {index}")
    for index in TAIL_INDICES:
        if sha256_bytes(reparsed_inner.entries[index].data) != original_tail_hashes[str(index)]:
            raise TitleCandidateError(f"JP tail title slot {index} changed")

    rebuilt_outer = codec.LZ4.rebuild_link(outer, {OUTER_TITLE_INDEX: rebuilt_inner})
    candidate_path = ensure_tmp_output_path(
        output_root / "candidate" / "RES_JP" / "res_lang.bin"
    )
    codec.atomic_write(
        candidate_path,
        rebuilt_outer,
        forbidden=(archive_path, switch_audit_path, *[Path(item) for item in source_file_hashes]),
    )
    candidate_spec = file_spec(candidate_path)
    require_exact_spec(candidate_spec, EXPECTED_JP_CANDIDATE, "Steam JP title candidate")

    # Release the original/rebuilt archive graphs before independently reading
    # the candidate back.  This keeps the full-resource verification bounded.
    del outer, original_inner, rebuilt_inner, reparsed_inner, rebuilt_outer, replacements
    gc.collect()

    candidate_blob = candidate_path.read_bytes()
    candidate_outer = codec.LZ4.parse_link(candidate_blob)
    del candidate_blob
    if len(candidate_outer.entries) != len(outer_non_title_hashes) + 1:
        raise TitleCandidateError("candidate JP outer LINK count changed")
    candidate_outer_hashes = {
        str(index): sha256_bytes(entry.data)
        for index, entry in enumerate(candidate_outer.entries)
        if index != OUTER_TITLE_INDEX
    }
    if candidate_outer_hashes != outer_non_title_hashes:
        raise TitleCandidateError("candidate changes an unrelated JP outer LINK entry")
    candidate_inner = codec.parse_inner_link32(candidate_outer.entries[OUTER_TITLE_INDEX].data)
    if len(candidate_inner.entries) != TARGET_COUNT + len(TAIL_INDICES):
        raise TitleCandidateError("candidate JP title LINK count changed on reparse")
    candidate_tail_hashes = {
        str(index): sha256_bytes(candidate_inner.entries[index].data) for index in TAIL_INDICES
    }
    if candidate_tail_hashes != original_tail_hashes:
        raise TitleCandidateError("candidate changes JP title slots 108/109")
    candidate_target_hashes = {
        str(index): sha256_bytes(candidate_inner.entries[index].data)
        for index in range(TARGET_COUNT)
    }
    if set(candidate_target_hashes) != {str(index) for index in range(TARGET_COUNT)}:
        raise TitleCandidateError("candidate does not retain exactly 108 title target slots")

    archive_after = file_spec(archive_path)
    require_exact_spec(archive_after, EXPECTED_JP_STOCK, "Steam JP source after build")
    if sha256_file(switch_audit_path) != audit_before:
        raise TitleCandidateError("Switch audit changed while building")
    for raw_path, expected_hash in source_file_hashes.items():
        if sha256_file(Path(raw_path)) != expected_hash:
            raise TitleCandidateError(f"source PNG changed while building: {raw_path}")

    report = {
        "schema": SCHEMA,
        "source_free": False,
        "file_only": True,
        "game_install_modified": False,
        "runtime_patch_features": [],
        "target_resource": TARGET_RESOURCE,
        "pins": {
            "steam_jp_font_baseline": dict(EXPECTED_JP_STOCK),
            "steam_jp_title_candidate": dict(EXPECTED_JP_CANDIDATE),
        },
        "inputs": {
            "steam_jp_font_baseline": {
                "path": str(archive_path),
                "before": archive_before,
                "after": archive_after,
                "unchanged": archive_before == archive_after,
            },
            "switch_v13_audit": {
                "path": str(switch_audit_path),
                "sha256": audit_before,
                "pinned": audit_before == EXPECTED_SWITCH_AUDIT_SHA256,
            },
            "switch_png_root": str(switch_png_root),
            "corrected_png_root": str(corrected_png_root),
        },
        "scope": {
            "outer_title_entry": OUTER_TITLE_INDEX,
            "title_slots": list(range(TARGET_COUNT)),
            "title_slot_count": TARGET_COUNT,
            "preserved_tail_slots": list(TAIL_INDICES),
            "source_remap": {str(key): value for key, value in SOURCE_REMAP.items()},
            "corrected_labels": {str(key): value for key, value in CORRECTED_LABELS.items()},
        },
        "placement": {
            "canvas": [PC_WIDTH, PC_HEIGHT],
            "mode": "jp_bbox_height_scale_top_left",
            "resampler": "fixed_separable_premultiplied_alpha_lanczos3",
            "runtime_screen_position_verified": False,
        },
        "entries": rows,
        "entries_sha256": canonical_json_hash(rows),
        "preservation": {
            "outer_non_title_entry_sha256": outer_non_title_hashes,
            "outer_non_title_entries_byte_preserved": True,
            "tail_slot_wrapper_sha256": original_tail_hashes,
            "tail_slots_108_109_byte_preserved": True,
            "candidate_title_wrapper_sha256": candidate_target_hashes,
        },
        "candidate": {
            "path": str(candidate_path),
            **candidate_spec,
            "pin_matches": candidate_spec == EXPECTED_JP_CANDIDATE,
            "outer_parse_valid": True,
            "inner_parse_valid": True,
            "all_108_titles_rebuilt": True,
            "candidate_title_slot_count": len(candidate_inner.entries),
            "output_under_tmp": True,
        },
        "private_payload_policy": {
            "contains_complete_game_resource": True,
            "contains_third_party_translation_pixels": True,
            "git_publish_allowed": False,
            "output_must_remain_under_tmp": True,
            "output_paths_resolve_under_tmp": True,
        },
    }
    report_path = ensure_tmp_output_path(output_root / "build_report.json")
    codec.write_json(report_path, report, forbidden=(archive_path, switch_audit_path))
    return report


def verify_output(output_root: Path) -> dict[str, Any]:
    """Re-verify a generated candidate without reading any game installation."""

    output_root = ensure_tmp_output_root(output_root)
    report_path = ensure_tmp_output_path(output_root / "build_report.json")
    candidate_path = ensure_tmp_output_path(
        output_root / "candidate" / "RES_JP" / "res_lang.bin"
    )
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TitleCandidateError(f"invalid candidate report: {exc}") from exc
    if not isinstance(report, dict) or report.get("schema") != SCHEMA:
        raise TitleCandidateError("candidate report schema mismatch")
    if report.get("target_resource") != TARGET_RESOURCE:
        raise TitleCandidateError("candidate report target resource mismatch")
    if report.get("file_only") is not True or report.get("game_install_modified") is not False:
        raise TitleCandidateError("candidate report violates file-only contract")
    actual_spec = file_spec(candidate_path)
    require_exact_spec(actual_spec, EXPECTED_JP_CANDIDATE, "written Steam JP title candidate")
    candidate = report.get("candidate")
    if not isinstance(candidate, dict) or {
        "size": candidate.get("size"),
        "sha256": candidate.get("sha256"),
    } != actual_spec:
        raise TitleCandidateError("candidate report does not match written file")
    preservation = report.get("preservation")
    if not isinstance(preservation, dict):
        raise TitleCandidateError("candidate report has no preservation proof")
    outer_hashes = preservation.get("outer_non_title_entry_sha256")
    tail_hashes = preservation.get("tail_slot_wrapper_sha256")
    if not isinstance(outer_hashes, dict) or not isinstance(tail_hashes, dict):
        raise TitleCandidateError("candidate preservation hashes are invalid")
    outer = codec.LZ4.parse_link(candidate_path.read_bytes())
    observed_outer = {
        str(index): sha256_bytes(entry.data)
        for index, entry in enumerate(outer.entries)
        if index != OUTER_TITLE_INDEX
    }
    if observed_outer != outer_hashes:
        raise TitleCandidateError("written candidate changes an unrelated outer LINK entry")
    inner = codec.parse_inner_link32(outer.entries[OUTER_TITLE_INDEX].data)
    if len(inner.entries) != TARGET_COUNT + len(TAIL_INDICES):
        raise TitleCandidateError("written candidate title slot count changed")
    observed_tail = {str(index): sha256_bytes(inner.entries[index].data) for index in TAIL_INDICES}
    if observed_tail != tail_hashes:
        raise TitleCandidateError("written candidate changes title slots 108/109")
    for index in range(TARGET_COUNT):
        _, raw_g1t = codec.LZ4.decompress_wrapper(inner.entries[index].data)
        texture = codec.parse_pc_title_g1t(raw_g1t)
        if (
            texture.format_code != codec.PC_FORMAT_BC3_ALIAS
            or (texture.width, texture.height, texture.mip_count)
            != (PC_WIDTH, PC_HEIGHT, 1)
        ):
            raise TitleCandidateError(f"written title slot {index} violates PC G1T contract")
    return {
        "candidate": actual_spec,
        "outer_non_title_entries_byte_preserved": True,
        "tail_slots_108_109_byte_preserved": True,
        "target_slot_pc_g1t_contract_verified": True,
        "target_slot_count": TARGET_COUNT,
        "game_install_modified": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    build = subcommands.add_parser("build", help="build the pinned tmp-only candidate")
    build.add_argument("--archive", type=Path, required=True)
    build.add_argument("--switch-png-root", type=Path, required=True)
    build.add_argument("--corrected-png-root", type=Path, required=True)
    build.add_argument("--switch-audit", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    verify = subcommands.add_parser("verify", help="verify a previously built tmp candidate")
    verify.add_argument("--output-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "build":
        report = build_candidate(
            archive_path=args.archive,
            switch_png_root=args.switch_png_root,
            corrected_png_root=args.corrected_png_root,
            switch_audit_path=args.switch_audit,
            output_root=args.output_root,
        )
        print(f"candidate={report['candidate']['path']}")
        print(f"candidate_sha256={report['candidate']['sha256']}")
        print(f"candidate_size={report['candidate']['size']}")
        print("target_titles=108")
        print("tail_slots_108_109_preserved=True")
        print("unrelated_outer_entries_preserved=True")
        print("game_install_modified=False")
        return 0
    result = verify_output(args.output_root)
    print(f"candidate_sha256={result['candidate']['sha256']}")
    print("verify=PASS")
    print("game_install_modified=False")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (TitleCandidateError, codec.CodecError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
