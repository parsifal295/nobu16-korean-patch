#!/usr/bin/env python3
"""Build Base authoring segment 430 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S430.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s430", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1983:0": ", 각오해라!\n",
    "7:1983:1": "은(는) 지킨다!",
    "7:1984:0": "에게\n",
    "7:1984:1": "을(를) 넘겨주지 않겠다",
    "7:1985:0": "을(를) 지키겠습니다\n목표—",
    "7:1986:0": "을(를) 지키기 위해\n",
    "7:1986:1": "을(를) 저지한다",
    "7:1987:0": "을(를) 공략하는 적군의 핵심—\n",
    "7:1987:1": "을(를) 친다",
    "7:1988:0": "을(를) 지킨다!\n",
    "7:1988:1": "을(를) 쳐라",
    "7:1989:0": "을(를) 쳐라\n",
    "7:1989:1": "을(를) 지켜야 한다",
    "7:1990:0": "을(를) 지키기 위해\n노릴 것은—",
    "7:1991:0": "을(를) 지킨다!\n",
    "7:1991:1": ", 각오해라!",
    "7:1992:0": "이(가) 위험하다……\n어서—",
    "7:1992:1": "을(를) 쳐라!",
    "7:1993:0": "은(는) 빼앗기지 않는다\n",
    "7:1993:1": "을(를) 요격한다",
    "7:1994:0": "은(는) 빼앗기지 않는다\n속히 적군을 섬멸하라!",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S430", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
