#!/usr/bin/env python3
"""Build the v0.13.0 horizontal ground-landmark label EXE candidate.

Runtime tracing identified the exact ground-landmark owner by its live vtable,
then Japanese/English binary comparison isolated the matching constructor.
This builder selects the executable's native horizontal text container, plate,
and renderer branches only inside that constructor.  Resource archives are not
changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import build_map_label_hotfix_v0121 as v0121


EXPECTED_V0121_SHA256 = (
    "7F5B28B5435AE8F808301E5D86F7CDE8481270856425B0BB3170BD4FFFE5674B"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FCA1D8CF58D44BDFAEFF338F5CF935AB9B2FA0F611EDC26CC8E9DF6E40B9D892"
)
HORIZONTAL_RESULT = bytes.fromhex("B8 01 00 00 00")

# All addresses are inside the exact ground-landmark owner constructor
# 0x140F42AD0 (English counterpart 0x140F3DED0).  The selected English-native
# branch changes the live text widget from 24x168 to 1200x24 and the associated
# plate from vertical geometry to [43, 183, 285, 40].
LANDMARK_HORIZONTAL_SITES = (
    (0x140F42BFB, bytes.fromhex("E8 90 D5 A7 FF"), "text widget horizontal placement table"),
    (0x140F42C2A, bytes.fromhex("E8 61 D5 A7 FF"), "disable Japanese vertical Y correction"),
    (0x140F42DC7, bytes.fromhex("E8 C4 D3 A7 FF"), "text renderer horizontal flags"),
    (0x140F42DFD, bytes.fromhex("E8 8E D3 A7 FF"), "text widget horizontal height"),
    (0x140F42E3D, bytes.fromhex("E8 4E D3 A7 FF"), "text widget horizontal width branch"),
    (0x140F42E52, bytes.fromhex("E8 39 D3 A7 FF"), "text widget 1200px width"),
    (0x140F42F13, bytes.fromhex("E8 78 D2 A7 FF"), "plate horizontal field 1"),
    (0x140F42F38, bytes.fromhex("E8 53 D2 A7 FF"), "plate horizontal field 2"),
    (0x140F42F5D, bytes.fromhex("E8 2E D2 A7 FF"), "plate horizontal field 3"),
    (0x140F42F82, bytes.fromhex("E8 09 D2 A7 FF"), "plate horizontal field 4"),
    (0x140F61B10, bytes.fromhex("E8 7B E6 A5 FF"), "live horizontal resize rectangle"),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def changed_runs(before: bytes, after: bytes) -> list[tuple[int, int]]:
    changed = [
        index
        for index, (old, new) in enumerate(zip(before, after, strict=True))
        if old != new
    ]
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


def build(source_path: Path, output_path: Path, manifest_path: Path) -> dict[str, object]:
    source = source_path.read_bytes()
    source_hash = sha256(source)
    if source_hash != EXPECTED_V0121_SHA256:
        raise RuntimeError(f"v0.12.1 candidate hash gate failed: {source_hash}")

    pe = v0121.parse_pe(source)
    if pe["image_base"] != v0121.IMAGE_BASE:
        raise RuntimeError("unexpected image base")

    candidate = bytearray(source)
    records: list[dict[str, object]] = []
    reviewed_offsets: set[int] = set()
    for va, expected, purpose in LANDMARK_HORIZONTAL_SITES:
        offset = v0121.va_to_file(source, pe, va)
        actual = source[offset : offset + len(expected)]
        if actual != expected:
            raise RuntimeError(
                f"reviewed landmark-label bytes changed at 0x{va:X}: "
                f"{actual.hex(' ').upper()}"
            )
        candidate[offset : offset + len(HORIZONTAL_RESULT)] = HORIZONTAL_RESULT
        reviewed_offsets.update(range(offset, offset + len(HORIZONTAL_RESULT)))
        records.append(
            {
                "va": f"0x{va:X}",
                "file_offset": f"0x{offset:X}",
                "before": expected.hex(" ").upper(),
                "after": HORIZONTAL_RESULT.hex(" ").upper(),
                "purpose": purpose,
            }
        )

    result = bytes(candidate)
    runs = changed_runs(source, result)
    changed_offsets = {
        offset for start, end in runs for offset in range(start, end)
    }
    if not changed_offsets or not changed_offsets <= reviewed_offsets:
        raise RuntimeError("candidate changed outside reviewed landmark-label sites")

    result_hash = sha256(result)
    if result_hash != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(f"v0.13.0 candidate hash changed: {result_hash}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(result)
    manifest = {
        "schema": "nobu16.map-labels-horizontal.v28-exact-ground-landmark-owner",
        "purpose": (
            "Select the native horizontal text container, renderer flags, and "
            "plate geometry in the exact ground-landmark owner constructor and "
            "its live resize vtable method."
        ),
        "input": {
            "path": str(source_path),
            "size": len(source),
            "sha256": source_hash,
        },
        "output": {
            "path": str(output_path),
            "size": len(result),
            "sha256": result_hash,
        },
        "patches": records,
        "changed_runs": [
            {"start": f"0x{start:X}", "end": f"0x{end:X}"}
            for start, end in runs
        ],
        "resource_archives_changed": False,
        "runtime_restart_required": True,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            build(args.source, args.output, args.manifest),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
