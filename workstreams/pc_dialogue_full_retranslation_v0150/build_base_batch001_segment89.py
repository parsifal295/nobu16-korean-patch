#!/usr/bin/env python3
"""Build Base authoring segment 89 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S89.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s89", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1401:0": "군단에 소속된 무장을 변경할 수 없습니다",
    "6:1402:0": "군단에 소속된 무장을 변경합니다",
    "6:1403:0": "군단에 소속된 성을 변경할 수 없습니다",
    "6:1404:0": "군단장의 지휘 범위를 벗어난 성입니다",
    "6:1405:0": "군단에 소속된 성을 변경합니다",
    "6:1406:0": "지휘 범위를 벗어나 최대 지배율과 소속 무장의\n획득 훈공이 감소합니다. 계속하시겠습니까?",
    "6:1407:0": "양도할 수 있는",
    "6:1407:1": "이(가) 없습니다",
    "6:1408:0": "어느 군단도",
    "6:1408:1": "을(를) 더 이상 보유할 수 없습니다",
    "6:1409:0": "불필요",
    "6:1410:0": "불필요",
    "6:1411:0": "군단의",
    "6:1411:1": "을(를) 조정합니다",
    "6:1412:0": "불필요",
    "6:1413:0": "불필요",
    "6:1414:0": "불필요",
    "6:1415:0": "다이묘 군단에 매월 상납할",
    "6:1415:1": "의 양을 설정합니다",
    "6:1416:0": "이 군단에는",
    "6:1416:1": "수입이 없습니다",
    "6:1417:0": "불필요",
    "6:1418:0": "불필요",
    "6:1419:0": "아무것도 변경하지 않았습니다",
    "6:1420:0": "군단을 편성할 수 없습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1407:0",
    "6:1407:1",
    "6:1408:0",
    "6:1408:1",
    "6:1411:0",
    "6:1411:1",
    "6:1415:0",
    "6:1415:1",
    "6:1416:0",
    "6:1416:1",
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
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
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
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S89",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
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
