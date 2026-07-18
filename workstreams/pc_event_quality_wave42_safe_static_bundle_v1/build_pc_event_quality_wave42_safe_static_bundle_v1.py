#!/usr/bin/env python3
"""Build a private, linebreak-stable static PC event bundle for Wave 42.

This composes only static event fixes whose source workstreams preserve the
existing manual-linebreak topology.  Rows whose break positions were moved,
and Base rows explicitly held for real-game display QA, are excluded.  The
builder has no Steam-write, Git, network, transaction, or release capability.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_DIRNAME = "candidate_linebreak_stable_v2"
COMPONENTS = {
    "wave31": (
        REPO / "workstreams" / "pc_event_quality_wave31_static_v1" / "build_pc_event_quality_wave31_static_v1.py",
        "71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A",
    ),
    "wave33": (
        REPO / "workstreams" / "pc_event_quality_wave33_strict_static_v1" / "build_pc_event_quality_wave33_strict_static_v1.py",
        "4F6E7AD16EC05EC2744E62804F4F79ABEED65F365FA1DAEBAC3BEEE0FCD79FDD",
    ),
    "wave40": (
        REPO / "workstreams" / "pc_event_quality_wave40_static_wording_v1" / "build_pc_event_quality_wave40_static_wording_v1.py",
        "3B8725BC2D862AF63271D7E2BDCA72134B4EB05DEDFEA2C9B443139DB80A1D1B",
    ),
}

SCHEMA = "nobu16.kr.pc-event-quality-wave42-safe-static-bundle.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-quality-wave42-safe-static-bundle-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-quality-wave42-safe-static-bundle-manifest.v1"
PK_MAX_LINE_PX = 912


class Wave42Error(RuntimeError):
    """Raised when a component, input, or private output differs."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave42Error(message)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_component(name: str) -> Any:
    path, expected_hash = COMPONENTS[name]
    require(path.is_file(), f"{name} component is absent")
    require(sha256_path(path) == expected_hash, f"{name} component hash differs")
    spec = importlib.util.spec_from_file_location(f"wave42_imported_{name}", path)
    if spec is None or spec.loader is None:
        raise Wave42Error(f"cannot load {name} component")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W31 = load_component("wave31")
W33 = load_component("wave33")
W40 = load_component("wave40")


@dataclass(frozen=True)
class IntegratedChange:
    source_wave: str
    resource: str
    entry_id: int
    current_utf16le_sha256: str
    target: str
    target_utf16le_sha256: str
    source_rationale: str


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


TARGET_PROFILES = {
    "base": {
        "size": 928_131,
        "sha256": "85CC7B26E2D9A159AABD71610A9694AD803CFADE8CCD12F1A082AE2A35E3FF45",
        "raw_size": 924_480,
        "raw_sha256": "4D6982491F63DDF7B0900B0F05339625D0B8B85F6CA119119F4F1FAE398A3717",
    },
    "pk": {
        "size": 994_739,
        "sha256": "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
        "raw_size": 990_828,
        "raw_sha256": "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
    },
}

# These rows remain in their own display-QA workstreams and are deliberately
# absent from this bundle.
EXCLUDED_DISPLAY_QA = {
    "wave31": {"base": [3898, 4507, 5528, 6379], "pk": [3898, 5528]},
    "wave33": {"base": [6772, 6941, 8776, 8803, 8947, 9292], "pk": [6772]},
    "wave41": {"pk": [5558, 5832, 7083, 7579, 7801, 7845]},
}


def collect_changes() -> tuple[IntegratedChange, ...]:
    changes: list[IntegratedChange] = []
    # Wave 31: 3898 and 5528 move a manual break and remain real-game QA-held.
    # Base UI scale is unproven for every Wave 31 event row, so it remains held.
    for change in W31.CHANGES:
        if change.resource == "pk" and change.entry_id not in {3898, 5528}:
            changes.append(IntegratedChange("wave31", change.resource, change.entry_id, change.current_utf16le_sha256, change.target, change.target_utf16le_sha256, change.rationale))
    # Wave 33 marks exactly six Base rows as display QA required.  PK 6772
    # also moves a manual break, even though its break count is unchanged.
    for change in W33.CHANGES:
        if change.resource == "pk" and change.entry_id != 6772:
            changes.append(IntegratedChange("wave33", change.resource, change.entry_id, change.current_utf16le_sha256, change.target, change.target_utf16le_sha256, change.rationale))
        elif change.resource == "base" and not change.base_real_game_qa_required:
            changes.append(IntegratedChange("wave33", change.resource, change.entry_id, change.current_utf16le_sha256, change.target, change.target_utf16le_sha256, change.rationale))
    # Wave 40 has no layout change and its Base spelling repair retains width.
    for change in W40.CHANGES:
        changes.append(IntegratedChange("wave40", change.resource, change.entry_id, change.current_utf16le_sha256, change.target, change.target_utf16le_sha256, change.rationale))
    require(len(changes) == 26, "safe static scope count differs")
    require(len({(change.resource, change.entry_id) for change in changes}) == len(changes), "safe static scope overlaps")
    return tuple(changes)


CHANGES = collect_changes()


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave42Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def verify_component_contracts() -> None:
    # Each source component validates PC source hashes, record structures, and
    # its own target profile in memory.  No component writes its candidate here.
    W31.prepare_candidate()
    W33.prepare_candidate()
    W40.prepare_candidate()
    for key in W31.RESOURCES:
        expected = W31.RESOURCES[key]
        actual = W33.RESOURCES[key]
        require(
            (actual.input_size, actual.input_sha256, actual.input_raw_size, actual.input_raw_sha256)
            == (expected.input_size, expected.input_sha256, expected.input_raw_size, expected.input_raw_sha256),
            f"Wave 33 {key} input profile differs",
        )


def prepare_candidate() -> CandidateBundle:
    verify_component_contracts()
    current = {key: W31.load_table(spec, f"current Steam {spec.relative}") for key, spec in W31.RESOURCES.items()}
    advance, font = W31.load_event_font()
    targets = {key: list(resource.table.texts) for key, resource in current.items()}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current[change.resource].table.texts[change.entry_id]
        require(W31.text_hash(before) == change.current_utf16le_sha256, f"{change.source_wave}:{change.resource}:{change.entry_id} current text differs")
        require(W31.text_hash(change.target) == change.target_utf16le_sha256, f"{change.source_wave}:{change.resource}:{change.entry_id} target differs")
        require(W31.protected_signature(before) == W31.protected_signature(change.target), f"{change.source_wave}:{change.resource}:{change.entry_id} changes control or linebreak topology")
        widths = W31.line_widths(change.target, advance)
        require(1 <= len(widths) <= 3, f"{change.source_wave}:{change.resource}:{change.entry_id} line count differs")
        if change.resource == "pk":
            require(max(widths) <= PK_MAX_LINE_PX, f"{change.source_wave}:{change.resource}:{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
        targets[change.resource][change.entry_id] = change.target
        rows.append(
            {
                "source_wave": change.source_wave,
                "resource": W31.RESOURCES[change.resource].relative,
                "id": change.entry_id,
                "current_utf16le_sha256": change.current_utf16le_sha256,
                "target_utf16le_sha256": change.target_utf16le_sha256,
                "target_line_widths_px": list(widths),
                "rationale": change.source_rationale,
            }
        )
    packed: dict[str, bytes] = {}
    raw: dict[str, bytes] = {}
    for key, resource in current.items():
        candidate_raw = W31.rebuild_message_table(resource.table, tuple(targets[key]))
        candidate_packed = W31.recompress_wrapper(candidate_raw, resource.header)
        profile = TARGET_PROFILES[key]
        require(len(candidate_raw) == profile["raw_size"] and W31.sha256_bytes(candidate_raw) == profile["raw_sha256"], f"{key} target raw profile differs")
        require(len(candidate_packed) == profile["size"] and W31.sha256_bytes(candidate_packed) == profile["sha256"], f"{key} target packed profile differs")
        header, decoded = W31.decompress_wrapper(candidate_packed)
        table = W31.parse_message_table(decoded)
        require(W31.rebuild_message_table(table, table.texts) == decoded and W31.recompress_wrapper(decoded, header) == candidate_packed, f"{key} candidate round-trip differs")
        changed = [index for index, (before, after) in enumerate(zip(resource.table.texts, table.texts)) if before != after]
        expected = sorted(change.entry_id for change in CHANGES if change.resource == key)
        require(changed == expected, f"{key} changed ID scope differs")
        packed[key] = candidate_packed
        raw[key] = candidate_raw
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pc_jp_en_sc_tc_only": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "component_builder_sha256": {name: expected for name, (_path, expected) in COMPONENTS.items()},
        "font": dict(font),
        "pk_max_line_px": PK_MAX_LINE_PX,
        "input": {
            key: {
                "size": spec.input_size,
                "sha256": spec.input_sha256,
                "raw_size": spec.input_raw_size,
                "raw_sha256": spec.input_raw_sha256,
            }
            for key, spec in W31.RESOURCES.items()
        },
        "target": TARGET_PROFILES,
        "changed_cell_count": len(CHANGES),
        "excluded_real_game_display_qa": EXCLUDED_DISPLAY_QA,
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            W31.RESOURCES[key].relative: {
                "input": audit["input"][key],
                "output": TARGET_PROFILES[key],
                "changed_ids": [change.entry_id for change in CHANGES if change.resource == key],
            }
            for key in W31.RESOURCES
        },
        "changed_cell_count": len(CHANGES),
        "excluded_real_game_display_qa": EXCLUDED_DISPLAY_QA,
        "audit_sha256": W31.sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed, raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(not output.exists(), f"candidate output already exists: {output}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for key, packed in bundle.packed.items():
            path = stage / W31.RESOURCES[key].relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    for key, packed in bundle.packed.items():
        path = output / W31.RESOURCES[key].relative
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {path}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_cell_count": len(CHANGES),
        "excluded_real_game_display_qa": EXCLUDED_DISPLAY_QA,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {"candidate_root": output.relative_to(REPO).as_posix(), "changed_cell_count": len(CHANGES), "steam_game_resource_written": False}
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
