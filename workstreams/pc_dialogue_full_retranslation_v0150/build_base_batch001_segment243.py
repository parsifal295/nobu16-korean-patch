#!/usr/bin/env python3
"""Build Base authoring segment 243 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S243.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s243", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3911:0": "아우의 원수로 여겨\n원한을 품고 있다",
    "6:3912:0": "가족의 원수로 여겨\n원한을 품고 있다",
    "6:3913:0": "지금 한창\n전쟁 중인 적이다",
    "6:3914:0": "칼을 맞댄 지 얼마 되지 않아\n경계하고 있다",
    "6:3915:0": "조략을 당해\n강하게 경계하고 있다",
    "6:3916:0": "을(를)\n혐오하고 있다",
    "6:3917:0": "동맹국이 있는\n우리 가문을 경계하고 있다",
    "6:3918:0": "와(과)는\n마음이 맞지 않는다",
    "6:3919:0": "우리 가문을 방패 삼아\n중개한 지 얼마 되지 않았다",
    "6:3920:0": "어느 역직을 내리시겠습니까?",
    "6:3921:0": "좋다",
    "6:3921:2": "을(를)",
    "6:3921:3": "에게 내린다고",
    "6:3921:4": "\n막부에 대한 충근을 기대",
    "6:3922:0": "에서",
    "6:3922:1": "의 건설을 시작",
    "6:3923:0": "에서",
    "6:3923:1": "의 건설을 중단",
    "6:3924:0": "에서",
    "6:3924:1": "의 건설을 완료",
}

STATIC_COORDINATES: set[str] = {
    "6:3911:0",
    "6:3912:0",
    "6:3913:0",
    "6:3914:0",
    "6:3915:0",
    "6:3917:0",
    "6:3919:0",
    "6:3920:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S243", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
