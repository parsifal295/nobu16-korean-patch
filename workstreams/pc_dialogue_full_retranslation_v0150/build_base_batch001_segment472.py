#!/usr/bin/env python3
"""Build Base authoring segment 472 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S472.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s472", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2657:0": "전공 제일이라……\n훗,",
    "7:2657:1": "(이)라면 당연한 활약이지",
    "7:2658:0": ", 많은 말은 하지 않겠다\n……훌륭했다",
    "7:2659:0": ", 전공 제일이라니 훌륭하구나\n적을 손바닥 위에 올려놓고 싸웠군",
    "7:2660:0": ", 눈부신 전공이로다\n그대라면 무용 천하제일도 노릴 만하겠구나",
    "7:2661:0": ", 허허 참으로 훌륭하구나\n전공 제일이라니 기쁜 일이로다",
    "7:2662:0": "역시 대단하구나,",
    "7:2662:1": "!\n해내리라 믿고 있었다!",
    "7:2663:0": "전공 제일은 역시",
    "7:2663:1": "인가!\n앞으로도 의지하마",
    "7:2664:0": "과연",
    "7:2664:1": "답구나\n기대 이상의 성과를 내 주었어",
    "7:2665:0": "이(가) 전공 제일이었는가\n나도 이처럼 결과로 말하는 무사가 되고 싶군",
    "7:2666:0": "제법이잖아,",
    "7:2666:1": "!\n나도 질 수는 없지!",
    "7:2667:0": "역시",
    "7:2667:1": "답군!\n전공 제일이라니 제법인데!",
    "7:2668:0": "……전공 제일이라니 참으로 경사스럽구나!\n빛나는 영예에 걸맞은 활약이었다!",
    "7:2669:0": "……참으로 장한 활약이다!\n전공 제일이라니 자랑스럽기 그지없구나",
    "7:2670:0": "장하도다,",
    "7:2670:1": "!\n내 일처럼 기쁘구나",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S472", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
