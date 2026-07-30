#!/usr/bin/env python3
"""Build Base authoring segment 732 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S732.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s732", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "9:3759:0": "제가 합전의 법도를 설명해 드리겠습니다\n이미 알고 계시리라 생각하오나\n혹시 모르니 말씀드리는 것이옵니다",
    "9:3760:0": "이제 군평정 시간이 되었습니다\n무엇을 결정하셔야 하는지\n제가 안내해 드리겠습니다",
    "9:3761:0": "합전에서 먼저 알아두셔야 할 것은\n무엇이 승리이고 무엇이 패배인가 하는 점입니다\n설명은 제게 맡겨 주십시오",
    "9:3765:0": "벌써 요충지를 제압하시다니 순조로운 출발입니다\n요충지를 장악해 우위를 얻는 것이 합전의 요체\n자세히 설명해 드리겠습니다",
}

NON_DISPLAY_TEXT = {
    **{f"9:{3741 + offset}:0": f"009_jinei_{group}_{slot}" for offset, (group, slot) in enumerate(
        ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3))
    )},
    **{f"9:{3747 + offset}:0": f"010_jinei_{group}_{slot}" for offset, (group, slot) in enumerate(
        ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3))
    )},
    **{f"9:{3753 + offset}:0": f"011_jinei_{group}_{slot}" for offset, (group, slot) in enumerate(
        ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3))
    )},
}
NON_DISPLAY_COORDINATES = set(NON_DISPLAY_TEXT)
OMITTED_EMPTY_RECORDS = {3762, 3763, 3764}
DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    pristine_records = ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    for record_id in OMITTED_EMPTY_RECORDS:
        source_literals = ENGINE.parse_record_literals(pristine_records[(9, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(9, record_id)])
        if [item.text for item in source_literals] != [""] or [item.text for item in current_literals] != [""]:
            raise RuntimeError(f"expected omitted empty record drift: 9:{record_id}")
    rows: list[dict[str, object]] = []
    coordinates = sorted(
        set(TRANSLATIONS) | NON_DISPLAY_COORDINATES,
        key=lambda value: tuple(int(part) for part in value.split(":")),
    )
    for coordinate in coordinates:
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        non_display = coordinate in NON_DISPLAY_COORDINATES
        if non_display:
            source_record = pristine_records[(block_id, record_id)]
            current_record = current_records[(block_id, record_id)]
            source_text = list(ENGINE.parse_record_literals(source_record))[literal_id].text
            current_text = list(ENGINE.parse_record_literals(current_record))[literal_id].text
            if (
                NON_DISPLAY_TEXT[coordinate] != source_text
                or source_text != current_text
                or not source_text.isascii()
                or source_record.data != current_record.data
                or not source_record.data.startswith(b"\x1bH\x07\x07\x01")
            ):
                raise RuntimeError(f"non-display formation identifier drift: {coordinate}")
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
            "semantic_review": "approved",
            "scope_classification": "confirmed_non_display" if non_display else "retranslated",
            "layout_review": "unchanged_from_current",
            "runtime_review": "not_required",
            "basis": (
                "pristine_base_pc_jp_with_base_sc_tc_and_exact_pk_record_context_where_available"
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
                "segment": "base_msggame_B001_S732",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS),
                "dynamic_runtime_review_pending": 0,
                "confirmed_non_display": len(NON_DISPLAY_COORDINATES),
                "omitted_empty_records": len(OMITTED_EMPTY_RECORDS),
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
