#!/usr/bin/env python3
"""Build Base authoring segment 298 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S298.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s298", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4458:0": "아직 여력이 있",
    "6:4458:2": "도 겸임할 수\n있을 듯하",
    "6:4459:0": "아직 더 일할 수 있",
    "6:4459:1": "\n해임",
    "6:4460:0": "설마 해임을 생각하고 계십니까?",
    "6:4460:1": "\n부디",
    "6:4460:2": " 다시 생각해 주십시오…",
    "6:4461:0": "에게 맡긴 아래 활동이 중단됩니다\n·임무「",
    "6:4461:1": "」\n·건의「",
    "6:4461:2": "」\n그래도 진행하시겠습니까?",
    "6:4462:0": "에게 맡긴 아래 활동이 중단됩니다\n·임무「",
    "6:4462:1": "」\n그래도 진행하시겠습니까?",
    "6:4463:0": "에게 맡긴 아래 활동이 중단됩니다\n·건의「",
    "6:4463:1": "」\n그래도 진행하시겠습니까?",
    "6:4464:0": "에서 온 원군이 임무를 마치고 퇴각",
    "6:4465:0": "에 파견한 원군이 성으로 귀환하기 시작",
    "6:4466:0": "우리의 도움이 더는 필요하지 않은 듯하군\n그럼 군을 물리도록 하겠소",
    "6:4467:0": "의 도움으로 목적을 달성했다\n이번 원군에 감사하오",
    "6:4468:0": "주가인 「",
    "6:4468:1": "」와(과) 「",
}

STATIC_COORDINATES: set[str] = {"6:4460:0", "6:4460:1", "6:4460:2", "6:4466:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S298", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
