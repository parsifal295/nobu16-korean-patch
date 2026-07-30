#!/usr/bin/env python3
"""Build Base authoring segment 613 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S613.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s613", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1359:0": "비탈 돌격이라니……?\n적이 한 수 위였구나",
    "9:1360:0": "물러나라!\n적이 도사리고 있다!",
    "9:1361:0": "적의 복병이다!\n물러나라!",
    "9:1362:0": "절묘한 곳에\n병사를 숨겨 두었구나……",
    "9:1363:0": "복병이 있군요……\n물러납시다",
    "9:1364:0": "복병인가!?\n물러나라!",
    "9:1365:0": "복병이 있음을 알고도\n나아갈 바보는 없다",
    "9:1366:0": "물러나라…… 하마터면\n복병에 걸릴 뻔했다",
    "9:1367:0": "에잇, 물러나라!",
    "9:1368:0": "적병!?\n여기서는 물러설 수밖에……",
    "9:1369:0": "불리하다…… 물러난다!",
    "9:1370:0": "이곳에 병사를\n숨겨 두다니……",
    "9:1371:0": "어쩔 수 없다…… 물러난다!",
    "9:1372:0": "감히 발목을\n붙잡다니!",
    "9:1373:0": "뜻대로\n진군할 수 없군……!",
    "9:1374:0": "적의 술수에\n빠지다니……!",
    "9:1375:0": "어떻게든\n움직여야……",
    "9:1376:0": "이래서는\n거의 나아갈 수 없구나……",
    "9:1377:0": "저지당하다니\n한심하군……",
    "9:1378:0": "꼼짝도 할 수 없사옵니다……",
    "9:1379:0": "괘씸한 것……\n발목을 붙잡는 수작이로다",
    "9:1380:0": "발이 묶였다고!?\n움직일 수 없군요……",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
                     "semantic_review": "approved",
                     "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current",
                     "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S613", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
