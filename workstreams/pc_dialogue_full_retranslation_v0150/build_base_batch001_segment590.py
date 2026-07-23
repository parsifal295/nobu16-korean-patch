#!/usr/bin/env python3
"""Build Base authoring segment 590 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S590.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s590", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:856:0": "물러난다…… 목숨이라도\n건졌으니 다행이다",
    "9:857:0": "면목 없소…… 내 무능함이\n부끄러울 따름이오……",
    "9:858:0": "미안하오……\n이만 물러나겠소",
    "9:859:0": "죄송합니다……\n뒷일은 부탁드립니다!",
    "9:860:0": "나는 여기까지다……\n뒷일은 부탁한다!",
    "9:861:0": "죄송합니다……\n먼저 물러나겠습니다……",
    "9:862:0": "먼저 물러나겠사옵니다……\n무운을 빕니다!",
    "9:863:0": "늦어 버린 모양이군……",
    "9:864:0": "내 전법을\n이제 와 써 봐야 무익한가",
    "9:865:0": "상대가 없군……\n늦었는가",
    "9:866:0": "제때 오지 못한\n것입니까……",
    "9:867:0": "이래서는\n전법을 쓸 수 없군……",
    "9:868:0": "전법을 펼칠 상황이\n아니게 되었는가……",
    "9:869:0": "쯤 되는 자가\n기회를 놓치다니……",
    "9:870:0": "으음, 제때 오지 못했는가",
    "9:871:0": "늦은 모양입니다……",
    "9:872:0": "큭……\n제때 오지 못했는가……",
    "9:873:0": "때를 놓쳤으니……\n아무 쓸모도 없게 되었사옵니다",
    "9:874:0": "상대가 없지 않소……?",
    "9:875:0": "단숨에 들이쳐라!",
    "9:876:0": "의 싸움을\n도와드리겠소!",
    "9:877:0": "모조리 쓸어버리고 와라!",
}

DYNAMIC_RUNTIME_COORDINATES = {"9:869:0", "9:876:0"}
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
                "segment": "base_msggame_B001_S590",
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
