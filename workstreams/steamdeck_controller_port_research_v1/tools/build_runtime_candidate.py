#!/usr/bin/env python3
"""Build the reviewed v0.90.0 horizontal controller-input runtime candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


EXPECTED_SOURCE_SIZE = 67_024_896
EXPECTED_SOURCE_SHA256 = (
    "7A0DF96C72A93F551F283EF14F06159F50E6A265A3BAC9C14151A1C2895D4DA0"
)
EXPECTED_ENTRY_POINT_RVA = 0x12FE4D0
PATCH_SITES = (
    (0x00C5D656, bytes.fromhex("E84525D6FF"), bytes.fromhex("B801000000")),
    (0x00C5D692, bytes.fromhex("E80925D6FF"), bytes.fromhex("B801000000")),
)


def sha256(data: bytes | bytearray) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def set_pe_checksum(image: bytearray) -> tuple[int, int]:
    if len(image) < 0x400 or image[:2] != b"MZ":
        raise RuntimeError("invalid PE DOS header")
    pe_offset = struct.unpack_from("<I", image, 0x3C)[0]
    optional_offset = pe_offset + 24
    if image[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise RuntimeError("invalid PE signature")
    if struct.unpack_from("<H", image, optional_offset)[0] != 0x20B:
        raise RuntimeError("expected PE32+ optional header")
    entry_point_rva = struct.unpack_from("<I", image, optional_offset + 16)[0]
    if entry_point_rva != EXPECTED_ENTRY_POINT_RVA:
        raise RuntimeError(
            f"entry point mismatch: 0x{entry_point_rva:X}/"
            f"0x{EXPECTED_ENTRY_POINT_RVA:X}"
        )

    checksum_offset = optional_offset + 64
    image[checksum_offset : checksum_offset + 4] = b"\0" * 4
    checksum_sum = 0
    for offset in range(0, len(image), 2):
        if checksum_offset <= offset < checksum_offset + 4:
            word = 0
        else:
            low = image[offset]
            high = image[offset + 1] if offset + 1 < len(image) else 0
            word = low | (high << 8)
        checksum_sum += word
        checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
    checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
    checksum = (checksum_sum + len(image)) & 0xFFFFFFFF
    struct.pack_into("<I", image, checksum_offset, checksum)
    return checksum_offset, checksum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = args.source.read_bytes()
    if len(source) != EXPECTED_SOURCE_SIZE:
        raise RuntimeError(
            f"source size mismatch: {len(source)}/{EXPECTED_SOURCE_SIZE}"
        )
    source_hash = sha256(source)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            f"source SHA-256 mismatch: {source_hash}/{EXPECTED_SOURCE_SHA256}"
        )

    candidate = bytearray(source)
    patch_offsets: set[int] = set()
    for offset, before, after in PATCH_SITES:
        actual = bytes(candidate[offset : offset + len(before)])
        if actual != before:
            raise RuntimeError(
                f"preimage mismatch at 0x{offset:X}: "
                f"{actual.hex().upper()}/{before.hex().upper()}"
            )
        candidate[offset : offset + len(after)] = after
        patch_offsets.update(range(offset, offset + len(after)))

    checksum_offset, checksum = set_pe_checksum(candidate)
    allowed_changes = patch_offsets | set(range(checksum_offset, checksum_offset + 4))
    actual_changes = {
        offset
        for offset, (before, after) in enumerate(zip(source, candidate))
        if before != after
    }
    unexpected_changes = actual_changes - allowed_changes
    if unexpected_changes:
        first = min(unexpected_changes)
        raise RuntimeError(f"unexpected byte change at 0x{first:X}")
    if not patch_offsets.issubset(actual_changes):
        raise RuntimeError("one or more reviewed patch bytes did not change")

    args.output.parent.mkdir(parents=True, exist_ok=False)
    args.output.write_bytes(candidate)

    report = {
        "source": str(args.source.resolve()),
        "source_size": len(source),
        "source_sha256": source_hash,
        "output": str(args.output.resolve()),
        "output_size": len(candidate),
        "output_sha256": sha256(candidate),
        "entry_point_rva": f"0x{EXPECTED_ENTRY_POINT_RVA:X}",
        "pe_checksum_offset": f"0x{checksum_offset:X}",
        "pe_checksum": f"0x{checksum:08X}",
        "changed_byte_count": len(actual_changes),
        "patch_sites": [
            {
                "offset": f"0x{offset:X}",
                "before_hex": before.hex().upper(),
                "after_hex": after.hex().upper(),
            }
            for offset, before, after in PATCH_SITES
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
