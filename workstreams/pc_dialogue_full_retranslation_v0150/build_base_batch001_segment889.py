#!/usr/bin/env python3
"""Build Base authoring segment 889 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment888 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S889.private.v1.jsonl"
)
SEGMENT = 889
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id in range(1371, 1375)
    for literal_id, translation in enumerate(PREVIOUS.COUNTY_DEVELOPMENT_CANONICAL)
}
RECORD_ARITIES = {record_id: 5 for record_id in range(1371, 1375)}
EXPECTED_BASE_JP = {
    record_id: PREVIOUS.COUNTY_DEVELOPMENT_SOURCE_JP
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: PREVIOUS.COUNTY_DEVELOPMENT_BASE_GAPS
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = {
    record_id: PREVIOUS.COUNTY_DEVELOPMENT_PK_GAPS
    for record_id in RECORD_ARITIES
}
PK_RECORD_MAP = {record_id: record_id + 15 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B107_pristine_base_pc_jp_authoritative_"
    "exact_19_record_county_development_report_group_records_1371_1374_"
    "with_explicit_plus_15_base_to_pk_mapping_blank_sc_tc_pk_en_auxiliary_"
    "context_S888_county_development_canonical_directly_imported_dynamic_"
    "county_development_type_officer_and_conjugation_tokens_exact_current_"
    "layout_opcode_skeleton_runtime_fragment_pending"
)


def source_literals(
    source_records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, record_id)])
    )


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(1370, 1389):
        if source_literals(source_records, record_id) != (
            PREVIOUS.COUNTY_DEVELOPMENT_SOURCE_JP
        ):
            raise RuntimeError(
                f"segment 889 exact 19-record development source drifted: {record_id}"
            )
    for record_id in RECORD_ARITIES:
        raw_group = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        )
        resolved_group = tuple(
            translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        )
        if raw_group != PREVIOUS.COUNTY_DEVELOPMENT_CANONICAL:
            raise RuntimeError(
                f"segment 889 imported raw development canonical drifted: {record_id}"
            )
        if resolved_group != PREVIOUS.COUNTY_DEVELOPMENT_CANONICAL:
            raise RuntimeError(
                f"segment 889 imported resolved development canonical drifted: "
                f"{record_id}"
            )
    if set(PK_RECORD_MAP.values()) != set(range(1386, 1390)):
        raise RuntimeError("segment 889 explicit +15 PK mapping drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_record_map=PK_RECORD_MAP,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 889 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S889",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "county_development_group_size": 19,
                "county_development_canonical_imported": True,
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
