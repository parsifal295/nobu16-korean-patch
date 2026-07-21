#!/usr/bin/env python3
"""Build the private W68 PC-only canonical PK event-title candidate.

W68 inherits the verified W67 candidate and restores katakana-only PK event
titles from Korean canonical-title anchors in the same pristine Steam PC JP
event table.  It changes only pure-static title rows: no manual line breaks,
runtime tokens, tags, opaque controls, Steam resources, Git state, network
state, or release state are touched.
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
W67_BUILDER = (
    REPO
    / "workstreams"
    / "pc_b17_static_boundary_spacing_wave67_v1"
    / "build_pc_b17_static_boundary_spacing_wave67_v1.py"
)


class Wave68Error(RuntimeError):
    """Raised when a pinned W67 source, canonical anchor, or output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave68Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave68Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w67 = load_module("pc_b17_wave67_for_wave68", W67_BUILDER)
w66 = w67.w66
BASE = w67.BASE
PK = w67.PK
MSGDATA = w67.MSGDATA
MSGEV = w67.MSGEV
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


# The title target and its canonical anchor are both rows in pristine PC JP
# msgev.bin.  The Korean target must exactly equal the currently correct PC
# Korean canonical-anchor row; no new wording is synthesized here.
TARGETS = (
    TitleTarget(14346, "미미카와노타타카이", "미미가와 전투", "ミミカワノタタカイ", 13547, "耳川の戦い", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 312),
    TitleTarget(14349, "미키캇센", "미키 합전", "ミキカッセン", 13550, "三木合戦", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 216),
    TitleTarget(14367, "노부야스지켄", "노부야스 사건", "ノブヤスジケン", 13568, "信康事件", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 312),
    TitleTarget(14369, "미쓰히데노야보", "미쓰히데의 야망", "ミツヒデノヤボウ", 13570, "光秀の野望", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 360),
    TitleTarget(14371, "혼간지타이쿄", "혼간지 퇴거", "ホンガンジタイキョ", 13572, "本願寺退去", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 264),
    TitleTarget(14372, "라이진오쓰구모노", "뇌신을 잇는 자", "ライジンヲツグモノ", 13573, "雷神を継ぐ者", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 336),
    TitleTarget(14374, "나오에케케이쇼", "나오에가 계승", "ナオエケケイショウ", 13575, "直江家継承", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 312),
    TitleTarget(14375, "덴쇼이가노란", "덴쇼 이가의 난", "テンショウイガノラン", 13576, "天正伊賀の乱", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 336),
    TitleTarget(14383, "시미즈무네하루노사이고", "시미즈 무네하루의 최후", "シミズムネハルノサイゴ", 13584, "清水宗治の最期", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 528),
    TitleTarget(14386, "야망을잇는자", "야망을 잇는 자", "ヤボウヲツグモノ", 13587, "野望を継ぐ者", "동일한 PC 정식 표제와 띄어쓰기를 일치시킨다.", 336),
    TitleTarget(14388, "사나다유키무라겐푸쿠", "사나다 유키무라 겐푸쿠", "サナダユキムラゲンプク", 13589, "真田幸村元服", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 528),
    TitleTarget(14391, "덴쇼진고의난", "덴쇼 진고의 난", "テンショウジンゴノラン", 13592, "天正壬午の乱", "동일한 PC 정식 표제와 띄어쓰기를 일치시킨다.", 336),
    TitleTarget(14392, "우에다조 지쿠조", "우에다성 축성", "ウエダジョウチクジョウ", 13593, "上田城築城", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 312),
    TitleTarget(14398, "오키타나와테노 다타카이", "오키타나와테 전투", "オキタナワテノタタカイ", 13599, "沖田畷の戦い", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 408),
    TitleTarget(14399, "에치고노 류오 구다스", "에치고의 용을 물리치다", "エチゴノリュウヲクダス", 13600, "越後の龍を下す", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 528),
    TitleTarget(14401, "마사무네토 고주로", "마사무네와 고주로", "マサムネトコジュウロウ", 13602, "政宗と小十郎", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 408),
    TitleTarget(14402, "도요히사노우이진", "도요히사의 첫 출진", "トヨヒサノウイジン", 13603, "豊久の初陣", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 432),
    TitleTarget(14403, "고마키나가쿠테전투", "고마키 나가쿠테 전투", "コマキガクテノタタカイ", 13604, "小牧長久手の戦い", "동일한 PC 정식 표제와 띄어쓰기를 일치시킨다.", 480),
    TitleTarget(14404, "데루무네토마사무네", "데루무네와 마사무네", "テルムネトマサムネ", 13605, "輝宗と政宗", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 456),
    TitleTarget(14405, "오사카조 간세이", "오사카성 완성", "オオサカジョウカンセイ", 13606, "大坂城完成", "가타카나 음역 잔재를 같은 PC 표제의 정식 한국어로 복원한다.", 312),
    TitleTarget(14621, "덴쇼진고의난", "덴쇼 진고의 난", "テンショウジンゴノラン", 13592, "天正壬午の乱", "동일한 제목 14391과 정식 PC 표제를 일치시킨다.", 336),
    TitleTarget(14622, "야망을잇는자", "야망을 잇는 자", "ヤボウヲツグモノ", 13587, "野望を継ぐ者", "동일한 제목 14386과 정식 PC 표제를 일치시킨다.", 336),
    TitleTarget(14627, "고마키나가쿠테전투", "고마키 나가쿠테 전투", "コマキガクテノタタカイ", 13604, "小牧長久手の戦い", "동일한 제목 14403과 정식 PC 표제를 일치시킨다.", 480),
)

EXPECTED_EVENT_IDS = tuple(target.entry_id for target in TARGETS)
EXPECTED_CLASS_COUNTS = {"fresh": 23, "already": 0, "override": 0}
EXPECTED_FINAL_PROFILE_DICTS: Mapping[str, Mapping[str, Any]] | None = {
    BASE: {
        "raw_sha256": "6B3777F916CBBC1138856B95BC26C21B9B746F7A6C579F47FB7083037FE13ED6",
        "raw_size": 1498552,
        "sha256": "F7E3705E421556DCF0BBF1F99562762471FA8E7563E5DFDC0F53BDDC0E24E969",
        "size": 1504454,
    },
    MSGDATA: {
        "raw_sha256": "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
        "raw_size": 495032,
        "sha256": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        "size": 496999,
    },
    MSGEV: {
        "raw_sha256": "7A5EFE1FCCEB801560D5A0C623058E763C46F285BABA480C801796E197C8D180",
        "raw_size": 990940,
        "sha256": "FD34C2FFB979E6D7E05AFC751A4E5738CEA634EF7FA7984262FE3C7539D99C08",
        "size": 994851,
    },
    PK: {
        "raw_sha256": "ADD199EA6B378F5F408497FBC544FA573118C6A4F08734EF5E165D1338500876",
        "raw_size": 1799488,
        "sha256": "06EC887CB3772D765501A5C270E6301344799585BACB47834873580CEB975747",
        "size": 1806570,
    },
}
EXPECTED_FINAL_RECORD_COUNTS: Mapping[str, int] | None = {
    BASE: 133,
    PK: 322,
    MSGDATA: 4,
    MSGEV: 234,
}
EXPECTED_FINAL_TOTAL_RECORDS: int | None = 693


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
        raise Wave68Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def target_map() -> dict[int, TitleTarget]:
    mapped = {target.entry_id: target for target in TARGETS}
    require(len(mapped) == len(TARGETS), "duplicate W68 event-title target")
    require(tuple(mapped) == EXPECTED_EVENT_IDS, "W68 event-title order or scope drift")
    return mapped


def overlay_events(
    w67_blob: bytes,
) -> tuple[bytes, dict[int, str], dict[str, tuple[int, ...]], tuple[Mapping[str, Any], ...]]:
    header, _raw, before = w66.w60.parse_table("W67 event", w67_blob)
    direct_jp_blob, _direct_profile = w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w66.w60.parse_table("pristine PC JP event", direct_jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "W67/direct-PC-JP event table length drift")
    font = w66.w64.layout.load_font()
    targets = target_map()
    effective: dict[int, str] = {}
    classes: dict[str, list[int]] = {"fresh": [], "already": [], "override": []}
    rows: list[Mapping[str, Any]] = []

    for entry_id, target in targets.items():
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        anchor_jp = direct_jp.texts[target.canonical_anchor_id]
        anchor_ko = before.texts[target.canonical_anchor_id]
        require(current == target.current_ko, f"W67 event KO preimage drift: {entry_id}")
        require(source_jp == target.direct_pc_jp, f"direct PC JP title witness drift: {entry_id}")
        require(anchor_jp == target.canonical_anchor_pc_jp, f"direct PC JP canonical anchor drift: {entry_id}")
        require(anchor_ko == target.target_ko, f"PC Korean canonical anchor drift: {entry_id}")
        source_signature = w66.static_event_signature(source_jp, entry_id, "direct PC JP title")
        require(
            w66.static_event_signature(current, entry_id, "W67 KO title") == source_signature,
            f"W67 event control/tag drift: {entry_id}",
        )
        require(
            w66.static_event_signature(target.target_ko, entry_id, "target KO title") == source_signature,
            f"W68 event control/tag drift: {entry_id}",
        )
        require(current.count("\n") == target.target_ko.count("\n") == 0, f"W68 event LF drift: {entry_id}")
        widths = w66.w64.layout.line_widths(target.target_ko, font)
        require(widths == (target.target_width_px,), f"W68 event width drift: {entry_id}: {widths}")
        require(max(widths) <= w66.w64.layout.PK_MAX_LINE_PX, f"W68 event over display gate: {entry_id}")
        if current == target.target_ko:
            classes["already"].append(entry_id)
        elif current == target.current_ko:
            classes["fresh"].append(entry_id)
            effective[entry_id] = target.target_ko
        else:
            classes["override"].append(entry_id)
        rows.append({
            "entry_id": entry_id,
            "w67_current_ko": current,
            "target_ko": target.target_ko,
            "direct_pc_jp": source_jp,
            "canonical_anchor_id": target.canonical_anchor_id,
            "canonical_anchor_pc_jp": anchor_jp,
            "canonical_anchor_ko": anchor_ko,
            "w67_current_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target.target_ko),
            "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
            "canonical_anchor_ko_utf16le_sha256": text_hash(anchor_ko),
            "source_manual_lf_count": current.count("\n"),
            "target_manual_lf_count": target.target_ko.count("\n"),
            "target_line_widths_px": list(widths),
            "control_signature": source_signature,
            "rationale": target.rationale,
        })

    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_CLASS_COUNTS,
        f"W68 event classification drift: {frozen}",
    )
    texts = list(before.texts)
    for entry_id, value in effective.items():
        texts[entry_id] = value
    raw = w66.w60.core.rebuild_message_table(before, tuple(texts))
    output = w66.w60.core.recompress_wrapper(raw, header)
    _header, output_raw, after = w66.w60.parse_table("W68 event", output)
    require(output_raw == raw, "W68 event raw mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(effective),
        "W68 event scope drift",
    )
    return output, effective, frozen, tuple(rows)


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w67.prepare(require_output_profiles=True)
    w67.verify_private_candidate(base)
    event_output, effective, classes, rows = overlay_events(base.outputs[MSGEV])
    outputs = {
        BASE: base.outputs[BASE],
        PK: base.outputs[PK],
        MSGDATA: base.outputs[MSGDATA],
        MSGEV: event_output,
    }
    require(outputs[BASE] == base.outputs[BASE], "W68 Base retention drift")
    require(outputs[PK] == base.outputs[PK], "W68 PK MSGGAME retention drift")
    require(outputs[MSGDATA] == base.outputs[MSGDATA], "W68 MSGDATA retention drift")
    profiles = {resource: w66.w61.profile(blob) for resource, blob in outputs.items()}
    w45 = w66.w62.load_w45_backups()
    base_records, _ = w66.w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _ = w66.w60.msggame_counts(w45[PK], outputs[PK])
    final_record_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w66.w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require(EXPECTED_FINAL_PROFILE_DICTS is not None, "W68 output profiles are not pinned")
        require(EXPECTED_FINAL_RECORD_COUNTS is not None, "W68 record counts are not pinned")
        require(EXPECTED_FINAL_TOTAL_RECORDS is not None, "W68 total records are not pinned")
        require(
            {resource: profile_dict(value) for resource, value in profiles.items()} == EXPECTED_FINAL_PROFILE_DICTS,
            "W68 output profile drift",
        )
        require(final_record_counts == EXPECTED_FINAL_RECORD_COUNTS, "W68 record count drift")
        require(sum(final_record_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS, "W68 total record drift")
    audit = {
        "schema": "nobu16.kr.pc-event-title-canonical-wave68-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W67 Steam-PC Korean candidate and pristine PC Japanese only",
            "canonical_korean_anchor": "same current PC event resource",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "w67_input_profiles": {resource: profile_dict(w66.w61.profile(base.outputs[resource])) for resource in ALL_RESOURCES},
        "classifications": {name: list(values) for name, values in classes.items()},
        "rows": list(rows),
        "final_record_counts": final_record_counts,
        "final_total_records": sum(final_record_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-title-canonical-wave68-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_record_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(outputs, profiles, effective, classes, rows, final_record_counts, audit, manifest)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W68 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W68 candidate staging already exists: {staging}")
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
    require(root.is_dir(), f"W68 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W68 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W68 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W68 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W68 manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_event_title_canonical_wave68_v1.py",
        WORKSTREAM / "test_pc_event_title_canonical_wave68_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W68 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W68 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
        "classifications": {name: list(values) for name, values in bundle.classifications.items()},
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
    }, ensure_ascii=False, indent=2, sort_keys=True))
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
