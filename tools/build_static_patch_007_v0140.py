#!/usr/bin/env python3
"""Build the v0.14.0 event-message typography BytePatch.

Patches 001 through 006 remain byte-identical to their published definitions.
Patch 007 changes only the two packed typography constants used when the
event narration text widget is constructed: line spacing 10 -> 8 and font
size 36 -> 30.  The game executable itself is never shipped.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import build_map_label_hotfix_v0121 as pe_tools
import build_map_label_status_icon_hotfix_v0131 as checksum_tools


EXPECTED_V0131_SHA256 = (
    "3548AD5B71168296DD03851B1F9613CAD1C325AF2AB916A11CC140DC61FA0E43"
)
EXPECTED_V0140_SHA256 = (
    "F424964405CFCD1AC454B3801DA4795A183A8271DD16EA8A6A7B97A2547232BF"
)
TARGET_SIZE = 67_024_384

LINE_SPACING_VA = 0x14089A17A
FONT_SIZE_VA = 0x14089A1BC

PatchSite = tuple[str, int, bytes, bytes]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def patch_sites(source: bytes) -> list[PatchSite]:
    """Return the two reviewed event-only typography patch sites."""
    pe = pe_tools.parse_pe(source)
    line_spacing_offset = pe_tools.va_to_file(source, pe, LINE_SPACING_VA)
    font_size_offset = pe_tools.va_to_file(source, pe, FONT_SIZE_VA)

    sites = [
        (
            "reduce event message line spacing from 10 to 8",
            line_spacing_offset,
            bytes.fromhex("BF000A0000"),
            bytes.fromhex("BF00080000"),
        ),
        (
            "reduce event message font size from 36 to 30",
            font_size_offset,
            bytes.fromhex("B924000000"),
            bytes.fromhex("B91E000000"),
        ),
    ]
    for name, offset, before, _after in sites:
        actual = source[offset : offset + len(before)]
        if actual != before:
            raise RuntimeError(
                f"source mismatch at {name}: expected={before.hex().upper()} "
                f"actual={actual.hex().upper()}"
            )
    return sites


def render_definition(sites: list[PatchSite]) -> str:
    lines = [
        "@{",
        "    Id = '007'",
        "    Name = 'Compact event message typography'",
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
    if len(source) != TARGET_SIZE or sha256(source) != EXPECTED_V0131_SHA256:
        raise RuntimeError(
            f"unexpected v0.13.1 candidate: size={len(source)} sha256={sha256(source)}"
        )

    sites = patch_sites(source)
    target = bytearray(source)
    occupied: set[int] = set()
    for name, offset, before, after in sites:
        if len(before) != len(after) or before == after:
            raise RuntimeError(f"invalid patch site: {name}")
        span = set(range(offset, offset + len(before)))
        if occupied.intersection(span):
            raise RuntimeError(f"overlapping patch site: {name}")
        occupied.update(span)
        target[offset : offset + len(after)] = after

    checksum_tools.set_pe_checksum(target)
    target_bytes = bytes(target)
    target_hash = sha256(target_bytes)
    if target_hash != EXPECTED_V0140_SHA256:
        raise RuntimeError(f"v0.14.0 candidate hash changed: {target_hash}")

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
