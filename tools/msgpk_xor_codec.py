#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
from pathlib import Path

# From legacy NOBU msg editor (Form5): repeating 4-byte XOR keys.
XOR_KEYS = (0x97, 0x9E, 0x79, 0xE9)


def transform_payload(data: bytearray, start_offset: int, phase: int = 0) -> None:
    if start_offset < 0 or start_offset > len(data):
        raise ValueError(f"invalid start_offset={start_offset}")
    for i in range(start_offset, len(data)):
        data[i] ^= XOR_KEYS[(phase + (i - start_offset)) & 3]


def auto_start_offset(data: bytes) -> int:
    if len(data) < 8:
        raise ValueError("input too small for auto start offset")
    return struct.unpack_from("<I", data, 4)[0]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MSG_PK xor transform (encrypt/decrypt are identical)")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument(
        "--start-offset",
        type=lambda x: int(x, 0),
        help="Transform start offset. Default: read LE u32 at file+0x4",
    )
    p.add_argument("--phase", type=int, default=0, help="XOR phase (0..3), default=0")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    inp = Path(args.input)
    out = Path(args.output)
    data = bytearray(inp.read_bytes())

    start = auto_start_offset(data) if args.start_offset is None else args.start_offset
    phase = args.phase & 3
    transform_payload(data, start, phase=phase)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)

    print(f"input={inp}")
    print(f"output={out}")
    print(f"size={len(data)}")
    print(f"start_offset=0x{start:X} ({start})")
    print(f"phase={phase}")
    print("mode=xor-transform")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
