#!/usr/bin/env python3
"""Build Base authoring segment 763 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S763.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s763", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:389:0": '"영내 제책"',
    "13:390:0": (
        "군 개발과 성하 시설 건설 외에도\n"
        "가신에게 영내를 발전시키는 제책을 명할 수 있습니다.\n"
        "\n"
        "【제책을 명하는 방법】\n"
        "①명할 제책을 정한다\n"
        "②제책의 대상을 정한다(대상이 필요할 때만)\n"
        "③실행할 무장을 정한다"
    ),
    "13:391:0": '"역직"',
    "13:392:0": (
        '"역직"은 정이대장군만 실행할 수 있는 명령입니다.\n'
        "다이묘 가문에 역직을 수여하면 자신에 대한 외교 자세를 개선할 수 있습니다.\n"
        "\n"
        "다만 역직을 얻은 세력은 위신이 높아지므로\n"
        "함부로 역직을 수여하지 말고 상대를 가려 외교합시다."
    ),
    "13:393:0": '"부대 지시"',
    "13:394:0": (
        "합전에서는 협격 저지나 퇴각로 공격처럼\n"
        "전장 전체를 보고 판단해야 하는 상황이 생깁니다.\n"
        "이런 상황에서는 무장이 어떻게 행동할지 지시를 구합니다.\n"
        "무엇을 우선할지 냉정하게 상황을 판단하는 것이 중요합니다.\n"
        "\n"
        "특성에 따라 선호하는 행동이 있는 무장은\n"
        "판단을 구하지 않고 독단으로 행동하기도 합니다."
    ),
    "13:395:0": (
        "무장의 제안을 받아들이려면 직접 부대에 이동 지시를 내립시다.\n"
        "부대를 선택한 뒤 이동할 지점을 선택합니다.\n"
        "\n"
        "명령받은 부대는 지정된 지점으로 이동해 그곳에서 대기합니다.\n"
        "대기를 해제하거나 명령을 중단하려면\n"
        "부대를 선택한 뒤 부대 위에 나타나는 버튼을 누릅니다."
    ),
    "13:396:0": (
        "무장의 제안을 받아들이려면 직접 부대에 이동 지시를 내립시다.\n"
        "부대를 선택한 뒤 이동할 지점을 선택합니다.\n"
        "\n"
        "명령받은 부대는 지정된 지점으로 이동해 그곳에서 대기합니다.\n"
        "대기를 해제하거나 명령을 중단하려면\n"
        "부대를 선택한 뒤 ㌘+㍗을 누릅니다."
    ),
    "13:397:0": '"무장의 지시 거부"',
    "13:398:0": (
        "부대 상황에 따라 무장이 지시를 거부할 수 있습니다.\n"
        "병력이 많은 적을 공격하거나 체력이 낮을 때 이동하라는 지시는\n"
        "거부당할 수 있습니다."
    ),
    "13:399:0": '"국인중"',
    "13:400:0": (
        "국인중은 전국에 흩어진 소규모 세력으로 무력으로는 지배할 수 없습니다.\n"
        "다만 주변 세력에 대한 종속도가 있으며\n"
        "종속도가 가장 높은 세력은 원군을 요청할 수 있습니다.\n"
        "자신에 대한 종속도가 원군 요청 기준에 이른 국인중은 아이콘이 녹색으로 표시됩니다.\n"
        "\n"
        '또한 종속도가 충분히 높은 국인중을 "편입"하면\n'
        "자기 세력에 흡수할 수도 있습니다."
    ),
    "13:401:0": (
        "【국인중 대응】\n"
        "·인근 영주가 국인중을 회유해 종속도를 높이기도 한다\n"
        "·영내 제책으로 국인중을 회유하도록 명할 수 있다\n"
        "·영내 제책으로 종속도가 충분히 높은 국인중을 편입하도록 명할 수 있다\n"
        "\n"
        "※원군으로 출진한 국인중 부대가 괴멸하면 종속도가 크게 낮아집니다"
    ),
    "13:402:0": '"이벤트 발생"',
    "13:403:0": (
        "기재된 조건을 충족하면 이벤트가 발생합니다.\n"
        "이벤트는 자기 세력과 다른 세력의 상황에 영향을 줄 수 있습니다.\n"
        "\n"
        "각 이벤트를 유효/무효로 설정할 수 있습니다.\n"
        "일부 이벤트는 유효/무효 설정이 서로 연동되기도 합니다.\n"
        "\n"
        "자기 세력이 관련되면 대화 이벤트가 재생됩니다.\n"
        "※자기 세력이 멸망하는 이벤트는 초기 상태에서는 무효입니다"
    ),
    "13:404:0": '"건의"',
    "13:405:0": (
        '가신은 세력 상황을 판단해 다양한 시책을 "건의"로 올립니다.\n'
        "효과에 따라 금전과 노동력을 소비하기도 합니다.\n"
        "지금 해야 하는지 정말 필요한지 생각한 뒤 승인 여부를 판단합시다."
    ),
    "13:406:0": '"지행"-군 선택-',
    "13:407:0": (
        "다이묘 가문의 영지를 가신의 지행지로 내릴 수 있습니다.\n"
        "다이묘가 있는 성(본거지)은 직할지이므로 가신에게 내릴 수 없습니다.\n"
        "\n"
        "【지행지를 내리는 순서】\n"
        "①성을 선택한 뒤 이어서 군을 선택한다\n"
        "②지행을 받을 무장을 선택한다\n"
        "\n"
        "※먼저 영주가 없는 회색 군을 선택합시다"
    ),
}

VISIBLE_RECORD_IDS = set(range(389, 409)).difference({408})
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）")
CONTROLLER_GLYPHS = set("㍑㌍㌦㍗㍍㎝㌣㌘")
BASIS = (
    "pristine_base_pc_jp_with_base_sc_tc_and_specified_offset_mapped_"
    "pk_jp_en_sc_tc_context_where_available"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    if 389 <= base_record_id <= 408:
        return base_record_id + 35
    raise RuntimeError(f"segment 763 record has no configured PK mapping: {base_record_id}")


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in CONTROLLER_GLYPHS]


def assert_available_duplicate_decision(coordinate: str, translation: str) -> None:
    decision_dir = OUTPUT.parent
    if not decision_dir.is_dir():
        return
    for decision_path in decision_dir.glob("base_msggame_B001_S*.private.v1.jsonl"):
        if decision_path == OUTPUT:
            continue
        for line in decision_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("coordinate") == coordinate and row.get("translation") != translation:
                raise RuntimeError(f"duplicate translation differs from {coordinate}")


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
    expected_divergences = {"JP": set(), "SC": set(), "TC": {392}}
    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in range(389, 409)
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
                f"segment 763 mapped PK {language} offsets drifted: {sorted(divergences)}"
            )
    source_blank = ENGINE.parse_record_literals(source_records[(13, 408)])[0]
    current_blank = ENGINE.parse_record_literals(current_records[(13, 408)])[0]
    if source_blank.text or current_blank.text:
        raise RuntimeError("13:408 blank contract drifted")
    if source_records[(13, 389)].data != source_records[(13, 246)].data:
        raise RuntimeError("pristine Base raw duplicate 13:389=13:246 drifted")
    if current_records[(13, 389)].data != current_records[(13, 246)].data:
        raise RuntimeError("current Base raw duplicate 13:389=13:246 drifted")
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
    if TRANSLATIONS["13:389:0"] != '"영내 제책"':
        raise RuntimeError("13:389 prior exact title translation drifted")
    assert_available_duplicate_decision("13:246:0", TRANSLATIONS["13:389:0"])
    if TRANSLATIONS["13:395:0"].splitlines()[:5] != TRANSLATIONS["13:396:0"].splitlines()[:5]:
        raise RuntimeError("13:395/396 shared instructions drifted")
    joined = "\n".join(TRANSLATIONS.values())
    required_terms = (
        "영내 제책",
        "역직",
        "정이대장군",
        "퇴각로",
        "국인중",
        "편입",
        "노동력",
        "지행",
        "지행지",
        "영지",
        "본거지",
    )
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 763 required terminology drifted")
    if "호족" in joined or "관직" in TRANSLATIONS["13:392:0"] or "노력" in joined:
        raise RuntimeError("segment 763 retains a forbidden legacy term")
    if "㌘+㍗" not in TRANSLATIONS["13:396:0"]:
        raise RuntimeError("13:396 controller instruction drifted")
    if len(TRANSLATIONS) != 19 or {int(key.split(":")[1]) for key in TRANSLATIONS} != VISIBLE_RECORD_IDS:
        raise RuntimeError("segment 763 decision/static classification count drifted")


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
                "segment": "base_msggame_B001_S763",
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
