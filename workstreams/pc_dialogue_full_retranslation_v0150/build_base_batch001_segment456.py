#!/usr/bin/env python3
"""Build Base authoring segment 456 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S456.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s456", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "7:2418:0": "와의 전투에는\n충분한 병력",
    "7:2418:1": "\n게다가 적군은 병량이 부족하",
    "7:2419:0": "와의 전투에는\n충분한 병력",
    "7:2420:0": "와의 전투에는 병력이 부족",
    "7:2420:1": "\n힘겨운 싸움이 되겠다니",
    "7:2420:2": "\n게다가 병량에는 불안이 남",
    "7:2420:3": ", 유의하시오",
    "7:2421:0": "와의 전투에는 병력이 부족",
    "7:2421:1": "\n힘겨운 싸움이 되겠다니",
    "7:2421:2": "\n하지만 적군은 병량이 부족하",
    "7:2422:0": "와의 전투에는 병력이 부족",
    "7:2422:1": "\n힘겨운 싸움이 되겠다니",
    "7:2423:0": "와 우리의 전력은 거의 호각\n승패는 지휘에 달렸다는 것이군",
    "7:2423:1": "\n다만 병량에는 불안이 남",
    "7:2423:2": ", 유의하시오",
    "7:2424:0": "와 우리의 전력은 거의 호각\n승패는 지휘에 달렸다는 것이군",
    "7:2424:1": "\n하지만 적군은 병량이 부족하",
    "7:2425:0": "와 우리의 전력은 거의 호각\n승패는 지휘에 달렸다는 것이군",
    "7:2426:0": "이만한 병력이라면—",
    "7:2426:1": "을(를)\n지켜 내기는 쉬운 일",
    "7:2426:2": "\n다만 병량에는 유의",
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
                     "basis": "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S456", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
