#!/usr/bin/env python3
"""Build Base authoring segment 318 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S318.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s318", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:324:0": "당분간은 무슨 말을 듣더라도\n",
    "7:324:1": "을(를) 섬길 마음은 없",
    "7:325:0": "거절하",
    "7:325:2": "을(를) 섬기다니\n상상만 해도 소름이 돋",
    "7:326:0": "라는 이름의 자에게\n",
    "7:326:1": "이(가) 무릎 꿇는 일은 없",
    "7:327:0": "……내 신조와 맞지 않는 자를\n주군으로 받들 마음은 없",
    "7:328:0": "에게도 긍지가 있",
    "7:328:1": "\n방금 전까지 적이던 상대를\n곧바로 주군으로 받들 수는 없",
    "7:329:0": "아무리 그래도 「",
    "7:329:1": "」은(는)\n내 대망을 꺾은 상대\n곧바로 귀순할 결단은 내릴 수 없",
    "7:330:0": "……그 온정에는 깊이 감사하",
    "7:330:1": "지만\n이번에는 거절하겠",
    "7:330:2": "\n아직은 도저히 그럴 마음이……",
    "7:331:0": "권유에는 감사하",
    "7:331:1": "지만\n당장 결단을 내리기는 어렵",
    "7:331:2": "……",
    "7:332:0": "면목이",
    "7:332:1": "지만\n주가를 잃은 지 얼마 되지 않아\n마음을 추스를 수가",
    "7:333:0": "의 등용에 실패했습니다",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S318", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
