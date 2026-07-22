#!/usr/bin/env python3
"""Build Base authoring segment 168 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S168.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s168", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3026:0": "이 정도면 불평할 리 없지\n오히려 크게 기뻐할 거야",
    "6:3027:0": "이 조건이라면 무사의 체면에\n상처를 내는 일은 없을 것이다",
    "6:3028:0": "이",
    "6:3028:1": "이(가) 이만큼 양보한 것이다\n설마 거절하지는 않겠지",
    "6:3029:0": "무난한 요구로군요\n거절당할 일은 없겠지요",
    "6:3030:0": "이 정도가 무난하겠군",
    "6:3031:0": "얻는 것보다 내주는 것이 많지만\n확실하군… 작게 잃고 크게 얻는 셈이지",
    "6:3032:0": "이 정도라면\n요구해도 괜찮을 것이다",
    "6:3033:0": "이만큼 양보하면\n상대도 납득하겠지",
    "6:3034:0": "이 정도를 요구해도\n상대는 싫은 내색을 하지 않겠지요",
    "6:3035:0": "이 정도를 요구해도 문제없겠지",
    "6:3036:0": "이것조차 거절한다면\n그릇이 얼마나 작은지 알 만하군요",
    "6:3037:0": "음, 이 정도라면 괜찮다",
    "6:3038:0": "이 내용으로 교섭을 제안하겠습니다만,\n괜찮겠습니까?",
    "6:3039:0": "조정과의 교섭을 중단합니다. 계속하시겠습니까?",
    "6:3040:0": "선택한 주청 내용을 모두 초기화합니다\n계속하시겠습니까?",
    "6:3041:0": "선택한 제안 내용을 모두 초기화합니다\n계속하시겠습니까?",
    "6:3042:0": "와(과)의 혼인 동맹이 해소",
    "6:3043:0": "와(과)의",
    "6:3043:1": "개월 동맹으로 전환",
}

STATIC_COORDINATES = {
    "6:3026:0", "6:3027:0", "6:3029:0", "6:3030:0", "6:3031:0",
    "6:3032:0", "6:3033:0", "6:3034:0", "6:3035:0", "6:3036:0",
    "6:3037:0", "6:3038:0", "6:3039:0", "6:3040:0", "6:3041:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S168", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
