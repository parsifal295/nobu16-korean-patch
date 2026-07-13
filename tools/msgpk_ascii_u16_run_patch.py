#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Entry:
    id: int
    file: str
    offset: int
    align: int
    allocated_bytes: int
    original_en: str
    translated_ko: str = ""
    status: str = "todo"
    notes: str = ""


PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[diuoxXfsc]")


def is_ascii_printable(b: int) -> bool:
    return 0x20 <= b <= 0x7E


def looks_english_run(text: str, min_chars: int, min_ratio: float) -> bool:
    if len(text) < min_chars:
        return False
    if not any(c.isalpha() for c in text):
        return False
    good = sum(c.isalnum() or c.isspace() or c in ".,:;!?-_/[](){}'\"&%+$*=<>|@#" for c in text)
    if good / max(1, len(text)) < min_ratio:
        return False
    return True


def scan_runs(
    data: bytes,
    input_file: Path,
    start: int,
    end: int,
    min_chars: int,
    min_ratio: float,
    aligns: tuple[int, ...],
) -> list[Entry]:
    out: list[Entry] = []

    for align in aligns:
        i = start + ((align - start) & 1)
        while i + 1 < end:
            if is_ascii_printable(data[i]) and data[i + 1] == 0x00:
                s = i
                chars: list[str] = []
                while i + 1 < end and is_ascii_printable(data[i]) and data[i + 1] == 0x00:
                    chars.append(chr(data[i]))
                    i += 2

                text = "".join(chars)
                if looks_english_run(text, min_chars=min_chars, min_ratio=min_ratio):
                    out.append(
                        Entry(
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

    # dedupe exact duplicate starts (prefer longer)
    best: dict[tuple[int, int], Entry] = {}
    for e in out:
        key = (e.offset, e.align)
        prev = best.get(key)
        if prev is None or e.allocated_bytes > prev.allocated_bytes:
            best[key] = e

    final = sorted(best.values(), key=lambda x: (x.offset, x.align))
    for idx, e in enumerate(final, 1):
        e.id = idx
    return final


def write_csv(path: Path, entries: list[Entry]) -> None:
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
                "translated_ko",
                "status",
                "notes",
            ]
        )
        for e in entries:
            w.writerow(
                [
                    e.id,
                    e.file,
                    f"0x{e.offset:X}",
                    e.offset,
                    e.align,
                    e.allocated_bytes,
                    e.allocated_bytes // 2,
                    e.original_en,
                    e.translated_ko,
                    e.status,
                    e.notes,
                ]
            )


def write_summary(path: Path, input_path: Path, entries: list[Entry], start: int, end: int) -> None:
    payload = {
        "input": str(input_path),
        "range": {"start": start, "end": end, "size": end - start},
        "count": len(entries),
        "sample": [asdict(e) for e in entries[:20]],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_entries(path: Path) -> list[Entry]:
    out: list[Entry] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            out.append(
                Entry(
                    id=int(row["id"]),
                    file=row.get("file", ""),
                    offset=int(row["offset"]),
                    align=int(row.get("align", "0")),
                    allocated_bytes=int(row["allocated_bytes"]),
                    original_en=row.get("original_en", ""),
                    translated_ko=row.get("translated_ko", ""),
                    status=row.get("status", "todo"),
                    notes=row.get("notes", ""),
                )
            )
    return out


def decode_run(data: bytes, offset: int, allocated_bytes: int) -> str:
    end = min(len(data), offset + allocated_bytes)
    out: list[str] = []
    for i in range(offset, end, 2):
        if i + 1 >= end:
            break
        lo = data[i]
        hi = data[i + 1]
        if hi != 0 or not is_ascii_printable(lo):
            break
        out.append(chr(lo))
    return "".join(out)


def encode_run_u16(text: str, ascii_only: bool) -> bytes:
    if ascii_only:
        out = bytearray()
        for ch in text:
            code = ord(ch)
            if not (0x20 <= code <= 0x7E):
                raise ValueError(f"non-ascii char in run text: {ch!r}")
            out.extend((code, 0x00))
        return bytes(out)
    return text.encode("utf-16-le")


def placeholder_list(text: str) -> list[str]:
    return PLACEHOLDER_RE.findall(text)


def validate(entries: list[Entry], exact_length: bool, ascii_only: bool) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    targets = 0

    for e in entries:
        t = e.translated_ko
        if not t.strip():
            continue
        targets += 1

        try:
            enc = encode_run_u16(t, ascii_only=ascii_only)
        except Exception as ex:
            errors.append(f"id={e.id} off=0x{e.offset:X}: {ex}")
            continue

        if exact_length and len(enc) != e.allocated_bytes:
            errors.append(
                f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} must equal allocated {e.allocated_bytes}"
            )
        elif len(enc) > e.allocated_bytes:
            errors.append(f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} > allocated {e.allocated_bytes}")

        src_ph = placeholder_list(e.original_en)
        dst_ph = placeholder_list(t)
        if src_ph != dst_ph:
            warnings.append(f"id={e.id} off=0x{e.offset:X}: placeholder mismatch src={src_ph} dst={dst_ph}")

    return errors, warnings, targets


def inject(
    src_bin: Path,
    entries: list[Entry],
    out_bin: Path,
    strict_original: bool,
    exact_length: bool,
    ascii_only: bool,
) -> tuple[int, int]:
    data = bytearray(src_bin.read_bytes())
    patched = 0
    skipped = 0

    for e in entries:
        t = e.translated_ko
        if not t.strip():
            skipped += 1
            continue

        if strict_original:
            cur = decode_run(data, e.offset, e.allocated_bytes)
            if cur != e.original_en:
                raise ValueError(f"id={e.id} off=0x{e.offset:X}: original mismatch current={cur!r} csv={e.original_en!r}")

        enc = encode_run_u16(t, ascii_only=ascii_only)
        if exact_length and len(enc) != e.allocated_bytes:
            raise ValueError(
                f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} must equal allocated {e.allocated_bytes}"
            )
        if len(enc) > e.allocated_bytes:
            raise ValueError(f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} > allocated {e.allocated_bytes}")

        if len(enc) < e.allocated_bytes:
            # Fill remainder with ASCII spaces to avoid stale tail text.
            pad_pairs = (e.allocated_bytes - len(enc)) // 2
            enc = enc + (b"\x20\x00" * pad_pairs)

        data[e.offset : e.offset + e.allocated_bytes] = enc
        patched += 1

    out_bin.parent.mkdir(parents=True, exist_ok=True)
    out_bin.write_bytes(data)
    return patched, skipped


def cmd_extract(args: argparse.Namespace) -> int:
    inp = Path(args.input)
    data = inp.read_bytes()
    start = max(0, args.start)
    end = len(data) if args.end is None else min(len(data), args.end)
    aligns = tuple(sorted(set(args.align)))

    entries = scan_runs(
        data=data,
        input_file=inp,
        start=start,
        end=end,
        min_chars=args.min_chars,
        min_ratio=args.min_ratio,
        aligns=aligns,
    )
    write_csv(Path(args.out_csv), entries)
    write_summary(Path(args.out_summary), inp, entries, start, end)

    print(f"extracted={len(entries)}")
    print(f"range=0x{start:X}~0x{end:X}")
    print(f"aligns={aligns}")
    print(f"out_csv={args.out_csv}")
    print(f"out_summary={args.out_summary}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    entries = load_entries(Path(args.input_csv))
    errors, warnings, targets = validate(
        entries,
        exact_length=not args.allow_shorter,
        ascii_only=args.ascii_only,
    )

    print(f"targets={targets}")
    print(f"errors={len(errors)}")
    print(f"warnings={len(warnings)}")
    for w in warnings[:50]:
        print("WARN", w)
    for e in errors[:50]:
        print("ERR", e)
    return 1 if errors else 0


def cmd_inject(args: argparse.Namespace) -> int:
    entries = load_entries(Path(args.input_csv))
    errors, warnings, targets = validate(
        entries,
        exact_length=not args.allow_shorter,
        ascii_only=args.ascii_only,
    )
    if errors:
        print("validation failed before inject")
        for e in errors[:50]:
            print("ERR", e)
        return 1
    for w in warnings[:50]:
        print("WARN", w)

    patched, skipped = inject(
        src_bin=Path(args.input_bin),
        entries=entries,
        out_bin=Path(args.output_bin),
        strict_original=not args.no_strict_original,
        exact_length=not args.allow_shorter,
        ascii_only=args.ascii_only,
    )
    print(f"targets={targets}")
    print(f"patched={patched}")
    print(f"skipped={skipped}")
    print(f"output={args.output_bin}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ASCII UTF-16LE run extractor/injector for msg binaries")
    sp = p.add_subparsers(dest="cmd", required=True)

    p_ex = sp.add_parser("extract")
    p_ex.add_argument("--input", required=True)
    p_ex.add_argument("--out-csv", required=True)
    p_ex.add_argument("--out-summary", required=True)
    p_ex.add_argument("--start", type=lambda x: int(x, 0), default=0)
    p_ex.add_argument("--end", type=lambda x: int(x, 0))
    p_ex.add_argument("--min-chars", type=int, default=4)
    p_ex.add_argument("--min-ratio", type=float, default=0.75)
    p_ex.add_argument("--align", action="append", type=int, default=[0, 1], help="0 or 1 (repeatable)")
    p_ex.set_defaults(func=cmd_extract)

    p_va = sp.add_parser("validate")
    p_va.add_argument("--input-csv", required=True)
    p_va.add_argument("--allow-shorter", action="store_true", default=False)
    p_va.add_argument("--ascii-only", action="store_true", default=False)
    p_va.set_defaults(func=cmd_validate)

    p_in = sp.add_parser("inject")
    p_in.add_argument("--input-bin", required=True)
    p_in.add_argument("--input-csv", required=True)
    p_in.add_argument("--output-bin", required=True)
    p_in.add_argument("--allow-shorter", action="store_true", default=False)
    p_in.add_argument("--no-strict-original", action="store_true")
    p_in.add_argument("--ascii-only", action="store_true", default=False)
    p_in.set_defaults(func=cmd_inject)

    return p


def main() -> int:
    p = build_parser()
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
