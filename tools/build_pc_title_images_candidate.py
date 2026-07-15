#!/usr/bin/env python3
"""Build a private PC PK RES_SC candidate from audited Switch title PNGs.

The command is deliberately file-only.  It reads one local PC ``res_lang.bin``
and the locally decoded Switch v1.3 title PNGs, rewrites only outer LINK entry
``/3`` and inner title entries ``/3/0..107``, and writes the candidate below the
repository's ignored ``tmp`` directory.  It never writes the game installation.

Seven audited semantic exceptions are fail-closed:

* target 0 reuses Switch 3 (``거래 내용 파악``), not the placeholder;
* targets 24 and 25 swap their Switch sources;
* targets 15, 37, 38 and 74 require deterministic corrected-label PNGs.

Every source PNG is alpha-bbox aligned to the corresponding PC title's original
ink origin on a transparent 512x128 canvas.  No Switch G1T/LINK bytes are copied.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TMP_ROOT = PROJECT_ROOT / "tmp"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pc_g1t_title_codec as codec  # noqa: E402


SCHEMA = "nobu16.pc-pk-title-images.private-batch.v1"
TARGET_COUNT = 108
PC_WIDTH = 512
PC_HEIGHT = 128
SOURCE_REMAP = {0: 3, 24: 25, 25: 24}
CORRECTED_LABELS = {38: "부대 편성", 74: "공주 정보"}


class BatchError(ValueError):
    """Raised when an input violates the audited batch contract."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def hash_json(value: Any) -> str:
    blob = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(blob)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BatchError(f"invalid JSON input {path}: {exc}") from exc


def ensure_private_output_root(raw: str | Path) -> Path:
    root = Path(raw).resolve()
    try:
        root.relative_to(TMP_ROOT.resolve())
    except ValueError as exc:
        raise BatchError(f"output root must stay under {TMP_ROOT.resolve()}") from exc
    root.mkdir(parents=True, exist_ok=True)
    return root


def alpha_bbox(rgba: bytes, width: int, height: int) -> tuple[int, int, int, int]:
    if len(rgba) != width * height * 4:
        raise BatchError("RGBA byte length does not match dimensions")
    min_x, min_y, max_x, max_y = width, height, -1, -1
    for y in range(height):
        row = y * width * 4
        for x in range(width):
            if rgba[row + x * 4 + 3]:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x < 0:
        raise BatchError("title PNG has no non-transparent pixels")
    return min_x, min_y, max_x, max_y


def paste_clipped(
    source: bytes,
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
    offset_x: int,
    offset_y: int,
) -> tuple[bytes, int]:
    """Place source RGBA on a transparent target without resampling."""

    if len(source) != source_width * source_height * 4:
        raise BatchError("source RGBA length mismatch")
    target = bytearray(target_width * target_height * 4)
    clipped_nontransparent = 0
    for sy in range(source_height):
        ty = sy + offset_y
        for sx in range(source_width):
            source_pos = (sy * source_width + sx) * 4
            alpha = source[source_pos + 3]
            if not alpha:
                continue
            tx = sx + offset_x
            if tx < 0 or tx >= target_width or ty < 0 or ty >= target_height:
                clipped_nontransparent += 1
                continue
            target_pos = (ty * target_width + tx) * 4
            target[target_pos : target_pos + 4] = source[source_pos : source_pos + 4]
    return bytes(target), clipped_nontransparent


def crop_rgba(
    rgba: bytes, width: int, height: int, bbox: tuple[int, int, int, int]
) -> tuple[bytes, int, int]:
    left, top, right, bottom = bbox
    if left < 0 or top < 0 or right >= width or bottom >= height:
        raise BatchError("crop bbox exceeds the source image")
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
        raise BatchError("resample dimensions must be positive")
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
    """Deterministic separable Lanczos3 resize in premultiplied-alpha space."""

    if len(source) != source_width * source_height * 4:
        raise BatchError("resize source RGBA length mismatch")
    horizontal = _resample_contributions(source_width, target_width)
    vertical = _resample_contributions(source_height, target_height)
    # Four float channels per pixel: R*A, G*A, B*A, A.
    intermediate = [0.0] * (target_width * source_height * 4)
    for y in range(source_height):
        for tx, contributions in enumerate(horizontal):
            red = green = blue = alpha = 0.0
            for sx, weight in contributions:
                pos = (y * source_width + sx) * 4
                a = source[pos + 3]
                red += source[pos] * a * weight
                green += source[pos + 1] * a * weight
                blue += source[pos + 2] * a * weight
                alpha += a * weight
            pos = (y * target_width + tx) * 4
            intermediate[pos : pos + 4] = [red, green, blue, alpha]

    output = bytearray(target_width * target_height * 4)
    for ty, contributions in enumerate(vertical):
        for x in range(target_width):
            red = green = blue = alpha = 0.0
            for sy, weight in contributions:
                pos = (sy * target_width + x) * 4
                red += intermediate[pos] * weight
                green += intermediate[pos + 1] * weight
                blue += intermediate[pos + 2] * weight
                alpha += intermediate[pos + 3] * weight
            a = min(255, max(0, int(alpha + 0.5)))
            pos = (ty * target_width + x) * 4
            if a:
                output[pos] = min(255, max(0, int(red / alpha + 0.5)))
                output[pos + 1] = min(255, max(0, int(green / alpha + 0.5)))
                output[pos + 2] = min(255, max(0, int(blue / alpha + 0.5)))
                output[pos + 3] = a
    return bytes(output)


def read_png(path: Path) -> tuple[bytes, int, int, str]:
    blob = path.read_bytes()
    rgba, width, height = codec.decode_png(blob)
    return rgba, width, height, sha256_bytes(blob)


def validate_audit(audit: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(audit, dict):
        raise BatchError("audit root must be an object")
    switch = audit.get("switch_v13")
    pc = audit.get("pc")
    if not isinstance(switch, list) or not isinstance(pc, list):
        raise BatchError("audit must contain switch_v13 and pc arrays")
    if len(switch) != TARGET_COUNT or len(pc) != TARGET_COUNT:
        raise BatchError("audit title count changed")
    for expected, row in enumerate(switch):
        if row.get("index") != expected or row.get("source") != "switch_v13":
            raise BatchError("switch audit index/source contract changed")
    for expected, row in enumerate(pc):
        if row.get("index") != expected or row.get("source") != "pc":
            raise BatchError("PC audit index/source contract changed")
    return switch, pc


def wrapper_for_rgba(
    entry_data: bytes, rgba: bytes
) -> tuple[bytes, dict[str, Any]]:
    header, raw = codec.LZ4.decompress_wrapper(entry_data)
    texture = codec.parse_pc_title_g1t(raw)
    bc3, preserved, encoded = codec.encode_bc3(
        rgba, texture.width, texture.height, template_bc3=texture.bc3
    )
    rebuilt_g1t = codec.replace_g1t_bc3(texture, bc3)
    if rebuilt_g1t == raw:
        wrapper = entry_data
    else:
        wrapper = codec.LZ4.recompress_wrapper(rebuilt_g1t, header)
        _, roundtrip = codec.LZ4.decompress_wrapper(wrapper)
        if roundtrip != rebuilt_g1t:
            raise BatchError("rebuilt title wrapper failed raw-LZ4 round-trip")
    return wrapper, {
        "total_blocks": len(texture.bc3) // 16,
        "preserved_template_blocks": preserved,
        "deterministically_encoded_blocks": encoded,
        "bc3_sha256": sha256_bytes(bc3),
        "g1t_sha256": sha256_bytes(rebuilt_g1t),
        "wrapper_sha256": sha256_bytes(wrapper),
    }


def build_candidate(
    *,
    archive_path: Path,
    switch_png_root: Path,
    corrected_png_root: Path,
    audit_path: Path,
    output_root: Path,
    expected_archive_sha256: str | None = None,
) -> dict[str, Any]:
    archive_path = archive_path.resolve()
    switch_png_root = switch_png_root.resolve()
    corrected_png_root = corrected_png_root.resolve()
    audit_path = audit_path.resolve()
    output_root = ensure_private_output_root(output_root)

    input_hashes: dict[Path, str] = {}
    archive_before = sha256_file(archive_path)
    audit_before = sha256_file(audit_path)
    input_hashes[archive_path] = archive_before
    input_hashes[audit_path] = audit_before
    if expected_archive_sha256 and archive_before != expected_archive_sha256.upper():
        raise BatchError(
            f"PC archive SHA-256 mismatch: expected={expected_archive_sha256.upper()} "
            f"actual={archive_before}"
        )
    switch_audit, pc_audit = validate_audit(load_json(audit_path))

    outer_blob = archive_path.read_bytes()
    archive_size = len(outer_blob)
    outer = codec.LZ4.parse_link(outer_blob)
    del outer_blob
    identity_outer = codec.LZ4.rebuild_link(outer)
    if len(identity_outer) != archive_size or sha256_bytes(identity_outer) != archive_before:
        raise BatchError("outer LINK identity gate failed")
    del identity_outer
    gc.collect()
    if codec.OUTER_TITLE_INDEX >= len(outer.entries):
        raise BatchError("PC archive has no title group /3")
    inner_blob = outer.entries[codec.OUTER_TITLE_INDEX].data
    inner = codec.parse_inner_link32(inner_blob)
    expected_inner_entries = TARGET_COUNT + 2
    if len(inner.entries) != expected_inner_entries:
        raise BatchError(
            "PC title group entry count mismatch: "
            f"expected={expected_inner_entries} actual={len(inner.entries)}"
        )
    original_outer_entry_sha256 = {
        index: sha256_bytes(entry.data) for index, entry in enumerate(outer.entries)
    }

    replacements: dict[int, bytes] = {}
    requested_rgba: dict[int, bytes] = {}
    rows: list[dict[str, Any]] = []
    for target_index in range(TARGET_COUNT):
        target_entry = inner.entries[target_index]
        target_header, target_raw = codec.LZ4.decompress_wrapper(target_entry.data)
        del target_header
        target_texture = codec.parse_pc_title_g1t(target_raw)
        target_rgba = codec.decode_bc3(
            target_texture.bc3, target_texture.width, target_texture.height
        )
        if sha256_bytes(target_rgba) != pc_audit[target_index].get("rgba_sha256"):
            raise BatchError(f"PC title audit mismatch at index {target_index}")
        target_bbox = alpha_bbox(target_rgba, PC_WIDTH, PC_HEIGHT)

        corrected = target_index in CORRECTED_LABELS
        source_index = SOURCE_REMAP.get(target_index, target_index)
        if corrected:
            image_path = corrected_png_root / f"{target_index:03d}.png"
            source_kind = "corrected_render"
        else:
            image_path = switch_png_root / f"{source_index:03d}.png"
            source_kind = "switch_v13"
        if not image_path.is_file():
            raise BatchError(f"missing title PNG: {image_path}")
        image_before = sha256_file(image_path)
        previous_input_hash = input_hashes.setdefault(image_path, image_before)
        if previous_input_hash != image_before:
            raise BatchError(f"source PNG hash changed within the build: {image_path}")
        source_rgba, source_width, source_height, png_sha = read_png(image_path)
        if (source_width, source_height) not in {(512, 64), (512, 128)}:
            raise BatchError(
                f"unsupported source dimensions at target {target_index}: "
                f"{source_width}x{source_height}"
            )
        if not corrected:
            audited = switch_audit[source_index]
            if (source_width, source_height) != (
                audited.get("width"),
                audited.get("height"),
            ) or sha256_bytes(source_rgba) != audited.get("rgba_sha256"):
                raise BatchError(
                    f"Switch v1.3 decoded PNG audit mismatch at source {source_index}"
                )
        source_bbox = alpha_bbox(source_rgba, source_width, source_height)
        cropped, cropped_width, cropped_height = crop_rgba(
            source_rgba, source_width, source_height, source_bbox
        )
        target_bbox_height = target_bbox[3] - target_bbox[1] + 1
        scale = target_bbox_height / cropped_height
        scaled_height = target_bbox_height
        scaled_width = max(1, int(cropped_width * scale + 0.5))
        horizontal_room = PC_WIDTH - target_bbox[0]
        if scaled_width > horizontal_room:
            scale = horizontal_room / cropped_width
            scaled_width = horizontal_room
            scaled_height = max(1, int(cropped_height * scale + 0.5))
        resized = resize_rgba_lanczos3_premultiplied(
            cropped,
            cropped_width,
            cropped_height,
            scaled_width,
            scaled_height,
        )
        offset_x = target_bbox[0]
        offset_y = target_bbox[1]
        canvas, clipped = paste_clipped(
            resized,
            scaled_width,
            scaled_height,
            PC_WIDTH,
            PC_HEIGHT,
            offset_x,
            offset_y,
        )
        if clipped:
            raise BatchError(
                f"alpha-bbox placement clips {clipped} non-transparent pixels "
                f"at target {target_index}"
            )
        canvas_bbox = alpha_bbox(canvas, PC_WIDTH, PC_HEIGHT)
        if abs(canvas_bbox[0] - target_bbox[0]) > 1 or abs(canvas_bbox[1] - target_bbox[1]) > 1:
            raise BatchError(f"scaled ink-origin alignment failed at target {target_index}")
        wrapper, encode_report = wrapper_for_rgba(target_entry.data, canvas)
        replacements[target_index] = wrapper
        requested_rgba[target_index] = canvas
        rows.append(
            {
                "target_index": target_index,
                "source_kind": source_kind,
                "source_index": None if corrected else source_index,
                "corrected_label": CORRECTED_LABELS.get(target_index),
                "source_png": {
                    "path": str(image_path),
                    "sha256": png_sha,
                    "rgba_sha256": sha256_bytes(source_rgba),
                    "width": source_width,
                    "height": source_height,
                    "alpha_bbox": list(source_bbox),
                },
                "pc_original_alpha_bbox": list(target_bbox),
                "placement": {
                    "mode": "pc_bbox_height_scale_top_left",
                    "resampler": "fixed_separable_premultiplied_alpha_lanczos3",
                    "source_crop_dimensions": [cropped_width, cropped_height],
                    "scale": scale,
                    "scaled_dimensions": [scaled_width, scaled_height],
                    "offset_x": offset_x,
                    "offset_y": offset_y,
                    "clipped_nontransparent_pixels": clipped,
                    "candidate_alpha_bbox": list(canvas_bbox),
                },
                "requested_rgba_sha256": sha256_bytes(canvas),
                "encode": encode_report,
                "source_png_sha256_before": image_before,
            }
        )

    rebuilt_inner = codec.rebuild_inner_link32(inner, replacements)
    reparsed_inner = codec.parse_inner_link32(rebuilt_inner)
    for index, wrapper in replacements.items():
        if reparsed_inner.entries[index].data != wrapper:
            raise BatchError(f"rebuilt inner LINK mismatch at index {index}")
    del replacements, reparsed_inner
    rebuilt_outer = codec.LZ4.rebuild_link(
        outer, {codec.OUTER_TITLE_INDEX: rebuilt_inner}
    )

    candidate_path = output_root / "private" / "candidate" / "RES_SC" / "res_lang.bin"
    forbidden_inputs = tuple(input_hashes)
    codec.atomic_write(candidate_path, rebuilt_outer, forbidden=forbidden_inputs)
    candidate_size = len(rebuilt_outer)
    candidate_sha256 = sha256_bytes(rebuilt_outer)
    original_tail_sha256 = {
        index: sha256_bytes(inner.entries[index].data) for index in (108, 109)
    }

    # Parsing an outer LINK materializes entry payloads.  Release the original
    # and rebuilt 180+ MiB graphs before loading the written candidate for the
    # independent 108-entry re-extraction pass.
    del (
        outer,
        inner_blob,
        inner,
        rebuilt_inner,
        rebuilt_outer,
    )
    gc.collect()

    # Re-extract every title from the written candidate and retain private PNGs
    # for visual QA.  Decoded BC3 is lossy, so the error metric is reported.
    candidate_blob = candidate_path.read_bytes()
    candidate_outer = codec.LZ4.parse_link(candidate_blob)
    del candidate_blob
    if len(candidate_outer.entries) != len(original_outer_entry_sha256):
        raise BatchError("candidate outer LINK entry count changed")
    for index, entry in enumerate(candidate_outer.entries):
        if index == codec.OUTER_TITLE_INDEX:
            continue
        if sha256_bytes(entry.data) != original_outer_entry_sha256[index]:
            raise BatchError(f"unrelated outer LINK entry {index} changed")
    candidate_inner_blob = candidate_outer.entries[codec.OUTER_TITLE_INDEX].data
    del candidate_outer
    gc.collect()
    candidate_inner = codec.parse_inner_link32(candidate_inner_blob)
    del candidate_inner_blob
    preview_root = output_root / "private" / "previews"
    preview_rows: list[bytes] = []
    for index in range(TARGET_COUNT):
        _, raw = codec.LZ4.decompress_wrapper(candidate_inner.entries[index].data)
        texture = codec.parse_pc_title_g1t(raw)
        decoded = codec.decode_bc3(texture.bc3, texture.width, texture.height)
        preview = codec.encode_rgba_png(decoded, texture.width, texture.height)
        preview_path = preview_root / f"{index:03d}.png"
        codec.atomic_write(preview_path, preview, forbidden=forbidden_inputs)
        rows[index]["candidate_preview"] = {
            "path": str(preview_path),
            "png_sha256": sha256_bytes(preview),
            "rgba_sha256": sha256_bytes(decoded),
            "error_against_requested_rgba": codec.rgba_error_metrics(
                requested_rgba[index], decoded
            ),
        }
        if index in {0, 15, 24, 25, 37, 38, 74}:
            preview_rows.append(decoded)

    problem_sheet_width = PC_WIDTH
    problem_sheet_height = PC_HEIGHT * len(preview_rows)
    problem_sheet_rgba = b"".join(preview_rows)
    problem_sheet = codec.encode_rgba_png(
        problem_sheet_rgba, problem_sheet_width, problem_sheet_height
    )
    problem_sheet_path = output_root / "private" / "problem_indices_preview.png"
    codec.atomic_write(problem_sheet_path, problem_sheet, forbidden=forbidden_inputs)

    archive_after = sha256_file(archive_path)
    audit_after = sha256_file(audit_path)
    if archive_after != archive_before or audit_after != audit_before:
        raise BatchError("archive or audit input changed during build")
    for path, expected_hash in input_hashes.items():
        current = sha256_file(path)
        if current != expected_hash:
            raise BatchError(f"source PNG changed during build: {path}")

    report = {
        "schema": SCHEMA,
        "file_only": True,
        "game_install_modified": False,
        "runtime_patch_features": [],
        "source": {
            "pc_archive": {
                "path": str(archive_path),
                "size": archive_size,
                "sha256_before": archive_before,
                "sha256_after": archive_after,
                "unchanged": True,
            },
            "private_audit": {
                "path": str(audit_path),
                "sha256_before": audit_before,
                "sha256_after": audit_after,
                "unchanged": True,
            },
            "switch_png_root": str(switch_png_root),
            "corrected_png_root": str(corrected_png_root),
        },
        "scope": {
            "outer_entry": codec.OUTER_TITLE_INDEX,
            "inner_indices": list(range(TARGET_COUNT)),
            "entry_count": TARGET_COUNT,
            "pc_only_tail_indices_preserved": [108, 109],
            "source_remap": {str(key): value for key, value in SOURCE_REMAP.items()},
            "corrected_labels": {
                str(key): value for key, value in CORRECTED_LABELS.items()
            },
        },
        "placement": {
            "mode": "pc_bbox_height_scale_top_left",
            "resampler": "fixed_separable_premultiplied_alpha_lanczos3",
            "canvas": [PC_WIDTH, PC_HEIGHT],
            "runtime_screen_position_verified": False,
        },
        "entries": rows,
        "entries_sha256": hash_json(rows),
        "candidate": {
            "path": str(candidate_path),
            "size": candidate_size,
            "sha256": candidate_sha256,
            "outer_parse_valid": True,
            "inner_parse_valid": True,
            "all_108_reextracted": True,
            "unrelated_outer_entries_preserved": True,
            "pc_only_tail_entries_preserved": all(
                sha256_bytes(candidate_inner.entries[index].data)
                == original_tail_sha256[index]
                for index in (108, 109)
            ),
        },
        "problem_indices_preview": {
            "indices_in_vertical_order": [0, 15, 24, 25, 37, 38, 74],
            "path": str(problem_sheet_path),
            "sha256": sha256_bytes(problem_sheet),
        },
        "private_payload_policy": {
            "contains_third_party_translation_pixels": True,
            "contains_complete_game_resource": True,
            "git_publish_allowed": False,
            "output_must_remain_under_tmp": True,
        },
    }
    report_path = output_root / "build_report.json"
    codec.write_json(report_path, report, forbidden=forbidden_inputs)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--switch-png-root", required=True)
    parser.add_argument("--corrected-png-root", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--expected-archive-sha256")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_candidate(
        archive_path=Path(args.archive),
        switch_png_root=Path(args.switch_png_root),
        corrected_png_root=Path(args.corrected_png_root),
        audit_path=Path(args.audit),
        output_root=Path(args.output_root),
        expected_archive_sha256=args.expected_archive_sha256,
    )
    print(f"candidate={report['candidate']['path']}")
    print(f"candidate_sha256={report['candidate']['sha256']}")
    print(f"entries={report['scope']['entry_count']}")
    print(f"problem_preview={report['problem_indices_preview']['path']}")
    print("input_unchanged=OK")
    print("game_install_modified=False")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BatchError, codec.CodecError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
