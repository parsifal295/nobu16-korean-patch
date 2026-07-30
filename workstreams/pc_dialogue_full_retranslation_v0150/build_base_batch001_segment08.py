#!/usr/bin/env python3
"""Classify the Base internal grammar/font test block for v0.15.0."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S08.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s08", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


RECORD_LITERAL_COUNTS: dict[int, int] = {
    7: 2,
    8: 1,
    9: 3,
    10: 6,
    11: 5,
    12: 6,
    13: 2,
    14: 4,
    15: 4,
    16: 2,
    17: 1,
    18: 4,
    19: 3,
    20: 4,
    21: 3,
    22: 3,
    23: 3,
    24: 2,
    25: 3,
    26: 2,
    27: 2,
    28: 2,
    29: 1,
    30: 3,
}

COORDINATES = tuple(
    f"1:{record_id}:{literal_id}"
    for record_id, literal_count in RECORD_LITERAL_COUNTS.items()
    for literal_id in range(literal_count)
)


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate in COORDINATES:
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "semantic_review": "approved",
                "scope_classification": "confirmed_non_display",
                "layout_review": "not_needed",
                "runtime_review": "not_required",
                "basis": "non_display_test_block_structural_evidence",
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(COORDINATES):
        raise RuntimeError("validated decision count differs from the segment classification count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S08",
                "decision_count": len(rows),
                "confirmed_non_display": len(rows),
                "dynamic_runtime_review_pending": 0,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
