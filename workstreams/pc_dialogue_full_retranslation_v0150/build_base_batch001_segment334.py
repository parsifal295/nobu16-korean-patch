#!/usr/bin/env python3
"""Build Base authoring segment 334 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S334.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s334", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:588:0": "밥이 다 떨어져 버렸잖아!\n이래서는 병사들을 다잡을 수 없어!",
    "7:589:0": "큭, 병량이…!\n병사들의 동요를 막을 수 없겠군…",
    "7:590:0": "병량이 다했나…\n병사들이 달아나는 것도 무리는 아니지…",
    "7:591:0": "병량이 다 떨어졌습니다!\n병사들이 달아나기 시작했습니다",
    "7:592:0": "이럴 수가…\n병량이 다했으니 싸울 형편이 아니야…",
    "7:593:0": "병량은 다했어…\n진이 무너지는 것도 시간문제야…",
    "7:594:0": "그런가, 병량이 다했군…\n부대가 무너지기 전에 승부를 내야겠군…",
    "7:595:0": "오오, 병사들이 달아나고 있구나…\n병량이 없으면 싸울 수 없지…",
    "7:596:0": "마침내 병량이…\n더는 군을 유지하기 어려울 듯합니다…",
    "7:597:0": "병량이 바닥났군…\n병사들이 달아나는 걸 막을 수 없겠어…",
    "7:598:0": "병량이 다 떨어졌습니다.\n이대로는 부대를 유지할 수 없습니다!",
    "7:599:0": "으음, 병량이 다했는가!\n이래서는 부대를 유지할 수 없겠구나!",
    "7:600:0": "이(가)",
    "7:600:1": "에 입성",
    "7:601:0": "들",
    "7:601:1": "명이",
    "7:601:2": "에 입성",
    "7:602:0": "설마 「",
    "7:602:1": "」이(가) 함락될 줄이야",
    "7:603:0": "은(는) 반드시 되찾고 말겠다",
}

STATIC_COORDINATES: set[str] = {
    "7:588:0",
    "7:589:0",
    "7:590:0",
    "7:591:0",
    "7:592:0",
    "7:593:0",
    "7:594:0",
    "7:595:0",
    "7:596:0",
    "7:597:0",
    "7:598:0",
    "7:599:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S334", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
