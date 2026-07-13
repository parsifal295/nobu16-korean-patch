#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Hit:
    file: str
    encoding: str  # utf16le or utf16be
    offset: int
    allocated_bytes: int
    original_en: str


def decode_code_unit(data: bytes, pos: int, enc: str) -> int:
    if enc == "utf16le":
        return data[pos] | (data[pos + 1] << 8)
    return (data[pos] << 8) | data[pos + 1]


def is_ascii_printable(code: int) -> bool:
    return code in (0x09, 0x0A, 0x0D) or (0x20 <= code <= 0x7E)


def looks_english(s: str, min_chars: int) -> bool:
    if len(s) < min_chars:
        return False
    if not any(c.isalpha() for c in s):
        return False
    # remove clearly broken garbage
    good = sum(c.isalnum() or c.isspace() or c in ".,:;!?-_/[](){}'\"&%+$*=<>|@#" for c in s)
    if good / max(1, len(s)) < 0.7:
        return False
    return True


def scan_file(path: Path, min_chars: int) -> list[Hit]:
    b = path.read_bytes()
    n = len(b)
    out: list[Hit] = []

    for enc in ("utf16le", "utf16be"):
        i = 0
        while i + 1 < n:
            if i % 2:
                i += 1
                continue

            start = i
            pos = i
            chars: list[str] = []
            terminated = False

            while pos + 1 < n:
                code = decode_code_unit(b, pos, enc)
                if code == 0:
                    terminated = True
                    pos += 2
                    break
                if not is_ascii_printable(code):
                    break
                chars.append(chr(code))
                pos += 2

            if terminated and chars:
                # Keep leading/trailing spaces to preserve exact strict-original matching.
                text = "".join(chars)
                alloc = pos - start
                if looks_english(text, min_chars):
                    out.append(Hit(str(path), enc, start, alloc, text))
                    i = pos
                    continue

            i = start + 2

    # dedupe by (file, offset), prefer hit with higher ascii ratio then longer text
    best: dict[tuple[str, int], Hit] = {}

    def score(h: Hit) -> tuple[float, int]:
        ascii_ratio = sum(ord(c) < 128 for c in h.original_en) / max(1, len(h.original_en))
        return (ascii_ratio, len(h.original_en))

    for h in out:
        k = (h.file, h.offset)
        prev = best.get(k)
        if prev is None or score(h) > score(prev):
            best[k] = h

    return sorted(best.values(), key=lambda x: (x.file, x.offset))


def load_existing(path: Path) -> dict[tuple[str, int], dict[str, str]]:
    if not path.exists():
        return {}
    out: dict[tuple[str, int], dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                key = (row["file"], int(row["offset"]))
            except Exception:
                continue
            out[key] = {
                "translated_ko": row.get("translated_ko", ""),
                "status": row.get("status", "todo"),
                "notes": row.get("notes", ""),
            }
    return out


def write_catalog(path: Path, hits: list[Hit], existing: dict[tuple[str, int], dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "id",
                "file",
                "encoding",
                "offset_hex",
                "offset",
                "allocated_bytes",
                "max_chars_est",
                "original_en",
                "translated_ko",
                "status",
                "notes",
            ]
        )
        for idx, h in enumerate(hits, 1):
            key = (h.file, h.offset)
            ex = existing.get(key, {})
            tr = ex.get("translated_ko", "")
            st = ex.get("status", "todo" if not tr else "done")
            nt = ex.get("notes", "")
            w.writerow(
                [
                    idx,
                    h.file,
                    h.encoding,
                    f"0x{h.offset:X}",
                    h.offset,
                    h.allocated_bytes,
                    max(0, (h.allocated_bytes - 2) // 2),
                    h.original_en,
                    tr,
                    st,
                    nt,
                ]
            )


def main() -> int:
    ap = argparse.ArgumentParser(description="Build master translation catalog from msg binaries")
    ap.add_argument("inputs", nargs="+", help="Input .bin files")
    ap.add_argument("--min-chars", type=int, default=2)
    ap.add_argument("--existing-csv", help="Existing catalog to merge translated_ko/status/notes")
    ap.add_argument("--out-csv", required=True)
    args = ap.parse_args()

    hits: list[Hit] = []
    for fp in args.inputs:
        p = Path(fp)
        if not p.is_file():
            continue
        hits.extend(scan_file(p, args.min_chars))

    # global dedupe by (file, offset)
    dedup: dict[tuple[str, int], Hit] = {}
    for h in hits:
        dedup[(h.file, h.offset)] = h
    final_hits = sorted(dedup.values(), key=lambda x: (x.file, x.offset))

    existing = load_existing(Path(args.existing_csv)) if args.existing_csv else {}
    write_catalog(Path(args.out_csv), final_hits, existing)

    print(f"entries={len(final_hits)}")
    print(f"out={args.out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
