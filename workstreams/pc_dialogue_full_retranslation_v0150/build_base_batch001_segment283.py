#!/usr/bin/env python3
"""Build Base authoring segment 283 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S283.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s283", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4311:0": "의 「",
    "6:4311:1": "」을(를) LV",
    "6:4311:2": "까지 증축",
    "6:4312:0": "이(가) 주도하는 건설을 돕습니다",
    "6:4313:0": "이(가) 주도하는 건설을 중단합니다",
    "6:4314:0": "이(가) 주도하는 건설을 중단합니다\n정말 괜찮으시겠습니까?",
    "6:4315:0": "성주를 중개자로 지명하는 동안에는\n자신의 성에서 내정을 하지 않게 됩니다\n괜찮으시겠습니까?",
    "6:4316:0": "자신의 세력에 속한 성은 선택할 수 없습니다",
    "6:4317:0": "아군 세력의 성은 선택할 수 없습니다",
    "6:4318:0": "의뢰 대상 측 아군 세력의 성은 선택할 수 없습니다",
    "6:4319:0": "의뢰 대상이 이미 공격 중인 성은 선택할 수 없습니다",
    "6:4320:0": "이미 원군을 요청한 성은 선택할 수 없습니다",
    "6:4321:0": "상대가 원군을 요청한 성은 선택할 수 없습니다",
    "6:4322:0": "그 성에 원군으로 보낼 병력을 확보할 수 없습니다",
    "6:4323:0": "우리 세력이나 의뢰 대상과 인접하지 않은 성은 선택할 수 없습니다",
    "6:4324:0": "우리 세력 또는 종속 세력의 성만 선택할 수 있습니다",
    "6:4325:0": "의뢰 대상 세력에 인접한 성만 선택할 수 있습니다",
    "6:4326:0": "그 성에 원군으로 보낼 병력을 확보할 수 없습니다",
    "6:4327:0": "적이 공격 중인 성만 선택할 수 있습니다",
    "6:4328:0": "은(는) 임무「",
}

STATIC_COORDINATES: set[str] = {
    "6:4315:0", "6:4316:0", "6:4317:0", "6:4318:0", "6:4319:0", "6:4320:0", "6:4321:0",
    "6:4322:0", "6:4323:0", "6:4324:0", "6:4325:0", "6:4326:0", "6:4327:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S283", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
