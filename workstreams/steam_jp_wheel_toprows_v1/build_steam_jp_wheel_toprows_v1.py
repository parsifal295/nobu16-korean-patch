#!/usr/bin/env python3
"""Build a *private*, PC-only Korean candidate for the main command wheel.

This is deliberately a narrow first image pass.  It reads the already-built
Steam-JP title candidate (``/3`` is Korean) and replaces only the Korean text
bands of the thirty main radial-command button states in ``/8/0``.  The Switch
v2.4 pixels are decoded only as a private visual source; no Switch LINK, LZ4,
G1T or BC3 bytes are copied.  The output is written below ``tmp`` only.

It does not touch a game installation, executable, DLL, registry, memory or
process.  A separate integration step must perform game-screen QA before any
apply or release operation.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import stat
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
TITLE_WORKSTREAM = REPO / "workstreams" / "steam_jp_title_images_v1"
for value in (TOOLS, TITLE_WORKSTREAM):
    if str(value) not in sys.path:
        sys.path.insert(0, str(value))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as codec  # noqa: E402
from build_steam_jp_title_images_v1 import (  # noqa: E402
    resize_rgba_lanczos3_premultiplied,
)


SCHEMA = "nobu16.kr.steam-jp-wheel-toprows.candidate.v1"
TARGET_RESOURCE = "RES_JP/res_lang.bin"
OUTER_INDEX = 8
NESTED_RESOURCE_ID = 474
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"

# This is the independently verified /3 title-image candidate, not the stock
# game archive.  The wheel builder must retain its Korean title replacement
# byte-for-byte while changing only /8.
TITLE_BASELINE = {
    "size": 160351447,
    "sha256": "D045B42BC3D4A4D4C501C5A0E010698AAE95AAE227775306A1272D5259E0888B",
}
SWITCH_V20 = {
    "zip_size": 84385377,
    "zip_sha256": "A7497986FCC53312BC40B470465CD4DD0AE5179B0B9DB92526541E10987079DD",
    "member_size": 86832335,
    "member_sha256": "79B572CE211A4D18F2A6CDF0AFD0197802463D270797993BA169F0D6BB651159",
}
SWITCH_V24 = {
    "zip_size": 83764122,
    "zip_sha256": "9BAC0A141A7DEBB779BF67EB35F582287B120CBDE6A4B4939AC4903315F7E04C",
    "member_size": 85549663,
    "member_sha256": "086A6AC3F22F09A77E325BF23675F792AB6ACA5D9CBC35564EE6BDB4433CDB06",
}

# The source is a 2048x1024 free-packed Switch atlas.  The PC atlas is
# 2048x2048 and has its large wheel arc in different holes, hence this is an
# explicit sprite mapping rather than a row/column offset.  Every mapping was
# visually checked against the Japanese PC/Switch icon and state appearance.
# ``source`` and ``target`` are (row, column) positions in their respective
# local pack grids; these are source coordinates, not a public raw atlas.
SPRITES: tuple[dict[str, Any], ...] = tuple(
    {"label": "평정", "state": state, "source": (0, 1 + state), "target": (0, 1 + state)}
    for state in range(1, 7)
) + tuple(
    {"label": "임명", "state": state, "source": (0, 7 + state), "target": (0, 7 + state)}
    for state in range(1, 7)
) + tuple(
    {
        "label": "군사",
        "state": state,
        "source": (0, 13 + state),
        "target": ((0, 13 + state) if state <= 3 else (1, state - 2)),
    }
    for state in range(1, 7)
) + tuple(
    {
        "label": "내정",
        "state": state,
        "source": ((0, 19 + state) if state <= 5 else (1, 2)),
        "target": (1, 4 + state),
    }
    for state in range(1, 7)
) + tuple(
    {
        "label": "외교",
        "state": state,
        "source": (1, 2 + state),
        "target": (1, 10 + state),
    }
    for state in range(1, 7)
)

# Switch source grid anchors and the PC grid anchors are derived from the
# observed 80px/112px sprite pitches.  Only the bounded bottom label band is
# resampled.  The source difference gate below proves the band contains text
# changes rather than icon pixels.
SWITCH_CELL = 80
SWITCH_ORIGIN = (34, -3)
PC_CELL = 112
PC_ORIGIN = (55, 0)
SOURCE_BAND = (4, 40, 76, 80)  # x0,y0,x1,y1 inside an 80x80 source sprite
TARGET_BAND = (6, 56, 107, 112)  # x0,y0,x1,y1 inside a 112x112 PC sprite


class WheelCandidateError(ValueError):
    """The constrained wheel-candidate contract was violated."""


@dataclass(frozen=True)
class WheelLink:
    fixed_header: bytes
    table_offset: int
    resource_id: int
    pre_slot: bytes
    wrapper: bytes
    tail: bytes
    slot_offset: int


@dataclass(frozen=True)
class G1TTexture:
    index: int
    start: int
    end: int
    payload_offset: int
    payload_end: int
    width: int
    height: int
    format_code: int
    mip_count: int
    extra_version: int
    extra_length: int


@dataclass(frozen=True)
class G1T:
    raw: bytes
    platform: int
    textures: tuple[G1TTexture, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WheelCandidateError(message)


def sha256_bytes(blob: bytes | bytearray | memoryview) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256_file(path)}


def require_spec(actual: Mapping[str, Any], expected: Mapping[str, Any], name: str) -> None:
    if actual.get("size") != expected.get("size") or actual.get("sha256") != expected.get("sha256"):
        raise WheelCandidateError(f"{name} pin mismatch: expected={dict(expected)} actual={dict(actual)}")


def is_reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT) or path.is_symlink() or path.is_junction()
    except OSError:
        return True


def lexical_tmp_path(path: Path) -> tuple[Path, Path]:
    """Reject outside paths *before* any output directory is created.

    ``Path.resolve`` alone is too late here: a caller-controlled ``mkdir``
    could create an outside directory before it is resolved and rejected.  Use
    an absolute lexical containment check first, then inspect each existing
    path component for any Windows reparse point as it is traversed.
    """

    tmp_lexical = Path(os.path.abspath(TMP_ROOT))
    candidate = Path(os.path.abspath(Path(path)))
    try:
        common = os.path.commonpath((os.path.normcase(str(tmp_lexical)), os.path.normcase(str(candidate))))
    except ValueError as exc:
        raise WheelCandidateError(f"output has incompatible drive: {candidate}") from exc
    if common != os.path.normcase(str(tmp_lexical)):
        raise WheelCandidateError(f"output lexically escapes tmp: {candidate}")
    try:
        candidate.relative_to(tmp_lexical)
    except ValueError as exc:
        raise WheelCandidateError(f"output lexically escapes tmp: {candidate}") from exc
    return tmp_lexical, candidate


def ensure_tmp(path: Path, *, mkdir: bool = False) -> Path:
    """Return a checked tmp path, creating only checked ordinary components."""

    tmp_lexical, candidate = lexical_tmp_path(path)
    # ``resolve`` follows a junction/symlink.  Inspect the lexical tmp root
    # first, otherwise a malicious/misconfigured tmp root could be followed
    # before this guard has a chance to reject it.
    if is_reparse(tmp_lexical):
        raise WheelCandidateError(f"tmp root is a reparse point: {tmp_lexical}")
    tmp = tmp_lexical.resolve()
    if is_reparse(tmp):
        raise WheelCandidateError(f"resolved tmp root is a reparse point: {tmp}")
    relative = candidate.relative_to(tmp_lexical)
    current = tmp
    for part in relative.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if is_reparse(current):
                raise WheelCandidateError(f"reparse point is forbidden in output path: {current}")
            resolved = current.resolve()
            try:
                resolved.relative_to(tmp)
            except ValueError as exc:
                raise WheelCandidateError(f"existing output component escapes tmp: {current}") from exc
            current = resolved
        elif mkdir:
            # The parent was already verified in the preceding iteration.
            current.mkdir(exist_ok=False)
            if is_reparse(current):
                raise WheelCandidateError(f"new output component is a reparse point: {current}")
        # A missing component has no target to follow; retain its checked
        # lexical path until it is created by a later caller.
    return current


def create_fresh_output_root(path: Path) -> Path:
    """Create one new ordinary output directory below tmp, exclusively."""

    raw = Path(path)
    parent = ensure_tmp(raw.parent, mkdir=True)
    candidate = parent / raw.name
    if candidate.exists() or candidate.is_symlink():
        raise WheelCandidateError(f"output root already exists: {candidate}")
    candidate.mkdir(exist_ok=False)
    return ensure_tmp(candidate)


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    path = ensure_tmp(path.parent, mkdir=True) / path.name
    path = ensure_tmp(path)
    for source in forbidden:
        if path == source.resolve():
            raise WheelCandidateError(f"refusing to overwrite input: {source}")
    if path.exists() or path.is_symlink():
        raise WheelCandidateError(f"refusing to overwrite existing output: {path}")
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temp_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if is_reparse(path.parent):
            raise WheelCandidateError(f"output parent became reparse point: {path.parent}")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: Mapping[str, Any], *, forbidden: Iterable[Path] = ()) -> None:
    atomic_write(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        forbidden=forbidden,
    )


def parse_wheel_link(blob: bytes) -> WheelLink:
    require(len(blob) >= 64 and blob[:4] == b"LINK", "wheel /8 is not LINK")
    count, table_offset, resource_id, aligned_end = struct.unpack_from("<4I", blob, 4)
    require(count == 1 and table_offset == 32, "wheel nested LINK shape drifted")
    require(resource_id == NESTED_RESOURCE_ID, "wheel nested resource id drifted")
    require(blob[20:32] == b"\0" * 12, "wheel nested LINK extension drifted")
    table_end = table_offset + count * 8
    require(aligned_end == 64 and aligned_end >= table_end, "wheel nested LINK alignment drifted")
    slot_offset, stored_size = struct.unpack_from("<II", blob, table_offset)
    require(slot_offset >= aligned_end and slot_offset + stored_size <= len(blob), "wheel /8/0 range invalid")
    return WheelLink(
        fixed_header=blob[:table_offset],
        table_offset=table_offset,
        resource_id=resource_id,
        pre_slot=blob[table_end:slot_offset],
        wrapper=blob[slot_offset : slot_offset + stored_size],
        tail=blob[slot_offset + stored_size :],
        slot_offset=slot_offset,
    )


def rebuild_wheel_link(link: WheelLink, wrapper: bytes) -> bytes:
    output = bytearray(link.fixed_header)
    output.extend(b"\0" * 8)
    output.extend(link.pre_slot)
    require(len(output) == link.slot_offset, "wheel nested LINK pre-slot placement drifted")
    struct.pack_into("<II", output, link.table_offset, len(output), len(wrapper))
    output.extend(wrapper)
    output.extend(link.tail)
    rebuilt = bytes(output)
    parsed = parse_wheel_link(rebuilt)
    require(parsed.wrapper == wrapper, "wheel nested LINK wrapper re-extraction failed")
    require(parsed.pre_slot == link.pre_slot and parsed.tail == link.tail, "wheel nested LINK surrounding bytes changed")
    return rebuilt


def parse_g1t(raw: bytes) -> G1T:
    require(len(raw) >= 32 and raw[:8] == b"GT1G0600", "wheel raw is not GT1G0600")
    declared_size, directory_offset, count, platform = struct.unpack_from("<4I", raw, 8)
    require(declared_size == len(raw), "wheel G1T declared size mismatch")
    # Unlike the single-texture title cards, this two-texture wheel node uses
    # a 36-byte G1T header and starts its directory at 0x24.
    require(directory_offset == 36 and count == 2 and platform == 0x0A, "wheel PC G1T contract drifted")
    # The two extra u32 words at 0x18 are format metadata.  Preserve them
    # byte-for-byte rather than falsely treating the wheel like a title card.
    require(raw[24:28] == b"\0" * 4, "wheel G1T extension drifted")
    starts = [directory_offset + struct.unpack_from("<I", raw, directory_offset + index * 4)[0] for index in range(count)]
    require(starts == sorted(starts) and starts[0] >= directory_offset + count * 4, "wheel G1T offsets invalid")
    textures: list[G1TTexture] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < count else len(raw)
        require(end - start >= 20, f"wheel G1T texture {index} truncated")
        packed, format_code, dimensions = struct.unpack_from("<BBB", raw, start)
        width = 1 << (dimensions & 0x0F)
        height = 1 << (dimensions >> 4)
        extra_version = raw[start + 7]
        extra_length = struct.unpack_from("<I", raw, start + 8)[0]
        payload_offset = start + 8 + extra_length
        require(extra_version == 0x10 and extra_length == 12 and payload_offset <= end, "wheel G1T extra header drifted")
        expected = ((width + 3) // 4) * ((height + 3) // 4) * 16 if format_code == 0x5B else -1
        require(expected >= 0 and payload_offset + expected == end, f"wheel texture {index} BC3 payload shape drifted")
        textures.append(G1TTexture(index, start, end, payload_offset, end, width, height, format_code, packed >> 4, extra_version, extra_length))
    require((textures[0].width, textures[0].height, textures[0].format_code, textures[0].mip_count) == (2048, 2048, 0x5B, 1), "wheel primary PC texture contract drifted")
    require((textures[1].width, textures[1].height, textures[1].format_code, textures[1].mip_count) == (64, 32, 0x5B, 1), "wheel secondary PC texture contract drifted")
    return G1T(raw=raw, platform=platform, textures=tuple(textures))


def extract_switch_atlas(zip_path: Path, pin: Mapping[str, Any], label: str) -> tuple[bytes, dict[str, Any]]:
    zip_path = zip_path.resolve()
    spec = {"zip_size": zip_path.stat().st_size, "zip_sha256": sha256_file(zip_path)}
    require(spec == {"zip_size": pin["zip_size"], "zip_sha256": pin["zip_sha256"]}, f"{label} ZIP pin mismatch")
    with zipfile.ZipFile(zip_path) as archive:
        try:
            info = archive.getinfo(SWITCH_MEMBER)
        except KeyError as exc:
            raise WheelCandidateError(f"{label} has no {SWITCH_MEMBER}") from exc
        resource = archive.read(info)
    require(len(resource) == pin["member_size"] and sha256_bytes(resource) == pin["member_sha256"], f"{label} resource pin mismatch")
    outer = lz4.parse_link(resource)
    require(lz4.rebuild_link(outer) == resource and OUTER_INDEX < len(outer.entries), f"{label} outer LINK contract drifted")
    nested = parse_wheel_link(outer.entries[OUTER_INDEX].data)
    header, raw = lz4.decompress_wrapper(nested.wrapper)
    require(header.uncompressed_size == len(raw), f"{label} wheel wrapper size drifted")
    # The Switch version differs in platform and primary height, but uses the
    # same two-texture G1T node shape.  Parse the first node locally.
    require(raw[:8] == b"GT1G0600" and struct.unpack_from("<I", raw, 20)[0] == 0x10, f"{label} is not Switch G1T")
    directory_offset, count = struct.unpack_from("<II", raw, 12)
    require(directory_offset == 36 and count == 2, f"{label} Switch G1T directory drifted")
    start = directory_offset + struct.unpack_from("<I", raw, directory_offset)[0]
    next_start = directory_offset + struct.unpack_from("<I", raw, directory_offset + 4)[0]
    packed, format_code, dimensions = struct.unpack_from("<BBB", raw, start)
    extra_version = raw[start + 7]
    extra_length = struct.unpack_from("<I", raw, start + 8)[0]
    payload_offset = start + 8 + extra_length
    width = 1 << (dimensions & 0x0F)
    height = 1 << (dimensions >> 4)
    require((width, height, format_code, packed >> 4, extra_version, extra_length) == (2048, 1024, 0x5B, 1, 0x10, 12), f"{label} Switch wheel primary contract drifted")
    require(payload_offset + 2048 * 1024 == next_start, f"{label} Switch wheel primary payload drifted")
    rgba = codec.decode_bc3(raw[payload_offset:next_start], width, height)
    return rgba, {
        "zip": {"size": zip_path.stat().st_size, "sha256": sha256_file(zip_path)},
        "member": {"size": len(resource), "sha256": sha256_bytes(resource)},
        "atlas": {"width": width, "height": height, "rgba_sha256": sha256_bytes(rgba)},
    }


def cell_origin(origin: tuple[int, int], cell: int, row: int, column: int) -> tuple[int, int]:
    return origin[0] + cell * column, origin[1] + cell * row


def crop_rgba(rgba: bytes, width: int, height: int, x: int, y: int, crop_width: int, crop_height: int) -> bytes:
    require(crop_width > 0 and crop_height > 0, "invalid crop dimensions")
    output = bytearray(crop_width * crop_height * 4)
    for source_y in range(crop_height):
        yy = y + source_y
        if yy < 0 or yy >= height:
            continue
        for source_x in range(crop_width):
            xx = x + source_x
            if xx < 0 or xx >= width:
                continue
            source = (yy * width + xx) * 4
            target = (source_y * crop_width + source_x) * 4
            output[target : target + 4] = rgba[source : source + 4]
    return bytes(output)


def changed_bbox(left: bytes, right: bytes, width: int, height: int) -> tuple[int, int, int, int]:
    require(len(left) == len(right) == width * height * 4, "difference buffers do not match")
    points: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            start = (y * width + x) * 4
            if left[start : start + 4] != right[start : start + 4]:
                points.append((x, y))
    require(points, "mapped Switch sprite has no JP→KO pixel difference")
    return min(x for x, _ in points), min(y for _, y in points), max(x for x, _ in points), max(y for _, y in points)


def overwrite_rgba(target: bytearray, target_width: int, x: int, y: int, source: bytes, source_width: int, source_height: int) -> None:
    require(0 <= x <= target_width - source_width and y >= 0, "target band x range is invalid")
    target_height = len(target) // (target_width * 4)
    require(y + source_height <= target_height, "target band y range is invalid")
    for row in range(source_height):
        source_start = row * source_width * 4
        target_start = ((y + row) * target_width + x) * 4
        target[target_start : target_start + source_width * 4] = source[source_start : source_start + source_width * 4]


def is_in_any_rect(x: int, y: int, rects: Iterable[tuple[int, int, int, int]]) -> bool:
    return any(left <= x < right and top <= y < bottom for left, top, right, bottom in rects)


def require_mapping_contract() -> None:
    require(len(SPRITES) == 30, "main radial mapping must contain 30 state sprites")
    expected_labels = {"평정": 6, "임명": 6, "군사": 6, "내정": 6, "외교": 6}
    actual: dict[str, int] = {}
    sources: set[tuple[int, int]] = set()
    destinations: set[tuple[int, int]] = set()
    for row in SPRITES:
        label = row["label"]
        actual[label] = actual.get(label, 0) + 1
        source = row["source"]
        target = row["target"]
        require(isinstance(source, tuple) and isinstance(target, tuple) and len(source) == len(target) == 2, "sprite coordinate shape invalid")
        require(source not in sources, "source coordinate unexpectedly duplicated")
        require(target not in destinations, "target coordinate unexpectedly duplicated")
        sources.add(source)
        destinations.add(target)
    require(actual == expected_labels, "main radial label/state coverage changed")


def build_candidate(
    *,
    title_baseline: Path,
    switch_v20_zip: Path,
    switch_v24_zip: Path,
    output_root: Path,
) -> dict[str, Any]:
    require_mapping_contract()
    title_baseline = title_baseline.resolve()
    switch_v20_zip = switch_v20_zip.resolve()
    switch_v24_zip = switch_v24_zip.resolve()
    output_root = create_fresh_output_root(output_root)
    baseline_before = file_spec(title_baseline)
    require_spec(baseline_before, TITLE_BASELINE, "title baseline")

    switch_jp, source_v20 = extract_switch_atlas(switch_v20_zip, SWITCH_V20, "Switch v2.0")
    switch_ko, source_v24 = extract_switch_atlas(switch_v24_zip, SWITCH_V24, "Switch v2.4")

    baseline_blob = title_baseline.read_bytes()
    outer = lz4.parse_link(baseline_blob)
    require(lz4.rebuild_link(outer) == baseline_blob, "title baseline outer LINK identity failed")
    require(OUTER_INDEX < len(outer.entries), "title baseline has no /8")
    outer_before = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(outer.entries)}
    require(outer_before.get("3") is not None, "title baseline has no /3")
    wheel = parse_wheel_link(outer.entries[OUTER_INDEX].data)
    wrapper_header, raw = lz4.decompress_wrapper(wheel.wrapper)
    g1t = parse_g1t(raw)
    primary, secondary = g1t.textures
    original_primary = raw[primary.payload_offset : primary.payload_end]
    original_secondary = raw[secondary.payload_offset : secondary.payload_end]
    pc_rgba = codec.decode_bc3(original_primary, primary.width, primary.height)
    requested = bytearray(pc_rgba)

    target_rectangles: list[tuple[int, int, int, int]] = []
    rows: list[dict[str, Any]] = []
    for item in SPRITES:
        source_row, source_col = item["source"]
        target_row, target_col = item["target"]
        sx, sy = cell_origin(SWITCH_ORIGIN, SWITCH_CELL, source_row, source_col)
        tx, ty = cell_origin(PC_ORIGIN, PC_CELL, target_row, target_col)
        source_jp_cell = crop_rgba(switch_jp, 2048, 1024, sx, sy, SWITCH_CELL, SWITCH_CELL)
        source_ko_cell = crop_rgba(switch_ko, 2048, 1024, sx, sy, SWITCH_CELL, SWITCH_CELL)
        difference = changed_bbox(source_jp_cell, source_ko_cell, SWITCH_CELL, SWITCH_CELL)
        require(
            SOURCE_BAND[0] <= difference[0] <= difference[2] < SOURCE_BAND[2]
            and SOURCE_BAND[1] <= difference[1] <= difference[3] < SOURCE_BAND[3],
            f"{item['label']} state {item['state']} changes pixels outside the text band: {difference}",
        )
        source_band = crop_rgba(
            source_ko_cell,
            SWITCH_CELL,
            SWITCH_CELL,
            SOURCE_BAND[0],
            SOURCE_BAND[1],
            SOURCE_BAND[2] - SOURCE_BAND[0],
            SOURCE_BAND[3] - SOURCE_BAND[1],
        )
        resized = resize_rgba_lanczos3_premultiplied(
            source_band,
            SOURCE_BAND[2] - SOURCE_BAND[0],
            SOURCE_BAND[3] - SOURCE_BAND[1],
            TARGET_BAND[2] - TARGET_BAND[0],
            TARGET_BAND[3] - TARGET_BAND[1],
        )
        destination = (tx + TARGET_BAND[0], ty + TARGET_BAND[1], tx + TARGET_BAND[2], ty + TARGET_BAND[3])
        require(not any(destination != rectangle and not (destination[2] <= rectangle[0] or rectangle[2] <= destination[0] or destination[3] <= rectangle[1] or rectangle[3] <= destination[1]) for rectangle in target_rectangles), "target label bands overlap")
        overwrite_rgba(requested, primary.width, destination[0], destination[1], resized, destination[2] - destination[0], destination[3] - destination[1])
        target_rectangles.append(destination)
        rows.append(
            {
                "label": item["label"],
                "state": item["state"],
                "switch_source_grid": [source_row, source_col],
                "pc_target_grid": [target_row, target_col],
                "switch_jp_to_ko_difference_bbox": list(difference),
                "switch_difference_is_within_text_band": True,
                "pc_replaced_label_band": list(destination),
                "source_ko_cell_rgba_sha256": sha256_bytes(source_ko_cell),
                "resized_band_rgba_sha256": sha256_bytes(resized),
            }
        )

    # Requested pixels may differ only inside the explicit 30 label bands.
    changed_outside_requested = 0
    for pixel in range(primary.width * primary.height):
        start = pixel * 4
        if requested[start : start + 4] != pc_rgba[start : start + 4]:
            x, y = pixel % primary.width, pixel // primary.width
            if not is_in_any_rect(x, y, target_rectangles):
                changed_outside_requested += 1
    require(changed_outside_requested == 0, "requested pixel edits escaped main-wheel label bands")

    rebuilt_primary, preserved_blocks, encoded_blocks = codec.encode_bc3(
        bytes(requested), primary.width, primary.height, template_bc3=original_primary
    )
    rebuilt_raw = raw[: primary.payload_offset] + rebuilt_primary + raw[primary.payload_end :]
    rebuilt_g1t = parse_g1t(rebuilt_raw)
    require(rebuilt_raw[secondary.payload_offset : secondary.payload_end] == original_secondary, "wheel texture 1 changed")
    require(rebuilt_raw[: primary.payload_offset] == raw[: primary.payload_offset] and rebuilt_raw[primary.payload_end :] == raw[primary.payload_end :], "wheel G1T bytes outside primary BC3 changed")
    rebuilt_wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, wrapper_header)
    _, wrapper_roundtrip = lz4.decompress_wrapper(rebuilt_wrapper)
    require(wrapper_roundtrip == rebuilt_raw, "wheel LZ4 wrapper round-trip failed")
    rebuilt_nested = rebuild_wheel_link(wheel, rebuilt_wrapper)
    candidate_blob = lz4.rebuild_link(outer, {OUTER_INDEX: rebuilt_nested})

    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    atomic_write(candidate_path, candidate_blob, forbidden=(title_baseline, switch_v20_zip, switch_v24_zip))
    del candidate_blob, baseline_blob, rebuilt_primary, rebuilt_raw, rebuilt_wrapper, rebuilt_nested
    gc.collect()

    candidate_outer = lz4.parse_link(candidate_path.read_bytes())
    require(len(candidate_outer.entries) == len(outer.entries), "candidate outer LINK count changed")
    outer_after = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(candidate_outer.entries)}
    for index, before_hash in outer_before.items():
        if index != str(OUTER_INDEX):
            require(outer_after.get(index) == before_hash, f"candidate changed unrelated outer /{index}")
    require(outer_after["3"] == outer_before["3"], "candidate changed Korean title /3")
    candidate_wheel = parse_wheel_link(candidate_outer.entries[OUTER_INDEX].data)
    _, candidate_raw = lz4.decompress_wrapper(candidate_wheel.wrapper)
    candidate_g1t = parse_g1t(candidate_raw)
    candidate_primary = candidate_g1t.textures[0]
    candidate_rgba = codec.decode_bc3(candidate_raw[candidate_primary.payload_offset : candidate_primary.payload_end], 2048, 2048)
    changed_outside_bc3 = 0
    for pixel in range(2048 * 2048):
        start = pixel * 4
        if candidate_rgba[start : start + 4] != pc_rgba[start : start + 4]:
            x, y = pixel % 2048, pixel // 2048
            # BC3 re-encoding may slightly alter the whole 4x4 block.  The
            # allowed area is the union of blocks intersecting a label band.
            bx, by = x & ~3, y & ~3
            if not is_in_any_rect(bx + 1, by + 1, [(left & ~3, top & ~3, (right + 3) & ~3, (bottom + 3) & ~3) for left, top, right, bottom in target_rectangles]):
                changed_outside_bc3 += 1
    require(changed_outside_bc3 == 0, "BC3 round-trip changed pixels outside permitted label blocks")
    require(candidate_raw[candidate_g1t.textures[1].payload_offset : candidate_g1t.textures[1].payload_end] == original_secondary, "candidate texture 1 differs")

    baseline_after = file_spec(title_baseline)
    require_spec(baseline_after, TITLE_BASELINE, "title baseline after build")
    candidate_spec = file_spec(candidate_path)
    report = {
        "schema": SCHEMA,
        "file_only": True,
        "game_install_modified": False,
        "runtime_patch_features": [],
        "target_resource": TARGET_RESOURCE,
        "scope": {
            "outer_entry": OUTER_INDEX,
            "nested_slot": 0,
            "primary_texture": 0,
            "labels": ["평정", "임명", "군사", "내정", "외교"],
            "state_sprite_count": len(SPRITES),
            "all_other_wheel_pixels_requested_unchanged": True,
            "outer_3_title_byte_preserved": True,
            "wheel_texture_1_byte_preserved": True,
        },
        "inputs": {
            "title_baseline": {"before": baseline_before, "after": baseline_after, "unchanged": baseline_before == baseline_after},
            "switch_v20": source_v20,
            "switch_v24": source_v24,
        },
        "sprites": rows,
        "bc3": {
            "total_blocks": len(original_primary) // 16,
            "preserved_template_blocks": preserved_blocks,
            "deterministically_reencoded_blocks": encoded_blocks,
            "requested_changed_pixels_outside_label_bands": changed_outside_requested,
            "candidate_changed_pixels_outside_label_blocks": changed_outside_bc3,
            "original_primary_sha256": sha256_bytes(original_primary),
            "candidate_primary_sha256": sha256_bytes(candidate_raw[candidate_primary.payload_offset : candidate_primary.payload_end]),
        },
        "preservation": {
            "outer_entry_sha256_before": outer_before,
            "outer_entry_sha256_after": outer_after,
            "all_non_8_outer_entries_byte_preserved": all(outer_before[str(index)] == outer_after[str(index)] for index in range(len(outer.entries)) if index != OUTER_INDEX),
            "outer_3_title_byte_preserved": outer_before["3"] == outer_after["3"],
            "texture_1_sha256": sha256_bytes(original_secondary),
            "texture_1_byte_preserved": True,
        },
        "candidate": {"path": str(candidate_path), **candidate_spec, "under_tmp": True, "outer_parse_valid": True, "wheel_parse_valid": True, "g1t_parse_valid": True},
        "private_payload_policy": {
            "contains_complete_game_resource": True,
            "contains_third_party_translation_pixels": True,
            "git_publish_allowed": False,
            "output_must_remain_under_tmp": True,
        },
    }
    report_path = ensure_tmp(output_root / "build_report.json")
    write_json(report_path, report, forbidden=(title_baseline, switch_v20_zip, switch_v24_zip))
    return report


def verify_output(output_root: Path) -> dict[str, Any]:
    output_root = ensure_tmp(output_root, mkdir=True)
    report_path = ensure_tmp(output_root / "build_report.json")
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WheelCandidateError(f"invalid candidate report: {exc}") from exc
    require(isinstance(report, dict) and report.get("schema") == SCHEMA, "candidate report schema mismatch")
    require(report.get("file_only") is True and report.get("game_install_modified") is False, "candidate report violates file-only contract")
    candidate = report.get("candidate")
    require(isinstance(candidate, dict) and {"size": candidate.get("size"), "sha256": candidate.get("sha256")} == file_spec(candidate_path), "candidate report hash mismatch")
    outer = lz4.parse_link(candidate_path.read_bytes())
    wheel = parse_wheel_link(outer.entries[OUTER_INDEX].data)
    _, raw = lz4.decompress_wrapper(wheel.wrapper)
    parsed = parse_g1t(raw)
    require((parsed.textures[0].width, parsed.textures[0].height) == (2048, 2048), "candidate primary geometry mismatch")
    preservation = report.get("preservation")
    require(isinstance(preservation, dict) and preservation.get("outer_3_title_byte_preserved") is True and preservation.get("texture_1_byte_preserved") is True, "candidate preservation proof missing")
    before = preservation.get("outer_entry_sha256_before")
    after = preservation.get("outer_entry_sha256_after")
    require(isinstance(before, dict) and isinstance(after, dict), "outer preservation hashes missing")
    observed = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(outer.entries)}
    require(observed == after and observed.get("3") == before.get("3"), "candidate reparse preservation mismatch")
    require_mapping_contract()
    return {"candidate": file_spec(candidate_path), "game_install_modified": False, "status": "PASS"}


def add_border(rgba: bytearray, width: int, height: int, color: tuple[int, int, int, int]) -> None:
    """Mark a private contact-sheet cell without relying on image libraries."""

    for x in range(width):
        rgba[x * 4 : x * 4 + 4] = bytes(color)
        bottom = ((height - 1) * width + x) * 4
        rgba[bottom : bottom + 4] = bytes(color)
    for y in range(height):
        left = (y * width) * 4
        right = (y * width + width - 1) * 4
        rgba[left : left + 4] = bytes(color)
        rgba[right : right + 4] = bytes(color)


def paste_rgba(canvas: bytearray, canvas_width: int, x: int, y: int, source: bytes, source_width: int, source_height: int) -> None:
    for row in range(source_height):
        source_start = row * source_width * 4
        target_start = ((y + row) * canvas_width + x) * 4
        canvas[target_start : target_start + source_width * 4] = source[source_start : source_start + source_width * 4]


def visual_qa(
    *,
    title_baseline: Path,
    switch_v20_zip: Path,
    switch_v24_zip: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Write a private four-panel visual QA sheet for the 30 mapped sprites."""

    require_mapping_contract()
    output_root = ensure_tmp(output_root)
    require_spec(file_spec(title_baseline.resolve()), TITLE_BASELINE, "title baseline for visual QA")
    switch_jp, source_v20 = extract_switch_atlas(switch_v20_zip.resolve(), SWITCH_V20, "Switch v2.0")
    switch_ko, source_v24 = extract_switch_atlas(switch_v24_zip.resolve(), SWITCH_V24, "Switch v2.4")
    baseline_outer = lz4.parse_link(title_baseline.resolve().read_bytes())
    baseline_wheel = parse_wheel_link(baseline_outer.entries[OUTER_INDEX].data)
    _, baseline_raw = lz4.decompress_wrapper(baseline_wheel.wrapper)
    baseline_g1t = parse_g1t(baseline_raw)
    baseline_primary = baseline_g1t.textures[0]
    baseline_rgba = codec.decode_bc3(baseline_raw[baseline_primary.payload_offset : baseline_primary.payload_end], 2048, 2048)
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    candidate_outer = lz4.parse_link(candidate_path.read_bytes())
    candidate_wheel = parse_wheel_link(candidate_outer.entries[OUTER_INDEX].data)
    _, candidate_raw = lz4.decompress_wrapper(candidate_wheel.wrapper)
    candidate_g1t = parse_g1t(candidate_raw)
    candidate_primary = candidate_g1t.textures[0]
    candidate_rgba = codec.decode_bc3(candidate_raw[candidate_primary.payload_offset : candidate_primary.payload_end], 2048, 2048)

    gutter = 4
    panel_width = PC_CELL
    canvas_width = panel_width * 4 + gutter * 5
    canvas_height = (PC_CELL + gutter) * len(SPRITES) + gutter
    canvas = bytearray(canvas_width * canvas_height * 4)
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(SPRITES):
        source_row, source_col = item["source"]
        target_row, target_col = item["target"]
        sx, sy = cell_origin(SWITCH_ORIGIN, SWITCH_CELL, source_row, source_col)
        tx, ty = cell_origin(PC_ORIGIN, PC_CELL, target_row, target_col)
        switch_jp_cell = crop_rgba(switch_jp, 2048, 1024, sx, sy, SWITCH_CELL, SWITCH_CELL)
        switch_ko_cell = crop_rgba(switch_ko, 2048, 1024, sx, sy, SWITCH_CELL, SWITCH_CELL)
        switch_jp_panel = resize_rgba_lanczos3_premultiplied(switch_jp_cell, SWITCH_CELL, SWITCH_CELL, PC_CELL, PC_CELL)
        switch_ko_panel = resize_rgba_lanczos3_premultiplied(switch_ko_cell, SWITCH_CELL, SWITCH_CELL, PC_CELL, PC_CELL)
        pc_jp_panel = crop_rgba(baseline_rgba, 2048, 2048, tx, ty, PC_CELL, PC_CELL)
        pc_ko_panel = crop_rgba(candidate_rgba, 2048, 2048, tx, ty, PC_CELL, PC_CELL)
        local_changed: list[tuple[int, int]] = []
        allowed = (TARGET_BAND[0] & ~3, TARGET_BAND[1] & ~3, (TARGET_BAND[2] + 3) & ~3, (TARGET_BAND[3] + 3) & ~3)
        for y in range(PC_CELL):
            for x in range(PC_CELL):
                point = (y * PC_CELL + x) * 4
                if pc_jp_panel[point : point + 4] != pc_ko_panel[point : point + 4]:
                    local_changed.append((x, y))
        require(local_changed, f"visual QA has no candidate delta for {item['label']} state {item['state']}")
        require(all(allowed[0] <= x < allowed[2] and allowed[1] <= y < allowed[3] for x, y in local_changed), f"visual QA delta escapes label blocks for {item['label']} state {item['state']}")
        panels = [switch_jp_panel, switch_ko_panel, pc_jp_panel, pc_ko_panel]
        colors = [(224, 64, 64, 255), (64, 208, 96, 255), (232, 196, 56, 255), (48, 208, 232, 255)]
        y = gutter + index * (PC_CELL + gutter)
        for panel_index, (panel, color) in enumerate(zip(panels, colors)):
            marked = bytearray(panel)
            add_border(marked, PC_CELL, PC_CELL, color)
            paste_rgba(canvas, canvas_width, gutter + panel_index * (PC_CELL + gutter), y, marked, PC_CELL, PC_CELL)
        rows.append(
            {
                "label": item["label"],
                "state": item["state"],
                "switch_source_grid": [source_row, source_col],
                "pc_target_grid": [target_row, target_col],
                "panels_left_to_right": ["switch_jp", "switch_ko", "pc_jp", "pc_ko_candidate"],
                "pc_candidate_changed_pixel_count": len(local_changed),
                "pc_candidate_delta_within_expanded_label_blocks": True,
            }
        )
    png = codec.encode_rgba_png(bytes(canvas), canvas_width, canvas_height)
    contact_path = ensure_tmp(output_root / "private" / "wheel_toprows_contact_sheet.png")
    report_path = ensure_tmp(output_root / "visual_qa.json")
    atomic_write(contact_path, png, forbidden=(title_baseline.resolve(), switch_v20_zip.resolve(), switch_v24_zip.resolve(), candidate_path))
    report = {
        "schema": "nobu16.kr.steam-jp-wheel-toprows.visual-qa.v1",
        "file_only": True,
        "game_install_modified": False,
        "contact_sheet": {
            "path": str(contact_path),
            "sha256": sha256_bytes(png),
            "dimensions": [canvas_width, canvas_height],
            "private_only": True,
            "panel_legend": {"red": "Switch JP", "green": "Switch KO", "yellow": "PC JP baseline", "cyan": "PC KO candidate"},
        },
        "inputs": {"switch_v20": source_v20, "switch_v24": source_v24, "title_baseline": TITLE_BASELINE, "candidate": file_spec(candidate_path)},
        "sprites": rows,
        "all_30_candidate_deltas_within_expanded_label_blocks": True,
    }
    write_json(report_path, report, forbidden=(title_baseline.resolve(), switch_v20_zip.resolve(), switch_v24_zip.resolve(), candidate_path))
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="write the private top-row wheel candidate below tmp")
    build.add_argument("--title-baseline", type=Path, required=True)
    build.add_argument("--switch-v20-zip", type=Path, required=True)
    build.add_argument("--switch-v24-zip", type=Path, required=True)
    build.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_wheel_toprows_v1" / "final")
    verify = sub.add_parser("verify", help="reparse a candidate already under tmp")
    verify.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_wheel_toprows_v1" / "final")
    visual = sub.add_parser("visual-qa", help="write a private four-panel QA contact sheet below an existing output root")
    visual.add_argument("--title-baseline", type=Path, required=True)
    visual.add_argument("--switch-v20-zip", type=Path, required=True)
    visual.add_argument("--switch-v24-zip", type=Path, required=True)
    visual.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_wheel_toprows_v1" / "final")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "build":
            result = build_candidate(
                title_baseline=args.title_baseline,
                switch_v20_zip=args.switch_v20_zip,
                switch_v24_zip=args.switch_v24_zip,
                output_root=args.output_root,
            )
        elif args.command == "verify":
            result = verify_output(args.output_root)
        else:
            result = visual_qa(
                title_baseline=args.title_baseline,
                switch_v20_zip=args.switch_v20_zip,
                switch_v24_zip=args.switch_v24_zip,
                output_root=args.output_root,
            )
    except (OSError, WheelCandidateError, lz4.LZ4Error, lz4.LinkError, codec.CodecError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result.get("candidate", result), ensure_ascii=False, sort_keys=True))
    print("game_install_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
