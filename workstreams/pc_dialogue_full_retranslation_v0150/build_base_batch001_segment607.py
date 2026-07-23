#!/usr/bin/env python3
"""Build Base authoring segment 607 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S607.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s607", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1228:0": "지금이다!\n바위를 힘껏 내던져라!",
    "9:1229:0": "바위를 떨어뜨려라!",
    "9:1230:0": "돌팔매 세례를 퍼부어라!",
    "9:1231:0": "돌팔매 싸움을 벌여 봅시다",
    "9:1232:0": "바위 맛을 보아라!",
    "9:1233:0": "옜다\n바위나 받아라",
    "9:1234:0": "후후……\n낙석을 조심하십시오",
    "9:1235:0": "지금이다!\n적을 짓뭉개 버려라!",
    "9:1236:0": "지금입니다! 낙석을!",
    "9:1237:0": "자, 바위를 떨어뜨려라!",
    "9:1238:0": "돌 세례를 퍼붓는 겁니다!",
    "9:1239:0": "바위로 적군을\n쓸어버려라!",
    "9:1240:0": "이제부터가 진짜다!\n기합을 넣어라!",
    "9:1241:0": "투지를 불태워라!\n지금이 승부처다!",
    "9:1242:0": "떨쳐 일어나라! 승리의 바람은\n우리에게 분다!",
    "9:1243:0": "모두, 끝까지\n방심하지 마라!",
    "9:1244:0": "여기가 승부의\n갈림길이다!",
    "9:1245:0": "분발하라!\n우리 가문의 승리를 위하여!",
    "9:1246:0": "자, 여기서부터\n승리를 향해 곧장 나아가자!",
    "9:1247:0": "떨쳐 일어나라!\n여기가 고비다!",
    "9:1248:0": "마지막에 이기는 것은\n우리입니다!",
    "9:1249:0": "용기를 불러일으켜라!\n모두, 승리하자!",
    "9:1250:0": "여기가 고비입니다\n마음을 다잡고 갑시다",
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
                "segment": "base_msggame_B001_S607",
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
