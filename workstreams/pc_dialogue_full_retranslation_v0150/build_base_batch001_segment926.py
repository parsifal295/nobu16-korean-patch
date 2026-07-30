#!/usr/bin/env python3
"""Build Base authoring segment 926 decisions for the v0.15.0 retranslation."""

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


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S926.private.v1.jsonl"
)
SEGMENT = 926
PROPOSAL_FAILURE_PREFIX = '죄송합니다. 지난번 "'
UNEXPECTED_EVENT_TRANSLATION = (
    PROPOSAL_FAILURE_PREFIX,
    (
        '" 제안은\n'
        "예기치 못한 일에 가로막혀 실패했습니다\n"
        "다시 기회를 엿보도록 하지요"
    ),
)
CANONICAL_TRANSLATIONS_BY_RECORD = {
    record_id: UNEXPECTED_EVENT_TRANSLATION
    for record_id in range(1680, 1692)
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    record_id: 2
    for record_id in range(1680, 1692)
}
UNEXPECTED_EVENT_JP = (
    "申し訳ありません、先日の「",
    "」の案は\n予期せぬ出来事に阻まれ失敗しました\nまた機を伺うとしましょう",
)
EXPECTED_BASE_JP = {
    record_id: UNEXPECTED_EVENT_JP
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
    1680: 1710,
    1681: 1711,
    1682: 1712,
    1683: 1713,
    1684: 1714,
    1685: 1715,
    1686: 1716,
    1687: 1717,
    1688: 1718,
    1689: 1719,
    1690: 1720,
    1691: 1721,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int],
    tuple[tuple[str, ...], tuple[str, ...]],
] = {}
BASIS = (
    "review_queue_base_msggame_B111_C_pristine_base_pc_jp_authoritative_"
    "proposal_failure_unexpected_event_canonical_group_with_explicit_base_"
    "1680_1691_to_pk1710_1721_mapping_exact_blank_base_pk_sc_tc_and_pk_en_"
    "auxiliary_context_dynamic_proposal_name_023c_token_direction_ascii_"
    "quotation_marks_polite_apology_and_retry_register_exact_tuple_object_"
    "reuse_current_line_counts_and_protected_skeleton_preserved_runtime_"
    "fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if any(
        translation_tuple is not UNEXPECTED_EVENT_TRANSLATION
        for translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.values()
    ):
        raise RuntimeError("segment 926 Korean canonical tuple object split")
    if any(
        source_tuple is not UNEXPECTED_EVENT_JP
        for source_tuple in EXPECTED_BASE_JP.values()
    ):
        raise RuntimeError("segment 926 JP canonical tuple object split")
    for record_id in RECORD_ARITIES:
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != UNEXPECTED_EVENT_JP:
            raise RuntimeError(
                f"segment 926 pristine canonical source drifted: {record_id}"
            )
        actual_translation = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual_translation != UNEXPECTED_EVENT_TRANSLATION:
            raise RuntimeError(
                f"segment 926 Korean canonical reuse drifted: {record_id}"
            )
    if set(PK_RECORD_MAP.items()) != {
        (1680, 1710),
        (1681, 1711),
        (1682, 1712),
        (1683, 1713),
        (1684, 1714),
        (1685, 1715),
        (1686, 1716),
        (1687, 1717),
        (1688, 1718),
        (1689, 1719),
        (1690, 1720),
        (1691, 1721),
    }:
        raise RuntimeError("segment 926 explicit Base-to-PK mapping drifted")
    if any(
        gaps != ("", "023c", "050505")
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 926 proposal-name token direction drifted")
    if UNEXPECTED_EVENT_TRANSLATION[0] != PROPOSAL_FAILURE_PREFIX:
        raise RuntimeError("segment 926 proposal failure prefix drifted")
    if not UNEXPECTED_EVENT_TRANSLATION[1].endswith(
        "다시 기회를 엿보도록 하지요"
    ):
        raise RuntimeError("segment 926 polite retry register drifted")
    joined = "\n".join(translations.values())
    for required in ("죄송합니다", "제안", "예기치 못한 일", "실패", "기회"):
        if required not in joined:
            raise RuntimeError(f"segment 926 required meaning drifted: {required}")
    for forbidden in ("「", "」", "。", "、", "예기치 않은", "」의 안"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 926 retained forbidden phrasing: {forbidden}"
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
        raise RuntimeError("segment 926 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 926 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 926 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S926",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "canonical_group_size": len(RECORD_ARITIES),
                "canonical_tuple_object_reused": True,
                "explicit_pk_mapping": True,
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
