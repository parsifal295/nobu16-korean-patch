#!/usr/bin/env python3
"""Build and verify the source-free PK msggame wave-06 partition."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
RESOURCE = "MSG_PK/SC/msggame.bin"
TARGET_CATALOG = REPO_ROOT / "data/public/translation_target_keys.v0.1.json"
PROGRESS = REPO_ROOT / "data/public/translation_progress.v0.1.json"
PARTITION_PATH = WORKSTREAM_ROOT / "partition.v1.json"
B04_PATH = REPO_ROOT / "workstreams/msggame_pk_ui_priority_b04/build_msggame_pk_ui_priority_b04.py"
B07_RELATIVE = (
    "workstreams/msggame_pk_ui_priority_b07/public/"
    "msggame_ko_pk_ui_priority_b07_300.v1.json"
)

TARGET_CATALOG_SHA256 = "E4207003341C214C7C124A9BC9A82E475851FF44D3B4C84A941F5E76F42DF142"
TARGET_COORDINATE_COUNT = 16_482
TARGET_COORDINATES_SHA256 = "60D7053C25D2AEA8D565A22BC7AFA7C18F233698EFB0975B54996665A02931AF"
PREFIX_PATTERN_COUNT = 34
PREFIX_PATTERNS_SHA256 = "BEAC189FB8E817BCAB9315A3C3CE761737EAB8FB0CC93F782C816DB69ADEAD52"
PREFIX_COORDINATE_COUNT = 11_722
PREFIX_COORDINATES_SHA256 = "82882CCE6B645BFDEE802AF5E4EDD47CD074C453E346AC64EAF4B8F6601A66FB"
REMAINING_COUNT = 4_760
REMAINING_COORDINATES_SHA256 = "3E5B0173AE80BDA5184CF01C7CD4F788C317F8195965EB87B2202F0116AD6D73"

BATCH_SPECS = (
    {
        "batch_id": "msggame_pk_parallel_b08_block17_a_625.v1",
        "block": 17,
        "start": 0,
        "stop": 625,
        "count": 625,
        "coordinates_sha256": "10033A34BA958C0788E3A33DEC9DF0337172A0347F1C4F508E262DE594DEC802",
    },
    {
        "batch_id": "msggame_pk_parallel_b09_block17_b_625.v1",
        "block": 17,
        "start": 625,
        "stop": 1_250,
        "count": 625,
        "coordinates_sha256": "04DBF294C76610745921910FB6C40C66AAA0EF35919FD8941ECCC997B86A88D7",
    },
    {
        "batch_id": "msggame_pk_parallel_b10_block17_c_623.v1",
        "block": 17,
        "start": 1_250,
        "stop": None,
        "count": 623,
        "coordinates_sha256": "1065BE788BFB31BA6DAE65B2C25C68ACB4ACC0129166FC62A609C029BA466941",
    },
    {
        "batch_id": "msggame_pk_parallel_b11_block15_a_546.v1",
        "block": 15,
        "start": 0,
        "stop": 546,
        "count": 546,
        "coordinates_sha256": "8C3F092D47CA408441CF5849DEE50405409DB48FCFDF25B58187174879446509",
    },
    {
        "batch_id": "msggame_pk_parallel_b12_block15_b_545.v1",
        "block": 15,
        "start": 546,
        "stop": None,
        "count": 545,
        "coordinates_sha256": "99883C7EEBEB4C393DC7605DC6701726D4AFD4471667C3CBB0EA2A55AA0BEE06",
    },
    {
        "batch_id": "msggame_pk_parallel_b13_block7_672.v1",
        "block": 7,
        "start": 0,
        "stop": None,
        "count": 672,
        "coordinates_sha256": "3D7FC482CFC520413FFDEF08D8A98667174FE6ACA8C690E1A12EBD230535BB86",
    },
    {
        "batch_id": "msggame_pk_parallel_b14_block6_628.v1",
        "block": 6,
        "start": 0,
        "stop": None,
        "count": 628,
        "coordinates_sha256": "BD9778DD3511F8F8378F389D7F1221BDCD1D4AB3EE86FB46CCEA8AF4E469035B",
    },
    {
        "batch_id": "msggame_pk_parallel_b15_misc_496.v1",
        "block": None,
        "start": 0,
        "stop": None,
        "count": 496,
        "coordinates_sha256": "34138FE21DF924D1A7016550789D5520229FAE574C5C8AE21A201AF1A8294B6A",
    },
)

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")


class PartitionError(ValueError):
    """Raised when a pinned source-free partition invariant changes."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def canonical_hash(value: Any) -> str:
    blob = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256(blob)


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PartitionError(f"JSON root must be an object: {path}")
    return value


def target_coordinates() -> set[tuple[int, int, int]]:
    blob = TARGET_CATALOG.read_bytes()
    if sha256(blob) != TARGET_CATALOG_SHA256:
        raise PartitionError("target catalog file pin changed")
    payload = json.loads(blob.decode("utf-8"))
    matches = [
        row for row in payload.get("resources", []) if row.get("path") == RESOURCE
    ]
    if len(matches) != 1:
        raise PartitionError("target catalog must contain one PK msggame row")
    row = matches[0]
    coordinates = {tuple(item) for item in row.get("target_coordinates", [])}
    if (
        len(coordinates) != TARGET_COORDINATE_COUNT
        or canonical_hash([list(item) for item in sorted(coordinates)])
        != TARGET_COORDINATES_SHA256
        or row.get("target_keys_sha256") != TARGET_COORDINATES_SHA256
    ):
        raise PartitionError("target coordinate pin changed")
    return coordinates


def resolve_pattern(pattern: str) -> Path:
    matches = sorted(REPO_ROOT.glob(pattern))
    if len(matches) != 1:
        raise PartitionError(f"progress pattern {pattern!r} resolved to {len(matches)} files")
    path = matches[0]
    if path.relative_to(REPO_ROOT).as_posix() != pattern:
        raise PartitionError("progress patterns must be exact logical paths")
    return path


def overlay_coordinates(path: Path) -> set[tuple[int, int, int]]:
    payload = read_json(path)
    if payload.get("resource") != RESOURCE:
        raise PartitionError(f"overlay resource mismatch: {path}")
    policy = payload.get("distribution_policy")
    if (
        not isinstance(policy, dict)
        or policy.get("contains_commercial_source_text") is not False
        or policy.get("contains_complete_game_resource") is not False
    ):
        raise PartitionError(f"overlay lacks source-free policy: {path}")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise PartitionError(f"overlay entries are invalid: {path}")
    coordinates: set[tuple[int, int, int]] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise PartitionError(f"overlay entry is invalid: {path}")
        coordinate = (
            entry.get("block_id"),
            entry.get("record_id"),
            entry.get("literal_id"),
        )
        if not all(type(value) is int for value in coordinate):
            raise PartitionError(f"overlay coordinate is invalid: {path}")
        coordinates.add(coordinate)
    if len(coordinates) != len(entries):
        raise PartitionError(f"overlay has duplicate coordinates: {path}")
    source = path.read_text(encoding="utf-8")
    if CJK_RE.search(source) or KANA_RE.search(source):
        raise PartitionError(f"commercial source script leaked into overlay: {path}")
    return coordinates


def registered_prefix(
    targets: set[tuple[int, int, int]],
) -> tuple[list[str], set[tuple[int, int, int]], list[str]]:
    progress = read_json(PROGRESS)
    matches = [
        row for row in progress.get("resources", []) if row.get("path") == RESOURCE
    ]
    if len(matches) != 1:
        raise PartitionError("progress must contain one PK msggame row")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(x, str) for x in patterns):
        raise PartitionError("PK msggame overlay list is invalid")
    if patterns.count(B07_RELATIVE) != 1:
        raise PartitionError("B07 boundary must be registered exactly once")
    boundary = patterns.index(B07_RELATIVE)
    prefix = patterns[: boundary + 1]
    suffix = patterns[boundary + 1 :]
    if (
        len(prefix) != PREFIX_PATTERN_COUNT
        or canonical_hash(prefix) != PREFIX_PATTERNS_SHA256
    ):
        raise PartitionError("B07 registration prefix changed")

    prefix_coordinates: set[tuple[int, int, int]] = set()
    for pattern in prefix:
        current = overlay_coordinates(resolve_pattern(pattern))
        if prefix_coordinates & current:
            raise PartitionError(f"registered prefix overlays overlap: {pattern}")
        prefix_coordinates.update(current)
    if (
        len(prefix_coordinates) != PREFIX_COORDINATE_COUNT
        or canonical_hash([list(item) for item in sorted(prefix_coordinates)])
        != PREFIX_COORDINATES_SHA256
        or not prefix_coordinates <= targets
    ):
        raise PartitionError("registered B07 coordinate prefix changed")

    suffix_coordinates: set[tuple[int, int, int]] = set()
    for pattern in suffix:
        current = overlay_coordinates(resolve_pattern(pattern))
        if current & prefix_coordinates or current & suffix_coordinates:
            raise PartitionError(f"post-B07 overlay overlaps history: {pattern}")
        if not current <= targets:
            raise PartitionError(f"post-B07 overlay escaped target catalog: {pattern}")
        suffix_coordinates.update(current)
    return prefix, prefix_coordinates, suffix


def compute_batches() -> tuple[set[tuple[int, int, int]], list[dict[str, Any]]]:
    targets = target_coordinates()
    _patterns, prefix, _suffix = registered_prefix(targets)
    remaining = targets - prefix
    if (
        len(remaining) != REMAINING_COUNT
        or canonical_hash([list(item) for item in sorted(remaining)])
        != REMAINING_COORDINATES_SHA256
    ):
        raise PartitionError("wave-06 remaining coordinate set changed")

    by_block = {
        block: sorted(item for item in remaining if item[0] == block)
        for block in (6, 7, 15, 17)
    }
    misc = sorted(item for item in remaining if item[0] not in by_block)
    batches: list[dict[str, Any]] = []
    union: set[tuple[int, int, int]] = set()
    for order, spec in enumerate(BATCH_SPECS, start=1):
        source = misc if spec["block"] is None else by_block[spec["block"]]
        coordinates = source[slice(spec["start"], spec["stop"])]
        coordinate_hash = canonical_hash([list(item) for item in coordinates])
        if len(coordinates) != spec["count"] or coordinate_hash != spec["coordinates_sha256"]:
            raise PartitionError(f"batch selection changed: {spec['batch_id']}")
        if union & set(coordinates):
            raise PartitionError(f"batch overlap: {spec['batch_id']}")
        union.update(coordinates)
        batches.append(
            {
                "order": order,
                "batch_id": spec["batch_id"],
                "selection": {
                    "block": spec["block"],
                    "sorted_slice_start": spec["start"],
                    "sorted_slice_stop": spec["stop"],
                },
                "coordinate_count": len(coordinates),
                "coordinates_sha256": coordinate_hash,
                "first_coordinate": list(coordinates[0]),
                "last_coordinate": list(coordinates[-1]),
                "coordinates": [list(item) for item in coordinates],
            }
        )
    if union != remaining:
        raise PartitionError("batch union does not equal all remaining coordinates")
    return remaining, batches


def make_partition() -> dict[str, Any]:
    remaining, batches = compute_batches()
    return {
        "schema": "nobu16.kr.msggame-pk-parallel-wave06-partition.v1",
        "resource": RESOURCE,
        "source_free": True,
        "contains_commercial_source_text": False,
        "immutable_boundary": {
            "last_registered_overlay": B07_RELATIVE,
            "pattern_count": PREFIX_PATTERN_COUNT,
            "patterns_sha256": PREFIX_PATTERNS_SHA256,
            "coordinate_count": PREFIX_COORDINATE_COUNT,
            "coordinates_sha256": PREFIX_COORDINATES_SHA256,
            "future_registrations_do_not_feed_partition": True,
        },
        "target_catalog": {
            "path": TARGET_CATALOG.relative_to(REPO_ROOT).as_posix(),
            "file_sha256": TARGET_CATALOG_SHA256,
            "coordinate_count": TARGET_COORDINATE_COUNT,
            "coordinates_sha256": TARGET_COORDINATES_SHA256,
        },
        "remaining": {
            "coordinate_count": len(remaining),
            "coordinates_sha256": REMAINING_COORDINATES_SHA256,
            "block_counts": {
                str(block): sum(item[0] == block for item in remaining)
                for block in sorted({item[0] for item in remaining})
            },
        },
        "batch_count": len(batches),
        "batches": batches,
        "proofs": {
            "batches_pairwise_disjoint": True,
            "batch_union_equals_remaining": True,
            "remaining_disjoint_from_registered_prefix": True,
            "remaining_subset_of_exact_target_catalog": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "complete_game_resource_included": False,
            "commercial_source_text_included": False,
            "executable_modified": False,
            "registry_modified": False,
            "process_memory_access": False,
        },
    }


def _load_b04() -> Any:
    spec = importlib.util.spec_from_file_location("wave06_b04_context", B04_PATH)
    if spec is None or spec.loader is None:
        raise PartitionError("cannot load pinned B04 parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _matching_source(candidates: list[Path], expected_sha256: str, label: str) -> Path:
    for path in candidates:
        if path.is_file() and sha256(path.read_bytes()) == expected_sha256:
            return path.resolve()
    raise PartitionError(f"pinned private {label} source is unavailable")


def default_sources(builder: Any) -> dict[str, Path]:
    return {
        "SC": _matching_source(
            [builder.DEFAULT_PK_SC], builder.SOURCE_PINS["SC"]["packed_sha256"], "SC"
        ),
        "JP": _matching_source(
            [
                GAME_ROOT / "MSG_PK/JP/msggame.bin",
                GAME_ROOT
                / "KR_PATCH_BACKUP/file_only_transaction/jp-runtime-wave05-20260715-v1/"
                "originals/MSG_PK/JP/msggame.bin",
            ],
            builder.SOURCE_PINS["JP"]["packed_sha256"],
            "JP",
        ),
        "EN": _matching_source(
            [builder.DEFAULT_PK_EN], builder.SOURCE_PINS["EN"]["packed_sha256"], "EN"
        ),
        "TC": _matching_source(
            [builder.DEFAULT_PK_TC], builder.SOURCE_PINS["TC"]["packed_sha256"], "TC"
        ),
    }


def export_private_context(output_root: Path) -> dict[str, Any]:
    tmp_root = (REPO_ROOT / "tmp").resolve()
    output = output_root.resolve()
    try:
        output.relative_to(tmp_root)
    except ValueError as exc:
        raise PartitionError("private context must stay under repository tmp") from exc
    output.mkdir(parents=True, exist_ok=True)
    builder = _load_b04()
    paths = default_sources(builder)
    before = {label: sha256(path.read_bytes()) for label, path in paths.items()}
    sources = {label: builder.load_source(path, label) for label, path in paths.items()}
    partition = make_partition()
    reports = []
    for batch in partition["batches"]:
        entries = []
        for raw_coordinate in batch["coordinates"]:
            coordinate = tuple(raw_coordinate)
            row = {"coordinate": raw_coordinate, "official": {}, "record_literal_counts": {}}
            for label, source in sources.items():
                literal = source["literals"].get(coordinate)
                row["official"][label] = None if literal is None else literal.text
                block, record, _literal = coordinate
                if block < len(source["archive"].blocks) and record < len(source["archive"].blocks[block].records):
                    row["record_literal_counts"][label] = len(
                        builder.parse_record_literals(source["archive"].blocks[block].records[record])
                    )
                else:
                    row["record_literal_counts"][label] = None
            sc_text = row["official"]["SC"]
            row["sc_invariants"] = builder.common.message_invariants(sc_text)
            entries.append(row)
        payload = {
            "schema": "nobu16.kr.private-msggame-wave06-context.v1",
            "private_commercial_source_context": True,
            "must_not_be_committed": True,
            "batch_id": batch["batch_id"],
            "coordinate_count": batch["coordinate_count"],
            "coordinates_sha256": batch["coordinates_sha256"],
            "entries": entries,
        }
        path = output / f"{batch['batch_id']}.private.json"
        path.write_bytes(encode_json(payload))
        reports.append({"path": str(path), "size": path.stat().st_size, "sha256": sha256(path.read_bytes())})
    after = {label: sha256(path.read_bytes()) for label, path in paths.items()}
    if before != after:
        raise PartitionError("private source changed during context export")
    return {"batch_count": len(reports), "reports": reports, "sources_unchanged": True}


def command_build(args: argparse.Namespace) -> int:
    payload = make_partition()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encode_json(payload))
    print(json.dumps({"output": str(args.output), "sha256": sha256(args.output.read_bytes())}, indent=2))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    expected = encode_json(make_partition())
    actual = args.partition.read_bytes()
    if actual != expected:
        raise PartitionError("checked partition differs from deterministic rebuild")
    print(json.dumps({"partition": str(args.partition), "sha256": sha256(actual), "ok": True}, indent=2))
    return 0


def command_export(args: argparse.Namespace) -> int:
    print(json.dumps(export_private_context(args.output_root), ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    commands = value.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--output", type=Path, default=PARTITION_PATH)
    build.set_defaults(handler=command_build)
    verify = commands.add_parser("verify")
    verify.add_argument("--partition", type=Path, default=PARTITION_PATH)
    verify.set_defaults(handler=command_verify)
    export = commands.add_parser("export-private")
    export.add_argument("--output-root", type=Path, required=True)
    export.set_defaults(handler=command_export)
    return value


def main() -> int:
    args = parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
