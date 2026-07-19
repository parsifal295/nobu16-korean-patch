#!/usr/bin/env python3
"""Build the private W56 PC union from pinned W55 and B06 candidates only.

The component files are diffed against the W45 Steam-PC baseline and merged at
the MSGGAME opaque-record/table-entry level.  This builder has no Steam apply,
Git, network, transaction, or release operation.
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
W55_BUILDER = REPO / "workstreams" / "pc_private_union_composite_wave55_v1" / "build_pc_private_union_composite_wave55_v1.py"


def load_wave55() -> Any:
    spec = importlib.util.spec_from_file_location("pc_private_union_composite_wave55_for_wave56", W55_BUILDER)
    if spec is None or spec.loader is None:  # pragma: no cover - import guard
        raise RuntimeError(f"cannot import W55 builder: {W55_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


wave55 = load_wave55()


class UnionError(RuntimeError):
    """Raised when a source, component, merge, or private output drifts."""


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
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


COMPONENTS = (
    ComponentSpec(
        "wave55",
        REPO / "tmp" / "pc_private_union_composite_wave55_v1" / "candidate",
        {
            "MSG/JP/msggame.bin": "50E78AE5BE920454EC8F4B20A485FEF2A1237F593EBF97D205799A2AD705E2B8",
            "MSG_PK/JP/msggame.bin": "646E806CADA8AD81D2ACC133F46B7559B268004FD9CF14F8E44257680435F79D",
            "MSG_PK/JP/msgdata.bin": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
            "MSG_PK/JP/msgev.bin": "959202F26B8D49A1D554688DA5B6DE29521405E13131DB9BE156C22728FC20A7",
        },
        {
            "MSG/JP/msggame.bin": 67,
            "MSG_PK/JP/msggame.bin": 196,
            "MSG_PK/JP/msgdata.bin": 4,
            "MSG_PK/JP/msgev.bin": 91,
        },
    ),
    ComponentSpec(
        "b06",
        REPO / "tmp" / "pc_b06_static_quality_candidate_v1" / "candidate",
        {"MSG_PK/JP/msggame.bin": "A5316297C0E8EE51B8E0DBBCDF62B1B28F93446C729BCF24E922D507146E3F47"},
        {"MSG_PK/JP/msggame.bin": 2},
    ),
)
EXPECTED_FINAL_RECORD_COUNTS = {
    "MSG/JP/msggame.bin": 67,
    "MSG_PK/JP/msggame.bin": 198,
    "MSG_PK/JP/msgdata.bin": 4,
    "MSG_PK/JP/msgev.bin": 91,
}
EXPECTED_FINAL_TOTAL = 360

# Filled from the deterministic `profile` command before build/test/commit.
EXPECTED_OUTPUT_PROFILES: Mapping[str, Any] = {
    "MSG/JP/msggame.bin": wave55.Profile(
        1_504_462,
        "50E78AE5BE920454EC8F4B20A485FEF2A1237F593EBF97D205799A2AD705E2B8",
        1_498_560,
        "8B14B76B1A3479C6261D4E2D8C8FD65877B4A3783EC8AF778C9F2B49679D3706",
    ),
    "MSG_PK/JP/msggame.bin": wave55.Profile(
        1_806_402,
        "EC57BA8BA01BDD8743A894A721416941A2D4BF5FD665C100FFD4C99FE5DE5A6F",
        1_799_320,
        "9CB1C6C3D3416A3744FA244D46617091F036AF8B1FCD81D53CBC989FCDA32A1F",
    ),
    "MSG_PK/JP/msgdata.bin": wave55.Profile(
        496_999,
        "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        495_032,
        "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
    ),
    "MSG_PK/JP/msgev.bin": wave55.Profile(
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
        raise UnionError(f"{label} escapes private W56 tmp root: {resolved}") from exc
    return resolved


def require_private_component(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = (REPO / "tmp").resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnionError(f"{label} is not a private tmp component: {resolved}") from exc
    return resolved


def load_sources() -> dict[str, Any]:
    return {resource.relative: wave55.load_source(resource) for resource in wave55.RESOURCES}


def load_component_diffs(sources: Mapping[str, Any]) -> tuple[dict[str, dict[str, dict[Any, Any]]], dict[str, dict[str, int]]]:
    all_diffs: dict[str, dict[str, dict[Any, Any]]] = {}
    all_counts: dict[str, dict[str, int]] = {}
    for component in COMPONENTS:
        root = require_private_component(component.root, component.name)
        require(root.is_dir(), f"component candidate absent: {component.name}")
        diffs: dict[str, dict[Any, Any]] = {}
        counts: dict[str, int] = {}
        for relative, expected_hash in component.resource_hashes.items():
            resource = wave55.RESOURCE_BY_RELATIVE[relative]
            path = root / relative
            require(path.is_file(), f"component resource absent: {component.name} {relative}")
            require(wave55.sha256_path(path) == expected_hash, f"component hash differs: {component.name} {relative}")
            changed = wave55.diff_resource(resource, sources[relative], path)
            diffs[relative] = changed
            counts[relative] = len(changed)
        require(counts == component.record_counts, f"component diff scope differs: {component.name} {counts}")
        all_diffs[component.name] = diffs
        all_counts[component.name] = counts
    return all_diffs, all_counts


def merge_diffs(component_diffs: Mapping[str, Mapping[str, Mapping[Any, Any]]]) -> dict[str, dict[Any, Any]]:
    merged: dict[str, dict[Any, Any]] = {resource.relative: {} for resource in wave55.RESOURCES}
    origins: dict[str, dict[Any, str]] = {resource.relative: {} for resource in wave55.RESOURCES}
    for component in COMPONENTS:
        for relative, changed in component_diffs[component.name].items():
            for coordinate, target in changed.items():
                if coordinate in merged[relative]:
                    raise UnionError(
                        f"unexpected duplicate coordinate: {relative} {coordinate!r} "
                        f"{origins[relative][coordinate]}->{component.name}"
                    )
                merged[relative][coordinate] = target
                origins[relative][coordinate] = component.name
    return merged


def prepare(*, require_output_profiles: bool) -> Bundle:
    sources = load_sources()
    component_diffs, component_counts = load_component_diffs(sources)
    merged = merge_diffs(component_diffs)
    final_counts = {relative: len(changed) for relative, changed in merged.items()}
    require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, f"final count differs: {final_counts}")
    require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL, "final total differs")
    outputs = {
        resource.relative: wave55.rebuild_resource(resource, sources[resource.relative], merged[resource.relative])
        for resource in wave55.RESOURCES
    }
    profiles = {relative: wave55.profile(blob) for relative, blob in outputs.items()}
    if require_output_profiles:
        require(set(EXPECTED_OUTPUT_PROFILES) == set(wave55.RESOURCE_BY_RELATIVE), "final output profiles are not pinned")
        for relative, expected in EXPECTED_OUTPUT_PROFILES.items():
            require(profiles[relative] == expected, f"final output profile differs: {relative}")
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave56-audit.v1",
        "source_policy": {
            "platform": "Steam PC",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "sources": {relative: wave55.profile_dict(wave55.profile(source.packed)) for relative, source in sources.items()},
        "components": {
            component.name: {
                "candidate_root": component.root.relative_to(REPO).as_posix(),
                "resource_hashes": dict(component.resource_hashes),
                "record_counts": component_counts[component.name],
            }
            for component in COMPONENTS
        },
        "final_record_counts": final_counts,
        "final_total_records": EXPECTED_FINAL_TOTAL,
        "holds_excluded": {
            "base_block15_width": "15:1121",
            "b17_runtime_particle": ["17:920:0", "17:920:1"],
            "b06_runtime_and_context_holds": ["6:751:0", "B06 grammar macros", "B06 manual-LF holds"],
        },
        "outputs": {relative: wave55.profile_dict(value) for relative, value in profiles.items()},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave56-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            relative: {
                "relative": relative,
                "output": wave55.profile_dict(profiles[relative]),
                "changed_record_count": final_counts[relative],
            }
            for relative in wave55.RESOURCE_BY_RELATIVE
        },
        "final_total_records": EXPECTED_FINAL_TOTAL,
    }
    return Bundle(outputs, profiles, merged, component_counts, audit, manifest)


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
        (staging / "audit.v1.json").write_bytes(wave55.canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(wave55.canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_candidate(bundle: Bundle) -> dict[str, Any]:
    root = candidate_root()
    require(root.is_dir(), f"candidate output absent: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *wave55.RESOURCE_BY_RELATIVE}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"candidate file set differs: {sorted(actual_files)}")
    for relative, expected in bundle.outputs.items():
        require((root / relative).read_bytes() == expected, f"candidate file differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == wave55.canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == wave55.canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_record_count": EXPECTED_FINAL_TOTAL,
        "changed_record_count_by_resource": EXPECTED_FINAL_RECORD_COUNTS,
        "steam_game_resource_written": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave56_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave56_v1.py",
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
                "output_profiles": {relative: wave55.profile_dict(value) for relative, value in bundle.profiles.items()},
                "final_record_counts": EXPECTED_FINAL_RECORD_COUNTS,
                "final_total_records": EXPECTED_FINAL_TOTAL,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
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
