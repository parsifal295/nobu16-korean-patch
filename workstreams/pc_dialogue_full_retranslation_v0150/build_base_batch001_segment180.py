#!/usr/bin/env python3
"""Build Base authoring segment 180 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S180.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s180", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3165:1": "이(가) 당신을 지켜 드리겠습니다",
    "6:3166:0": "따른다면 받아들일 따름\n",
    "6:3166:1": "이(가) 그대를 지켜 주리라",
    "6:3167:0": "따르겠다고 하신다면 받아들이겠습니다\n",
    "6:3167:1": "이(가) 지켜 드리겠습니다",
    "6:3168:0": "따르겠다고 한다면 받아들여 주마\n",
    "6:3168:1": "이(가) 자네들을 지켜 주마",
    "6:3169:0": "좋아\n계속 맹우로 지내는 데 이의는 없어",
    "6:3170:0": "좋다\n맹약의 연장, 이의 없다",
    "6:3171:0": "좋다\n맹약을 잇는 데 우리도 이의는 없다",
    "6:3172:0": "알겠습니다\n맹약을 잇는 데 이의는 없사옵니다",
    "6:3173:0": "알겠소\n앞으로도 우리는 맹우일 것이오",
    "6:3174:0": "좋다\n이 맹약에는 아직 이득이 있다",
    "6:3175:0": "좋다\n맹약은 계속 이어야겠지",
    "6:3176:0": "좋다\n이 맹약은 소중히 지켜야겠군",
    "6:3177:0": "좋습니다\n저도 계속 맹우로 남고 싶었습니다",
    "6:3178:0": "좋다\n맹약을 잇는 데 이의는 없다",
    "6:3179:0": "기꺼이 받아들이겠습니다\n앞으로도 서로 도우며 나아갑시다",
    "6:3180:0": "좋다\n계속 맹우로 지내는 데 이의는 없다",
    "6:3181:0": "우리 맹약도 이젠 반석처럼 굳건해졌군\n앞으로도 믿고 의지하겠다",
}

STATIC_COORDINATES: set[str] = {
    "6:3169:0",
    "6:3170:0",
    "6:3171:0",
    "6:3172:0",
    "6:3173:0",
    "6:3174:0",
    "6:3175:0",
    "6:3176:0",
    "6:3177:0",
    "6:3178:0",
    "6:3179:0",
    "6:3180:0",
    "6:3181:0",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S180", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
