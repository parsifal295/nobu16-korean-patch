#!/usr/bin/env python3
"""Read-only codec audit for Steam JP ``RES_JP/res_lang.bin /1``.

This workstream is deliberately limited to the six startup/boot-warning G1T
textures used by the PC Steam Japanese route.  It identifies the exact
``GT1G0600`` ``format_code == 0x01`` variant observed in Steam 1.1.7 and
proves a *narrow* decoder:

* PC platform field is ``0x0A``;
* texture payload is exactly ``width * height * 4`` bytes;
* bytes are linear, row-major ``RGBA8`` for this observed variant; and
* decode -> encode is byte-identical for every payload.

The tool never writes a game resource.  ``audit`` emits only source-free
metadata (hashes, sizes, and structural facts).  ``private-preview`` may
derive PNG previews only below the repository's ignored ``tmp`` directory;
those previews are intentionally never written into this workstream or a
release candidate.

This is empirical support for one NOBU16 PC layout, not a general G1T format
specification.  It must not be used to copy Switch/SC resources into PC JP.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


WORKSTREAM = Path(__file__).resolve().parent
PROJECT_ROOT = WORKSTREAM.parents[1]
TOOLS = PROJECT_ROOT / "tools"
TMP_ROOT = PROJECT_ROOT / "tmp"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-boot-warning-codec-audit.v1"
DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_VALIDATION = WORKSTREAM / "validation.v1.json"
DEFAULT_PREVIEW_DIR = TMP_ROOT / "steam_jp_boot_warning_codec_audit_v1" / "private_preview"
RESOURCE_RELATIVE_PATH = Path("RES_JP") / "res_lang.bin"
OUTER_ENTRY_INDEX = 1
PC_PLATFORM = 0x0A
FORMAT_RGBA8 = 0x01
G1T_MAGIC = b"GT1G0600"


class AuditError(ValueError):
    """Raised when the narrow, audited layout is not present."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256_bytes(data: bytes | memoryview) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def stable_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def align_up(value: int, alignment: int) -> int:
    require(alignment > 0 and not alignment & (alignment - 1), "alignment must be a power of two")
    return (value + alignment - 1) & -alignment


@dataclass(frozen=True)
class InnerEntry:
    index: int
    offset: int
    stored_size: int
    data: bytes
    gap_after: bytes


@dataclass(frozen=True)
class InnerLink32:
    fixed_header: bytes
    table_offset: int
    resource_id: int
    aligned_table_end: int
    pre_data: bytes
    entries: tuple[InnerEntry, ...]
    original_size: int
    original_sha256: str


@dataclass(frozen=True)
class Format01Texture:
    raw_sha256: str
    raw_size: int
    declared_size: int
    directory_offset: int
    texture_count: int
    platform: int
    texture_offset: int
    packed_info: int
    mip_count: int
    format_code: int
    packed_dimensions: int
    width: int
    height: int
    extra_version: int
    extra_length: int
    payload_offset: int
    payload: bytes


@dataclass(frozen=True)
class BootBundle:
    input_path: Path
    input_size: int
    sha256_before_read: str
    sha256_after_read: str
    outer_entry_count: int
    outer_version: int
    outer_reserved: int
    outer_offset: int
    outer_stored_size: int
    outer_next_offset: int
    outer_data_sha256: str
    inner: InnerLink32


def parse_inner_link32(blob: bytes, label: str) -> InnerLink32:
    """Parse and identity-rebuild the exact 32-byte nested LINK variant."""

    require(len(blob) >= 32 and blob[:4] == b"LINK", f"{label}: expected nested LINK")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", blob, 4)
    require(count > 0, f"{label}: no nested entries")
    require(table_offset == 32, f"{label}: table offset must be 32")
    require(blob[20:32] == b"\0" * 12, f"{label}: nested LINK extension is not zero-filled")
    table_end = table_offset + count * 8
    require(table_end <= len(blob), f"{label}: table exceeds nested LINK")
    require(
        aligned_table_end == align_up(table_end, 32),
        f"{label}: aligned-table field is inconsistent",
    )
    pairs = [struct.unpack_from("<II", blob, table_offset + index * 8) for index in range(count)]
    first_offset = pairs[0][0]
    require(first_offset >= aligned_table_end and first_offset <= len(blob), f"{label}: first entry offset is invalid")
    entries: list[InnerEntry] = []
    for index, (offset, stored_size) in enumerate(pairs):
        next_offset = pairs[index + 1][0] if index + 1 < count else len(blob)
        end = offset + stored_size
        require(offset % 32 == 0, f"{label}: slot {index} is not 32-byte aligned")
        require(offset >= first_offset, f"{label}: slot {index} precedes the first entry")
        require(end <= next_offset <= len(blob), f"{label}: slot {index} overlaps or exceeds the bundle")
        entries.append(InnerEntry(index, offset, stored_size, blob[offset:end], blob[end:next_offset]))
    parsed = InnerLink32(
        fixed_header=blob[:table_offset],
        table_offset=table_offset,
        resource_id=resource_id,
        aligned_table_end=aligned_table_end,
        pre_data=blob[table_end:first_offset],
        entries=tuple(entries),
        original_size=len(blob),
        original_sha256=sha256_bytes(blob),
    )
    require(rebuild_inner_link32_identity(parsed) == blob, f"{label}: identity rebuild failed")
    return parsed


def rebuild_inner_link32_identity(archive: InnerLink32) -> bytes:
    """Reconstruct an unchanged nested LINK byte-for-byte.

    No replacement API is intentionally exposed here.  This audit proves the
    PC container boundary without creating an easy-to-misuse mutator.  A later
    candidate builder must separately validate wrappers, inner LINK offsets,
    all non-target bytes, and a reversible game-closed transaction.
    """

    output = bytearray(archive.fixed_header)
    output.extend(b"\0" * (len(archive.entries) * 8))
    output.extend(archive.pre_data)
    pairs: list[tuple[int, int]] = []
    for entry in archive.entries:
        require(len(output) == entry.offset, "identity rebuild offset drift")
        pairs.append((len(output), len(entry.data)))
        output.extend(entry.data)
        output.extend(entry.gap_after)
    for index, (offset, stored_size) in enumerate(pairs):
        struct.pack_into("<II", output, archive.table_offset + index * 8, offset, stored_size)
    return bytes(output)


def parse_format01_g1t(raw: bytes, label: str) -> Format01Texture:
    """Parse the observed PC ``GT1G0600`` single-texture RGBA8 variant."""

    require(len(raw) >= 56 and raw[:8] == G1T_MAGIC, f"{label}: expected GT1G0600")
    declared_size, directory_offset, texture_count, platform = struct.unpack_from("<4I", raw, 8)
    require(declared_size == len(raw), f"{label}: declared G1T size mismatch")
    require(directory_offset == 32, f"{label}: directory offset is not 32")
    require(texture_count == 1, f"{label}: this audit supports one texture only")
    require(platform == PC_PLATFORM, f"{label}: platform is not PC 0x0A")
    require(raw[24:32] == b"\0" * 8, f"{label}: unexpected G1T header extension")
    texture_offset = directory_offset + struct.unpack_from("<I", raw, directory_offset)[0]
    require(texture_offset == 36, f"{label}: unexpected texture offset 0x{texture_offset:X}")
    require(texture_offset + 20 <= len(raw), f"{label}: texture header is truncated")
    packed_info, format_code, packed_dimensions = struct.unpack_from("<BBB", raw, texture_offset)
    mip_count = packed_info >> 4
    require(packed_info & 0x0F == 0, f"{label}: unsupported packed-info low nibble")
    require(mip_count == 1, f"{label}: expected one mip level")
    require(format_code == FORMAT_RGBA8, f"{label}: expected format 0x01")
    width = 1 << (packed_dimensions & 0x0F)
    height = 1 << (packed_dimensions >> 4)
    require(width >= 2 and height >= 2, f"{label}: malformed dimensions")
    extra_version = raw[texture_offset + 7]
    extra_length = struct.unpack_from("<I", raw, texture_offset + 8)[0]
    require(extra_version == 0x10, f"{label}: expected extra version 0x10")
    require(extra_length == 12, f"{label}: expected 12-byte extra header")
    payload_offset = texture_offset + 8 + extra_length
    require(payload_offset <= len(raw), f"{label}: payload offset is outside G1T")
    payload = raw[payload_offset:]
    expected_payload_size = width * height * 4
    require(
        len(payload) == expected_payload_size,
        f"{label}: format 0x01 payload {len(payload)} != {width}*{height}*4",
    )
    return Format01Texture(
        raw_sha256=sha256_bytes(raw),
        raw_size=len(raw),
        declared_size=declared_size,
        directory_offset=directory_offset,
        texture_count=texture_count,
        platform=platform,
        texture_offset=texture_offset,
        packed_info=packed_info,
        mip_count=mip_count,
        format_code=format_code,
        packed_dimensions=packed_dimensions,
        width=width,
        height=height,
        extra_version=extra_version,
        extra_length=extra_length,
        payload_offset=payload_offset,
        payload=payload,
    )


def decode_format01_rgba(payload: bytes, width: int, height: int) -> bytes:
    """Decode the narrow observed PC layout into linear row-major RGBA8."""

    expected = width * height * 4
    require(len(payload) == expected, f"RGBA8 decoder received {len(payload)} bytes, expected {expected}")
    # The format is already linear RGBA8.  ``bytes`` makes the no-swizzle,
    # no-channel-reorder contract explicit and keeps callers immutable.
    return bytes(payload)


def encode_format01_rgba(rgba: bytes, width: int, height: int) -> bytes:
    """Inverse of :func:`decode_format01_rgba` for proof only, not a patcher."""

    expected = width * height * 4
    require(len(rgba) == expected, f"RGBA8 encoder received {len(rgba)} bytes, expected {expected}")
    return bytes(rgba)


def read_boot_bundle(game_root: Path) -> BootBundle:
    """Read the one PC JP bundle and prove the input remained unchanged."""

    input_path = (game_root / RESOURCE_RELATIVE_PATH).resolve()
    require(input_path.is_file(), f"missing PC JP resource: {input_path}")
    before = sha256_file(input_path)
    input_size = input_path.stat().st_size
    archive = lz4.parse_link(input_path.read_bytes())
    require(OUTER_ENTRY_INDEX < len(archive.entries), "outer /1 is missing")
    outer = archive.entries[OUTER_ENTRY_INDEX]
    next_offset = (
        archive.entries[OUTER_ENTRY_INDEX + 1].offset
        if OUTER_ENTRY_INDEX + 1 < len(archive.entries)
        else archive.original_size
    )
    inner = parse_inner_link32(outer.data, "RES_JP/res_lang.bin /1")
    after = sha256_file(input_path)
    require(before == after, "input changed during read-only audit")
    return BootBundle(
        input_path=input_path,
        input_size=input_size,
        sha256_before_read=before,
        sha256_after_read=after,
        outer_entry_count=len(archive.entries),
        outer_version=archive.version,
        outer_reserved=archive.reserved,
        outer_offset=outer.offset,
        outer_stored_size=outer.stored_size,
        outer_next_offset=next_offset,
        outer_data_sha256=sha256_bytes(outer.data),
        inner=inner,
    )


def observe_slot(entry: InnerEntry) -> tuple[dict[str, Any], Format01Texture]:
    header, raw = lz4.decompress_wrapper(entry.data)
    texture = parse_format01_g1t(raw, f"boot-warning slot {entry.index}")
    rgba = decode_format01_rgba(texture.payload, texture.width, texture.height)
    rebuilt_payload = encode_format01_rgba(rgba, texture.width, texture.height)
    require(rebuilt_payload == texture.payload, f"slot {entry.index}: RGBA encode/decode identity failed")
    alpha_values = set(rgba[3::4])
    return (
        {
            "slot": entry.index,
            "offset": entry.offset,
            "stored_size": entry.stored_size,
            "gap_after_size": len(entry.gap_after),
            "wrapper_sha256": sha256_bytes(entry.data),
            "wrapper": {
                "prefix_sha256": sha256_bytes(header.prefix),
                "uncompressed_size": header.uncompressed_size,
                "compressed_size": header.compressed_size,
                "exact_payload_size": len(entry.data) - 24,
            },
            "g1t": {
                "raw_sha256": texture.raw_sha256,
                "raw_size": texture.raw_size,
                "declared_size": texture.declared_size,
                "directory_offset": texture.directory_offset,
                "texture_count": texture.texture_count,
                "platform": f"0x{texture.platform:02X}",
                "texture_offset": texture.texture_offset,
                "packed_info": f"0x{texture.packed_info:02X}",
                "mip_count": texture.mip_count,
                "format_code": f"0x{texture.format_code:02X}",
                "dimensions": [texture.width, texture.height],
                "extra_version": f"0x{texture.extra_version:02X}",
                "extra_length": texture.extra_length,
                "payload_offset": texture.payload_offset,
                "payload_size": len(texture.payload),
                "payload_sha256": sha256_bytes(texture.payload),
                "bytes_per_pixel": 4,
                "alpha_value_count": len(alpha_values),
                "decode_encode_identity": True,
            },
        },
        texture,
    )


def make_validation(bundle: BootBundle) -> dict[str, Any]:
    slots: list[dict[str, Any]] = []
    dimension_counts: dict[str, int] = {}
    for entry in bundle.inner.entries:
        row, _ = observe_slot(entry)
        slots.append(row)
        width, height = row["g1t"]["dimensions"]
        key = f"{width}x{height}"
        dimension_counts[key] = dimension_counts.get(key, 0) + 1
    require(len(slots) == 6, f"expected six boot-warning slots, received {len(slots)}")
    require(dimension_counts == {"2048x2048": 3, "4096x4096": 3}, "unexpected boot-warning canvas mix")
    identity_rebuild_sha256 = sha256_bytes(rebuild_inner_link32_identity(bundle.inner))
    identity_rebuild_exact = identity_rebuild_sha256 == bundle.inner.original_sha256
    require(identity_rebuild_exact, "nested LINK identity hash drift")
    evidence_core = {
        "input_sha256": bundle.sha256_before_read,
        "outer_entry_sha256": bundle.outer_data_sha256,
        "slot_wrapper_sha256": [slot["wrapper_sha256"] for slot in slots],
        "slot_raw_sha256": [slot["g1t"]["raw_sha256"] for slot in slots],
        "slot_payload_sha256": [slot["g1t"]["payload_sha256"] for slot in slots],
        "dimension_counts": dimension_counts,
    }
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "platform": "PC Steam Japanese route",
            "steam_game_version": "1.1.7",
            "logical_target": "RES_JP/res_lang.bin /1",
            "outer_entry_index": OUTER_ENTRY_INDEX,
            "game_files_written": False,
            "patch_candidate_created": False,
            "switch_or_sc_raw_copy_used": False,
            "committed_binary_assets": False,
            "output_is_source_free_metadata_only": True,
        },
        "input": {
            "relative_path": RESOURCE_RELATIVE_PATH.as_posix(),
            "size": bundle.input_size,
            "sha256_before_read": bundle.sha256_before_read,
            "sha256_after_read": bundle.sha256_after_read,
            "read_only_identity_preserved": bundle.sha256_before_read == bundle.sha256_after_read,
            "outer_link_entry_count": bundle.outer_entry_count,
            "outer_link_version": bundle.outer_version,
            "outer_link_reserved": bundle.outer_reserved,
        },
        "container": {
            "outer_entry": {
                "offset": bundle.outer_offset,
                "stored_size": bundle.outer_stored_size,
                "next_offset": bundle.outer_next_offset,
                "sha256": bundle.outer_data_sha256,
            },
            "nested_link": {
                "header_size": 32,
                "entry_count": len(bundle.inner.entries),
                "table_offset": bundle.inner.table_offset,
                "resource_id": bundle.inner.resource_id,
                "aligned_table_end": bundle.inner.aligned_table_end,
                "pre_data_size": len(bundle.inner.pre_data),
                "identity_rebuild_sha256": identity_rebuild_sha256,
                "identity_rebuild_exact": identity_rebuild_exact,
                "identity_rebuild_note": "Parser performs an exact byte-for-byte identity gate before metadata is emitted.",
            },
        },
        "format_0x01_contract": {
            "status": "identified_for_this_observed_pc_variant",
            "g1t_magic": "GT1G0600",
            "pc_platform": "0x0A",
            "format_code": "0x01",
            "pixel_storage": "linear row-major RGBA8",
            "bytes_per_pixel": 4,
            "mip_count": 1,
            "extra_header": {"version": "0x10", "length": 12},
            "dimension_counts": dimension_counts,
            "non_generalization": "Do not infer this mapping for arbitrary G1T format 0x01 resources or non-PC platforms.",
        },
        "decoder_proof": {
            "all_six_payloads_match_width_times_height_times_4": True,
            "all_six_decode_encode_identity": True,
            "container_identity_rebuild_exact": identity_rebuild_exact,
            "private_visual_check": {
                "slot": 0,
                "method": "Decode as RGBA8, nearest-scale privately, and inspect the Japanese startup warning; no PNG is committed.",
                "observed_result": "Readable Japanese warning with the ご注意 heading; channel-reordered comparison is visibly incorrect.",
                "status": "completed_private_manual_check",
            },
            "evidence_core_sha256": stable_hash(evidence_core),
        },
        "slots": slots,
        "implementation_status": {
            "decoder": "ready_for_private_inspection_only",
            "encoder": "byte-identity inverse proven; not exposed as a game patch writer",
            "container_mutator": "intentionally_not_implemented_in_this_audit",
            "safe_next_step": [
                "Approve Korean warning copy and render each exact PC canvas in private tmp using RGBA8; do not use Switch or SC raw containers.",
                "Build a separate, fail-closed candidate composer that preserves each G1T header, wrapper prefix, non-target inner/outer bytes, and proves all six decode/re-encode checks.",
                "Run candidate-only structural checks plus actual startup screen capture while the game is closed; only then use a reversible transaction with pre/post hashes.",
            ],
        },
        "provenance": {
            "builder": "build_steam_jp_boot_warning_codec_audit_v1.py",
            "builder_sha256": sha256_file(Path(__file__)),
            "generated_utc": "2026-07-16T00:00:00Z",
        },
    }
    validate_metadata(result)
    return result


def _walk_json(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child)


def validate_metadata(value: dict[str, Any]) -> None:
    require(value.get("schema") == SCHEMA, "unexpected schema")
    scope = value.get("scope")
    require(isinstance(scope, dict), "scope missing")
    for key in (
        "game_files_written",
        "patch_candidate_created",
        "switch_or_sc_raw_copy_used",
        "committed_binary_assets",
        "output_is_source_free_metadata_only",
    ):
        require(scope.get(key) is False if key != "output_is_source_free_metadata_only" else scope.get(key) is True, f"scope.{key} invariant failed")
    contract = value.get("format_0x01_contract")
    require(isinstance(contract, dict), "format contract missing")
    require(contract.get("pixel_storage") == "linear row-major RGBA8", "RGBA8 contract missing")
    require(contract.get("format_code") == "0x01", "format code mismatch")
    nested = value.get("container", {}).get("nested_link", {})
    require(nested.get("identity_rebuild_exact") is True, "nested LINK identity gate failed")
    slots = value.get("slots")
    require(isinstance(slots, list) and len(slots) == 6, "six-slot contract failed")
    dimensions = [tuple(slot["g1t"]["dimensions"]) for slot in slots]
    require(dimensions.count((2048, 2048)) == 3 and dimensions.count((4096, 4096)) == 3, "dimension contract failed")
    for slot in slots:
        g1t = slot.get("g1t")
        require(isinstance(g1t, dict), "slot G1T record missing")
        width, height = g1t["dimensions"]
        require(g1t["payload_size"] == width * height * 4, "payload byte-size contract failed")
        require(g1t["decode_encode_identity"] is True, "codec identity contract failed")
        for hash_key in ("wrapper_sha256",):
            require(len(slot[hash_key]) == 64, f"invalid {hash_key}")
        for hash_key in ("raw_sha256", "payload_sha256"):
            require(len(g1t[hash_key]) == 64, f"invalid {hash_key}")
    banned_exact_keys = {"data", "raw", "payload", "png", "image", "binary", "g1t_bytes"}
    for key, child in _walk_json(value):
        require(key not in banned_exact_keys, f"source-free metadata contains forbidden key: {key}")
        if isinstance(child, str):
            require(not child.startswith("data:"), "source-free metadata contains a data URL")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def encode_png_rgba(rgba: bytes, width: int, height: int) -> bytes:
    require(len(rgba) == width * height * 4, "PNG input does not match RGBA dimensions")
    scanlines = bytearray()
    stride = width * 4
    for y in range(height):
        scanlines.append(0)
        scanlines.extend(rgba[y * stride : (y + 1) * stride])

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(
        b"IDAT", zlib.compress(bytes(scanlines), 9)
    ) + chunk(b"IEND", b"")


def nearest_resize_rgba(rgba: bytes, width: int, height: int, target_width: int, target_height: int) -> bytes:
    require(target_width > 0 and target_height > 0, "preview dimensions must be positive")
    require(len(rgba) == width * height * 4, "resize input does not match RGBA dimensions")
    output = bytearray(target_width * target_height * 4)
    for target_y in range(target_height):
        source_y = target_y * height // target_height
        for target_x in range(target_width):
            source_x = target_x * width // target_width
            source = (source_y * width + source_x) * 4
            target = (target_y * target_width + target_x) * 4
            output[target : target + 4] = rgba[source : source + 4]
    return bytes(output)


def require_tmp_output(path: Path) -> Path:
    resolved = path.resolve()
    root = TMP_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AuditError(f"preview output must be under ignored tmp root: {root}") from exc
    return resolved


def make_private_preview(bundle: BootBundle, output_dir: Path, max_dimension: int) -> dict[str, Any]:
    output_dir = require_tmp_output(output_dir)
    require(max_dimension >= 64, "max preview dimension must be at least 64")
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    previews: list[tuple[bytes, int, int]] = []
    for entry in bundle.inner.entries:
        _, raw = lz4.decompress_wrapper(entry.data)
        texture = parse_format01_g1t(raw, f"boot-warning slot {entry.index}")
        rgba = decode_format01_rgba(texture.payload, texture.width, texture.height)
        scale = min(1.0, max_dimension / max(texture.width, texture.height))
        target_width = max(1, round(texture.width * scale))
        target_height = max(1, round(texture.height * scale))
        preview = nearest_resize_rgba(rgba, texture.width, texture.height, target_width, target_height)
        filename = f"slot_{entry.index:02d}_{texture.width}x{texture.height}.rgba.png"
        target = output_dir / filename
        target.write_bytes(encode_png_rgba(preview, target_width, target_height))
        rows.append(
            {
                "slot": entry.index,
                "dimensions": [texture.width, texture.height],
                "preview_dimensions": [target_width, target_height],
                "filename": filename,
                "png_sha256": sha256_file(target),
            }
        )
        previews.append((preview, target_width, target_height))
    columns = 3
    cell_width = max(width for _, width, _ in previews)
    cell_height = max(height for _, _, height in previews)
    rows_count = math.ceil(len(previews) / columns)
    canvas = bytearray(cell_width * columns * cell_height * rows_count * 4)
    for index, (preview, width, height) in enumerate(previews):
        cell_x = (index % columns) * cell_width
        cell_y = (index // columns) * cell_height
        for y in range(height):
            source = y * width * 4
            target = ((cell_y + y) * (cell_width * columns) + cell_x) * 4
            canvas[target : target + width * 4] = preview[source : source + width * 4]
    contact = output_dir / "contact_sheet.rgba.png"
    contact.write_bytes(encode_png_rgba(bytes(canvas), cell_width * columns, cell_height * rows_count))
    result = {
        "schema": "nobu16.kr.steam-jp-boot-warning-private-preview.v1",
        "source_free_workstream": True,
        "private_output_root": str(output_dir),
        "slot_previews": rows,
        "contact_sheet": {
            "filename": contact.name,
            "dimensions": [cell_width * columns, cell_height * rows_count],
            "png_sha256": sha256_file(contact),
        },
        "input_sha256": bundle.sha256_before_read,
        "input_unchanged": bundle.sha256_before_read == bundle.sha256_after_read,
    }
    write_json(output_dir / "preview_manifest.json", result)
    return result


def cmd_audit(args: argparse.Namespace) -> int:
    bundle = read_boot_bundle(Path(args.game_root))
    value = make_validation(bundle)
    output = Path(args.output)
    write_json(output, value)
    print(f"output={output}")
    print(f"input_sha256={bundle.sha256_before_read}")
    print(f"slot_count={len(bundle.inner.entries)}")
    print("status=PASS")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    path = Path(args.input)
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_metadata(value)
    print(f"input={path}")
    print("status=PASS")
    return 0


def cmd_private_preview(args: argparse.Namespace) -> int:
    bundle = read_boot_bundle(Path(args.game_root))
    result = make_private_preview(bundle, Path(args.output_dir), args.max_dimension)
    print(f"output={result['private_output_root']}")
    print(f"contact_sheet_sha256={result['contact_sheet']['png_sha256']}")
    print("status=PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="Read the PC JP input and emit source-free validation metadata")
    audit.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    audit.add_argument("--output", type=Path, default=DEFAULT_VALIDATION)
    audit.set_defaults(func=cmd_audit)
    verify = sub.add_parser("verify", help="Validate already-emitted source-free metadata without opening game files")
    verify.add_argument("--input", type=Path, default=DEFAULT_VALIDATION)
    verify.set_defaults(func=cmd_verify)
    preview = sub.add_parser("private-preview", help="Write private derived PNG previews under ignored tmp only")
    preview.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    preview.add_argument("--output-dir", type=Path, default=DEFAULT_PREVIEW_DIR)
    preview.add_argument("--max-dimension", type=int, default=512)
    preview.set_defaults(func=cmd_private_preview)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (AuditError, lz4.LZ4Error, lz4.LinkError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
