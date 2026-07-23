#!/usr/bin/env python3
"""Build Base authoring segment 601 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S601.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s601", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1096:0": "여기서부터\n전세를 뒤집어 주마!",
    "9:1097:0": "여기서부터\n흐름을 바꾸어 보자!",
    "9:1098:0": "든든한 아군이\n있었구나",
    "9:1099:0": "우리의 승기를……\n찾아냈습니다",
    "9:1100:0": "좋아, 이것으로\n아직 이길 수 있겠구나!",
    "9:1101:0": "활로를 찾아냈다……\n해 보자!",
    "9:1102:0": "훌륭하오…… 기사회생이란\n바로 이런 것이오!",
    "9:1103:0": "고맙구나!\n우리는 아직 더 싸울 수 있다",
    "9:1104:0": "이것으로\n유리하게 싸울 수 있겠군요",
    "9:1105:0": "아직 활로가\n남아 있다는 뜻이군!",
    "9:1106:0": "살았습니다……\n아직 싸울 수 있겠군요",
    "9:1107:0": "오오! 이것으로……!\n……지금부터로군요",
    "9:1108:0": "재미있군, 투지가\n불타오르잖아!",
    "9:1109:0": "아직이다! 싸움은 아직\n끝나지 않았다!",
    "9:1110:0": "적도 제법 움직이는군",
    "9:1111:0": "그 정도로는\n동요하지 않습니다",
    "9:1112:0": "이까짓 것……\n아직 끝낼 수는 없다!",
    "9:1113:0": "……허둥대지 마라\n아직 패배가 정해진 건 아니다",
    "9:1114:0": "조금…… 궁지에 몰리고\n말았군요",
    "9:1115:0": "당했구나…… 에잇!\n전세를 뒤집는 게다!",
    "9:1116:0": "퇴로가…… 하지만\n아직 싸울 수 있습니다!",
    "9:1117:0": "이쯤이야!\n살을 내주고 뼈를 취하리라",
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
                "segment": "base_msggame_B001_S601",
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
