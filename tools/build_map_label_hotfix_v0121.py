#!/usr/bin/env python3
"""Build the v0.12.1 dual-resolution map-label EXE candidate.

The v0.12.0 candidate embeds only the normal-resolution horizontal map-label
atlas.  At 4K the game asks the same loader call sites for group 0x17ED, but
the original loader returns a different 4096-wide PORT atlas.  Returning the
normal-resolution replacement on that branch corrupts every rectangle lookup.

This builder keeps the reviewed v0.12.0 normal-resolution atlas, constructs a
matching high-resolution atlas from the JP/EN PORT resources, and replaces the
three scoped wrappers so they select the replacement matching the size returned
by the original loader.  No resource archive is changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import nobu16_lz4 as lz4


EXPECTED_V0120_SHA256 = (
    "5D5B1F0B9CDE3A651DFA84E19FD5C7F2C6DF06D6D25C3674C049F7F049D26BF7"
)
EXPECTED_JP_PORT2_SHA256 = (
    "09531F21FA3BD56E2554C47942E47B5ACB61A7F279EFBF4AF85E4CAB963E4FAA"
)
EXPECTED_EN_PORT2_SHA256 = (
    "C6F012B7482AB4BF7D2266170649199C29A5E0FB6AF13D3D060DA34FA8CCEC57"
)
EXPECTED_HIGH_OUTER_SHA256 = (
    "04588145445136874AA9ABBCE47196179B085DAEA79231DA84710E8870AEF485"
)
EXPECTED_HIGH_RAW_G1T_SHA256 = (
    "BC6564B5F966C85ABE91F43292AD5F9F470EC8F6A001FF0AEE5F8C15A01B7AD7"
)
EXPECTED_CANDIDATE_SHA256 = (
    "7F5B28B5435AE8F808301E5D86F7CDE8481270856425B0BB3170BD4FFFE5674B"
)

EXPECTED_RECT_WRAPPER_SHA256 = (
    "A2CF28EE90077D4B9B3F25B7595D69DB16392A815B1CC6DBC00B510B0DFAD90E"
)
EXPECTED_OUTER_PROVIDER_SHA256 = (
    "6B34FFFC2F906E00B990937C340383D8FF4216BBC9C8A11F75B1FC810382E4EB"
)
EXPECTED_NESTED_PROVIDER_SHA256 = (
    "A2E53036AF9470B3EA18A067A3D95A9A30E8599AF4D664F5D580FAD6CCDED8F0"
)

IMAGE_BASE = 0x140000000
GROUP_KEY = 0x17ED
LOGICAL_BASE = 0x123C8
PORT_OUTER_INDEX = 2

LOADER_CALL_VA = 0x140963387
ORIGINAL_ARCHIVE_LOOKUP_VA = 0x1408A6A10
NESTED_LOADER_CALL_VA = 0x1409633B8
ORIGINAL_NESTED_LOOKUP_VA = 0x1408A7460
RECT_HOOK_VA = 0x140967FAD

CODE_SECTION = ".mlbx"
DATA_SECTION = ".mlbd"
CODE_SECTION_VA = 0x14261A000
LOW_OUTER_VA = 0x14261B180
LOW_OUTER_SIZE = 0xE83E6
LOW_RAW_G1T_VA = 0x142703570
LOW_RAW_G1T_SIZE = 0x600054
LOW_SOURCE_OUTER_SIZE = 0x8D9A6
LOW_SOURCE_RAW_G1T_SIZE = 0x300054
HIGH_SOURCE_OUTER_SIZE = 0x1B842C
HIGH_SOURCE_RAW_G1T_SIZE = 0xC00054

RECT_WRAPPER_OFFSET = 0x00
WIDTH_STUB_OFFSET = 0x86
WIDTH_STUB_SIZE = 38
OUTER_PROVIDER_OFFSET = 0xB0
NESTED_PROVIDER_OFFSET = 0x140

TARGET_GROUPS = (
    0x124CB,
    0x124CE,
    0x124E2,
    0x12507,
    0x12675,
    0x12678,
    0x1267E,
    0x1268D,
)
TARGET_IDS = tuple(base + delta for base in TARGET_GROUPS for delta in range(3))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def rel32(source_next_va: int, target_va: int) -> bytes:
    displacement = target_va - source_next_va
    if not -(1 << 31) <= displacement < (1 << 31):
        raise RuntimeError("rel32 target out of range")
    return struct.pack("<i", displacement)


def parse_pe(data: bytes) -> dict[str, object]:
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise RuntimeError("input is not a PE image")
    coff = pe_offset + 4
    machine, count, _ts, _sym, _nsym, optional_size, _chars = struct.unpack_from(
        "<HHIIIHH", data, coff
    )
    optional = coff + 20
    if machine != 0x8664 or struct.unpack_from("<H", data, optional)[0] != 0x20B:
        raise RuntimeError("input is not PE32+ x64")
    section_alignment, file_alignment = struct.unpack_from("<II", data, optional + 0x20)
    image_base = struct.unpack_from("<Q", data, optional + 0x18)[0]
    size_image = struct.unpack_from("<I", data, optional + 0x38)[0]
    table = optional + optional_size
    sections: list[dict[str, int | str]] = []
    for index in range(count):
        header = table + index * 40
        name = data[header : header + 8].split(b"\0", 1)[0].decode("ascii")
        virtual_size, rva, raw_size, raw_pointer, _pr, _pl, _nr, _nl, chars = (
            struct.unpack_from("<IIIIIIHHI", data, header + 8)
        )
        sections.append(
            {
                "index": index,
                "header_offset": header,
                "name": name,
                "virtual_size": virtual_size,
                "rva": rva,
                "raw_size": raw_size,
                "raw_pointer": raw_pointer,
                "characteristics": chars,
            }
        )
    return {
        "pe": pe_offset,
        "coff": coff,
        "optional": optional,
        "section_count": count,
        "section_alignment": section_alignment,
        "file_alignment": file_alignment,
        "image_base": image_base,
        "size_image": size_image,
        "sections": sections,
    }


def section(pe: dict[str, object], name: str) -> dict[str, int | str]:
    matches = [entry for entry in pe["sections"] if entry["name"] == name]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {name} section")
    return matches[0]


def va_to_file(data: bytes, pe: dict[str, object], va: int) -> int:
    rva = va - int(pe["image_base"])
    for entry in pe["sections"]:
        start = int(entry["rva"])
        extent = max(int(entry["virtual_size"]), int(entry["raw_size"]))
        if start <= rva < start + extent:
            return int(entry["raw_pointer"]) + rva - start
    raise RuntimeError(f"VA is not file-backed: 0x{va:X}")


def top_outer(blob: bytes, index: int) -> tuple[bytes, int, int]:
    if blob[:4] != b"LINK" or struct.unpack_from("<I", blob, 4)[0] <= index:
        raise RuntimeError("unexpected top-level language archive")
    offset, size = struct.unpack_from("<II", blob, 0x10 + index * 8)
    if offset + size > len(blob):
        raise RuntimeError("outer entry exceeds archive")
    return blob[offset : offset + size], offset, size


def parse_outer(outer: bytes) -> dict[str, object]:
    if outer[:4] != b"LINK" or struct.unpack_from("<I", outer, 4)[0] != 1:
        raise RuntimeError("map-label outer is not a one-slot LINK")
    if struct.unpack_from("<I", outer, 8)[0] != 0x20:
        raise RuntimeError("map-label outer table offset changed")
    record_count = struct.unpack_from("<I", outer, 0xC)[0]
    slot_offset, slot_size = struct.unpack_from("<II", outer, 0x20)
    if record_count != 0x366 or slot_offset != 0x2920:
        raise RuntimeError("map-label metadata layout changed")
    if slot_offset + slot_size != len(outer):
        raise RuntimeError("map-label slot is not the exact outer tail")
    wrapper = outer[slot_offset : slot_offset + slot_size]
    header, raw = lz4.decompress_wrapper(wrapper)
    if raw[:4] != b"GT1G":
        raise RuntimeError("map-label slot is not a G1T")
    file_size, directory_offset, texture_count, platform = struct.unpack_from(
        "<4I", raw, 8
    )
    if file_size != len(raw):
        raise RuntimeError("G1T file size field changed")
    offsets = struct.unpack_from("<" + "I" * texture_count, raw, directory_offset)
    return {
        "record_count": record_count,
        "slot_offset": slot_offset,
        "slot_size": slot_size,
        "wrapper_header": header,
        "raw": raw,
        "directory_offset": directory_offset,
        "texture_count": texture_count,
        "platform": platform,
        "texture_offsets": offsets,
    }


def record_at(outer: bytes, logical_id: int) -> tuple[int, int, int, int, int, int]:
    if not LOGICAL_BASE <= logical_id < LOGICAL_BASE + 0x366:
        raise RuntimeError(f"logical ID outside group: 0x{logical_id:X}")
    return struct.unpack_from("<6H", outer, 0x40 + (logical_id - LOGICAL_BASE) * 12)


def build_high_outer(
    jp_outer: bytes, en_outer: bytes
) -> tuple[bytes, bytes, list[dict[str, object]]]:
    jp = parse_outer(jp_outer)
    en = parse_outer(en_outer)
    for label, parsed in (("JP", jp), ("EN", en)):
        if parsed["texture_count"] != 2 or parsed["directory_offset"] != 0x24:
            raise RuntimeError(f"unexpected {label} high-resolution texture directory")
        if tuple(parsed["texture_offsets"]) != (0x8, 0x80001C):
            raise RuntimeError(f"unexpected {label} high-resolution texture offsets")
        if len(parsed["raw"]) != HIGH_SOURCE_RAW_G1T_SIZE:
            raise RuntimeError(f"unexpected {label} high-resolution G1T size")

    jraw = bytes(jp["raw"])
    eraw = bytes(en["raw"])
    if jraw[0x800042] != 0xAC or eraw[0x2E] != 0xBC:
        raise RuntimeError("high-resolution source texture dimensions changed")

    # JP texture 0 is 4096x2048 and texture 1 is 4096x1024.  Preserve both,
    # extend texture 1 to 4096x4096, then place the EN 4096x2048 texture-0
    # rows below the original JP texture-1 rows.  The final 1024 rows stay zero.
    new_raw = bytearray(jraw)
    new_raw[0x800042] = 0xCC
    new_raw += eraw[0x40:0x800040]
    new_raw += bytes(0x400000)
    if len(new_raw) != 0x1800054:
        raise RuntimeError(f"unexpected composite high-resolution G1T size: 0x{len(new_raw):X}")
    struct.pack_into("<I", new_raw, 8, len(new_raw))

    wrapped = lz4.recompress_wrapper_greedy(bytes(new_raw), jp["wrapper_header"])
    _header, roundtrip = lz4.decompress_wrapper(wrapped)
    if roundtrip != bytes(new_raw):
        raise RuntimeError("high-resolution G1T wrapper roundtrip failed")

    custom = bytearray(jp_outer[: int(jp["slot_offset"])])
    rows: list[dict[str, object]] = []
    for logical_id in TARGET_IDS:
        x, y, width, height, texture, reserved = record_at(en_outer, logical_id)
        if texture != 0 or reserved != 0:
            raise RuntimeError(f"high-resolution EN record contract changed: 0x{logical_id:X}")
        runtime_y = y + 1024
        if runtime_y + height > 3072:
            raise RuntimeError(f"high-resolution imported row exceeds stacked payload: 0x{logical_id:X}")
        runtime = (x, runtime_y, width, height, 1, 0)
        offset = 0x40 + (logical_id - LOGICAL_BASE) * 12
        struct.pack_into("<6H", custom, offset, *runtime)
        rows.append(
            {
                "id": f"0x{logical_id:X}",
                "source": [x, y, width, height, texture, reserved],
                "runtime": list(runtime),
            }
        )
    struct.pack_into("<I", custom, 0x24, len(wrapped))
    custom += wrapped
    custom_bytes = bytes(custom)
    new_raw_bytes = bytes(new_raw)
    if sha256(custom_bytes) != EXPECTED_HIGH_OUTER_SHA256:
        raise RuntimeError("composite high-resolution outer hash changed")
    if sha256(new_raw_bytes) != EXPECTED_HIGH_RAW_G1T_SHA256:
        raise RuntimeError("composite high-resolution raw G1T hash changed")
    return custom_bytes, new_raw_bytes, rows


class CodeBuilder:
    def __init__(self, va: int) -> None:
        self.va = va
        self.code = bytearray()
        self.labels: dict[str, int] = {}
        self.rel8: list[tuple[int, str]] = []

    def emit(self, data: bytes | bytearray) -> None:
        self.code += data

    def label(self, name: str) -> None:
        if name in self.labels:
            raise RuntimeError(f"duplicate code label: {name}")
        self.labels[name] = len(self.code)

    def branch8(self, opcode: int, label: str) -> None:
        self.code += bytes((opcode, 0))
        self.rel8.append((len(self.code) - 1, label))

    def call(self, target_va: int) -> None:
        self.code += b"\xE8" + rel32(self.va + len(self.code) + 5, target_va)

    def jump(self, target_va: int) -> None:
        self.code += b"\xE9" + rel32(self.va + len(self.code) + 5, target_va)

    def lea_rax(self, target_va: int) -> None:
        self.code += bytes.fromhex("48 8D 05") + rel32(
            self.va + len(self.code) + 7, target_va
        )

    def finish(self) -> bytes:
        for at, label in self.rel8:
            if label not in self.labels:
                raise RuntimeError(f"missing code label: {label}")
            displacement = self.labels[label] - (at + 1)
            if not -128 <= displacement <= 127:
                raise RuntimeError(f"short branch to {label} is out of range")
            self.code[at] = displacement & 0xFF
        return bytes(self.code)


def build_outer_provider(
    provider_va: int,
    low_va: int,
    low_size: int,
    high_va: int,
    high_size: int,
    resolution_flag_va: int,
) -> bytes:
    c = CodeBuilder(provider_va)
    c.emit(bytes.fromhex("81 FA ED 17 00 00"))
    c.branch8(0x74, "custom")
    c.jump(ORIGINAL_ARCHIVE_LOOKUP_VA)
    c.label("custom")
    c.emit(bytes.fromhex("48 83 EC 38"))
    c.emit(bytes.fromhex("4C 89 44 24 20 4C 89 4C 24 28"))
    c.call(ORIGINAL_ARCHIVE_LOOKUP_VA)
    c.emit(bytes.fromhex("4C 8B 54 24 20 4C 8B 5C 24 28"))
    c.emit(bytes.fromhex("41 81 3B") + struct.pack("<I", HIGH_SOURCE_OUTER_SIZE))
    c.branch8(0x74, "high")
    c.emit(bytes.fromhex("41 81 3B") + struct.pack("<I", LOW_SOURCE_OUTER_SIZE))
    c.branch8(0x75, "done")
    c.lea_rax(low_va)
    c.emit(bytes.fromhex("49 89 02 41 C7 03") + struct.pack("<I", low_size))
    c.emit(bytes.fromhex("C6 05") + rel32(
        provider_va + len(c.code) + 7, resolution_flag_va
    ) + b"\x00")
    c.emit(bytes.fromhex("31 C0"))
    c.branch8(0xEB, "done")
    c.label("high")
    c.lea_rax(high_va)
    c.emit(bytes.fromhex("49 89 02 41 C7 03") + struct.pack("<I", high_size))
    c.emit(bytes.fromhex("C6 05") + rel32(
        provider_va + len(c.code) + 7, resolution_flag_va
    ) + b"\x01")
    c.emit(bytes.fromhex("31 C0"))
    c.label("done")
    c.emit(bytes.fromhex("48 83 C4 38 C3"))
    return c.finish()


def build_nested_provider(
    provider_va: int,
    low_va: int,
    low_size: int,
    high_va: int,
    high_size: int,
    resolution_flag_va: int,
) -> bytes:
    c = CodeBuilder(provider_va)
    c.emit(bytes.fromhex("81 FA ED 17 00 00"))
    c.branch8(0x74, "custom")
    c.jump(ORIGINAL_NESTED_LOOKUP_VA)
    c.label("custom")
    c.emit(bytes.fromhex("4C 8B 54 24 28 4C 8B 5C 24 30"))
    c.emit(bytes.fromhex("48 83 EC 58"))
    c.emit(bytes.fromhex("4C 89 54 24 20 4C 89 5C 24 28"))
    c.emit(bytes.fromhex("4C 89 54 24 30 4C 89 5C 24 38"))
    c.call(ORIGINAL_NESTED_LOOKUP_VA)
    c.emit(bytes.fromhex("4C 8B 54 24 30 4C 8B 5C 24 38"))
    c.emit(bytes.fromhex("41 81 3B") + struct.pack("<I", HIGH_SOURCE_RAW_G1T_SIZE))
    c.branch8(0x74, "high")
    c.emit(bytes.fromhex("41 81 3B") + struct.pack("<I", LOW_SOURCE_RAW_G1T_SIZE))
    c.branch8(0x75, "done")
    c.lea_rax(low_va)
    c.emit(bytes.fromhex("49 89 02 41 C7 03") + struct.pack("<I", low_size))
    c.emit(bytes.fromhex("C6 05") + rel32(
        provider_va + len(c.code) + 7, resolution_flag_va
    ) + b"\x00")
    c.emit(bytes.fromhex("B8 01 00 00 00"))
    c.branch8(0xEB, "done")
    c.label("high")
    c.lea_rax(high_va)
    c.emit(bytes.fromhex("49 89 02 41 C7 03") + struct.pack("<I", high_size))
    c.emit(bytes.fromhex("C6 05") + rel32(
        provider_va + len(c.code) + 7, resolution_flag_va
    ) + b"\x01")
    c.emit(bytes.fromhex("B8 01 00 00 00"))
    c.label("done")
    c.emit(bytes.fromhex("48 83 C4 58 C3"))
    return c.finish()


def build_rect_wrapper(
    wrapper_va: int, table_va: int, resolution_flag_va: int
) -> bytes:
    c = CodeBuilder(wrapper_va)
    c.emit(bytes.fromhex("81 3B ED 17 00 00"))
    c.branch8(0x75, "replay")
    c.emit(bytes.fromhex("4C 8D 15") + rel32(wrapper_va + len(c.code) + 7, table_va))
    c.emit(bytes.fromhex("B9 18 00 00 00"))
    c.label("loop")
    c.emit(bytes.fromhex("41 3B 2A"))
    c.branch8(0x74, "found")
    c.emit(bytes.fromhex("49 83 C2 1C FF C9"))
    c.branch8(0x75, "loop")
    c.branch8(0xEB, "replay")
    c.label("found")
    c.emit(bytes.fromhex("48 8B 43 70 4A 8B 14 F0"))
    c.emit(bytes.fromhex("49 8D 42 04"))
    c.emit(bytes.fromhex("80 3D") + rel32(
        wrapper_va + len(c.code) + 7, resolution_flag_va
    ) + b"\x00")
    c.branch8(0x74, "copy")
    c.emit(bytes.fromhex("48 83 C0 0C"))
    c.label("copy")
    c.emit(bytes.fromhex("4C 8B 18 4C 89 1A"))
    c.emit(bytes.fromhex("8B 40 08 89 42 08"))
    c.label("replay")
    c.emit(bytes.fromhex("48 8B 43 70 4A 8D 14 F5 00 00 00 00 C3"))
    return c.finish()


def build_combined_rect_table(low_outer: bytes, high_outer: bytes) -> bytes:
    table = bytearray()
    for logical_id in TARGET_IDS:
        low = record_at(low_outer, logical_id)
        high = record_at(high_outer, logical_id)
        if low[4:] != (1, 0) or high[4:] != (1, 0):
            raise RuntimeError(f"replacement record is not texture 1: 0x{logical_id:X}")
        table += struct.pack("<I6H6H", logical_id, *low, *high)
    if len(table) != len(TARGET_IDS) * 28:
        raise RuntimeError("combined rectangle table size changed")
    return bytes(table)


def changed_runs(before: bytes, after: bytes) -> list[tuple[int, int]]:
    changed = [index for index, (old, new) in enumerate(zip(before, after)) if old != new]
    if len(after) > len(before):
        changed.extend(range(len(before), len(after)))
    if not changed:
        return []
    runs: list[tuple[int, int]] = []
    start = previous = changed[0]
    for index in changed[1:]:
        if index != previous + 1:
            runs.append((start, previous + 1))
            start = index
        previous = index
    runs.append((start, previous + 1))
    return runs


def build(
    v0120_path: Path,
    jp_port2_path: Path,
    en_port2_path: Path,
    output_path: Path,
    manifest_path: Path,
) -> dict[str, object]:
    source = v0120_path.read_bytes()
    jp_blob = jp_port2_path.read_bytes()
    en_blob = en_port2_path.read_bytes()
    gates = {
        "v0.12.0 candidate": (sha256(source), EXPECTED_V0120_SHA256),
        "JP PORT2": (sha256(jp_blob), EXPECTED_JP_PORT2_SHA256),
        "EN PORT2": (sha256(en_blob), EXPECTED_EN_PORT2_SHA256),
    }
    for label, (actual, expected) in gates.items():
        if actual != expected:
            raise RuntimeError(f"{label} hash gate failed: {actual}")

    pe = parse_pe(source)
    if pe["image_base"] != IMAGE_BASE or pe["section_count"] != 9:
        raise RuntimeError("unexpected v0.12.0 PE layout")
    code_section = section(pe, CODE_SECTION)
    data_section = section(pe, DATA_SECTION)
    if int(code_section["raw_size"]) != 0x200:
        raise RuntimeError("unexpected .mlbx raw size")
    if int(data_section["raw_pointer"]) + int(data_section["raw_size"]) != len(source):
        raise RuntimeError(".mlbd is not the final file-backed section")

    jp_outer, jp_outer_offset, jp_outer_size = top_outer(jp_blob, PORT_OUTER_INDEX)
    en_outer, en_outer_offset, en_outer_size = top_outer(en_blob, PORT_OUTER_INDEX)
    if jp_outer_size != HIGH_SOURCE_OUTER_SIZE:
        raise RuntimeError(f"unexpected JP high-resolution outer size: 0x{jp_outer_size:X}")
    high_outer, high_raw, high_rows = build_high_outer(jp_outer, en_outer)

    low_outer_offset = va_to_file(source, pe, LOW_OUTER_VA)
    low_outer = source[low_outer_offset : low_outer_offset + LOW_OUTER_SIZE]
    low_parsed = parse_outer(low_outer)
    if len(low_parsed["raw"]) != LOW_RAW_G1T_SIZE:
        raise RuntimeError("embedded normal-resolution G1T contract changed")
    combined_table = build_combined_rect_table(low_outer, high_outer)

    old_data_raw_size = int(data_section["raw_size"])
    data_va = IMAGE_BASE + int(data_section["rva"])
    resolution_flag_offset = old_data_raw_size
    table_offset = align(resolution_flag_offset + 1, 0x10)
    high_outer_offset = align(table_offset + len(combined_table), 0x10)
    high_raw_offset = align(high_outer_offset + len(high_outer), 0x10)
    extension = bytearray(high_raw_offset - old_data_raw_size)
    relative_table = table_offset - old_data_raw_size
    extension[relative_table : relative_table + len(combined_table)] = combined_table
    relative_high_outer = high_outer_offset - old_data_raw_size
    extension[relative_high_outer : relative_high_outer + len(high_outer)] = high_outer
    relative_high_raw = high_raw_offset - old_data_raw_size
    extension[relative_high_raw : relative_high_raw + len(high_raw)] = high_raw

    table_va = data_va + table_offset
    resolution_flag_va = data_va + resolution_flag_offset
    high_outer_va = data_va + high_outer_offset
    high_raw_va = data_va + high_raw_offset
    rect_va = CODE_SECTION_VA + RECT_WRAPPER_OFFSET
    outer_va = CODE_SECTION_VA + OUTER_PROVIDER_OFFSET
    nested_va = CODE_SECTION_VA + NESTED_PROVIDER_OFFSET
    rect_wrapper = build_rect_wrapper(rect_va, table_va, resolution_flag_va)
    outer_provider = build_outer_provider(
        outer_va,
        LOW_OUTER_VA,
        LOW_OUTER_SIZE,
        high_outer_va,
        len(high_outer),
        resolution_flag_va,
    )
    nested_provider = build_nested_provider(
        nested_va,
        LOW_RAW_G1T_VA,
        LOW_RAW_G1T_SIZE,
        high_raw_va,
        len(high_raw),
        resolution_flag_va,
    )

    wrapper_gates = {
        "rectangle wrapper": (sha256(rect_wrapper), EXPECTED_RECT_WRAPPER_SHA256),
        "outer provider": (sha256(outer_provider), EXPECTED_OUTER_PROVIDER_SHA256),
        "nested provider": (sha256(nested_provider), EXPECTED_NESTED_PROVIDER_SHA256),
    }
    for label, (actual, expected) in wrapper_gates.items():
        if actual != expected:
            raise RuntimeError(f"{label} code hash changed: {actual}")

    if len(rect_wrapper) > WIDTH_STUB_OFFSET:
        raise RuntimeError("dual-resolution rectangle wrapper overlaps width stub")
    if OUTER_PROVIDER_OFFSET + len(outer_provider) > NESTED_PROVIDER_OFFSET:
        raise RuntimeError("dual-resolution outer provider overlaps nested provider")
    if NESTED_PROVIDER_OFFSET + len(nested_provider) > int(code_section["raw_size"]):
        raise RuntimeError("dual-resolution wrapper code exceeds .mlbx")

    code_raw = int(code_section["raw_pointer"])
    old_width_stub = source[
        code_raw + WIDTH_STUB_OFFSET : code_raw + WIDTH_STUB_OFFSET + WIDTH_STUB_SIZE
    ]
    if sha256(old_width_stub) != "28BCEA539C8B81A228A42BF5EFD287CC7CB58E4D7E741F04C0A0634CE5CFB35E":
        raise RuntimeError("reviewed Korean dynamic-width stub changed")
    code_payload = bytearray(int(code_section["raw_size"]))
    code_payload[RECT_WRAPPER_OFFSET : RECT_WRAPPER_OFFSET + len(rect_wrapper)] = rect_wrapper
    code_payload[WIDTH_STUB_OFFSET : WIDTH_STUB_OFFSET + WIDTH_STUB_SIZE] = old_width_stub
    code_payload[OUTER_PROVIDER_OFFSET : OUTER_PROVIDER_OFFSET + len(outer_provider)] = outer_provider
    code_payload[NESTED_PROVIDER_OFFSET : NESTED_PROVIDER_OFFSET + len(nested_provider)] = nested_provider

    candidate = bytearray(source)
    candidate[code_raw : code_raw + len(code_payload)] = code_payload
    for call_va, target_va, expected in (
        (LOADER_CALL_VA, outer_va, bytes.fromhex("E8 74 6C CB 01")),
        (NESTED_LOADER_CALL_VA, nested_va, bytes.fromhex("E8 03 6D CB 01")),
    ):
        offset = va_to_file(source, pe, call_va)
        if source[offset : offset + 5] != expected:
            raise RuntimeError(f"reviewed loader call changed at 0x{call_va:X}")
        candidate[offset : offset + 5] = b"\xE8" + rel32(call_va + 5, target_va)
    rect_hook_offset = va_to_file(source, pe, RECT_HOOK_VA)
    expected_rect_hook = bytes.fromhex("E8 8E 20 CB 01 90 90 90 90 90 90 90")
    if source[rect_hook_offset : rect_hook_offset + 12] != expected_rect_hook:
        raise RuntimeError("reviewed rectangle hook changed")
    candidate[rect_hook_offset : rect_hook_offset + 12] = (
        b"\xE8" + rel32(RECT_HOOK_VA + 5, rect_va) + b"\x90" * 7
    )

    padded_extension_size = align(len(extension), int(pe["file_alignment"]))
    candidate += extension
    candidate += bytes(padded_extension_size - len(extension))
    new_data_raw_size = old_data_raw_size + padded_extension_size
    new_data_virtual_size = old_data_raw_size + len(extension)
    struct.pack_into(
        "<I", candidate, int(code_section["header_offset"]) + 8,
        max(
            RECT_WRAPPER_OFFSET + len(rect_wrapper),
            WIDTH_STUB_OFFSET + WIDTH_STUB_SIZE,
            OUTER_PROVIDER_OFFSET + len(outer_provider),
            NESTED_PROVIDER_OFFSET + len(nested_provider),
        ),
    )
    struct.pack_into(
        "<I", candidate, int(data_section["header_offset"]) + 8, new_data_virtual_size
    )
    struct.pack_into(
        "<I", candidate, int(data_section["header_offset"]) + 16, new_data_raw_size
    )
    struct.pack_into(
        "<I",
        candidate,
        int(data_section["header_offset"]) + 36,
        int(data_section["characteristics"]) | 0x80000000,
    )
    new_size_image = align(
        int(data_section["rva"]) + new_data_virtual_size,
        int(pe["section_alignment"]),
    )
    struct.pack_into("<I", candidate, int(pe["optional"]) + 0x38, new_size_image)

    reparsed = parse_pe(candidate)
    new_data = section(reparsed, DATA_SECTION)
    if int(new_data["raw_pointer"]) + int(new_data["raw_size"]) != len(candidate):
        raise RuntimeError("expanded .mlbd does not end at EOF")
    high_outer_file = int(data_section["raw_pointer"]) + high_outer_offset
    high_raw_file = int(data_section["raw_pointer"]) + high_raw_offset
    if bytes(candidate[high_outer_file : high_outer_file + len(high_outer)]) != high_outer:
        raise RuntimeError("embedded high-resolution outer differs")
    if bytes(candidate[high_raw_file : high_raw_file + len(high_raw)]) != high_raw:
        raise RuntimeError("embedded high-resolution raw G1T differs")

    candidate_sha256 = sha256(candidate)
    if candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(f"dual-resolution candidate hash changed: {candidate_sha256}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(candidate)
    manifest = {
        "schema": "nobu16.map-labels-horizontal.v24-dual-resolution",
        "purpose": (
            "Preserve the reviewed normal-resolution Korean horizontal map-label "
            "atlas and add the matching 4096-wide PORT atlas for 4K rendering."
        ),
        "input": {
            "v0.12.0_candidate": {
                "path": str(v0120_path),
                "size": len(source),
                "sha256": sha256(source),
            },
            "jp_port2": {
                "path": str(jp_port2_path),
                "size": len(jp_blob),
                "sha256": sha256(jp_blob),
                "outer_index": PORT_OUTER_INDEX,
                "outer_offset": f"0x{jp_outer_offset:X}",
                "outer_size": f"0x{jp_outer_size:X}",
            },
            "en_port2": {
                "path": str(en_port2_path),
                "size": len(en_blob),
                "sha256": sha256(en_blob),
                "outer_index": PORT_OUTER_INDEX,
                "outer_offset": f"0x{en_outer_offset:X}",
                "outer_size": f"0x{en_outer_size:X}",
            },
        },
        "output": {
            "path": str(output_path),
            "size": len(candidate),
            "sha256": candidate_sha256,
        },
        "assets": {
            "normal": {
                "outer_va": f"0x{LOW_OUTER_VA:X}",
                "outer_size": f"0x{LOW_OUTER_SIZE:X}",
                "raw_g1t_va": f"0x{LOW_RAW_G1T_VA:X}",
                "raw_g1t_size": f"0x{LOW_RAW_G1T_SIZE:X}",
            },
            "high": {
                "outer_va": f"0x{high_outer_va:X}",
                "outer_size": f"0x{len(high_outer):X}",
                "outer_sha256": sha256(high_outer),
                "raw_g1t_va": f"0x{high_raw_va:X}",
                "raw_g1t_size": f"0x{len(high_raw):X}",
                "raw_g1t_sha256": sha256(high_raw),
                "texture_dimensions": ["4096x2048", "4096x4096"],
            },
            "combined_rect_table_va": f"0x{table_va:X}",
            "combined_rect_table_size": f"0x{len(combined_table):X}",
            "resolution_flag_va": f"0x{resolution_flag_va:X}",
            "rows": high_rows,
        },
        "dispatch": {
            "outer_original_sizes": {
                "normal": f"0x{LOW_SOURCE_OUTER_SIZE:X}",
                "high": f"0x{HIGH_SOURCE_OUTER_SIZE:X}",
            },
            "nested_original_raw_sizes": {
                "normal": f"0x{LOW_SOURCE_RAW_G1T_SIZE:X}",
                "high": f"0x{HIGH_SOURCE_RAW_G1T_SIZE:X}",
            },
            "unknown_contract_falls_back_to_original": True,
            "rect_resolution_signal": (
                "0x17ED loader-owned byte flag: 0=normal, 1=high"
            ),
        },
        "wrappers": {
            "rect": {"va": f"0x{rect_va:X}", "size": len(rect_wrapper)},
            "outer": {"va": f"0x{outer_va:X}", "size": len(outer_provider)},
            "nested": {"va": f"0x{nested_va:X}", "size": len(nested_provider)},
            "dynamic_width_stub_preserved": f"0x{CODE_SECTION_VA + WIDTH_STUB_OFFSET:X}",
        },
        "pe": {
            "section_count": pe["section_count"],
            "mlbx_virtual_size": section(reparsed, CODE_SECTION)["virtual_size"],
            "mlbd_virtual_size": new_data_virtual_size,
            "mlbd_raw_size": new_data_raw_size,
            "size_of_image": new_size_image,
            "changed_runs": [
                {"start": f"0x{start:X}", "end": f"0x{end:X}"}
                for start, end in changed_runs(source, bytes(candidate))
            ],
        },
        "runtime_restart_required": True,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v0120", required=True, type=Path)
    parser.add_argument("--jp-port2", required=True, type=Path)
    parser.add_argument("--en-port2", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    result = build(
        args.v0120, args.jp_port2, args.en_port2, args.output, args.manifest
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
