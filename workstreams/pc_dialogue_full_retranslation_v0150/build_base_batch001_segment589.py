#!/usr/bin/env python3
"""Build Base authoring segment 589 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S589.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s589", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:838:0": "을(를) 격파하다니\n장하다, 참으로 장하다!",
    "9:839:0": "따위는\n상대도 안 되지!",
    "9:840:0": "의 활약은\n역시 대단하구나!",
    "9:841:0": "훌륭한 활약이다\n",
    "9:841:1": "도 지지 않겠다",
    "9:842:0": "역시 훌륭한 활약이군요\n본보기로 삼고 싶습니다",
    "9:843:0": "훌륭한 활약을 하는군\n장하도다!",
    "9:844:0": "후후…… 좋은 활약을\n펼쳐 주는구나",
    "9:845:0": "눈부신 무공이로다!",
    "9:846:0": "오오, 과연 대단하구나!",
    "9:847:0": "대단합니다―",
    "9:847:1": "을(를)\n압도했군요!",
    "9:848:0": "제법이군!\n",
    "9:848:1": "도 질 수는 없다!",
    "9:849:0": "훌륭합니다!\n정말 잘해 주셨습니다",
    "9:850:0": "!\n가는 곳마다 적수가 없구나",
    "9:851:0": "미안하다\n뒤는 맡겼다!",
    "9:852:0": "미안하오!\n뒤는 부탁드리오!",
    "9:853:0": "먼저 물러나겠다……\n뒤는 맡겼다",
    "9:854:0": "죄송합니다……\n먼저 철수하겠습니다",
    "9:855:0": "전장을 떠나야\n하다니…… 분하구나",
}

STATIC_COORDINATES: set[str] = {
    "9:842:0",
    "9:843:0",
    "9:844:0",
    "9:845:0",
    "9:846:0",
    "9:849:0",
    "9:851:0",
    "9:852:0",
    "9:853:0",
    "9:854:0",
    "9:855:0",
}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S589", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
