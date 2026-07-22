#!/usr/bin/env python3
"""Build Base authoring segment 322 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S322.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s322", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:383:1": "」을(를) 입수했습니다",
    "7:384:0": "처우를 결정하지 않은 모든 무장을 해방합니다\n계속하시겠습니까?",
    "7:385:0": "무르구나, 두고 보아라",
    "7:386:0": "살려 두어 무엇 하려는가",
    "7:387:0": "오오, 고맙소!",
    "7:388:0": "이 은혜, 결코 잊지 않겠사옵니다!",
    "7:389:0": "참으로 고맙도다",
    "7:390:0": "이 은혜는 평생 잊지 않겠다",
    "7:391:0": "살려 둔다니 무슨 속셈이냐",
    "7:392:0": "나중에 후회해도 늦을 것이다",
    "7:393:0": "고맙도다",
    "7:394:0": "다음에는 반드시 이기리라",
    "7:395:0": "정말 괜찮은가? 참으로 고맙군",
    "7:396:0": "귀공의 그릇을 내가 잘못 보았구나",
    "7:397:0": "참으로 고맙다!",
    "7:398:0": "이 은혜 잊지 않겠다!",
    "7:399:0": "살아서 돌아갈 수 있을 줄이야",
    "7:400:0": "이 큰 은혜는 언젠가 갚겠사옵니다",
    "7:401:0": "날 풀어 준다고!?",
    "7:402:0": "고맙다!",
}

STATIC_COORDINATES: set[str] = {
    "7:384:0", "7:385:0", "7:386:0", "7:387:0", "7:388:0", "7:389:0", "7:390:0", "7:391:0",
    "7:392:0", "7:393:0", "7:394:0", "7:395:0", "7:396:0", "7:397:0", "7:398:0", "7:399:0",
    "7:400:0", "7:401:0", "7:402:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S322", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
