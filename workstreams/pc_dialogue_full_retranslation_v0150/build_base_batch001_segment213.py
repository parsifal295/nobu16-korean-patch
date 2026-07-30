#!/usr/bin/env python3
"""Build Base authoring segment 213 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S213.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s213", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3570:0": "이 몸이 스러질 때까지 힘쓰",
    "6:3570:1": "\n맡겨 주시오",
    "6:3571:0": "예, 반드시 기대에\n부응하겠사옵니다",
    "6:3572:0": "옛, 어떤 일이든\n맡겨 주십시오",
    "6:3573:0": "물론입니다\n맡겨",
    "6:3574:0": "옛, 반드시\n도움이 되는 모습을 보여 드리",
    "6:3575:0": "뭐, 그러니까…\n잘 부탁하네",
    "6:3576:0": "굳건히",
    "6:3576:1": "을(를) 따르거라",
    "6:3577:0": "으로(로)서",
    "6:3577:1": "을(를) 보필할 준비는\n되어 있겠지",
    "6:3578:0": "부부로서 서로 굳게 의지하며\n살아가고 싶군",
    "6:3579:0": "오늘부터 부부다\n경사로다, 경사로다",
    "6:3580:0": "을(를) 위해",
    "6:3580:1": "으로(로)서 받들거라\n알겠느냐",
    "6:3581:0": "오늘부터 부부…\n잘 부탁드립니다",
    "6:3582:0": "설마",
    "6:3582:1": "의",
    "6:3582:2": "이(가) 될 줄은\n생각지도 못했겠지",
    "6:3583:0": "으로(로)서",
}

STATIC_COORDINATES: set[str] = {
    "6:3571:0",
    "6:3572:0",
    "6:3575:0",
    "6:3578:0",
    "6:3579:0",
    "6:3581:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S213", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
