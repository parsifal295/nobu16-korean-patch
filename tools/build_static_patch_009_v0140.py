#!/usr/bin/env python3
"""Build patch 009 for the v0.14.0 static EXE installer.

Patch 009 follows the existing 001--008 chain and changes only the event
dialogue parent rectangle width.  The 60-pixel text inset remains unchanged,
so the effective event-text lane expands from 822 to 912 pixels.  The game
executable itself is never shipped.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import build_map_label_hotfix_v0121 as pe_tools
import build_map_label_status_icon_hotfix_v0131 as checksum_tools


EXPECTED_PATCH008_SHA256 = (
    "01C8769F09BD9A5459844FF5E335A71048C1F11CC7AF7738517EFEE61D4BF28D"
)
EXPECTED_PATCH009_SHA256 = (
    "4ED6C7DBF3F9DF55F574D285DF82653C9A48BC4212DBF8728DE225946A34D730"
)
TARGET_SIZE = 67_024_384

PARENT_WIDTH_VA = 0x14151D388
PARENT_WIDTH_BEFORE = bytes.fromhex("00805C44")  # 882.0f
PARENT_WIDTH_AFTER = bytes.fromhex("00007344")   # 972.0f

PatchSite = tuple[str, int, bytes, bytes]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def patch_sites(source: bytes) -> list[PatchSite]:
    """Return the reviewed event-parent width site."""
    pe = pe_tools.parse_pe(source)
    parent_width_offset = pe_tools.va_to_file(source, pe, PARENT_WIDTH_VA)
    site = (
        "expand event message parent width from 882 to 972",
        parent_width_offset,
        PARENT_WIDTH_BEFORE,
        PARENT_WIDTH_AFTER,
    )
    name, offset, before, _after = site
    actual = source[offset : offset + len(before)]
    if actual != before:
        raise RuntimeError(
            f"source mismatch at {name}: expected={before.hex().upper()} "
            f"actual={actual.hex().upper()}"
        )
    return [site]


def render_definition(sites: list[PatchSite]) -> str:
    lines = [
        "@{",
        "    Id = '009'",
        "    Name = 'Expand event message parent width'",
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
    if len(source) != TARGET_SIZE or sha256(source) != EXPECTED_PATCH008_SHA256:
        raise RuntimeError(
            f"unexpected pre-009 candidate: size={len(source)} sha256={sha256(source)}"
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
    if target_hash != EXPECTED_PATCH009_SHA256:
        raise RuntimeError(f"patch 009 candidate hash changed: {target_hash}")

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
