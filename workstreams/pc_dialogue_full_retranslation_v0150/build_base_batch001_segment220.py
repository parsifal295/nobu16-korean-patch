#!/usr/bin/env python3
"""Build Base authoring segment 220 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S220.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s220", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3644:0": "의 취향을\n참 잘 아시",
    "6:3645:0": ", 이",
    "6:3645:1": "은(는)\n그야말로",
    "6:3645:2": "의 취향",
    "6:3646:0": "에게 이토록 훌륭한 일품을…\n무척 마음에 들었습니다",
    "6:3647:0": "이토록 훌륭한 일품을 받게 되다니…\n보자마자 마음에 들었습니다",
    "6:3648:0": ",",
    "6:3648:1": "의 취향에 맞는 일품이 아니\n",
    "6:3648:2": "까",
    "6:3649:0": ", 이것은",
    "6:3649:1": "입니까?\n분에 넘치는 영광",
    "6:3650:0": "오랫동안 바라던",
    "6:3650:1": "을(를)\n이렇게 내려 주시다니…\n감사의 말씀도",
    "6:3651:0": "의 취향에 꼭 맞는 일품…\n기쁘지 않을 리가\n설마 있",
    "6:3651:1": "인가",
    "6:3652:0": "이럴 수가,",
    "6:3652:1": "을(를)…!\n",
    "6:3652:2": "의 취향을 알고 계시다니\n놀라움을 금할 수 없",
    "6:3653:0": "…\n받을 수 있는 것은 감사히\n받아 두",
    "6:3654:0": "이것이",
}

STATIC_COORDINATES: set[str] = {
    "6:3647:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S220", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
