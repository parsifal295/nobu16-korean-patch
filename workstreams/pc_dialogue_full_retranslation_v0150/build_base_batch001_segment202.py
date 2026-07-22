#!/usr/bin/env python3
"""Build Base authoring segment 202 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S202.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s202", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3469:1": "이(가) 일등이라니…!\n아아, 이 벅차오르는 행복감!\n참으로 오랜만에 가슴이 뜨거워졌소이다",
    "6:3470:0": "이(가) 되었으니\n이 정도는 해내야지\n다른 녀석들한테 얕보이지 않겠어?",
    "6:3471:0": "쯤 되었으니\n과연",
    "6:3471:1": ", 비할 데 없다고…\n먼 나라에까지 이름을 떨칠 활약을 해야겠군",
    "6:3472:0": "훈공의 선두에 서게 되다니\n더없는 영광으로 여기오\n앞으로도 우리 가문을 더욱 융성케 하겠소이다",
    "6:3473:0": "의",
    "6:3473:1": "이(가) 일등이옵니까\n더없이 감사한 일…이옵니다만\n아랫사람들도 더욱 분발해 주었으면 합니다",
    "6:3474:0": "훈공 1위는,",
    "6:3474:1": "의 지위가 세운 공일 뿐이지\n아무래도 지위라는 갑옷에 갇혀 버렸군…\n창 한 자루로 자유로이 전장을 누비던 때가 그립다",
    "6:3475:0": "무슨 일이든",
    "6:3475:1": "을(를) 위하고\n",
    "6:3475:2": "을(를) 보필하는 것이",
    "6:3475:3": "의 소임\n훈공 1위 따위는 그에 따라온 것일 뿐이옵니다",
    "6:3476:0": "더없이 감사할 따름이옵니다\n",
    "6:3476:1": "의 지위에 있으면서도 훈공 1위조차 차지하지 못한다면\n그 지위를 훔친 것이나 다름없사옵니다",
    "6:3477:0": "라 하오나\n",
    "6:3477:1": "은(는) 아직 한창 젊으니 말이오\n훈공 1위는 다른 자에게 넘길 수 없소이다!",
    "6:3478:0": "좋아!　",
    "6:3478:1": "의 체면은 세웠군요\n…",
    "6:3478:2": "라 하면 나이가 든 것 같아서\n그리 기분 좋지는 않습니다만…",
}

STATIC_COORDINATES: set[str] = {
    "6:3472:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S202", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
