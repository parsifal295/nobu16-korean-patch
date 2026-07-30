#!/usr/bin/env python3
"""Build Base authoring segment 231 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S231.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s231", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3762:0": "우리 가문으로서는",
    "6:3762:1": "와(과)의 관계를\n오래도록 이어가고자 생각하",
    "6:3762:3": "찬동해 주시",
    "6:3762:4": "까?",
    "6:3763:0": "좋은 답변을 주시니 더없이 기쁘옵니다\n앞으로도 잘 부탁드리겠습니다",
    "6:3764:0": "…알겠",
    "6:3764:1": "\n그것이 귀 가문의 뜻이라면\n그대로 받아들이",
    "6:3765:0": "어떤 교섭을",
    "6:3766:0": "에게 원군을 보내 달라고 전하",
    "6:3767:0": "에게 정전 중재를 청하",
    "6:3768:0": "와(과)의 맹약은\n이제 무용지물",
    "6:3769:0": "을(를) 종속시킵시다",
    "6:3770:0": "지금은",
    "6:3770:1": "에게 신종하여\n때를 기다립시다",
    "6:3771:0": "와(과) 관계를 맺는 것",
    "6:3771:1": "\n좋은 방안",
    "6:3772:0": "에게 성 방위를 부탁하",
    "6:3773:0": "재미있군, 손잡아 주지\n단, 당분간뿐이다\n그다음 일은 그때의 내가 알아서 하겠지",
    "6:3774:0": "동맹 제의는 받아들였다\n당분간은 손을 잡도록 하지\n그 뒤 일은 그때 다시 이야기하자꾸나",
    "6:3775:0": "동맹 제의는 받아들이겠다\n당분간 우리는 맹우다\n그 뒤 일은 때가 되면 정하면 된다",
}

STATIC_COORDINATES: set[str] = {
    "6:3763:0",
    "6:3773:0",
    "6:3774:0",
    "6:3775:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S231", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
