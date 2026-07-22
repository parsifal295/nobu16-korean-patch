#!/usr/bin/env python3
"""Build Base authoring segment 192 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S192.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s192", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3359:0": "아아…\n이것으로",
    "6:3359:1": "와(과)의 혼인 동맹마저\n사라지고 마는구나…",
    "6:3360:0": "을(를) 추방하면\n",
    "6:3360:1": "와(과)의 혼인 동맹이\n파기되고 말 텐데도…",
    "6:3361:0": "어리석구나…\n",
    "6:3361:1": "와(과)의 혼인 동맹을 버리면서까지\n",
    "6:3361:2": "을(를) 추방하다니…!",
    "6:3362:0": "군단장인",
    "6:3362:1": "이(가) 쓸모없다고…?\n제멋대로 지껄여 대기는!",
    "6:3363:0": "한 군단을 이끈 내 무략이\n설마 쓸모없다며 일축당할 줄이야…",
    "6:3364:0": "군단을 이끌면서도 쓸모없다니…\n내가 생각해도 실로 한심하군",
    "6:3365:0": "군단을 이끄는 이 몸마저\n쓸모없다는 말씀이십니까…!",
    "6:3366:0": "이래 봬도 군단을 이끄는 몸이다\n그런 내가 쓸모없다고…?",
    "6:3367:0": "내 군단은 내 재능 없이는 유지되지 못한다\n나를 추방한 일을 후회하게 될 것이다",
    "6:3368:0": "설마 군단장인",
    "6:3368:1": "이(가)\n쫓겨날 줄이야…",
    "6:3369:0": "이래 봬도 군단장이거늘…\n참으로 한탄스럽구나…",
    "6:3370:0": "군단장인",
    "6:3370:1": "을(를) 추방하다니\n몹시 미움받고 있었나 보군요…",
    "6:3371:0": "군단장인 나를 추방한다고…?\n말도 안 된다, 무언가 잘못된 게 틀림없다!",
}

STATIC_COORDINATES: set[str] = {
    "6:3363:0",
    "6:3364:0",
    "6:3365:0",
    "6:3366:0",
    "6:3367:0",
    "6:3369:0",
    "6:3371:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S192", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
