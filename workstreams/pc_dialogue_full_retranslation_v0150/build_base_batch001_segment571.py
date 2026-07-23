#!/usr/bin/env python3
"""Build Base authoring segment 571 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S571.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s571", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:461:0": "혼쭐을\n내줍시다!",
    "9:462:0": "벌써부터 팔이 근질거리는군!",
    "9:463:0": "의 힘을\n똑똑히 깨닫게 해 줍시다",
    "9:464:0": "우리의 힘을\n똑똑히 보여 주자!",
    "9:465:0": "이(가) 있는 건가\n피가 끓어오르는군!",
    "9:466:0": "을(를) 쓰러뜨려\n내 무예를 빛내리라!",
    "9:467:0": "나의 호적수여\n함께 무예를 겨루자",
    "9:468:0": "이(가) 있다니\n뜻밖이네요……",
    "9:469:0": "호오……",
    "9:469:1": "와(과)\n싸울 수 있다니",
    "9:470:0": "……전장에서\n만나다니 행운인가 불행인가",
    "9:471:0": "의 앞에서\n추태를 보일 수는 없지요",
    "9:472:0": "싸울 날이 왔는가……\n이보게,",
    "9:472:1": "……",
    "9:473:0": "이(가) 이 전장에\n있다니!",
    "9:474:0": "잘 왔군!\n무예를 겨루지 않겠나",
    "9:475:0": "그렇군요……",
    "9:475:1": "이(가)\n있는 것이군요……",
    "9:476:0": "뭐라고!\n",
    "9:476:1": "이(가) 있을 줄이야",
}

STATIC_COORDINATES: set[str] = {
    "9:461:0",
    "9:462:0",
    "9:464:0",
    "9:467:0",
    "9:474:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S571", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
