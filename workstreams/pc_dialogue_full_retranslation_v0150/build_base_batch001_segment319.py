#!/usr/bin/env python3
"""Build Base authoring segment 319 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S319.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s319", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:334:0": "을(를) 비롯한 총",
    "7:334:1": "명의 등용에 실패했습니다",
    "7:335:0": "멸하지 않을 자가 있으랴",
    "7:336:0": "내 주검을 넘어 나아가라",
    "7:337:0": "꿈을 이루기도 전에 스러지다니…",
    "7:338:0": "각오는 되어 있다, 어서 하거라!",
    "7:339:0": "내 대망을 끝내 이루지 못하는가…",
    "7:340:0": "저승에서 귀공을 기다리겠노라",
    "7:341:0": "내 길이 이리 끊기다니…",
    "7:342:0": "황천길에서 기다리마",
    "7:343:0": "이 얼마나 원통한 일인가",
    "7:344:0": "먼저 가마",
    "7:345:0": "내 계략도 여기까지인가…",
    "7:346:0": "저승이라는 곳에서 기다리마",
    "7:347:0": "용이 땅에 떨어졌구나…",
    "7:348:0": "내 목을 가져가라!",
    "7:349:0": "뜻을 이루지 못하고 스러지다니…",
    "7:350:0": "여기가 나의 최후인가…",
    "7:351:0": "좋아, 목을 베어라!",
    "7:352:0": "지옥에서 기다려 주마!",
}

STATIC_COORDINATES: set[str] = {
    "7:335:0", "7:336:0", "7:337:0", "7:338:0", "7:339:0", "7:340:0", "7:341:0", "7:342:0",
    "7:343:0", "7:344:0", "7:345:0", "7:346:0", "7:347:0", "7:348:0", "7:349:0", "7:350:0",
    "7:351:0", "7:352:0",
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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S319", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
