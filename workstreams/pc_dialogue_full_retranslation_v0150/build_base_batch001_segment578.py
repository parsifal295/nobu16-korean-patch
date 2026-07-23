#!/usr/bin/env python3
"""Build Base authoring segment 578 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S578.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s578", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:605:0": "힘들군…… 이토록\n병력을 잃어서는……",
    "9:606:0": "원군이 제때 오지 않으면\n전멸이다!",
    "9:607:0": "이대로라면\n전멸하고 맙니다",
    "9:608:0": "큰일이군…… 모두가\n전사하고 말겠어……",
    "9:609:0": "교대해 주십시오……\n이대로면 전멸할 수도……",
    "9:610:0": "병력이 꽤\n줄었군……",
    "9:611:0": "지원인가, 고맙구먼!",
    "9:612:0": "가세해 주어 감사하오!",
    "9:613:0": "지원인가…… 이 은혜는 잊지 않겠다!",
    "9:614:0": "이 은혜는 잊지 않겠사옵니다!",
    "9:615:0": "지원에 감사한다",
    "9:616:0": "지원 덕분에 무사히 교대했어",
    "9:617:0": "지원해 주시니 황공하옵니다",
    "9:618:0": "지원해 주어 황송하오!",
    "9:619:0": "지원해 주셔서 살았습니다!",
    "9:620:0": "미안하오, 잠시 엄호를 부탁하오!",
    "9:621:0": "지원해 주셔서 감사합니다",
    "9:622:0": "지원해 주시니 큰 도움이 됩니다!",
    "9:623:0": "미안하다!\n뒤는 맡겼다!",
    "9:624:0": "고맙소\n뒤는 맡기겠소",
    "9:625:0": "음, 감사히\n물러나도록 하겠소",
    "9:626:0": "죄송합니다……\n뒤는 맡기겠습니다",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S578", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
