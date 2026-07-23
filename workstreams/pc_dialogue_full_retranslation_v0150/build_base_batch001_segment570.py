#!/usr/bin/env python3
"""Build Base authoring segment 570 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S570.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s570", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:440:0": "이(가)\n토착 무사 참전으로 병력 회복",
    "9:441:0": "을(를) 포함한 총",
    "9:441:1": "개 부대가\n토착 무사 참전으로 병력 회복",
    "9:442:0": "적군이 둑을 터뜨려 유역의\n",
    "9:442:1": "개 부대가 휩쓸렸습니다",
    "9:443:0": "사태가 급변하여\n전령이 귀환",
    "9:444:0": "요충지를 제압해 아군 총사기 상승",
    "9:445:0": "요충지가 제압되어 아군 총사기 하락",
    "9:446:0": "퇴로를 파괴해 아군 총사기 상승",
    "9:447:0": "퇴로가 파괴되어 아군 총사기 하락",
    "9:448:0": "적 부대를 격파해 아군 총사기 상승",
    "9:449:0": "아군 부대가 궤멸해 아군 총사기 하락",
    "9:450:0": "적 부대를 퇴각시켜 아군 총사기 상승",
    "9:451:0": "아군 부대가 퇴각해 아군 총사기 하락",
    "9:452:0": "의 무장",
    "9:452:1": "명이 전사하거나 포박됨",
    "9:453:0": "우오오!\n해내고 말 테다!",
    "9:454:0": "무공을 세울 절호의 기회다!",
    "9:455:0": "가문을 위해\n미력이나마 다하리라",
    "9:456:0": "제 지혜를\n빌려드리겠습니다",
    "9:457:0": "내 무예를 선보이리라",
    "9:458:0": "후후후…… 맡겨 주십시오",
    "9:459:0": "우리 장병의 기세가 드높도다",
    "9:460:0": "우오오!\n힘이 솟구치는구나!",
}

STATIC_COORDINATES: set[str] = {
    "9:443:0",
    "9:444:0",
    "9:445:0",
    "9:446:0",
    "9:447:0",
    "9:448:0",
    "9:449:0",
    "9:450:0",
    "9:451:0",
    "9:453:0",
    "9:454:0",
    "9:455:0",
    "9:456:0",
    "9:457:0",
    "9:458:0",
    "9:459:0",
    "9:460:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S570", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
