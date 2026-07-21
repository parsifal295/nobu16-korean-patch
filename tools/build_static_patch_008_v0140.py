#!/usr/bin/env python3
"""Build patch 008 for the v0.14.0 static EXE installer.

Patches 001 through 007 remain byte-identical.  Patch 008 chains the reviewed
auxiliary-indicator helper from the published patch 006 wrapper and contains
only the helper bytes, the wrapper epilogue jump, and the .mlbd virtual-size
extension.  The game executable itself is never shipped.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import build_map_label_aux_status_hotfix_v0140 as hotfix
import build_map_label_hotfix_v0121 as pe_tools
import build_map_label_status_icon_hotfix_v0131 as checksum_tools


EXPECTED_V0140_SHA256 = hotfix.EXPECTED_V0140_SHA256
EXPECTED_PATCH008_SHA256 = hotfix.EXPECTED_CANDIDATE_SHA256
TARGET_SIZE = hotfix.TARGET_SIZE

PatchSite = tuple[str, int, bytes, bytes]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def with_pe_checksum(data: bytes) -> bytes:
    result = bytearray(data)
    checksum_tools.set_pe_checksum(result)
    return bytes(result)


def patch_sites(source: bytes, target: bytes) -> list[PatchSite]:
    pe = pe_tools.parse_pe(source)
    sections = [section for section in pe["sections"] if section["name"] == hotfix.CODE_SECTION]
    if len(sections) != 1:
        raise RuntimeError(f"expected exactly one {hotfix.CODE_SECTION} section")
    section = sections[0]

    unaligned_file_offset = section["raw_pointer"] + section["virtual_size"]
    code_file_offset = (unaligned_file_offset + 15) & ~15
    code_padding = code_file_offset - unaligned_file_offset
    code_va = pe["image_base"] + section["rva"] + section["virtual_size"] + code_padding
    injected, _labels = hotfix.build_injected_code(code_va)

    virtual_size_offset = section["header_offset"] + 8
    epilogue_offset = pe_tools.va_to_file(source, pe, hotfix.EXISTING_006_EPILOGUE_VA)
    sites = [
        (
            "extend .mlbd virtual size through patch 008 helper",
            virtual_size_offset,
            source[virtual_size_offset : virtual_size_offset + 4],
            target[virtual_size_offset : virtual_size_offset + 4],
        ),
        (
            "chain patch 006 wrapper into auxiliary indicator alignment",
            epilogue_offset,
            source[epilogue_offset : epilogue_offset + 5],
            target[epilogue_offset : epilogue_offset + 5],
        ),
        (
            "align battle-ready number and no-castle-lord warning",
            code_file_offset,
            source[code_file_offset : code_file_offset + len(injected)],
            target[code_file_offset : code_file_offset + len(injected)],
        ),
    ]
    if code_padding != 14:
        raise RuntimeError(f"unexpected patch 008 alignment padding: {code_padding}")
    if sites[-1][2] != b"\0" * len(injected):
        raise RuntimeError("patch 008 helper destination is not empty")
    if sites[-1][3] != injected:
        raise RuntimeError("patch 008 helper bytes differ from the reviewed builder")
    return sites


def render_definition(sites: list[PatchSite]) -> str:
    lines = [
        "@{",
        "    Id = '008'",
        "    Name = 'Dynamic map auxiliary indicator alignment'",
        "    Kind = 'BytePatch'",
        "    Sites = @(",
    ]
    for name, offset, before, after in sites:
        lines.append(
            "        @{ "
            f"Name = '{name}'; Offset = 0x{offset:08X}; "
            f"Before = '{before.hex().upper()}'; After = '{after.hex().upper()}' "
            "}"
        )
    lines.extend(("    )", "}", ""))
    return "\n".join(lines)


def build(source_path: Path, target_path: Path, definition_path: Path) -> dict[str, object]:
    source = source_path.read_bytes()
    target = target_path.read_bytes()
    if len(source) != TARGET_SIZE or sha256(source) != EXPECTED_V0140_SHA256:
        raise RuntimeError(
            f"unexpected pre-008 candidate: size={len(source)} sha256={sha256(source)}"
        )
    if not EXPECTED_PATCH008_SHA256:
        raise RuntimeError("EXPECTED_PATCH008_SHA256 must be pinned before definition build")
    if len(target) != TARGET_SIZE or sha256(target) != EXPECTED_PATCH008_SHA256:
        raise RuntimeError(
            f"unexpected patch-008 candidate: size={len(target)} sha256={sha256(target)}"
        )

    sites = patch_sites(source, target)
    if len(sites) != 3:
        raise RuntimeError(f"unexpected patch 008 site count: {len(sites)}")

    occupied: set[int] = set()
    reconstructed = bytearray(source)
    for name, offset, before, after in sites:
        if len(before) != len(after) or before == after:
            raise RuntimeError(f"invalid patch site: {name}")
        span = set(range(offset, offset + len(before)))
        if occupied.intersection(span):
            raise RuntimeError(f"overlapping patch site: {name}")
        occupied.update(span)
        if source[offset : offset + len(before)] != before:
            raise RuntimeError(f"source mismatch at patch site: {name}")
        reconstructed[offset : offset + len(after)] = after

    checksum_tools.set_pe_checksum(reconstructed)
    if bytes(reconstructed) != target:
        raise RuntimeError("patch 008 sites plus PE checksum do not reconstruct the target")

    source_installed_hash = sha256(with_pe_checksum(source))
    target_installed_hash = sha256(with_pe_checksum(target))
    definition = render_definition(sites)
    definition_bytes = definition.encode("ascii")
    definition_path.parent.mkdir(parents=True, exist_ok=True)
    definition_path.write_text(definition, encoding="ascii", newline="\n")
    return {
        "site_count": len(sites),
        "injected_code_size": len(sites[-1][2]),
        "definition_size": len(definition_bytes),
        "definition_sha256": sha256(definition_bytes),
        "source_size": len(source),
        "source_sha256": sha256(source),
        "target_size": len(target),
        "target_sha256": sha256(target),
        "source_installed_sha256": source_installed_hash,
        "target_installed_sha256": target_installed_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--definition", required=True, type=Path)
    args = parser.parse_args()
    print(build(args.source, args.target, args.definition))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
