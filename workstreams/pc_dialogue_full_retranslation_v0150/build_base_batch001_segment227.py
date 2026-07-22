#!/usr/bin/env python3
"""Build Base authoring segment 227 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S227.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s227", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3718:2": "\n그 뒤에도 화친을 유지할지 깊이 생각해 보시기 바랍니다",
    "6:3719:0": "와(과)의 정전도 2개월이 채 남지 않",
    "6:3719:1": "\n정전이 끝나면 상대 영내에 주둔한 병력을 철수시키",
    "6:3719:2": "\n그 뒤에도 화친을 유지할지 깊이 생각해 보시기 바랍니다",
    "6:3720:0": "와(과)의 정전도 2개월이 채 남지 않",
    "6:3720:1": "\n정전이 끝나면 상대 영내에 주둔한 병력을 철수시키",
    "6:3720:2": "\n그 뒤에도 화친을 유지할지 깊이 생각해 보시기 바랍니다",
    "6:3721:0": "와(과)의 정전도 2개월이 채 남지 않",
    "6:3721:1": "\n정전이 끝나면 상대 영내에 주둔한 병력을 철수시키",
    "6:3721:2": "\n그 뒤에도 화친을 유지할지 깊이 생각해 보시기 바랍니다",
    "6:3722:0": "와(과)의 정전도 2개월이 채 남지 않",
    "6:3722:1": "\n정전이 끝나면 상대 영내에 주둔한 병력을 철수시키",
    "6:3722:2": "\n그 뒤에도 화친을 유지할지 깊이 생각해 보시기 바랍니다",
    "6:3723:0": "와(과)의 정전도 2개월이 채 남지 않",
    "6:3723:1": "\n정전이 끝나면 상대 영내에 주둔한 병력을 철수시키",
    "6:3723:2": "\n그 뒤에도 화친을 유지할지 깊이 생각해 보시기 바랍니다",
    "6:3724:0": "와(과)의 정전도 2개월이 채 남지 않",
    "6:3724:1": "\n정전이 끝나면 상대 영내에 주둔한 병력을 철수시키",
    "6:3724:2": "\n그 뒤에도 화친을 유지할지 깊이 생각해 보시기 바랍니다",
    "6:3725:0": "와(과)의 정전도 2개월이 채 남지 않",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S227", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
