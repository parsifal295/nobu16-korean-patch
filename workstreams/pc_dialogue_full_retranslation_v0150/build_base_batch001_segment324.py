#!/usr/bin/env python3
"""Build Base authoring segment 324 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S324.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s324", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:423:0": "이럴 수가, 고맙구나",
    "7:424:0": "이 은혜는 잊지 않겠다",
    "7:425:0": "을(를) 해방했습니다",
    "7:426:0": "을(를) 비롯해 총",
    "7:426:1": "명을 해방했습니다",
    "7:427:0": "어쩔 수 없군, 물러나겠다",
    "7:428:0": "이대로 끝나지는 않는다",
    "7:429:0": "이 무슨 꼴이란 말인가",
    "7:430:0": "여기까지로다!",
    "7:431:0": "도망쳐라……아니, 퇴각하라!",
    "7:432:0": "두고 보아라!",
    "7:433:0": "분하지만 여기까지로군",
    "7:434:0": "물러나다니 한심하구나",
    "7:435:0": "이번 패배를 밑거름으로 삼겠다",
    "7:436:0": "이 몸이 너무 서둘렀는가",
    "7:437:0": "패배에는 익숙하지 않구나",
    "7:438:0": "방심했구나",
    "7:439:0": "힘이 미치지 못했으니, 원통하구나",
    "7:440:0": "미안하다, 물러나겠다",
    "7:441:0": "이런 실책을!",
}

STATIC_COORDINATES: set[str] = {
    "7:423:0", "7:424:0", "7:427:0", "7:428:0", "7:429:0", "7:430:0", "7:431:0",
    "7:432:0", "7:433:0", "7:434:0", "7:435:0", "7:436:0", "7:437:0", "7:438:0",
    "7:439:0", "7:440:0", "7:441:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S324", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
