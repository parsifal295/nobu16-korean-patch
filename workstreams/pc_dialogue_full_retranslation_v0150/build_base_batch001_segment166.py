#!/usr/bin/env python3
"""Build Base authoring segment 166 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S166.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s166", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2988:0": "님, 안녕하셨습니까",
    "6:2989:0": "님, 오늘은 무슨 용무로 오셨습니까",
    "6:2990:0": "은(는) 무엇을 요구하려는 거지…",
    "6:2991:0": "\n부디 보답을 제시해 주시오",
    "6:2992:0": "님께서는 무엇을 바라시는가…",
    "6:2993:0": "님께서는 무엇을 바라십니까",
    "6:2994:0": ", 부디 너무 무리한 요구는 말게",
    "6:2995:0": "헌데… 보답으로 무엇을 바라시는가",
    "6:2996:0": "\n보답으로는 무엇을 원하시오?",
    "6:2997:0": "무, 무엇을 요구하려는 게야…?\n가슴이 두근거리는구먼",
    "6:2998:0": "무엇을 바라시는 걸까요…",
    "6:2999:0": "자, 조건을 제시해 주시오",
    "6:3000:0": "조건을 말씀해 주십시오",
    "6:3001:0": "님께서는 무엇을 바라시옵니까?",
    "6:3002:0": "아무리",
    "6:3002:1": "이라 해도\n이 요구는 웃어넘길 수 없겠군…",
    "6:3003:0": "상대의 긍지를 무시한 제안은\n하지 않는 법이다",
    "6:3004:0": "분별없이 값을 올려 봐야\n상대를 화나게 할 뿐인가…",
    "6:3005:0": "이렇게까지 욕심을 부리면\n상대가 화를 내겠지요…",
    "6:3006:0": "역시 무리인가…",
}

STATIC_COORDINATES = {
    "6:2995:0", "6:2997:0", "6:2998:0", "6:2999:0", "6:3000:0",
    "6:3003:0", "6:3004:0", "6:3005:0", "6:3006:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S166", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
