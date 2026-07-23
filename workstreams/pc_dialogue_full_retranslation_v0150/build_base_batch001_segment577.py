#!/usr/bin/env python3
"""Build Base authoring segment 577 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S577.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s577", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:583:0": "이렇게 밀리고 말다니……\n어서 전열을 재정비해야 해!",
    "9:584:0": "무엇을 하고 있느냐!?\n적을 밀어내라!",
    "9:585:0": "밀리고 있다……\n즉시 전열을 재정비하라",
    "9:586:0": "큰일이다……\n어서 밀어내야 한다!",
    "9:587:0": "더는 못 버티겠어……\n어서 교대해 줘!",
    "9:588:0": "전의가……\n서둘러 교대해야 한다……!",
    "9:589:0": "더는 전의를 유지할 수 없다……\n교대할 자는 없는가!",
    "9:590:0": "전의가…… 이대로라면\n패주하고 말 것입니다",
    "9:591:0": "원군을 서둘러 보내라!\n병사들이 한계에 달했다!",
    "9:592:0": "원호를…… 그렇지 않으면\n전의가 무너진다",
    "9:593:0": "병사들의 마음이 꺾이겠다……\n맡은 자리를 교대해 다오!",
    "9:594:0": "맡은 자리를 교대해 다오\n병사들이 버티지 못한다!",
    "9:595:0": "전의가…… 빨리\n교대해 주지 않으면……",
    "9:596:0": "더는 전의를 유지할 수 없다……\n이대로라면 궤멸이다",
    "9:597:0": "모두의 마음이 꺾이겠어요……\n여기까지……인 걸까요",
    "9:598:0": "전의가……\n어서 교대해 주시오",
    "9:599:0": "이대로라면 모두\n당하고 말겠어……",
    "9:600:0": "서둘러 교대해 주시오\n아군의 병력이……",
    "9:601:0": "병사를 너무 많이 잃었다……\n교대하지 않으면 전멸인가……",
    "9:602:0": "전멸만은\n피하고 싶습니다만……",
    "9:603:0": "병사들이 속절없이……!\n크윽……! 부탁한다……!",
    "9:604:0": "병력이 너무 많이 줄었군……\n교대가 제때 이뤄질까……?",
}

STATIC_COORDINATES: set[str] = set(TRANSLATIONS)


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S577", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
