#!/usr/bin/env python3
"""Build Base authoring segment 779 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S779.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s779", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:50:0": "◇증축",
    "14:50:1": (
        "\n건설한 시설은 금전과 노동력을 더 들여 강화할 수 있습니다.\n"
        "다만 강화할수록 필요한 금전이 늘어납니다.\n"
        '일부 시설은 일정 이상의 "석고"와 "상업"도 필요합니다.\n'
        "\n"
    ),
    "14:50:2": "◇철거",
    "14:50:3": (
        "\n건설한 시설을 철거하여 구획을 비울 수 있습니다.\n"
        "철거에는 금전과 노동력이 들지 않으며, 기간도 걸리지 않아 즉시 이루어집니다.\n"
        "실행 무장을 임명할 필요도 없습니다.\n"
        "\n"
    ),
    "14:50:4": "◇성하 방침",
    "14:50:5": (
        "\n성하 방침을 정하면 성주가 자율적으로 성하 시설을 건설합니다.\n"
        '정책 "제도 개신" LV1을 발령하면 설정할 수 있으며, 건설 비용은 들지 않습니다.\n'
        "다만 해제할 때까지 노동력을 계속 사용하므로 주의합시다.\n"
        '※정책 "재량권 위양"을 발령하면 노동력도 필요하지 않습니다\n'
        "\n"
        '"제도 개신" LV2를 발령하면 증축도 합니다.\n'
        '※"성하 방침"의 건설 속도는 성 능력에 따라 달라집니다'
    ),
    "14:51:0": "[공략 목표]",
    "14:51:1": (
        '\n"공략 목표"를 설정하면 선정된 성의 가신들이\n'
        "공략 목표로 지정된 성을 공격하고자 군비를 갖춥니다.\n"
        "\n"
    ),
    "14:51:2": "◇군비",
    "14:51:3": (
        '\n선정된 성 영내의 군은 "군비"를 시작하고, 완료되면 "임전" 상태가 됩니다.\n'
        "임전 상태인 군은 출진할 때 부대 능력이 일시적으로 강화되고, 휴대 군량도 늘어납니다.\n"
        "또한 군비가 끝나면 적 영지에 인접한 지략 60 이상의 영주가 조략을 시도합니다.\n"
        "※성주/영주/대관이 없는 군은 군비를 할 수 없습니다\n"
        "\n"
    ),
    "14:51:4": "◇포인트",
    "14:51:5": (
        "\n임전 상태로 출진하면 강력하지만\n"
        "임전 상태가 될 때까지 성주/영주/대관은 군비 외의 영내 행동을 하지 않습니다.\n"
        "군비가 끝난 뒤에도 내정을 중단하고 조략 등 공략과 관련된 행동만 합니다.\n"
        "강한 세력을 공격할 때처럼 결정적인 순간에 사용합시다.\n"
        "임전 상태는 한 번 출진한 뒤 귀성하거나 일정 시간이 지나면 해제됩니다.\n"
        "\n"
        "성 영내에서 임전 상태인 군의 수는 성 위쪽에"
    ),
    "14:51:6": "╋",
    "14:51:7": "아이콘으로 표시됩니다.\n※모든 군이 임전 상태가 되면 아이콘 색이 바뀝니다",
    "14:52:0": "[출진]",
    "14:52:1": (
        "\n목표를 선택하면 목표의 상황에 맞는 부대 편제가 제안됩니다.\n"
        "직접 부대 편제나 목표를 수정할 수도 있습니다.\n"
        "출진하여 시간을 진행하면 부대는 목표를 향해 자동으로 행군합니다.\n"
        "\n"
    ),
    "14:52:2": "◇행군 시 주의",
    "14:52:3": (
        "\n\u3000·행군 중에는 휴대 군량(부대가 휴대하는 식량)을 소비한다\n"
        "  병량이 떨어지면 병력이 조금씩 감소한다\n"
        " ·적의 군에 도달하면 군을 제압할 때까지 발이 묶이며\n"
        '  취락 "요새"가 있으면 영주의 무용에 따라 피해를 받는다\n'
        " ·적 부대나 성과 접촉하면 전투가 시작된다\n"
        " ·병력이 0이 되면 부대가 괴멸하며, 무장이 전사할 수도 있다"
    ),
    "14:53:0": "◇행군 요령",
    "14:53:1": (
        "\n\u3000·적 부대나 성을 협격하면 유리해진다\n"
        "  적에게 협격당하지 않도록 하는 것이 중요하다\n"
        ' ·다이묘 부대가 교전 중이거나 다이묘 근처의 부대가 교전 중이면 다이묘 부대가 "합전"을 벌일 수 있다\n'
        " ·Shift + 드래그로 여러 부대를 선택하여 동시에 명령할 수 있다\n"
        " ·목표 변경 시 Shift + 좌클릭으로 중계점을 설정할 수 있다\n"
        " ·여러 부대를 선택한 상태에서 중계점을 설정하면 합류점이 되어\n"
        "  각 부대가 모일 때까지 기다린 뒤 행군한다"
    ),
    "14:54:0": "◇행군 요령",
    "14:54:1": (
        "\n\u3000·적 부대나 성을 협격하면 유리해진다\n"
        "  적에게 협격당하지 않도록 하는 것이 중요하다\n"
        ' ·다이묘 부대가 가까이 있으면 "합전"으로 단숨에 승부를 낼 수 있다\n'
        " ·㍉㎝㍑㎝㌣로 여러 부대를 선택하여 동시에 명령할 수 있다\n"
        " ·목표 변경 시 ㌘+㍑로 중계점을 설정할 수 있다\n"
        " ·여러 부대를 선택한 상태에서 중계점을 설정하면 합류점이 되어\n"
        "  각 부대가 모일 때까지 기다린 뒤 행군한다"
    ),
}

BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
PROTECTED_GLYPHS = set("◇╋㍑㍉㌘㌣㎝")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)
EXPECTED_ARITY = {50: 6, 51: 8, 52: 4, 53: 2, 54: 2}


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {50: 73, 51: 74, 52: 75, 53: 76, 54: 77}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 779 record has no configured PK mapping: {base_record_id}") from exc


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


def assert_scope(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }
    expected_divergences = {"JP": {51, 52}, "SC": set(), "TC": set()}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(50, 55)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(14, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(14, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != expected_divergences[language]:
            raise RuntimeError(
                f"segment 779 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id, expected_arity in EXPECTED_ARITY.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 779 literal arity drifted: 14:{record_id}")
    for coordinate, translation in TRANSLATIONS.items():
        _, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(14, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} LF/U+3000/token layout signature drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} retains CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} protected-glyph skeleton drifted")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "증축",
        "노동력",
        "공략 목표",
        "출진",
        "행군",
        "부대",
        "합전",
        "군비",
        "임전",
        "휴대 군량",
        "병량",
        "적 영지",
        "선정된 성",
        "협격",
        "성하 방침",
        "제도 개신",
        "재량권 위양",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 779 required terminology drifted")
    if TRANSLATIONS["14:51:4"] != "◇포인트" or TRANSLATIONS["14:51:6"] != "╋":
        raise RuntimeError("segment 779 cross-segment exact literal drifted")
    if TRANSLATIONS["14:53:0"] != TRANSLATIONS["14:54:0"]:
        raise RuntimeError("14:53:0 and 14:54:0 exact translation drifted")
    if any(
        term in joined
        for term in (
            "추가 성 공략",
            "공성전 페이지",
            "적령",
            "선출된 성",
            "협공",
            "노력",
        )
    ):
        raise RuntimeError("segment 779 imported PK-only guidance")
    expected_coordinates = {
        f"14:{record_id}:{literal_id}"
        for record_id, arity in EXPECTED_ARITY.items()
        for literal_id in range(arity)
    }
    if len(TRANSLATIONS) != 22 or set(TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 779 decision/static classification count drifted")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S779",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": 0,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
