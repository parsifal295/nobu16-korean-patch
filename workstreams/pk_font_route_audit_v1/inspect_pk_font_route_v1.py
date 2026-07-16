#!/usr/bin/env python3
"""Read-only, source-free audit of NOBU16 base/PK language font routes.

The inspector accepts a private game root, reads sixteen language archives,
and emits only structural counts, sizes, and SHA-256 digests.  It has no file
write path and never prints the private root or extracts a game resource.

Version 1 pins the observed PC topology:

* every regular base archive has two direct G1N objects at outer entries 6/7;
* SC/TC/EN PK and every expansion archive have no G1N object;
* JP PK alone has two direct G1N objects at outer entries 16/17; and
* JP base 6/7 and JP PK 16/17 share the complete pre-atlas G1N bytes while
  differing only in a non-zero number of atlas bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.dont_write_bytecode = True

from nobu16_lz4 import (  # noqa: E402
    LZ4Error,
    LinkError,
    decompress_wrapper,
    parse_link,
    parse_wrapper_header,
)


SCHEMA = "nobu16.pk_font_route_audit.v1"
INSPECTOR_VERSION = "1.0.0"
G1N_MAGIC = b"_N1G0000"
G1T_MAGIC = b"GT1G"
G1M_MAGIC = b"G1M_"
MAP_ENTRIES = 0x10000
MAP_SIZE = MAP_ENTRIES * 2
RECORD_SIZE = 12
PALETTE_SIZE = 0x40
MAX_RECURSION = 32


@dataclass(frozen=True)
class ArchiveSpec:
    language: str
    route: str
    family: str
    logical_path: str


def _archive_specs() -> tuple[ArchiveSpec, ...]:
    result: list[ArchiveSpec] = []
    for language in ("SC", "TC", "EN", "JP"):
        result.extend(
            (
                ArchiveSpec(language, "base", "regular", f"RES_{language}/res_lang.bin"),
                ArchiveSpec(
                    language,
                    "base",
                    "expansion",
                    f"RES_{language}/res_lang_exp.bin",
                ),
                ArchiveSpec(
                    language,
                    "pk",
                    "regular",
                    f"RES_{language}_PK/res_lang_pk.bin",
                ),
                ArchiveSpec(
                    language,
                    "pk",
                    "expansion",
                    f"RES_{language}_PK/res_lang_exp_pk.bin",
                ),
            )
        )
    return tuple(result)


ARCHIVE_SPECS = _archive_specs()
EXPECTED_DIRECT_G1N = {
    spec.logical_path: (
        [6, 7]
        if spec.route == "base" and spec.family == "regular"
        else [16, 17]
        if spec.language == "JP" and spec.route == "pk" and spec.family == "regular"
        else []
    )
    for spec in ARCHIVE_SPECS
}
JP_G1N_PAIRS = (
    {
        "profile": "large",
        "base_logical_path": "RES_JP/res_lang.bin",
        "base_outer_entry": 6,
        "pk_logical_path": "RES_JP_PK/res_lang_pk.bin",
        "pk_outer_entry": 16,
    },
    {
        "profile": "small",
        "base_logical_path": "RES_JP/res_lang.bin",
        "base_outer_entry": 7,
        "pk_logical_path": "RES_JP_PK/res_lang_pk.bin",
        "pk_outer_entry": 17,
    },
)


class AuditError(ValueError):
    """Raised when a private input or the pinned route violates the contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _u32(data: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise AuditError(f"{label}: u32 at 0x{offset:X} is outside a {len(data)}-byte object")
    return struct.unpack_from("<I", data, offset)[0]


def _strict_json(raw: bytes, label: str) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        folded: set[str] = set()
        for key, value in pairs:
            lowered = key.casefold()
            if key in result or lowered in folded:
                raise AuditError(f"{label}: duplicate/case-colliding key {key!r}")
            result[key] = value
            folded.add(lowered)
        return result

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"{label}: invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"{label}: top-level JSON must be an object")
    return value


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _mapped_nonzero(mapping_blob: bytes) -> int:
    if len(mapping_blob) != MAP_SIZE:
        raise AuditError("internal G1N map size mismatch")
    return sum(value != 0 for (value,) in struct.iter_unpack("<H", mapping_blob))


def parse_g1n_summary(raw: bytes) -> dict[str, Any]:
    """Strictly summarize one raw G1N without exposing map cells or pixels."""

    if len(raw) < 0x20 or raw[:8] != G1N_MAGIC:
        raise AuditError("object is not a G1N")
    declared_size = _u32(raw, 0x08, "G1N declared_size")
    header_size = _u32(raw, 0x0C, "G1N header_size")
    unknown = _u32(raw, 0x10, "G1N unknown")
    atlas_offset = _u32(raw, 0x14, "G1N atlas_offset")
    palette_count = _u32(raw, 0x18, "G1N palette_count")
    table_count = _u32(raw, 0x1C, "G1N table_count")

    if declared_size != len(raw):
        raise AuditError(
            f"G1N declared_size={declared_size}, actual_size={len(raw)}"
        )
    if not 1 <= table_count <= 32:
        raise AuditError(f"G1N table_count={table_count} is implausible")
    expected_header_size = 0x20 + table_count * 4 + palette_count * PALETTE_SIZE
    if header_size != expected_header_size:
        raise AuditError(
            f"G1N header_size=0x{header_size:X}, expected=0x{expected_header_size:X}"
        )
    if not header_size < atlas_offset <= len(raw):
        raise AuditError("G1N header/table/atlas ordering is invalid")

    table_offsets = [
        _u32(raw, 0x20 + table_index * 4, f"G1N table[{table_index}] offset")
        for table_index in range(table_count)
    ]
    if table_offsets != sorted(set(table_offsets)) or table_offsets[0] != header_size:
        raise AuditError("G1N table offsets are not unique, ordered, and header-aligned")

    tables: list[dict[str, Any]] = []
    for table_index, table_offset in enumerate(table_offsets):
        table_end = (
            table_offsets[table_index + 1]
            if table_index + 1 < table_count
            else atlas_offset
        )
        record_start = table_offset + MAP_SIZE
        if not table_offset <= record_start <= table_end <= atlas_offset:
            raise AuditError(f"G1N table[{table_index}] range is invalid")
        record_bytes = table_end - record_start
        if record_bytes % RECORD_SIZE:
            raise AuditError(
                f"G1N table[{table_index}] record bytes are not divisible by {RECORD_SIZE}"
            )
        record_count = record_bytes // RECORD_SIZE
        if not 1 <= record_count <= MAP_ENTRIES:
            raise AuditError(f"G1N table[{table_index}] record_count={record_count}")
        map_blob = raw[table_offset:record_start]
        records_blob = raw[record_start:table_end]
        largest_ordinal = max(
            (value for (value,) in struct.iter_unpack("<H", map_blob)),
            default=0,
        )
        if largest_ordinal >= record_count:
            raise AuditError(
                f"G1N table[{table_index}] map ordinal {largest_ordinal} exceeds "
                f"record_count={record_count}"
            )
        tables.append(
            {
                "index": table_index,
                "offset": table_offset,
                "record_count": record_count,
                "mapped_nonzero_count": _mapped_nonzero(map_blob),
                "map_sha256": sha256_bytes(map_blob),
                "records_sha256": sha256_bytes(records_blob),
            }
        )

    header_region = raw[:header_size]
    palette_start = 0x20 + table_count * 4
    palette_region = raw[palette_start:header_size]
    atlas = raw[atlas_offset:]
    return {
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "declared_size": declared_size,
        "header_size": header_size,
        "unknown": unknown,
        "atlas_offset": atlas_offset,
        "atlas_size": len(atlas),
        "palette_count": palette_count,
        "table_count": table_count,
        "table_offsets": table_offsets,
        "header_sha256": sha256_bytes(header_region),
        "palette_sha256": sha256_bytes(palette_region),
        "pre_atlas_sha256": sha256_bytes(raw[:atlas_offset]),
        "atlas_sha256": sha256_bytes(atlas),
        "tables": tables,
    }


def _empty_scan_counts() -> dict[str, int]:
    return {
        "LINK": 0,
        "LZ4": 0,
        "G1N": 0,
        "G1T": 0,
        "G1M": 0,
        "DDS": 0,
        "RIFF": 0,
        "PNG": 0,
        "empty": 0,
        "other": 0,
        "link_entries_total": 0,
        "lz4_packed_bytes_total": 0,
        "lz4_unpacked_bytes_total": 0,
    }


def _scan_blob(blob: bytes, counts: dict[str, int], depth: int = 0) -> None:
    if depth > MAX_RECURSION:
        raise AuditError(f"container recursion exceeds {MAX_RECURSION}")
    if not blob:
        counts["empty"] += 1
        return
    if blob.startswith(b"LINK"):
        try:
            archive = parse_link(blob)
        except LinkError as exc:
            raise AuditError(f"invalid nested LINK: {exc}") from exc
        counts["LINK"] += 1
        counts["link_entries_total"] += len(archive.entries)
        for entry in archive.entries:
            _scan_blob(entry.data, counts, depth + 1)
        return
    if blob.startswith(G1N_MAGIC):
        parse_g1n_summary(blob)
        counts["G1N"] += 1
        return
    for magic, label in (
        (G1T_MAGIC, "G1T"),
        (G1M_MAGIC, "G1M"),
        (b"DDS ", "DDS"),
        (b"RIFF", "RIFF"),
        (b"\x89PNG\r\n\x1a\n", "PNG"),
    ):
        if blob.startswith(magic):
            counts[label] += 1
            return

    try:
        wrapper_header = parse_wrapper_header(blob)
    except LZ4Error:
        counts["other"] += 1
        return
    try:
        _, raw = decompress_wrapper(blob)
    except LZ4Error as exc:
        raise AuditError(f"plausible LZ4 wrapper does not decode: {exc}") from exc
    counts["LZ4"] += 1
    counts["lz4_packed_bytes_total"] += wrapper_header.compressed_size
    counts["lz4_unpacked_bytes_total"] += len(raw)
    _scan_blob(raw, counts, depth + 1)


def _unwrap_direct_g1n(blob: bytes) -> tuple[int, bytes] | None:
    depth = 0
    current = blob
    while depth <= MAX_RECURSION:
        if current.startswith(G1N_MAGIC):
            return depth, current
        try:
            parse_wrapper_header(current)
        except LZ4Error:
            return None
        try:
            _, current = decompress_wrapper(current)
        except LZ4Error as exc:
            raise AuditError(f"direct outer wrapper does not decode: {exc}") from exc
        depth += 1
    raise AuditError(f"direct outer wrapper depth exceeds {MAX_RECURSION}")


def inspect_archive(path: Path, spec: ArchiveSpec) -> tuple[dict[str, Any], dict[int, bytes]]:
    try:
        blob = path.read_bytes()
    except OSError as exc:
        raise AuditError(f"cannot read required input {spec.logical_path}: {exc}") from exc
    try:
        outer = parse_link(blob)
    except LinkError as exc:
        raise AuditError(f"{spec.logical_path}: root is not a valid LINK: {exc}") from exc

    counts = _empty_scan_counts()
    _scan_blob(blob, counts)
    direct_objects: list[dict[str, Any]] = []
    direct_raw: dict[int, bytes] = {}
    for entry in outer.entries:
        result = _unwrap_direct_g1n(entry.data)
        if result is None:
            continue
        wrapper_depth, raw = result
        summary = parse_g1n_summary(raw)
        direct_objects.append(
            {
                "outer_entry": entry.index,
                "wrapper_depth": wrapper_depth,
                **summary,
            }
        )
        direct_raw[entry.index] = raw

    actual_indices = [item["outer_entry"] for item in direct_objects]
    expected_indices = EXPECTED_DIRECT_G1N[spec.logical_path]
    if actual_indices != expected_indices:
        raise AuditError(
            f"{spec.logical_path}: direct G1N entries={actual_indices}, "
            f"expected={expected_indices}"
        )
    if counts["G1N"] != len(expected_indices):
        raise AuditError(
            f"{spec.logical_path}: recursive G1N count={counts['G1N']}, "
            f"expected={len(expected_indices)}"
        )

    return (
        {
            "language": spec.language,
            "route": spec.route,
            "family": spec.family,
            "logical_path": spec.logical_path,
            "file_size": len(blob),
            "file_sha256": sha256_bytes(blob),
            "outer_link_entry_count": len(outer.entries),
            "recursive_counts": counts,
            "direct_g1n_outer_entries": actual_indices,
            "direct_g1n": direct_objects,
        },
        direct_raw,
    )


def _table_projection(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "index": table["index"],
            "offset": table["offset"],
            "record_count": table["record_count"],
            "mapped_nonzero_count": table["mapped_nonzero_count"],
            "map_sha256": table["map_sha256"],
            "records_sha256": table["records_sha256"],
        }
        for table in summary["tables"]
    ]


def compare_jp_g1n(
    base_raw: bytes,
    pk_raw: bytes,
    pair: dict[str, Any],
) -> dict[str, Any]:
    base = parse_g1n_summary(base_raw)
    pk = parse_g1n_summary(pk_raw)
    layout_keys = (
        "raw_size",
        "declared_size",
        "header_size",
        "unknown",
        "atlas_offset",
        "atlas_size",
        "palette_count",
        "table_count",
        "table_offsets",
    )
    layout_equal = all(base[key] == pk[key] for key in layout_keys)
    tables_equal = _table_projection(base) == _table_projection(pk)
    palette_equal = base["palette_sha256"] == pk["palette_sha256"]
    header_equal = base["header_sha256"] == pk["header_sha256"]
    pre_atlas_equal = base["pre_atlas_sha256"] == pk["pre_atlas_sha256"]
    atlas = base_raw[base["atlas_offset"] :]
    pk_atlas = pk_raw[pk["atlas_offset"] :]
    atlas_length_equal = len(atlas) == len(pk_atlas)
    changed_atlas_byte_count = (
        sum(left != right for left, right in zip(atlas, pk_atlas, strict=True))
        if atlas_length_equal
        else -1
    )
    atlas_equal = base["atlas_sha256"] == pk["atlas_sha256"]
    only_atlas_bytes_differ = (
        layout_equal
        and header_equal
        and palette_equal
        and tables_equal
        and pre_atlas_equal
        and atlas_length_equal
        and not atlas_equal
        and changed_atlas_byte_count > 0
    )
    result = {
        **pair,
        "base_raw_size": base["raw_size"],
        "base_raw_sha256": base["raw_sha256"],
        "pk_raw_size": pk["raw_size"],
        "pk_raw_sha256": pk["raw_sha256"],
        "layout_equal": layout_equal,
        "header_equal": header_equal,
        "palette_equal": palette_equal,
        "table_maps_and_records_equal": tables_equal,
        "pre_atlas_equal": pre_atlas_equal,
        "base_pre_atlas_sha256": base["pre_atlas_sha256"],
        "pk_pre_atlas_sha256": pk["pre_atlas_sha256"],
        "atlas_length_equal": atlas_length_equal,
        "base_atlas_sha256": base["atlas_sha256"],
        "pk_atlas_sha256": pk["atlas_sha256"],
        "atlas_equal": atlas_equal,
        "changed_atlas_byte_count": changed_atlas_byte_count,
        "only_atlas_bytes_differ": only_atlas_bytes_differ,
        "tables": _table_projection(base),
    }
    if not only_atlas_bytes_differ:
        raise AuditError(
            f"JP {pair['profile']} G1N pair is not identical outside a non-empty atlas diff"
        )
    return result


def _route_matrix(archives: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "language": item["language"],
            "route": item["route"],
            "family": item["family"],
            "logical_path": item["logical_path"],
            "recursive_g1n_count": item["recursive_counts"]["G1N"],
            "direct_g1n_outer_entries": item["direct_g1n_outer_entries"],
        }
        for item in archives
    ]


def build_report(game_root: Path) -> dict[str, Any]:
    """Build a deterministic report; this function performs reads only."""

    root = game_root.resolve()
    if not root.is_dir():
        raise AuditError(f"private game root is not a directory: {game_root}")

    archives: list[dict[str, Any]] = []
    direct_raw_by_path: dict[str, dict[int, bytes]] = {}
    for spec in ARCHIVE_SPECS:
        # All logical paths are fixed literals without parent traversal.
        path = root.joinpath(*spec.logical_path.split("/"))
        summary, direct_raw = inspect_archive(path, spec)
        archives.append(summary)
        direct_raw_by_path[spec.logical_path] = direct_raw

    comparisons = [
        compare_jp_g1n(
            direct_raw_by_path[pair["base_logical_path"]][pair["base_outer_entry"]],
            direct_raw_by_path[pair["pk_logical_path"]][pair["pk_outer_entry"]],
            pair,
        )
        for pair in JP_G1N_PAIRS
    ]
    return {
        "schema": SCHEMA,
        "inspector_version": INSPECTOR_VERSION,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_extracted_binary_payload": False,
            "contains_only_counts_sizes_hashes_and_boolean_structure": True,
        },
        "scope": {
            "languages": ["SC", "TC", "EN", "JP"],
            "routes": ["base", "pk"],
            "families": ["regular", "expansion"],
            "archive_count": len(ARCHIVE_SPECS),
            "port_archives_in_scope": False,
            "runtime_loader_trace_in_scope": False,
        },
        "route_matrix": _route_matrix(archives),
        "archives": archives,
        "jp_base_pk_g1n_comparisons": comparisons,
        "conclusions": {
            "sc_tc_en_pk_have_no_recursive_g1n": True,
            "jp_pk_has_two_recursive_g1n": True,
            "base_regular_archives_have_two_recursive_g1n": True,
            "all_expansion_archives_have_zero_recursive_g1n": True,
            "jp_pairs_differ_only_in_atlas_bytes": True,
        },
    }


def verify_expected(actual: dict[str, Any], expected_path: Path) -> None:
    try:
        expected = _strict_json(expected_path.read_bytes(), str(expected_path))
    except OSError as exc:
        raise AuditError(f"cannot read expected evidence {expected_path}: {exc}") from exc
    if canonical_json(actual) != canonical_json(expected):
        raise AuditError("private inputs do not match the pinned evidence")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-root",
        type=Path,
        required=True,
        help="private NOBU16 root containing RES_SC, RES_TC, RES_EN, and RES_JP trees",
    )
    parser.add_argument(
        "--expect",
        type=Path,
        help="read-only exact comparison against a source-free evidence JSON",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="emit canonical one-line JSON instead of indented JSON",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = build_report(args.game_root)
        if args.expect is not None:
            verify_expected(report, args.expect)
            print("PASS: private archives exactly match pinned source-free evidence")
            return 0
        if args.compact:
            sys.stdout.buffer.write(canonical_json(report) + b"\n")
        else:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0
    except (AuditError, OSError, LinkError, LZ4Error, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
