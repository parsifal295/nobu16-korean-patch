#!/usr/bin/env python3
"""Build Base authoring segment 15 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S15.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s15", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:401:0": "네버 기브 업!\n절대 포기하지 않아!",
    "2:402:0": "여기가 승부처다!\n모두, 포기하지 마라",
    "2:402:1": "!",
    "2:403:0": "자, 듣거라! 나야말로 미나모토노 구로 요시쓰네!\n솜씨 있는 자라면 한판 겨뤄 보자!",
    "2:404:0": "야말로",
    "2:404:1": "!\n한판 겨뤄 보",
    "2:404:2": "!",
    "2:405:0": "성을 칠 때는 바로 지금이다!\n우리 정예병이 모조리 제압해 주마!",
    "2:406:0": "성을 칠 때는 바로 지금",
    "2:406:1": "!\n모조리 제압해 보이겠",
    "2:406:2": "!",
    "2:407:0": "하늘이여, 지켜보소서!\n백성을 위해서라면 이 몸을 바치리라!",
    "2:408:0": "하늘이여, 지켜보소서!",
    "2:408:1": "\n백성을 위해 이 몸을 ",
    "2:408:2": "바치겠다!",
    "2:409:0": "흉포한 적에게는 매와 같이!\n용병의 극의가 바로 여기에 있다!",
    "2:410:0": "흉포한 적에게는 매와 같이!\n용병의 극의는 ",
    "2:410:1": "이것이다!",
    "2:411:0": "덴넨리신류의 검술,\n그 일단을 여기서 보여 주지!",
    "2:412:0": "내 검술의\n진수를 여기서 보여 ",
    "2:412:1": "주마!",
}

NON_DISPLAY_COORDINATES = {f"2:{record_id}:0" for record_id in range(413, 424)}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {402, 404, 406, 408, 410, 412}
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    coordinates = sorted(
        set(TRANSLATIONS) | NON_DISPLAY_COORDINATES,
        key=lambda value: tuple(int(part) for part in value.split(":")),
    )
    for coordinate in coordinates:
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        non_display = coordinate in NON_DISPLAY_COORDINATES
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
            "semantic_review": "approved",
            "scope_classification": (
                "confirmed_non_display"
                if non_display
                else "runtime_fragment_pending" if dynamic else "retranslated"
            ),
            "layout_review": "not_needed" if non_display else "unchanged_from_current",
            "runtime_review": "not_required" if non_display or not dynamic else "pending",
            "basis": (
                "explicit_contiguous_unused_trait_dummy_tail_structural_evidence"
                if non_display
                else "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available"
            ),
            "historic_korean_used": False,
            "switch_korean_used": False,
        }
        if not non_display:
            row["translation"] = TRANSLATIONS[coordinate]
        rows.append(row)
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    expected_count = len(TRANSLATIONS) + len(NON_DISPLAY_COORDINATES)
    if len(validated) != expected_count:
        raise RuntimeError("validated decision count differs from the segment decision count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S15",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "confirmed_non_display": len(NON_DISPLAY_COORDINATES),
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
