#!/usr/bin/env python3
"""Build Base authoring segment 507 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S507.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s507", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:359:0": "올해는 풍작인 듯합니다",
    "8:360:0": "올해는 흉작인 듯합니다",
    "8:361:0": "건조한 날씨가 이어져 가뭄이 발생한 듯합니다",
    "8:362:0": "폭우로 홍수가 발생한 듯합니다",
    "8:363:0": "대형 태풍이 상륙한 듯합니다",
    "8:364:0": "내 목숨을 걸고도\n천하 통일에는 이르지 못했는가……",
    "8:365:0": "의 「",
    "8:365:1": "」이(가) 발전했습니다",
    "8:366:0": "이(가) 「",
    "8:366:1": "」을(를) 탈취했습니다",
    "8:367:0": "을(를) 「",
    "8:367:1": "」에게 빼앗겼습니다",
    "8:368:0": "아군이 「",
    "8:368:1": "」에서 야전 준비에 들어갔습니다!",
    "8:369:0": "이(가) 「",
    "8:369:1": "」의 야전에 합류했습니다!",
    "8:370:0": "난세를 끝낼 영웅은 나타나지 않았습니다\n이로써 전국시대는 막을 내립니다",
    "8:371:0": "저장할 수 없는 상황이 발생하여\n자동 저장에 실패했습니다\n하드 디스크 용량 등을 확인해 주십시오",
}

STATIC_COORDINATES = {
    *(f"8:{record_id}:0" for record_id in range(359, 365)),
    "8:370:0",
    "8:371:0",
}


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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S507", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
