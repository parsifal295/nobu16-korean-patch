#!/usr/bin/env python3
"""Build a private exact-profile envelope for the conservative text bundles.

The envelope combines Wave 42's 26 linebreak-stable event cells and Wave 44's
51 conservative dialogue records from the untouched Steam JP baseline.  It
writes only under ``tmp/``.  Steam application remains a separate, process-
gated transaction and is intentionally absent from this builder.
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
CANDIDATE_DIRNAME = "candidate_safe_static_v2"
GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
COMPONENTS = {
    "wave42": (
        REPO / "workstreams" / "pc_event_quality_wave42_safe_static_bundle_v1" / "build_pc_event_quality_wave42_safe_static_bundle_v1.py",
        "7E95C231B4B0E39FEA2F59D2682E25FD76FC805B6B0B78C8E443829A2C7075A3",
    ),
    "wave44": (
        REPO / "workstreams" / "pc_dialogue_quality_wave44_safe_static_bundle_v1" / "build_pc_dialogue_quality_wave44_safe_static_bundle_v1.py",
        "2360AC8B741CBF3D407F8E7D8215A4998B10529A7E62656D003E85228414C3F2",
    ),
}

SCHEMA = "nobu16.kr.pc-text-quality-wave45-safe-static-transaction-envelope.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-text-quality-wave45-safe-static-transaction-envelope-audit.v1"
EXPECTED_RELATIVES = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgui.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgstf_ce.bin",
)
INPUT_PROFILES = {
    "MSG/JP/ev_strdata.bin": {"size": 928_119, "sha256": "02AC90B818E8F75683CD5BACF277E91048D4510E448A8699242D3B19299FE067"},
    "MSG/JP/msggame.bin": {"size": 1_504_422, "sha256": "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688"},
    "MSG/JP/strdata.bin": {"size": 957_200, "sha256": "37A1F6280B2663A7FF055C6A2105B5658CA62065582A66213C6D4D4AE2A79E0A"},
    "MSG_PK/JP/msgui.bin": {"size": 122_733, "sha256": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7"},
    "MSG_PK/JP/msgev.bin": {"size": 994_727, "sha256": "AEE0D9992B963E17B3C118AA54DACC60390936FF48876674CA7675A2A11A3668"},
    "MSG_PK/JP/msgdata.bin": {"size": 496_991, "sha256": "8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A"},
    "MSG_PK/JP/msgbre.bin": {"size": 484_068, "sha256": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939"},
    "MSG_PK/JP/msgire.bin": {"size": 23_128, "sha256": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB"},
    "MSG_PK/JP/msgstf.bin": {"size": 17_341, "sha256": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B"},
    "MSG_PK/JP/msggame.bin": {"size": 1_806_542, "sha256": "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9"},
    "MSG_PK/JP/msgstf_ce.bin": {"size": 18_767, "sha256": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63"},
}
TARGET_PROFILES = {
    **INPUT_PROFILES,
    "MSG/JP/ev_strdata.bin": {"size": 928_131, "sha256": "85CC7B26E2D9A159AABD71610A9694AD803CFADE8CCD12F1A082AE2A35E3FF45"},
    "MSG/JP/msggame.bin": {"size": 1_504_410, "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB"},
    "MSG_PK/JP/msgev.bin": {"size": 994_739, "sha256": "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE"},
    "MSG_PK/JP/msggame.bin": {"size": 1_806_538, "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092"},
}
REPLACED_RELATIVES = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
)


class Wave45Error(RuntimeError):
    """Raised when a pinned input or private envelope differs."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave45Error(message)


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


def load_component(name: str) -> Any:
    path, expected_hash = COMPONENTS[name]
    require(path.is_file(), f"{name} component is absent")
    require(sha256_path(path) == expected_hash, f"{name} component hash differs")
    spec = importlib.util.spec_from_file_location(f"wave45_imported_{name}", path)
    if spec is None or spec.loader is None:
        raise Wave45Error(f"cannot load {name} component")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W42 = load_component("wave42")
W44 = load_component("wave44")


@dataclass(frozen=True)
class CandidateEnvelope:
    files: Mapping[str, bytes]
    audit: Mapping[str, Any]


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave45Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def profile_of(value: bytes) -> dict[str, Any]:
    return {"size": len(value), "sha256": sha256_bytes(value)}


def read_private_component_candidate(
    module: Any,
    candidate_root: Path,
    expected_resources: Mapping[str, Mapping[str, Any]],
    expected_audit_target: Mapping[str, Any],
    expected_count: int,
    count_key: str,
    label: str,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = candidate_root.resolve(strict=True)
    expected_files = set(expected_resources) | {"audit.v1.json", "candidate_manifest.v1.json"}
    discovered = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(discovered == expected_files, f"{label} private candidate file set differs")
    payloads: dict[str, bytes] = {}
    for relative, profile in expected_resources.items():
        payload = (root / Path(relative)).read_bytes()
        expected_packed = {"size": profile["size"], "sha256": profile["sha256"]}
        require(profile_of(payload) == expected_packed, f"{label} private target profile differs: {relative}")
        payloads[relative] = payload
    try:
        audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Wave45Error(f"{label} private candidate metadata is invalid") from exc
    audit_hash = W44.W39.sha256_bytes(W44.canonical_json(audit)) if module is W44 else W42.W31.sha256_bytes(W42.canonical_json(audit))
    require(manifest.get("audit_sha256") == audit_hash, f"{label} private audit binding differs")
    require(audit.get("target") == dict(expected_audit_target), f"{label} private audit target differs")
    require(audit.get(count_key) == expected_count, f"{label} private audit count differs")
    return payloads, audit


def prepare_candidate() -> CandidateEnvelope:
    event_resources = {
        W42.W31.RESOURCES["base"].relative: W42.TARGET_PROFILES["base"],
        W42.W31.RESOURCES["pk"].relative: W42.TARGET_PROFILES["pk"],
    }
    dialogue_resources = dict(W44.TARGET_PROFILES)
    event_payloads, event_audit = read_private_component_candidate(
        W42,
        W42.TMP_ROOT / W42.CANDIDATE_DIRNAME,
        event_resources,
        W42.TARGET_PROFILES,
        len(W42.CHANGES),
        "changed_cell_count",
        "Wave 42",
    )
    dialogue_payloads, dialogue_audit = read_private_component_candidate(
        W44,
        W44.TMP_ROOT / "candidate",
        dialogue_resources,
        W44.TARGET_PROFILES,
        len(W44.CHANGES),
        "changed_record_count",
        "Wave 44",
    )
    replacements = {
        **event_payloads,
        **dialogue_payloads,
    }
    require(set(replacements) == set(REPLACED_RELATIVES), "replacement scope differs")
    files: dict[str, bytes] = {}
    retained: list[str] = []
    for relative in EXPECTED_RELATIVES:
        source = GAME_ROOT / Path(relative)
        require(source.is_file(), f"installed input is absent: {relative}")
        before = source.read_bytes()
        require(profile_of(before) == INPUT_PROFILES[relative], f"installed input profile differs: {relative}")
        after = replacements.get(relative, before)
        require(profile_of(after) == TARGET_PROFILES[relative], f"target profile differs: {relative}")
        files[relative] = after
        if relative not in replacements:
            require(after == before, f"retained input differs: {relative}")
            retained.append(relative)
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "component_builder_sha256": {name: expected for name, (_path, expected) in COMPONENTS.items()},
        "candidate_profile_kind": "exact_pc_only_text_audit_11_file_set",
        "input": INPUT_PROFILES,
        "target": TARGET_PROFILES,
        "replaced_relatives": list(REPLACED_RELATIVES),
        "retained_relatives": retained,
        "wave42_changed_cell_count": len(W42.CHANGES),
        "wave42_excluded_real_game_display_qa": W42.EXCLUDED_DISPLAY_QA,
        "wave42_component_audit_sha256": W42.W31.sha256_bytes(W42.canonical_json(event_audit)),
        "wave44_changed_record_count": len(W44.CHANGES),
        "wave44_excluded_real_game_qa": W44.EXCLUDED_REAL_GAME_QA,
        "wave44_component_audit_sha256": W44.W39.sha256_bytes(W44.canonical_json(dialogue_audit)),
    }
    return CandidateEnvelope(files, audit)


def write_candidate(envelope: CandidateEnvelope) -> Path:
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(not output.exists(), f"candidate output already exists: {output}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for relative, payload in envelope.files.items():
            path = stage / Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        os.replace(stage, output)
        (TMP_ROOT / "audit.v1.json").write_bytes(canonical_json(envelope.audit))
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    envelope = prepare_candidate()
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(output.is_dir(), "private candidate is absent")
    discovered = sorted(path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file())
    require(discovered == sorted(EXPECTED_RELATIVES), "private candidate file set differs")
    for relative, payload in envelope.files.items():
        path = output / Path(relative)
        require(path.is_file() and path.read_bytes() == payload, f"private candidate differs: {relative}")
    audit_path = TMP_ROOT / "audit.v1.json"
    require(audit_path.read_bytes() == canonical_json(envelope.audit), "private envelope audit differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "candidate_profile_kind": envelope.audit["candidate_profile_kind"],
        "replaced_relatives": list(REPLACED_RELATIVES),
        "retained_file_count": len(envelope.audit["retained_relatives"]),
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        envelope = prepare_candidate()
        output = write_candidate(envelope)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "candidate_profile_kind": envelope.audit["candidate_profile_kind"],
            "replaced_relatives": list(REPLACED_RELATIVES),
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
