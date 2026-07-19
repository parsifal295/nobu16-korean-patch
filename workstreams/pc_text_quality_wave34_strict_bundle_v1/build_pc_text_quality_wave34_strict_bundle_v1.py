#!/usr/bin/env python3
"""Compose Waves 31--33 into one private, non-applying PC text candidate."""

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

SCHEMA = "nobu16.kr.pc-text-quality-wave34-strict-bundle.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-text-quality-wave34-strict-bundle-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-text-quality-wave34-strict-bundle-manifest.v1"

COMPONENTS = {
    "event_wave31": (
        REPO / "workstreams" / "pc_event_quality_wave31_static_v1" / "build_pc_event_quality_wave31_static_v1.py",
        "71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A",
    ),
    "dialogue_wave32": (
        REPO / "workstreams" / "pc_dialogue_quality_wave32_static_remainder_v1" / "build_pc_dialogue_quality_wave32_static_remainder_v1.py",
        "442ECDF8ABB5998B020AC2BA55420E9397FACF31D942A33D8285165685F9C92F",
    ),
    "event_wave33": (
        REPO / "workstreams" / "pc_event_quality_wave33_strict_static_v1" / "build_pc_event_quality_wave33_strict_static_v1.py",
        "4F6E7AD16EC05EC2744E62804F4F79ABEED65F365FA1DAEBAC3BEEE0FCD79FDD",
    ),
}

RESOURCE_SPECS = {
    "MSG/JP/ev_strdata.bin": {
        "input_size": 928_119,
        "input_sha256": "02AC90B818E8F75683CD5BACF277E91048D4510E448A8699242D3B19299FE067",
        "output_size": 928_107,
        "output_sha256": "C93FC11239959C3D50F6F8A729FFE07B4BE18A5FF81648A5C95A32811E0BAF6D",
        "output_raw_size": 924_456,
        "output_raw_sha256": "B355B24DD7C80A5A547F258FAC70CF28CAB7A01D1ED22A8677DBC21322138AC3",
    },
    "MSG_PK/JP/msgev.bin": {
        "input_size": 994_727,
        "input_sha256": "AEE0D9992B963E17B3C118AA54DACC60390936FF48876674CA7675A2A11A3668",
        "output_size": 994_739,
        "output_sha256": "86DF4ECECAC07426F63358C643B3B4AFDE44A2336E5790EA0B629B2CEABDB537",
        "output_raw_size": 990_828,
        "output_raw_sha256": "2888100B24BC97C929DBB72C69298BC16651432BD6408484DB79C6777397A61B",
    },
    "MSG_PK/JP/msggame.bin": {
        "input_size": 1_806_542,
        "input_sha256": "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9",
        "output_size": 1_806_498,
        "output_sha256": "37644F37ABDB03B16BA6D722C03A9BB4F899F7A684665F3DB55501E46180AA14",
        "output_raw_size": 1_799_416,
        "output_raw_sha256": "2ABF271A08660062468AEED9C743215A06F77B052F87B88FF955FA675C6A7F1A",
    },
}


class Wave34Error(RuntimeError):
    """Raised when component proof or composed private output drifts."""


@dataclass(frozen=True)
class CandidateBundle:
    files: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave34Error(label)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave34Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_component(name: str) -> Any:
    path, expected_hash = COMPONENTS[name]
    require(path.is_file() and sha256_path(path) == expected_hash, f"{name} builder differs")
    spec = importlib.util.spec_from_file_location(f"wave34_{name}", path)
    if spec is None or spec.loader is None:
        raise Wave34Error(f"cannot import {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def merge_event_resource(relative: str, key: str, current: Any, components: tuple[tuple[Any, Any], ...]) -> tuple[bytes, list[int]]:
    target_texts = list(current.table.texts)
    changed_ids: set[int] = set()
    for module, bundle in components:
        _header, raw = module.decompress_wrapper(bundle.packed[key])
        candidate = module.parse_message_table(raw)
        for change in module.CHANGE_BY_RESOURCE[key]:
            require(change.entry_id not in changed_ids, f"duplicate composed event ID: {relative}:{change.entry_id}")
            require(candidate.texts[change.entry_id] != current.table.texts[change.entry_id], f"component event target is unchanged: {relative}:{change.entry_id}")
            target_texts[change.entry_id] = candidate.texts[change.entry_id]
            changed_ids.add(change.entry_id)
    raw = components[1][0].rebuild_message_table(current.table, tuple(target_texts))
    packed = components[1][0].recompress_wrapper(raw, current.header)
    spec = RESOURCE_SPECS[relative]
    require(len(raw) == spec["output_raw_size"] and sha256_bytes(raw) == spec["output_raw_sha256"], f"combined raw profile differs: {relative}")
    require(len(packed) == spec["output_size"] and sha256_bytes(packed) == spec["output_sha256"], f"combined packed profile differs: {relative}")
    _header, decoded = components[1][0].decompress_wrapper(packed)
    table = components[1][0].parse_message_table(decoded)
    actual_changed = [index for index, (before, after) in enumerate(zip(current.table.texts, table.texts)) if before != after]
    require(actual_changed == sorted(changed_ids), f"combined changed ID scope differs: {relative}")
    return packed, sorted(changed_ids)


def prepare_candidate() -> CandidateBundle:
    wave31 = load_component("event_wave31")
    wave32 = load_component("dialogue_wave32")
    wave33 = load_component("event_wave33")
    bundle31 = wave31.prepare_candidate()
    bundle32 = wave32.prepare_candidate()
    bundle33 = wave33.prepare_candidate()

    current_base = wave33.load_table(wave33.RESOURCES["base"], "current Steam Base event")
    current_pk = wave33.load_table(wave33.RESOURCES["pk"], "current Steam PK event")
    base, base_ids = merge_event_resource("MSG/JP/ev_strdata.bin", "base", current_base, ((wave31, bundle31), (wave33, bundle33)))
    pk_event, pk_event_ids = merge_event_resource("MSG_PK/JP/msgev.bin", "pk", current_pk, ((wave31, bundle31), (wave33, bundle33)))
    pk_dialogue = bundle32.packed
    dialogue_spec = RESOURCE_SPECS["MSG_PK/JP/msggame.bin"]
    require(len(pk_dialogue) == dialogue_spec["output_size"] and sha256_bytes(pk_dialogue) == dialogue_spec["output_sha256"], "component dialogue profile differs")

    files = {
        "MSG/JP/ev_strdata.bin": base,
        "MSG_PK/JP/msgev.bin": pk_event,
        "MSG_PK/JP/msggame.bin": pk_dialogue,
    }
    component_audits = {
        "event_wave31": sha256_bytes(canonical_json(bundle31.audit)),
        "dialogue_wave32": sha256_bytes(canonical_json(bundle32.audit)),
        "event_wave33": sha256_bytes(canonical_json(bundle33.audit)),
    }
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "component_pc_jp_en_sc_tc_only": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "component_builder_sha256": {name: expected_hash for name, (_path, expected_hash) in COMPONENTS.items()},
        "component_audit_sha256": component_audits,
        "resources": {
            relative: {"input": {"size": spec["input_size"], "sha256": spec["input_sha256"]}, "output": {"size": spec["output_size"], "sha256": spec["output_sha256"], "raw_size": spec["output_raw_size"], "raw_sha256": spec["output_raw_sha256"]}}
            for relative, spec in RESOURCE_SPECS.items()
        },
        "changed": {
            "MSG/JP/ev_strdata.bin": base_ids,
            "MSG_PK/JP/msgev.bin": pk_event_ids,
            "MSG_PK/JP/msggame.bin": [f"{change.pk_coordinate[0]}:{change.pk_coordinate[1]}" for change in wave32.CHANGES],
        },
        "changed_event_cell_count": len(base_ids) + len(pk_event_ids),
        "changed_dialogue_record_count": len(wave32.CHANGES),
        "changed_total_count": len(base_ids) + len(pk_event_ids) + len(wave32.CHANGES),
        "base_real_game_qa_required_ids": bundle33.audit["base_real_game_qa_required_ids"],
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {relative: {"input": {"size": spec["input_size"], "sha256": spec["input_sha256"]}, "output": {"size": spec["output_size"], "sha256": spec["output_sha256"]}} for relative, spec in RESOURCE_SPECS.items()},
        "changed_total_count": audit["changed_total_count"],
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(files, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for relative, content in bundle.files.items():
            path = stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "build_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for relative, content in bundle.files.items():
        path = output / relative
        require(path.is_file() and path.read_bytes() == content, f"private candidate differs: {relative}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_total_count": bundle.audit["changed_total_count"], "base_real_game_qa_required": True, "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {"candidate_root": output.relative_to(REPO).as_posix(), "changed_total_count": bundle.audit["changed_total_count"], "base_real_game_qa_required": True, "steam_game_resource_written": False}
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
