#!/usr/bin/env python3
"""Build Base authoring segment 436 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S436.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s436", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2060:0": "을(를) 강공하라\n힘으로 짓눌러 버려라",
    "7:2061:0": "을(를) 공격하라\n모조리 쳐부숴라!",
    "7:2062:0": "을(를) 강공한다\n힘으로 밀어붙여라!",
    "7:2063:0": "을(를) 강공하라\n주춤하지 마라, 덤벼라",
    "7:2064:0": "을(를) 공격하라\n온 힘을 다해 덤벼라!",
    "7:2065:0": "을(를) 공격합니다\n단숨에 함락시킵시다",
    "7:2066:0": "을(를) 강공하라\n힘으로 짓눌러라!",
    "7:2067:0": "을(를) 공격한다\n속히 함락해 주마",
    "7:2068:0": "을(를) 강공하라\n강행하기로 하지",
    "7:2069:0": "을(를) 공격한다!\n무리해서라도 함락시켜라!",
    "7:2070:0": "을(를) 공격합니다\n힘으로 밀어붙입시다",
    "7:2071:0": "을(를) 강공한다\n힘으로 빼앗겠노라!",
    "7:2072:0": "을(를) 공격합니다\n모두 처단하십시오",
    "7:2073:0": "을(를) 강공하라\n힘으로 함락시켜라!",
    "7:2074:0": "의 병량은\n곧 바닥난다. 손대지 마라",
    "7:2075:0": "의 병량은\n얼마 없다. 여기서는 포위다",
    "7:2076:0": "의 병량이\n바닥날 때까지 기다리자",
    "7:2077:0": "의 병량은\n얼마 없다. 포위하도록 하지",
    "7:2078:0": "의 병량은\n얼마 없다. 그저 기다려라",
    "7:2079:0": "의 병량이\n바닥나기를 기다리면 된다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S436", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
