#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Seed:
    id: int
    file: str
    offset: int
    align: int
    allocated_bytes: int
    original_en: str


@dataclass
class ContextRow:
    id: int
    file: str
    offset: int
    align: int
    allocated_bytes: int
    original_en: str
    mixed_context_en: str
    translated_ko: str = ""
    status: str = "todo"
    notes: str = ""


def is_ascii_printable(b: int) -> bool:
    return 0x20 <= b <= 0x7E


def looks_seed(text: str, min_chars: int, min_ratio: float) -> bool:
    if len(text) < min_chars:
        return False
    if not any(c.isalpha() for c in text):
        return False
    good = sum(c.isalnum() or c.isspace() or c in ".,:;!?-_/[](){}'\"&%+$*=<>|@#" for c in text)
    if good / max(1, len(text)) < min_ratio:
        return False
    return True


def scan_ascii_u16_seeds(
    data: bytes,
    input_file: Path,
    start: int,
    end: int,
    min_chars: int,
    min_ratio: float,
    aligns: tuple[int, ...],
) -> list[Seed]:
    out: list[Seed] = []

    for align in aligns:
        i = start + ((align - start) & 1)
        while i + 1 < end:
            if is_ascii_printable(data[i]) and data[i + 1] == 0:
                s = i
                chars: list[str] = []
                while i + 1 < end and is_ascii_printable(data[i]) and data[i + 1] == 0:
                    chars.append(chr(data[i]))
                    i += 2

                text = "".join(chars)
                if looks_seed(text, min_chars=min_chars, min_ratio=min_ratio):
                    out.append(
                        Seed(
                            id=0,
                            file=str(input_file),
                            offset=s,
                            align=align,
                            allocated_bytes=len(chars) * 2,
                            original_en=text,
                        )
                    )
                continue

            i += 2

    best: dict[tuple[int, int], Seed] = {}
    for s in out:
        key = (s.offset, s.align)
        prev = best.get(key)
        if prev is None or s.allocated_bytes > prev.allocated_bytes:
            best[key] = s
    final = sorted(best.values(), key=lambda x: (x.offset, x.align))
    for idx, s in enumerate(final, 1):
        s.id = idx
    return final


def decode_mixed_context(
    data: bytes,
    start: int,
    max_scan_bytes: int,
    stop_bad: int,
    max_chars: int,
) -> str:
    i = start
    end = min(len(data), start + max_scan_bytes)
    out: list[str] = []
    bad = 0

    while i + 1 < end and len(out) < max_chars:
        lo = data[i]
        hi = data[i + 1]
        if is_ascii_printable(lo) and hi == 0:
            out.append(chr(lo))
            i += 2
            bad = 0
            continue
        i += 1
        bad += 1
        if bad >= stop_bad and out:
            break

    return "".join(out)


def write_csv(path: Path, rows: list[ContextRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "id",
                "file",
                "offset_hex",
                "offset",
                "align",
                "allocated_bytes",
                "max_chars_est",
                "original_en",
                "mixed_context_en",
                "translated_ko",
                "status",
                "notes",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.id,
                    r.file,
                    f"0x{r.offset:X}",
                    r.offset,
                    r.align,
                    r.allocated_bytes,
                    r.allocated_bytes // 2,
                    r.original_en,
                    r.mixed_context_en,
                    r.translated_ko,
                    r.status,
                    r.notes,
                ]
            )


def write_summary(path: Path, input_file: Path, rows: list[ContextRow], start: int, end: int) -> None:
    payload = {
        "input": str(input_file),
        "range": {"start": start, "end": end, "size": end - start},
        "count": len(rows),
        "sample": [asdict(r) for r in rows[:20]],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract msggame ASCII-u16 seeds + mixed context hints")
    p.add_argument("--input", required=True)
    p.add_argument("--out-csv", required=True)
    p.add_argument("--out-summary", required=True)
    p.add_argument("--start", type=lambda x: int(x, 0), default=0x7FFA)
    p.add_argument("--end", type=lambda x: int(x, 0))
    p.add_argument("--min-chars", type=int, default=4)
    p.add_argument("--min-ratio", type=float, default=0.75)
    p.add_argument("--align", action="append", type=int, default=[0, 1], help="0 or 1 (repeatable)")
    p.add_argument("--ctx-max-scan", type=int, default=512)
    p.add_argument("--ctx-stop-bad", type=int, default=16)
    p.add_argument("--ctx-max-chars", type=int, default=220)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    inp = Path(args.input)
    data = inp.read_bytes()
    start = max(0, args.start)
    end = len(data) if args.end is None else min(len(data), args.end)
    aligns = tuple(sorted(set(args.align)))

    seeds = scan_ascii_u16_seeds(
        data=data,
        input_file=inp,
        start=start,
        end=end,
        min_chars=args.min_chars,
        min_ratio=args.min_ratio,
        aligns=aligns,
    )

    rows: list[ContextRow] = []
    for s in seeds:
        ctx = decode_mixed_context(
            data=data,
            start=s.offset,
            max_scan_bytes=args.ctx_max_scan,
            stop_bad=args.ctx_stop_bad,
            max_chars=args.ctx_max_chars,
        )
        rows.append(
            ContextRow(
                id=s.id,
                file=s.file,
                offset=s.offset,
                align=s.align,
                allocated_bytes=s.allocated_bytes,
                original_en=s.original_en,
                mixed_context_en=ctx,
            )
        )

    write_csv(Path(args.out_csv), rows)
    write_summary(Path(args.out_summary), inp, rows, start, end)

    print(f"seeds={len(seeds)}")
    print(f"range=0x{start:X}~0x{end:X}")
    print(f"aligns={aligns}")
    print(f"out_csv={args.out_csv}")
    print(f"out_summary={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
