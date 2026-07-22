#!/usr/bin/env python3
"""Build Base authoring segment 165 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S165.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s165", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2972:1": "밖에 부탁할 이가 없군",
    "6:2973:0": "긴히 부탁할 일이 있소\n", "6:2973:1": ", 들어주지 않겠는가",
    "6:2974:0": "부탁을 들어주시겠습니까\n훗날 양가 모두에게 이익이 될 것입니다",
    "6:2975:0": "청이 있어 찾아왔소\n부디 이야기를 들어주시길 바라오",
    "6:2976:0": "시간을 내주시니 황공하옵니다\n오늘은 청이 있어 찾아뵈었습니다",
    "6:2977:0": "우리 가문을 돕는다 생각하시고 이 부탁을\n부디 들어주시옵소서!",
    "6:2978:0": "오,", "6:2978:1": ", 무슨 일이냐?",
    "6:2979:0": "오오, 이분은,", "6:2979:1": "님",
    "6:2980:0": "님, 오늘은 어인 일이십니까",
    "6:2981:0": "뭐, 요구와 대가에 달렸다고…\n할 수 있겠군요",
    "6:2982:0": "흠, 그렇군…?",
    "6:2983:0": "물론 양가를 위한 이야기라면\n기꺼이…",
    "6:2984:0": "오오,", "6:2984:1": "님이 아니시오",
    "6:2985:0": "어서 오시오",
    "6:2986:0": "님, 곤란하신 모양이군요",
    "6:2987:0": "님, 잘 오셨습니다!",
}

STATIC_COORDINATES = {
    "6:2974:0", "6:2975:0", "6:2976:0", "6:2977:0",
    "6:2981:0", "6:2982:0", "6:2983:0", "6:2985:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S165", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
