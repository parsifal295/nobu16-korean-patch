#!/usr/bin/env python3
"""Build Base authoring segment 959 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment955 as FOUNDATION


ENGINE = FOUNDATION.ENGINE
COMMON = FOUNDATION.COMMON
SUPPORT = FOUNDATION.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S959.private.v1.jsonl"
)
SEGMENT = 959
ACTION_TOKEN = "1B434D023C1B435A"
FORCE_TOKEN = "025032"
CASTLE_TOKEN = "026432"
TRANSLATIONS_BY_RECORD = {
    2033: (
        "와(과)의 싸움을 앞두고\n",
        "을(를) 시행하여\n대비책으로 삼고자 하옵니다",
    ),
    2034: (
        "목표와는 관계없는 일이라 미안하네만\n",
        "의 시행을 허락해 주게",
    ),
    2035: (
        "우리 가문의 지침과는 어긋나지만\n",
        "을(를) 추진하고자 하오",
    ),
    2036: (
        "을(를) 공략할 준비와 병행하여\n",
        "을(를) 시행하고 싶어…",
    ),
    2037: (
        "현재 지침은",
        "을(를) 공격하는 것이나\n이 건의와는 관계가 없어 송구하오나\n",
        "의 시행을 허락해 주시기를 청하옵니다",
    ),
    2038: (
        "을(를) 공격하는 일은 긴요하지만\n",
        "을(를) 또한\n추진해야 할 사안이라 사료되옵니다",
    ),
    2039: (
        "을(를) 공략하는 것만이 전략의 전부는 아니니\n",
        "의 시행도\n검토해 주시오",
    ),
    2040: (
        "현재 목표와는 무관하지만\n",
        "의 시행을\n허락해 주십시오",
    ),
    2041: (
        "을(를) 공격하는 일도 중요하지만\n",
        "에도\n눈을 돌려 보시는 게 어떻겠소?",
    ),
    2042: (
        "을(를) 공격하는 데만 마음 쓰지 마시고\n",
        "에도 부디\n눈을 돌려 주시옵소서",
    ),
    2043: (
        "의 시행을 허락해 주시기를 바라오\n",
        "을(를) 공략하는 일과는 무관하여\n송구하기 그지없으나…",
    ),
}
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
    2033: ("との戦の前に\n", "を行い\n備えとしたく存じます"),
    2034: ("目標とは関係なく申し訳ないが\n", "の許可をくれ"),
    2035: ("当家の指針とは離れるが\n", "を進めたく存ずる"),
    2036: ("攻略準備と並行し\n", "を行いたく…"),
    2037: (
        "指針である",
        "攻めとは\n関係がなく恐縮ですが\n",
        "のご許可を",
    ),
    2038: ("攻めは肝要なれど\n", "もまた\n進めるべき事案かと"),
    2039: ("攻略のみが戦略にあらず\n", "について\n実行をご検討あれ"),
    2040: ("現在の目標とは関係ありませんが\n", "の実行を\nお許しください"),
    2041: ("攻めも重要なれど\n", "にも\n目を向けられてはいかがか"),
    2042: ("攻めのみに心砕かず\n", "にもまた\n目をお向けくださいませ"),
    2043: ("のご許可を\n", "攻略とは関係がなく\n恐縮の限りだが…"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2033: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2034: ("", ACTION_TOKEN, "050505"),
    2035: ("", ACTION_TOKEN, "050505"),
    2036: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2037: ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2038: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2039: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2040: ("", ACTION_TOKEN, "050505"),
    2041: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2042: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2043: (ACTION_TOKEN, CASTLE_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2036:1", "15:2043:1"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2036): (
        ("在准备攻略", "的同时，\n我想进行", "……"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2036): (
        ("於", "攻略準備當下，\n", "盼能並行……"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2037): (
        ("虽然此事与攻打", "\n的指针无关，但恕我冒昧，\n请您同意", "。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2037): (
        ("與攻打", "雖無直接關聯，\n尚請大人批准。"),
        (ACTION_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("SC", 2038): (
        ("攻打", "很关键，\n但", "也是\n应当推进的工作。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2038): (
        ("攻略雖為重中之重，\n", "亦為須行之事。"),
        (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2042): (
        ("请您不要只顾着攻打", "，\n偶尔也关注一下\n", "吧。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2042): (
        ("別僅為", "攻略費盡思量，\n", "同樣需要關心。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2036: (
        (
            "I would like to perform ",
            " as we prepare for the attack on ",
            ".",
        ),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2037: (
        (
            "I apologize that this has no connection with the attack on the ",
            ", but would you consider permitting ",
            "?",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2038: (
        (
            "The attack on the ",
            " is of grave importance, but I must again recommend ",
            ".",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2042: (
        (
            "Instead of exhausting ourselves by focusing solely on capturing ",
            ", would you consider having another look at ",
            "?",
        ),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B115_B_pristine_base_pc_jp_authoritative_"
    "goal_and_guideline_adjacent_peacetime_and_attack_preparation_policy_"
    "proposals_with_explicit_base2033_2043_to_pk2063_2073_mapping_exact_"
    "base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_dynamic_action_"
    "force_and_castle_tokens_direction_our_house_guideline_submission_"
    "terminology_attack_capture_and_war_kept_distinct_project_ellipsis_"
    "pairs_current_line_counts_and_protected_skeleton_preserved_runtime_"
    "fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 959 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 959 Base-to-PK JP literal drifted")
    if (
        EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS
        or EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS
    ):
        raise RuntimeError("segment 959 exact gap mapping drifted")
    if any(
        sum(gap.count(ACTION_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 959 action-token cardinality drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 959 project ellipsis pair drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "지침",
        "건의",
        "청하옵니다",
        "공략",
        "공격",
        "싸움",
        "검토",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 959 required meaning drifted: {required}")
    for forbidden in ("당가", "방침", "을(를) 행하여", "전중"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 959 forbidden phrasing retained: {forbidden}"
            )
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 959 visible decision count drifted")


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
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 959 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 959 runtime/authority classification drifted")
    line_distribution = {
        line_count: sum(
            text.count("\n") + 1 == line_count
            for text in translations.values()
        )
        for line_count in (1, 2, 3)
    }
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S959",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "dynamic_action_policy_token": ACTION_TOKEN,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [],
                "pristine_current_gap_divergence_records": [],
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": line_distribution,
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
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
