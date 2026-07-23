#!/usr/bin/env python3
"""Build Base authoring segment 677 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S677.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s677", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2628:0": "이(가) 철포대로 사격",
    "9:2629:0": "철포가 나설 차례다!\n쏘아 꿰뚫어라!",
    "9:2630:0": "철포대, 사격 준비!\n놈들의 기세를 꺾어라!",
    "9:2631:0": "철포를 겨눠라!\n빗맞히지 마라",
    "9:2632:0": "철포대, 사격 준비!\n기선을 꺾어 버려라!",
    "9:2633:0": "철포대, 쏴라!\n적의 수를 줄여라!",
    "9:2634:0": "철포를 겨눠라!\n기마 무사를 노려라!",
    "9:2635:0": "철포를 겨눠라\n잘 조준하라",
    "9:2636:0": "철포가 나설 차례다!\n자, 쏘아 꿰뚫어라!",
    "9:2637:0": "철포대, 겨누세요!\n잘 조준해 주세요!",
    "9:2638:0": "철포대, 잘 조준하라!\n놓치지 마라!",
    "9:2639:0": "철포대, 공격 개시!\n확실히 쓰러뜨리세요!",
    "9:2640:0": "철포대, 사격 준비!\n놈들의 기세를 꺾어라!",
    "9:2641:0": "첫 공은―",
    "9:2641:1": "의 몫이다!\n돌격하라!",
    "9:2642:0": "첫 공은 내가 차지한다!\n뒤처지지 마라!",
    "9:2643:0": "첫 공을 노린다!\n모두, 나를 따르라!",
    "9:2644:0": "첫 공은―",
    "9:2644:1": "이(가) 차지한다!\n모두, 앞으로 나서라!",
    "9:2645:0": "첫 공은 내가 차지하겠다!\n전속력으로 달려라!",
    "9:2646:0": "초반이 중요하다!\n자, 첫 공을 세우자",
    "9:2647:0": "전력으로 달려라!\n첫 공은 우리가 차지한다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2628:0",
    "9:2641:0",
    "9:2641:1",
    "9:2644:0",
    "9:2644:1",
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
                "segment": "base_msggame_B001_S677",
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
