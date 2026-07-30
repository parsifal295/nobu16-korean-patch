#!/usr/bin/env python3
"""Build Base batch 001 segment 04 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S04.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s04", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:132:0": "편히 쉬십시오\n우리 가문은… 반드시 끝까지 지켜 내겠습니다",
    "2:133:0": "뒷일은 맡겨 주시오\n반드시 가문을 끝까지 지켜 내겠소!",
    "2:134:0": "선대의 뒤를 이어\n",
    "2:134:1": "이 이 가문을 끝까지 지키겠습니다",
    "2:135:0": "에게 맡겨 주십시오\n반드시 이 가문을 끝까지 지켜 내겠습니다",
    "2:136:0": "님, 이",
    "2:136:1": "은 목숨을 걸고\n반드시",
    "2:136:2": "의 존속과 번영을\n이루어 내겠",
    "2:137:0": "이",
    "2:137:1": "의 당주로",
    "2:138:0": "의",
    "2:138:1": "이 출가",
    "2:139:0": "에서",
    "2:139:1": "가문",
    "2:139:2": "으로 세력명 변경",
    "2:140:0": "은",
    "2:140:1": "에 의해 멸망",
    "2:141:0": "은",
    "2:141:1": "에 의해 멸망",
    "2:142:0": "이 병에 걸렸습니다",
    "2:143:0": "을 포함한",
    "2:143:1": "명이 병에 걸렸습니다",
    "2:144:0": "이 병에서 회복했습니다",
    "2:145:0": "을 포함한",
    "2:145:1": "명이 병에서 회복했습니다",
    "2:146:0": "공략 대상인",
    "2:146:1": "을 제압해 공략 방침을 달성했습니다",
}


STATIC_RUNTIME_NOT_REQUIRED = {
    "2:132:0",
    "2:133:0",
}


DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS) - STATIC_RUNTIME_NOT_REQUIRED


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
                "scope_classification": (
                    "runtime_fragment_pending"
                    if coordinate in DYNAMIC_RUNTIME_COORDINATES
                    else "retranslated"
                ),
                "layout_review": "unchanged_from_current",
                "runtime_review": (
                    "pending" if coordinate in DYNAMIC_RUNTIME_COORDINATES else "not_required"
                ),
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context",
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
                "segment": "base_msggame_B001_S04",
                "decision_count": len(rows),
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
