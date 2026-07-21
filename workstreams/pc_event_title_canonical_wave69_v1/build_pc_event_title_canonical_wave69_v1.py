#!/usr/bin/env python3
"""Build the private W69 PC-only canonical PK event-title candidate.

W69 inherits W68 and restores ten early katakana-only event titles from exact
canonical Korean-title anchors in the same Steam PC event resource.  It is a
pure-static title pass: Steam, Git, networking, release state, manual line
breaks, and message controls are outside its scope.
"""

from __future__ import annotations

import argparse
import hashlib
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
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
W68_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_title_canonical_wave68_v1"
    / "build_pc_event_title_canonical_wave68_v1.py"
)


class Wave69Error(RuntimeError):
    """Raised when a pinned W68 source, anchor, or output contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave69Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave69Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w68 = load_module("pc_event_title_wave68_for_wave69", W68_BUILDER)
w66 = w68.w66
BASE = w68.BASE
PK = w68.PK
MSGDATA = w68.MSGDATA
MSGEV = w68.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class TitleTarget:
    entry_id: int
    current_ko: str
    target_ko: str
    direct_pc_jp: str
    canonical_anchor_id: int
    canonical_anchor_pc_jp: str
    rationale: str
    target_width_px: int


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    effective: Mapping[int, str]
    classifications: Mapping[str, tuple[int, ...]]
    rows: tuple[Mapping[str, Any], ...]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


TARGETS = (
    TitleTarget(14001, "혼노지노헨", "혼노지의 변", "\u30db\u30f3\u30ce\u30a6\u30b8\u30ce\u30d8\u30f3", 13202, "\u672c\u80fd\u5bfa\u306e\u5909", "같은 PC 정식 표제 앵커로 가타카나 음역을 복원한다.", 264),
    TitleTarget(14002, "기초 혼례", "기초 혼인", "\u30ad\u30c1\u30e7\u30a6\u30b3\u30b7\u30a4\u30ec", 13203, "\u5e30\u8776\u8f3f\u5165\u308c", "같은 PC 정식 표제 앵커로 제목 용어를 복원한다.", 216),
    TitleTarget(14003, "나가시노노타타카이", "나가시노 전투", "\u30ca\u30ac\u30b7\u30ce\u30ce\u30bf\u30bf\u30ab\u30a4", 13204, "\u9577\u7be0\u306e\u6226\u3044", "같은 PC 정식 표제 앵커로 가타카나 음역을 복원한다.", 312),
    TitleTarget(14004, "가와나카지마노 다타카이", "가와나카지마 전투", "\u30ab\u30ef\u30ca\u30ab\u30b8\u30de\u30ce\u30bf\u30bf\u30ab\u30a4", 13205, "\u5ddd\u4e2d\u5cf6\u306e\u6226\u3044", "같은 PC 정식 표제 앵커로 가타카나 음역을 복원한다.", 408),
    TitleTarget(14010, "기초 혼례", "기초 혼인", "\u30ad\u30c1\u30e7\u30a6\u30b3\u30b7\u30a4\u30ec", 13211, "\u5e30\u8776\u8f3f\u5165\u308c", "동일한 제목 14002와 정식 PC 표제를 일치시킨다.", 216),
    TitleTarget(14013, "가와나카지마노 다타카이", "가와나카지마 전투", "\u30ab\u30ef\u30ca\u30ab\u30b8\u30de\u30ce\u30bf\u30bf\u30ab\u30a4", 13214, "\u5ddd\u4e2d\u5cf6\u306e\u6226\u3044", "동일한 제목 14004와 정식 PC 표제를 일치시킨다.", 408),
    TitleTarget(14014, "가네가사키 뎃타이센", "가네가사키 철수전", "\u30ab\u30cd\u30ac\u30b5\u30ad\u30c6\u30c3\u30bf\u30a4\u30bb\u30f3", 13215, "\u91d1\u30f6\u5d0e\u64a4\u9000\u6226", "같은 PC 정식 표제 앵커로 가타카나 음역을 복원한다.", 408),
    TitleTarget(14015, "히에이잔야키우치", "히에이산 방화", "\u30d2\u30a8\u30a4\u30b6\u30f3\u30e4\u30ad\u30a6\u30c1", 13216, "\u6bd4\u53e1\u5c71\u713c\u304d\u8a0e\u3061", "같은 PC 정식 표제 앵커로 가타카나 음역을 복원한다.", 312),
    TitleTarget(14016, "미카타가하라노 다타카이", "미카타가하라 전투", "\u30df\u30ab\u30bf\u30ac\u30cf\u30e9\u30ce\u30bf\u30bf\u30ab\u30a4", 13217, "\u4e09\u65b9\u30f6\u539f\u306e\u6226\u3044", "같은 PC 정식 표제 앵커로 가타카나 음역을 복원한다.", 408),
    TitleTarget(14017, "나가시노노타타카이", "나가시노 전투", "\u30ca\u30ac\u30b7\u30ce\u30ce\u30bf\u30bf\u30ab\u30a4", 13218, "\u9577\u7be0\u306e\u6226\u3044", "동일한 제목 14003과 정식 PC 표제를 일치시킨다.", 312),
)

EXPECTED_EVENT_IDS = tuple(target.entry_id for target in TARGETS)
EXPECTED_CLASS_COUNTS = {"fresh": 10, "already": 0, "override": 0}
EXPECTED_EVENT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "A9A89C0985612CEFBE05216AFF0E47BD6B5410A57429FA691C496ED73E504FA9",
    "raw_size": 990912,
    "sha256": "8B1650BBD1E83DE786E6312C009D802EB446F115B5A7B80A35339CE2EFD7E95C",
    "size": 994823,
}
EXPECTED_EVENT_RECORD_COUNT: int | None = 244
EXPECTED_TOTAL_RECORDS: int | None = 703


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w66.profile_dict(value)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave69Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def target_map() -> dict[int, TitleTarget]:
    mapped = {target.entry_id: target for target in TARGETS}
    require(len(mapped) == len(TARGETS), "duplicate W69 event-title target")
    require(tuple(mapped) == EXPECTED_EVENT_IDS, "W69 event-title order or scope drift")
    return mapped


def expected_final_profile_dicts() -> dict[str, Mapping[str, Any]]:
    require(w68.EXPECTED_FINAL_PROFILE_DICTS is not None, "W68 upstream profiles are not pinned")
    require(EXPECTED_EVENT_PROFILE is not None, "W69 event profile is not pinned")
    expected = {resource: dict(value) for resource, value in w68.EXPECTED_FINAL_PROFILE_DICTS.items()}
    expected[MSGEV] = dict(EXPECTED_EVENT_PROFILE)
    return expected


def expected_final_record_counts() -> dict[str, int]:
    require(w68.EXPECTED_FINAL_RECORD_COUNTS is not None, "W68 upstream record counts are not pinned")
    require(EXPECTED_EVENT_RECORD_COUNT is not None, "W69 event record count is not pinned")
    expected = dict(w68.EXPECTED_FINAL_RECORD_COUNTS)
    expected[MSGEV] = EXPECTED_EVENT_RECORD_COUNT
    return expected


def overlay_events(w68_blob: bytes) -> tuple[bytes, dict[int, str], dict[str, tuple[int, ...]], tuple[Mapping[str, Any], ...]]:
    header, _raw, before = w66.w60.parse_table("W68 event", w68_blob)
    direct_jp_blob, _direct_profile = w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w66.w60.parse_table("pristine PC JP event", direct_jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "W68/direct-PC-JP event table length drift")
    font = w66.w64.layout.load_font()
    effective: dict[int, str] = {}
    classes: dict[str, list[int]] = {"fresh": [], "already": [], "override": []}
    rows: list[Mapping[str, Any]] = []
    for entry_id, target in target_map().items():
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        anchor_jp = direct_jp.texts[target.canonical_anchor_id]
        anchor_ko = before.texts[target.canonical_anchor_id]
        require(current == target.current_ko, f"W68 event KO preimage drift: {entry_id}")
        require(source_jp == target.direct_pc_jp, f"direct PC JP title witness drift: {entry_id}")
        require(anchor_jp == target.canonical_anchor_pc_jp, f"direct PC JP canonical anchor drift: {entry_id}")
        require(anchor_ko == target.target_ko, f"PC Korean canonical anchor drift: {entry_id}")
        signature = w66.static_event_signature(source_jp, entry_id, "direct PC JP title")
        require(w66.static_event_signature(current, entry_id, "W68 KO title") == signature, f"W68 title control drift: {entry_id}")
        require(w66.static_event_signature(target.target_ko, entry_id, "target KO title") == signature, f"W69 title control drift: {entry_id}")
        require(current.count("\n") == target.target_ko.count("\n") == 0, f"W69 title LF drift: {entry_id}")
        widths = w66.w64.layout.line_widths(target.target_ko, font)
        require(widths == (target.target_width_px,), f"W69 title width drift: {entry_id}: {widths}")
        require(max(widths) <= w66.w64.layout.PK_MAX_LINE_PX, f"W69 title over display gate: {entry_id}")
        if current == target.target_ko:
            classes["already"].append(entry_id)
        elif current == target.current_ko:
            classes["fresh"].append(entry_id)
            effective[entry_id] = target.target_ko
        else:
            classes["override"].append(entry_id)
        rows.append({
            "entry_id": entry_id,
            "w68_current_ko": current,
            "target_ko": target.target_ko,
            "direct_pc_jp": source_jp,
            "canonical_anchor_id": target.canonical_anchor_id,
            "canonical_anchor_pc_jp": anchor_jp,
            "canonical_anchor_ko": anchor_ko,
            "w68_current_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target.target_ko),
            "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
            "canonical_anchor_ko_utf16le_sha256": text_hash(anchor_ko),
            "target_line_widths_px": list(widths),
            "control_signature": signature,
            "rationale": target.rationale,
        })
    frozen = {name: tuple(values) for name, values in classes.items()}
    require({name: len(values) for name, values in frozen.items()} == EXPECTED_CLASS_COUNTS, f"W69 event classification drift: {frozen}")
    texts = list(before.texts)
    for entry_id, value in effective.items():
        texts[entry_id] = value
    raw = w66.w60.core.rebuild_message_table(before, tuple(texts))
    output = w66.w60.core.recompress_wrapper(raw, header)
    _header, output_raw, after = w66.w60.parse_table("W69 event", output)
    require(output_raw == raw, "W69 event raw mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(effective), "W69 event scope drift")
    return output, effective, frozen, tuple(rows)


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w68.prepare(require_output_profiles=True)
    w68.verify_private_candidate(base)
    event_output, effective, classes, rows = overlay_events(base.outputs[MSGEV])
    outputs = {BASE: base.outputs[BASE], PK: base.outputs[PK], MSGDATA: base.outputs[MSGDATA], MSGEV: event_output}
    require(outputs[BASE] == base.outputs[BASE], "W69 Base retention drift")
    require(outputs[PK] == base.outputs[PK], "W69 PK MSGGAME retention drift")
    require(outputs[MSGDATA] == base.outputs[MSGDATA], "W69 MSGDATA retention drift")
    profiles = {resource: w66.w61.profile(blob) for resource, blob in outputs.items()}
    w45 = w66.w62.load_w45_backups()
    base_records, _ = w66.w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _ = w66.w60.msggame_counts(w45[PK], outputs[PK])
    final_record_counts = {BASE: base_records, PK: pk_records, MSGDATA: 4, MSGEV: w66.w60.event_count(w45[MSGEV], outputs[MSGEV])}
    if require_output_profiles:
        require({resource: profile_dict(value) for resource, value in profiles.items()} == expected_final_profile_dicts(), "W69 output profile drift")
        require(final_record_counts == expected_final_record_counts(), "W69 record count drift")
        require(EXPECTED_TOTAL_RECORDS is not None, "W69 total records are not pinned")
        require(sum(final_record_counts.values()) == EXPECTED_TOTAL_RECORDS, "W69 total record drift")
    audit = {
        "schema": "nobu16.kr.pc-event-title-canonical-wave69-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W68 Steam-PC Korean candidate and pristine PC Japanese only",
            "canonical_korean_anchor": "same current PC event resource",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "w68_input_profiles": {resource: profile_dict(w66.w61.profile(base.outputs[resource])) for resource in ALL_RESOURCES},
        "classifications": {name: list(values) for name, values in classes.items()},
        "rows": list(rows),
        "final_record_counts": final_record_counts,
        "final_total_records": sum(final_record_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-title-canonical-wave69-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {resource: {"relative": resource, "output": profile_dict(profiles[resource]), "changed_record_count": final_record_counts[resource]} for resource in ALL_RESOURCES},
        "final_total_records": sum(final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(outputs, profiles, effective, classes, rows, final_record_counts, audit, manifest)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W69 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W69 candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    bundle = bundle or prepare(require_output_profiles=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W69 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W69 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W69 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W69 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W69 manifest differs")
    return {"candidate_root": root.relative_to(REPO).as_posix(), "final_record_counts": bundle.final_record_counts, "final_total_records": sum(bundle.final_record_counts.values()), "steam_game_resource_written": False, "git_operation_performed": False, "release_published": False}


def source_whitespace_check() -> None:
    for path in (WORKSTREAM / "build_pc_event_title_canonical_wave69_v1.py", WORKSTREAM / "test_pc_event_title_canonical_wave69_v1.py", WORKSTREAM / "README_KO.md"):
        require(path.is_file(), f"W69 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W69 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({"profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()}, "classifications": {name: list(values) for name, values in bundle.classifications.items()}, "final_record_counts": bundle.final_record_counts, "final_total_records": sum(bundle.final_record_counts.values())}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=True)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_private_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
