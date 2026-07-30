#!/usr/bin/env python3
"""Build Base authoring segment 770 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S770.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s770",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "14:7:0": "[보조 명령]",
    "14:7:1": (
        "\n　·헌언     ... 가신에게서 공략 방책을 받는다\n"
        " ·카메라 줌  ... 카메라의 확대/축소를 설정한다\n"
        " ·카메라 북향 ... 카메라가 북쪽을 향하도록 조정한다\n"
        " ·본거지 이동 ... 카메라를 본거지 위치로 이동한다\n"
        " ·뷰 전환   ... 전용 정보를 지도에 표시한다\n"
        " ·보고     ... 세력 내 수지 보고와 사건 등을 열람한다\n"
        " ·이벤트 목록 ... 이벤트 발생 조건을 열람한다\n"
        "           이벤트 발생 여부를 설정한다\n"
        " ·정보 목록  ... 각종 정보를 열람한다\n"
        " ·기능     ... 저장 및 설정\n"
        " ·도움말    ... 플레이 방법을 확인한다"
    ),
    "14:8:0": "[행동 목록]",
    "14:8:1": "\n가신의 건의나 내린 명령의 진행 상황 등을 확인할 수 있습니다.\n\n",
    "14:8:2": "◇표시되는 내용",
    "14:8:3": (
        "\n　·가신의 건의\n"
        "  ※튜토리얼 이외의 건의는 가운데 클릭으로 거부할 수 있습니다\n"
        " ·내린 명령의 진행 상황(군 개발, 정책 발령 등)\n"
        " ·영내 문제"
    ),
    "14:9:0": "[행동 목록]",
    "14:9:1": "\n가신의 건의나 내린 명령의 진행 상황 등을 확인할 수 있습니다.\n\n",
    "14:9:2": "◇표시되는 내용",
    "14:9:3": (
        "\n　·가신의 건의\n"
        " ·내린 명령의 진행 상황(군 개발, 정책 발령 등)\n"
        " ·영내 문제"
    ),
    "14:10:0": "[부대 목록]",
    "14:10:1": (
        "\n출진 중인 부대를 목록으로 확인할 수 있습니다.\n"
        "남은 병량이 적어지면 얼굴 옆에 아이콘이 표시됩니다.\n"
        " ·남은 병량 60일분 이하 ... 황색\n"
        " ·남은 병량 30일분 이하 ... 적색"
    ),
    "14:11:0": "[로그]",
    "14:11:1": (
        "\n게임 전체에서 일어난 사건이 로그로 표시됩니다.\n"
        "로그 상세 버튼을 누르면 지난 이력을 확인할 수 있습니다."
    ),
    "14:12:0": "[국인중]",
    "14:12:1": (
        '\n일부 군에는 "국인중"이라 불리는 독립 세력이 있습니다.\n'
        "국인중은 종속도가 가장 높은 세력을 지원합니다.\n"
        "종속도는"
    ),
    "14:12:2": "┥",
    "14:12:3": (
        "아이콘 색으로 확인할 수 있습니다.\n"
        " ·흰색 ... 종속도 1위가 자세력이 아님\n"
        " ·녹색 ... 종속도 1위가 자세력\n\n"
    ),
    "14:12:4": "◇자세력에 대한 종속도를 높이려면",
    "14:12:5": (
        "\n　·성 영지 안의 어느 군에든 영주를 임명한다\n"
        ' ·"영내 제책"에서 "국인중 회유"를 실행한다'
    ),
    "14:13:0": "[부대]",
    "14:13:1": (
        "\n출진 중인 부대입니다.\n"
        "자세력은 청색, 적 세력은 적색, 동맹 세력은 녹색으로 표시됩니다."
    ),
}

EXPECTED_ARITIES = {7: 2, 8: 4, 9: 4, 10: 2, 11: 2, 12: 6, 13: 2}
EXPECTED_DIVERGENCES = {
    "JP": {8, 9, 13},
    "SC": {8, 13},
    "TC": {8, 9, 13},
}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
)
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_exact_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_semantics_priority"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {7: 9, 8: 11, 9: 13, 10: 15, 11: 16, 12: 17, 13: 18}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(
            f"segment 770 record has no configured PK mapping: {base_record_id}"
        ) from exc


def line_layout_signature(text: str) -> tuple[object, ...]:
    lines = text.split("\n")
    leading = tuple(
        line[: len(line) - len(line.lstrip(" \t\u3000"))]
        for line in lines
    )
    trailing = tuple(
        line[len(line.rstrip(" \t\u3000")) :]
        for line in lines
    )
    return (
        text.count("\n"),
        leading,
        trailing,
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
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

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(7, 14)
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
        if divergences != EXPECTED_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 770 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )

    expected_coordinates: set[str] = set()
    for record_id, expected_arity in EXPECTED_ARITIES.items():
        source_literals = ENGINE.parse_record_literals(source_records[(14, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(14, record_id)])
        if len(source_literals) != expected_arity or len(current_literals) != expected_arity:
            raise RuntimeError(f"segment 770 arity drifted at 14:{record_id}")
        for literal in current_literals:
            coordinate = f"14:{record_id}:{literal.literal_id}"
            if not ENGINE.is_visible_translation_candidate(literal.text):
                raise RuntimeError(f"segment 770 unexpectedly contains a blank target: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 770 decision is missing: {coordinate}")
            if line_layout_signature(translation) != line_layout_signature(literal.text):
                raise RuntimeError(f"segment 770 layout signature drifted: {coordinate}")
            if "\r" in translation:
                raise RuntimeError(f"segment 770 adds CR: {coordinate}")
            if ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 770 retains kana or CJK Han text: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 770 retains banned fullwidth punctuation: {coordinate}")

    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 22:
        raise RuntimeError("segment 770 decision universe drifted")
    for literal_id in (0, 1, 2):
        if TRANSLATIONS[f"14:8:{literal_id}"] != TRANSLATIONS[f"14:9:{literal_id}"]:
            raise RuntimeError(f"14:8:{literal_id}/14:9:{literal_id} exact translation drifted")
    if TRANSLATIONS["14:12:2"] != "┥":
        raise RuntimeError("14:12:2 must preserve the Base UI glyph exactly")

    base_action_8 = ENGINE.parse_record_literals(source_records[(14, 8)])[3].text
    base_action_9 = ENGINE.parse_record_literals(source_records[(14, 9)])[3].text
    pk_action_8 = ENGINE.parse_record_literals(
        pk_source_records[(14, mapped_pk_record_id(8))]
    )[3].text
    pk_action_9 = ENGINE.parse_record_literals(
        pk_source_records[(14, mapped_pk_record_id(9))]
    )[3].text
    if "軍団状況" in base_action_8 or "軍団状況" in base_action_9:
        raise RuntimeError("14:8/9 Base action lists unexpectedly contain the PK-only corps status")
    if "軍団状況" not in pk_action_8 or "軍団状況" not in pk_action_9:
        raise RuntimeError("14:8/9 mapped PK corps-status expansion contract drifted")
    base_unit_colors = ENGINE.parse_record_literals(source_records[(14, 13)])[1].text
    pk_unit_colors = ENGINE.parse_record_literals(
        pk_source_records[(14, mapped_pk_record_id(13))]
    )[1].text
    if "同盟勢力" not in base_unit_colors or "味方勢力" in base_unit_colors:
        raise RuntimeError("14:13 Base allied-clan wording contract drifted")
    if "味方勢力" not in pk_unit_colors:
        raise RuntimeError("14:13 mapped PK friendly-clan wording contract drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = ("헌언", "건의", "국인중", "영내 제책", "병량", "동맹 세력")
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 770 required terminology drifted")
    if any(term in joined for term in ("호족", "군단 상황", "아군 세력", "헌책", "커맨드")):
        raise RuntimeError("segment 770 retains a forbidden or PK-only term")


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
        target = prepared.visible_targets.get(
            ("base_msggame", block_id, record_id, literal_id)
        )
        if target is None:
            raise RuntimeError(
                f"decision target is absent from the current Base universe: {coordinate}"
            )
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
        raise RuntimeError(
            "validated decision count differs from the segment translation count"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S770",
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
