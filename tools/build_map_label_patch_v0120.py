#!/usr/bin/env python3
"""Build the v0.12.0 structural EXE patch from reviewed local candidates.

The release never ships NOBU16PK.exe.  It stores exact in-place byte edits and
a deterministic gzip payload for the new PE sections appended by the reviewed
horizontal map-label candidate.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import struct
from pathlib import Path


EXPECTED_BASE_SHA256 = (
    "FD7F07A29DBD76E4AB18B1D1EE85D6B1677E0A4827A79E3732075D4CACBA8BB6"
)
EXPECTED_CANDIDATE_SHA256 = (
    "5D5B1F0B9CDE3A651DFA84E19FD5C7F2C6DF06D6D25C3674C049F7F049D26BF7"
)
PATCH_NAME = "004-HorizontalMapLabelsDynamicWidth.psd1"
PAYLOAD_NAME = "004-HorizontalMapLabelsDynamicWidth.append.gz"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def pe_checksum_offset(data: bytes) -> int:
    if len(data) < 0x400 or data[:2] != b"MZ":
        raise RuntimeError("input is not a PE executable")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe : pe + 4] != b"PE\0\0":
        raise RuntimeError("input PE signature is invalid")
    optional = pe + 24
    if struct.unpack_from("<H", data, optional)[0] != 0x20B:
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


def changed_runs(before: bytes, after: bytes, ignored: range) -> list[tuple[int, bytes, bytes]]:
    ignored_offsets = set(ignored)
    changed = [
        index
        for index, (old, new) in enumerate(zip(before, after, strict=True))
        if old != new and index not in ignored_offsets
    ]
    runs: list[tuple[int, bytes, bytes]] = []
    if not changed:
        return runs
    start = previous = changed[0]
    for index in changed[1:]:
        if index != previous + 1:
            end = previous + 1
            runs.append((start, before[start:end], after[start:end]))
            start = index
        previous = index
    end = previous + 1
    runs.append((start, before[start:end], after[start:end]))
    return runs


def ps_hex(data: bytes) -> str:
    return data.hex().upper()


def render_definition(
    runs: list[tuple[int, bytes, bytes]],
    base_size: int,
    target_size: int,
    payload_size: int,
    payload_sha256: str,
    append_size: int,
    append_sha256: str,
) -> str:
    lines = [
        "@{",
        "    Id = '004'",
        "    Name = 'Korean horizontal map labels with dynamic plates'",
        "    Kind = 'AppendOverlay'",
        f"    BaseSize = {base_size}L",
        f"    TargetSize = {target_size}L",
        "    Append = @{",
        f"        File = 'Payloads/{PAYLOAD_NAME}'",
        f"        Size = {payload_size}L",
        f"        Sha256 = '{payload_sha256}'",
        f"        ExpandedSize = {append_size}L",
        f"        ExpandedSha256 = '{append_sha256}'",
        "        Compression = 'gzip'",
        "    }",
        "    Sites = @(",
    ]
    for index, (offset, before, after) in enumerate(runs, start=1):
        lines.append(
            "        @{ Name = 'map-label structural edit "
            f"{index:03d}'; Offset = 0x{offset:08X}; "
            f"Before = '{ps_hex(before)}'; After = '{ps_hex(after)}' }}"
        )
    lines.extend(("    )", "}", ""))
    return "\n".join(lines)


def build(base_path: Path, candidate_path: Path, output_root: Path) -> dict[str, object]:
    base = base_path.read_bytes()
    candidate_input = candidate_path.read_bytes()
    if sha256(base) != EXPECTED_BASE_SHA256:
        raise RuntimeError(f"unexpected all-applied v0.11.6 base: {sha256(base)}")
    if sha256(candidate_input) != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(f"unexpected reviewed v23 candidate: {sha256(candidate_input)}")
    if len(candidate_input) <= len(base):
        raise RuntimeError("reviewed candidate does not contain appended PE sections")

    candidate = bytearray(candidate_input)
    set_pe_checksum(candidate)
    checksum_offset = pe_checksum_offset(candidate)
    runs = changed_runs(
        base,
        bytes(candidate[: len(base)]),
        range(checksum_offset, checksum_offset + 4),
    )
    if not runs:
        raise RuntimeError("candidate has no reviewed in-place edits")

    append = bytes(candidate[len(base) :])
    compressed = gzip.compress(append, compresslevel=9, mtime=0)
    payload_root = output_root / "Payloads"
    payload_root.mkdir(parents=True, exist_ok=True)
    payload_path = payload_root / PAYLOAD_NAME
    definition_path = output_root / PATCH_NAME
    payload_path.write_bytes(compressed)
    definition_path.write_text(
        render_definition(
            runs,
            len(base),
            len(candidate),
            len(compressed),
            sha256(compressed),
            len(append),
            sha256(append),
        ),
        encoding="ascii",
        newline="\n",
    )
    return {
        "definition": str(definition_path),
        "definition_size": definition_path.stat().st_size,
        "definition_sha256": sha256(definition_path.read_bytes()),
        "payload": str(payload_path),
        "payload_size": len(compressed),
        "payload_sha256": sha256(compressed),
        "append_size": len(append),
        "append_sha256": sha256(append),
        "site_count": len(runs),
        "output_size": len(candidate),
        "output_sha256": sha256(candidate),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    result = build(args.base, args.candidate, args.output_root)
    for key, value in result.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
