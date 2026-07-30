#!/usr/bin/env python3
"""Build Base authoring segment 676 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S676.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s676", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2606:0": "원호하기에는 너무 멀군요\n포진 위치를 바꾸겠습니다",
    "9:2607:0": "전황이 보이지 않는군\n앞으로 나아간다!",
    "9:2608:0": "포진 위치가 좋지 않군\n움직이기 좋은 곳으로 나간다",
    "9:2609:0": "여기서는 지원할 수 없다\n우리도 앞으로 나간다",
    "9:2610:0": "원호하기에는 멀구나\n앞으로 나아가자",
    "9:2611:0": "지원하기에는 멀군요\n전진합시다!",
    "9:2612:0": "전선에서 너무 멀어졌다\n이동을 시작하라!",
    "9:2613:0": "적에게서 너무 멀어졌습니다\n이동하겠습니다!",
    "9:2614:0": "여기서는 지원할 수 없다\n우리도 앞으로 나간다",
    "9:2615:0": "이(가) 기마대로 돌격",
    "9:2616:0": "기마대, 돌격!\n들이쳐라!",
    "9:2617:0": "기마대, 전진!\n베어 무너뜨려라!",
    "9:2618:0": "기마대, 전진하라!\n적진에 쐐기를 박아라!",
    "9:2619:0": "기마대를 앞으로!\n적진으로 베어 들어가세요!",
    "9:2620:0": "기마대, 돌진하라!\n모조리 쓸어버려라!",
    "9:2621:0": "기마대, 앞으로!\n적진에 돌격하라!",
    "9:2622:0": "기마대, 준비하라!\n돌격 개시!",
    "9:2623:0": "기마대, 나아가라!\n모조리 짓밟아라!",
    "9:2624:0": "기마대, 공격!\n적진을 무너뜨리겠습니다!",
    "9:2625:0": "기마대, 전력 돌격!\n힘으로 제압하라!",
    "9:2626:0": "기마대, 나아가세요!\n그대로 돌파하는 겁니다!",
    "9:2627:0": "기마대, 가라!\n들이쳐 무너뜨려라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2615:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
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
                "segment": "base_msggame_B001_S676",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
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
