#!/usr/bin/env python3
"""Build Base authoring segment 268 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S268.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s268", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4144:0": "병력 준비는 만전",
    "6:4144:1": "\n영지 확대의 기회가 온다면\n즉시 출진",
    "6:4145:0": "병력이 부족해 영지 확대는 바랄",
    "6:4145:1": "\n당분간 영지 발전에 힘쓰며\n주변의 빈틈을 엿보",
    "6:4146:0": "영내의 병력이 줄어들고 있어\n병력 확보를 추진해",
    "6:4147:0": "전선의 병력이 부족해\n공략할 수 있는 세력이",
    "6:4147:1": "\n다른 군단의 지원이 있다면 혹시…",
    "6:4148:0": "적의 성을 공략하기에는\n전선의 병력만으로는 부족하다\n더 많은 병력이 필요하다",
    "6:4149:0": "상황이 바뀌어\n공략 지시를",
    "6:4149:1": "성을\n공격할 수 있",
    "6:4150:0": "주변에 공략할 수 있는 성이 없어\n영지 발전에 힘써",
    "6:4151:0": "주변에 공략할 수 있는 성이 없어\n영내 발전에 주력하",
    "6:4151:1": "\n이미 모든 취락을 장악하",
    "6:4152:0": "주변에 공략할 수 있는 성이",
    "6:4152:1": "\n군단 방침을 제시하여",
    "6:4152:2": "면\n",
    "6:4152:3": "의 출진 원호도 가능합니다",
    "6:4153:0": "주변에 공략할 수 있는 성이",
    "6:4153:1": "\n내정을 추진하고 있으며",
    "6:4153:2": "을(를) 포함한\n",
}

STATIC_COORDINATES: set[str] = set()


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
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S268", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
