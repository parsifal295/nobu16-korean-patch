#!/usr/bin/env python3
"""Extract and rebuild NOBU16 single-block message string tables.

This tool handles the decompressed/raw form of the common message resources:
``msgbre``, ``msgdata``, ``msgev``, ``msgire``, ``msgstf``, and ``msgui``.
It deliberately does not handle ``msggame``: that resource is a multi-block
bytecode container, not this single UTF-16LE string-table format.

The table contains only string offsets: its first u32 is string id 0's
table-relative offset.  Because the packed offset array ends exactly where
string id 0 begins, ``first_offset / 4`` is the string count.

CSV output has the columns ``id,text,translation`` and is UTF-8 without a BOM.
Standard CSV quoting safely preserves embedded newlines.  JSONL is also
supported for workflows that prefer one escaped JSON object per physical line.
During rebuild, a non-empty ``translation`` replaces ``text``; an empty one
keeps the original text.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


U32_SIZE = 4
BLOCK_TABLE_REL_FIELD = 0x0C
ALIGNMENT = 4


class MessageTableError(ValueError):
    """Raised when a raw message table or translation file is invalid."""


@dataclass(frozen=True)
class MessageTable:
    blob: bytes
    block_offset: int
    logical_size: int
    logical_end: int
    padding: bytes
    table_offset: int
    table_size: int
    string_offsets: tuple[int, ...]
    string_start: int
    texts: tuple[str, ...]

    @property
    def string_count(self) -> int:
        return len(self.texts)


def _u32(blob: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + U32_SIZE > len(blob):
        raise MessageTableError(f"{label} u32 at 0x{offset:X} is outside the file")
    return struct.unpack_from("<I", blob, offset)[0]


def _read_utf16lez(blob: bytes, start: int, limit: int, entry_id: int) -> tuple[str, int]:
    if start < 0 or start >= limit:
        raise MessageTableError(
            f"string id {entry_id} starts at 0x{start:X}, outside logical data ending 0x{limit:X}"
        )
    if start & 1:
        raise MessageTableError(f"string id {entry_id} starts at unaligned offset 0x{start:X}")

    end = start
    while end + 1 < limit and blob[end : end + 2] != b"\x00\x00":
        end += 2
    if end + 1 >= limit:
        raise MessageTableError(f"string id {entry_id} has no UTF-16LE terminator")
    try:
        text = blob[start:end].decode("utf-16le")
    except UnicodeDecodeError as exc:
        raise MessageTableError(f"string id {entry_id} is invalid UTF-16LE: {exc}") from exc
    return text, end + 2


def parse_message_table(blob: bytes) -> MessageTable:
    """Parse and strictly validate a decompressed common message table."""
    if len(blob) < 0x24:
        raise MessageTableError("file is too small for a NOBU16 message table")

    block_count = _u32(blob, 0, "outer block count")
    if block_count != 1:
        raise MessageTableError(
            f"unsupported block_count={block_count}; this tool only handles the six "
            "single-block common tables. msggame is multi-block bytecode and is out of scope"
        )

    block_offset = _u32(blob, 4, "block descriptor offset")
    logical_size = _u32(blob, 8, "logical block size")
    if block_offset < 0x0C or block_offset + BLOCK_TABLE_REL_FIELD + 4 > len(blob):
        raise MessageTableError(f"invalid block offset 0x{block_offset:X}")
    logical_end = block_offset + logical_size
    if logical_end > len(blob):
        raise MessageTableError(
            f"logical block ends at 0x{logical_end:X}, beyond file size 0x{len(blob):X}"
        )
    padding = blob[logical_end:]
    if len(padding) >= ALIGNMENT or any(padding):
        raise MessageTableError(
            f"expected 0-3 zero alignment bytes after logical data, found {len(padding)} bytes"
        )

    table_rel = _u32(blob, block_offset + BLOCK_TABLE_REL_FIELD, "table relative offset")
    table_offset = block_offset + table_rel
    first_offset = _u32(blob, table_offset, "string id 0 offset")
    if first_offset < U32_SIZE or first_offset % U32_SIZE:
        raise MessageTableError(
            f"first string offset {first_offset} must be a positive multiple of four"
        )
    table_size = first_offset
    table_end = table_offset + table_size
    if table_end > logical_end:
        raise MessageTableError(
            f"table ends at 0x{table_end:X}, beyond logical data ending 0x{logical_end:X}"
        )

    # The first offset points just past the packed offset array, so its value
    # divided by four is the number of offsets/strings.
    string_count = first_offset // U32_SIZE
    offsets = tuple(
        _u32(blob, table_offset + entry_id * U32_SIZE, f"string id {entry_id} offset")
        for entry_id in range(string_count)
    )
    if any(current <= previous for previous, current in zip(offsets, offsets[1:])):
        raise MessageTableError("string offsets must be strictly increasing")
    if offsets[0] != table_size:
        raise MessageTableError(
            f"first string relative offset 0x{offsets[0]:X} does not equal table size 0x{table_size:X}"
        )

    texts: list[str] = []
    ends: list[int] = []
    for entry_id, relative_offset in enumerate(offsets):
        text, end = _read_utf16lez(blob, table_offset + relative_offset, logical_end, entry_id)
        texts.append(text)
        ends.append(end)
    for entry_id in range(string_count - 1):
        expected = table_offset + offsets[entry_id + 1]
        if ends[entry_id] != expected:
            raise MessageTableError(
                f"string id {entry_id} ends at 0x{ends[entry_id]:X}, but id {entry_id + 1} "
                f"starts at 0x{expected:X}; non-contiguous string pools are unsupported"
            )
    if ends[-1] != logical_end:
        raise MessageTableError(
            f"last string ends at 0x{ends[-1]:X}, logical data ends at 0x{logical_end:X}"
        )

    return MessageTable(
        blob=blob,
        block_offset=block_offset,
        logical_size=logical_size,
        logical_end=logical_end,
        padding=padding,
        table_offset=table_offset,
        table_size=table_size,
        string_offsets=offsets,
        string_start=table_offset + offsets[0],
        texts=tuple(texts),
    )


def _infer_format(path: Path, requested: str | None) -> str:
    if requested:
        return requested
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    raise MessageTableError("cannot infer table format; use a .csv/.jsonl name or --format")


def export_rows(path: Path, rows: Sequence[dict[str, object]], file_format: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if file_format == "csv":
        # newline="" is required by csv and prevents Windows newline translation.
        # encoding="utf-8" deliberately emits no BOM.
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=("id", "text", "translation"),
                lineterminator="\n",
                extrasaction="raise",
            )
            writer.writeheader()
            writer.writerows(rows)
        return
    if file_format == "jsonl":
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
                stream.write("\n")
        return
    raise MessageTableError(f"unsupported translation format: {file_format}")


def load_rows(path: Path, file_format: str) -> list[dict[str, object]]:
    if file_format == "csv":
        # utf-8-sig also accepts BOM-less UTF-8 while being forgiving of editors that add a BOM.
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["id", "text", "translation"]:
                raise MessageTableError(
                    "CSV header must be exactly: id,text,translation"
                )
            return [dict(row) for row in reader]
    if file_format == "jsonl":
        rows: list[dict[str, object]] = []
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise MessageTableError(f"invalid JSONL at line {line_number}: {exc}") from exc
                if not isinstance(row, dict):
                    raise MessageTableError(f"JSONL line {line_number} is not an object")
                if set(row) != {"id", "text", "translation"}:
                    raise MessageTableError(
                        f"JSONL line {line_number} must contain only id, text, translation"
                    )
                rows.append(row)
        return rows
    raise MessageTableError(f"unsupported translation format: {file_format}")


def _normalize_rows(
    rows: Sequence[dict[str, object]], original_texts: Sequence[str]
) -> tuple[str, ...]:
    expected_count = len(original_texts)
    if len(rows) != expected_count:
        raise MessageTableError(f"translation rows={len(rows)}, expected={expected_count}")

    normalized: dict[int, tuple[str, str]] = {}
    for row_number, row in enumerate(rows, 2):
        raw_id = row.get("id")
        try:
            entry_id = int(raw_id)  # accepts CSV strings and JSON integer ids
        except (TypeError, ValueError) as exc:
            raise MessageTableError(f"row {row_number} has invalid id {raw_id!r}") from exc
        if isinstance(raw_id, bool) or str(raw_id) != str(entry_id):
            raise MessageTableError(f"row {row_number} id must be a plain decimal integer")
        if entry_id in normalized:
            raise MessageTableError(f"duplicate id {entry_id}")
        text = row.get("text")
        translation = row.get("translation")
        if not isinstance(text, str) or not isinstance(translation, str):
            raise MessageTableError(f"id {entry_id}: text and translation must be strings")
        if "\x00" in text or "\x00" in translation:
            raise MessageTableError(f"id {entry_id}: embedded NUL is not allowed")
        normalized[entry_id] = (text, translation)

    expected_ids = set(range(expected_count))
    if set(normalized) != expected_ids:
        missing = sorted(expected_ids - set(normalized))
        extra = sorted(set(normalized) - expected_ids)
        raise MessageTableError(f"ids must be 0..{expected_count - 1}; missing={missing[:5]}, extra={extra[:5]}")

    replacements: list[str] = []
    for entry_id, original in enumerate(original_texts):
        source, translation = normalized[entry_id]
        if source != original:
            raise MessageTableError(
                f"id {entry_id}: source text differs from the raw input; edit translation, not text"
            )
        replacements.append(translation if translation != "" else original)
    return tuple(replacements)


def rebuild_message_table(table: MessageTable, texts: Sequence[str]) -> bytes:
    """Rebuild all offsets and the logical size while preserving opaque metadata."""
    if len(texts) != table.string_count:
        raise MessageTableError(f"replacement strings={len(texts)}, expected={table.string_count}")

    prefix = bytearray(table.blob[: table.string_start])
    string_pool = bytearray()
    new_offsets: list[int] = []
    relative = table.string_start - table.table_offset
    for entry_id, text in enumerate(texts):
        if not isinstance(text, str):
            raise MessageTableError(f"replacement id {entry_id} is not a string")
        if "\x00" in text:
            raise MessageTableError(f"replacement id {entry_id} contains an embedded NUL")
        try:
            encoded = text.encode("utf-16le")
        except UnicodeEncodeError as exc:
            raise MessageTableError(f"replacement id {entry_id} is not valid UTF-16 text: {exc}") from exc
        if relative > 0xFFFFFFFF:
            raise MessageTableError("rebuilt string offset exceeds u32")
        new_offsets.append(relative)
        string_pool.extend(encoded)
        string_pool.extend(b"\x00\x00")
        relative += len(encoded) + 2

    for entry_id, relative_offset in enumerate(new_offsets):
        struct.pack_into(
            "<I", prefix, table.table_offset + entry_id * U32_SIZE, relative_offset
        )

    unpadded = prefix + string_pool
    new_logical_size = len(unpadded) - table.block_offset
    if new_logical_size > 0xFFFFFFFF:
        raise MessageTableError("rebuilt logical block size exceeds u32")
    struct.pack_into("<I", unpadded, 8, new_logical_size)
    padding_size = (-len(unpadded)) % ALIGNMENT
    return bytes(unpadded) + b"\x00" * padding_size


def _refuse_input_overwrite(output: Path, inputs: Sequence[Path]) -> None:
    resolved = output.resolve()
    for input_path in inputs:
        if resolved == input_path.resolve():
            raise MessageTableError(f"refusing to overwrite input file: {input_path}")


def cmd_info(args: argparse.Namespace) -> int:
    source = Path(args.input)
    table = parse_message_table(source.read_bytes())
    info = {
        "path": str(source),
        "file_size": len(table.blob),
        "block_offset": table.block_offset,
        "logical_size": table.logical_size,
        "padding_size": len(table.padding),
        "table_offset": table.table_offset,
        "table_size": table.table_size,
        "table_word_count": table.table_size // 4,
        "string_count": table.string_count,
        "string_start": table.string_start,
        "sha256": hashlib.sha256(table.blob).hexdigest(),
    }
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        for key, value in info.items():
            print(f"{key}={value}")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    source = Path(args.input)
    output = Path(args.output)
    _refuse_input_overwrite(output, (source,))
    table = parse_message_table(source.read_bytes())
    rows = [
        {"id": entry_id, "text": text, "translation": ""}
        for entry_id, text in enumerate(table.texts)
    ]
    file_format = _infer_format(output, args.format)
    export_rows(output, rows, file_format)
    print(f"input={source}")
    print(f"output={output}")
    print(f"format={file_format}")
    print(f"strings={table.string_count}")
    print("encoding=utf-8-no-bom")
    return 0


def cmd_rebuild(args: argparse.Namespace) -> int:
    source = Path(args.input)
    translations = Path(args.translations)
    output = Path(args.output)
    _refuse_input_overwrite(output, (source, translations))
    table = parse_message_table(source.read_bytes())
    file_format = _infer_format(translations, args.format)
    rows = load_rows(translations, file_format)
    replacement_texts = _normalize_rows(rows, table.texts)
    rebuilt = rebuild_message_table(table, replacement_texts)
    check = parse_message_table(rebuilt)
    if check.texts != replacement_texts:
        raise MessageTableError("internal rebuilt parse verification failed")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(rebuilt)
    changed = sum(a != b for a, b in zip(table.texts, replacement_texts))
    print(f"input={source}")
    print(f"translations={translations}")
    print(f"output={output}")
    print(f"format={file_format}")
    print(f"strings={table.string_count}")
    print(f"changed={changed}")
    print(f"old_size={len(table.blob)}")
    print(f"new_size={len(rebuilt)}")
    print("parse_roundtrip=OK")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    source = Path(args.input)
    blob = source.read_bytes()
    table = parse_message_table(blob)
    rebuilt = rebuild_message_table(table, table.texts)
    if rebuilt != blob:
        raise MessageTableError("unchanged parse -> rebuild is not byte-identical")
    reparsed = parse_message_table(rebuilt)
    if reparsed.texts != table.texts:
        raise MessageTableError("unchanged rebuilt parse verification failed")
    print(f"input={source}")
    print(f"strings={table.string_count}")
    print(f"size={len(blob)}")
    print(f"sha256={hashlib.sha256(blob).hexdigest()}")
    print("byte_identical_roundtrip=OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info", help="Inspect and validate a decompressed common table")
    info.add_argument("input")
    info.add_argument("--json", action="store_true")
    info.set_defaults(func=cmd_info)

    extract = sub.add_parser("extract", help="Export id, text, translation rows")
    extract.add_argument("input", help="Decompressed/raw common msg file")
    extract.add_argument("output", help="UTF-8 .csv or newline-safe .jsonl")
    extract.add_argument("--format", choices=("csv", "jsonl"))
    extract.set_defaults(func=cmd_extract)

    rebuild = sub.add_parser("rebuild", help="Apply translations and rebuild every string offset")
    rebuild.add_argument("input", help="Original decompressed/raw common msg file")
    rebuild.add_argument("translations", help="Edited .csv or .jsonl")
    rebuild.add_argument("output", help="New decompressed/raw msg file")
    rebuild.add_argument("--format", choices=("csv", "jsonl"))
    rebuild.set_defaults(func=cmd_rebuild)

    verify = sub.add_parser("verify", help="Require a byte-identical unchanged round trip")
    verify.add_argument("input")
    verify.set_defaults(func=cmd_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, MessageTableError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
