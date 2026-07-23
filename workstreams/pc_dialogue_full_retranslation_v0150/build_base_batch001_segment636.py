#!/usr/bin/env python3
"""Build Base authoring segment 636 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S636.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s636", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1841:0": "뭘, 안심하라고\n남은 우리끼리 해낼 수 있어",
    "9:1842:0": "주군……!\n면목이 없사옵니다",
    "9:1843:0": "주군…… 부디\n무리하지 마시옵소서……",
    "9:1844:0": "부상이 가볍기만을\n빌 따름입니다",
    "9:1845:0": "주군을 다치게 한 죄는\n무겁다……!",
    "9:1846:0": ", 주군을 위해\n계속 싸우겠사옵니다",
    "9:1847:0": "지금―",
    "9:1847:1": "이(가) 할 수 있는 일은\n싸우는 것뿐……",
    "9:1848:0": "상처가\n악화되지 않으면 좋으련만……",
    "9:1849:0": "부디 무사하시기를……",
    "9:1850:0": "이 무슨 일이란 말인가!\n참으로 한심하구나!",
    "9:1851:0": "용태가 걱정됩니다……",
    "9:1852:0": "이건…… 이미 패한 게\n아닌가……",
    "9:1853:0": "걱정하지 마라!\n",
    "9:1853:1": "이(가) 해낼 테니까!",
    "9:1854:0": "주군……\n에잇, 한심하구나!",
    "9:1855:0": "주군의 부대가 궤멸……?\n어찌 이런 일이……",
    "9:1856:0": "……어쨌든 사기가\n무너지지 않게 해야 한다……",
    "9:1857:0": "이럴 수가, 주군께서!",
    "9:1858:0": "무사하시다면 다행이다……\n문제는 전황이다……",
    "9:1859:0": "병사들의 동요가\n퍼져 나간다……!",
    "9:1860:0": "오오, 주군!\n이 무슨 변고인가!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1846:0",
    "9:1847:0",
    "9:1847:1",
    "9:1853:0",
    "9:1853:1",
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
                "segment": "base_msggame_B001_S636",
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
