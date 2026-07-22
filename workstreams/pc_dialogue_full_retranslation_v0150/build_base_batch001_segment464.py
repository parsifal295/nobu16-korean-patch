#!/usr/bin/env python3
"""Build Base authoring segment 464 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S464.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s464", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2534:0": "이번 일번창은",
    "7:2534:1": "이로다\n자, 비사문천의 깃발을 내걸고\n천하에 의를 보이리라",
    "7:2535:0": "평소에는 전선에 나서지 않는다만\n이번에는 이상하게 피가 끓는구나\n용서하라,",
    "7:2535:1": "도 무사인 까닭이다",
    "7:2536:0": "이번 일번창은 이 몸이다!\n독안룡이 날뛰는 모습을\n똑똑히 그 눈에 새겼느냐!",
    "7:2537:0": "일번창,",
    "7:2537:1": "이(가) 해냈다\n전쟁 없는 태평성대를 이루고자\n지금만은 수라가 되리라",
    "7:2538:0": "이번 일번창은 이 몸이다!\n선봉은 우리 같은 거친 놈들에게 맡겨라\n공을 잔뜩 세워 줄 테니 말이야!",
    "7:2539:0": "일번창,",
    "7:2539:1": "이(가) 해냈다\n충의를 위해 죽음도 마다하지 않는\n무사의 혼을 보시옵소서!",
    "7:2540:0": "이번 일번창은",
    "7:2540:1": "이옵니다\n",
    "7:2540:2": "도 무사의 자식. 마음만 먹으면\n일만 대군도 물리쳐 보이겠소",
    "7:2541:0": "일번창,",
    "7:2541:1": "이(가) 해냈습니다\n제 계책이 통한 덕에\n적의 기세를 꺾은 듯하군요",
    "7:2542:0": "이번 일번창은",
    "7:2542:1": "다!\n모두,",
    "7:2542:2": "을(를) 본보기로 삼아라\n그러면 범과 같은 군대가 되리라",
    "7:2543:0": "지모와 무용만으로 싸움은 움직이지 않는다\n때로는 선두에 서서\n사지로 뛰어들 각오도 필요한 법이다",
    "7:2544:0": "이(가) 수훈자인 모양이군\n일번창을 차지한 보람이 있었군\n좋은 싸움이었다!",
}

STATIC_COORDINATES: set[str] = {
    "7:2536:0", "7:2538:0", "7:2543:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S464", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
