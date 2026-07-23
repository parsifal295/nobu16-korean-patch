#!/usr/bin/env python3
"""Build Base authoring segment 719 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S719.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s719", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3486:0": "퇴각로를 파괴해 승기를 잡는다",
    "9:3487:0": "목표 변경, 퇴각로를 먼저 파괴한다\n허둥댈 놈들의 얼굴이 눈에 선하군",
    "9:3488:0": "퇴각로가 노릴 만하겠군\n퇴로를 잃으면 적도 동요하겠지",
    "9:3489:0": "정면 대결만이 싸움의 전부는 아니다!\n퇴각로를 파괴해 퇴로를 끊으리라!",
    "9:3490:0": "목표를 퇴각로로 바꾸겠습니다\n퇴로를 막으면 유리하게 싸울 수 있습니다!",
    "9:3491:0": "먼저 퇴각로를 파괴하리라!\n퇴로만 끊으면 어려울 것도 없다",
    "9:3492:0": "목표를 퇴각로로 바꾸겠습니다\n퇴로를 막으면 우위를 점할 수 있습니다",
    "9:3493:0": "목표를 적의 퇴각로로 바꾼다\n퇴로만 막으면 손쉽게 이기리라",
    "9:3494:0": ", 지원하러 가겠다!\n그때까지 버텨 다오!",
    "9:3495:0": "지원이 필요한 듯하군\n",
    "9:3495:1": ", 곧 가겠다. 잠시 기다려라!",
    "9:3496:0": "지원이 필요한 듯하오\n",
    "9:3496:1": ", 곧 가겠소. 잠시 기다리시오!",
    "9:3497:0": "이제 지원하러 간다!\n조금만 더 버텨 다오!",
    "9:3498:0": "이제 지원하러 가겠습니다!\n조금만 더 버텨 주십시오!",
    "9:3499:0": "저희가 지원하겠습니다\n어떻게든 버텨 주십시오",
    "9:3500:0": ", 지원에 나서겠다!\n마음을 굳게 먹어라!",
    "9:3501:0": ", 지원하겠소!\n마음을 굳게 가지시오!",
    "9:3502:0": "지원은 맡겨라!\n당장 그리로 가겠다!",
    "9:3503:0": "지원은 맡겨 주십시오!\n당장 그리로 가겠습니다!",
    "9:3504:0": ", 원호를 맡겠다\n조금만 더 버텨 다오!",
    "9:3505:0": ", 원호를 맡겠습니다\n조금만 더 버텨 주십시오!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:3494:0",
    "9:3495:0",
    "9:3495:1",
    "9:3496:0",
    "9:3496:1",
    "9:3500:0",
    "9:3501:0",
    "9:3504:0",
    "9:3505:0",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
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
                "segment": "base_msggame_B001_S719",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
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
