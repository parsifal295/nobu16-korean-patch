#!/usr/bin/env python3
"""Build Base authoring segment 931 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment929 as CANONICAL_S929


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S931.private.v1.jsonl"
)
SEGMENT = 931
SCHEME_DETECTED_FAILURE_TRANSLATION = (
    CANONICAL_S926.PROPOSAL_FAILURE_PREFIX,
    (
        '" 제안은\n'
        "계책을 적에게 간파당하고 말아 실패했습니다\n"
        "제 계책을 꿰뚫어 볼 자가 있다니, 불찰이었습니다…"
    ),
)
CANONICAL_TRANSLATIONS_BY_RECORD = {
    record_id: SCHEME_DETECTED_FAILURE_TRANSLATION
    for record_id in range(1740, 1752)
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    record_id: 2
    for record_id in range(1740, 1752)
}
SCHEME_DETECTED_FAILURE_JP = (
    "申し訳ありません、先日の「",
    (
        "」の案は\n敵の者に看破されてしまい、失敗しました\n"
        "私の策を見破れる者がいるとは不覚…"
    ),
)
EXPECTED_BASE_JP = {
    record_id: SCHEME_DETECTED_FAILURE_JP
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
    1740: 1770,
    1741: 1771,
    1742: 1772,
    1743: 1773,
    1744: 1774,
    1745: 1775,
    1746: 1776,
    1747: 1777,
    1748: 1778,
    1749: 1779,
    1750: 1780,
    1751: 1781,
}
CURRENT_ELLIPSIS_COORDINATES = {
    f"15:{record_id}:1"
    for record_id in RECORD_ARITIES
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int],
    tuple[tuple[str, ...], tuple[str, ...]],
] = {}
BASIS = (
    "review_queue_base_msggame_B112_pristine_base_pc_jp_authoritative_"
    "proposal_failure_scheme_detected_by_enemy_canonical_group_with_"
    "explicit_base1740_1751_to_pk1770_1781_plus30_mapping_exact_base_pk_"
    "jp_and_blank_base_pk_sc_tc_pk_en_auxiliary_context_dynamic_proposal_"
    "name_023c_token_direction_no_separate_speaker_suffix_opcode_s926_"
    "apology_prefix_exact_object_reuse_enemy_detection_scheme_and_"
    "self_reproach_meaning_polite_humble_register_project_ellipsis_pair_"
    "current_line_counts_and_protected_skeleton_preserved_runtime_fragment_"
    "pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if any(
        translation_tuple is not SCHEME_DETECTED_FAILURE_TRANSLATION
        for translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.values()
    ):
        raise RuntimeError("segment 931 Korean canonical tuple object split")
    if any(
        source_tuple is not SCHEME_DETECTED_FAILURE_JP
        for source_tuple in EXPECTED_BASE_JP.values()
    ):
        raise RuntimeError("segment 931 JP canonical tuple object split")
    for record_id in RECORD_ARITIES:
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != SCHEME_DETECTED_FAILURE_JP:
            raise RuntimeError(
                f"segment 931 pristine canonical source drifted: {record_id}"
            )
        actual_translation = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual_translation != SCHEME_DETECTED_FAILURE_TRANSLATION:
            raise RuntimeError(
                f"segment 931 Korean canonical reuse drifted: {record_id}"
            )
    if set(PK_RECORD_MAP.items()) != {
        (1740, 1770),
        (1741, 1771),
        (1742, 1772),
        (1743, 1773),
        (1744, 1774),
        (1745, 1775),
        (1746, 1776),
        (1747, 1777),
        (1748, 1778),
        (1749, 1779),
        (1750, 1780),
        (1751, 1781),
    }:
        raise RuntimeError("segment 931 explicit Base-to-PK mapping drifted")
    if (
        set(EXPECTED_BASE_GAPS.values())
        != {CANONICAL_S929.PROPOSAL_TOKEN_SKELETON}
        or EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS
        or EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS
    ):
        raise RuntimeError(
            "segment 931 Base/current/PK speaker skeleton variant drifted"
        )
    if SCHEME_DETECTED_FAILURE_TRANSLATION[0] is not (
        CANONICAL_S926.PROPOSAL_FAILURE_PREFIX
    ):
        raise RuntimeError("segment 931 shared apology prefix object drifted")
    if not SCHEME_DETECTED_FAILURE_TRANSLATION[1].endswith(
        "제 계책을 꿰뚫어 볼 자가 있다니, 불찰이었습니다…"
    ):
        raise RuntimeError("segment 931 self-reproach speaker register drifted")
    joined = "\n".join(translations.values())
    for required in (
        "죄송합니다",
        "제안",
        "계책",
        "적에게 간파",
        "꿰뚫어 볼 자",
        "불찰",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 931 required meaning drifted: {required}")
    for forbidden in (
        "「",
        "」",
        "。",
        "、",
        "내 책략",
        "간파당하여",
        "자 가",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 931 retained forbidden phrasing: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 931 ellipsis seed/pair drifted: {coordinate}"
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
    if len(rows) != 24 or len(translations) != 24:
        raise RuntimeError("segment 931 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 931 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 931 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S931",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "scheme_detected_canonical_group_size": len(RECORD_ARITIES),
                "canonical_tuple_object_reused": True,
                "shared_apology_prefix_object_reused": True,
                "explicit_plus30_pk_mapping": True,
                "base_pk_jp_exception_records": [],
                "auxiliary_records_blank": len(RECORD_ARITIES),
                "dynamic_proposal_name_token": "023c",
                "separate_speaker_suffix_opcode": False,
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
