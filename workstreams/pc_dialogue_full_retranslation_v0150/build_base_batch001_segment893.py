#!/usr/bin/env python3
"""Build Base authoring segment 893 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment888 as DEVELOPMENT_B107
import build_base_batch001_segment892 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = DEVELOPMENT_B107.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S893.private.v1.jsonl"
)
SEGMENT = 893
DEVELOPMENT_SOURCE_JP = DEVELOPMENT_B107.COUNTY_DEVELOPMENT_SOURCE_JP
DEVELOPMENT_CANONICAL = DEVELOPMENT_B107.COUNTY_DEVELOPMENT_CANONICAL
DEVELOPMENT_BASE_GAPS = DEVELOPMENT_B107.COUNTY_DEVELOPMENT_BASE_GAPS
DEVELOPMENT_PK_GAPS = DEVELOPMENT_B107.COUNTY_DEVELOPMENT_PK_GAPS
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id in range(1389, 1393)
    for literal_id, translation in enumerate(DEVELOPMENT_CANONICAL)
}
RECORD_ARITIES = {record_id: 5 for record_id in range(1389, 1393)}
EXPECTED_BASE_JP = {
    record_id: DEVELOPMENT_SOURCE_JP for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: DEVELOPMENT_BASE_GAPS for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = {
    record_id: DEVELOPMENT_PK_GAPS for record_id in RECORD_ARITIES
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "county_development_exact_continuation_with_uniform_plus_15_pk_jp_sc_tc_"
    "mapping_blank_auxiliary_context_b107_s888_canonical_imported_dynamic_"
    "county_development_trait_officer_tokens_current_layout_and_opcode_"
    "skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in RECORD_ARITIES:
        if COMMON.CORE.source_literals(
            source_records, record_id
        ) != DEVELOPMENT_SOURCE_JP:
            raise RuntimeError(
                f"segment 893 county-development source drifted: {record_id}"
            )
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(5)
        )
        if actual != DEVELOPMENT_CANONICAL:
            raise RuntimeError(
                f"segment 893 B107 development canonical drifted: {record_id}"
            )
    if DEVELOPMENT_CANONICAL is not DEVELOPMENT_B107.COUNTY_DEVELOPMENT_CANONICAL:
        raise RuntimeError("segment 893 development canonical was copied")
    joined = "\n".join(translations.values())
    for required in ("개척하", "백성", "힘을 보태", "인망"):
        if required not in joined:
            raise RuntimeError(
                f"segment 893 development semantics drifted: {required}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != len(translations):
        raise RuntimeError("segment 893 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S893",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "exact_development_records": len(RECORD_ARITIES),
                "base_to_pk_offset": 15,
                "b107_development_canonical_imported": True,
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
