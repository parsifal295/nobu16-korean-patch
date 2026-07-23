#!/usr/bin/env python3
"""Build Base authoring segment 584 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S584.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s584", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:733:0": "이곳은",
    "9:733:1": "에게 맡기고\n성으로 돌아가시오",
    "9:734:0": "물러나십시오\n상처를 치료하는 것이 우선입니다",
    "9:735:0": "……물러나시오\n안정을 취하도록 하시오",
    "9:736:0": "아프군…… 이건……",
    "9:737:0": "이는 우리 군에\n큰 타격이군……",
    "9:738:0": "이럴 수가……!\n정신을 단단히 차리시오",
    "9:739:0": "큰일이야!?\n어서 치료를!",
    "9:740:0": "물러나시오\n나머지는",
    "9:740:1": "이(가) 맡겠소",
    "9:741:0": "조심하세요……\n무사하시길 빌겠습니다",
    "9:742:0": "이 얼마나 안타까운가……\n서둘러 성으로 돌아가시오",
    "9:743:0": "잘도 이런 짓을……\n감히 주군께 상처를 입히다니",
    "9:744:0": "부상까지 당하시다니……\n크윽…… 면목이 없소!",
    "9:745:0": "으음, 이 사태는……\n우리 가문의 명예에도 흠이 가겠군",
    "9:746:0": "이는…… 우리 가문에 치명상이\n될 수도 있겠군요",
    "9:747:0": "궤멸한 데다\n부상까지 당하시다니……",
    "9:748:0": "주군께서 다치셨다고?\n목숨에는 지장이 없는 게지?",
    "9:749:0": "이 상황에 주군께서\n다치시다니 뼈아프군……",
    "9:750:0": "아니, 다치셨다고?\n이놈들……!",
    "9:751:0": "주군께서!?\n괜찮으신 겁니까!?",
    "9:752:0": "이놈들!\n감히 주군을!",
    "9:753:0": "주군께서!? 아아!\n어쩌다 이런 일이……",
}

STATIC_COORDINATES: set[str] = {
    "9:734:0",
    "9:735:0",
    "9:736:0",
    "9:737:0",
    "9:738:0",
    "9:739:0",
    "9:741:0",
    "9:742:0",
    "9:743:0",
    "9:744:0",
    "9:745:0",
    "9:746:0",
    "9:747:0",
    "9:748:0",
    "9:749:0",
    "9:750:0",
    "9:751:0",
    "9:752:0",
    "9:753:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S584", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
