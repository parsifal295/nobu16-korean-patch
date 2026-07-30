#!/usr/bin/env python3
"""Build Base authoring segment 927 decisions for the v0.15.0 retranslation."""

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
    / "base_msggame_B001_S927.private.v1.jsonl"
)
SEGMENT = 927
LUCK_FAILURE_TRANSLATION = (
    CANONICAL_S926.PROPOSAL_FAILURE_PREFIX,
    (
        '" 제안은\n'
        "운마저 따르지 않아 실패로 끝났습니다\n"
        "좋은 기회라고 생각했습니다만…"
    ),
)
CANONICAL_TRANSLATIONS_BY_RECORD = {
    record_id: LUCK_FAILURE_TRANSLATION
    for record_id in range(1692, 1704)
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    record_id: 2
    for record_id in range(1692, 1704)
}
LUCK_FAILURE_JP = (
    "申し訳ありません、先日の「",
    "」の案は\n運にも見放され、失敗に終わりました\n好機だと思ったのですが…",
)
EXPECTED_BASE_JP = {
    record_id: LUCK_FAILURE_JP
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
    1692: 1722,
    1693: 1723,
    1694: 1724,
    1695: 1725,
    1696: 1726,
    1697: 1727,
    1698: 1728,
    1699: 1729,
    1700: 1730,
    1701: 1731,
    1702: 1732,
    1703: 1733,
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
    "review_queue_base_msggame_B111_C_pristine_base_pc_jp_authoritative_"
    "proposal_failure_abandoned_by_luck_canonical_group_with_explicit_base_"
    "1692_1703_to_pk1722_1733_mapping_exact_blank_base_pk_sc_tc_and_pk_en_"
    "auxiliary_context_dynamic_proposal_name_023c_token_direction_ascii_"
    "quotation_marks_shared_apology_prefix_polite_regret_register_exact_"
    "tuple_object_reuse_project_ellipsis_pair_current_line_counts_and_"
    "protected_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if any(
        translation_tuple is not LUCK_FAILURE_TRANSLATION
        for translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.values()
    ):
        raise RuntimeError("segment 927 Korean canonical tuple object split")
    if any(
        source_tuple is not LUCK_FAILURE_JP
        for source_tuple in EXPECTED_BASE_JP.values()
    ):
        raise RuntimeError("segment 927 JP canonical tuple object split")
    for record_id in RECORD_ARITIES:
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != LUCK_FAILURE_JP:
            raise RuntimeError(
                f"segment 927 pristine canonical source drifted: {record_id}"
            )
        actual_translation = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual_translation != LUCK_FAILURE_TRANSLATION:
            raise RuntimeError(
                f"segment 927 Korean canonical reuse drifted: {record_id}"
            )
    if set(PK_RECORD_MAP.items()) != {
        (1692, 1722),
        (1693, 1723),
        (1694, 1724),
        (1695, 1725),
        (1696, 1726),
        (1697, 1727),
        (1698, 1728),
        (1699, 1729),
        (1700, 1730),
        (1701, 1731),
        (1702, 1732),
        (1703, 1733),
    }:
        raise RuntimeError("segment 927 explicit Base-to-PK mapping drifted")
    if LUCK_FAILURE_TRANSLATION[0] is not (
        CANONICAL_S926.PROPOSAL_FAILURE_PREFIX
    ):
        raise RuntimeError("segment 927 shared apology prefix object drifted")
    if not LUCK_FAILURE_TRANSLATION[1].endswith(
        "좋은 기회라고 생각했습니다만…"
    ):
        raise RuntimeError("segment 927 polite regret register drifted")
    joined = "\n".join(translations.values())
    for required in ("죄송합니다", "제안", "운마저", "실패", "좋은 기회"):
        if required not in joined:
            raise RuntimeError(f"segment 927 required meaning drifted: {required}")
    for forbidden in ("「", "」", "。", "、", "호기라고"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 927 retained forbidden phrasing: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 927 ellipsis seed/pair drifted: {coordinate}"
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
        raise RuntimeError("segment 927 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 927 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 927 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S927",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "canonical_group_size": len(RECORD_ARITIES),
                "canonical_tuple_object_reused": True,
                "shared_apology_prefix_object_reused": True,
                "explicit_pk_mapping": True,
                "base_pk_jp_exception_records": [],
                "auxiliary_records_blank": len(RECORD_ARITIES),
                "dynamic_proposal_name_token": "023c",
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
