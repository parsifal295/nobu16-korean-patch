#!/usr/bin/env python3
"""Build Base authoring segment 622 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S622.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s622", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1550:0": "지금은 견뎌 내야 한다……",
    "9:1551:0": "끝까지 버텨\n보이리라……!",
    "9:1552:0": "해치워 버려!\n",
    "9:1552:1": "!",
    "9:1553:0": "!\n밀어붙여라! 조금만 더 힘내라!",
    "9:1554:0": "조금만 더 힘내라―",
    "9:1554:1": "\n저력을 보여라!",
    "9:1555:0": "\n조금만 더 버텨 주십시오",
    "9:1556:0": "!\n짓눌러 버려라!",
    "9:1557:0": "호오, 이건 되겠군……",
    "9:1558:0": "적이 무너지고 있군요……!",
    "9:1559:0": "!\n바로 지금이다, 밀어붙여라!",
    "9:1560:0": "!\n조금만 더 힘내십시오!",
    "9:1561:0": "조금만 더 힘내면 된다!",
    "9:1562:0": "좋습니다, 바로 그겁니다!",
    "9:1563:0": "!\n힘내 주시오!",
    "9:1564:0": "좋았어!\n해냈잖아!",
    "9:1565:0": "!\n훌륭한 투지였다!",
    "9:1566:0": "잘했다……\n훌륭한 활약이로다",
    "9:1567:0": "오오…… 훌륭하군요",
    "9:1568:0": "!\n끝까지 잘 밀어붙였다!",
    "9:1569:0": "……\n제법 하는구나……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1552:0",
    "9:1552:1",
    "9:1553:0",
    "9:1554:0",
    "9:1554:1",
    "9:1555:0",
    "9:1556:0",
    "9:1559:0",
    "9:1560:0",
    "9:1563:0",
    "9:1565:0",
    "9:1568:0",
    "9:1569:0",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S622", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
