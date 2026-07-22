#!/usr/bin/env python3
"""Build Base authoring segment 435 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S435.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s435", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2045:0": "적은 이제 됐다\n",
    "7:2045:1": "을(를) 수비해야 한다",
    "7:2046:0": "음…… 너무 깊이 추격했구나\n",
    "7:2046:1": "을(를) 방어하러 돌아간다",
    "7:2047:0": "서둘러—",
    "7:2047:1": "(으)로 돌아가라\n……설마 유인당한 것인가?",
    "7:2048:0": "이런—",
    "7:2048:1": "에\n돌아가야겠군",
    "7:2049:0": "에서\n떨어져서는 안 되겠군",
    "7:2050:0": "이(가) 걱정입니다\n서둘러 돌아가야겠습니다……",
    "7:2051:0": "그만 흥분했나……\n",
    "7:2051:1": "(으)로 돌아가야겠군",
    "7:2052:0": "어머—",
    "7:2052:1": "에\n돌아가야겠어요",
    "7:2053:0": "이(가) 걱정이다\n수비하러 가자",
    "7:2054:0": "을(를) 강공하라\n모조리 쳐라!",
    "7:2055:0": "을(를) 공격하라!\n힘으로 함락시켜라!",
    "7:2056:0": "을(를) 강공하겠다\n신속히 탈취하라!",
    "7:2057:0": "을(를) 공격하라\n정면에서 당당히 쳐라!",
    "7:2058:0": "을(를) 차지하리라\n사력을 다하라",
    "7:2059:0": "을(를) 공격하라\n잔재주는 필요 없다!",
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
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S435", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
