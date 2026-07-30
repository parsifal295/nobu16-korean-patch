#!/usr/bin/env python3
"""Build Base authoring segment 373 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S373.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s373", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1060:0": "이(가) 상대라면\n성에 남겨 둘 병력도\n고려해야 하겠군요",
    "7:1061:0": ", 상대로 삼기에\n부족함이 없도다\n자, 맞아 싸우리라",
    "7:1062:0": ", 이 에치고의 용마저\n무사의 피가 끓게 하다니\n좌시할 수 없도다",
    "7:1063:0": "은(는) 우리와 맞먹는 적\n침공해 온 이상\n반드시 요격해야 할 것입니다",
    "7:1064:0": "와(과)는 병력이 대등하다\n적의 움직임을 읽고 허를 찔러\n신속히 섬멸해야 한다",
    "7:1065:0": "이(가) 쳐들어오다니\n내버려 두면\n훗날 큰 화근이 될지도 모른다",
    "7:1066:0": "은(는) 나와 동격인 상대\n하지만 이 정도에 겁먹는다면\n독안룡의 이름에 먹칠하리라!",
    "7:1067:0": "은(는) 우리와 맞먹는 적\n하지만 힘을 아끼지 않는다면\n승산은 있을 것입니다",
    "7:1068:0": "은(는) 우리와 호각이니\n주군의 지휘에 따라\n승패가 갈릴 것이옵니다",
    "7:1069:0": "은(는) 강해\n싸우려면 우리에게 맡겨 줘\n되레 박살 내 주겠어!",
    "7:1070:0": "이(가) 쳐들어왔군\n쫓아낼 수는 있다만\n어떻게 할 거지?",
    "7:1071:0": ", 상대로 삼기에\n부족함이 없도다!\n되받아쳐 주마!",
    "7:1072:0": "이(가) 상대라니\n더없는 영광이로다\n등을 보이면 후대까지 수치다!",
    "7:1073:0": "에게 기죽지 마라\n우리는 주군의 지휘를 믿고\n길을 개척할 뿐이다",
    "7:1074:0": "와(과)의 싸움이라면\n좋은 승부가 되겠구나\n무사의 피가 끓는구먼",
    "7:1075:0": "와(과) 우리 군의 병력은\n서로 대등하옵니다\n어찌하시겠사옵니까",
    "7:1076:0": "이(가) 상대라니……\n병력 차이가 염려되지만\n방심하지 않으면 이길 수 있을 것입니다",
    "7:1077:0": "따위가 무엇이 두려우랴\n소인이 선봉을 맡아\n적에게 한 칼 먹여 주겠나이다!",
    "7:1078:0": "은(는) 내 호적수로\n손색없는 자로다\n꼭 전력으로 겨뤄 보고 싶구나",
    "7:1079:0": "에게는 없고\n우리에게 있는 것이라면\n뛰어난 책사이겠지",
}

STATIC_COORDINATES: set[str] = set()


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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S373", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
