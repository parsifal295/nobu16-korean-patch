#!/usr/bin/env python3
"""Build Base authoring segment 588 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S588.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s588", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:816:0": "적장의 수급까지 한 걸음!\n이 무훈은 천하에 울려 퍼지리라!",
    "9:817:0": "놓쳤는가……\n하지만 잘했다!",
    "9:818:0": "상처를 입히다니\n상당한 전과입니다",
    "9:819:0": "장하다, 큰 공을 세웠구나!\n그 기운을 나도 받고 싶도다",
    "9:820:0": "대장 부대를 궤멸시키고\n상처까지 입히다니!",
    "9:821:0": "아깝게도 베어 쓰러뜨리지 못했나……\n그래도 큰 공입니다",
    "9:822:0": "좀처럼 보기 힘든 큰 공이로다……\n대장에게 상처를 입히다니",
    "9:823:0": "상처를 입히다니!\n해냈군요!",
    "9:824:0": "한 걸음이 모자랐나……\n그래도 훌륭했다!",
    "9:825:0": "이만큼 타격을 주었으면\n충분하겠지요",
    "9:826:0": "그만큼 해냈다면\n충분하고도 남소이다!",
    "9:827:0": "제법이군!\n저런 거물을 꺾다니",
    "9:828:0": "대장 부대의 궤멸이라니……!\n무공의 영예가 한이 없도다!",
    "9:829:0": "을(를) 격파하다니\n장하도다!",
    "9:830:0": "적의 다이묘마저……\n대단합니다!",
    "9:831:0": "대장 부대를 무너뜨렸나!\n이 기세로 몰아붙인다!",
    "9:832:0": "대장 부대가 궤멸했다고? 후후후……\n이미 이긴 것이나 다름없지 않은가",
    "9:833:0": "을(를) 격멸하여\n천하에 이름을 떨쳤노라!",
    "9:834:0": "장하다!　",
    "9:834:1": "은(는)\n도망치고 말았구나",
    "9:835:0": "훌륭합니다!\n거물을 해치우셨군요",
    "9:836:0": "……",
    "9:836:1": "을(를)\n격파하다니……!",
    "9:837:0": "훌륭합니다!\n거물을 해치우셨군요",
}

STATIC_COORDINATES: set[str] = {
    "9:816:0",
    "9:817:0",
    "9:818:0",
    "9:819:0",
    "9:820:0",
    "9:821:0",
    "9:822:0",
    "9:823:0",
    "9:824:0",
    "9:825:0",
    "9:826:0",
    "9:827:0",
    "9:828:0",
    "9:830:0",
    "9:831:0",
    "9:832:0",
    "9:835:0",
    "9:837:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S588", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
