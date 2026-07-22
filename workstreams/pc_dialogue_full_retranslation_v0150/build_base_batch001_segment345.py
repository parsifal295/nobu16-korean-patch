#!/usr/bin/env python3
"""Build Base authoring segment 345 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S345.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s345", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:739:0": "네놈, 죽어서도 저주해 주마…",
    "7:740:0": "계책이 미치지 못해 멸망하다니…",
    "7:741:0": "우리 가문도 여기까지인가…",
    "7:742:0": "선조들께 면목이 없구나…",
    "7:743:0": "이것이 전국시대란 말입니까…",
    "7:744:0": "원통하기 그지없구나…",
    "7:745:0": "원통하옵니다…",
    "7:746:0": "이제 모든 것이 끝이로구나…",
    "7:747:0": "을(를) 멸망시켰습니다",
    "7:748:0": "승리의 함성을 올려라!\n적 본거지 「",
    "7:748:1": "」은(는)\n우리 군문에 항복하",
    "7:748:2": "!",
    "7:749:0": "적 본거지 「",
    "7:749:1": "」을(를) 함락시켰다!\n우리 「",
    "7:749:2": "」의 대승리",
    "7:749:3": "!",
    "7:750:0": "우리 깃발을 높이 들어라!\n적 본거지 「",
    "7:750:1": "」은(는)\n우리 손안에 있다!",
    "7:751:0": "적 본거지 「",
    "7:751:1": "」을(를) 빼앗았구나!",
}

STATIC_COORDINATES: set[str] = {
    "7:739:0",
    "7:740:0",
    "7:741:0",
    "7:742:0",
    "7:743:0",
    "7:744:0",
    "7:745:0",
    "7:746:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S345", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
