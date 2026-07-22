#!/usr/bin/env python3
"""Build Base authoring segment 255 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S255.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s255", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4048:0": "동맹이나 원군 등의 교섭을 위해 다른 세력의 신용을 높입니다",
    "6:4049:0": "신용을 소비하여 동맹이나 정전을 맺습니다",
    "6:4050:0": "조정에 헌금하여 신용을 높이고 관직을 받습니다",
    "6:4051:0": "여러 다이묘를 막부 역직에 임명하여 외교 자세를 개선합니다",
    "6:4052:0": "이제부터",
    "6:4052:1": "을(를) 본거지로 정하",
    "6:4052:2": "\n그 땅을 우리 가문의 중심으로 삼아 번영시키",
    "6:4053:0": "금전 수지가 악화되어 재정이 어려워집니다\n이대로 본거지를 이전해도 괜찮겠습니까?",
    "6:4054:0": "의",
    "6:4054:1": "장악이 완료",
    "6:4055:0": "이(가)",
    "6:4055:1": "명의 병력으로",
    "6:4055:2": "으로(로) 진군 중",
    "6:4056:0": "이(가)",
    "6:4056:1": "명의 병력으로",
    "6:4056:2": "의 적과",
    "6:4056:3": "에서 전투 중",
    "6:4057:0": "의",
    "6:4057:1": "이(가)",
    "6:4057:2": "명의 병력으로 영내의",
}

STATIC_COORDINATES: set[str] = {
    "6:4048:0",
    "6:4049:0",
    "6:4050:0",
    "6:4051:0",
    "6:4053:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S255", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
