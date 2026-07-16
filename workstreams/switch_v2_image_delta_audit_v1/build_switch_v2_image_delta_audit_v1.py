#!/usr/bin/env python3
"""Read-only audit of the Switch v2.x wheel and button image deltas.

The public Switch releases are evidence only.  This script records metadata
and hashes, but never writes a game file, patch candidate, Switch container,
or decoded image into the workstream.  The optional preview command emits
private PNGs below the ignored project ``tmp`` directory only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
PROJECT_ROOT = WORKSTREAM.parents[1]
TOOLS = PROJECT_ROOT / "tools"
TMP_ROOT = PROJECT_ROOT / "tmp"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as image_codec  # noqa: E402
import trace_bottom_return_button as trace  # noqa: E402


SCHEMA = "nobu16.kr.switch-v2-image-delta-audit.v1"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
PC_RELATIVE_PATH = "RES_JP/res_lang.bin"
DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_AUDIT = WORKSTREAM / "audit.v1.json"
DEFAULT_PREVIEW_ROOT = TMP_ROOT / "switch_v2_image_delta_audit_v1" / "private" / "preview"

RELEASE_PATHS: Mapping[str, Path] = {
    "v20": PROJECT_ROOT / "tmp" / "third_party_switch_v20" / "NobunagaShinsei_KoreanPatch_v2.0.zip",
    "v21": PROJECT_ROOT / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.1.zip",
    "v22": PROJECT_ROOT / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.2.zip",
    "v23": PROJECT_ROOT / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.3.zip",
    "v24": PROJECT_ROOT / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.4.zip",
}
RELEASE_ORDER = tuple(RELEASE_PATHS)

# The private v2.2 atlas review identifies each Korean-labelled bundle.  The
# screen gate remains mandatory because Switch and PC atlas geometry differs.
TARGETS: Mapping[int, Mapping[str, str]] = {
    5: {
        "priority": "P1",
        "status": "confirmed_by_private_atlas_review",
        "family": "system/navigation action-button atlas",
        "visual_evidence": "v2.2 changed texture 1 shows Korean action buttons in multiple colour states (close, reject, confirm, back, etc.)",
        "screen_gate": "trace the PC button coordinates and state variants before rendering",
    },
    8: {
        "priority": "P0",
        "status": "confirmed",
        "family": "main-screen radial command wheel / command-button atlas",
        "screen_gate": "open the PC main map command wheel and capture every labelled state",
    },
    12: {
        "priority": "P1",
        "status": "confirmed_by_private_atlas_review",
        "family": "battle military-assessment overlay",
        "visual_evidence": "v2.2 changed texture 0 shows gunpyeong, victory, defeat and merit labels",
        "screen_gate": "open the exact PC battle-assessment screen and map text rectangles",
    },
    13: {
        "priority": "P1",
        "status": "confirmed_by_private_atlas_review",
        "family": "battle-start banner family",
        "visual_evidence": "v2.2 changed textures 48..56 are nine Korean battle-title banners",
        "screen_gate": "trigger or select each matching PC battle/event before rendering",
    },
    16: {
        "priority": "P1",
        "status": "confirmed_by_private_atlas_review",
        "family": "tutorial flow diagram",
        "visual_evidence": "v2.2 changed texture 0 shows action/domestic/battle/unification and faction/castle/army/officer diagrams",
        "screen_gate": "open the exact PC tutorial/help panel and map text rectangles",
    },
    24: {
        "priority": "P2",
        "status": "confirmed_by_private_atlas_review",
        "family": "title-screen top-right additional-content label",
        "visual_evidence": "v2.1→v2.2 rendered delta is confined to 48x21 pixels at [1996,2]..[2043,22]: Japanese U+8FFD U+52A0 becomes Korean 추가; title logo remains unchanged",
        "screen_gate": "capture the matching PC title/menu surface before rendering the tiny label",
    },
}

EXPECTED_DELTAS: Mapping[str, tuple[int, ...]] = {
    "v20_to_v21": (8,),
    "v21_to_v22": (5, 8, 12, 13, 16, 24),
    "v22_to_v23": (6, 7),
    "v23_to_v24": (6, 7),
}
# Verified from the v2.1 -> v2.2 metadata delta.  The optional private
# preview can focus on these exact Korean-labelled payloads without decoding
# unrelated icon/background texture pages in the same bundle.
V21_TO_V22_CHANGED_TEXTURES: Mapping[int, tuple[int, ...]] = {
    5: (1,),
    8: (0,),
    12: (0,),
    13: tuple(range(48, 57)),
    16: (0,),
    24: (0,),
}

EXPECTED_RELEASE_ZIP_SHA256: Mapping[str, str] = {
    "v20": "A7497986FCC53312BC40B470465CD4DD0AE5179B0B9DB92526541E10987079DD",
    "v21": "473213B0013FB24C812C517A147A15D51EFCBFCE975FBB51738EFC34F5E7B387",
    "v22": "5E6354069E38BE22E3B3C9272A6CEC8A4B4110DF2486B9A63E84D1058C35D7F7",
    "v23": "A085B5D7F661786CF8E6568A36CF24E7BE1ADF81D042FF8C3D2E220D46A09388",
    "v24": "9BAC0A141A7DEBB779BF67EB35F582287B120CBDE6A4B4939AC4903315F7E04C",
}
EXPECTED_RELEASE_MEMBER_SHA256: Mapping[str, str] = {
    "v20": "79B572CE211A4D18F2A6CDF0AFD0197802463D270797993BA169F0D6BB651159",
    "v21": "C79B8F205CDAAF374B2F84F3AE4E385CE8498C5BA7CB8071DD2B9A178A27688D",
    "v22": "F179D9A89A7D20B51E26681208CA7186BDD1DC6B2F09FAF9CA8154B35933557F",
    "v23": "20A548D544BEB40A45359914777DB7467F6D319078CE43BC566F0BBD6D64F9FB",
    "v24": "086A6AC3F22F09A77E325BF23675F792AB6ACA5D9CBC35564EE6BDB4433CDB06",
}


class AuditError(ValueError):
    """Raised when an input archive drifts from the reviewed contract."""


@dataclass(frozen=True)
class SwitchInput:
    label: str
    zip_path: Path
    zip_sha256: str
    member_size: int
    member_crc32: str
    member_sha256: str
    outer: lz4.LinkArchive


def sha256_bytes(data: bytes | memoryview) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def stable_hash(value: Any) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def require_private_output(path: Path) -> Path:
    resolved = path.resolve()
    require(is_within(resolved, TMP_ROOT), f"private output must be below {TMP_ROOT}")
    return resolved


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def public_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_switch(label: str, path: Path) -> SwitchInput:
    require(path.is_file(), f"missing Switch release {label}: {path}")
    zip_hash_before = sha256_file(path)
    with zipfile.ZipFile(path) as archive:
        try:
            info = archive.getinfo(SWITCH_MEMBER)
        except KeyError as exc:
            raise AuditError(f"{path.name}: missing {SWITCH_MEMBER}") from exc
        member = archive.read(info)
    zip_hash_after = sha256_file(path)
    require(zip_hash_before == zip_hash_after, f"{path.name}: ZIP changed during read-only audit")
    outer = lz4.parse_link(member)
    require(lz4.rebuild_link(outer) == member, f"{path.name}: outer LINK identity rebuild failed")
    return SwitchInput(
        label=label,
        zip_path=path,
        zip_sha256=zip_hash_before,
        member_size=len(member),
        member_crc32=f"{info.CRC:08X}",
        member_sha256=sha256_bytes(member),
        outer=outer,
    )


def read_pc(path: Path) -> tuple[lz4.LinkArchive, dict[str, Any]]:
    require(path.is_file(), f"missing Steam JP resource: {path}")
    before = sha256_file(path)
    data = path.read_bytes()
    after = sha256_file(path)
    require(before == after, "Steam JP resource changed during read-only audit")
    outer = lz4.parse_link(data)
    require(lz4.rebuild_link(outer) == data, "Steam JP outer LINK identity rebuild failed")
    return outer, {
        "relative_path": PC_RELATIVE_PATH,
        "size": len(data),
        "sha256_before_read": before,
        "sha256_after_read": after,
        "read_only_identity_preserved": True,
        "outer_entry_count": len(outer.entries),
        "outer_link_version": outer.version,
        "outer_link_reserved": outer.reserved,
    }


def texture_metadata(texture: trace.Texture) -> dict[str, Any]:
    return {
        "texture": texture.index,
        "dimensions": [texture.width, texture.height],
        "format_code": f"0x{texture.format_code:02X}",
        "mip_count": texture.mip_count,
        "extra_version": texture.extra_version,
        "payload_size": len(texture.base_payload),
        "payload_sha256": sha256_bytes(texture.base_payload),
    }


def bundle_metadata(entry: lz4.LinkEntry, *, label: str) -> dict[str, Any]:
    require(entry.data.startswith(b"LINK"), f"{label}: outer entry is not a nested LINK")
    bundle = trace.parse_bundle(entry.data)
    slot_rows: list[dict[str, Any]] = []
    for inner in bundle.entries:
        try:
            header, raw = lz4.decompress_wrapper(inner.data)
        except lz4.LZ4Error as exc:
            raise AuditError(f"{label}: nested slot {inner.index} is not a valid LZ4 wrapper") from exc
        require(raw.startswith(b"GT1G0600"), f"{label}: nested slot {inner.index} is not G1T")
        g1t, textures = trace.parse_g1t(raw)
        slot_rows.append(
            {
                "slot": inner.index,
                "stored_size": inner.stored_size,
                "wrapper_sha256": sha256_bytes(inner.data),
                "wrapper_prefix_sha256": sha256_bytes(header.prefix),
                "wrapper_uncompressed_size": header.uncompressed_size,
                "wrapper_compressed_size": header.compressed_size,
                "raw_sha256": sha256_bytes(raw),
                "g1t": {
                    "platform": g1t["platform"],
                    "texture_count": len(textures),
                    "textures": [texture_metadata(texture) for texture in textures],
                },
            }
        )
    require(slot_rows, f"{label}: nested LINK contains no physical G1T slots")
    result = {
        "outer": {
            "index": entry.index,
            "offset": entry.offset,
            "stored_size": entry.stored_size,
            "sha256": sha256_bytes(entry.data),
        },
        "nested_link": {
            "resource_id": bundle.resource_id,
            "physical_slot_count": len(bundle.entries),
            "physical_slots": [slot.index for slot in bundle.entries],
        },
        "slots": slot_rows,
    }
    result["inventory_sha256"] = stable_hash(result)
    return result


def compact_inventory(inventory: Mapping[str, Any], detail_texture_indices: Iterable[int]) -> dict[str, Any]:
    """Publish metadata for changed textures while hashing full topology.

    Full texture metadata remains in memory only long enough to prove the
    exact delta.  This keeps the committed audit focused and source-free
    without hiding the total texture set or geometry contract.
    """

    details = set(detail_texture_indices)
    slots: list[dict[str, Any]] = []
    for slot in inventory["slots"]:
        textures = slot["g1t"]["textures"]
        slots.append(
            {
                "slot": slot["slot"],
                "stored_size": slot["stored_size"],
                "wrapper_sha256": slot["wrapper_sha256"],
                "raw_sha256": slot["raw_sha256"],
                "g1t": {
                    "platform": slot["g1t"]["platform"],
                    "texture_count": slot["g1t"]["texture_count"],
                    "texture_indices": [texture["texture"] for texture in textures],
                    "all_texture_metadata_sha256": stable_hash(textures),
                    "changed_texture_details": [
                        texture for texture in textures if texture["texture"] in details
                    ],
                },
            }
        )
    result = {
        "outer": inventory["outer"],
        "nested_link": inventory["nested_link"],
        "slots": slots,
        "full_inventory_sha256": inventory["inventory_sha256"],
    }
    result["public_inventory_sha256"] = stable_hash(result)
    return result


def entry_hashes(outer: lz4.LinkArchive) -> list[str]:
    return [sha256_bytes(entry.data) for entry in outer.entries]


def outer_delta(left: lz4.LinkArchive, right: lz4.LinkArchive, *, label: str) -> list[int]:
    require(len(left.entries) == len(right.entries), f"{label}: outer entry count changed")
    return [index for index, (a, b) in enumerate(zip(left.entries, right.entries)) if a.data != b.data]


def slot_by_id(inventory: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    return {int(row["slot"]): row for row in inventory["slots"]}


def texture_by_id(slot: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    return {int(row["texture"]): row for row in slot["g1t"]["textures"]}


def inventory_delta(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    left_slots = slot_by_id(left)
    right_slots = slot_by_id(right)
    common = sorted(set(left_slots) & set(right_slots))
    require(set(left_slots) == set(right_slots), "nested physical slot set changed")
    slot_rows: list[dict[str, Any]] = []
    for slot_id in common:
        left_slot = left_slots[slot_id]
        right_slot = right_slots[slot_id]
        left_textures = texture_by_id(left_slot)
        right_textures = texture_by_id(right_slot)
        require(set(left_textures) == set(right_textures), f"nested slot {slot_id}: texture set changed")
        changed_textures = [
            texture_id
            for texture_id in sorted(left_textures)
            if left_textures[texture_id]["payload_sha256"] != right_textures[texture_id]["payload_sha256"]
        ]
        slot_rows.append(
            {
                "slot": slot_id,
                "raw_sha256_equal": left_slot["raw_sha256"] == right_slot["raw_sha256"],
                "platform_equal": left_slot["g1t"]["platform"] == right_slot["g1t"]["platform"],
                "texture_count_equal": left_slot["g1t"]["texture_count"] == right_slot["g1t"]["texture_count"],
                "changed_texture_indices": changed_textures,
            }
        )
    return {
        "nested_resource_id_equal": left["nested_link"]["resource_id"] == right["nested_link"]["resource_id"],
        "physical_slot_count_equal": left["nested_link"]["physical_slot_count"] == right["nested_link"]["physical_slot_count"],
        "changed_slot_indices": [row["slot"] for row in slot_rows if not row["raw_sha256_equal"]],
        "slots": slot_rows,
    }


def pc_mapping_gate(
    switch: Mapping[str, Any],
    pc: Mapping[str, Any],
    selected_texture_indices: Iterable[int],
) -> dict[str, Any]:
    switch_slots = slot_by_id(switch)
    pc_slots = slot_by_id(pc)
    common = sorted(set(switch_slots) & set(pc_slots))
    slot_rows: list[dict[str, Any]] = []
    for slot_id in common:
        sw_slot = switch_slots[slot_id]
        pc_slot = pc_slots[slot_id]
        sw_textures = texture_by_id(sw_slot)
        pc_textures = texture_by_id(pc_slot)
        shared_texture_ids = sorted(
            (set(sw_textures) & set(pc_textures)) & set(selected_texture_indices)
        )
        rows = []
        for texture_id in shared_texture_ids:
            sw_texture = sw_textures[texture_id]
            pc_texture = pc_textures[texture_id]
            rows.append(
                {
                    "texture": texture_id,
                    "format_code_equal": sw_texture["format_code"] == pc_texture["format_code"],
                    "dimensions_equal": sw_texture["dimensions"] == pc_texture["dimensions"],
                    "switch_dimensions": sw_texture["dimensions"],
                    "pc_dimensions": pc_texture["dimensions"],
                }
            )
        slot_rows.append(
            {
                "slot": slot_id,
                "platform": {"switch": sw_slot["g1t"]["platform"], "pc": pc_slot["g1t"]["platform"], "equal": sw_slot["g1t"]["platform"] == pc_slot["g1t"]["platform"]},
                "texture_count_equal": sw_slot["g1t"]["texture_count"] == pc_slot["g1t"]["texture_count"],
                "textures": rows,
            }
        )
    geometry_equal_count = sum(
        1
        for row in slot_rows
        for texture in row["textures"]
        if texture["dimensions_equal"]
    )
    geometry_row_count = sum(len(row["textures"]) for row in slot_rows)
    return {
        "nested_resource_id_equal": switch["nested_link"]["resource_id"] == pc["nested_link"]["resource_id"],
        "physical_slot_set_equal": set(switch_slots) == set(pc_slots),
        "slot_rows": slot_rows,
        "selected_texture_geometry_equal_count": geometry_equal_count,
        "selected_texture_geometry_row_count": geometry_row_count,
        "whole_switch_copy_allowed": False,
        "pc_only_rebuild_required": True,
    }


def release_metadata(input_: SwitchInput) -> dict[str, Any]:
    return {
        "zip_filename": input_.zip_path.name,
        "zip_size": input_.zip_path.stat().st_size,
        "zip_sha256": input_.zip_sha256,
        "member": SWITCH_MEMBER,
        "member_size": input_.member_size,
        "member_crc32": input_.member_crc32,
        "member_sha256": input_.member_sha256,
        "outer_entry_count": len(input_.outer.entries),
        "outer_link_version": input_.outer.version,
        "outer_link_reserved": input_.outer.reserved,
    }


def build_audit(game_root: Path, releases: Mapping[str, Path]) -> dict[str, Any]:
    pc_outer, pc_input = read_pc(game_root / PC_RELATIVE_PATH)
    switches = {label: read_switch(label, Path(releases[label])) for label in RELEASE_ORDER}
    for label, input_ in switches.items():
        require(len(input_.outer.entries) == len(pc_outer.entries), f"{label}: Switch/PC outer entry count mismatch")
        require(input_.zip_sha256 == EXPECTED_RELEASE_ZIP_SHA256[label], f"{label}: release ZIP SHA-256 drifted")
        require(input_.member_sha256 == EXPECTED_RELEASE_MEMBER_SHA256[label], f"{label}: res_lang member SHA-256 drifted")

    delta_pairs = (("v20", "v21"), ("v21", "v22"), ("v22", "v23"), ("v23", "v24"))
    deltas: dict[str, Any] = {}
    for left, right in delta_pairs:
        name = f"{left}_to_{right}"
        changed = outer_delta(switches[left].outer, switches[right].outer, label=name)
        require(tuple(changed) == EXPECTED_DELTAS[name], f"{name}: changed outer indices drifted: {changed}")
        deltas[name] = {
            "left": left,
            "right": right,
            "changed_outer_indices": changed,
            "expected_changed_outer_indices": list(EXPECTED_DELTAS[name]),
            "exact_expected_delta": True,
        }

    assets: dict[str, Any] = {}
    for index in sorted(TARGETS):
        switch_v21 = bundle_metadata(switches["v21"].outer.entries[index], label=f"Switch v2.1 /{index}")
        switch_v22 = bundle_metadata(switches["v22"].outer.entries[index], label=f"Switch v2.2 /{index}")
        switch_v24 = bundle_metadata(switches["v24"].outer.entries[index], label=f"Switch v2.4 /{index}")
        pc = bundle_metadata(pc_outer.entries[index], label=f"Steam JP /{index}")
        v21_v22 = inventory_delta(switch_v21, switch_v22)
        changed_textures = tuple(
            texture
            for row in v21_v22["slots"]
            for texture in row["changed_texture_indices"]
        )
        require(
            changed_textures == V21_TO_V22_CHANGED_TEXTURES[index],
            f"/{index}: changed texture set drifted: {changed_textures}",
        )
        assets[str(index)] = {
            "logical_path": f"RES_JP/res_lang.bin/{index}",
            **TARGETS[index],
            "switch_v21": compact_inventory(switch_v21, changed_textures),
            "switch_v22": compact_inventory(switch_v22, changed_textures),
            "switch_v24": compact_inventory(switch_v24, changed_textures),
            "steam_jp": compact_inventory(pc, changed_textures),
            "switch_v21_to_v22": v21_v22,
            "switch_v22_to_v24_outer_byte_equal": switches["v22"].outer.entries[index].data == switches["v24"].outer.entries[index].data,
            "pc_mapping_gate": pc_mapping_gate(switch_v22, pc, changed_textures),
        }

    # The exact requirement behind the user-reported wheel: latest v2.4 uses
    # the v2.2 size-adjusted wheel, while v2.1 is the initial addition.
    wheel = assets["8"]
    require(wheel["switch_v21_to_v22"]["changed_slot_indices"] == [0], "wheel v2.1→v2.2 changed slot set drifted")
    require(wheel["switch_v22_to_v24_outer_byte_equal"], "wheel v2.2/v2.4 is no longer byte-identical")

    output: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "platform": "PC Steam Japanese route",
            "steam_game_version": "1.1.7",
            "route": "JP only",
            "game_files_written": False,
            "patch_candidate_created": False,
            "switch_raw_or_archive_copy": False,
        },
        "inputs": {
            "steam_jp": pc_input,
            "switch_releases": {label: release_metadata(input_) for label, input_ in switches.items()},
        },
        "release_deltas": deltas,
        "assets": assets,
        "priorities": {
            "P0": ["/8 main-screen radial command wheel; latest visual reference is v2.4 which is byte-identical to v2.2"],
            "P1": ["/5/0 texture 1 system/navigation buttons; /12/0 military-assessment overlay; /13/0 textures 48..56 battle banners; /16/0 tutorial flow diagram"],
            "P2": ["/24/0 texture 0 title-screen top-right additional-content label; deliberately preserve the title logo"],
            "out_of_scope": ["/6 and /7 are v2.3/v2.4 font-only changes, outside this raster rebuild train"],
        },
        "implementation_gate": [
            "Do not copy Switch LINK, LZ4, G1T, BC3 payload, archive, executable, or exefs bytes to the PC route.",
            "For each selected outer bundle, start from the exact Steam JP 1.1.7 structure and re-render only verified Korean text coordinates.",
            "Preserve all non-target outer entries byte-identically; preserve unrelated nested slots and non-text pixels within each target.",
            "Require private visual atlas QA plus the actual matching PC screen before game apply or release.",
        ],
        "source_free_guarantees": {
            "committed_game_archives": False,
            "committed_switch_payload_bytes": False,
            "committed_g1t_or_texture_bytes": False,
            "committed_decoded_images": False,
            "metadata_only": True,
        },
    }
    output["audit_sha256"] = stable_hash(output)
    return output


def verify_audit(audit: Mapping[str, Any]) -> None:
    require(audit.get("schema") == SCHEMA, "schema mismatch")
    scope = audit.get("scope")
    require(isinstance(scope, Mapping) and scope.get("route") == "JP only", "route must be JP only")
    require(scope.get("game_files_written") is False and scope.get("patch_candidate_created") is False, "unsafe scope flags")
    deltas = audit.get("release_deltas")
    require(isinstance(deltas, Mapping), "release_deltas missing")
    for name, expected in EXPECTED_DELTAS.items():
        row = deltas.get(name)
        require(isinstance(row, Mapping) and tuple(row.get("changed_outer_indices", ())) == expected, f"delta mismatch: {name}")
    assets = audit.get("assets")
    require(isinstance(assets, Mapping) and set(assets) == {str(index) for index in TARGETS}, "asset set mismatch")
    wheel = assets["8"]
    require(wheel.get("status") == "confirmed" and wheel.get("priority") == "P0", "wheel priority lost")
    require(wheel.get("switch_v22_to_v24_outer_byte_equal") is True, "wheel latest reference drifted")
    require(wheel["switch_v21_to_v22"]["changed_slot_indices"] == [0], "wheel slot proof drifted")
    for index, expected_textures in V21_TO_V22_CHANGED_TEXTURES.items():
        actual = tuple(
            texture
            for row in assets[str(index)]["switch_v21_to_v22"]["slots"]
            for texture in row["changed_texture_indices"]
        )
        require(actual == expected_textures, f"changed texture proof drifted at /{index}")
    require(assets["5"].get("priority") == "P1", "/5 button atlas must follow wheel")
    require(assets["24"].get("priority") == "P2", "/24 tiny title label priority drifted")
    guarantees = audit.get("source_free_guarantees")
    require(isinstance(guarantees, Mapping) and guarantees.get("metadata_only") is True, "source-free guarantee missing")
    audit_without_hash = dict(audit)
    observed = audit_without_hash.pop("audit_sha256", None)
    require(isinstance(observed, str) and observed == stable_hash(audit_without_hash), "audit hash mismatch")


def _preview_bundle(
    switch_entry: lz4.LinkEntry,
    pc_entry: lz4.LinkEntry,
    index: int,
    output_root: Path,
    texture_indices: Iterable[int] | None = None,
) -> dict[str, Any]:
    switch_bundle = trace.parse_bundle(switch_entry.data)
    pc_bundle = trace.parse_bundle(pc_entry.data)
    pc_by_slot = {entry.index: entry for entry in pc_bundle.entries}
    per_slot: list[dict[str, Any]] = []
    for switch_inner in switch_bundle.entries:
        if switch_inner.index not in pc_by_slot:
            continue
        _, sw_raw = lz4.decompress_wrapper(switch_inner.data)
        _, pc_raw = lz4.decompress_wrapper(pc_by_slot[switch_inner.index].data)
        sw_header, sw_textures = trace.parse_g1t(sw_raw)
        pc_header, pc_textures = trace.parse_g1t(pc_raw)
        slot_dir = output_root / f"outer_{index:02d}" / f"slot_{switch_inner.index:03d}"
        slot_dir.mkdir(parents=True, exist_ok=True)
        images: list[dict[str, Any]] = []
        selected_textures = None if texture_indices is None else set(texture_indices)
        for texture_index, (sw_texture, pc_texture) in enumerate(zip(sw_textures, pc_textures)):
            if selected_textures is not None and texture_index not in selected_textures:
                continue
            if sw_texture.format_code not in (0x59, 0x5B) or pc_texture.format_code not in (0x59, 0x5B):
                continue
            sw_rgba = trace.composite_checker(trace.decode_texture(sw_texture), sw_texture.width, sw_texture.height)
            pc_rgba = trace.composite_checker(trace.decode_texture(pc_texture), pc_texture.width, pc_texture.height)
            png_path = slot_dir / f"texture_{texture_index:03d}_switch.png"
            pc_png_path = slot_dir / f"texture_{texture_index:03d}_pc.png"
            atomic_write(png_path, image_codec.encode_rgba_png(sw_rgba, sw_texture.width, sw_texture.height))
            atomic_write(pc_png_path, image_codec.encode_rgba_png(pc_rgba, pc_texture.width, pc_texture.height))
            images.append({
                "texture": texture_index,
                "switch_png": str(png_path),
                "switch_png_sha256": sha256_file(png_path),
                "pc_png": str(pc_png_path),
                "pc_png_sha256": sha256_file(pc_png_path),
                "switch_dimensions": [sw_texture.width, sw_texture.height],
                "pc_dimensions": [pc_texture.width, pc_texture.height],
                "pc_rgba_sha256": sha256_bytes(pc_rgba),
            })
        per_slot.append({
            "slot": switch_inner.index,
            "switch_platform": sw_header["platform"],
            "pc_platform": pc_header["platform"],
            "images": images,
        })
    return {"outer_index": index, "slots": per_slot}


def build_previews(
    game_root: Path,
    switch_v22_path: Path,
    output_root: Path,
    outer_indices: Iterable[int] | None = None,
    changed_only: bool = False,
) -> dict[str, Any]:
    output_root = require_private_output(output_root)
    if output_root.exists():
        raise AuditError(f"refusing to replace an existing private preview root: {output_root}")
    output_root.mkdir(parents=True, exist_ok=False)
    pc_outer, pc_input = read_pc(game_root / PC_RELATIVE_PATH)
    switch = read_switch("v22", switch_v22_path)
    selected = tuple(sorted(TARGETS if outer_indices is None else set(outer_indices)))
    require(selected, "preview selection is empty")
    require(set(selected).issubset(TARGETS), f"unknown preview outer indices: {sorted(set(selected) - set(TARGETS))}")
    rows = [
        _preview_bundle(
            switch.outer.entries[index],
            pc_outer.entries[index],
            index,
            output_root,
            V21_TO_V22_CHANGED_TEXTURES[index] if changed_only else None,
        )
        for index in selected
    ]
    manifest = {
        "scope": {"private_tmp_only": True, "game_files_written": False, "switch_raw_or_archive_copy": False},
        "pc_input_sha256": pc_input["sha256_before_read"],
        "switch_v22_zip_sha256": switch.zip_sha256,
        "bundles": rows,
    }
    atomic_write(output_root / "preview_manifest.json", public_json_bytes(manifest))
    return manifest


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit")
    audit.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    audit.add_argument("--output", type=Path, default=DEFAULT_AUDIT)
    for label, path in RELEASE_PATHS.items():
        audit.add_argument(f"--{label}-zip", type=Path, default=path)
    verify = sub.add_parser("verify")
    verify.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    preview = sub.add_parser("preview")
    preview.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    preview.add_argument("--switch-v22-zip", type=Path, default=RELEASE_PATHS["v22"])
    preview.add_argument("--output-root", type=Path, default=DEFAULT_PREVIEW_ROOT)
    preview.add_argument("--outer", type=int, nargs="*", choices=sorted(TARGETS))
    preview.add_argument("--changed-only", action="store_true")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "audit":
        releases = {label: getattr(args, f"{label}_zip") for label in RELEASE_ORDER}
        audit = build_audit(args.game_root, releases)
        atomic_write(args.output, public_json_bytes(audit))
        print(f"audit={args.output}")
        print(f"audit_sha256={audit['audit_sha256']}")
        print("game_files_written=false")
        return 0
    if args.command == "verify":
        require(args.audit.is_file(), f"missing audit: {args.audit}")
        audit = json.loads(args.audit.read_text(encoding="utf-8"))
        verify_audit(audit)
        print("status=PASS")
        print("game_files_written=false")
        return 0
    if args.command == "preview":
        manifest = build_previews(
            args.game_root,
            args.switch_v22_zip,
            args.output_root,
            args.outer,
            args.changed_only,
        )
        print(f"preview_root={args.output_root}")
        print(f"bundle_count={len(manifest['bundles'])}")
        print("game_files_written=false")
        return 0
    raise AuditError(f"unknown command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, lz4.LZ4Error, trace.TraceError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
