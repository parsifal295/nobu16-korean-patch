#!/usr/bin/env python3
"""Build Base authoring segment 92 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S92.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s92", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1461:0": "알겠습니다",
    "6:1461:1": "…\n우리 가문을 위한 일이라면 어쩔 수 없지요",
    "6:1462:0": "성주 이동은 정책「",
    "6:1462:1": "」 LV",
    "6:1462:2": "에서 해금됩니다",
    "6:1463:0": "군단장이 이동할 수 있는 성이 없습니다",
    "6:1464:0": "군단장이 출진 중입니다",
    "6:1465:0": "군단장의 소속 성을 변경합니다",
    "6:1466:0": "합계",
    "6:1466:1": "개 성이 통치 범위를 벗어나\n다이묘 군단 소속이 됩니다. 계속하시겠습니까?",
    "6:1467:0": "새 군단에 소속시킬 성을 선택하십시오",
    "6:1468:0": "편성 대상 무장이나 성이 임무 또는 건의를\n수행 중이면 해당 행동이 중지됩니다\n계속하시겠습니까?",
    "6:1469:0": "이(가)",
    "6:1469:1": "을(를) 종속시킴",
    "6:1470:0": "이(가)",
    "6:1470:1": "에게 신종",
    "6:1471:0": "와(과)",
    "6:1471:1": "이(가) 혼인 동맹",
    "6:1472:0": "와(과)",
    "6:1472:1": "이(가) 혼인 동맹",
    "6:1473:0": "와(과)",
    "6:1473:1": "이(가) 절연",
    "6:1474:0": "와(과)",
    "6:1474:1": "이(가) 절연",
    "6:1475:0": "와(과)",
    "6:1475:1": "이(가) 절연",
    "6:1476:0": "이(가)",
    "6:1476:1": "을(를) 종속시킴",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {1461, 1462, 1466, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476}
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
                "segment": "base_msggame_B001_S92",
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
