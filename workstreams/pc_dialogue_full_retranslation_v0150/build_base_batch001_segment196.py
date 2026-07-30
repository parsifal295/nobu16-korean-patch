#!/usr/bin/env python3
"""Build Base authoring segment 196 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S196.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s196", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3402:0": "안심하고",
    "6:3402:1": ", 이",
    "6:3402:2": "이(가)\n당주라니",
    "6:3402:3": "인 이상, 어떤 수를\n써서라도 가문을 번영시켜 보이겠",
    "6:3403:0": ", 반드시",
    "6:3403:1": "기대에\n부응할 것을 이 자리에서 맹세하",
    "6:3403:2": ".\n",
    "6:3403:3": "은(는) 나에게",
    "6:3404:0": "우리 가문을 이끄는 일을 일임받다니\n더없는 기쁨과 함께,",
    "6:3404:1": "책임의 무게에\n마음이 절로 다잡히는 기분",
    "6:3405:0": "설마 이 늙은 몸에 차례가 돌아올 줄은\n몰랐다만… 이 몸이 스러질 때까지\n",
    "6:3405:1": "을(를) 반드시 지켜 보이",
    "6:3406:0": "이런, 이런. 살날이 얼마 남지 않은 몸으로 무거운 짐을\n지게 될 줄이야… 허나\n",
    "6:3406:1": "의",
    "6:3406:2": "기대에는 부응해 보이",
    "6:3407:0": ", 안심하고",
    "6:3407:1": ".\n",
    "6:3407:2": "은(는) 이",
    "6:3407:3": "이(가)\n목숨을 바쳐서라도 지켜 보이",
    "6:3408:0": "뒷일은",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S196", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
