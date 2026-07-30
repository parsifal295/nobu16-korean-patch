#!/usr/bin/env python3
"""Build Base authoring segment 753 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S753.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s753", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "13:182:0": "의 생각은 알겠다\n요컨대…",
    "13:183:0": "가신에게 영지를 내리고\n영내를 발전시켜 힘을 기른 뒤,\n그 힘으로 적의 영지를 빼앗으라는 말이군",
    "13:184:0": "그렇습니다\n우선 국력을 높이기 위해\n지행과 내정부터 시작해야 할 줄로 아옵니다",
    "13:185:0": "앞으로는 고쇼가 자세히 설명해 드리도록\n일러두었으니,\n그 설명을 참고해 주십시오",
    "13:186:0": "좋다!　이를 바탕으로\n군을, 그리고 나라를 강하게 만들자!\n모두 함께 나아가자!",
    "13:187:0": "말할 것도 없다!　우리의 명운은\n",
    "13:187:1": "와(과) 함께하옵니다\n무엇이든 명해 주십시오!",
    "13:188:0": "용맹한 말이로다!　훌륭한 가신들의 진언도\n적극적으로 받아들이겠다!\n뜻을 하나로 모아 천하통일을 향해 매진하겠다!",
    "13:189:0": "예!\n",
    "13:189:1": "의 야망을 반드시 이루어 내겠습니다!",
    "13:190:0": "외람되오나 나라를 강하게 하기 위해\n우선 해야 할 일을 제가 진언드리겠습니다",
    "13:191:0": "영지 경영의 기초를 알려 드릴 테니\n도움이 되기를 바랍니다",
    "13:192:0": "먼저 화면 왼쪽의 행동 목록에서\n",
    "13:192:1": "┨",
    "13:192:2": "이(가) 표시된 건의를\n선택해 주십시오",
    "13:193:0": "㍍를 누른 채 ㌣를 기울여\n'행동 목록'을 선택한 뒤\n㍍에서 손을 떼면 커서가 행동 목록을 가리킵니다",
    "13:194:0": "㍍㎝㌣으로 '행동 목록' 선택",
    "13:195:0": "㍑으로",
    "13:195:1": "┨",
    "13:195:2": "이(가) 표시된 건의를 선택",
    "13:196:0": "이처럼 '다음에 해야 할 일'이\n건의됩니다",
    "13:197:0": "또한 명령을 실행하면\n내용 설명이 다시 표시됩니다\n조작 안내에 따라 직접 해 봅시다",
    "13:198:0": "게임 전체의 개요는 행동 목록에서\n'기본 사항'을 선택하면 확인할 수 있습니다\n기본을 알고 싶다면 살펴봅시다",
    "13:199:0": "이제 어느 정도 익숙해지셨습니까?\n가신들이 의견을 내고 싶어 하니\n앞으로는 건의와 조언을 드리겠습니다",
    "13:200:0": "건의된 내용은\n화면 왼쪽의 행동 목록에 나열되니\n시간이 날 때 확인해 주십시오",
    "13:201:0": "건의에 관한 자세한 설명은 화면 오른쪽 위의\n'도움말　>　용어　>　건의'\n에서 확인할 수 있습니다",
}

RUNTIME_RECORD_IDS = {182, 187, 189}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
EXPECTED_CURRENT_GAPS: dict[int, tuple[bytes, ...]] = {
    182: (b"\x01\x43\x08\x00\x00\x00", b"\x05\x05\x05"),
    187: (b"", b"\x02\x50\x32", b"\x05\x05\x05"),
    189: (b"", b"\x02\x50\x32", b"\x05\x05\x05"),
}
EXPECTED_STATIC_COLOUR_GAPS: dict[int, tuple[bytes, ...]] = {
    192: (b"", b"\x1b\x43\x50", b"\x1b\x43\x5a", b"\x05\x05\x05"),
    195: (b"", b"\x1b\x43\x50", b"\x1b\x43\x5a", b"\x05\x05\x05"),
}
A_EXACT_REUSE: dict[int, int] = {
    186: 131,
    187: 132,
    188: 134,
    189: 135,
}
A_EXACT_TRANSLATIONS = {
    "13:186:0": "좋다!\u3000이를 바탕으로\n군을, 그리고 나라를 강하게 만들자!\n모두 함께 나아가자!",
    "13:187:0": "말할 것도 없다!\u3000우리의 명운은\n",
    "13:187:1": "와(과) 함께하옵니다\n무엇이든 명해 주십시오!",
    "13:188:0": "용맹한 말이로다!\u3000훌륭한 가신들의 진언도\n적극적으로 받아들이겠다!\n뜻을 하나로 모아 천하통일을 향해 매진하겠다!",
    "13:189:0": "예!\n",
    "13:189:1": "의 야망을 반드시 이루어 내겠습니다!",
}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」")


def record_gaps(record: Any) -> tuple[bytes, ...]:
    gaps: list[bytes] = []
    cursor = 0
    for literal in ENGINE.parse_record_literals(record):
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def assert_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in {**EXPECTED_CURRENT_GAPS, **EXPECTED_STATIC_COLOUR_GAPS}.items():
        if record_gaps(source_records[(13, record_id)]) != expected:
            raise RuntimeError(f"pristine literal/opcode boundary drift: 13:{record_id}")
        if record_gaps(current_records[(13, record_id)]) != expected:
            raise RuntimeError(f"current literal/opcode boundary drift: 13:{record_id}")
    for target_id, prior_id in A_EXACT_REUSE.items():
        if source_records[(13, target_id)].data != source_records[(13, prior_id)].data:
            raise RuntimeError(f"B092-A exact source reuse drift: 13:{target_id} != 13:{prior_id}")
    for coordinate, expected in A_EXACT_TRANSLATIONS.items():
        if TRANSLATIONS[coordinate] != expected:
            raise RuntimeError(f"B092-A exact translation reuse drift: {coordinate}")
    expected_u3000 = {
        "13:186:0": 1,
        "13:187:0": 1,
        "13:188:0": 1,
        "13:201:0": 4,
    }
    for coordinate, expected in expected_u3000.items():
        if TRANSLATIONS[coordinate].count("\u3000") != expected:
            raise RuntimeError(f"U+3000 restoration drift: {coordinate}")
    actual_u3000 = {
        coordinate: translation.count("\u3000")
        for coordinate, translation in TRANSLATIONS.items()
        if "\u3000" in translation
    }
    if actual_u3000 != expected_u3000:
        raise RuntimeError(f"segment 753 U+3000 scope drift: {actual_u3000}")
    if TRANSLATIONS["13:187:0"].count("\n") != 1 or not TRANSLATIONS["13:187:0"].endswith("\n"):
        raise RuntimeError("13:187:0 must preserve its trailing LF")
    if TRANSLATIONS["13:189:0"].count("\n") != 1 or not TRANSLATIONS["13:189:0"].endswith("\n"):
        raise RuntimeError("13:189:0 must preserve its trailing LF")
    if TRANSLATIONS["13:192:0"].count("\n") != 1 or not TRANSLATIONS["13:192:0"].endswith("\n"):
        raise RuntimeError("13:192:0 must preserve its trailing LF")
    for translation in TRANSLATIONS.values():
        if "\r" in translation or BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError("segment 753 retains CR or banned fullwidth punctuation")


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
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_jp_en_sc_tc_context"
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
                "segment": "base_msggame_B001_S753",
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
