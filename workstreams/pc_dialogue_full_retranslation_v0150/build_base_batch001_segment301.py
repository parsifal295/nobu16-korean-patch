#!/usr/bin/env python3
"""Build Base authoring segment 301 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S301.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s301", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4515:0": "그대와는 마음이 맞지 않는다",
    "6:4516:0": "활약할 기회를 얻을지도 모른다",
    "6:4517:0": "크게 활약할 기회가 있을 듯하다",
    "6:4555:0": "의 빼내기는 순조롭게 진행되고 있으며\n조건에 따라 성째로 귀순할 뜻도 있다고 합니다\n",
    "6:4555:1": "께서 몸소 교섭해 주시지 않겠",
    "6:4555:2": "습니까?",
    "6:4556:0": "의 빼내기는 순조롭게 진행되고 있으며\n소령 안도가 이루어지면 성째로 귀순할 뜻도 있다고 합니다\n",
    "6:4556:1": "께서 몸소 교섭해 주시지 않겠",
    "6:4556:2": "습니까?",
    "6:4557:0": "의 빼내기가 난항을 겪고 있어\n이대로는 실패로 끝나",
    "6:4557:2": "께서 힘을 보태 주시지 않겠",
    "6:4557:3": "습니까?",
    "6:4558:0": "이(가) 우리 가문의 빼내기 제안에 마음이 흔들리면서도\n한 번 더 밀어붙일 힘이 부족",
    "6:4558:1": "상황…\n",
    "6:4558:2": "께서 힘을 보태 주시지 않겠",
    "6:4558:3": "습니까?",
    "6:4559:0": "의 빼내기가 난항을 겪고 있어\n요구를 받아들이지 않으면 응해 주지",
    "6:4559:2": "께서 힘을 보태 주시지 않겠",
    "6:4559:3": "습니까?",
    "6:4567:0": "그럼 성째 귀순은 포기하고\n",
}

STATIC_COORDINATES: set[str] = {"6:4515:0", "6:4516:0", "6:4517:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S301", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
