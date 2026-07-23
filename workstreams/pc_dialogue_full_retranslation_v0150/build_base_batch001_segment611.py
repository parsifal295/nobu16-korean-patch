#!/usr/bin/env python3
"""Build Base authoring segment 611 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S611.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s611", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1316:0": "크윽, 불찰이다!",
    "9:1317:0": "말도 안 돼…… 아군의 계략에\n휘말리다니",
    "9:1318:0": "을(를) 희생시켜\n수공을……!?",
    "9:1319:0": "이런……\n휘말렸…… 윽!",
    "9:1320:0": "너무 가까이 다가갔군요……",
    "9:1321:0": "경솔했군……!\n아군의 계략에 걸리다니",
    "9:1322:0": "에게까지\n피해가 미치다니……",
    "9:1323:0": "어…… 어째서\n",
    "9:1323:1": "까지……",
    "9:1324:0": "아파!\n돌이 쏟아져 내리잖아!",
    "9:1325:0": "큭!\n바위라고!?",
    "9:1326:0": "낙석 따위에\n겁먹지 마라!",
    "9:1327:0": "낙석인가…… 머리 위를\n조심해야 합니다!",
    "9:1328:0": "으아악!\n모두 버텨라!",
    "9:1329:0": "낙석계에 당하다니……\n불찰이로다!",
    "9:1330:0": "큭!\n바위가 빗발치듯……!",
    "9:1331:0": "이놈!\n비겁하구나!",
    "9:1332:0": "낙석!?\n당황하지 마!",
    "9:1333:0": "돌이 쏟아진다고!?",
    "9:1334:0": "낙석에 모두가\n동요하고 있군요……",
    "9:1335:0": "우와아앗!\n이놈, 돌이 비처럼 쏟아지는군……!",
    "9:1336:0": "다리가 불타 버렸다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1318:0",
    "9:1322:0",
    "9:1323:0",
    "9:1323:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S611", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
