#!/usr/bin/env python3
"""Build Base authoring segment 765 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S765.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s765", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:423:0": "사자의 헌금 요구에 여러 번 응하면 조정과 직접 외교할 수 있습니다.\n조정에서 관직을 받으면 위신이 높아지므로 적극적으로 외교합시다.\n\n[위신을 높이는 이점]\n·정책을 발령할 수 있다\n·상대보다 위신이 높으면 침공한 적병이 위축되어 유리하게 싸울 수 있다\n·자신보다 위신이 낮은 세력과의 외교가 유리해진다",
    "13:424:0": '"적 세력의 침공"',
    "13:425:0": "적 세력이 영토를 넓히려고 침공해 오기도 합니다.\n자세력의 병력이 출진 중이거나 상대보다 적을 때는\n평소보다 침공받기 쉬우므로 주의합시다.\n\n[붉은색 세력]\n다음 세력은 지도에서 붉은색으로 표시됩니다. 특히 주의합시다.\n·현재 공격 중이거나 자세력을 공격 중인 상대\n·공략 목표이거나 자세력을 공략 목표로 삼은 상대",
    "13:426:0": "[침공받았을 때의 대처 예]\n·부대를 출진시켜 요격한다\n·동맹 세력에 원군을 요청한다\n·병력이나 위신이 높은 세력에 정전 중재를 부탁한다",
    "13:427:0": '"적의 성 제압"',
    "13:428:0": "적 세력의 성을 제압했습니다. 훌륭하십니다!\n성이 늘어 세력이 더욱 강해집니다.\n획득한 성에는 성주와 영주를 임명해 둡시다.\n\n이 기세로 영지를 넓히면 천하통일도 꿈이 아닙니다!",
    "13:429:0": '"처우 선택"',
    "13:430:0": "포박한 무장의 처우를 정합니다.\n적장을 등용하거나 처단하면 전투를 유리하게 이끌 수 있습니다.\n\n[포박한 무장에게 할 수 있는 일]\n◇등용 … 자세력에 출사하도록 권한다\n◇처단 … 처단된 무장은 해당 게임에서\n다시는 등장하지 않는다\n◇해방 … 아무 조치 없이 풀어 준다. 다시 포박하면 등용에 응하기 쉬워진다",
    "13:431:0": "[등용에 대하여]\n·충성이 충분히 높은 무장은 절대 등용에 응하지 않는다\n·충성이 낮을수록 등용에 응하기 쉽다\n·주가가 멸망했으면 등용에 응하기 쉽다\n·여러 번 포박될수록 등용에 응하기 쉬워진다",
    "13:432:0": '"풍문"',
    "13:433:0": "다른 가문에 큰일이 생기면 풍문이 전해져 오기도 합니다.\n관심이 있다면 확인해 봅시다.\n※풍문을 확인하지 않아도 게임에 영향은 없습니다.",
    "13:434:0": '"가도 봉쇄"',
    "13:435:0": "휘하 무장이 스스로 판단해 진군로를 바꾸었습니다.\n적의 성을 포위하고 주변 가도를 봉쇄하면 공성전에서 유리하므로\n이를 노린 행동인 듯합니다.\n\n무장들은 이처럼 상황을 스스로 판단하기도 합니다.\n필요하다면 직접 지시해 효율적으로 공성전을 진행합시다.",
    "13:436:0": '"성주 항복"',
    "13:437:0": "충성이 낮은 무장은 성이 함락되기 전에 항복하기도 합니다.\n\n충성이 낮은 무장을 전선의 성주로 임명한다면\n가보나 관직을 내려 충성을 높게 유지합시다.",
    "13:438:0": '"독단 철수"',
    "13:439:0": "충성이 낮은 무장의 부대가 불리해지면\n명령을 무시하고 철수하기도 합니다.\n\n가보나 관직을 내려 충성을 높이거나\n되도록 고립시키지 않도록 하여\n제멋대로 전장을 떠나지 않게 주의합시다.",
    "13:440:0": '"조략 간파"',
    "13:441:0": "지략이 높은 영주는 적이 걸어 온 조략을 간파하기도 합니다.\n적 영토와 인접한 군에는 지략이 높은 무장을 영주로 임명하는 것도 효과적입니다.\n\n간파에 성공하면 적이 건 조략을 중지시키지만\n실패하기도 합니다.\n",
    "13:442:0": '"소규모 접전"',
    "13:443:0": '혈기 왕성한 성주는 인접한 적의 성에 빼앗을 만한 군이 있으면\n스스로 출진해 제압하러 가기도 합니다.\n그런 무장을 전선의 성주로 임명할 때는 주의합시다.\n\n[독단으로 군 제압에 출진하는 무장]\n·특성 "혈기"를 지닌 무장\n·지략이 60 미만인 무장',
    "13:444:0": '"제도 개신 LV2"',
    "13:445:0": '정책 "제도 개신"이 LV2로 오르면서\n"영주의 지행지 교체" 등을 할 수 있게 되었습니다.\n자세력의 영지를 점검해 지행지 배분을 다시 검토합시다.\n\n[해금된 내용]\n·영주의 지행지 교체\n·"전봉"으로 여러 무장의 지행지를 한꺼번에 변경\n·성하 방침을 설정한 성주가 증축도 수행',
}

BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）【】")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if 423 <= base_record_id <= 426:
        return base_record_id + 36
    if 427 <= base_record_id <= 445:
        return base_record_id + 38
    raise RuntimeError(f"segment 765 record has no configured PK mapping: {base_record_id}")


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
    expected_divergences = {
        "JP": {435, 437},
        "SC": {426, 435, 437},
        "TC": {426, 435, 437},
    }
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(423, 446)
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
                f"segment 765 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    for record_id in range(423, 446):
        source_literals = ENGINE.parse_record_literals(source_records[(13, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(13, record_id)])
        if len(source_literals) != 1 or len(current_literals) != 1:
            raise RuntimeError(f"segment 765 record must remain a single static literal: 13:{record_id}")
    for coordinate, translation in TRANSLATIONS.items():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError(f"segment 765 must not add U+3000 or CR: {coordinate}")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"segment 765 retains banned fullwidth punctuation: {coordinate}")
    if TRANSLATIONS["13:427:0"] != '"적의 성 제압"' or "인접한 적의 성" not in TRANSLATIONS["13:443:0"]:
        raise RuntimeError("13:427/443 must translate 敵城 without the ambiguous 적성 form")
    if "공성전" not in TRANSLATIONS["13:435:0"]:
        raise RuntimeError("13:435 must follow Base 攻城戦 authority")
    if "상대 세력의 등용" in TRANSLATIONS["13:437:0"]:
        raise RuntimeError("13:437 imported a PK-only surrender explanation")
    if not TRANSLATIONS["13:441:0"].endswith("\n"):
        raise RuntimeError("13:441:0 must preserve one trailing LF")
    if "소규모 접전" not in TRANSLATIONS["13:442:0"]:
        raise RuntimeError("13:442 must retain 小競り合い=소규모 접전")
    if "제도 개신" not in TRANSLATIONS["13:444:0"] or "제도 개신" not in TRANSLATIONS["13:445:0"]:
        raise RuntimeError("13:444/445 must retain 制度改新=제도 개신")
    if any(term in "\n".join(TRANSLATIONS.values()) for term in ("자동 임명", "전마제")):
        raise RuntimeError("segment 765 imported a PK-only explanation")
    if len(TRANSLATIONS) != 23:
        raise RuntimeError("segment 765 decision count drifted")


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
                "segment": "base_msggame_B001_S765",
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
