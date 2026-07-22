#!/usr/bin/env python3
"""Build Base authoring segment 446 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S446.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s446", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2259:0": "에 대한 공격은\n중단하고 퇴각하라",
    "7:2260:0": "의 공략은\n그만둔다. 철수하라!",
    "7:2261:0": "에 대한 공격을\n끝내고 철수한다",
    "7:2262:0": "에 대한 공격은\n무리다. 철수할 수밖에 없어",
    "7:2263:0": "의 공략은\n어렵다…… 철수한다",
    "7:2264:0": "에 대한 공격은\n중단한다. 철수하라!",
    "7:2265:0": "의 공략은\n그만두고 퇴각합니다",
    "7:2266:0": "에 대한 공격은\n포기하고 물러나자……",
    "7:2267:0": "의 공략은\n어려운가…… 귀환하자",
    "7:2268:0": "에 대한 공격은\n포기한다. 철수하라",
    "7:2269:0": "의 공략은\n그만둔다. 철수하라!",
    "7:2270:0": "의 공략을\n중단하고 물러납시다",
    "7:2271:0": "의 공략은\n무리인가. 철수한다!",
    "7:2272:0": "에 대한 공격은\n포기하고 철수합시다",
    "7:2273:0": "의 공략은\n어렵다. 철수한다",
    "7:2274:0": "때가 무르익었다\n",
    "7:2274:1": "을(를) 공격하라!",
    "7:2275:0": "이제 남은 사냥감은\n",
    "7:2275:1": "뿐이다!",
    "7:2276:0": "남은 것은 성뿐인가\n이제 본격적으로 공략하자꾸나",
}

STATIC_COORDINATES: set[str] = {"7:2276:0"}


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
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S446", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
