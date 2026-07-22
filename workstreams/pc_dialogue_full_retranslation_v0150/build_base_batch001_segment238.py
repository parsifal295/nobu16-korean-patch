#!/usr/bin/env python3
"""Build Base authoring segment 238 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S238.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s238", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3847:0": "와(과)의 정전을",
    "6:3847:1": "개월 연장",
    "6:3848:0": "그러면 3개월간의 정전이 끝난 뒤\n",
    "6:3848:1": "와(과)는 적이 되",
    "6:3848:2": "\n부디 각별히 조심하십시오…",
    "6:3849:0": "의 영내에 부대가 남아 있어\n정전이 연장되",
    "6:3849:1": "지만\n주변 세력의 불신을 사",
    "6:3849:2": "…",
    "6:3850:0": "다음은",
    "6:3850:1": "의 관직",
    "6:3850:2": "\n우리 가문의 위신이 부족하여\n천거해 주실 것 같지 않",
    "6:3851:0": "다음은",
    "6:3851:1": "의 관직에\n천거받을 수 있도록 힘쓰",
    "6:3852:0": "다음은",
    "6:3852:1": "의 관직",
    "6:3852:2": "우리 가문의 위신은 격식에 다소 못 미치므로\n금전이 상당히 들 듯하",
    "6:3853:0": "중개자 무장이 부재 중이므로\n조정의 신용이 오르지 않습니다",
    "6:3854:0": "조정의 신용은 충분히 얻었으나\n관직에 빈자리가 없다고 하니…\n헌금을 중단하고 기다릴 수밖에 없",
    "6:3855:0": "그대가 품은 근왕의 뜻은 잘 알았느니라\n천황의 명이니,",
    "6:3855:1": "을(를) 내리겠노라",
}

STATIC_COORDINATES: set[str] = {
    "6:3853:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S238", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
