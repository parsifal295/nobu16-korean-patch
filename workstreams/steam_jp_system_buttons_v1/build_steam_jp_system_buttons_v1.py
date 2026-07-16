#!/usr/bin/env python3
"""Build a bounded Steam-JP Korean system-button candidate.

Only ``RES_JP/res_lang.bin`` outer entry ``/5`` is in scope.  This module
starts from the immutable Steam 1.1.7 JP backup and uses the Switch v2.1 to
v2.2 delta purely as a private, decoded visual reference.  It never copies a
Switch container, wrapper, G1T, or BC payload into the PC result.

The initial ``audit`` command is intentionally useful on its own: it writes
only private previews below ``tmp`` and identifies safely bounded Korean text
regions before any candidate is permitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp"
for value in (TOOLS,):
    if str(value) not in sys.path:
        sys.path.insert(0, str(value))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as codec  # noqa: E402
import trace_bottom_return_button as trace  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-system-buttons.candidate.v1"
TARGET_RESOURCE = "RES_JP/res_lang.bin"
OUTER_INDEX = 5
NESTED_SLOT = 0
TEXTURE_INDEX = 1
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
# A candidate archive is deliberately disabled until a reviewable immutable
# PC-background donor plan exists.  Private audit commands remain read-only.
CANDIDATE_GENERATION_ENABLED = False
GAME_INSTALL_WRITE_ENABLED = False
GIT_OR_RELEASE_WRITE_ENABLED = False

BASELINE = {
    "size": 154216023,
    "sha256": "0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0",
}
SWITCH_V21 = {
    "zip_size": 84369615,
    "zip_sha256": "473213B0013FB24C812C517A147A15D51EFCBFCE975FBB51738EFC34F5E7B387",
    "member_size": 86777150,
    "member_sha256": "C79B8F205CDAAF374B2F84F3AE4E385CE8498C5BA7CB8071DD2B9A178A27688D",
}
SWITCH_V22 = {
    "zip_size": 83752794,
    "zip_sha256": "5E6354069E38BE22E3B3C9272A6CEC8A4B4110DF2486B9A63E84D1058C35D7F7",
    "member_size": 85548771,
    "member_sha256": "F179D9A89A7D20B51E26681208CA7186BDD1DC6B2F09FAF9CA8154B35933557F",
}

# The mapping is deliberately small and manual.  Each row was checked against
# private 1:1 PC/Switch atlas crops.  A source band supplies only the Korean
# word area; its corresponding PC destination band preserves a PC-only icon
# (when one exists) and the surrounding native button background.  Rows with
# an uncertain semantic/state match remain audit-only rather than being
# broadened automatically.
MAPPINGS: tuple[dict[str, Any], ...] = (
    {
        "label_ko": "닫기",
        "state": "cyan",
        "source_cell": (0, 176, 132, 240),
        "source_band": (50, 10, 130, 54),
        "target_cell": (0, 88, 192, 176),
        "target_band": (72, 14, 188, 74),
        "target_has_icon": True,
    },
    {
        "label_ko": "중지",
        "state": "cyan",
        "source_cell": (648, 128, 780, 192),
        "source_band": (50, 10, 130, 54),
        "target_cell": (648, 88, 840, 176),
        "target_band": (72, 14, 188, 74),
        "target_has_icon": False,
    },
    {
        "label_ko": "결정",
        "state": "white",
        "source_cell": (396, 240, 528, 304),
        "source_band": (50, 10, 130, 54),
        "target_cell": (576, 176, 768, 264),
        "target_band": (72, 14, 188, 74),
        "target_has_icon": True,
    },
    {
        "label_ko": "거부",
        "state": "white",
        "source_cell": (1716, 256, 1848, 320),
        "source_band": (50, 10, 130, 54),
        "target_cell": (0, 176, 192, 264),
        "target_band": (72, 14, 188, 74),
        "target_has_icon": True,
    },
    {
        "label_ko": "뒤로",
        "state": "white",
        "source_cell": (0, 304, 132, 368),
        "source_band": (50, 10, 130, 54),
        "target_cell": (3264, 176, 3456, 264),
        "target_band": (72, 14, 188, 74),
        "target_has_icon": True,
    },
    {
        "label_ko": "아니오",
        "state": "white",
        "source_cell": (1584, 320, 1716, 384),
        "source_band": (16, 10, 120, 54),
        "target_cell": (192, 264, 384, 352),
        "target_band": (24, 14, 176, 74),
        "target_has_icon": False,
    },
    {
        "label_ko": "건너뛰기",
        "state": "cyan",
        "source_cell": (132, 496, 264, 560),
        "source_band": (6, 10, 128, 54),
        "target_cell": (3648, 352, 3840, 440),
        "target_band": (8, 14, 184, 74),
        "target_has_icon": False,
    },
    {
        "label_ko": "예",
        "state": "cyan",
        "source_cell": (1716, 576, 1848, 640),
        "source_band": (20, 10, 112, 54),
        "target_cell": (384, 512, 576, 600),
        "target_band": (28, 14, 164, 74),
        "target_has_icon": False,
    },
)

# These cells were independently matched after the core eight were frozen.
# They are a catalog for the *next* donor-validated batch, not candidate work:
# ``CANDIDATE_GENERATION_ENABLED`` remains false and no text/background pixels
# from these rows are currently emitted.
NEXT_BATCH_MAPPINGS: tuple[dict[str, Any], ...] = (
    {
        "label_ko": "전부개방",
        "state": "cyan",
        "source_cell": (132, 240, 264, 304),
        "target_cell": (192, 176, 384, 264),
        "target_has_icon": False,
    },
    {
        "label_ko": "희",
        "state": "cyan",
        "source_cell": (132, 368, 264, 432),
        "target_cell": (1536, 264, 1728, 352),
        "target_has_icon": False,
    },
    {
        "label_ko": "지휘",
        "state": "white",
        "source_cell": (396, 368, 528, 432),
        "target_cell": (2880, 264, 3072, 352),
        "target_has_icon": False,
    },
    {
        "label_ko": "재교섭",
        "state": "blue",
        "source_cell": (660, 368, 792, 432),
        "target_cell": (2112, 352, 2304, 440),
        "target_has_icon": True,
    },
    {
        "label_ko": "승낙",
        "state": "white",
        "source_cell": (0, 432, 132, 496),
        "target_cell": (768, 352, 960, 440),
        "target_has_icon": True,
    },
    {
        "label_ko": "처단",
        "state": "blue",
        "source_cell": (528, 432, 660, 496),
        "target_cell": (2688, 352, 2880, 440),
        "target_has_icon": False,
    },
    {
        "label_ko": "등용",
        "state": "blue",
        "source_cell": (660, 496, 792, 560),
        "target_cell": (0, 440, 192, 528),
        "target_has_icon": False,
    },
    {
        "label_ko": "무장",
        "state": "white",
        "source_cell": (0, 560, 132, 624),
        "target_cell": (2880, 440, 3072, 528),
        "target_has_icon": False,
    },
    {
        "label_ko": "다음",
        "state": "white",
        "source_cell": (792, 576, 924, 640),
        "target_cell": (768, 512, 960, 600),
        "target_has_icon": True,
    },
    {
        "label_ko": "승인",
        "state": "cyan",
        "source_cell": (1452, 128, 1584, 192),
        "target_cell": (2688, 0, 2880, 88),
        "target_has_icon": True,
    },
    {
        "label_ko": "부인",
        "state": "cyan",
        "source_cell": (1584, 192, 1716, 256),
        "target_cell": (2880, 88, 3072, 176),
        "target_has_icon": True,
    },
)

DEFERRED_LABELS_KO = (
    "개시",
)

# A cell correspondence is not itself a safe editable mapping.  The PC
# ``뒤로`` target crosses adjacent button art and contains a residual prior
# label fragment, so it is explicitly excluded from any future candidate
# until a screen-level remap has been reviewed.
INVALID_CORE_MAPPINGS: tuple[dict[str, Any], ...] = (
    {
        "label_ko": "뒤로",
        "source_cell": (0, 304, 132, 368),
        "target_cell": (3264, 176, 3456, 264),
        "reason": "PC target cell crosses button boundaries and contains a residual previous-label fragment; screen-level remap required",
    },
)


class SystemButtonsError(ValueError):
    """The constrained system-button contract was violated."""


@dataclass(frozen=True)
class DecodedTexture:
    archive_sha256: str
    bundle_sha256: str
    wrapper_sha256: str
    raw_sha256: str
    texture: trace.Texture
    rgba: bytes


@dataclass(frozen=True)
class SystemBundle:
    fixed_header: bytes
    table_offset: int
    resource_id: int
    pre_slot: bytes
    wrapper: bytes
    tail: bytes
    slot_offset: int


def require(value: bool, message: str) -> None:
    if not value:
        raise SystemButtonsError(message)


def sha256_bytes(blob: bytes | bytearray | memoryview) -> str:
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
    require(dict(actual) == dict(expected), f"{label} pin mismatch: {actual}")


def is_reparse(path: Path) -> bool:
    try:
        return bool(path.lstat().st_file_attributes & 0x400)
    except (AttributeError, FileNotFoundError):
        return path.is_symlink()


def lexical_tmp_path(path: Path) -> tuple[Path, Path]:
    raw = path.expanduser()
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    lexical = Path(os.path.abspath(str(raw)))
    tmp_lexical = Path(os.path.abspath(str(TMP_ROOT)))
    try:
        lexical.relative_to(tmp_lexical)
    except ValueError as exc:
        raise SystemButtonsError(f"output must remain below {tmp_lexical}: {lexical}") from exc
    cursor = lexical
    while True:
        if cursor.exists() and is_reparse(cursor):
            raise SystemButtonsError(f"refusing reparse-point path below tmp: {cursor}")
        if cursor == tmp_lexical:
            break
        cursor = cursor.parent
    return lexical, tmp_lexical


def ensure_tmp(path: Path, *, mkdir: bool = False) -> Path:
    lexical, tmp_lexical = lexical_tmp_path(path)
    if is_reparse(tmp_lexical):
        raise SystemButtonsError(f"tmp root is a reparse point: {tmp_lexical}")
    if mkdir:
        lexical.mkdir(parents=True, exist_ok=True)
    resolved = lexical.resolve()
    tmp = tmp_lexical.resolve()
    try:
        resolved.relative_to(tmp)
    except ValueError as exc:
        raise SystemButtonsError(f"resolved output escaped tmp: {resolved}") from exc
    if is_reparse(resolved):
        raise SystemButtonsError(f"resolved output is a reparse point: {resolved}")
    return resolved


def fresh_output_root(path: Path) -> Path:
    path = ensure_tmp(path)
    require(not path.exists(), f"refusing to replace existing output root: {path}")
    path.mkdir(parents=True, exist_ok=False)
    return ensure_tmp(path)


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    path = ensure_tmp(path)
    forbidden_resolved = {item.resolve() for item in forbidden}
    require(path not in forbidden_resolved, f"refusing to overwrite input: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: Mapping[str, Any], *, forbidden: Iterable[Path] = ()) -> None:
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"), forbidden=forbidden)


def switch_resource(zip_path: Path, pin: Mapping[str, Any], label: str) -> tuple[bytes, str]:
    zip_path = zip_path.resolve()
    require_spec(file_spec(zip_path), {"size": pin["zip_size"], "sha256": pin["zip_sha256"]}, f"{label} ZIP")
    with zipfile.ZipFile(zip_path) as archive:
        try:
            resource = archive.read(SWITCH_MEMBER)
        except KeyError as exc:
            raise SystemButtonsError(f"{label}: missing {SWITCH_MEMBER}") from exc
    require(len(resource) == pin["member_size"] and sha256_bytes(resource) == pin["member_sha256"], f"{label} resource pin mismatch")
    return resource, sha256_file(zip_path)


def decode_outer_texture(blob: bytes, *, label: str) -> DecodedTexture:
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"{label}: outer LINK identity failed")
    require(OUTER_INDEX < len(outer.entries), f"{label}: missing /{OUTER_INDEX}")
    bundle_data = outer.entries[OUTER_INDEX].data
    bundle = trace.parse_bundle(bundle_data)
    slots = {entry.index: entry for entry in bundle.entries}
    require(set(slots) == {NESTED_SLOT}, f"{label}: unexpected physical /5 slot set: {sorted(slots)}")
    wrapper = slots[NESTED_SLOT].data
    _, raw = lz4.decompress_wrapper(wrapper)
    header, textures = trace.parse_g1t(raw)
    require(TEXTURE_INDEX < len(textures), f"{label}: missing texture {TEXTURE_INDEX}")
    texture = textures[TEXTURE_INDEX]
    require(texture.format_code == 0x5B and texture.mip_count == 1 and texture.extra_version == 0x10, f"{label}: /5/0 texture1 contract drifted")
    rgba = trace.decode_texture(texture)
    return DecodedTexture(
        archive_sha256=sha256_bytes(blob),
        bundle_sha256=sha256_bytes(bundle_data),
        wrapper_sha256=sha256_bytes(wrapper),
        raw_sha256=sha256_bytes(raw),
        texture=texture,
        rgba=rgba,
    )


def parse_system_bundle(blob: bytes) -> SystemBundle:
    """Parse the one-slot ``/5`` nested LINK without treating it as outer LINK."""

    require(len(blob) >= 64 and blob[:4] == b"LINK", "/5 is not a nested LINK")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", blob, 4)
    require(count == 1 and table_offset == 32 and resource_id == 3856, "/5 nested LINK contract drifted")
    require(blob[20:32] == b"\0" * 12, "/5 nested LINK extension drifted")
    table_end = table_offset + count * 8
    require(
        aligned_table_end == 64 and aligned_table_end >= table_end,
        f"/5 nested LINK alignment drifted: count={count} table_offset={table_offset} resource_id={resource_id} aligned_table_end={aligned_table_end} table_end={table_end}",
    )
    slot_offset, stored_size = struct.unpack_from("<II", blob, table_offset)
    require(slot_offset >= aligned_table_end and slot_offset + stored_size <= len(blob), "/5 nested slot range invalid")
    return SystemBundle(
        fixed_header=blob[:table_offset],
        table_offset=table_offset,
        resource_id=resource_id,
        pre_slot=blob[table_end:slot_offset],
        wrapper=blob[slot_offset : slot_offset + stored_size],
        tail=blob[slot_offset + stored_size :],
        slot_offset=slot_offset,
    )


def rebuild_system_bundle(bundle: SystemBundle, wrapper: bytes) -> bytes:
    output = bytearray(bundle.fixed_header)
    output.extend(b"\0" * 8)
    output.extend(bundle.pre_slot)
    require(len(output) == bundle.slot_offset, "/5 nested pre-slot placement drifted")
    struct.pack_into("<II", output, bundle.table_offset, len(output), len(wrapper))
    output.extend(wrapper)
    output.extend(bundle.tail)
    rebuilt = bytes(output)
    parsed = parse_system_bundle(rebuilt)
    require(parsed.wrapper == wrapper and parsed.pre_slot == bundle.pre_slot and parsed.tail == bundle.tail, "/5 nested LINK replacement re-extraction failed")
    return rebuilt


def box_width(box: tuple[int, int, int, int]) -> int:
    return box[2] - box[0]


def box_height(box: tuple[int, int, int, int]) -> int:
    return box[3] - box[1]


def require_box(box: tuple[int, int, int, int], width: int, height: int, name: str) -> None:
    require(0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height, f"{name} is outside {width}x{height}: {box}")


def offset_box(cell: tuple[int, int, int, int], relative: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return (cell[0] + relative[0], cell[1] + relative[1], cell[0] + relative[2], cell[1] + relative[3])


def lanczos3(value: float) -> float:
    """Return the locally-owned Lanczos-3 kernel for raster-only resampling."""

    value = abs(value)
    if value < 1e-12:
        return 1.0
    if value >= 3.0:
        return 0.0
    return math.sin(math.pi * value) * math.sin(math.pi * value / 3.0) / (math.pi * math.pi * value * value / 3.0)


def resample_contributions(source_size: int, target_size: int) -> list[list[tuple[int, float]]]:
    require(source_size > 0 and target_size > 0, "resample dimensions must be positive")
    scale = target_size / source_size
    output: list[list[tuple[int, float]]] = []
    for target in range(target_size):
        source_position = (target + 0.5) / scale - 0.5
        first = math.floor(source_position) - 2
        weighted: list[tuple[int, float]] = []
        total = 0.0
        for source in range(first, first + 6):
            if 0 <= source < source_size:
                weight = lanczos3(source_position - source)
                if weight:
                    weighted.append((source, weight))
                    total += weight
        if not weighted or abs(total) < 1e-12:
            output.append([(min(source_size - 1, max(0, int(source_position + 0.5))), 1.0)])
        else:
            output.append([(source, weight / total) for source, weight in weighted])
    return output


def resize_rgba_lanczos3_premultiplied(
    source: bytes,
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
) -> bytes:
    """Resize RGBA in premultiplied-alpha space without title-art dependencies."""

    require(len(source) == source_width * source_height * 4, "invalid resample source RGBA")
    horizontal = resample_contributions(source_width, target_width)
    vertical = resample_contributions(source_height, target_height)
    intermediate = [0.0] * (target_width * source_height * 4)
    for y in range(source_height):
        for target_x, contributions in enumerate(horizontal):
            red = green = blue = alpha = 0.0
            for source_x, weight in contributions:
                point = (y * source_width + source_x) * 4
                source_alpha = source[point + 3]
                red += source[point] * source_alpha * weight
                green += source[point + 1] * source_alpha * weight
                blue += source[point + 2] * source_alpha * weight
                alpha += source_alpha * weight
            point = (y * target_width + target_x) * 4
            intermediate[point : point + 4] = [red, green, blue, alpha]

    output = bytearray(target_width * target_height * 4)
    for target_y, contributions in enumerate(vertical):
        for x in range(target_width):
            red = green = blue = alpha = 0.0
            for source_y, weight in contributions:
                point = (source_y * target_width + x) * 4
                red += intermediate[point] * weight
                green += intermediate[point + 1] * weight
                blue += intermediate[point + 2] * weight
                alpha += intermediate[point + 3] * weight
            rounded_alpha = min(255, max(0, int(alpha + 0.5)))
            if rounded_alpha:
                point = (target_y * target_width + x) * 4
                output[point] = min(255, max(0, int(red / alpha + 0.5)))
                output[point + 1] = min(255, max(0, int(green / alpha + 0.5)))
                output[point + 2] = min(255, max(0, int(blue / alpha + 0.5)))
                output[point + 3] = rounded_alpha
    return bytes(output)


def boxes_overlap(left: tuple[int, int, int, int], right: tuple[int, int, int, int]) -> bool:
    return not (left[2] <= right[0] or right[2] <= left[0] or left[3] <= right[1] or right[3] <= left[1])


def mapping_contract() -> None:
    labels: set[str] = set()
    source_cells: set[tuple[int, int, int, int]] = set()
    target_cells: set[tuple[int, int, int, int]] = set()
    target_bands: list[tuple[int, int, int, int]] = []
    for row in MAPPINGS:
        label = row["label_ko"]
        require(isinstance(label, str) and label and label not in labels, "mapping Korean label contract drifted")
        labels.add(label)
        source_cell = row["source_cell"]
        target_cell = row["target_cell"]
        require(isinstance(source_cell, tuple) and isinstance(target_cell, tuple), "mapping cell type drifted")
        require_box(source_cell, 2048, 2048, f"{label} source cell")
        require_box(target_cell, 4096, 2048, f"{label} target cell")
        require(source_cell not in source_cells, f"duplicated source cell for {label}")
        source_cells.add(source_cell)
        require(target_cell not in target_cells, f"duplicated target cell for {label}")
        target_cells.add(target_cell)
        source_band = offset_box(source_cell, row["source_band"])
        target_band = offset_box(target_cell, row["target_band"])
        require_box(source_band, 2048, 2048, f"{label} source band")
        require_box(target_band, 4096, 2048, f"{label} target band")
        require(source_cell[0] <= source_band[0] < source_band[2] <= source_cell[2] and source_cell[1] <= source_band[1] < source_band[3] <= source_cell[3], f"{label} source band escaped source cell")
        require(target_cell[0] <= target_band[0] < target_band[2] <= target_cell[2] and target_cell[1] <= target_band[1] < target_band[3] <= target_cell[3], f"{label} target band escaped target cell")
        require(not any(boxes_overlap(target_band, previous) for previous in target_bands), f"target label bands overlap at {label}")
        target_bands.append(target_band)
    require(len(MAPPINGS) == 8 and labels == {"닫기", "중지", "결정", "거부", "뒤로", "아니오", "건너뛰기", "예"}, "manual mapping coverage drifted")
    next_batch_mapping_contract(labels, source_cells, target_cells)
    invalid_core_mapping_contract()


def next_batch_mapping_contract(
    core_labels: set[str],
    core_source_cells: set[tuple[int, int, int, int]],
    core_target_cells: set[tuple[int, int, int, int]],
) -> None:
    """Validate the audit-only next-batch catalog without emitting pixels."""

    labels: set[str] = set()
    source_cells: set[tuple[int, int, int, int]] = set()
    target_cells: set[tuple[int, int, int, int]] = set()
    for row in NEXT_BATCH_MAPPINGS:
        label = row["label_ko"]
        source_cell = row["source_cell"]
        target_cell = row["target_cell"]
        require(isinstance(label, str) and label and label not in labels and label not in core_labels, "next-batch label contract drifted")
        require(row["state"] in {"cyan", "white", "blue"} and isinstance(row["target_has_icon"], bool), f"next-batch state/icon contract drifted at {label}")
        require_box(source_cell, 2048, 2048, f"{label} next-batch source cell")
        require_box(target_cell, 4096, 2048, f"{label} next-batch target cell")
        require(source_cell not in source_cells and source_cell not in core_source_cells, f"next-batch source collision at {label}")
        require(target_cell not in target_cells and target_cell not in core_target_cells, f"next-batch target collision at {label}")
        labels.add(label)
        source_cells.add(source_cell)
        target_cells.add(target_cell)
    require(len(NEXT_BATCH_MAPPINGS) == 11 and labels == {"전부개방", "희", "지휘", "재교섭", "승낙", "처단", "등용", "무장", "다음", "승인", "부인"}, "next-batch catalog coverage drifted")
    require(not labels.intersection(DEFERRED_LABELS_KO), "next-batch catalog overlaps deferred labels")
    # The catalog stores whole cells only, so it must not silently promise a
    # particular label-band/donor plan before the immutable-donor review.


def invalid_core_mapping_contract() -> None:
    """Keep screen-boundary exclusions explicit in source-free metadata."""

    core_by_label = {row["label_ko"]: row for row in MAPPINGS}
    require(len(INVALID_CORE_MAPPINGS) == 1 and INVALID_CORE_MAPPINGS[0]["label_ko"] == "뒤로", "invalid-core catalog coverage drifted")
    for row in INVALID_CORE_MAPPINGS:
        label = row["label_ko"]
        core = core_by_label.get(label)
        require(core is not None, f"invalid core label no longer exists: {label}")
        require(core["source_cell"] == row["source_cell"] and core["target_cell"] == row["target_cell"], f"invalid core coordinate drifted: {label}")
        require(isinstance(row["reason"], str) and row["reason"], f"invalid core reason missing: {label}")


def local_contrast_mask(rgba: bytes, width: int, height: int, *, threshold: int) -> bytearray:
    """Return a mask for locally high-contrast text-like pixels in a band."""

    require(len(rgba) == width * height * 4 and width >= 5 and height >= 5, "invalid local-contrast source")
    require(0 <= threshold <= 255, "invalid local-contrast threshold")
    mask = bytearray(width * height)
    for y in range(2, height - 2):
        for x in range(2, width - 2):
            offset = (y * width + x) * 4
            if rgba[offset + 3] < 32:
                continue
            total = [0, 0, 0]
            count = 0
            for yy in range(y - 2, y + 3):
                for xx in range(x - 2, x + 3):
                    if xx != x or yy != y:
                        point = (yy * width + xx) * 4
                        for channel in range(3):
                            total[channel] += rgba[point + channel]
                        count += 1
            contrast = max(abs(rgba[offset + channel] - total[channel] // count) for channel in range(3))
            if contrast >= threshold:
                mask[y * width + x] = 1
    return mask


def resize_mask_nearest(mask: bytearray, width: int, height: int, target_width: int, target_height: int) -> bytearray:
    """Scale a binary glyph mask without introducing antialiased coverage."""

    require(len(mask) == width * height and target_width > 0 and target_height > 0, "invalid binary mask resize")
    output = bytearray(target_width * target_height)
    for y in range(target_height):
        source_y = min(height - 1, y * height // target_height)
        for x in range(target_width):
            output[y * target_width + x] = mask[source_y * width + min(width - 1, x * width // target_width)]
    return output


def korean_glyph_foreground(jp_rgba: bytes, ko_rgba: bytes, width: int, height: int) -> tuple[bytes, int]:
    """Extract only Switch v2.2 Korean glyph deltas, never its button skin."""

    require(len(jp_rgba) == len(ko_rgba) == width * height * 4, "invalid Korean glyph delta source")
    contrast = local_contrast_mask(ko_rgba, width, height, threshold=28)
    initial = bytearray(width * height)
    for pixel, active in enumerate(contrast):
        if not active:
            continue
        offset = pixel * 4
        if max(abs(ko_rgba[offset + channel] - jp_rgba[offset + channel]) for channel in range(4)) >= 24:
            initial[pixel] = 1
    # One-cell dilation preserves antialiased Korean outlines without pulling
    # in the platform-specific Switch button fill.
    mask = dilate(initial, width, height, 1)
    output = bytearray(ko_rgba)
    count = 0
    for pixel, active in enumerate(mask):
        offset = pixel * 4
        if active:
            count += 1
        else:
            output[offset + 3] = 0
    require(count >= max(24, width * height // 48), "Korean glyph delta extraction is unexpectedly sparse")
    return bytes(output), count


def inpaint_masked_pc_glyphs(
    target: bytearray,
    target_width: int,
    box: tuple[int, int, int, int],
    mask: bytearray,
) -> int:
    """Replace only detected Japanese glyph pixels with local PC neighbours.

    The PC texture's alpha encodes antialiasing and shadow geometry.  Filling
    only the text mask avoids the transparent rectangular holes caused by
    replacing an entire band with a flat cross-platform background.
    """

    target_height = len(target) // (target_width * 4)
    require_box(box, target_width, target_height, "masked PC glyph inpaint box")
    width, height = box_width(box), box_height(box)
    require(len(mask) == width * height, "masked PC glyph inpaint dimensions mismatch")
    working = bytearray(crop_rgba(bytes(target), target_width, target_height, box))
    pending = bytearray(mask)
    changed = 0
    for _ in range(width + height):
        source = bytes(working)
        filled: list[tuple[int, tuple[int, int, int, int]]] = []
        for pixel, active in enumerate(pending):
            if not active:
                continue
            x, y = pixel % width, pixel // width
            neighbours: list[int] = []
            for yy in range(max(0, y - 1), min(height, y + 2)):
                for xx in range(max(0, x - 1), min(width, x + 2)):
                    neighbour = yy * width + xx
                    if neighbour != pixel and not pending[neighbour]:
                        neighbours.append(neighbour)
            if neighbours:
                filled.append(
                    (
                        pixel,
                        tuple(sum(source[neighbour * 4 + channel] for neighbour in neighbours) // len(neighbours) for channel in range(4)),
                    )
                )
        if not filled:
            break
        for pixel, colour in filled:
            point = pixel * 4
            working[point : point + 4] = bytes(colour)
            pending[pixel] = 0
            changed += 1
        if not any(pending):
            break
    require(not any(pending), "PC glyph inpaint mask could not reach native background samples")
    for y in range(height):
        source = y * width * 4
        destination = ((box[1] + y) * target_width + box[0]) * 4
        target[destination : destination + width * 4] = working[source : source + width * 4]
    return changed


def alpha_composite(target: bytearray, target_width: int, box: tuple[int, int, int, int], foreground: bytes) -> None:
    """Alpha-composite source glyph pixels over an inpainted native PC band."""

    width, height = box_width(box), box_height(box)
    require(len(foreground) == width * height * 4, "foreground dimensions mismatch")
    for y in range(height):
        for x in range(width):
            source = (y * width + x) * 4
            alpha = foreground[source + 3]
            if alpha == 0:
                continue
            destination = ((box[1] + y) * target_width + box[0] + x) * 4
            inverse = 255 - alpha
            for channel in range(3):
                target[destination + channel] = (foreground[source + channel] * alpha + target[destination + channel] * inverse + 127) // 255
            target[destination + 3] = alpha + (target[destination + 3] * inverse + 127) // 255


def is_in_any_rect(x: int, y: int, rects: Iterable[tuple[int, int, int, int]]) -> bool:
    return any(left <= x < right and top <= y < bottom for left, top, right, bottom in rects)


def block_expanded(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return (box[0] & ~3, box[1] & ~3, (box[2] + 3) & ~3, (box[3] + 3) & ~3)


def changed_bc3_blocks_outside(
    left: bytes,
    right: bytes,
    width: int,
    allowed: Iterable[tuple[int, int, int, int]],
) -> int:
    """Count altered BC3 blocks that do not intersect an approved label band."""

    require(len(left) == len(right) and len(left) % 16 == 0 and width % 4 == 0, "invalid BC3 block buffers")
    blocks_wide = width // 4
    outside = 0
    for block_index in range(len(left) // 16):
        start = block_index * 16
        if left[start : start + 16] == right[start : start + 16]:
            continue
        x = (block_index % blocks_wide) * 4
        y = (block_index // blocks_wide) * 4
        if not is_in_any_rect(x + 1, y + 1, allowed):
            outside += 1
    return outside


def build_candidate(
    *,
    baseline: Path,
    switch_v21_zip: Path,
    switch_v22_zip: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Rebuild exactly one PC ``/5/0 texture1`` candidate below ``tmp``."""

    require(
        CANDIDATE_GENERATION_ENABLED,
        "candidate generation is disabled: no immutable PC-background donor/pixel-bound proof has been approved",
    )
    mapping_contract()
    baseline = baseline.resolve()
    switch_v21_zip = switch_v21_zip.resolve()
    switch_v22_zip = switch_v22_zip.resolve()
    require_spec(file_spec(baseline), BASELINE, "Steam JP 1.1.7 baseline")
    output_root = fresh_output_root(output_root)
    baseline_before = file_spec(baseline)
    baseline_blob = baseline.read_bytes()
    outer = lz4.parse_link(baseline_blob)
    require(lz4.rebuild_link(outer) == baseline_blob and OUTER_INDEX < len(outer.entries), "Steam JP /5 outer LINK identity failed")
    outer_before = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(outer.entries)}
    bundle = parse_system_bundle(outer.entries[OUTER_INDEX].data)
    wrapper_header, raw = lz4.decompress_wrapper(bundle.wrapper)
    g1t_header, textures = trace.parse_g1t(raw)
    require(g1t_header["platform"] == 0x0A and len(textures) == 13, "Steam JP /5 G1T topology drifted")
    target_texture = textures[TEXTURE_INDEX]
    require((target_texture.width, target_texture.height, target_texture.format_code, target_texture.mip_count, target_texture.extra_version) == (4096, 2048, 0x5B, 1, 0x10), "Steam JP /5 texture1 contract drifted")
    payload_end = target_texture.payload_offset + len(target_texture.base_payload)
    require(payload_end == target_texture.end, "Steam JP /5 texture1 has unexpected trailing mip bytes")
    pc_rgba = codec.decode_bc3(target_texture.base_payload, target_texture.width, target_texture.height)
    requested = bytearray(pc_rgba)
    sw21_blob, sw21_zip_hash = switch_resource(switch_v21_zip, SWITCH_V21, "Switch v2.1")
    sw22_blob, sw22_zip_hash = switch_resource(switch_v22_zip, SWITCH_V22, "Switch v2.2")
    sw21 = decode_outer_texture(sw21_blob, label="Switch v2.1")
    sw22 = decode_outer_texture(sw22_blob, label="Switch v2.2")
    require((sw21.texture.width, sw21.texture.height, sw22.texture.width, sw22.texture.height) == (2048, 2048, 2048, 2048), "Switch button texture geometry drifted")

    target_bands: list[tuple[int, int, int, int]] = []
    rows: list[dict[str, Any]] = []
    for row in MAPPINGS:
        label = row["label_ko"]
        source_cell = row["source_cell"]
        target_cell = row["target_cell"]
        source_band = offset_box(source_cell, row["source_band"])
        target_band = offset_box(target_cell, row["target_band"])
        switch_jp_cell = crop_rgba(sw21.rgba, 2048, 2048, source_cell)
        switch_ko_cell = crop_rgba(sw22.rgba, 2048, 2048, source_cell)
        require(switch_jp_cell != switch_ko_cell, f"{label}: Switch v2.1→v2.2 source cell has no Korean delta")
        source_jp_band = crop_rgba(sw21.rgba, 2048, 2048, source_band)
        source_ko_band = crop_rgba(sw22.rgba, 2048, 2048, source_band)
        source_foreground, foreground_pixel_count = korean_glyph_foreground(
            source_jp_band,
            source_ko_band,
            box_width(source_band),
            box_height(source_band),
        )
        destination = resize_rgba_lanczos3_premultiplied(
            source_foreground,
            box_width(source_band),
            box_height(source_band),
            box_width(target_band),
            box_height(target_band),
        )
        existing = crop_rgba(pc_rgba, 4096, 2048, target_band)
        require(any(existing[offset + 3] >= 32 for offset in range(0, len(existing), 4)), f"{label}: target PC label band has no visible pixels")
        source_jp_glyph_mask = local_contrast_mask(source_jp_band, box_width(source_band), box_height(source_band), threshold=48)
        pc_glyph_mask = resize_mask_nearest(
            source_jp_glyph_mask,
            box_width(source_band),
            box_height(source_band),
            box_width(target_band),
            box_height(target_band),
        )
        erased_pc_glyph_pixel_count = inpaint_masked_pc_glyphs(requested, 4096, target_band, pc_glyph_mask)
        alpha_composite(requested, 4096, target_band, destination)
        target_bands.append(target_band)
        rows.append(
            {
                "label_ko": label,
                "state": row["state"],
                "target_has_icon": row["target_has_icon"],
                "switch_source_cell": list(source_cell),
                "switch_source_band": list(source_band),
                "pc_target_cell": list(target_cell),
                "pc_replaced_label_band": list(target_band),
                "switch_jp_cell_rgba_sha256": sha256_bytes(switch_jp_cell),
                "switch_ko_cell_rgba_sha256": sha256_bytes(switch_ko_cell),
                "source_japanese_glyph_mask_pixel_count": sum(source_jp_glyph_mask),
                "source_korean_glyph_foreground_pixel_count": foreground_pixel_count,
                "pc_japanese_glyph_inpainted_pixel_count": erased_pc_glyph_pixel_count,
                "resampled_korean_glyph_foreground_rgba_sha256": sha256_bytes(destination),
            }
        )

    # Every edit above is confined to a contract-checked, pairwise-disjoint
    # target band.  The independent proof below validates each changed *BC3
    # block* after native PC recompression.
    rebuilt_bc3, preserved_blocks, reencoded_blocks = codec.encode_bc3(bytes(requested), 4096, 2048, template_bc3=target_texture.base_payload)
    rebuilt_raw = raw[: target_texture.payload_offset] + rebuilt_bc3 + raw[payload_end:]
    _, rebuilt_textures = trace.parse_g1t(rebuilt_raw)
    rebuilt_texture = rebuilt_textures[TEXTURE_INDEX]
    require(rebuilt_raw[: target_texture.payload_offset] == raw[: target_texture.payload_offset] and rebuilt_raw[payload_end:] == raw[payload_end:], "bytes outside /5/0 texture1 BC3 payload changed")
    for texture_index, texture in enumerate(textures):
        if texture_index != TEXTURE_INDEX:
            require(rebuilt_raw[texture.start : texture.end] == raw[texture.start : texture.end], f"unrelated /5/0 texture {texture_index} changed")
    rebuilt_wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, wrapper_header)
    _, wrapper_roundtrip = lz4.decompress_wrapper(rebuilt_wrapper)
    require(wrapper_roundtrip == rebuilt_raw, "rebuilt /5 wrapper LZ4 round-trip failed")
    rebuilt_bundle = rebuild_system_bundle(bundle, rebuilt_wrapper)
    candidate_blob = lz4.rebuild_link(outer, {OUTER_INDEX: rebuilt_bundle})
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    atomic_write(candidate_path, candidate_blob, forbidden=(baseline, switch_v21_zip, switch_v22_zip))

    candidate_outer = lz4.parse_link(candidate_path.read_bytes())
    require(len(candidate_outer.entries) == len(outer.entries), "candidate outer entry count changed")
    outer_after = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(candidate_outer.entries)}
    for index, before_hash in outer_before.items():
        if index != str(OUTER_INDEX):
            require(outer_after[index] == before_hash, f"candidate changed unrelated outer /{index}")
    candidate_bundle = parse_system_bundle(candidate_outer.entries[OUTER_INDEX].data)
    _, candidate_raw = lz4.decompress_wrapper(candidate_bundle.wrapper)
    _, candidate_textures = trace.parse_g1t(candidate_raw)
    candidate_texture = candidate_textures[TEXTURE_INDEX]
    require(candidate_texture.base_payload == rebuilt_bc3, "candidate /5 texture1 BC3 re-extraction differs")
    changed_bc3_outside = changed_bc3_blocks_outside(
        target_texture.base_payload,
        candidate_texture.base_payload,
        4096,
        [block_expanded(box) for box in target_bands],
    )
    require(changed_bc3_outside == 0, "BC3 reconstruction changed blocks outside allowed label bands")
    baseline_after = file_spec(baseline)
    require_spec(baseline_after, BASELINE, "Steam JP baseline after candidate build")
    report = {
        "schema": SCHEMA,
        "file_only": True,
        "game_install_modified": False,
        "runtime_patch_features": [],
        "target_resource": TARGET_RESOURCE,
        "scope": {
            "outer_entry": OUTER_INDEX,
            "nested_slot": NESTED_SLOT,
            "texture": TEXTURE_INDEX,
            "mapped_label_count": len(rows),
            "mapped_labels_ko": [row["label_ko"] for row in rows],
            "deferred_labels_ko": list(DEFERRED_LABELS_KO),
            "all_other_outer_entries_byte_preserved": True,
            "all_other_g1t_textures_byte_preserved": True,
        },
        "inputs": {
            "steam_jp_baseline": {"before": baseline_before, "after": baseline_after, "unchanged": baseline_before == baseline_after},
            "switch_v21": {"zip_sha256": sw21_zip_hash, "resource_sha256": sw21.archive_sha256},
            "switch_v22": {"zip_sha256": sw22_zip_hash, "resource_sha256": sw22.archive_sha256},
        },
        "mappings": rows,
        "bc3": {
            "total_blocks": len(target_texture.base_payload) // 16,
            "preserved_template_blocks": preserved_blocks,
            "deterministically_reencoded_blocks": reencoded_blocks,
            "candidate_changed_pixels_outside_expanded_label_blocks": changed_bc3_outside,
            "original_texture_payload_sha256": sha256_bytes(target_texture.base_payload),
            "candidate_texture_payload_sha256": sha256_bytes(candidate_texture.base_payload),
        },
        "preservation": {
            "outer_entry_sha256_before": outer_before,
            "outer_entry_sha256_after": outer_after,
            "all_non_5_outer_entries_byte_preserved": all(outer_before[str(index)] == outer_after[str(index)] for index in range(len(outer.entries)) if index != OUTER_INDEX),
            "nested_pre_slot_sha256": sha256_bytes(bundle.pre_slot),
            "nested_tail_sha256": sha256_bytes(bundle.tail),
            "all_other_texture_bytes_preserved": True,
        },
        "candidate": {"path": str(candidate_path), **file_spec(candidate_path), "under_tmp": True, "outer_parse_valid": True, "bundle_parse_valid": True, "g1t_parse_valid": True},
        "private_payload_policy": {"contains_complete_game_resource": True, "contains_third_party_translation_pixels": True, "git_publish_allowed": False, "output_must_remain_under_tmp": True},
    }
    write_json(ensure_tmp(output_root / "build_report.json"), report, forbidden=(baseline, switch_v21_zip, switch_v22_zip, candidate_path))
    return report


def verify_output(output_root: Path) -> dict[str, Any]:
    """Re-parse a completed private candidate without touching a game install."""

    mapping_contract()
    output_root = ensure_tmp(output_root)
    report_path = ensure_tmp(output_root / "build_report.json")
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemButtonsError(f"invalid system-button candidate report: {exc}") from exc
    require(isinstance(report, dict) and report.get("schema") == SCHEMA, "candidate report schema mismatch")
    require(report.get("file_only") is True and report.get("game_install_modified") is False, "candidate report violates file-only contract")
    candidate = report.get("candidate")
    require(isinstance(candidate, Mapping) and {"size": candidate.get("size"), "sha256": candidate.get("sha256")} == file_spec(candidate_path), "candidate report hash mismatch")
    blob = candidate_path.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob and OUTER_INDEX < len(outer.entries), "candidate outer LINK identity failed")
    bundle = parse_system_bundle(outer.entries[OUTER_INDEX].data)
    _, raw = lz4.decompress_wrapper(bundle.wrapper)
    header, textures = trace.parse_g1t(raw)
    require(header["platform"] == 0x0A and len(textures) == 13, "candidate /5 G1T topology drifted")
    texture = textures[TEXTURE_INDEX]
    require((texture.width, texture.height, texture.format_code, texture.mip_count) == (4096, 2048, 0x5B, 1), "candidate texture1 geometry drifted")
    preservation = report.get("preservation")
    require(isinstance(preservation, Mapping) and preservation.get("all_non_5_outer_entries_byte_preserved") is True and preservation.get("all_other_texture_bytes_preserved") is True, "candidate preservation proof missing")
    before = preservation.get("outer_entry_sha256_before")
    after = preservation.get("outer_entry_sha256_after")
    require(isinstance(before, Mapping) and isinstance(after, Mapping), "candidate outer preservation hashes missing")
    observed = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(outer.entries)}
    require(observed == after, "candidate outer entry reparse preservation mismatch")
    for index, before_hash in before.items():
        if index != str(OUTER_INDEX):
            require(observed.get(index) == before_hash, f"candidate modified non-/5 outer {index}")
    return {"candidate": file_spec(candidate_path), "game_install_modified": False, "status": "PASS"}


def add_border(rgba: bytearray, width: int, height: int, color: tuple[int, int, int, int]) -> None:
    for x in range(width):
        rgba[x * 4 : x * 4 + 4] = bytes(color)
        bottom = ((height - 1) * width + x) * 4
        rgba[bottom : bottom + 4] = bytes(color)
    for y in range(height):
        left = (y * width) * 4
        right = (y * width + width - 1) * 4
        rgba[left : left + 4] = bytes(color)
        rgba[right : right + 4] = bytes(color)


def paste_canvas(canvas: bytearray, canvas_width: int, x: int, y: int, source: bytes, source_width: int, source_height: int) -> None:
    for row in range(source_height):
        source_start = row * source_width * 4
        target_start = ((y + row) * canvas_width + x) * 4
        canvas[target_start : target_start + source_width * 4] = source[source_start : source_start + source_width * 4]


def visual_qa(
    *,
    baseline: Path,
    switch_v21_zip: Path,
    switch_v22_zip: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Write a private four-panel proof sheet for every explicitly mapped band."""

    mapping_contract()
    baseline = baseline.resolve()
    switch_v21_zip = switch_v21_zip.resolve()
    switch_v22_zip = switch_v22_zip.resolve()
    require_spec(file_spec(baseline), BASELINE, "Steam JP 1.1.7 baseline for visual QA")
    output_root = ensure_tmp(output_root)
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    baseline_texture = decode_outer_texture(baseline.read_bytes(), label="Steam JP baseline for visual QA")
    candidate_texture = decode_outer_texture(candidate_path.read_bytes(), label="candidate for visual QA")
    sw21_blob, _ = switch_resource(switch_v21_zip, SWITCH_V21, "Switch v2.1 visual QA")
    sw22_blob, _ = switch_resource(switch_v22_zip, SWITCH_V22, "Switch v2.2 visual QA")
    sw21 = decode_outer_texture(sw21_blob, label="Switch v2.1 visual QA")
    sw22 = decode_outer_texture(sw22_blob, label="Switch v2.2 visual QA")
    require((baseline_texture.texture.width, baseline_texture.texture.height, candidate_texture.texture.width, candidate_texture.texture.height) == (4096, 2048, 4096, 2048), "visual QA PC geometry drifted")

    panel_width, panel_height, gutter = 192, 88, 4
    canvas_width = panel_width * 4 + gutter * 5
    canvas_height = (panel_height + gutter) * len(MAPPINGS) + gutter
    canvas = bytearray(canvas_width * canvas_height * 4)
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(MAPPINGS):
        label = row["label_ko"]
        source_cell = row["source_cell"]
        target_cell = row["target_cell"]
        target_band = offset_box(target_cell, row["target_band"])
        switch_jp = crop_rgba(sw21.rgba, 2048, 2048, source_cell)
        switch_ko = crop_rgba(sw22.rgba, 2048, 2048, source_cell)
        switch_jp_panel = resize_rgba_lanczos3_premultiplied(switch_jp, box_width(source_cell), box_height(source_cell), panel_width, panel_height)
        switch_ko_panel = resize_rgba_lanczos3_premultiplied(switch_ko, box_width(source_cell), box_height(source_cell), panel_width, panel_height)
        pc_jp_panel = crop_rgba(baseline_texture.rgba, 4096, 2048, target_cell)
        pc_ko_panel = crop_rgba(candidate_texture.rgba, 4096, 2048, target_cell)
        changed: list[tuple[int, int]] = []
        local_allowed = block_expanded((row["target_band"][0], row["target_band"][1], row["target_band"][2], row["target_band"][3]))
        for pixel in range(panel_width * panel_height):
            point = pixel * 4
            if pc_jp_panel[point : point + 4] != pc_ko_panel[point : point + 4]:
                x, y = pixel % panel_width, pixel // panel_width
                changed.append((x, y))
        require(changed, f"visual QA has no candidate delta for {label}")
        require(all(local_allowed[0] <= x < local_allowed[2] and local_allowed[1] <= y < local_allowed[3] for x, y in changed), f"visual QA delta escapes label blocks for {label}")
        panels = (switch_jp_panel, switch_ko_panel, pc_jp_panel, pc_ko_panel)
        colors = ((224, 64, 64, 255), (64, 208, 96, 255), (232, 196, 56, 255), (48, 208, 232, 255))
        y = gutter + index * (panel_height + gutter)
        for panel_index, (panel, color) in enumerate(zip(panels, colors)):
            marked = bytearray(panel)
            add_border(marked, panel_width, panel_height, color)
            paste_canvas(canvas, canvas_width, gutter + panel_index * (panel_width + gutter), y, marked, panel_width, panel_height)
        rows.append(
            {
                "label_ko": label,
                "state": row["state"],
                "switch_source_cell": list(source_cell),
                "pc_target_cell": list(target_cell),
                "pc_replaced_label_band": list(target_band),
                "panels_left_to_right": ["switch_jp", "switch_ko", "pc_jp_baseline", "pc_ko_candidate"],
                "candidate_changed_pixel_count": len(changed),
                "candidate_delta_within_expanded_label_blocks": True,
            }
        )
    private = ensure_tmp(output_root / "private", mkdir=True)
    contact_path = ensure_tmp(private / "system_buttons_contact_sheet.png")
    png = codec.encode_rgba_png(bytes(canvas), canvas_width, canvas_height)
    atomic_write(contact_path, png, forbidden=(baseline, switch_v21_zip, switch_v22_zip, candidate_path))
    report = {
        "schema": SCHEMA + ".visual-qa",
        "file_only": True,
        "game_install_modified": False,
        "contact_sheet": {
            "path": str(contact_path),
            "sha256": sha256_bytes(png),
            "dimensions": [canvas_width, canvas_height],
            "private_only": True,
            "panel_legend": {"red": "Switch JP", "green": "Switch KO", "yellow": "PC JP baseline", "cyan": "PC KO candidate"},
        },
        "candidate": file_spec(candidate_path),
        "mappings": rows,
        "all_candidate_deltas_within_expanded_label_blocks": True,
    }
    write_json(ensure_tmp(output_root / "visual_qa.json"), report, forbidden=(baseline, switch_v21_zip, switch_v22_zip, candidate_path))
    return report


def diff_mask(left: bytes, right: bytes) -> bytearray:
    require(len(left) == len(right) and len(left) % 4 == 0, "invalid RGBA comparison buffers")
    return bytearray(1 if left[index : index + 4] != right[index : index + 4] else 0 for index in range(0, len(left), 4))


def strong_diff_mask(left: bytes, right: bytes, *, minimum_max_channel_delta: int) -> bytearray:
    """Keep only source deltas too large to be BC3 block-side effects.

    Switch v2.2 re-encodes the entire button texture, so byte-level changes
    leak into neighbouring background pixels.  A candidate may only use the
    visibly strong portion as a text-mask clue; it never treats the complete
    changed BC3 block as Korean glyph artwork.
    """

    require(len(left) == len(right) and len(left) % 4 == 0, "invalid RGBA comparison buffers")
    require(0 <= minimum_max_channel_delta <= 255, "invalid strong-diff threshold")
    return bytearray(
        1
        if max(abs(left[index + channel] - right[index + channel]) for channel in range(4)) >= minimum_max_channel_delta
        else 0
        for index in range(0, len(left), 4)
    )


def dilate(mask: bytearray, width: int, height: int, radius: int) -> bytearray:
    require(len(mask) == width * height and radius >= 0, "invalid mask dimensions")
    output = bytearray(len(mask))
    for y in range(height):
        for x in range(width):
            if not mask[y * width + x]:
                continue
            for yy in range(max(0, y - radius), min(height, y + radius + 1)):
                start = yy * width + max(0, x - radius)
                output[start : yy * width + min(width, x + radius + 1)] = b"\x01" * (min(width, x + radius + 1) - max(0, x - radius))
    return output


def connected_boxes(mask: bytearray, width: int, height: int, *, min_pixels: int) -> list[dict[str, int]]:
    require(len(mask) == width * height, "invalid component mask dimensions")
    visited = bytearray(len(mask))
    output: list[dict[str, int]] = []
    for start in range(len(mask)):
        if not mask[start] or visited[start]:
            continue
        stack = [start]
        visited[start] = 1
        x0 = x1 = start % width
        y0 = y1 = start // width
        count = 0
        while stack:
            point = stack.pop()
            x = point % width
            y = point // width
            count += 1
            x0, x1 = min(x0, x), max(x1, x)
            y0, y1 = min(y0, y), max(y1, y)
            for yy in range(max(0, y - 1), min(height, y + 2)):
                for xx in range(max(0, x - 1), min(width, x + 2)):
                    next_point = yy * width + xx
                    if mask[next_point] and not visited[next_point]:
                        visited[next_point] = 1
                        stack.append(next_point)
        if count >= min_pixels:
            output.append({"x0": x0, "y0": y0, "x1": x1 + 1, "y1": y1 + 1, "pixels": count})
    return sorted(output, key=lambda row: (row["y0"], row["x0"]))


def crop_rgba(rgba: bytes, width: int, height: int, box: tuple[int, int, int, int]) -> bytes:
    x0, y0, x1, y1 = box
    require(0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height, f"invalid crop box: {box}")
    output = bytearray((x1 - x0) * (y1 - y0) * 4)
    for row in range(y1 - y0):
        source = ((y0 + row) * width + x0) * 4
        target = row * (x1 - x0) * 4
        output[target : target + (x1 - x0) * 4] = rgba[source : source + (x1 - x0) * 4]
    return bytes(output)


def draw_rect(rgba: bytearray, width: int, height: int, box: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    for x in range(max(0, x0), min(width, x1)):
        for y in (y0, y1 - 1):
            if 0 <= y < height:
                position = (y * width + x) * 4
                rgba[position : position + 4] = bytes(color)
    for y in range(max(0, y0), min(height, y1)):
        for x in (x0, x1 - 1):
            if 0 <= x < width:
                position = (y * width + x) * 4
                rgba[position : position + 4] = bytes(color)


def alpha_spans_at_row(rgba: bytes, width: int, height: int, y: int, *, minimum_alpha: int = 32, minimum_width: int = 16) -> list[list[int]]:
    """Return opaque-ish horizontal spans for a private atlas coordinate probe."""

    require(0 <= y < height, f"row outside atlas: {y}")
    spans: list[list[int]] = []
    start: int | None = None
    for x in range(width + 1):
        active = x < width and rgba[(y * width + x) * 4 + 3] >= minimum_alpha
        if active and start is None:
            start = x
        if not active and start is not None:
            if x - start >= minimum_width:
                spans.append([start, x])
            start = None
    return spans


def audit(
    *,
    baseline: Path,
    switch_v21_zip: Path,
    switch_v22_zip: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Decode only private visual evidence and group v2.1→v2.2 text deltas."""

    baseline = baseline.resolve()
    require_spec(file_spec(baseline), BASELINE, "Steam JP 1.1.7 baseline")
    output_root = fresh_output_root(output_root)
    baseline_before = file_spec(baseline)
    pc = decode_outer_texture(baseline.read_bytes(), label="Steam JP baseline")
    sw21_blob, sw21_zip_hash = switch_resource(switch_v21_zip, SWITCH_V21, "Switch v2.1")
    sw22_blob, sw22_zip_hash = switch_resource(switch_v22_zip, SWITCH_V22, "Switch v2.2")
    sw21 = decode_outer_texture(sw21_blob, label="Switch v2.1")
    sw22 = decode_outer_texture(sw22_blob, label="Switch v2.2")
    require((sw21.texture.width, sw21.texture.height) == (2048, 2048), "Switch v2.1 texture geometry drifted")
    require((sw22.texture.width, sw22.texture.height) == (2048, 2048), "Switch v2.2 texture geometry drifted")
    require((pc.texture.width, pc.texture.height) == (4096, 2048), "Steam JP texture geometry drifted")

    raw_mask = diff_mask(sw21.rgba, sw22.rgba)
    groups = connected_boxes(dilate(raw_mask, 2048, 2048, 3), 2048, 2048, min_pixels=32)
    strong_mask = strong_diff_mask(sw21.rgba, sw22.rgba, minimum_max_channel_delta=48)
    strong_groups = connected_boxes(dilate(strong_mask, 2048, 2048, 2), 2048, 2048, min_pixels=12)
    annotated = bytearray(trace.composite_checker(sw22.rgba, 2048, 2048))
    for item in groups:
        draw_rect(annotated, 2048, 2048, (item["x0"], item["y0"], item["x1"], item["y1"]), (255, 64, 224, 255))
    private = ensure_tmp(output_root / "private", mkdir=True)
    pc_checker = trace.composite_checker(pc.rgba, 4096, 2048)
    atomic_write(private / "switch_v22_system_buttons.png", codec.encode_rgba_png(trace.composite_checker(sw22.rgba, 2048, 2048), 2048, 2048), forbidden=(baseline, switch_v21_zip, switch_v22_zip))
    atomic_write(private / "switch_v21_to_v22_delta_groups.png", codec.encode_rgba_png(bytes(annotated), 2048, 2048), forbidden=(baseline, switch_v21_zip, switch_v22_zip))
    atomic_write(private / "pc_jp_system_buttons.png", codec.encode_rgba_png(pc_checker, 4096, 2048), forbidden=(baseline, switch_v21_zip, switch_v22_zip))
    # 1:1 crops avoid downscaling away exact PC button coordinates during
    # private manual mapping review.  These previews contain no new asset.
    for x0 in (0, 1024, 2048, 3072):
        for y0 in (0, 512, 1024, 1536):
            box = (x0, y0, x0 + 1024, y0 + 512)
            crop = crop_rgba(pc_checker, 4096, 2048, box)
            atomic_write(private / f"pc_jp_x{x0:04d}_y{y0:04d}.png", codec.encode_rgba_png(crop, 1024, 512), forbidden=(baseline, switch_v21_zip, switch_v22_zip))
    switch_checker = trace.composite_checker(sw22.rgba, 2048, 2048)
    for x0 in (0, 1024):
        for y0 in (0, 512, 1024, 1536):
            box = (x0, y0, x0 + 1024, y0 + 512)
            crop = crop_rgba(switch_checker, 2048, 2048, box)
            atomic_write(private / f"switch_v22_x{x0:04d}_y{y0:04d}.png", codec.encode_rgba_png(crop, 1024, 512), forbidden=(baseline, switch_v21_zip, switch_v22_zip))
    baseline_after = file_spec(baseline)
    require_spec(baseline_after, BASELINE, "Steam JP baseline after audit")
    report = {
        "schema": SCHEMA + ".private-audit",
        "file_only": True,
        "game_install_modified": False,
        "scope": {"outer_entry": OUTER_INDEX, "nested_slot": NESTED_SLOT, "texture": TEXTURE_INDEX, "switch_raw_or_payload_copied": False},
        "inputs": {
            "steam_jp_baseline": {"before": baseline_before, "after": baseline_after, "unchanged": baseline_before == baseline_after},
            "switch_v21": {"zip_sha256": sw21_zip_hash, "resource_sha256": sw21.archive_sha256, "texture_rgba_sha256": sha256_bytes(sw21.rgba)},
            "switch_v22": {"zip_sha256": sw22_zip_hash, "resource_sha256": sw22.archive_sha256, "texture_rgba_sha256": sha256_bytes(sw22.rgba)},
        },
        "geometry": {"pc": [pc.texture.width, pc.texture.height], "switch": [sw22.texture.width, sw22.texture.height]},
        "private_coordinate_probe": {
            "pc_alpha_spans": {
                str(y): alpha_spans_at_row(pc.rgba, pc.texture.width, pc.texture.height, y)
                for y in (24, 48, 112, 136, 200, 224, 288, 312, 376, 400, 464, 488, 552, 576, 640)
            },
            "switch_alpha_spans": {
                str(y): alpha_spans_at_row(sw21.rgba, sw21.texture.width, sw21.texture.height, y)
                for y in (152, 168, 192, 216, 256, 280, 320, 344, 384, 408, 448, 472, 512, 536, 576, 600)
            },
        },
        "raw_changed_pixel_count": sum(raw_mask),
        "delta_groups_dilated_3px": groups,
        "strong_changed_pixel_count_threshold_48": sum(strong_mask),
        "strong_delta_groups_dilated_2px_threshold_48": strong_groups,
        "private_outputs": {
            "switch_v22_atlas": str(private / "switch_v22_system_buttons.png"),
            "switch_delta_groups": str(private / "switch_v21_to_v22_delta_groups.png"),
            "pc_jp_atlas": str(private / "pc_jp_system_buttons.png"),
        },
    }
    write_json(ensure_tmp(output_root / "audit.json"), report, forbidden=(baseline, switch_v21_zip, switch_v22_zip))
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    audit_parser = sub.add_parser("audit", help="write private /5 v2.1→v2.2 raster-delta evidence below tmp")
    audit_parser.add_argument("--baseline", type=Path, required=True)
    audit_parser.add_argument("--switch-v21-zip", type=Path, required=True)
    audit_parser.add_argument("--switch-v22-zip", type=Path, required=True)
    audit_parser.add_argument("--output-root", type=Path, required=True)
    build = sub.add_parser("build", help="build a private PC-native /5 candidate below tmp")
    build.add_argument("--baseline", type=Path, required=True)
    build.add_argument("--switch-v21-zip", type=Path, required=True)
    build.add_argument("--switch-v22-zip", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    verify = sub.add_parser("verify", help="reparse an existing private /5 candidate")
    verify.add_argument("--output-root", type=Path, required=True)
    visual = sub.add_parser("visual-qa", help="write a private four-panel system-button QA sheet")
    visual.add_argument("--baseline", type=Path, required=True)
    visual.add_argument("--switch-v21-zip", type=Path, required=True)
    visual.add_argument("--switch-v22-zip", type=Path, required=True)
    visual.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "audit":
            result = audit(
                baseline=args.baseline,
                switch_v21_zip=args.switch_v21_zip,
                switch_v22_zip=args.switch_v22_zip,
                output_root=args.output_root,
            )
        elif args.command == "build":
            result = build_candidate(
                baseline=args.baseline,
                switch_v21_zip=args.switch_v21_zip,
                switch_v22_zip=args.switch_v22_zip,
                output_root=args.output_root,
            )
        elif args.command == "verify":
            result = verify_output(args.output_root)
        else:
            result = visual_qa(
                baseline=args.baseline,
                switch_v21_zip=args.switch_v21_zip,
                switch_v22_zip=args.switch_v22_zip,
                output_root=args.output_root,
            )
    except (OSError, SystemButtonsError, lz4.LZ4Error, lz4.LinkError, trace.TraceError, codec.CodecError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "delta_groups": len(result.get("delta_groups_dilated_3px", ())),
                "mapping_rows": len(result.get("rows", ())),
                "candidate_sha256": result.get("candidate", {}).get("sha256") if isinstance(result.get("candidate"), Mapping) else None,
                "status": result.get("status"),
            },
            sort_keys=True,
        )
    )
    print("game_install_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
