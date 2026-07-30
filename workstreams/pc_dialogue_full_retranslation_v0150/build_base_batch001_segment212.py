#!/usr/bin/env python3
"""Build Base authoring segment 212 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S212.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s212", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3551:0": "두 사람 모두, 앞으로도 부탁하",
    "6:3552:0": "두 사람의 힘으로 우리 가문을 떠받쳐",
    "6:3553:0": "참으로 경사스럽다\n앞으로도 우리 가문을 떠받쳐",
    "6:3554:0": "앞으로 두 사람이 힘을 합쳐\n우리 가문을 떠받쳐",
    "6:3555:0": "경사로다, 경사로다\n앞으로도 부탁하",
    "6:3556:0": "이 두 사람이라면\n우리 가문을 떠받칠 기둥이 되",
    "6:3557:0": "앞으로도 잘 부탁드립니다",
    "6:3558:0": "두 사람의 힘이 우리 가문에 필요하네\n잘 부탁하네",
    "6:3559:0": "두 사람 모두 그 재능을 살려\n우리 가문을 떠받쳐",
    "6:3560:0": "두 사람의 활약을 기대하고 있습니다\n잘 부탁드립니다",
    "6:3561:0": "좋은 인연이군요\n앞으로도 잘 부탁드립니다",
    "6:3562:0": "앞으로 두 사람이 힘을 합쳐\n우리 가문을 떠받쳐",
    "6:3563:0": "그래, 맡겨 두라니까\n반드시 힘이 되어 보이",
    "6:3564:0": "감사한 말씀이옵니다\n무엇이든",
    "6:3565:0": "옛, 기대를 저버리지 않는 활약을\n보여 드리",
    "6:3566:0": "반드시 도움이 되는 모습을\n보여 드리",
    "6:3567:0": "옛, 어떤 일이든\n맡겨",
    "6:3568:0": "기대 이상의 활약을\n보여",
    "6:3569:0": "뜻을 받들겠습니다\n반드시 힘이 되",
}

STATIC_COORDINATES: set[str] = {
    "6:3558:0",
    "6:3560:0",
    "6:3561:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S212", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
