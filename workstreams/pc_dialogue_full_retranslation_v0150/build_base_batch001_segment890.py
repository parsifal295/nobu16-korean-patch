#!/usr/bin/env python3
"""Build Base authoring segment 890 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment884 as FRAMEWORK
import build_base_batch001_segment888 as CANONICAL_B107


ENGINE = FRAMEWORK.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S890.private.v1.jsonl"
)
SEGMENT = 890
DEVELOPMENT_SOURCE = CANONICAL_B107.COUNTY_DEVELOPMENT_SOURCE_JP
DEVELOPMENT_CANONICAL = CANONICAL_B107.COUNTY_DEVELOPMENT_CANONICAL
BASE_GAPS = CANONICAL_B107.COUNTY_DEVELOPMENT_BASE_GAPS
PK_GAPS = CANONICAL_B107.COUNTY_DEVELOPMENT_PK_GAPS
PK_OFFSET = 15
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id in range(1375, 1379)
    for literal_id, translation in enumerate(DEVELOPMENT_CANONICAL)
}
RECORD_ARITIES = {record_id: 5 for record_id in range(1375, 1379)}
PK_RECORD_MAP = {
    record_id: record_id + PK_OFFSET for record_id in RECORD_ARITIES
}
EXPECTED_BASE_JP = {
    record_id: DEVELOPMENT_SOURCE for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    record_id: BASE_GAPS for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = {
    record_id: PK_GAPS for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B107_pristine_base_pc_jp_authoritative_"
    "exact_county_development_completion_report_family_imported_s888_"
    "canonical_with_explicit_base_to_pk_plus_15_mapping_blank_sc_tc_pk_en_"
    "auxiliary_context_dynamic_location_development_target_person_and_"
    "conjugation_tokens_people_cooperation_and_local_ruler_popularity_"
    "meanings_current_layout_and_opcode_skeleton_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if (
        DEVELOPMENT_SOURCE is not CANONICAL_B107.COUNTY_DEVELOPMENT_SOURCE_JP
        or DEVELOPMENT_CANONICAL
        is not CANONICAL_B107.COUNTY_DEVELOPMENT_CANONICAL
        or BASE_GAPS is not CANONICAL_B107.COUNTY_DEVELOPMENT_BASE_GAPS
        or PK_GAPS is not CANONICAL_B107.COUNTY_DEVELOPMENT_PK_GAPS
    ):
        raise RuntimeError("segment 890 S888 canonical object identity drifted")
    prior_group = tuple(
        CANONICAL_B107.RAW_TRANSLATIONS[f"15:1370:{literal_id}"]
        for literal_id in range(5)
    )
    if prior_group != DEVELOPMENT_CANONICAL:
        raise RuntimeError("segment 890 S888 development canonical drifted")
    record_ids = sorted(
        {int(coordinate.split(":")[1]) for coordinate in raw_translations}
    )
    for record_id in record_ids:
        if (
            tuple(
                item.text
                for item in ENGINE.parse_record_literals(
                    source_records[(15, record_id)]
                )
            )
            != DEVELOPMENT_SOURCE
        ):
            raise RuntimeError(
                f"segment 890 development source drifted: {record_id}"
            )
        raw_group = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(5)
        )
        resolved_group = tuple(
            translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(5)
        )
        if (
            raw_group != DEVELOPMENT_CANONICAL
            or resolved_group != DEVELOPMENT_CANONICAL
        ):
            raise RuntimeError(
                f"segment 890 development canonical drifted: {record_id}"
            )
    if (
        PK_OFFSET != 15
        or BASE_GAPS[:2] != ("029632", "02BE32")
        or BASE_GAPS[4] != "014301000000"
        or PK_GAPS[:2] != ("029632", "02BE32")
        or PK_GAPS[4] != "014301000000"
        or BASE_GAPS[2:4] != ("014314020000", "014368020000")
        or PK_GAPS[2:4] != ("01431A020000", "014374020000")
        or BASE_GAPS[5] != "014356020000050505"
        or PK_GAPS[5] != "014362020000050505"
    ):
        raise RuntimeError("segment 890 dynamic token/opcode positions drifted")
    if (
        not DEVELOPMENT_CANONICAL[1].endswith("개척하")
        or not DEVELOPMENT_CANONICAL[2].endswith("큰 도움이")
        or DEVELOPMENT_CANONICAL[3] != "\n이 또한 이 땅을 다스리는"
        or DEVELOPMENT_CANONICAL[4] != "의 인망"
    ):
        raise RuntimeError("segment 890 dynamic conjugation/token roles drifted")


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    basis: str,
) -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    pk_record_map = {
        record_id: record_id + PK_OFFSET for record_id in record_arities
    }
    expected_base_jp = {
        record_id: DEVELOPMENT_SOURCE for record_id in record_arities
    }
    return FRAMEWORK.build_segment_rows(
        output=output,
        segment=segment,
        raw_translations=raw_translations,
        record_arities=record_arities,
        pk_record_map=pk_record_map,
        expected_base_jp=expected_base_jp,
        expected_pk_jp=expected_base_jp,
        base_gaps={record_id: BASE_GAPS for record_id in record_arities},
        pk_jp_gaps={record_id: PK_GAPS for record_id in record_arities},
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=basis,
        semantic_assertions=assert_semantics,
    )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        basis=BASIS,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 890 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S890",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "exact_development_records": len(RECORD_ARITIES),
                "base_to_pk_offset": PK_OFFSET,
                "s888_canonical_imported": True,
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
