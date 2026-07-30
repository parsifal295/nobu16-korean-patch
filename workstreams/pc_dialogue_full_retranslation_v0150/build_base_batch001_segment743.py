#!/usr/bin/env python3
"""Build Base authoring segment 743 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S743.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s743", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:8:0": (
        "\n다이묘는 본래 영지에서 쌀 등의 농산물을 '연공'\n"
        "으로 거두어 수입으로 삼았다.\n"
        "그러나 영지를 '지행지'로 가신에게 나누어 주었기에\n"
        "연공은 남은 직할지에서만 거둘 수 있었다.\n"
        "\n"
        "이에 다이묘는 본래 임시 수입이었던 단전·동별전·\n"
        "관전 등을 상시 부과하기로 했다.\n"
        "유력 다이묘라면 가신과 국인, 사찰과 신사를 포함해 영내\n"
        "모든 토지에 두루 세금을 부과할 수 있었기에 그 액수는\n"
        "연공 수입을 훨씬 웃돌았다고 한다.\n"
        "\n"
        "더 나아가 상업을 활성화하고 광산 개발 등을 추진하여\n"
        "수익, 곧 권력 기반을 강화해 갔다.\n"
        "가신에게는 소령 안도를 약속하는 한편, 전쟁 때에는 병사와\n"
        "무기, 병량 등을 스스로 마련하게 하는 군역을 부과했다.\n"
        "이것이 '전국 다이묘'의 탄생이다.\n"
        "\n"
        "한정된 재원과 노동력을 어떻게 늘리고 가신단을\n"
        "어떻게 통제할 것인가... 당신의 수완이 시험대에 오른다."
    ),
    "13:9:0": "모두 수고했다!\n지금부터 평정을 시작한다!\n고개를 들라!",
    "13:12:0": "들으라!\n우리 가문은 이제부터 천하통일에 나선다!\n각자 마음껏 계책을 내놓아라!",
    "13:13:0": "분부대로 하겠습니다!",
    "13:14:0": "지금부터 평정을 시작한다!",
    "13:15:0": "우리 가문은 아직 강대한 세력이라 할 수 없으나\n나의 야망은 이 땅에 머무르지 않는다!\n이제부터 '",
    "13:15:1": "'은(는) 천하를 노린다!",
    "13:16:0": "우리 가문은 전국에서도 손꼽히는 세력이 되었으나\n그것만으로 만족해서는 안 된다!\n",
    "13:16:1": "은(는) 어디까지나 천하통일을 노린다!",
    "13:17:0": "처, 천하를!?\n이건... 참으로 원대한 포부이십니다.\n하지만 그렇기에 보필할 보람도 있겠지요.",
    "13:18:0": "당장 우리 가문에 필요한 것은\n병력, 병량, 금전!\n더 나아가 강국과 동맹을 맺고...",
    "13:19:0": "아니, 그 모든 일을 한꺼번에 추진하기는 어렵다고\n사료되옵니다. 우선 필요한 일부터 차례대로...\n다만 지침이 없으면 가신들도 건의하기 어렵지 않겠습니까?",
    "13:20:0": "좋아, 그렇다면 우선\n우리 가문이 처한 상황부터 확인해 볼까\n지도를 가져오너라!",
    "13:21:0": "예!",
    "13:22:0": "우리 가문이 목표로 삼아야 할 것은\n",
    "13:22:1": "을(를) 쓰러뜨리는 일이라 사료되옵니다\n우선은 '",
    "13:22:2": "'부터 공격하는 것이 어떠하신지",
}

RUNTIME_RECORD_IDS = {15, 16, 22}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_LITERAL_COUNTS = {
    9: (2, 1),
    17: (2, 1),
}
BLANK_RECORD_IDS = {7, 10, 11}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」")


def assert_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in EXPECTED_LITERAL_COUNTS.items():
        actual = (
            len(ENGINE.parse_record_literals(source_records[(13, record_id)])),
            len(ENGINE.parse_record_literals(current_records[(13, record_id)])),
        )
        if actual != expected:
            raise RuntimeError(f"literal-count mapping drift at 13:{record_id}: {actual}")
    for record_id in BLANK_RECORD_IDS:
        literals = ENGINE.parse_record_literals(current_records[(13, record_id)])
        if any(ENGINE.is_visible_translation_candidate(literal.text) for literal in literals):
            raise RuntimeError(f"expected blank record became visible: 13:{record_id}")
    for record_id in (15, 16):
        if b"\x01\x43" not in current_records[(13, record_id)].data:
            raise RuntimeError(f"expected live 0143 token is absent: 13:{record_id}")
    for opcode in (b"\x02\x50\x32", b"\x02\x64\x32", b"\x01\x43"):
        if opcode not in current_records[(13, 22)].data:
            raise RuntimeError(f"expected live token is absent from 13:22: {opcode.hex()}")
    for translation in TRANSLATIONS.values():
        if "\u3000" in translation or "\r" in translation:
            raise RuntimeError("segment 743 must not add U+3000 or CR")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 743 retains banned fullwidth punctuation")
    if TRANSLATIONS["13:8:0"].count("\n") != 19:
        raise RuntimeError("13:8 must remain a 20-line historical explanation")
    required_historical_terms = {
        "연공",
        "지행지",
        "단전",
        "동별전",
        "관전",
        "국인",
        "소령 안도",
        "군역",
    }
    missing_terms = {
        term for term in required_historical_terms if term not in TRANSLATIONS["13:8:0"]
    }
    if missing_terms or "국인중" in TRANSLATIONS["13:8:0"] or "호족" in TRANSLATIONS["13:8:0"]:
        raise RuntimeError(f"13:8 historical terminology drifted: missing={sorted(missing_terms)}")
    if "지침" not in TRANSLATIONS["13:19:0"] or "건의" not in TRANSLATIONS["13:19:0"]:
        raise RuntimeError("13:19 must preserve 指針=지침 and 具申=건의")
    if any("당가" in translation for translation in TRANSLATIONS.values()):
        raise RuntimeError("segment 743 must use 우리 가문 for 当家")


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
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_same_coordinate_pk_jp_en_sc_tc_context_where_available"
                ),
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
                "segment": "base_msggame_B001_S743",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
