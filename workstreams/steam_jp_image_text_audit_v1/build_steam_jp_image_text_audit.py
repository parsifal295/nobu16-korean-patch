#!/usr/bin/env python3
"""Read-only source-free audit for the next Steam JP raster-text targets.

This tool inventories only metadata and SHA-256 evidence.  It never writes a
game archive, never writes extracted textures, and deliberately omits every
resource, wrapper, G1T, BC payload, and decoded image from its public output.

Targets are intentionally narrow:

* ``RES_JP/res_lang.bin /1``       -- boot/startup-warning bundle;
* ``RES_JP/res_lang.bin /4``       -- base historical-title raster family;
* ``RES_JP_PK/res_lang_pk.bin /18`` -- PK reward label; and
* ``RES_JP_PK/res_lang_pk.bin /21`` -- PK historical-episode title card.

The public JSON is an implementation gate, not a patch.  A later renderer may
only create a candidate after it satisfies the prerequisites recorded here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


WORKSTREAM = Path(__file__).resolve().parent
PROJECT_ROOT = WORKSTREAM.parents[1]
TOOLS = PROJECT_ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-image-text-audit.v1"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_SWITCH_V13_ZIP = (
    PROJECT_ROOT / "tmp" / "third_party_switch_v13" / "NobunagaShinsei_KoreanPatch_v1.3.zip"
)
DEFAULT_SWITCH_V20_ZIP = (
    PROJECT_ROOT / "tmp" / "third_party_switch_v20" / "NobunagaShinsei_KoreanPatch_v2.0.zip"
)
DEFAULT_AUDIT = WORKSTREAM / "audit.v1.json"


class AuditError(ValueError):
    """Raised for an unexpected resource container or invalid audit."""


@dataclass(frozen=True)
class OuterEntry:
    index: int
    offset: int
    stored_size: int
    next_offset: int
    data: bytes


@dataclass(frozen=True)
class OuterArchive:
    entry_count: int
    version: int
    reserved: int
    size: int
    sha256: str
    sha256_after_read: str
    read_only_identity_preserved: bool
    entries: dict[int, OuterEntry]


TARGETS: tuple[dict[str, Any], ...] = (
    {
        "id": "base_boot_warning",
        "archive": "res_lang",
        "outer_index": 1,
        "pc_jp_relative_path": "RES_JP/res_lang.bin",
        "pc_sc_relative_path": "RES_SC/res_lang.bin",
        "logical_path": "RES_JP/res_lang.bin/1",
        "runtime": {
            "expected_surface": "게임 기동 직후 타이틀/인트로 이전의 부트 경고·고지 화면",
            "confidence": "task-confirmed target; exact slot-to-window capture is still required",
            "screen_gate": "새 프로세스로 기동해 경고 화면의 6-slot 해상도 선택과 표시 순서를 캡처",
        },
        "switch_reference": True,
    },
    {
        "id": "base_historical_title_cards",
        "archive": "res_lang",
        "outer_index": 4,
        "pc_jp_relative_path": "RES_JP/res_lang.bin",
        "pc_sc_relative_path": "RES_SC/res_lang.bin",
        "logical_path": "RES_JP/res_lang.bin/4",
        "runtime": {
            "expected_surface": "본편의 역사적 전투·이벤트 제목 카드(시네마틱/이벤트 오버레이)",
            "confidence": "decoded private sample visual confirmed a brush-title family; individual slot-to-event mapping remains pending",
            "screen_gate": "각 후보 슬롯을 이벤트 ID/화면 캡처와 1:1로 연결하고 1024×256 ink origin을 확인",
        },
        "switch_reference": True,
    },
    {
        "id": "pk_mixed_menu_labels",
        "archive": "res_lang_pk",
        "outer_index": 18,
        "pc_jp_relative_path": "RES_JP_PK/res_lang_pk.bin",
        "pc_sc_relative_path": "RES_SC_PK/res_lang_pk.bin",
        "logical_path": "RES_JP_PK/res_lang_pk.bin/18",
        "runtime": {
            "expected_surface": "PK의 혼합 메뉴/콘텐츠 라벨 묶음(보상·소목표·BGM 등 512×128 라벨)",
            "confidence": "private sample에서 서로 다른 메뉴 라벨 계열임을 확인; 실제 메뉴 경로는 open trace가 필요",
            "screen_gate": "PK 추가 콘텐츠/갤러리·보상·과제 관련 화면을 열어 각 slot의 실제 소비 경로와 배율을 캡처",
        },
        "switch_reference": False,
    },
    {
        "id": "pk_historical_episode_title",
        "archive": "res_lang_pk",
        "outer_index": 21,
        "pc_jp_relative_path": "RES_JP_PK/res_lang_pk.bin",
        "pc_sc_relative_path": "RES_SC_PK/res_lang_pk.bin",
        "logical_path": "RES_JP_PK/res_lang_pk.bin/21",
        "runtime": {
            "expected_surface": "PK 역사 에피소드/이벤트 제목 카드",
            "confidence": "decoded private visual confirmed a large brush-title card; exact trigger remains pending",
            "screen_gate": "해당 PK 역사 에피소드의 재생/목록 화면을 캡처해 1024×256 title-card 소비를 확인",
        },
        "switch_reference": False,
    },
)

ARCHIVE_PATHS = {
    "pc_jp_res_lang": "RES_JP/res_lang.bin",
    "pc_sc_res_lang": "RES_SC/res_lang.bin",
    "pc_jp_res_lang_pk": "RES_JP_PK/res_lang_pk.bin",
    "pc_sc_res_lang_pk": "RES_SC_PK/res_lang_pk.bin",
}

FORMAT_NAMES = {
    0x59: "BC1/DXT1",
    0x5B: "BC3/DXT5",
}


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _parse_outer_table(header_and_table: bytes, total_size: int) -> tuple[int, int, int, list[tuple[int, int]]]:
    require(len(header_and_table) >= 16, "outer LINK is smaller than its fixed header")
    require(header_and_table[:4] == b"LINK", "outer resource is not LINK")
    entry_count, version, reserved = struct.unpack_from("<III", header_and_table, 4)
    table_size = 16 + entry_count * 8
    require(len(header_and_table) >= table_size, "outer LINK table is truncated")
    pairs = [struct.unpack_from("<II", header_and_table, 16 + index * 8) for index in range(entry_count)]
    previous = -1
    for index, (offset, stored_size) in enumerate(pairs):
        require(offset >= previous, f"outer LINK offsets decrease at {index}")
        next_offset = pairs[index + 1][0] if index + 1 < len(pairs) else total_size
        if offset >= total_size and stored_size == 0:
            require(all(size == 0 for _, size in pairs[index:]), "outer virtual empty slot is not trailing")
        else:
            require(offset <= total_size and offset + stored_size <= total_size, f"outer slot {index} is outside the file")
            require(offset + stored_size <= next_offset, f"outer slot {index} overlaps the next slot")
        previous = offset
    return entry_count, version, reserved, pairs


def read_outer_archive_file(path: Path, indices: Iterable[int]) -> OuterArchive:
    if not path.is_file():
        raise AuditError(f"missing PC resource: {path}")
    total_size = path.stat().st_size
    sha256_before_read = sha256_file(path)
    with path.open("rb") as stream:
        fixed = stream.read(16)
        require(len(fixed) == 16 and fixed[:4] == b"LINK", f"{path.name}: not a LINK resource")
        entry_count = struct.unpack_from("<I", fixed, 4)[0]
        table = fixed + stream.read(entry_count * 8)
        parsed_count, version, reserved, pairs = _parse_outer_table(table, total_size)
        require(parsed_count == entry_count, "outer table count changed while reading")
        entries: dict[int, OuterEntry] = {}
        for index in sorted(set(indices)):
            require(0 <= index < entry_count, f"outer slot {index} is missing from {path.name}")
            offset, stored_size = pairs[index]
            next_offset = pairs[index + 1][0] if index + 1 < entry_count else total_size
            require(offset < total_size or stored_size == 0, f"target outer slot {index} is virtual")
            stream.seek(offset)
            data = stream.read(stored_size)
            require(len(data) == stored_size, f"failed to read outer slot {index}")
            entries[index] = OuterEntry(index, offset, stored_size, next_offset, data)
    sha256_after_read = sha256_file(path)
    require(sha256_before_read == sha256_after_read, f"{path.name}: input changed during read-only audit")
    return OuterArchive(
        entry_count=entry_count,
        version=version,
        reserved=reserved,
        size=total_size,
        sha256=sha256_before_read,
        sha256_after_read=sha256_after_read,
        read_only_identity_preserved=True,
        entries=entries,
    )


def read_outer_archive_bytes(data: bytes, indices: Iterable[int]) -> OuterArchive:
    entry_count, version, reserved, pairs = _parse_outer_table(data, len(data))
    entries: dict[int, OuterEntry] = {}
    for index in sorted(set(indices)):
        require(0 <= index < entry_count, f"Switch outer slot {index} is missing")
        offset, stored_size = pairs[index]
        next_offset = pairs[index + 1][0] if index + 1 < entry_count else len(data)
        require(offset < len(data) or stored_size == 0, f"Switch target outer slot {index} is virtual")
        entries[index] = OuterEntry(index, offset, stored_size, next_offset, data[offset : offset + stored_size])
    return OuterArchive(
        entry_count=entry_count,
        version=version,
        reserved=reserved,
        size=len(data),
        sha256=sha256_bytes(data),
        sha256_after_read=sha256_bytes(data),
        read_only_identity_preserved=True,
        entries=entries,
    )


def parse_bundle_slots(data: bytes, label: str) -> tuple[int, int, list[dict[str, Any]]]:
    """Parse NOBU16's 32-byte nested LINK bundle without retaining texture bytes."""

    require(len(data) >= 32 and data[:4] == b"LINK", f"{label}: expected a 32-byte LINK bundle")
    count, table_offset, resource_id, aligned_table_end = struct.unpack_from("<4I", data, 4)
    require(table_offset == 32, f"{label}: nested table offset is not 32")
    require(data[20:32] == b"\0" * 12, f"{label}: nested extension is not zero-filled")
    table_end = table_offset + count * 8
    expected_aligned_end = (table_end + 31) & ~31
    require(aligned_table_end == expected_aligned_end, f"{label}: nested aligned-table end is invalid")
    require(aligned_table_end <= len(data), f"{label}: nested table exceeds bundle")
    pairs = [struct.unpack_from("<II", data, table_offset + slot * 8) for slot in range(count)]
    result: list[dict[str, Any]] = []
    previous = -1
    for slot, (offset, stored_size) in enumerate(pairs):
        require(offset >= previous, f"{label}: nested offsets decrease at slot {slot}")
        end = offset + stored_size
        next_offset = pairs[slot + 1][0] if slot + 1 < count else end
        require(end <= next_offset, f"{label}: nested slot {slot} overlaps the next slot")
        physical = offset < len(data) and end <= len(data)
        if not physical:
            # Switch retains a few semantic slots with nominal ranges beyond
            # EOF.  Preserve their metadata as virtual rather than reading or
            # silently treating them as texture bytes.
            result.append(
                {
                    "slot": slot,
                    "physical": False,
                    "offset": offset,
                    "stored_size": stored_size,
                    "next_offset": next_offset,
                    "virtual_reason": "range_outside_physical_bundle",
                }
            )
        else:
            result.append(
                {
                    "slot": slot,
                    "physical": True,
                    "offset": offset,
                    "stored_size": stored_size,
                    "next_offset": next_offset,
                    "data": data[offset:end],
                }
            )
        previous = offset
    return count, resource_id, result


def parse_g1t(raw: bytes, label: str) -> dict[str, Any]:
    require(len(raw) >= 32 and raw[:8] == b"GT1G0600", f"{label}: expected GT1G0600")
    declared_size, directory_offset, texture_count, platform = struct.unpack_from("<4I", raw, 8)
    require(declared_size == len(raw), f"{label}: G1T declared size mismatch")
    require(texture_count > 0, f"{label}: G1T texture count is zero")
    directory_end = directory_offset + texture_count * 4
    require(32 <= directory_offset <= directory_end <= len(raw), f"{label}: G1T directory is out of range")
    relative_offsets = struct.unpack_from("<" + "I" * texture_count, raw, directory_offset)
    starts = [directory_offset + value for value in relative_offsets]
    require(starts == sorted(starts), f"{label}: G1T texture offsets are not ordered")
    require(starts[0] >= directory_end and starts[-1] < len(raw), f"{label}: G1T texture range is invalid")
    textures: list[dict[str, Any]] = []
    raw_view = memoryview(raw)
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(raw)
        require(end - start >= 8, f"{label}: texture {index} header is truncated")
        packed_info, format_code, packed_dimensions = struct.unpack_from("<BBB", raw, start)
        width = 1 << (packed_dimensions & 0x0F)
        height = 1 << (packed_dimensions >> 4)
        mip_count = packed_info >> 4
        extra_version = raw[start + 7]
        extra_length = 0
        payload_offset = start + 8
        if extra_version:
            require(end - start >= 12, f"{label}: texture {index} extra header is truncated")
            extra_length = struct.unpack_from("<I", raw, start + 8)[0]
            require(extra_length >= 4, f"{label}: texture {index} extra header length is invalid")
            payload_offset = start + 8 + extra_length
        require(payload_offset <= end, f"{label}: texture {index} payload begins beyond texture end")
        textures.append(
            {
                "texture": index,
                "dimensions": [width, height],
                "format_code": f"0x{format_code:02X}",
                "format_name": FORMAT_NAMES.get(format_code, "unclassified_codec_required"),
                "mip_count": mip_count,
                "extra_version": extra_version,
                "extra_length": extra_length,
                "node_size": end - start,
                "node_sha256": sha256_bytes(raw_view[start:end]),
                "payload_size": end - payload_offset,
                "payload_sha256": sha256_bytes(raw_view[payload_offset:end]),
            }
        )
    return {
        "magic": "GT1G0600",
        "declared_size": declared_size,
        "directory_offset": directory_offset,
        "texture_count": texture_count,
        "platform": platform,
        "textures": textures,
    }


def inspect_nested_slot(slot: dict[str, Any], label: str) -> dict[str, Any]:
    result = {key: value for key, value in slot.items() if key != "data"}
    if not slot["physical"]:
        return result
    wrapper = slot["data"]
    result["wrapper_sha256"] = sha256_bytes(wrapper)
    try:
        header, raw = lz4.decompress_wrapper(wrapper)
    except lz4.LZ4Error as exc:
        result.update({"decode_status": "not_raw_lz4_wrapper", "decode_error": str(exc)})
        return result
    try:
        result.update(
            {
                "decode_status": "decoded",
                "wrapper_uncompressed_size": header.uncompressed_size,
                "wrapper_compressed_size": header.compressed_size,
                "wrapper_prefix_sha256": sha256_bytes(header.prefix),
                "raw_sha256": sha256_bytes(raw),
                "raw_kind": "GT1G0600" if raw.startswith(b"GT1G0600") else "other",
            }
        )
        if raw.startswith(b"GT1G0600"):
            result["g1t"] = parse_g1t(raw, label)
    finally:
        # Never retain raw texture bytes in a result object or public output.
        del raw
    return result


def _summary_slots(slots: list[dict[str, Any]]) -> dict[str, Any]:
    physical = [slot for slot in slots if slot["physical"]]
    g1t_slots = [slot for slot in physical if "g1t" in slot]
    texture_rows = [texture for slot in g1t_slots for texture in slot["g1t"]["textures"]]
    dimensions = Counter("×".join(str(part) for part in texture["dimensions"]) for texture in texture_rows)
    formats = Counter(texture["format_code"] for texture in texture_rows)
    return {
        "table_slot_count": len(slots),
        "physical_slot_count": len(physical),
        "virtual_slot_count": len(slots) - len(physical),
        "decoded_g1t_slot_count": len(g1t_slots),
        "texture_count": len(texture_rows),
        "format_counts": dict(sorted(formats.items())),
        "dimension_counts": dict(sorted(dimensions.items())),
    }


def inspect_target(archive: OuterArchive, outer_index: int, archive_relative_path: str) -> dict[str, Any]:
    outer = archive.entries[outer_index]
    label = f"{archive_relative_path}/{outer_index}"
    slot_count, resource_id, parsed_slots = parse_bundle_slots(outer.data, label)
    slots = [inspect_nested_slot(slot, f"{label}/{slot['slot']}") for slot in parsed_slots]
    target = {
        "path": f"{archive_relative_path}/{outer_index}",
        "outer_index": outer_index,
        "outer_entry": {
            "offset": outer.offset,
            "stored_size": outer.stored_size,
            "next_offset": outer.next_offset,
            "sha256": sha256_bytes(outer.data),
        },
        "nested_link": {
            "resource_id": resource_id,
            "table_slot_count": slot_count,
        },
        "summary": _summary_slots(slots),
        "slots": slots,
    }
    target["inventory_sha256"] = stable_hash(target)
    return target


def _layout_signature(slot: dict[str, Any]) -> list[dict[str, Any]] | None:
    if "g1t" not in slot:
        return None
    return [
        {
            "dimensions": texture["dimensions"],
            "format_code": texture["format_code"],
            "mip_count": texture["mip_count"],
            "extra_version": texture["extra_version"],
            "extra_length": texture["extra_length"],
            "payload_size": texture["payload_size"],
        }
        for texture in slot["g1t"]["textures"]
    ]


def compare_targets(left: dict[str, Any], right: dict[str, Any], *, left_label: str, right_label: str) -> dict[str, Any]:
    left_slots = {slot["slot"]: slot for slot in left["slots"]}
    right_slots = {slot["slot"]: slot for slot in right["slots"]}
    rows: list[dict[str, Any]] = []
    for slot_index in sorted(set(left_slots) | set(right_slots)):
        left_slot = left_slots.get(slot_index)
        right_slot = right_slots.get(slot_index)
        row: dict[str, Any] = {"slot": slot_index, f"{left_label}_present": left_slot is not None, f"{right_label}_present": right_slot is not None}
        if left_slot is None or right_slot is None:
            rows.append(row)
            continue
        row.update(
            {
                "both_physical": bool(left_slot["physical"] and right_slot["physical"]),
                "stored_size_equal": left_slot["stored_size"] == right_slot["stored_size"],
                "wrapper_sha256_equal": left_slot.get("wrapper_sha256") == right_slot.get("wrapper_sha256"),
                "raw_sha256_equal": left_slot.get("raw_sha256") == right_slot.get("raw_sha256"),
                "g1t_layout_equal": _layout_signature(left_slot) == _layout_signature(right_slot),
            }
        )
        left_payloads = [item["payload_sha256"] for item in left_slot.get("g1t", {}).get("textures", [])]
        right_payloads = [item["payload_sha256"] for item in right_slot.get("g1t", {}).get("textures", [])]
        row["texture_payload_sha256_equal"] = left_payloads == right_payloads
        row["changed_texture_payload_count"] = sum(
            first != second for first, second in zip(left_payloads, right_payloads)
        ) + abs(len(left_payloads) - len(right_payloads))
        rows.append(row)
    raw_equal = sum(row.get("raw_sha256_equal") is True for row in rows)
    raw_different = sum(row.get("raw_sha256_equal") is False for row in rows)
    payload_different = sum(row.get("texture_payload_sha256_equal") is False for row in rows)
    result = {
        "left": {"label": left_label, "path": left["path"], "inventory_sha256": left["inventory_sha256"]},
        "right": {"label": right_label, "path": right["path"], "inventory_sha256": right["inventory_sha256"]},
        "table_slot_count_equal": left["summary"]["table_slot_count"] == right["summary"]["table_slot_count"],
        "physical_slot_count_equal": left["summary"]["physical_slot_count"] == right["summary"]["physical_slot_count"],
        "slots": rows,
        "summary": {
            "slot_row_count": len(rows),
            "raw_sha256_equal_slot_count": raw_equal,
            "raw_sha256_different_slot_count": raw_different,
            "texture_payload_different_slot_count": payload_different,
        },
    }
    result["comparison_sha256"] = stable_hash(result)
    return result


def inspect_pc_archives(game_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[int, dict[str, Any]]]]:
    indices_by_archive = {
        "pc_jp_res_lang": [1, 4],
        "pc_sc_res_lang": [1, 4],
        "pc_jp_res_lang_pk": [18, 21],
        "pc_sc_res_lang_pk": [18, 21],
    }
    archive_metadata: dict[str, dict[str, Any]] = {}
    targets: dict[str, dict[int, dict[str, Any]]] = {}
    for archive_id, indices in indices_by_archive.items():
        relative_path = ARCHIVE_PATHS[archive_id]
        archive = read_outer_archive_file(game_root / relative_path, indices)
        archive_metadata[archive_id] = {
            "relative_path": relative_path,
            "size": archive.size,
            "sha256_before_read": archive.sha256,
            "sha256_after_read": archive.sha256_after_read,
            "read_only_identity_preserved": archive.read_only_identity_preserved,
            "outer_link_entry_count": archive.entry_count,
            "outer_link_version": archive.version,
            "outer_link_reserved": archive.reserved,
        }
        targets[archive_id] = {
            index: inspect_target(archive, index, relative_path)
            for index in indices
        }
    return archive_metadata, targets


def _zip_member_identity(path: Path, member: str) -> tuple[dict[str, Any], bytes | None]:
    if not path.is_file():
        raise AuditError(f"missing Switch reference ZIP: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        present = member in names
        record: dict[str, Any] = {
            "zip_filename": path.name,
            "zip_size": path.stat().st_size,
            "zip_sha256": sha256_file(path),
            "member": member,
            "member_present": present,
        }
        if not present:
            return record, None
        info = archive.getinfo(member)
        payload = archive.read(member)
        record.update(
            {
                "member_size": info.file_size,
                "member_crc32": f"{info.CRC:08X}",
                "member_sha256": sha256_bytes(payload),
            }
        )
        return record, payload


def inspect_switch_sources(switch_v13_zip: Path, switch_v20_zip: Path) -> dict[str, Any]:
    v13, v13_payload = _zip_member_identity(switch_v13_zip, SWITCH_MEMBER)
    v20, v20_payload = _zip_member_identity(switch_v20_zip, SWITCH_MEMBER)
    require(v13_payload is not None and v20_payload is not None, "Switch reference ZIP lacks RES_JP/res_lang.bin")
    same_member = v13["member_sha256"] == v20["member_sha256"]
    require(same_member, "Switch v1.3/v2.0 RES_JP/res_lang.bin differs; source version must be selected explicitly")
    archive = read_outer_archive_bytes(v13_payload, [1, 4])
    source_targets = {
        1: inspect_target(archive, 1, "RES_JP/res_lang.bin"),
        4: inspect_target(archive, 4, "RES_JP/res_lang.bin"),
    }
    # Release archives intentionally contain only the base RES_JP member.  Do
    # not imply that a PK resource source exists merely because the PC has one.
    with zipfile.ZipFile(switch_v13_zip) as source_zip:
        v13_pk_present = "NobunagaShinsei_KR/romfs/RES_JP_PK/res_lang_pk.bin" in source_zip.namelist()
    with zipfile.ZipFile(switch_v20_zip) as source_zip:
        v20_pk_present = "NobunagaShinsei_KR/romfs/RES_JP_PK/res_lang_pk.bin" in source_zip.namelist()
    return {
        "v13": v13,
        "v20": v20,
        "v13_v20_base_member_sha256_equal": same_member,
        "canonical_member": "v1.3 (byte-identical to v2.0)",
        "res_jp_pk_member_present": {"v1.3": v13_pk_present, "v2.0": v20_pk_present},
        "base_targets": source_targets,
    }


def target_switch_source(target: dict[str, Any], switch: dict[str, Any], pc_jp: dict[str, Any]) -> dict[str, Any]:
    if not target["switch_reference"]:
        return {
            "status": "unavailable",
            "reason": "Switch v1.3/v2.0 distribution has no RES_JP_PK/res_lang_pk.bin member",
            "whole_switch_resource_copy_allowed": False,
        }
    source = switch["base_targets"][target["outer_index"]]
    return {
        "status": "available_reference_only",
        "member": SWITCH_MEMBER,
        "canonical_source": switch["canonical_member"],
        "whole_switch_resource_copy_allowed": False,
        "pc_jp_vs_switch_structure": compare_targets(pc_jp, source, left_label="pc_jp", right_label="switch_ko"),
        "switch_inventory": source,
    }


def build_audit(game_root: Path, switch_v13_zip: Path, switch_v20_zip: Path) -> dict[str, Any]:
    pc_archives, pc_targets = inspect_pc_archives(game_root)
    switch = inspect_switch_sources(switch_v13_zip, switch_v20_zip)
    result_targets: list[dict[str, Any]] = []
    for target in TARGETS:
        if target["archive"] == "res_lang":
            jp_key, sc_key = "pc_jp_res_lang", "pc_sc_res_lang"
        else:
            jp_key, sc_key = "pc_jp_res_lang_pk", "pc_sc_res_lang_pk"
        outer_index = target["outer_index"]
        jp = pc_targets[jp_key][outer_index]
        sc = pc_targets[sc_key][outer_index]
        row = {
            "id": target["id"],
            "logical_path": target["logical_path"],
            "pc_jp": jp,
            "pc_sc": sc,
            "jp_sc_difference_evidence": compare_targets(jp, sc, left_label="jp", right_label="sc"),
            "switch_source_availability": target_switch_source(target, switch, jp),
            "expected_runtime_screen_mapping": target["runtime"],
            "safe_next_implementation_prerequisites": [],
        }
        if target["id"] == "base_boot_warning":
            row["safe_next_implementation_prerequisites"] = [
                "format 0x01의 PC G1T pixel codec/extra-header contract를 독립적으로 판독·재인코드 검증한다",
                "6개 slot의 해상도 선택과 부트 화면 소비 순서를 새 기동 화면 캡처로 확정한다",
                "PC JP 원본 outer/inner LINK와 wrapper를 기준으로 slot별 재조립하며 Switch 바이트를 복사하지 않는다",
            ]
        elif target["id"] == "base_historical_title_cards":
            row["safe_next_implementation_prerequisites"] = [
                "105개 슬롯을 이벤트 ID와 화면 캡처에 1:1로 매핑하고 의미/용어 검토표를 만든다",
                "PC 1024×256 BC3 canvas의 alpha bbox·ink origin을 유지한 채 한국어 픽셀을 PC G1T/LINK로 재조립한다",
                "Switch v1.3/v2.0는 번역 참고 픽셀만 사용하고, Switch G1T/LINK/wrapper/전체 파일 복사는 금지한다",
            ]
        else:
            row["safe_next_implementation_prerequisites"] = [
                "Switch 배포본에 해당 RES_JP_PK 소스가 없으므로 한국어 문구와 자체 렌더 계획을 먼저 확정한다",
                "JP/SC 차이 증거 및 실제 PK 화면 캡처로 선택한 PC slot의 소비를 검증한다",
                "PC JP 1.1.7 원본의 해당 inner slot만 재조립하고 outer LINK의 비대상 슬롯을 byte-identical로 보존한다",
            ]
        result_targets.append(row)
    audit = {
        "schema": SCHEMA,
        "scope": {
            "platform": "PC Steam Japanese route",
            "steam_game_version": "1.1.7",
            "game_files_written": False,
            "patch_candidate_created": False,
            "target_ids": [target["id"] for target in TARGETS],
        },
        "pc_inputs": pc_archives,
        "switch_reference_inputs": {
            key: value
            for key, value in switch.items()
            if key not in {"base_targets"}
        },
        "targets": result_targets,
        "global_safe_implementation_prerequisites": [
            "게임을 종료한 상태에서 Steam JP 1.1.7 입력 SHA를 다시 고정한다",
            "각 변경 대상은 기존 PC archive/inner LINK/raw-LZ4/G1T에서 재조립하고 비대상 바이트 보존을 검증한다",
            "새 후보는 private tmp에서만 생성·재추출·화면 QA한 뒤 복원 가능한 트랜잭션으로만 적용한다",
            "메모리 패치, DLL 주입, 후킹, EXE/레지스트리 변경은 사용하지 않는다",
        ],
        "source_free_guarantees": {
            "committed_game_archives": False,
            "committed_g1t_or_texture_bytes": False,
            "committed_decoded_images": False,
            "committed_switch_payload_bytes": False,
            "metadata_only": True,
        },
    }
    audit["audit_sha256"] = stable_hash(audit)
    validate_audit(audit)
    return audit


def validate_audit(audit: dict[str, Any]) -> None:
    require(audit.get("schema") == SCHEMA, "schema mismatch")
    expected_audit_sha = stable_hash({key: value for key, value in audit.items() if key != "audit_sha256"})
    require(audit.get("audit_sha256") == expected_audit_sha, "audit SHA-256 mismatch")
    require(audit.get("scope", {}).get("game_files_written") is False, "audit cannot claim a game write")
    require(audit.get("source_free_guarantees", {}).get("metadata_only") is True, "source-free metadata flag is missing")
    targets = audit.get("targets")
    require(isinstance(targets, list) and len(targets) == len(TARGETS), "unexpected target count")
    expected = {target["id"]: target for target in TARGETS}
    observed = {target.get("id"): target for target in targets}
    require(set(observed) == set(expected), "target ID set mismatch")
    for target_id, expected_target in expected.items():
        row = observed[target_id]
        require(row["logical_path"] == expected_target["logical_path"], f"{target_id}: logical path mismatch")
        for language in ("pc_jp", "pc_sc"):
            details = row[language]
            require(details["summary"]["table_slot_count"] > 0, f"{target_id}: no {language} slots")
            require(details["summary"]["physical_slot_count"] > 0, f"{target_id}: no physical {language} slots")
            for slot in details["slots"]:
                require("data" not in slot and "raw" not in slot, f"{target_id}: binary payload leaked into audit")
                if slot["physical"]:
                    require("wrapper_sha256" in slot, f"{target_id}: missing wrapper hash")
        switch_status = row["switch_source_availability"]["status"]
        if expected_target["switch_reference"]:
            require(switch_status == "available_reference_only", f"{target_id}: missing Switch reference")
        else:
            require(switch_status == "unavailable", f"{target_id}: unexpected Switch PK source")
    source = audit["switch_reference_inputs"]
    require(source["v13_v20_base_member_sha256_equal"] is True, "Switch v1.3/v2.0 source equality gate failed")
    require(source["res_jp_pk_member_present"] == {"v1.3": False, "v2.0": False}, "Switch PK availability result drifted")


def write_audit(audit: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser("audit", help="read inputs and write source-free audit JSON")
    audit_parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    audit_parser.add_argument("--switch-v13-zip", type=Path, default=DEFAULT_SWITCH_V13_ZIP)
    audit_parser.add_argument("--switch-v20-zip", type=Path, default=DEFAULT_SWITCH_V20_ZIP)
    audit_parser.add_argument("--output", type=Path, default=DEFAULT_AUDIT)
    verify_parser = subparsers.add_parser("verify", help="validate an existing source-free audit without game I/O")
    verify_parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "audit":
        audit = build_audit(args.game_root, args.switch_v13_zip, args.switch_v20_zip)
        write_audit(audit, args.output)
        print(json.dumps({"output": str(args.output), "audit_sha256": audit["audit_sha256"], "target_count": len(audit["targets"])}, ensure_ascii=False))
        return 0
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    validate_audit(audit)
    print(json.dumps({"audit": str(args.audit), "audit_sha256": audit.get("audit_sha256"), "status": "PASS"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
