#!/usr/bin/env python3
"""Build Base authoring segment 598 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S598.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s598", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1033:0": "그렇게 만만하진\n않은 모양이군……",
    "9:1034:0": "거짓 정보를 간파하다니……",
    "9:1035:0": "까다로운 적이로군……",
    "9:1036:0": "맡겨 둬!",
    "9:1037:0": "알겠다!",
    "9:1038:0": "자, 나아가겠다!",
    "9:1039:0": "시작합니다!",
    "9:1040:0": "옛!",
    "9:1041:0": "맡겨 주십시오……",
    "9:1042:0": "알겠습니다!",
    "9:1043:0": "분부 받들겠소!",
    "9:1044:0": "하겠습니다!",
    "9:1045:0": "내게 맡겨라!",
    "9:1046:0": "맡겨 주시오!",
    "9:1047:0": "해내겠소!",
    "9:1048:0": "결판내 주마!",
    "9:1049:0": "자, 전력을 다해 나아가리라!",
    "9:1050:0": "내 모든 힘을 받아라!",
    "9:1051:0": "이슬처럼 스러져\n주시지요",
    "9:1052:0": "각오하라",
    "9:1053:0": "이것이 마지막이다",
    "9:1054:0": "진형 전법을\n발동합시다",
    "9:1055:0": "이것으로 끝이로다!",
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
                "segment": "base_msggame_B001_S598",
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
