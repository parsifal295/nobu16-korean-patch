#!/usr/bin/env python3
"""Build Base authoring segment 737 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S737.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s737", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "12:20:0": "뭐라…?\n흐음…",
    "12:20:1": "을(를)\n삼직 중 하나에 앉히고 싶다, 그 말인가?",
    "12:21:0": "뭐, 뭐라고!\u3000삼직이라 하면\n「태정대신」「관백」「정이대장군」…!\n어찌 답해야 할",
    "12:21:1": "까…",
    "12:22:0": "그리 당황하",
    "12:22:1": "\n허나, 그렇군,",
    "12:22:2": "의 대답은…",
    "12:23:0": "은(는) 관백에 취임하고자 한다",
    "12:24:0": "참으로 훌륭하신 결단이옵니다!\n곧바로 조정에 답신을 올리겠습니다.",
    "12:25:0": "은(는) 태정대신에 취임하고자 한다",
    "12:26:0": "참으로 훌륭하신 결단이옵니다!\n곧바로 조정에 답신을 올리겠습니다.",
    "12:27:0": "은(는) 정이대장군에 취임하고자 한다",
    "12:28:0": "참으로 훌륭하신 결단이옵니다!\n곧바로 조정에 답신을 올리겠습니다.",
    "12:29:0": "취임할 관직을 선택해 주십시오",
    "12:30:0": "관백",
    "12:31:0": "태정대신",
    "12:32:0": "정이대장군",
    "12:33:0": "사양한다",
    "12:34:0": "에 취임하는 엔딩을 맞이하며\n게임을 종료합니다\n괜찮으시겠습니까?",
    "12:35:0": "삼직 취임을 사양하고 게임을 계속하시겠습니까?\n조정의 요청은 다시 올 수도 있습니다",
    "12:36:0": "당신의 다이묘 가문은 모든 성을 잃었습니다\n당신의 야망도 여기까지입니다",
    "12:37:0": "당신의 다이묘 가문을 이을 자가 없었습니다\n당신의 야망도 여기까지입니다",
}

RUNTIME_RECORD_IDS = {20, 22, 23, 25, 27, 34}
DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in RUNTIME_RECORD_IDS
}
SOURCE_INFLECTION_REMOVED_RECORD_IDS = {21, 24, 26, 28}


def assert_runtime_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id in RUNTIME_RECORD_IDS - {34}:
        if b"\x01\x43" not in current_records[(12, record_id)].data:
            raise RuntimeError(f"expected live 0143 runtime opcode is absent: 12:{record_id}")
    if b"\x02\x3c" not in current_records[(12, 34)].data:
        raise RuntimeError("expected selected-office token is absent: 12:34")
    for record_id in SOURCE_INFLECTION_REMOVED_RECORD_IDS:
        if b"\x01\x43" not in source_records[(12, record_id)].data:
            raise RuntimeError(f"pristine inflection opcode is absent: 12:{record_id}")
        if b"\x01\x43" in current_records[(12, record_id)].data:
            raise RuntimeError(f"removed inflection opcode unexpectedly survives: 12:{record_id}")
    if TRANSLATIONS["12:21:0"].count("\u3000") != 1:
        raise RuntimeError("12:21:0 must restore exactly one U+3000 separator")
    duplicate_source_records = [source_records[(12, record_id)].data for record_id in (24, 26, 28)]
    if len(set(duplicate_source_records)) != 1:
        raise RuntimeError("12:24/26/28 pristine records are no longer raw-identical")
    duplicate_translations = [TRANSLATIONS[f"12:{record_id}:0"] for record_id in (24, 26, 28)]
    if len(set(duplicate_translations)) != 1:
        raise RuntimeError("12:24/26/28 translations must remain exact")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_runtime_scope(prepared)
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
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
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
                "segment": "base_msggame_B001_S737",
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
