#!/usr/bin/env python3
"""Build Base authoring segment 671 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S671.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s671", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "9:2519:0": "협격이라고!?\n내가 이런 실수를 하다니…!",
    "9:2520:0": "협격인가!\n한 수 제대로 당했군…!",
    "9:2521:0": "협격이라니 불찰이군…!\n한눈을 팔고 있었나…",
    "9:2522:0": "협격이라니!?\n제법이군요…",
    "9:2523:0": "협격이라니!\n상대도 제법이군…",
    "9:2524:0": "여기서 협격이라니!?\n악수를 두었나…!",
    "9:2525:0": "협격이라고!?\n방심했던가…",
    "9:2526:0": "협격이라고!?\n경계를 게을리하다니…!",
    "9:2527:0": "협격이라니!?\n당했군요…",
    "9:2528:0": "협격이라니!?\n성가시군…!",
    "9:2529:0": "협격입니까…\n방심했습니다…",
    "9:2530:0": "협격인가!\n한 수 제대로 당했군…!",
    "9:2531:0": "설마,",
    "9:2531:1": "이(가)\n적의 유인책에 걸렸다고…!?",
    "9:2532:0": "겁먹지 마라!\n정면의 부대를 꿰뚫어라!",
    "9:2533:0": "퇴각로를 노리는가!\n그렇게는 못 한다!",
    "9:2534:0": "퇴각로에 적군이!\n즉시 요격한다!",
    "9:2535:0": "퇴각로를 잃을 수는 없다\n요격하러 간다!",
    "9:2536:0": "퇴각로를 노리는 군세라고?\n서둘러 쳐부수겠습니다",
    "9:2537:0": "퇴각로를 내줄 성싶으냐!\n",
    "9:2537:1": "이(가) 나선다!",
    "9:2538:0": "퇴각로가 위태로운가\n그리로 향해야겠군",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2531:0",
    "9:2531:1",
    "9:2537:0",
    "9:2537:1",
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
                "segment": "base_msggame_B001_S671",
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
