#!/usr/bin/env python3
"""Build Base authoring segment 273 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S273.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s273", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4196:0": "금전 수입을 늘리기 위해\n상업을 진흥하",
    "6:4197:0": "침공에 대비해 외벽 수복을 명하고\n성의 내구를 회복하",
    "6:4198:0": "세력 내 유망한 낭인을\n찾아내 등용하",
    "6:4199:0": "실행 가능한 다이묘 또는 특성「",
    "6:4199:1": "」을(를) 가진 무장이 없습니다",
    "6:4200:0": "실행 가능한 다이묘·성주·측근이 없습니다",
    "6:4201:0": "금전이 부족합니다",
    "6:4202:0": "노동력이 부족합니다",
    "6:4203:0": "인접한 성에서 빼내 올 수 있는 무장이 없습니다",
    "6:4204:0": "회유할 수 있는 국인중이 없습니다",
    "6:4205:0": "편입할 수 있는 국인중이 없습니다",
    "6:4206:0": "선동을 실행할 수 있는 인접 성이 없습니다 ",
    "6:4207:0": "파괴를 실행할 수 있는 인접 성이 없습니다",
    "6:4208:0": "막부 또는 인접 세력에 공물을 보낼 수 있는 성이 없습니다",
    "6:4209:0": "방화를 실행할 수 있는 인접 성이 없습니다",
    "6:4210:0": "유언비어를 퍼뜨릴 수 있는 인접 성이 없습니다",
    "6:4211:0": "장악을 더 진행할 수 있는 성이 없습니다",
    "6:4212:0": "장악을 더 진행할 수 있는 성이 없습니다",
    "6:4213:0": "내구가 감소한 성이 없습니다",
    "6:4214:0": "\n어떤 지시를 전하",
}

STATIC_COORDINATES: set[str] = {
    "6:4200:0", "6:4201:0", "6:4202:0", "6:4203:0", "6:4204:0", "6:4205:0", "6:4206:0",
    "6:4207:0", "6:4208:0", "6:4209:0", "6:4210:0", "6:4211:0", "6:4212:0", "6:4213:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S273", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
