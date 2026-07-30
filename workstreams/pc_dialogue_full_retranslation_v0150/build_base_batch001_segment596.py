#!/usr/bin/env python3
"""Build Base authoring segment 596 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S596.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s596", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:989:0": "겁먹고 허둥대거라!",
    "9:990:0": "내 계책에 현혹되어라",
    "9:991:0": "멋대로 하시면\n곤란하니까요",
    "9:992:0": "두려워하라, 갈피를 잃어라!",
    "9:993:0": "가장 큰 적은 두려워하는 마음\n그 사실을 가르쳐 주마",
    "9:994:0": "전장에서 갈피를 잃으면\n곧 죽음이다",
    "9:995:0": "정신없이 허둥대거라!",
    "9:996:0": "잠시 얌전히\n있어 주셔야겠습니다!",
    "9:997:0": "이것으로\n자유로이 움직이지 못하리라!",
    "9:998:0": "혼란도\n식은 죽 먹기랍니다",
    "9:999:0": "혼란에 빠뜨려 주겠어!",
    "9:1000:0": "침착하게 굴기는……",
    "9:1001:0": "큭!\n조금도 동요하지 않다니……",
    "9:1002:0": "배짱이 두둑하구나……",
    "9:1003:0": "다른 수를 궁리해야겠군……",
    "9:1004:0": "으으음, 통하지 않는가……",
    "9:1005:0": "큭……\n내 계책이 통하지 않다니",
    "9:1006:0": "군기가 철저히 잡혀\n있는 모양이군요……",
    "9:1007:0": "이럴 수가, 혼란에 빠질\n기미조차 없구나",
    "9:1008:0": "잘 풀리지 않는군요……",
    "9:1009:0": "현혹되지 않는가……",
    "9:1010:0": "상대가 한 수 위였습니까……",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
                "segment": "base_msggame_B001_S596",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
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
