#!/usr/bin/env python3
"""Build Base authoring segment 314 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S314.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s314", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:266:1": "제안을 받아들이",
    "7:267:0": "의지할 곳 없는 몸이 된 지금\n그 온정, 감사히 받아들이",
    "7:268:0": "……옛 주군을 당장 잊을 수는 없",
    "7:268:1": "지만\n이 또한 난세의 이치\n앞으로 잘 부탁하오",
    "7:269:0": "우리 가문이 천하를 다스릴 길은 끊기",
    "7:269:1": "……\n이후로는 「",
    "7:269:2": "」을(를) 주군으로 받들어\n천하를 위해 힘쓰",
    "7:270:0": "이렇게 된 이상 어쩔 수",
    "7:270:1": "……\n이 「",
    "7:270:2": "」, 이후로는 한 사람의 가신이 되어\n부족한 재주나마 다하",
    "7:271:0": "한번 버린 이 목숨……거두어 주시겠다면\n이후,",
    "7:271:1": "뜻대로 쓰시오",
    "7:272:0": "……한번 목숨을 건져 주신 은혜를 입은 몸\n",
    "7:272:1": "을(를) 섬기게 되",
    "7:272:2": "\n이 또한 인연……",
    "7:273:0": "에게는 놓아주신 은혜가",
    "7:273:1": "\n이렇게 다시 불러 주신 이상\n따를 수밖에 없",
    "7:273:2": "으리라",
    "7:274:0": "예전에 포박되었던 나를 풀어 주신 은혜를\n결코 잊어서는",
    "7:274:1": "\n분골쇄신하여 「",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S314", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
