#!/usr/bin/env python3
"""Build Base authoring segment 445 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S445.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s445", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2240:0": "은(는) 필요한 곳이다\n탈환해 두어야겠군",
    "7:2241:0": "을(를)\n지금 탈환해 둔다",
    "7:2242:0": "을(를) 탈환하라!\n원래 우리 거라고!",
    "7:2243:0": "은(는)\n탈환해 두겠다",
    "7:2244:0": "을(를) 공격하라\n본래 우리 영지다!",
    "7:2245:0": "은(는) 탈환해\n두도록 합시다",
    "7:2246:0": "을(를) 탈환해\n주변을 견제한다",
    "7:2247:0": "은(는)\n우리 가문이 되찾겠다",
    "7:2248:0": "은(는) 본래 우리의 군이다\n탈환하겠다",
    "7:2249:0": "을(를)\n탈환해 둘까",
    "7:2250:0": "을(를)\n탈환하겠습니다",
    "7:2251:0": "우리는—",
    "7:2251:1": "을(를)\n탈환한다!",
    "7:2252:0": "을(를)\n탈환하도록 합시다",
    "7:2253:0": "을(를) 제압해\n우리 영지로 되돌리자",
    "7:2254:0": "의 공략은\n끝이다. 철수하라",
    "7:2255:0": "의 공략은\n어렵다…… 철수하라!",
    "7:2256:0": "의 공략을\n포기하고 철수하도록 하지",
    "7:2257:0": "의 공략은\n중단하고 퇴각하라",
    "7:2258:0": "의 공략은\n중지하고 철수하라",
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
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "pending",
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S445", "decision_count": len(rows),
                             "retranslated": 0, "dynamic_runtime_review_pending": len(rows),
                             "steam_write_performed": False, "output": str(OUTPUT)},
                            ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
