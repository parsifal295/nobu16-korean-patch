#!/usr/bin/env python3
"""Build Base authoring segment 304 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S304.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s304", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:4616:0": "밤의 고요함이 이토록 섬뜩할 줄이야…",
    "6:4617:0": "혹시 무언가의 신호를 기다리고 있는 건가…?",
    "6:4618:0": "………? 설마 자고 있는 건 아니겠지?",
    "6:4619:0": "그렇습니까… 어쩔 수 없군요",
    "6:4620:0": "분하지만, 단념하도록 하겠습니다",
    "6:4624:0": "이 기회를 놓친 것은\n큰 손실일지도 모릅니다…?",
    "6:4625:0": "무리라면 어쩔 수 없지요…\n우리는 서로 뜻을 함께할 수 없다는 것입니다",
    "6:4626:0": "정말 괜찮겠느냐?\n멸망의 길을 걷게 되어도 나는 모른다",
    "6:4627:0": "그런가…\n그렇다면 어쩔 수 없지",
    "6:4638:0": ",",
    "6:4638:1": "\n그럼 일단 성으로 돌아갔다가\n곧 예물을 가지고 찾아뵙겠습니다",
    "6:4639:0": "제 바람을 들어 주셔서,",
    "6:4639:1": "\n그럼 지금 성으로 돌아가\n곧 예물을 가지고 찾아뵙겠습니다",
    "6:4640:0": "이토록 많이 내어 주시다니,",
    "6:4640:1": "\n이 조건이라면 기꺼이 섬기겠습니다",
    "6:4641:0": "제 바람을 들어 주셔서,",
    "6:4641:1": "\n이 조건이라면 기꺼이 섬기겠습니다",
    "6:4646:0": "의 요구를 거절하면\n즉시 출분합니다\n계속하시겠습니까?",
    "6:4647:0": "의 등용을 포기합니다\n계속하시겠습니까?",
    "6:4648:0": "의 등용을 포기하게 됩니다\n처단하거나 해방할 수밖에 없습니다\n계속하시겠습니까?",
}

STATIC_COORDINATES: set[str] = {
    "6:4616:0", "6:4617:0", "6:4618:0", "6:4619:0", "6:4620:0",
    "6:4624:0", "6:4625:0", "6:4626:0", "6:4627:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S304", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
