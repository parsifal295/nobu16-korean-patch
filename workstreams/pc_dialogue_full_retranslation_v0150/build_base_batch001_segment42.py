#!/usr/bin/env python3
"""Build Base authoring segment 42 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S42.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s42", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:532:0": "짬이 날 때마다\n군단을 손보시는군요",
    "6:533:0": "군단은\n상황에 맞춰야 하는 법",
    "6:534:0": "좋도다, 좋도다\n군단은 자주 손보거라",
    "6:535:0": "군단 변경은\n마음에 들 때까지 얼마든지",
    "6:536:0": "군단을 손보실 때면\n문득 눈빛이 진지해지시는군",
    "6:537:0": "군단을 마음껏 부리며\n공격하면 재미있겠지",
    "6:538:0": "군단을 손보는 솜씨가\n아직 한참 부족하다",
    "6:539:0": "상황에 따라\n군단의 운용도 바꿔야 한다",
    "6:540:0": "군단을 손보는 일을\n좋아하시는군요",
    "6:541:0": "오오… 다 해냈다는 표정을\n짓고 계시는구나",
    "6:542:0": "군단은 상황에 맞춰\n손보아야 하지…",
    "6:543:0": "당연",
    "6:544:0": "다음에도 힘쓰겠습니다.",
    "6:545:0": "\n그렇게 나오는",
    "6:545:1": "가.",
    "6:546:0": "무슨 일이 있어도\n훈공을 세워 보이겠습니다.",
    "6:547:0": "어떻게 해야",
    "6:547:1": "의 눈에\n들 수 있을까?",
    "6:548:0": "모든 일은 신뢰가 있어야 가능한 법",
    "6:549:0": "이것저것 세심히 살피는 것도\n중요한 일",
    "6:550:0": "는 그렇게\n생각하십니까?",
    "6:551:0": "조정과의 관계도\n소중히 여겨야 합니다.",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {543, 544, 545, 546, 547, 550, 551}
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S42",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
