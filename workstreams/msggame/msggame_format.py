#!/usr/bin/env python3
"""Parse and rebuild the decompressed multi-block ``msggame`` resource.

The packed game resource is a normal NOBU16 24-byte raw-LZ4 wrapper.  Its
decompressed payload has this layout (all integers are unsigned little
endian):

    u32 block_count
    block_count * (u32 block_offset, u32 block_size)
    zero padding to 4-byte alignment
    blocks...

Each block is another indexed variable-length table:

    u32 record_count
    record_count * u32 record_offset   # relative to the block
    record bytes...
    zero padding to the next block's 4-byte-aligned offset

There is no terminal record offset.  The final record ends at block_size.
This module intentionally treats record payloads as opaque bytecode until the
embedded-text opcode grammar has been proved separately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

from nobu16_lz4 import (  # noqa: E402
    WrapperHeader,
    decompress_wrapper,
    recompress_wrapper,
)


ALIGNMENT = 4
U32_MAX = 0xFFFFFFFF
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"


class MsgGameFormatError(ValueError):
    """Raised when a decompressed msggame table violates the format."""


@dataclass(frozen=True)
class MsgGameRecord:
    block_id: int
    record_id: int
    relative_offset: int
    data: bytes


@dataclass(frozen=True)
class MsgGameLiteral:
    block_id: int
    record_id: int
    literal_id: int
    marker_offset: int
    marker_end: int
    text: str


@dataclass(frozen=True)
class MsgGameBlock:
    block_id: int
    offset: int
    size: int
    records: tuple[MsgGameRecord, ...]
    gap_after: bytes


@dataclass(frozen=True)
class MsgGameArchive:
    blocks: tuple[MsgGameBlock, ...]
    raw_size: int

    @property
    def record_count(self) -> int:
        return sum(len(block.records) for block in self.blocks)


@dataclass(frozen=True)
class PackedMsgGame:
    header: WrapperHeader
    archive: MsgGameArchive


def _u32(blob: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(blob):
        raise MsgGameFormatError(
            f"{label}: u32 at 0x{offset:X} exceeds buffer size 0x{len(blob):X}"
        )
    return struct.unpack_from("<I", blob, offset)[0]


def _align(value: int, alignment: int = ALIGNMENT) -> int:
    return (value + alignment - 1) & -alignment


def parse_raw_msggame(raw: bytes) -> MsgGameArchive:
    """Strictly parse one decompressed msggame payload."""
    if len(raw) < 4:
        raise MsgGameFormatError("raw msggame is smaller than its block count")

    block_count = _u32(raw, 0, "block_count")
    directory_end = 4 + block_count * 8
    if directory_end > len(raw):
        raise MsgGameFormatError(
            f"block directory ends at 0x{directory_end:X}, beyond 0x{len(raw):X}"
        )
    if block_count == 0:
        if raw != b"\0\0\0\0":
            raise MsgGameFormatError("zero-block msggame has trailing bytes")
        return MsgGameArchive((), len(raw))

    pairs = [
        (
            _u32(raw, 4 + block_id * 8, f"block[{block_id}].offset"),
            _u32(raw, 8 + block_id * 8, f"block[{block_id}].size"),
        )
        for block_id in range(block_count)
    ]
    if pairs[0][0] != _align(directory_end):
        raise MsgGameFormatError(
            f"first block starts at 0x{pairs[0][0]:X}; expected aligned "
            f"directory end 0x{_align(directory_end):X}"
        )
    pre_block_gap = raw[directory_end : pairs[0][0]]
    if any(pre_block_gap):
        raise MsgGameFormatError("non-zero bytes between directory and first block")

    blocks: list[MsgGameBlock] = []
    for block_id, (block_offset, block_size) in enumerate(pairs):
        if block_offset % ALIGNMENT:
            raise MsgGameFormatError(
                f"block[{block_id}] offset 0x{block_offset:X} is not 4-byte aligned"
            )
        if block_offset < directory_end:
            raise MsgGameFormatError(f"block[{block_id}] overlaps the block directory")
        block_end = block_offset + block_size
        if block_end > len(raw):
            raise MsgGameFormatError(
                f"block[{block_id}] ends at 0x{block_end:X}, beyond 0x{len(raw):X}"
            )
        next_offset = pairs[block_id + 1][0] if block_id + 1 < block_count else len(raw)
        if block_end > next_offset:
            raise MsgGameFormatError(f"block[{block_id}] overlaps the following block")
        expected_next = _align(block_end)
        if next_offset != expected_next:
            raise MsgGameFormatError(
                f"block[{block_id}] next offset 0x{next_offset:X}; "
                f"expected 0x{expected_next:X}"
            )
        gap_after = raw[block_end:next_offset]
        if any(gap_after):
            raise MsgGameFormatError(f"block[{block_id}] has non-zero alignment padding")
        if block_size < 4:
            raise MsgGameFormatError(f"block[{block_id}] is smaller than its record count")

        record_count = _u32(raw, block_offset, f"block[{block_id}].record_count")
        record_directory_end = 4 + record_count * 4
        if record_directory_end > block_size:
            raise MsgGameFormatError(
                f"block[{block_id}] record directory ends at 0x{record_directory_end:X}, "
                f"beyond block size 0x{block_size:X}"
            )
        record_offsets = [
            _u32(
                raw,
                block_offset + 4 + record_id * 4,
                f"block[{block_id}].record[{record_id}].offset",
            )
            for record_id in range(record_count)
        ]
        if record_count and record_offsets[0] != record_directory_end:
            raise MsgGameFormatError(
                f"block[{block_id}] first record starts at 0x{record_offsets[0]:X}; "
                f"expected 0x{record_directory_end:X}"
            )

        records: list[MsgGameRecord] = []
        previous = record_directory_end
        for record_id, record_offset in enumerate(record_offsets):
            if record_offset < previous:
                raise MsgGameFormatError(
                    f"block[{block_id}] record offsets are not monotonic at {record_id}"
                )
            record_end = (
                record_offsets[record_id + 1]
                if record_id + 1 < record_count
                else block_size
            )
            if record_end < record_offset or record_end > block_size:
                raise MsgGameFormatError(
                    f"block[{block_id}] record[{record_id}] range is outside its block"
                )
            records.append(
                MsgGameRecord(
                    block_id=block_id,
                    record_id=record_id,
                    relative_offset=record_offset,
                    data=raw[block_offset + record_offset : block_offset + record_end],
                )
            )
            previous = record_offset

        # A zero-record block can only contain the four-byte count.
        if not record_count and block_size != 4:
            raise MsgGameFormatError(
                f"block[{block_id}] has no records but size is 0x{block_size:X}"
            )
        blocks.append(
            MsgGameBlock(
                block_id=block_id,
                offset=block_offset,
                size=block_size,
                records=tuple(records),
                gap_after=gap_after,
            )
        )

    return MsgGameArchive(tuple(blocks), len(raw))


def parse_packed_msggame(packed: bytes) -> PackedMsgGame:
    header, raw = decompress_wrapper(packed)
    return PackedMsgGame(header=header, archive=parse_raw_msggame(raw))


def parse_record_literals(record: MsgGameRecord) -> tuple[MsgGameLiteral, ...]:
    """Decode every proved ``07 07 01 ... 07 07 02`` UTF-16LE literal."""
    payload = record.data
    literals: list[MsgGameLiteral] = []
    cursor = 0
    while True:
        start = payload.find(LITERAL_START, cursor)
        orphan_end = payload.find(LITERAL_END, cursor)
        if start < 0:
            if orphan_end >= 0:
                raise MsgGameFormatError(
                    f"block[{record.block_id}] record[{record.record_id}] has an "
                    f"orphan literal-end marker at 0x{orphan_end:X}"
                )
            break
        if 0 <= orphan_end < start:
            raise MsgGameFormatError(
                f"block[{record.block_id}] record[{record.record_id}] has an "
                f"orphan literal-end marker at 0x{orphan_end:X}"
            )
        text_start = start + len(LITERAL_START)
        end = payload.find(LITERAL_END, text_start)
        if end < 0:
            raise MsgGameFormatError(
                f"block[{record.block_id}] record[{record.record_id}] has an "
                f"unterminated literal at 0x{start:X}"
            )
        nested = payload.find(LITERAL_START, text_start, end)
        if nested >= 0:
            raise MsgGameFormatError(
                f"block[{record.block_id}] record[{record.record_id}] has a nested "
                f"literal marker at 0x{nested:X}"
            )
        raw_text = payload[text_start:end]
        if len(raw_text) % 2:
            raise MsgGameFormatError(
                f"block[{record.block_id}] record[{record.record_id}] literal "
                f"{len(literals)} has an odd UTF-16LE byte count"
            )
        try:
            text = raw_text.decode("utf-16-le")
        except UnicodeDecodeError as exc:
            raise MsgGameFormatError(
                f"block[{record.block_id}] record[{record.record_id}] literal "
                f"{len(literals)} is not valid UTF-16LE: {exc}"
            ) from exc
        marker_end = end + len(LITERAL_END)
        literals.append(
            MsgGameLiteral(
                block_id=record.block_id,
                record_id=record.record_id,
                literal_id=len(literals),
                marker_offset=start,
                marker_end=marker_end,
                text=text,
            )
        )
        cursor = marker_end
    return tuple(literals)


def iter_literals(archive: MsgGameArchive):
    for block in archive.blocks:
        for record in block.records:
            yield from parse_record_literals(record)


def is_visible_translation_candidate(text: str) -> bool:
    """Return true when a literal contains at least one visible non-space char."""
    return any(character.isprintable() and not character.isspace() for character in text)


def rebuild_record_literals(
    record: MsgGameRecord,
    replacements: Mapping[int, str] | None = None,
) -> bytes:
    """Replace selected literal texts while preserving all bytecode around them."""
    replacements = replacements or {}
    literals = parse_record_literals(record)
    unknown = sorted(set(replacements) - {literal.literal_id for literal in literals})
    if unknown:
        raise MsgGameFormatError(
            f"block[{record.block_id}] record[{record.record_id}] has no literals {unknown}"
        )
    if not replacements:
        return record.data

    output = bytearray()
    cursor = 0
    for literal in literals:
        output.extend(record.data[cursor : literal.marker_offset])
        output.extend(LITERAL_START)
        replacement = replacements.get(literal.literal_id, literal.text)
        if not isinstance(replacement, str):
            raise MsgGameFormatError("literal replacement values must be strings")
        encoded = replacement.encode("utf-16-le")
        if LITERAL_START in encoded or LITERAL_END in encoded:
            raise MsgGameFormatError(
                f"replacement for block[{record.block_id}] record[{record.record_id}] "
                f"literal[{literal.literal_id}] contains a reserved marker byte sequence"
            )
        output.extend(encoded)
        output.extend(LITERAL_END)
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


def literal_record_replacements(
    archive: MsgGameArchive,
    replacements: Mapping[tuple[int, int, int], str],
) -> dict[tuple[int, int], bytes]:
    """Convert literal-coordinate replacements into complete rebuilt records."""
    grouped: dict[tuple[int, int], dict[int, str]] = {}
    for key, replacement in replacements.items():
        if len(key) != 3:
            raise MsgGameFormatError(f"literal replacement key must have 3 integers: {key!r}")
        block_id, record_id, literal_id = key
        grouped.setdefault((block_id, record_id), {})[literal_id] = replacement

    records = {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }
    unknown = sorted(set(grouped) - set(records))
    if unknown:
        raise MsgGameFormatError(f"literal replacements reference missing records: {unknown[:5]}")
    return {
        key: rebuild_record_literals(records[key], values)
        for key, values in grouped.items()
    }


def rebuild_raw_with_literals(
    archive: MsgGameArchive,
    replacements: Mapping[tuple[int, int, int], str],
) -> bytes:
    return rebuild_raw_msggame(archive, literal_record_replacements(archive, replacements))


def rebuild_packed_with_literals(
    packed: bytes,
    replacements: Mapping[tuple[int, int, int], str],
) -> bytes:
    parsed = parse_packed_msggame(packed)
    raw = rebuild_raw_with_literals(parsed.archive, replacements)
    rebuilt = recompress_wrapper(raw, parsed.header)
    _header, roundtrip = decompress_wrapper(rebuilt)
    if roundtrip != raw:
        raise MsgGameFormatError("literal overlay wrapper round-trip mismatch")
    return rebuilt


def rebuild_raw_msggame(
    archive: MsgGameArchive,
    replacements: Mapping[tuple[int, int], bytes] | None = None,
) -> bytes:
    """Rebuild an archive, optionally replacing complete opaque records."""
    replacements = replacements or {}
    valid_keys = {
        (record.block_id, record.record_id)
        for block in archive.blocks
        for record in block.records
    }
    unknown = sorted(set(replacements) - valid_keys)
    if unknown:
        raise MsgGameFormatError(f"replacement keys do not exist: {unknown[:5]}")

    block_blobs: list[bytes] = []
    for block in archive.blocks:
        record_payloads = [
            bytes(replacements.get((record.block_id, record.record_id), record.data))
            for record in block.records
        ]
        table_size = 4 + 4 * len(record_payloads)
        cursor = table_size
        offsets: list[int] = []
        for payload in record_payloads:
            offsets.append(cursor)
            cursor += len(payload)
            if cursor > U32_MAX:
                raise MsgGameFormatError("rebuilt block exceeds the u32 offset range")
        block_blob = bytearray(struct.pack("<I", len(record_payloads)))
        block_blob.extend(b"".join(struct.pack("<I", offset) for offset in offsets))
        block_blob.extend(b"".join(record_payloads))
        block_blobs.append(bytes(block_blob))

    block_count = len(block_blobs)
    directory_size = 4 + 8 * block_count
    cursor = _align(directory_size)
    pairs: list[tuple[int, int]] = []
    for block_blob in block_blobs:
        if cursor > U32_MAX or len(block_blob) > U32_MAX:
            raise MsgGameFormatError("rebuilt archive exceeds the u32 block range")
        pairs.append((cursor, len(block_blob)))
        cursor = _align(cursor + len(block_blob))

    out = bytearray(struct.pack("<I", block_count))
    for offset, size in pairs:
        out.extend(struct.pack("<II", offset, size))
    out.extend(b"\0" * (_align(len(out)) - len(out)))
    for block_blob in block_blobs:
        out.extend(block_blob)
        out.extend(b"\0" * (_align(len(out)) - len(out)))

    rebuilt = bytes(out)
    parse_raw_msggame(rebuilt)
    return rebuilt


def rebuild_packed_msggame(
    packed: bytes,
    replacements: Mapping[tuple[int, int], bytes] | None = None,
) -> bytes:
    """Rebuild and raw-LZ4-wrap a packed resource without touching its source."""
    parsed = parse_packed_msggame(packed)
    raw = rebuild_raw_msggame(parsed.archive, replacements)
    rebuilt = recompress_wrapper(raw, parsed.header)
    _header, roundtrip = decompress_wrapper(rebuilt)
    if roundtrip != raw:
        raise MsgGameFormatError("wrapped msggame decompression round-trip mismatch")
    return rebuilt


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def structural_summary(packed: bytes) -> dict[str, object]:
    parsed = parse_packed_msggame(packed)
    raw = rebuild_raw_msggame(parsed.archive)
    literals = list(iter_literals(parsed.archive))
    marker_records = len({(literal.block_id, literal.record_id) for literal in literals})
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "block_count": len(parsed.archive.blocks),
        "record_count": parsed.archive.record_count,
        "block_record_counts": [len(block.records) for block in parsed.archive.blocks],
        "block_sizes": [block.size for block in parsed.archive.blocks],
        "literal_marker_record_count": marker_records,
        "literal_slot_count": len(literals),
        "literal_nonempty_count": sum(bool(literal.text) for literal in literals),
        "literal_stripped_nonempty_count": sum(
            bool(literal.text.strip()) for literal in literals
        ),
        "visible_translation_candidate_count": sum(
            is_visible_translation_candidate(literal.text) for literal in literals
        ),
        "literal_marker_parse": "OK",
        "raw_parse_rebuild_byte_exact": raw
        == decompress_wrapper(packed)[1],
        "wrapper_decompression": "OK",
    }


def _cmd_inspect(args: argparse.Namespace) -> int:
    packed = args.input.read_bytes()
    summary = structural_summary(packed)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        for key, value in summary.items():
            print(f"{key}={value}")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    packed = args.input.read_bytes()
    parsed = parse_packed_msggame(packed)
    _header, original_raw = decompress_wrapper(packed)
    rebuilt_raw = rebuild_raw_msggame(parsed.archive)
    if rebuilt_raw != original_raw:
        raise MsgGameFormatError("raw parse/rebuild is not byte-exact")
    wrapped = rebuild_packed_msggame(packed)
    _new_header, wrapped_raw = decompress_wrapper(wrapped)
    if wrapped_raw != original_raw:
        raise MsgGameFormatError("recompressed wrapper changed the raw resource")
    print(f"input={args.input}")
    print(f"blocks={len(parsed.archive.blocks)}")
    print(f"records={parsed.archive.record_count}")
    print(f"raw_sha256={sha256(original_raw)}")
    print("raw_parse_rebuild_byte_exact=OK")
    print("wrapper_semantic_roundtrip=OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Print source-free structure metadata")
    inspect.add_argument("input", type=Path)
    inspect.add_argument("--json", action="store_true")
    inspect.set_defaults(func=_cmd_inspect)
    verify = sub.add_parser("verify", help="Require a byte-exact raw round-trip")
    verify.add_argument("input", type=Path)
    verify.set_defaults(func=_cmd_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, MsgGameFormatError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
