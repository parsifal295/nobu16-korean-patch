#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class TextHit:
    file: str
    encoding: str
    offset: int
    length_chars: int
    length_bytes: int
    text: str


def is_allowed_wide_char(code: int) -> bool:
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


def cleanup_text(value: str) -> str:
    out = []
    for ch in value:
        if ch in "\t\n\r":
            out.append(ch)
            continue
        cat = unicodedata.category(ch)
        if cat.startswith("C"):
            continue
        out.append(ch)
    return "".join(out).strip()


def text_quality_ok(text: str, min_chars: int) -> bool:
    if len(text) < min_chars:
        return False
    meaningful = 0
    letters = 0
    for ch in text:
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
    return ratio >= 0.7 and letters >= 1


def scan_ascii(data: bytes, src: str, min_chars: int) -> Iterable[TextHit]:
    start = None
    for i, b in enumerate(data):
        if 0x20 <= b <= 0x7E or b in (0x09, 0x0A, 0x0D):
            if start is None:
                start = i
        else:
            if start is not None:
                chunk = data[start:i]
                if len(chunk) >= min_chars:
                    text = cleanup_text(chunk.decode("latin1", errors="ignore"))
                    if text_quality_ok(text, min_chars):
                        yield TextHit(src, "ascii", start, len(text), len(chunk), text)
                start = None
    if start is not None:
        chunk = data[start:]
        if len(chunk) >= min_chars:
            text = cleanup_text(chunk.decode("latin1", errors="ignore"))
            if text_quality_ok(text, min_chars):
                yield TextHit(src, "ascii", start, len(text), len(chunk), text)


def scan_utf16(data: bytes, src: str, min_chars: int) -> Iterable[TextHit]:
    size = len(data)
    for align in (0, 1):
        pos = align
        while pos + 1 < size:
            code = data[pos] | (data[pos + 1] << 8)
            if not is_allowed_wide_char(code):
                pos += 2
                continue

            start = pos
            chars = []
            while pos + 1 < size:
                code = data[pos] | (data[pos + 1] << 8)
                if not is_allowed_wide_char(code):
                    break
                chars.append(chr(code))
                pos += 2

            if len(chars) >= min_chars:
                raw = "".join(chars)
                text = cleanup_text(raw)
                if text_quality_ok(text, min_chars):
                    yield TextHit(src, f"utf16le_a{align}", start, len(text), len(chars) * 2, text)

            if pos == start:
                pos += 2


def dedupe_hits(hits: list[TextHit]) -> list[TextHit]:
    best: dict[tuple[str, int, str], TextHit] = {}
    for h in hits:
        key = (h.file, h.offset, h.text)
        prev = best.get(key)
        if prev is None or h.length_chars > prev.length_chars:
            best[key] = h
    ordered = sorted(best.values(), key=lambda x: (x.file, x.offset, x.encoding))
    return ordered


def write_csv(path: Path, hits: list[TextHit]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "encoding", "offset", "length_chars", "length_bytes", "text"])
        for h in hits:
            writer.writerow([h.file, h.encoding, h.offset, h.length_chars, h.length_bytes, h.text])


def write_summary(path: Path, hits: list[TextHit]) -> None:
    per_file: dict[str, dict[str, int]] = {}
    for h in hits:
        slot = per_file.setdefault(h.file, {"total": 0})
        slot["total"] += 1
        slot[h.encoding] = slot.get(h.encoding, 0) + 1

    payload = {
        "files": sorted(per_file.keys()),
        "total_hits": len(hits),
        "by_file": per_file,
        "sample": [asdict(h) for h in hits[:20]],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Extract string candidates from binary files.")
    p.add_argument("inputs", nargs="+", help="Input files")
    p.add_argument("--min-chars", type=int, default=4)
    p.add_argument("--out-csv", required=True)
    p.add_argument("--out-summary", required=True)
    args = p.parse_args()

    all_hits: list[TextHit] = []
    for fp in args.inputs:
        path = Path(fp)
        if not path.is_file():
            continue
        data = path.read_bytes()
        src = str(path)
        all_hits.extend(scan_ascii(data, src, args.min_chars))
        all_hits.extend(scan_utf16(data, src, args.min_chars))

    all_hits = dedupe_hits(all_hits)

    write_csv(Path(args.out_csv), all_hits)
    write_summary(Path(args.out_summary), all_hits)

    print(f"extracted {len(all_hits)} candidates")
    print(f"csv: {args.out_csv}")
    print(f"summary: {args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
