#!/usr/bin/env python3
"""Build Base authoring segment 963 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment962 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
CANONICAL_B1 = PREVIOUS.PREVIOUS
CANONICAL_B0 = CANONICAL_B1.PREVIOUS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S963.private.v1.jsonl"
)
SEGMENT = 963
ACTION_TOKEN = PREVIOUS.ACTION_TOKEN
CANONICAL_RECORD_MAP = {
    2071: 2047,
    2072: 2048,
    2073: 2049,
    2074: 2050,
    2075: 2051,
    2076: 2049,
    2077: 2053,
    2078: 2054,
    2079: 2055,
    2080: 2054,
    2081: 2047,
}


def canonical_module(record_id: int) -> Any:
    return CANONICAL_B0 if record_id <= 2054 else CANONICAL_B1


TRANSLATIONS_BY_RECORD = {
    record_id: canonical_module(canonical_id).TRANSLATIONS_BY_RECORD[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:2071:1": "\n",
    "15:2073:1": "\n",
    "15:2076:1": "\n",
    "15:2081:1": "\n",
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    record_id: canonical_module(canonical_id).EXPECTED_BASE_JP[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: canonical_module(canonical_id).EXPECTED_BASE_GAPS[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2077:0"}
AUXILIARY_RECORD_MAP = {
    2072: 2048,
    2073: 2049,
    2074: 2050,
    2078: 2054,
}
AUXILIARY_OVERRIDES = {
    (side, language, record_id): canonical_module(canonical_id).AUXILIARY_OVERRIDES[
        (side, language, canonical_id)
    ]
    for record_id, canonical_id in AUXILIARY_RECORD_MAP.items()
    for side, language, source_id in canonical_module(
        canonical_id
    ).AUXILIARY_OVERRIDES
    if source_id == canonical_id
}
BASIS = (
    "review_queue_base_msggame_B115_C_pristine_base_pc_jp_authoritative_"
    "wartime_dynamic_action_policy_proposals_exactly_reusing_final_B_"
    "canonical_Korean_source_gap_and_auxiliary_tuples_with_explicit_"
    "base2071_2081_to_pk2101_2111_mapping_dynamic_action_token_direction_"
    "war_attack_and_capture_distinctions_preserved_current_korean_"
    "morphology_terminal_corpora_hidden_lf_excluded_project_ellipsis_pair_"
    "current_line_counts_and_protected_skeleton_preserved_runtime_fragment_"
    "pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    142: CANONICAL_B0.EXPECTED_BASE_MORPHOLOGY_TERMINALS[142],
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    142: CANONICAL_B0.EXPECTED_PK_MORPHOLOGY_TERMINALS[142],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items():
        module = canonical_module(canonical_id)
        if (
            TRANSLATIONS_BY_RECORD[record_id]
            is not module.TRANSLATIONS_BY_RECORD[canonical_id]
        ):
            raise RuntimeError(
                f"segment 963 canonical Korean tuple alias drifted: {record_id}"
            )
        source = source_records[(15, record_id)]
        canonical = source_records[(15, canonical_id)]
        if (
            tuple(x.text for x in ENGINE.parse_record_literals(source))
            != tuple(x.text for x in ENGINE.parse_record_literals(canonical))
            or COMMON.UTIL.record_gaps(source)
            != COMMON.UTIL.record_gaps(canonical)
        ):
            raise RuntimeError(
                f"segment 963 live exact-source reuse drifted: "
                f"{canonical_id}/{record_id}"
            )
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 963 Base-to-PK mapping drifted")
    if (
        EXPECTED_BASE_JP != EXPECTED_PK_JP
        or EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS
        or EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS
    ):
        raise RuntimeError("segment 963 exact source/gap mapping drifted")
    if any(
        sum(gap.count(ACTION_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 963 action-token cardinality drifted")
    if (
        raw_translations["15:2077:0"].count("…") != 1
        or translations["15:2077:0"].count("…") != 2
    ):
        raise RuntimeError("segment 963 project ellipsis pair drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 963 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 963 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 963 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S963",
                "source_literal_count": 26,
                "decision_count": len(rows),
                "hidden_non_display_count": 4,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "runtime_fragment_pending": len(rows),
                "canonical_record_map": CANONICAL_RECORD_MAP,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": {
                    line_count: sum(
                        text.count("\n") + 1 == line_count
                        for text in translations.values()
                    )
                    for line_count in (1, 2, 3)
                },
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
