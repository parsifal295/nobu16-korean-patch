#!/usr/bin/env python3
"""Rebuild the v0.90 vertical executable with a loader-valid final section.

The v0.90.0 vertical recipe placed ``.mlbd`` at RVA 0x261B000 while the
preceding ``.reloc`` section ended at 0x261A000.  Windows rejects that image
with ERROR_BAD_EXE_FORMAT (193).  This builder moves ``.mlbd`` to the adjacent
RVA, fixes every affected relative branch, clears the stale certificate
directory, and recalculates the PE checksum.

Only hashes, offsets, and generated patch evidence are stored in the
repository.  The caller supplies the private executable and append payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


EXPECTED_SOURCE_SIZE = 31_747_848
EXPECTED_SOURCE_SHA256 = (
    "DD7DEBDA1C093D12CDE3C3DD85244DA3350C47120D8C4EDAC7195D83C384A344"
)
EXPECTED_OLD_PAYLOAD_SIZE = 760
EXPECTED_OLD_PAYLOAD_SHA256 = (
    "EC35CA776AC332DC0B0CBAEC5DB8E73C7E53BACEB9AF82E2559BE5EC0CCCF44F"
)

IMAGE_BASE = 0x140000000
EXPECTED_ENTRY_RVA = 0x12FE4D0
EXPECTED_SECTION_COUNT = 7
EXPECTED_SIZE_OF_IMAGE = 0x261A000
NEW_SECTION_RVA = 0x261A000
NEW_SECTION_NAME = b".mlbd\0\0\0"
NEW_SECTION_CHARACTERISTICS = 0x60000020

HOOK_FILE_OFFSET = 9_908_758
HOOK_RVA = 0x973E16
HOOK_BEFORE = bytes.fromhex("488BF9488B0D986E8101488B01")
HOOK_AFTER = bytes.fromhex("E9E561CA019090909090909090")

CONTROLLER_HOOK_FILE_OFFSET = 5_703_744
CONTROLLER_HOOK_BEFORE = bytes.fromhex("48895C2410")
CONTROLLER_HOOK_AFTER = bytes.fromhex("E9A28D0A02")
CONTROLLER_STUB_OFFSET_IN_SECTION = 0x1E7
CONTROLLER_STUB = bytes.fromhex(
    "C7056B35B6FF0100000048895C2410E94A72F5FD"
)

PAYLOAD_CODE_OFFSET = 0xF8
PAYLOAD_RIP_DISP_OFFSET = PAYLOAD_CODE_OFFSET + 0x1DB
PAYLOAD_RETURN_DISP_OFFSET = PAYLOAD_CODE_OFFSET + 0x1E3
OLD_RIP_DISP = bytes.fromhex("D9FAB6FF")
NEW_RIP_DISP = bytes.fromhex("D90AB7FF")
OLD_RETURN_DISP = bytes.fromhex("3C8C35FE")
NEW_RETURN_DISP = bytes.fromhex("3C9C35FE")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def read_u16(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_u32(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def parse_pe(data: bytes | bytearray) -> dict[str, Any]:
    if data[:2] != b"MZ":
        raise RuntimeError("missing DOS signature")
    pe_offset = read_u32(data, 0x3C)
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise RuntimeError("missing PE signature")
    optional = pe_offset + 24
    if read_u16(data, optional) != 0x20B:
        raise RuntimeError("expected PE32+ optional header")
    optional_size = read_u16(data, pe_offset + 20)
    section_table = optional + optional_size
    section_count = read_u16(data, pe_offset + 6)
    sections = []
    for index in range(section_count):
        offset = section_table + index * 40
        name = data[offset : offset + 8].rstrip(b"\0").decode("ascii")
        virtual_size, rva, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", data, offset + 8
        )
        sections.append(
            {
                "index": index,
                "offset": offset,
                "name": name,
                "virtual_size": virtual_size,
                "rva": rva,
                "raw_size": raw_size,
                "raw_pointer": raw_pointer,
                "characteristics": read_u32(data, offset + 36),
            }
        )
    return {
        "pe_offset": pe_offset,
        "optional": optional,
        "section_table": section_table,
        "section_count": section_count,
        "section_alignment": read_u32(data, optional + 0x20),
        "file_alignment": read_u32(data, optional + 0x24),
        "size_of_code": read_u32(data, optional + 4),
        "size_of_image": read_u32(data, optional + 0x38),
        "size_of_headers": read_u32(data, optional + 0x3C),
        "entry_rva": read_u32(data, optional + 0x10),
        "checksum_offset": optional + 0x40,
        "certificate_directory_offset": optional + 0x70 + 4 * 8,
        "sections": sections,
    }


def set_pe_checksum(data: bytearray, checksum_offset: int) -> int:
    data[checksum_offset : checksum_offset + 4] = b"\0" * 4
    total = 0
    for offset in range(0, len(data), 2):
        word = data[offset]
        if offset + 1 < len(data):
            word |= data[offset + 1] << 8
        total += word
        total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    checksum = (total + len(data)) & 0xFFFFFFFF
    struct.pack_into("<I", data, checksum_offset, checksum)
    return checksum


def replace_exact(data: bytearray, offset: int, before: bytes, after: bytes) -> None:
    if len(before) != len(after):
        raise RuntimeError("replacement length mismatch")
    observed = bytes(data[offset : offset + len(before)])
    if observed != before:
        raise RuntimeError(
            f"preimage mismatch at 0x{offset:X}: {observed.hex().upper()} / "
            f"{before.hex().upper()}"
        )
    data[offset : offset + len(after)] = after


def patch_payload(old_payload: bytes) -> bytes:
    if len(old_payload) != EXPECTED_OLD_PAYLOAD_SIZE:
        raise RuntimeError("old payload size mismatch")
    if sha256(old_payload) != EXPECTED_OLD_PAYLOAD_SHA256:
        raise RuntimeError("old payload SHA-256 mismatch")
    payload = bytearray(old_payload)
    replace_exact(payload, PAYLOAD_RIP_DISP_OFFSET, OLD_RIP_DISP, NEW_RIP_DISP)
    replace_exact(
        payload,
        PAYLOAD_RETURN_DISP_OFFSET,
        OLD_RETURN_DISP,
        NEW_RETURN_DISP,
    )
    return bytes(payload)


def validate_adjacency(pe: dict[str, Any]) -> None:
    sections = pe["sections"]
    for previous, current in zip(sections, sections[1:]):
        previous_end = align(
            previous["rva"] + previous["virtual_size"],
            pe["section_alignment"],
        )
        if current["rva"] != previous_end:
            raise RuntimeError(
                f"non-adjacent sections: {previous['name']} ends at "
                f"0x{previous_end:X}, {current['name']} starts at "
                f"0x{current['rva']:X}"
            )


def build(
    source_path: Path,
    old_payload_path: Path,
    output_path: Path,
    payload_path: Path,
    manifest_path: Path,
    controller: bool,
) -> dict[str, Any]:
    source = source_path.read_bytes()
    if len(source) != EXPECTED_SOURCE_SIZE or sha256(source) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("vertical pre-012 source profile mismatch")

    pe = parse_pe(source)
    if pe["section_count"] != EXPECTED_SECTION_COUNT:
        raise RuntimeError("unexpected source section count")
    if pe["size_of_image"] != EXPECTED_SIZE_OF_IMAGE:
        raise RuntimeError("unexpected source SizeOfImage")
    if pe["entry_rva"] != EXPECTED_ENTRY_RVA:
        raise RuntimeError("unexpected source entry point")
    if pe["sections"][-1]["name"] != ".reloc":
        raise RuntimeError("expected .reloc as the final source section")

    reloc = pe["sections"][-1]
    reloc_end = align(
        reloc["rva"] + reloc["virtual_size"],
        pe["section_alignment"],
    )
    if reloc_end != NEW_SECTION_RVA:
        raise RuntimeError("new .mlbd section would not be adjacent to .reloc")

    section_header_offset = pe["section_table"] + pe["section_count"] * 40
    if section_header_offset + 40 > pe["size_of_headers"]:
        raise RuntimeError("no room for the .mlbd section header")
    if source[section_header_offset : section_header_offset + 40] != b"\0" * 40:
        raise RuntimeError(".mlbd section-header slot is not empty")

    payload = bytearray(patch_payload(old_payload_path.read_bytes()))
    raw_pointer = align(len(source), pe["file_alignment"])
    if raw_pointer - len(source) != PAYLOAD_CODE_OFFSET:
        raise RuntimeError("unexpected payload alignment padding")
    raw_size = pe["file_alignment"]
    if len(payload) != raw_pointer - len(source) + raw_size:
        raise RuntimeError("payload does not fill one aligned raw section")

    candidate = bytearray(source)
    candidate.extend(payload)

    struct.pack_into("<H", candidate, pe["pe_offset"] + 6, pe["section_count"] + 1)
    struct.pack_into(
        "<I",
        candidate,
        pe["optional"] + 4,
        pe["size_of_code"] + raw_size,
    )
    virtual_size = 0x200 if controller else 0x1E7
    new_size_of_image = align(
        NEW_SECTION_RVA + virtual_size,
        pe["section_alignment"],
    )
    struct.pack_into("<I", candidate, pe["optional"] + 0x38, new_size_of_image)

    section_header = struct.pack(
        "<8sIIIIIIHHI",
        NEW_SECTION_NAME,
        virtual_size,
        NEW_SECTION_RVA,
        raw_size,
        raw_pointer,
        0,
        0,
        0,
        0,
        NEW_SECTION_CHARACTERISTICS,
    )
    candidate[
        section_header_offset : section_header_offset + len(section_header)
    ] = section_header

    replace_exact(candidate, HOOK_FILE_OFFSET, HOOK_BEFORE, HOOK_AFTER)

    certificate_offset = pe["certificate_directory_offset"]
    old_certificate_directory = bytes(
        candidate[certificate_offset : certificate_offset + 8]
    )
    if old_certificate_directory != bytes.fromhex("10CAE70108290000"):
        raise RuntimeError("unexpected stale certificate directory")
    candidate[certificate_offset : certificate_offset + 8] = b"\0" * 8

    controller_sites: list[dict[str, Any]] = []
    if controller:
        replace_exact(
            candidate,
            CONTROLLER_HOOK_FILE_OFFSET,
            CONTROLLER_HOOK_BEFORE,
            CONTROLLER_HOOK_AFTER,
        )
        controller_stub_file_offset = raw_pointer + CONTROLLER_STUB_OFFSET_IN_SECTION
        replace_exact(
            candidate,
            controller_stub_file_offset,
            b"\0" * len(CONTROLLER_STUB),
            CONTROLLER_STUB,
        )
        controller_sites = [
            {
                "offset": CONTROLLER_HOOK_FILE_OFFSET,
                "after_hex": CONTROLLER_HOOK_AFTER.hex().upper(),
            },
            {
                "offset": controller_stub_file_offset,
                "after_hex": CONTROLLER_STUB.hex().upper(),
            },
        ]

    checksum = set_pe_checksum(candidate, pe["checksum_offset"])
    result = bytes(candidate)
    result_pe = parse_pe(result)
    validate_adjacency(result_pe)
    if result_pe["size_of_image"] != 0x261B000:
        raise RuntimeError("fixed SizeOfImage mismatch")
    if result_pe["sections"][-1]["rva"] != NEW_SECTION_RVA:
        raise RuntimeError("fixed .mlbd RVA mismatch")
    if result[
        result_pe["certificate_directory_offset"] :
        result_pe["certificate_directory_offset"] + 8
    ] != b"\0" * 8:
        raise RuntimeError("certificate directory was not cleared")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(result)
    payload_path.write_bytes(bytes(payload))

    manifest: dict[str, Any] = {
        "schema": "nobu16.vertical-pe-section-hotfix.v0901",
        "controller": controller,
        "input": {
            "size": len(source),
            "sha256": sha256(source),
        },
        "old_payload": {
            "size": len(old_payload_path.read_bytes()),
            "sha256": sha256(old_payload_path.read_bytes()),
        },
        "new_payload": {
            "size": len(payload),
            "sha256": sha256(bytes(payload)),
        },
        "output": {
            "size": len(result),
            "sha256": sha256(result),
            "checksum": f"0x{checksum:08X}",
        },
        "pe": {
            "previous_section": ".reloc",
            "previous_section_aligned_end_rva": f"0x{reloc_end:X}",
            "new_section": ".mlbd",
            "new_section_rva": f"0x{NEW_SECTION_RVA:X}",
            "new_section_virtual_size": virtual_size,
            "size_of_image": f"0x{result_pe['size_of_image']:X}",
            "certificate_directory_cleared": True,
            "sections_adjacent": True,
        },
        "patch_sites": {
            "render_hook": {
                "offset": HOOK_FILE_OFFSET,
                "before_hex": HOOK_BEFORE.hex().upper(),
                "after_hex": HOOK_AFTER.hex().upper(),
            },
            "section_header": {
                "offset": section_header_offset,
                "after_hex": section_header.hex().upper(),
            },
            "certificate_directory": {
                "offset": certificate_offset,
                "before_hex": old_certificate_directory.hex().upper(),
                "after_hex": "00" * 8,
            },
            "controller": controller_sites,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--old-payload", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--payload", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--controller", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            build(
                args.source,
                args.old_payload,
                args.output,
                args.payload,
                args.manifest,
                args.controller,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
