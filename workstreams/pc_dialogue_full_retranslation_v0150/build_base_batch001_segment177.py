#!/usr/bin/env python3
"""Build Base authoring segment 177 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S177.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s177", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3114:0": "실속 있는 교섭이었군",
    "6:3115:0": "제법 교섭 수완이 뛰어나군…\n훌륭하도다",
    "6:3116:0": "흡족한 교섭이었구나",
    "6:3117:0": "나쁘지 않은 교섭이었습니다",
    "6:3118:0": "교섭 성과가 아주 좋군",
    "6:3119:0": "교섭한 보람이 있었습니다",
    "6:3120:0": "교섭이란 참으로 품이 드는 일이로군",
    "6:3121:0": "좋아\n전쟁은 일단 접어 두자고",
    "6:3122:0": "알겠다\n정전 제의를 받아들이마",
    "6:3123:0": "좋다\n이번 싸움은 이것으로 끝낸다",
    "6:3124:0": "좋습니다\n정전 제의를 받아들이겠습니다",
    "6:3125:0": "좋다\n싸움은 일단 그치게 하겠다",
    "6:3126:0": "좋다…화의에 응해 주마\n이 일은 내게 빚진 셈이다",
    "6:3127:0": "좋다\n우선 휴전하도록 하지",
    "6:3128:0": "좋다!\n우선 싸움을 그치자꾸나",
    "6:3129:0": "어쩔 수 없네요\n우선 군사를 거두지요",
    "6:3130:0": "좋다\n여기서는 서로 군사를 물리자꾸나",
    "6:3131:0": "좋습니다\n싸움은 일단 그만두겠습니다",
    "6:3132:0": "좋다\n싸움은 일단 그치도록 하지",
    "6:3133:0": "좋아, 이걸로 전쟁은 끝이다\n잊지 마, 알겠냐?",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S177", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
