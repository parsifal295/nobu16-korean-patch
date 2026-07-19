#!/usr/bin/env python3
"""Build the private W58 Steam-PC text union from pinned W56 and dialogue fixes.

Every component is diffed against the W45 PC baseline before merge.  MSGGAME
uses complete opaque records so text replacement never drops an existing
runtime/control-byte change.  This builder cannot apply to Steam, commit, push,
or create a release.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_NAME = "candidate"
W56_BUILDER = REPO / "workstreams" / "pc_private_union_composite_wave56_v1" / "build_pc_private_union_composite_wave56_v1.py"


def load_wave56() -> Any:
    spec = importlib.util.spec_from_file_location("pc_private_union_composite_wave56_for_wave58", W56_BUILDER)
    if spec is None or spec.loader is None:  # pragma: no cover - import guard
        raise RuntimeError(f"cannot import W56 builder: {W56_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


wave56 = load_wave56()
core = wave56.wave55


class UnionError(RuntimeError):
    """Raised when the pinned source/component contracts are violated."""


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    root: Path
    resource_hashes: Mapping[str, str]
    record_counts: Mapping[str, int]


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    merged: Mapping[str, Mapping[Any, Any]]
    component_counts: Mapping[str, Mapping[str, int]]
    overlaps: tuple[Mapping[str, Any], ...]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


COMPONENTS = (
    ComponentSpec(
        "wave56",
        REPO / "tmp" / "pc_private_union_composite_wave56_v1" / "candidate",
        {
            "MSG/JP/msggame.bin": "50E78AE5BE920454EC8F4B20A485FEF2A1237F593EBF97D205799A2AD705E2B8",
            "MSG_PK/JP/msggame.bin": "EC57BA8BA01BDD8743A894A721416941A2D4BF5FD665C100FFD4C99FE5DE5A6F",
            "MSG_PK/JP/msgdata.bin": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
            "MSG_PK/JP/msgev.bin": "959202F26B8D49A1D554688DA5B6DE29521405E13131DB9BE156C22728FC20A7",
        },
        {
            "MSG/JP/msggame.bin": 67,
            "MSG_PK/JP/msggame.bin": 198,
            "MSG_PK/JP/msgdata.bin": 4,
            "MSG_PK/JP/msgev.bin": 91,
        },
    ),
    ComponentSpec(
        "b00_b05",
        REPO / "tmp" / "pc_b00_b05_static_quality_candidate_v1" / "candidate",
        {
            "MSG/JP/msggame.bin": "7A60B8CFB105893569127A707422980AE60CACF5346AEEA46D2744E0F924E971",
            "MSG_PK/JP/msggame.bin": "0121A40493D0A963F8685AB625E6922805C3DA56FEF42F49B337BBB584FC8DFF",
        },
        {"MSG/JP/msggame.bin": 5, "MSG_PK/JP/msggame.bin": 3},
    ),
    ComponentSpec(
        "b07_b10",
        REPO / "tmp" / "pc_b07_b10_static_quality_candidate_v1" / "candidate",
        {
            "MSG/JP/msggame.bin": "C13090B0D004D54E44872480DE13FA9CF0C0288EAF195B76E7C668F7B198AC74",
            "MSG_PK/JP/msggame.bin": "618086A21438F61EB31397F94271DBF62EEEEE3D3ADCC0F31D884E17C4E64E8B",
        },
        {"MSG/JP/msggame.bin": 3, "MSG_PK/JP/msggame.bin": 3},
    ),
    ComponentSpec(
        "b11_b13",
        REPO / "tmp" / "pc_b11_b13_static_quality_candidate_v1" / "candidate",
        {
            "MSG/JP/msggame.bin": "FFD9B5A53EE6B7F3B491B98441A68A0F26319AF947F4202829734722D99E6D97",
            "MSG_PK/JP/msggame.bin": "8D1D7F08D92ACB0BF128E46953749A096339C7C33BF26F7DEFB584A459618697",
        },
        {"MSG/JP/msggame.bin": 2, "MSG_PK/JP/msggame.bin": 6},
    ),
)
EXPECTED_FINAL_RECORD_COUNTS = {
    "MSG/JP/msggame.bin": 77,
    "MSG_PK/JP/msggame.bin": 209,
    "MSG_PK/JP/msgdata.bin": 4,
    "MSG_PK/JP/msgev.bin": 91,
}
EXPECTED_FINAL_TOTAL = 381
EXPECTED_OUTPUT_PROFILES: Mapping[str, Any] = {
    "MSG/JP/msggame.bin": core.Profile(
        1_504_446,
        "F9EFC3744F8FEAA2388EA4025DB87CE50B517AD35D3620C530C0EB9D41354168",
        1_498_544,
        "9ACDCA2A8242A0B97780C6552B955C432D7B32AC258B9C26FC2CCF848E5D5B5D",
    ),
    "MSG_PK/JP/msggame.bin": core.Profile(
        1_806_402,
        "A5A0865425010F95064CE68EA102EB445A7E7734B47AFFD5A80D10B3F07B7EEF",
        1_799_320,
        "7573CDF410DA1FA64EF718C3E6DFB064A49BA7867FF5A4BCE67FA91607053A47",
    ),
    "MSG_PK/JP/msgdata.bin": core.Profile(
        496_999,
        "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        495_032,
        "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
    ),
    "MSG_PK/JP/msgev.bin": core.Profile(
        994_715,
        "959202F26B8D49A1D554688DA5B6DE29521405E13131DB9BE156C22728FC20A7",
        990_804,
        "DD08819BE730C922707D219F68CFBD6120BEE43B677B578CC3B0B37D3EAFC552",
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise UnionError(message)


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnionError(f"{label} escapes private W58 tmp root: {resolved}") from exc
    return resolved


def require_private_component(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = (REPO / "tmp").resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnionError(f"{label} is not a private candidate: {resolved}") from exc
    return resolved


def load_sources() -> dict[str, Any]:
    return wave56.load_sources()


def load_component_diffs(sources: Mapping[str, Any]) -> tuple[dict[str, dict[str, dict[Any, Any]]], dict[str, dict[str, int]]]:
    all_diffs: dict[str, dict[str, dict[Any, Any]]] = {}
    all_counts: dict[str, dict[str, int]] = {}
    for component in COMPONENTS:
        root = require_private_component(component.root, component.name)
        require(root.is_dir(), f"component candidate absent: {component.name}")
        diffs: dict[str, dict[Any, Any]] = {}
        counts: dict[str, int] = {}
        for relative, expected_hash in component.resource_hashes.items():
            resource = core.RESOURCE_BY_RELATIVE[relative]
            path = root / relative
            require(path.is_file(), f"component resource absent: {component.name} {relative}")
            require(core.sha256_path(path) == expected_hash, f"component hash differs: {component.name} {relative}")
            changed = core.diff_resource(resource, sources[relative], path)
            diffs[relative] = changed
            counts[relative] = len(changed)
        require(counts == component.record_counts, f"component scope differs: {component.name} {counts}")
        all_diffs[component.name] = diffs
        all_counts[component.name] = counts
    return all_diffs, all_counts


def merge_diffs(
    component_diffs: Mapping[str, Mapping[str, Mapping[Any, Any]]],
) -> tuple[dict[str, dict[Any, Any]], tuple[Mapping[str, Any], ...]]:
    merged: dict[str, dict[Any, Any]] = {resource.relative: {} for resource in core.RESOURCES}
    provenance: dict[str, dict[Any, str]] = {resource.relative: {} for resource in core.RESOURCES}
    overlaps: list[Mapping[str, Any]] = []
    for component in COMPONENTS:
        for relative, changed in component_diffs[component.name].items():
            for coordinate, value in changed.items():
                if coordinate in merged[relative]:
                    if (
                        relative == "MSG_PK/JP/msggame.bin"
                        and coordinate == (9, 4113)
                        and provenance[relative][coordinate] == "wave56"
                        and component.name == "b07_b10"
                        and merged[relative][coordinate] == value
                    ):
                        overlaps.append(
                            {
                                "resource": relative,
                                "coordinate": [9, 4113],
                                "previous_component": "wave56",
                                "incoming_component": "b07_b10",
                                "resolution": "same_payload_already_in_wave56",
                            }
                        )
                        continue
                    raise UnionError(
                        f"duplicate coordinate: {relative} {coordinate!r} "
                        f"{provenance[relative][coordinate]}->{component.name}"
                    )
                merged[relative][coordinate] = value
                provenance[relative][coordinate] = component.name
    expected_overlaps = (
        {
            "resource": "MSG_PK/JP/msggame.bin",
            "coordinate": [9, 4113],
            "previous_component": "wave56",
            "incoming_component": "b07_b10",
            "resolution": "same_payload_already_in_wave56",
        },
    )
    require(tuple(overlaps) == expected_overlaps, f"overlap set differs: {overlaps!r}")
    return merged, tuple(overlaps)


def prepare(*, require_output_profiles: bool) -> Bundle:
    sources = load_sources()
    component_diffs, component_counts = load_component_diffs(sources)
    merged, overlaps = merge_diffs(component_diffs)
    final_counts = {relative: len(changed) for relative, changed in merged.items()}
    require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, f"final scope differs: {final_counts}")
    require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL, "final total differs")
    outputs = {
        resource.relative: core.rebuild_resource(resource, sources[resource.relative], merged[resource.relative])
        for resource in core.RESOURCES
    }
    profiles = {relative: core.profile(blob) for relative, blob in outputs.items()}
    if require_output_profiles:
        require(set(EXPECTED_OUTPUT_PROFILES) == set(core.RESOURCE_BY_RELATIVE), "output profiles are not pinned")
        for relative, expected in EXPECTED_OUTPUT_PROFILES.items():
            require(profiles[relative] == expected, f"output profile differs: {relative}")
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave58-audit.v1",
        "source_policy": {
            "platform": "Steam PC",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "sources": {relative: core.profile_dict(core.profile(source.packed)) for relative, source in sources.items()},
        "components": {
            component.name: {
                "candidate_root": component.root.relative_to(REPO).as_posix(),
                "resource_hashes": dict(component.resource_hashes),
                "record_counts": component_counts[component.name],
            }
            for component in COMPONENTS
        },
        "overlaps": list(overlaps),
        "overlap_count": len(overlaps),
        "final_record_counts": final_counts,
        "final_total_records": EXPECTED_FINAL_TOTAL,
        "holds_excluded": {
            "base_block15_width": "15:1121",
            "b17_runtime_particle": ["17:920:0", "17:920:1"],
            "b00_b05_held_runtime_and_lf": True,
            "b07_b10_name_and_runtime_holds": True,
            "b11_b13_control_and_layout_holds": True,
        },
        "outputs": {relative: core.profile_dict(value) for relative, value in profiles.items()},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave58-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            relative: {
                "relative": relative,
                "output": core.profile_dict(profiles[relative]),
                "changed_record_count": final_counts[relative],
            }
            for relative in core.RESOURCE_BY_RELATIVE
        },
        "final_total_records": EXPECTED_FINAL_TOTAL,
    }
    return Bundle(outputs, profiles, merged, component_counts, overlaps, audit, manifest)


def candidate_root() -> Path:
    return require_private(TMP_ROOT / CANDIDATE_NAME, "candidate root")


def write_candidate(bundle: Bundle) -> Path:
    output = candidate_root()
    require(not output.exists(), f"candidate already exists: {output}")
    staging = require_private(TMP_ROOT / f".{CANDIDATE_NAME}.staging", "candidate staging")
    require(not staging.exists(), f"candidate staging exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(core.canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(core.canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_candidate(bundle: Bundle) -> dict[str, Any]:
    root = candidate_root()
    require(root.is_dir(), f"candidate absent: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *core.RESOURCE_BY_RELATIVE}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"candidate file scope differs: {sorted(actual_files)}")
    for relative, expected in bundle.outputs.items():
        require((root / relative).read_bytes() == expected, f"candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == core.canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == core.canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_record_count": EXPECTED_FINAL_TOTAL,
        "changed_record_count_by_resource": EXPECTED_FINAL_RECORD_COUNTS,
        "steam_game_resource_written": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave58_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave58_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"authoring file absent: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({"output_profiles": {key: core.profile_dict(value) for key, value in bundle.profiles.items()}, "final_record_counts": EXPECTED_FINAL_RECORD_COUNTS, "final_total_records": EXPECTED_FINAL_TOTAL}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_build() -> int:
    bundle = prepare(require_output_profiles=True)
    write_candidate(bundle)
    print(json.dumps(verify_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_verify() -> int:
    print(json.dumps(verify_candidate(prepare(require_output_profiles=True)), ensure_ascii=False, indent=2, sort_keys=True))
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
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        return command_build()
    if command == "verify-private":
        return command_verify()
    return command_diff_check()


if __name__ == "__main__":
    raise SystemExit(main())
