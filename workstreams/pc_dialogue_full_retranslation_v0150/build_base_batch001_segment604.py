#!/usr/bin/env python3
"""Build Base authoring segment 604 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S604.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s604", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1162:0": "적의 마음은 꺾인 듯하니……\n단숨에 쓸어버려라!",
    "9:1163:0": "적은 이미 달아날 태세다\n공격하라!",
    "9:1164:0": "적의 사기가 떨어졌습니다\n계속 몰아붙입시다!",
    "9:1165:0": "흐름은 우리 쪽에 있다!\n몰아붙여라!",
    "9:1166:0": "이 기세 그대로\n계속 공격해야 합니다!",
    "9:1167:0": "노도와 같은 기세로\n몰아붙여라!",
    "9:1168:0": "이기고 싶다면\n멈춰 서지 마라!",
    "9:1169:0": "병사가 아무리 많이 쓰러져도\n결코 포기하지 않겠다!",
    "9:1170:0": "장수를 믿어라\n승리는 우리의 것이다",
    "9:1171:0": "역전할 길은\n아직 남아 있을 터……!",
    "9:1172:0": "살아남은 자들이여\n쓰러진 이들의 원수를 갚아라!",
    "9:1173:0": "이건……\n철수도 생각해야 하나?",
    "9:1174:0": "병사도 상당히\n줄어들고 말았군……",
    "9:1175:0": "아직 끝낼 수 없다!\n끝낼 수 없도다!",
    "9:1176:0": "아직 승패가 결정된\n것은 아닙니다!",
    "9:1177:0": "포기하지 마라!\n승기는 아직 남아 있다!",
    "9:1178:0": "벌써 약한 소리를 하기에는\n너무 이릅니다",
    "9:1179:0": "어떻게든\n살아남아야 한다!",
    "9:1180:0": "이건……\n어쩔 도리가 없구먼",
    "9:1181:0": "마지막 한 병사가 되더라도\n끝까지 싸우겠다!",
    "9:1182:0": "만사휴의인가……",
    "9:1183:0": "최선을\n다했습니다만……",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S604", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
