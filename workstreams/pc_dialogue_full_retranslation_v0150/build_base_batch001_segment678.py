#!/usr/bin/env python3
"""Build Base authoring segment 678 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S678.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s678", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2648:0": "자, 달려라, 달려!\n첫 공을 남에게 내주지 마라!",
    "9:2649:0": "첫 공은 제가 차지하겠습니다\n여러분, 따라오세요!",
    "9:2650:0": "전속력으로 전진!\n첫 공은―",
    "9:2650:1": "이(가) 차지한다!",
    "9:2651:0": "첫 공을 노리겠습니다!\n자, 전력으로 달리세요",
    "9:2652:0": "첫 공은 내가 차지한다!\n",
    "9:2652:1": "을(를) 따르라!",
    "9:2653:0": "첫 공은 반드시 내가 차지한다!\n죽을 각오로 달려라!",
    "9:2654:0": "계속 달려라!\n첫 공을 남에게 내주지 마라!",
    "9:2655:0": "공은 남에게 내주지 않는다!\n첫 공을 노리고 달려라",
    "9:2656:0": "곧장 달리세요!\n첫 공을 차지하는 겁니다!",
    "9:2657:0": "주위는 신경 쓰지 마라!\n전력을 다해 첫 공을 세운다!",
    "9:2658:0": "첫 공은 이미 내 손안이다!\n적을 향해 달려들어라!",
    "9:2659:0": "노리는 것은 첫 공!\n오직 달려라!",
    "9:2660:0": "이(가) 첫 공을 세운다\n주저 말고 돌진하라!",
    "9:2661:0": "반드시 첫 공을 세운다!\n달리고 또 달려 끝까지 내달린다",
    "9:2662:0": "달려라!　반드시\n첫 공을 세워라!",
    "9:2663:0": "노리는 것은 오직 첫 공\n결코 양보하지 않겠습니다",
    "9:2664:0": "달려라!　첫 공을 세워라!\n공을 놓치지 마라!",
    "9:2665:0": "에게\n지지 마라!",
    "9:2666:0": "에게\n뒤처질 수는 없다!",
    "9:2667:0": "을(를)\n뒤쫓아라, 질 수는 없다!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2650:0",
    "9:2650:1",
    "9:2652:0",
    "9:2652:1",
    "9:2660:0",
    "9:2665:0",
    "9:2666:0",
    "9:2667:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
                ),
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
                "segment": "base_msggame_B001_S678",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
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
