#!/usr/bin/env python3
"""Build Base authoring segment 740 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S740.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s740", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "12:53:0": "참으로 경사스러운 일입니다!\n",
    "12:53:1": "도카이",
    "12:53:2": "에 있는 성은 모두 우리 가문이\n장악했습니다",
    "12:53:3": ". 천추만세!",
    "12:54:0": "도카이",
    "12:54:1": " 지방 전역에\n평온을 가져올 수 있었군…\n모두, 수고했다",
    "12:54:2": "!",
    "12:55:0": "축하드립니다",
    "12:55:1": "!\n",
    "12:55:2": "긴키",
    "12:55:3": "의 성은 모두 우리 가문이 장악했습니다",
    "12:55:4": ".\n수백 년 만의 쾌거가 아니겠습니까",
    "12:55:5": "!",
    "12:56:0": "마침내 ",
    "12:56:1": "기나이",
    "12:56:2": "와 그 인근에\n평온을 가져올 수 있었군…\n모두, 수고했다",
    "12:56:3": "!",
    "12:57:0": "축하드립니다",
    "12:57:1": "!\n",
    "12:57:2": "주고쿠",
    "12:57:3": " 지방의 성을 모두 우리 가문이 장악했습니다",
    "12:57:4": ".\n전례 없는 쾌거입니다",
    "12:57:5": "!",
}

STATIC_COORDINATES = set(TRANSLATIONS)
DYNAMIC_RUNTIME_COORDINATES: set[str] = set()
COLOURED_STATIC_RECORD_IDS = {53, 54, 55, 56, 57}


def assert_static_colour_scope(prepared: Any) -> None:
    source_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id in COLOURED_STATIC_RECORD_IDS:
        source = source_records[(12, record_id)].data
        current = current_records[(12, record_id)].data
        if b"\x01\x43" not in source:
            raise RuntimeError(f"pristine inflection opcode is absent: 12:{record_id}")
        if b"\x01\x43" in current:
            raise RuntimeError(f"removed inflection opcode unexpectedly survives: 12:{record_id}")
        if current.count(b"\x1b\x43\x43") < 1 or current.count(b"\x1b\x43\x5a") < 1:
            raise RuntimeError(f"regional colour wrapper drift: 12:{record_id}")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_static_colour_scope(prepared)
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
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
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
                "segment": "base_msggame_B001_S740",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": 0,
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
