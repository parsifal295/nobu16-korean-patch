#!/usr/bin/env python3
"""Build Base authoring segment 960 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment959 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
FOUNDATION = PREVIOUS.FOUNDATION
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S960.private.v1.jsonl"
)
SEGMENT = 960
ACTION_TOKEN = PREVIOUS.ACTION_TOKEN

# Public canonical tuple objects for S961 and the following C range.
ROUGH_WARTIME_REQUEST_TRANSLATION = FOUNDATION.PREVIOUS.TRANSLATIONS_BY_RECORD[1986]
FORMAL_WARTIME_PROPOSAL_TRANSLATION = (
    "전시 중이나 건의",
    "\n",
    "을(를) 추진하고자 하오",
)
STRATEGY_BEYOND_WAR_PERMISSION_TRANSLATION = (
    FOUNDATION.PREVIOUS.TRANSLATIONS_BY_RECORD[1988]
)
WARTIME_OPPORTUNITY_TRANSLATION = FOUNDATION.WARTIME_OPPORTUNITY_TRANSLATION
WARTIME_SUBMISSION_TRANSLATION = FOUNDATION.TRANSLATIONS_BY_RECORD[1990]
POSTWAR_FORESIGHT_TRANSLATION = FOUNDATION.TRANSLATIONS_BY_RECORD[1991]
WARTIME_APOLOGY_TRANSLATION = FOUNDATION.TRANSLATIONS_BY_RECORD[1993]
CIVILIAN_CONSIDERATION_TRANSLATION = (
    "전장 밖에도 백성이 있사오니\n",
    "을(를) 건의",
)

TRANSLATIONS_BY_RECORD = {
    2044: (
        "목표 공략과는 다소 거리가 있사오나\n",
        "을(를) 시행하도록\n허락해 주시겠습니까?",
    ),
    2045: (
        "우리 가문의 목표와는 관계없소만\n",
        "을(를) 시행하도록\n허락해 주시기를 바라옵니다",
    ),
    2046: ROUGH_WARTIME_REQUEST_TRANSLATION,
    2047: FORMAL_WARTIME_PROPOSAL_TRANSLATION,
    2048: STRATEGY_BEYOND_WAR_PERMISSION_TRANSLATION,
    2049: WARTIME_OPPORTUNITY_TRANSLATION,
    2050: WARTIME_SUBMISSION_TRANSLATION,
    2051: POSTWAR_FORESIGHT_TRANSLATION,
    2052: WARTIME_OPPORTUNITY_TRANSLATION,
    2053: WARTIME_APOLOGY_TRANSLATION,
    2054: CIVILIAN_CONSIDERATION_TRANSLATION,
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:2047:1": "\n",
    "15:2049:1": "\n",
    "15:2052:1": "\n",
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
    2044: ("目標の攻略とはやや離れますが\n", "の実行を\nお許し願えませんか？"),
    2045: ("当家の目標とは関係ござらんが\n", "の実行を\nお許し願いたく存じます"),
    2046: ("戦の最中にすまねえ\n", "をやらせてくれ"),
    2047: ("戦時なれど具申", "\n", "を進めたく存ずる"),
    2048: ("戦のみが戦略にあらず\n", "の許可をいただきたい"),
    2049: ("戦にて多忙の折失礼", "\n", "の機と存じます"),
    2050: ("戦の最中なれど御免\n", "を具申"),
    2051: ("現在の戦の先を見据え\n", "を実行しては"),
    2052: ("戦にて多忙の折失礼", "\n", "の機と存じます"),
    2053: ("戦の最中に言うも心苦しいが…\n", "を進めたく存ずる"),
    2054: ("戦地以外にも人はおりますれば\n", "を具申"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2044: ("", ACTION_TOKEN, "050505"),
    2045: ("", ACTION_TOKEN, "050505"),
    2046: ("", ACTION_TOKEN, "050505"),
    2047: ("", "01438E000000", ACTION_TOKEN, "050505"),
    2048: ("", ACTION_TOKEN, "050505"),
    2049: ("", "01438E000000", ACTION_TOKEN, "050505"),
    2050: ("", ACTION_TOKEN, "01438E000000050505"),
    2051: ("", ACTION_TOKEN, "050505"),
    2052: ("", "01438E000000", ACTION_TOKEN, "050505"),
    2053: ("", ACTION_TOKEN, "050505"),
    2054: ("", ACTION_TOKEN, "01438E000000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2053:0"}
SHARED_AUXILIARY = {
    ("SC", 2048): (
        ("战略并不仅限于战争，\n我想请您批准", "。"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("TC", 2048): (
        ("戰略並非僅限於打仗，\n盼大人允准", "。"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("SC", 2049): (
        ("在您忙于战事时打扰您了，\n窃以为现在是", "的良机。"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("TC", 2049): (
        ("戰事繁忙中且容稟告，\n現為", "之機。"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("SC", 2050): (
        ("抱歉在战事中打扰您了，\n容我呈报", "。"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("TC", 2050): (
        ("陣中打擾，望請見諒。\n微臣奏請", "。"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("SC", 2054): (
        ("战地以外也有人在，\n容我呈报", "。"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("TC", 2054): (
        ("戰場之外亦有百姓，\n微臣奏請", "。"),
        ("", ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2048: (
        (
            "War is not won by fighting alone. "
            "I would ask your permission to perform ",
            ".",
        ),
        ("", ACTION_TOKEN, "050505"),
    ),
    2049: (
        (
            "I am sorry to interfere in the midst of battle, "
            "but I believe this may be a good opportunity to perform ",
            ".",
        ),
        ("", ACTION_TOKEN, "050505"),
    ),
    2050: (
        (
            "I apologize for asking in the middle of battle, "
            "but I have a submission for ",
            ".",
        ),
        ("", ACTION_TOKEN, "050505"),
    ),
    2054: (
        (
            "As we also have personnel outside of the battlefield, "
            "I wanted to make a submission for ",
            ".",
        ),
        ("", ACTION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B115_B_pristine_base_pc_jp_authoritative_"
    "goal_adjacent_and_wartime_dynamic_action_policy_proposals_with_"
    "explicit_base2044_2054_to_pk2074_2084_mapping_exact_base_pk_jp_sc_"
    "tc_and_actual_pk_en_auxiliary_context_dynamic_action_token_direction_"
    "current_korean_morphology_terminal_corpus_hidden_lf_excluded_exact_"
    "canonical_groups_exposed_for_following_c_range_our_house_submission_"
    "and_war_register_project_ellipsis_pair_current_line_counts_and_"
    "protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    142: ("하겠습니다", "하다", "하겠사옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    142: EXPECTED_BASE_MORPHOLOGY_TERMINALS[142],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    expected_aliases = {
        2046: FOUNDATION.PREVIOUS.TRANSLATIONS_BY_RECORD[1986],
        2047: FORMAL_WARTIME_PROPOSAL_TRANSLATION,
        2048: FOUNDATION.PREVIOUS.TRANSLATIONS_BY_RECORD[1988],
        2049: FOUNDATION.WARTIME_OPPORTUNITY_TRANSLATION,
        2050: FOUNDATION.TRANSLATIONS_BY_RECORD[1990],
        2051: FOUNDATION.TRANSLATIONS_BY_RECORD[1991],
        2052: FOUNDATION.WARTIME_OPPORTUNITY_TRANSLATION,
        2053: FOUNDATION.TRANSLATIONS_BY_RECORD[1993],
        2054: CIVILIAN_CONSIDERATION_TRANSLATION,
    }
    if any(
        TRANSLATIONS_BY_RECORD[record_id] is not canonical
        for record_id, canonical in expected_aliases.items()
    ):
        raise RuntimeError("segment 960 B114 canonical tuple reuse drifted")
    if (
        TRANSLATIONS_BY_RECORD[2049] is not TRANSLATIONS_BY_RECORD[2052]
        or EXPECTED_BASE_JP[2049] != EXPECTED_BASE_JP[2052]
        or EXPECTED_BASE_GAPS[2049] != EXPECTED_BASE_GAPS[2052]
    ):
        raise RuntimeError("segment 960 Base2049/2052 exact reuse drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 960 Base-to-PK mapping drifted")
    if (
        EXPECTED_BASE_JP != EXPECTED_PK_JP
        or EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS
        or EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS
    ):
        raise RuntimeError("segment 960 exact source/gap mapping drifted")
    expected_hidden = {
        "15:2047:1": "\n",
        "15:2049:1": "\n",
        "15:2052:1": "\n",
    }
    if EXCLUDED_NONVISIBLE_COORDINATES != expected_hidden:
        raise RuntimeError("segment 960 hidden LF exclusion drifted")
    if any(
        sum(gap.count(ACTION_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 960 action-token cardinality drifted")
    if (
        raw_translations["15:2053:0"].count("…") != 1
        or translations["15:2053:0"].count("…") != 2
    ):
        raise RuntimeError("segment 960 project ellipsis pair drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "공략",
        "전시",
        "싸움",
        "건의",
        "백성",
        "있사오니",
        "허락",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 960 required meaning drifted: {required}")
    for forbidden in ("당가", "전중", "진행하고자", "허가"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 960 forbidden phrasing retained: {forbidden}"
            )
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 960 visible decision count drifted")


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
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 960 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 960 runtime/authority classification drifted")
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
                "segment": "base_msggame_B001_S960",
                "source_literal_count": 25,
                "decision_count": len(rows),
                "hidden_non_display_count": 3,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "dynamic_action_policy_token": ACTION_TOKEN,
                "canonical_exact_groups": {
                    "2046=2070": True,
                    "2047=2057=2071=2081": True,
                    "2048=2072": True,
                    "2049=2052=2073=2076": True,
                    "2050=2074": True,
                    "2051=2075": True,
                    "2053=2077": True,
                    "2054=2056=2078=2080": True,
                },
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
