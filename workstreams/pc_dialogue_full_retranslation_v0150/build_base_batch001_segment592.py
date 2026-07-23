#!/usr/bin/env python3
"""Build Base authoring segment 592 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S592.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s592", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:900:0": "다케다의 군법을\n눈으로 보라, 귀로 들어라!",
    "9:901:0": "이거나\n먹어라!",
    "9:902:0": "나의 투지를 보시라!",
    "9:903:0": "적을 격멸하리라!",
    "9:904:0": "도망칠 곳은 없습니다",
    "9:905:0": "내 오의의 진면목을\n똑똑히 보아라!",
    "9:906:0": "후후, 이건 잘 통하겠군……",
    "9:907:0": "일섬으로 적을 멸하리라!",
    "9:908:0": "받아 보아라!",
    "9:909:0": "이거나\n받아 보세요!",
    "9:910:0": "받아라, 나의 오의!",
    "9:911:0": "이것을 받아 보세요!",
    "9:912:0": "이것이라면 어떠냐!",
    "9:913:0": "이겼다, 이겼다!\n모두 뒤따르라!",
    "9:914:0": "이 야샤미노의 창을\n받아 보아라!",
    "9:915:0": "에잇! 얍!\n에잇! 얍!",
    "9:916:0": "아주 난리가 났구먼!",
    "9:917:0": "이 한 수로 혼란에 빠져라!",
    "9:918:0": "한동안은 움직이지 못하리라",
    "9:919:0": "적의 통솔이\n흐트러지고 있군요",
    "9:920:0": "혼란에 빠졌는가……\n지금이 공격할 때다!",
    "9:921:0": "혼란에 빠뜨리는 것쯤\n손쉬운 일이지",
    "9:922:0": "경솔한 자들은\n교란하기 쉽다",
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
                "segment": "base_msggame_B001_S592",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": 0,
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
