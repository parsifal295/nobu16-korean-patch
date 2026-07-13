#!/usr/bin/env python3
from __future__ import annotations

import argparse
import cmd
import shlex
from pathlib import Path

import msgpk_ascii_u16_run_patch as core


def save_csv(path: Path, entries: list[core.Entry]) -> None:
    core.write_csv(path, entries)


def entry_by_id(entries: list[core.Entry]) -> dict[int, core.Entry]:
    return {e.id: e for e in entries}


def print_entry(e: core.Entry) -> None:
    print(f"id={e.id} off=0x{e.offset:X} alloc={e.allocated_bytes} align={e.align}")
    print(f"original : {e.original_en}")
    print(f"translated: {e.translated_ko}")
    print(f"status   : {e.status}")
    print(f"notes    : {e.notes}")


def stats(entries: list[core.Entry]) -> None:
    total = len(entries)
    translated = sum(1 for e in entries if e.translated_ko.strip())
    todo = total - translated
    print(f"total={total} translated={translated} todo={todo}")


def print_list(entries: list[core.Entry], only_todo: bool, limit: int) -> None:
    shown = 0
    for e in entries:
        if only_todo and e.translated_ko.strip():
            continue
        print(
            f"{e.id:>3} 0x{e.offset:06X} alloc={e.allocated_bytes:>3} "
            f"src={e.original_en!r} ko={e.translated_ko!r}"
        )
        shown += 1
        if limit > 0 and shown >= limit:
            break
    print(f"shown={shown}")


def set_translation(entries: list[core.Entry], idx: int, text: str, ascii_only: bool) -> None:
    by_id = entry_by_id(entries)
    if idx not in by_id:
        raise KeyError(f"id not found: {idx}")
    e = by_id[idx]
    enc = core.encode_run_u16(text, ascii_only=ascii_only)
    if len(enc) > e.allocated_bytes:
        raise ValueError(f"encoded bytes {len(enc)} > allocated {e.allocated_bytes}")
    e.translated_ko = text
    e.status = "translated" if text.strip() else "todo"
    print(f"set id={idx} bytes={len(enc)}/{e.allocated_bytes}")


def clear_translation(entries: list[core.Entry], idx: int) -> None:
    by_id = entry_by_id(entries)
    if idx not in by_id:
        raise KeyError(f"id not found: {idx}")
    e = by_id[idx]
    e.translated_ko = ""
    e.status = "todo"
    print(f"cleared id={idx}")


def run_validate(entries: list[core.Entry], allow_shorter: bool, ascii_only: bool) -> int:
    errors, warnings, targets = core.validate(
        entries=entries, exact_length=not allow_shorter, ascii_only=ascii_only
    )
    print(f"targets={targets} errors={len(errors)} warnings={len(warnings)}")
    for w in warnings[:20]:
        print("WARN", w)
    for e in errors[:20]:
        print("ERR", e)
    return 1 if errors else 0


def run_inject(
    entries: list[core.Entry],
    input_bin: Path,
    output_bin: Path,
    allow_shorter: bool,
    ascii_only: bool,
    no_strict_original: bool,
) -> int:
    errors, warnings, targets = core.validate(
        entries=entries, exact_length=not allow_shorter, ascii_only=ascii_only
    )
    if errors:
        print(f"validation failed: {len(errors)} errors")
        for e in errors[:20]:
            print("ERR", e)
        return 1
    for w in warnings[:20]:
        print("WARN", w)

    patched, skipped = core.inject(
        src_bin=input_bin,
        entries=entries,
        out_bin=output_bin,
        strict_original=not no_strict_original,
        exact_length=not allow_shorter,
        ascii_only=ascii_only,
    )
    print(f"targets={targets} patched={patched} skipped={skipped}")
    print(f"output={output_bin}")
    return 0


class MsgEditShell(cmd.Cmd):
    intro = "msgedit REPL. type 'help' for commands."
    prompt = "(msgedit) "

    def __init__(self, csv_path: Path, allow_shorter: bool, ascii_only: bool) -> None:
        super().__init__()
        self.csv_path = csv_path
        self.entries = core.load_entries(csv_path)
        self.allow_shorter = allow_shorter
        self.ascii_only = ascii_only

    def do_stats(self, arg: str) -> None:
        stats(self.entries)

    def do_list(self, arg: str) -> None:
        toks = shlex.split(arg)
        only_todo = False
        limit = 20
        for t in toks:
            if t == "todo":
                only_todo = True
            else:
                limit = int(t)
        print_list(self.entries, only_todo=only_todo, limit=limit)

    def do_find(self, arg: str) -> None:
        q = arg.strip().lower()
        if not q:
            print("usage: find <text>")
            return
        shown = 0
        for e in self.entries:
            if q in e.original_en.lower() or q in e.translated_ko.lower():
                print(
                    f"{e.id:>3} 0x{e.offset:06X} src={e.original_en!r} "
                    f"ko={e.translated_ko!r}"
                )
                shown += 1
        print(f"matches={shown}")

    def do_show(self, arg: str) -> None:
        toks = shlex.split(arg)
        if len(toks) != 1:
            print("usage: show <id>")
            return
        idx = int(toks[0])
        by_id = entry_by_id(self.entries)
        if idx not in by_id:
            print(f"id not found: {idx}")
            return
        print_entry(by_id[idx])

    def do_set(self, arg: str) -> None:
        toks = shlex.split(arg)
        if len(toks) < 2:
            print("usage: set <id> <translated text>")
            return
        idx = int(toks[0])
        text = " ".join(toks[1:])
        try:
            set_translation(self.entries, idx=idx, text=text, ascii_only=self.ascii_only)
        except Exception as ex:
            print(f"ERR {ex}")

    def do_clear(self, arg: str) -> None:
        toks = shlex.split(arg)
        if len(toks) != 1:
            print("usage: clear <id>")
            return
        idx = int(toks[0])
        try:
            clear_translation(self.entries, idx=idx)
        except Exception as ex:
            print(f"ERR {ex}")

    def do_note(self, arg: str) -> None:
        toks = shlex.split(arg)
        if len(toks) < 2:
            print("usage: note <id> <text>")
            return
        idx = int(toks[0])
        by_id = entry_by_id(self.entries)
        if idx not in by_id:
            print(f"id not found: {idx}")
            return
        by_id[idx].notes = " ".join(toks[1:])
        print(f"note updated id={idx}")

    def do_validate(self, arg: str) -> None:
        run_validate(self.entries, allow_shorter=self.allow_shorter, ascii_only=self.ascii_only)

    def do_inject(self, arg: str) -> None:
        toks = shlex.split(arg)
        if len(toks) != 2:
            print("usage: inject <input_bin> <output_bin>")
            return
        rc = run_inject(
            self.entries,
            input_bin=Path(toks[0]),
            output_bin=Path(toks[1]),
            allow_shorter=self.allow_shorter,
            ascii_only=self.ascii_only,
            no_strict_original=False,
        )
        if rc != 0:
            print("inject failed")

    def do_save(self, arg: str) -> None:
        toks = shlex.split(arg)
        out = self.csv_path if not toks else Path(toks[0])
        save_csv(out, self.entries)
        print(f"saved {out}")

    def do_exit(self, arg: str) -> bool:
        return True

    def do_quit(self, arg: str) -> bool:
        return True

    def do_EOF(self, arg: str) -> bool:
        print()
        return True


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="msgedit-style tool for msggame run CSV editing")
    sp = p.add_subparsers(dest="cmd", required=True)

    p_stats = sp.add_parser("stats")
    p_stats.add_argument("--csv", required=True)

    p_list = sp.add_parser("list")
    p_list.add_argument("--csv", required=True)
    p_list.add_argument("--todo-only", action="store_true", default=False)
    p_list.add_argument("--limit", type=int, default=30)

    p_set = sp.add_parser("set")
    p_set.add_argument("--csv", required=True)
    p_set.add_argument("--id", type=int, required=True)
    p_set.add_argument("--text", required=True)
    p_set.add_argument("--out-csv", required=True)
    p_set.add_argument("--ascii-only", action="store_true", default=False)

    p_clear = sp.add_parser("clear")
    p_clear.add_argument("--csv", required=True)
    p_clear.add_argument("--id", type=int, required=True)
    p_clear.add_argument("--out-csv", required=True)

    p_validate = sp.add_parser("validate")
    p_validate.add_argument("--csv", required=True)
    p_validate.add_argument("--allow-shorter", action="store_true", default=False)
    p_validate.add_argument("--ascii-only", action="store_true", default=False)

    p_inject = sp.add_parser("inject")
    p_inject.add_argument("--csv", required=True)
    p_inject.add_argument("--input-bin", required=True)
    p_inject.add_argument("--output-bin", required=True)
    p_inject.add_argument("--allow-shorter", action="store_true", default=False)
    p_inject.add_argument("--ascii-only", action="store_true", default=False)
    p_inject.add_argument("--no-strict-original", action="store_true", default=False)

    p_repl = sp.add_parser("repl")
    p_repl.add_argument("--csv", required=True)
    p_repl.add_argument("--allow-shorter", action="store_true", default=False)
    p_repl.add_argument("--ascii-only", action="store_true", default=False)
    return p


def main() -> int:
    p = build_parser()
    args = p.parse_args()

    if args.cmd == "stats":
        entries = core.load_entries(Path(args.csv))
        stats(entries)
        return 0

    if args.cmd == "list":
        entries = core.load_entries(Path(args.csv))
        print_list(entries, only_todo=args.todo_only, limit=args.limit)
        return 0

    if args.cmd == "set":
        entries = core.load_entries(Path(args.csv))
        set_translation(entries, idx=args.id, text=args.text, ascii_only=args.ascii_only)
        save_csv(Path(args.out_csv), entries)
        return 0

    if args.cmd == "clear":
        entries = core.load_entries(Path(args.csv))
        clear_translation(entries, idx=args.id)
        save_csv(Path(args.out_csv), entries)
        return 0

    if args.cmd == "validate":
        entries = core.load_entries(Path(args.csv))
        return run_validate(entries, allow_shorter=args.allow_shorter, ascii_only=args.ascii_only)

    if args.cmd == "inject":
        entries = core.load_entries(Path(args.csv))
        return run_inject(
            entries,
            input_bin=Path(args.input_bin),
            output_bin=Path(args.output_bin),
            allow_shorter=args.allow_shorter,
            ascii_only=args.ascii_only,
            no_strict_original=args.no_strict_original,
        )

    if args.cmd == "repl":
        shell = MsgEditShell(
            csv_path=Path(args.csv), allow_shorter=args.allow_shorter, ascii_only=args.ascii_only
        )
        shell.cmdloop()
        return 0

    raise ValueError(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
