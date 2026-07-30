#!/usr/bin/env python3
"""Build Base authoring segment 668 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S668.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s668", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2455:0": "새 병력이 와도\n적수가 되지 못한다!",
    "9:2456:0": "이거 힘들겠는데……\n새 병력이 온단 말은 못 들었다고",
    "9:2457:0": "적의 예비대인가……\n오래 버티지는 못하겠군……",
    "9:2458:0": "예비대가 있었는가……\n힘겨운 싸움이 되겠군……",
    "9:2459:0": "아직 전력이 남았다고……?\n적도 제법 하는군요……",
    "9:2460:0": "적의 증원군이라고!?\n온전한 상태라면 단숨에 해치울 텐데……",
    "9:2461:0": "여기서 예비대라니……?\n우리의 소모를 노린 건가",
    "9:2462:0": "여기서 새 병력이라니……\n연전은 버거운가",
    "9:2463:0": "아직 적이 남아 있었는가……\n이건 고되겠구나……",
    "9:2464:0": "연전은 힘겹군요……\n물러날 때를 가늠해야겠습니다……",
    "9:2465:0": "적의 증원군이라고!?\n연전은 버겁다만……",
    "9:2466:0": "여기서 새 병력이라……\n적도 제법 약삭빠르구나",
    "9:2467:0": "여기서 새 병력이라니……\n오래 버티지 못하겠군……",
    "9:2468:0": "이(가) 피로로 인해 일시 후퇴",
    "9:2469:0": "피로가 한계에 달했군……\n좋아, 물러난다!",
    "9:2470:0": "무리는 금물이다……\n후방으로 물러나자",
    "9:2471:0": "질 싸움은 할 수 없다……\n지금은 물러나자",
    "9:2472:0": "병사들을 쉬게 합시다……\n우리는 물러나겠습니다",
    "9:2473:0": "연전은 무리다……\n물러난다!",
    "9:2474:0": "병사들이 지쳤군……\n물러날 수밖에 없다",
    "9:2475:0": "이래서는 버티지 못하겠군……\n물러난다",
    "9:2476:0": "더는 버티지 못하겠는가……\n후퇴하라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2468:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
    print(ENGINE.json.dumps({"status":"ok", "segment":"base_msggame_B001_S668", "decision_count":len(rows),
                             "retranslated":len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending":len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed":False, "output":str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
