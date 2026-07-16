#!/usr/bin/env python3
"""Private, PC-native candidate builder for Steam JP military-overlay UI.

The scope is deliberately limited to ``RES_JP/res_lang.bin /12/0`` on the
Steam Japanese 1.1.7 baseline.  Switch v2.1/v2.2 are read only as *decoded
visual evidence*: no Switch archive, LINK, LZ4, G1T, BC3, or PNG payload is
copied into the PC candidate.  The output candidate and preview imagery may
exist only below the ignored project ``tmp`` directory.

At present ``inspect`` is the evidence/mapping phase.  It extracts the exact
v2.1 -> v2.2 changed visual components privately and emits source-free
metadata.  A later build phase must use only explicitly mapped, safe PC text
rectangles.  Game files, releases, and Git state are never written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import sys
import tempfile
import zipfile
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp"
TITLE_WORKSTREAM = REPO / "workstreams" / "steam_jp_title_images_v1"
for path in (TOOLS, TITLE_WORKSTREAM):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as codec  # noqa: E402
import trace_bottom_return_button as trace  # noqa: E402
from build_steam_jp_title_images_v1 import resize_rgba_lanczos3_premultiplied  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-military-overlay.candidate.v1"
TARGET_RESOURCE = "RES_JP/res_lang.bin"
OUTER_INDEX = 12
NESTED_SLOT = 0
TARGET_TEXTURE = 0
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
BASELINE_SPEC = {
    "size": 154216023,
    "sha256": "0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0",
}
SWITCH_V21 = {
    "zip_size": 84369615,
    "zip_sha256": "473213B0013FB24C812C517A147A15D51EFCBFCE975FBB51738EFC34F5E7B387",
    "member_size": 86777150,
    "member_sha256": "C79B8F205CDAAF374B2F84F3AE4E385CE8498C5BA7CB8071DD2B9A178A27688D",
    "outer_sha256": "84A77685D2F0AA6841804E0DFAC7A7B883F8673398DA1638A080CCDCF5D36C30",
}
SWITCH_V22 = {
    "zip_size": 83752794,
    "zip_sha256": "5E6354069E38BE22E3B3C9272A6CEC8A4B4110DF2486B9A63E84D1058C35D7F7",
    "member_size": 85548771,
    "member_sha256": "F179D9A89A7D20B51E26681208CA7186BDD1DC6B2F09FAF9CA8154B35933557F",
    "outer_sha256": "0FDAE5E5652611A69D2038965D601511AA41C82437DF2DC6655C815DF2941025",
}

# The source rectangles are the exact, private v2.1->v2.2 Korean text
# difference groups.  The PC rectangles were individually mapped against the
# Japanese PC atlas and deliberately lie in transparent text-only islands.
# They are block-aligned so a BC3 re-encode cannot spill into adjacent UI art.
#
# Do not add game logos or title art here.  ``군평정`` is the /12 screen's UI
# heading, not the game's product logo; it is in the user-approved scope.
SAFE_MAPPINGS: tuple[dict[str, Any], ...] = (
    {
        "id": "military_assessment_heading",
        "label": "군평정",
        "source_rect": (1168, 8, 1508, 188),
        "pc_target_rect": (0, 144, 632, 472),
        "kind": "screen_ui_heading",
    },
    {
        "id": "victory_result",
        "label": "승리",
        "source_rect": (1802, 89, 1932, 169),
        "pc_target_rect": (640, 384, 852, 512),
        "kind": "result_label",
    },
    {
        "id": "defeat_result",
        "label": "패배",
        "source_rect": (1800, 1, 1933, 77),
        "pc_target_rect": (1800, 320, 2048, 464),
        "kind": "result_label",
    },
    {
        "id": "button_prompt",
        "label": "아무 버튼이나 누르십시오.",
        "source_rect": (764, 128, 1060, 171),
        "pc_target_rect": (1080, 196, 1488, 256),
        "kind": "instruction_text",
    },
)

# These are positively identified Korean source groups but sit on PC button
# gradients.  Do not clear/repaint their PC backgrounds until a separate
# native text-layer renderer can prove background preservation.
AUDIT_ONLY_MAPPINGS: tuple[dict[str, Any], ...] = (
    {"id": "merit_rank_1", "label": "전공 1위", "source_rect": (1828, 172, 1924, 197), "reason": "PC badge-background preservation unresolved"},
    {"id": "merit_rank_2", "label": "전공 2위", "source_rect": (460, 196, 568, 223), "reason": "PC badge-background preservation unresolved"},
    {"id": "merit_rank_3", "label": "전공 3위", "source_rect": (620, 197, 708, 223), "reason": "PC badge-background preservation unresolved"},
)


class OverlayError(ValueError):
    """Raised when a narrow military-overlay contract is violated."""


@dataclass(frozen=True)
class InnerEntry:
    index: int
    offset: int
    stored_size: int
    data: bytes
    gap_after: bytes


@dataclass(frozen=True)
class InnerLink:
    fixed_header: bytes
    table_offset: int
    resource_id: int
    aligned_table_end: int
    pre_data: bytes
    entries: tuple[InnerEntry, ...]
    original_size: int


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


@dataclass(frozen=True)
class G1T:
    raw: bytes
    platform: int
    textures: tuple[G1TTexture, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OverlayError(message)


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


def require_spec(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = file_spec(path)
    require(actual == dict(expected), f"{label} pin mismatch: expected={dict(expected)} actual={actual}")
    return actual


def is_reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT) or path.is_symlink() or path.is_junction()
    except OSError:
        return True


def lexical_tmp_path(path: Path) -> tuple[Path, Path]:
    root = Path(os.path.abspath(TMP_ROOT))
    candidate = Path(os.path.abspath(path))
    try:
        common = os.path.commonpath((os.path.normcase(str(root)), os.path.normcase(str(candidate))))
    except ValueError as exc:
        raise OverlayError(f"output drive differs from tmp root: {candidate}") from exc
    if common != os.path.normcase(str(root)):
        raise OverlayError(f"output lexically escapes tmp root: {candidate}")
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise OverlayError(f"output lexically escapes tmp root: {candidate}") from exc
    return root, candidate


def ensure_tmp(path: Path, *, mkdir: bool = False) -> Path:
    """Validate a tmp-only output path before any directory is made."""

    root_lexical, candidate = lexical_tmp_path(path)
    if is_reparse(root_lexical):
        raise OverlayError(f"tmp root is a reparse point: {root_lexical}")
    root = root_lexical.resolve()
    if is_reparse(root):
        raise OverlayError(f"resolved tmp root is a reparse point: {root}")
    current = root
    for part in candidate.relative_to(root_lexical).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if is_reparse(current):
                raise OverlayError(f"reparse point forbidden in output path: {current}")
            resolved = current.resolve()
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise OverlayError(f"existing component escapes tmp: {current}") from exc
            current = resolved
        elif mkdir:
            current.mkdir(exist_ok=False)
            if is_reparse(current):
                raise OverlayError(f"new output component is a reparse point: {current}")
    return current


def create_fresh_output_root(path: Path) -> Path:
    parent = ensure_tmp(Path(path).parent, mkdir=True)
    target = parent / Path(path).name
    if target.exists() or target.is_symlink():
        raise OverlayError(f"refusing to replace existing output root: {target}")
    target.mkdir(exist_ok=False)
    return ensure_tmp(target)


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    parent = ensure_tmp(Path(path).parent, mkdir=True)
    target = ensure_tmp(parent / Path(path).name)
    for source in forbidden:
        if target == source.resolve():
            raise OverlayError(f"refusing to overwrite input: {source}")
    if target.exists() or target.is_symlink():
        raise OverlayError(f"refusing to overwrite existing output: {target}")
    handle, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if is_reparse(target.parent):
            raise OverlayError(f"output parent became a reparse point: {target.parent}")
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: Mapping[str, Any], *, forbidden: Iterable[Path] = ()) -> None:
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"), forbidden=forbidden)


def align_up(value: int, alignment: int) -> int:
    require(alignment > 0 and not alignment & (alignment - 1), "alignment must be a power of two")
    return (value + alignment - 1) & -alignment


def parse_inner_link(blob: bytes, label: str) -> InnerLink:
    require(len(blob) >= 32 and blob[:4] == b"LINK", f"{label}: expected nested LINK")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", blob, 4)
    require(count == 1 and table_offset == 32, f"{label}: nested LINK shape drifted")
    require(blob[20:32] == b"\0" * 12, f"{label}: nested LINK extension drifted")
    table_end = table_offset + count * 8
    require(aligned_table_end == align_up(table_end, 32), f"{label}: invalid nested LINK alignment")
    offset, stored_size = struct.unpack_from("<II", blob, table_offset)
    end = offset + stored_size
    require(offset >= aligned_table_end and end <= len(blob), f"{label}: nested slot bounds invalid")
    entry = InnerEntry(0, offset, stored_size, blob[offset:end], blob[end:])
    parsed = InnerLink(blob[:table_offset], table_offset, resource_id, aligned_table_end, blob[table_end:offset], (entry,), len(blob))
    require(rebuild_inner_link(parsed) == blob, f"{label}: nested LINK identity rebuild failed")
    return parsed


def rebuild_inner_link(archive: InnerLink, replacements: Mapping[int, bytes] | None = None) -> bytes:
    replacements = replacements or {}
    output = bytearray(archive.fixed_header)
    output.extend(b"\0" * (len(archive.entries) * 8))
    output.extend(archive.pre_data)
    pairs: list[tuple[int, int]] = []
    for entry in archive.entries:
        data = replacements.get(entry.index, entry.data)
        require(len(output) == entry.offset, "nested LINK slot alignment drifted")
        pairs.append((len(output), len(data)))
        output.extend(data)
        output.extend(entry.gap_after)
    for index, (offset, size) in enumerate(pairs):
        struct.pack_into("<II", output, archive.table_offset + index * 8, offset, size)
    rebuilt = bytes(output)
    # ``parse_inner_link`` itself identity-rebuilds as a gate, so calling it
    # here would recurse indefinitely.  Validate the fixed nested header
    # directly; callers that need a full parse invoke ``parse_inner_link``
    # after rebuilding.
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", rebuilt, 4)
    require(
        rebuilt[:4] == b"LINK"
        and count == len(archive.entries)
        and table_offset == archive.table_offset
        and resource_id == archive.resource_id
        and aligned_table_end == archive.aligned_table_end,
        "nested LINK header drifted",
    )
    return rebuilt


def parse_g1t(raw: bytes, label: str) -> G1T:
    require(len(raw) >= 56 and raw[:8] == b"GT1G0600", f"{label}: expected GT1G0600")
    declared, directory_offset, count, platform = struct.unpack_from("<4I", raw, 8)
    require(declared == len(raw), f"{label}: declared G1T size mismatch")
    require(directory_offset == 32 and count == 1 and platform == 0x0A, f"{label}: PC G1T shape drifted")
    # This observed one-texture atlas has one zero word followed by the
    # one-texture ``0x01`` extension word.  Preserve both unchanged;
    # they are not a texture payload and must never be synthesized.
    require(raw[24:28] == b"\0" * 4 and raw[28:32] == struct.pack("<I", 0x01), f"{label}: unexpected G1T extension")
    start = directory_offset + struct.unpack_from("<I", raw, directory_offset)[0]
    require(start == 36 and start + 20 <= len(raw), f"{label}: texture offset drifted")
    packed, fmt, dimensions = struct.unpack_from("<BBB", raw, start)
    width = 1 << (dimensions & 0x0F)
    height = 1 << (dimensions >> 4)
    extra_version = raw[start + 7]
    extra_length = struct.unpack_from("<I", raw, start + 8)[0]
    payload_offset = start + 8 + extra_length
    expected = ((width + 3) // 4) * ((height + 3) // 4) * 16
    require((packed >> 4, fmt, extra_version, extra_length) == (1, 0x5B, 0x10, 12), f"{label}: unsupported BC3 contract")
    require((width, height) == (2048, 512), f"{label}: expected 2048x512 atlas")
    require(payload_offset + expected == len(raw), f"{label}: BC3 payload range drifted")
    texture = G1TTexture(0, start, len(raw), payload_offset, payload_offset + expected, width, height, fmt, packed >> 4)
    return G1T(raw, platform, (texture,))


def extract_switch_atlas(zip_path: Path, spec: Mapping[str, Any], label: str) -> tuple[bytes, dict[str, Any]]:
    zip_path = zip_path.resolve()
    require_spec(zip_path, {"size": spec["zip_size"], "sha256": spec["zip_sha256"]}, f"{label} ZIP")
    with zipfile.ZipFile(zip_path) as archive:
        try:
            info = archive.getinfo(SWITCH_MEMBER)
        except KeyError as exc:
            raise OverlayError(f"{label}: missing {SWITCH_MEMBER}") from exc
        resource = archive.read(info)
    require(len(resource) == spec["member_size"] and sha256_bytes(resource) == spec["member_sha256"], f"{label}: resource pin mismatch")
    outer = lz4.parse_link(resource)
    require(lz4.rebuild_link(outer) == resource, f"{label}: outer LINK identity rebuild failed")
    require(OUTER_INDEX < len(outer.entries) and sha256_bytes(outer.entries[OUTER_INDEX].data) == spec["outer_sha256"], f"{label}: /12 pin mismatch")
    bundle = trace.parse_bundle(outer.entries[OUTER_INDEX].data)
    entries = {entry.index: entry for entry in bundle.entries}
    require(set(entries) == {NESTED_SLOT} and bundle.resource_id == 58, f"{label}: nested /12 structure drifted")
    _, raw = lz4.decompress_wrapper(entries[NESTED_SLOT].data)
    header, textures = trace.parse_g1t(raw)
    require(header["platform"] == 0x10 and len(textures) == 1, f"{label}: Switch G1T shape drifted")
    texture = textures[TARGET_TEXTURE]
    require((texture.width, texture.height, texture.format_code, texture.mip_count) == (2048, 256, 0x5B, 1), f"{label}: Switch atlas contract drifted")
    rgba = trace.decode_texture(texture)
    return rgba, {
        "zip": {"size": zip_path.stat().st_size, "sha256": sha256_file(zip_path)},
        "member": {"size": len(resource), "sha256": sha256_bytes(resource)},
        "outer_12_sha256": sha256_bytes(outer.entries[OUTER_INDEX].data),
        "atlas": {"dimensions": [texture.width, texture.height], "rgba_sha256": sha256_bytes(rgba)},
    }


def extract_pc_atlas(baseline: Path) -> tuple[lz4.LinkArchive, InnerLink, lz4.WrapperHeader, G1T, bytes]:
    require_spec(baseline, BASELINE_SPEC, "Steam JP 1.1.7 baseline")
    outer_blob = baseline.read_bytes()
    outer = lz4.parse_link(outer_blob)
    require(lz4.rebuild_link(outer) == outer_blob and OUTER_INDEX < len(outer.entries), "PC outer LINK identity failed")
    inner = parse_inner_link(outer.entries[OUTER_INDEX].data, "Steam JP /12")
    require(inner.resource_id == 58 and len(inner.entries) == 1, "PC /12 nested resource drifted")
    wrapper, raw = lz4.decompress_wrapper(inner.entries[NESTED_SLOT].data)
    g1t = parse_g1t(raw, "Steam JP /12/0")
    texture = g1t.textures[TARGET_TEXTURE]
    rgba = codec.decode_bc3(raw[texture.payload_offset:texture.payload_end], texture.width, texture.height)
    return outer, inner, wrapper, g1t, rgba


def rgba_difference_components(left: bytes, right: bytes, width: int, height: int) -> list[dict[str, int]]:
    """Return coalesced changed regions without persisting decoded source bytes.

    Tiny BC3 anti-alias specks are joined with a 3px halo.  The output is for
    private atlas mapping only and contains dimensions/counts, never pixels.
    """

    require(len(left) == len(right) == width * height * 4, "diff inputs do not match atlas geometry")
    changed = bytearray(width * height)
    for pixel in range(width * height):
        offset = pixel * 4
        changed[pixel] = left[offset:offset + 4] != right[offset:offset + 4]
    visited = bytearray(width * height)
    components: list[dict[str, int]] = []
    for start in range(width * height):
        if not changed[start] or visited[start]:
            continue
        queue: deque[int] = deque((start,))
        visited[start] = 1
        x0 = x1 = start % width
        y0 = y1 = start // width
        count = 0
        while queue:
            point = queue.popleft()
            x, y = point % width, point // width
            count += 1
            x0, x1 = min(x0, x), max(x1, x)
            y0, y1 = min(y0, y), max(y1, y)
            for yy in range(max(0, y - 1), min(height, y + 2)):
                row = yy * width
                for xx in range(max(0, x - 1), min(width, x + 2)):
                    target = row + xx
                    if changed[target] and not visited[target]:
                        visited[target] = 1
                        queue.append(target)
        components.append({"x0": x0, "y0": y0, "x1": x1 + 1, "y1": y1 + 1, "pixel_count": count})
    return components


def coalesce_components(components: Sequence[Mapping[str, int]], gap: int = 12) -> list[dict[str, int]]:
    """Group glyph-sized components into conservative UI-label rectangles."""

    pending = [dict(component) for component in components]
    merged: list[dict[str, int]] = []
    while pending:
        current = pending.pop(0)
        changed = True
        while changed:
            changed = False
            survivors: list[dict[str, int]] = []
            for candidate in pending:
                separated = (
                    candidate["x0"] > current["x1"] + gap
                    or current["x0"] > candidate["x1"] + gap
                    or candidate["y0"] > current["y1"] + gap
                    or current["y0"] > candidate["y1"] + gap
                )
                if separated:
                    survivors.append(candidate)
                    continue
                current = {
                    "x0": min(current["x0"], candidate["x0"]),
                    "y0": min(current["y0"], candidate["y0"]),
                    "x1": max(current["x1"], candidate["x1"]),
                    "y1": max(current["y1"], candidate["y1"]),
                    "pixel_count": current["pixel_count"] + candidate["pixel_count"],
                }
                changed = True
            pending = survivors
        merged.append(current)
    return sorted(merged, key=lambda row: (row["y0"], row["x0"]))


def crop_rgba(rgba: bytes, width: int, height: int, rect: tuple[int, int, int, int]) -> bytes:
    x0, y0, x1, y1 = rect
    require(0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height, f"crop lies outside {width}x{height}: {rect}")
    output = bytearray((x1 - x0) * (y1 - y0) * 4)
    for row in range(y1 - y0):
        source = ((y0 + row) * width + x0) * 4
        target = row * (x1 - x0) * 4
        output[target:target + (x1 - x0) * 4] = rgba[source:source + (x1 - x0) * 4]
    return bytes(output)


def paste_rgba(canvas: bytearray, canvas_width: int, x0: int, y0: int, source: bytes, width: int, height: int) -> None:
    canvas_height = len(canvas) // (canvas_width * 4)
    require(0 <= x0 <= canvas_width - width and 0 <= y0 <= canvas_height - height, "paste rectangle outside canvas")
    for row in range(height):
        src = row * width * 4
        dst = ((y0 + row) * canvas_width + x0) * 4
        canvas[dst:dst + width * 4] = source[src:src + width * 4]


def mark_rect(canvas: bytearray, width: int, height: int, rect: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = rect
    for x in range(x0, x1):
        canvas[(y0 * width + x) * 4:(y0 * width + x) * 4 + 4] = bytes(color)
        canvas[((y1 - 1) * width + x) * 4:((y1 - 1) * width + x) * 4 + 4] = bytes(color)
    for y in range(y0, y1):
        canvas[(y * width + x0) * 4:(y * width + x0) * 4 + 4] = bytes(color)
        canvas[(y * width + x1 - 1) * 4:(y * width + x1 - 1) * 4 + 4] = bytes(color)


def rect_dimensions(rect: tuple[int, int, int, int]) -> tuple[int, int]:
    x0, y0, x1, y1 = rect
    require(x0 < x1 and y0 < y1, f"invalid rectangle: {rect}")
    return x1 - x0, y1 - y0


def rectangles_overlap(left: tuple[int, int, int, int], right: tuple[int, int, int, int]) -> bool:
    return not (left[2] <= right[0] or right[2] <= left[0] or left[3] <= right[1] or right[3] <= left[1])


def validate_mapping_contract() -> None:
    require(len(SAFE_MAPPINGS) == 4 and len(AUDIT_ONLY_MAPPINGS) == 3, "unexpected mapping inventory")
    ids = [str(row["id"]) for row in SAFE_MAPPINGS + AUDIT_ONLY_MAPPINGS]
    require(len(ids) == len(set(ids)), "mapping identifiers must be unique")
    for row in SAFE_MAPPINGS:
        source = tuple(row["source_rect"])
        target = tuple(row["pc_target_rect"])
        rect_dimensions(source)
        rect_dimensions(target)
        require(0 <= source[0] < source[2] <= 2048 and 0 <= source[1] < source[3] <= 256, f"source rectangle escapes Switch atlas: {row['id']}")
        require(0 <= target[0] < target[2] <= 2048 and 0 <= target[1] < target[3] <= 512, f"target rectangle escapes PC atlas: {row['id']}")
        require(all(value % 4 == 0 for value in target), f"PC target must be BC3-block aligned: {row['id']}")
        require("logo" not in str(row["id"]).lower() and "title_art" not in str(row["id"]).lower(), "logo/title-art entry is forbidden")
    for position, left in enumerate(SAFE_MAPPINGS):
        for right in SAFE_MAPPINGS[position + 1:]:
            require(not rectangles_overlap(tuple(left["pc_target_rect"]), tuple(right["pc_target_rect"])), f"PC target rectangles overlap: {left['id']} / {right['id']}")
    for row in AUDIT_ONLY_MAPPINGS:
        source = tuple(row["source_rect"])
        rect_dimensions(source)
        require(0 <= source[0] < source[2] <= 2048 and 0 <= source[1] < source[3] <= 256, f"audit-only source rectangle escapes atlas: {row['id']}")
        require("pc_target_rect" not in row, f"audit-only entry cannot have a candidate target: {row['id']}")


def clear_rect_rgba(target: bytearray, width: int, height: int, rect: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = rect
    require(0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height, f"clear rectangle outside canvas: {rect}")
    for row in range(y0, y1):
        start = (row * width + x0) * 4
        target[start:start + (x1 - x0) * 4] = b"\0" * ((x1 - x0) * 4)


def changed_pixel_count(left: bytes, right: bytes, width: int, height: int, *, within: tuple[int, int, int, int] | None = None) -> int:
    require(len(left) == len(right) == width * height * 4, "change comparison geometry mismatch")
    count = 0
    for pixel in range(width * height):
        x, y = pixel % width, pixel // width
        if within is not None and not (within[0] <= x < within[2] and within[1] <= y < within[3]):
            continue
        start = pixel * 4
        if left[start:start + 4] != right[start:start + 4]:
            count += 1
    return count


def changed_pixels_escape_rectangles(
    left: bytes,
    right: bytes,
    width: int,
    height: int,
    allowed: Sequence[tuple[int, int, int, int]],
) -> int:
    require(len(left) == len(right) == width * height * 4, "change comparison geometry mismatch")
    escaped = 0
    for pixel in range(width * height):
        start = pixel * 4
        if left[start:start + 4] == right[start:start + 4]:
            continue
        x, y = pixel % width, pixel // width
        if not any(rect[0] <= x < rect[2] and rect[1] <= y < rect[3] for rect in allowed):
            escaped += 1
    return escaped


def add_border(rgba: bytearray, width: int, height: int, color: tuple[int, int, int, int]) -> None:
    for x in range(width):
        rgba[x * 4:x * 4 + 4] = bytes(color)
        bottom = ((height - 1) * width + x) * 4
        rgba[bottom:bottom + 4] = bytes(color)
    for y in range(height):
        left = (y * width) * 4
        right = (y * width + width - 1) * 4
        rgba[left:left + 4] = bytes(color)
        rgba[right:right + 4] = bytes(color)


def build_visual_qa(
    *,
    switch_jp: bytes,
    switch_ko: bytes,
    pc_baseline: bytes,
    pc_candidate: bytes,
    output_root: Path,
    forbidden: Iterable[Path],
) -> dict[str, Any]:
    """Create a private four-panel contact sheet for safe mappings only."""

    gutter = 8
    max_width = max(rect_dimensions(tuple(item["pc_target_rect"]))[0] for item in SAFE_MAPPINGS)
    max_height = max(rect_dimensions(tuple(item["pc_target_rect"]))[1] for item in SAFE_MAPPINGS)
    canvas_width = max_width * 4 + gutter * 5
    canvas_height = (max_height + gutter) * len(SAFE_MAPPINGS) + gutter
    canvas = bytearray(canvas_width * canvas_height * 4)
    rows: list[dict[str, Any]] = []
    colors = ((224, 64, 64, 255), (64, 208, 96, 255), (232, 196, 56, 255), (48, 208, 232, 255))
    for index, item in enumerate(SAFE_MAPPINGS):
        source_rect = tuple(item["source_rect"])
        target_rect = tuple(item["pc_target_rect"])
        target_width, target_height = rect_dimensions(target_rect)
        source_width, source_height = rect_dimensions(source_rect)
        source_jp = resize_rgba_lanczos3_premultiplied(crop_rgba(switch_jp, 2048, 256, source_rect), source_width, source_height, target_width, target_height)
        source_ko = resize_rgba_lanczos3_premultiplied(crop_rgba(switch_ko, 2048, 256, source_rect), source_width, source_height, target_width, target_height)
        pc_jp = crop_rgba(pc_baseline, 2048, 512, target_rect)
        pc_ko = crop_rgba(pc_candidate, 2048, 512, target_rect)
        local_change_count = changed_pixel_count(pc_jp, pc_ko, target_width, target_height)
        require(local_change_count > 0, f"visual QA has no candidate change: {item['id']}")
        y = gutter + index * (max_height + gutter)
        panels = (source_jp, source_ko, pc_jp, pc_ko)
        for panel_index, (panel, color) in enumerate(zip(panels, colors)):
            marked = bytearray(panel)
            add_border(marked, target_width, target_height, color)
            paste_rgba(canvas, canvas_width, gutter + panel_index * (max_width + gutter), y, bytes(marked), target_width, target_height)
        rows.append(
            {
                "id": item["id"],
                "label": item["label"],
                "pc_target_rect": list(target_rect),
                "panels_left_to_right": ["switch_jp_reference", "switch_ko_reference", "pc_jp_baseline", "pc_ko_candidate"],
                "pc_candidate_changed_pixel_count": local_change_count,
            }
        )
    contact_path = ensure_tmp(output_root / "private", mkdir=True) / "military_overlay_contact_sheet.png"
    png = codec.encode_rgba_png(bytes(canvas), canvas_width, canvas_height)
    atomic_write(contact_path, png, forbidden=forbidden)
    return {
        "path": str(contact_path),
        "sha256": sha256_bytes(png),
        "dimensions": [canvas_width, canvas_height],
        "private_tmp_only": True,
        "panel_legend": {"red": "Switch v2.1 Japanese reference", "green": "Switch v2.2 Korean reference", "yellow": "Steam JP baseline", "cyan": "PC Korean candidate"},
        "rows": rows,
    }


def inspect(
    *, baseline: Path, switch_v21_zip: Path, switch_v22_zip: Path, output_root: Path
) -> dict[str, Any]:
    validate_mapping_contract()
    output_root = create_fresh_output_root(output_root)
    baseline = baseline.resolve()
    switch_v21_zip = switch_v21_zip.resolve()
    switch_v22_zip = switch_v22_zip.resolve()
    baseline_before = require_spec(baseline, BASELINE_SPEC, "Steam JP 1.1.7 baseline")
    _, _, _, _, pc_rgba = extract_pc_atlas(baseline)
    switch_jp, v21 = extract_switch_atlas(switch_v21_zip, SWITCH_V21, "Switch v2.1")
    switch_ko, v22 = extract_switch_atlas(switch_v22_zip, SWITCH_V22, "Switch v2.2")
    components = rgba_difference_components(switch_jp, switch_ko, 2048, 256)
    merged = coalesce_components(components)
    require(components and merged, "Switch v2.1 -> v2.2 has no visible /12 differences")

    # A private three-row reference sheet: Switch Japanese, Switch Korean,
    # and PC Japanese.  Yellow rectangles identify only image-difference
    # groups; no decoded asset is emitted outside ignored tmp.
    canvas = bytearray(2048 * (256 + 256 + 512) * 4)
    paste_rgba(canvas, 2048, 0, 0, switch_jp, 2048, 256)
    paste_rgba(canvas, 2048, 0, 256, switch_ko, 2048, 256)
    paste_rgba(canvas, 2048, 0, 512, pc_rgba, 2048, 512)
    for row in merged:
        rect = (row["x0"], row["y0"], row["x1"], row["y1"])
        mark_rect(canvas, 2048, 1024, rect, (255, 224, 64, 255))
        mark_rect(canvas, 2048, 1024, (rect[0], rect[1] + 256, rect[2], rect[3] + 256), (64, 224, 96, 255))
    preview_path = ensure_tmp(output_root / "private", mkdir=True) / "switch_pc_mapping_sheet.png"
    atomic_write(preview_path, codec.encode_rgba_png(bytes(canvas), 2048, 1024), forbidden=(baseline, switch_v21_zip, switch_v22_zip))

    report = {
        "schema": SCHEMA,
        "phase": "inspect_only_no_pc_candidate",
        "file_only": True,
        "game_install_modified": False,
        "git_or_release_modified": False,
        "scope": {
            "target_resource": TARGET_RESOURCE,
            "outer_entry": OUTER_INDEX,
            "nested_slot": NESTED_SLOT,
            "texture": TARGET_TEXTURE,
            "excluded_outer_entries": [3, 24],
            "game_logo_or_title_art_modified": False,
            "switch_raw_link_lz4_g1t_bc_payload_copied": False,
        },
        "mapping_plan": {
            "candidate_safe_text_rectangles": [
                {"id": row["id"], "label": row["label"], "source_rect": list(row["source_rect"]), "pc_target_rect": list(row["pc_target_rect"])}
                for row in SAFE_MAPPINGS
            ],
            "audit_only_text_rectangles": [
                {"id": row["id"], "label": row["label"], "source_rect": list(row["source_rect"]), "reason": row["reason"]}
                for row in AUDIT_ONLY_MAPPINGS
            ],
        },
        "inputs": {
            "steam_jp_baseline": baseline_before,
            "switch_v21": v21,
            "switch_v22": v22,
        },
        "switch_v21_to_v22_difference": {
            "raw_component_count": len(components),
            "coalesced_group_count": len(merged),
            "coalesced_rectangles": merged,
            "purpose": "private mapping evidence only; text identity/PC target mapping remains an explicit build gate",
        },
        "private_visual_qa": {
            "path": str(preview_path),
            "sha256": sha256_file(preview_path),
            "dimensions": [2048, 1024],
            "rows_top_to_bottom": ["Switch v2.1 Japanese", "Switch v2.2 Korean", "Steam JP 1.1.7 Japanese"],
            "yellow_rectangles": "coalesced Switch v2.1-to-v2.2 difference groups",
            "private_tmp_only": True,
        },
        "next_gate": [
            "Map only clearly identified text rectangles to the PC atlas; do not map crest, patterned background, buttons, logos, or title art.",
            "For each mapped PC target, prove all changed BC3 blocks fall inside that target's expanded block rectangle.",
            "Leave uncertain regions audit-only and do not create a game-write transaction in this workstream.",
        ],
    }
    report_path = ensure_tmp(output_root / "inspect_report.json")
    write_json(report_path, report, forbidden=(baseline, switch_v21_zip, switch_v22_zip))
    baseline_after = require_spec(baseline, BASELINE_SPEC, "Steam JP baseline after inspect")
    require(baseline_after == baseline_before, "baseline changed during inspect")
    return report


def build_candidate(
    *, baseline: Path, switch_v21_zip: Path, switch_v22_zip: Path, output_root: Path
) -> dict[str, Any]:
    """Build one private candidate from four verified text-only rectangles."""

    validate_mapping_contract()
    output_root = create_fresh_output_root(output_root)
    baseline = baseline.resolve()
    switch_v21_zip = switch_v21_zip.resolve()
    switch_v22_zip = switch_v22_zip.resolve()
    baseline_before = require_spec(baseline, BASELINE_SPEC, "Steam JP 1.1.7 baseline")
    outer, inner, wrapper, g1t, pc_rgba = extract_pc_atlas(baseline)
    switch_jp, v21 = extract_switch_atlas(switch_v21_zip, SWITCH_V21, "Switch v2.1")
    switch_ko, v22 = extract_switch_atlas(switch_v22_zip, SWITCH_V22, "Switch v2.2")
    texture = g1t.textures[TARGET_TEXTURE]
    original_payload = g1t.raw[texture.payload_offset:texture.payload_end]
    requested = bytearray(pc_rgba)
    rows: list[dict[str, Any]] = []
    target_rectangles = [tuple(item["pc_target_rect"]) for item in SAFE_MAPPINGS]
    for item in SAFE_MAPPINGS:
        source_rect = tuple(item["source_rect"])
        target_rect = tuple(item["pc_target_rect"])
        source_width, source_height = rect_dimensions(source_rect)
        target_width, target_height = rect_dimensions(target_rect)
        korean_source = crop_rgba(switch_ko, 2048, 256, source_rect)
        japanese_source = crop_rgba(switch_jp, 2048, 256, source_rect)
        resized = resize_rgba_lanczos3_premultiplied(korean_source, source_width, source_height, target_width, target_height)
        # The PC targets are pre-validated transparent text-only regions.
        # Clearing removes the Japanese raster before the Korean visual
        # reference is encoded; no button/background/crest pixels are copied.
        clear_rect_rgba(requested, 2048, 512, target_rect)
        paste_rgba(requested, 2048, target_rect[0], target_rect[1], resized, target_width, target_height)
        rows.append(
            {
                "id": item["id"],
                "label": item["label"],
                "kind": item["kind"],
                "switch_source_rect": list(source_rect),
                "pc_target_rect": list(target_rect),
                "switch_reference_jp_rgba_sha256": sha256_bytes(japanese_source),
                "switch_reference_ko_rgba_sha256": sha256_bytes(korean_source),
                "pc_resampled_ko_rgba_sha256": sha256_bytes(resized),
            }
        )
    requested_bytes = bytes(requested)
    requested_escape = changed_pixels_escape_rectangles(pc_rgba, requested_bytes, 2048, 512, target_rectangles)
    require(requested_escape == 0, "requested text replacement escaped PC target rectangles")
    for item in SAFE_MAPPINGS:
        target = tuple(item["pc_target_rect"])
        require(changed_pixel_count(pc_rgba, requested_bytes, 2048, 512, within=target) > 0, f"requested replacement is empty: {item['id']}")

    rebuilt_payload, preserved_blocks, encoded_blocks = codec.encode_bc3(
        requested_bytes,
        texture.width,
        texture.height,
        template_bc3=original_payload,
    )
    rebuilt_raw = g1t.raw[:texture.payload_offset] + rebuilt_payload + g1t.raw[texture.payload_end:]
    rebuilt_g1t = parse_g1t(rebuilt_raw, "candidate Steam JP /12/0")
    require(
        rebuilt_raw[:texture.payload_offset] == g1t.raw[:texture.payload_offset]
        and rebuilt_raw[texture.payload_end:] == g1t.raw[texture.payload_end:],
        "candidate changed G1T bytes outside BC3 texture payload",
    )
    rebuilt_wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, wrapper)
    roundtrip_header, roundtrip_raw = lz4.decompress_wrapper(rebuilt_wrapper)
    require(roundtrip_raw == rebuilt_raw and roundtrip_header.prefix == wrapper.prefix, "candidate LZ4 round-trip/prefix failed")
    rebuilt_inner = rebuild_inner_link(inner, {NESTED_SLOT: rebuilt_wrapper})
    parsed_inner = parse_inner_link(rebuilt_inner, "candidate Steam JP /12")
    require(parsed_inner.entries[NESTED_SLOT].data == rebuilt_wrapper, "candidate nested wrapper re-extraction failed")
    candidate_blob = lz4.rebuild_link(outer, {OUTER_INDEX: rebuilt_inner})
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP", mkdir=True) / "res_lang.bin"
    atomic_write(candidate_path, candidate_blob, forbidden=(baseline, switch_v21_zip, switch_v22_zip))

    candidate_outer = lz4.parse_link(candidate_path.read_bytes())
    require(len(candidate_outer.entries) == len(outer.entries), "candidate outer entry count drifted")
    before_outer = {str(entry.index): sha256_bytes(entry.data) for entry in outer.entries}
    after_outer = {str(entry.index): sha256_bytes(entry.data) for entry in candidate_outer.entries}
    for entry in outer.entries:
        if entry.index != OUTER_INDEX:
            require(candidate_outer.entries[entry.index].data == entry.data, f"candidate changed unrelated outer /{entry.index}")
    require(before_outer["3"] == after_outer["3"] and before_outer["24"] == after_outer["24"], "candidate changed forbidden logo/title outer entry")
    candidate_inner = parse_inner_link(candidate_outer.entries[OUTER_INDEX].data, "candidate outer /12")
    candidate_header, candidate_raw = lz4.decompress_wrapper(candidate_inner.entries[NESTED_SLOT].data)
    candidate_g1t = parse_g1t(candidate_raw, "candidate outer /12/0")
    candidate_texture = candidate_g1t.textures[TARGET_TEXTURE]
    candidate_payload = candidate_raw[candidate_texture.payload_offset:candidate_texture.payload_end]
    candidate_rgba = codec.decode_bc3(candidate_payload, 2048, 512)
    candidate_escape = changed_pixels_escape_rectangles(pc_rgba, candidate_rgba, 2048, 512, target_rectangles)
    require(candidate_escape == 0, "BC3 candidate changed pixels outside block-aligned text rectangles")
    for item in SAFE_MAPPINGS:
        target = tuple(item["pc_target_rect"])
        require(changed_pixel_count(pc_rgba, candidate_rgba, 2048, 512, within=target) > 0, f"BC3 candidate delta missing: {item['id']}")
    require(candidate_raw[:candidate_texture.payload_offset] == g1t.raw[:texture.payload_offset], "candidate raw G1T header drifted")
    require(candidate_raw[candidate_texture.payload_end:] == g1t.raw[texture.payload_end:], "candidate raw G1T suffix drifted")
    require(candidate_header.prefix == wrapper.prefix, "candidate wrapper prefix drifted")

    visual = build_visual_qa(
        switch_jp=switch_jp,
        switch_ko=switch_ko,
        pc_baseline=pc_rgba,
        pc_candidate=candidate_rgba,
        output_root=output_root,
        forbidden=(baseline, switch_v21_zip, switch_v22_zip, candidate_path),
    )
    baseline_after = require_spec(baseline, BASELINE_SPEC, "Steam JP 1.1.7 baseline after build")
    require(baseline_after == baseline_before, "Steam JP baseline changed during private candidate build")
    report = {
        "schema": SCHEMA,
        "phase": "private_pc_candidate",
        "file_only": True,
        "game_install_modified": False,
        "git_or_release_modified": False,
        "target_resource": TARGET_RESOURCE,
        "scope": {
            "outer_entry": OUTER_INDEX,
            "nested_slot": NESTED_SLOT,
            "texture": TARGET_TEXTURE,
            "safe_candidate_text_count": len(SAFE_MAPPINGS),
            "audit_only_text_count": len(AUDIT_ONLY_MAPPINGS),
            "audit_only_reason": "merit-rank badge backgrounds are intentionally preserved pending a text-layer renderer",
            "forbidden_outer_entries_preserved": [3, 24],
            "game_logo_or_title_art_modified": False,
            "battle_animation_or_crest_modified": False,
            "switch_raw_link_lz4_g1t_bc_payload_copied": False,
        },
        "inputs": {"steam_jp_baseline": baseline_before, "switch_v21": v21, "switch_v22": v22},
        "applied_safe_text": rows,
        "audit_only_text": [dict(row) for row in AUDIT_ONLY_MAPPINGS],
        "bc3": {
            "total_blocks": len(original_payload) // 16,
            "preserved_template_blocks": preserved_blocks,
            "deterministically_reencoded_blocks": encoded_blocks,
            "requested_changed_pixels_outside_target_rectangles": requested_escape,
            "candidate_changed_pixels_outside_target_rectangles": candidate_escape,
            "original_payload_sha256": sha256_bytes(original_payload),
            "candidate_payload_sha256": sha256_bytes(candidate_payload),
        },
        "preservation": {
            "outer_entry_sha256_before": before_outer,
            "outer_entry_sha256_after": after_outer,
            "all_non_12_outer_entry_data_byte_preserved": all(before_outer[str(index)] == after_outer[str(index)] for index in range(len(outer.entries)) if index != OUTER_INDEX),
            "outer_3_game_title_data_byte_preserved": before_outer["3"] == after_outer["3"],
            "outer_24_additional_content_label_data_byte_preserved": before_outer["24"] == after_outer["24"],
            "g1t_non_payload_bytes_preserved": True,
            "wrapper_prefix_preserved": True,
            "nested_resource_id": candidate_inner.resource_id,
        },
        "candidate": {"path": str(candidate_path), **file_spec(candidate_path), "under_tmp": True, "outer_parse_valid": True, "nested_parse_valid": True, "g1t_parse_valid": True, "lz4_roundtrip_valid": True},
        "private_visual_qa": visual,
        "private_payload_policy": {
            "contains_complete_game_resource": True,
            "contains_third_party_translation_pixels": True,
            "git_publish_allowed": False,
            "release_upload_allowed": False,
            "steam_live_apply_allowed": False,
            "output_must_remain_under_tmp": True,
        },
    }
    report_path = ensure_tmp(output_root / "build_report.json")
    write_json(report_path, report, forbidden=(baseline, switch_v21_zip, switch_v22_zip, candidate_path))
    return report


def verify_inspect(output_root: Path) -> dict[str, Any]:
    output_root = ensure_tmp(output_root)
    report_path = ensure_tmp(output_root / "inspect_report.json")
    value = json.loads(report_path.read_text(encoding="utf-8"))
    require(value.get("schema") == SCHEMA and value.get("phase") == "inspect_only_no_pc_candidate", "inspect schema/phase mismatch")
    require(value.get("game_install_modified") is False and value.get("git_or_release_modified") is False, "scope invariants lost")
    scope = value.get("scope")
    require(isinstance(scope, Mapping) and scope.get("outer_entry") == OUTER_INDEX and scope.get("excluded_outer_entries") == [3, 24], "scope mismatch")
    difference = value.get("switch_v21_to_v22_difference")
    require(isinstance(difference, Mapping) and difference.get("raw_component_count", 0) > 0 and difference.get("coalesced_group_count", 0) > 0, "difference evidence missing")
    preview = value.get("private_visual_qa")
    require(isinstance(preview, Mapping), "private visual QA missing")
    preview_path = ensure_tmp(Path(str(preview["path"])))
    require(preview_path.is_file() and sha256_file(preview_path) == preview.get("sha256"), "private mapping sheet hash mismatch")
    return {"status": "PASS", "game_install_modified": False, "phase": "inspect_only_no_pc_candidate"}


def verify_candidate(output_root: Path) -> dict[str, Any]:
    validate_mapping_contract()
    output_root = ensure_tmp(output_root)
    report_path = ensure_tmp(output_root / "build_report.json")
    value = json.loads(report_path.read_text(encoding="utf-8"))
    require(value.get("schema") == SCHEMA and value.get("phase") == "private_pc_candidate", "candidate schema/phase mismatch")
    require(value.get("file_only") is True and value.get("game_install_modified") is False and value.get("git_or_release_modified") is False, "candidate scope invariants lost")
    scope = value.get("scope")
    require(isinstance(scope, Mapping), "candidate scope missing")
    require(scope.get("outer_entry") == OUTER_INDEX and scope.get("nested_slot") == NESTED_SLOT and scope.get("texture") == TARGET_TEXTURE, "candidate target path drifted")
    require(scope.get("forbidden_outer_entries_preserved") == [3, 24] and scope.get("game_logo_or_title_art_modified") is False and scope.get("battle_animation_or_crest_modified") is False, "forbidden image scope drifted")
    require(scope.get("safe_candidate_text_count") == len(SAFE_MAPPINGS) and scope.get("audit_only_text_count") == len(AUDIT_ONLY_MAPPINGS), "mapping-count drifted")
    candidate_row = value.get("candidate")
    require(isinstance(candidate_row, Mapping), "candidate record missing")
    candidate_path = ensure_tmp(Path(str(candidate_row["path"])))
    require(candidate_path.is_file() and file_spec(candidate_path) == {"size": candidate_row.get("size"), "sha256": candidate_row.get("sha256")}, "candidate file hash mismatch")
    outer = lz4.parse_link(candidate_path.read_bytes())
    inner = parse_inner_link(outer.entries[OUTER_INDEX].data, "verified candidate /12")
    _, raw = lz4.decompress_wrapper(inner.entries[NESTED_SLOT].data)
    g1t = parse_g1t(raw, "verified candidate /12/0")
    require((g1t.textures[TARGET_TEXTURE].width, g1t.textures[TARGET_TEXTURE].height) == (2048, 512), "candidate atlas geometry drifted")
    preservation = value.get("preservation")
    require(isinstance(preservation, Mapping), "candidate preservation report missing")
    before = preservation.get("outer_entry_sha256_before")
    after = preservation.get("outer_entry_sha256_after")
    require(isinstance(before, Mapping) and isinstance(after, Mapping), "outer preservation hashes missing")
    observed = {str(entry.index): sha256_bytes(entry.data) for entry in outer.entries}
    require(observed == after, "candidate outer data hashes do not match report")
    require(before.get("3") == observed.get("3") and before.get("24") == observed.get("24"), "forbidden outer entry data changed")
    for index in range(len(outer.entries)):
        if index != OUTER_INDEX:
            require(before.get(str(index)) == observed.get(str(index)), f"unrelated outer /{index} changed")
    bc3 = value.get("bc3")
    require(isinstance(bc3, Mapping) and bc3.get("requested_changed_pixels_outside_target_rectangles") == 0 and bc3.get("candidate_changed_pixels_outside_target_rectangles") == 0, "BC3 target-boundary proof failed")
    applied = value.get("applied_safe_text")
    audit_only = value.get("audit_only_text")
    require(isinstance(applied, list) and [row.get("id") for row in applied] == [row["id"] for row in SAFE_MAPPINGS], "applied safe mapping list drifted")
    require(isinstance(audit_only, list) and [row.get("id") for row in audit_only] == [row["id"] for row in AUDIT_ONLY_MAPPINGS], "audit-only mapping list drifted")
    visual = value.get("private_visual_qa")
    require(isinstance(visual, Mapping), "visual QA report missing")
    visual_path = ensure_tmp(Path(str(visual["path"])))
    require(visual_path.is_file() and sha256_file(visual_path) == visual.get("sha256"), "visual QA contact-sheet hash mismatch")
    policy = value.get("private_payload_policy")
    require(isinstance(policy, Mapping) and policy.get("git_publish_allowed") is False and policy.get("release_upload_allowed") is False and policy.get("steam_live_apply_allowed") is False, "private-output policy drifted")
    return {"status": "PASS", "candidate": file_spec(candidate_path), "game_install_modified": False}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("inspect", help="create tmp-only Switch/PC mapping evidence for /12")
    inspect_parser.add_argument("--baseline", type=Path, required=True)
    inspect_parser.add_argument("--switch-v21-zip", type=Path, required=True)
    inspect_parser.add_argument("--switch-v22-zip", type=Path, required=True)
    inspect_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_military_overlay_v1" / "inspect")
    verify = sub.add_parser("verify-inspect", help="verify an existing private inspect output")
    verify.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_military_overlay_v1" / "inspect")
    build = sub.add_parser("build", help="build a tmp-only PC-native /12 candidate")
    build.add_argument("--baseline", type=Path, required=True)
    build.add_argument("--switch-v21-zip", type=Path, required=True)
    build.add_argument("--switch-v22-zip", type=Path, required=True)
    build.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_military_overlay_v1" / "candidate")
    verify_candidate_parser = sub.add_parser("verify", help="verify a tmp-only /12 candidate")
    verify_candidate_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_military_overlay_v1" / "candidate")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "inspect":
            result = inspect(
                baseline=args.baseline,
                switch_v21_zip=args.switch_v21_zip,
                switch_v22_zip=args.switch_v22_zip,
                output_root=args.output_root,
            )
        elif args.command == "verify-inspect":
            result = verify_inspect(args.output_root)
        elif args.command == "build":
            result = build_candidate(
                baseline=args.baseline,
                switch_v21_zip=args.switch_v21_zip,
                switch_v22_zip=args.switch_v22_zip,
                output_root=args.output_root,
            )
        else:
            result = verify_candidate(args.output_root)
    except (OSError, OverlayError, lz4.LZ4Error, lz4.LinkError, codec.CodecError, trace.TraceError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print("game_install_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
