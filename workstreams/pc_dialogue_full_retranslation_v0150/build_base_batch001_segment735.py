#!/usr/bin/env python3
"""Build Base authoring segment 735 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S735.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s735", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3789:0": "……!　복병을 둔 진형이로구나!\n전진!　",
    "9:3789:1": "다키타 일행",
    "9:3789:2": "을 구하라!",
    "9:3790:0": "진군을 멈춰라\n주군의 신호가 있을 때까지 대기하라",
    "9:3791:0": "이쯤에 병력을 매복시키자\n얼마나 걸려들지 기대되는구나",
    "9:3792:0": "걸려들었군, 전군 전진!\n",
    "9:3792:1": "오토모",
    "9:3792:2": "군을 일망타진하라!",
    "9:3793:0": "돌격이다!\n놈들을 ",
    "9:3793:1": "다카조가와",
    "9:3793:2": "에 처넣어라!",
    "9:3794:0": "역시 복병인가……\n원군은 제때 오지 못하는가……!",
    "9:3795:0": "복병이 있었군! 혼란한 틈에 쓸어버리자!",
    "9:3796:0": "설마 간파당할 줄이야……",
    "9:3797:0": "이, 이럴 리가……\n이 대군으로도 어찌하여……",
    "9:3798:0": "천하의 규슈 단다이가 이 꼴이라니……\n역시 규슈는 형님께서 다스려야 마땅하다",
    "9:3799:0": "오토모",
    "9:3799:1": "의 책사는 반드시 베어라\n",
    "9:3799:2": "츠노쿠마가",
    "9:3799:3": " 없는 ",
    "9:3799:4": "오토모",
    "9:3799:5": "는 두려워할 것도 없다",
    "9:3800:0": "이것은 ",
    "9:3800:1": "오니시마즈",
    "9:3800:2": "의 부대인가……!\n",
    "9:3800:3": "오토모",
    "9:3800:4": "를 위해서라도 살아 돌아가야 한다……",
}

STATIC_COORDINATES = set(TRANSLATIONS)
DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S735",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "confirmed_non_display": 0,
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
