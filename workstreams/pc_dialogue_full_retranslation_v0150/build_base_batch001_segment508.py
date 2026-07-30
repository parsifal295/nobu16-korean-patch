#!/usr/bin/env python3
"""Build Base authoring segment 508 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S508.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s508", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:372:0": "의 영지가\n풍요로워졌습니다",
    "8:373:0": "백성이 번영을\n기뻐하고 있구나!",
    "8:374:0": "이 땅도 살기 좋은 곳이\n되었습니다",
    "8:375:0": "이 땅도\n풍요로워졌는가",
    "8:376:0": "영지가\n풍요로워졌군!",
    "8:377:0": "토지가\n발전한 모양이군!",
    "8:378:0": "땅을 번영시켰노라",
    "8:379:0": "땅이 풍요로워졌는가",
    "8:380:0": "백성이 기뻐하고 있군",
    "8:381:0": "정사의 성과가\n나타난 모양이군",
    "8:382:0": "백성도 인재도\n공을 들이면 성장하는 법",
    "8:383:0": "발전을 백성도\n기뻐하고 있구나",
    "8:384:0": "그렇",
    "8:384:1": "…\n부디 대체 영지를 검토해",
    "8:385:0": "…알겠",
    "8:385:1": "\n무언가,",
    "8:385:2": "생각이 있으셔서 하신 일…\n다른 영지가 있다면 불만은 없",
    "8:386:0": "명이라면 따르",
    "8:387:0": "승복할 수 없소\n재고해 주길 바라오",
    "8:388:0": "그것이 「",
    "8:388:1": "」에 대한\n평가",
    "8:389:0": "이번에는 승복하겠",
    "8:389:1": "\n두 번은 없을 것이오",
    "8:390:0": "선뜻 수긍할 수는 없",
    "8:390:1": "\n하지만 따를 수밖에 없",
}

STATIC_COORDINATES = {
    *(f"8:{record_id}:0" for record_id in range(373, 384)),
    "8:387:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S508", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
