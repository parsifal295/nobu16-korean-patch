#!/usr/bin/env python3
"""Read-only integrity check for one MSGGAME literal.

The command deliberately reports only structure, script classes, and hashes;
it never prints or stores the commercial source text and never modifies a game
file.  It is useful for proving that an installed JP-route candidate actually
contains a Korean replacement at a captured runtime coordinate.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "workstreams" / "msggame"))

from msggame_format import iter_literals, parse_packed_msggame  # noqa: E402


HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
JAPANESE_RE = re.compile(r"[\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("block_id", type=int)
    parser.add_argument("record_id", type=int)
    parser.add_argument("literal_id", type=int)
    args = parser.parse_args()

    path = args.path.resolve()
    coordinate = (args.block_id, args.record_id, args.literal_id)
    archive = parse_packed_msggame(path.read_bytes()).archive
    literals = {
        (item.block_id, item.record_id, item.literal_id): item.text
        for item in iter_literals(archive)
    }
    if coordinate not in literals:
        print("coordinate_present=false")
        print(f"literal_count={len(literals)}")
        return 2
    text = literals[coordinate]
    print("coordinate_present=true")
    print(f"literal_count={len(literals)}")
    print(f"has_hangul={str(bool(HANGUL_RE.search(text))).lower()}")
    print(f"has_japanese_script={str(bool(JAPANESE_RE.search(text))).lower()}")
    print(f"utf16le_sha256={sha256(text.encode('utf-16-le'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
