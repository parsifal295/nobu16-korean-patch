#!/usr/bin/env python3
"""Build Base authoring segment 656 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S656.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s656", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2236:0": "호되게 당했군요……",
    "9:2237:0": "적도 제법 하는군……",
    "9:2238:0": "어찌……\n이리도 참혹한 짓을……",
    "9:2239:0": "크으윽!\n이 무슨……!",
    "9:2240:0": "이 정도쯤은\n아무렇지도 않다고!",
    "9:2241:0": "이 정도인가……\n네 무예의 한계가 보이는군",
    "9:2242:0": "이것을 오의라 부르는가……?",
    "9:2243:0": "설마\n힘을 다하지 않으신 겁니까?",
    "9:2244:0": "안 통한다, 안 통해\n이 몸에게는 통하지 않느니라!",
    "9:2245:0": "후후후\n시시한 수를……",
    "9:2246:0": "이까짓 기술은\n",
    "9:2246:1": "에게는 통하지 않는다!",
    "9:2247:0": "어머, 가소롭구나!\n한심한 공격이로다!",
    "9:2248:0": "이 정도라면\n문제없습니다!",
    "9:2249:0": "별것 아니다",
    "9:2250:0": "겨우 그 정도입니까?",
    "9:2251:0": "하하하\n김이 빠졌구나!",
    "9:2252:0": "당했다!\n",
    "9:2252:1": "…… 이놈!",
    "9:2253:0": "손쓸 도리가 없다……\n두렵도다―",
    "9:2254:0": "에게\n휘둘리고 있구나",
    "9:2255:0": "이대로는\n",
    "9:2255:1": "의 손아귀에서 놀아날 뿐이다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2246:0",
    "9:2246:1",
    "9:2252:0",
    "9:2252:1",
    "9:2253:0",
    "9:2254:0",
    "9:2255:0",
    "9:2255:1",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S656", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
