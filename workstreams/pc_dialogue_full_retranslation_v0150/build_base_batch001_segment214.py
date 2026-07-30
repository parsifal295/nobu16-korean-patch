#!/usr/bin/env python3
"""Build Base authoring segment 214 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S214.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s214", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3583:1": "을(를)\n보필하",
    "6:3584:0": "부부로서 서로 의지하며 살아갑시다",
    "6:3585:0": "오늘부터 부부로군요\n잘 부탁드리겠습니다",
    "6:3586:0": "오늘부터",
    "6:3586:1": "으로(로)서",
    "6:3586:2": "을(를)\n보필하",
    "6:3587:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3588:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3589:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3590:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3591:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3592:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3593:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3594:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3595:0": "미력하나마\n힘이 되고자 하옵니다",
    "6:3596:0": "예, 반드시\n힘이 되고자 하옵니다",
    "6:3597:0": "의 힘이 조금이나마 도움이 된다면\n기쁘겠사옵니다",
    "6:3598:0": "예, 미력하나마\n힘이 되고자 하옵니다",
    "6:3599:0": "뭐랄까…",
    "6:3599:1": "보다 먼저 죽게 두진 않겠어",
}

STATIC_COORDINATES: set[str] = {
    "6:3584:0",
    "6:3585:0",
    "6:3587:0",
    "6:3588:0",
    "6:3589:0",
    "6:3590:0",
    "6:3591:0",
    "6:3592:0",
    "6:3593:0",
    "6:3594:0",
    "6:3595:0",
    "6:3596:0",
    "6:3598:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S214", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
