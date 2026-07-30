#!/usr/bin/env python3
"""Build Base authoring segment 302 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S302.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s302", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4567:1": "을(를) 우리 가문에 맞아들일 절차를\n진행해 두지요",
    "6:4568:0": "그럼 「",
    "6:4568:1": "」의 빼내기는 포기하겠습니다\n",
    "6:4568:2": "의 힘이 미치지 못해 송구합니다",
    "6:4576:0": "이럴 수가, 「",
    "6:4576:1": "」께서 몸소\n찾아오시다니…",
    "6:4577:0": "한 번은 거절했을 터인데…\n이번에는 「",
    "6:4577:1": "」께서 몸소 찾아오시다니",
    "6:4585:0": ", 위험을 무릅쓰고\n성을 선물 삼아 귀순하려는 자에게는\n성의를 보여 줘야 하",
    "6:4586:0": "그대를 우리 가문에 맞아들이려면\n그에 걸맞은 예의가 필요하다고 여겼을 뿐…\n바라는 것이 있다면 말해 보라",
    "6:4589:0": ", 이 조건으로는 응할 수 없",
    "6:4589:1": "…",
    "6:4590:0": "조금 더 얹어 주길 바라는 참",
    "6:4590:1": "만…",
    "6:4591:0": "음, 이 조건이라면 받아들이겠다",
    "6:4592:0": "이 정도 조건이라면 기꺼이 받아들이겠다",
    "6:4593:0": "그것만은 도저히 양보할 수 없",
    "6:4594:0": "바람은 이루어 줄 수 없",
    "6:4594:1": "는가…",
}

STATIC_COORDINATES: set[str] = {"6:4586:0", "6:4591:0", "6:4592:0"}


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S302", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
