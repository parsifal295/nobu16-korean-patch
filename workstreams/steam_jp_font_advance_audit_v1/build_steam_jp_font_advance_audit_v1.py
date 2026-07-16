#!/usr/bin/env python3
"""Audit Switch v2.2 -> v2.3 Korean G1N advance changes for Steam JP.

This is deliberately an *audit only*.  It reads two third-party Switch
release ZIPs and the already-installed Steam-JP ``RES_JP/res_lang.bin``
candidate, emits source-free metric evidence, and never writes to a game
file.  It does not copy Switch pixels, font data, or an entire Switch archive.

The format evidence matters here: the Switch v2.3 optimizer uses one coherent
G1N *layout triplet*: byte 0 (visible width), byte 4 (advance), and byte 5
(negative 4bpp row stride).  It leaves maps and pointers intact, but it also
re-packs each affected atlas allocation after a glyph-specific horizontal
crop.  A future PC candidate may use that policy only after proving that the
same three fields remain internally consistent and that the newly narrow width
does not crop the independently rasterized PC glyph pixels.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import struct
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TOOLS_LZ4 = REPO_ROOT / "tools" / "nobu16_lz4.py"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
G1N_MAGIC = b"_N1G0000"
MAP_ENTRIES = 0x10000
MAP_SIZE = MAP_ENTRIES * 2
RECORD_SIZE = 12
TARGET_OUTERS = (6, 7)


class AuditError(ValueError):
    """Raised for a malformed or unsupported audit input."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_codepoint_hash(codepoints: Iterable[int]) -> str:
    return sha256(",".join(f"U+{codepoint:04X}" for codepoint in sorted(set(codepoints))).encode("ascii"))


def contiguous_ranges(codepoints: Iterable[int]) -> list[str]:
    ordered = sorted(set(codepoints))
    if not ordered:
        return []
    result: list[str] = []
    first = previous = ordered[0]
    for codepoint in ordered[1:]:
        if codepoint == previous + 1:
            previous = codepoint
            continue
        result.append(
            f"U+{first:04X}" if first == previous else f"U+{first:04X}-U+{previous:04X}"
        )
        first = previous = codepoint
    result.append(f"U+{first:04X}" if first == previous else f"U+{first:04X}-U+{previous:04X}")
    return result


def compact_range_summary(codepoints: Iterable[int]) -> dict[str, Any]:
    """Give human-readable coverage without publishing a multi-thousand row dump.

    The count and canonical SHA-256 fields stored beside this summary are the
    exact coverage contract.  The head/tail merely make the evidence easy to
    inspect in a review.
    """

    ranges = contiguous_ranges(codepoints)
    if len(ranges) <= 24:
        return {"range_count": len(ranges), "ranges": ranges}
    return {
        "range_count": len(ranges),
        "head": ranges[:12],
        "tail": ranges[-12:],
    }


def load_lz4() -> Any:
    spec = importlib.util.spec_from_file_location("nobu16_lz4_advance_audit", TOOLS_LZ4)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot import LZ4 helper: {TOOLS_LZ4}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class G1NTable:
    index: int
    cell: int
    mapping: tuple[int, ...]
    records: tuple[bytes, ...]

    def codepoints_for_ordinal(self, ordinal: int) -> tuple[int, ...]:
        return tuple(index for index, mapped in enumerate(self.mapping) if mapped == ordinal)


@dataclass(frozen=True)
class G1N:
    raw: bytes
    tables: tuple[G1NTable, ...]
    atlas_offset: int


def parse_g1n(raw: bytes, label: str) -> G1N:
    if len(raw) < 0x20 or raw[:8] != G1N_MAGIC:
        raise AuditError(f"{label}: not a G1N")
    declared, header, _unknown, atlas, palettes, table_count = struct.unpack_from("<6I", raw, 8)
    if declared != len(raw):
        raise AuditError(f"{label}: declared size differs from payload")
    if not 1 <= table_count <= 32:
        raise AuditError(f"{label}: invalid table count")
    expected_header = 0x20 + table_count * 4 + palettes * 0x40
    if header != expected_header or not header <= atlas <= len(raw):
        raise AuditError(f"{label}: invalid header/atlas geometry")
    offsets = list(struct.unpack_from(f"<{table_count}I", raw, 0x20))
    if offsets[0] != header or offsets != sorted(offsets) or len(set(offsets)) != table_count:
        raise AuditError(f"{label}: invalid table offsets")
    tables: list[G1NTable] = []
    for index, offset in enumerate(offsets):
        end = offsets[index + 1] if index + 1 < len(offsets) else atlas
        record_start = offset + MAP_SIZE
        if record_start > end or (end - record_start) % RECORD_SIZE:
            raise AuditError(f"{label}: table {index} record geometry is invalid")
        mapping = struct.unpack_from(f"<{MAP_ENTRIES}H", raw, offset)
        records = tuple(
            raw[position : position + RECORD_SIZE]
            for position in range(record_start, end, RECORD_SIZE)
        )
        if not records or max(mapping) >= len(records):
            raise AuditError(f"{label}: table {index} map exceeds record count")
        cells = {record[field] for record in records for field in (1, 3, 7)}
        if len(cells) != 1:
            raise AuditError(f"{label}: table {index} does not have a uniform cell")
        cell = next(iter(cells))
        # Switch and PC use different raster grids (the Korean Switch font is
        # expected to be 24/36 while the PC route is 32/48).  Cell height is
        # evidence for an explicit rational scale, not a reason to discard a
        # structurally valid Switch table.
        if not 1 <= cell <= 255:
            raise AuditError(f"{label}: table {index} has an invalid cell {cell}")
        tables.append(G1NTable(index, cell, tuple(mapping), records))
    return G1N(raw=raw, tables=tuple(tables), atlas_offset=atlas)


def extract_link_g1n(archive_blob: bytes, outer: int, label: str, lz4: Any) -> bytes:
    archive = lz4.parse_link(archive_blob)
    if lz4.rebuild_link(archive) != archive_blob:
        raise AuditError(f"{label}: LINK identity round-trip failed")
    if outer >= len(archive.entries):
        raise AuditError(f"{label}: missing outer /{outer}")
    try:
        _header, raw = lz4.decompress_wrapper(archive.entries[outer].data)
    except Exception as exc:  # the helper has its own format-specific exceptions
        raise AuditError(f"{label}: /{outer} cannot be decompressed as a wrapper") from exc
    parse_g1n(raw, f"{label} /{outer}")
    return raw


def switch_archive_from_zip(path: Path) -> bytes:
    if not path.is_file():
        raise AuditError(f"missing Switch ZIP: {path}")
    try:
        with zipfile.ZipFile(path) as source:
            info = source.getinfo(SWITCH_MEMBER)
            if info.is_dir():
                raise AuditError(f"{path}: expected resource member is a directory")
            return source.read(info)
    except KeyError as exc:
        raise AuditError(f"{path}: missing {SWITCH_MEMBER}") from exc
    except zipfile.BadZipFile as exc:
        raise AuditError(f"{path}: invalid ZIP") from exc


def inverse_map(table: G1NTable) -> dict[int, tuple[int, ...]]:
    values: dict[int, list[int]] = defaultdict(list)
    for codepoint, ordinal in enumerate(table.mapping):
        values[ordinal].append(codepoint)
    return {ordinal: tuple(codepoints) for ordinal, codepoints in values.items()}


def table_summary(table: G1NTable) -> dict[str, Any]:
    mapped = [codepoint for codepoint, ordinal in enumerate(table.mapping) if ordinal]
    hangul = [codepoint for codepoint in mapped if 0xAC00 <= codepoint <= 0xD7A3]
    advances = [table.records[ordinal][4] for ordinal in {table.mapping[cp] for cp in hangul}]
    return {
        "table": table.index,
        "cell": table.cell,
        "record_count": len(table.records),
        "mapped_codepoint_count": len(mapped),
        "hangul_codepoint_count": len(hangul),
        "hangul_codepoints_sha256": canonical_codepoint_hash(hangul),
        "hangul_advance_min": min(advances) if advances else None,
        "hangul_advance_max": max(advances) if advances else None,
        "hangul_uniform_advance": len(set(advances)) <= 1,
        "hangul_advance_histogram": {
            str(value): count for value, count in sorted(Counter(advances).items())
        },
    }


def delta_table(before: G1NTable, after: G1NTable, label: str) -> dict[str, Any]:
    if before.cell != after.cell or before.mapping != after.mapping or len(before.records) != len(after.records):
        raise AuditError(f"{label}: table topology/map changed; metric-only transfer is unsafe")
    before_inverse = inverse_map(before)
    after_inverse = inverse_map(after)
    if before_inverse != after_inverse:
        raise AuditError(f"{label}: map aliases changed; metric-only transfer is unsafe")
    changed_ordinals = [
        ordinal
        for ordinal, (left, right) in enumerate(zip(before.records, after.records, strict=True))
        if left != right
    ]
    byte_positions = Counter(
        position
        for ordinal in changed_ordinals
        for position, (left, right) in enumerate(
            zip(before.records[ordinal], after.records[ordinal], strict=True)
        )
        if left != right
    )
    codepoints = sorted(
        codepoint
        for ordinal in changed_ordinals
        for codepoint in before_inverse.get(ordinal, ())
    )
    hangul = [codepoint for codepoint in codepoints if 0xAC00 <= codepoint <= 0xD7A3]
    non_hangul = [codepoint for codepoint in codepoints if not 0xAC00 <= codepoint <= 0xD7A3]
    advance_deltas = Counter(
        after.records[ordinal][4] - before.records[ordinal][4] for ordinal in changed_ordinals
    )
    width_deltas = Counter(
        after.records[ordinal][0] - before.records[ordinal][0] for ordinal in changed_ordinals
    )
    layout_positions = {0, 4, 5}
    non_layout_metric_changed = any(position not in layout_positions for position in byte_positions)
    pointer_changed = any(position >= 8 for position in byte_positions)
    triplet_valid = all(
        after.records[ordinal][0] == after.records[ordinal][4]
        and after.records[ordinal][0] % 2 == 0
        and after.records[ordinal][5] == (-after.records[ordinal][0] // 2) % 256
        for ordinal in changed_ordinals
    )
    examples = []
    for ordinal in changed_ordinals[:16]:
        cps = before_inverse.get(ordinal, ())
        examples.append(
            {
                "ordinal": ordinal,
                "codepoints": [f"U+{codepoint:04X}" for codepoint in cps[:8]],
                "before_metric_hex": before.records[ordinal][:8].hex().upper(),
                "after_metric_hex": after.records[ordinal][:8].hex().upper(),
            }
        )
    return {
        "table": before.index,
        "cell": before.cell,
        "changed_record_count": len(changed_ordinals),
        "changed_codepoint_count": len(codepoints),
        "changed_codepoints_sha256": canonical_codepoint_hash(codepoints),
        "changed_codepoint_range_summary": compact_range_summary(codepoints),
        "changed_hangul_codepoint_count": len(hangul),
        "changed_hangul_codepoints_sha256": canonical_codepoint_hash(hangul),
        "changed_hangul_range_summary": compact_range_summary(hangul),
        "changed_non_hangul_codepoints": [f"U+{codepoint:04X}" for codepoint in non_hangul],
        "changed_byte_positions": {str(position): count for position, count in sorted(byte_positions.items())},
        "layout_triplet_byte_positions": [0, 4, 5],
        "only_width_advance_row_stride_triplet_changed": (
            not non_layout_metric_changed and triplet_valid
        ),
        "changed_triplet_internal_contract_valid": triplet_valid,
        "pointer_bytes_changed": pointer_changed,
        "advance_delta_histogram": {str(value): count for value, count in sorted(advance_deltas.items())},
        "storage_width_delta_histogram": {str(value): count for value, count in sorted(width_deltas.items())},
        "examples": examples,
    }


def g1n_non_metric_delta_summary(before: G1N, after: G1N, label: str) -> dict[str, Any]:
    """Prove whether Switch v2.3 touched pixels or only metric triplets."""

    if len(before.raw) != len(after.raw) or before.atlas_offset != after.atlas_offset:
        raise AuditError(f"{label}: G1N length/atlas offset changed; no metric-only transfer")
    allowed: set[int] = set()
    for table in before.tables:
        table_offset = struct.unpack_from("<I", before.raw, 0x20 + table.index * 4)[0]
        record_start = table_offset + MAP_SIZE
        for ordinal in range(len(table.records)):
            base = record_start + ordinal * RECORD_SIZE
            allowed.update((base, base + 4, base + 5))
    changed = [
        position
        for position, (left, right) in enumerate(zip(before.raw, after.raw, strict=True))
        if left != right
    ]
    outside = [position for position in changed if position not in allowed]
    atlas = [position for position in changed if position >= before.atlas_offset]
    return {
        "raw_size": len(before.raw),
        "raw_sha256_before": sha256(before.raw),
        "raw_sha256_after": sha256(after.raw),
        "changed_byte_count": len(changed),
        "changed_bytes_outside_width_advance_row_stride_triplets": len(outside),
        "changed_atlas_pixel_byte_count": len(atlas),
        "maps_headers_and_all_pixel_bytes_exact": not outside and not atlas,
    }


def signed_byte(value: int) -> int:
    return value - 256 if value >= 128 else value


def unpack_row(packed: bytes) -> tuple[int, ...]:
    return tuple(value for byte in packed for value in (byte >> 4, byte & 0x0F))


def g1n_row_pack_equivalence_summary(before: G1N, after: G1N, label: str) -> dict[str, Any]:
    """Test the concrete Switch v2.3 atlas repacking rule.

    Each original glyph allocation remains at the same pointer.  For an
    optimized glyph, the left ``new_stride`` bytes of each old row are copied
    consecutively at the start of that allocation, and the unused allocation
    tail is zeroed.  This is why changing metrics without repacking pixels is
    unsafe even though all pointer values remain unchanged.
    """

    before_entries: list[tuple[int, int, int, bytes]] = []
    after_entries: dict[tuple[int, int], bytes] = {}
    for table in before.tables:
        for ordinal, record in enumerate(table.records):
            before_entries.append((struct.unpack_from("<I", record, 8)[0], table.index, ordinal, record))
    for table in after.tables:
        for ordinal, record in enumerate(table.records):
            after_entries[(table.index, ordinal)] = record
    before_entries.sort()
    if len({entry[0] for entry in before_entries}) != len(before_entries):
        raise AuditError(f"{label}: duplicate G1N pointers are unsupported for row-pack proof")
    atlas_before = before.raw[before.atlas_offset :]
    atlas_after = after.raw[after.atlas_offset :]
    prefix_exact = 0
    zero_tail = 0
    changed = 0
    invalid = 0
    crop_alignment = Counter()
    for index, (pointer, table_index, ordinal, old_record) in enumerate(before_entries):
        new_record = after_entries[(table_index, ordinal)]
        if old_record == new_record:
            continue
        changed += 1
        next_pointer = (
            before_entries[index + 1][0] if index + 1 < len(before_entries) else len(atlas_before)
        )
        old_stride = abs(signed_byte(old_record[5]))
        new_stride = abs(signed_byte(new_record[5]))
        height = old_record[1]
        old_payload = old_stride * height
        new_payload = new_stride * height
        if (
            new_record[1] != height
            or new_stride > old_stride
            or pointer + old_payload > next_pointer
            or pointer + new_payload > next_pointer
        ):
            invalid += 1
            continue
        expected = b"".join(
            atlas_before[pointer + row * old_stride : pointer + row * old_stride + new_stride]
            for row in range(height)
        )
        if atlas_after[pointer : pointer + new_payload] == expected:
            prefix_exact += 1
        target_rows = tuple(
            unpack_row(atlas_after[pointer + row * new_stride : pointer + (row + 1) * new_stride])
            for row in range(height)
        )
        source_rows = tuple(
            unpack_row(atlas_before[pointer + row * old_stride : pointer + (row + 1) * old_stride])
            for row in range(height)
        )
        matched_alignment: str | None = None
        for reverse in (False, True):
            ordered_rows = tuple(reversed(source_rows)) if reverse else source_rows
            for x_offset in range(old_record[0] - new_record[0] + 1):
                if all(
                    target == source[x_offset : x_offset + new_record[0]]
                    for target, source in zip(target_rows, ordered_rows, strict=True)
                ):
                    matched_alignment = f"{'bottom_to_top' if reverse else 'top_to_bottom'}:x{x_offset}"
                    break
            if matched_alignment is not None:
                break
        crop_alignment[matched_alignment or "no_exact_crop"] += 1
        if not any(atlas_after[pointer + new_payload : next_pointer]):
            zero_tail += 1
    return {
        "changed_record_count": changed,
        "valid_narrowing_record_count": changed - invalid,
        "row_packed_prefix_exact_count": prefix_exact,
        "exact_source_crop_alignment_histogram": dict(sorted(crop_alignment.items())),
        "unused_allocation_tail_zeroed_count": zero_tail,
        "all_changed_records_follow_crop_and_row_pack_rule": (
            invalid == 0
            and crop_alignment.get("no_exact_crop", 0) == 0
            and zero_tail == changed
        ),
    }


def pc_transfer_summary(switch_after: G1N, pc: G1N, switch_outer: int, pc_outer: int) -> dict[str, Any]:
    if len(switch_after.tables) != len(pc.tables):
        raise AuditError(f"PC /{pc_outer}: table count differs from Switch /{switch_outer}")
    rows: list[dict[str, Any]] = []
    total_overlap = 0
    total_switch_only = 0
    total_pc_only = 0
    uniform_pc_advance = True
    for switch_table, pc_table in zip(switch_after.tables, pc.tables, strict=True):
        divisor = math.gcd(switch_table.cell, pc_table.cell)
        scale_numerator = pc_table.cell // divisor
        scale_denominator = switch_table.cell // divisor
        switch_hangul = {
            codepoint for codepoint, ordinal in enumerate(switch_table.mapping)
            if ordinal and 0xAC00 <= codepoint <= 0xD7A3
        }
        pc_hangul = {
            codepoint for codepoint, ordinal in enumerate(pc_table.mapping)
            if ordinal and 0xAC00 <= codepoint <= 0xD7A3
        }
        overlap = sorted(switch_hangul & pc_hangul)
        pc_advances = [pc_table.records[pc_table.mapping[codepoint]][4] for codepoint in overlap]
        switch_advances = [switch_table.records[switch_table.mapping[codepoint]][4] for codepoint in overlap]
        uniform_pc_advance = uniform_pc_advance and len(set(pc_advances)) <= 1
        total_overlap += len(overlap)
        total_switch_only += len(switch_hangul - pc_hangul)
        total_pc_only += len(pc_hangul - switch_hangul)
        rows.append(
            {
                "table": pc_table.index,
                "switch_cell": switch_table.cell,
                "pc_cell": pc_table.cell,
                "pc_per_switch_scale": {
                    "numerator": scale_numerator,
                    "denominator": scale_denominator,
                },
                "overlap_hangul_count": len(overlap),
                "overlap_hangul_sha256": canonical_codepoint_hash(overlap),
                "switch_only_hangul_count": len(switch_hangul - pc_hangul),
                "pc_only_hangul_count": len(pc_hangul - switch_hangul),
                "pc_before_advance_histogram": {
                    str(value): count for value, count in sorted(Counter(pc_advances).items())
                },
                "switch_v23_advance_histogram": {
                    str(value): count for value, count in sorted(Counter(switch_advances).items())
                },
                "required_metric_triplet_edits": sum(
                    left != right for left, right in zip(pc_advances, switch_advances, strict=True)
                ),
            }
        )
    return {
        "switch_outer": switch_outer,
        "pc_outer": pc_outer,
        "tables": rows,
        "overlap_hangul_count": total_overlap,
        "switch_only_hangul_count": total_switch_only,
        "pc_only_hangul_count": total_pc_only,
        "pc_overlap_hangul_advance_uniform_before": uniform_pc_advance,
        "direct_same_cell_triplet_transfer_permitted_by_geometry": all(
            row["switch_cell"] == row["pc_cell"] for row in rows
        ),
        "scaled_triplet_transfer_requires_explicit_rounding_contract": any(
            row["switch_cell"] != row["pc_cell"] for row in rows
        ),
    }


def pc_full_coverage_summary(
    switch_before: G1N, switch_after: G1N, pc: G1N, outer: int
) -> dict[str, Any]:
    """Show whether the full Switch v2.3 optimized set exists in PC maps.

    This deliberately covers the full 2,404 Korean (syllable + compatibility
    jamo) set plus the optimized space glyph rather than merely the characters
    that happen to occur in today's translated catalog.
    """

    if len(switch_before.tables) != len(switch_after.tables) or len(pc.tables) != len(switch_after.tables):
        raise AuditError(f"/{outer}: table count is not transferable")
    changed: set[int] = set()
    for before_table, after_table in zip(switch_before.tables, switch_after.tables, strict=True):
        inverse = inverse_map(before_table)
        for ordinal, (left, right) in enumerate(zip(before_table.records, after_table.records, strict=True)):
            if left != right:
                changed.update(inverse.get(ordinal, ()))
    hangul = {codepoint for codepoint in changed if 0xAC00 <= codepoint <= 0xD7A3}
    jamo = {codepoint for codepoint in changed if 0x3131 <= codepoint <= 0x3163}
    rows: list[dict[str, Any]] = []
    for pc_table in pc.tables:
        present = {codepoint for codepoint in changed if pc_table.mapping[codepoint] != 0}
        missing = sorted(changed - present)
        missing_hangul = [codepoint for codepoint in missing if 0xAC00 <= codepoint <= 0xD7A3]
        missing_jamo = [codepoint for codepoint in missing if 0x3131 <= codepoint <= 0x3163]
        rows.append(
            {
                "table": pc_table.index,
                "cell": pc_table.cell,
                "current_record_count": len(pc_table.records),
                "record_capacity": 0xFFFF,
                "record_capacity_remaining": 0xFFFF - len(pc_table.records),
                "optimized_codepoints_present": len(present),
                "optimized_codepoints_missing": len(missing),
                "missing_codepoints_sha256": canonical_codepoint_hash(missing),
                "missing_codepoint_range_summary": compact_range_summary(missing),
                "missing_hangul_syllable_count": len(missing_hangul),
                "missing_compatibility_jamo_count": len(missing_jamo),
                "full_switch_optimized_set_can_be_appended": len(missing) <= 0xFFFF - len(pc_table.records),
            }
        )
    return {
        "outer_entry": outer,
        "switch_v23_optimized_codepoint_count": len(changed),
        "switch_v23_optimized_codepoints_sha256": canonical_codepoint_hash(changed),
        "switch_v23_optimized_hangul_syllable_count": len(hangul),
        "switch_v23_optimized_compatibility_jamo_count": len(jamo),
        "switch_v23_optimized_space_included": 0x20 in changed,
        "pc_tables": rows,
    }


def audit(switch_v22_zip: Path, switch_v23_zip: Path, pc_res_lang: Path) -> dict[str, Any]:
    lz4 = load_lz4()
    v22_blob = switch_archive_from_zip(switch_v22_zip)
    v23_blob = switch_archive_from_zip(switch_v23_zip)
    if not pc_res_lang.is_file():
        raise AuditError(f"missing PC resource: {pc_res_lang}")
    pc_blob = pc_res_lang.read_bytes()
    rows: list[dict[str, Any]] = []
    all_layout_triplet_only = True
    changed_codepoints_union: set[int] = set()
    changed_hangul_union: set[int] = set()
    for outer in TARGET_OUTERS:
        v22_raw = extract_link_g1n(v22_blob, outer, f"Switch v2.2 {switch_v22_zip.name}", lz4)
        v23_raw = extract_link_g1n(v23_blob, outer, f"Switch v2.3 {switch_v23_zip.name}", lz4)
        pc_raw = extract_link_g1n(pc_blob, outer, f"Steam JP {pc_res_lang}", lz4)
        v22 = parse_g1n(v22_raw, f"Switch v2.2 /{outer}")
        v23 = parse_g1n(v23_raw, f"Switch v2.3 /{outer}")
        pc = parse_g1n(pc_raw, f"Steam JP /{outer}")
        deltas = [
            delta_table(before, after, f"Switch /{outer} table {before.index}")
            for before, after in zip(v22.tables, v23.tables, strict=True)
        ]
        non_metric_delta = g1n_non_metric_delta_summary(v22, v23, f"Switch /{outer}")
        row_pack = g1n_row_pack_equivalence_summary(v22, v23, f"Switch /{outer}")
        only_layout_triplet = all(
            not delta["changed_record_count"]
            or delta["only_width_advance_row_stride_triplet_changed"]
            for delta in deltas
        ) and bool(row_pack["all_changed_records_follow_crop_and_row_pack_rule"])
        all_layout_triplet_only = all_layout_triplet_only and only_layout_triplet
        for delta in deltas:
            changed_codepoints_union.update(
                int(value[2:], 16)
                for value in delta["changed_non_hangul_codepoints"]
            )
            # The report intentionally stores compact ranges rather than a
            # 2,000+ raw codepoint dump.  Reconstruct the source set from the
            # map for exact union evidence below.
        for before_table, after_table in zip(v22.tables, v23.tables, strict=True):
            inverse = inverse_map(before_table)
            for ordinal, (left, right) in enumerate(zip(before_table.records, after_table.records, strict=True)):
                if left != right:
                    for codepoint in inverse.get(ordinal, ()):
                        changed_codepoints_union.add(codepoint)
                        if 0xAC00 <= codepoint <= 0xD7A3:
                            changed_hangul_union.add(codepoint)
        rows.append(
            {
                "outer_entry": outer,
                "switch_v22_g1n_sha256": sha256(v22_raw),
                "switch_v23_g1n_sha256": sha256(v23_raw),
                "steam_jp_g1n_sha256": sha256(pc_raw),
                "switch_v22_tables": [table_summary(table) for table in v22.tables],
                "switch_v23_tables": [table_summary(table) for table in v23.tables],
                "steam_jp_tables": [table_summary(table) for table in pc.tables],
                "v22_to_v23_delta": deltas,
                "v22_to_v23_non_metric_delta": non_metric_delta,
                "v22_to_v23_row_pack_equivalence": row_pack,
                "v23_to_steam_jp_transfer": pc_transfer_summary(v23, pc, outer, outer),
                "full_switch_optimized_coverage_in_current_pc": pc_full_coverage_summary(
                    v22, v23, pc, outer
                ),
                "switch_delta_follows_metric_triplet_plus_crop_rowpack": only_layout_triplet,
            }
        )
    return {
        "schema": "nobu16.kr.steam-jp-font-advance-audit.v1",
        "public_source_free": True,
        "switch_archive_raw_copy": False,
        "installed_game_files_modified": False,
        "inputs": {
            "switch_v22_zip": {
                "name": switch_v22_zip.name,
                "size": switch_v22_zip.stat().st_size,
                "sha256": sha256_file(switch_v22_zip),
                "resource_member": SWITCH_MEMBER,
                "res_lang_size": len(v22_blob),
                "res_lang_sha256": sha256(v22_blob),
            },
            "switch_v23_zip": {
                "name": switch_v23_zip.name,
                "size": switch_v23_zip.stat().st_size,
                "sha256": sha256_file(switch_v23_zip),
                "resource_member": SWITCH_MEMBER,
                "res_lang_size": len(v23_blob),
                "res_lang_sha256": sha256(v23_blob),
            },
            "steam_jp_res_lang": {
                "logical_path": "RES_JP/res_lang.bin",
                "size": pc_res_lang.stat().st_size,
                "sha256": sha256_file(pc_res_lang),
            },
        },
        "outer_entries": rows,
        "conclusion": {
            "switch_v22_to_v23_changed_font_outers": list(TARGET_OUTERS),
            "changed_codepoint_count_unique": len(changed_codepoints_union),
            "changed_codepoints_sha256_unique": canonical_codepoint_hash(changed_codepoints_union),
            "changed_codepoint_range_summary_unique": compact_range_summary(changed_codepoints_union),
            "changed_hangul_codepoint_count_unique": len(changed_hangul_union),
            "changed_hangul_codepoints_sha256_unique": canonical_codepoint_hash(changed_hangul_union),
            "changed_hangul_range_summary_unique": compact_range_summary(changed_hangul_union),
            "all_switch_font_deltas_follow_metric_triplet_plus_crop_rowpack": all_layout_triplet_only,
            "safe_next_step": (
                "A PC candidate may edit the coherent raw G1N width/advance/row-stride "
                "triplet (bytes 0,4,5) together with crop-and-row-packed pixels inside the "
                "same glyph allocation, after per-route scale, rounding, and ink-clipping proof; "
                "preserve maps, bytes 1-3 and 6-11, LINK structure, and every non-font entry byte-for-byte."
                if all_layout_triplet_only
                else "Do not construct a PC candidate: the Switch delta changes fields outside the approved metric triplet."
            ),
            "unsupported_shortcut": "Do not copy Switch RES_JP/res_lang.bin, Switch G1N payloads, or Switch pixels into the Steam build.",
        },
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(encoded, encoding="utf-8", newline="\n")


def compact_public_projection(report: dict[str, Any]) -> dict[str, Any]:
    """Build the reviewed, source-free projection of a fresh full audit.

    ``audit.v1.json`` is intentionally compact: the full report contains
    table-by-table histograms and examples which are useful in ``tmp`` during
    a build but create noisy tracked metadata.  This function is the one
    canonical reduction.  Consequently ``--expected-compact`` can prove that
    the checked-in artifact was regenerated from exactly the same inputs,
    rather than being a manually copied summary that silently drifted.
    """

    conclusion = report["conclusion"]
    outer_rows = {row["outer_entry"]: row for row in report["outer_entries"]}
    if set(outer_rows) != set(TARGET_OUTERS):
        raise AuditError("compact projection: unexpected Switch font outer entries")

    non_hangul: set[int] = set()
    for row in outer_rows.values():
        for delta in row["v22_to_v23_delta"]:
            non_hangul.update(int(value[2:], 16) for value in delta["changed_non_hangul_codepoints"])
    compatibility_jamo = sum(0x3131 <= value <= 0x3163 for value in non_hangul)
    space_count = int(0x20 in non_hangul)
    if compatibility_jamo + space_count != len(non_hangul):
        raise AuditError("compact projection: unexpected non-Hangul optimized codepoint")

    def outer_projection(outer: int) -> dict[str, Any]:
        row = outer_rows[outer]
        deltas = row["v22_to_v23_delta"]
        non_metric = row["v22_to_v23_non_metric_delta"]
        row_pack = row["v22_to_v23_row_pack_equivalence"]
        if not row["switch_delta_follows_metric_triplet_plus_crop_rowpack"]:
            raise AuditError(f"compact projection: Switch /{outer} proof did not pass")
        if not row_pack["all_changed_records_follow_crop_and_row_pack_rule"]:
            raise AuditError(f"compact projection: Switch /{outer} row-pack proof did not pass")
        return {
            "cell_hierarchy": [table["cell"] for table in row["switch_v23_tables"]],
            "changed_records": [delta["changed_record_count"] for delta in deltas],
            "pointer_bytes_exact": not any(delta["pointer_bytes_changed"] for delta in deltas),
            # ``delta_table`` rejects map topology changes before it returns;
            # retain the result explicitly in the compact artifact.
            "map_bytes_exact": True,
            "changed_atlas_bytes": non_metric["changed_atlas_pixel_byte_count"],
            "repack_contract": (
                "every changed allocation is a glyph-specific horizontal crop followed by "
                "row-pack; unused allocation tail is zeroed"
            ),
        }

    pc_rows = [
        table
        for row in outer_rows.values()
        for table in row["full_switch_optimized_coverage_in_current_pc"]["pc_tables"]
    ]
    if not pc_rows:
        raise AuditError("compact projection: PC coverage rows are missing")
    present = {table["optimized_codepoints_present"] for table in pc_rows}
    missing = {table["optimized_codepoints_missing"] for table in pc_rows}
    missing_hangul = {table["missing_hangul_syllable_count"] for table in pc_rows}
    missing_jamo = {table["missing_compatibility_jamo_count"] for table in pc_rows}
    if any(len(values) != 1 for values in (present, missing, missing_hangul, missing_jamo)):
        raise AuditError("compact projection: PC coverage is inconsistent by table")

    inputs = report["inputs"]
    def switch_input(key: str) -> dict[str, Any]:
        value = inputs[key]
        return {
            "name": value["name"],
            "size": value["size"],
            "sha256": value["sha256"],
            "member": value["resource_member"],
            "res_lang_size": value["res_lang_size"],
            "res_lang_sha256": value["res_lang_sha256"],
        }

    return {
        "schema": report["schema"],
        "public_source_free": report["public_source_free"],
        "switch_archive_raw_copy": report["switch_archive_raw_copy"],
        "switch_pixels_copied": False,
        "installed_game_files_modified": report["installed_game_files_modified"],
        "inputs": {
            "switch_v22_zip": switch_input("switch_v22_zip"),
            "switch_v23_zip": switch_input("switch_v23_zip"),
            "steam_jp_res_lang": inputs["steam_jp_res_lang"],
        },
        "optimized_codepoints": {
            "count": conclusion["changed_codepoint_count_unique"],
            "sha256": conclusion["changed_codepoints_sha256_unique"],
            "space_count": space_count,
            "compatibility_jamo_count": compatibility_jamo,
            "hangul_syllable_count": conclusion["changed_hangul_codepoint_count_unique"],
        },
        "switch_v22_to_v23": {
            "changed_outer_entries": conclusion["switch_v22_to_v23_changed_font_outers"],
            "record_metric_fields": {
                "visible_width_byte": 0,
                "advance_byte": 4,
                "signed_4bpp_row_stride_byte": 5,
                "contract": "byte0 == byte4, byte5 == -(byte0/2), byte0 is even",
            },
            "outer_6": outer_projection(6),
            "outer_7": outer_projection(7),
        },
        "pc_current_coverage_per_table": {
            "present": present.pop(),
            "missing": missing.pop(),
            "missing_hangul_syllables": missing_hangul.pop(),
            "missing_compatibility_jamo": missing_jamo.pop(),
            "record_capacity_remaining_minimum": min(
                table["record_capacity_remaining"] for table in pc_rows
            ),
        },
        "candidate_policy": {
            "switch_pixels_are_not_copied": True,
            "existing_pc_pixels_use_pc_ink_bbox_crop_and_row_pack": True,
            "missing_pc_glyphs_use_official_seoulhangang_raster": True,
            "space_is_the_only_permitted_blank_glyph": True,
            "non_space_blank_or_ink_clipping_fails_closed": True,
            "game_apply_or_release_completed": False,
        },
    }


def canonical_json(value: dict[str, Any]) -> bytes:
    """Return the stable byte representation used for compact verification."""

    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--switch-v22-zip", type=Path, required=True)
    parser.add_argument("--switch-v23-zip", type=Path, required=True)
    parser.add_argument("--steam-jp-res-lang", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--compact-output",
        type=Path,
        help="optional generated compact public projection (normally audit.v1.json)",
    )
    parser.add_argument(
        "--expected-compact",
        type=Path,
        help="fail if this tracked compact artifact differs from the fresh projection",
    )
    args = parser.parse_args(argv)
    try:
        report = audit(args.switch_v22_zip, args.switch_v23_zip, args.steam_jp_res_lang)
        write_json(args.output, report)
        compact = compact_public_projection(report)
        if args.compact_output is not None:
            write_json(args.compact_output, compact)
        if args.expected_compact is not None:
            try:
                expected = json.loads(args.expected_compact.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise AuditError(f"cannot read expected compact artifact: {args.expected_compact}") from exc
            if canonical_json(compact) != canonical_json(expected):
                raise AuditError(
                    "compact public artifact drifted: regenerate it with --compact-output and review the diff"
                )
    except AuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        "PASS "
        f"metrics_and_rowpack_only={report['conclusion']['all_switch_font_deltas_follow_metric_triplet_plus_crop_rowpack']} "
        f"output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
