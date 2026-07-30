#!/usr/bin/env python3
"""Build Base authoring segment 44 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S44.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s44", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:572:0": "아… 아직인가…?\n설마",
    "6:572:1": "의 건의는…?",
    "6:573:0": "헌책을 올렸건만…\n기다리는 처지는 괴롭구나…",
    "6:574:0": "언젠가 건의를 알아보실 터…\n그날을 믿으며…",
    "6:575:0": "건의를… 받아들여\n주시려나…",
    "6:576:0": "견디기 어렵군…\n헌책을 거두어들일까",
    "6:577:0": "공성이라면 승산이 있겠지\n",
    "6:577:1": "라면 말이야",
    "6:578:0": "공격이\n잘 풀리면 좋겠군",
    "6:579:0": "…\n부디 방심하지 마라",
    "6:580:0": "공격이\n잘 풀리면 좋으련만",
    "6:581:0": "라면\n공략을 성공시키리라",
    "6:582:0": "공략인가…\n아군을 믿어 보자",
    "6:583:0": "라면\n분명 예상대로…",
    "6:584:0": "공략이\n성공하기를 기원합시다",
    "6:585:0": "로는\n저 성을 함락할 수 있을까",
    "6:586:0": "인가…\n함락시킬 수 있으면 좋으련만",
    "6:587:0": "설령",
    "6:587:1": "이(가)\n패하더라도 방책은 있다…",
    "6:588:0": "공격에서\n승리를 거두기를",
    "6:589:0": "의\n분전을 기대합시다",
    "6:590:0": "공략은\n성공하겠습니다만…",
    "6:591:0": "의 힘으로\n함락할 수 있을까…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) == 572 or int(coordinate.split(":")[1]) >= 577
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
                "segment": "base_msggame_B001_S44",
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
