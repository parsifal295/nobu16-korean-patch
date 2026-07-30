#!/usr/bin/env python3
"""Build Base authoring segment 467 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S467.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s467", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2576:0": "요지를 차지한—",
    "7:2576:1": "의 활약이\n모두를 승리로 이끌었다\n전공 제일은 지극히 당연하다!",
    "7:2577:0": "전공 제일은 내 것인가\n확실히 요지 확보는 긴요하니\n이번 승리로 이어졌는지도 모르겠군",
    "7:2578:0": "내가 전공 제일인가!\n이기기 위해 요지를 빼앗은 보람이 있었군!",
    "7:2579:0": "전공 제일의 영예는 내 것이로다!\n요지 점거도 싸움의 중요한 한 수\n소홀히 할 수 없는 법이지",
    "7:2580:0": "전공 제일이라니 영예롭구나\n요지 점령에 힘쓴 것이\n싸움과 무공 모두에 좋은 결과를 냈군",
    "7:2581:0": "우리가 요지를 제압하고\n아군을 계속 엄호했습니다\n전공 제일도 당연하겠지요",
    "7:2582:0": "호오…… 전공 제일인가\n스스로 무훈을 자랑하자니 외람되지만\n요지 점거에 집중한 보람이 있었도다",
    "7:2583:0": "설마 전공 제일이라니\n요지를 장악한 일이\n상당히 주효했던 모양이군",
    "7:2584:0": "오오……",
    "7:2584:1": "이(가) 전공 제일인가\n요지를 훌륭히 장악한 것이 주효했군\n화려하게 날뛰는 것만이 싸움은 아니지",
    "7:2585:0": "호호오—",
    "7:2585:1": "이(가) 전공 제일이라니!\n이토록 요지 제압의 중요성을 보여 준 싸움은\n달리 없을 것이오!",
    "7:2586:0": "이(가) 가장 큰 전공을 세웠습니다!\n역시 요지를 장악한 것이\n싸움의 흐름을 결정했군요",
    "7:2587:0": "요지를 장악했다!\n적군을 격파했다!\n최고의 성과라 할 만하다!",
    "7:2588:0": "전공 제일을 차지했답니다\n요지를 확보한 것이 주효했던 듯해요\n다음에도 이랬으면 좋겠네요",
    "7:2589:0": "이(가) 전공 제일이라니 기쁘구나\n싸움에서는 요지를 차지하는 것이 긴요하니……\n내 전술은 틀리지 않았던 모양이군",
    "7:2590:0": "나의 이름이여, 온 천하에 울려 퍼져라!",
    "7:2591:0": "공을 다투는 데서\n남에게 뒤질 수는 없으니 말이야!",
    "7:2592:0": "보았느냐, 미카와 무사의 저력을!",
}

PENDING_COORDINATES = {
    "7:2576:0", "7:2576:1", "7:2584:0", "7:2584:1",
    "7:2585:0", "7:2585:1", "7:2586:0", "7:2589:0",
}
STATIC_COORDINATES: set[str] = set(TRANSLATIONS) - PENDING_COORDINATES


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
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S467", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
