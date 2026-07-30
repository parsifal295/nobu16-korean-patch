#!/usr/bin/env python3
"""Build Base authoring segment 930 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment908 as COMMON
import build_base_batch001_segment929 as CANONICAL_S929


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S930.private.v1.jsonl"
)
SEGMENT = 930
HIDDEN_INTENT_FAILURE_TRANSLATION = (
    CANONICAL_S929.HIDDEN_INTENT_FAILURE_TRANSLATION
)
CANONICAL_TRANSLATIONS_BY_RECORD = {
    record_id: HIDDEN_INTENT_FAILURE_TRANSLATION
    for record_id in range(1729, 1740)
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    record_id: 2
    for record_id in range(1729, 1740)
}
HIDDEN_INTENT_FAILURE_JP = CANONICAL_S929.HIDDEN_INTENT_FAILURE_JP
EXPECTED_BASE_JP = {
    record_id: HIDDEN_INTENT_FAILURE_JP
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: CANONICAL_S929.PROPOSAL_TOKEN_SKELETON
    for record_id in RECORD_ARITIES
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {
    1729: 1759,
    1730: 1760,
    1731: 1761,
    1732: 1762,
    1733: 1763,
    1734: 1764,
    1735: 1765,
    1736: 1766,
    1737: 1767,
    1738: 1768,
    1739: 1769,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int],
    tuple[tuple[str, ...], tuple[str, ...]],
] = {}
BASIS = (
    "review_queue_base_msggame_B112_pristine_base_pc_jp_authoritative_"
    "proposal_failure_suspected_hidden_intent_canonical_group_with_explicit_"
    "base1729_1739_to_pk1759_1769_plus30_mapping_exact_base_pk_jp_and_"
    "blank_base_pk_sc_tc_pk_en_auxiliary_context_dynamic_proposal_name_"
    "023c_token_direction_no_separate_speaker_suffix_opcode_s929_source_"
    "translation_and_s926_apology_prefix_exact_object_reuse_hidden_intent_"
    "and_human_heart_meaning_polite_reflective_register_current_line_counts_"
    "and_protected_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if HIDDEN_INTENT_FAILURE_TRANSLATION is not (
        CANONICAL_S929.HIDDEN_INTENT_FAILURE_TRANSLATION
    ):
        raise RuntimeError("segment 930 S929 translation object split")
    if HIDDEN_INTENT_FAILURE_JP is not (
        CANONICAL_S929.HIDDEN_INTENT_FAILURE_JP
    ):
        raise RuntimeError("segment 930 S929 source object split")
    if any(
        translation_tuple is not HIDDEN_INTENT_FAILURE_TRANSLATION
        for translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.values()
    ):
        raise RuntimeError("segment 930 Korean canonical tuple object split")
    if any(
        source_tuple is not HIDDEN_INTENT_FAILURE_JP
        for source_tuple in EXPECTED_BASE_JP.values()
    ):
        raise RuntimeError("segment 930 JP canonical tuple object split")
    for record_id in RECORD_ARITIES:
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != HIDDEN_INTENT_FAILURE_JP:
            raise RuntimeError(
                f"segment 930 pristine canonical source drifted: {record_id}"
            )
        actual_translation = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual_translation != HIDDEN_INTENT_FAILURE_TRANSLATION:
            raise RuntimeError(
                f"segment 930 Korean canonical reuse drifted: {record_id}"
            )
    if set(PK_RECORD_MAP.items()) != {
        (1729, 1759),
        (1730, 1760),
        (1731, 1761),
        (1732, 1762),
        (1733, 1763),
        (1734, 1764),
        (1735, 1765),
        (1736, 1766),
        (1737, 1767),
        (1738, 1768),
        (1739, 1769),
    }:
        raise RuntimeError("segment 930 explicit Base-to-PK mapping drifted")
    if (
        set(EXPECTED_BASE_GAPS.values())
        != {CANONICAL_S929.PROPOSAL_TOKEN_SKELETON}
        or EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS
        or EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS
    ):
        raise RuntimeError(
            "segment 930 Base/current/PK speaker skeleton variant drifted"
        )
    if not HIDDEN_INTENT_FAILURE_TRANSLATION[1].endswith(
        "사람의 마음이란 참 알 수 없는 법이군요"
    ):
        raise RuntimeError("segment 930 hidden-intent speaker register drifted")
    joined = "\n".join(translations.values())
    for required in (
        "죄송합니다",
        "제안",
        "숨은 의도",
        "의심받았는지",
        "사람의 마음",
        "법이군요",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 930 required meaning drifted: {required}")
    for forbidden in (
        "「",
        "」",
        "。",
        "、",
        "속셈이 있다 의심",
        "간파당해",
        "알 수 없는 것이지요",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 930 retained forbidden phrasing: {forbidden}"
            )
    if any("…" in translation for translation in raw_translations.values()):
        raise RuntimeError("segment 930 false ellipsis drifted")


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
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 22 or len(translations) != 22:
        raise RuntimeError("segment 930 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 930 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 930 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S930",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "hidden_intent_canonical_group_size": len(RECORD_ARITIES),
                "canonical_tuple_objects_reused": True,
                "shared_apology_prefix_object_reused": True,
                "explicit_plus30_pk_mapping": True,
                "base_pk_jp_exception_records": [],
                "auxiliary_records_blank": len(RECORD_ARITIES),
                "dynamic_proposal_name_token": "023c",
                "separate_speaker_suffix_opcode": False,
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
