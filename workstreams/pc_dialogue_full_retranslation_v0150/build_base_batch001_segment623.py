#!/usr/bin/env python3
"""Build Base authoring segment 623 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S623.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s623", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1570:0": "과연 훌륭한\n활약이시옵니다",
    "9:1571:0": "장하도다! 해냈구나!",
    "9:1572:0": "좋습니다! 해냈군요!",
    "9:1573:0": "정말 잘했다!",
    "9:1574:0": "훌륭하다는 말밖에는\n할 말이 없군요",
    "9:1575:0": "\n해내셨구려!",
    "9:1576:0": "그렇게는 못 한다!\n한 방 먹여 줘라!",
    "9:1577:0": "그렇게는 못 한다! 자, 쏴라!",
    "9:1578:0": "괘씸한 것들…… 사격을\n멈추지 마라!",
    "9:1579:0": "그 여유를 곧\n무너뜨려 드리지요",
    "9:1580:0": "밀고 들어오게 둘쏘냐\n쏴라!",
    "9:1581:0": "그렇게 두지 않을 자는\n바로―",
    "9:1581:1": "이다!",
    "9:1582:0": "원호 사격!\n적의 돌진을 저지하라",
    "9:1583:0": "쏴라, 쏴라!\n밀고 들어오게 두지 마라!",
    "9:1584:0": "그렇게는 못 합니다!\n공격을 계속하세요!",
    "9:1585:0": "부질없는 짓을!\n계속 쏘아라!",
    "9:1586:0": "이 공격을 과연\n견딜 수 있겠습니까",
    "9:1587:0": "원호로\n밀어내 주마……!",
    "9:1588:0": "도와주마! 버텨라!",
    "9:1589:0": "지원하겠습니다! 버텨 주십시오!",
    "9:1590:0": "도와주마! 기죽지 마라!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1575:0",
    "9:1581:0",
    "9:1581:1",
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
                "segment": "base_msggame_B001_S623",
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
