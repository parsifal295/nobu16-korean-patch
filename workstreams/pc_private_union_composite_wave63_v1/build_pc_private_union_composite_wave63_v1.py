#!/usr/bin/env python3
"""Build the private W63 overlay from W62 direct-PC corrections.

W63 fixes only literals proven safe without runtime-name interpretation:
ten dialogue literals (one Base, nine PK) and four event literals.  It reads W62's private
candidate and pristine PC Japanese data, then writes only under its own tmp
directory.  It has no Steam-apply, Git, or network capability.
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
CANDIDATE_ROOT = TMP_ROOT / "candidate"
W62_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave62_v1"
    / "build_pc_private_union_composite_wave62_v1.py"
)
EVENT_LAYOUT_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_reflow_static_batch_d_candidate_v1"
    / "build_pc_event_reflow_static_batch_d_candidate_v1.py"
)


class Wave63Error(RuntimeError):
    """Raised when a pinned source or W63 output contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave63Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave63Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w62 = load_module("pc_private_union_wave62_for_wave63", W62_BUILDER)
layout = load_module("pc_event_layout_for_wave63", EVENT_LAYOUT_BUILDER)
w61 = w62.w61
w60 = w62.w60
w59 = w62.w59

BASE = w62.BASE
PK = w62.PK
MSGDATA = w62.MSGDATA
MSGEV = w62.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class DialogueTarget:
    resource: str
    coordinate: tuple[int, int, int]
    current_ko: str
    target_ko: str
    pc_jp: str
    rationale: str

    @property
    def coordinate_text(self) -> str:
        return ":".join(str(value) for value in self.coordinate)


@dataclass(frozen=True)
class EventTarget:
    entry_id: int
    current_ko: str
    target_ko: str
    pc_jp: str
    rationale: str
    expected_line_widths: tuple[int, ...]


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    dialogue_effective: Mapping[tuple[str, int, int, int], str]
    dialogue_classifications: Mapping[str, tuple[tuple[str, int, int, int], ...]]
    event_effective: Mapping[int, str]
    event_classifications: Mapping[str, tuple[int, ...]]
    event_line_widths: Mapping[int, tuple[int, ...]]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


REINFORCEMENT_CURRENT = "입니다\n전력은 서로 대등하니\n원군을 보낼 아군을 늘리는 게 어떻겠습니까?"
REINFORCEMENT_TARGET = "입니다\n전력은 서로 대등하니\n원군을 청할 아군을 늘리는 게 어떻겠습니까?"
REINFORCEMENT_JP = "が目標となりますが\nお互いの戦力は拮抗しています\n援軍を頼める味方を増やしてはどうでしょう"

DIALOGUE_TARGETS = (
    *(
        DialogueTarget(
            PK,
            (6, record_id, 1),
            REINFORCEMENT_CURRENT,
            REINFORCEMENT_TARGET,
            REINFORCEMENT_JP,
            "원군을 보내는 쪽이 아니라 원군을 청할 동맹국을 늘리는 문맥이다.",
        )
        for record_id in (1230, 1231, 1232, 1234, 1235, 1236, 1237, 1238)
    ),
    DialogueTarget(
        BASE,
        (9, 3622, 1),
        "의 모계에 미혹되어라!",
        "의 계략에 미혹되어라!",
        "の謀計に惑うがよいわ！",
        "謀計는 혈통 모계가 아니라 계략이다.",
    ),
    DialogueTarget(
        PK,
        (9, 3867, 1),
        "의 모계에 미혹되어라!",
        "의 계략에 미혹되어라!",
        "の謀計に惑うがよいわ！",
        "謀計는 혈통 모계가 아니라 계략이다.",
    ),
)

EVENT_TARGETS = (
    EventTarget(
        4960,
        "\x1bCB[bs1871]\x1bCZ의 당주인 당신은\n"
        "\x1bCB이마가와\x1bCZ 인질이 아니다. \x1bCA요시모토\x1bCZ 사후,\n"
        "\x1bCB[bs1871]\x1bCZ는 \x1bCB해방됐다\x1bCZ.",
        "당신은 본래 \x1bCB[bs1871]\x1bCZ의 당주…\n"
        "\x1bCB이마가와\x1bCZ 인질이 아니다. \x1bCA요시모토\x1bCZ 사후,\n"
        "\x1bCB[bs1871]\x1bCZ는 \x1bCB이마가와\x1bCZ의 속박을 벗었다.",
        "あなた様は本来、\x1bCB[bs1871]\x1bCZの当主…\x1bCB今川\x1bCZの人質\n"
        "ではござらぬ。\x1bCA義元\x1bCZ様が討たれた今、\x1bCB[bs1871]\x1bCZは\n"
        "\x1bCB今川\x1bCZの軛より放たれたのでございます。",
        "색상 태그가 ‘해방됐다’를 감싸던 오류를 가문명 이마가와로 되돌리고 원문 의미를 복원한다.",
        (696, 912, 864),
    ),
    EventTarget(
        10386,
        "급히 알려 드립니다. \x1bCC내대신\x1bCZ께서\n"
        "\x1bCA세키가하라\x1bCZ에서 대승을 거두셨습니다.",
        "급히 알려 드립니다. \x1bCC세키가하라\x1bCZ에서\n"
        "\x1bCA내대신\x1bCZ께서 대승을 거두셨습니다.",
        "取り急ぎ、お知らせいたします。\n\x1bCC関ヶ原\x1bCZにて、\x1bCA内府\x1bCZが大勝いたしました。",
        "CC 지명과 CA 인물 태그의 대상이 뒤바뀐 오류를 원문 순서로 복원한다.",
        (816, 744),
    ),
    EventTarget(
        10483,
        "\x1bCB나이후\x1bCZ 님께서는 \x1bCB우에스기\x1bCZ와 맺은\n"
        "\x1bCB다테\x1bCZ의 맹약을 깨고 \x1bCA우에스기\x1bCZ\n"
        "영지를 공격하라고 하신 것이로군.",
        "그리고 \x1bCB다테\x1bCZ는 \x1bCB우에스기\x1bCZ와의 맹약을 깨고\n"
        "\x1bCB우에스기\x1bCZ 영지를 공격하라고 \x1bCA내대신\x1bCZ께서\n"
        "말씀하신 것이로군.",
        "そして\x1bCB伊達\x1bCZは\x1bCB上杉\x1bCZとの盟約を破り\n"
        "\x1bCB上杉\x1bCZ領へ攻めかかれと\n\x1bCA内府\x1bCZ殿はそう言っているのだな。",
        "가문·세력·인물 태그 네 개의 대상과 발화 주체를 원문 구조로 복원한다.",
        (912, 888, 432),
    ),
    EventTarget(
        10484,
        "그렇습니다. \x1bCB나이후\x1bCZ 님께서는\n"
        "빼앗은 땅을 \x1bCA다테\x1bCZ의 영지로\n"
        "삼아도 좋다고 보증하셨습니다.",
        "그렇습니다. 빼앗은 땅을\n"
        "\x1bCB다테\x1bCZ의 영지로 삼아도 좋다고\n"
        "\x1bCA내대신\x1bCZ께서 보증하셨습니다.",
        "左様にござりまする。\n奪った地は\x1bCB伊達\x1bCZの所領にしてもよいと\n"
        "\x1bCA内府\x1bCZ殿よりお墨付きもございます。",
        "가문 태그와 인물 태그가 서로 뒤바뀐 문장을 원문 구조로 복원한다.",
        (552, 648, 624),
    ),
)

EXPECTED_FINAL_PROFILE_DICTS: dict[str, dict[str, Any]] | None = {
    BASE: {
        "raw_sha256": "7DA010184830AC83600F6DC301BBF134D6F8CAC9A5CE3818BDB4A3246E2F4A63",
        "raw_size": 1498548,
        "sha256": "02C8B0F0A175B85BDE223355620124DF5DC07B20FE804D26212E10C307D7C099",
        "size": 1504450,
    },
    PK: {
        "raw_sha256": "EBE0BB1F7440963300B225DC18B31281382A6A988B1A65875EC14A5F177D4056",
        "raw_size": 1799448,
        "sha256": "FC28D8394D40C5EF45D3BFCEF7161E05B6536B1874AAE90BA8ED14C99F28B351",
        "size": 1806530,
    },
    MSGDATA: {
        "raw_sha256": "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
        "raw_size": 495032,
        "sha256": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        "size": 496999,
    },
    MSGEV: {
        "raw_sha256": "85EB4267650296C950FAC9CE2A61711A55B9BD50814EA4ABD5D3F6DA9397B428",
        "raw_size": 990844,
        "sha256": "14A8042D6DA2A7EFF350BD9B62536B72889C9808FF0110F53F35E07547066DC2",
        "size": 994755,
    },
}
EXPECTED_FINAL_RECORD_COUNTS = {BASE: 109, PK: 282, MSGDATA: 4, MSGEV: 139}
EXPECTED_FINAL_TOTAL_RECORDS = 534
EXPECTED_DIALOGUE_CLASSES = {"fresh": 10, "already": 0, "override": 0}
EXPECTED_DIALOGUE_CLASSES_BY_RESOURCE = {
    BASE: {"fresh": 1, "already": 0, "override": 0},
    PK: {"fresh": 9, "already": 0, "override": 0},
}
EXPECTED_EVENT_CLASSES = {"fresh": 4, "already": 0, "override": 0}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w62.profile_dict(value)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave63Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def parse_msggame(blob: bytes, label: str) -> Any:
    return w59.assert_archive_parse_roundtrip(label, blob)


def literal_at(archive: Any, coordinate: tuple[int, int, int], label: str) -> str:
    return w61.literal_at(archive, coordinate, label)


def dialogue_target_map(resource: str) -> dict[tuple[int, int, int], DialogueTarget]:
    require(resource in (BASE, PK), f"unsupported W63 dialogue resource: {resource}")
    selected = tuple(target for target in DIALOGUE_TARGETS if target.resource == resource)
    mapped = {target.coordinate: target for target in selected}
    require(len(mapped) == len(selected), f"duplicate W63 dialogue target coordinate: {resource}")
    return mapped


def event_target_map() -> dict[int, EventTarget]:
    mapped = {target.entry_id: target for target in EVENT_TARGETS}
    require(len(mapped) == len(EVENT_TARGETS), "duplicate W63 event target ID")
    return mapped


def overlay_dialogue(
    resource: str,
    w62_blob: bytes,
) -> tuple[bytes, dict[tuple[int, int, int], str], dict[str, tuple[tuple[int, int, int], ...]]]:
    before = parse_msggame(w62_blob, f"W62 {resource}")
    jp = w61.load_direct_jp(resource)
    effective: dict[tuple[int, int, int], str] = {}
    classes: dict[str, list[tuple[int, int, int]]] = {"fresh": [], "already": [], "override": []}
    for coordinate, target in sorted(dialogue_target_map(resource).items()):
        current = literal_at(before, coordinate, f"W62 {resource}")
        source_jp = literal_at(jp, coordinate, f"pristine PC JP {resource}")
        require(source_jp == target.pc_jp, f"direct PC JP dialogue evidence drift: {coordinate}")
        require(
            w61.literal_signature(target.current_ko) == w61.literal_signature(target.target_ko),
            f"manual LF/control drift: {coordinate}",
        )
        if current == target.target_ko:
            classes["already"].append(coordinate)
        elif current == target.current_ko:
            classes["fresh"].append(coordinate)
            effective[coordinate] = target.target_ko
        else:
            raise Wave63Error(f"W62 dialogue KO preimage drift: {coordinate}")
    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_DIALOGUE_CLASSES_BY_RESOURCE[resource],
        f"W63 dialogue classification drift: {resource}: {frozen}",
    )
    output = w59.rebuild_packed_with_literals(w62_blob, effective)
    after = parse_msggame(output, f"W63 {resource}")
    w59.assert_same_literal_topology_and_skeleton(f"W62-to-W63 {resource}", before, after)
    before_records = w59.archive_records(before)
    after_records = w59.archive_records(after)
    before_texts = w59.literal_texts(before)
    after_texts = w59.literal_texts(after)
    require(
        {coordinate for coordinate in before_texts if before_texts[coordinate] != after_texts[coordinate]} == set(effective),
        "W63 dialogue literal scope drift",
    )
    require(
        {key for key in before_records if before_records[key].data != after_records[key].data}
        == {(block, record) for block, record, _literal in effective},
        "W63 dialogue record scope drift",
    )
    return output, effective, frozen


def event_control_signature(value: str) -> dict[str, Any]:
    return dict(layout.control_signature(value))


def overlay_event(
    w62_blob: bytes,
) -> tuple[bytes, dict[int, str], dict[str, tuple[int, ...]], dict[int, tuple[int, ...]], list[dict[str, Any]]]:
    header, _raw, before = w60.parse_table("W62 event", w62_blob)
    direct_jp_blob, _direct_jp_profile = w62.load_direct_jp_event()
    _jp_header, _jp_raw, jp = w60.parse_table("pristine PC JP event", direct_jp_blob)
    require(len(before.texts) == len(jp.texts), "event table topology drift")
    font = layout.load_font()
    effective: dict[int, str] = {}
    classes: dict[str, list[int]] = {"fresh": [], "already": [], "override": []}
    widths: dict[int, tuple[int, ...]] = {}
    rows: list[dict[str, Any]] = []
    for entry_id, target in sorted(event_target_map().items()):
        current = before.texts[entry_id]
        source_jp = jp.texts[entry_id]
        require(source_jp == target.pc_jp, f"direct PC JP event evidence drift: {entry_id}")
        current_controls = event_control_signature(target.current_ko)
        target_controls = event_control_signature(target.target_ko)
        jp_controls = event_control_signature(target.pc_jp)
        require(current_controls == target_controls == jp_controls, f"event control/tag drift: {entry_id}")
        line_widths = layout.line_widths(target.target_ko, font)
        require(line_widths == target.expected_line_widths, f"event width drift: {entry_id}")
        require(1 <= len(line_widths) <= layout.MAX_LINES, f"event line count drift: {entry_id}")
        require(max(line_widths, default=0) <= layout.PK_MAX_LINE_PX, f"event line width drift: {entry_id}")
        if current == target.target_ko:
            classes["already"].append(entry_id)
        elif current == target.current_ko:
            classes["fresh"].append(entry_id)
            effective[entry_id] = target.target_ko
        else:
            raise Wave63Error(f"W62 event KO preimage drift: {entry_id}")
        widths[entry_id] = line_widths
        rows.append({
            "entry_id": entry_id,
            "current_ko": current,
            "target_ko": target.target_ko,
            "pc_jp": source_jp,
            "rationale": target.rationale,
            "control_signature": target_controls,
            "line_widths_px": list(line_widths),
        })
    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_EVENT_CLASSES,
        f"W63 event classification drift: {frozen}",
    )
    texts = list(before.texts)
    for entry_id, target in effective.items():
        texts[entry_id] = target
    raw = w60.core.rebuild_message_table(before, tuple(texts))
    output = w60.core.recompress_wrapper(raw, header)
    _output_header, output_raw, after = w60.parse_table("W63 event", output)
    require(output_raw == raw, "W63 event raw mismatch")
    changed = {index for index, value in enumerate(before.texts) if value != after.texts[index]}
    require(changed == set(effective), f"W63 event scope drift: {sorted(changed)}")
    return output, effective, frozen, widths, rows


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w62.prepare(require_output_profiles=True)
    w62.verify_private_candidate(base)
    base_output, base_dialogue_effective, base_dialogue_classes = overlay_dialogue(
        BASE,
        base.outputs[BASE],
    )
    pk_output, pk_dialogue_effective, pk_dialogue_classes = overlay_dialogue(
        PK,
        base.outputs[PK],
    )
    dialogue_effective = {
        (resource, *coordinate): text
        for resource, effective in ((BASE, base_dialogue_effective), (PK, pk_dialogue_effective))
        for coordinate, text in effective.items()
    }
    dialogue_classifications = {
        name: tuple(
            (resource, *coordinate)
            for resource, classes in ((BASE, base_dialogue_classes), (PK, pk_dialogue_classes))
            for coordinate in classes[name]
        )
        for name in ("fresh", "already", "override")
    }
    event_output, event_effective, event_classifications, event_line_widths, event_rows = overlay_event(
        base.outputs[MSGEV]
    )
    outputs = {
        BASE: base_output,
        PK: pk_output,
        MSGDATA: base.outputs[MSGDATA],
        MSGEV: event_output,
    }
    profiles = {resource: w62.w61.profile(blob) for resource, blob in outputs.items()}
    w45 = w62.load_w45_backups()
    base_records, _base_literals = w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _pk_literals = w60.msggame_counts(w45[PK], outputs[PK])
    final_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require(EXPECTED_FINAL_PROFILE_DICTS is not None, "W63 output profile constants are not pinned")
        require(
            {resource: profile_dict(value) for resource, value in profiles.items()} == EXPECTED_FINAL_PROFILE_DICTS,
            "W63 output profile drift",
        )
        require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, "W63 final record count drift")
        require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS, "W63 final total drift")
    dialogue_rows = [
        {
            "resource": target.resource,
            "slot": target.coordinate_text,
            "current_ko": target.current_ko,
            "target_ko": target.target_ko,
            "pc_jp": target.pc_jp,
            "rationale": target.rationale,
            "manual_lf_count": target.current_ko.count("\n"),
        }
        for target in DIALOGUE_TARGETS
    ]
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave63-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W62 Steam-PC Korean candidate and pristine PC Japanese only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "base_w62": {resource: profile_dict(w62.w61.profile(base.outputs[resource])) for resource in ALL_RESOURCES},
        "direct_jp": {
            BASE: profile_dict(w61.JP_SOURCES[BASE].profile),
            PK: profile_dict(w61.JP_SOURCES[PK].profile),
            MSGEV: w62.load_direct_jp_event()[1],
        },
        "dialogue_target_rows": dialogue_rows,
        "dialogue_classifications": {
            name: [list(value) for value in coordinates]
            for name, coordinates in dialogue_classifications.items()
        },
        "event_target_rows": event_rows,
        "event_classifications": {name: list(value) for name, value in event_classifications.items()},
        "w62_to_w63_changed_literals": {
            BASE: len(base_dialogue_effective),
            PK: len(pk_dialogue_effective),
        },
        "w62_to_w63_changed_event_rows": len(event_effective),
        "final_record_counts": final_counts,
        "final_total_records": sum(final_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave63-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(
        outputs,
        profiles,
        dialogue_effective,
        dialogue_classifications,
        event_effective,
        event_classifications,
        event_line_widths,
        final_counts,
        audit,
        manifest,
    )


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W63 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W63 candidate staging already exists: {staging}")
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
    require(root.is_dir(), f"W63 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W63 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W63 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W63 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W63 manifest differs")
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
        WORKSTREAM / "build_pc_private_union_composite_wave63_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave63_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W63 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W63 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
        "dialogue_classifications": {
            name: [list(value) for value in coordinates]
            for name, coordinates in bundle.dialogue_classifications.items()
        },
        "event_classifications": {name: list(value) for name, value in bundle.event_classifications.items()},
        "event_line_widths": {str(entry_id): list(widths) for entry_id, widths in bundle.event_line_widths.items()},
        "w62_to_w63_changed_literals": {
            BASE: sum(1 for resource, *_coordinate in bundle.dialogue_effective if resource == BASE),
            PK: sum(1 for resource, *_coordinate in bundle.dialogue_effective if resource == PK),
        },
        "w62_to_w63_changed_event_rows": len(bundle.event_effective),
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
