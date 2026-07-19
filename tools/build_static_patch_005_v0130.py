#!/usr/bin/env python3
"""Build v0.13.0 installer patch 005 from reviewed EXE candidates.

Patch 004 is an immutable v0.12.0 append overlay.  Patch 005 starts from that
exact state, appends the dual-resolution atlas produced for issue 68, and
includes the exact ground-landmark horizontal-label branches for issue 70.
The game executable itself is never shipped; only the deterministic append
payload and a byte-pinned PowerShell data definition are emitted.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
from pathlib import Path


EXPECTED_V0120_SHA256 = (
    "5D5B1F0B9CDE3A651DFA84E19FD5C7F2C6DF06D6D25C3674C049F7F049D26BF7"
)
EXPECTED_V0130_SHA256 = (
    "FCA1D8CF58D44BDFAEFF338F5CF935AB9B2FA0F611EDC26CC8E9DF6E40B9D892"
)
BASE_SIZE = 38_991_872
TARGET_SIZE = 67_024_384


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def changed_runs(before: bytes, after: bytes) -> list[tuple[int, int]]:
    if len(before) != len(after):
        raise ValueError("changed-run inputs must have equal length")
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


def render_definition(
    source: bytes,
    target: bytes,
    compressed: bytes,
) -> str:
    expanded = target[BASE_SIZE:]
    runs = changed_runs(source, target[:BASE_SIZE])
    if not runs:
        raise RuntimeError("patch 005 has no in-place edits")
    lines = [
        "@{",
        "    Id = '005'",
        "    Name = 'Dual-resolution map labels and horizontal landmark names'",
        "    Kind = 'AppendOverlay'",
        f"    BaseSize = {BASE_SIZE}L",
        f"    TargetSize = {TARGET_SIZE}L",
        "    Append = @{",
        "        File = 'Payloads/005-DualResolutionAndHorizontalLandmarks.append.gz'",
        f"        Size = {len(compressed)}L",
        f"        Sha256 = '{sha256(compressed)}'",
        f"        ExpandedSize = {len(expanded)}L",
        f"        ExpandedSha256 = '{sha256(expanded)}'",
        "        Compression = 'gzip'",
        "    }",
        "    Sites = @(",
    ]
    for index, (start, end) in enumerate(runs, 1):
        before = source[start:end].hex().upper()
        after = target[start:end].hex().upper()
        lines.append(
            "        @{ "
            f"Name = 'v0.13.0 cumulative map-label edit {index:03d}'; "
            f"Offset = 0x{start:08X}; Before = '{before}'; After = '{after}' "
            "}"
        )
    lines.extend(("    )", "}", ""))
    return "\n".join(lines)


def build(
    source_path: Path,
    target_path: Path,
    definition_path: Path,
    payload_path: Path,
) -> dict[str, object]:
    source = source_path.read_bytes()
    target = target_path.read_bytes()
    if len(source) != BASE_SIZE or sha256(source) != EXPECTED_V0120_SHA256:
        raise RuntimeError(
            f"unexpected v0.12.0 candidate: size={len(source)} sha256={sha256(source)}"
        )
    if len(target) != TARGET_SIZE or sha256(target) != EXPECTED_V0130_SHA256:
        raise RuntimeError(
            f"unexpected v0.13.0 candidate: size={len(target)} sha256={sha256(target)}"
        )

    expanded = target[BASE_SIZE:]
    compressed = gzip.compress(expanded, compresslevel=9, mtime=0)
    definition = render_definition(source, target, compressed)

    definition_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    definition_path.write_text(definition, encoding="ascii", newline="\n")
    payload_path.write_bytes(compressed)
    return {
        "site_count": len(changed_runs(source, target[:BASE_SIZE])),
        "definition_size": len(definition.encode("ascii")),
        "definition_sha256": sha256(definition.encode("ascii")),
        "payload_size": len(compressed),
        "payload_sha256": sha256(compressed),
        "expanded_size": len(expanded),
        "expanded_sha256": sha256(expanded),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--definition", required=True, type=Path)
    parser.add_argument("--payload", required=True, type=Path)
    args = parser.parse_args()
    print(build(args.source, args.target, args.definition, args.payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
