#!/usr/bin/env python3
"""Assemble the private Wave 20 Japanese text-audit bundle.

The bundle composes exactly two already-built private candidates:

* Wave 21's complete eleven-file JP_TEXT_AUDIT profile; and
* Wave 18's reviewed MSGEV static-label candidate.

It retains every Wave 21 file byte-for-byte except MSG_PK/JP/msgev.bin,
which is replaced with Wave 18's pinned output.  In particular, the two
Issue 61 retention paths (MSG/JP/strdata.bin and MSG_PK/JP/msgdata.bin)
remain Wave 21 bytes.  The builder has no Steam, Git, release, transaction,
or network operation; it can only create a new candidate below its own tmp
directory.
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

WAVE21_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave21_static_quality_v1"
WAVE21_CANDIDATE_ROOT = WAVE21_ROOT / "candidate"
WAVE21_AUDIT_PATH = WAVE21_ROOT / "audit.v1.json"
WAVE21_MANIFEST_PATH = WAVE21_ROOT / "build_manifest.v1.json"

WAVE18_ROOT = REPO / "tmp" / "pc_event_static_labels_wave18_v1"
WAVE18_CANDIDATE_ROOT = WAVE18_ROOT / "candidate-v1"
WAVE18_AUDIT_PATH = WAVE18_CANDIDATE_ROOT / "audit.v1.json"
WAVE18_MANIFEST_PATH = WAVE18_CANDIDATE_ROOT / "candidate_manifest.v1.json"

SCHEMA = "nobu16.kr.pc-text-quality-wave20-bundle.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-text-quality-wave20-bundle-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-text-quality-wave20-bundle-manifest.v1"

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
ISSUE61_RETAINED_PATHS = ("MSG/JP/strdata.bin", "MSG_PK/JP/msgdata.bin")

# Wave 21 is the only accepted complete profile.  Its manifest records the
# Wave 19 predecessor map; Wave 20 must retain this complete Wave 21 result.
WAVE21_INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "C00B78165B06A5A9D2BFBE134E847E4B00EC3E5243EE9A1981BA1BB68CFA79C6",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    PK_MSGEV: "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3",
    PK_MSGGAME: "7D7826A575E4BA80FEE1E4FE920CBD7E16A48F0DA529D06514EDB59B11422FBC",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
WAVE21_SHA256 = {
    **WAVE21_INPUT_SHA256,
    PK_MSGGAME: "0C3C2196E59BCBC1A066DF7097B37C281F8A6236DE70876CCD7BCAB44459BEA9",
}
WAVE21_SIZES = {
    "MSG/JP/ev_strdata.bin": 928_123,
    BASE_MSGGAME: 1_504_671,
    "MSG/JP/strdata.bin": 957_204,
    "MSG_PK/JP/msgbre.bin": 484_068,
    "MSG_PK/JP/msgdata.bin": 496_995,
    PK_MSGEV: 994_711,
    PK_MSGGAME: 1_806_775,
    "MSG_PK/JP/msgire.bin": 23_128,
    "MSG_PK/JP/msgstf.bin": 17_341,
    "MSG_PK/JP/msgstf_ce.bin": 18_767,
    "MSG_PK/JP/msgui.bin": 122_733,
}

WAVE21_AUDIT_SIZE = 10_546
WAVE21_AUDIT_SHA256 = "F8F0E075BF24113B9F68473387D2D603A9956EA72C48A9C1D9CB4D3F6E4C8331"
WAVE21_MANIFEST_SIZE = 4_333
WAVE21_MANIFEST_SHA256 = "A4A0ADE835A3013ED321B9AB67F250CF82337DCDEFF79B914DDFFB8D8EF8B542"
WAVE21_COORDINATES = (
    "MSG_PK/JP/msggame.bin:2:249:1",
    "MSG_PK/JP/msggame.bin:2:321:1",
)

# Wave 18 is accepted only as a reviewed replacement for Wave 21's CE1A
# MSGEV member.  Its output contains these eight and only these eight text
# changes; the full packed file is separately pinned below.
WAVE18_MSGEV_SHA256 = "D922E7C2B0BD4078A5DB14C87973ECB7BB1A62A4CA2EA30A03A231AB40C1E86B"
WAVE18_MSGEV_SIZE = 994_727
WAVE18_EVENT_IDS = (11007, 14040, 14386, 14391, 14403, 14623, 14648, 14651)
WAVE18_EVENT_TEXT_HASHES = {
    11007: (
        "CE09E23C5049CFFF024A4FABF4D540D13A9AFE039A7316BAD8EE1C48C5488612",
        "20C1177749D8D064F55EAB592EFAEBC5AFED32E5188F087D858ED8985FFD9DCF",
    ),
    14040: (
        "487AB0E66ACCA98774AEDA07E97ED3A5115155E3805022A8B37D336882A04222",
        "1783CE86C06EE7188AEEBF28722B472B605F955F1048C5AD0C657C8B6B0F6B92",
    ),
    14386: (
        "70EA289A0A1A52A8FD86F5F7154EF265F8B6C0C55ED9E1FBBCB7739DC2301E12",
        "8563D1232D3D57CDA9B202BF5B4E871DC195FC488D8B6587CF04BD1662ED6E35",
    ),
    14391: (
        "FFD12229B5EEEB774EDEC300CD5E22DA527C1E8210684508B25A6401104DC013",
        "17673B651C90E851B227416C48C21EE906358F4E4E353A64E369D45A03B12DEA",
    ),
    14403: (
        "2848E41B70A59175371D30C803FFBED6D09D75B131A59B74463669377C026A02",
        "5C15341DC6CEF92CB76CBF7998B0D96BEB7D8153077B3CEC78B4F5263121E34A",
    ),
    14623: (
        "1CAB77164CB7E32F9F65419C20FE4828DBEC182FD1AC6A15D6A283D615C4975A",
        "268717A64E9CE98D8D17FBF369ADF8344BDEF767069FBC07BE0E0CBCABCBC8D5",
    ),
    14648: (
        "3E40D6D3A5FD808A6B520E7715E29CA7B2175A4EFEB61DC013FD4C837A75C16E",
        "E100CE5A7B5533CD1972C692780584DD4AD9B211D3BDF276648225617D31890C",
    ),
    14651: (
        "3E40D6D3A5FD808A6B520E7715E29CA7B2175A4EFEB61DC013FD4C837A75C16E",
        "E100CE5A7B5533CD1972C692780584DD4AD9B211D3BDF276648225617D31890C",
    ),
}
WAVE18_AUDIT_SIZE = 22_730
WAVE18_AUDIT_SHA256 = "036F8CADA0CD7C1EE1668FC438836FCFEBF505D0DA7B464BE6C1DC6DA70F2FA2"
WAVE18_MANIFEST_SIZE = 863
WAVE18_MANIFEST_SHA256 = "9D82E26D250671CFA709A0CDBB336596DBB387955B4230A14A8BE9264E6ADCB9"
EXPECTED_EVENT_STRING_COUNT = 17_916

FINAL_SHA256 = {**WAVE21_SHA256, PK_MSGEV: WAVE18_MSGEV_SHA256}
FINAL_SIZES = {**WAVE21_SIZES, PK_MSGEV: WAVE18_MSGEV_SIZE}
FINAL_CHANGED_FROM_WAVE21 = (PK_MSGEV,)


class BundleError(RuntimeError):
    """A source, profile, static-text diff, or output guard failed."""


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


def require_exact_path(path: Path, expected: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    require(resolved == expected.resolve(strict=False), f"{label} differs from its only accepted path")
    return resolved


def require_tmp(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BundleError(f"{label} must stay under {root}") from exc
    return resolved


def require_tmp_child(path: Path, label: str) -> Path:
    resolved = require_tmp(path, label)
    require(resolved != TMP_ROOT.resolve(strict=False), f"{label} must be a child of the tmp root")
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
    require(isinstance(value, dict), f"{label} JSON root is not an object")
    return value


def profile_hashes(profile: Mapping[str, bytes]) -> dict[str, str]:
    return {relative: sha256_bytes(profile[relative]) for relative in PROFILE_PATHS}


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


def relative_file_set(root: Path) -> tuple[str, ...]:
    if not root.is_dir():
        raise BundleError(f"required directory is absent: {root}")
    return tuple(sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()))


def require_file_set(root: Path, expected: tuple[str, ...], label: str) -> None:
    require(relative_file_set(root) == tuple(sorted(expected)), f"{label} file set differs")


def read_profile(
    root: Path,
    expected_hashes: Mapping[str, str],
    expected_sizes: Mapping[str, int],
    label: str,
    *,
    expected_files: tuple[str, ...] | None = None,
) -> dict[str, bytes]:
    if expected_files is not None:
        require_file_set(root, expected_files, label)
    profile: dict[str, bytes] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise BundleError(f"{label} lacks profile resource: {relative}")
        profile[relative] = path.read_bytes()
    assert_profile(profile, expected_hashes, expected_sizes, label)
    return profile


def changed_paths(before: Mapping[str, str], after: Mapping[str, str]) -> tuple[str, ...]:
    require(tuple(before) == PROFILE_PATHS, "before profile path set differs")
    require(tuple(after) == PROFILE_PATHS, "after profile path set differs")
    return tuple(relative for relative in PROFILE_PATHS if before[relative] != after[relative])


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    require(isinstance(value, dict), f"{label} is absent or not an object")
    return value


def validate_wave21_evidence(audit: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    require(
        audit.get("schema") == "nobu16.kr.pc-dialogue-quality-wave21-static-quality-audit.v1",
        "Wave 21 audit schema differs",
    )
    require(audit.get("input_sha256") == WAVE21_INPUT_SHA256, "Wave 21 audit predecessor profile differs")
    require(audit.get("target_sha256") == WAVE21_SHA256, "Wave 21 audit target profile differs")
    require(audit.get("changed_record_count") == 2, "Wave 21 audit record count differs")
    records = audit.get("records")
    require(isinstance(records, list), "Wave 21 audit records are absent")
    require([record.get("coordinate") for record in records] == ["2:249", "2:321"], "Wave 21 audit coordinates differ")
    policy = require_mapping(audit.get("source_policy"), "Wave 21 audit policy")
    require(policy.get("switch_korean_read") is False, "Wave 21 audit used Switch Korean")
    require(policy.get("steam_game_resource_written") is False, "Wave 21 audit wrote Steam")
    require(policy.get("git_operation") == "absent", "Wave 21 audit Git policy differs")
    require(policy.get("release_operation") == "absent", "Wave 21 audit release policy differs")
    require(policy.get("issue61_strdata_msgdata_preserved") is True, "Wave 21 Issue 61 retention differs")
    require(policy.get("predecessor_profile") == "wave19_private_candidate", "Wave 21 predecessor differs")
    require(policy.get("wave19_full_profile_required") is True, "Wave 21 full profile policy differs")

    require(
        manifest.get("schema") == "nobu16.kr.pc-dialogue-quality-wave21-static-quality.v1",
        "Wave 21 manifest schema differs",
    )
    require(manifest.get("candidate_only") is True, "Wave 21 candidate-only flag differs")
    require(manifest.get("profile_paths") == list(PROFILE_PATHS), "Wave 21 manifest profile differs")
    require(manifest.get("changed_paths") == [PK_MSGGAME], "Wave 21 manifest change set differs")
    require(manifest.get("coordinates") == list(WAVE21_COORDINATES), "Wave 21 manifest coordinates differ")
    require(manifest.get("record_count") == 2, "Wave 21 manifest record count differs")
    require(manifest.get("input_sha256") == WAVE21_INPUT_SHA256, "Wave 21 manifest predecessor differs")
    require(manifest.get("output_sha256") == WAVE21_SHA256, "Wave 21 manifest output differs")
    require(manifest.get("pinned_output_sha256") == WAVE21_SHA256, "Wave 21 manifest pinned output differs")
    require(manifest.get("audit_sha256") == WAVE21_AUDIT_SHA256, "Wave 21 manifest audit differs")
    require(manifest.get("issue61_strdata_msgdata_preserved") is True, "Wave 21 manifest Issue 61 retention differs")
    require(manifest.get("steam_write_capability") == "absent", "Wave 21 manifest Steam policy differs")
    require(manifest.get("git_operation") == "absent", "Wave 21 manifest Git policy differs")
    require(manifest.get("release_operation") == "absent", "Wave 21 manifest release policy differs")
    require(manifest.get("real_game_qa_required_before_release") is True, "Wave 21 real-game QA gate differs")
    require(manifest.get("transaction_id") == "pc-dialogue-quality-wave21-static-quality-v1", "Wave 21 transaction ID differs")


def validate_wave18_evidence(audit: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    require(
        audit.get("schema") == "nobu16.kr.pc-event-static-labels-wave18-audit.v1",
        "Wave 18 audit schema differs",
    )
    require(audit.get("resource") == PK_MSGEV, "Wave 18 audit resource differs")
    require(audit.get("only_changed_ids") == list(WAVE18_EVENT_IDS), "Wave 18 audit ID set differs")
    input_spec = require_mapping(audit.get("input"), "Wave 18 audit input")
    output_spec = require_mapping(audit.get("output"), "Wave 18 audit output")
    require(input_spec.get("sha256") == WAVE21_SHA256[PK_MSGEV], "Wave 18 audit input SHA-256 differs")
    require(input_spec.get("size") == WAVE21_SIZES[PK_MSGEV], "Wave 18 audit input size differs")
    require(output_spec.get("sha256") == WAVE18_MSGEV_SHA256, "Wave 18 audit output SHA-256 differs")
    require(output_spec.get("size") == WAVE18_MSGEV_SIZE, "Wave 18 audit output size differs")
    require(input_spec.get("string_count") == EXPECTED_EVENT_STRING_COUNT, "Wave 18 input string count differs")
    require(output_spec.get("string_count") == EXPECTED_EVENT_STRING_COUNT, "Wave 18 output string count differs")
    records = audit.get("records")
    require(isinstance(records, list), "Wave 18 audit records are absent")
    require([record.get("id") for record in records] == list(WAVE18_EVENT_IDS), "Wave 18 audit record order differs")
    for record in records:
        entry_id = record["id"]
        current_hash, target_hash = WAVE18_EVENT_TEXT_HASHES[entry_id]
        require(record.get("current_utf16le_sha256") == current_hash, f"Wave 18 current text hash differs: {entry_id}")
        require(record.get("target_utf16le_sha256") == target_hash, f"Wave 18 target text hash differs: {entry_id}")
        require(require_mapping(record.get("format_invariants"), f"Wave 18 format invariants {entry_id}").get("identical") is True, f"Wave 18 formatting differs: {entry_id}")
    policy = require_mapping(audit.get("source_policy"), "Wave 18 audit policy")
    require(policy.get("switch_korean_read") is False, "Wave 18 audit used Switch Korean")
    require(policy.get("steam_game_resource_written") is False, "Wave 18 audit wrote Steam")
    require(policy.get("git_operation_capability") == "absent", "Wave 18 audit Git policy differs")
    require(policy.get("steam_apply_or_transaction_capability") == "absent", "Wave 18 audit Steam policy differs")
    require(policy.get("existing_korean_translation_artifacts_read") is False, "Wave 18 audit used existing Korean artifacts")

    require(
        manifest.get("schema") == "nobu16.kr.pc-event-static-labels-wave18-manifest.v1",
        "Wave 18 manifest schema differs",
    )
    require(manifest.get("candidate_only") is True, "Wave 18 candidate-only flag differs")
    require(manifest.get("resource") == PK_MSGEV, "Wave 18 manifest resource differs")
    require(manifest.get("changed_ids") == list(WAVE18_EVENT_IDS), "Wave 18 manifest ID set differs")
    require(manifest.get("input") == {"sha256": WAVE21_SHA256[PK_MSGEV], "size": WAVE21_SIZES[PK_MSGEV]}, "Wave 18 manifest input differs")
    require(manifest.get("output") == {"sha256": WAVE18_MSGEV_SHA256, "size": WAVE18_MSGEV_SIZE}, "Wave 18 manifest output differs")
    require(manifest.get("audit_sha256") == WAVE18_AUDIT_SHA256, "Wave 18 manifest audit differs")
    require(manifest.get("switch_korean_input") == "forbidden", "Wave 18 Switch policy differs")
    require(manifest.get("steam_game_resource_write") == "absent", "Wave 18 Steam policy differs")
    require(manifest.get("steam_apply") == "not_implemented", "Wave 18 Steam apply policy differs")
    require(manifest.get("git_commit") == "not_implemented", "Wave 18 Git policy differs")
    require(manifest.get("transaction") == "not_implemented", "Wave 18 transaction policy differs")


def load_wave21_source() -> tuple[dict[str, bytes], dict[str, Any]]:
    root = require_exact_path(WAVE21_CANDIDATE_ROOT, WAVE21_CANDIDATE_ROOT, "Wave 21 candidate root")
    profile = read_profile(
        root,
        WAVE21_SHA256,
        WAVE21_SIZES,
        "Wave 21 source profile",
        expected_files=PROFILE_PATHS,
    )
    audit = read_pinned_json(
        require_exact_path(WAVE21_AUDIT_PATH, WAVE21_AUDIT_PATH, "Wave 21 audit path"),
        label="Wave 21 audit",
        expected_size=WAVE21_AUDIT_SIZE,
        expected_sha256=WAVE21_AUDIT_SHA256,
    )
    manifest = read_pinned_json(
        require_exact_path(WAVE21_MANIFEST_PATH, WAVE21_MANIFEST_PATH, "Wave 21 manifest path"),
        label="Wave 21 manifest",
        expected_size=WAVE21_MANIFEST_SIZE,
        expected_sha256=WAVE21_MANIFEST_SHA256,
    )
    validate_wave21_evidence(audit, manifest)
    return profile, {
        "candidate_root": WAVE21_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "profile_sha256": WAVE21_SHA256,
        "profile_sizes": WAVE21_SIZES,
        "audit": {"size": WAVE21_AUDIT_SIZE, "sha256": WAVE21_AUDIT_SHA256},
        "manifest": {"size": WAVE21_MANIFEST_SIZE, "sha256": WAVE21_MANIFEST_SHA256},
    }


def load_wave18_source() -> tuple[bytes, dict[str, Any]]:
    root = require_exact_path(WAVE18_CANDIDATE_ROOT, WAVE18_CANDIDATE_ROOT, "Wave 18 candidate root")
    require_file_set(root, (PK_MSGEV, "audit.v1.json", "candidate_manifest.v1.json"), "Wave 18 candidate")
    resource_path = root / PK_MSGEV
    spec = file_spec(resource_path)
    require(spec == {"size": WAVE18_MSGEV_SIZE, "sha256": WAVE18_MSGEV_SHA256}, "Wave 18 msgev differs")
    audit = read_pinned_json(
        require_exact_path(WAVE18_AUDIT_PATH, WAVE18_AUDIT_PATH, "Wave 18 audit path"),
        label="Wave 18 audit",
        expected_size=WAVE18_AUDIT_SIZE,
        expected_sha256=WAVE18_AUDIT_SHA256,
    )
    manifest = read_pinned_json(
        require_exact_path(WAVE18_MANIFEST_PATH, WAVE18_MANIFEST_PATH, "Wave 18 manifest path"),
        label="Wave 18 manifest",
        expected_size=WAVE18_MANIFEST_SIZE,
        expected_sha256=WAVE18_MANIFEST_SHA256,
    )
    validate_wave18_evidence(audit, manifest)
    return resource_path.read_bytes(), {
        "candidate_root": WAVE18_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "resource": {"size": WAVE18_MSGEV_SIZE, "sha256": WAVE18_MSGEV_SHA256},
        "audit": {"size": WAVE18_AUDIT_SIZE, "sha256": WAVE18_AUDIT_SHA256},
        "manifest": {"size": WAVE18_MANIFEST_SIZE, "sha256": WAVE18_MANIFEST_SHA256},
    }


def validate_event_static_diff(before: bytes, after: bytes) -> dict[str, Any]:
    try:
        before_header, before_raw = decompress_wrapper(before)
        after_header, after_raw = decompress_wrapper(after)
        before_table = parse_message_table(before_raw)
        after_table = parse_message_table(after_raw)
    except Exception as exc:
        raise BundleError("MSGEV source cannot be parsed as a wrapped message table") from exc
    require(before_header.prefix == after_header.prefix, "MSGEV wrapper prefix differs")
    require(rebuild_message_table(before_table, before_table.texts) == before_raw, "Wave 21 MSGEV table rebuild differs")
    require(rebuild_message_table(after_table, after_table.texts) == after_raw, "Wave 18 MSGEV table rebuild differs")
    require(before_table.string_count == EXPECTED_EVENT_STRING_COUNT, "Wave 21 MSGEV string count differs")
    require(after_table.string_count == EXPECTED_EVENT_STRING_COUNT, "Wave 18 MSGEV string count differs")
    changed_ids = tuple(
        entry_id
        for entry_id, (current, target) in enumerate(zip(before_table.texts, after_table.texts))
        if current != target
    )
    require(changed_ids == WAVE18_EVENT_IDS, f"Wave 18 MSGEV text diff differs: {changed_ids}")
    rows: list[dict[str, Any]] = []
    for entry_id in changed_ids:
        current_hash = text_hash(before_table.texts[entry_id])
        target_hash = text_hash(after_table.texts[entry_id])
        expected_current, expected_target = WAVE18_EVENT_TEXT_HASHES[entry_id]
        require(current_hash == expected_current, f"Wave 18 current text hash differs: {entry_id}")
        require(target_hash == expected_target, f"Wave 18 target text hash differs: {entry_id}")
        rows.append(
            {
                "id": entry_id,
                "current_utf16le_sha256": current_hash,
                "target_utf16le_sha256": target_hash,
            }
        )
    return {"changed_ids": list(changed_ids), "rows": rows}


def validate_final_profile(
    profile: Mapping[str, bytes],
    wave21_profile: Mapping[str, bytes],
) -> dict[str, Any]:
    assert_profile(profile, FINAL_SHA256, FINAL_SIZES, "final JP_TEXT_AUDIT profile")
    final_hashes = profile_hashes(profile)
    require(
        changed_paths(WAVE21_SHA256, final_hashes) == FINAL_CHANGED_FROM_WAVE21,
        "final profile must differ from Wave 21 only in MSGEV",
    )
    for relative in PROFILE_PATHS:
        if relative == PK_MSGEV:
            continue
        require(profile[relative] == wave21_profile[relative], f"bundle did not retain Wave 21 bytes: {relative}")
    for relative in ISSUE61_RETAINED_PATHS:
        require(profile[relative] == wave21_profile[relative], f"Issue 61 path was not retained: {relative}")
        require(final_hashes[relative] == WAVE21_SHA256[relative], f"Issue 61 SHA-256 differs: {relative}")
    event_diff = validate_event_static_diff(wave21_profile[PK_MSGEV], profile[PK_MSGEV])
    return {
        "baseline": "Wave 21 JP_TEXT_AUDIT profile",
        "changed_paths": list(FINAL_CHANGED_FROM_WAVE21),
        "retained_paths": [relative for relative in PROFILE_PATHS if relative != PK_MSGEV],
        "issue61_retained_paths": list(ISSUE61_RETAINED_PATHS),
        "per_file": [
            {
                "path": relative,
                "wave21_sha256": WAVE21_SHA256[relative],
                "final_sha256": final_hashes[relative],
                "changed_from_wave21": relative in FINAL_CHANGED_FROM_WAVE21,
            }
            for relative in PROFILE_PATHS
        ],
        "event_static_text_diff": event_diff,
    }


def build_manifest(audit: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "profile": PROFILE_NAME,
        "profile_paths": list(PROFILE_PATHS),
        "wave21_source_sha256": WAVE21_SHA256,
        "wave18_msgev_sha256": WAVE18_MSGEV_SHA256,
        "final_sha256": FINAL_SHA256,
        "final_sizes": FINAL_SIZES,
        "changed_from_wave21": list(FINAL_CHANGED_FROM_WAVE21),
        "issue61_retained_paths": list(ISSUE61_RETAINED_PATHS),
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
    """Read two pinned private sources and assemble the final profile in memory."""

    wave21_profile, wave21_evidence = load_wave21_source()
    wave18_msgev, wave18_evidence = load_wave18_source()
    final_profile = dict(wave21_profile)
    final_profile[PK_MSGEV] = wave18_msgev
    final_diff = validate_final_profile(final_profile, wave21_profile)
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "private candidate composition",
            "wave21_candidate_read": True,
            "wave18_candidate_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
            "network_operation": "absent",
        },
        "profile": PROFILE_NAME,
        "profile_paths": list(PROFILE_PATHS),
        "source_candidates": {"wave21": wave21_evidence, "wave18": wave18_evidence},
        "wave21_source_sha256": WAVE21_SHA256,
        "wave18_msgev_sha256": WAVE18_MSGEV_SHA256,
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
    resolved = require_tmp_child(path, "private cleanup")
    if resolved.exists():
        shutil.rmtree(resolved)


def write_bundle(bundle: Bundle, output_root: Path) -> dict[str, Any]:
    output_root = require_tmp_child(output_root, "candidate output")
    if output_root.exists():
        raise BundleError(f"refusing to overwrite candidate output: {output_root}")
    staging = output_root.parent / f".{output_root.name}.staging-{uuid.uuid4().hex}"
    staging = require_tmp_child(staging, "candidate staging output")
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
        staged_profile = read_profile(
            staging,
            FINAL_SHA256,
            FINAL_SIZES,
            "bundle staging profile",
            expected_files=(*PROFILE_PATHS, "audit.v1.json", "bundle_manifest.v1.json"),
        )
        staged_wave21_profile, _evidence = load_wave21_source()
        validate_final_profile(staged_profile, staged_wave21_profile)
        require(
            sha256_path(staging / "audit.v1.json") == bundle.manifest["audit_sha256"],
            "written bundle audit SHA-256 differs",
        )
        require(
            (staging / "bundle_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
            "written bundle manifest differs",
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
        "changed_from_wave21": list(FINAL_CHANGED_FROM_WAVE21),
        "steam_game_resource_write": "absent",
    }


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp_child(candidate_root, "private candidate")
    bundle = prepare_bundle()
    profile = read_profile(
        candidate_root,
        FINAL_SHA256,
        FINAL_SIZES,
        "private bundle profile",
        expected_files=(*PROFILE_PATHS, "audit.v1.json", "bundle_manifest.v1.json"),
    )
    for relative in PROFILE_PATHS:
        require(profile[relative] == bundle.profile[relative], f"private bundle bytes differ: {relative}")
    audit_path = candidate_root / "audit.v1.json"
    manifest_path = candidate_root / "bundle_manifest.v1.json"
    require(audit_path.read_bytes() == canonical_json(bundle.audit), "private bundle audit differs")
    require(manifest_path.read_bytes() == canonical_json(bundle.manifest), "private bundle manifest differs")


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True))


def command_hash(_args: argparse.Namespace) -> int:
    bundle = prepare_bundle()
    print_json(
        {
            "status": "ok",
            "profile": PROFILE_NAME,
            "changed_from_wave21": list(FINAL_CHANGED_FROM_WAVE21),
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
    hash_command = commands.add_parser("hash", help="verify sources and assemble in memory")
    hash_command.set_defaults(func=command_hash)
    build_command = commands.add_parser("build", help="write one private bundle below tmp")
    build_command.add_argument(
        "--output-root",
        type=Path,
        default=TMP_ROOT / "candidate-v1",
        help="must be a new directory below this workstream's tmp root",
    )
    build_command.set_defaults(func=command_build)
    verify_command = commands.add_parser("verify-private", help="verify a private bundle")
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
