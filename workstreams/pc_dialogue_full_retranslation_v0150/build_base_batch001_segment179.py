#!/usr/bin/env python3
"""Build Base authoring segment 179 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S179.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s179", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3154:0": "이 또한 가문을 지키기 위함…\n부디 잘 부탁하오",
    "6:3155:0": "이 또한 가문을 지키기 위함입니다…\n부디 잘 부탁드립니다",
    "6:3156:0": "이 또한 가문을 지키기 위함…\n아무쪼록 잘 부탁드리오",
    "6:3157:0": "따르겠다는데 거절할 순 없지\n좋아,",
    "6:3157:1": "이(가) 지켜 주마",
    "6:3158:0": "따르겠다고 하니 받아들이겠소\n",
    "6:3158:1": "의 휘하에서 비호하겠소",
    "6:3159:0": "종속의 건, 받아들였노라\n",
    "6:3159:1": "의 산하에서 가문의 명맥을 지키거라",
    "6:3160:0": "따르겠다고 하신다면 받아들이지요\n",
    "6:3160:1": "이(가) 귀 가문을 지켜 드리겠습니다",
    "6:3161:0": "따르겠다고 한다면 받아들이겠노라\n",
    "6:3161:1": "이(가) 지켜 주마",
    "6:3162:0": "따르겠다고 한다면 받아들이겠노라\n",
    "6:3162:1": "이(가) 귀 가문의 후견이 되어 주마",
    "6:3163:0": "따르겠다고 한다면 받아들이겠노라\n",
    "6:3163:1": "이(가) 그대들을 지키겠다",
    "6:3164:0": "따르겠다고 한다면 받아들여 주지\n",
    "6:3164:1": "이(가) 자네들을 비호하겠소",
    "6:3165:0": "따르겠다고 하신다면 받아들이지요\n",
}

STATIC_COORDINATES: set[str] = {
    "6:3154:0",
    "6:3155:0",
    "6:3156:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S179", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
