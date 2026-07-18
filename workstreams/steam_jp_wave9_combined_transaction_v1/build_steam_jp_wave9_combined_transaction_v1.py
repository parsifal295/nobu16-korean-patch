#!/usr/bin/env python3
"""Assemble the private full-profile Wave9 Steam transaction candidate.

This builder does not write the Steam installation. It accepts only the
pinned Wave8 full profile plus the already-built Wave9 runtime and event
candidate artefacts, and writes a complete candidate and manifest only below
this workstream's tmp directory.
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
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "candidate-build-1"
DEFAULT_MANIFEST = TMP_ROOT / "build_manifest.v1.json"

RUNTIME_WORKSTREAM = REPO / "workstreams" / "pc_dialogue_runtime_wave9_candidate_v1"
RUNTIME_COMPONENT_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_wave9_candidate_v1" / "candidate-build-1"
)
RUNTIME_COMPONENT_MANIFEST = (
    REPO / "tmp" / "pc_dialogue_runtime_wave9_candidate_v1" / "build_manifest.v1.json"
)
EVENT_WORKSTREAM = REPO / "workstreams" / "pc_event_linebreak_wave9_candidate_v1"
EVENT_COMPONENT_BUILD_ROOT = REPO / "tmp" / "pc_event_linebreak_wave9_candidate_v1"
EVENT_COMPONENT_ROOT = EVENT_COMPONENT_BUILD_ROOT / "candidate"
EVENT_COMPONENT_MANIFEST = (
    REPO / "tmp" / "pc_event_linebreak_wave9_candidate_v1" / "build_manifest.v1.json"
)
EVENT_COMPONENT_SUMMARY = REPO / "tmp" / "pc_event_linebreak_wave9_candidate_v1" / "summary.v1.json"

SCHEMA = "nobu16.kr.steam-jp-wave9-combined-transaction.v1"
TRANSACTION_ID = "steam-jp-wave9-combined-transaction-v1"
RUNTIME_MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-runtime-wave9.v1"
EVENT_MANIFEST_SCHEMA = "nobu16.kr.pc-event-linebreak-wave9-build-manifest.v1"

PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
CHANGED_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
)

INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834",
    "MSG/JP/msggame.bin": "7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "1880A8052C916FAC7F262CCC8638477F5AA124F248A6468E0533A8E252AB55C5",
    "MSG_PK/JP/msggame.bin": "454A18B0F0ED5E39A3AC823AD0A30086C25226BF6E48D4580962DFEE84E24A32",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}

RUNTIME_COMPONENT_OUTPUT_SHA256 = {
    **INPUT_SHA256,
    "MSG_PK/JP/msggame.bin": "209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930",
}

EVENT_COMPONENT_TARGET_SHA256 = {
    "MSG/JP/ev_strdata.bin": "3A7BE17B7DA97B89BD82DFFF44EBC28DA2D3AA91D2E970A0F6C26DE22C657A22",
    "MSG_PK/JP/msgev.bin": "73DEC80A85B5441AFFFA725DAB72CF02D334D29B297AD08050BC496D532CB8F3",
}

TARGET_SHA256 = {
    "MSG/JP/ev_strdata.bin": "3A7BE17B7DA97B89BD82DFFF44EBC28DA2D3AA91D2E970A0F6C26DE22C657A22",
    "MSG/JP/msggame.bin": "7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "73DEC80A85B5441AFFFA725DAB72CF02D334D29B297AD08050BC496D532CB8F3",
    "MSG_PK/JP/msggame.bin": "209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}


class CombinedTransactionError(RuntimeError):
    """A pinned component or full-profile transaction contract changed."""


@dataclass(frozen=True)
class CombinedPayload:
    files: dict[str, bytes]
    component_contract: dict[str, Any]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CombinedTransactionError(message)


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise CombinedTransactionError(f"{label} escapes approved root: {resolved_path}") from exc
    return resolved_path


def require_tmp(path: Path, label: str) -> Path:
    return require_under(TMP_ROOT, path, label)


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise CombinedTransactionError(f"{label} is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CombinedTransactionError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CombinedTransactionError(f"{label} must be a JSON object")
    return value


def require_profile(value: Any, expected: Mapping[str, str], label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise CombinedTransactionError(f"{label} must be a profile object")
    actual = {relative: str(value.get(relative, "")).upper() for relative in PROFILE_PATHS}
    if set(value) != set(PROFILE_PATHS) or actual != dict(expected):
        mismatch = {
            relative: {"expected": expected[relative], "actual": actual[relative]}
            for relative in PROFILE_PATHS
            if actual[relative] != expected[relative]
        }
        raise CombinedTransactionError(f"{label} differs from its pinned profile: {mismatch}")
    return actual


def profile_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = root / Path(relative)
        if not path.is_file():
            raise CombinedTransactionError(f"candidate profile is missing: {relative}")
        result[relative] = sha256_path(path)
    return result


def relative_to_repo(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def runtime_component_contract() -> dict[str, Any]:
    root = require_under(REPO / "tmp", RUNTIME_COMPONENT_ROOT, "runtime candidate root")
    manifest_path = require_under(REPO / "tmp", RUNTIME_COMPONENT_MANIFEST, "runtime manifest")
    require(root.is_dir(), f"runtime candidate root is missing: {root}")
    manifest = read_json(manifest_path, "runtime component manifest")
    require(
        manifest.get("schema") == RUNTIME_MANIFEST_SCHEMA,
        "runtime component manifest schema differs",
    )
    require(
        manifest.get("changed_paths") == ["MSG_PK/JP/msggame.bin"],
        "runtime component changed path contract differs",
    )
    require_profile(
        manifest.get("input_profile_sha256"), INPUT_SHA256, "runtime component input profile"
    )
    require_profile(
        manifest.get("output_profile_sha256"),
        RUNTIME_COMPONENT_OUTPUT_SHA256,
        "runtime component output profile",
    )
    actual_profile = profile_hashes(root)
    require(
        actual_profile == RUNTIME_COMPONENT_OUTPUT_SHA256,
        "runtime component candidate tree differs from pinned profile",
    )
    return {
        "workstream": RUNTIME_WORKSTREAM.name,
        "manifest": relative_to_repo(manifest_path),
        "manifest_sha256": sha256_path(manifest_path),
        "candidate_root": relative_to_repo(root),
        "changed_paths": ["MSG_PK/JP/msggame.bin"],
        "input_profile_sha256": INPUT_SHA256,
        "output_profile_sha256": actual_profile,
    }


def event_component_contract() -> dict[str, Any]:
    root = require_under(REPO / "tmp", EVENT_COMPONENT_ROOT, "event candidate root")
    build_root = require_under(
        REPO / "tmp", EVENT_COMPONENT_BUILD_ROOT, "event component build root"
    )
    manifest_path = require_under(REPO / "tmp", EVENT_COMPONENT_MANIFEST, "event manifest")
    summary_path = require_under(REPO / "tmp", EVENT_COMPONENT_SUMMARY, "event summary")
    require(root.is_dir(), f"event candidate root is missing: {root}")
    manifest = read_json(manifest_path, "event component manifest")
    summary = read_json(summary_path, "event component summary")
    require(manifest.get("schema") == EVENT_MANIFEST_SCHEMA, "event component manifest schema differs")
    candidates = manifest.get("candidates")
    require(isinstance(candidates, list) and len(candidates) == 2, "event component candidate list differs")
    by_resource = {
        str(item.get("resource")): item
        for item in candidates
        if isinstance(item, dict)
    }
    require(set(by_resource) == set(EVENT_COMPONENT_TARGET_SHA256), "event component resources differ")
    for relative, expected_hash in EVENT_COMPONENT_TARGET_SHA256.items():
        item = by_resource[relative]
        relative_path = str(item.get("relative_path", "")).replace("/", "\\")
        candidate_path = require_under(
            build_root, build_root / relative_path, f"event candidate {relative}"
        )
        require(
            candidate_path == root / Path(relative),
            f"event manifest candidate path differs: {relative}",
        )
        require(candidate_path.is_file(), f"event candidate file is missing: {relative}")
        require(
            str(item.get("packed_sha256", "")).upper() == expected_hash,
            f"event manifest hash differs: {relative}",
        )
        require(
            sha256_path(candidate_path) == expected_hash,
            f"event candidate file hash differs: {relative}",
        )
    inputs = summary.get("inputs")
    require(isinstance(inputs, dict), "event component summary inputs are missing")
    for key, relative in (("base", "MSG/JP/ev_strdata.bin"), ("pk", "MSG_PK/JP/msgev.bin")):
        row = inputs.get(key)
        require(isinstance(row, dict) and isinstance(row.get("source"), dict), f"event {key} source is missing")
        require(
            str(row["source"].get("sha256", "")).upper() == INPUT_SHA256[relative],
            f"event {key} does not start from the Wave8 preimage",
        )
    scope = summary.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("base_candidate_count") == 15
        and scope.get("pk_candidate_count") == 5
        and scope.get("total_candidate_count") == 20,
        "event component candidate-count contract differs",
    )
    return {
        "workstream": EVENT_WORKSTREAM.name,
        "manifest": relative_to_repo(manifest_path),
        "manifest_sha256": sha256_path(manifest_path),
        "summary": relative_to_repo(summary_path),
        "summary_sha256": sha256_path(summary_path),
        "candidate_root": relative_to_repo(root),
        "changed_paths": list(EVENT_COMPONENT_TARGET_SHA256),
        "input_sha256": {
            "MSG/JP/ev_strdata.bin": INPUT_SHA256["MSG/JP/ev_strdata.bin"],
            "MSG_PK/JP/msgev.bin": INPUT_SHA256["MSG_PK/JP/msgev.bin"],
        },
        "output_sha256": dict(EVENT_COMPONENT_TARGET_SHA256),
    }


def construct_payload() -> CombinedPayload:
    runtime_contract = runtime_component_contract()
    event_contract = event_component_contract()
    files = {
        relative: (RUNTIME_COMPONENT_ROOT / Path(relative)).read_bytes()
        for relative in PROFILE_PATHS
    }
    for relative in EVENT_COMPONENT_TARGET_SHA256:
        files[relative] = (EVENT_COMPONENT_ROOT / Path(relative)).read_bytes()
    actual = {relative: sha256_bytes(files[relative]) for relative in PROFILE_PATHS}
    require(actual == TARGET_SHA256, "combined payload differs from the pinned Wave9 target profile")
    changed = {
        relative
        for relative in PROFILE_PATHS
        if actual[relative] != INPUT_SHA256[relative]
    }
    require(changed == set(CHANGED_PATHS), f"combined changed path set differs: {sorted(changed)}")
    return CombinedPayload(
        files=files,
        component_contract={
            "runtime": runtime_contract,
            "event": event_contract,
        },
    )


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(value)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def build_manifest(payload: CombinedPayload) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "transaction_id": TRANSACTION_ID,
        "profile_paths": list(PROFILE_PATHS),
        "changed_paths": list(CHANGED_PATHS),
        "input_sha256": INPUT_SHA256,
        "output_sha256": TARGET_SHA256,
        "pinned_output_sha256": TARGET_SHA256,
        "component_contract": payload.component_contract,
        "real_game_qa_required_before_release": True,
        "steam_write_capability": "absent; candidate builder is tmp-only",
    }


def build_candidate(output_root: Path, manifest_path: Path) -> dict[str, Any]:
    output_root = require_tmp(output_root, "combined candidate output")
    manifest_path = require_tmp(manifest_path, "combined manifest output")
    require(not output_root.exists(), f"refusing to overwrite candidate directory: {output_root}")
    require(not manifest_path.exists(), f"refusing to overwrite manifest: {manifest_path}")
    payload = construct_payload()
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            destination = stage / Path(relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload.files[relative])
        actual = profile_hashes(stage)
        require(actual == TARGET_SHA256, "staged combined candidate profile differs")
        os.replace(stage, output_root)
        manifest = build_manifest(payload)
        atomic_write(manifest_path, canonical_json(manifest))
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def verify_components() -> dict[str, Any]:
    payload = construct_payload()
    profile = {relative: sha256_bytes(payload.files[relative]) for relative in PROFILE_PATHS}
    return {
        "status": "PASS",
        "input_sha256": INPUT_SHA256,
        "output_sha256": profile,
        "changed_paths": list(CHANGED_PATHS),
        "component_contract": payload.component_contract,
        "steam_game_resource_written": False,
        "write_scope": "none",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify = subparsers.add_parser("verify", help="verify components and compute the full profile")
    verify.set_defaults(command_handler="verify")
    build = subparsers.add_parser("build", help="write a full candidate only under tmp")
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    build.set_defaults(command_handler="build")
    args = parser.parse_args(argv)
    try:
        if args.command_handler == "verify":
            result = verify_components()
        else:
            manifest = build_candidate(args.output_root, args.manifest)
            result = {
                "status": "PASS",
                "candidate_root": str(args.output_root),
                "manifest": str(args.manifest),
                "changed_paths": manifest["changed_paths"],
                "output_sha256": manifest["output_sha256"],
                "steam_game_resource_written": False,
                "write_scope": "tmp",
            }
    except (CombinedTransactionError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
