#!/usr/bin/env python3
"""Build the private W45 PC union candidate for reviewed dialogue and event fixes.

This builder deliberately reconstructs every output from W45 Steam-PC inputs and
the *record/literal diffs* of prior private candidates.  It never copies a
component packed file over another component, and it has no Steam apply, Git,
network, transaction, or release capability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME_ROOT = REPO / "workstreams" / "msggame"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_NAME = "candidate"

for import_root in (TOOLS, MSGGAME_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
import msggame_format as msggame  # noqa: E402


class UnionError(RuntimeError):
    """Raised when a W45 source, component, merge, or private output drifts."""


@dataclass(frozen=True)
class ResourceSpec:
    relative: str
    kind: str
    source: Path
    input_sha256: str


@dataclass(frozen=True)
class PackedResource:
    packed: bytes
    header: Any
    raw: bytes
    parsed: Any


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Profile]
    merged: Mapping[str, Mapping[Any, Any]]
    component_counts: Mapping[str, Mapping[str, int]]
    overlaps: tuple[Mapping[str, Any], ...]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


BASE_MSGGAME = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin")
PK_MSGGAME = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin")
PK_MSGDATA = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgdata.bin")
PK_EVENT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")

RESOURCES: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        "MSG/JP/msggame.bin",
        "msggame",
        BASE_MSGGAME,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
    ),
    ResourceSpec(
        "MSG_PK/JP/msggame.bin",
        "msggame",
        PK_MSGGAME,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
    ),
    ResourceSpec(
        "MSG_PK/JP/msgdata.bin",
        "table",
        PK_MSGDATA,
        "8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A",
    ),
    ResourceSpec(
        "MSG_PK/JP/msgev.bin",
        "table",
        PK_EVENT,
        "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    ),
)
RESOURCE_BY_RELATIVE = {spec.relative: spec for spec in RESOURCES}

COMPONENT_ROOTS = {
    "wave53": REPO / "tmp" / "pc_private_union_composite_wave53_v1" / "candidate",
    "event3956": REPO / "tmp" / "pc_event_3956_name_semantic_reflow_v1" / "candidate",
    "semantic8": REPO / "tmp" / "pc_event_semantic_reflow_wave54_v1" / "candidate",
    "event_batch_a": REPO / "tmp" / "pc_event_tag_reflow_batch_a_candidate_v1" / "candidate",
    "event_batch_b": REPO / "tmp" / "pc_event_tag_reflow_batch_b_candidate_v1" / "candidate",
    "event_batch_c": REPO / "tmp" / "pc_event_tag_reflow_batch_c_candidate_v1" / "candidate",
    "b17": REPO / "tmp" / "pc_b17_static_quality_candidate_v1" / "candidate",
}
COMPONENT_RESOURCE_HASHES: Mapping[str, Mapping[str, str]] = {
    "wave53": {
        "MSG/JP/msggame.bin": "50E78AE5BE920454EC8F4B20A485FEF2A1237F593EBF97D205799A2AD705E2B8",
        "MSG_PK/JP/msggame.bin": "E470EA330510C571E7B142211C27C49E4E4508C1026FEA6BBC55F07675B71FD7",
        "MSG_PK/JP/msgdata.bin": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        "MSG_PK/JP/msgev.bin": "E088299D725472827D32B3F16541DD49663C5CD80FA8CA4FF3E5C9BCBCD0B2AF",
    },
    "event3956": {"MSG_PK/JP/msgev.bin": "D7CA54F9F942251B980B6D0ECC88347FAF794408EBA6AFC779B43897D6532218"},
    "semantic8": {"MSG_PK/JP/msgev.bin": "30CED81B2F9B3B02FE0F8EFFEA1D9CF05E513E854CCAC3B84C6B7213947EB429"},
    "event_batch_a": {"MSG_PK/JP/msgev.bin": "BE5734E36B18153622A6306006F3BCE7A9C217FCF856E006A7D5C32D4CFCB676"},
    "event_batch_b": {"MSG_PK/JP/msgev.bin": "5325EE8C902CE834A2C18D243A23D40393873ED167D925FF7F105E8CDA6299AF"},
    "event_batch_c": {"MSG_PK/JP/msgev.bin": "DE3B6899F82D7C9A0781AD54AF635EF2061C59BF8DFA0E6BFD984EB5343FD31A"},
    "b17": {"MSG_PK/JP/msggame.bin": "B03D4EFBFC61BD1BCCFC5472052805D79CC215996394211D23DB197B3CC4D9C9"},
}
COMPONENT_EXPECTED_RECORDS: Mapping[str, Mapping[str, int]] = {
    "wave53": {
        "MSG/JP/msggame.bin": 67,
        "MSG_PK/JP/msggame.bin": 166,
        "MSG_PK/JP/msgdata.bin": 4,
        "MSG_PK/JP/msgev.bin": 52,
    },
    "event3956": {"MSG_PK/JP/msgev.bin": 1},
    "semantic8": {"MSG_PK/JP/msgev.bin": 8},
    "event_batch_a": {"MSG_PK/JP/msgev.bin": 10},
    "event_batch_b": {"MSG_PK/JP/msgev.bin": 10},
    "event_batch_c": {"MSG_PK/JP/msgev.bin": 11},
    "b17": {"MSG_PK/JP/msggame.bin": 31},
}
COMPONENT_ORDER = (
    "wave53",
    "event3956",
    "semantic8",
    "event_batch_a",
    "event_batch_b",
    "event_batch_c",
    "b17",
)

EVENT_3960_TARGET = (
    "교묘한 수였으나, \x1bCA모토나리\x1bCZ의\n"
    "끝까지 비정한 결단으로 \x1bCB이노우에 일파\x1bCZ의\n"
    "가문 내 영향력은 일소되었다."
)
WAVE53_B17_1064_TARGET = "이…\n이번 싸움은 우리가 졌군……"
B17_COMPONENT_1064_TARGET = "이…\n이번 싸움은 우리가 졌군…"

EXPECTED_FINAL_RECORD_COUNTS = {
    "MSG/JP/msggame.bin": 67,
    "MSG_PK/JP/msggame.bin": 196,
    "MSG_PK/JP/msgdata.bin": 4,
    "MSG_PK/JP/msgev.bin": 91,
}
EXPECTED_FINAL_TOTAL = 358

# Filled from the deterministic `profile` command before build/test/commit.
EXPECTED_OUTPUT_PROFILES: Mapping[str, Profile] = {
    "MSG/JP/msggame.bin": Profile(
        1_504_462,
        "50E78AE5BE920454EC8F4B20A485FEF2A1237F593EBF97D205799A2AD705E2B8",
        1_498_560,
        "8B14B76B1A3479C6261D4E2D8C8FD65877B4A3783EC8AF778C9F2B49679D3706",
    ),
    "MSG_PK/JP/msggame.bin": Profile(
        1_806_402,
        "646E806CADA8AD81D2ACC133F46B7559B268004FD9CF14F8E44257680435F79D",
        1_799_320,
        "AC24C163FF93540A836B58244A5D02BF9BBB7573483F3C7DFDC159412BB6B800",
    ),
    "MSG_PK/JP/msgdata.bin": Profile(
        496_999,
        "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        495_032,
        "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
    ),
    "MSG_PK/JP/msgev.bin": Profile(
        994_715,
        "959202F26B8D49A1D554688DA5B6DE29521405E13131DB9BE156C22728FC20A7",
        990_804,
        "DD08819BE730C922707D219F68CFBD6120BEE43B677B578CC3B0B37D3EAFC552",
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise UnionError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile(blob: bytes) -> Profile:
    header, raw = decompress_wrapper(blob)
    del header
    return Profile(len(blob), sha256_bytes(blob), len(raw), sha256_bytes(raw))


def profile_dict(value: Profile) -> dict[str, Any]:
    return {
        "size": value.size,
        "sha256": value.sha256,
        "raw_size": value.raw_size,
        "raw_sha256": value.raw_sha256,
    }


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnionError(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_source(spec: ResourceSpec) -> PackedResource:
    require(spec.source.is_file(), f"W45 source absent: {spec.relative}")
    packed = spec.source.read_bytes()
    require(sha256_bytes(packed) == spec.input_sha256, f"W45 source hash differs: {spec.relative}")
    header, raw = decompress_wrapper(packed)
    if spec.kind == "msggame":
        parsed = msggame.parse_packed_msggame(packed).archive
    else:
        parsed = parse_message_table(raw)
    return PackedResource(packed, header, raw, parsed)


def record_map(archive: Any) -> dict[tuple[int, int], bytes]:
    return {
        (record.block_id, record.record_id): record.data
        for block in archive.blocks
        for record in block.records
    }


def record_literal_texts(data: bytes, coordinate: tuple[int, int]) -> tuple[str, ...]:
    record = msggame.MsgGameRecord(coordinate[0], coordinate[1], 0, data)
    return tuple(literal.text for literal in msggame.parse_record_literals(record))


def diff_resource(spec: ResourceSpec, base: PackedResource, candidate: Path) -> dict[Any, Any]:
    require(candidate.is_file(), f"component output absent: {candidate}")
    candidate_packed = candidate.read_bytes()
    if spec.kind == "msggame":
        before = record_map(base.parsed)
        after = record_map(msggame.parse_packed_msggame(candidate_packed).archive)
        require(set(before) == set(after), f"component record topology differs: {candidate}")
        return {key: after[key] for key in before if before[key] != after[key]}
    _header, raw = decompress_wrapper(candidate_packed)
    after_table = parse_message_table(raw)
    require(len(after_table.texts) == len(base.parsed.texts), f"component table size differs: {candidate}")
    return {
        index: after_table.texts[index]
        for index, before in enumerate(base.parsed.texts)
        if before != after_table.texts[index]
    }


def record_count(spec: ResourceSpec, changes: Mapping[Any, Any]) -> int:
    # MSGGAME resources use opaque (block, record) units; table resources use
    # entry IDs.  The component manifests use the same coordinate convention.
    del spec
    return len(changes)


def load_component_diffs(
    sources: Mapping[str, PackedResource],
) -> tuple[dict[str, dict[str, dict[Any, Any]]], dict[str, dict[str, int]]]:
    all_diffs: dict[str, dict[str, dict[Any, Any]]] = {}
    counts: dict[str, dict[str, int]] = {}
    for component in COMPONENT_ORDER:
        root = COMPONENT_ROOTS[component]
        expected_hashes = COMPONENT_RESOURCE_HASHES[component]
        require(root.is_dir(), f"component candidate absent: {component}")
        component_diffs: dict[str, dict[Any, Any]] = {}
        component_counts: dict[str, int] = {}
        for relative, expected_hash in expected_hashes.items():
            spec = RESOURCE_BY_RELATIVE[relative]
            path = root / relative
            require(sha256_path(path) == expected_hash, f"component hash differs: {component} {relative}")
            changes = diff_resource(spec, sources[relative], path)
            component_diffs[relative] = changes
            component_counts[relative] = record_count(spec, changes)
        require(
            component_counts == COMPONENT_EXPECTED_RECORDS[component],
            f"component W45 diff scope differs: {component} {component_counts}",
        )
        all_diffs[component] = component_diffs
        counts[component] = component_counts
    return all_diffs, counts


def merge_diffs(
    component_diffs: Mapping[str, Mapping[str, Mapping[Any, Any]]],
) -> tuple[dict[str, dict[Any, Any]], tuple[Mapping[str, Any], ...]]:
    merged: dict[str, dict[Any, Any]] = {spec.relative: {} for spec in RESOURCES}
    provenance: dict[str, dict[Any, str]] = {spec.relative: {} for spec in RESOURCES}
    overlaps: list[Mapping[str, Any]] = []
    for component in COMPONENT_ORDER:
        for relative, changes in component_diffs[component].items():
            for coordinate, target in changes.items():
                if coordinate not in merged[relative]:
                    merged[relative][coordinate] = target
                    provenance[relative][coordinate] = component
                    continue
                previous_component = provenance[relative][coordinate]
                previous = merged[relative][coordinate]
                if relative == "MSG_PK/JP/msgev.bin" and coordinate == 3960:
                    require(previous_component == "wave53", "3960 prior component differs")
                    require(component == "event_batch_c", "3960 replacement component differs")
                    require(target == EVENT_3960_TARGET, "3960 target differs")
                    require(previous != target, "3960 replacement is not distinct")
                    merged[relative][coordinate] = target
                    provenance[relative][coordinate] = component
                    overlaps.append(
                        {
                            "resource": relative,
                            "coordinate": 3960,
                            "previous_component": previous_component,
                            "incoming_component": component,
                            "resolution": "incoming_event_batch_c_replaces_wave53_name_only",
                        }
                    )
                    continue
                if relative == "MSG_PK/JP/msggame.bin" and coordinate == (17, 1064):
                    require(previous_component == "wave53", "17:1064 prior component differs")
                    require(component == "b17", "17:1064 incoming component differs")
                    require(
                        record_literal_texts(previous, coordinate)[1] == WAVE53_B17_1064_TARGET,
                        "wave53 17:1064 literal target differs",
                    )
                    require(
                        record_literal_texts(target, coordinate)[1] == B17_COMPONENT_1064_TARGET,
                        "B17 17:1064 literal target differs",
                    )
                    overlaps.append(
                        {
                            "resource": relative,
                            "coordinate": [17, 1064],
                            "previous_component": previous_component,
                            "incoming_component": component,
                            "resolution": "keep_wave53_existing_semantic_fix_project_ellipsis_style",
                        }
                    )
                    continue
                raise UnionError(
                    f"unexpected duplicate coordinate: {relative} {coordinate!r} "
                    f"{previous_component}->{component}"
                )
    expected_overlaps = (
        {
            "resource": "MSG_PK/JP/msgev.bin",
            "coordinate": 3960,
            "previous_component": "wave53",
            "incoming_component": "event_batch_c",
            "resolution": "incoming_event_batch_c_replaces_wave53_name_only",
        },
        {
            "resource": "MSG_PK/JP/msggame.bin",
            "coordinate": [17, 1064],
            "previous_component": "wave53",
            "incoming_component": "b17",
            "resolution": "keep_wave53_existing_semantic_fix_project_ellipsis_style",
        },
    )
    require(tuple(overlaps) == expected_overlaps, f"overlap set differs: {overlaps!r}")
    return merged, tuple(overlaps)


def rebuild_resource(spec: ResourceSpec, base: PackedResource, changes: Mapping[Any, Any]) -> bytes:
    if spec.kind == "msggame":
        rebuilt = msggame.rebuild_packed_msggame(base.packed, changes)
        rebuilt_archive = msggame.parse_packed_msggame(rebuilt).archive
        before = record_map(base.parsed)
        after = record_map(rebuilt_archive)
        changed = {key: after[key] for key in before if before[key] != after[key]}
        require(changed == dict(changes), f"rebuilt msggame scope differs: {spec.relative}")
        return rebuilt
    texts = list(base.parsed.texts)
    for entry_id, target in changes.items():
        texts[entry_id] = target
    raw = rebuild_message_table(base.parsed, tuple(texts))
    rebuilt = recompress_wrapper(raw, base.header)
    header, decoded = decompress_wrapper(rebuilt)
    after = parse_message_table(decoded)
    require(rebuild_message_table(after, after.texts) == decoded, f"table parser round trip differs: {spec.relative}")
    require(recompress_wrapper(decoded, header) == rebuilt, f"table LZ4 round trip differs: {spec.relative}")
    changed = {
        index: after.texts[index]
        for index, before in enumerate(base.parsed.texts)
        if before != after.texts[index]
    }
    require(changed == dict(changes), f"rebuilt table scope differs: {spec.relative}")
    return rebuilt


def source_profiles(sources: Mapping[str, PackedResource]) -> dict[str, Profile]:
    return {relative: profile(value.packed) for relative, value in sources.items()}


def prepare(*, require_output_profiles: bool) -> Bundle:
    sources = {spec.relative: load_source(spec) for spec in RESOURCES}
    component_diffs, component_counts = load_component_diffs(sources)
    merged, overlaps = merge_diffs(component_diffs)
    final_counts = {
        spec.relative: record_count(spec, merged[spec.relative])
        for spec in RESOURCES
    }
    require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, f"final count differs: {final_counts}")
    require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL, "final total differs")
    outputs = {
        spec.relative: rebuild_resource(spec, sources[spec.relative], merged[spec.relative])
        for spec in RESOURCES
    }
    profiles = {relative: profile(blob) for relative, blob in outputs.items()}
    if require_output_profiles:
        require(set(EXPECTED_OUTPUT_PROFILES) == set(RESOURCE_BY_RELATIVE), "final output profiles are not pinned")
        for relative, expected in EXPECTED_OUTPUT_PROFILES.items():
            require(profiles[relative] == expected, f"final output profile differs: {relative}")
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave55-audit.v1",
        "source_policy": {
            "platform": "Steam PC",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "sources": {relative: profile_dict(value) for relative, value in source_profiles(sources).items()},
        "components": {
            name: {
                "candidate_root": str(COMPONENT_ROOTS[name].relative_to(REPO)).replace("\\", "/"),
                "record_counts": component_counts[name],
                "resource_hashes": COMPONENT_RESOURCE_HASHES[name],
            }
            for name in COMPONENT_ORDER
        },
        "overlaps": list(overlaps),
        "final_record_counts": final_counts,
        "final_total_records": EXPECTED_FINAL_TOTAL,
        "holds_excluded": {
            "base_block15_width": "15:1121",
            "b17_runtime_particle": ["17:920:0", "17:920:1"],
            "event_3960_name_only_component": "superseded by event batch C",
        },
        "outputs": {relative: profile_dict(value) for relative, value in profiles.items()},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave55-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": str(TMP_ROOT.relative_to(REPO)).replace("\\", "/"),
        "resources": {
            relative: {
                "relative": relative,
                "output": profile_dict(profiles[relative]),
                "changed_record_count": final_counts[relative],
            }
            for relative in RESOURCE_BY_RELATIVE
        },
        "final_total_records": EXPECTED_FINAL_TOTAL,
    }
    return Bundle(outputs, profiles, merged, component_counts, overlaps, audit, manifest)


def candidate_root() -> Path:
    return require_private(TMP_ROOT / CANDIDATE_NAME, "candidate root")


def write_candidate(bundle: Bundle) -> Path:
    output = candidate_root()
    require(not output.exists(), f"candidate output already exists: {output}")
    staging = require_private(TMP_ROOT / f".{CANDIDATE_NAME}.staging", "candidate staging")
    require(not staging.exists(), f"candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_candidate(bundle: Bundle) -> dict[str, Any]:
    root = candidate_root()
    require(root.is_dir(), f"candidate output absent: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *RESOURCE_BY_RELATIVE}
    actual_files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }
    require(actual_files == expected_files, f"candidate file set differs: {sorted(actual_files)}")
    for relative, expected in bundle.outputs.items():
        actual = (root / relative).read_bytes()
        require(actual == expected, f"candidate file differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require(
        (root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "candidate manifest differs",
    )
    return {
        "candidate_root": str(root.relative_to(REPO)).replace("\\", "/"),
        "changed_record_count": EXPECTED_FINAL_TOTAL,
        "changed_record_count_by_resource": EXPECTED_FINAL_RECORD_COUNTS,
        "overlap_count": len(bundle.overlaps),
        "steam_game_resource_written": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave55_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave55_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"authoring file absent: {path.name}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{line_number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(
        json.dumps(
            {
                "output_profiles": {
                    relative: profile_dict(value) for relative, value in bundle.profiles.items()
                },
                "final_record_counts": EXPECTED_FINAL_RECORD_COUNTS,
                "final_total_records": EXPECTED_FINAL_TOTAL,
                "overlaps": list(bundle.overlaps),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def command_build() -> int:
    bundle = prepare(require_output_profiles=True)
    root = write_candidate(bundle)
    print(json.dumps({"candidate_root": str(root.relative_to(REPO)).replace("\\", "/"), **verify_candidate(bundle)}, ensure_ascii=False, indent=2))
    return 0


def command_verify() -> int:
    bundle = prepare(require_output_profiles=True)
    print(json.dumps(verify_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_diff_check() -> int:
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    args = parser.parse_args()
    if args.command == "profile":
        return command_profile()
    if args.command == "build":
        return command_build()
    if args.command == "verify-private":
        return command_verify()
    return command_diff_check()


if __name__ == "__main__":
    raise SystemExit(main())
