#!/usr/bin/env python3
"""Build Base authoring segment 660 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S660.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s660", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2308:0": "후방이 위험하다고?\n여기서는 물러날까요……",
    "9:2309:0": "으음…… 물러나는 편이\n낫다는 거로군……?",
    "9:2310:0": "거짓인지 참인지, 후방을\n확인하러 가야겠군……",
    "9:2311:0": "좋아, 퇴각로를 지켜\n공을 세우겠다!",
    "9:2312:0": "(이)란\n결국 허풍이잖아?",
    "9:2313:0": "우리에게―",
    "9:2313:1": "이(가)\n통할 거라 생각하지 마라",
    "9:2314:0": "……\n거짓임을 갈파했도다!",
    "9:2315:0": "을(를) 쓰려거든\n",
    "9:2315:1": "이(가) 아닌 다른 상대를 골라라",
    "9:2316:0": "이것이―",
    "9:2316:1": "인가\n참으로 시시하군",
    "9:2317:0": "여기서―",
    "9:2317:1": "(이)라니\n어리석기 짝이 없는 계책이군",
    "9:2318:0": "에게―",
    "9:2318:1": "따위\n통할 리가 없다",
    "9:2319:0": "가소롭구나!　",
    "9:2319:1": "(으)로\n물러설 줄 알았느냐!",
    "9:2320:0": "이것이―",
    "9:2320:1": "인가……\n가공할 책략이군…… 위험할 뻔했다",
    "9:2321:0": "그것으로―",
    "9:2321:1": "이(가) 물러날 거라고?\n얕보지 마라―",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2312:0",
    "9:2313:0",
    "9:2313:1",
    "9:2314:0",
    "9:2315:0",
    "9:2315:1",
    "9:2316:0",
    "9:2316:1",
    "9:2317:0",
    "9:2317:1",
    "9:2318:0",
    "9:2318:1",
    "9:2319:0",
    "9:2319:1",
    "9:2320:0",
    "9:2320:1",
    "9:2321:0",
    "9:2321:1",
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
    print(ENGINE.json.dumps({"status":"ok", "segment":"base_msggame_B001_S660", "decision_count":len(rows),
                             "retranslated":len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending":len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed":False, "output":str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
