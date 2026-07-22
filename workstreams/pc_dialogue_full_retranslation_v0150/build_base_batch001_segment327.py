#!/usr/bin/env python3
"""Build Base authoring segment 327 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S327.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s327", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:482:0": "물러날 수밖에 없습니다",
    "7:483:0": "분하옵니다",
    "7:484:0": "여기까지인가, 물러나라!",
    "7:485:0": "물러나는 수밖에 없다",
    "7:486:0": "이 몸으로는 당해낼 수 없는가",
    "7:487:0": "이(가) 궤멸",
    "7:488:0": "이(가) 병량 고갈로 궤멸",
    "7:489:0": "이여, 내 앞을 막지 마라!",
    "7:490:0": "은(는) 참으로 무르구나",
    "7:491:0": "이여, 눈에 거슬리는구나\n사라져라",
    "7:492:0": "이(가) 물러났다!",
    "7:493:0": "을(를) 격퇴했노라!",
    "7:494:0": "은(는) 적수조차 되지 못했구나",
    "7:495:0": "은(는) 내가 분쇄해 주었노라",
    "7:496:0": "좋아,",
    "7:496:1": "을(를) 끝내 밀어붙였군",
    "7:497:0": "모두의 덕분에 「",
    "7:497:1": "」을(를) 격퇴했노라",
    "7:498:0": "은(는) 무너졌다\n이 몸을 상대한 탓이지",
    "7:499:0": "쯤은 손쉽게 짓뭉개 주었노라",
}

STATIC_COORDINATES: set[str] = {
    "7:482:0", "7:483:0", "7:484:0", "7:485:0", "7:486:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S327", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
