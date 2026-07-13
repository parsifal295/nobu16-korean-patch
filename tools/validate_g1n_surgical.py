#!/usr/bin/env python3
"""Read-only structural and preservation validator for NOBU16 G1N fonts.

The validator deliberately does not rebuild a G1N.  It supports two narrowly
defined comparison policies:

* alias: only previously-unmapped uint16 codepoint-map cells may change, and
  they may only point at an existing glyph ordinal.  Every other byte must be
  identical to the stock file.
* append-tail: new ordinals are appended to each table, while the complete
  stock atlas remains a byte-identical prefix and only new pixel blocks are
  appended at EOF.  Table offsets, atlas offset, old records and file size
  must follow the format's insertion equations.

Only Python's standard library is used.  Files are opened in binary read-only
mode and this program has no write path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


MAGIC = b"_N1G0000"
FIXED_HEADER_SIZE = 0x20
MAP_ENTRIES = 0x10000
MAP_SIZE = MAP_ENTRIES * 2
RECORD_SIZE = 12
PALETTE_SIZE = 0x40  # sixteen little-endian ARGB uint32 values


class ValidationError(Exception):
    """Raised when a file cannot be parsed safely as the expected G1N form."""


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _i8(value: int) -> int:
    return value if value < 0x80 else value - 0x100


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _cp(codepoint: int) -> str:
    if 0x20 <= codepoint <= 0x7E:
        return f"U+{codepoint:04X}({chr(codepoint)!r})"
    return f"U+{codepoint:04X}"


@dataclass(frozen=True)
class GlyphRecord:
    ordinal: int
    raw: bytes
    width: int
    height: int
    x_offset: int
    baseline: int
    advance: int
    row_stride: int
    mirror_x_offset: int
    mirror_height: int
    pointer: int
    pixel_size: int

    @property
    def metric_bytes(self) -> bytes:
        return self.raw[:8]


@dataclass
class G1NTable:
    index: int
    offset: int
    end_offset: int
    mapping: tuple[int, ...]
    records: list[GlyphRecord]
    logical_atlas_start: int
    atlas_size: int
    pointer_bias: int
    map_sha256: str
    records_sha256: str
    mapped_nonzero: int
    duplicate_nonzero: int
    unreachable_nonzero_ordinals: list[int]
    pointer_errors: list[str] = field(default_factory=list)

    @property
    def record_count(self) -> int:
        return len(self.records)

    def codepoints_for_ordinal(self) -> dict[int, list[int]]:
        result: dict[int, list[int]] = {}
        for codepoint, ordinal in enumerate(self.mapping):
            if ordinal:
                result.setdefault(ordinal, []).append(codepoint)
        return result


@dataclass
class G1NFile:
    path: Path
    data: bytes
    declared_size: int
    header_size: int
    unknown: int
    atlas_offset: int
    palette_count: int
    table_count: int
    table_offsets: list[int]
    palette_blob: bytes
    tables: list[G1NTable]
    structural_errors: list[str]

    @property
    def sha256(self) -> str:
        return _sha256(self.data)

    @property
    def palette_sha256(self) -> str:
        return _sha256(self.palette_blob)

    @property
    def atlas_size(self) -> int:
        return len(self.data) - self.atlas_offset


@dataclass
class CompareResult:
    mode: str
    source: G1NFile
    candidate: G1NFile
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    changed_codepoints: dict[int, list[int]] = field(default_factory=dict)
    added_records: list[int] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_g1n(path: Path) -> G1NFile:
    """Parse a G1N without modifying it and retain raw preservation regions."""
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc

    if len(data) < FIXED_HEADER_SIZE:
        raise ValidationError(f"{path}: file is shorter than the fixed header")
    if data[:8] != MAGIC:
        raise ValidationError(f"{path}: signature is not {MAGIC!r}")

    declared_size = _u32(data, 0x08)
    header_size = _u32(data, 0x0C)
    unknown = _u32(data, 0x10)
    atlas_offset = _u32(data, 0x14)
    palette_count = _u32(data, 0x18)
    table_count = _u32(data, 0x1C)
    errors: list[str] = []

    if not 1 <= table_count <= 32:
        raise ValidationError(f"{path}: implausible table count {table_count}")
    pointer_end = FIXED_HEADER_SIZE + table_count * 4
    palette_end = pointer_end + palette_count * PALETTE_SIZE
    if palette_end > len(data):
        raise ValidationError(f"{path}: palette blob extends past EOF")
    table_offsets = [_u32(data, FIXED_HEADER_SIZE + 4 * i) for i in range(table_count)]
    palette_blob = data[pointer_end:palette_end]

    if declared_size != len(data):
        errors.append(f"declared size 0x{declared_size:X} != actual 0x{len(data):X}")
    if header_size != palette_end:
        errors.append(
            f"header size 0x{header_size:X} != pointer/palette end 0x{palette_end:X}"
        )
    if table_offsets[0] != header_size:
        errors.append(
            f"table 0 offset 0x{table_offsets[0]:X} != header size 0x{header_size:X}"
        )
    if table_offsets != sorted(table_offsets) or len(set(table_offsets)) != table_count:
        errors.append("table offsets are not strictly increasing")
    if not (header_size <= table_offsets[0] < atlas_offset <= len(data)):
        errors.append("header/table/atlas offsets are out of order or outside the file")

    tables: list[G1NTable] = []
    logical_atlas_start = 0
    for table_index, table_offset in enumerate(table_offsets):
        table_end = table_offsets[table_index + 1] if table_index + 1 < table_count else atlas_offset
        record_start = table_offset + MAP_SIZE
        if not (0 <= table_offset <= record_start <= table_end <= len(data)):
            raise ValidationError(
                f"{path}: table {table_index} map/record region is outside the file"
            )
        record_bytes = table_end - record_start
        if record_bytes % RECORD_SIZE:
            raise ValidationError(
                f"{path}: table {table_index} record region 0x{record_bytes:X} "
                f"is not divisible by {RECORD_SIZE}"
            )
        record_count = record_bytes // RECORD_SIZE
        if not 1 <= record_count <= 0x10000:
            raise ValidationError(
                f"{path}: table {table_index} has implausible record count {record_count}"
            )

        mapping = struct.unpack_from(f"<{MAP_ENTRIES}H", data, table_offset)
        bad_ordinal = next((value for value in mapping if value >= record_count), None)
        if bad_ordinal is not None:
            errors.append(
                f"table {table_index}: map ordinal {bad_ordinal} is outside "
                f"0..{record_count - 1}"
            )
        counts = Counter(value for value in mapping if value)
        unreachable = [ordinal for ordinal in range(1, record_count) if ordinal not in counts]
        duplicate_count = sum(count - 1 for count in counts.values() if count > 1)
        if unreachable:
            errors.append(
                f"table {table_index}: {len(unreachable)} nonzero record ordinal(s) "
                "are unreachable from the codepoint map"
            )

        records: list[GlyphRecord] = []
        local_pixel_offset = 0
        pointer_errors: list[str] = []
        first_pointer = _u32(data, record_start + 8)
        pointer_bias = first_pointer - logical_atlas_start
        for ordinal in range(record_count):
            offset = record_start + ordinal * RECORD_SIZE
            raw = data[offset : offset + RECORD_SIZE]
            width, height = raw[0], raw[1]
            x_offset, baseline = _i8(raw[2]), _i8(raw[3])
            advance, row_stride = raw[4], _i8(raw[5])
            mirror_x_offset, mirror_height = _i8(raw[6]), raw[7]
            pointer = struct.unpack_from("<I", raw, 8)[0]
            pixel_size = abs(row_stride) * height
            expected_pointer = logical_atlas_start + local_pixel_offset + pointer_bias
            if pointer != expected_pointer:
                pointer_errors.append(
                    f"ordinal {ordinal}: pointer 0x{pointer:X} != expected "
                    f"0x{expected_pointer:X}"
                )
            if width == 0 or height == 0 or row_stride == 0 or pixel_size == 0:
                errors.append(f"table {table_index} ordinal {ordinal}: zero-sized glyph record")
            if abs(row_stride) < (width + 1) // 2:
                errors.append(
                    f"table {table_index} ordinal {ordinal}: row stride {row_stride} "
                    f"is too small for width {width} at 4bpp"
                )
            if mirror_x_offset != x_offset or mirror_height != height:
                errors.append(
                    f"table {table_index} ordinal {ordinal}: mirrored metric bytes differ"
                )
            records.append(
                GlyphRecord(
                    ordinal=ordinal,
                    raw=raw,
                    width=width,
                    height=height,
                    x_offset=x_offset,
                    baseline=baseline,
                    advance=advance,
                    row_stride=row_stride,
                    mirror_x_offset=mirror_x_offset,
                    mirror_height=mirror_height,
                    pointer=pointer,
                    pixel_size=pixel_size,
                )
            )
            local_pixel_offset += pixel_size

        tables.append(
            G1NTable(
                index=table_index,
                offset=table_offset,
                end_offset=table_end,
                mapping=mapping,
                records=records,
                logical_atlas_start=logical_atlas_start,
                atlas_size=local_pixel_offset,
                pointer_bias=pointer_bias,
                map_sha256=_sha256(data[table_offset:record_start]),
                records_sha256=_sha256(data[record_start:table_end]),
                mapped_nonzero=sum(counts.values()),
                duplicate_nonzero=duplicate_count,
                unreachable_nonzero_ordinals=unreachable,
                pointer_errors=pointer_errors,
            )
        )
        logical_atlas_start += local_pixel_offset

    actual_atlas_size = len(data) - atlas_offset
    if logical_atlas_start != actual_atlas_size:
        errors.append(
            f"record-derived atlas size 0x{logical_atlas_start:X} != physical "
            f"atlas size 0x{actual_atlas_size:X}"
        )

    # Pixel pointers are atlas-relative in the game.  Table-contiguous order is
    # a useful property of stock files, but a surgical tail append intentionally
    # breaks that ordering while still covering the atlas exactly once.  Check
    # the stronger loader-relevant invariant: no pointer interval is out of
    # bounds, overlapping, or leaves a hole.
    intervals: list[tuple[int, int, int, int]] = []
    for table in tables:
        for record in table.records:
            intervals.append(
                (
                    record.pointer,
                    record.pointer + record.pixel_size,
                    table.index,
                    record.ordinal,
                )
            )
    intervals.sort()
    cursor = 0
    for start, end, table_index, ordinal in intervals:
        if start != cursor:
            relation = "overlap" if start < cursor else "gap"
            errors.append(
                f"atlas pointer {relation} before table {table_index} ordinal {ordinal}: "
                f"expected 0x{cursor:X}, got 0x{start:X}"
            )
            cursor = max(cursor, end)
        else:
            cursor = end
    if cursor != actual_atlas_size:
        errors.append(
            f"atlas pointer coverage ends at 0x{cursor:X}, physical atlas ends at "
            f"0x{actual_atlas_size:X}"
        )

    return G1NFile(
        path=path,
        data=data,
        declared_size=declared_size,
        header_size=header_size,
        unknown=unknown,
        atlas_offset=atlas_offset,
        palette_count=palette_count,
        table_count=table_count,
        table_offsets=table_offsets,
        palette_blob=palette_blob,
        tables=tables,
        structural_errors=errors,
    )


def _same_fixed_layout(source: G1NFile, candidate: G1NFile, result: CompareResult) -> None:
    checks = (
        (source.data[:8], candidate.data[:8], "signature"),
        (source.header_size, candidate.header_size, "header size"),
        (source.unknown, candidate.unknown, "unknown header field"),
        (source.palette_count, candidate.palette_count, "palette count"),
        (source.table_count, candidate.table_count, "table count"),
        (source.palette_blob, candidate.palette_blob, "palette blob"),
    )
    for stock_value, candidate_value, label in checks:
        if stock_value != candidate_value:
            result.errors.append(f"{label} changed")


def compare_alias(source: G1NFile, candidate: G1NFile) -> CompareResult:
    result = CompareResult(mode="alias", source=source, candidate=candidate)
    _same_fixed_layout(source, candidate, result)
    if len(source.data) != len(candidate.data):
        result.errors.append("alias candidate changed file size")
    if source.declared_size != candidate.declared_size:
        result.errors.append("alias candidate changed declared file size")
    if source.atlas_offset != candidate.atlas_offset:
        result.errors.append("alias candidate changed atlas offset")
    if source.table_offsets != candidate.table_offsets:
        result.errors.append("alias candidate changed table offsets")
    if source.table_count != candidate.table_count:
        return result

    for stock_table, test_table in zip(source.tables, candidate.tables):
        changed: list[int] = []
        if stock_table.record_count != test_table.record_count:
            result.errors.append(f"table {stock_table.index}: alias changed record count")
            continue
        for codepoint, (stock_ordinal, test_ordinal) in enumerate(
            zip(stock_table.mapping, test_table.mapping)
        ):
            if stock_ordinal == test_ordinal:
                continue
            changed.append(codepoint)
            if stock_ordinal != 0:
                result.errors.append(
                    f"table {stock_table.index} {_cp(codepoint)}: existing mapping "
                    f"{stock_ordinal} changed to {test_ordinal}"
                )
            elif not 1 <= test_ordinal < stock_table.record_count:
                result.errors.append(
                    f"table {stock_table.index} {_cp(codepoint)}: alias target "
                    f"{test_ordinal} is not an existing nonzero ordinal"
                )
        result.changed_codepoints[stock_table.index] = changed

        stock_record_region = source.data[
            stock_table.offset + MAP_SIZE : stock_table.end_offset
        ]
        test_record_region = candidate.data[
            test_table.offset + MAP_SIZE : test_table.end_offset
        ]
        if stock_record_region != test_record_region:
            result.errors.append(f"table {stock_table.index}: glyph records changed")

    if source.data[source.atlas_offset :] != candidate.data[candidate.atlas_offset :]:
        result.errors.append("alias candidate changed atlas bytes")
    if not any(result.changed_codepoints.values()):
        result.warnings.append("candidate is byte-identical/no-op; no aliases were added")
    _check_changed_sets(result)
    return result


def compare_append_tail(source: G1NFile, candidate: G1NFile) -> CompareResult:
    result = CompareResult(mode="append-tail", source=source, candidate=candidate)
    _same_fixed_layout(source, candidate, result)
    if source.table_count != candidate.table_count:
        return result

    deltas = [
        candidate.tables[i].record_count - source.tables[i].record_count
        for i in range(source.table_count)
    ]
    result.added_records = deltas
    if any(delta < 0 for delta in deltas):
        result.errors.append(f"record count decreased: {deltas}")
        return result
    if not any(deltas):
        result.errors.append("append mode selected but no records were appended")

    expected_table_offsets: list[int] = []
    preceding_record_growth = 0
    for table in source.tables:
        expected_table_offsets.append(table.offset + preceding_record_growth)
        preceding_record_growth += deltas[table.index] * RECORD_SIZE
    if candidate.table_offsets != expected_table_offsets:
        result.errors.append(
            "table offsets do not match stock_offset + 12 * prior_appended_records: "
            f"expected {[hex(v) for v in expected_table_offsets]}, got "
            f"{[hex(v) for v in candidate.table_offsets]}"
        )
    expected_atlas_offset = source.atlas_offset + RECORD_SIZE * sum(deltas)
    if candidate.atlas_offset != expected_atlas_offset:
        result.errors.append(
            f"atlas offset 0x{candidate.atlas_offset:X} != expected "
            f"0x{expected_atlas_offset:X}"
        )

    added_pixel_sizes = [
        sum(record.pixel_size for record in candidate.tables[i].records[source.tables[i].record_count :])
        for i in range(source.table_count)
    ]
    expected_file_size = (
        len(source.data) + RECORD_SIZE * sum(deltas) + sum(added_pixel_sizes)
    )
    if len(candidate.data) != expected_file_size:
        result.errors.append(
            f"candidate size 0x{len(candidate.data):X} != expected 0x{expected_file_size:X}"
        )
    if candidate.declared_size != len(candidate.data):
        result.errors.append("candidate declared file size is not its actual size")

    stock_atlas = source.data[source.atlas_offset :]
    candidate_atlas_prefix = candidate.data[
        candidate.atlas_offset : candidate.atlas_offset + len(stock_atlas)
    ]
    if candidate_atlas_prefix != stock_atlas:
        result.errors.append("complete stock atlas is not a byte-identical candidate prefix")

    tail_cursor = source.atlas_size
    for stock_table, test_table in zip(source.tables, candidate.tables):
        changed: list[int] = []
        new_ordinal_counts: Counter[int] = Counter()
        for codepoint, (stock_ordinal, test_ordinal) in enumerate(
            zip(stock_table.mapping, test_table.mapping)
        ):
            if stock_ordinal == test_ordinal:
                continue
            changed.append(codepoint)
            if stock_ordinal != 0:
                result.errors.append(
                    f"table {stock_table.index} {_cp(codepoint)}: existing mapping "
                    f"{stock_ordinal} changed to {test_ordinal}"
                )
            elif not stock_table.record_count <= test_ordinal < test_table.record_count:
                result.errors.append(
                    f"table {stock_table.index} {_cp(codepoint)}: new mapping ordinal "
                    f"{test_ordinal} is outside appended range "
                    f"{stock_table.record_count}..{test_table.record_count - 1}"
                )
            else:
                new_ordinal_counts[test_ordinal] += 1
        result.changed_codepoints[stock_table.index] = changed

        expected_new_ordinals = set(range(stock_table.record_count, test_table.record_count))
        mapped_new_ordinals = set(new_ordinal_counts)
        if mapped_new_ordinals != expected_new_ordinals:
            missing = sorted(expected_new_ordinals - mapped_new_ordinals)
            extra = sorted(mapped_new_ordinals - expected_new_ordinals)
            result.errors.append(
                f"table {stock_table.index}: appended ordinal coverage mismatch "
                f"(missing={missing[:8]}, extra={extra[:8]})"
            )
        aliased_new = sorted(ordinal for ordinal, count in new_ordinal_counts.items() if count != 1)
        if aliased_new:
            result.errors.append(
                f"table {stock_table.index}: appended ordinals are not one-codepoint/one-glyph: "
                f"{aliased_new[:8]}"
            )

        for ordinal in range(stock_table.record_count):
            stock_record = stock_table.records[ordinal]
            test_record = test_table.records[ordinal]
            if stock_record.raw != test_record.raw:
                result.errors.append(
                    f"table {stock_table.index} ordinal {ordinal}: stock record bytes changed"
                )
                break

        for record in test_table.records[stock_table.record_count :]:
            if record.pointer != tail_cursor:
                result.errors.append(
                    f"table {stock_table.index} ordinal {record.ordinal}: appended pixel "
                    f"pointer 0x{record.pointer:X} != tail cursor 0x{tail_cursor:X}"
                )
            physical = candidate.atlas_offset + record.pointer
            pixels = candidate.data[physical : physical + record.pixel_size]
            if len(pixels) != record.pixel_size:
                result.errors.append(
                    f"table {stock_table.index} ordinal {record.ordinal}: pixel block is truncated"
                )
            elif not any(pixels):
                result.errors.append(
                    f"table {stock_table.index} ordinal {record.ordinal}: appended glyph is blank"
                )
            tail_cursor += record.pixel_size

    if tail_cursor != candidate.atlas_size:
        result.errors.append(
            f"appended tail ends at 0x{tail_cursor:X}, candidate atlas ends at "
            f"0x{candidate.atlas_size:X}"
        )

    _check_changed_sets(result)
    return result


def _check_changed_sets(result: CompareResult) -> None:
    if len(result.changed_codepoints) < 2:
        return
    sets = {index: set(values) for index, values in result.changed_codepoints.items()}
    first_index = min(sets)
    first = sets[first_index]
    for index in sorted(sets):
        if sets[index] != first:
            result.errors.append(
                f"changed codepoint set differs between table {first_index} and table {index}"
            )


def compare_g1n(source: G1NFile, candidate: G1NFile, mode: str) -> CompareResult:
    if mode == "auto":
        same_counts = (
            source.table_count == candidate.table_count
            and all(
                left.record_count == right.record_count
                for left, right in zip(source.tables, candidate.tables)
            )
        )
        mode = "alias" if same_counts else "append"
    result = (
        compare_alias(source, candidate)
        if mode == "alias"
        else compare_append_tail(source, candidate)
    )
    if source.structural_errors:
        result.errors.extend(f"stock structural error: {item}" for item in source.structural_errors)
    if candidate.structural_errors:
        # Aliases intentionally produce duplicate map references, but duplicates are
        # informational and therefore never enter structural_errors.
        result.errors.extend(
            f"candidate structural error: {item}" for item in candidate.structural_errors
        )
    return result


def _parse_codepoints(text: str | None) -> set[int] | None:
    if text is None:
        return None
    result: set[int] = set()
    for token in text.replace(",", " ").split():
        upper = token.upper()
        if upper.startswith("U+"):
            value = int(token[2:], 16)
        elif upper.startswith("0X"):
            value = int(token, 16)
        elif len(token) == 1 and not token.isdecimal():
            value = ord(token)
        else:
            value = int(token, 10)
        if not 0 <= value < MAP_ENTRIES:
            raise argparse.ArgumentTypeError(f"codepoint out of BMP range: {token}")
        result.add(value)
    return result


def _enforce_expected_codepoints(result: CompareResult, expected: set[int] | None) -> None:
    if expected is None:
        return
    for table_index, actual_values in result.changed_codepoints.items():
        actual = set(actual_values)
        if actual != expected:
            missing = ", ".join(_cp(value) for value in sorted(expected - actual)) or "none"
            extra = ", ".join(_cp(value) for value in sorted(actual - expected)) or "none"
            result.errors.append(
                f"table {table_index}: changed codepoints do not match --expect-codepoints "
                f"(missing: {missing}; extra: {extra})"
            )


def inspect_dict(font: G1NFile) -> dict[str, object]:
    return {
        "path": str(font.path),
        "sha256": font.sha256,
        "actual_size": len(font.data),
        "declared_size": font.declared_size,
        "header_size": font.header_size,
        "unknown": font.unknown,
        "atlas_offset": font.atlas_offset,
        "atlas_size": font.atlas_size,
        "palette_count": font.palette_count,
        "palette_sha256": font.palette_sha256,
        "table_count": font.table_count,
        "structural_errors": font.structural_errors,
        "tables": [
            {
                "index": table.index,
                "offset": table.offset,
                "end_offset": table.end_offset,
                "record_count": table.record_count,
                "mapped_nonzero": table.mapped_nonzero,
                "duplicate_nonzero": table.duplicate_nonzero,
                "logical_atlas_start": table.logical_atlas_start,
                "atlas_size": table.atlas_size,
                "pointer_bias": table.pointer_bias,
                "pixel_sizes": sorted({record.pixel_size for record in table.records}),
                "row_strides": sorted({record.row_stride for record in table.records}),
                "pixel_size_counts": dict(
                    sorted(Counter(record.pixel_size for record in table.records).items())
                ),
                "row_stride_counts": dict(
                    sorted(Counter(record.row_stride for record in table.records).items())
                ),
                "map_sha256": table.map_sha256,
                "records_sha256": table.records_sha256,
                "pointer_error_count": len(table.pointer_errors),
            }
            for table in font.tables
        ],
    }


def compare_dict(result: CompareResult) -> dict[str, object]:
    return {
        "ok": result.ok,
        "mode": result.mode,
        "source": inspect_dict(result.source),
        "candidate": inspect_dict(result.candidate),
        "added_records": result.added_records,
        "changed_codepoints": {
            str(index): [f"U+{value:04X}" for value in values]
            for index, values in result.changed_codepoints.items()
        },
        "errors": result.errors,
        "warnings": result.warnings,
    }


def print_inspect(font: G1NFile) -> None:
    status = "PASS" if not font.structural_errors else "FAIL"
    print(f"[{status}] {font.path}")
    print(
        f"  sha256={font.sha256} size=0x{len(font.data):X} "
        f"header=0x{font.header_size:X} atlas=0x{font.atlas_offset:X}+0x{font.atlas_size:X}"
    )
    print(
        f"  unknown=0x{font.unknown:X} palettes={font.palette_count} "
        f"palette_sha256={font.palette_sha256} tables={font.table_count}"
    )
    for table in font.tables:
        size_counts = Counter(record.pixel_size for record in table.records)
        stride_counts = Counter(record.row_stride for record in table.records)
        sizes = ",".join(
            f"0x{value:X}x{count}" for value, count in sorted(size_counts.items())
        )
        strides = ",".join(
            f"{value}x{count}" for value, count in sorted(stride_counts.items())
        )
        print(
            f"  table[{table.index}] off=0x{table.offset:X} records={table.record_count} "
            f"mapped={table.mapped_nonzero} dup={table.duplicate_nonzero} "
            f"atlas=0x{table.logical_atlas_start:X}+0x{table.atlas_size:X} "
            f"bias={table.pointer_bias} pixel_sizes={sizes} row_strides={strides}"
        )
    for error in font.structural_errors:
        print(f"  ERROR: {error}")


def print_compare(result: CompareResult) -> None:
    print(f"[{'PASS' if result.ok else 'FAIL'}] mode={result.mode}")
    print(f"  stock={result.source.path} sha256={result.source.sha256}")
    print(f"  candidate={result.candidate.path} sha256={result.candidate.sha256}")
    if result.added_records:
        print(f"  appended_records={result.added_records}")
    for table_index in sorted(result.changed_codepoints):
        values = result.changed_codepoints[table_index]
        preview = ", ".join(_cp(value) for value in values[:16])
        if len(values) > 16:
            preview += f", ... (+{len(values) - 16})"
        print(f"  table[{table_index}] changed_codepoints={len(values)}: {preview}")
    for warning in result.warnings:
        print(f"  WARNING: {warning}")
    for error in result.errors:
        print(f"  ERROR: {error}")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stock", type=Path, help="stock/original decompressed G1N")
    parser.add_argument(
        "candidate",
        type=Path,
        nargs="?",
        help="candidate G1N; omit for read-only structural inspection",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "alias", "append", "append-tail"),
        default="auto",
        help="comparison policy (append is an alias for append-tail)",
    )
    parser.add_argument(
        "--expect-codepoints",
        metavar="LIST",
        help="comma/space separated BMP values (U+AC00, 0xAC00, decimal, or literal char)",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        expected = _parse_codepoints(args.expect_codepoints)
        stock = parse_g1n(args.stock)
        if args.candidate is None:
            if args.json:
                print(json.dumps(inspect_dict(stock), ensure_ascii=False, indent=2))
            else:
                print_inspect(stock)
            return 0 if not stock.structural_errors else 1

        candidate = parse_g1n(args.candidate)
        result = compare_g1n(stock, candidate, args.mode)
        _enforce_expected_codepoints(result, expected)
        if args.json:
            print(json.dumps(compare_dict(result), ensure_ascii=False, indent=2))
        else:
            print_compare(result)
        return 0 if result.ok else 1
    except (ValidationError, OSError, struct.error, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
