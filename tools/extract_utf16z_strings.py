#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Hit:
    file: str
    encoding: str
    offset: int
    length_chars: int
    text: str


def is_reasonable_char(code: int) -> bool:
    if code in (0x09, 0x0A, 0x0D):
        return True
    if 0x20 <= code <= 0x7E:
        return True
    if 0x00A1 <= code <= 0x024F:
        return True
    if 0x3000 <= code <= 0x303F:
        return True
    if 0x3040 <= code <= 0x30FF:
        return True
    if 0x3400 <= code <= 0x4DBF:
        return True
    if 0x4E00 <= code <= 0x9FFF:
        return True
    if 0xAC00 <= code <= 0xD7A3:
        return True
    if 0xFF01 <= code <= 0xFFEE:
        return True
    return False


def cleanup(s: str) -> str:
    out = []
    for ch in s:
        if ch in "\t\n\r":
            out.append(ch)
            continue
        cat = unicodedata.category(ch)
        if cat.startswith("C"):
            continue
        out.append(ch)
    return "".join(out).strip()


def quality_ok(text: str, min_chars: int) -> bool:
    if len(text) < min_chars:
        return False
    meaningful = 0
    letters = 0
    ascii_cnt = 0
    for ch in text:
        if ord(ch) < 128:
            ascii_cnt += 1
        if ch in "\t\n\r ":
            meaningful += 1
            continue
        cat = unicodedata.category(ch)
        if cat[0] in ("L", "N"):
            meaningful += 1
            if cat[0] == "L":
                letters += 1
            continue
        if ch in ".,:;!?+-_/[](){}<>\"'@#$%^&*~`|=\\":
            meaningful += 1

    ratio = meaningful / len(text)
    ascii_ratio = ascii_cnt / len(text)

    # keep either mostly ASCII EN strings or non-ASCII text with enough letters
    return ratio >= 0.8 and letters >= 1 and (ascii_ratio >= 0.6 or ascii_ratio <= 0.1)


def decode_code_unit(data: bytes, pos: int, endian: str) -> int:
    if endian == "le":
        return data[pos] | (data[pos + 1] << 8)
    return (data[pos] << 8) | data[pos + 1]


def extract_utf16z(path: Path, min_chars: int, endian: str) -> list[Hit]:
    data = path.read_bytes()
    n = len(data)
    i = 0
    hits: list[Hit] = []

    while i + 1 < n:
        if i % 2 != 0:
            i += 1
            continue

        start = i
        chars = []
        pos = i
        terminated = False

        while pos + 1 < n:
            code = decode_code_unit(data, pos, endian)
            if code == 0:
                terminated = True
                pos += 2
                break
            if not is_reasonable_char(code):
                break
            chars.append(chr(code))
            pos += 2

        if terminated and len(chars) >= min_chars:
            raw = "".join(chars)
            text = cleanup(raw)
            if quality_ok(text, min_chars):
                enc = "utf16le_z" if endian == "le" else "utf16be_z"
                hits.append(Hit(str(path), enc, start, len(text), text))
                i = pos
                continue

        i = start + 2

    return hits


def dedupe(hits: list[Hit]) -> list[Hit]:
    best: dict[tuple[str, int], Hit] = {}

    def score(h: Hit) -> tuple[float, int]:
        ascii_ratio = sum(ord(c) < 128 for c in h.text) / max(1, len(h.text))
        return (ascii_ratio, h.length_chars)

    for h in hits:
        key = (h.file, h.offset)
        old = best.get(key)
        if old is None or score(h) > score(old):
            best[key] = h

    return sorted(best.values(), key=lambda x: (x.file, x.offset))


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract UTF-16LE null-terminated strings")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--min-chars", type=int, default=4)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-summary", required=True)
    args = ap.parse_args()

    hits: list[Hit] = []
    for fp in args.inputs:
        p = Path(fp)
        if p.exists():
            hits.extend(extract_utf16z(p, args.min_chars, "le"))
            hits.extend(extract_utf16z(p, args.min_chars, "be"))

    hits = dedupe(hits)

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "encoding", "offset", "length_chars", "length_bytes", "text"])
        for h in hits:
            w.writerow([h.file, h.encoding, h.offset, h.length_chars, h.length_chars * 2, h.text])

    by_file: dict[str, int] = {}
    for h in hits:
        by_file[h.file] = by_file.get(h.file, 0) + 1

    out_summary = Path(args.out_summary)
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    out_summary.write_text(
        json.dumps(
            {
                "total_hits": len(hits),
                "by_file": by_file,
                "sample": [asdict(h) for h in hits[:20]],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"extracted {len(hits)}")
    print(f"csv: {out_csv}")
    print(f"summary: {out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
