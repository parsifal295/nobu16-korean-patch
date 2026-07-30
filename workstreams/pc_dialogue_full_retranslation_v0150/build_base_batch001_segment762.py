#!/usr/bin/env python3
"""Build Base authoring segment 762 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S762.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s762", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:366:0": '"특수 요충지 발동"',
    "13:367:0": (
        '제압한 "특수 요충지"의 효과를 발동할 수 있게 되었습니다.\n'
        "재발동하는 데 시간이 걸리므로 결정적인 순간에 사용합시다."
    ),
    "13:368:0": '"합전에서의 전투"',
    "13:369:0": (
        "정면으로 싸우는 것만이 합전의 전부는 아닙니다.\n"
        "의견에 귀 기울여도 좋고 스스로 호기를 찾아내도 좋습니다.\n"
        "정확한 판단으로 전황을 유리하게 이끕시다.\n"
        "\n"
        "【유리하게 싸우려면】\n"
        "·전법을 발동한다\n"
        "·적 부대를 협격한다\n"
        "·고지대에서 사격한다"
    ),
    "13:370:0": (
        "【전법】\n"
        "전법을 발동하면 강력한 효과를 얻습니다.\n"
        "모든 무장이 보유하고 있으며 각자 판단하여 발동합니다.\n"
        "\n"
        "전법 버튼을 오른쪽 클릭하면\n"
        "전법을 수동 발동으로 전환할 수도 있습니다.\n"
        "※왼쪽 클릭으로 수동 발동할 수 있습니다"
    ),
    "13:371:0": (
        "【전법】\n"
        "전법을 발동하면 강력한 효과를 얻습니다.\n"
        "모든 무장이 보유하고 있으며 각자 알맞은 때에 발동합니다.\n"
        "\n"
        "부대 목록에서 부대를 선택하고 ㌘+㌦을 누르면\n"
        "전법을 수동으로만 발동하도록 전환할 수도 있습니다.\n"
        "※㌦(으)로 수동 발동할 수 있습니다"
    ),
    "13:372:0": (
        "【협격】\n"
        "적 부대를 여러 방향에서 동시에 공격하면 협격이 됩니다.\n"
        "협격 중에는 적의 병력과 체력에 큰 피해를 줄 수 있습니다."
    ),
    "13:373:0": (
        "【사격】\n"
        "고지대 요충지 중에는 활 아이콘이 표시된 곳이 있습니다.\n"
        "이 요충지의 부대는 절벽 아래 적 부대를 사격할 수 있습니다.\n"
        "사격은 병력에 큰 피해를 주며 반격도 받지 않습니다."
    ),
    "13:374:0": '"부대 상태"',
    "13:375:0": (
        "부대는 전투를 계속하면 병력과 체력이 줄어들어\n"
        "마침내 싸울 수 없게 됩니다.\n"
        "부대가 온전한 상태로 싸울 수 있도록 상태를 주의 깊게 살핍시다."
    ),
    "13:376:0": (
        "【주의해야 할 아군 상태】\n"
        "·부대의 병력\n"
        "·부대의 체력\n"
        "·상태 이상"
    ),
    "13:377:0": (
        "【병력】\n"
        '병력이 0이 된 부대는 "괴멸"하며 지휘하던 무장은\n'
        "포박이나 전사의 위험에 처합니다.\n"
        '병력이 적어진 부대는 괴멸을 피하고자 "퇴각"합니다.\n'
        "퇴각 중인 부대는 어떤 지시도 받지 않고 아군 퇴각로만을 향합니다.\n"
        "포박이나 전사를 막으려면 호위할 필요도 있습니다."
    ),
    "13:378:0": (
        "【체력】\n"
        '합전에서 부대는 병력 외에 "체력"도 지닙니다.\n'
        "체력이 줄어들면 부대 능력이 떨어집니다.\n"
        "\n"
        "·체력은 전투하면 줄고 전투하지 않고 대기하면 회복된다\n"
        "·방어력이 높을수록 체력이 잘 줄지 않는다\n"
        "·체력이 적어진 부대는 공격과 방어가 크게 저하된다"
    ),
    "13:379:0": (
        "【상태 이상】\n"
        "상태 이상이 된 부대는 행동이 제한됩니다.\n"
        "\n"
        "◇혼란\n"
        "·전법, 특수 요충지 발동, 퇴각로 파괴로 발생\n"
        "·이동, 전투, 명령이 불가능해진다. 일정 시간이 지나면 해제"
    ),
    "13:380:0": (
        "◇퇴각\n"
        "·병력이 적어지면 발생\n"
        "·전투나 명령이 불가능해지고 가장 가까운 아군 퇴각로로 이동한다\n"
        "·퇴각로에 도착하면 전장에서 이탈한다\n"
        "  ※충성이 낮은 무장이나 국인중 부대는 평소보다 일찍 퇴각한다"
    ),
    "13:381:0": '"무장 승진"',
    "13:382:0": (
        "무장이 얻은 훈공이 일정량에 이르면\n"
        "계절이 바뀔 때 열리는 논공행상에서 승진합니다.\n"
        "\n"
        "이 화면에서는 무장의 훈공 내역과 승진한 무장 등을 확인할 수 있습니다.\n"
        "※확인하지 않아도 무장은 승진합니다"
    ),
    "13:383:0": (
        "【승진하려면】\n"
        "승진하려면 훈공이 필요합니다.\n"
        "훈공은 내정, 건의, 합전 등으로 얻을 수 있습니다.\n"
        "\n"
        "【승진하면】\n"
        "승진하면 군단장/성주/영주 임명이 가능해집니다.\n"
        "가장 낮은 신분인 조두는 영지를 가질 수 없으므로\n"
        "대관에 임명되거나 다이묘의 명령을 수행해 훈공을 얻어야 합니다."
    ),
    "13:384:0": '"부대 편제"',
    "13:385:0": (
        "출진할 무장을 정합니다.\n"
        "각 무장은 자기 영지의 병사를 이끌고 하나의 부대로 출진합니다.\n"
        "성 능력과 마찬가지로 부대장이 부대 능력의 기준이 됩니다.\n"
        "※성의 군량이 병력보다 적으면 부대의 휴대 군량 일수가 줄어드니 주의합시다\n"
        "\n"
        "【부대를 강화하려면】\n"
        "·성주/영주를 바꾸어 성 능력이나 특성 레벨을 높인다\n"
        "·공략 목표를 설정해 임전 상태로 만든다"
    ),
    "13:386:0": (
        "【부대 능력을 높이려면】\n"
        "·능력이 높은 무장을 성주로 삼는다\n"
        "·능력 하나라도 부대장보다 높은 무장을 부대에 편성한다\n"
        "·부대장과 상성이 좋은 무장을 부대에 편성한다\n"
        "·공략 목표를 설정해 임전 상태로 만든다"
    ),
    "13:387:0": (
        "【특성】\n"
        "·부대 특성은 무장이 지닌 특성의 합계\n"
        "·같은 특성을 지닌 무장이 여럿이면 특성 LV가 오른다\n"
        "·LV는 최대 5"
    ),
    "13:388:0": (
        "【주의】\n"
        "·성의 군량이 병력보다 적으면 부대 군량의 지속 일수가 줄어든다"
    ),
}

BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if 366 <= base_record_id <= 367:
        return base_record_id + 32
    if 368 <= base_record_id <= 383:
        return base_record_id + 33
    if 384 <= base_record_id <= 385:
        return base_record_id + 34
    if 386 <= base_record_id <= 388:
        return base_record_id + 35
    raise RuntimeError(f"segment 762 record has no configured PK mapping: {base_record_id}")


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


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
    expected_divergences = {"JP": {383}, "SC": {383}, "TC": set()}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(366, 389)
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(13, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(13, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != expected_divergences[language]:
            raise RuntimeError(
                f"segment 762 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for coordinate, translation in TRANSLATIONS.items():
        record_id = int(coordinate.split(":")[1])
        current_text = ENGINE.parse_record_literals(current_records[(13, record_id)])[0].text
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(f"{coordinate} line-count contract drifted")
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} controller-glyph skeleton drifted")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "특수 요충지",
        "퇴각로",
        "국인중",
        "휴대 군량",
        "영지",
        "군단장",
        "성주",
        "영주",
        "조두",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 762 required terminology drifted")
    if "호족" in joined or "병량" in joined or "퇴로" in joined or "철수" in joined:
        raise RuntimeError("segment 762 retains a forbidden legacy term")
    if "㌘+㌦" not in TRANSLATIONS["13:371:0"]:
        raise RuntimeError("13:371 controller instruction drifted")
    if "퇴각로" not in TRANSLATIONS["13:377:0"] or "퇴각로" not in TRANSLATIONS["13:379:0"]:
        raise RuntimeError("segment 762 must use 退き口=퇴각로")
    if len(TRANSLATIONS) != 23 or set(TRANSLATIONS) != {
        f"13:{record_id}:0" for record_id in range(366, 389)
    }:
        raise RuntimeError("segment 762 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S762",
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
