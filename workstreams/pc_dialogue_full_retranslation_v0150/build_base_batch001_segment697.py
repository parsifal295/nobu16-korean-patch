#!/usr/bin/env python3
"""Build Base authoring segment 697 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S697.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s697", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3066:0": "에워싸여서는 당해낼 수 없다\n여기서는 거리를 두어라",
    "9:3067:0": "협격을 당하다니…\n후퇴도 어쩔 수 없겠군",
    "9:3068:0": "협격이라니 제법이구나…\n여기서는 물러난다!",
    "9:3069:0": "협격당하다니…\n한번 물러납시다",
    "9:3070:0": "협격이라니 비겁하구나\n일단… 물러난다!",
    "9:3071:0": "협격을 피하겠습니다\n한번 물러납시다",
    "9:3072:0": "에워싸이면 버틸 수 없다\n여기서는 일단 물러나자…",
    "9:3073:0": "병사들이 더는 버티지 못하겠어…\n교대 부대를 보내 줘!",
    "9:3074:0": "병사들의 피로가 한계로군…\n교대 부대를 보내 주면 좋겠는데…",
    "9:3075:0": "병사들이 지쳐 더는 싸울 수 없다…\n교대 부대를 부탁하고 싶군",
    "9:3076:0": "병사들의 체력이 한계입니다…\n교대 부대를 부탁드립니다",
    "9:3077:0": "피로가 이제 한계다…\n교대 부대는 아직인가…?",
    "9:3078:0": "병사들의 체력은 이제 한계로군…\n교대 부대를 이쪽으로 보내 주셨으면 하오",
    "9:3079:0": "그야말로 녹초가 됐군…\n교대 부대를 보내 주었으면 한다",
    "9:3080:0": "지쳐서 더는 싸울 수 없다…\n교대 부대는 어디 있는가…",
    "9:3081:0": "병사들이 지쳐 있사옵니다…\n교대 부대를 파견해 주십시오",
    "9:3082:0": "병사들이 지쳐 싸울 수 없다…\n교대 부대를 부탁하고 싶다",
    "9:3083:0": "이대로는 더 버틸 체력이 없습니다…\n교대 부대를 부탁드립니다",
    "9:3084:0": "병사들의 체력이 한계에 이르렀사옵니다…\n교대 부대를 보내 주시옵소서",
    "9:3085:0": "미안하다…\n더는 버틸 수가 없어",
    "9:3086:0": "너무 많은 병사를 잃었는가…\n미안하오, 철수하겠소",
    "9:3087:0": "병력을 너무 많이 잃었군\n어쩔 수 없다, 철수한다!",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()
STATIC_COORDINATES = set(TRANSLATIONS)


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
                "segment": "base_msggame_B001_S697",
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
