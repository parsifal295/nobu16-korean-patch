#!/usr/bin/env python3
"""Build Base authoring segment 928 decisions for the v0.15.0 retranslation."""

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
    / "base_msggame_B001_S928.private.v1.jsonl"
)
SEGMENT = 928
POLITICS_FAILURE_TRANSLATION = (
    CANONICAL_S926.PROPOSAL_FAILURE_PREFIX,
    (
        '" 제안은\n'
        "예상만큼 일이 진척되지 않아 실패했습니다\n"
        "정무에는 자신이 있었습니다만…"
    ),
)
TACTICS_FAILURE_TRANSLATION = (
    CANONICAL_S926.PROPOSAL_FAILURE_PREFIX,
    (
        '" 제안은\n'
        "병사들과 뜻대로 호흡을 맞추지 못해 실패했습니다\n"
        "이래서는 싸움에 능하다는 이름을 내려놓아야겠군요…"
    ),
)
CANONICAL_TRANSLATIONS_BY_RECORD = {
    **{
        record_id: POLITICS_FAILURE_TRANSLATION
        for record_id in range(1704, 1716)
    },
    **{
        record_id: TACTICS_FAILURE_TRANSLATION
        for record_id in range(1716, 1718)
    },
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    record_id: 2
    for record_id in range(1704, 1718)
}
POLITICS_FAILURE_JP = (
    "申し訳ありません、先日の「",
    "」の案は\n想定よりも作業が進まず、失敗しました\n政には自信があったのですが…",
)
TACTICS_FAILURE_JP = (
    "申し訳ありません、先日の「",
    (
        "」の案は\n思うように兵と連携が取れず、失敗しました\n"
        "これでは戦上手を返上せねば、なりませぬな…"
    ),
)
EXPECTED_BASE_JP = {
    **{
        record_id: POLITICS_FAILURE_JP
        for record_id in range(1704, 1716)
    },
    **{
        record_id: TACTICS_FAILURE_JP
        for record_id in range(1716, 1718)
    },
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: ("", "023c", "050505")
    for record_id in RECORD_ARITIES
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {
    1704: 1734,
    1705: 1735,
    1706: 1736,
    1707: 1737,
    1708: 1738,
    1709: 1739,
    1710: 1740,
    1711: 1741,
    1712: 1742,
    1713: 1743,
    1714: 1744,
    1715: 1745,
    1716: 1746,
    1717: 1747,
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
    "proposal_failure_politics_work_progress_and_soldier_coordination_"
    "tactician_reputation_canonical_groups_with_explicit_base1704_1717_to_"
    "pk1734_1747_mapping_exact_blank_base_pk_sc_tc_and_pk_en_auxiliary_"
    "context_dynamic_proposal_name_023c_token_direction_ascii_quotation_"
    "marks_shared_apology_prefix_distinct_polite_politics_and_self_deprecating_"
    "military_registers_exact_tuple_object_reuse_project_ellipsis_pair_"
    "current_line_counts_and_protected_skeleton_preserved_runtime_fragment_"
    "pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(1704, 1716):
        if (
            CANONICAL_TRANSLATIONS_BY_RECORD[record_id]
            is not POLITICS_FAILURE_TRANSLATION
            or EXPECTED_BASE_JP[record_id] is not POLITICS_FAILURE_JP
        ):
            raise RuntimeError(
                f"segment 928 politics canonical tuple object split: {record_id}"
            )
    for record_id in range(1716, 1718):
        if (
            CANONICAL_TRANSLATIONS_BY_RECORD[record_id]
            is not TACTICS_FAILURE_TRANSLATION
            or EXPECTED_BASE_JP[record_id] is not TACTICS_FAILURE_JP
        ):
            raise RuntimeError(
                f"segment 928 tactics canonical tuple object split: {record_id}"
            )
    for record_id in RECORD_ARITIES:
        expected_source = (
            POLITICS_FAILURE_JP
            if record_id <= 1715
            else TACTICS_FAILURE_JP
        )
        expected_translation = (
            POLITICS_FAILURE_TRANSLATION
            if record_id <= 1715
            else TACTICS_FAILURE_TRANSLATION
        )
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != expected_source:
            raise RuntimeError(
                f"segment 928 pristine canonical source drifted: {record_id}"
            )
        actual_translation = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual_translation != expected_translation:
            raise RuntimeError(
                f"segment 928 Korean canonical reuse drifted: {record_id}"
            )
    if set(PK_RECORD_MAP.items()) != {
        (1704, 1734),
        (1705, 1735),
        (1706, 1736),
        (1707, 1737),
        (1708, 1738),
        (1709, 1739),
        (1710, 1740),
        (1711, 1741),
        (1712, 1742),
        (1713, 1743),
        (1714, 1744),
        (1715, 1745),
        (1716, 1746),
        (1717, 1747),
    }:
        raise RuntimeError("segment 928 explicit Base-to-PK mapping drifted")
    if (
        POLITICS_FAILURE_TRANSLATION[0]
        is not CANONICAL_S926.PROPOSAL_FAILURE_PREFIX
        or TACTICS_FAILURE_TRANSLATION[0]
        is not CANONICAL_S926.PROPOSAL_FAILURE_PREFIX
    ):
        raise RuntimeError("segment 928 shared apology prefix object drifted")
    if not POLITICS_FAILURE_TRANSLATION[1].endswith(
        "정무에는 자신이 있었습니다만…"
    ):
        raise RuntimeError("segment 928 politics speaker register drifted")
    if not TACTICS_FAILURE_TRANSLATION[1].endswith(
        "싸움에 능하다는 이름을 내려놓아야겠군요…"
    ):
        raise RuntimeError("segment 928 military speaker register drifted")
    joined = "\n".join(translations.values())
    for required in (
        "죄송합니다",
        "제안",
        "진척",
        "정무",
        "병사들",
        "호흡을 맞추지 못해",
        "싸움에 능하다는 이름",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 928 required meaning drifted: {required}")
    for forbidden in (
        "「",
        "」",
        "。",
        "、",
        "작업이 진척",
        "싸움 잘한다는 말",
        "전술가",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 928 retained forbidden phrasing: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 928 ellipsis seed/pair drifted: {coordinate}"
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
    if len(rows) != 28 or len(translations) != 28:
        raise RuntimeError("segment 928 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 928 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 928 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S928",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "politics_canonical_group_size": 12,
                "tactics_canonical_group_size": 2,
                "canonical_tuple_objects_reused": True,
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
