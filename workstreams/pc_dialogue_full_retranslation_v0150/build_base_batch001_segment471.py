#!/usr/bin/env python3
"""Build Base authoring segment 471 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S471.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s471", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2645:0": "설마",
    "7:2645:1": "에게 전공으로 지다니……\n오늘부터 훈련을 두 배로 늘리겠다!",
    "7:2646:0": "이(가) 전공 제일입니까……\n",
    "7:2646:1": "에게도 더 큰 힘이 있었다면……",
    "7:2647:0": "아아……",
    "7:2647:1": "보다 못한 처지가 되다니\n분하구나……",
    "7:2648:0": "이(가) 전공 제일이라고!?\n그자에게 뒤처지다니 분하군……",
    "7:2649:0": "에게 공으로 뒤졌는가\n다음에는 질 수 없겠군……",
    "7:2650:0": "과연 대단하군,",
    "7:2650:1": "\n그래야 내 등을 맡길 만하지",
    "7:2651:0": "전공 제일이라니 장하도다,",
    "7:2651:1": "!\n천하에 이름을 떨쳤구나",
    "7:2652:0": "대단하구나,",
    "7:2652:1": "!\n다음에도 기대하마!",
    "7:2653:0": "오오,",
    "7:2653:1": "이(가) 가장 앞장섰는가!\n내 일처럼 기쁘구나!",
    "7:2654:0": ", 장하도다\n그 무용이 있다면 든든하구나",
    "7:2655:0": "이(가) 전공 제일이라니 더없이 기쁘구나\n앞으로도 무예에 힘쓰거라",
    "7:2656:0": "훌륭하구나,",
    "7:2656:1": "\n앞으로도 서로 절차탁마해 나가자",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S471", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
