#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
from pathlib import Path

import nobu16_msg_model as model


XOR_KEY = bytes([0x97, 0x9E, 0x79, 0xE9])


def _stats(entries: list[model.Entry]) -> str:
    total = len(entries)
    translated = sum(1 for e in entries if e.translated_ko.strip())
    todo = total - translated
    files = len({e.file for e in entries})
    return f"files={files} total={total} translated={translated} todo={todo}"


def _print_stats(entries: list[model.Entry]) -> None:
    print(_stats(entries))


def _iter_list(entries: list[model.Entry], *, todo_only: bool, file_substr: str, limit: int) -> int:
    shown = 0
    q = file_substr.lower()
    for e in entries:
        if todo_only and e.translated_ko.strip():
            continue
        if q and q not in e.file.lower():
            continue
        print(
            f"{e.id:>4} {e.encoding:>10} off=0x{e.offset:06X} alloc={e.allocated_bytes:>4} "
            f"file={Path(e.file).name} src={e.original_en!r} ko={e.translated_ko!r}"
        )
        shown += 1
        if limit > 0 and shown >= limit:
            break
    return shown


def _entry_by_id(entries: list[model.Entry]) -> dict[int, model.Entry]:
    return {e.id: e for e in entries}


def _check_n15_like(data: bytes, start: int) -> tuple[bool, str]:
    size = len(data)
    if start >= size:
        return (False, f"start_offset out of range: 0x{start:X}")
    if start + 14 > size:
        return (False, "start+14 out of range")

    count = struct.unpack_from("<H", data, start)[0]
    ptr_off = start + 12
    ptr_end = ptr_off + count * 4
    if count == 0 or count > 200000:
        return (False, f"count not plausible: {count}")
    if ptr_end > size:
        return (False, f"pointer table out of range: count={count}")

    ptrs = [struct.unpack_from("<I", data, ptr_off + i * 4)[0] for i in range(count)]
    if any(ptrs[i] > ptrs[i + 1] for i in range(count - 1)):
        return (False, "pointers are not monotonic")
    data_start = start + 12 + count * 4
    if data_start + ptrs[-1] > size:
        return (False, "last pointer exceeds file size")
    return (True, f"count={count} ptr0={ptrs[0]} data_start=0x{data_start:X}")


def _xor_from_start(data: bytes, start: int) -> bytes:
    if start >= len(data):
        return data
    out = bytearray(data)
    for i in range(start, len(out)):
        out[i] ^= XOR_KEY[(i - start) % 4]
    return bytes(out)


def _probe_format(path: Path) -> int:
    data = path.read_bytes()
    size = len(data)
    if size < 8:
        print(f"file too small: {size}")
        return 1

    magic = data[:4].hex(" ")
    start = struct.unpack_from("<I", data, 4)[0]
    print(f"file={path}")
    print(f"size={size}")
    print(f"header[0:4]={magic}")
    print(f"u32_le@0x4(start_offset)=0x{start:X} ({start})")

    ok_raw, msg_raw = _check_n15_like(data, start)
    print(f"n15_like_raw={ok_raw} ({msg_raw})")

    dec = _xor_from_start(data, start)
    ok_dec, msg_dec = _check_n15_like(dec, start)
    print(f"n15_like_xor_once={ok_dec} ({msg_dec})")

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="NOBU16 message editor core CLI")
    sp = p.add_subparsers(dest="cmd", required=True)

    p_stats = sp.add_parser("stats")
    p_stats.add_argument("--csv", required=True)

    p_list = sp.add_parser("list")
    p_list.add_argument("--csv", required=True)
    p_list.add_argument("--todo-only", action="store_true", default=False)
    p_list.add_argument("--file-substr", default="")
    p_list.add_argument("--limit", type=int, default=30)

    p_set = sp.add_parser("set")
    p_set.add_argument("--csv", required=True)
    p_set.add_argument("--id", type=int, required=True)
    p_set.add_argument("--text", required=True)
    p_set.add_argument("--out-csv", required=True)
    p_set.add_argument("--ascii-only-run", action="store_true", default=False)

    p_clear = sp.add_parser("clear")
    p_clear.add_argument("--csv", required=True)
    p_clear.add_argument("--id", type=int, required=True)
    p_clear.add_argument("--out-csv", required=True)

    p_validate = sp.add_parser("validate")
    p_validate.add_argument("--csv", required=True)
    p_validate.add_argument("--allow-shorter", action="store_true", default=False)
    p_validate.add_argument("--ascii-only-run", action="store_true", default=False)

    p_inject_bin = sp.add_parser("inject-bin")
    p_inject_bin.add_argument("--csv", required=True)
    p_inject_bin.add_argument("--input-bin", required=True)
    p_inject_bin.add_argument("--output-bin", required=True)
    p_inject_bin.add_argument("--file-substr", default="")
    p_inject_bin.add_argument("--allow-shorter", action="store_true", default=False)
    p_inject_bin.add_argument("--ascii-only-run", action="store_true", default=False)
    p_inject_bin.add_argument("--no-strict-original", action="store_true", default=False)

    p_inject_tree = sp.add_parser("inject-tree")
    p_inject_tree.add_argument("--csv", required=True)
    p_inject_tree.add_argument("--src-root", required=True)
    p_inject_tree.add_argument("--out-root", required=True)
    p_inject_tree.add_argument("--allow-shorter", action="store_true", default=False)
    p_inject_tree.add_argument("--ascii-only-run", action="store_true", default=False)
    p_inject_tree.add_argument("--no-strict-original", action="store_true", default=False)

    p_probe = sp.add_parser("probe-format")
    p_probe.add_argument("--input-bin", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()

    if args.cmd == "probe-format":
        return _probe_format(Path(args.input_bin))

    cat = model.load_catalog(Path(args.csv))

    if args.cmd == "stats":
        _print_stats(cat.entries)
        return 0

    if args.cmd == "list":
        shown = _iter_list(
            cat.entries,
            todo_only=args.todo_only,
            file_substr=args.file_substr,
            limit=args.limit,
        )
        print(f"shown={shown}")
        return 0

    if args.cmd == "set":
        by_id = _entry_by_id(cat.entries)
        e = by_id.get(args.id)
        if e is None:
            raise ValueError(f"id not found: {args.id}")
        enc = model.encode_text(args.text, e.encoding, ascii_only_run=args.ascii_only_run)
        if len(enc) > e.allocated_bytes:
            raise ValueError(f"encoded bytes {len(enc)} > allocated {e.allocated_bytes}")
        e.translated_ko = args.text
        e.status = "translated" if args.text.strip() else "todo"
        model.save_catalog(Path(args.out_csv), cat)
        print(f"set id={e.id} bytes={len(enc)}/{e.allocated_bytes}")
        print(_stats(cat.entries))
        return 0

    if args.cmd == "clear":
        by_id = _entry_by_id(cat.entries)
        e = by_id.get(args.id)
        if e is None:
            raise ValueError(f"id not found: {args.id}")
        e.translated_ko = ""
        e.status = "todo"
        model.save_catalog(Path(args.out_csv), cat)
        print(f"cleared id={e.id}")
        print(_stats(cat.entries))
        return 0

    if args.cmd == "validate":
        errors, warnings, targets = model.validate_entries(
            cat.entries,
            exact_length=not args.allow_shorter,
            ascii_only_run=args.ascii_only_run,
        )
        print(f"targets={targets} errors={len(errors)} warnings={len(warnings)}")
        for w in warnings[:20]:
            print("WARN", w)
        for e in errors[:20]:
            print("ERR", e)
        return 1 if errors else 0

    if args.cmd == "inject-bin":
        entries = cat.entries
        if args.file_substr:
            q = args.file_substr.lower()
            entries = [e for e in entries if q in e.file.lower()]
            if not entries:
                raise ValueError(f"no rows matched --file-substr {args.file_substr!r}")
        files = {e.file for e in entries if e.translated_ko.strip()}
        if len(files) > 1:
            raise ValueError(
                "inject-bin received multiple files. use --file-substr to narrow rows or use inject-tree."
            )
        errors, warnings, targets = model.validate_entries(
            entries,
            exact_length=not args.allow_shorter,
            ascii_only_run=args.ascii_only_run,
        )
        if errors:
            print(f"validation failed: {len(errors)} errors")
            for e in errors[:20]:
                print("ERR", e)
            return 1
        for w in warnings[:20]:
            print("WARN", w)
        patched, skipped = model.inject_single_file(
            src_bin=Path(args.input_bin),
            out_bin=Path(args.output_bin),
            entries=entries,
            strict_original=not args.no_strict_original,
            exact_length=not args.allow_shorter,
            ascii_only_run=args.ascii_only_run,
        )
        print(f"targets={targets} patched={patched} skipped={skipped}")
        print(f"output={args.output_bin}")
        return 0

    if args.cmd == "inject-tree":
        errors, warnings, targets = model.validate_entries(
            cat.entries,
            exact_length=not args.allow_shorter,
            ascii_only_run=args.ascii_only_run,
        )
        if errors:
            print(f"validation failed: {len(errors)} errors")
            for e in errors[:20]:
                print("ERR", e)
            return 1
        for w in warnings[:20]:
            print("WARN", w)
        files, patched, skipped = model.inject_tree(
            src_root=Path(args.src_root).resolve(),
            out_root=Path(args.out_root).resolve(),
            entries=cat.entries,
            strict_original=not args.no_strict_original,
            exact_length=not args.allow_shorter,
            ascii_only_run=args.ascii_only_run,
        )
        print(f"targets={targets} files={files} patched={patched} skipped={skipped}")
        print(f"out_root={Path(args.out_root).resolve()}")
        return 0

    raise ValueError(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
