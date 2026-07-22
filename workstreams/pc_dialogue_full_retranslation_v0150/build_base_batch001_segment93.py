#!/usr/bin/env python3
"""Build Base authoring segment 93 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S93.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s93", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1477:0": "와(과)", "6:1477:1": "이(가)", "6:1477:2": "개월간 정전",
    "6:1478:0": "와(과)", "6:1478:1": "의 정전이", "6:1478:2": "개월 연장",
    "6:1479:0": "와(과)", "6:1479:1": "이(가)", "6:1479:2": "개월간 정전",
    "6:1480:0": "와(과)", "6:1480:1": "의 정전이", "6:1480:2": "개월 연장",
    "6:1481:0": "와(과)", "6:1481:1": "이(가) 무기한 정전",
    "6:1482:0": "와(과)", "6:1482:1": "이(가) 무기한 정전",
    "6:1483:0": "와(과)", "6:1483:1": "이(가) 칙명으로 강화",
    "6:1484:0": "와(과)", "6:1484:1": "이(가) 칙명으로 강화",
    "6:1485:0": "와(과)", "6:1485:1": "이(가)", "6:1485:2": "개월간 동맹",
    "6:1486:0": "와(과)", "6:1486:1": "의 동맹이", "6:1486:2": "개월 연장",
    "6:1487:0": "와(과)", "6:1487:1": "이(가)", "6:1487:2": "개월간 동맹",
    "6:1488:0": "와(과)", "6:1488:1": "의 동맹이", "6:1488:2": "개월 연장",
    "6:1489:0": "의 공략 원군 요청을 달성",
    "6:1490:0": "이(가) 공략 원군 요청을 달성",
    "6:1491:0": "의 공략 원군 요청이 종료",
    "6:1492:0": "에 대한 공략 원군 요청이 종료",
    "6:1493:0": "의 방어 원군 요청을 달성하지 못함",
    "6:1494:0": "이(가) 방어 원군 요청을 달성하지 못함",
    "6:1495:0": "의 공략 원군 요청을 달성하지 못함",
    "6:1496:0": "이(가) 공략 원군 요청을 달성하지 못함",
}

DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
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
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
    print(ENGINE.json.dumps({"status":"ok","segment":"base_msggame_B001_S93","decision_count":len(rows),"retranslated":0,"dynamic_runtime_review_pending":len(rows),"steam_write_performed":False,"output":str(OUTPUT)},ensure_ascii=True,separators=(",",":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
