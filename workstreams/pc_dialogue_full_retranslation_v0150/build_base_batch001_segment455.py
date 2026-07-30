#!/usr/bin/env python3
"""Build Base authoring segment 455 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S455.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s455", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2407:0": "선택 중인 부대가 너무 많아 합류점을 설정할 수 없습니다",
    "7:2408:0": "출진할 부대를 확인·변경할 수 있습니다",
    "7:2409:0": "출진할 부대를 확인·변경할 수 있습니다",
    "7:2410:0": "출진할 무장을 선택해 주십시오",
    "7:2411:0": "지원은",
    "7:2411:2": "의 군단도 출진",
    "7:2412:0": "약속은—",
    "7:2412:1": "에 투입할 병력은—",
    "7:2412:2": " 이상\n확실히 완수하",
    "7:2413:0": "따위는\n문제없이 쳐부숴라",
    "7:2414:0": "을(를) 상대하기에는\n병력이 부족하",
    "7:2414:1": "\n힘겨운 싸움이 되",
    "7:2415:0": "와(과) 우리의 힘은 거의 호각\n승패는 지휘에 달렸다는 것이군",
    "7:2416:0": "의 병력과 휴대 병량의 양을 감안하건대\n",
    "7:2416:1": "을(를) 함락하기는 어려울 듯하옵니다\n주명이시라면 전력을 다해 공격은",
    "7:2416:2": "하지만……",
    "7:2417:0": "와(과) 싸우기에는\n충분한 병력",
    "7:2417:1": "\n다만 병량에는 불안이 남",
    "7:2417:2": ", 유의하시오",
}

STATIC_COORDINATES: set[str] = {
    "7:2407:0", "7:2408:0", "7:2409:0", "7:2410:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S455", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
