#!/usr/bin/env python3
"""Build Base authoring segment 438 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S438.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s438", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2100:0": "의 위기다!\n서둘러 본거지를 함락시켜라",
    "7:2101:0": "이(가) 위험한가\n어서 이 성을 함락시켜야겠군",
    "7:2102:0": "이(가) 위험하다!\n얼른 이 성을 함락한다!",
    "7:2103:0": "의 위기다!\n어서 끝내라!",
    "7:2104:0": "이(가) 위험하다!\n재빨리 이 성을 함락시켜라!",
    "7:2105:0": "이(가) 위태롭습니다……\n속히 이 성을 함락시키겠습니다",
    "7:2106:0": "이(가) 위험하다!\n서둘러 끝내자꾸나!",
    "7:2107:0": "이(가) 위태롭다\n시급히 이 성을 함락시켜야겠군",
    "7:2108:0": "이(가) 위험한가\n속히 이 성을 함락시켜야겠군",
    "7:2109:0": "이(가)?\n당장 이 성을 함락시켜야겠군!",
    "7:2110:0": "이(가) 큰일이야……\n어서 이 성을 함락해야 해!",
    "7:2111:0": "이(가) 위험하다!\n당장 끝낸다!",
    "7:2112:0": "이(가) 위험합니다……\n당장 이 성을 함락시킵시다",
    "7:2113:0": "이(가) 위험하다!\n어서 끝내야 한다!",
    "7:2114:0": "병량이 부족하다고?\n즉시 성을 함락시켜라",
    "7:2115:0": "병량이 얼마 남지 않았다……\n어서 끝내야 한다!",
    "7:2116:0": "남은 병량이 불안하다\n시급히 성을 함락시켜야겠군",
    "7:2117:0": "병량이 걱정되는구나\n성 함락을 서두르게 하자",
    "7:2118:0": "병량이 불안하다\n즉시 성을 함락시켜라",
    "7:2119:0": "병량이 넉넉하지 않다\n힘으로 밀어붙일까",
}

STATIC_COORDINATES: set[str] = {
    "7:2114:0", "7:2115:0", "7:2116:0", "7:2117:0", "7:2118:0", "7:2119:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S438", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
