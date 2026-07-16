#!/usr/bin/env python3
"""Build a private PC-native Korean candidate for nine battle-start banners.

The supported path is deliberately narrow::

    Steam JP 1.1.7 v0.9 baseline RES_JP/res_lang.bin
      /13 (one-slot LINK bundle)
        /0 (raw-LZ4 wrapped 57-texture PC G1T)
          textures 48..56 (2048x256 BC3)

Only the nine battle-start banner textures are reconstructed.  The Switch
v2.1/v2.2 archives are decoded in memory solely to establish the Korean
visual delta and coordinate mapping.  No Switch LINK, LZ4, G1T, BC3, archive,
or decoded image is copied into the candidate.  The candidate is rebuilt in
the PC G1T/BC3/LZ4 structure and written only beneath the ignored ``tmp``
directory.

This program never writes a game installation, executable, DLL, registry,
process memory, or a release artifact.  Screen QA remains a separate gate.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
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
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as codec  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-battle-banners.candidate.v1"
TARGET_RESOURCE = "RES_JP/res_lang.bin"
OUTER_INDEX = 13
NESTED_RESOURCE_ID = 79
NESTED_SLOT = 0
TARGET_TEXTURES = tuple(range(48, 57))
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
PC_WIDTH = 2048
PC_HEIGHT = 256
SWITCH_WIDTH = 2048
SWITCH_HEIGHT = 128
SOURCE_PADDING = 4
SCALE_NUMERATOR = 3
SCALE_DENOMINATOR = 2

# The source is a restored Steam 1.1.7 v0.9 resource, not the currently
# title/wheel-modified live file.  Its hash is part of the candidate contract.
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

# Korean labels are public translation metadata.  No Japanese source text,
# source pixels, or source coordinates are committed into this workstream.
BANNERS: tuple[tuple[int, str], ...] = (
    (48, "오케하자마 전투"),
    (49, "나가시노 전투"),
    (50, "미카타가하라 전투"),
    (51, "히에이잔 방화"),
    (52, "가네가사키 철퇴전"),
    (53, "기초 훈련"),
    (54, "젠토쿠지 회맹"),
    (55, "이쓰쿠시마 전투"),
    (56, "가와나카지마 전투"),
)


class BannerCandidateError(ValueError):
    """The constrained battle-banner candidate contract was violated."""


@dataclass(frozen=True)
class BannerLink:
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
        raise BannerCandidateError(message)


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


def require_spec(actual: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    require(
        actual.get("size") == expected.get("size")
        and actual.get("sha256") == expected.get("sha256"),
        f"{label} pin mismatch: expected={dict(expected)} actual={dict(actual)}",
    )


def is_reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT) or path.is_symlink() or path.is_junction()
    except OSError:
        return True


def lexical_tmp_path(path: Path) -> tuple[Path, Path]:
    """Reject an escape before creating any output directory."""

    tmp_lexical = Path(os.path.abspath(TMP_ROOT))
    candidate = Path(os.path.abspath(Path(path)))
    try:
        common = os.path.commonpath((os.path.normcase(str(tmp_lexical)), os.path.normcase(str(candidate))))
    except ValueError as exc:
        raise BannerCandidateError(f"output has incompatible drive: {candidate}") from exc
    if common != os.path.normcase(str(tmp_lexical)):
        raise BannerCandidateError(f"output lexically escapes tmp: {candidate}")
    try:
        candidate.relative_to(tmp_lexical)
    except ValueError as exc:
        raise BannerCandidateError(f"output lexically escapes tmp: {candidate}") from exc
    return tmp_lexical, candidate


def ensure_tmp(path: Path, *, mkdir: bool = False) -> Path:
    """Return a checked ordinary path below ``tmp``.

    The lexical root is checked for a reparse point before ``resolve``.  That
    prevents a junction at the tmp root from being followed before the guard.
    """

    tmp_lexical, candidate = lexical_tmp_path(path)
    if is_reparse(tmp_lexical):
        raise BannerCandidateError(f"tmp root is a reparse point: {tmp_lexical}")
    tmp = tmp_lexical.resolve()
    if is_reparse(tmp):
        raise BannerCandidateError(f"resolved tmp root is a reparse point: {tmp}")
    relative = candidate.relative_to(tmp_lexical)
    current = tmp
    for part in relative.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if is_reparse(current):
                raise BannerCandidateError(f"reparse point is forbidden in output path: {current}")
            resolved = current.resolve()
            try:
                resolved.relative_to(tmp)
            except ValueError as exc:
                raise BannerCandidateError(f"existing output component escapes tmp: {current}") from exc
            current = resolved
        elif mkdir:
            current.mkdir(exist_ok=False)
            if is_reparse(current):
                raise BannerCandidateError(f"new output component is a reparse point: {current}")
    return current


def create_fresh_output_root(path: Path) -> Path:
    raw = Path(path)
    parent = ensure_tmp(raw.parent, mkdir=True)
    candidate = parent / raw.name
    if candidate.exists() or candidate.is_symlink():
        raise BannerCandidateError(f"output root already exists: {candidate}")
    candidate.mkdir(exist_ok=False)
    return ensure_tmp(candidate)


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    path = ensure_tmp(path.parent, mkdir=True) / path.name
    path = ensure_tmp(path)
    for source in forbidden:
        if path == source.resolve():
            raise BannerCandidateError(f"refusing to overwrite input: {source}")
    if path.exists() or path.is_symlink():
        raise BannerCandidateError(f"refusing to overwrite existing output: {path}")
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if is_reparse(path.parent):
            raise BannerCandidateError(f"output parent became reparse point: {path.parent}")
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


def parse_banner_link(blob: bytes) -> BannerLink:
    """Parse the exact one-slot 32-byte LINK layout used by outer ``/13``."""

    require(len(blob) >= 64 and blob[:4] == b"LINK", "battle-banner /13 is not LINK")
    count, table_offset, resource_id, aligned_end = struct.unpack_from("<4I", blob, 4)
    require(count == 1 and table_offset == 32, "battle-banner nested LINK shape drifted")
    require(resource_id == NESTED_RESOURCE_ID, "battle-banner nested resource id drifted")
    require(blob[20:32] == b"\0" * 12, "battle-banner nested LINK extension drifted")
    table_end = table_offset + count * 8
    require(aligned_end == 64 and aligned_end >= table_end, "battle-banner nested LINK alignment drifted")
    slot_offset, stored_size = struct.unpack_from("<II", blob, table_offset)
    require(slot_offset >= aligned_end and slot_offset + stored_size <= len(blob), "battle-banner slot range invalid")
    return BannerLink(
        fixed_header=blob[:table_offset],
        table_offset=table_offset,
        resource_id=resource_id,
        pre_slot=blob[table_end:slot_offset],
        wrapper=blob[slot_offset : slot_offset + stored_size],
        tail=blob[slot_offset + stored_size :],
        slot_offset=slot_offset,
    )


def rebuild_banner_link(link: BannerLink, wrapper: bytes) -> bytes:
    output = bytearray(link.fixed_header)
    output.extend(b"\0" * 8)
    output.extend(link.pre_slot)
    require(len(output) == link.slot_offset, "battle-banner nested LINK pre-slot placement drifted")
    struct.pack_into("<II", output, link.table_offset, len(output), len(wrapper))
    output.extend(wrapper)
    output.extend(link.tail)
    rebuilt = bytes(output)
    parsed = parse_banner_link(rebuilt)
    require(parsed.wrapper == wrapper, "battle-banner wrapper re-extraction failed")
    require(parsed.pre_slot == link.pre_slot and parsed.tail == link.tail, "battle-banner surrounding bytes changed")
    return rebuilt


def bc3_size(width: int, height: int) -> int:
    return ((width + 3) // 4) * ((height + 3) // 4) * 16


def parse_g1t(raw: bytes, *, expected_platform: int, expected_height: int) -> G1T:
    """Parse the observed 57-texture PC/Switch battle-banner G1T layout."""

    require(len(raw) >= 32 and raw[:8] == b"GT1G0600", "battle-banner raw is not GT1G0600")
    declared_size, directory_offset, count, platform = struct.unpack_from("<4I", raw, 8)
    require(declared_size == len(raw), "battle-banner G1T declared size mismatch")
    # Unlike the two-texture command wheel, this 57-texture bundle reserves a
    # 0x100-byte G1T header/directory region.  Treat that PC/Switch topology
    # as an exact contract rather than assuming the smaller wheel layout.
    require(directory_offset == 0x100 and count == 57 and platform == expected_platform, "battle-banner G1T topology drifted")
    directory_end = directory_offset + count * 4
    require(directory_end <= len(raw), "battle-banner G1T directory exceeds raw")
    starts = [directory_offset + struct.unpack_from("<I", raw, directory_offset + index * 4)[0] for index in range(count)]
    require(starts == sorted(starts) and starts[0] >= directory_end and starts[-1] < len(raw), "battle-banner G1T offsets invalid")
    textures: list[G1TTexture] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < count else len(raw)
        require(end - start >= 20, f"battle-banner G1T texture {index} truncated")
        packed, format_code, dimensions = struct.unpack_from("<BBB", raw, start)
        width = 1 << (dimensions & 0x0F)
        height = 1 << (dimensions >> 4)
        extra_version = raw[start + 7]
        extra_length = struct.unpack_from("<I", raw, start + 8)[0]
        payload_offset = start + 8 + extra_length
        require(extra_version == 0x10 and extra_length == 12 and payload_offset <= end, f"battle-banner G1T texture {index} extra header drifted")
        payload_end = payload_offset + (bc3_size(width, height) if format_code == 0x5B else 0)
        if index in TARGET_TEXTURES:
            require(
                (width, height, format_code, packed >> 4, extra_version, extra_length) == (PC_WIDTH, expected_height, 0x5B, 1, 0x10, 12),
                f"battle-banner texture {index} contract drifted",
            )
            require(payload_end == end, f"battle-banner texture {index} BC3 payload shape drifted")
        textures.append(
            G1TTexture(index, start, end, payload_offset, payload_end, width, height, format_code, packed >> 4, extra_version, extra_length)
        )
    return G1T(raw=raw, platform=platform, textures=tuple(textures))


def texture_by_index(g1t: G1T, index: int) -> G1TTexture:
    try:
        texture = g1t.textures[index]
    except IndexError as exc:
        raise BannerCandidateError(f"battle-banner texture {index} is absent") from exc
    require(texture.index == index, f"battle-banner texture ordering drifted at {index}")
    return texture


def extract_switch_textures(zip_path: Path, pin: Mapping[str, Any], label: str) -> tuple[dict[int, bytes], dict[str, Any]]:
    """Decode only the nine source textures into memory after exact pin checks."""

    zip_path = zip_path.resolve()
    archive_spec = {"zip_size": zip_path.stat().st_size, "zip_sha256": sha256_file(zip_path)}
    require(
        archive_spec == {"zip_size": pin["zip_size"], "zip_sha256": pin["zip_sha256"]},
        f"{label} ZIP pin mismatch",
    )
    with zipfile.ZipFile(zip_path) as archive:
        try:
            info = archive.getinfo(SWITCH_MEMBER)
        except KeyError as exc:
            raise BannerCandidateError(f"{label} has no {SWITCH_MEMBER}") from exc
        require(info.file_size == pin["member_size"], f"{label} member size pin mismatch")
        resource = archive.read(info)
    require(sha256_bytes(resource) == pin["member_sha256"], f"{label} member pin mismatch")
    outer = lz4.parse_link(resource)
    require(lz4.rebuild_link(outer) == resource and OUTER_INDEX < len(outer.entries), f"{label} outer LINK contract drifted")
    nested = parse_banner_link(outer.entries[OUTER_INDEX].data)
    wrapper_header, raw = lz4.decompress_wrapper(nested.wrapper)
    require(wrapper_header.uncompressed_size == len(raw), f"{label} wrapper size drifted")
    g1t = parse_g1t(raw, expected_platform=0x10, expected_height=SWITCH_HEIGHT)
    decoded: dict[int, bytes] = {}
    for index in TARGET_TEXTURES:
        texture = texture_by_index(g1t, index)
        decoded[index] = codec.decode_bc3(raw[texture.payload_offset : texture.payload_end], texture.width, texture.height)
    metadata = {
        "zip": {"size": zip_path.stat().st_size, "sha256": sha256_file(zip_path)},
        "member": {"size": len(resource), "sha256": sha256_bytes(resource)},
        "outer_entry": OUTER_INDEX,
        "nested_slot": NESTED_SLOT,
        "texture_geometry": [SWITCH_WIDTH, SWITCH_HEIGHT, "BC3"],
        "decoded_texture_rgba_sha256": {str(index): sha256_bytes(decoded[index]) for index in TARGET_TEXTURES},
    }
    del resource, raw
    return decoded, metadata


def changed_bbox(left: bytes, right: bytes, width: int, height: int) -> tuple[int, int, int, int]:
    require(len(left) == len(right) == width * height * 4, "difference buffers do not match")
    min_x = width
    min_y = height
    max_x = -1
    max_y = -1
    for y in range(height):
        for x in range(width):
            pos = (y * width + x) * 4
            if (
                left[pos] != right[pos]
                or left[pos + 1] != right[pos + 1]
                or left[pos + 2] != right[pos + 2]
                or left[pos + 3] != right[pos + 3]
            ):
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    require(max_x >= min_x and max_y >= min_y, "Switch JP/Korean banner pair has no visual delta")
    return min_x, min_y, max_x, max_y


def alpha_bbox(rgba: bytes, width: int, height: int) -> tuple[int, int, int, int]:
    require(len(rgba) == width * height * 4, "alpha-bbox buffer size mismatch")
    min_x = width
    min_y = height
    max_x = -1
    max_y = -1
    for y in range(height):
        for x in range(width):
            if rgba[(y * width + x) * 4 + 3]:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    require(max_x >= min_x and max_y >= min_y, "battle-banner texture has no visible pixels")
    return min_x, min_y, max_x, max_y


def expand_rect(rect: tuple[int, int, int, int], padding: int, width: int, height: int) -> tuple[int, int, int, int]:
    """Turn an inclusive bounding box into a padded half-open rectangle."""

    left, top, right, bottom = rect
    require(0 <= left <= right < width and 0 <= top <= bottom < height, "bounding box is outside source")
    return max(0, left - padding), max(0, top - padding), min(width, right + 1 + padding), min(height, bottom + 1 + padding)


def source_to_pc_rect(rect: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Map a half-open Switch label rectangle to the measured PC grid.

    The Switch and PC banner canvases differ in height, but their visible
    Japanese title regions map at exactly 3:2 in both axes.  The PC canvas
    keeps the resulting lower transparent area; it is not stretched to 256px.
    """

    left, top, right, bottom = rect
    result = (
        left * SCALE_NUMERATOR // SCALE_DENOMINATOR,
        top * SCALE_NUMERATOR // SCALE_DENOMINATOR,
        (right * SCALE_NUMERATOR + SCALE_DENOMINATOR - 1) // SCALE_DENOMINATOR,
        (bottom * SCALE_NUMERATOR + SCALE_DENOMINATOR - 1) // SCALE_DENOMINATOR,
    )
    require(0 <= result[0] < result[2] <= PC_WIDTH and 0 <= result[1] < result[3] <= PC_HEIGHT, f"mapped PC label rectangle is outside canvas: {result}")
    return result


def contains_rect(outer: tuple[int, int, int, int], inner: tuple[int, int, int, int]) -> bool:
    return outer[0] <= inner[0] and outer[1] <= inner[1] and inner[2] <= outer[2] and inner[3] <= outer[3]


def crop_rgba(rgba: bytes, width: int, rect: tuple[int, int, int, int]) -> bytes:
    left, top, right, bottom = rect
    height = len(rgba) // (width * 4)
    require(0 <= left < right <= width and 0 <= top < bottom <= height, "RGBA crop is outside image")
    output = bytearray((right - left) * (bottom - top) * 4)
    for row in range(bottom - top):
        source_start = ((top + row) * width + left) * 4
        target_start = row * (right - left) * 4
        output[target_start : target_start + (right - left) * 4] = rgba[source_start : source_start + (right - left) * 4]
    return bytes(output)


def overwrite_rgba(target: bytearray, width: int, rect: tuple[int, int, int, int], source: bytes) -> None:
    left, top, right, bottom = rect
    height = len(target) // (width * 4)
    patch_width = right - left
    patch_height = bottom - top
    require(0 <= left < right <= width and 0 <= top < bottom <= height, "target patch is outside image")
    require(len(source) == patch_width * patch_height * 4, "target patch size mismatch")
    for row in range(patch_height):
        source_start = row * patch_width * 4
        target_start = ((top + row) * width + left) * 4
        target[target_start : target_start + patch_width * 4] = source[source_start : source_start + patch_width * 4]


def pixel_changes_outside(left: bytes, right: bytes, width: int, allowed: tuple[int, int, int, int]) -> int:
    require(len(left) == len(right), "pixel comparison buffer sizes differ")
    count = 0
    left_x, top_y, right_x, bottom_y = allowed
    for pixel in range(len(left) // 4):
        start = pixel * 4
        if left[start : start + 4] != right[start : start + 4]:
            x = pixel % width
            y = pixel // width
            if not (left_x <= x < right_x and top_y <= y < bottom_y):
                count += 1
    return count


def expanded_block_rect(rect: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return rect[0] & ~3, rect[1] & ~3, min(PC_WIDTH, (rect[2] + 3) & ~3), min(PC_HEIGHT, (rect[3] + 3) & ~3)


def _sinc(value: float) -> float:
    if abs(value) < 1e-12:
        return 1.0
    value *= math.pi
    return math.sin(value) / value


def _lanczos3(value: float) -> float:
    if abs(value) >= 3.0:
        return 0.0
    return _sinc(value) * _sinc(value / 3.0)


def _resample_contributions(source_size: int, target_size: int) -> list[list[tuple[int, float]]]:
    require(source_size > 0 and target_size > 0, "invalid resize dimensions")
    scale = source_size / target_size
    rows: list[list[tuple[int, float]]] = []
    for target in range(target_size):
        source_position = (target + 0.5) * scale - 0.5
        first = math.floor(source_position) - 2
        weighted: list[tuple[int, float]] = []
        total = 0.0
        for source in range(first, first + 6):
            if 0 <= source < source_size:
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


def resize_rgba_lanczos3_premultiplied(source: bytes, source_width: int, source_height: int, target_width: int, target_height: int) -> bytes:
    """Deterministically resize a label patch in premultiplied-alpha space."""

    require(len(source) == source_width * source_height * 4, "resize source RGBA length mismatch")
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


def decode_pc_baseline(path: Path) -> tuple[lz4.LinkArchive, BannerLink, lz4.WrapperHeader, bytes, G1T]:
    path = path.resolve()
    require_spec(file_spec(path), BASELINE, "Steam JP v0.9 baseline")
    outer_blob = path.read_bytes()
    outer = lz4.parse_link(outer_blob)
    require(lz4.rebuild_link(outer) == outer_blob and OUTER_INDEX < len(outer.entries), "baseline outer LINK identity failed")
    nested = parse_banner_link(outer.entries[OUTER_INDEX].data)
    wrapper_header, raw = lz4.decompress_wrapper(nested.wrapper)
    require(wrapper_header.uncompressed_size == len(raw), "baseline banner wrapper size drifted")
    g1t = parse_g1t(raw, expected_platform=0x0A, expected_height=PC_HEIGHT)
    return outer, nested, wrapper_header, raw, g1t


def unchanged_outside_selected(before: bytes, after: bytes, g1t: G1T) -> bool:
    """Ensure G1T headers and all non-target texture bytes are unchanged."""

    require(len(before) == len(after), "battle-banner G1T size changed")
    cursor = 0
    for index in TARGET_TEXTURES:
        texture = texture_by_index(g1t, index)
        if before[cursor : texture.payload_offset] != after[cursor : texture.payload_offset]:
            return False
        cursor = texture.payload_end
    return before[cursor:] == after[cursor:]


def build_candidate(*, baseline: Path, switch_v21_zip: Path, switch_v22_zip: Path, output_root: Path) -> dict[str, Any]:
    """Write a one-off candidate beneath ``tmp`` after all input gates pass."""

    baseline = baseline.resolve()
    switch_v21_zip = switch_v21_zip.resolve()
    switch_v22_zip = switch_v22_zip.resolve()
    output_root = create_fresh_output_root(output_root)
    baseline_before = file_spec(baseline)
    require_spec(baseline_before, BASELINE, "Steam JP v0.9 baseline")
    switch_jp, source_v21 = extract_switch_textures(switch_v21_zip, SWITCH_V21, "Switch v2.1")
    switch_ko, source_v22 = extract_switch_textures(switch_v22_zip, SWITCH_V22, "Switch v2.2")
    outer, nested, wrapper_header, raw, g1t = decode_pc_baseline(baseline)
    outer_before = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(outer.entries)}
    requested_raw = bytearray(raw)
    per_banner: list[dict[str, Any]] = []
    per_bc3: list[dict[str, Any]] = []

    for index, label in BANNERS:
        texture = texture_by_index(g1t, index)
        pc_payload = raw[texture.payload_offset : texture.payload_end]
        pc_rgba = codec.decode_bc3(pc_payload, PC_WIDTH, PC_HEIGHT)
        switch_difference = changed_bbox(switch_jp[index], switch_ko[index], SWITCH_WIDTH, SWITCH_HEIGHT)
        switch_korean_alpha = alpha_bbox(switch_ko[index], SWITCH_WIDTH, SWITCH_HEIGHT)
        pc_japanese_alpha = alpha_bbox(pc_rgba, PC_WIDTH, PC_HEIGHT)
        require(
            switch_difference[0] <= switch_korean_alpha[0] <= switch_korean_alpha[2] <= switch_difference[2]
            and switch_difference[1] <= switch_korean_alpha[1] <= switch_korean_alpha[3] <= switch_difference[3],
            f"texture {index}: Korean source pixels escape Switch delta",
        )
        source_patch = expand_rect(switch_difference, SOURCE_PADDING, SWITCH_WIDTH, SWITCH_HEIGHT)
        target_patch = source_to_pc_rect(source_patch)
        pc_alpha_half_open = (pc_japanese_alpha[0], pc_japanese_alpha[1], pc_japanese_alpha[2] + 1, pc_japanese_alpha[3] + 1)
        require(contains_rect(target_patch, pc_alpha_half_open), f"texture {index}: PC Japanese banner escapes mapped patch")
        source = crop_rgba(switch_ko[index], SWITCH_WIDTH, source_patch)
        target_width = target_patch[2] - target_patch[0]
        target_height = target_patch[3] - target_patch[1]
        resized = resize_rgba_lanczos3_premultiplied(source, source_patch[2] - source_patch[0], source_patch[3] - source_patch[1], target_width, target_height)
        requested = bytearray(pc_rgba)
        overwrite_rgba(requested, PC_WIDTH, target_patch, resized)
        requested_outside = pixel_changes_outside(pc_rgba, bytes(requested), PC_WIDTH, target_patch)
        require(requested_outside == 0, f"texture {index}: requested pixels escaped mapped patch")
        rebuilt_bc3, preserved_blocks, encoded_blocks = codec.encode_bc3(bytes(requested), PC_WIDTH, PC_HEIGHT, template_bc3=pc_payload)
        requested_raw[texture.payload_offset : texture.payload_end] = rebuilt_bc3
        per_banner.append(
            {
                "texture": index,
                "label": label,
                "switch_jp_to_ko_difference_bbox": list(switch_difference),
                "switch_korean_alpha_bbox": list(switch_korean_alpha),
                "pc_japanese_alpha_bbox": list(pc_japanese_alpha),
                "switch_source_patch": list(source_patch),
                "pc_target_patch": list(target_patch),
                "pc_target_expanded_bc3_block_patch": list(expanded_block_rect(target_patch)),
                "switch_to_pc_coordinate_scale": [SCALE_NUMERATOR, SCALE_DENOMINATOR],
                "requested_changed_pixels_outside_target_patch": requested_outside,
                "source_patch_rgba_sha256": sha256_bytes(source),
                "resized_pc_patch_rgba_sha256": sha256_bytes(resized),
            }
        )
        per_bc3.append(
            {
                "texture": index,
                "total_blocks": len(pc_payload) // 16,
                "preserved_template_blocks": preserved_blocks,
                "deterministically_reencoded_blocks": encoded_blocks,
                "original_payload_sha256": sha256_bytes(pc_payload),
                "candidate_payload_sha256": sha256_bytes(rebuilt_bc3),
            }
        )

    rebuilt_raw = bytes(requested_raw)
    require(unchanged_outside_selected(raw, rebuilt_raw, g1t), "G1T bytes outside selected banner payloads changed")
    rebuilt_g1t = parse_g1t(rebuilt_raw, expected_platform=0x0A, expected_height=PC_HEIGHT)
    for index in TARGET_TEXTURES:
        original_texture = texture_by_index(g1t, index)
        candidate_texture = texture_by_index(rebuilt_g1t, index)
        require(
            (candidate_texture.width, candidate_texture.height, candidate_texture.format_code, candidate_texture.mip_count)
            == (original_texture.width, original_texture.height, original_texture.format_code, original_texture.mip_count),
            f"texture {index}: candidate geometry changed",
        )
    rebuilt_wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, wrapper_header)
    _, wrapper_roundtrip = lz4.decompress_wrapper(rebuilt_wrapper)
    require(wrapper_roundtrip == rebuilt_raw, "battle-banner LZ4 wrapper round-trip failed")
    rebuilt_nested = rebuild_banner_link(nested, rebuilt_wrapper)
    candidate_blob = lz4.rebuild_link(outer, {OUTER_INDEX: rebuilt_nested})
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    atomic_write(candidate_path, candidate_blob, forbidden=(baseline, switch_v21_zip, switch_v22_zip))

    candidate_outer = lz4.parse_link(candidate_path.read_bytes())
    require(len(candidate_outer.entries) == len(outer.entries), "candidate outer LINK count changed")
    outer_after = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(candidate_outer.entries)}
    for index, before_hash in outer_before.items():
        if index != str(OUTER_INDEX):
            require(outer_after.get(index) == before_hash, f"candidate changed unrelated outer /{index}")
    candidate_nested = parse_banner_link(candidate_outer.entries[OUTER_INDEX].data)
    _, candidate_raw = lz4.decompress_wrapper(candidate_nested.wrapper)
    candidate_g1t = parse_g1t(candidate_raw, expected_platform=0x0A, expected_height=PC_HEIGHT)
    require(unchanged_outside_selected(raw, candidate_raw, g1t), "candidate G1T bytes outside selected banner payloads changed")
    candidate_delta_rows: list[dict[str, Any]] = []
    for row in per_banner:
        index = int(row["texture"])
        original_texture = texture_by_index(g1t, index)
        candidate_texture = texture_by_index(candidate_g1t, index)
        pc_rgba = codec.decode_bc3(raw[original_texture.payload_offset : original_texture.payload_end], PC_WIDTH, PC_HEIGHT)
        candidate_rgba = codec.decode_bc3(candidate_raw[candidate_texture.payload_offset : candidate_texture.payload_end], PC_WIDTH, PC_HEIGHT)
        allowed = tuple(int(value) for value in row["pc_target_expanded_bc3_block_patch"])
        outside = pixel_changes_outside(pc_rgba, candidate_rgba, PC_WIDTH, allowed)
        require(outside == 0, f"texture {index}: BC3 candidate pixels escaped allowed blocks")
        require(pc_rgba != candidate_rgba, f"texture {index}: candidate has no visual delta")
        candidate_delta_rows.append({"texture": index, "candidate_changed_pixels_outside_expanded_bc3_patch": outside})

    baseline_after = file_spec(baseline)
    require_spec(baseline_after, BASELINE, "Steam JP v0.9 baseline after build")
    candidate_spec = file_spec(candidate_path)
    report = {
        "schema": SCHEMA,
        "file_only": True,
        "game_install_modified": False,
        "runtime_patch_features": [],
        "target_resource": TARGET_RESOURCE,
        "scope": {
            "outer_entry": OUTER_INDEX,
            "nested_slot": NESTED_SLOT,
            "textures": list(TARGET_TEXTURES),
            "texture_geometry": [PC_WIDTH, PC_HEIGHT, "BC3"],
            "logo_or_title_art_touched": False,
        },
        "inputs": {
            "baseline": {"before": baseline_before, "after": baseline_after, "unchanged": baseline_before == baseline_after},
            "switch_v21": source_v21,
            "switch_v22": source_v22,
        },
        "banners": per_banner,
        "bc3": per_bc3,
        "candidate_delta": candidate_delta_rows,
        "preservation": {
            "outer_entry_sha256_before": outer_before,
            "outer_entry_sha256_after": outer_after,
            "all_non_13_outer_entries_byte_preserved": all(outer_before[str(index)] == outer_after[str(index)] for index in range(len(outer.entries)) if index != OUTER_INDEX),
            "nested_resource_id": NESTED_RESOURCE_ID,
            "all_nonselected_g1t_bytes_byte_preserved": True,
            "all_nine_texture_geometries_preserved": True,
            "lz4_roundtrip": True,
        },
        "candidate": {
            "path": str(candidate_path),
            **candidate_spec,
            "under_tmp": True,
            "outer_parse_valid": True,
            "banner_link_parse_valid": True,
            "g1t_parse_valid": True,
        },
        "screen_qa_required_before_apply": True,
        "private_payload_policy": {
            "contains_complete_game_resource": True,
            "contains_third_party_translation_pixels": True,
            "git_publish_allowed": False,
            "output_must_remain_under_tmp": True,
        },
    }
    report_path = ensure_tmp(output_root / "build_report.json")
    write_json(report_path, report, forbidden=(baseline, switch_v21_zip, switch_v22_zip, candidate_path))
    del candidate_blob, rebuilt_raw, rebuilt_wrapper, rebuilt_nested, raw, candidate_raw
    gc.collect()
    return report


def verify_output(*, baseline: Path, output_root: Path) -> dict[str, Any]:
    """Reparse a private candidate and reprove its exact preservation scope."""

    baseline = baseline.resolve()
    output_root = ensure_tmp(output_root)
    require(output_root.is_dir(), f"candidate output root does not exist: {output_root}")
    report_path = ensure_tmp(output_root / "build_report.json")
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BannerCandidateError(f"invalid candidate report: {exc}") from exc
    require(isinstance(report, dict) and report.get("schema") == SCHEMA, "candidate report schema mismatch")
    require(report.get("file_only") is True and report.get("game_install_modified") is False, "candidate report violates file-only contract")
    candidate = report.get("candidate")
    require(isinstance(candidate, dict) and {"size": candidate.get("size"), "sha256": candidate.get("sha256")} == file_spec(candidate_path), "candidate report hash mismatch")
    baseline_outer, _, _, baseline_raw, baseline_g1t = decode_pc_baseline(baseline)
    candidate_outer = lz4.parse_link(candidate_path.read_bytes())
    require(len(candidate_outer.entries) == len(baseline_outer.entries), "candidate outer entry count differs from baseline")
    before = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(baseline_outer.entries)}
    after = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(candidate_outer.entries)}
    require(all(before[str(index)] == after[str(index)] for index in range(len(baseline_outer.entries)) if index != OUTER_INDEX), "candidate changed unrelated outer entry")
    candidate_nested = parse_banner_link(candidate_outer.entries[OUTER_INDEX].data)
    _, candidate_raw = lz4.decompress_wrapper(candidate_nested.wrapper)
    candidate_g1t = parse_g1t(candidate_raw, expected_platform=0x0A, expected_height=PC_HEIGHT)
    require(unchanged_outside_selected(baseline_raw, candidate_raw, baseline_g1t), "candidate changed G1T bytes outside nine banner payloads")
    for index in TARGET_TEXTURES:
        original = texture_by_index(baseline_g1t, index)
        rebuilt = texture_by_index(candidate_g1t, index)
        require(
            (rebuilt.width, rebuilt.height, rebuilt.format_code, rebuilt.mip_count)
            == (original.width, original.height, original.format_code, original.mip_count),
            f"candidate texture geometry drifted at {index}",
        )
    preservation = report.get("preservation")
    require(isinstance(preservation, dict), "candidate preservation report missing")
    require(preservation.get("outer_entry_sha256_before") == before and preservation.get("outer_entry_sha256_after") == after, "candidate outer preservation report mismatch")
    require(preservation.get("all_non_13_outer_entries_byte_preserved") is True, "candidate outer preservation flag missing")
    require(preservation.get("all_nonselected_g1t_bytes_byte_preserved") is True, "candidate G1T preservation flag missing")
    return {"candidate": file_spec(candidate_path), "game_install_modified": False, "status": "PASS"}


def composite_checker(rgba: bytes, width: int, height: int) -> bytes:
    output = bytearray(len(rgba))
    for y in range(height):
        for x in range(width):
            source = (y * width + x) * 4
            alpha = rgba[source + 3]
            background = 42 if ((x // 8) ^ (y // 8)) & 1 else 26
            for channel in range(3):
                value = rgba[source + channel]
                output[source + channel] = (value * alpha + background * (255 - alpha) + 127) // 255
            output[source + 3] = 255
    return bytes(output)


def nearest_resize(rgba: bytes, width: int, height: int, target_width: int, target_height: int) -> bytes:
    output = bytearray(target_width * target_height * 4)
    for y in range(target_height):
        source_y = min(height - 1, y * height // target_height)
        for x in range(target_width):
            source_x = min(width - 1, x * width // target_width)
            source = (source_y * width + source_x) * 4
            target = (y * target_width + x) * 4
            output[target : target + 4] = rgba[source : source + 4]
    return bytes(output)


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


def paste_rgba(canvas: bytearray, canvas_width: int, x: int, y: int, source: bytes, source_width: int, source_height: int) -> None:
    for row in range(source_height):
        source_start = row * source_width * 4
        target_start = ((y + row) * canvas_width + x) * 4
        canvas[target_start : target_start + source_width * 4] = source[source_start : source_start + source_width * 4]


def visual_qa(*, baseline: Path, switch_v21_zip: Path, switch_v22_zip: Path, output_root: Path) -> dict[str, Any]:
    """Write a private four-panel contact sheet for the nine banner pairs."""

    baseline = baseline.resolve()
    switch_v21_zip = switch_v21_zip.resolve()
    switch_v22_zip = switch_v22_zip.resolve()
    output_root = ensure_tmp(output_root)
    require(output_root.is_dir(), f"candidate output root does not exist: {output_root}")
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    switch_jp, source_v21 = extract_switch_textures(switch_v21_zip, SWITCH_V21, "Switch v2.1")
    switch_ko, source_v22 = extract_switch_textures(switch_v22_zip, SWITCH_V22, "Switch v2.2")
    _, _, _, baseline_raw, baseline_g1t = decode_pc_baseline(baseline)
    candidate_outer = lz4.parse_link(candidate_path.read_bytes())
    candidate_nested = parse_banner_link(candidate_outer.entries[OUTER_INDEX].data)
    _, candidate_raw = lz4.decompress_wrapper(candidate_nested.wrapper)
    candidate_g1t = parse_g1t(candidate_raw, expected_platform=0x0A, expected_height=PC_HEIGHT)

    panel_width = 512
    panel_height = 64
    gutter = 4
    canvas_width = panel_width * 4 + gutter * 5
    canvas_height = (panel_height + gutter) * len(BANNERS) + gutter
    canvas = bytearray(canvas_width * canvas_height * 4)
    rows: list[dict[str, Any]] = []
    colors = [(224, 64, 64, 255), (64, 208, 96, 255), (232, 196, 56, 255), (48, 208, 232, 255)]
    for row_index, (index, label) in enumerate(BANNERS):
        original_texture = texture_by_index(baseline_g1t, index)
        candidate_texture = texture_by_index(candidate_g1t, index)
        pc_jp = codec.decode_bc3(baseline_raw[original_texture.payload_offset : original_texture.payload_end], PC_WIDTH, PC_HEIGHT)
        pc_ko = codec.decode_bc3(candidate_raw[candidate_texture.payload_offset : candidate_texture.payload_end], PC_WIDTH, PC_HEIGHT)
        switch_difference = changed_bbox(switch_jp[index], switch_ko[index], SWITCH_WIDTH, SWITCH_HEIGHT)
        target_patch = source_to_pc_rect(expand_rect(switch_difference, SOURCE_PADDING, SWITCH_WIDTH, SWITCH_HEIGHT))
        outside = pixel_changes_outside(pc_jp, pc_ko, PC_WIDTH, expanded_block_rect(target_patch))
        require(outside == 0 and pc_jp != pc_ko, f"visual QA delta is invalid for texture {index}")
        panels = [
            nearest_resize(composite_checker(switch_jp[index], SWITCH_WIDTH, SWITCH_HEIGHT), SWITCH_WIDTH, SWITCH_HEIGHT, panel_width, panel_height),
            nearest_resize(composite_checker(switch_ko[index], SWITCH_WIDTH, SWITCH_HEIGHT), SWITCH_WIDTH, SWITCH_HEIGHT, panel_width, panel_height),
            nearest_resize(composite_checker(pc_jp, PC_WIDTH, PC_HEIGHT), PC_WIDTH, PC_HEIGHT, panel_width, panel_height),
            nearest_resize(composite_checker(pc_ko, PC_WIDTH, PC_HEIGHT), PC_WIDTH, PC_HEIGHT, panel_width, panel_height),
        ]
        y = gutter + row_index * (panel_height + gutter)
        for panel_index, (panel, color) in enumerate(zip(panels, colors)):
            marked = bytearray(panel)
            add_border(marked, panel_width, panel_height, color)
            paste_rgba(canvas, canvas_width, gutter + panel_index * (panel_width + gutter), y, marked, panel_width, panel_height)
        rows.append(
            {
                "texture": index,
                "label": label,
                "panels_left_to_right": ["switch_jp", "switch_ko", "pc_jp_baseline", "pc_ko_candidate"],
                "pc_candidate_changed_pixels_outside_expanded_bc3_patch": outside,
            }
        )
    png = codec.encode_rgba_png(bytes(canvas), canvas_width, canvas_height)
    contact_path = ensure_tmp(output_root / "private" / "battle_banners_contact_sheet.png")
    report_path = ensure_tmp(output_root / "visual_qa.json")
    atomic_write(contact_path, png, forbidden=(baseline, switch_v21_zip, switch_v22_zip, candidate_path))
    report = {
        "schema": "nobu16.kr.steam-jp-battle-banners.visual-qa.v1",
        "file_only": True,
        "game_install_modified": False,
        "contact_sheet": {
            "path": str(contact_path),
            "sha256": sha256_bytes(png),
            "dimensions": [canvas_width, canvas_height],
            "private_only": True,
            "panel_legend": {"red": "Switch JP", "green": "Switch KO", "yellow": "PC JP baseline", "cyan": "PC KO candidate"},
        },
        "inputs": {"switch_v21": source_v21, "switch_v22": source_v22, "baseline": BASELINE, "candidate": file_spec(candidate_path)},
        "banners": rows,
        "all_nine_candidate_deltas_within_expanded_bc3_patches": True,
        "screen_qa_required_before_apply": True,
    }
    write_json(report_path, report, forbidden=(baseline, switch_v21_zip, switch_v22_zip, candidate_path, contact_path))
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="write a private battle-banner candidate below tmp")
    build.add_argument("--baseline", type=Path, required=True)
    build.add_argument("--switch-v21-zip", type=Path, required=True)
    build.add_argument("--switch-v22-zip", type=Path, required=True)
    build.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_battle_banners_v1" / "final")
    verify = sub.add_parser("verify", help="reparse a candidate already under tmp")
    verify.add_argument("--baseline", type=Path, required=True)
    verify.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_battle_banners_v1" / "final")
    visual = sub.add_parser("visual-qa", help="write a private four-panel QA contact sheet")
    visual.add_argument("--baseline", type=Path, required=True)
    visual.add_argument("--switch-v21-zip", type=Path, required=True)
    visual.add_argument("--switch-v22-zip", type=Path, required=True)
    visual.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_battle_banners_v1" / "final")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "build":
            result = build_candidate(
                baseline=args.baseline,
                switch_v21_zip=args.switch_v21_zip,
                switch_v22_zip=args.switch_v22_zip,
                output_root=args.output_root,
            )
        elif args.command == "verify":
            result = verify_output(baseline=args.baseline, output_root=args.output_root)
        elif args.command == "visual-qa":
            result = visual_qa(
                baseline=args.baseline,
                switch_v21_zip=args.switch_v21_zip,
                switch_v22_zip=args.switch_v22_zip,
                output_root=args.output_root,
            )
        else:  # pragma: no cover - argparse owns command selection
            raise BannerCandidateError(f"unsupported command: {args.command}")
    except (BannerCandidateError, lz4.LZ4Error, lz4.LinkError, codec.CodecError, OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
