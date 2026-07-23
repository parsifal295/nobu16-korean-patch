#!/usr/bin/env python3
"""Build Base authoring segment 720 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S720.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s720", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3506:0": ", 원호하겠다!\n안심하고 기다리시오!",
    "9:3507:0": ", 원호하겠습니다!\n안심하고 기다리십시오!",
    "9:3508:0": ", 지원하겠습니다!\n조금만 더 버텨 주십시오!",
    "9:3509:0": "지원이 필요한 듯하군\n우리가 도착할 때까지 버텨라!",
    "9:3510:0": "지원이 필요한 듯하오\n우리가 도착할 때까지 기다리시오!",
    "9:3511:0": ", 지원하러 가겠습니다\n잠시만 기다려 주시옵소서",
    "9:3512:0": ", 지원하러 가겠다!\n그때까지 버텨 다오!",
    "9:3513:0": ", 지원하러 가겠습니다!\n그때까지 버텨 주십시오!",
    "9:3514:0": "여기서는 지원할 수 없다\n더 앞으로 나간다",
    "9:3515:0": "지원하기에는 너무 먼가\n모두, 전진하라!",
    "9:3516:0": "바로 지원할 수 있도록\n배치를 바꾸겠다",
    "9:3517:0": "여기서는 지원할 수 없군요\n자리를 옮기도록 하지요",
    "9:3518:0": "이곳은 위치가 좋지 않군\n지원할 수 있는 곳으로 이동한다",
    "9:3519:0": "여기서는 지원할 수 없군\n좀 더 가까이 가도록 하지",
    "9:3520:0": "지원하기에는 너무 멀군\n자리를 옮겨야겠군",
    "9:3521:0": "여기는 너무 멀군\n지원할 수 있는 위치로 가자",
    "9:3522:0": "여기서는 지원할 수 없습니다\n저희는 전진하겠습니다",
    "9:3523:0": "아군을 지원하기에는 너무 멀군\n그렇다면 이동하도록 하지",
    "9:3524:0": "이 위치는 좋지 않군요\n지원할 수 있는 곳으로 이동하겠습니다",
    "9:3525:0": "아군을 지원하기에는 너무 멀군\n이동하자",
    "9:3526:0": "놈들이 오고 있군!\n무슨 일이 있어도 지켜 내겠다",
    "9:3527:0": "빼앗기게 둘 수는 없다!\n요격하러 간다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:3506:0",
    "9:3507:0",
    "9:3508:0",
    "9:3511:0",
    "9:3512:0",
    "9:3513:0",
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
                "segment": "base_msggame_B001_S720",
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
