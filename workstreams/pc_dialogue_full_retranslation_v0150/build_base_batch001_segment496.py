#!/usr/bin/env python3
"""Build Base authoring segment 496 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S496.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s496", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "8:277:0": "올해는 참으로 통탄스럽게도\n우리 영내가 흉작에 시달리",
    "8:277:1": "\n병사들을 굶길 수는 없",
    "8:278:0": "올해는 흉작이 들",
    "8:278:1": "\n여차하면 거래로 쌀을 구하는 방안도\n고려해야 하",
    "8:279:0": "유감스럽게도 흉작을 맞았사",
    "8:279:1": "\n올해 연공미는 예년 수준에\n한참 못 미치",
    "8:280:0": "을(를) 비롯해 피해를 입은 군은 총",
    "8:280:1": "개로,\n병량 조달에 차질이 생기",
    "8:281:0": "을(를) 비롯해 피해를 입은 군은 총",
    "8:281:1": "개로,\n병량 조달에 차질이 생기",
    "8:282:0": "을(를) 비롯해 피해를 입은 군은 총",
    "8:282:1": "개로,\n병량 조달에 차질이 생기",
    "8:283:0": "을(를) 비롯해 피해를 입은 군은 총",
    "8:283:1": "개로,\n병량 조달에 차질이 생기",
    "8:284:0": "을(를) 비롯해 피해를 입은 군은 총",
    "8:284:1": "개로,\n병량 조달에 차질이 생기",
    "8:285:0": "영내에 가뭄이 발생하",
    "8:285:1": "\n미리 대책을 세워 둔",
    "8:285:2": "지역은\n화를 면한 듯하",
    "8:286:0": "가뭄이 닥치",
    "8:286:1": "\n대책을 마련한 영지는 화를 면하였사오",
    "8:286:2": "\n선견지명이란 바로 이런 것이",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S496", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
