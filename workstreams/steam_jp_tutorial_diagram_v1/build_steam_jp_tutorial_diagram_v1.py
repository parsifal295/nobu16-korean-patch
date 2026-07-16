#!/usr/bin/env python3
"""Build a private, PC-native Korean candidate for the tutorial diagram.

Only the ``RES_JP/res_lang.bin`` outer entry ``/16`` (nested slot ``/0``,
texture ``/0``) is in scope.  The Switch v2.1/v2.2 archives are read-only
visual evidence: their decoded raster is never placed in this workstream or
in a game directory, and no Switch LINK, LZ4, G1T or BC3 bytes are copied.

``probe`` is intentionally available before a candidate mapping is accepted.
It writes decoded reference PNGs, a difference mask, and component evidence
only under the ignored ``tmp`` root.  Candidate creation remains fail-closed
until every source-to-PC text rectangle is explicitly mapped and reviewed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
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
import trace_bottom_return_button as trace  # noqa: E402
from build_steam_jp_title_images_v1 import resize_rgba_lanczos3_premultiplied  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-tutorial-diagram.candidate.v1"
TARGET_RESOURCE = "RES_JP/res_lang.bin"
OUTER_INDEX = 16
NESTED_RESOURCE_ID = 64
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
BASELINE = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.10.0-images-preview"
    r"\originals\RES_JP\res_lang.bin"
)
BASELINE_PIN = {
    "size": 154216023,
    "sha256": "0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0",
}
SWITCH_V21 = REPO / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.1.zip"
SWITCH_V22 = REPO / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.2.zip"
SWITCH_PINS: Mapping[str, Mapping[str, Any]] = {
    "v21": {
        "zip": {"size": 84369615, "sha256": "473213B0013FB24C812C517A147A15D51EFCBFCE975FBB51738EFC34F5E7B387"},
        "member": {"size": 86777150, "sha256": "C79B8F205CDAAF374B2F84F3AE4E385CE8498C5BA7CB8071DD2B9A178A27688D"},
    },
    "v22": {
        "zip": {"size": 83752794, "sha256": "5E6354069E38BE22E3B3C9272A6CEC8A4B4110DF2486B9A63E84D1058C35D7F7"},
        "member": {"size": 85548771, "sha256": "F179D9A89A7D20B51E26681208CA7186BDD1DC6B2F09FAF9CA8154B35933557F"},
    },
}


class TutorialDiagramError(ValueError):
    """Raised when an exact tutorial-diagram contract is violated."""


@dataclass(frozen=True)
class Atlas:
    rgba: bytes
    width: int
    height: int
    wrapper: bytes
    raw: bytes
    raw_prefix: bytes
    raw_suffix: bytes
    texture_payload: bytes
    platform: int


@dataclass(frozen=True)
class TutorialLink:
    """The one-slot, 32-byte-header LINK used by outer entry ``/16``."""

    fixed_header: bytes
    table_offset: int
    resource_id: int
    pre_slot: bytes
    wrapper: bytes
    tail: bytes
    slot_offset: int


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TutorialDiagramError(message)


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
    require(dict(actual) == dict(expected), f"{label} pin mismatch: expected={dict(expected)} actual={dict(actual)}")


def is_reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT) or path.is_symlink() or path.is_junction()
    except OSError:
        return True


def lexical_tmp_path(path: Path) -> tuple[Path, Path]:
    """Verify lexical tmp containment before any caller-controlled mkdir."""

    root = Path(os.path.abspath(TMP_ROOT))
    candidate = Path(os.path.abspath(path))
    try:
        common = os.path.commonpath((os.path.normcase(str(root)), os.path.normcase(str(candidate))))
    except ValueError as exc:
        raise TutorialDiagramError(f"output drive differs from tmp: {candidate}") from exc
    require(common == os.path.normcase(str(root)), f"output lexically escapes tmp: {candidate}")
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise TutorialDiagramError(f"output lexically escapes tmp: {candidate}") from exc
    return root, candidate


def ensure_tmp(path: Path, *, mkdir: bool = False) -> Path:
    """Return an ordinary checked tmp path; reject symlink/junction traversal."""

    root_lexical, candidate = lexical_tmp_path(path)
    require(not is_reparse(root_lexical), f"tmp root is a reparse point: {root_lexical}")
    root = root_lexical.resolve()
    require(not is_reparse(root), f"resolved tmp root is a reparse point: {root}")
    current = root
    for part in candidate.relative_to(root_lexical).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            require(not is_reparse(current), f"reparse point forbidden in output path: {current}")
            resolved = current.resolve()
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise TutorialDiagramError(f"output component escapes tmp: {current}") from exc
            current = resolved
        elif mkdir:
            current.mkdir(exist_ok=False)
            require(not is_reparse(current), f"new output component is a reparse point: {current}")
    return current


def create_fresh_output_root(path: Path) -> Path:
    parent = ensure_tmp(path.parent, mkdir=True)
    output = parent / path.name
    require(not output.exists() and not output.is_symlink(), f"refusing to overwrite output root: {output}")
    output.mkdir(exist_ok=False)
    require(not is_reparse(output), f"new output root is a reparse point: {output}")
    return output


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    raw_path = Path(path)
    parent = ensure_tmp(raw_path.parent, mkdir=True)
    path = ensure_tmp(parent / raw_path.name)
    require(not path.exists() and not path.is_symlink(), f"refusing to overwrite output: {path}")
    for source in forbidden:
        require(path.resolve() != source.resolve(), f"refusing to overwrite input: {source}")
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
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), forbidden=forbidden)


def parse_tutorial_link(blob: bytes, *, label: str) -> TutorialLink:
    """Parse, and later byte-preservingly rebuild, the observed ``/16`` LINK.

    Unlike title cards, its third u32 is the resource id (64), not a duplicate
    entry count.  It therefore must not be passed to the title-only helper.
    """

    require(len(blob) >= 64 and blob[:4] == b"LINK", f"{label} /16 is not LINK")
    count, table_offset, resource_id, aligned_end = (
        int.from_bytes(blob[4:8], "little"),
        int.from_bytes(blob[8:12], "little"),
        int.from_bytes(blob[12:16], "little"),
        int.from_bytes(blob[16:20], "little"),
    )
    require(
        (count, table_offset, resource_id, aligned_end) == (1, 32, NESTED_RESOURCE_ID, 64),
        f"{label} /16 LINK header contract changed",
    )
    require(blob[20:32] == b"\0" * 12, f"{label} /16 LINK extension changed")
    slot_offset = int.from_bytes(blob[32:36], "little")
    stored_size = int.from_bytes(blob[36:40], "little")
    require(slot_offset >= aligned_end and slot_offset + stored_size <= len(blob), f"{label} /16 slot range invalid")
    link = TutorialLink(
        fixed_header=blob[:32],
        table_offset=table_offset,
        resource_id=resource_id,
        pre_slot=blob[40:slot_offset],
        wrapper=blob[slot_offset : slot_offset + stored_size],
        tail=blob[slot_offset + stored_size :],
        slot_offset=slot_offset,
    )
    require(rebuild_tutorial_link(link, link.wrapper) == blob, f"{label} /16 LINK identity failed")
    return link


def rebuild_tutorial_link(link: TutorialLink, wrapper: bytes) -> bytes:
    output = bytearray(link.fixed_header)
    output.extend(b"\0" * 8)
    output.extend(link.pre_slot)
    require(len(output) == link.slot_offset, "tutorial LINK pre-slot placement drifted")
    output[link.table_offset : link.table_offset + 8] = len(output).to_bytes(4, "little") + len(wrapper).to_bytes(4, "little")
    output.extend(wrapper)
    output.extend(link.tail)
    rebuilt = bytes(output)
    # One shallow parse is sufficient to prove the new wrapper range; avoid
    # a recursive identity call through ``parse_tutorial_link`` here.
    require(rebuilt[:32] == link.fixed_header and rebuilt[40:link.slot_offset] == link.pre_slot, "tutorial LINK surrounding bytes changed")
    return rebuilt


def read_switch_resource(label: str, zip_path: Path) -> tuple[bytes, dict[str, Any]]:
    pin = SWITCH_PINS[label]
    zip_path = zip_path.resolve()
    require_spec(file_spec(zip_path), pin["zip"], f"Switch {label} ZIP")
    with zipfile.ZipFile(zip_path) as archive:
        try:
            info = archive.getinfo(SWITCH_MEMBER)
        except KeyError as exc:
            raise TutorialDiagramError(f"Switch {label} archive lacks {SWITCH_MEMBER}") from exc
        resource = archive.read(info)
    require_spec({"size": len(resource), "sha256": sha256_bytes(resource)}, pin["member"], f"Switch {label} resource")
    return resource, {"zip": dict(pin["zip"]), "member": dict(pin["member"])}


def extract_atlas_from_outer(outer_blob: bytes, *, expected_platform: int, label: str) -> Atlas:
    outer = lz4.parse_link(outer_blob)
    require(lz4.rebuild_link(outer) == outer_blob, f"{label} outer LINK identity failed")
    require(OUTER_INDEX < len(outer.entries), f"{label} has no outer /16")
    inner = parse_tutorial_link(outer.entries[OUTER_INDEX].data, label=label)
    wrapper = inner.wrapper
    wrapper_header, raw = lz4.decompress_wrapper(wrapper)
    require(wrapper_header.uncompressed_size == len(raw), f"{label} /16 wrapper size changed")
    g1t_header, textures = trace.parse_g1t(raw)
    require(g1t_header["platform"] == expected_platform and len(textures) == 1, f"{label} G1T platform/texture count changed")
    texture = textures[0]
    require(
        (texture.index, texture.format_code, texture.mip_count, texture.extra_version, texture.width)
        == (0, 0x5B, 1, 0x10, 2048),
        f"{label} G1T texture contract changed",
    )
    expected_height = 2048 if expected_platform == 10 else 1024
    require(texture.height == expected_height, f"{label} G1T height changed")
    rgba = codec.decode_bc3(texture.base_payload, texture.width, texture.height)
    return Atlas(
        rgba=rgba,
        width=texture.width,
        height=texture.height,
        wrapper=wrapper,
        raw=raw,
        raw_prefix=raw[: texture.payload_offset],
        raw_suffix=raw[texture.payload_offset + len(texture.base_payload) :],
        texture_payload=texture.base_payload,
        platform=g1t_header["platform"],
    )


def changed_block_components(left: bytes, right: bytes, width: int, height: int) -> tuple[list[dict[str, Any]], bytes]:
    """Return 4x4 BC3-block components plus a transparent Korean-only mask."""

    require(len(left) == len(right) == width * height * 4, "difference atlas shapes differ")
    blocks_wide, blocks_high = width // 4, height // 4
    changed: set[tuple[int, int]] = set()
    mask = bytearray(width * height * 4)
    for block_y in range(blocks_high):
        for block_x in range(blocks_wide):
            differs = False
            for local_y in range(4):
                start = ((block_y * 4 + local_y) * width + block_x * 4) * 4
                end = start + 16
                if left[start:end] != right[start:end]:
                    differs = True
                    break
            if differs:
                changed.add((block_x, block_y))
                for local_y in range(4):
                    start = ((block_y * 4 + local_y) * width + block_x * 4) * 4
                    mask[start : start + 16] = right[start : start + 16]

    # Labels can have letter gaps: merge nearby 4x4 blocks using an 8px halo.
    remaining = set(changed)
    components: list[dict[str, Any]] = []
    while remaining:
        seed = remaining.pop()
        pending = [seed]
        group = {seed}
        while pending:
            bx, by = pending.pop()
            neighbors = [point for point in tuple(remaining) if abs(point[0] - bx) <= 2 and abs(point[1] - by) <= 2]
            for neighbor in neighbors:
                remaining.remove(neighbor)
                group.add(neighbor)
                pending.append(neighbor)
        xs, ys = zip(*group)
        components.append({
            "block_count": len(group),
            "block_bbox": [min(xs), min(ys), max(xs), max(ys)],
            "pixel_bbox": [min(xs) * 4, min(ys) * 4, (max(xs) + 1) * 4, (max(ys) + 1) * 4],
        })
    components.sort(key=lambda value: (value["pixel_bbox"][1], value["pixel_bbox"][0]))
    return components, bytes(mask)


def crop_rgba(rgba: bytes, width: int, height: int, rect: tuple[int, int, int, int]) -> bytes:
    left, top, right, bottom = rect
    require(0 <= left < right <= width and 0 <= top < bottom <= height, f"crop out of range: {rect}")
    output = bytearray((right - left) * (bottom - top) * 4)
    for y in range(top, bottom):
        source = (y * width + left) * 4
        target = ((y - top) * (right - left)) * 4
        output[target : target + (right - left) * 4] = rgba[source : source + (right - left) * 4]
    return bytes(output)


def paste_rgba(canvas: bytearray, canvas_width: int, canvas_height: int, x: int, y: int, rgba: bytes, width: int, height: int) -> None:
    require(0 <= x <= canvas_width - width and 0 <= y <= canvas_height - height, "paste out of range")
    for row in range(height):
        source = row * width * 4
        target = ((y + row) * canvas_width + x) * 4
        canvas[target : target + width * 4] = rgba[source : source + width * 4]


def horizontal_contact(panels: Sequence[bytes], width: int, height: int, *, gap: int = 4) -> tuple[bytes, int, int]:
    require(panels, "contact sheet requires at least one panel")
    canvas_width = len(panels) * width + (len(panels) + 1) * gap
    canvas_height = height + gap * 2
    canvas = bytearray(bytes((16, 16, 16, 255)) * (canvas_width * canvas_height))
    for index, panel in enumerate(panels):
        require(len(panel) == width * height * 4, "contact panel dimensions differ")
        paste_rgba(canvas, canvas_width, canvas_height, gap + index * (width + gap), gap, panel, width, height)
    return bytes(canvas), canvas_width, canvas_height


def build_probe(
    *,
    baseline: Path,
    switch_v21: Path,
    switch_v22: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Write private decoded evidence only; it never writes a candidate."""

    baseline = baseline.resolve()
    require_spec(file_spec(baseline), BASELINE_PIN, "Steam JP 1.1.7/v0.9 baseline")
    output_root = create_fresh_output_root(output_root)
    switch21_blob, switch21_spec = read_switch_resource("v21", switch_v21)
    switch22_blob, switch22_spec = read_switch_resource("v22", switch_v22)
    pc = extract_atlas_from_outer(baseline.read_bytes(), expected_platform=10, label="Steam JP baseline")
    sw_jp = extract_atlas_from_outer(switch21_blob, expected_platform=16, label="Switch v2.1")
    sw_ko = extract_atlas_from_outer(switch22_blob, expected_platform=16, label="Switch v2.2")
    components, mask = changed_block_components(sw_jp.rgba, sw_ko.rgba, sw_jp.width, sw_jp.height)
    require(components, "Switch v2.1->v2.2 tutorial atlas has no changed BC3 blocks")

    private = ensure_tmp(output_root / "private", mkdir=True)
    paths = {
        "switch_v21_jp": private / "tutorial_switch_v21_jp.png",
        "switch_v22_ko": private / "tutorial_switch_v22_ko.png",
        "switch_v21_to_v22_ko_blocks": private / "tutorial_switch_v21_to_v22_ko_blocks.png",
        "steam_jp": private / "tutorial_steam_jp.png",
    }
    forbidden = (baseline, switch_v21.resolve(), switch_v22.resolve())
    for key, path in paths.items():
        source, width, height = {
            "switch_v21_jp": (sw_jp.rgba, sw_jp.width, sw_jp.height),
            "switch_v22_ko": (sw_ko.rgba, sw_ko.width, sw_ko.height),
            "switch_v21_to_v22_ko_blocks": (mask, sw_ko.width, sw_ko.height),
            "steam_jp": (pc.rgba, pc.width, pc.height),
        }[key]
        atomic_write(path, codec.encode_rgba_png(source, width, height), forbidden=forbidden)

    # Reference-only registration aids.  They are deliberately cropped to
    # diagram panels, never to title/logo outer entries, and never leave tmp.
    top_switch_rect = (0, 0, 776, 437)
    top_pc_rect = (1204, 0, 1974, 437)
    faction_switch_rect = (780, 309, 1296, 600)
    faction_pc_rect = (1204, 440, 1974, 876)
    contacts: dict[str, Path] = {}
    for name, sw_rect, pc_rect in (
        ("top", top_switch_rect, top_pc_rect),
        ("faction", faction_switch_rect, faction_pc_rect),
    ):
        panel_width, panel_height = pc_rect[2] - pc_rect[0], pc_rect[3] - pc_rect[1]
        sw_jp_panel = crop_rgba(sw_jp.rgba, sw_jp.width, sw_jp.height, sw_rect)
        sw_ko_panel = crop_rgba(sw_ko.rgba, sw_ko.width, sw_ko.height, sw_rect)
        pc_panel = crop_rgba(pc.rgba, pc.width, pc.height, pc_rect)
        source_width, source_height = sw_rect[2] - sw_rect[0], sw_rect[3] - sw_rect[1]
        sw_jp_scaled = resize_rgba_lanczos3_premultiplied(sw_jp_panel, source_width, source_height, panel_width, panel_height)
        sw_ko_scaled = resize_rgba_lanczos3_premultiplied(sw_ko_panel, source_width, source_height, panel_width, panel_height)
        contact, contact_width, contact_height = horizontal_contact((sw_jp_scaled, sw_ko_scaled, pc_panel), panel_width, panel_height)
        path = private / f"{name}_reference_contact.png"
        atomic_write(path, codec.encode_rgba_png(contact, contact_width, contact_height), forbidden=forbidden)
        contacts[name] = path

    report = {
        "schema": "nobu16.kr.steam-jp-tutorial-diagram.probe.v1",
        "file_only": True,
        "game_install_modified": False,
        "candidate_created": False,
        "scope": {
            "target_resource": TARGET_RESOURCE,
            "outer_entry": OUTER_INDEX,
            "nested_slot": 0,
            "texture": 0,
            "title_or_logo_outer_entries_touched": [],
            "switch_payload_copied": False,
        },
        "inputs": {
            "steam_jp_baseline": dict(BASELINE_PIN),
            "switch_v21": switch21_spec,
            "switch_v22": switch22_spec,
        },
        "atlas": {
            "steam_jp": {"platform": pc.platform, "dimensions": [pc.width, pc.height], "rgba_sha256": sha256_bytes(pc.rgba)},
            "switch_v21": {"platform": sw_jp.platform, "dimensions": [sw_jp.width, sw_jp.height], "rgba_sha256": sha256_bytes(sw_jp.rgba)},
            "switch_v22": {"platform": sw_ko.platform, "dimensions": [sw_ko.width, sw_ko.height], "rgba_sha256": sha256_bytes(sw_ko.rgba)},
        },
        "switch_changed_bc3_components": components,
        "private_decoded_reference": {
            "root": str(private),
            "paths": {key: str(value) for key, value in paths.items()},
            "png_sha256": {key: sha256_file(value) for key, value in paths.items()},
            "not_for_git_or_release": True,
        },
        "private_registration_contacts": {
            "paths": {key: str(value) for key, value in contacts.items()},
            "png_sha256": {key: sha256_file(value) for key, value in contacts.items()},
            "panel_legend": ["Switch v2.1 JP resized", "Switch v2.2 KO resized", "Steam JP baseline"],
            "not_for_git_or_release": True,
        },
    }
    write_json(ensure_tmp(output_root / "probe_report.json"), report, forbidden=forbidden)
    return report


# These are atlas-panel registrations, not title or logo paths.  The two
# registrations were checked against the decoded Switch v2.1/v2.2 reference
# and Steam JP baseline in the private probe contact sheets.  The candidate
# applies only blocks whose *resized Switch JP vs KO* pixels differ, so the
# non-text art in each panel remains native Steam bytes.
PANEL_MAPPINGS: tuple[Mapping[str, Any], ...] = (
    {
        "name": "progress_flow",
        "switch_rect": (0, 0, 776, 437),
        "pc_rect": (1204, 0, 1974, 437),
        "labels": ("진행", "내정", "전투", "천하통일"),
    },
    {
        "name": "faction_hierarchy",
        "switch_rect": (780, 309, 1296, 600),
        "pc_rect": (1204, 440, 1974, 876),
        "labels": ("세력", "성", "군", "무장"),
    },
)


def panel_scaled_rgba(atlas: Atlas, mapping: Mapping[str, Any]) -> tuple[bytes, int, int]:
    sw_rect = tuple(mapping["switch_rect"])
    pc_rect = tuple(mapping["pc_rect"])
    source_width, source_height = sw_rect[2] - sw_rect[0], sw_rect[3] - sw_rect[1]
    target_width, target_height = pc_rect[2] - pc_rect[0], pc_rect[3] - pc_rect[1]
    source = crop_rgba(atlas.rgba, atlas.width, atlas.height, sw_rect)
    # Full-panel Lanczos (four 770px-wide panels per build) is needlessly
    # expensive in pure Python.  The Japanese and PC diagrams are already
    # registered at native authored resolutions; a deterministic nearest map
    # keeps the candidate bounded to the decoded label blocks and leaves final
    # BC3 filtering to the same native PC texture route.
    scaled = resize_rgba_nearest(source, source_width, source_height, target_width, target_height)
    return scaled, target_width, target_height


def resize_rgba_nearest(source: bytes, source_width: int, source_height: int, target_width: int, target_height: int) -> bytes:
    require(len(source) == source_width * source_height * 4, "nearest resize source dimensions differ")
    require(source_width > 0 and source_height > 0 and target_width > 0 and target_height > 0, "nearest resize dimensions must be positive")
    xmap = [min(source_width - 1, (x * source_width) // target_width) for x in range(target_width)]
    output = bytearray(target_width * target_height * 4)
    for y in range(target_height):
        source_y = min(source_height - 1, (y * source_height) // target_height)
        source_row = source_y * source_width * 4
        target_row = y * target_width * 4
        for x, source_x in enumerate(xmap):
            source_offset = source_row + source_x * 4
            target_offset = target_row + x * 4
            output[target_offset : target_offset + 4] = source[source_offset : source_offset + 4]
    return bytes(output)


def changed_bc3_blocks(left: bytes, right: bytes, width: int, height: int) -> set[tuple[int, int]]:
    require(len(left) == len(right) == width * height * 4, "block comparison dimensions differ")
    result: set[tuple[int, int]] = set()
    for by in range((height + 3) // 4):
        for bx in range((width + 3) // 4):
            differs = False
            for local_y in range(4):
                y = by * 4 + local_y
                if y >= height:
                    break
                for local_x in range(4):
                    x = bx * 4 + local_x
                    if x >= width:
                        break
                    offset = (y * width + x) * 4
                    if left[offset : offset + 4] != right[offset : offset + 4]:
                        differs = True
                        break
                if differs:
                    break
            if differs:
                result.add((bx, by))
    return result


def block_bbox(blocks: Iterable[tuple[int, int]]) -> list[int] | None:
    values = tuple(blocks)
    if not values:
        return None
    xs, ys = zip(*values)
    return [min(xs), min(ys), max(xs) + 1, max(ys) + 1]


def overwrite_block(
    target: bytearray,
    target_width: int,
    target_block_x: int,
    target_block_y: int,
    source: bytes,
    source_width: int,
    source_block_x: int,
    source_block_y: int,
) -> None:
    for local_y in range(4):
        source_offset = ((source_block_y * 4 + local_y) * source_width + source_block_x * 4) * 4
        target_offset = ((target_block_y * 4 + local_y) * target_width + target_block_x * 4) * 4
        target[target_offset : target_offset + 16] = source[source_offset : source_offset + 16]


def registration_metrics(reference: bytes, baseline: bytes, width: int, height: int, excluded_blocks: set[tuple[int, int]]) -> dict[str, Any]:
    """Quantify native-PC vs resized-JP agreement outside text-change blocks."""

    require(len(reference) == len(baseline) == width * height * 4, "registration shapes differ")
    samples = 0
    absolute = 0
    maximum = 0
    # Four-pixel sampling matches the BC3 decision grid and avoids making the
    # registration metric the dominant cost of a candidate build.
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            if (x // 4, y // 4) in excluded_blocks:
                continue
            offset = (y * width + x) * 4
            for channel in range(4):
                delta = abs(reference[offset + channel] - baseline[offset + channel])
                absolute += delta
                maximum = max(maximum, delta)
                samples += 1
    require(samples > 0, "registration unexpectedly excludes every pixel")
    return {
        "sampled_channels": samples,
        "mean_absolute_channel_error": round(absolute / samples, 6),
        "max_absolute_channel_error": maximum,
    }


def compose_requested_rgba(pc: Atlas, sw_jp: Atlas, sw_ko: Atlas) -> tuple[bytes, set[tuple[int, int]], list[dict[str, Any]]]:
    """Create a requested native-PC raster by copying only proven text blocks.

    Each Korean source panel is decoded then deterministically rescaled into
    the already-validated PC panel geometry.  The *source delta* decides
    which BC3 blocks may change; complete source panels are never copied.
    """

    requested = bytearray(pc.rgba)
    allowed: set[tuple[int, int]] = set()
    rows: list[dict[str, Any]] = []
    for mapping in PANEL_MAPPINGS:
        pc_rect = tuple(mapping["pc_rect"])
        require(pc_rect[0] % 4 == 0 and pc_rect[1] % 4 == 0, f"{mapping['name']} PC origin is not BC3 aligned")
        source_jp, width, height = panel_scaled_rgba(sw_jp, mapping)
        source_ko, ko_width, ko_height = panel_scaled_rgba(sw_ko, mapping)
        require((ko_width, ko_height) == (width, height), f"{mapping['name']} Korean panel geometry differs")
        diff_blocks = changed_bc3_blocks(source_jp, source_ko, width, height)
        require(diff_blocks, f"{mapping['name']} has no Korean source delta")
        baseline_panel = crop_rgba(pc.rgba, pc.width, pc.height, pc_rect)
        metrics = registration_metrics(source_jp, baseline_panel, width, height, diff_blocks)
        target_blocks: set[tuple[int, int]] = set()
        for local_x, local_y in diff_blocks:
            require(local_x * 4 + 4 <= width and local_y * 4 + 4 <= height, f"{mapping['name']} source delta touches partial panel block")
            global_x = pc_rect[0] // 4 + local_x
            global_y = pc_rect[1] // 4 + local_y
            # Target blocks must remain completely inside the established PC
            # panel; any edge drift is a mapping failure, not a crop request.
            require(
                pc_rect[0] <= global_x * 4 and global_x * 4 + 4 <= pc_rect[2]
                and pc_rect[1] <= global_y * 4 and global_y * 4 + 4 <= pc_rect[3],
                f"{mapping['name']} target delta touches panel edge",
            )
            require((global_x, global_y) not in allowed, f"panel target blocks overlap at {(global_x, global_y)}")
            overwrite_block(requested, pc.width, global_x, global_y, source_ko, width, local_x, local_y)
            target_blocks.add((global_x, global_y))
        allowed.update(target_blocks)
        rows.append({
            "name": mapping["name"],
            "labels": list(mapping["labels"]),
            "switch_rect": list(mapping["switch_rect"]),
            "pc_rect": list(pc_rect),
            "resized_dimensions": [width, height],
            "resampler": "deterministic_nearest_native_panel_registration",
            "source_changed_bc3_block_count": len(diff_blocks),
            "source_changed_bc3_block_bbox": block_bbox(diff_blocks),
            "pc_allowed_bc3_block_count": len(target_blocks),
            "pc_allowed_bc3_block_bbox": block_bbox(target_blocks),
            "registration_outside_text_blocks": metrics,
            "switch_jp_resized_rgba_sha256": sha256_bytes(source_jp),
            "switch_ko_resized_rgba_sha256": sha256_bytes(source_ko),
        })
    return bytes(requested), allowed, rows


def requested_changes_outside_blocks(before: bytes, after: bytes, width: int, allowed: set[tuple[int, int]]) -> int:
    require(len(before) == len(after), "requested comparison shapes differ")
    escaped = 0
    for pixel in range(len(before) // 4):
        offset = pixel * 4
        if before[offset : offset + 4] != after[offset : offset + 4]:
            x, y = pixel % width, pixel // width
            if (x // 4, y // 4) not in allowed:
                escaped += 1
    return escaped


def encode_selected_bc3_blocks(
    requested: bytes,
    width: int,
    height: int,
    template: bytes,
    allowed: set[tuple[int, int]],
) -> tuple[bytes, int, int]:
    """Re-encode only explicitly allowed blocks; copy every other BC3 byte.

    The general codec's full-atlas equality scan is deliberately avoided here:
    this candidate already proves that requested RGBA changes are inside the
    bounded block set, so untouched blocks can remain byte-identical without
    decoding/re-encoding the entire 2048² atlas.
    """

    require(width % 4 == 0 and height % 4 == 0, "tutorial atlas must be BC3 block aligned")
    blocks_wide, blocks_high = width // 4, height // 4
    require(len(template) == blocks_wide * blocks_high * 16, "template BC3 dimensions differ")
    output = bytearray(template)
    encoded = 0
    preserved = blocks_wide * blocks_high - len(allowed)
    for block_x, block_y in sorted(allowed):
        require(0 <= block_x < blocks_wide and 0 <= block_y < blocks_high, f"allowed BC3 block out of range: {(block_x, block_y)}")
        index = block_y * blocks_wide + block_x
        before = template[index * 16 : index * 16 + 16]
        requested_block = codec.extract_rgba_block(requested, width, height, block_x, block_y)
        if codec.decode_bc3_block(before) == requested_block:
            preserved += 1
            continue
        output[index * 16 : index * 16 + 16] = codec.encode_bc3_block(requested_block)
        encoded += 1
    return bytes(output), preserved, encoded


def parse_candidate_atlas(candidate_blob: bytes, *, label: str) -> tuple[lz4.LinkArchive, TutorialLink, lz4.WrapperHeader, Atlas]:
    outer = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(outer) == candidate_blob, f"{label} outer LINK identity failed")
    inner = parse_tutorial_link(outer.entries[OUTER_INDEX].data, label=label)
    header, raw = lz4.decompress_wrapper(inner.wrapper)
    atlas = extract_atlas_from_outer(candidate_blob, expected_platform=10, label=label)
    require(raw == atlas.raw, f"{label} wrapper extraction drifted")
    return outer, inner, header, atlas


def build_candidate(
    *,
    baseline: Path,
    switch_v21: Path,
    switch_v22: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Build a strictly tmp-only PC native tutorial-diagram candidate."""

    baseline = baseline.resolve()
    require_spec(file_spec(baseline), BASELINE_PIN, "Steam JP 1.1.7/v0.9 baseline")
    output_root = create_fresh_output_root(output_root)
    print("stage=baseline", flush=True)
    baseline_blob = baseline.read_bytes()
    outer_before, inner_before, wrapper_header, pc = parse_candidate_atlas(baseline_blob, label="Steam JP baseline")
    outer_hashes_before = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(outer_before.entries)}
    print("stage=baseline_decoded", flush=True)
    switch21_blob, switch21_spec = read_switch_resource("v21", switch_v21)
    switch22_blob, switch22_spec = read_switch_resource("v22", switch_v22)
    sw_jp = extract_atlas_from_outer(switch21_blob, expected_platform=16, label="Switch v2.1")
    sw_ko = extract_atlas_from_outer(switch22_blob, expected_platform=16, label="Switch v2.2")
    print("stage=switch_decoded", flush=True)
    requested, allowed_blocks, panels = compose_requested_rgba(pc, sw_jp, sw_ko)
    require(allowed_blocks, "no allowed tutorial blocks were derived")
    escaped_pixels = requested_changes_outside_blocks(pc.rgba, requested, pc.width, allowed_blocks)
    require(escaped_pixels == 0, "requested pixels escaped allowed Korean text blocks")
    print(f"stage=requested allowed_blocks={len(allowed_blocks)}", flush=True)

    rebuilt_payload, preserved_blocks, encoded_blocks = encode_selected_bc3_blocks(requested, pc.width, pc.height, pc.texture_payload, allowed_blocks)
    print(f"stage=bc3 encoded_blocks={encoded_blocks}", flush=True)
    rebuilt_raw = pc.raw_prefix + rebuilt_payload + pc.raw_suffix
    require(rebuilt_raw[: len(pc.raw_prefix)] == pc.raw_prefix and rebuilt_raw[len(pc.raw_prefix) + len(rebuilt_payload) :] == pc.raw_suffix, "G1T bytes outside texture payload changed")
    rebuilt_wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, wrapper_header)
    _, wrapper_roundtrip = lz4.decompress_wrapper(rebuilt_wrapper)
    require(wrapper_roundtrip == rebuilt_raw, "tutorial wrapper LZ4 round-trip failed")
    print("stage=lz4", flush=True)
    rebuilt_inner = rebuild_tutorial_link(inner_before, rebuilt_wrapper)
    candidate_blob = lz4.rebuild_link(outer_before, {OUTER_INDEX: rebuilt_inner})

    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    atomic_write(candidate_path, candidate_blob, forbidden=(baseline, switch_v21.resolve(), switch_v22.resolve()))
    print("stage=candidate_written", flush=True)
    candidate_outer, candidate_inner, _, candidate = parse_candidate_atlas(candidate_path.read_bytes(), label="candidate")
    outer_hashes_after = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(candidate_outer.entries)}
    require(len(candidate_outer.entries) == len(outer_before.entries), "candidate outer LINK count changed")
    for index, before_hash in outer_hashes_before.items():
        if index != str(OUTER_INDEX):
            require(outer_hashes_after[index] == before_hash, f"candidate changed unrelated outer /{index}")
    require(candidate_inner.fixed_header == inner_before.fixed_header and candidate_inner.pre_slot == inner_before.pre_slot and candidate_inner.tail == inner_before.tail, "candidate changed /16 bytes outside wrapper")
    require(candidate.raw_prefix == pc.raw_prefix and candidate.raw_suffix == pc.raw_suffix, "candidate changed G1T bytes outside texture payload")

    changed_blocks: set[tuple[int, int]] = set()
    blocks_wide = pc.width // 4
    for index in range(len(pc.texture_payload) // 16):
        before = pc.texture_payload[index * 16 : index * 16 + 16]
        after = candidate.texture_payload[index * 16 : index * 16 + 16]
        if before != after:
            changed_blocks.add((index % blocks_wide, index // blocks_wide))
    require(changed_blocks.issubset(allowed_blocks), "candidate BC3 changed outside allowed Korean text blocks")
    require(changed_blocks, "candidate has no BC3 block changes")
    baseline_after = file_spec(baseline)
    require_spec(baseline_after, BASELINE_PIN, "Steam JP baseline after build")

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
            "texture": 0,
            "title_or_logo_outer_entries_touched": [],
            "all_other_outer_entries_byte_preserved": True,
            "all_non_text_bc3_blocks_byte_preserved": True,
        },
        "inputs": {
            "steam_jp_baseline": {"before": dict(BASELINE_PIN), "after": baseline_after, "unchanged": baseline_after == BASELINE_PIN},
            "switch_v21": switch21_spec,
            "switch_v22": switch22_spec,
        },
        "panel_mappings": panels,
        "bc3": {
            "total_blocks": len(pc.texture_payload) // 16,
            "allowed_korean_text_blocks": len(allowed_blocks),
            "allowed_korean_text_block_bbox": block_bbox(allowed_blocks),
            "candidate_changed_blocks": len(changed_blocks),
            "candidate_changed_block_bbox": block_bbox(changed_blocks),
            "candidate_changes_subset_of_allowed_text_blocks": changed_blocks.issubset(allowed_blocks),
            "requested_changed_pixels_outside_allowed_text_blocks": escaped_pixels,
            "preserved_template_blocks": preserved_blocks,
            "deterministically_reencoded_blocks": encoded_blocks,
            "baseline_payload_sha256": sha256_bytes(pc.texture_payload),
            "candidate_payload_sha256": sha256_bytes(candidate.texture_payload),
        },
        "preservation": {
            "outer_entry_sha256_before": outer_hashes_before,
            "outer_entry_sha256_after": outer_hashes_after,
            "all_non_16_outer_entries_byte_preserved": all(outer_hashes_before[str(index)] == outer_hashes_after[str(index)] for index in range(len(outer_before.entries)) if index != OUTER_INDEX),
            "outer_3_title_byte_preserved": outer_hashes_before["3"] == outer_hashes_after["3"],
            "outer_24_title_additional_content_byte_preserved": outer_hashes_before["24"] == outer_hashes_after["24"],
            "tutorial_link_non_wrapper_bytes_preserved": True,
            "g1t_non_texture_bytes_preserved": True,
        },
        "candidate": {
            "path": str(candidate_path),
            **candidate_spec,
            "under_tmp": True,
            "outer_parse_valid": True,
            "tutorial_link_parse_valid": True,
            "g1t_parse_valid": True,
        },
        "private_payload_policy": {
            "contains_complete_game_resource": True,
            "contains_third_party_translation_pixels": True,
            "git_publish_allowed": False,
            "output_must_remain_under_tmp": True,
            "switch_link_lz4_g1t_bc3_payload_copied": False,
        },
    }
    write_json(ensure_tmp(output_root / "build_report.json"), report, forbidden=(baseline, switch_v21.resolve(), switch_v22.resolve(), candidate_path))
    return report


def verify_output(output_root: Path) -> dict[str, Any]:
    output_root = ensure_tmp(output_root, mkdir=True)
    report_path = ensure_tmp(output_root / "build_report.json")
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TutorialDiagramError(f"invalid candidate report: {exc}") from exc
    require(report.get("schema") == SCHEMA, "candidate report schema mismatch")
    require(report.get("file_only") is True and report.get("game_install_modified") is False, "candidate violates file-only scope")
    candidate = report.get("candidate")
    require(isinstance(candidate, Mapping) and file_spec(candidate_path) == {"size": candidate.get("size"), "sha256": candidate.get("sha256")}, "candidate hash differs from report")
    outer, inner, _, atlas = parse_candidate_atlas(candidate_path.read_bytes(), label="candidate verification")
    preservation = report.get("preservation")
    require(isinstance(preservation, Mapping), "candidate preservation proof missing")
    before = preservation.get("outer_entry_sha256_before")
    after = preservation.get("outer_entry_sha256_after")
    observed = {str(index): sha256_bytes(entry.data) for index, entry in enumerate(outer.entries)}
    require(isinstance(before, Mapping) and isinstance(after, Mapping) and observed == after, "candidate outer hashes mismatch")
    require(before.get("3") == after.get("3") and before.get("24") == after.get("24"), "candidate unexpectedly changed title/logo paths")
    bc3 = report.get("bc3")
    require(isinstance(bc3, Mapping) and int(bc3.get("candidate_changed_blocks", 0)) > 0 and bc3.get("candidate_changes_subset_of_allowed_text_blocks") is True, "candidate text-block proof missing")
    require((atlas.width, atlas.height, atlas.platform) == (2048, 2048, 10), "candidate PC G1T geometry drifted")
    require(inner.resource_id == NESTED_RESOURCE_ID, "candidate tutorial resource id drifted")
    return {"status": "PASS", "candidate": file_spec(candidate_path), "game_install_modified": False}


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


def visual_qa(*, baseline: Path, switch_v21: Path, switch_v22: Path, output_root: Path) -> dict[str, Any]:
    """Create a private, four-column contact sheet for human visual QA."""

    output_root = ensure_tmp(output_root, mkdir=True)
    baseline = baseline.resolve()
    require_spec(file_spec(baseline), BASELINE_PIN, "Steam JP baseline for visual QA")
    candidate_path = ensure_tmp(output_root / "candidate" / "RES_JP" / "res_lang.bin")
    _, _, _, pc = parse_candidate_atlas(baseline.read_bytes(), label="Steam JP visual baseline")
    _, _, _, candidate = parse_candidate_atlas(candidate_path.read_bytes(), label="candidate visual QA")
    switch21_blob, switch21_spec = read_switch_resource("v21", switch_v21)
    switch22_blob, switch22_spec = read_switch_resource("v22", switch_v22)
    sw_jp = extract_atlas_from_outer(switch21_blob, expected_platform=16, label="Switch v2.1 visual QA")
    sw_ko = extract_atlas_from_outer(switch22_blob, expected_platform=16, label="Switch v2.2 visual QA")

    width = 770
    gutter = 4
    row_heights = [437, 436]
    canvas_width = width * 4 + gutter * 5
    canvas_height = sum(row_heights) + gutter * 3
    canvas = bytearray(bytes((16, 16, 16, 255)) * (canvas_width * canvas_height))
    colors = ((224, 64, 64, 255), (64, 208, 96, 255), (232, 196, 56, 255), (48, 208, 232, 255))
    rows: list[dict[str, Any]] = []
    y = gutter
    for mapping, row_height in zip(PANEL_MAPPINGS, row_heights):
        sw_jp_panel, panel_width, panel_height = panel_scaled_rgba(sw_jp, mapping)
        sw_ko_panel, _, _ = panel_scaled_rgba(sw_ko, mapping)
        pc_rect = tuple(mapping["pc_rect"])
        pc_panel = crop_rgba(pc.rgba, pc.width, pc.height, pc_rect)
        candidate_panel = crop_rgba(candidate.rgba, candidate.width, candidate.height, pc_rect)
        require((panel_width, panel_height) == (width, row_height), f"visual QA panel geometry drifted for {mapping['name']}")
        panel_blocks = changed_bc3_blocks(pc_panel, candidate_panel, panel_width, panel_height)
        require(panel_blocks, f"visual QA candidate has no delta for {mapping['name']}")
        for index, (panel, color) in enumerate(zip((sw_jp_panel, sw_ko_panel, pc_panel, candidate_panel), colors)):
            marked = bytearray(panel)
            add_border(marked, panel_width, panel_height, color)
            paste_rgba(canvas, canvas_width, canvas_height, gutter + index * (width + gutter), y, marked, panel_width, panel_height)
        rows.append({
            "name": mapping["name"],
            "labels": list(mapping["labels"]),
            "pc_candidate_changed_block_count": len(panel_blocks),
            "pc_candidate_changed_block_bbox": block_bbox(panel_blocks),
        })
        y += row_height + gutter
    contact_path = ensure_tmp(output_root / "private" / "tutorial_diagram_contact_sheet.png")
    atomic_write(contact_path, codec.encode_rgba_png(bytes(canvas), canvas_width, canvas_height), forbidden=(baseline, switch_v21.resolve(), switch_v22.resolve(), candidate_path))
    report = {
        "schema": "nobu16.kr.steam-jp-tutorial-diagram.visual-qa.v1",
        "file_only": True,
        "game_install_modified": False,
        "contact_sheet": {
            "path": str(contact_path),
            "sha256": sha256_file(contact_path),
            "dimensions": [canvas_width, canvas_height],
            "private_only": True,
            "panel_legend": {"red": "Switch v2.1 JP resized", "green": "Switch v2.2 KO resized", "yellow": "Steam JP baseline", "cyan": "Steam JP Korean candidate"},
        },
        "inputs": {"switch_v21": switch21_spec, "switch_v22": switch22_spec, "baseline": dict(BASELINE_PIN), "candidate": file_spec(candidate_path)},
        "rows": rows,
        "title_or_logo_outer_entries_touched": [],
    }
    write_json(ensure_tmp(output_root / "visual_qa.json"), report, forbidden=(baseline, switch_v21.resolve(), switch_v22.resolve(), candidate_path))
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    probe = subcommands.add_parser("probe", help="decode only private v2.1/v2.2 reference evidence")
    probe.add_argument("--baseline", type=Path, default=BASELINE)
    probe.add_argument("--switch-v21-zip", type=Path, default=SWITCH_V21)
    probe.add_argument("--switch-v22-zip", type=Path, default=SWITCH_V22)
    probe.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_tutorial_diagram_v1" / "probe")
    build = subcommands.add_parser("build", help="write a private PC-native /16 candidate below tmp")
    build.add_argument("--baseline", type=Path, default=BASELINE)
    build.add_argument("--switch-v21-zip", type=Path, default=SWITCH_V21)
    build.add_argument("--switch-v22-zip", type=Path, default=SWITCH_V22)
    build.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_tutorial_diagram_v1" / "run")
    verify = subcommands.add_parser("verify", help="reparse a previously built private candidate")
    verify.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_tutorial_diagram_v1" / "run")
    visual = subcommands.add_parser("visual-qa", help="write a private four-column visual QA contact sheet")
    visual.add_argument("--baseline", type=Path, default=BASELINE)
    visual.add_argument("--switch-v21-zip", type=Path, default=SWITCH_V21)
    visual.add_argument("--switch-v22-zip", type=Path, default=SWITCH_V22)
    visual.add_argument("--output-root", type=Path, default=TMP_ROOT / "steam_jp_tutorial_diagram_v1" / "run")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "probe":
        report = build_probe(
            baseline=args.baseline,
            switch_v21=args.switch_v21_zip,
            switch_v22=args.switch_v22_zip,
            output_root=args.output_root,
        )
        print(f"probe={args.output_root}")
        print(f"switch_changed_components={len(report['switch_changed_bc3_components'])}")
        print("game_install_modified=false")
        return 0
    if args.command == "build":
        report = build_candidate(
            baseline=args.baseline,
            switch_v21=args.switch_v21_zip,
            switch_v22=args.switch_v22_zip,
            output_root=args.output_root,
        )
        print(f"candidate={report['candidate']['path']}")
        print(f"candidate_sha256={report['candidate']['sha256']}")
        print(f"candidate_changed_bc3_blocks={report['bc3']['candidate_changed_blocks']}")
        print("game_install_modified=false")
        return 0
    if args.command == "verify":
        report = verify_output(args.output_root)
        print(f"status={report['status']}")
        print(f"candidate_sha256={report['candidate']['sha256']}")
        print("game_install_modified=false")
        return 0
    if args.command == "visual-qa":
        report = visual_qa(
            baseline=args.baseline,
            switch_v21=args.switch_v21_zip,
            switch_v22=args.switch_v22_zip,
            output_root=args.output_root,
        )
        print(f"contact_sheet={report['contact_sheet']['path']}")
        print("game_install_modified=false")
        return 0
    raise TutorialDiagramError(f"unknown command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (TutorialDiagramError, codec.CodecError, lz4.LZ4Error, lz4.LinkError, trace.TraceError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
