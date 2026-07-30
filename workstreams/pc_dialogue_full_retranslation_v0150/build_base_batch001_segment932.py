#!/usr/bin/env python3
"""Build Base authoring segment 932 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment926 as CANONICAL_S926


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S932.private.v1.jsonl"
)
SEGMENT = 932
NEGOTIATION_BREAKDOWN_TRANSLATION = (
    CANONICAL_S926.PROPOSAL_FAILURE_PREFIX,
    (
        '" 제안은\n'
        "교섭이 결렬되고 말아 실패했습니다\n"
        "제가 자만했던 탓인지 너무 강하게 밀어붙였습니다"
    ),
)
CANONICAL_TRANSLATIONS_BY_RECORD = {
    record_id: NEGOTIATION_BREAKDOWN_TRANSLATION
    for record_id in range(1752, 1761)
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    record_id: 2
    for record_id in range(1752, 1761)
}
NEGOTIATION_BREAKDOWN_JP = (
    "申し訳ありません、先日の「",
    "」の案は\n交渉が決裂してしまい、失敗しました\n私に驕りがあったのか、強く出過ぎました",
)
EXPECTED_BASE_JP = {
    record_id: NEGOTIATION_BREAKDOWN_JP
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: ("", "023c", "050505")
    for record_id in RECORD_ARITIES
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {
    1752: 1782,
    1753: 1783,
    1754: 1784,
    1755: 1785,
    1756: 1786,
    1757: 1787,
    1758: 1788,
    1759: 1789,
    1760: 1790,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int],
    tuple[tuple[str, ...], tuple[str, ...]],
] = {}
BASIS = (
    "review_queue_base_msggame_B112_B_pristine_base_pc_jp_authoritative_"
    "negotiation_breakdown_arrogance_failure_canonical_group_with_explicit_"
    "base1752_1760_to_pk1782_1790_mapping_exact_blank_base_pk_sc_tc_and_"
    "pk_en_auxiliary_context_dynamic_proposal_name_023c_token_direction_"
    "s926_ascii_quote_apology_prefix_exact_object_reuse_polite_self_"
    "criticism_current_line_counts_and_protected_skeleton_preserved_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if any(
        translation_tuple is not NEGOTIATION_BREAKDOWN_TRANSLATION
        for translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.values()
    ):
        raise RuntimeError("segment 932 Korean canonical tuple object split")
    if any(
        source_tuple is not NEGOTIATION_BREAKDOWN_JP
        for source_tuple in EXPECTED_BASE_JP.values()
    ):
        raise RuntimeError("segment 932 JP canonical tuple object split")
    if (
        NEGOTIATION_BREAKDOWN_TRANSLATION[0]
        is not CANONICAL_S926.PROPOSAL_FAILURE_PREFIX
    ):
        raise RuntimeError("segment 932 shared apology prefix object drifted")
    for record_id in RECORD_ARITIES:
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != NEGOTIATION_BREAKDOWN_JP:
            raise RuntimeError(
                f"segment 932 pristine canonical source drifted: {record_id}"
            )
        actual_translation = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual_translation != NEGOTIATION_BREAKDOWN_TRANSLATION:
            raise RuntimeError(
                f"segment 932 Korean canonical reuse drifted: {record_id}"
            )
    if any(
        mapped_id != record_id + 30
        for record_id, mapped_id in PK_RECORD_MAP.items()
    ):
        raise RuntimeError("segment 932 Base-to-PK mapping drifted")
    if any(
        gaps != ("", "023c", "050505")
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 932 proposal-name token direction drifted")
    joined = "\n".join(translations.values())
    for required in (
        "죄송합니다.",
        "제안",
        "교섭",
        "결렬",
        "자만",
        "강하게 밀어붙였습니다",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 932 required meaning drifted: {required}")
    for forbidden in (
        "죄송합니다,",
        "지난번의",
        "「",
        "」",
        "제게 자만이",
        "너무 강하게 나갔습니다",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 932 retained forbidden phrasing: {forbidden}"
            )


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
    if len(rows) != 18 or len(translations) != 18:
        raise RuntimeError("segment 932 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 932 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 932 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S932",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "canonical_group_size": len(RECORD_ARITIES),
                "canonical_tuple_object_reused": True,
                "shared_s926_apology_prefix_object_reused": True,
                "explicit_plus30_pk_mapping": True,
                "base_pk_jp_exception_records": [],
                "auxiliary_records_blank": len(RECORD_ARITIES),
                "dynamic_proposal_name_token": "023c",
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
