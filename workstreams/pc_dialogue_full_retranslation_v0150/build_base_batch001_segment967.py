#!/usr/bin/env python3
"""Build Base authoring segment 967 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment966 as PREVIOUS
import build_base_batch001_segment958 as CANONICAL_A0
import build_base_batch001_segment959 as CANONICAL_A1


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S967.private.v1.jsonl"
)
SEGMENT = 967
ACTION_TOKEN = PREVIOUS.ACTION_TOKEN
CANONICAL_RECORD_MAP = {
    record_id: record_id - 84
    for record_id in range(2116, 2127)
}


def canonical_module(record_id: int) -> Any:
    return CANONICAL_A0 if record_id == 2032 else CANONICAL_A1


TRANSLATIONS_BY_RECORD = {
    record_id: canonical_module(canonical_id).TRANSLATIONS_BY_RECORD[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
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
EXPECTED_PK_JP_GAPS = {
    record_id: canonical_module(canonical_id).EXPECTED_PK_JP_GAPS[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2120:1"}
AUXILIARY_OVERRIDES = {
    (side, language, record_id): expected
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
    for (side, language, source_id), expected
    in canonical_module(canonical_id).AUXILIARY_OVERRIDES.items()
    if source_id == canonical_id
}
# The repeated SC line uses one source ellipsis here rather than two.
for side in ("base", "pk"):
    AUXILIARY_OVERRIDES[(side, "SC", 2120)] = (
        ("在准备攻略", "的同时，\n我想进行", "…"),
        ("", CANONICAL_A1.CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    )
BASIS = (
    "review_queue_base_msggame_B116_A_pristine_base_pc_jp_authoritative_"
    "battle_preparation_goal_guideline_and_dynamic_action_policy_proposals_"
    "exactly_reusing_final_S958_record2032_and_S959_records2033_2042_"
    "canonical_Korean_tuple_objects_with_live_base2116_2126_plus84_exact_"
    "source_assertions_explicit_base_to_pk_plus30_mapping_exact_jp_sc_tc_"
    "literals_and_gaps_actual_auxiliary_context_with_distinct_single_sc_"
    "ellipsis_2120_dynamic_castle_force_and_colour_wrapped_action_tokens_"
    "our_house_guideline_submission_capture_attack_battle_and_action_"
    "execution_implementation_distinctions_project_ellipsis_pair_current_"
    "line_counts_and_protected_skeleton_preserved_runtime_fragment_pending"
)


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
                f"segment 967 canonical Korean tuple alias drifted: {record_id}"
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
                f"segment 967 live +84 exact source reuse drifted: "
                f"{canonical_id}/{record_id}"
            )
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 967 Base-to-PK mapping drifted")
    if (
        EXPECTED_BASE_JP != EXPECTED_PK_JP
        or EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS
        or EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS
    ):
        raise RuntimeError("segment 967 exact source/gap mapping drifted")
    if any(
        sum(gap.count(ACTION_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 967 action-token cardinality drifted")
    if (
        raw_translations["15:2120:1"].count("…") != 1
        or translations["15:2120:1"].count("…") != 2
    ):
        raise RuntimeError("segment 967 project ellipsis pair drifted")
    for side in ("base", "pk"):
        if AUXILIARY_OVERRIDES[(side, "SC", 2120)][0][2] != "…":
            raise RuntimeError("segment 967 distinct SC 2120 ellipsis drifted")
    required_by_coordinate = {
        "15:2116:1": "실행",
        "15:2117:1": "시행",
        "15:2119:1": "추진",
        "15:2121:1": "공격",
        "15:2123:0": "공략",
    }
    for coordinate, required in required_by_coordinate.items():
        if required not in translations[coordinate]:
            raise RuntimeError(
                f"segment 967 terminology drifted: {coordinate}/{required}"
            )
    if any("진행" in translation for translation in translations.values()):
        raise RuntimeError("segment 967 forbidden 진행 wording retained")
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 967 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows_with_current_gaps(
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


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 967 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 967 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S967",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": 0,
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
