#!/usr/bin/env python3
"""Build Base authoring segment 468 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S468.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s468", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2593:0": "5할, 6할의 승리를 신조로 삼고 있거늘\n전공 제일이라니 쑥스럽구나",
    "7:2594:0": "이 싸움, 이 무공으로……\n천하에 의를 보였는가",
    "7:2595:0": "모리의 싸움에는 빈틈이 없다",
    "7:2596:0": "오슈의 독안룡이란 바로—",
    "7:2596:1": "을(를) 두고 하는 말이지!",
    "7:2597:0": "난세를 비추는 한 줄기 빛이 되리라!",
    "7:2598:0": "어떠냐, 이 몸도 제법이지!",
    "7:2599:0": "내 활약을 능가할 자는 없다!",
    "7:2600:0": "실로 훌륭한 싸움이었다",
    "7:2601:0": "내 활약, 참으로 두드러졌군요",
    "7:2602:0": "무략으로 나와 견줄 자는 없다",
    "7:2603:0": "이번 싸움은 내 손안에 있었도다",
    "7:2604:0": "적도 우리의 강한 군세에 놀랐을 것이다",
    "7:2605:0": "허허허, 아직 젊은이들에게는 지지 않는다!",
    "7:2606:0": "어떻습니까!\n이것이 바로—",
    "7:2606:1": "의 실력입니다!",
    "7:2607:0": "빛나는 승리는 내 손에 있다!",
    "7:2608:0": "우리를 얕본 순간 운이 다한 것,\n그런 셈이겠지요……",
    "7:2609:0": "천하무쌍! 보았느냐, 내 싸움 솜씨를!",
}

PENDING_COORDINATES = {"7:2596:0", "7:2596:1", "7:2606:0", "7:2606:1"}
STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - PENDING_COORDINATES


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S468", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
