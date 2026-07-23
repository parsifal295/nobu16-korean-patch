#!/usr/bin/env python3
"""Build Base authoring segment 929 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment928 as CANONICAL_S928


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S929.private.v1.jsonl"
)
SEGMENT = 929
PROPOSAL_TOKEN_SKELETON = ("", "023c", "050505")
TACTICS_FAILURE_TRANSLATION = CANONICAL_S928.TACTICS_FAILURE_TRANSLATION
HIDDEN_INTENT_FAILURE_TRANSLATION = (
    CANONICAL_S926.PROPOSAL_FAILURE_PREFIX,
    (
        '" 제안은\n'
        "숨은 의도가 있다고 의심받았는지 실패했습니다\n"
        "사람의 마음이란 참 알 수 없는 법이군요"
    ),
)
CANONICAL_TRANSLATIONS_BY_RECORD = {
    **{
        record_id: TACTICS_FAILURE_TRANSLATION
        for record_id in range(1718, 1728)
    },
    1728: HIDDEN_INTENT_FAILURE_TRANSLATION,
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    record_id: 2
    for record_id in range(1718, 1729)
}
TACTICS_FAILURE_JP = CANONICAL_S928.TACTICS_FAILURE_JP
HIDDEN_INTENT_FAILURE_JP = (
    "申し訳ありません、先日の「",
    (
        "」の案は\n話に裏があると疑われたのか、失敗しました\n"
        "人の心というものは分からぬものですな"
    ),
)
EXPECTED_BASE_JP = {
    **{
        record_id: TACTICS_FAILURE_JP
        for record_id in range(1718, 1728)
    },
    1728: HIDDEN_INTENT_FAILURE_JP,
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: PROPOSAL_TOKEN_SKELETON
    for record_id in RECORD_ARITIES
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {
    1718: 1748,
    1719: 1749,
    1720: 1750,
    1721: 1751,
    1722: 1752,
    1723: 1753,
    1724: 1754,
    1725: 1755,
    1726: 1756,
    1727: 1757,
    1728: 1758,
}
CURRENT_ELLIPSIS_COORDINATES = {
    f"15:{record_id}:1"
    for record_id in range(1718, 1728)
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int],
    tuple[tuple[str, ...], tuple[str, ...]],
] = {}
BASIS = (
    "review_queue_base_msggame_B112_pristine_base_pc_jp_authoritative_"
    "proposal_failure_tactician_reputation_and_suspected_hidden_intent_"
    "groups_with_explicit_base1718_1728_to_pk1748_1758_plus30_mapping_"
    "exact_base_pk_jp_and_blank_base_pk_sc_tc_pk_en_auxiliary_context_"
    "dynamic_proposal_name_023c_token_direction_no_separate_speaker_suffix_"
    "opcode_s928_tactics_source_translation_and_s926_apology_prefix_exact_"
    "object_reuse_battle_skill_reputation_hidden_intent_and_human_heart_"
    "meaning_polite_self_deprecating_register_project_ellipsis_pair_"
    "current_line_counts_and_protected_skeleton_preserved_runtime_fragment_"
    "pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if TACTICS_FAILURE_TRANSLATION is not (
        CANONICAL_S928.TACTICS_FAILURE_TRANSLATION
    ):
        raise RuntimeError("segment 929 S928 tactics translation object split")
    if TACTICS_FAILURE_JP is not CANONICAL_S928.TACTICS_FAILURE_JP:
        raise RuntimeError("segment 929 S928 tactics source object split")
    for record_id in range(1718, 1728):
        if (
            CANONICAL_TRANSLATIONS_BY_RECORD[record_id]
            is not CANONICAL_S928.TACTICS_FAILURE_TRANSLATION
            or EXPECTED_BASE_JP[record_id]
            is not CANONICAL_S928.TACTICS_FAILURE_JP
        ):
            raise RuntimeError(
                f"segment 929 S928 exact object reuse drifted: {record_id}"
            )
    if CANONICAL_TRANSLATIONS_BY_RECORD[1728] is not (
        HIDDEN_INTENT_FAILURE_TRANSLATION
    ):
        raise RuntimeError("segment 929 hidden-intent translation object split")
    if EXPECTED_BASE_JP[1728] is not HIDDEN_INTENT_FAILURE_JP:
        raise RuntimeError("segment 929 hidden-intent source object split")
    for record_id in RECORD_ARITIES:
        expected_source = (
            TACTICS_FAILURE_JP
            if record_id <= 1727
            else HIDDEN_INTENT_FAILURE_JP
        )
        expected_translation = (
            TACTICS_FAILURE_TRANSLATION
            if record_id <= 1727
            else HIDDEN_INTENT_FAILURE_TRANSLATION
        )
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != expected_source:
            raise RuntimeError(
                f"segment 929 pristine canonical source drifted: {record_id}"
            )
        actual_translation = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual_translation != expected_translation:
            raise RuntimeError(
                f"segment 929 Korean canonical reuse drifted: {record_id}"
            )
    if set(PK_RECORD_MAP.items()) != {
        (1718, 1748),
        (1719, 1749),
        (1720, 1750),
        (1721, 1751),
        (1722, 1752),
        (1723, 1753),
        (1724, 1754),
        (1725, 1755),
        (1726, 1756),
        (1727, 1757),
        (1728, 1758),
    }:
        raise RuntimeError("segment 929 explicit Base-to-PK mapping drifted")
    if any(
        gaps is not PROPOSAL_TOKEN_SKELETON
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 929 Base proposal skeleton object split")
    if (
        set(EXPECTED_BASE_GAPS.values())
        != {PROPOSAL_TOKEN_SKELETON}
        or EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS
        or EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS
    ):
        raise RuntimeError(
            "segment 929 Base/current/PK speaker skeleton variant drifted"
        )
    if (
        TACTICS_FAILURE_TRANSLATION[0]
        is not CANONICAL_S926.PROPOSAL_FAILURE_PREFIX
        or HIDDEN_INTENT_FAILURE_TRANSLATION[0]
        is not CANONICAL_S926.PROPOSAL_FAILURE_PREFIX
    ):
        raise RuntimeError("segment 929 shared apology prefix object drifted")
    if not TACTICS_FAILURE_TRANSLATION[1].endswith(
        "싸움에 능하다는 이름을 내려놓아야겠군요…"
    ):
        raise RuntimeError("segment 929 battle-skill reputation drifted")
    if not HIDDEN_INTENT_FAILURE_TRANSLATION[1].endswith(
        "사람의 마음이란 참 알 수 없는 법이군요"
    ):
        raise RuntimeError("segment 929 hidden-intent speaker register drifted")
    joined = "\n".join(translations.values())
    for required in (
        "죄송합니다",
        "제안",
        "병사들",
        "싸움에 능하다는 이름",
        "숨은 의도",
        "사람의 마음",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 929 required meaning drifted: {required}")
    for forbidden in (
        "「",
        "」",
        "。",
        "、",
        "싸움 잘한다는 말",
        "속셈이 있다 의심",
        "이름을 반납",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 929 retained forbidden phrasing: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 929 ellipsis seed/pair drifted: {coordinate}"
            )
    if any(
        "…" in raw_translations[f"15:1728:{literal_id}"]
        for literal_id in range(2)
    ):
        raise RuntimeError("segment 929 hidden-intent false ellipsis drifted")


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
        raise RuntimeError("segment 929 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 929 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 929 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S929",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "s928_tactics_exact_reuse_records": 10,
                "hidden_intent_records": 1,
                "canonical_tuple_objects_reused": True,
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
