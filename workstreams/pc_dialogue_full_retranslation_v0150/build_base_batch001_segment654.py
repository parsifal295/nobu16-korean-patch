#!/usr/bin/env python3
"""Build Base authoring segment 654 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S654.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s654", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2202:0": "거짓말은 그만하세요\n속지 않아요",
    "9:2203:0": "하마터면 믿어\n버릴 뻔했군요……",
    "9:2204:0": "흥, 건방진 수작을!",
    "9:2205:0": "으윽!\n이 무슨 일인가……",
    "9:2206:0": "평범한 수단으로는\n통하지 않는가……",
    "9:2207:0": "자, 이제\n어찌 움직여야 할까……",
    "9:2208:0": "윽!　히……힘이……",
    "9:2209:0": "크윽…… 이렇게 나오는가……",
    "9:2210:0": "비겁한 수작을……",
    "9:2211:0": "으으음, 괘씸한……",
    "9:2212:0": "하필 여기서\n책략을 걸어오다니……",
    "9:2213:0": "크윽!\n성가시게 됐군……",
    "9:2214:0": "괴이한 책략을……",
    "9:2215:0": "이 수를 꺼내 들었는가……!",
    "9:2216:0": "이…… 이것이\n",
    "9:2216:1": "의 위력인가!",
    "9:2217:0": "……!\n참으로 빼어난 기예로다!",
    "9:2218:0": "이(가) 이런\n오의를 숨기고 있었다니",
    "9:2219:0": "의 위력……\n얕볼 수 없군요",
    "9:2220:0": "크윽……",
    "9:2220:1": "……\n참으로 무시무시한 무위로다……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2216:0",
    "9:2216:1",
    "9:2217:0",
    "9:2218:0",
    "9:2219:0",
    "9:2220:0",
    "9:2220:1",
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
                "segment": "base_msggame_B001_S654",
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
