#!/usr/bin/env python3
"""Build Base authoring segment 190 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S190.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s190", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3335:0": "이 세력과",
    "6:3335:1": "와(과)의 강화를 주청하기에는 금전이 부족합니다",
    "6:3336:0": "이미 선택한 세력입니다",
    "6:3337:0": "가상한 마음가짐이오\n앞으로도 근왕의 뜻을 잊지 마시오",
    "6:3338:0": "의 사람이 찾아오다니 별일이로군\n무슨 용무인고?",
    "6:3339:0": "인가\n잘 찾아왔구려",
    "6:3340:0": "오오,",
    "6:3340:1": "인가\n오랜만이로군",
    "6:3341:0": "오오,",
    "6:3341:1": "님!\n천황께서도 기다리고 계시네",
    "6:3342:0": "칙명 강화를 주청할 수 있는 대상 세력이 없습니다",
    "6:3343:0": "이(가)",
    "6:3343:1": "에 취임",
    "6:3344:0": "의 악명이",
    "6:3344:1": "으로(로)",
    "6:3345:0": "의 조정 공헌치가",
    "6:3345:1": "으로(로)",
    "6:3346:0": "해고하면\n군단이 해산되고 혼인 동맹도 파기됩니다\n괜찮으시겠습니까?",
    "6:3347:0": "해고하면\n군단이 해산됩니다\n괜찮으시겠습니까?",
    "6:3348:0": "해고하면\n혼인 동맹이 파기됩니다\n괜찮으시겠습니까?",
}

STATIC_COORDINATES: set[str] = {
    "6:3336:0", "6:3337:0", "6:3342:0", "6:3346:0", "6:3347:0", "6:3348:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S190", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
