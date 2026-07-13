#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[diuoxXfsc]")


@dataclass
class Entry:
    id: int
    offset: int
    allocated_bytes: int
    original_en: str
    translated_ko: str = ""
    status: str = "todo"
    notes: str = ""


def is_allowed_ascii_char(code: int) -> bool:
    # printable ascii + tabs/newlines for safety
    return code in (0x09, 0x0A, 0x0D) or (0x20 <= code <= 0x7E)


def decode_utf16le_z(data: bytes, offset: int, max_bytes: int | None = None) -> tuple[str, int, bool]:
    end = len(data) if max_bytes is None else min(len(data), offset + max_bytes)
    pos = offset
    chars: list[str] = []

    while pos + 1 < end:
        code = data[pos] | (data[pos + 1] << 8)
        if code == 0:
            return ("".join(chars), (pos + 2) - offset, True)
        if not is_allowed_ascii_char(code):
            return ("".join(chars), pos - offset, False)
        chars.append(chr(code))
        pos += 2

    return ("".join(chars), pos - offset, False)


def looks_name_or_ui(text: str, min_chars: int) -> bool:
    if len(text) < min_chars:
        return False
    if not any(c.isalpha() for c in text):
        return False
    if re.fullmatch(r"\s*", text):
        return False
    return True


def extract_entries(data: bytes, start: int, end: int, min_chars: int) -> list[Entry]:
    out: list[Entry] = []

    i = start
    if i % 2:
        i += 1
    if end % 2:
        end -= 1

    while i + 1 < end:
        s = i
        text, used, terminated = decode_utf16le_z(data, s, max_bytes=end - s)
        if terminated and used >= 4 and looks_name_or_ui(text, min_chars):
            out.append(
                Entry(
                    id=0,
                    offset=s,
                    allocated_bytes=used,
                    original_en=text,
                )
            )
            i = s + used
            continue
        i = s + 2

    for idx, e in enumerate(out, 1):
        e.id = idx
    return out


def write_csv(path: Path, entries: list[Entry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "id",
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
        for e in entries:
            w.writerow(
                [
                    e.id,
                    f"0x{e.offset:X}",
                    e.offset,
                    e.allocated_bytes,
                    max(0, (e.allocated_bytes - 2) // 2),
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
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            out.append(
                Entry(
                    id=int(row["id"]),
                    offset=int(row["offset"]),
                    allocated_bytes=int(row["allocated_bytes"]),
                    original_en=row.get("original_en", ""),
                    translated_ko=row.get("translated_ko", ""),
                    status=row.get("status", "todo"),
                    notes=row.get("notes", ""),
                )
            )
    return out


def placeholder_list(text: str) -> list[str]:
    return PLACEHOLDER_RE.findall(text)


def validate(entries: list[Entry]) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    targets = 0

    for e in entries:
        t = e.translated_ko.strip()
        if not t:
            continue
        targets += 1

        enc = t.encode("utf-16-le") + b"\x00\x00"
        if len(enc) > e.allocated_bytes:
            errors.append(
                f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} > allocated {e.allocated_bytes}"
            )

        src_ph = placeholder_list(e.original_en)
        dst_ph = placeholder_list(t)
        if src_ph != dst_ph:
            warnings.append(
                f"id={e.id} off=0x{e.offset:X}: placeholder mismatch src={src_ph} dst={dst_ph}"
            )

    return errors, warnings, targets


def inject(src_bin: Path, entries: list[Entry], out_bin: Path, strict_original: bool) -> tuple[int, int]:
    data = bytearray(src_bin.read_bytes())
    patched = 0
    skipped = 0

    for e in entries:
        t = e.translated_ko.strip()
        if not t:
            skipped += 1
            continue

        if strict_original:
            cur, used, term = decode_utf16le_z(data, e.offset, max_bytes=e.allocated_bytes)
            if not term:
                raise ValueError(f"id={e.id} off=0x{e.offset:X}: no terminator inside allocation")
            if cur != e.original_en:
                raise ValueError(
                    f"id={e.id} off=0x{e.offset:X}: original mismatch current={cur!r} csv={e.original_en!r}"
                )
            if used > e.allocated_bytes:
                raise ValueError(f"id={e.id} off=0x{e.offset:X}: used {used} > alloc {e.allocated_bytes}")

        enc = t.encode("utf-16-le") + b"\x00\x00"
        if len(enc) > e.allocated_bytes:
            raise ValueError(
                f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} > allocated {e.allocated_bytes}"
            )

        patch = enc + (b"\x00" * (e.allocated_bytes - len(enc)))
        data[e.offset : e.offset + e.allocated_bytes] = patch
        patched += 1

    out_bin.parent.mkdir(parents=True, exist_ok=True)
    out_bin.write_bytes(data)
    return patched, skipped


def cmd_extract(args: argparse.Namespace) -> int:
    inp = Path(args.input)
    data = inp.read_bytes()
    start = max(0, args.start)
    end = len(data) if args.end is None else min(len(data), args.end)

    entries = extract_entries(data, start, end, args.min_chars)
    write_csv(Path(args.out_csv), entries)
    write_summary(Path(args.out_summary), inp, entries, start, end)

    print(f"extracted={len(entries)}")
    print(f"out_csv={args.out_csv}")
    print(f"out_summary={args.out_summary}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    entries = load_entries(Path(args.input_csv))
    errors, warnings, targets = validate(entries)

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
    errors, warnings, targets = validate(entries)

    if errors:
        print("validation failed before inject")
        for e in errors[:50]:
            print("ERR", e)
        return 1

    for w in warnings[:50]:
        print("WARN", w)

    patched, skipped = inject(
        Path(args.input_bin),
        entries,
        Path(args.output_bin),
        strict_original=not args.no_strict_original,
    )

    print(f"targets={targets}")
    print(f"patched={patched}")
    print(f"skipped={skipped}")
    print(f"output={args.output_bin}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="UTF-16LE name/ui table patch tool")
    sp = p.add_subparsers(dest="cmd", required=True)

    p_ex = sp.add_parser("extract")
    p_ex.add_argument("--input", required=True)
    p_ex.add_argument("--out-csv", required=True)
    p_ex.add_argument("--out-summary", required=True)
    p_ex.add_argument("--start", type=int, default=0)
    p_ex.add_argument("--end", type=int)
    p_ex.add_argument("--min-chars", type=int, default=3)
    p_ex.set_defaults(func=cmd_extract)

    p_va = sp.add_parser("validate")
    p_va.add_argument("--input-csv", required=True)
    p_va.set_defaults(func=cmd_validate)

    p_in = sp.add_parser("inject")
    p_in.add_argument("--input-bin", required=True)
    p_in.add_argument("--input-csv", required=True)
    p_in.add_argument("--output-bin", required=True)
    p_in.add_argument("--no-strict-original", action="store_true")
    p_in.set_defaults(func=cmd_inject)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
