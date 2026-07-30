#!/usr/bin/env python3
"""Build Base batch 001 segment 07 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S07.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s07", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:181:0": "세력이 다스리는 지역:",
    "2:181:1": "의 모든 성",
    "2:182:0": "옛 본거지:",
    "2:182:1": "에서\n",
    "2:182:2": "에 옮길 수 없는 시설이 있습니다\n그대로 본거지를 이전하시겠습니까?",
    "2:183:0": "본거지 이전 예정지:",
    "2:183:1": "에서\n",
    "2:183:2": "에 옮길 수 없는 시설이 있습니다\n그대로 본거지를 이전하시겠습니까?",
    "2:184:0": "에 옮길 대상:",
    "2:184:1": (
        "의 시설\n"
        "건설 칸이 부족합니다\n"
        "이설을 포기할 시설을 선택해 주십시오"
    ),
    "2:185:0": "에서",
    "2:185:1": "으로\n본거지 이전을 완료했습니다",
    "2:186:0": "옛 본거지:",
    "2:186:1": "이 함락되어\n",
    "2:186:2": "으로 본거지를 옮겼습니다",
    "2:187:0": "철회한 정책: 「",
    "2:187:1": "」 외",
    "2:187:2": "개",
    "2:188:0": "철회한 정책: 「",
    "2:188:1": "」",
    "2:189:0": "위신 저하로 철회한 정책: 「",
    "2:189:1": "」",
    "2:190:0": "다이묘의 주의와 맞지 않아 철회한 정책: 「",
    "2:190:1": "」",
    "2:191:0": "철회한 정책: 「",
    "2:191:1": "」",
    "2:192:0": "발령한 정책: 「",
    "2:192:1": "」 외",
    "2:192:2": "개",
    "2:193:0": "정책 발령: 「",
    "2:193:1": "」 레벨:",
    "2:193:2": "단계",
    "2:194:0": "발령한 정책: 「",
    "2:194:1": "」 외",
    "2:194:2": "개",
    "2:195:0": "정책 발령: 「",
    "2:195:1": "」 레벨:",
    "2:195:2": "단계",
    "2:196:0": "철회 예정 정책: 「",
    "2:196:1": "」",
    "2:197:0": "철회 예정 정책: 「",
    "2:197:1": "」 외",
    "2:197:2": "개",
    "2:198:0": "발령 준비를 시작한 정책: 「",
    "2:198:1": "」 레벨:",
    "2:198:2": "단계",
    "2:199:0": "발령 준비를 시작한 정책: 「",
    "2:199:1": "」 외",
    "2:199:2": "개",
    "2:200:0": "발령 준비를 시작한 정책: 「",
    "2:200:1": "」 레벨:",
    "2:200:2": "단계",
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
                "segment": "base_msggame_B001_S07",
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
