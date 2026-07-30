#!/usr/bin/env python3
"""Build Base authoring segment 617 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S617.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s617", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1445:0": "문답무용!\n무슨 수를 써서라도 베겠다!",
    "9:1446:0": "도리어 해치워 주마!",
    "9:1447:0": "가볍게 해치워\n드리지요",
    "9:1448:0": "지껄이지 말고\n덤벼라!",
    "9:1449:0": "후후, 도리어 해치울\n좋은 기회로군……",
    "9:1450:0": "……여전히 눈엣가시로군",
    "9:1451:0": "흥, 끝장을\n내 주마!",
    "9:1452:0": "질 수는\n없다!",
    "9:1453:0": "좋다, 상대해 주마!",
    "9:1454:0": "얕보시면\n곤란합니다",
    "9:1455:0": "덤빌 상대를 잘못 골랐구나!",
    "9:1456:0": "덤벼라……\n박살 내 주마!",
    "9:1457:0": "정정당당히, 승부다!",
    "9:1458:0": "혈기가 왕성하구나\n덤벼 보아라!",
    "9:1459:0": "분수도 모르다니\n어리석군요",
    "9:1460:0": "나의 무예를 선보이리라!",
    "9:1461:0": "온다…… 방심하지 마라",
    "9:1462:0": "온다, 대비하라",
    "9:1463:0": "자, 덤벼 보시게나!",
    "9:1464:0": "상대가 누구든\n방심하지 않겠습니다!",
    "9:1465:0": "우리를 이길 수 있다고\n생각하느냐",
    "9:1466:0": "쉽게 이길 수 있으리라\n생각하지 마십시오",
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
                "segment": "base_msggame_B001_S617",
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
