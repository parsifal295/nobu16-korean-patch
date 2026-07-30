#!/usr/bin/env python3
"""Build Base authoring segment 961 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment960 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
FOUNDATION = PREVIOUS.FOUNDATION
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S961.private.v1.jsonl"
)
SEGMENT = 961
ACTION_TOKEN = PREVIOUS.ACTION_TOKEN
FORCE_TOKEN = PREVIOUS.PREVIOUS.FORCE_TOKEN
WARTIME_PERMISSION_TRANSLATION = (
    "전시 중이오나 양해해 주시오\n",
    "을(를) 추진하고자 하오",
)
TRANSLATIONS_BY_RECORD = {
    2055: WARTIME_PERMISSION_TRANSLATION,
    2056: PREVIOUS.CIVILIAN_CONSIDERATION_TRANSLATION,
    2057: PREVIOUS.FORMAL_WARTIME_PROPOSAL_TRANSLATION,
    2058: (
        "적은",
        "인가…하지만\n목표로 삼을 성은 정해지지 않았다\n지금은",
        "이라도 시행",
        "?",
    ),
    2059: (
        "을(를) 공격할 때는 아직 한참\n남은 듯하니, 지금은",
        "\n이라도 시행해 둘까?",
    ),
    2060: (
        "적은",
        "이지만 목표로 삼을 성은\n없으니…지금이라면",
        "을(를)\n시험",
        "?",
    ),
    2061: (
        "을(를) 공격하려면 공략 목표의\n결정을",
        ". 하지만\n지금은 우선",
        "을(를) 시행할까…",
    ),
    2062: (
        "이(가) 상대라고는 하나\n지금은 공략 목표로 정한 곳이",
        "\n",
        "에 착수해 보는 건 어떻겠소?",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:2057:1": "\n",
    "15:2062:1": "\n",
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
    2055: ("戦時なれど御免\n", "を進めたく存ずる"),
    2056: ("戦地以外にも人はおりますれば\n", "を具申"),
    2057: ("戦時なれど具申", "\n", "を進めたく存ずる"),
    2058: (
        "敵は",
        "か…だが\n目標の城は決まってない\nここは",
        "でも",
        "か",
    ),
    2059: ("攻めはまだ当分\n先のようだし、今は", "\nでもやっておくか"),
    2060: (
        "敵は",
        "だが目標の城は\nなし、か…今なら",
        "を\n試してみ",
        "か",
    ),
    2061: ("を攻めるなら目標を\n決めて", "が\n今はひとまず", "か…"),
    2062: ("が相手とはいえ\n今は目標も", "\n", "に着手してみては？"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2055: ("", ACTION_TOKEN, "050505"),
    2056: ("", ACTION_TOKEN, "01438E000000050505"),
    2057: ("", "01438E000000", ACTION_TOKEN, "050505"),
    2058: ("", FORCE_TOKEN, ACTION_TOKEN, "0143CC010000", "050505"),
    2059: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2060: ("", FORCE_TOKEN, ACTION_TOKEN, "01433C040000", "050505"),
    2061: (FORCE_TOKEN, "014376030000", ACTION_TOKEN, "050505"),
    2062: (FORCE_TOKEN, "0143DA020000", ACTION_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2058: ("", FORCE_TOKEN, ACTION_TOKEN, "0143D2010000", "050505"),
    2060: ("", FORCE_TOKEN, ACTION_TOKEN, "014348040000", "050505"),
    2061: (FORCE_TOKEN, "014382030000", ACTION_TOKEN, "050505"),
    2062: (FORCE_TOKEN, "0143E6020000", ACTION_TOKEN, "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2058:1",
    "15:2060:1",
    "15:2061:2",
}
SHARED_AUXILIARY = {
    ("SC", 2060): (
        ("敌人是", "，但没有\n目标的城啊……现在\n可以试试", "。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2060): (
        ("敵人為", "卻無目標的城嗎……\n現在不妨試試", "。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2061): (
        ("要攻打", "的话，\n我希望您确定目标，\n但现在要先", "啊……"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2061): (
        ("若欲攻打", "，\n請先決定目標。\n現在姑且", "……"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2062): (
        ("是对手，\n但如今没有目标，\n不如开始", "吧？"),
        (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2062): (
        ("雖為對手，\n目前卻無目標。 \n不妨先著手", "？"),
        (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2060: (
        (
            "Our enemy is the ",
            ", but we have no castles targeted. "
            "Would you consider this a good time to test ",
            "?",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2061: (
        (
            "If we are to attack the ",
            ", I would ask that a target be set. "
            "But perhaps performing ",
            " would be best for now...",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2062: (
        (
            "Even though our opponents are the ",
            ", we have no target. What if we began work on ",
            "?",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)

# The following C range imports these exact-source Korean tuple objects.
CANONICAL_EXACT_TRANSLATIONS = {
    (2046, 2070): PREVIOUS.ROUGH_WARTIME_REQUEST_TRANSLATION,
    (2047, 2057, 2071, 2081): PREVIOUS.FORMAL_WARTIME_PROPOSAL_TRANSLATION,
    (2048, 2072): PREVIOUS.STRATEGY_BEYOND_WAR_PERMISSION_TRANSLATION,
    (2049, 2052, 2073, 2076): PREVIOUS.WARTIME_OPPORTUNITY_TRANSLATION,
    (2050, 2074): PREVIOUS.WARTIME_SUBMISSION_TRANSLATION,
    (2051, 2075): PREVIOUS.POSTWAR_FORESIGHT_TRANSLATION,
    (2053, 2077): PREVIOUS.WARTIME_APOLOGY_TRANSLATION,
    (2054, 2056, 2078, 2080): PREVIOUS.CIVILIAN_CONSIDERATION_TRANSLATION,
    (2055, 2079): WARTIME_PERMISSION_TRANSLATION,
}
BASIS = (
    "review_queue_base_msggame_B115_B_pristine_base_pc_jp_authoritative_"
    "wartime_policy_proposals_and_no_attack_target_interim_action_advice_"
    "with_explicit_base2055_2062_to_pk2085_2092_mapping_exact_base_pk_jp_"
    "sc_tc_and_actual_pk_en_auxiliary_context_dynamic_action_and_force_"
    "tokens_direction_current_korean_morphology_terminal_corpora_base_pk_"
    "opcode_divergences_recorded_hidden_lf_excluded_exact_canonical_groups_"
    "exposed_for_following_c_range_attack_capture_and_war_kept_distinct_"
    "project_ellipsis_pairs_current_line_counts_and_protected_skeleton_"
    "preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    142: ("하겠습니다", "하다", "하겠사옵니다"),
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
    730: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
    886: ("원한다", "받고 싶다"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    142: EXPECTED_BASE_MORPHOLOGY_TERMINALS[142],
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
    742: EXPECTED_BASE_MORPHOLOGY_TERMINALS[730],
    898: EXPECTED_BASE_MORPHOLOGY_TERMINALS[886],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if (
        TRANSLATIONS_BY_RECORD[2055] is not WARTIME_PERMISSION_TRANSLATION
        or TRANSLATIONS_BY_RECORD[2056]
        is not PREVIOUS.CIVILIAN_CONSIDERATION_TRANSLATION
        or TRANSLATIONS_BY_RECORD[2057]
        is not PREVIOUS.FORMAL_WARTIME_PROPOSAL_TRANSLATION
    ):
        raise RuntimeError("segment 961 canonical tuple reuse drifted")
    if (
        EXPECTED_BASE_JP[2056] != PREVIOUS.EXPECTED_BASE_JP[2054]
        or EXPECTED_BASE_GAPS[2056] != PREVIOUS.EXPECTED_BASE_GAPS[2054]
        or EXPECTED_BASE_JP[2057] != PREVIOUS.EXPECTED_BASE_JP[2047]
        or EXPECTED_BASE_GAPS[2057] != PREVIOUS.EXPECTED_BASE_GAPS[2047]
    ):
        raise RuntimeError("segment 961 cross-segment exact source reuse drifted")
    for group, canonical in CANONICAL_EXACT_TRANSLATIONS.items():
        reference_id = group[0]
        reference_literals = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, reference_id)]
            )
        )
        reference_gaps = COMMON.UTIL.record_gaps(
            source_records[(15, reference_id)]
        )
        if len(canonical) != len(reference_literals):
            raise RuntimeError(
                f"segment 961 canonical tuple arity drifted: {group}"
            )
        for record_id in group[1:]:
            actual_literals = tuple(
                literal.text
                for literal in ENGINE.parse_record_literals(
                    source_records[(15, record_id)]
                )
            )
            actual_gaps = COMMON.UTIL.record_gaps(
                source_records[(15, record_id)]
            )
            if (
                actual_literals != reference_literals
                or actual_gaps != reference_gaps
            ):
                raise RuntimeError(
                    f"segment 961 future exact-source group drifted: {group}"
                )
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 961 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 961 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2058, 2060, 2061, 2062}:
        raise RuntimeError("segment 961 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 961 pristine-to-current gap drifted")
    expected_hidden = {
        "15:2057:1": "\n",
        "15:2062:1": "\n",
    }
    if EXCLUDED_NONVISIBLE_COORDINATES != expected_hidden:
        raise RuntimeError("segment 961 hidden LF exclusion drifted")
    if any(
        sum(gap.count(ACTION_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 961 action-token cardinality drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 961 project ellipsis pair drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "전시",
        "건의",
        "공략",
        "공격",
        "목표",
        "시행",
        "시험",
        "착수",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 961 required meaning drifted: {required}")
    for forbidden in ("전중", "여기는", "진행하고자", "공격은 아직"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 961 forbidden phrasing retained: {forbidden}"
            )
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 961 visible decision count drifted")


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
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 961 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 961 runtime/authority classification drifted")
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
                "segment": "base_msggame_B001_S961",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 2,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "dynamic_action_policy_token": ACTION_TOKEN,
                "canonical_exact_groups": {
                    "=".join(map(str, group)): True
                    for group in CANONICAL_EXACT_TRANSLATIONS
                },
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2058, 2060, 2061, 2062],
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
