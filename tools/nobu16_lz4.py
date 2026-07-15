#!/usr/bin/env python3
"""Inspect and rebuild NOBU16 raw-LZ4 wrappers and LINK archives.

The game stores many resources as:

    0x00  8 bytes   opaque prefix (preserve it verbatim)
    0x08  u64le     uncompressed size
    0x10  u64le     compressed size
    0x18  bytes     raw LZ4 block (no LZ4 frame header)

LINK archives use a 16-byte header followed by ``count`` pairs of
``(u32le offset, u32le stored_size)``.  The size excludes the four-byte
entry trailer (normally EF CD AB 89 for a non-empty entry).

No third-party Python package is required.  The default recompressor retains
the original deterministic literal-only behavior used by existing message
recipes.  Font archives can opt into the deterministic greedy compressor to
avoid inflating large atlas wrappers beyond the stock loading profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


WRAPPER_SIZE = 24
LINK_FIXED_HEADER_SIZE = 16
LINK_MAGIC = b"LINK"
LINK_ENTRY_TRAILER = bytes.fromhex("EF CD AB 89")


class LZ4Error(ValueError):
    """Raised for an invalid raw LZ4 block."""


class LinkError(ValueError):
    """Raised for an invalid LINK archive."""


@dataclass(frozen=True)
class WrapperHeader:
    prefix: bytes
    uncompressed_size: int
    compressed_size: int

    @property
    def marker_u16(self) -> int:
        return struct.unpack_from("<H", self.prefix, 0)[0]

    @property
    def tag_u16(self) -> int:
        return struct.unpack_from("<H", self.prefix, 2)[0]

    @property
    def param_u32(self) -> int:
        return struct.unpack_from("<I", self.prefix, 4)[0]

    @property
    def word0_u32(self) -> int:
        return struct.unpack_from("<I", self.prefix, 0)[0]


@dataclass(frozen=True)
class LinkEntry:
    index: int
    offset: int
    stored_size: int
    data: bytes
    gap_after: bytes


@dataclass(frozen=True)
class LinkArchive:
    version: int
    reserved: int
    fixed_header: bytes
    pre_data_padding: bytes
    entries: tuple[LinkEntry, ...]
    original_size: int


def parse_wrapper_header(blob: bytes, *, require_exact_size: bool = True) -> WrapperHeader:
    if len(blob) < WRAPPER_SIZE:
        raise LZ4Error(f"file is smaller than the {WRAPPER_SIZE}-byte wrapper")
    uncompressed_size, compressed_size = struct.unpack_from("<QQ", blob, 8)
    if compressed_size > len(blob) - WRAPPER_SIZE:
        raise LZ4Error(
            f"compressed_size={compressed_size} exceeds payload={len(blob) - WRAPPER_SIZE}"
        )
    if require_exact_size and compressed_size != len(blob) - WRAPPER_SIZE:
        raise LZ4Error(
            f"compressed_size={compressed_size}, but payload={len(blob) - WRAPPER_SIZE}"
        )
    return WrapperHeader(blob[:8], uncompressed_size, compressed_size)


def raw_lz4_decompress(src: bytes, expected_size: int) -> bytes:
    """Decode one raw LZ4 block using the standard token stream."""
    if expected_size < 0:
        raise LZ4Error("negative expected size")
    if expected_size == 0 and not src:
        return b""

    out = bytearray()
    pos = 0
    src_len = len(src)

    while pos < src_len:
        token = src[pos]
        pos += 1

        literal_length = token >> 4
        if literal_length == 15:
            while True:
                if pos >= src_len:
                    raise LZ4Error("truncated literal-length extension")
                value = src[pos]
                pos += 1
                literal_length += value
                if value != 255:
                    break

        literal_end = pos + literal_length
        if literal_end > src_len:
            raise LZ4Error("literal run exceeds compressed input")
        if len(out) + literal_length > expected_size:
            raise LZ4Error("literal run exceeds expected output size")
        out.extend(src[pos:literal_end])
        pos = literal_end

        # A final literal-only sequence has no match offset.
        if pos == src_len:
            break

        if pos + 2 > src_len:
            raise LZ4Error("truncated match offset")
        match_offset = src[pos] | (src[pos + 1] << 8)
        pos += 2
        if match_offset == 0 or match_offset > len(out):
            raise LZ4Error(f"invalid match offset {match_offset} at compressed 0x{pos - 2:X}")

        match_length = (token & 0x0F) + 4
        if (token & 0x0F) == 15:
            while True:
                if pos >= src_len:
                    raise LZ4Error("truncated match-length extension")
                value = src[pos]
                pos += 1
                match_length += value
                if value != 255:
                    break

        if len(out) + match_length > expected_size:
            raise LZ4Error("match exceeds expected output size")

        # Repeating the preceding offset-byte pattern is equivalent to the
        # overlapping byte-at-a-time LZ4 match copy, but much faster in Python.
        pattern = bytes(out[-match_offset:])
        repeats = (match_length + match_offset - 1) // match_offset
        out.extend((pattern * repeats)[:match_length])

    if pos != src_len:
        raise LZ4Error(f"decoder stopped at {pos}, input size is {src_len}")
    if len(out) != expected_size:
        raise LZ4Error(f"decoded size={len(out)}, expected={expected_size}")
    return bytes(out)


def raw_lz4_compress_literal_only(raw: bytes) -> bytes:
    """Create a valid raw LZ4 block containing one final literal sequence."""
    length = len(raw)
    if length == 0:
        return b""
    if length < 15:
        return bytes((length << 4,)) + raw

    result = bytearray((0xF0,))
    remaining = length - 15
    while remaining >= 255:
        result.append(255)
        remaining -= 255
    result.append(remaining)  # A terminating byte is required, including zero.
    result.extend(raw)
    return bytes(result)


def _append_lz4_length(result: bytearray, length: int) -> None:
    """Append one LZ4 token-length extension, including its terminator."""

    while length >= 255:
        result.append(255)
        length -= 255
    result.append(length)


def raw_lz4_compress_greedy(raw: bytes) -> bytes:
    """Create a deterministic compressed raw-LZ4 block.

    This is a small standard-library implementation of the usual single-entry
    hash-table LZ4 strategy.  It intentionally favors a compact, auditable
    implementation over maximum compression ratio.  The final five input
    bytes remain literals, matching the canonical LZ4 block constraints used
    by the stock NOBU16 resources.
    """

    size = len(raw)
    if size < 13:
        return raw_lz4_compress_literal_only(raw)

    hash_bits = 16
    hash_shift = 32 - hash_bits
    hash_mask = (1 << hash_bits) - 1
    table = [-1] * (1 << hash_bits)
    result = bytearray()
    anchor = 0
    cursor = 0
    match_limit = size - 12
    copy_limit = size - 5

    def hash_at(position: int) -> int:
        sequence = struct.unpack_from("<I", raw, position)[0]
        return ((sequence * 2654435761) & 0xFFFFFFFF) >> hash_shift & hash_mask

    while cursor <= match_limit:
        slot = hash_at(cursor)
        candidate = table[slot]
        table[slot] = cursor
        if (
            candidate < 0
            or cursor - candidate > 0xFFFF
            or raw[candidate : candidate + 4] != raw[cursor : cursor + 4]
        ):
            cursor += 1
            continue

        # Extend backwards without crossing the pending literal run.  This
        # improves ratio while preserving a positive 16-bit match offset.
        match_start = cursor
        reference = candidate
        while match_start > anchor and reference > 0 and raw[match_start - 1] == raw[reference - 1]:
            match_start -= 1
            reference -= 1

        match_end = match_start + 4
        reference_end = reference + 4
        while match_end + 8 <= copy_limit:
            if raw[match_end : match_end + 8] != raw[reference_end : reference_end + 8]:
                break
            match_end += 8
            reference_end += 8
        while match_end < copy_limit and raw[match_end] == raw[reference_end]:
            match_end += 1
            reference_end += 1

        literal_length = match_start - anchor
        match_length = match_end - match_start
        encoded_match_length = match_length - 4
        token = min(literal_length, 15) << 4 | min(encoded_match_length, 15)
        result.append(token)
        if literal_length >= 15:
            _append_lz4_length(result, literal_length - 15)
        result.extend(raw[anchor:match_start])
        result.extend(struct.pack("<H", match_start - reference))
        if encoded_match_length >= 15:
            _append_lz4_length(result, encoded_match_length - 15)

        # Seed positions near the end of the skipped match so the next search
        # can still find short-distance repetitions without visiting every
        # byte inside a long run.
        cursor = match_end
        for position in range(max(match_start + 1, cursor - 3), cursor):
            if position <= match_limit:
                table[hash_at(position)] = position
        anchor = cursor

    literal_length = size - anchor
    result.append(min(literal_length, 15) << 4)
    if literal_length >= 15:
        _append_lz4_length(result, literal_length - 15)
    result.extend(raw[anchor:])

    compressed = bytes(result)
    if len(compressed) >= len(raw_lz4_compress_literal_only(raw)):
        return raw_lz4_compress_literal_only(raw)
    return compressed


def decompress_wrapper(blob: bytes) -> tuple[WrapperHeader, bytes]:
    header = parse_wrapper_header(blob)
    start = WRAPPER_SIZE
    end = start + header.compressed_size
    return header, raw_lz4_decompress(blob[start:end], header.uncompressed_size)


def recompress_wrapper(raw: bytes, template: bytes | WrapperHeader) -> bytes:
    header = template if isinstance(template, WrapperHeader) else parse_wrapper_header(template)
    compressed = raw_lz4_compress_literal_only(raw)
    return header.prefix + struct.pack("<QQ", len(raw), len(compressed)) + compressed


def recompress_wrapper_greedy(raw: bytes, template: bytes | WrapperHeader) -> bytes:
    """Wrap raw bytes using the deterministic greedy raw-LZ4 compressor."""

    header = template if isinstance(template, WrapperHeader) else parse_wrapper_header(template)
    compressed = raw_lz4_compress_greedy(raw)
    return header.prefix + struct.pack("<QQ", len(raw), len(compressed)) + compressed


def parse_link(blob: bytes) -> LinkArchive:
    if len(blob) < LINK_FIXED_HEADER_SIZE or blob[:4] != LINK_MAGIC:
        raise LinkError("not a LINK archive")
    count, version, reserved = struct.unpack_from("<III", blob, 4)
    header_size = LINK_FIXED_HEADER_SIZE + count * 8
    if header_size > len(blob):
        raise LinkError(f"LINK table ends at 0x{header_size:X}, beyond file size")

    pairs = [struct.unpack_from("<II", blob, LINK_FIXED_HEADER_SIZE + i * 8) for i in range(count)]
    if not pairs:
        return LinkArchive(version, reserved, blob[:16], blob[16:], (), len(blob))

    first_offset = pairs[0][0]
    if first_offset < header_size:
        raise LinkError(f"first entry offset 0x{first_offset:X} overlaps the table")
    if first_offset > len(blob):
        raise LinkError("first entry starts beyond end of file")

    entries: list[LinkEntry] = []
    previous_offset = -1
    for index, (offset, stored_size) in enumerate(pairs):
        if offset < previous_offset:
            raise LinkError(f"entry {index} offsets are not monotonic")
        end = offset + stored_size
        next_offset = pairs[index + 1][0] if index + 1 < count else len(blob)
        # Some archives retain trailing empty table slots whose virtual offsets
        # are EOF, EOF+4, EOF+8, ... without storing physical trailer bytes.
        # They are valid only as a trailing run of zero-sized entries.
        is_virtual_empty = offset >= len(blob) and stored_size == 0
        if is_virtual_empty:
            if any(size != 0 for _, size in pairs[index:]):
                raise LinkError(f"entry {index} is outside the file")
            entries.append(LinkEntry(index, offset, 0, b"", b""))
            previous_offset = offset
            continue
        if offset > len(blob) or end > len(blob):
            raise LinkError(f"entry {index} is outside the file")
        if end > next_offset:
            raise LinkError(f"entry {index} overlaps entry {index + 1}")
        physical_next = min(next_offset, len(blob))
        entries.append(LinkEntry(index, offset, stored_size, blob[offset:end], blob[end:physical_next]))
        previous_offset = offset

    return LinkArchive(
        version=version,
        reserved=reserved,
        fixed_header=blob[:16],
        pre_data_padding=blob[header_size:first_offset],
        entries=tuple(entries),
        original_size=len(blob),
    )


def rebuild_link(archive: LinkArchive, replacements: dict[int, bytes] | None = None) -> bytes:
    replacements = replacements or {}
    count = len(archive.entries)
    table_size = LINK_FIXED_HEADER_SIZE + count * 8
    output = bytearray(archive.fixed_header)
    output.extend(b"\0" * (count * 8))
    output.extend(archive.pre_data_padding)
    if len(output) < table_size:
        raise LinkError("internal error while rebuilding LINK table")

    new_pairs: list[tuple[int, int]] = []
    for entry in archive.entries:
        is_virtual_empty = entry.offset >= archive.original_size and entry.stored_size == 0
        if is_virtual_empty:
            if entry.index in replacements and replacements[entry.index]:
                raise LinkError("cannot materialize a virtual trailing empty LINK entry")
            virtual_delta = entry.offset - archive.original_size
            new_pairs.append((len(output) + virtual_delta, 0))
            continue
        data = replacements.get(entry.index, entry.data)
        offset = len(output)
        if offset > 0xFFFFFFFF or len(data) > 0xFFFFFFFF:
            raise LinkError("LINK uses 32-bit offsets/sizes; rebuilt archive is too large")
        new_pairs.append((offset, len(data)))
        output.extend(data)
        output.extend(entry.gap_after)

    for index, (offset, stored_size) in enumerate(new_pairs):
        struct.pack_into("<II", output, LINK_FIXED_HEADER_SIZE + index * 8, offset, stored_size)
    return bytes(output)


def classify_plain(blob: bytes) -> str:
    signatures = (
        (b"LINK", "LINK"),
        (b"_N1G0000", "G1N"),
        (b"GT1G", "G1T"),
        (b"G1M_", "G1M"),
        (b"DDS ", "DDS"),
        (b"RIFF", "RIFF"),
        (b"\x89PNG\r\n\x1a\n", "PNG"),
    )
    for signature, name in signatures:
        if blob.startswith(signature):
            return name
    return "raw"


def inspect_blob(blob: bytes, *, probe_lz4: bool, max_probe_size: int) -> dict[str, object]:
    result: dict[str, object] = {"type": classify_plain(blob), "stored_size": len(blob)}
    if result["type"] != "raw":
        return result
    try:
        header = parse_wrapper_header(blob)
    except LZ4Error:
        return result

    result.update(
        {
            "type": "raw-lz4-wrapper",
            "wrapper_prefix": header.prefix.hex(" ").upper(),
            "compressed_size": header.compressed_size,
            "uncompressed_size": header.uncompressed_size,
        }
    )
    if header.uncompressed_size:
        result["ratio"] = round(header.compressed_size / header.uncompressed_size, 6)
    if probe_lz4 and header.uncompressed_size <= max_probe_size:
        try:
            _, raw = decompress_wrapper(blob)
        except LZ4Error as exc:
            result["lz4_valid"] = False
            result["lz4_error"] = str(exc)
        else:
            inner = classify_plain(raw)
            result["lz4_valid"] = True
            result["inner_type"] = inner
            result["type"] = f"raw-lz4:{inner}"
    return result


def wrapper_dict(header: WrapperHeader, file_size: int) -> dict[str, object]:
    return {
        "file_size": file_size,
        "prefix_hex": header.prefix.hex(" ").upper(),
        "word0_u32": header.word0_u32,
        "marker_u16": header.marker_u16,
        "tag_u16": header.tag_u16,
        "param_u32": header.param_u32,
        "uncompressed_size": header.uncompressed_size,
        "compressed_size": header.compressed_size,
        "payload_size": file_size - WRAPPER_SIZE,
        "ratio": (
            round(header.compressed_size / header.uncompressed_size, 6)
            if header.uncompressed_size
            else None
        ),
    }


def print_mapping(mapping: dict[str, object]) -> None:
    for key, value in mapping.items():
        if key.endswith("_size") or key in {"word0_u32", "param_u32"}:
            if isinstance(value, int):
                print(f"{key}={value} (0x{value:X})")
                continue
        print(f"{key}={value}")


def write_output(path: Path, data: bytes, *, inputs: Sequence[Path]) -> None:
    resolved = path.resolve()
    for input_path in inputs:
        if resolved == input_path.resolve():
            raise ValueError(f"refusing to overwrite input file: {input_path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def cmd_detect(args: argparse.Namespace) -> int:
    path = Path(args.input)
    blob = path.read_bytes()
    info = inspect_blob(blob, probe_lz4=True, max_probe_size=args.max_probe_size)
    info["path"] = str(path)
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print_mapping(info)
    return 0


def cmd_header(args: argparse.Namespace) -> int:
    path = Path(args.input)
    blob = path.read_bytes()
    header = parse_wrapper_header(blob)
    info = {"path": str(path), **wrapper_dict(header, len(blob))}
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print_mapping(info)
    return 0


def cmd_decompress(args: argparse.Namespace) -> int:
    source = Path(args.input)
    output = Path(args.output)
    blob = source.read_bytes()
    header, raw = decompress_wrapper(blob)
    write_output(output, raw, inputs=(source,))
    print(f"input={source}")
    print(f"output={output}")
    print(f"compressed_size={header.compressed_size}")
    print(f"uncompressed_size={len(raw)}")
    print(f"sha256={hashlib.sha256(raw).hexdigest()}")
    return 0


def cmd_recompress(args: argparse.Namespace) -> int:
    source = Path(args.input)
    template = Path(args.template)
    output = Path(args.output)
    raw = source.read_bytes()
    template_blob = template.read_bytes()
    wrapped = recompress_wrapper(raw, template_blob)
    write_output(output, wrapped, inputs=(source, template))
    _, decoded = decompress_wrapper(wrapped)
    if decoded != raw:
        raise LZ4Error("internal recompression round-trip mismatch")
    header = parse_wrapper_header(wrapped)
    print(f"input={source}")
    print(f"template={template}")
    print(f"output={output}")
    print(f"uncompressed_size={len(raw)}")
    print(f"compressed_size={header.compressed_size}")
    print("roundtrip=OK")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    source = Path(args.input)
    blob = source.read_bytes()
    old_header, raw = decompress_wrapper(blob)
    rebuilt = recompress_wrapper(raw, old_header)
    new_header, decoded = decompress_wrapper(rebuilt)
    if decoded != raw:
        raise LZ4Error("decompress -> recompress -> decompress mismatch")
    print(f"input={source}")
    print(f"original_compressed_size={old_header.compressed_size}")
    print(f"literal_only_compressed_size={new_header.compressed_size}")
    print(f"uncompressed_size={len(raw)}")
    print(f"sha256={hashlib.sha256(raw).hexdigest()}")
    print("roundtrip=OK")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    path = Path(args.archive)
    blob = path.read_bytes()
    archive = parse_link(blob)
    rows: list[dict[str, object]] = []
    for entry in archive.entries:
        info = inspect_blob(
            entry.data,
            probe_lz4=not args.no_decompress_probe,
            max_probe_size=args.max_probe_size,
        )
        row: dict[str, object] = {
            "index": entry.index,
            "offset": entry.offset,
            "stored_size": entry.stored_size,
            "gap_size": len(entry.gap_after),
            "trailer_hex": entry.gap_after.hex(" ").upper(),
        }
        row.update(info)
        rows.append(row)

    if args.json:
        print(
            json.dumps(
                {
                    "path": str(path),
                    "count": len(archive.entries),
                    "version": archive.version,
                    "reserved": archive.reserved,
                    "table_size": LINK_FIXED_HEADER_SIZE + 8 * len(archive.entries),
                    "entries": rows,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(f"path={path}")
    print(f"count={len(rows)} version={archive.version} reserved={archive.reserved}")
    print("idx  offset      stored      gap  type                 unpacked    packed")
    for row in rows:
        unpacked = row.get("uncompressed_size", "-")
        packed = row.get("compressed_size", "-")
        print(
            f"{row['index']:>3}  0x{row['offset']:08X}  {row['stored_size']:>10}  "
            f"{row['gap_size']:>3}  {str(row['type']):<20} {str(unpacked):>10} {str(packed):>10}"
        )
    return 0


def cmd_extract_entry(args: argparse.Namespace) -> int:
    archive_path = Path(args.archive)
    output = Path(args.output)
    archive = parse_link(archive_path.read_bytes())
    if args.index < 0 or args.index >= len(archive.entries):
        raise LinkError(f"entry index out of range: {args.index}")
    data = archive.entries[args.index].data
    if args.decompress:
        _, data = decompress_wrapper(data)
    write_output(output, data, inputs=(archive_path,))
    print(f"archive={archive_path}")
    print(f"index={args.index}")
    print(f"output={output}")
    print(f"size={len(data)}")
    print(f"type={classify_plain(data)}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    return 0


def cmd_repack_entry(args: argparse.Namespace) -> int:
    archive_path = Path(args.archive)
    replacement_path = Path(args.replacement)
    output = Path(args.output)
    original_blob = archive_path.read_bytes()
    archive = parse_link(original_blob)
    if args.index < 0 or args.index >= len(archive.entries):
        raise LinkError(f"entry index out of range: {args.index}")

    replacement = replacement_path.read_bytes()
    if args.compress:
        template_entry = archive.entries[args.index].data
        replacement = recompress_wrapper(replacement, template_entry)
        _, check = decompress_wrapper(replacement)
        if check != replacement_path.read_bytes():
            raise LZ4Error("replacement wrapper verification failed")

    rebuilt = rebuild_link(archive, {args.index: replacement})
    # Always validate the new table and the exact replacement bytes before write.
    parsed = parse_link(rebuilt)
    if parsed.entries[args.index].data != replacement:
        raise LinkError("rebuilt LINK replacement verification failed")
    write_output(output, rebuilt, inputs=(archive_path, replacement_path))
    print(f"archive={archive_path}")
    print(f"index={args.index}")
    print(f"replacement={replacement_path}")
    print(f"output={output}")
    print(f"old_entry_size={archive.entries[args.index].stored_size}")
    print(f"new_entry_size={len(replacement)}")
    print(f"old_archive_size={len(original_blob)}")
    print(f"new_archive_size={len(rebuilt)}")
    print("verify=OK")
    return 0


def cmd_verify_link(args: argparse.Namespace) -> int:
    path = Path(args.archive)
    blob = path.read_bytes()
    archive = parse_link(blob)
    rebuilt = rebuild_link(archive)
    if rebuilt != blob:
        raise LinkError("parse -> rebuild was not byte-identical")
    print(f"archive={path}")
    print(f"count={len(archive.entries)}")
    print(f"sha256={hashlib.sha256(blob).hexdigest()}")
    print("byte_identical_roundtrip=OK")
    return 0


def add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Print JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    detect = sub.add_parser("detect", help="Detect LINK/raw-LZ4/plain resource type")
    detect.add_argument("input")
    detect.add_argument("--max-probe-size", type=lambda x: int(x, 0), default=128 * 1024 * 1024)
    add_json_flag(detect)
    detect.set_defaults(func=cmd_detect)

    header = sub.add_parser("header", help="Show the 24-byte raw-LZ4 wrapper header")
    header.add_argument("input")
    add_json_flag(header)
    header.set_defaults(func=cmd_header)

    decompress = sub.add_parser("decompress", help="Decompress a wrapped raw LZ4 resource")
    decompress.add_argument("input")
    decompress.add_argument("output")
    decompress.set_defaults(func=cmd_decompress)

    recompress = sub.add_parser(
        "recompress", help="Wrap raw input using literal-only LZ4 and an original header template"
    )
    recompress.add_argument("input", help="Raw/decompressed input")
    recompress.add_argument("output")
    recompress.add_argument("--template", required=True, help="Original wrapped file (prefix donor)")
    recompress.set_defaults(func=cmd_recompress)

    verify = sub.add_parser("verify", help="In-memory wrapper round-trip verification")
    verify.add_argument("input")
    verify.set_defaults(func=cmd_verify)

    list_cmd = sub.add_parser("list", help="List a LINK archive table and inferred entry types")
    list_cmd.add_argument("archive")
    list_cmd.add_argument("--no-decompress-probe", action="store_true")
    list_cmd.add_argument("--max-probe-size", type=lambda x: int(x, 0), default=128 * 1024 * 1024)
    add_json_flag(list_cmd)
    list_cmd.set_defaults(func=cmd_list)

    extract = sub.add_parser("extract-entry", help="Extract one top-level LINK entry")
    extract.add_argument("archive")
    extract.add_argument("index", type=lambda x: int(x, 0))
    extract.add_argument("output")
    extract.add_argument("--decompress", action="store_true", help="Also remove its raw-LZ4 wrapper")
    extract.set_defaults(func=cmd_extract_entry)

    repack = sub.add_parser("repack-entry", help="Replace one top-level LINK entry and rebuild offsets")
    repack.add_argument("archive")
    repack.add_argument("index", type=lambda x: int(x, 0))
    repack.add_argument("replacement")
    repack.add_argument("output")
    repack.add_argument(
        "--compress",
        action="store_true",
        help="Replacement is decompressed data; raw-LZ4-wrap it using the old entry prefix",
    )
    repack.set_defaults(func=cmd_repack_entry)

    verify_link = sub.add_parser("verify-link", help="Require byte-identical LINK parse/rebuild")
    verify_link.add_argument("archive")
    verify_link.set_defaults(func=cmd_verify_link)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, LZ4Error, LinkError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
