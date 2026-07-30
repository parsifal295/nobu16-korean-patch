#!/usr/bin/env python3
"""Build Base authoring segment 188 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S188.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s188", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3297:0": "을(를) 잃을 수는 없습니다\n무슨 일이 있어도 지켜 주십시오",
    "6:3298:0": "을(를) 빼앗길 수는 없다\n수비를 부탁한다…",
    "6:3299:0": "을(를) 잃으면 큰일이 날 것입니다…\n부디 적을 막아 주십시오",
    "6:3300:0": "은(는) 우리에게 없어서는 안 될 땅이오\n끝까지 지켜 주시오",
    "6:3301:0": "소지금이 부족하여 조정과 교섭할 수 없습니다",
    "6:3302:0": "우리 가문은 조정과 교섭한 지 얼마 되지 않았습니다",
    "6:3303:0": "금전이 부족하여 조정에 주청할 수 있는 항목이 없습니다",
    "6:3304:0": "위신이 부족하여 조정에 주청할 수 있는 항목이 없습니다",
    "6:3305:0": "조정에 주청할 수 있는 항목이 없습니다",
    "6:3306:0": "다른 항목과 동시에 주청할 수 없습니다",
    "6:3307:0": "우리 가문의 악명이 높아 관직을 내려 주지 않을 듯합니다",
    "6:3308:0": "우리 가문은 관직을 주청할 만큼 규모가 크지 않습니다",
    "6:3309:0": "주청할 수 있는 관직이 없습니다",
    "6:3310:0": "다른 항목과 동시에 주청할 수 없습니다",
    "6:3311:0": "다른 가문에 종속되어 있어 칙명 강화를 요청할 수 없습니다",
    "6:3312:0": "우리 가문의 악명이 높아 칙명 강화를 주청할 수 없습니다",
    "6:3313:0": "다른 항목과 동시에 주청할 수 없습니다",
    "6:3314:0": "악명을 낮출 필요가 없습니다",
    "6:3315:0": "다른 항목과 동시에 주청할 수 없습니다",
    "6:3316:0": "우리 가문은 이미 조정에 충분히 공헌했습니다",
}

STATIC_COORDINATES: set[str] = {
    "6:3301:0", "6:3302:0", "6:3303:0", "6:3304:0", "6:3305:0", "6:3306:0",
    "6:3307:0", "6:3308:0", "6:3309:0", "6:3310:0", "6:3311:0", "6:3312:0",
    "6:3313:0", "6:3314:0", "6:3315:0", "6:3316:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S188", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
