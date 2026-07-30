#!/usr/bin/env python3
"""Build Base authoring segment 568 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S568.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s568", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:410:0": "에\n낙석이 명중",
    "9:411:0": "을(를) 포함한 총",
    "9:411:1": "개 부대에\n낙석이 명중",
    "9:412:0": "이(가)\n격려를 받아 전의 상승",
    "9:413:0": "을(를) 포함한 총",
    "9:413:1": "개 부대가\n격려를 받아 전의 상승",
    "9:414:0": "쓰러진 나무로 인해\n진로 봉쇄",
    "9:415:0": "쓰러진 나무 제거\n진로 통행 가능",
    "9:416:0": "다리를 불태웠습니다\n진로 차단",
    "9:417:0": "이(가)\n비탈을 내리달리며 공격",
    "9:418:0": "을(를) 포함한 총",
    "9:418:1": "개 부대가\n비탈을 내리달리며 공격",
    "9:419:0": "이(가)\n위병계에 걸려 후퇴",
    "9:420:0": "을(를) 포함한 총",
    "9:420:1": "개 부대가\n위병계에 걸려 후퇴",
    "9:421:0": "을(를)\n저지",
    "9:422:0": "을(를) 포함한 총",
    "9:422:1": "개 부대를\n저지",
    "9:423:0": "이(가)\n토착 무사 참전으로 병력 회복",
    "9:424:0": "을(를) 포함한 총",
    "9:424:1": "개 부대가\n토착 무사 참전으로 병력 회복",
}

STATIC_COORDINATES: set[str] = {
    "9:414:0",
    "9:415:0",
    "9:416:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S568", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
