#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def encode_text(text: str, enc: str) -> bytes:
    if enc == "utf16le":
        return text.encode("utf-16-le") + b"\x00\x00"
    if enc == "utf16be":
        return text.encode("utf-16-be") + b"\x00\x00"
    if enc == "utf16le_run":
        return text.encode("utf-16-le")
    raise ValueError(f"unknown encoding: {enc}")


def decode_current_terminated(data: bytes, offset: int, alloc: int, enc: str) -> tuple[str, bool]:
    end = min(len(data), offset + alloc)
    pos = offset
    chars: list[str] = []

    while pos + 1 < end:
        if enc == "utf16le":
            code = data[pos] | (data[pos + 1] << 8)
        else:
            code = (data[pos] << 8) | data[pos + 1]

        if code == 0:
            return ("".join(chars), True)

        try:
            chars.append(chr(code))
        except ValueError:
            return ("".join(chars), False)
        pos += 2

    return ("".join(chars), False)


def decode_current_run(data: bytes, offset: int, alloc: int, enc: str) -> str:
    end = min(len(data), offset + alloc)
    chunk = bytes(data[offset:end])
    if len(chunk) % 2:
        raise ValueError(f"odd-sized run chunk: {len(chunk)}")
    if enc != "utf16le_run":
        raise ValueError(f"unsupported run encoding: {enc}")
    return chunk.decode("utf-16-le", errors="strict")


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply master translation catalog to bin files")
    ap.add_argument("--catalog-csv", required=True)
    ap.add_argument("--src-root", required=True, help="Root dir for source files")
    ap.add_argument("--out-root", required=True, help="Root dir for patched output tree")
    ap.add_argument("--strict-original", action="store_true", default=False)
    args = ap.parse_args()

    src_root = Path(args.src_root).resolve()
    out_root = Path(args.out_root).resolve()
    rows_by_file: dict[Path, list[dict[str, str]]] = defaultdict(list)

    with Path(args.catalog_csv).open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            tr_raw = row.get("translated_ko", "")
            if not tr_raw.strip():
                continue
            file_path = Path(row["file"]).resolve()
            rows_by_file[file_path].append(row)

    total_targets = 0
    total_patched = 0

    for file_path, rows in sorted(rows_by_file.items(), key=lambda x: str(x[0])):
        if not file_path.exists():
            print(f"WARN missing source file: {file_path}")
            continue

        data = bytearray(file_path.read_bytes())
        patched = 0

        for row in rows:
            total_targets += 1
            off = int(row["offset"])
            alloc = int(row["allocated_bytes"])
            enc = row["encoding"]
            en = row.get("original_en", "")
            ko = row.get("translated_ko", "")

            enc_bytes = encode_text(ko, enc)
            if len(enc_bytes) > alloc:
                raise ValueError(
                    f"{file_path} off=0x{off:X}: encoded {len(enc_bytes)} > allocated {alloc}"
                )

            if args.strict_original:
                if enc == "utf16le_run":
                    cur = decode_current_run(data, off, alloc, enc)
                    if cur != en:
                        raise ValueError(
                            f"{file_path} off=0x{off:X}: run original mismatch current={cur!r} csv={en!r}"
                        )
                else:
                    cur, term = decode_current_terminated(data, off, alloc, enc)
                    if not term:
                        raise ValueError(
                            f"{file_path} off=0x{off:X}: current text has no terminator in allocation"
                        )
                    if cur != en:
                        raise ValueError(
                            f"{file_path} off=0x{off:X}: original mismatch current={cur!r} csv={en!r}"
                        )

            if enc == "utf16le_run" and len(enc_bytes) < alloc:
                pad_pairs = (alloc - len(enc_bytes)) // 2
                patch = enc_bytes + (b"\x20\x00" * pad_pairs)
            else:
                patch = enc_bytes + (b"\x00" * (alloc - len(enc_bytes)))
            data[off : off + alloc] = patch
            patched += 1

        rel = file_path.relative_to(src_root) if file_path.is_relative_to(src_root) else Path(file_path.name)
        out_path = out_root / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)

        total_patched += patched
        print(f"patched {patched:4d} -> {out_path}")

    print(f"targets={total_targets}")
    print(f"patched={total_patched}")
    print(f"out_root={out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
