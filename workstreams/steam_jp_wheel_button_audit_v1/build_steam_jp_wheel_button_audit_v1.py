#!/usr/bin/env python3
"""Audit the Switch wheel-command texture source against Steam JP safely.

The Switch v2.1 changelog identifies the main-screen radial command wheel as
``RES_JP/res_lang.bin`` outer LINK entry ``/8``.  This utility proves that
claim from the actual public Switch release archives, compares it with the
Steam 1.1.7 Japanese resource, and emits source-free metadata only.

It deliberately does *not* build a patch.  A separate PC-only rebuilder must
first map the 2048x1024 Switch atlas onto the Steam 2048x2048 atlas.  Raw
Switch LINK/G1T/LZ4 bytes are never copied and no game file is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as bc3  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-wheel-button-audit.v1"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
PC_RELATIVE_PATH = "RES_JP/res_lang.bin"
OUTER_INDEX = 8
EXPECTED_RESOURCE_ID = 474
EXPECTED_NESTED_SLOT = 0
SWITCH_RELEASES = ("v20", "v21", "v22", "v23", "v24")


class AuditError(ValueError):
    """Raised when a release resource is not the audited wheel-button shape."""


@dataclass(frozen=True)
class OuterEntry:
    index: int
    offset: int
    stored_size: int
    next_offset: int
    data: bytes


@dataclass(frozen=True)
class OuterTable:
    entry_count: int
    version: int
    reserved: int
    size: int
    entries: tuple[OuterEntry, ...]


def sha256_bytes(blob: bytes | memoryview) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def stable_hash(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    destination = path.resolve()
    for item in forbidden:
        if destination == item.resolve():
            raise AuditError(f"refusing to overwrite input: {item}")
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


def parse_outer(blob: bytes) -> OuterTable:
    require(len(blob) >= 16 and blob[:4] == b"LINK", "outer resource is not LINK")
    entry_count, version, reserved = struct.unpack_from("<III", blob, 4)
    table_end = 16 + entry_count * 8
    require(table_end <= len(blob), "outer LINK table is truncated")
    pairs = [struct.unpack_from("<II", blob, 16 + index * 8) for index in range(entry_count)]
    entries: list[OuterEntry] = []
    previous = -1
    for index, (offset, stored_size) in enumerate(pairs):
        next_offset = pairs[index + 1][0] if index + 1 < entry_count else len(blob)
        require(offset >= previous, f"outer offsets decrease at {index}")
        if offset >= len(blob) and stored_size == 0:
            require(all(size == 0 for _, size in pairs[index:]), "non-trailing virtual outer slot")
            data = b""
        else:
            require(offset + stored_size <= next_offset <= len(blob), f"outer slot {index} overlaps")
            data = blob[offset : offset + stored_size]
        entries.append(OuterEntry(index, offset, stored_size, next_offset, data))
        previous = offset
    return OuterTable(entry_count, version, reserved, len(blob), tuple(entries))


def read_pc_outer(path: Path) -> tuple[OuterTable, dict[str, Any]]:
    require(path.is_file(), f"missing Steam JP resource: {path}")
    before = sha256_file(path)
    blob = path.read_bytes()
    after = sha256_file(path)
    require(before == after, "Steam resource changed during read-only audit")
    return parse_outer(blob), {
        "relative_path": PC_RELATIVE_PATH,
        "size": len(blob),
        "sha256_before_read": before,
        "sha256_after_read": after,
        "read_only_identity_preserved": True,
    }


def read_switch_release(path: Path) -> tuple[OuterTable, dict[str, Any]]:
    require(path.is_file(), f"missing Switch release ZIP: {path}")
    zip_hash = sha256_file(path)
    with zipfile.ZipFile(path) as archive:
        try:
            info = archive.getinfo(SWITCH_MEMBER)
        except KeyError as exc:
            raise AuditError(f"{path.name}: missing {SWITCH_MEMBER}") from exc
        blob = archive.read(info)
    return parse_outer(blob), {
        "zip_filename": path.name,
        "zip_size": path.stat().st_size,
        "zip_sha256": zip_hash,
        "member": SWITCH_MEMBER,
        "member_size": len(blob),
        "member_crc32": f"{info.CRC:08X}",
        "member_sha256": sha256_bytes(blob),
    }


def _g1t_textures(raw: bytes) -> list[dict[str, Any]]:
    require(len(raw) >= 32 and raw[:8] == b"GT1G0600", "wheel slot raw is not GT1G0600")
    declared_size, directory_offset, texture_count, platform = struct.unpack_from("<4I", raw, 8)
    require(declared_size == len(raw), "G1T declared size mismatch")
    require(texture_count > 0, "G1T has no textures")
    directory_end = directory_offset + texture_count * 4
    require(32 <= directory_offset <= directory_end <= len(raw), "G1T directory out of range")
    starts = [directory_offset + struct.unpack_from("<I", raw, directory_offset + index * 4)[0] for index in range(texture_count)]
    require(starts == sorted(starts), "G1T texture offsets are unordered")
    require(starts[0] >= directory_end and starts[-1] < len(raw), "G1T texture starts invalid")
    rows: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(raw)
        require(end - start >= 8, f"G1T texture {index} header truncated")
        packed_info, format_code, packed_dimensions = struct.unpack_from("<BBB", raw, start)
        width = 1 << (packed_dimensions & 0x0F)
        height = 1 << (packed_dimensions >> 4)
        extra_version = raw[start + 7]
        extra_length = 0
        payload_offset = start + 8
        if extra_version:
            require(end - start >= 12, f"G1T texture {index} extra header truncated")
            extra_length = struct.unpack_from("<I", raw, start + 8)[0]
            require(extra_length >= 4, f"G1T texture {index} extra header malformed")
            payload_offset = start + 8 + extra_length
        require(payload_offset <= end, f"G1T texture {index} payload out of range")
        rows.append(
            {
                "texture": index,
                "dimensions": [width, height],
                "format_code": f"0x{format_code:02X}",
                "mip_count": packed_info >> 4,
                "extra_version": extra_version,
                "extra_length": extra_length,
                "node_size": end - start,
                "node_sha256": sha256_bytes(raw[start:end]),
                "payload_size": end - payload_offset,
                "payload_sha256": sha256_bytes(raw[payload_offset:end]),
                "_payload_offset": payload_offset,
                "_payload_end": end,
            }
        )
    return rows


def inspect_wheel(outer: OuterTable, *, label: str, retain_raw: bool = False) -> dict[str, Any]:
    require(OUTER_INDEX < outer.entry_count, f"{label}: outer /{OUTER_INDEX} missing")
    entry = outer.entries[OUTER_INDEX]
    nested = entry.data
    require(len(nested) >= 32 and nested[:4] == b"LINK", f"{label}: /8 is not nested LINK")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", nested, 4)
    require(table_offset == 32, f"{label}: nested table offset is {table_offset}, expected 32")
    require(resource_id == EXPECTED_RESOURCE_ID, f"{label}: resource ID drifted: {resource_id}")
    require(nested[20:32] == b"\0" * 12, f"{label}: nested LINK extension is non-zero")
    table_end = table_offset + count * 8
    require(aligned_table_end == (table_end + 31) & ~31, f"{label}: nested table alignment invalid")
    require(table_end <= len(nested), f"{label}: nested table exceeds /8")
    require(count == 1, f"{label}: unexpected nested slot count {count}")
    offset, stored_size = struct.unpack_from("<II", nested, table_offset + EXPECTED_NESTED_SLOT * 8)
    require(offset >= aligned_table_end and offset + stored_size <= len(nested), f"{label}: nested /0 out of range")
    wrapper = nested[offset : offset + stored_size]
    header, raw = lz4.decompress_wrapper(wrapper)
    textures = _g1t_textures(raw)
    public_textures = [{key: value for key, value in row.items() if not key.startswith("_")} for row in textures]
    require(public_textures[0]["format_code"] == "0x5B", f"{label}: primary atlas is not BC3")
    result: dict[str, Any] = {
        "path": f"RES_JP/res_lang.bin/{OUTER_INDEX}",
        "outer_index": OUTER_INDEX,
        "outer_entry": {
            "offset": entry.offset,
            "stored_size": entry.stored_size,
            "next_offset": entry.next_offset,
            "sha256": sha256_bytes(entry.data),
        },
        "nested_link": {
            "resource_id": resource_id,
            "table_slot_count": count,
            "table_offset": table_offset,
            "aligned_table_end": aligned_table_end,
            "pre_slot_size": offset - aligned_table_end,
            "pre_slot_sha256": sha256_bytes(nested[aligned_table_end:offset]),
            "tail_size": len(nested) - (offset + stored_size),
            "tail_sha256": sha256_bytes(nested[offset + stored_size:]),
        },
        "slot": {
            "slot": EXPECTED_NESTED_SLOT,
            "offset": offset,
            "stored_size": stored_size,
            "wrapper_sha256": sha256_bytes(wrapper),
            "wrapper_prefix_sha256": sha256_bytes(header.prefix),
            "wrapper_uncompressed_size": header.uncompressed_size,
            "wrapper_compressed_size": header.compressed_size,
            "raw_sha256": sha256_bytes(raw),
            "raw_kind": "GT1G0600",
            "g1t": {
                "declared_size": len(raw),
                "platform": struct.unpack_from("<I", raw, 20)[0],
                "texture_count": len(public_textures),
                "textures": public_textures,
            },
        },
    }
    result["inventory_sha256"] = stable_hash(result)
    if retain_raw:
        result["_raw"] = raw
        result["_textures_internal"] = textures
    return result


def _outer_hashes(outer: OuterTable) -> list[str]:
    return [sha256_bytes(entry.data) for entry in outer.entries]


def compare_versions(
    left_outer: OuterTable,
    left: Mapping[str, Any],
    right_outer: OuterTable,
    right: Mapping[str, Any],
    *,
    left_label: str,
    right_label: str,
) -> dict[str, Any]:
    left_hashes = _outer_hashes(left_outer)
    right_hashes = _outer_hashes(right_outer)
    require(len(left_hashes) == len(right_hashes), "Switch outer slot count changed")
    changed_outer = [index for index, pair in enumerate(zip(left_hashes, right_hashes)) if pair[0] != pair[1]]
    left_textures = left["slot"]["g1t"]["textures"]
    right_textures = right["slot"]["g1t"]["textures"]
    require(len(left_textures) == len(right_textures), "wheel G1T texture count changed")
    changed_textures = [
        index
        for index, pair in enumerate(zip(left_textures, right_textures))
        if pair[0]["payload_sha256"] != pair[1]["payload_sha256"]
    ]
    layout_equal = [
        {key: item[key] for key in ("dimensions", "format_code", "mip_count", "extra_version", "extra_length", "payload_size")}
        for item in left_textures
    ] == [
        {key: item[key] for key in ("dimensions", "format_code", "mip_count", "extra_version", "extra_length", "payload_size")}
        for item in right_textures
    ]
    result = {
        "left": left_label,
        "right": right_label,
        "outer_entry_count_equal": True,
        "changed_outer_indices": changed_outer,
        "wheel_outer_changed": OUTER_INDEX in changed_outer,
        "wheel_nested_contract_equal": left["nested_link"] == right["nested_link"],
        "wheel_g1t_layout_equal": layout_equal,
        "wheel_changed_texture_indices": changed_textures,
        "wheel_primary_texture_changed": 0 in changed_textures,
    }
    result["comparison_sha256"] = stable_hash(result)
    return result


def compare_switch_to_pc(switch: Mapping[str, Any], pc: Mapping[str, Any]) -> dict[str, Any]:
    switch_primary = switch["slot"]["g1t"]["textures"][0]
    pc_primary = pc["slot"]["g1t"]["textures"][0]
    result = {
        "switch_outer_index": OUTER_INDEX,
        "pc_outer_index": OUTER_INDEX,
        "nested_resource_id_equal": switch["nested_link"]["resource_id"] == pc["nested_link"]["resource_id"],
        "nested_slot_count_equal": switch["nested_link"]["table_slot_count"] == pc["nested_link"]["table_slot_count"],
        "g1t_platform": {
            "switch": switch["slot"]["g1t"]["platform"],
            "pc": pc["slot"]["g1t"]["platform"],
            "equal": switch["slot"]["g1t"]["platform"] == pc["slot"]["g1t"]["platform"],
        },
        "primary_texture": {
            "format_code": {"switch": switch_primary["format_code"], "pc": pc_primary["format_code"], "equal": switch_primary["format_code"] == pc_primary["format_code"]},
            "dimensions": {"switch": switch_primary["dimensions"], "pc": pc_primary["dimensions"], "equal": switch_primary["dimensions"] == pc_primary["dimensions"]},
            "payload_size": {"switch": switch_primary["payload_size"], "pc": pc_primary["payload_size"], "equal": switch_primary["payload_size"] == pc_primary["payload_size"]},
        },
        "raw_or_wrapper_copy_allowed": False,
        "pc_only_rebuild_required": True,
    }
    result["comparison_sha256"] = stable_hash(result)
    return result


def build_audit(game_root: Path, releases: Mapping[str, Path]) -> dict[str, Any]:
    require(tuple(releases) == SWITCH_RELEASES, "release order must be v20, v21, v22, v23, v24")
    pc_outer, pc_input = read_pc_outer(game_root / PC_RELATIVE_PATH)
    switch_outers: dict[str, OuterTable] = {}
    switch_inputs: dict[str, dict[str, Any]] = {}
    wheel: dict[str, dict[str, Any]] = {}
    for label, path in releases.items():
        outer, source = read_switch_release(path)
        switch_outers[label] = outer
        switch_inputs[label] = source
        wheel[label] = inspect_wheel(outer, label=f"Switch {label}")
    pc = inspect_wheel(pc_outer, label="Steam JP")
    v20_v21 = compare_versions(switch_outers["v20"], wheel["v20"], switch_outers["v21"], wheel["v21"], left_label="switch_v20", right_label="switch_v21")
    v21_v22 = compare_versions(switch_outers["v21"], wheel["v21"], switch_outers["v22"], wheel["v22"], left_label="switch_v21", right_label="switch_v22")
    v22_v23 = compare_versions(switch_outers["v22"], wheel["v22"], switch_outers["v23"], wheel["v23"], left_label="switch_v22", right_label="switch_v23")
    v23_v24 = compare_versions(switch_outers["v23"], wheel["v23"], switch_outers["v24"], wheel["v24"], left_label="switch_v23", right_label="switch_v24")
    require(v20_v21["changed_outer_indices"] == [OUTER_INDEX], "v2.1 wheel-only outer change gate failed")
    require(v20_v21["wheel_primary_texture_changed"] is True, "v2.1 did not change primary wheel atlas")
    require(v21_v22["wheel_primary_texture_changed"] is True, "v2.2 wheel-size adjustment gate failed")
    require(v22_v23["wheel_outer_changed"] is False, "v2.3 unexpectedly changed the wheel atlas")
    require(v23_v24["wheel_outer_changed"] is False, "v2.4 unexpectedly changed the wheel atlas")
    require(wheel["v22"]["outer_entry"]["sha256"] == wheel["v24"]["outer_entry"]["sha256"], "v2.2/v2.4 wheel atlas identity gate failed")
    result = {
        "schema": SCHEMA,
        "scope": {
            "platform": "PC Steam Japanese route",
            "steam_game_version": "1.1.7",
            "game_files_written": False,
            "patch_candidate_created": False,
            "switch_raw_or_archive_copy": False,
        },
        "identification": {
            "asset": "main-screen radial command wheel / command-button atlas",
            "switch_source_path": "RES_JP/res_lang.bin/8/0",
            "switch_v21_change_proof": "v2.0→v2.1 changes only outer /8; its primary 2048x1024 BC3 texture changes while nested layout remains stable",
            "switch_v22_adjustment_proof": "v2.1→v2.2 changes /8 again; v2.2 is the intended command-label size adjustment",
            "latest_source_choice": "Switch v2.4 /8 is byte-identical to v2.2 /8, so v2.4 may be used as the latest visual reference while preserving the v2.2-adjusted wheel pixels",
            "pc_target_path": "RES_JP/res_lang.bin/8/0",
        },
        "pc_input": pc_input,
        "switch_releases": switch_inputs,
        "wheel_inventories": {"switch_v20": wheel["v20"], "switch_v21": wheel["v21"], "switch_v24": wheel["v24"], "steam_jp": pc},
        "comparisons": {
            "switch_v20_to_v21": v20_v21,
            "switch_v21_to_v22": v21_v22,
            "switch_v22_to_v23": v22_v23,
            "switch_v23_to_v24": v23_v24,
            "switch_v22_to_steam_jp": compare_switch_to_pc(wheel["v22"], pc),
        },
        "implementation_gate": {
            "status": "blocked_pending_pc_atlas_mapping_and_visual_qa",
            "why": [
                "Switch /8/0 primary atlas is 2048x1024, while Steam JP /8/0 is 2048x2048.",
                "Switch and PC G1T platform fields differ (0x10 vs 0x0A).",
                "Raw Switch LINK, wrapper, G1T, or payload byte copying is prohibited.",
            ],
            "next_pc_only_rebuild_gate": [
                "Use the Switch v2.4 primary BC3 pixels only as a private preview; its /8 is byte-identical to the v2.2 wheel-size-adjusted atlas.",
                "Map the Korean labels onto the Steam JP 2048x2048 layout by visual correspondence; do not assume matching coordinates.",
                "Render Korean labels into the Steam JP atlas while preserving icons, clouds, arrows, backgrounds, texture 1, and all non-/8 outer entries byte-identically.",
                "Rebuild only Steam JP /8/0 with the PC 0x0A G1T, PC wrapper, and PC LINK structures; then require parse, hash, and in-game main-screen wheel QA before any apply.",
            ],
        },
    }
    result["audit_sha256"] = stable_hash(result)
    return result


def validate_audit_document(document: Mapping[str, Any]) -> None:
    """Validate the source-free audit without reopening proprietary inputs."""

    require(document.get("schema") == SCHEMA, "audit schema mismatch")
    scope = document.get("scope")
    require(isinstance(scope, Mapping), "audit scope missing")
    require(scope.get("platform") == "PC Steam Japanese route", "wrong target route")
    require(scope.get("steam_game_version") == "1.1.7", "wrong Steam version")
    require(scope.get("game_files_written") is False, "audit claims a game write")
    require(scope.get("patch_candidate_created") is False, "audit claims a candidate")
    comparisons = document.get("comparisons")
    require(isinstance(comparisons, Mapping), "audit comparisons missing")
    v20_v21 = comparisons.get("switch_v20_to_v21")
    require(isinstance(v20_v21, Mapping), "v2.0→v2.1 comparison missing")
    require(v20_v21.get("changed_outer_indices") == [OUTER_INDEX], "wheel-only v2.1 proof drifted")
    require(v20_v21.get("wheel_primary_texture_changed") is True, "primary wheel texture gate missing")
    v21_v22 = comparisons.get("switch_v21_to_v22")
    require(isinstance(v21_v22, Mapping) and v21_v22.get("wheel_primary_texture_changed") is True, "v2.2 wheel adjustment proof missing")
    v22_v23 = comparisons.get("switch_v22_to_v23")
    require(isinstance(v22_v23, Mapping) and v22_v23.get("wheel_outer_changed") is False, "v2.3 wheel identity proof missing")
    v23_v24 = comparisons.get("switch_v23_to_v24")
    require(isinstance(v23_v24, Mapping) and v23_v24.get("wheel_outer_changed") is False, "v2.4 wheel identity proof missing")
    pc = comparisons.get("switch_v22_to_steam_jp")
    require(isinstance(pc, Mapping), "Switch→Steam comparison missing")
    require(pc.get("pc_only_rebuild_required") is True, "PC-only rebuild gate missing")
    require(pc.get("raw_or_wrapper_copy_allowed") is False, "raw copy prohibition missing")
    primary = pc.get("primary_texture")
    require(isinstance(primary, Mapping), "primary texture comparison missing")
    dimensions = primary.get("dimensions")
    require(isinstance(dimensions, Mapping) and dimensions.get("equal") is False, "cross-platform atlas geometry gate missing")
    gate = document.get("implementation_gate")
    require(isinstance(gate, Mapping), "implementation gate missing")
    require(gate.get("status") == "blocked_pending_pc_atlas_mapping_and_visual_qa", "implementation gate status drifted")
    expected_hash = document.get("audit_sha256")
    require(isinstance(expected_hash, str), "audit hash missing")
    without_hash = {key: value for key, value in document.items() if key != "audit_sha256"}
    require(expected_hash == stable_hash(without_hash), "audit hash mismatch")


def ensure_private_output_root(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(TMP_ROOT.resolve())
    except ValueError as exc:
        raise AuditError(f"preview output must remain under {TMP_ROOT.resolve()}") from exc
    return resolved


def preview_from_outer(outer: OuterTable, output_root: Path, *, label: str, source_name: str) -> dict[str, Any]:
    inspected = inspect_wheel(outer, label=label, retain_raw=True)
    raw = inspected.pop("_raw")
    textures = inspected.pop("_textures_internal")
    primary = textures[0]
    require(primary["format_code"] == "0x5B", "preview requires BC3 primary atlas")
    width, height = primary["dimensions"]
    payload = raw[primary["_payload_offset"] : primary["_payload_end"]]
    rgba = bc3.decode_bc3(payload, width, height)
    png = bc3.encode_rgba_png(rgba, width, height)
    output = ensure_private_output_root(output_root) / "private" / f"{label}_wheel_primary.png"
    # The output root is fail-closed under ``tmp``; neither Switch ZIP nor
    # Steam resource paths can therefore be replaced by this preview command.
    atomic_write(output, png)
    return {
        "preview_png": str(output),
        "preview_png_sha256": sha256_bytes(png),
        "dimensions": [width, height],
        "source": source_name,
        "game_files_written": False,
    }


def preview_wheel(release_path: Path, output_root: Path, *, label: str) -> dict[str, Any]:
    outer, _source = read_switch_release(release_path)
    return preview_from_outer(outer, output_root, label=label, source_name=release_path.name)


def preview_pc_wheel(game_root: Path, output_root: Path) -> dict[str, Any]:
    outer, source = read_pc_outer(game_root / PC_RELATIVE_PATH)
    result = preview_from_outer(outer, output_root, label="steam_jp", source_name=source["relative_path"])
    result["steam_input_sha256"] = source["sha256_before_read"]
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="write source-free audit JSON")
    audit.add_argument("--game-root", type=Path, required=True)
    audit.add_argument("--switch-v20-zip", type=Path, required=True)
    audit.add_argument("--switch-v21-zip", type=Path, required=True)
    audit.add_argument("--switch-v22-zip", type=Path, required=True)
    audit.add_argument("--switch-v23-zip", type=Path, required=True)
    audit.add_argument("--switch-v24-zip", type=Path, required=True)
    audit.add_argument("--output", type=Path, default=WORKSTREAM / "audit.v1.json")
    verify = sub.add_parser("verify", help="validate the source-free audit document")
    verify.add_argument("--input", type=Path, default=WORKSTREAM / "audit.v1.json")
    preview = sub.add_parser("preview", help="decode one Switch wheel atlas to a private PNG")
    preview.add_argument("--switch-zip", type=Path, required=True)
    preview.add_argument("--label", choices=SWITCH_RELEASES, required=True)
    preview.add_argument("--output-root", type=Path, default=TMP_ROOT / "switch_wheel_button_audit")
    preview_pc = sub.add_parser("preview-pc", help="decode the Steam JP wheel atlas to a private PNG")
    preview_pc.add_argument("--game-root", type=Path, required=True)
    preview_pc.add_argument("--output-root", type=Path, default=TMP_ROOT / "switch_wheel_button_audit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "audit":
        audit = build_audit(
            args.game_root,
            {
                "v20": args.switch_v20_zip,
                "v21": args.switch_v21_zip,
                "v22": args.switch_v22_zip,
                "v23": args.switch_v23_zip,
                "v24": args.switch_v24_zip,
            },
        )
        output = args.output.resolve()
        require(output == (WORKSTREAM / "audit.v1.json").resolve() or output.is_relative_to(TMP_ROOT.resolve()), "audit output must be workstream metadata or tmp")
        atomic_write(output, (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"audit={output}")
        print(f"audit_sha256={audit['audit_sha256']}")
        print("game_files_written=False")
        return 0
    if args.command == "verify":
        try:
            document = json.loads(args.input.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AuditError(f"invalid audit JSON: {exc}") from exc
        require(isinstance(document, Mapping), "audit root must be an object")
        validate_audit_document(document)
        print(f"audit={args.input.resolve()}")
        print("verify=PASS")
        print("game_files_written=False")
        return 0
    if args.command == "preview-pc":
        result = preview_pc_wheel(args.game_root, args.output_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    result = preview_wheel(args.switch_zip, args.output_root, label=args.label)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
