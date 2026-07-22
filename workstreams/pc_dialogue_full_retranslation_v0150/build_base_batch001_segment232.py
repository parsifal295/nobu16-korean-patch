#!/usr/bin/env python3
"""Build Base authoring segment 232 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S232.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s232", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3776:0": "동맹 제의는 알겠습니다\n당분간은 손을 잡도록 하지요\n그 뒤 일은 때가 되면 다시 이야기하지요",
    "6:3777:0": "맹약은 받아들이겠다\n당분간은 손을 잡도록 하자\n그 뒤 일은 때가 되면 논하면 된다",
    "6:3778:0": "동맹 제의는 받아들이겠다\n당분간 서로 손을 잡도록 하지\n그 뒤 일은 그때 생각하면 된다",
    "6:3779:0": "동맹 제의는 받아들이겠다\n당분간은 손을 잡도록 하지\n그 뒤 일은 때가 되면 다시 논하자",
    "6:3780:0": "동맹 제의는 승낙했다\n당분간은 손을 잡도록 하지\n그 뒤 일은 때가 되면 다시 논하면 되겠지",
    "6:3781:0": "동맹 제의는 받아들이겠습니다\n당분간은 손을 잡도록 하지요\n그 뒤 일은 그때 다시 의논하지요",
    "6:3782:0": "동맹 제의는 받아들이겠다\n당분간은 벗이 되자\n그 뒤 일은 때가 되면 다시 생각하면 된다",
    "6:3783:0": "동맹 제의, 삼가 받아들이겠습니다\n당분간 손을 잡고…\n그 뒤 일은 훗날 다시…",
    "6:3784:0": "동맹 제의는 받아들이겠다\n당분간은 손을 잡도록 하지\n그 뒤 일은 때가 되면 다시 논하자",
    "6:3785:0": "이야기는 알겠",
    "6:3785:2": "의",
    "6:3785:3": "을(를) 확실히 맡",
    "6:3786:0": "이야기는 알겠",
    "6:3786:2": "의",
    "6:3786:3": "을(를) 확실히 맡",
    "6:3787:0": "이야기는 알겠",
    "6:3787:2": "의",
    "6:3787:3": "을(를) 확실히 맡",
}

STATIC_COORDINATES: set[str] = {
    "6:3776:0",
    "6:3777:0",
    "6:3778:0",
    "6:3779:0",
    "6:3780:0",
    "6:3781:0",
    "6:3782:0",
    "6:3783:0",
    "6:3784:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S232", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
