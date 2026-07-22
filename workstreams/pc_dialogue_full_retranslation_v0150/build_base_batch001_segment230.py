#!/usr/bin/env python3
"""Build Base authoring segment 230 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S230.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s230", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3754:0": "중개자 무장이 부재 중이므로\n신용이 오르지 않습니다",
    "6:3755:0": "중개자 무장을 임명하면\n매달 신용이 상승합니다",
    "6:3756:0": "에게 당장 원군을 청하기는 어려우니\n그것이 목적이라면 재고해야 할 일",
    "6:3756:1": "지만\n앞날까지 내다본 것이라면 좋은 방안이라 생각하오",
    "6:3757:0": "에게 당장 원군을 청하기는 어렵다\n그것이 목적이라면 어리석은 계책",
    "6:3757:1": "지만\n앞날을 내다보고 신용을 쌓는 것도 나쁘지 않",
    "6:3758:0": ",",
    "6:3758:1": "의",
    "6:3758:2": "이(가)\n찾아오셨",
    "6:3759:0": "두 가문 사이에 굳건한 신뢰를 쌓고자…\n훗날 동맹을 맺겠다는 약정에\n동의해 주시",
    "6:3759:1": "까?",
    "6:3760:0": "때가 무르익으면,",
    "6:3760:1": "와(과)는\n손을 잡고 싶다고 생각하",
    "6:3760:2": "\n그때는 좋은",
    "6:3760:3": "답변을 기대해도 되겠습니까…?",
    "6:3761:0": "훗날에는",
    "6:3761:1": "에게 원군이나 중재 등\n군사적",
    "6:3761:2": "협력을 청하고자…\n",
    "6:3761:3": "약속해 주시",
    "6:3761:4": "까?",
}

STATIC_COORDINATES: set[str] = {
    "6:3754:0",
    "6:3755:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S230", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
