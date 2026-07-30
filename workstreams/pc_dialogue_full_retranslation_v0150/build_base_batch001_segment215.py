#!/usr/bin/env python3
"""Build Base authoring segment 215 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S215.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s215", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3600:0": "옛, 이 목숨이 있는 한!",
    "6:3601:0": "음, 이 목숨을 바쳐서라도\n지켜 드리",
    "6:3602:0": "무슨 일이 있더라도\n끝까지 곁을 지키겠습니다",
    "6:3603:0": "음, 목숨이 다하는 날까지\n싸워 나갈 뿐이다!",
    "6:3604:0": "이 재주를 마음껏 발휘하여\n보여 드리겠습니다",
    "6:3605:0": "좋은 반려가 되어 보이겠습니다",
    "6:3606:0": "조금이나마 도움이 될 수 있다면\n기쁘기 그지없구나",
    "6:3607:0": ", 이 목숨이 있는 한\n힘을 다할 각오",
    "6:3608:0": ", 이 목숨이 있는 한\n힘을 다할 각오",
    "6:3609:0": ", 이 목숨이 있는 한\n힘을 다할 각오",
    "6:3610:0": ", 이 목숨이 있는 한\n힘을 다할 각오",
    "6:3611:0": "의 가보를\n몰수하게 됩니다만\n괜찮으시겠습니까?",
    "6:3612:0": "입력한 내용이 폐기됩니다\n괜찮으시겠습니까?",
    "6:3613:0": "이(가) 지닌 관직은\n조정에 반납됩니다만\n괜찮으시겠습니까?",
    "6:3614:0": "을(를) 줄 테니\n",
    "6:3614:1": "을(를) 돌려달라니…\n마음대로 하",
    "6:3615:0": "이(가)\n",
    "6:3615:1": "이(가) 지닌",
    "6:3615:2": "보다\n적어도 낫거나 못지않은 물건이라면…",
    "6:3616:0": "마음에는 감사하",
}

STATIC_COORDINATES: set[str] = {
    "6:3600:0",
    "6:3602:0",
    "6:3603:0",
    "6:3604:0",
    "6:3605:0",
    "6:3606:0",
    "6:3612:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S215", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
