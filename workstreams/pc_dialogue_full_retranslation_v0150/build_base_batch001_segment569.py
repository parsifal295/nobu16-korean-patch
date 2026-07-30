#!/usr/bin/env python3
"""Build Base authoring segment 569 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S569.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s569", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:425:0": "돌발 홍수로 유역의\n",
    "9:425:1": "개 부대가 휩쓸렸습니다",
    "9:426:0": "적군이\n요충지 발동에 실패",
    "9:427:0": "에\n낙석이 명중",
    "9:428:0": "을(를) 포함한 총",
    "9:428:1": "개 부대에\n낙석이 명중",
    "9:429:0": "적군,",
    "9:429:1": "\n격려를 받아 전의 상승",
    "9:430:0": "적군,",
    "9:430:1": "을(를) 포함한 총",
    "9:430:2": "개 부대가\n격려를 받아 전의 상승",
    "9:431:0": "적군, 쓰러진 나무로 인해\n진로 봉쇄",
    "9:432:0": "적군, 쓰러진 나무 제거\n진로 통행 가능",
    "9:433:0": "적군이 다리를 불태운 듯합니다\n진로 차단",
    "9:434:0": "이(가)\n비탈을 내리달리며 진군",
    "9:435:0": "을(를) 포함한 총",
    "9:435:1": "개 부대가\n비탈을 내리달리며 진군",
    "9:436:0": "\n적군의 위병계에 걸려 후퇴",
    "9:437:0": "을(를) 포함한 총",
    "9:437:1": "개 부대가\n적군의 위병계에 걸려 후퇴",
    "9:438:0": "이(가)\n저지당함",
    "9:439:0": "을(를) 포함한 총",
    "9:439:1": "개 부대가\n저지당함",
}

STATIC_COORDINATES: set[str] = {
    "9:426:0",
    "9:431:0",
    "9:432:0",
    "9:433:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S569", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
