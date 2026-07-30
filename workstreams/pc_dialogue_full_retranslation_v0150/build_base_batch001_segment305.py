#!/usr/bin/env python3
"""Build Base authoring segment 305 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S305.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s305", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4649:0": "의 직담 요청을 거절하면\n담당 중인 건의는 실패합니다\n계속하시겠습니까?",
    "6:4650:0": "의 항복 교섭을 거절하고\n공성전으로 돌아갑니다. 계속하시겠습니까?",
    "6:4651:0": "의 제안을 거절하고\n빼내기를 진행합니다. 계속하시겠습니까?",
    "6:4652:0": "의 빼내기를 포기합니다\n계속하시겠습니까?",
    "6:4653:0": "와의 정전 교섭을 중지합니다\n계속하시겠습니까?",
    "6:4654:0": "에게 양도하는 절차를 중지합니다\n계속하시겠습니까?",
    "6:4655:0": "\n을(를) 가재로 임명합니다\n계속하시겠습니까?",
    "6:4656:1": "\n을(를) 종속 다이묘 가재로 임명합니다\n계속하시겠습니까?",
    "6:4657:4": "\n이상 인물들을 봉행으로 임명합니다\n계속하시겠습니까?",
    "7:112:0": "출진할 수 있는 무장이 없습니다",
    "7:113:0": "더 이상 부대를 출진시킬 수 없습니다",
    "7:114:0": "출진할 수 있는 성이 없습니다",
    "7:115:0": "새 임무를 생성합니다",
    "7:116:0": "목표 지점을\n선택해 주십시오",
    "7:117:0": "목표 지점 또는 이미 출진한\n부대를 선택해 주십시오",
    "7:118:0": "제가 직접\n방안을 내겠습니다",
    "7:119:0": "내가 직접\n방안을 내 보지",
    "7:120:0": "이 「",
    "7:120:1": "」의 군략을\n한번 선보여 주지",
    "7:121:0": "흠, 내 생각을\n여기서 한번 보여 주지",
}

STATIC_COORDINATES: set[str] = {
    "7:112:0", "7:113:0", "7:114:0", "7:115:0", "7:116:0",
    "7:117:0", "7:118:0", "7:119:0", "7:121:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S305", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
