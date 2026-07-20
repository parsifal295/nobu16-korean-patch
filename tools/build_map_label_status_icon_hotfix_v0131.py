#!/usr/bin/env python3
"""Build the issue-72 dynamic map-label overlay candidate for v0.13.1.

The horizontal castle label already exposes its rendered width through the
widget at label-object offset 0x140.  This patch wraps the single status-icon
update call in FUN_140F98390 and, after the original update has completed:

* moves the active status icon at label-object offset 0x248 by that width and
  vertically centers it inside the horizontal name plate;
* finds the same castle key in the paired supply-label pool and places that
  group at label-root X + rendered width.

No fixed pixel offset is used.  The independent castle/crest icon pool and
the special map cursor path are deliberately untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import build_map_label_hotfix_v0121 as pe_tools


EXPECTED_V0130_SHA256 = (
    "FCA1D8CF58D44BDFAEFF338F5CF935AB9B2FA0F611EDC26CC8E9DF6E40B9D892"
)
# Pinned after the first deterministic build and before live-game QA.
EXPECTED_CANDIDATE_SHA256 = (
    "811F6B31C09AD87F2D73F1349FB17AA4C9ABEA76F2415083C78E932D0B1D5A31"
)

IMAGE_BASE = 0x140000000
STATUS_UPDATE_VA = 0x140FA52B0
STATUS_UPDATE_CALL_SITE = 0x140F98764
STATUS_UPDATE_CALL_BEFORE = bytes.fromhex("E8 47 CB 00 00")

POOL_STRIDE = 0x10038
POOL_HEADER_BASE_VA = 0x142252694
LABEL_POOL_1_VA = POOL_HEADER_BASE_VA + POOL_STRIDE
SUPPLY_POOL_2_VA = POOL_HEADER_BASE_VA + POOL_STRIDE * 2
LABEL_POOL_3_VA = POOL_HEADER_BASE_VA + POOL_STRIDE * 3
SUPPLY_POOL_4_VA = POOL_HEADER_BASE_VA + POOL_STRIDE * 4
LABEL_POOL_PAIR_DELTA = LABEL_POOL_3_VA - LABEL_POOL_1_VA

LABEL_WIDTH_WIDGET_OFFSET = 0x140
LABEL_STATUS_WIDGET_OFFSET = 0x248
WIDGET_X_OFFSET = 0x08
WIDGET_WIDTH_OFFSET = 0x10
POOL_RECORD_STRIDE = 0x30
POOL_KEY_TYPE_OFFSET = 0x08
POOL_KEY_POINTER_OFFSET = 0x10
CASTLE_KEY_TYPE = 2
ACTIVE_STATUS_BASE_X_BITS = 0x41F00000  # 30.0f

CODE_SECTION = ".mlbd"
EXPECTED_SECTION_VIRTUAL_SIZE = 35_275_348
EXPECTED_SECTION_RAW_SIZE = 35_275_776
IMAGE_SCN_CNT_CODE = 0x20
IMAGE_SCN_MEM_EXECUTE = 0x20000000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def rel32(source_next_va: int, target_va: int) -> bytes:
    displacement = target_va - source_next_va
    if not -(1 << 31) <= displacement < (1 << 31):
        raise RuntimeError("rel32 target out of range")
    return struct.pack("<i", displacement)


def pe_checksum_offset(data: bytes) -> int:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    optional = pe + 24
    if data[pe : pe + 4] != b"PE\0\0" or struct.unpack_from("<H", data, optional)[0] != 0x20B:
        raise RuntimeError("input is not PE32+")
    return optional + 64


def set_pe_checksum(data: bytearray) -> None:
    checksum_offset = pe_checksum_offset(data)
    data[checksum_offset : checksum_offset + 4] = b"\0" * 4
    total = 0
    for offset in range(0, len(data), 2):
        if checksum_offset <= offset < checksum_offset + 4:
            word = 0
        else:
            high = data[offset + 1] if offset + 1 < len(data) else 0
            word = data[offset] | high << 8
        total += word
        total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    struct.pack_into("<I", data, checksum_offset, (total + len(data)) & 0xFFFFFFFF)


class CodeBuilder:
    def __init__(self, base_va: int) -> None:
        self.base_va = base_va
        self.code = bytearray()
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, int, str]] = []

    @property
    def va(self) -> int:
        return self.base_va + len(self.code)

    def emit(self, raw: bytes | str) -> None:
        self.code += bytes.fromhex(raw) if isinstance(raw, str) else raw

    def label(self, name: str) -> None:
        if name in self.labels:
            raise RuntimeError(f"duplicate code label: {name}")
        self.labels[name] = len(self.code)

    def call(self, target_va: int) -> None:
        call_va = self.va
        self.emit(b"\xE8" + rel32(call_va + 5, target_va))

    def lea_rip(self, prefix: bytes | str, target_va: int) -> None:
        raw = bytes.fromhex(prefix) if isinstance(prefix, str) else prefix
        instruction_va = self.va
        self.emit(raw + rel32(instruction_va + len(raw) + 4, target_va))

    def branch8(self, opcode: int, label: str) -> None:
        self.emit(bytes((opcode, 0)))
        self.fixups.append((len(self.code) - 1, 1, label))

    def branch32(self, opcode: int, label: str) -> None:
        self.emit(bytes((0x0F, opcode)) + b"\0\0\0\0")
        self.fixups.append((len(self.code) - 4, 4, label))

    def finish(self) -> bytes:
        for offset, size, label in self.fixups:
            if label not in self.labels:
                raise RuntimeError(f"undefined code label: {label}")
            target = self.labels[label]
            next_offset = offset + size
            displacement = target - next_offset
            if size == 1:
                if not -128 <= displacement <= 127:
                    raise RuntimeError(f"short branch out of range: {label}")
                struct.pack_into("<b", self.code, offset, displacement)
            else:
                struct.pack_into("<i", self.code, offset, displacement)
        return bytes(self.code)


def build_injected_code(code_va: int) -> tuple[bytes, dict[str, int]]:
    code = CodeBuilder(code_va)
    code.label("status_and_supply_wrapper")

    # FUN_140FA52B0 has six parameters.  Forward both stack arguments while
    # retaining the label object beyond the original call.  At wrapper entry
    # the incoming argument 5/6 slots are [rsp+0x28]/[rsp+0x30].
    code.emit("48 83 EC 58")          # sub rsp, 0x58 (shadow + locals, aligned)
    code.emit("48 89 4C 24 40")       # mov [rsp+0x40], rcx (label object)
    code.emit("8B 84 24 80 00 00 00") # mov eax, [rsp+0x80] (incoming arg 5)
    code.emit("89 44 24 20")          # mov [rsp+0x20], eax (forward arg 5)
    code.emit("8B 84 24 88 00 00 00") # mov eax, [rsp+0x88] (incoming arg 6)
    code.emit("89 44 24 28")          # mov [rsp+0x28], eax (forward arg 6)
    code.call(STATUS_UPDATE_VA)
    code.emit("48 8B 4C 24 40")       # mov rcx, [rsp+0x40] (label object)
    code.emit("48 85 C9")             # test rcx, rcx
    code.branch32(0x84, "return")

    code.emit("48 8B 81 40 01 00 00") # mov rax, [rcx+0x140] (width widget)
    code.emit("48 85 C0")             # test rax, rax
    code.branch32(0x84, "return")
    code.emit("F3 0F 10 48 10")       # movss xmm1, [rax+0x10] (rendered width)
    code.emit("0F 57 C0")             # xorps xmm0, xmm0
    code.emit("0F 2F C8")             # comiss xmm1, xmm0
    code.branch32(0x86, "return")     # jbe return (zero, negative, or NaN)

    # The original status writer has just restored active icons to the native
    # horizontal base X of 30.0.  Add width exactly once; leave the inactive
    # sentinel (312.0) and every unrelated child untouched.
    code.emit("48 8B 91 48 02 00 00") # mov rdx, [rcx+0x248] (status widget)
    code.emit("48 85 D2")             # test rdx, rdx
    code.branch8(0x74, "find_label_pool")
    code.emit("81 7A 08 00 00 F0 41") # cmp dword [rdx+8], 0x41f00000
    code.branch8(0x75, "find_label_pool")
    code.emit("F3 0F 10 42 08")       # movss xmm0, [rdx+8]
    code.emit("F3 0F 58 C1")          # addss xmm0, xmm1
    code.emit("F3 0F 11 42 08")       # movss [rdx+8], xmm0

    # The old vertical layout also leaves active status variants at Y=79/92,
    # visibly above the horizontal name plate.  Derive the correct Y from the
    # live widgets instead of using another fixed offset:
    # plate Y + (plate height - status height) / 2.
    code.emit("F3 0F 10 40 0C")       # movss xmm0, [rax+0xc] (plate Y)
    code.emit("F3 0F 10 50 14")       # movss xmm2, [rax+0x14] (plate height)
    code.emit("F3 0F 5C 52 14")       # subss xmm2, [rdx+0x14] (status height)
    code.emit("41 BA 00 00 00 3F")    # mov r10d, 0x3f000000 (0.5f)
    code.emit("66 41 0F 6E DA")       # movd xmm3, r10d
    code.emit("F3 0F 59 D3")          # mulss xmm2, xmm3
    code.emit("F3 0F 58 C2")          # addss xmm0, xmm2
    code.emit("F3 0F 11 42 0C")       # movss [rdx+0xc], xmm0

    # Find which main-label pool owns RCX.  The pool header is an unaligned
    # {uint32 count; uint64 records;} pair and every record is 0x30 bytes.
    code.label("find_label_pool")
    code.lea_rip("4C 8D 05", LABEL_POOL_1_VA)  # lea r8, label pool 1
    code.emit("41 BB 02 00 00 00")    # mov r11d, 2 (label pools 1 and 3)

    code.label("label_pool_loop")
    code.emit("45 8B 08")             # mov r9d, [r8] (count)
    code.emit("4D 8B 50 04")          # mov r10, [r8+4] (records, unaligned)
    code.emit("31 C0")                # xor eax, eax (index)

    code.label("label_record_loop")
    code.emit("44 39 C8")             # cmp eax, r9d
    code.branch8(0x73, "next_label_pool")
    code.emit("49 39 0A")             # cmp [r10], rcx (label object)
    code.branch8(0x74, "label_record_found")
    code.emit("49 83 C2 30")          # add r10, 0x30
    code.emit("FF C0")                # inc eax
    code.branch8(0xEB, "label_record_loop")

    code.label("next_label_pool")
    code.emit("49 81 C0 70 00 02 00") # add r8, 2 * 0x10038 (pool 1 -> 3)
    code.emit("41 FF CB")             # dec r11d
    code.branch8(0x75, "label_pool_loop")
    code.branch32(0x84, "return")     # jz return

    code.label("label_record_found")
    code.emit("41 83 7A 08 02")       # cmp dword [r10+8], castle key type 2
    code.branch32(0x85, "return")
    code.emit("49 8B 52 10")          # mov rdx, [r10+0x10] (castle key)
    code.emit("48 85 D2")             # test rdx, rdx
    code.branch32(0x84, "return")

    # The supply pool immediately follows its corresponding main-label pool:
    # 1 -> 2 and 3 -> 4.  Match by the exact castle key, then anchor the whole
    # group at label-root X + rendered width.
    code.emit("49 81 C0 38 00 01 00") # add r8, 0x10038 (paired supply pool)
    code.emit("45 8B 08")             # mov r9d, [r8] (count)
    code.emit("4D 8B 50 04")          # mov r10, [r8+4] (records)
    code.emit("31 C0")                # xor eax, eax (index)

    code.label("supply_record_loop")
    code.emit("44 39 C8")             # cmp eax, r9d
    code.branch8(0x73, "return_short")
    code.emit("41 83 7A 08 02")       # cmp dword [r10+8], castle key type 2
    code.branch8(0x75, "next_supply_record")
    code.emit("49 39 52 10")          # cmp [r10+0x10], rdx
    code.branch8(0x75, "next_supply_record")
    code.emit("49 8B 02")             # mov rax, [r10] (supply object)
    code.emit("48 85 C0")             # test rax, rax
    code.branch8(0x74, "return_short")
    code.emit("F3 0F 10 41 08")       # movss xmm0, [rcx+8] (label root X)
    code.emit("F3 0F 58 C1")          # addss xmm0, xmm1
    code.emit("F3 0F 11 40 08")       # movss [rax+8], xmm0 (supply root X)
    code.branch8(0xEB, "return_short")

    code.label("next_supply_record")
    code.emit("49 83 C2 30")          # add r10, 0x30
    code.emit("FF C0")                # inc eax
    code.branch8(0xEB, "supply_record_loop")

    code.label("return_short")
    code.branch8(0xEB, "return")
    code.label("return")
    code.emit("48 83 C4 58 C3")       # add rsp, 0x58; ret

    injected = code.finish()
    labels = {name: code_va + offset for name, offset in code.labels.items()}
    return injected, labels


def build(source_path: Path, output_path: Path, manifest_path: Path) -> dict[str, object]:
    source = source_path.read_bytes()
    source_hash = sha256(source)
    if source_hash != EXPECTED_V0130_SHA256:
        raise RuntimeError(f"v0.13.0 candidate hash gate failed: {source_hash}")

    pe = pe_tools.parse_pe(source)
    if pe["image_base"] != IMAGE_BASE:
        raise RuntimeError("unexpected image base")
    sections = [section for section in pe["sections"] if section["name"] == CODE_SECTION]
    if len(sections) != 1:
        raise RuntimeError(f"expected exactly one {CODE_SECTION} section")
    section = sections[0]
    if section["virtual_size"] != EXPECTED_SECTION_VIRTUAL_SIZE:
        raise RuntimeError("unexpected .mlbd virtual size")
    if section["raw_size"] != EXPECTED_SECTION_RAW_SIZE:
        raise RuntimeError("unexpected .mlbd raw size")

    unaligned_file_offset = section["raw_pointer"] + section["virtual_size"]
    code_file_offset = (unaligned_file_offset + 15) & ~15
    code_padding = code_file_offset - unaligned_file_offset
    code_va = IMAGE_BASE + section["rva"] + section["virtual_size"] + code_padding
    injected, labels = build_injected_code(code_va)
    raw_end = section["raw_pointer"] + section["raw_size"]
    if code_file_offset + len(injected) > raw_end:
        raise RuntimeError("issue-72 code exceeds .mlbd raw tail")
    if source[unaligned_file_offset : code_file_offset + len(injected)] != b"\0" * (
        code_padding + len(injected)
    ):
        raise RuntimeError(".mlbd code tail is not empty")

    candidate = bytearray(source)
    candidate[code_file_offset : code_file_offset + len(injected)] = injected
    virtual_size_offset = section["header_offset"] + 8
    characteristics_offset = section["header_offset"] + 36
    new_virtual_size = section["virtual_size"] + code_padding + len(injected)
    new_characteristics = section["characteristics"] | IMAGE_SCN_CNT_CODE | IMAGE_SCN_MEM_EXECUTE
    struct.pack_into("<I", candidate, virtual_size_offset, new_virtual_size)
    struct.pack_into("<I", candidate, characteristics_offset, new_characteristics)

    hook_offset = pe_tools.va_to_file(source, pe, STATUS_UPDATE_CALL_SITE)
    before = source[hook_offset : hook_offset + 5]
    if before != STATUS_UPDATE_CALL_BEFORE:
        raise RuntimeError(
            f"status-update hook mismatch at 0x{STATUS_UPDATE_CALL_SITE:X}: "
            f"{before.hex(' ').upper()}"
        )
    target = STATUS_UPDATE_CALL_SITE + 5 + struct.unpack_from("<i", before, 1)[0]
    if target != STATUS_UPDATE_VA:
        raise RuntimeError(f"status-update target mismatch: 0x{target:X}")
    wrapper_va = labels["status_and_supply_wrapper"]
    after = b"\xE8" + rel32(STATUS_UPDATE_CALL_SITE + 5, wrapper_va)
    candidate[hook_offset : hook_offset + 5] = after

    checksum_offset = pe_checksum_offset(candidate)
    set_pe_checksum(candidate)

    result = bytes(candidate)
    if len(result) != len(source):
        raise RuntimeError("candidate size changed")
    reviewed_offsets = set(range(code_file_offset, code_file_offset + len(injected)))
    reviewed_offsets.update(range(virtual_size_offset, virtual_size_offset + 4))
    reviewed_offsets.update(range(characteristics_offset, characteristics_offset + 4))
    reviewed_offsets.update(range(hook_offset, hook_offset + 5))
    reviewed_offsets.update(range(checksum_offset, checksum_offset + 4))
    changed_offsets = {
        offset
        for offset, (source_byte, result_byte) in enumerate(zip(source, result, strict=True))
        if source_byte != result_byte
    }
    if not changed_offsets or not changed_offsets <= reviewed_offsets:
        raise RuntimeError("candidate changed outside reviewed issue-72 sites")

    result_hash = sha256(result)
    if EXPECTED_CANDIDATE_SHA256 and result_hash != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(f"v0.13.1 candidate hash changed: {result_hash}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(result)
    manifest: dict[str, object] = {
        "schema": "nobu16.map-label-status-and-supply-alignment.v5",
        "issue": 72,
        "purpose": (
            "Place battle-ready, defensive-base, attack-objective, and supply "
            "markers after the dynamically sized horizontal castle label."
        ),
        "input": {"path": str(source_path), "size": len(source), "sha256": source_hash},
        "output": {"path": str(output_path), "size": len(result), "sha256": result_hash},
        "alignment": {
            "axis": "x-and-y",
            "fixed_offset": None,
            "width_source": "label object +0x140 widget +0x10 rendered width",
            "status_widget": "label object +0x248",
            "status_native_base_x": 30.0,
            "status_y_formula": (
                "plate Y + (plate height - status height) / 2"
            ),
            "paired_pool_categories": [[1, 2], [3, 4]],
            "pool_header_base_virtual_address": f"0x{POOL_HEADER_BASE_VA:X}",
            "pool_stride": f"0x{POOL_STRIDE:X}",
            "key_match": "record key type 2 and exact key pointer",
            "excluded": ["castle/crest icon pool", "special map cursor"],
        },
        "hook": {
            "call_site_virtual_address": f"0x{STATUS_UPDATE_CALL_SITE:X}",
            "original_target_virtual_address": f"0x{STATUS_UPDATE_VA:X}",
            "before": before.hex(" ").upper(),
            "after": after.hex(" ").upper(),
            "wrapper_virtual_address": f"0x{wrapper_va:X}",
        },
        "injected_code": {
            "section": CODE_SECTION,
            "virtual_address": f"0x{code_va:X}",
            "file_offset": f"0x{code_file_offset:X}",
            "size": len(injected),
            "padding": code_padding,
            "new_section_virtual_size": new_virtual_size,
            "new_section_characteristics": f"0x{new_characteristics:08X}",
        },
        "changed_byte_count": len(changed_offsets),
        "resource_archives_changed": False,
        "runtime_restart_required": True,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output, args.manifest), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
