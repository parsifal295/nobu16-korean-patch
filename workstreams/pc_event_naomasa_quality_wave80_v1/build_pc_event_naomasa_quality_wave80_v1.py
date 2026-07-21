#!/usr/bin/env python3
"""Build the W80 Naomasa event-quality candidate from strict on-disk W79."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
W79_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_otate_quality_wave79_v1"
    / "build_pc_event_otate_quality_wave79_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(7_675, 7_714))
CHANGED_IDS = (
    7_675,
    7_676,
    7_677,
    7_679,
    7_680,
    7_682,
    7_683,
    7_684,
    7_685,
    7_688,
    7_690,
    7_691,
    7_692,
    7_693,
    7_695,
    7_696,
    7_699,
    7_703,
    7_706,
    7_707,
    7_710,
    7_711,
    7_712,
    7_713,
)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W79_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "6A04C331F21F01D29402153D2DDD30F26678049DA9B25E804A6EA9FFE96A27DE",
    "raw_size": 993_488,
    "sha256": "0740190230C2C2771CB4FAEEB9231E4DC0FE1A4127784A3FA84C511D1153804A",
    "size": 997_409,
}

# Pinned from the single read-only W80 profile pass before the only candidate write.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "1F70E64756B4EF214734245D85A93328753EAA8B47DA247F915F6707C0EE5EA5",
    "raw_size": 993_952,
    "sha256": "0553580CE8F5A0274D6DD792A23F9D3BBD48960820F0931C920962B6E039B08C",
    "size": 997_875,
}

# Scene-limited conservative layout reservations.  They are not claimed as
# observations of a live runtime substitution.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[b1871]": {
        "display": "마쓰다이라 모토야스",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W79 slot 1871; conservative historical full-name reservation",
    },
    "[bm1871]": {
        "display": "마쓰다이라 모토야스",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W79 slot 1871; conservative historical full-name reservation",
    },
    "[bs1871]": {
        "display": "마쓰다이라",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W79 slot 1871; conservative surname reservation",
    },
    "[bm1251]": {
        "display": "다케다 하루노부",
        "source_slot_id": 1251,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W79 slot 1251; conservative historical full-name reservation",
    },
    "[b1448]": {
        "display": "나가오 가게토라",
        "source_slot_id": 1448,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W79 slot 1448; conservative historical full-name reservation",
    },
    "[bm1448]": {
        "display": "나가오 가게토라",
        "source_slot_id": 1448,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W79 slot 1448; conservative historical full-name reservation",
    },
}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    7675: (
        f"{E}CB[bs1871]{E}CZ의 가신인 {E}CA이이 나오마사{E}CZ는\n"
        "지략과 용맹이 뛰어난 명장이었으나,\n"
        "그 격한 성격이 화를 불러왔는지,"
    ),
    7676: (
        "신하의 사소한 잘못도 그냥 넘기지 못하고\n"
        "곧바로 베어 죽였기에,\n"
        f"'사람 베는 {E}CA효부{E}CZ'라 불렸다."
    ),
    7677: (
        f"특히 {E}CA[bm1871]{E}CZ 휘하에 들어온\n"
        f"옛 {E}CB다케다{E}CZ 가신들은 {E}CA나오마사{E}CZ를 두려워해,\n"
        f"{E}CA[bm1871]{E}CZ에게 어떻게든 이 일을\n"
        "해결해 달라고 호소했다."
    ),
    7679: (
        "으으음… 곤란하구나.\n"
        f"{E}CA나오마사{E}CZ는 반드시 천하의 명장이 될\n"
        "사내다. 하찮은 일로 그 마음을 꺾고\n"
        "싶지는 않다."
    ),
    7680: (
        "허나 사람들 사이에 화합이 없다면\n"
        f"{E}CA나오마사{E}CZ도 장수로서 명성을 떨치기는\n"
        "어려울 것이옵니다…"
    ),
    7682: (
        f"{E}CB다케다{E}CZ를 섬겼던 자들은\n"
        f"{E}CA나오마사{E}CZ에게 호적수를 두게 하는 것이\n"
        "좋겠다고 아뢰고 있습니다."
    ),
    7683: f"흠?\n{E}CA나오마사{E}CZ와 경쟁할 상대란 말인가.",
    7684: (
        f"예, {E}CB다케다{E}CZ 사람들이 말하기를\n"
        f"그 {E}CA[bm1251]{E}CZ 공도 늘\n"
        f"{E}CA[b1448]{E}CZ 공을 훌륭한 적수로\n"
        "인정하셨다고 합니다."
    ),
    7685: (
        f"어느 때라도 {E}CA[bm1448]{E}CZ 공에게\n"
        "뒤지지 않도록 정진했기에,\n"
        f"{E}CA[bm1251]{E}CZ 공은 중요한 전투에서\n"
        "크게 패한 적이 없었다고 합니다."
    ),
    7688: "있지 않은가!\n다름 아닌 우리 가신들 중에\n걸맞은 자가 말일세.",
    7690: (
        f"{E}CA혼다 헤이하치로 다다카쓰{E}CZ.\n"
        "나아가든 물러서든 천하에 그를\n"
        "당할 자 없는 고금무쌍의 명장이란,\n"
        f"바로 {E}CA다다카쓰{E}CZ를 두고 하는 말일세!"
    ),
    7691: (
        f"{E}CA나오마사{E}CZ에게 앞으로\n"
        f"{E}CA다다카쓰{E}CZ를 본보기이자 숙적으로 삼아\n"
        "정진하라고 전하라."
    ),
    7692: (
        f"훗날 {E}CA이이 나오마사{E}CZ는\n"
        f"{E}CB도쿠가와{E}CZ 사천왕 가운데서도 가장 높은\n"
        "녹봉을 받는 지위에까지 오른다."
    ),
    7693: (
        f"이것이 {E}CA다다카쓰{E}CZ를 경쟁 상대로 삼은\n"
        "효과인지는 확실하지 않으나…"
    ),
    7695: (
        f"{E}CB다케다 가문{E}CZ의 옛 영지인 {E}CC가이{E}CZ·{E}CC시나노{E}CZ를\n"
        f"영토에 더한 {E}CA[b1871]{E}CZ는\n"
        f"정예 {E}CB다케다{E}CZ군을 지탱하던 뛰어난 인재를\n"
        "확보하기 시작했다."
    ),
    7696: (
        f"그 {E}CB다케다 가문{E}CZ 옛 가신들을 통솔할 인물로\n"
        f"{E}CA[bm1871]{E}CZ가 눈여겨본 이는\n"
        "성장이 눈부신 젊은 무사\n"
        f"{E}CA이이 나오마사{E}CZ였다."
    ),
    7699: (
        f"무서운 싸움이었다…그 {E}CA야마가타{E}CZ에게\n"
        "쫓겼을 때는 살아 있는 심정이 아니었다…\n"
        "그러니, 어쩔 수 없었던 게야…"
    ),
    7703: (
        f"그들을 {E}CB[bs1871]{E}CZ의 가신으로 맞아들여\n"
        f"{E}CB다케다{E}CZ의 피로 {E}CB[bs1871]{E}CZ를 강하게\n"
        "만든다."
    ),
    7706: (
        "적이었던 우리를 반기지 않는 자도 많겠지.\n"
        f"허나 {E}CA[bm1251]{E}CZ를 받들어 싸운\n"
        "그들의 기술과 지혜는 반드시\n"
        "우리에게 도움이 될 것이다."
    ),
    7707: (
        "맡겨 주시오.\n"
        f"반드시 그들을 {E}CB[bs1871]{E}CZ의 첨병으로\n"
        "단련해 보이겠나이다."
    ),
    7710: (
        "그래, 붉은 군장을 그대가 잇는 것이다.\n"
        f"천하무쌍 {E}CB다케다{E}CZ의 붉은 군장은\n"
        f"{E}CB이이{E}CZ의 붉은 군장으로\n"
        "다시 태어나는 것이다!"
    ),
    7711: (
        f"{E}CA[bm1871]{E}CZ가 {E}CB다케다 가문{E}CZ의\n"
        f"옛 가신들 처우를 {E}CA나오마사{E}CZ에게 맡긴 것은\n"
        f"급격히 출세한 그에게 {E}CC미카와{E}CZ의\n"
        "확고한 기반이 없었기 때문이기도 하나…"
    ),
    7712: (
        "휘하를 엄히 단련하기로 정평이 난\n"
        f"{E}CA나오마사{E}CZ가, 옛 적이자 기개 있는\n"
        f"{E}CC고슈{E}CZ 병사를 다루기에 적임이었다는\n"
        "이유도 있었다."
    ),
    7713: "그 엄격함은 또 다른 문제를 낳게 되지만…\n그것은 또 훗날의 이야기다.",
}

RATIONALES: Mapping[int, str] = {
    7675: "지략·용맹·명장과 격한 성격의 인과를 자연스러운 한국어로 복원",
    7676: "인물 별칭을 보존하고 따옴표 내부가 분리되지 않도록 재배치",
    7677: "옛 다케다 가신의 공포와 해결 요청을 원문 의미대로 복원",
    7679: "명장이 될 인물이라는 판단과 마음을 꺾고 싶지 않다는 의도를 복원",
    7680: "사람 사이 화합과 장수로서 명성을 이루기 어려운 조건을 명확화",
    7682: "호적수를 두게 하라는 제안을 자연스럽게 복원",
    7683: "상대가 필요하다는 발화의 의문형을 복원",
    7684: "항상·훌륭한 적수라는 원문 정보를 복원",
    7685: "뒤지지 않으려 정진해 중요 전투에서 대패하지 않았다는 인과를 복원",
    7688: "가신들 가운데 적합한 인물이 있다는 지시 대상을 정리",
    7690: "다다카쓰의 진퇴·천하무쌍 평가를 전부 복원",
    7691: "본보기이자 숙적으로 삼으라는 지시를 재배치",
    7692: "사천왕 중 최고 녹봉이라는 서술을 복원",
    7693: "경쟁 상대로 삼은 효과인지 불명이라는 유보를 복원",
    7695: "가이·시나노 편입과 인재 확보 착수를 복원",
    7696: "옛 가신 통솔자 선정과 성장한 젊은 무사라는 묘사를 복원",
    7699: "미카타가하라 회상 대사의 구어체와 공포를 자연스럽게 복원",
    7703: "옛 가신 수용과 다케다의 피로 가문을 강화한다는 문장을 복원",
    7706: "옛 적의 반감과 기술·지혜 활용의 근거를 복원",
    7707: "옛 가신을 첨병으로 단련하겠다는 결의를 재배치",
    7710: "적비 계승과 이이 적비로의 재탄생을 복원",
    7711: "급격한 출세와 미카와 기반 부재라는 배경을 복원",
    7712: "엄격한 휘하 단련과 고슈 병사 통솔 적임성을 복원",
    7713: "엄격함이 훗날 다른 문제를 낳는다는 후일담을 복원",
}


class Wave80Error(RuntimeError):
    """Raised when the strict W79 predecessor or W80 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave80Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave80Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w79 = load_module("pc_event_wave79_for_wave80", W79_BUILDER)
parse_table = w79.parse_table
core = w79.core
control_signature = w79.control_signature
is_full_width_visible = w79.is_full_width_visible


@dataclass(frozen=True)
class Bundle:
    event: bytes
    changed: Mapping[int, str]
    rows: tuple[Mapping[str, Any], ...]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave80Error(f"candidate escapes tmp root: {resolved}") from exc
    return resolved


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(event),
        "size": len(event),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def runtime_tokens(value: str) -> tuple[str, ...]:
    return tuple(RUNTIME_RE.findall(value))


def assert_no_break_inside_tag(value: str) -> None:
    in_colour_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            if token == "\x1bCZ":
                require(in_colour_span, "unpaired ESC close")
                in_colour_span = False
            else:
                require(not in_colour_span, "nested ESC colour span")
                in_colour_span = True
            cursor += 3
            continue
        require(not (in_colour_span and value[cursor] in "\r\n"), "line break inside colour tag")
        cursor += 1
    require(not in_colour_span, "unterminated ESC colour span")


def rendered_display_line(value: str) -> str:
    rendered: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token in layout: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        if runtime is not None:
            token = runtime.group(0)
            reservation = SCENE_RUNTIME_RESERVATIONS.get(token)
            require(reservation is not None, f"missing W80 scene reservation: {token}")
            rendered.append(str(reservation["display"]))
            cursor = runtime.end()
            continue
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if is_full_width_visible(character))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        rows.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_live_raw_960px": raw > RAW_LINE_LIMIT_PX,
            }
        )
    return tuple(rows)


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = w79.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W79 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W79 Naomasa predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W79_PROFILE, "W79 on-disk event profile drift")
    require(w79.EXPECTED_OUTPUT_PROFILE == EXPECTED_W79_PROFILE, "W79 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W79_PROFILE, "W79 audit output profile drift")
    require(manifest["output"] == EXPECTED_W79_PROFILE, "W79 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_jp() -> Any:
    return w79.load_direct_jp()


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W80 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W80 retained scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Naomasa row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W79/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W80 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W80 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W80 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w79_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w79_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES.get(entry_id, "직접 PC JP 및 PC EN/SC/TC 문맥 대조 후 유지"),
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(runtime_tokens(target)),
                "runtime_proven": False,
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W80 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W79 Naomasa predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W80 Naomasa event", event)
    require(after_raw == rebuilt_raw, "W80 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W80 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W80 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W80 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-naomasa-quality-wave80-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W79 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_text_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "strict_live_raw_line_limit_px": RAW_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_is_report_only": True,
            "runtime_reservations": SCENE_RUNTIME_RESERVATIONS,
            "runtime_reservations_scene_limited": True,
            "runtime_proven": False,
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": list(RETAINED_IDS),
            "unchanged_after_review_count": len(RETAINED_IDS),
        },
        "input_w79_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-naomasa-quality-wave80-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w79.WORKSTREAM.name,
            "candidate_relative": (w79.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
        },
        "changed_row_ids": list(CHANGED_IDS),
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, changed, tuple(rows), audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W80 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W80 candidate staging exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.write_bytes(bundle.event)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W80 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W80 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W80 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W80 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W80 candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "runtime_proven": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_naomasa_quality_wave80_v1.py",
        WORKSTREAM / "test_pc_event_naomasa_quality_wave80_v1.py",
    ):
        require(path.is_file(), f"W80 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W80 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        bundle = prepare(require_output_profile=False)
        print(json.dumps(bundle.profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        bundle = prepare(require_output_profile=True)
        print(write_candidate(bundle))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": list(bundle.changed), "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
