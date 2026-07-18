#!/usr/bin/env python3
"""Assemble the private Wave 15 plus Wave 16 Japanese text-audit bundle.

The bundle reads only two already-built private candidates below this
workspace's tmp directory:

* the Wave 16 eleven-file dialogue profile; and
* the Wave 15 event-name msgev candidate.

It never reads Nintendo Switch data or writes Steam, Git, a release, or a
transaction.  Its only write path is this workstream's own tmp directory.
All source-candidate artifacts, per-file profiles, and the final three-file
diff from the Wave 14 baseline are pinned and checked before output is made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name

WAVE16_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave16_static_inflection_v1"
WAVE16_CANDIDATE_ROOT = WAVE16_ROOT / "candidate"
WAVE16_AUDIT_PATH = WAVE16_ROOT / "audit.v1.json"
WAVE16_MANIFEST_PATH = WAVE16_ROOT / "build_manifest.v1.json"

WAVE15_CANDIDATE_ROOT = REPO / "tmp" / "pc_event_name_quality_wave15_v1" / "candidate-v1"
WAVE15_RESOURCE = "MSG_PK/JP/msgev.bin"
WAVE15_AUDIT_PATH = WAVE15_CANDIDATE_ROOT / "audit.v1.json"
WAVE15_MANIFEST_PATH = WAVE15_CANDIDATE_ROOT / "candidate_manifest.v1.json"

SCHEMA = "nobu16.kr.pc-text-quality-wave15-bundle.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-text-quality-wave15-bundle-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-text-quality-wave15-bundle-manifest.v1"

PROFILE_NAME = "JP_TEXT_AUDIT"
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
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGEV = "MSG_PK/JP/msgev.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
FINAL_CHANGED_PATHS = (BASE_MSGGAME, PK_MSGEV, PK_MSGGAME)
WAVE15_EVENT_NAME_IDS = (3015, 3016, 3084)

# The only accepted predecessor profile: Wave 14's eleven-file Japanese
# text-audit profile.  The final bundle must differ from this map in exactly
# the three paths in FINAL_CHANGED_PATHS.
WAVE14_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8",
    "MSG/JP/strdata.bin": "5F308F416378976C1AB0B50D4A91C9DA38C637A0A842BAB04FB48256B2103E28",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "69090EC9EEE1DF9EAFB64BB35CEFD285A5089FDE78E9A4A855EAA0AE5991C168",
    PK_MSGEV: "3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5",
    PK_MSGGAME: "BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}

# The Wave 16 source candidate is a complete eleven-file profile.  Only its
# two msggame members differ from Wave 14.
WAVE16_SHA256 = {
    **WAVE14_SHA256,
    BASE_MSGGAME: "EEA622999F38C72F2088467E04D4A885B684D3FD3CF99FB72879A72079CF9351",
    PK_MSGGAME: "9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC",
}
WAVE16_SIZES = {
    "MSG/JP/ev_strdata.bin": 928_123,
    BASE_MSGGAME: 1_504_655,
    "MSG/JP/strdata.bin": 957_204,
    "MSG_PK/JP/msgbre.bin": 484_068,
    "MSG_PK/JP/msgdata.bin": 496_995,
    PK_MSGEV: 994_707,
    PK_MSGGAME: 1_806_759,
    "MSG_PK/JP/msgire.bin": 23_128,
    "MSG_PK/JP/msgstf.bin": 17_341,
    "MSG_PK/JP/msgstf_ce.bin": 18_767,
    "MSG_PK/JP/msgui.bin": 122_733,
}

WAVE15_MSGEV_SHA256 = "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3"
WAVE15_MSGEV_SIZE = 994_711
WAVE15_CURRENT_TEXT_SHA256 = {
    3015: "28CB219E5D8FBDB0D0C5145FF7BEB026174B77FBB53399A2F2EFAA8700E99756",
    3016: "3EF6F51F5F2ED6A8FE67F23DE3D0C5EDF96D9D50E0A8A9E64D9B2A62B4284F37",
    3084: "BFE97B5118DC094195C93FD16BE8447D3F64C9525320A337506AB753D44617DF",
}
WAVE15_TARGET_TEXT_SHA256 = {
    3015: "17771E37F3BAEA251D037D54E856883A0C86E90E680CD62567D38E44A0186018",
    3016: "E3FEBFE1AE661F7126FDDBFE603D3A8972C481C685BFD01FA5033566EEBF6B53",
    3084: "0D8D92E08B423CA3ABA3BD56DF6B46B143B2920CD64B2A823C2A2C1B5AEE62EF",
}

FINAL_SHA256 = {**WAVE16_SHA256, PK_MSGEV: WAVE15_MSGEV_SHA256}
FINAL_SIZES = {**WAVE16_SIZES, PK_MSGEV: WAVE15_MSGEV_SIZE}

# Source audit and manifest bytes are separately pinned.  This prevents a
# same-path candidate from being silently substituted with an unrelated
# artifact, even before its profile is considered.
WAVE16_AUDIT_SIZE = 11_407
WAVE16_AUDIT_SHA256 = "5933023D10714439A839F044694C2447E90AE72E5D7E953B958689F588421690"
WAVE16_MANIFEST_SIZE = 4_292
WAVE16_MANIFEST_SHA256 = "108ACF1353CE300FF597B0F7BA509D37F256E067204BC85263977D37A7EBFE7A"
WAVE15_AUDIT_SIZE = 5_968
WAVE15_AUDIT_SHA256 = "B6EC426363CC25426A8E2FF8C5C0A1A5E6646CD9D610FE1F07910F88EFBDE744"
WAVE15_MANIFEST_SIZE = 803
WAVE15_MANIFEST_SHA256 = "D8471D794CDA61B215E2DB2CF7E470BFB69E5253F2A03B335D1D72ED421EC64D"


class BundleError(RuntimeError):
    """A source-candidate, profile, diff, or private-output guard failed."""


@dataclass(frozen=True)
class Bundle:
    profile: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require(condition: bool, label: str) -> None:
    if not condition:
        raise BundleError(label)


def require_tmp(path: Path, label: str) -> Path:
    resolved_path = path.resolve(strict=False)
    resolved_root = TMP_ROOT.resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise BundleError(f"{label} must stay under {resolved_root}") from exc
    return resolved_path


def require_exact_path(path: Path, expected: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    if resolved != expected.resolve(strict=False):
        raise BundleError(f"{label} differs from its only accepted source path")
    return resolved


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise BundleError(f"required file is absent: {path}")
    return {"size": path.stat().st_size, "sha256": sha256_path(path)}


def read_pinned_json(
    path: Path,
    *,
    label: str,
    expected_size: int,
    expected_sha256: str,
) -> dict[str, Any]:
    spec = file_spec(path)
    require(spec["size"] == expected_size, f"{label} size differs")
    require(spec["sha256"] == expected_sha256, f"{label} SHA-256 differs")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"{label} JSON cannot be read") from exc
    if not isinstance(value, dict):
        raise BundleError(f"{label} JSON root is not an object")
    return value


def profile_hashes(profile: Mapping[str, bytes]) -> dict[str, str]:
    return {path: sha256_bytes(profile[path]) for path in PROFILE_PATHS}


def assert_profile(
    profile: Mapping[str, bytes],
    expected_hashes: Mapping[str, str],
    expected_sizes: Mapping[str, int],
    label: str,
) -> None:
    require(tuple(profile) == PROFILE_PATHS, f"{label} path order or set differs")
    require(tuple(expected_hashes) == PROFILE_PATHS, f"{label} expected hash path set differs")
    require(tuple(expected_sizes) == PROFILE_PATHS, f"{label} expected size path set differs")
    for relative in PROFILE_PATHS:
        payload = profile[relative]
        require(len(payload) == expected_sizes[relative], f"{label} size differs: {relative}")
        require(
            sha256_bytes(payload) == expected_hashes[relative],
            f"{label} SHA-256 differs: {relative}",
        )


def read_profile(
    root: Path,
    expected_hashes: Mapping[str, str],
    expected_sizes: Mapping[str, int],
    label: str,
) -> dict[str, bytes]:
    profile: dict[str, bytes] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise BundleError(f"{label} lacks profile resource: {relative}")
        profile[relative] = path.read_bytes()
    assert_profile(profile, expected_hashes, expected_sizes, label)
    return profile


def validate_wave16_evidence(audit: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    require(
        audit.get("schema") == "nobu16.kr.pc-dialogue-quality-wave16-static-inflection-audit.v1",
        "Wave 16 audit schema differs",
    )
    require(audit.get("input_sha256") == WAVE14_SHA256, "Wave 16 audit predecessor profile differs")
    require(audit.get("target_sha256") == WAVE16_SHA256, "Wave 16 audit target profile differs")
    policy = audit.get("source_policy")
    require(isinstance(policy, dict), "Wave 16 audit policy is absent")
    require(policy.get("switch_korean_read") is False, "Wave 16 audit used Switch Korean")
    require(policy.get("steam_game_resource_written") is False, "Wave 16 audit wrote Steam")
    require(policy.get("git_operation") == "absent", "Wave 16 audit Git policy differs")
    require(policy.get("release_operation") == "absent", "Wave 16 audit release policy differs")

    require(
        manifest.get("schema") == "nobu16.kr.pc-dialogue-quality-wave16-static-inflection.v1",
        "Wave 16 manifest schema differs",
    )
    require(manifest.get("profile_paths") == list(PROFILE_PATHS), "Wave 16 manifest profile differs")
    require(manifest.get("changed_paths") == [BASE_MSGGAME, PK_MSGGAME], "Wave 16 change set differs")
    require(manifest.get("input_sha256") == WAVE14_SHA256, "Wave 16 manifest predecessor differs")
    require(manifest.get("output_sha256") == WAVE16_SHA256, "Wave 16 manifest output differs")
    require(manifest.get("pinned_output_sha256") == WAVE16_SHA256, "Wave 16 pinned output differs")
    require(manifest.get("audit_sha256") == WAVE16_AUDIT_SHA256, "Wave 16 manifest audit differs")
    require(manifest.get("steam_write_capability") == "absent", "Wave 16 manifest Steam policy differs")
    require(manifest.get("git_operation") == "absent", "Wave 16 manifest Git policy differs")
    require(manifest.get("release_operation") == "absent", "Wave 16 manifest release policy differs")


def validate_wave15_evidence(audit: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    require(
        audit.get("schema") == "nobu16.kr.pc-event-name-quality-wave15-audit.v1",
        "Wave 15 audit schema differs",
    )
    require(audit.get("resource") == PK_MSGEV, "Wave 15 audit resource differs")
    require(audit.get("only_changed_ids") == list(WAVE15_EVENT_NAME_IDS), "Wave 15 audit ID set differs")
    require(audit.get("input", {}).get("sha256") == WAVE14_SHA256[PK_MSGEV], "Wave 15 input differs")
    require(audit.get("output", {}).get("sha256") == WAVE15_MSGEV_SHA256, "Wave 15 output differs")
    policy = audit.get("source_policy")
    require(isinstance(policy, dict), "Wave 15 audit policy is absent")
    require(policy.get("switch_korean_read") is False, "Wave 15 audit used Switch Korean")
    require(policy.get("steam_game_resource_written") is False, "Wave 15 audit wrote Steam")
    require(policy.get("git_operation_capability") == "absent", "Wave 15 Git policy differs")
    require(policy.get("steam_apply_or_transaction_capability") == "absent", "Wave 15 Steam policy differs")

    require(
        manifest.get("schema") == "nobu16.kr.pc-event-name-quality-wave15-manifest.v1",
        "Wave 15 manifest schema differs",
    )
    require(manifest.get("candidate_only") is True, "Wave 15 candidate-only flag differs")
    require(manifest.get("resource") == PK_MSGEV, "Wave 15 manifest resource differs")
    require(manifest.get("changed_ids") == list(WAVE15_EVENT_NAME_IDS), "Wave 15 manifest ID set differs")
    require(manifest.get("input", {}).get("sha256") == WAVE14_SHA256[PK_MSGEV], "Wave 15 manifest input differs")
    require(manifest.get("output", {}).get("sha256") == WAVE15_MSGEV_SHA256, "Wave 15 manifest output differs")
    require(manifest.get("audit_sha256") == WAVE15_AUDIT_SHA256, "Wave 15 manifest audit differs")
    require(manifest.get("switch_korean_input") == "forbidden", "Wave 15 Switch policy differs")
    require(manifest.get("steam_game_resource_write") == "absent", "Wave 15 Steam policy differs")
    require(manifest.get("git_commit") == "not_implemented", "Wave 15 Git policy differs")


def load_wave16_source() -> tuple[dict[str, bytes], dict[str, Any]]:
    root = require_exact_path(WAVE16_CANDIDATE_ROOT, WAVE16_CANDIDATE_ROOT, "Wave 16 root")
    profile = read_profile(root, WAVE16_SHA256, WAVE16_SIZES, "Wave 16 source profile")
    audit = read_pinned_json(
        require_exact_path(WAVE16_AUDIT_PATH, WAVE16_AUDIT_PATH, "Wave 16 audit path"),
        label="Wave 16 audit",
        expected_size=WAVE16_AUDIT_SIZE,
        expected_sha256=WAVE16_AUDIT_SHA256,
    )
    manifest = read_pinned_json(
        require_exact_path(WAVE16_MANIFEST_PATH, WAVE16_MANIFEST_PATH, "Wave 16 manifest path"),
        label="Wave 16 manifest",
        expected_size=WAVE16_MANIFEST_SIZE,
        expected_sha256=WAVE16_MANIFEST_SHA256,
    )
    validate_wave16_evidence(audit, manifest)
    return profile, {
        "candidate_root": WAVE16_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "profile_sha256": WAVE16_SHA256,
        "audit": {"size": WAVE16_AUDIT_SIZE, "sha256": WAVE16_AUDIT_SHA256},
        "manifest": {"size": WAVE16_MANIFEST_SIZE, "sha256": WAVE16_MANIFEST_SHA256},
    }


def load_wave15_source() -> tuple[bytes, dict[str, Any]]:
    root = require_exact_path(WAVE15_CANDIDATE_ROOT, WAVE15_CANDIDATE_ROOT, "Wave 15 root")
    resource_path = root / PK_MSGEV
    spec = file_spec(resource_path)
    require(spec["size"] == WAVE15_MSGEV_SIZE, "Wave 15 msgev size differs")
    require(spec["sha256"] == WAVE15_MSGEV_SHA256, "Wave 15 msgev SHA-256 differs")
    audit = read_pinned_json(
        require_exact_path(WAVE15_AUDIT_PATH, WAVE15_AUDIT_PATH, "Wave 15 audit path"),
        label="Wave 15 audit",
        expected_size=WAVE15_AUDIT_SIZE,
        expected_sha256=WAVE15_AUDIT_SHA256,
    )
    manifest = read_pinned_json(
        require_exact_path(WAVE15_MANIFEST_PATH, WAVE15_MANIFEST_PATH, "Wave 15 manifest path"),
        label="Wave 15 manifest",
        expected_size=WAVE15_MANIFEST_SIZE,
        expected_sha256=WAVE15_MANIFEST_SHA256,
    )
    validate_wave15_evidence(audit, manifest)
    return resource_path.read_bytes(), {
        "candidate_root": WAVE15_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "resource": {"size": WAVE15_MSGEV_SIZE, "sha256": WAVE15_MSGEV_SHA256},
        "audit": {"size": WAVE15_AUDIT_SIZE, "sha256": WAVE15_AUDIT_SHA256},
        "manifest": {"size": WAVE15_MANIFEST_SIZE, "sha256": WAVE15_MANIFEST_SHA256},
    }


def changed_paths(before: Mapping[str, str], after: Mapping[str, str]) -> tuple[str, ...]:
    require(tuple(before) == PROFILE_PATHS, "before profile path set differs")
    require(tuple(after) == PROFILE_PATHS, "after profile path set differs")
    return tuple(relative for relative in PROFILE_PATHS if before[relative] != after[relative])


def validate_event_name_diff(before: bytes, after: bytes) -> dict[str, Any]:
    try:
        _before_header, before_raw = decompress_wrapper(before)
        _after_header, after_raw = decompress_wrapper(after)
        before_table = parse_message_table(before_raw)
        after_table = parse_message_table(after_raw)
    except Exception as exc:
        raise BundleError("Wave 15 msgev source cannot be parsed") from exc
    require(
        rebuild_message_table(before_table, before_table.texts) == before_raw,
        "Wave 16 msgev source table rebuild differs",
    )
    require(
        rebuild_message_table(after_table, after_table.texts) == after_raw,
        "Wave 15 msgev source table rebuild differs",
    )
    require(before_table.string_count == after_table.string_count, "msgev string count changed")
    actual_ids = tuple(
        entry_id
        for entry_id, (old, new) in enumerate(zip(before_table.texts, after_table.texts))
        if old != new
    )
    require(actual_ids == WAVE15_EVENT_NAME_IDS, f"Wave 15 msgev text diff differs: {actual_ids}")
    rows: list[dict[str, Any]] = []
    for entry_id in actual_ids:
        current_hash = text_hash(before_table.texts[entry_id])
        target_hash = text_hash(after_table.texts[entry_id])
        require(
            current_hash == WAVE15_CURRENT_TEXT_SHA256[entry_id],
            f"Wave 15 current text hash differs: {entry_id}",
        )
        require(
            target_hash == WAVE15_TARGET_TEXT_SHA256[entry_id],
            f"Wave 15 target text hash differs: {entry_id}",
        )
        rows.append(
            {
                "id": entry_id,
                "current_utf16le_sha256": current_hash,
                "target_utf16le_sha256": target_hash,
            }
        )
    return {"changed_ids": list(actual_ids), "rows": rows}


def validate_final_profile(profile: Mapping[str, bytes], wave16_profile: Mapping[str, bytes]) -> dict[str, Any]:
    assert_profile(profile, FINAL_SHA256, FINAL_SIZES, "final JP_TEXT_AUDIT profile")
    final_hashes = profile_hashes(profile)
    require(
        changed_paths(WAVE14_SHA256, final_hashes) == FINAL_CHANGED_PATHS,
        "final profile does not have exactly the required three-file diff",
    )
    require(
        changed_paths(WAVE14_SHA256, WAVE16_SHA256) == (BASE_MSGGAME, PK_MSGGAME),
        "Wave 16 source profile diff differs",
    )
    require(
        changed_paths(WAVE16_SHA256, final_hashes) == (PK_MSGEV,),
        "bundle must alter only msgev after Wave 16",
    )
    for relative in PROFILE_PATHS:
        if relative == PK_MSGEV:
            continue
        require(
            profile[relative] == wave16_profile[relative],
            f"bundle did not retain Wave 16 bytes: {relative}",
        )
    event_diff = validate_event_name_diff(wave16_profile[PK_MSGEV], profile[PK_MSGEV])
    return {
        "baseline": "Wave 14 JP_TEXT_AUDIT profile",
        "changed_paths": list(FINAL_CHANGED_PATHS),
        "unchanged_paths": [path for path in PROFILE_PATHS if path not in FINAL_CHANGED_PATHS],
        "wave16_to_bundle_changed_paths": [PK_MSGEV],
        "per_file": [
            {
                "path": path,
                "wave14_sha256": WAVE14_SHA256[path],
                "wave16_source_sha256": WAVE16_SHA256[path],
                "final_sha256": final_hashes[path],
                "changed_from_wave14": path in FINAL_CHANGED_PATHS,
            }
            for path in PROFILE_PATHS
        ],
        "event_name_text_diff": event_diff,
    }


def build_manifest(audit: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "profile": PROFILE_NAME,
        "profile_paths": list(PROFILE_PATHS),
        "wave14_predecessor_sha256": WAVE14_SHA256,
        "final_sha256": FINAL_SHA256,
        "final_sizes": FINAL_SIZES,
        "changed_from_wave14": list(FINAL_CHANGED_PATHS),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "switch_korean_input": "absent",
        "steam_game_resource_write": "absent",
        "steam_apply": "absent",
        "git_operation": "absent",
        "release_operation": "absent",
        "network_operation": "absent",
    }


def prepare_bundle() -> Bundle:
    """Read and validate both private sources, then assemble the final profile."""

    wave16_profile, wave16_evidence = load_wave16_source()
    wave15_msgev, wave15_evidence = load_wave15_source()
    final_profile = dict(wave16_profile)
    final_profile[PK_MSGEV] = wave15_msgev
    final_diff = validate_final_profile(final_profile, wave16_profile)

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "private candidate composition",
            "wave15_candidate_read": True,
            "wave16_candidate_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
            "network_operation": "absent",
        },
        "profile": PROFILE_NAME,
        "profile_paths": list(PROFILE_PATHS),
        "source_candidates": {"wave15": wave15_evidence, "wave16": wave16_evidence},
        "wave14_predecessor_sha256": WAVE14_SHA256,
        "wave16_source_sha256": WAVE16_SHA256,
        "final_sha256": FINAL_SHA256,
        "final_sizes": FINAL_SIZES,
        "final_diff": final_diff,
    }
    return Bundle(final_profile, audit, build_manifest(audit))


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with temporary.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def remove_private_tree(path: Path) -> None:
    resolved = require_tmp(path, "private cleanup")
    if resolved.exists():
        shutil.rmtree(resolved)


def write_bundle(bundle: Bundle, output_root: Path) -> dict[str, Any]:
    output_root = require_tmp(output_root, "candidate output")
    if output_root.exists():
        raise BundleError(f"refusing to overwrite candidate output: {output_root}")
    staging = output_root.parent / f".{output_root.name}.staging-{uuid.uuid4().hex}"
    staging = require_tmp(staging, "candidate staging output")
    if staging.exists():
        raise BundleError(f"candidate staging path already exists: {staging}")
    try:
        staging.mkdir(parents=True, exist_ok=False)
        for relative in PROFILE_PATHS:
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(destination, bundle.profile[relative])
        atomic_write(staging / "audit.v1.json", canonical_json(bundle.audit))
        atomic_write(staging / "bundle_manifest.v1.json", canonical_json(bundle.manifest))
        staged_profile = read_profile(staging, FINAL_SHA256, FINAL_SIZES, "bundle staging profile")
        # Re-read the Wave 16 source through its full pinned-profile and
        # evidence checks instead of trusting a bare path during the write.
        staged_wave16_profile, _evidence = load_wave16_source()
        validate_final_profile(staged_profile, staged_wave16_profile)
        require(
            sha256_path(staging / "audit.v1.json") == bundle.manifest["audit_sha256"],
            "written bundle audit SHA-256 differs",
        )
        os.replace(staging, output_root)
    except Exception:
        remove_private_tree(staging)
        raise
    return {
        "candidate": output_root.relative_to(REPO).as_posix(),
        "audit": (output_root / "audit.v1.json").relative_to(REPO).as_posix(),
        "manifest": (output_root / "bundle_manifest.v1.json").relative_to(REPO).as_posix(),
        "profile": PROFILE_NAME,
        "changed_from_wave14": list(FINAL_CHANGED_PATHS),
        "steam_game_resource_write": "absent",
    }


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "private candidate")
    bundle = prepare_bundle()
    profile = read_profile(candidate_root, FINAL_SHA256, FINAL_SIZES, "private bundle profile")
    for relative in PROFILE_PATHS:
        require(profile[relative] == bundle.profile[relative], f"private bundle bytes differ: {relative}")
    audit_path = candidate_root / "audit.v1.json"
    manifest_path = candidate_root / "bundle_manifest.v1.json"
    require(audit_path.is_file() and manifest_path.is_file(), "private bundle metadata is absent")
    require(audit_path.read_bytes() == canonical_json(bundle.audit), "private bundle audit differs")
    require(
        manifest_path.read_bytes() == canonical_json(bundle.manifest),
        "private bundle manifest differs",
    )


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True))


def command_hash(_args: argparse.Namespace) -> int:
    bundle = prepare_bundle()
    print_json(
        {
            "status": "ok",
            "profile": PROFILE_NAME,
            "changed_from_wave14": list(FINAL_CHANGED_PATHS),
            "final_sha256": profile_hashes(bundle.profile),
            "steam_game_resource_write": "absent",
        }
    )
    return 0


def command_build(args: argparse.Namespace) -> int:
    bundle = prepare_bundle()
    result = write_bundle(bundle, args.output_root)
    verify_private_candidate(args.output_root)
    print_json({"status": "ok", **result})
    return 0


def command_verify_private(args: argparse.Namespace) -> int:
    verify_private_candidate(args.candidate_root)
    print_json(
        {
            "status": "ok",
            "candidate": args.candidate_root.resolve(strict=False).relative_to(REPO).as_posix(),
            "steam_game_resource_write": "absent",
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    hash_command = commands.add_parser("hash", help="verify both sources and assemble in memory")
    hash_command.set_defaults(func=command_hash)
    build_command = commands.add_parser("build", help="write one private bundle below tmp")
    build_command.add_argument(
        "--output-root",
        type=Path,
        default=TMP_ROOT / "candidate-v1",
        help="must be a new directory below this workstream's tmp root",
    )
    build_command.set_defaults(func=command_build)
    verify_command = commands.add_parser("verify-private", help="verify a previously built private bundle")
    verify_command.add_argument("--candidate-root", type=Path, required=True)
    verify_command.set_defaults(func=command_verify_private)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, BundleError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
