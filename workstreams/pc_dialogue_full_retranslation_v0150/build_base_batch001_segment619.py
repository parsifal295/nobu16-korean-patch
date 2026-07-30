#!/usr/bin/env python3
"""Build Base authoring segment 619 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S619.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s619", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1489:0": "언제까지\n대기해야 하는가……",
    "9:1490:0": "그저 보고만 있는\n것이라니……",
    "9:1491:0": "이대로 헛되이\n시간을 보내야 하는가……",
    "9:1492:0": "좋다,",
    "9:1492:1": "!\n해치워 버려라!",
    "9:1493:0": "!\n이겨 줘",
    "9:1493:1": "!",
    "9:1494:0": "인가……\n참으로 든든하구나",
    "9:1495:0": "좋은 소식을\n기다리겠습니다",
    "9:1496:0": "!\n마음껏 무예를 펼쳐 보이시오",
    "9:1497:0": "의 분전에\n기대해 볼까……",
    "9:1498:0": "에게\n무운이 함께하기를",
    "9:1499:0": "(이)라면\n해내 주겠지",
    "9:1500:0": "!\n그 적은 맡기겠습니다!",
    "9:1501:0": "놈의 상대는 맡겼다!",
    "9:1502:0": "여기서 쓰러뜨려\n두고 싶군요",
    "9:1503:0": "!\n힘내 주시오!",
    "9:1504:0": "뭐라고?　",
    "9:1504:1": "!\n네 도움 따윈 필요 없어",
    "9:1505:0": "따위에게\n도움을 받다니……",
    "9:1506:0": "의 원호……\n반길 마음은 들지 않는군",
    "9:1507:0": "원호입니까……\n무슨 속셈인지 모르겠군요",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1492:0",
    "9:1492:1",
    "9:1493:0",
    "9:1493:1",
    "9:1494:0",
    "9:1496:0",
    "9:1497:0",
    "9:1498:0",
    "9:1499:0",
    "9:1500:0",
    "9:1503:0",
    "9:1504:0",
    "9:1504:1",
    "9:1505:0",
    "9:1506:0",
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
                "segment": "base_msggame_B001_S619",
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
