#!/usr/bin/env python3
"""Build Base authoring segment 229 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S229.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s229", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3740:1": "이(가)",
    "6:3740:2": "영지에",
    "6:3741:0": "교섭을 위해,",
    "6:3741:1": "이(가)",
    "6:3741:2": "영지에",
    "6:3742:0": "와(과)의 중개자 무장을 해임합니다\n정말 괜찮으시겠습니까?",
    "6:3743:0": "와(과)의 관계를 돈독히 하고자\n마음을 다해 임무에 임하",
    "6:3744:0": "에 대한 중개를\n중단했",
    "6:3745:0": "을(를) 대신해\n",
    "6:3745:1": "와(과)의 관계 강화를 꾀하",
    "6:3746:0": "을(를) 대신해\n",
    "6:3746:1": "와(과)의 관계 유지에 힘쓰",
    "6:3747:0": "의 신용을 일정 수준 이상으로 올리고자\n관계 강화를 꾀하",
    "6:3748:0": "와(과)의 관계 유지에 힘쓰",
    "6:3749:0": "관계 유지에는 그리 많은 비용이 들지",
    "6:3751:0": "우리 가문과",
    "6:3751:1": "의 사이를\n중개해 보이",
    "6:3752:0": "의 신용을 얻고자\n세심한 주의를 기울여 임하",
    "6:3753:0": "우리 가문의 대표로서",
    "6:3753:1": "에게서\n반드시 신용을 얻어 보이",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S229", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
