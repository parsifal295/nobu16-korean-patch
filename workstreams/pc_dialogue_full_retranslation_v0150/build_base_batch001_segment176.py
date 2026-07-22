#!/usr/bin/env python3
"""Build Base authoring segment 176 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S176.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s176", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3100:0": "이동을 시작합니다",
    "6:3101:0": "무장을 이동시킬 필요는 없을 듯합니다",
    "6:3102:0": "이(가)",
    "6:3102:1": "에 입성",
    "6:3103:0": "들",
    "6:3103:1": "명이",
    "6:3103:2": "에 입성",
    "6:3104:0": "…역시 서로 용납할 수 없는 운명이었던 듯",
    "6:3104:2": "와(과)는 여기까지",
    "6:3105:0": "군단장·",
    "6:3105:1": "이(가) 출분",
    "6:3106:0": "의 주군·",
    "6:3106:1": "이(가) 출분",
    "6:3107:0": "이(가) 출분",
    "6:3108:0": "그대들과의 맹약은,\n이제 무용지물일 뿐…\n이것으로 끊도록 하겠소",
    "6:3109:0": "나쁘지 않은 거래였군",
    "6:3110:0": "교섭 성과는 그런대로인가",
    "6:3111:0": "앞으로도\n원만히 지내고 싶은 법이로군",
    "6:3112:0": "좋은 교섭이었다고 생각합니다",
    "6:3113:0": "끈기 있게 교섭한 보람이 있었군",
}

STATIC_COORDINATES: set[str] = {
    "6:3100:0",
    "6:3101:0",
    "6:3108:0",
    "6:3109:0",
    "6:3110:0",
    "6:3111:0",
    "6:3112:0",
    "6:3113:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S176", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
