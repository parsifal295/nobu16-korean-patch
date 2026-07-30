#!/usr/bin/env python3
"""Build Base authoring segment 274 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S274.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s274", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4214:1": "시겠습니까?",
    "6:4215:0": "이라면,\n이 책략이 어떻",
    "6:4216:0": "에 대해서는\n이 책략이 어떻",
    "6:4217:0": "의 공략을 위해\n국인중을 우리 편으로 끌어들이는 것도\n한 가지 선택일 듯하",
    "6:4218:0": "을(를) 실행하려면\n금전이 부족하",
    "6:4219:0": "을(를) 실행하려면\n노동력이 부족하",
    "6:4220:0": "에서",
    "6:4220:1": "의 장악을 중단",
    "6:4221:0": "에서",
    "6:4221:1": "의 건설을 중단",
    "6:4222:0": "조정의 중개자 무장을 해임합니다\n정말 괜찮으시겠습니까?",
    "6:4223:0": "조정의 후원을 얻기 위해\n빈틈없이 교섭하",
    "6:4224:0": "조정과의 교섭을\n중단하",
    "6:4225:0": "을(를) 대신해\n조정과의 관계 강화를 꾀하",
    "6:4226:0": "이(가) 조정과의 교섭을 시작",
    "6:4227:0": "조정과의 교섭을 종료",
    "6:4228:0": "금전 부족으로 모든 정책을 중단하",
    "6:4228:1": "\n필요한 정책은 다시 발령하도록 지시해 주십시오",
    "6:4229:0": "금전 부족으로 정책「",
    "6:4229:1": "」의 작업을 중단",
}

STATIC_COORDINATES: set[str] = {"6:4222:0", "6:4227:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S274", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
