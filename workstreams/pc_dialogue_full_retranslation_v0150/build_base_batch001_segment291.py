#!/usr/bin/env python3
"""Build Base authoring segment 291 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S291.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s291", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4389:0": ", 「",
    "6:4389:1": "」 일동\n총력을 다해 임하",
    "6:4390:0": "방침, 받들",
    "6:4390:1": "\n이제 이를 실현하기만 하면 됩니다",
    "6:4391:0": "명을 받들겠습니다",
    "6:4392:0": "명을 받들겠습니다",
    "6:4392:1": "\n임무와 전투가 끝나는 대로\n착수하겠습니다",
    "6:4393:0": "명을 받들겠습니다",
    "6:4393:1": "\n전투에서 돌아오는 대로\n착수하겠습니다",
    "6:4394:0": "명을 받들겠습니다",
    "6:4394:1": "\n임무를 마치는 대로\n착수하겠습니다",
    "6:4395:0": "성주 「",
    "6:4395:1": "」님이 다스리는\n",
    "6:4395:2": "에서 떠나기 어렵",
    "6:4396:0": "성주가 아니라 영주를 맡으라고요…?\n…",
    "6:4396:1": ", 불만이 있는 것은 아닙니다",
    "6:4397:0": "을(를) 맡을 수 있다면\n영지에 대한 불만 따위\n품을 리가",
    "6:4398:0": "이 땅을 받는다고 충의가\n높아지는 것은",
    "6:4398:1": "지만\n받을 수 있는 것은 받",
    "6:4399:0": "미사용",
}

STATIC_COORDINATES: set[str] = {"6:4399:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S291", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
