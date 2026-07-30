#!/usr/bin/env python3
"""Build Base authoring segment 191 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S191.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s191", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3349:0": "을(를) 내쫓으면\n",
    "6:3349:1": "와(과)의 관계도\n끝장나 버린다고…!",
    "6:3350:0": "어찌하여 추방하시려는 것이오…\n",
    "6:3350:1": "와(과)의 혼인 동맹이\n어찌 되어도 좋단 말이오!",
    "6:3351:0": "이 추방이 뜻하는 바는\n",
    "6:3351:1": "와(과)의 혼인 동맹 파기다\n그래도 좋단 말인가…!",
    "6:3352:0": "있을 수 없습니다… 이래서는\n",
    "6:3352:1": "와(과)의 혼인 동맹이\n무너지고 맙니다…",
    "6:3353:0": "추방이라니…\n",
    "6:3353:1": "와(과)의 혼인 동맹을 깨뜨릴 셈인가…!",
    "6:3354:0": "와(과)의 혼인 동맹을 희생하면서까지\n내 재능을 두려워해 추방하려 했단 말인가…",
    "6:3355:0": "을(를) 추방하면\n",
    "6:3355:1": "와(과)의 혼인 동맹은\n없던 일이 될 터인데…",
    "6:3356:0": "이럴 수가,",
    "6:3356:1": "을(를) 추방한다고?\n",
    "6:3356:2": "와(과)의 혼인 동맹은\n필요 없다는 말인가…?",
    "6:3357:0": "을(를) 내쫓으면\n",
    "6:3357:1": "와(과)의 혼인 동맹이\n사라지고 맙니다만…",
    "6:3358:0": "혼인 동맹을 버리면서까지\n",
    "6:3358:1": "을(를) 추방하려는 것이로군…",
}

STATIC_COORDINATES: set[str] = set()


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S191", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
