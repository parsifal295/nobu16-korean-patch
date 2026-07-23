#!/usr/bin/env python3
"""Build Base authoring segment 742 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S742.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s742", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "12:63:0": "이(가)",
    "12:63:1": "(으)로 개명",
    "12:64:0": "상황이 달라져\n",
    "12:64:1": "들",
    "12:64:2": "부대(병력",
    "12:64:3": ")가 귀환했습니다\n남은",
    "12:64:4": "부대(병력",
    "12:64:5": ")도 귀환시키겠습니까?",
    "12:65:0": "상황이 달라져\n",
    "12:65:1": "(병력",
    "12:65:2": ")가 귀환했습니다\n남은",
    "12:65:3": "부대(병력",
    "12:65:4": ")도 귀환시키겠습니까?",
    "12:66:0": "상황이 달라져\n",
    "12:66:1": "들",
    "12:66:2": "부대(병력",
    "12:66:3": ")가 귀환했습니다",
    "12:67:0": "상황이 달라져\n",
    "12:67:1": "(병력",
    "12:67:2": ")가 귀환했습니다",
}

STATIC_COORDINATES: set[str] = set()
DYNAMIC_RUNTIME_COORDINATES = set(TRANSLATIONS)
EXPECTED_RUNTIME_GAPS: dict[int, tuple[bytes, ...]] = {
    63: (b"\x02\x3c", b"\x02\x3d", b"\x05\x05\x05"),
    64: (
        b"",
        b"\x1b\x43\x41\x02\x3c\x1b\x43\x5a",
        b"\x02\x32",
        b"\x02\x33",
        b"\x02\x34",
        b"\x02\x35",
        b"\x05\x05\x05",
    ),
    65: (
        b"",
        b"\x1b\x43\x41\x02\x3c\x1b\x43\x5a",
        b"\x02\x33",
        b"\x02\x34",
        b"\x02\x35",
        b"\x05\x05\x05",
    ),
    66: (
        b"",
        b"\x1b\x43\x41\x02\x3c\x1b\x43\x5a",
        b"\x02\x32",
        b"\x02\x33",
        b"\x05\x05\x05",
    ),
    67: (
        b"",
        b"\x1b\x43\x41\x02\x3c\x1b\x43\x5a",
        b"\x02\x33",
        b"\x05\x05\x05",
    ),
}


def record_gaps(record: Any) -> tuple[bytes, ...]:
    gaps: list[bytes] = []
    cursor = 0
    for literal in ENGINE.parse_record_literals(record):
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def assert_runtime_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id, expected in EXPECTED_RUNTIME_GAPS.items():
        if record_gaps(source_records[(12, record_id)]) != expected:
            raise RuntimeError(f"pristine runtime skeleton drift: 12:{record_id}")
        if record_gaps(current_records[(12, record_id)]) != expected:
            raise RuntimeError(f"current runtime skeleton drift: 12:{record_id}")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_runtime_scope(prepared)
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_same_coordinate_pk_jp_en_sc_tc_context"
                ),
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S742",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "confirmed_non_display": 0,
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
