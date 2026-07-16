#!/usr/bin/env python3
"""Build an offline Steam-JP full Korean G1N width candidate.

This is the PC counterpart of the Switch v2.3 Korean typesetting update.  It
uses Switch only as *metric evidence*: the full optimized set is 2,405
codepoints (space + 51 compatibility jamo + 2,353 Hangul syllables).  No
Switch game resource, atlas, or raster pixels are copied.  Missing PC glyphs
are rasterized from SHA-pinned official SeoulHangang fonts; existing PC glyph
pixels are crop-and-row-packed inside their own allocations.

The program is offline-only.  It only writes beneath an explicitly supplied
empty repository ``tmp`` directory, never applies or modifies a game file,
and never uses process memory, DLL injection, executable modification, or the
registry.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import stat
import struct
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TMP_ROOT = REPO_ROOT / "tmp"
AUDIT_PATH = SCRIPT_DIR / "build_steam_jp_font_advance_audit_v1.py"
JP_FONT_PATH = REPO_ROOT / "workstreams" / "font_jp_seoulhangang_v1" / "build_jp_seoulhangang_v1.py"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
FULL_SET_HASH = "FD1338F53F1AB1B634496C65CA5AED5F5D182C2731B6A32E4AE1366A6030848D"
FULL_SET_COUNT = 2_405
FULL_HANGUL_COUNT = 2_353
FULL_JAMO_COUNT = 51
# Fullwidth-normalization work may prefer U+30FB (Japanese middle dot), but it
# is intentionally outside the Switch v2.3 width-optimization set.  This
# candidate must preserve the existing U+00B7 behaviour and make any U+30FB
# absence an explicit follow-up, never silently append it while building the
# 2,405-codepoint candidate.
DEFERRED_PUNCTUATION = (0x00B7, 0x30FB)


class CandidateError(ValueError):
    """Raised when an input, preservation, or rendering safety contract fails."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("nobu16_steam_jp_font_advance_audit_v1", AUDIT_PATH)
JP = load_module("nobu16_steam_jp_font_advance_candidate_base", JP_FONT_PATH)
LZ4 = JP.LZ4


@dataclass(frozen=True)
class Route:
    key: str
    relative_path: str
    size: int
    sha256: str
    targets: tuple[tuple[int, int], ...]  # (outer LINK entry, JP font profile entry)


# Steam PK 1.1.7, after the verified v0.9 JP font route.  Each target maps to
# the same G1N hierarchy already used by the JP font builder.
ROUTES: tuple[Route, ...] = (
    Route(
        "base",
        "RES_JP/res_lang.bin",
        154_216_023,
        "0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0",
        ((6, 6), (7, 7)),
    ),
    Route(
        "pk",
        "RES_JP_PK/res_lang_pk.bin",
        141_746_742,
        "EC758BC9B87F98B42E01CA6F841D963811BB944D113E2C65A1E9F5AE19F1DF08",
        ((16, 6), (17, 7)),
    ),
    Route(
        "pk_port1",
        "RES_JP_PK_PORT/res_lang_pk_port1.bin",
        79_243_911,
        "00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7",
        ((1, 101),),
    ),
    Route(
        "pk_port2",
        "RES_JP_PK_PORT/res_lang_pk_port2.bin",
        67_086_423,
        "F18D99C4802AAB78C60C372FF0106ABD61ABDD8C026DC53CAE8FDE47C992C205",
        ((0, 200), (1, 201)),
    ),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_hash(codepoints: Iterable[int]) -> str:
    return hashlib.sha256(",".join(f"U+{value:04X}" for value in sorted(set(codepoints))).encode("ascii")
    ).hexdigest().upper()


def signed_byte(value: int) -> int:
    return value - 256 if value >= 128 else value


def pack_nibbles(values: Iterable[int]) -> bytes:
    row = list(values)
    if len(row) % 2:
        raise CandidateError("4bpp row width must be even")
    if any(not 0 <= value <= 15 for value in row):
        raise CandidateError("invalid 4bpp nibble")
    return bytes((left << 4) | right for left, right in zip(row[0::2], row[1::2], strict=True))


def unpack_nibbles(data: bytes) -> list[int]:
    return [value for byte in data for value in (byte >> 4, byte & 0x0F)]


def atomic_write(path: Path, data: bytes) -> None:
    require_no_reparse_components(TMP_ROOT, path.parent)
    path.parent.mkdir(parents=True, exist_ok=True)
    require_no_reparse_components(TMP_ROOT, path.parent)
    handle: int | None = None
    temporary: Path | None = None
    try:
        handle, temporary_name = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
        temporary = Path(temporary_name)
        with os.fdopen(handle, "wb") as stream:
            handle = None
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if handle is not None:
            os.close(handle)
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def is_reparse_point(path: Path) -> bool:
    """Return true for a symlink/junction without following it."""

    try:
        status = path.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(status, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def require_no_reparse_components(base: Path, target: Path) -> None:
    """Reject symlink/junction escapes before opening a tmp output path."""

    base_absolute = base.absolute()
    target_absolute = target.absolute()
    try:
        relative = target_absolute.relative_to(base_absolute)
    except ValueError as exc:
        raise CandidateError(f"output path escapes repository tmp: {target}") from exc
    if is_reparse_point(base_absolute):
        raise CandidateError(f"repository tmp is a reparse point: {base_absolute}")
    current = base_absolute
    for part in relative.parts:
        if is_reparse_point(current):
            raise CandidateError(f"output path traverses a reparse point: {current}")
        current = current / part
        if current.exists() and is_reparse_point(current):
            raise CandidateError(f"output path is or traverses a reparse point: {current}")


def safe_output_root(root: Path) -> Path:
    require_no_reparse_components(TMP_ROOT, root)
    resolved = root.resolve()
    tmp = TMP_ROOT.resolve()
    if resolved == tmp or tmp not in resolved.parents:
        raise CandidateError(f"output must be an empty child of repository tmp: {tmp}")
    if root.exists() and (is_reparse_point(root) or any(root.iterdir())):
        raise CandidateError(f"output root must be absent or empty: {root}")
    return root


def require_route(path: Path, route: Route) -> bytes:
    if not path.is_file():
        raise CandidateError(f"missing {route.relative_path}: {path}")
    actual_size = path.stat().st_size
    actual_sha = sha256_file(path)
    if actual_size != route.size or actual_sha != route.sha256:
        raise CandidateError(
            f"{route.relative_path}: preimage gate failed: expected {route.size}/{route.sha256}; "
            f"got {actual_size}/{actual_sha}"
        )
    return path.read_bytes()


def table_offset(raw: bytes, table: int) -> int:
    return struct.unpack_from("<I", raw, 0x20 + table * 4)[0]


def record_offset(raw: bytes, table: int, ordinal: int) -> int:
    return table_offset(raw, table) + AUDIT.MAP_SIZE + ordinal * AUDIT.RECORD_SIZE


def inverse_map(table: Any) -> dict[int, tuple[int, ...]]:
    values: dict[int, list[int]] = defaultdict(list)
    for codepoint, ordinal in enumerate(table.mapping):
        values[ordinal].append(codepoint)
    return {ordinal: tuple(codepoints) for ordinal, codepoints in values.items()}


def changed_codepoints(before: Any, after: Any) -> set[int]:
    if len(before.tables) != len(after.tables):
        raise CandidateError("Switch G1N table count changed")
    result: set[int] = set()
    for before_table, after_table in zip(before.tables, after.tables, strict=True):
        if before_table.mapping != after_table.mapping or len(before_table.records) != len(after_table.records):
            raise CandidateError("Switch G1N map/record topology changed")
        inverse = inverse_map(before_table)
        for ordinal, (left, right) in enumerate(zip(before_table.records, after_table.records, strict=True)):
            if left != right:
                result.update(inverse.get(ordinal, ()))
    return result


def require_switch_metric_triplet(record: bytes, label: str) -> int:
    if len(record) != AUDIT.RECORD_SIZE:
        raise CandidateError(f"{label}: record size")
    width = record[0]
    if (
        width <= 0
        or width % 2
        or record[4] != width
        or signed_byte(record[5]) != -(width // 2)
    ):
        raise CandidateError(f"{label}: unsupported width/advance/row-stride triplet")
    return width


def scale_to_even(source_width: int, source_cell: int, target_cell: int) -> int:
    """Scale a Switch metric to a PC cell, choosing nearest even width.

    4bpp G1N rows need an even number of pixels.  We minimize the exact
    rational error ``abs(width*source_cell - source_width*target_cell)``;
    ties choose the wider value.  The later per-glyph ink gate is deliberately
    fail-closed instead of silently widening a metric that does not fit.
    """

    if source_width <= 0 or source_width % 2 or source_cell <= 0 or target_cell <= 0:
        raise CandidateError("invalid source/target metric scale")
    numerator = source_width * target_cell
    lower = (numerator // source_cell) // 2 * 2
    candidates = [value for value in (lower, lower + 2) if 2 <= value <= target_cell]
    if not candidates:
        raise CandidateError("scaled metric is outside target cell")
    return min(candidates, key=lambda value: (abs(value * source_cell - numerator), -value))


def source_selector(profile: str, target_table: int) -> tuple[int, int]:
    """Map each PC font profile/table to its closest Switch metric tier.

    Switch has optimized Korean entries /6 table 0/1 at 48px and /7 table 0
    at 24px.  The PC JP builder uses the same EB profile for /6 table 2, so
    its fallback table deliberately uses /6 table 0.  Likewise B32/B64 use
    the optimized /7 table 0 metric source.  No Switch pixel bytes are used.
    """

    if profile in {"eb48", "eb96"}:
        return 6, 1 if target_table == 1 else 0
    if profile in {"b32", "b64"}:
        return 7, 0
    raise CandidateError(f"unsupported PC font profile: {profile}")


def build_switch_metric_sources(v22_blob: bytes, v23_blob: bytes) -> tuple[set[int], dict[tuple[int, int], Any]]:
    v22_raw = {outer: AUDIT.extract_link_g1n(v22_blob, outer, f"Switch v2.2 /{outer}", LZ4) for outer in (6, 7)}
    v23_raw = {outer: AUDIT.extract_link_g1n(v23_blob, outer, f"Switch v2.3 /{outer}", LZ4) for outer in (6, 7)}
    v22 = {outer: AUDIT.parse_g1n(raw, f"Switch v2.2 /{outer}") for outer, raw in v22_raw.items()}
    v23 = {outer: AUDIT.parse_g1n(raw, f"Switch v2.3 /{outer}") for outer, raw in v23_raw.items()}
    for outer in (6, 7):
        proof = AUDIT.g1n_row_pack_equivalence_summary(v22[outer], v23[outer], f"Switch /{outer}")
        if not proof["all_changed_records_follow_crop_and_row_pack_rule"]:
            raise CandidateError(f"Switch /{outer}: row-pack evidence failed")
    full_set = changed_codepoints(v22[6], v23[6]) | changed_codepoints(v22[7], v23[7])
    if len(full_set) != FULL_SET_COUNT or canonical_hash(full_set) != FULL_SET_HASH:
        raise CandidateError("Switch v2.3 optimized codepoint coverage drifted")
    if sum(0xAC00 <= value <= 0xD7A3 for value in full_set) != FULL_HANGUL_COUNT:
        raise CandidateError("Switch v2.3 Hangul coverage drifted")
    if sum(0x3131 <= value <= 0x3163 for value in full_set) != FULL_JAMO_COUNT or 0x20 not in full_set:
        raise CandidateError("Switch v2.3 jamo/space coverage drifted")
    for outer, table in ((6, 0), (6, 1), (7, 0)):
        source_table = v23[outer].tables[table]
        absent = [value for value in full_set if source_table.mapping[value] == 0]
        if absent:
            raise CandidateError(f"Switch /{outer} table {table}: metric source misses optimized glyphs")
        for value in full_set:
            require_switch_metric_triplet(
                source_table.records[source_table.mapping[value]],
                f"Switch /{outer} table {table} U+{value:04X}",
            )
    return full_set, v23


def route_profile_for_table(profile_entry: int, table: int) -> str:
    try:
        return JP.PROFILE_TABLES[profile_entry][table]
    except (KeyError, IndexError) as exc:
        raise CandidateError(f"unsupported route profile entry/table: {profile_entry}/{table}") from exc


def desired_width(
    switch_v23: dict[int, Any],
    profile: str,
    target_table: int,
    target_cell: int,
    codepoint: int,
) -> tuple[int, dict[str, int]]:
    outer, source_table_index = source_selector(profile, target_table)
    source_table = switch_v23[outer].tables[source_table_index]
    ordinal = source_table.mapping[codepoint]
    if not ordinal:
        raise CandidateError(f"Switch source /{outer} table {source_table_index} misses U+{codepoint:04X}")
    record = source_table.records[ordinal]
    source_width = require_switch_metric_triplet(record, f"Switch U+{codepoint:04X}")
    width = scale_to_even(source_width, source_table.cell, target_cell)
    return width, {
        "source_outer": outer,
        "source_table": source_table_index,
        "source_cell": source_table.cell,
        "source_width": source_width,
        "target_cell": target_cell,
        "target_width": width,
    }


def all_pointer_allocations(raw: bytes, g1n: Any) -> dict[tuple[int, int], tuple[int, int]]:
    rows: list[tuple[int, int, int]] = []
    for table in g1n.tables:
        for ordinal, record in enumerate(table.records):
            rows.append((struct.unpack_from("<I", record, 8)[0], table.index, ordinal))
    rows.sort()
    if len({pointer for pointer, _table, _ordinal in rows}) != len(rows):
        raise CandidateError("duplicate G1N pointers are unsupported")
    atlas_size = len(raw) - g1n.atlas_offset
    result: dict[tuple[int, int], tuple[int, int]] = {}
    for index, (pointer, table, ordinal) in enumerate(rows):
        next_pointer = rows[index + 1][0] if index + 1 < len(rows) else atlas_size
        if not 0 <= pointer < next_pointer <= atlas_size:
            raise CandidateError("invalid G1N pointer allocation")
        result[(table, ordinal)] = (pointer, next_pointer)
    return result


def crop_window(rows: list[list[int]], target_width: int) -> tuple[int, dict[str, int]]:
    positions = [
        x
        for row in rows
        for x, value in enumerate(row)
        if value
    ]
    if not positions:
        raise CandidateError("glyph pixels are blank")
    ink_left = min(positions)
    ink_right = max(positions)
    ink_width = ink_right - ink_left + 1
    old_width = len(rows[0])
    if any(len(row) != old_width for row in rows):
        raise CandidateError("glyph rows have inconsistent width")
    lower = max(0, ink_right - target_width + 1)
    upper = min(ink_left, old_width - target_width)
    if target_width > old_width or lower > upper:
        raise CandidateError(
            f"ink bbox {ink_left}..{ink_right} does not fit requested width {target_width}"
        )
    # Center the actual ink inside the selectable window.  This intentionally
    # derives a PC window from PC SeoulHangang pixels; it does not copy the
    # Switch crop offset or Switch raster bytes.
    ideal = (ink_left + ink_right + 1 - target_width) / 2
    start = max(lower, min(upper, math.floor(ideal + 0.5)))
    if not lower <= start <= upper:
        raise CandidateError("crop window calculation escaped its safe range")
    return start, {
        "ink_left": ink_left,
        "ink_right": ink_right,
        "ink_width": ink_width,
        "crop_start": start,
        "crop_width": target_width,
    }


def fit_width_to_pc_ink(
    rows: list[list[int]], desired_width: int, maximum_width: int, codepoints: set[int], label: str
) -> tuple[int, dict[str, int | bool]]:
    """Keep the scaled Switch metric unless the PC raster itself needs more.

    The Switch and Steam builds use independently rasterized SeoulHangang
    atlases.  A Switch-derived width is therefore a target, not permission to
    crop a wider PC ink box.  The smallest fitting even width is an explicit
    per-glyph floor; this still removes all safe excess width while preserving
    every PC ink pixel.  It is recorded in the manifest instead of silently
    claiming an exact Switch-width transfer.
    """

    positions = [x for row in rows for x, value in enumerate(row) if value]
    if not positions:
        if codepoints == {0x20}:
            return desired_width, {
                "pc_ink_width": 0,
                "pc_ink_fit_width": desired_width,
                "pc_ink_fit_override": False,
            }
        raise CandidateError(f"{label}: non-space glyph pixels are blank")
    ink_width = max(positions) - min(positions) + 1
    ink_floor = (ink_width + 1) & ~1
    applied_width = max(desired_width, ink_floor)
    if applied_width > maximum_width:
        raise CandidateError(
            f"{label}: PC ink width {ink_width} cannot fit its allocation width {maximum_width}"
        )
    return applied_width, {
        "pc_ink_width": ink_width,
        "pc_ink_fit_width": applied_width,
        "pc_ink_fit_override": applied_width != desired_width,
    }


def pack_rows_for_target(
    rows: list[list[int]], target_width: int, codepoints: set[int], label: str
) -> tuple[bytes, str, str]:
    """Crop visible PC ink or encode the one permitted blank glyph (space)."""

    if any(value for row in rows for value in row):
        crop_start, crop = crop_window(rows, target_width)
        packed = b"".join(pack_nibbles(row[crop_start : crop_start + target_width]) for row in rows)
        return packed, str(crop_start), str(crop["ink_width"])
    if codepoints == {0x20}:
        return b"\0" * ((target_width // 2) * len(rows)), "blank_space", "0"
    raise CandidateError(f"{label}: non-space glyph pixels are blank")


def assert_atlas_changes_within_allocations(
    original: bytes, candidate: bytes, allocations: list[tuple[int, int]], label: str
) -> None:
    """Reject a changed atlas byte outside sorted non-overlapping allocations.

    Use interval walking rather than a set of individual byte offsets: a PORT
    96px font can otherwise allocate several gigabytes of Python integer/set
    overhead merely to verify a few megabytes of atlas data.
    """

    if len(original) != len(candidate):
        raise CandidateError(f"{label}: atlas size changed")
    permitted_intervals = sorted(allocations)
    if any(
        start < 0 or end <= start
        for start, end in permitted_intervals
    ) or any(
        left[1] > right[0]
        for left, right in zip(permitted_intervals, permitted_intervals[1:])
    ):
        raise CandidateError(f"{label}: invalid/overlapping changed atlas allocations")
    interval_index = 0
    for offset, (left, right) in enumerate(zip(original, candidate, strict=True)):
        if left == right:
            continue
        while (
            interval_index < len(permitted_intervals)
            and permitted_intervals[interval_index][1] <= offset
        ):
            interval_index += 1
        if (
            interval_index >= len(permitted_intervals)
            or not permitted_intervals[interval_index][0] <= offset < permitted_intervals[interval_index][1]
        ):
            raise CandidateError(f"{label}: atlas changed outside optimized glyph allocations")


def transform_g1n(
    raw: bytes,
    full_set: set[int],
    switch_v23: dict[int, Any],
    profile_entry: int,
    label: str,
) -> tuple[bytes, dict[str, Any]]:
    """Apply full-set metrics and PC-derived crop+row-pack to one G1N."""

    before = AUDIT.parse_g1n(raw, f"{label} before")
    mutable = bytearray(raw)
    allocations = all_pointer_allocations(raw, before)
    atlas_start = before.atlas_offset
    proposals: dict[tuple[int, int], tuple[int, dict[str, int], set[int]]] = {}
    for table in before.tables:
        profile = route_profile_for_table(profile_entry, table.index)
        inverse = inverse_map(table)
        for codepoint in full_set:
            ordinal = table.mapping[codepoint]
            if not ordinal:
                raise CandidateError(f"{label} table {table.index}: U+{codepoint:04X} is still unmapped")
            width, source = desired_width(switch_v23, profile, table.index, table.cell, codepoint)
            key = (table.index, ordinal)
            current = proposals.get(key)
            if current is None:
                proposals[key] = (width, source, {codepoint})
            else:
                if current[0] != width or current[1] != source:
                    raise CandidateError(f"{label} table {table.index}: aliased glyph has conflicting metrics")
                current[2].add(codepoint)
        for ordinal, aliases in inverse.items():
            if (table.index, ordinal) in proposals and any(value not in full_set for value in aliases):
                raise CandidateError(f"{label} table {table.index}: optimized record is shared with non-target codepoint")

    changed_allocations: list[tuple[int, int]] = []
    crop_starts: Counter[str] = Counter()
    ink_widths: Counter[str] = Counter()
    pc_ink_fit_override_count = 0
    pc_ink_fit_override_by_table: Counter[str] = Counter()
    for (table_index, ordinal), (new_width, source, codepoints) in sorted(proposals.items()):
        record_start = record_offset(raw, table_index, ordinal)
        old_record = raw[record_start : record_start + AUDIT.RECORD_SIZE]
        old_width = old_record[0]
        old_stride = abs(signed_byte(old_record[5]))
        storage_width = old_stride * 2
        height = old_record[1]
        pointer, next_pointer = allocations[(table_index, ordinal)]
        old_payload = old_stride * height
        is_space_placeholder = (
            codepoints == {0x20}
            and old_width == 0
            and old_record[4] == 0
            and old_stride > 0
        )
        if (
            (not is_space_placeholder and (
                old_width <= 0
                or old_width != old_record[4]
                or old_width % 2
            ))
            # Table 2 fallback glyphs may have a deliberately narrow logical
            # advance but retain a full-cell physical row allocation.  The
            # actual storage width, not the old advance, is the safe upper
            # bound for a re-packed PC glyph.
            or old_width > storage_width
            or pointer + old_payload > next_pointer
        ):
            raise CandidateError(f"{label} table {table_index} ordinal {ordinal}: unsupported preimage metric/storage")
        if new_width > storage_width:
            raise CandidateError(f"{label} table {table_index} ordinal {ordinal}: desired metric widens storage")
        rows = [
            unpack_nibbles(raw[atlas_start + pointer + row * old_stride : atlas_start + pointer + (row + 1) * old_stride])
            for row in range(height)
        ]
        codepoint_label = ",".join(f"U+{codepoint:04X}" for codepoint in sorted(codepoints))
        applied_width, fit = fit_width_to_pc_ink(
            rows,
            new_width,
            storage_width,
            codepoints,
            f"{label} table {table_index} ordinal {ordinal} {codepoint_label}",
        )
        source = {
            **source,
            "switch_scaled_width": new_width,
            "preimage_logical_width": old_width,
            "preimage_storage_width": storage_width,
            "preimage_space_placeholder": int(is_space_placeholder),
            "pc_ink_width": int(fit["pc_ink_width"]),
            "pc_ink_fit_width": int(fit["pc_ink_fit_width"]),
        }
        if bool(fit["pc_ink_fit_override"]):
            pc_ink_fit_override_count += 1
            pc_ink_fit_override_by_table[str(table_index)] += 1
        new_width = applied_width
        proposals[(table_index, ordinal)] = (new_width, source, codepoints)
        # Switch v2.3 includes U+0020 in its optimized set.  The helper
        # permits that one intentional blank glyph and rejects every other
        # blank codepoint as a raster/coverage failure.
        packed, crop_key, ink_key = pack_rows_for_target(
            rows, new_width, codepoints, f"{label} table {table_index} ordinal {ordinal}"
        )
        crop_starts[crop_key] += 1
        ink_widths[ink_key] += 1
        new_stride = new_width // 2
        if len(packed) != new_stride * height or len(packed) > next_pointer - pointer:
            raise CandidateError(f"{label} table {table_index} ordinal {ordinal}: packed pixel bounds")
        mutable[atlas_start + pointer : atlas_start + next_pointer] = packed + b"\0" * (next_pointer - pointer - len(packed))
        mutable[record_start] = new_width
        mutable[record_start + 4] = new_width
        mutable[record_start + 5] = (-new_stride) & 0xFF
        if mutable[record_start + 8 : record_start + 12] != old_record[8:12]:
            raise CandidateError("pointer changed while applying metric triplet")
        changed_allocations.append((pointer, next_pointer))

    candidate = bytes(mutable)
    after = AUDIT.parse_g1n(candidate, f"{label} after")
    if len(before.tables) != len(after.tables) or before.atlas_offset != after.atlas_offset:
        raise CandidateError(f"{label}: structural header changed")
    for before_table, after_table in zip(before.tables, after.tables, strict=True):
        if before_table.mapping != after_table.mapping or len(before_table.records) != len(after_table.records):
            raise CandidateError(f"{label}: map or record count changed during metric transform")
        for ordinal, (left, right) in enumerate(zip(before_table.records, after_table.records, strict=True)):
            key = (before_table.index, ordinal)
            if key not in proposals:
                if left != right:
                    raise CandidateError(f"{label}: non-target record changed")
                continue
            if left[1:4] != right[1:4] or left[6:12] != right[6:12]:
                raise CandidateError(f"{label}: protected record fields changed")
            if right[0] != right[4] or signed_byte(right[5]) != -(right[0] // 2):
                raise CandidateError(f"{label}: output metric triplet invalid")
    original_atlas = raw[atlas_start:]
    candidate_atlas = candidate[atlas_start:]
    assert_atlas_changes_within_allocations(
        original_atlas,
        candidate_atlas,
        changed_allocations,
        label,
    )
    coverage = []
    for table in after.tables:
        mapped = [codepoint for codepoint in full_set if table.mapping[codepoint] != 0]
        if set(mapped) != full_set:
            raise CandidateError(f"{label} table {table.index}: output coverage is incomplete")
        widths = [after_table_record[0] for codepoint in full_set for after_table_record in [table.records[table.mapping[codepoint]]]]
        coverage.append(
            {
                "table": table.index,
                "cell": table.cell,
                "coverage_count": len(mapped),
                "coverage_sha256": canonical_hash(mapped),
                "width_histogram": {str(value): count for value, count in sorted(Counter(widths).items())},
                "average_width": sum(widths) / len(widths),
                "average_reduction_percent": (1 - sum(widths) / (len(widths) * table.cell)) * 100,
            }
        )
    switch_scaled_width_histograms: dict[str, dict[str, int]] = {}
    profile_width_histograms: dict[str, Counter[int]] = defaultdict(Counter)
    for table in after.tables:
        table_proposals = [
            (width, source)
            for (table_index, _ordinal), (width, source, _points) in proposals.items()
            if table_index == table.index
        ]
        switch_scaled_width_histograms[str(table.index)] = {
            str(value): count
            for value, count in sorted(Counter(source["switch_scaled_width"] for _width, source in table_proposals).items())
        }
        profile_width_histograms[route_profile_for_table(profile_entry, table.index)].update(
            width for width, _source in table_proposals
        )
    return candidate, {
        "label": label,
        "profile_entry": profile_entry,
        "input_g1n_sha256": sha256(raw),
        "output_g1n_sha256": sha256(candidate),
        "input_g1n_size": len(raw),
        "output_g1n_size": len(candidate),
        "optimized_record_count": len(proposals),
        "optimized_codepoint_count_per_table": FULL_SET_COUNT,
        "record_pointer_bytes_exact": True,
        "maps_exact_during_metric_transform": True,
        "protected_record_fields_exact": True,
        "atlas_changed_only_inside_optimized_allocations": True,
        "crop_window_source": "PC SeoulHangang raster ink bbox; Switch crop offsets/pixels are never copied",
        "all_crop_windows_preserve_nonzero_ink": True,
        "crop_start_histogram": dict(sorted(crop_starts.items())),
        "ink_width_histogram": dict(sorted(ink_widths.items())),
        "pc_ink_fit_floor_policy": (
            "applied width is max(scaled Switch width, smallest even PC ink-bbox width); "
            "an allocation overflow fails closed"
        ),
        "pc_ink_fit_override_count": pc_ink_fit_override_count,
        "pc_ink_fit_override_by_table": dict(sorted(pc_ink_fit_override_by_table.items())),
        "switch_scaled_width_histograms": switch_scaled_width_histograms,
        "profile_width_histograms": {
            profile: {
                str(value): count
                for value, count in sorted(histogram.items())
            }
            for profile, histogram in sorted(profile_width_histograms.items())
        },
        "coverage": coverage,
    }


def append_missing_and_transform(
    raw: bytes,
    full_set: set[int],
    switch_v23: dict[int, Any],
    profile_entry: int,
    profile_pixels: dict[str, bytes],
    raster_codepoints: list[int],
    label: str,
) -> tuple[bytes, dict[str, Any]]:
    before = AUDIT.parse_g1n(raw, f"{label} preimage")
    missing_by_table = {
        table.index: sorted(codepoint for codepoint in full_set if table.mapping[codepoint] == 0)
        for table in before.tables
    }
    missing_sets = {tuple(values) for values in missing_by_table.values()}
    if len(missing_sets) != 1:
        raise CandidateError(f"{label}: current coverage differs by table")
    missing = next(iter(missing_sets))
    if missing != tuple(raster_codepoints):
        raise CandidateError(f"{label}: global raster codepoint set differs from route missing set")
    if len(before.tables) != 3:
        raise CandidateError(f"{label}: expected exactly three G1N tables")
    if any(len(table.records) + len(missing) > 0xFFFF for table in before.tables):
        raise CandidateError(f"{label}: G1N record capacity exhausted")
    appended, append_validation = JP.build_g1n_append(
        raw,
        profile_pixels,
        {},
        profile_entry,
        raster_codepoints,
        missing_by_table,
        label,
    )
    final, transform = transform_g1n(appended, full_set, switch_v23, profile_entry, label)
    return final, {
        "preimage_g1n_sha256": sha256(raw),
        "post_append_pre_transform_g1n_sha256": sha256(appended),
        "final_g1n_sha256": sha256(final),
        "missing_append_count_per_table": len(missing),
        "missing_append_sha256": canonical_hash(missing),
        "append_validation": append_validation,
        "metric_transform": transform,
        "deferred_punctuation": audit_deferred_punctuation(raw, final, label),
    }


def audit_deferred_punctuation(before_raw: bytes, after_raw: bytes, label: str) -> dict[str, Any]:
    """Prove scope exclusion and preservation for middle-dot normalization.

    This candidate's 2,405-codepoint contract has no U+30FB.  Record its
    actual mapping state in every target table while proving that U+00B7 and
    U+30FB map/record state was not altered by the width pass.  A later text
    normalization patch can consume this evidence and add a deliberately
    separate, safely-rasterized punctuation glyph if required.
    """

    before = AUDIT.parse_g1n(before_raw, f"{label} punctuation before")
    after = AUDIT.parse_g1n(after_raw, f"{label} punctuation after")
    if len(before.tables) != len(after.tables):
        raise CandidateError(f"{label}: punctuation audit table count changed")
    by_codepoint: dict[str, Any] = {}
    for codepoint in DEFERRED_PUNCTUATION:
        rows: list[dict[str, Any]] = []
        for before_table, after_table in zip(before.tables, after.tables, strict=True):
            before_ordinal = before_table.mapping[codepoint]
            after_ordinal = after_table.mapping[codepoint]
            if before_ordinal != after_ordinal:
                raise CandidateError(
                    f"{label} table {before_table.index}: U+{codepoint:04X} mapping changed outside scope"
                )
            record_exact = (
                before_table.records[before_ordinal] == after_table.records[after_ordinal]
                if before_ordinal
                else True
            )
            if not record_exact:
                raise CandidateError(
                    f"{label} table {before_table.index}: U+{codepoint:04X} record changed outside scope"
                )
            rows.append(
                {
                    "table": before_table.index,
                    "mapped": bool(before_ordinal),
                    "ordinal": before_ordinal,
                    "mapping_exact": True,
                    "record_exact_when_mapped": record_exact,
                }
            )
        by_codepoint[f"U+{codepoint:04X}"] = {
            "mapped_table_count": sum(row["mapped"] for row in rows),
            "unmapped_table_count": sum(not row["mapped"] for row in rows),
            "tables": rows,
        }
    return {
        "candidate_scope_excludes_u30fb": True,
        "u30fb_follow_up_required_if_text_normalization_emits_it": (
            by_codepoint["U+30FB"]["unmapped_table_count"] > 0
        ),
        "u00b7_existing_behavior_preserved": all(
            row["mapping_exact"] and row["record_exact_when_mapped"]
            for row in by_codepoint["U+00B7"]["tables"]
        ),
        "codepoints": by_codepoint,
    }


def input_root_paths(root: Path) -> dict[str, Path]:
    return {route.key: root / Path(route.relative_path) for route in ROUTES}


def validate_requested_font_cmaps(
    font_paths: dict[str, Path], codepoints: list[int]
) -> list[dict[str, Any]]:
    """Require that both pinned official TTFs directly cover this build's set.

    The reusable JP builder's cmap checker intentionally encodes a *different*
    contract: its normal translation-demand set must leave a known group of
    stock-reuse punctuation unmapped.  The v2.3 width candidate only asks the
    fonts to rasterize 1,152 missing Hangul/jamo glyphs, all of which must be
    directly available from both official TTFs.  Reusing that broader
    checker here would reject a safe subset merely because omitted unrelated
    punctuation is no longer part of the requested set.
    """

    try:
        JP.SC_FONT.require_official_fonts(font_paths)
    except Exception as exc:  # helper-specific pin errors become our build error
        raise CandidateError(f"official SeoulHangang pin gate failed: {exc}") from exc
    reports: list[dict[str, Any]] = []
    for profile, font_key in (("eb48_eb96", "entry6_48px_eb"), ("b32_b64", "entry7_32px_b")):
        path = font_paths[font_key]
        try:
            subtables = JP.parse_unicode_cmap(path.read_bytes(), f"official {font_key}")
            covered = {
                codepoint
                for codepoint in codepoints
                if any(JP.cmap_glyph_id(row, codepoint, f"official {font_key}") for row in subtables)
            }
        except Exception as exc:
            raise CandidateError(f"official {font_key} cmap parse gate failed: {exc}") from exc
        missing = sorted(set(codepoints) - covered)
        if missing:
            preview = ", ".join(f"U+{codepoint:04X}" for codepoint in missing[:16])
            suffix = " ..." if len(missing) > 16 else ""
            raise CandidateError(
                f"official {font_key} lacks {len(missing)} requested v2.3 glyph(s): {preview}{suffix}"
            )
        reports.append(
            {
                "profile": profile,
                "font_key": font_key,
                "font_sha256": sha256_file(path),
                "requested_codepoint_count": len(codepoints),
                "covered_codepoint_count": len(covered),
                "covered_codepoints_sha256": canonical_hash(covered),
                "missing_codepoint_count": 0,
                "gdi_fallback_forbidden": True,
            }
        )
    return reports


def raster_missing_glyphs(
    output_root: Path,
    font_paths: dict[str, Path],
    powershell: Path,
    codepoints: list[int],
    reuse_raster_root: Path | None = None,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    if not codepoints:
        raise CandidateError("missing codepoint set is empty; full candidate should already exist")
    # The full optimized set is cmap-gated; raster work only covers the actual
    # 1,152 missing entries because existing SeoulHangang pixels are preserved.
    cmap_gate = validate_requested_font_cmaps(font_paths, codepoints)
    request_path = output_root / "private" / "raster_request.json"
    raster_root = output_root / "private" / "raster"
    request_bytes = json.dumps(
        JP.raster_request_v3(font_paths, codepoints),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    atomic_write(request_path, request_bytes)
    if reuse_raster_root is None:
        try:
            result = JP.SC_FONT.run_rasterizer(powershell, request_path, raster_root)
        except Exception as exc:
            raise CandidateError(f"SeoulHangang rasterizer failed: {exc}") from exc
        raster_mode = "fresh_private_raster"
    else:
        require_no_reparse_components(TMP_ROOT, reuse_raster_root)
        result_path = reuse_raster_root / "raster_result.json"
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CandidateError(f"reused raster result is unreadable: {result_path}") from exc
        if result.get("request_sha256") != sha256(request_bytes):
            raise CandidateError(
                "reused raster request SHA does not match this exact font/codepoint/profile request"
            )
        raster_root = reuse_raster_root
        raster_mode = "validated_private_raster_reuse"
    try:
        full_pixels = JP.validate_raster_result_v3(result, raster_root, codepoints)
    except Exception as exc:
        raise CandidateError(f"SeoulHangang raster result validation failed: {exc}") from exc
    profile_pixels, profiles = JP.prepare_raster_profiles(full_pixels, codepoints)
    return profile_pixels, {
        "mode": raster_mode,
        "raster_codepoint_count": len(codepoints),
        "raster_codepoints_sha256": canonical_hash(codepoints),
        "raster_result_sha256": sha256_file(raster_root / "raster_result.json"),
        "profiles": profiles,
        "font_cmap_gate": cmap_gate,
    }


def verify_candidate_route(
    route: Route,
    source_blob: bytes,
    candidate_blob: bytes,
    raw_replacements: dict[int, bytes],
) -> dict[str, Any]:
    preservation = JP.verify_archive_preservation(
        source_blob, candidate_blob, raw_replacements, f"{route.key} final"
    )
    candidate_archive = JP.parse_stock_archive(candidate_blob, f"{route.key} final")
    targets = []
    for outer, raw in sorted(raw_replacements.items()):
        extracted = JP.extract_raw_g1n(candidate_archive, outer, f"{route.key} final")
        if extracted != raw:
            raise CandidateError(f"{route.key} /{outer}: final re-extraction differs")
        targets.append({"outer_entry": outer, "g1n_sha256": sha256(raw), "g1n_size": len(raw)})
    return {"preservation": preservation, "targets": targets}


def build(
    input_root: Path,
    switch_v22_zip: Path,
    switch_v23_zip: Path,
    font_eb: Path,
    font_b: Path,
    powershell: Path,
    output_root: Path,
    reuse_raster_root: Path | None = None,
    base_res_lang_override: Path | None = None,
) -> dict[str, Any]:
    output_root = safe_output_root(output_root)
    v22_blob = AUDIT.switch_archive_from_zip(switch_v22_zip)
    v23_blob = AUDIT.switch_archive_from_zip(switch_v23_zip)
    full_set, switch_v23 = build_switch_metric_sources(v22_blob, v23_blob)
    if canonical_hash(full_set) != FULL_SET_HASH:
        raise CandidateError("optimized set hash drift")
    source_paths = {
        route.key: (
            base_res_lang_override
            if route.key == "base" and base_res_lang_override is not None
            else input_root / Path(route.relative_path)
        )
        for route in ROUTES
    }
    source_blobs = {
        route.key: require_route(source_paths[route.key], route)
        for route in ROUTES
    }
    # Compute the common missing set before starting any raster or output work.
    global_missing: set[int] | None = None
    coverage_before: dict[str, Any] = {}
    for route in ROUTES:
        archive = JP.parse_stock_archive(source_blobs[route.key], f"{route.key} input")
        rows = []
        for outer, _profile_entry in route.targets:
            raw = JP.extract_raw_g1n(archive, outer, f"{route.key} input")
            g1n = AUDIT.parse_g1n(raw, f"{route.key} /{outer}")
            for table in g1n.tables:
                missing = {codepoint for codepoint in full_set if table.mapping[codepoint] == 0}
                if global_missing is None:
                    global_missing = set(missing)
                elif missing != global_missing:
                    raise CandidateError(f"{route.key} /{outer} table {table.index}: missing set differs")
                rows.append({
                    "outer_entry": outer,
                    "table": table.index,
                    "cell": table.cell,
                    "record_count": len(table.records),
                    "record_capacity_remaining": 0xFFFF - len(table.records),
                    "coverage_before": FULL_SET_COUNT - len(missing),
                    "missing_before": len(missing),
                    "missing_sha256": canonical_hash(missing),
                })
        coverage_before[route.key] = rows
    if global_missing is None or len(global_missing) != 1_152:
        raise CandidateError("expected 1,152 missing full-coverage glyphs")
    raster_codepoints = sorted(global_missing)
    font_paths = {
        "entry6_48px_eb": font_eb,
        "entry7_32px_b": font_b,
    }
    profile_pixels, raster_evidence = raster_missing_glyphs(
        output_root, font_paths, powershell, raster_codepoints, reuse_raster_root
    )

    route_outputs: list[dict[str, Any]] = []
    for route in ROUTES:
        archive = JP.parse_stock_archive(source_blobs[route.key], f"{route.key} input")
        replacements: dict[int, bytes] = {}
        target_rows: list[dict[str, Any]] = []
        for outer, profile_entry in route.targets:
            raw = JP.extract_raw_g1n(archive, outer, f"{route.key} input")
            final_raw, evidence = append_missing_and_transform(
                raw,
                full_set,
                switch_v23,
                profile_entry,
                profile_pixels,
                raster_codepoints,
                f"{route.key} /{outer}",
            )
            replacements[outer] = final_raw
            target_rows.append({"outer_entry": outer, "profile_entry": profile_entry, **evidence})
        candidate_blob = JP.rebuild_link_with_g1n_replacements(
            source_blobs[route.key], replacements, f"{route.key} candidate"
        )
        candidate_path = output_root / "private" / "candidate" / Path(route.relative_path)
        atomic_write(candidate_path, candidate_blob)
        route_outputs.append({
            "route": route.key,
            "logical_path": route.relative_path,
            "preimage_source": (
                "explicit_v0.9_base_backup" if route.key == "base" and base_res_lang_override is not None
                else "input_root"
            ),
            "preimage_size": len(source_blobs[route.key]),
            "preimage_sha256": sha256(source_blobs[route.key]),
            "candidate_size": len(candidate_blob),
            "candidate_sha256": sha256(candidate_blob),
            "targets": target_rows,
            "verification": verify_candidate_route(route, source_blobs[route.key], candidate_blob, replacements),
        })

    punctuation_targets = [
        {
            "route": route["route"],
            "logical_path": route["logical_path"],
            "outer_entry": target["outer_entry"],
            **target["deferred_punctuation"],
        }
        for route in route_outputs
        for target in route["targets"]
    ]
    punctuation_table_count = sum(
        len(target["codepoints"]["U+30FB"]["tables"])
        for target in punctuation_targets
    )
    u30fb_unmapped_table_count = sum(
        target["codepoints"]["U+30FB"]["unmapped_table_count"]
        for target in punctuation_targets
    )

    manifest = {
        "schema": "nobu16.kr.steam-jp-font-advance-candidate.v1",
        "file_only": True,
        "installed_game_files_modified": False,
        "process_memory_access": False,
        "dll_injection": False,
        "exe_or_registry_modified": False,
        "switch_archive_raw_copy": False,
        "switch_pixels_copied": False,
        "pc_existing_glyph_pixels_preserved_by_crop_and_row_pack": True,
        "new_glyph_pixels_from_official_seoulhangang": True,
        "output_is_private_tmp_only": True,
        "optimized_codepoints": {
            "count": len(full_set),
            "sha256": canonical_hash(full_set),
            "hangul_syllable_count": sum(0xAC00 <= value <= 0xD7A3 for value in full_set),
            "compatibility_jamo_count": sum(0x3131 <= value <= 0x3163 for value in full_set),
            "space_included": 0x20 in full_set,
        },
        "pc_full_coverage_expansion": {
            "missing_append_count": len(raster_codepoints),
            "missing_append_sha256": canonical_hash(raster_codepoints),
            "coverage_before": coverage_before,
        },
        "switch_inputs": {
            "v22_zip": {"name": switch_v22_zip.name, "size": switch_v22_zip.stat().st_size, "sha256": sha256_file(switch_v22_zip), "member": SWITCH_MEMBER, "res_lang_sha256": sha256(v22_blob)},
            "v23_zip": {"name": switch_v23_zip.name, "size": switch_v23_zip.stat().st_size, "sha256": sha256_file(switch_v23_zip), "member": SWITCH_MEMBER, "res_lang_sha256": sha256(v23_blob)},
        },
        "official_fonts": {
            key: {"path_name": path.name, "size": path.stat().st_size, "sha256": sha256_file(path)}
            for key, path in font_paths.items()
        },
        "metric_scaling": {
            "policy": "nearest even target width minimizes exact rational scale error; ties choose wider; non-fitting PC ink fails closed",
            "source_profiles": {
                "eb48": "Switch /6 table0 (PC table0/2) or table1 (PC table1), 48->48",
                "b32": "Switch /7 table0, 24->32 (4/3)",
                "b64": "Switch /7 table0, 24->64 (8/3)",
                "eb96": "Switch /6 table0 (PC table0/2) or table1 (PC table1), 48->96 (2/1)",
            },
        },
        "deferred_punctuation_audit": {
            "scope": "U+30FB is outside the fixed Switch v2.3 2,405-codepoint width set",
            "u00b7_existing_behavior_preserved": all(
                target["u00b7_existing_behavior_preserved"] for target in punctuation_targets
            ),
            "u30fb_active_target_table_count": punctuation_table_count,
            "u30fb_unmapped_active_target_table_count": u30fb_unmapped_table_count,
            "u30fb_follow_up_required_before_emitting_normalized_text": (
                u30fb_unmapped_table_count > 0
            ),
            "targets": punctuation_targets,
        },
        "raster": raster_evidence,
        "routes": route_outputs,
    }
    manifest_path = output_root / "private" / "manifest.json"
    atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--switch-v22-zip", type=Path, required=True)
    parser.add_argument("--switch-v23-zip", type=Path, required=True)
    parser.add_argument("--font-eb", type=Path, required=True)
    parser.add_argument("--font-b", type=Path, required=True)
    parser.add_argument("--powershell", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--reuse-raster-root",
        type=Path,
        help="validated private tmp raster result for the exact same request; never a game asset",
    )
    parser.add_argument(
        "--base-res-lang-override",
        type=Path,
        help="optional read-only v0.9 RES_JP/res_lang.bin backup when live RES_JP already has a separate image candidate",
    )
    args = parser.parse_args(argv)
    try:
        manifest = build(
            args.input_root,
            args.switch_v22_zip,
            args.switch_v23_zip,
            args.font_eb,
            args.font_b,
            args.powershell,
            args.output_root,
            args.reuse_raster_root,
            args.base_res_lang_override,
        )
    except CandidateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        "PASS "
        f"coverage={manifest['optimized_codepoints']['count']} "
        f"routes={len(manifest['routes'])} "
        f"output={args.output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
