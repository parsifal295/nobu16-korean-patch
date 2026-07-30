#!/usr/bin/env python3
"""Build Base authoring segment 760 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S760.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s760", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:320:0": "【행군 중의 행동】\n행군 중인 부대는 일시적으로 진군을 멈추고 다음 행동을 하기도 합니다.\n·군 제압 … 적 세력의 군에 도달하면 발생\n·부대와 전투 … 적 부대와 접촉하면 발생\n·공성전 … 적 세력의 성과 접촉하면 발생\n\n적 부대와 전투하거나 공성전을 벌이면 병력이 감소합니다.\n또한 군을 제압하는 동안 적 세력이 부대를 파견해 오기도 합니다.",
    "13:321:0": '"합전 실행"',
    "13:322:0": '다이묘 부대가 전투에 참가 중이거나 근처에 있으면,\n다이묘 부대의 메뉴에서 "합전"을 실행할 수 있습니다.\n※합전이 가능할 때는 다이묘 부대에 "합전 가능"이 표시됩니다\n\n【합전이란】\n·합전장을 무대로 최대 16개 부대끼리 벌이는 전투\n·승리하면 참전한 부대 수에 따라 "위풍"이 발생\n·"위풍"이 발생하면 주변의 성과 군, 국인중이 아군으로 돌아서기도 한다',
    "13:323:0": '"합전"',
    "13:324:0": "적과 아군의 부대가 한 전장에 모여 승패를 가리는 것이 합전입니다.\n무장들은 승리와 공명을 위해 스스로 판단하여 부대를 움직이고 싸웁니다.\n다만 전황이 바뀌면 판단을 구해 오기도 합니다.\n호기와 위기에 어떻게 대응하느냐가 합전의 승패를 좌우합니다.",
    "13:325:0": '【승리 조건】\n다음 중 하나를 달성한 진영이 승리합니다.\n①적의 "총사기"를 0으로 만든다\n②적 부대를 모두 격파한다\n③적의 "퇴각로"를 모두 파괴한다\n④적의 다이묘를 토벌한다',
    "13:326:0": "【부대】\n부대로 적 부대와 퇴각로, 요충지를 공격합니다.\n·동시에 8개 부대까지 출진할 수 있다\n·나머지 부대는 출진 중인 부대가 괴멸하거나 퇴각하면 출진한다\n·전장에 표시된 선을 따라 이동하며, 적 부대와 접촉하면 공격한다",
    "13:327:0": "【부대】\n·평소에는 스스로 판단하여 이동하고 공격하지만 플레이어가 지시할 수도 있다\n·지시할 때 Shift + 왼쪽 클릭으로 중계점을 설정할 수 있다",
    "13:328:0": "【부대】\n·평소에는 스스로 판단하여 이동하고 공격하지만 플레이어가 지시할 수도 있다\n·지시할 때 ㌘㎝㍑으로 중계점을 설정할 수 있다",
    "13:329:0": '【퇴각로】\n각 진영에서 부대가 퇴각할 때 이용하는 출입구가 퇴각로입니다.\n모두 파괴되면 패배합니다.\n·예비 부대의 출진 지점이다\n·부대의 공격으로 내구를 0으로 만들면 "파괴"된다\n·파괴되면 모든 부대가 혼란에 빠지고 능력이 저하되며 진영의 총사기가 내려간다',
    "13:330:0": '【요충지】\n전장 곳곳에 있는 중요 지점입니다. 많이 제압할수록 전투가 유리해집니다.\n·내구를 0으로 만들면 "제압"된다\n·제압하면 모든 부대의 능력이 상승하고 진영의 총사기가 오른다\n\n요충지 중에는 발동 효과가 있는 "특수 요충지"도 존재합니다.\n제압한 뒤 잠시 지나면 요충지 위의 버튼으로 특별한 효과를 발동할 수 있습니다.',
    "13:331:0": '"공성전"',
    "13:332:0": '부대가 적의 성과 접촉하면 공성전이 시작됩니다.\n\n【공성전 규칙】\n·내구를 0으로 만들면 성을 제압한다\n·여러 길에서 성을 포위하면 유리해진다\n·공성 측에는 "포위"와 "강공", 두 가지 공격 방식이 있다\n·부대장의 판단으로 포위와 강공을 바꾸기도 한다',
    "13:333:0": '【포위란】\n·제압까지 시간이 걸리지만 반격을 받지 않는다\n·피해는 부대의 "포위" 값과 성 측의 "대포위" 값으로 결정된다\n\n【강공이란】\n·성에 주는 피해가 크지만 반격을 받는다\n·포위와 달리 성의 병력에도 피해를 준다\n·강공 중 피해는 부대의 "공격" 값과 성 측의 "방어" 값으로 결정된다',
    "13:334:0": '"성주 임명"',
    "13:335:0": '신분이 "사무라이 대장" 이상인 가신을 성주로 임명할 수 있습니다.\n\n【성주를 임명하면】\n·성주의 능력이 성 능력의 바탕이 된다\n·성하 시설 건설과 정책 준비 등 다양한 임무를 지시할 수 있다\n\n※한번 성주로 삼으면 정책 "제도 개신" LV3를 발령할 때까지 변경할 수 없습니다',
    "13:336:0": '"정책"-세력 강화-',
    "13:337:0": "충분한 금전 수입을 확보했다면\n정책을 발령하여 세력 전체를 강화합시다.\n\n【정책이란】\n·세력 전체에 효과를 준다\n·유지 비용이 든다\n·LV를 높이면 더욱 강력한 효과를 얻을 수 있다",
    "13:338:0": '어떤 정책을 발령할지 고민된다면 "제도 개신"을 발령하여\n성하 방침 설정을 해금하는 것을 추천합니다.\n\n【주의】\n·각 정책에는 저마다 발령 조건이 있다\n·신분이 "부장" 이상이어야 정책 발령에 참여할 수 있다\n·유지 비용을 지불하지 못하면 발령 중인 모든 정책이 중지된다',
    "13:339:0": '"조작 설명"',
    "13:340:0": "·왼쪽 클릭 … 선택/결정\n·오른쪽 클릭 … 명령 메뉴 열기(메인 화면)\n         취소(각종 메뉴나 창을 열었을 때)\n·Space 키 … 시간 진행/정지(메인 화면)\n         ※각종 메뉴가 열려 있는 동안에는 시간이 정지",
    "13:341:0": '【힌트】\n게임의 기본 흐름은 화면 왼쪽의 목록에서 고쇼가 설명합니다.\n무엇을 해야 할지 모르겠다면 이야기를 들어 봅시다.\n곤란할 때는 화면 오른쪽 위의 "도움말"을 살펴봅시다.',
}

BASE_PK_DIVERGENCES = {
    "JP": {320, 326, 327, 328, 329, 330, 331, 332, 337},
    "SC": {320, 326, 327, 328, 329, 330, 331, 332, 337},
    "TC": {320, 326, 327, 328, 329, 330, 331, 332, 337},
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available_base_jp_authoritative"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if base_record_id == 320:
        return base_record_id + 22
    if 321 <= base_record_id <= 338:
        return base_record_id + 23
    if 339 <= base_record_id <= 341:
        return base_record_id + 24
    raise RuntimeError(f"segment 760 record has no configured PK mapping: {base_record_id}")


def prior_translation(coordinate: str) -> str:
    for decision_path in sorted(OUTPUT.parent.glob("base_msggame_B001_S*.private.v1.jsonl")):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate:
                return str(row["translation"])
    raise RuntimeError(f"prior exact translation is absent: {coordinate}")


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
            for record_id in range(320, 342)
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
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 760 mapped PK {language} divergences drifted: {sorted(divergences)}"
            )

    if TRANSLATIONS["13:334:0"] != prior_translation("13:230:0"):
        raise RuntimeError("13:334 must exactly reuse the approved 13:230 translation")
    if source_records[(13, 334)].data != source_records[(13, 230)].data:
        raise RuntimeError("pristine exact reuse drifted: 13:334 != 13:230")
    if current_records[(13, 334)].data != current_records[(13, 230)].data:
        raise RuntimeError("current exact reuse drifted: 13:334 != 13:230")

    if source_records[(13, 339)].data != source_records[(13, 342)].data:
        raise RuntimeError("pristine follow-up exact reuse drifted: 13:339 != 13:342")
    if current_records[(13, 339)].data != current_records[(13, 342)].data:
        raise RuntimeError("current follow-up exact reuse drifted: 13:339 != 13:342")
    if TRANSLATIONS["13:339:0"] != '"조작 설명"':
        raise RuntimeError("13:339 approved exact translation drifted")
    if "고쇼" not in TRANSLATIONS["13:341:0"] or "시동" in TRANSLATIONS["13:341:0"]:
        raise RuntimeError("13:341 must translate 小姓 as the approved term 고쇼")

    if "아군으로 돌아서" not in TRANSLATIONS["13:322:0"]:
        raise RuntimeError("13:322 must preserve the direction of 寝返る")
    if "국인중" not in TRANSLATIONS["13:322:0"]:
        raise RuntimeError("13:322 must translate 国衆 as 국인중")
    for record_id in (325, 326, 329):
        translation = TRANSLATIONS[f"13:{record_id}:0"]
        if "퇴각로" not in translation or "퇴로" in translation or "퇴각구" in translation:
            raise RuntimeError(f"13:{record_id} must consistently translate 退き口 as 퇴각로")
    if "사무라이 대장" not in TRANSLATIONS["13:335:0"]:
        raise RuntimeError("13:335 must translate 侍大将 as 사무라이 대장")
    if "제도 개신" not in TRANSLATIONS["13:335:0"] or "제도 개신" not in TRANSLATIONS["13:338:0"]:
        raise RuntimeError("制度改新 must remain 제도 개신")
    if "요충지" not in TRANSLATIONS["13:326:0"] or "특수 요충지" not in TRANSLATIONS["13:330:0"]:
        raise RuntimeError("要所/特殊要所 terminology drifted")
    if "총사기" not in TRANSLATIONS["13:325:0"] or "총사기" not in TRANSLATIONS["13:330:0"]:
        raise RuntimeError("総士気 terminology drifted")
    if "중계점" not in TRANSLATIONS["13:327:0"] or "중계점" not in TRANSLATIONS["13:328:0"]:
        raise RuntimeError("中継点 terminology drifted")
    if "㌘㎝㍑" not in TRANSLATIONS["13:328:0"]:
        raise RuntimeError("13:328 must preserve its embedded input glyph text")

    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 760 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 760 retains banned fullwidth punctuation")
    if len(TRANSLATIONS) != 22:
        raise RuntimeError("segment 760 decision count drifted")


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
                "segment": "base_msggame_B001_S760",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS),
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
