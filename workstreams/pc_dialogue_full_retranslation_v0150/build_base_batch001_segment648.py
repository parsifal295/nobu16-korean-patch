#!/usr/bin/env python3
"""Build Base authoring segment 648 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S648.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s648", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:2086:0": "이 피해는 웃어넘길 수 없겠군……",
    "9:2087:0": "단숨에 궁지로\n몰리고 말았군요……",
    "9:2088:0": "이 몸―",
    "9:2088:1": "이(가)\n이 지경까지 몰리다니……!?",
    "9:2089:0": "이토록 많은 병사를\n잃고 말았는가……",
    "9:2090:0": "크윽, 피해 상황은\n차마 눈 뜨고 볼 수 없구나……",
    "9:2091:0": "안 되겠군…… 이렇게까지\n당하고만 있어서는……!",
    "9:2092:0": "이건……\n상당히 힘들겠군요……",
    "9:2093:0": "큭……!?\n이대로는 큰일 나겠군……",
    "9:2094:0": "으으윽……\n상당한 타격입니다……",
    "9:2095:0": "은(는) 자비도\n손속도 모르는가!",
    "9:2096:0": "전력이 상당히 깎였군……",
    "9:2097:0": "크으윽……!\n이 무슨 위력이냐!",
    "9:2098:0": "이 피해는 웃어넘길 수 없겠군……",
    "9:2099:0": "단숨에 궁지로\n몰리고 말았군요……",
    "9:2100:0": "이 몸―",
    "9:2100:1": "이(가)\n이 지경까지 몰리다니……!?",
    "9:2101:0": "이토록 많은 병사를\n잃고 말았는가……",
    "9:2102:0": "크윽, 피해 상황은\n차마 눈 뜨고 볼 수 없구나……",
    "9:2103:0": "안 되겠군…… 이렇게까지\n당하고만 있어서는……!",
    "9:2104:0": "이건……\n상당히 힘들겠군요……",
    "9:2105:0": "큭……!?\n이대로는 큰일 나겠군……",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:2088:0",
    "9:2088:1",
    "9:2095:0",
    "9:2100:0",
    "9:2100:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S648", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
