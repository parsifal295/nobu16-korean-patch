#!/usr/bin/env python3
"""Build patch 010 for the v0.14.0 static EXE installer.

Patch 010 follows the existing 001--009 chain and changes only the event
message preformatter's automatic line-width limit from 40 to 60 units.  It
preserves authored line feeds and changes no dialogue text or control tags.
The game executable itself is never shipped.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import build_map_label_hotfix_v0121 as pe_tools
import build_map_label_status_icon_hotfix_v0131 as checksum_tools


EXPECTED_PATCH009_SHA256 = (
    "4ED6C7DBF3F9DF55F574D285DF82653C9A48BC4212DBF8728DE225946A34D730"
)
EXPECTED_PATCH010_SHA256 = (
    "C1E9123539506055C1ACB96A15A446C43952AED607DEA2C9646F690813FA53D5"
)
TARGET_SIZE = 67_024_384

AUTO_WRAP_WIDTH_BEFORE = bytes.fromhex("27")  # 40 units: 20 fullwidth glyphs
AUTO_WRAP_WIDTH_AFTER = bytes.fromhex("3B")   # 60 units: 30 fullwidth glyphs
AUTO_WRAP_SITES = (
    (
        "expand primary event auto-wrap limit from 40 to 60",
        0x0085C9D4,
        bytes.fromhex("458D4127488D5590498BCEE81FC11900"),
    ),
    (
        "expand alternate event auto-wrap limit from 40 to 60",
        0x0088F6F1,
        bytes.fromhex("458D4127488D542440498BCEE801941600"),
    ),
)

PatchSite = tuple[str, int, bytes, bytes]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def patch_sites(source: bytes) -> list[PatchSite]:
    """Return the reviewed automatic event-wrap width site."""
    pe = pe_tools.parse_pe(source)
    image_base = pe["image_base"]
    sites: list[PatchSite] = []
    for name, rva, signature in AUTO_WRAP_SITES:
        auto_wrap_offset = pe_tools.va_to_file(source, pe, image_base + rva)
        if source[auto_wrap_offset - 3 : auto_wrap_offset - 3 + len(signature)] != signature:
            raise RuntimeError(f"event auto-wrap call signature changed: {name}")
        site = (name, auto_wrap_offset, AUTO_WRAP_WIDTH_BEFORE, AUTO_WRAP_WIDTH_AFTER)
        _name, offset, before, _after = site
        actual = source[offset : offset + len(before)]
        if actual != before:
            raise RuntimeError(
                f"source mismatch at {_name}: expected={before.hex().upper()} "
                f"actual={actual.hex().upper()}"
            )
        sites.append(site)
    return sites


def render_definition(sites: list[PatchSite]) -> str:
    lines = [
        "@{",
        "    Id = '010'",
        "    Name = 'Expanded event message auto-wrap limit'",
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
    if len(source) != TARGET_SIZE or sha256(source) != EXPECTED_PATCH009_SHA256:
        raise RuntimeError(
            f"unexpected pre-010 candidate: size={len(source)} sha256={sha256(source)}"
        )

    sites = patch_sites(source)
    target = bytearray(source)
    for name, offset, before, after in sites:
        if len(before) != len(after) or before == after:
            raise RuntimeError(f"invalid patch site: {name}")
        target[offset : offset + len(after)] = after

    checksum_tools.set_pe_checksum(target)
    target_bytes = bytes(target)
    target_hash = sha256(target_bytes)
    if EXPECTED_PATCH010_SHA256 and target_hash != EXPECTED_PATCH010_SHA256:
        raise RuntimeError(f"patch 010 candidate hash changed: {target_hash}")

    definition = render_definition(sites)
    definition_bytes = definition.encode("ascii")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    definition_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(target_bytes)
    definition_path.write_text(definition, encoding="ascii", newline="\n")
    return {
        "site_count": len(sites),
        "definition_size": len(definition_bytes),
        "definition_sha256": sha256(definition_bytes),
        "source_size": len(source),
        "source_sha256": sha256(source),
        "target_size": len(target_bytes),
        "target_sha256": target_hash,
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
