#!/usr/bin/env python3
"""Build Base authoring segment 156 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S156.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s156", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:2847:0": "어쩔 수 없군…\n", "6:2847:1": "와(과)의 맹약은 끊도록 하겠소",
    "6:2848:0": "좋아, 알았다\n우리는,", "6:2848:1": "을(를) 공격하겠다",
    "6:2849:0": "음, 알겠다\n우리는,", "6:2849:1": "을(를) 공략하러 나서자",
    "6:2850:0": "음, 확실히 알겠소\n우리는,", "6:2850:1": "을(를) 공격하도록 하지",
    "6:2851:0": "알겠습니다\n", "6:2851:1": "을(를) 공격합시다",
    "6:2852:0": "잘 알겠소\n", "6:2852:1": "을(를) 공격하자꾸나",
    "6:2853:0": "흠, 알았다\n", "6:2853:1": "을(를) 공격해 드리지",
    "6:2854:0": "흠, 그런 것인가\n그렇다면,", "6:2854:1": "을(를) 공격하기로 하지",
    "6:2855:0": "맡겨 두거라\n", "6:2855:1": "을(를) 쳐서 멸해 주마",
    "6:2856:0": "알겠습니다\n우리는,", "6:2856:1": "을(를) 공격하겠습니다",
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
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S156", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
