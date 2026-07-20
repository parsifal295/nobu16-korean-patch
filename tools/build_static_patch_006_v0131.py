#!/usr/bin/env python3
"""Build the v0.13.1 installer BytePatch for issue 72.

Patches 001 through 005 remain byte-identical to their published definitions.
Patch 006 applies after the v0.13.0 structural state and contains only the
reviewed update-call hook, its dynamic X/Y and supply-alignment wrapper, and
the two PE section metadata fields needed to execute that wrapper.  The game
executable itself is never shipped.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import build_map_label_status_icon_hotfix_v0131 as hotfix
import build_map_label_hotfix_v0121 as pe_tools


EXPECTED_V0130_SHA256 = hotfix.EXPECTED_V0130_SHA256
EXPECTED_V0131_SHA256 = hotfix.EXPECTED_CANDIDATE_SHA256
EXPECTED_V0130_INSTALLED_SHA256 = (
    "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6"
)
EXPECTED_V0131_INSTALLED_SHA256 = (
    "811F6B31C09AD87F2D73F1349FB17AA4C9ABEA76F2415083C78E932D0B1D5A31"
)
TARGET_SIZE = 67_024_384

PatchSite = tuple[str, int, bytes, bytes]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def with_pe_checksum(data: bytes) -> bytes:
    """Match Invoke-Nobu16StaticPatches.ps1 Set-PeChecksum."""
    result = bytearray(data)
    hotfix.set_pe_checksum(result)
    return bytes(result)


def patch_sites(source: bytes, target: bytes) -> list[PatchSite]:
    """Return the four reviewed, non-checksum v0.13.1 patch sites."""
    pe = pe_tools.parse_pe(source)
    sections = [section for section in pe["sections"] if section["name"] == hotfix.CODE_SECTION]
    if len(sections) != 1:
        raise RuntimeError(f"expected exactly one {hotfix.CODE_SECTION} section")
    section = sections[0]

    unaligned_file_offset = section["raw_pointer"] + section["virtual_size"]
    code_file_offset = (unaligned_file_offset + 15) & ~15
    code_padding = code_file_offset - unaligned_file_offset
    code_va = pe["image_base"] + section["rva"] + section["virtual_size"] + code_padding
    injected, _ = hotfix.build_injected_code(code_va)

    virtual_size_offset = section["header_offset"] + 8
    characteristics_offset = section["header_offset"] + 36
    hook_offset = pe_tools.va_to_file(source, pe, hotfix.STATUS_UPDATE_CALL_SITE)

    sites: list[PatchSite] = []
    for name, offset, size in (
        ("extend .mlbd virtual size through issue-72 wrapper", virtual_size_offset, 4),
        ("mark .mlbd executable for issue-72 wrapper", characteristics_offset, 4),
        ("wrap map-label status update with dynamic alignment", hook_offset, 5),
        (
            "dynamic map status X/Y and paired supply-root alignment wrapper",
            code_file_offset,
            len(injected),
        ),
    ):
        sites.append((name, offset, source[offset : offset + size], target[offset : offset + size]))

    if sites[-1][2] != b"\0" * len(injected):
        raise RuntimeError("issue-72 wrapper destination is not empty in v0.13.0")
    if sites[-1][3] != injected:
        raise RuntimeError("v0.13.1 wrapper bytes differ from the reviewed builder")
    return sites


def render_definition(sites: list[PatchSite]) -> str:
    lines = [
        "@{",
        "    Id = '006'",
        "    Name = 'Dynamic horizontal map status and supply alignment'",
        "    Kind = 'BytePatch'",
        "    Sites = @(",
    ]
    for name, offset, before, after in sites:
        safe_name = name.replace("'", "''")
        lines.append(
            "        @{ "
            f"Name = '{safe_name}'; Offset = 0x{offset:08X}; "
            f"Before = '{before.hex().upper()}'; After = '{after.hex().upper()}' "
            "}"
        )
    lines.extend(("    )", "}", ""))
    return "\n".join(lines)


def build(source_path: Path, target_path: Path, definition_path: Path) -> dict[str, object]:
    source = source_path.read_bytes()
    target = target_path.read_bytes()
    if len(source) != TARGET_SIZE or sha256(source) != EXPECTED_V0130_SHA256:
        raise RuntimeError(
            f"unexpected v0.13.0 candidate: size={len(source)} sha256={sha256(source)}"
        )
    if len(target) != TARGET_SIZE or sha256(target) != EXPECTED_V0131_SHA256:
        raise RuntimeError(
            f"unexpected v0.13.1 candidate: size={len(target)} sha256={sha256(target)}"
        )

    source_installed_hash = sha256(with_pe_checksum(source))
    target_installed_hash = sha256(with_pe_checksum(target))
    if source_installed_hash != EXPECTED_V0130_INSTALLED_SHA256:
        raise RuntimeError("v0.13.0 installed checksum hash changed: " + source_installed_hash)
    if target_installed_hash != EXPECTED_V0131_INSTALLED_SHA256:
        raise RuntimeError("v0.13.1 installed checksum hash changed: " + target_installed_hash)

    sites = patch_sites(source, target)
    if len(sites) != 4:
        raise RuntimeError(f"unexpected patch 006 site count: {len(sites)}")

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

    hotfix.set_pe_checksum(reconstructed)
    if bytes(reconstructed) != target:
        raise RuntimeError("patch 006 sites plus PE checksum do not reconstruct the target")

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
