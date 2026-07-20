#!/usr/bin/env python3
"""Build the private Static Patch 007 manual_compact restoration batch 04.

Only the on-disk batch03 candidate provides Korean text. This batch reuses the
committed batch03 codec/audit engine with a separately pinned scope and output
profile; direct PC JP/EN/SC/TC resources remain read-only semantic evidence.
It produces one candidate beneath ``tmp`` and has no Steam, Git, release, or
network path.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
MSGEV = "MSG_PK/JP/msgev.bin"

BATCH03_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_static007_batch03_v1"
    / "build_pc_event_manual_compact_static007_batch03_v1.py"
)
PREDECESSOR_WORKSTREAM = "pc_event_manual_compact_static007_batch03_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_PREDECESSOR_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "A2815BB64F67F85A4033A907ADD3688B479CD88E34E32BF8E8C9F976B0A879D5",
    "raw_size": 996_456,
    "sha256": "259908A5D24CB0C81B3A66FBBD55AE9A97D5210DE24555B1BDBF79AAF0C90B16",
    "size": 1_000_389,
}
# Deterministic output from the pinned batch03 strict predecessor.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "2D9696B6693D13CAA5043423FFFF3B598ACFFDDBC205CD2A2633BB67C8B0900C",
    "raw_size": 996_452,
    "sha256": "753D2675875A61CB6516D906E529E2E77AADA172160F65D93B2FDB2B301BE836",
    "size": 1_000_385,
}

SCENE_NAME = "xavier_arrival_and_mission"
SCENE_IDS = tuple(range(3_277, 3_287))
CHANGED_IDS = (3_285,)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)
E = "\x1b"

TARGETS: Mapping[int, str] = {
    3_285: (
        f"{E}CA하비에르{E}CZ는 {E}CC가고시마{E}CZ에 상륙한 뒤,\n"
        "2년 남짓 머무르며 일본 각지를 돌고,\n"
        "많은 다이묘와 백성에게 교리를 전했다."
    ),
}
TARGET_LAYOUTS: Mapping[int, tuple[tuple[int, ...], tuple[int, ...]]] = {
    3_285: ((768, 840, 888), (480, 525, 555)),
}
RATIONALES: Mapping[int, str] = {
    3_285: "가고시마 상륙 뒤의 2년 남짓 체류, 일본 각지 순회, 다이묘와 백성 전교라는 현재 품질본의 의미를 모두 보존해 세 문장 단위로 정리했다.",
}
CURRENT_QUALITY_PRESERVED: Mapping[int, tuple[str, ...]] = {
    3_285: ("하비에르", "가고시마", "상륙한 뒤", "2년 남짓", "일본 각지", "많은 다이묘와 백성", "교리를 전했다"),
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if not BATCH03_BUILDER.is_file():
    raise RuntimeError(f"batch03 helper missing: {BATCH03_BUILDER}")
engine = load_module("manual_compact_static007_batch03_engine", BATCH03_BUILDER)


class ManualCompactStatic007Batch04Error(RuntimeError):
    """Raised when strict input, evidence, layout, or output drifts."""


@dataclass(frozen=True)
class Bundle:
    event: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManualCompactStatic007Batch04Error(message)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ManualCompactStatic007Batch04Error(f"candidate path escapes tmp: {resolved}") from exc
    return resolved


def validate_authored_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "target ID order/scope drift")
    require(set(CHANGED_IDS).isdisjoint(RETAINED_IDS), "changed/retained scope overlap")
    require(SCENE_IDS == tuple(range(3277, 3287)), "scene scope drift")
    for entry_id, target in TARGETS.items():
        require("\x00" not in target, f"embedded terminator: {entry_id}")
        engine.base.base.assert_no_break_inside_tag(target)
        signature = engine.base.base.control_signature(target)
        require(signature["runtime_tokens"] == [], f"runtime token in target: {entry_id}")
        require(signature["printf_tokens"] == [], f"printf token in target: {entry_id}")
        require(signature["unknown_percent_count"] == 0, f"unknown percent in target: {entry_id}")
        require(signature["other_controls"] == [], f"other control in target: {entry_id}")
        metrics = engine.base.base.line_metrics(target)
        require(1 <= len(metrics) <= 4, f"target line count exceeds max: {entry_id}")
        require(all(line["passes_static_patch_007"] for line in metrics), f"target fails Static Patch 007: {entry_id}")
        if TARGET_LAYOUTS:
            expected_raw, expected_effective = TARGET_LAYOUTS[entry_id]
            require(tuple(line["raw_g1n_width_px"] for line in metrics) == expected_raw, f"target raw drift: {entry_id}")
            require(
                tuple(line["effective_width_px"] for line in metrics) == expected_effective,
                f"target effective drift: {entry_id}",
            )


def configure_engine() -> None:
    """Bind the committed generic codec/audit engine to this batch's strict scope."""
    engine.WORKSTREAM = WORKSTREAM
    engine.TMP_ROOT = TMP_ROOT
    engine.CANDIDATE_ROOT = CANDIDATE_ROOT
    engine.PREDECESSOR_WORKSTREAM = PREDECESSOR_WORKSTREAM
    engine.PREDECESSOR_CANDIDATE_ROOT = PREDECESSOR_CANDIDATE_ROOT
    engine.EXPECTED_PREDECESSOR_PROFILE = EXPECTED_PREDECESSOR_PROFILE
    engine.EXPECTED_OUTPUT_PROFILE = EXPECTED_OUTPUT_PROFILE
    engine.SCENE_NAME = SCENE_NAME
    engine.SCENE_IDS = SCENE_IDS
    engine.CHANGED_IDS = CHANGED_IDS
    engine.RETAINED_IDS = RETAINED_IDS
    engine.TARGETS = TARGETS
    engine.TARGET_LAYOUTS = TARGET_LAYOUTS
    engine.RATIONALES = RATIONALES
    engine.CURRENT_QUALITY_PRESERVED = CURRENT_QUALITY_PRESERVED
    engine.validate_authored_targets = validate_authored_targets


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any], Mapping[str, Any]]:
    configure_engine()
    return engine.load_predecessor()


def prepare(*, require_output_profile: bool) -> Bundle:
    configure_engine()
    engine_bundle = engine.prepare(require_output_profile=require_output_profile)
    audit = copy.deepcopy(engine_bundle.audit)
    manifest = copy.deepcopy(engine_bundle.manifest)
    audit["schema"] = "nobu16.kr.pc-event-manual-compact-static007-batch04-audit.v1"
    profiles = audit["source_profiles"]
    require("strict_predecessor_batch02" in profiles, "engine predecessor profile key drift")
    profiles["strict_predecessor_batch03"] = profiles.pop("strict_predecessor_batch02")
    manifest["schema"] = "nobu16.kr.pc-event-manual-compact-static007-batch04-manifest.v1"
    return Bundle(engine_bundle.event, audit, manifest, engine_bundle.profile)


def write_candidate(bundle: Bundle) -> Path:
    configure_engine()
    return engine.write_candidate(bundle)


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "candidate event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_manual_compact_static007_batch04_v1.py",
        WORKSTREAM / "test_pc_event_manual_compact_static007_batch04_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("authoring-check", "profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "authoring-check":
        validate_authored_targets()
        print(json.dumps({entry_id: list(engine.base.base.line_metrics(text)) for entry_id, text in TARGETS.items()}, ensure_ascii=False))
        return 0
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": bundle.audit["actual_changed_row_ids"], "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
