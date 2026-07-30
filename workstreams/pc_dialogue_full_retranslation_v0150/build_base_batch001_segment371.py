#!/usr/bin/env python3
"""Build Base authoring segment 371 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S371.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s371", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:1020:0": "따위는\n우리 군의 적수가 못 된다",
    "7:1021:0": "을(를) 격퇴하는 일이라면\n가볍게 끝나겠지",
    "7:1022:0": "\n반격할 틈도 주지 않고\n쳐부술 뿐이다",
    "7:1023:0": "을(를) 격퇴하는 일이라면\n무난하겠지",
    "7:1024:0": "에게\n모신의 전술을 보여 주마",
    "7:1025:0": "따위는\n가볍게 받아넘겨 주리라",
    "7:1026:0": "이(가) 상대인가\n두려워할 것 없군",
    "7:1027:0": "은(는) 병력이 적으니\n쉽게 격퇴할 수 있을 것입니다",
    "7:1028:0": "라면\n승산은 충분하고도 남습니다",
    "7:1029:0": "라면\n격퇴쯤은 식은 죽 먹기다!",
    "7:1030:0": "에게는 힘의 차이를\n뼈저리게 가르쳐 줘야겠군",
    "7:1031:0": "라면\n무용을 마음껏 발휘할 수 있겠지요",
    "7:1032:0": "따위는\n소수 병력이라 해도\n우리는 전력으로 상대하겠소",
    "7:1033:0": "이(가) 이번 상대인가\n그런 소수 병력으로 오다니, 대단한 배짱이로다",
    "7:1034:0": "와(과)의 싸움에서\n얻을 것도 적지 않을 것이오",
    "7:1035:0": "라면\n승산이 높을 것입니다",
    "7:1036:0": "은(는)\n그리 강한 군세가 아니옵니다",
    "7:1037:0": "따위에게\n뒤처질 수는 없다",
    "7:1038:0": "은(는) 내 호적수가\n될 수 있을까",
    "7:1039:0": "따위는\n지모로 맞서면 적수가 못 된다",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S371", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
