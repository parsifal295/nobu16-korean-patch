#!/usr/bin/env python3
"""Build Base authoring segment 658 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S658.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s658", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2272:0": "이것은 적의 책략인가!?\n침착하세요!",
    "9:2273:0": "무, 뭐냐!?\n몸을 움직일 수가 없다!",
    "9:2274:0": "병사들이 이런 상태로는\n움직일 수 없습니다……",
    "9:2275:0": "진정하라,\n정신을 똑바로 차려라!",
    "9:2276:0": "(이)라고?\n이름뿐이잖아!",
    "9:2277:0": "따위\n겨우 이 정도다!",
    "9:2278:0": "…… 허무하게\n허공만 가른 모양이군",
    "9:2279:0": "훗―",
    "9:2279:1": "\n불발인가요?",
    "9:2280:0": "가소롭도다―",
    "9:2281:0": "후후―",
    "9:2281:1": "\n두려워할 만한 것이 못 된다",
    "9:2282:0": "도\n",
    "9:2282:1": "에게는 통하지 않는다",
    "9:2283:0": "글쎄―",
    "9:2283:1": "(이)란\n대체 무엇이었던가?",
    "9:2284:0": "……?\n아무 일도 일어나지 않습니다……",
    "9:2285:0": "(이)라고……?\n웃기는구나!",
    "9:2286:0": "판단이 너무 안일한 것 아니오\n",
    "9:2286:1": "?",
    "9:2287:0": "!\n",
    "9:2287:1": "을(를) 얕보았구나",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2276:0",
    "9:2277:0",
    "9:2278:0",
    "9:2279:0",
    "9:2279:1",
    "9:2280:0",
    "9:2281:0",
    "9:2281:1",
    "9:2282:0",
    "9:2282:1",
    "9:2283:0",
    "9:2283:1",
    "9:2284:0",
    "9:2285:0",
    "9:2286:0",
    "9:2286:1",
    "9:2287:0",
    "9:2287:1",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S658", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
