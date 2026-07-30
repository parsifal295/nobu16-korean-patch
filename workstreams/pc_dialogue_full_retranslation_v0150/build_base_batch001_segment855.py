#!/usr/bin/env python3
"""Build Base authoring segment 855 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment854 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S855.private.v1.jsonl"
SEGMENT = 855
FAILURE_SOURCE = (
    "への工作は失敗いたしました\n"
    "不覚にも工作が露見してしまい\n"
    "面目次第もございません",
)
FAILURE_TRANSLATION = (
    "에 대한 공작은 실패하였사옵니다\n"
    "불찰로 공작이 발각되고 말아\n"
    "면목이 없사옵니다"
)
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:0": FAILURE_TRANSLATION for record_id in range(945, 967)
}
RECORD_ARITIES = {record_id: 1 for record_id in range(945, 967)}
EXPECTED_JP = {record_id: FAILURE_SOURCE for record_id in range(945, 967)}
EXPECTED_BASE_GAPS = {
    record_id: ("026432", "050505") for record_id in range(945, 967)
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B103_pristine_base_pc_jp_authoritative_"
    "castle_destabilization_failure_reports_with_exact_cross_segment_24_record_"
    "source_and_translation_group_uniform_plus_7_pk_jp_sc_tc_arrays_pk_en_sc_"
    "tc_empty_context_humble_historical_register_current_pc_line_token_gap_"
    "signature_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(945, 969):
        if COMMON.CORE.source_literals(source_records, record_id) != FAILURE_SOURCE:
            raise RuntimeError(
                f"segment 855/856 exact failure source group drifted: {record_id}"
            )
    if len(set(raw_translations.values())) != 1:
        raise RuntimeError("segment 855 exact failure translation group drifted")
    if next(iter(raw_translations.values())) != FAILURE_TRANSLATION:
        raise RuntimeError("segment 855 failure canonical drifted")
    joined = "\n".join(translations.values())
    for required in ("공작", "실패하였사옵니다", "불찰", "발각", "면목이 없사옵니다"):
        if required not in joined:
            raise RuntimeError(f"segment 855 failure register drifted: {required}")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_blank_coordinates=set(),
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 855 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S855",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": 0,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
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
