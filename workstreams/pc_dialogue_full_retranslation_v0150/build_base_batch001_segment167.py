#!/usr/bin/env python3
"""Build Base authoring segment 167 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S167.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s167", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3007:0": "말도 안 되는군\n상대를 화나게 할 뿐이다",
    "6:3008:0": "너무 많이 바랐나… 품위가 없군",
    "6:3009:0": "이건… 좀… 지나친 욕심이로군",
    "6:3010:0": "이렇게까지 요구하면\n",
    "6:3010:1": "님도 화를 내시겠지요…",
    "6:3011:0": "역시 지나친 요구인가\n상대를 화나게 해서는 소용이 없다",
    "6:3012:0": "이보다 더 값을 올리면\n상대를 화나게 하겠군요",
    "6:3013:0": "욕심이 지나치면 일을 그르치는 법\n과도한 요구는 삼가야겠군",
    "6:3014:0": "모 아니면 도군…\n뭐, 크게 질러 보는 것도 나쁘진 않지",
    "6:3015:0": "미묘하군… 받아들일 수도 있다\n하지만 화나게 할 가능성도 있어…",
    "6:3016:0": "모 아니면 도인가…\n고민되는구나…",
    "6:3017:0": "응할지 거절할지…\n제법 도박이겠군요…",
    "6:3018:0": "운을 하늘에 맡겨 볼까…",
    "6:3019:0": "이 조건을 제시하여\n용기와 운을 시험해 볼 텐가?",
    "6:3020:0": "정말 이만큼 얻을 수 있다면 좋겠지만…",
    "6:3021:0": "어려운 대목이로다…\n어찌해야 할꼬…",
    "6:3022:0": "상대가 거절할지도…\n판단하기 어렵군요",
    "6:3023:0": "너무 세게 불렀나?\n상대가 승낙할지는 확실치 않군",
    "6:3024:0": "응해 줄지는\n상대의 기분에 달렸겠지요",
    "6:3025:0": "상대의 기분에 따라서는\n거절당할지도 모르겠군…",
}

STATIC_COORDINATES = {
    "6:3007:0", "6:3008:0", "6:3009:0", "6:3011:0", "6:3012:0",
    "6:3013:0", "6:3014:0", "6:3015:0", "6:3016:0", "6:3017:0",
    "6:3018:0", "6:3019:0", "6:3020:0", "6:3021:0", "6:3022:0",
    "6:3023:0", "6:3024:0", "6:3025:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S167", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
