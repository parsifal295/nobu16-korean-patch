#!/usr/bin/env python3
"""Build a private, conservative static PC dialogue bundle for Wave 44.

Only baseline-anchored dialogue corrections with unchanged literal boundaries,
manual-line count, opaque bytes, marker topology, and terminator are composed.
Rows at the 912 px boundary, explicitly marked for display QA, or merely
stylistic clarity changes are deliberately excluded.  This builder cannot
write Steam resources, transact, operate Git, contact a network, or release.
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
COMPONENTS = {
    "wave32": (
        REPO / "workstreams" / "pc_dialogue_quality_wave32_static_remainder_v1" / "build_pc_dialogue_quality_wave32_static_remainder_v1.py",
        "442ECDF8ABB5998B020AC2BA55420E9397FACF31D942A33D8285165685F9C92F",
    ),
    "wave36": (
        REPO / "workstreams" / "pc_dialogue_quality_wave36_static_crossfile_v1" / "build_pc_dialogue_quality_wave36_static_crossfile_v1.py",
        "E2171B9DF10D1C6D634E001FC2FA50895F8DF6345F64E2552316674ABC38A690",
    ),
    "wave39": (
        REPO / "workstreams" / "pc_dialogue_quality_wave39_static_dialogue_v1" / "build_pc_dialogue_quality_wave39_static_dialogue_v1.py",
        "2A5E1B69415BC34302B6123B8FFEEA3EAE7BE76EB3AE9ED1A948CFA97A357EFD",
    ),
}

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave44-safe-static-bundle.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave44-safe-static-bundle-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave44-safe-static-bundle-manifest.v1"
MAX_SAFE_LINE_PX_EXCLUSIVE = 912


class Wave44Error(RuntimeError):
    """Raised when an input, component, or private output differs."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave44Error(message)


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
    spec = importlib.util.spec_from_file_location(f"wave44_imported_{name}", path)
    if spec is None or spec.loader is None:
        raise Wave44Error(f"cannot load {name} component")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W32 = load_component("wave32")
W36 = load_component("wave36")
W39 = load_component("wave39")
W27 = W39.W27
BASE_RESOURCE = W39.BASE_RESOURCE
PK_RESOURCE = W39.PK_RESOURCE
RESOURCE_PATHS = W39.RESOURCE_PATHS
INPUT_PROFILES = W39.INPUT_PROFILES
TARGET_PROFILES = {
    BASE_RESOURCE: {
        "size": 1_504_410,
        "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        "raw_size": 1_498_508,
        "raw_sha256": "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D",
    },
    PK_RESOURCE: {
        "size": 1_806_538,
        "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        "raw_size": 1_799_456,
        "raw_sha256": "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E",
    },
}

# These are not errors in source evidence; they are deliberately outside this
# conservative private bundle until their actual UI is inspected.
EXCLUDED_REAL_GAME_QA = {
    "wave32_pk_boundary": ["7:2482", "15:2279"],
    "wave36_pk_boundary": ["17:714", "17:821"],
    "wave39_base_display": ["6:4039", "6:4045"],
    "wave39_pk_display_or_boundary": ["9:3880", "17:80", "17:401"],
}
EXCLUDED_NON_ERROR_CLARITY = {"wave35": ["17:938"]}


@dataclass(frozen=True)
class IntegratedChange:
    source_wave: str
    resource: str
    coordinate: tuple[int, int]
    component_change: Any


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def collect_changes() -> tuple[IntegratedChange, ...]:
    changes: list[IntegratedChange] = []
    wave32_holds = {(7, 2482), (15, 2279)}
    for change in W32.CHANGES:
        if change.pk_coordinate not in wave32_holds:
            changes.append(IntegratedChange("wave32", W32.RESOURCE, change.pk_coordinate, change))
    for change in W36.CHANGES:
        if change.resource == BASE_RESOURCE:
            changes.append(IntegratedChange("wave36", change.resource, change.coordinate, change))
    wave39_holds = {(17, 80), (17, 401)}
    for change in W39.CHANGES:
        if not change.base_display_qa_required and not change.pk_display_qa_required and change.coordinate not in wave39_holds:
            changes.append(IntegratedChange("wave39", change.resource, change.coordinate, change))
    require(len(changes) == 51, "conservative static scope count differs")
    require(sum(change.resource == BASE_RESOURCE for change in changes) == 13, "Base scope count differs")
    require(sum(change.resource == PK_RESOURCE for change in changes) == 38, "PK scope count differs")
    require(len({(change.resource, change.coordinate) for change in changes}) == len(changes), "resource-qualified coordinates overlap")
    require(all(change.coordinate != (8, 633) for change in changes), "known semantic inversion must stay excluded")
    return tuple(changes)


CHANGES = collect_changes()


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave44Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def verify_component_contracts() -> None:
    # Each original builder validates its pinned PC source evidence and its
    # own target-record contract in memory before this bundle composes records.
    W32.prepare_candidate()
    W36.prepare_candidate()
    W39.prepare_candidate()
    require(
        (W32.INPUT_SIZE, W32.INPUT_SHA256)
        == (INPUT_PROFILES[PK_RESOURCE]["size"], INPUT_PROFILES[PK_RESOURCE]["sha256"]),
        "Wave 32 PK baseline differs",
    )
    require(W36.INPUT_PROFILES == INPUT_PROFILES, "Wave 36 baseline differs")
    require(W39.INPUT_PROFILES == INPUT_PROFILES, "Wave 39 baseline differs")


def source_maps() -> tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], Mapping[str, str]]:
    wave32, wave32_hashes = W32.load_source_records()
    wave36, wave36_hashes = W36.load_source_records()
    wave39, wave39_hashes = W39.W37.load_source_records()
    hashes = {
        "wave32": wave32_hashes,
        "wave36": wave36_hashes,
        "wave39": wave39_hashes,
    }
    return wave32, wave36, wave39, hashes


def validate_integrated_change(
    change: IntegratedChange,
    before: Any,
    advance: Any,
    wave32_sources: Mapping[str, Any],
    wave36_sources: Mapping[str, Any],
    wave39_sources: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    if change.source_wave == "wave32":
        anchor = W32.validate_source_anchor(change.component_change, wave32_sources)
        replacement, row = W32.validate_change(change.component_change, before, advance)
    elif change.source_wave == "wave36":
        anchor = W36.validate_source_anchor(change.component_change, wave36_sources)
        replacement, row = W36.validate_change(change.component_change, before, advance)
    elif change.source_wave == "wave39":
        replacement, row = W39.validate_change(change.component_change, before, wave39_sources, advance)
        anchor = row.pop("pc_source_record_sha256")
    else:  # pragma: no cover - collection above is closed.
        raise Wave44Error(f"unsupported source wave: {change.source_wave}")
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, replacement)
    before_opaque = W27.opaque_spans(before)
    require(not W27.complete_0143_commands(before_opaque), f"{change.source_wave}:{change.coordinate} has a static 0143 command")
    require(not any(span.startswith(b"\x02") for span in before_opaque), f"{change.source_wave}:{change.coordinate} has a runtime opcode")
    require(W27.opaque_spans(after) == before_opaque, f"{change.source_wave}:{change.coordinate} opaque bytes differ")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"{change.source_wave}:{change.coordinate} marker topology differs")
    require(before.data.endswith(W27.RECORD_TERMINATOR) and after.data.endswith(W27.RECORD_TERMINATOR), f"{change.source_wave}:{change.coordinate} terminator differs")
    before_text = "".join(W27.literal_texts(before))
    target_text = "".join(change.component_change.target_literals)
    require(before_text.count("\n") == target_text.count("\n"), f"{change.source_wave}:{change.coordinate} manual line count differs")
    layout = W27.line_layout(change.component_change.target_literals, advance)
    require(layout["line_count"] <= 3, f"{change.source_wave}:{change.coordinate} exceeds three lines")
    require(layout["max_width_px"] < MAX_SAFE_LINE_PX_EXCLUSIVE, f"{change.source_wave}:{change.coordinate} reaches the boundary width")
    require(not layout["wide_fallback_codepoints"], f"{change.source_wave}:{change.coordinate} uses a fallback glyph")
    row.update(
        {
            "source_wave": change.source_wave,
            "resource": change.resource,
            "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
            "pc_source_anchor": anchor,
            "target_line_widths_px": list(layout["line_widths_px"]),
        }
    )
    return replacement, row


def prepare_candidate() -> CandidateBundle:
    verify_component_contracts()
    current_packed: dict[str, bytes] = {}
    current_records: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource, path in RESOURCE_PATHS.items():
        checked = W39.W37.reject_switch(path, f"current Steam {resource}")
        packed = checked.read_bytes()
        profile = INPUT_PROFILES[resource]
        require(len(packed) == profile["size"] and W39.sha256_bytes(packed) == profile["sha256"], f"current Steam profile differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"current Steam {resource}")
        current_packed[resource] = packed
        current_records[resource] = W27.records_by_coordinate(packed)
    advance, font = W27.load_font_advance()
    wave32_sources, wave36_sources, wave39_sources, source_hashes = source_maps()
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in RESOURCE_PATHS}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current_records[change.resource].get(change.coordinate)
        require(before is not None and change.coordinate not in replacements[change.resource], f"current coordinate differs: {change.source_wave}:{change.coordinate}")
        replacement, row = validate_integrated_change(change, before, advance, wave32_sources, wave36_sources, wave39_sources)
        replacements[change.resource][change.coordinate] = replacement
        rows.append(row)
    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource, packed in current_packed.items():
        candidate = W27.rebuild_packed_msggame(packed, replacements[resource])
        W27.validate_raw_roundtrip(candidate, f"Wave 44 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        profile = TARGET_PROFILES[resource]
        require(len(candidate) == profile["size"] and W39.sha256_bytes(candidate) == profile["sha256"], f"target packed profile differs: {resource}")
        require(len(raw) == profile["raw_size"] and W39.sha256_bytes(raw) == profile["raw_sha256"], f"target raw profile differs: {resource}")
        after = W27.records_by_coordinate(candidate)
        changed = {coordinate for coordinate in current_records[resource] if current_records[resource][coordinate].data != after[coordinate].data}
        expected = {change.coordinate for change in CHANGES if change.resource == resource}
        require(changed == expected and set(current_records[resource]) == set(after), f"changed record scope differs: {resource}")
        packed_output[resource] = candidate
        raw_output[resource] = raw
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
        "font": font,
        "max_safe_line_px_exclusive": MAX_SAFE_LINE_PX_EXCLUSIVE,
        "input": INPUT_PROFILES,
        "target": TARGET_PROFILES,
        "changed_record_count": len(CHANGES),
        "excluded_real_game_qa": EXCLUDED_REAL_GAME_QA,
        "excluded_non_error_clarity": EXCLUDED_NON_ERROR_CLARITY,
        "pc_source_packed_sha256": source_hashes,
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "input": INPUT_PROFILES[resource],
                "output": TARGET_PROFILES[resource],
                "changed_coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES if change.resource == resource],
            }
            for resource in RESOURCE_PATHS
        },
        "changed_record_count": len(CHANGES),
        "excluded_real_game_qa": EXCLUDED_REAL_GAME_QA,
        "excluded_non_error_clarity": EXCLUDED_NON_ERROR_CLARITY,
        "audit_sha256": W39.sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_output, raw_output, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require(not output.exists(), f"candidate output already exists: {output}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            path = stage / resource
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
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for resource, packed in bundle.packed.items():
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "excluded_real_game_qa": EXCLUDED_REAL_GAME_QA,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "steam_game_resource_written": False}
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
