#!/usr/bin/env python3
"""Build a private, direct-PC-only candidate for PK event record 3956.

The candidate starts from the exact installed Steam PC W45 Korean event table.
It changes one reviewed record only, writes only below its private ``tmp`` root,
and has no Steam-apply, transaction, Git, network, or release operation.
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
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_DIRNAME = "candidate"
STEAM_PK_EVENT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")
W31_WIDTH_UTILITY = (
    REPO
    / "workstreams"
    / "pc_event_quality_wave31_static_v1"
    / "build_pc_event_quality_wave31_static_v1.py"
)

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-3956-name-semantic-reflow.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-3956-name-semantic-reflow-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-3956-name-semantic-reflow-manifest.v1"
PK_MAX_LINE_PX = 912
INPUT_RECORD_COUNT = 17_916
EVENT_ID = 3956
W31_WIDTH_UTILITY_SHA256 = "71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A"


class Event3956CandidateError(RuntimeError):
    """Raised when the pinned PC input or candidate contract differs."""


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class TableResource:
    packed: bytes
    header: Any
    raw: bytes
    table: Any


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Exact installed W45 Steam PC Korean input. Any byte drift stops the build.
W45_INPUT_PROFILE = Profile(
    994_739,
    "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    990_828,
    "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
)

# Exact output of applying only TARGET to record 3956 of W45_INPUT_PROFILE.
TARGET_PROFILE = Profile(
    994_739,
    "D7CA54F9F942251B980B6D0ECC88347FAF794408EBA6AFC779B43897D6532218",
    990_828,
    "73EFCEAB8E609B0806D85CCE31E9489AFD916046BA85669F89F49CC0370C1AFB",
)

CURRENT_UTF16LE_SHA256 = "EBC680BBA570A02485D3123FD64DB69352ADD7BBFAFEAE66451F8C40C8B8F58C"
TARGET_UTF16LE_SHA256 = "F8A2A7A12F77B6A04D7EFD6AB063BFBB075B9FD02956C8E2C026D1B2D5999D5C"
TARGET_LINE_WIDTHS_PX = (840, 912, 912)

# Use actual ESC control bytes. These are not the visible six-character text
# sequence "\\x1b"; Python resolves each \x1b literal to U+001B.
TARGET = (
    "\x1bCA모토나리\x1bCZ는 몰래 \x1bCA이노우에 모토카네\x1bCZ를\n"
    "자객으로 암살해 동요한 \x1bCB이노우에 일파\x1bCZ의\n"
    "저택을 급습해 일족 30여 명을 숙청했다."
)

SEMANTIC_RETENTION_TOKENS = ("몰래", "자객", "암살", "급습", "30여 명", "숙청")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Event3956CandidateError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "size": profile.size,
        "sha256": profile.sha256,
        "raw_size": profile.raw_size,
        "raw_sha256": profile.raw_sha256,
    }


def require_profile(packed: bytes, raw: bytes, profile: Profile, label: str) -> None:
    require(len(packed) == profile.size, f"{label} packed size differs")
    require(sha256_bytes(packed) == profile.sha256, f"{label} packed SHA-256 differs")
    require(len(raw) == profile.raw_size, f"{label} raw size differs")
    require(sha256_bytes(raw) == profile.raw_sha256, f"{label} raw SHA-256 differs")


def reject_switch(path: Path, label: str) -> Path:
    """Refuse a Nintendo Switch path before it can be read."""
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Event3956CandidateError(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Event3956CandidateError(f"{label} escapes private tmp root: {resolved}") from exc
    require(resolved != root, f"{label} must be below the private tmp root")
    return resolved


def load_w45() -> TableResource:
    """Read and round-trip only the pinned Steam PC W45 event resource."""
    path = reject_switch(STEAM_PK_EVENT, "W45 Steam PC PK event input")
    packed = path.read_bytes()
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise Event3956CandidateError("W45 Steam PC PK event input cannot be parsed") from exc
    require_profile(packed, raw, W45_INPUT_PROFILE, "W45 Steam PC PK event input")
    require(len(table.texts) == INPUT_RECORD_COUNT, "W45 Steam PC record count differs")
    require(rebuild_message_table(table, table.texts) == raw, "W45 parser raw round-trip differs")
    require(recompress_wrapper(raw, header) == packed, "W45 LZ4 packed round-trip differs")
    return TableResource(packed, header, raw, table)


def load_width_utility() -> Any:
    """Import the pinned PC actual-event-font helper without opening Switch data."""
    require(W31_WIDTH_UTILITY.is_file(), "W31 actual-font utility is absent")
    require(
        sha256_path(W31_WIDTH_UTILITY) == W31_WIDTH_UTILITY_SHA256,
        "W31 actual-font utility hash differs",
    )
    spec = importlib.util.spec_from_file_location("event3956_width_utility", W31_WIDTH_UTILITY)
    if spec is None or spec.loader is None:
        raise Event3956CandidateError("cannot import W31 actual-font utility")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def control_tag_runtime_signature(width: Any, value: str) -> dict[str, Any]:
    """Immutable ESC tag, runtime, printf, C0-control, and outer-space data."""
    return dict(width.protected_nonlayout_signature(value))


def assert_no_linebreak_inside_color_span(value: str) -> None:
    """Require each color-tag span to close before a manual LF is encountered."""
    active_tag: str | None = None
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(len(token) == 3 and token[1] == "C" and token[2].isupper(), "malformed color tag")
            if token[2] == "Z":
                require(active_tag is not None, "color close without matching open")
                active_tag = None
            else:
                require(active_tag is None, "nested color tag is not expected")
                active_tag = token
            cursor += 3
            continue
        if character == "\n":
            require(active_tag is None, "manual LF is inside a color-tag span")
        cursor += 1
    require(active_tag is None, "unterminated color tag")


def ensure_semantic_contract(target: str) -> None:
    require("단숨에" not in target, "semantic compaction did not remove the permitted emphasis token")
    for token in SEMANTIC_RETENTION_TOKENS:
        require(token in target, f"semantic retention token is absent: {token}")


def prepare_candidate() -> CandidateBundle:
    current = load_w45()
    require(EVENT_ID < len(current.table.texts), "event ID 3956 is absent from W45")
    before = current.table.texts[EVENT_ID]
    require(text_hash(before) == CURRENT_UTF16LE_SHA256, "3956 W45 preimage differs")
    require(text_hash(TARGET) == TARGET_UTF16LE_SHA256, "3956 literal target differs")

    width = load_width_utility()
    advance, font = width.load_event_font()
    require(
        control_tag_runtime_signature(width, before) == control_tag_runtime_signature(width, TARGET),
        "3956 changes control/tag/runtime signature",
    )
    assert_no_linebreak_inside_color_span(TARGET)
    ensure_semantic_contract(TARGET)
    widths = width.line_widths(TARGET, advance)
    require(widths == TARGET_LINE_WIDTHS_PX, "3956 actual event-font widths differ")
    require(len(widths) == 3, "3956 must be exactly three lines")
    require(max(widths) <= PK_MAX_LINE_PX, "3956 exceeds the 912px event-line bound")

    target_texts = list(current.table.texts)
    target_texts[EVENT_ID] = TARGET
    candidate_raw = rebuild_message_table(current.table, tuple(target_texts))
    candidate_packed = recompress_wrapper(candidate_raw, current.header)
    require_profile(candidate_packed, candidate_raw, TARGET_PROFILE, "3956 candidate target")
    try:
        decoded_header, decoded_raw = decompress_wrapper(candidate_packed)
        decoded_table = parse_message_table(decoded_raw)
    except Exception as exc:
        raise Event3956CandidateError("3956 candidate cannot be parsed after LZ4 wrapping") from exc
    require(decoded_raw == candidate_raw, "3956 candidate decompressed raw differs")
    require(rebuild_message_table(decoded_table, decoded_table.texts) == decoded_raw, "3956 candidate parser raw round-trip differs")
    require(recompress_wrapper(decoded_raw, decoded_header) == candidate_packed, "3956 candidate LZ4 packed round-trip differs")
    changed_ids = [
        entry_id
        for entry_id, (source, candidate) in enumerate(zip(current.table.texts, decoded_table.texts))
        if source != candidate
    ]
    require(changed_ids == [EVENT_ID], "3956 candidate changed ID scope differs")
    require(decoded_table.texts[EVENT_ID] == TARGET, "3956 candidate target record differs")

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "source_baseline": "installed_W45_MSG_PK/JP/msgev.bin",
            "switch_path_or_file_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "input": {
            "relative": "MSG_PK/JP/msgev.bin",
            **profile_dict(W45_INPUT_PROFILE),
            "record_count": INPUT_RECORD_COUNT,
        },
        "target": {
            "relative": "MSG_PK/JP/msgev.bin",
            **profile_dict(TARGET_PROFILE),
        },
        "font": dict(font),
        "pk_max_line_px": PK_MAX_LINE_PX,
        "changed_record_count": 1,
        "changed_ids": [EVENT_ID],
        "records": [
            {
                "id": EVENT_ID,
                "current_utf16le_sha256": CURRENT_UTF16LE_SHA256,
                "target_utf16le_sha256": TARGET_UTF16LE_SHA256,
                "target_line_widths_px": list(widths),
                "control_tag_runtime_signature_identical": True,
                "manual_lf_inside_color_tag_span": False,
                "semantic_compaction": {
                    "omitted_lexeme_only": "단숨에",
                    "reason": "three-line actual PC event-font fit at 912px maximum",
                    "retained": ["몰래", "자객", "암살", "급습", "일족 30여 명", "숙청"],
                },
                "rationale": "이노에→이노우에 표기 교정과 3줄 재구성. 삭제한 어휘는 속도 강조어 ‘단숨에’뿐이다.",
            }
        ],
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": {
            "relative": "MSG_PK/JP/msgev.bin",
            "input": profile_dict(W45_INPUT_PROFILE),
            "output": profile_dict(TARGET_PROFILE),
            "changed_ids": [EVENT_ID],
        },
        "changed_record_count": 1,
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(candidate_packed, candidate_raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(not output.exists(), f"candidate output already exists: {output}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = require_private(Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT)), "candidate staging output")
    try:
        resource_path = stage / "MSG_PK" / "JP" / "msgev.bin"
        resource_path.parent.mkdir(parents=True, exist_ok=True)
        resource_path.write_bytes(bundle.packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(stage, output)
    finally:
        if stage.exists():
            require_private(stage, "candidate staging cleanup")
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(output.is_dir(), "private candidate is absent")
    expected_files = {
        "MSG_PK/JP/msgev.bin",
        "audit.v1.json",
        "candidate_manifest.v1.json",
    }
    actual_files = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    require(actual_files == expected_files, "private candidate file set differs")
    require((output / "MSG_PK" / "JP" / "msgev.bin").read_bytes() == bundle.packed, "private event candidate differs")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require(
        (output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "private manifest differs",
    )
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_ids": [EVENT_ID],
        "candidate_sha256": TARGET_PROFILE.sha256,
        "steam_game_resource_written": False,
    }


def private_diff_check() -> dict[str, Any]:
    """Check only this private workstream; this deliberately does not use Git."""
    result = verify_private()
    authoring_files = (
        SCRIPT,
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "test_pc_event_3956_name_semantic_reflow_v1.py",
    )
    for path in authoring_files:
        text = path.read_text(encoding="utf-8")
        require("\r" not in text, f"{path.name} contains CR line endings")
        require(
            all(not line.endswith((" ", "\t")) for line in text.splitlines()),
            f"{path.name} contains trailing whitespace",
        )
    result["private_authoring_whitespace_check"] = "passed"
    result["git_used"] = False
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private", "diff-check"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result: dict[str, Any] = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_ids": [EVENT_ID],
            "candidate_sha256": TARGET_PROFILE.sha256,
            "steam_game_resource_written": False,
        }
    elif args.command == "verify-private":
        result = verify_private()
    else:
        result = private_diff_check()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
