#!/usr/bin/env python3
"""Build Base authoring segment 193 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S193.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s193", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3372:0": "슬프군요…\n이래 봬도 한 군단을 이끄는 몸인데…",
    "6:3373:0": "군단을 이끄는",
    "6:3373:1": "을(를)\n쓸모없다고 하는 것인가…",
    "6:3374:0": "필요 없다면\n내 발로 나가 주마!",
    "6:3375:0": "필요 없다면\n더는 충절을 다할 의리도 없지…",
    "6:3376:0": "내가 필요 없다는 것인가\n어리석은 당주에게 미련 따위 없다",
    "6:3377:0": "저를 필요로 하지 않으신다면\n미련은 없습니다…",
    "6:3378:0": "내가 필요 없다면\n미련 따위 없다…",
    "6:3379:0": "내가 필요 없다면\n내 재능을 펼칠 가문을 찾으면 그만이다",
    "6:3380:0": "흠…\n상성이 맞지 않았던 게지…",
    "6:3381:0": "을(를) 추방하다니\n아무것도 모르는군…",
    "6:3382:0": "을(를) 필요로 하는 이가 있는 곳으로\n가려고 합니다…",
    "6:3383:0": "미련 따위 없다\n잘 있거라…",
    "6:3384:0": "그동안 신세 많이 졌습니다\n그럼 이만…",
    "6:3385:0": "나를 필요로 하지 않는다면\n미련은 없다…",
    "6:3386:0": "나, 납득할 수",
    "6:3386:1": "!\n어찌하여",
    "6:3386:2": "이(가)…",
    "6:3387:0": "어, 어찌 이런…\n섬길 주인을 잘못",
    "6:3387:1": "인가",
}

STATIC_COORDINATES = {
    "6:3372:0", "6:3374:0", "6:3375:0", "6:3376:0", "6:3377:0", "6:3378:0",
    "6:3379:0", "6:3380:0", "6:3383:0", "6:3384:0", "6:3385:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S193", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
