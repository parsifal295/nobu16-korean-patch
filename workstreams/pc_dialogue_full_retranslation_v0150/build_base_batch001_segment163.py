#!/usr/bin/env python3
"""Build Base authoring segment 163 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S163.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s163", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2935:0": "이거 참, 실로 어려운 부탁을 하시는군요…\n그에 걸맞은 보답은 준비하셨겠지요?",
    "6:2936:0": "이 정도 돈으로는\n조정이 납득하지 않겠지…",
    "6:2937:0": "이 정도 돈으로는\n조정이 납득할 리 없을 터…",
    "6:2938:0": "이 정도 돈으로는\n조정도 수긍하지 않겠군…",
    "6:2939:0": "이 정도 돈으로는\n조정이 납득하지 않을 것입니다…",
    "6:2940:0": "이 정도 돈으로는\n조정도 납득하지 않으리…",
    "6:2941:0": "이 정도 돈으로는\n조정이 납득하지 않겠지…",
    "6:2942:0": "이 정도 돈으로\n조정이 납득하리라고는 생각지 않지만…",
    "6:2943:0": "이 정도 돈으로는\n조정도 납득하지 않겠구나…",
    "6:2944:0": "고작 이만큼으로는\n조정도 납득하지 않겠지요…",
    "6:2945:0": "이 정도 돈으로\n조정이 납득하겠는가…?",
    "6:2946:0": "이 정도로 조정이 납득하겠습니까…",
    "6:2947:0": "이 정도 돈으로는\n조정이 납득하지 않겠지…",
    "6:2948:0": "이만큼이면\n조정도 부탁을 들어주겠지",
    "6:2949:0": "이만큼이면\n조정도 우리의 부탁을 들어주리라",
    "6:2950:0": "이만큼이면\n조정도 기꺼이 부탁을 들어주겠지",
    "6:2951:0": "이만큼이면\n조정도 기꺼이 부탁을 들어줄 것입니다",
    "6:2952:0": "이만큼이면 조정도 기꺼이 응하리라",
    "6:2953:0": "이만큼이면 조정도 움직일 수 있다…!",
    "6:2954:0": "이만큼이면\n조정에 올린 요구도 받아들여질 터",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S163", "decision_count": len(rows),
                             "retranslated": len(rows), "dynamic_runtime_review_pending": 0,
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
