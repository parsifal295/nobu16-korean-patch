#!/usr/bin/env python3
"""Build Base authoring segment 985 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment984 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S985.private.v1.jsonl"
)
SEGMENT = 985
CASTLE_GOAL_TRANSLATION = PREVIOUS.CASTLE_GOAL_TRANSLATION
RETAINER_GOAL_TRANSLATION = (
    "우리 가문의 목표로\n휘하 가신의 수를 늘리자고\n내거는 것은",
)
POLICY_GOAL_TRANSLATION = (
    "우리 가문의 목표로\n더 많고 강력한 정책을 발령하자고\n내거는 것은",
)
FACILITY_GOAL_TRANSLATION = (
    "우리 가문의 목표로\n영내 성하에 더 많은\n시설을 건설하자고 내거는 것은",
)
KOKUDAKA_GOAL_TRANSLATION = (
    "우리 가문의 목표로 석고 증대를 내걸고\n"
    "영내 개간을 장려하여\n"
    "국력을 키우는 것은",
)
COMMERCE_GOAL_TRANSLATION = (
    "우리 가문의 목표로 상업 진흥을 내걸고\n"
    "영내 상업을 장려하여\n"
    "국력을 키우는 것은",
)
TRANSLATIONS_BY_RECORD = {
    2309: CASTLE_GOAL_TRANSLATION,
    2310: CASTLE_GOAL_TRANSLATION,
    2311: RETAINER_GOAL_TRANSLATION,
    2312: RETAINER_GOAL_TRANSLATION,
    2313: RETAINER_GOAL_TRANSLATION,
    2314: POLICY_GOAL_TRANSLATION,
    2315: POLICY_GOAL_TRANSLATION,
    2316: POLICY_GOAL_TRANSLATION,
    2317: FACILITY_GOAL_TRANSLATION,
    2318: FACILITY_GOAL_TRANSLATION,
    2319: FACILITY_GOAL_TRANSLATION,
    2320: KOKUDAKA_GOAL_TRANSLATION,
    2321: KOKUDAKA_GOAL_TRANSLATION,
    2322: KOKUDAKA_GOAL_TRANSLATION,
    2323: COMMERCE_GOAL_TRANSLATION,
    2324: COMMERCE_GOAL_TRANSLATION,
    2325: COMMERCE_GOAL_TRANSLATION,
    2326: (
        "우리 가문의 목표로\n공략 목표로 정한 적성을 제압하자고\n내거는 것은",
    ),
    2327: (
        "우리 가문의 목표로\n합전에서 승리하자고\n내거는 것은",
    ),
    2328: (
        "막연히 판도를 넓히기보다는\n"
        "목표 수치를 모두에게 명시하여\n"
        "사기를 높이는 것이 상책일 듯합니다",
    ),
    2329: (
        "가신의 수는 곧 가문의 힘\n"
        "온갖 방도를 써서 휘하 인원을 늘리고\n"
        "다른 가문보다 앞서야 합니다",
    ),
    2330: (
        "영내 전체를 풍요롭고 강하게 하려면\n"
        "정책 발령이야말로 정도…\n"
        "그 목표치를 가신단에 제시하는 것이 좋겠습니다",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:0": translations[0]
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
RECORD_ARITIES = {record_id: 1 for record_id in TRANSLATIONS_BY_RECORD}
CASTLE_GOAL_JP = PREVIOUS.EXPECTED_BASE_JP[2308]
RETAINER_GOAL_JP = ("当家の目標として\n配下である家臣の人数増を\n掲げてみては",)
POLICY_GOAL_JP = ("当家の目標として\nより多く、強力な政策の発令を\n掲げては",)
FACILITY_GOAL_JP = ("当家の目標として\n領国の城下にて、より多くの\n施設を建設しては",)
KOKUDAKA_GOAL_JP = ("当家の目標に石高向上を掲げ\n領国における開墾を奨励し\n国力を高めては",)
COMMERCE_GOAL_JP = ("当家の目標に商業向上を掲げ\n領国における商いを奨励し\n国力を高めては",)
EXPECTED_BASE_JP = {
    2309: CASTLE_GOAL_JP,
    2310: CASTLE_GOAL_JP,
    2311: RETAINER_GOAL_JP,
    2312: RETAINER_GOAL_JP,
    2313: RETAINER_GOAL_JP,
    2314: POLICY_GOAL_JP,
    2315: POLICY_GOAL_JP,
    2316: POLICY_GOAL_JP,
    2317: FACILITY_GOAL_JP,
    2318: FACILITY_GOAL_JP,
    2319: FACILITY_GOAL_JP,
    2320: KOKUDAKA_GOAL_JP,
    2321: KOKUDAKA_GOAL_JP,
    2322: KOKUDAKA_GOAL_JP,
    2323: COMMERCE_GOAL_JP,
    2324: COMMERCE_GOAL_JP,
    2325: COMMERCE_GOAL_JP,
    2326: ("当家の目標として\n攻略目標と定めた敵城の制圧を\n掲げては",),
    2327: ("当家の目標として\n合戦における勝利を\n掲げては",),
    2328: ("漫然と版図を広げるのではなく\n目処となる数を皆に指示し\n意気を高めるのが上策かと",),
    2329: ("家臣の人数は、即ち家の強さ\n手を尽くして配下の人数を増やし\n他家に先駆けては",),
    2330: ("領国全てを富ませ、強化するには\n政策の発令こそが常道…\nその目安を家中に示しては",),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
GOAL_BASE_GAPS = PREVIOUS.EXPECTED_BASE_GAPS[2308]
GOAL_PK_GAPS = PREVIOUS.EXPECTED_PK_JP_GAPS[2308]
EXPECTED_BASE_GAPS = {
    **{record_id: GOAL_BASE_GAPS for record_id in range(2309, 2328)},
    **{record_id: ("", "050505") for record_id in range(2328, 2331)},
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **{record_id: GOAL_PK_GAPS for record_id in range(2309, 2328)},
    **{record_id: ("", "050505") for record_id in range(2328, 2331)},
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2330:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

CASTLE_SC = PREVIOUS.SHARED_AUXILIARY[("SC", 2308)]
CASTLE_TC = PREVIOUS.SHARED_AUXILIARY[("TC", 2308)]
CASTLE_EN = PREVIOUS.PK_EN_AUXILIARY[2308]
RETAINER_SC = (
    ("将麾下家臣的数量增加，\n作为本家的目标，\n公布于众如何？",),
    ("", "050505"),
)
RETAINER_TC = (
    ("以增加麾下家臣人數\n作為本家的目標如何？ ",),
    ("", "050505"),
)
RETAINER_EN = (
    (
        "What do you think of setting a goal of increasing the number of "
        "retainers bound to our clan?",
    ),
    ("", "050505"),
)
POLICY_SC = (
    ("将更多强大的政策颁布，\n作为本家的目标，\n公布于众如何？",),
    ("", "050505"),
)
POLICY_TC = (
    ("以頒布更多強大政策\n作為本家目標如何？ ",),
    ("", "050505"),
)
POLICY_EN = (
    ("What do you think of setting a goal of issuing more and stronger policies?",),
    ("", "050505"),
)
FACILITY_SC = (
    ("在领土内的城下，\n建设更多的设施\n作为本家的目标如何？",),
    ("", "050505"),
)
FACILITY_TC = (
    ("作為本家的目標，\n在領土內的城下\n建設更多的設施如何？ ",),
    ("", "050505"),
)
FACILITY_EN = (
    (
        "What do you think of setting a goal of adding more facilities to our "
        "territoryÖs castle towns?",
    ),
    ("", "050505"),
)
KOKUDAKA_SC = (
    ("将提升石高作为本家的目标，\n奖励在领土内开荒，\n从而提升国力如何？",),
    ("", "050505"),
)
KOKUDAKA_TC = (
    ("將提升石高作為本家的目標，\n獎勵在領土內開荒，\n從而提升國力如何？",),
    ("", "050505"),
)
KOKUDAKA_EN = (
    (
        "What do you think of setting a goal of increasing our crops by "
        "encouraging new cultivation throughout the territory?",
    ),
    ("", "050505"),
)
COMMERCE_SC = (
    ("将提升商业作为本家的目标，\n奖励在领土内行商，\n从而提升国力如何？",),
    ("", "050505"),
)
COMMERCE_TC = (
    ("將提升商業作為本家的目標，\n獎勵在領土內行商，\n從而提升國力如何？",),
    ("", "050505"),
)
COMMERCE_EN = (
    (
        "What do you think of setting a goal of increasing commerce by "
        "encouraging trade throughout the territory?",
    ),
    ("", "050505"),
)
SHARED_AUXILIARY = {
    **{
        (language, record_id): expected
        for language, expected in (("SC", CASTLE_SC), ("TC", CASTLE_TC))
        for record_id in (2309, 2310)
    },
    **{
        (language, record_id): expected
        for language, expected in (("SC", RETAINER_SC), ("TC", RETAINER_TC))
        for record_id in (2311, 2312, 2313)
    },
    **{
        (language, record_id): expected
        for language, expected in (("SC", POLICY_SC), ("TC", POLICY_TC))
        for record_id in (2314, 2315, 2316)
    },
    **{
        (language, record_id): expected
        for language, expected in (("SC", FACILITY_SC), ("TC", FACILITY_TC))
        for record_id in (2317, 2318, 2319)
    },
    **{
        (language, record_id): expected
        for language, expected in (("SC", KOKUDAKA_SC), ("TC", KOKUDAKA_TC))
        for record_id in (2320, 2321, 2322)
    },
    **{
        (language, record_id): expected
        for language, expected in (("SC", COMMERCE_SC), ("TC", COMMERCE_TC))
        for record_id in (2323, 2324, 2325)
    },
    ("SC", 2326): (
        ("将压制目标敌城之事，\n作为本家的目标\n公布于众如何？",),
        ("", "050505"),
    ),
    ("TC", 2326): (
        ("以壓制攻略目標的敵城\n作為本家的目標如何？ ",),
        ("", "050505"),
    ),
    ("SC", 2327): (
        ("将多次会战取胜之事，\n作为本家的目标\n公布于众如何？",),
        ("", "050505"),
    ),
    ("TC", 2327): (
        ("以於會戰中取勝\n作為本家的目標如何？ ",),
        ("", "050505"),
    ),
    ("SC", 2328): (
        ("肆意扩大领土并不是一个好选择，\n应向众人明示目标的数量，\n鼓舞军心才为上策。",),
        ("", "050505"),
    ),
    ("TC", 2328): (
        ("我認為不宜漫無目標地擴大領土，\n理應向眾人明示目標的數目\n以振奮士氣。",),
        ("", "050505"),
    ),
    ("SC", 2329): (
        ("家臣的人数关系到势力的强弱，\n得用尽一切手段，抢在其他势力之前，\n增加人才。",),
        ("", "050505"),
    ),
    ("TC", 2329): (
        ("家臣人數等同於家的實力。\n務必極力設法增加麾下的人數，\n領先於其他家之前。",),
        ("", "050505"),
    ),
    ("SC", 2330): (
        ("若想让全国走向富裕，变得更强大，\n常见手段便是发布政策……\n就让以此为目标行动吧。",),
        ("", "050505"),
    ),
    ("TC", 2330): (
        ("若想讓所有的領國富強，\n頒布政策是有效的手段……\n向家中指示達成目標。",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    **{record_id: CASTLE_EN for record_id in (2309, 2310)},
    **{record_id: RETAINER_EN for record_id in (2311, 2312, 2313)},
    **{record_id: POLICY_EN for record_id in (2314, 2315, 2316)},
    **{record_id: FACILITY_EN for record_id in (2317, 2318, 2319)},
    **{record_id: KOKUDAKA_EN for record_id in (2320, 2321, 2322)},
    **{record_id: COMMERCE_EN for record_id in (2323, 2324, 2325)},
    2326: (
        (
            "What do you think of setting a goal of increasing the number of "
            "targeted enemy castles we occupy?",
        ),
        ("", "050505"),
    ),
    2327: (
        (
            "What do you think of setting a goal of increasing the number of "
            "victories we achieve in battle?",
        ),
        ("", "050505"),
    ),
    2328: (
        (
            "Instead of haphazardly expanding our domain, I think setting a "
            "clear target to boost morale would serve us better.",
        ),
        ("", "050505"),
    ),
    2329: (
        (
            "The strength of a clan lies in the number of its retainers. We "
            "must use every means to increase our personnel and keep ahead of "
            "the other clans.",
        ),
        ("", "050505"),
    ),
    2330: (
        (
            "It is only proper that we issue policies to enrich and strengthen "
            "our domain. That goal should be communicated to all within our clan.",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B118_A_pristine_base_pc_jp_authoritative_"
    "clan_goal_proposals_castles_retainers_policies_castle_town_"
    "facilities_kokudaka_cultivation_commerce_enemy_castle_control_and_"
    "battle_victories_plus_domain_morale_and_household_counsel_with_"
    "explicit_base2309_2330_to_pk2340_2361_plus31_mapping_exact_base_pk_"
    "jp_sc_tc_literals_actual_pk_en_auxiliary_context_kotobank_toke_"
    "kachuu_hanto_kokudaka_dictionary_and_historical_encyclopedia_"
    "meanings_project_gasin-dan_yeongnae_pando_seokgo_terms_s984_2308_"
    "through_2310_and_five_internal_triples_source_gap_korean_tuple_"
    "canonical_object_identity_actual_morphology_terminal_corpora_"
    "current_line_counts_ellipsis_pair_and_protected_skeleton_preserved_"
    "runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
}
EXACT_GROUPS = (
    (2309, 2310),
    (2311, 2312, 2313),
    (2314, 2315, 2316),
    (2317, 2318, 2319),
    (2320, 2321, 2322),
    (2323, 2324, 2325),
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 985 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 985 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != set(range(2309, 2328)):
        raise RuntimeError("segment 985 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 985 pristine/current gap drifted")
    if (
        PREVIOUS.EXPECTED_BASE_JP[2308] != EXPECTED_BASE_JP[2309]
        or EXPECTED_BASE_JP[2309] != EXPECTED_BASE_JP[2310]
        or PREVIOUS.EXPECTED_BASE_GAPS[2308] != EXPECTED_BASE_GAPS[2309]
        or EXPECTED_BASE_GAPS[2309] != EXPECTED_BASE_GAPS[2310]
        or PREVIOUS.EXPECTED_PK_JP_GAPS[2308] != EXPECTED_PK_JP_GAPS[2309]
        or EXPECTED_PK_JP_GAPS[2309] != EXPECTED_PK_JP_GAPS[2310]
    ):
        raise RuntimeError("segment 985 cross-boundary 2308-2310 source/gap exact drifted")
    if (
        PREVIOUS.TRANSLATIONS_BY_RECORD[2308] is not TRANSLATIONS_BY_RECORD[2309]
        or TRANSLATIONS_BY_RECORD[2309] is not TRANSLATIONS_BY_RECORD[2310]
    ):
        raise RuntimeError("segment 985 cross-boundary castle Korean tuple identity drifted")
    for group in EXACT_GROUPS:
        canonical = group[0]
        if any(
            EXPECTED_BASE_JP[record_id] != EXPECTED_BASE_JP[canonical]
            or EXPECTED_BASE_GAPS[record_id] != EXPECTED_BASE_GAPS[canonical]
            or EXPECTED_PK_JP_GAPS[record_id] != EXPECTED_PK_JP_GAPS[canonical]
            or TRANSLATIONS_BY_RECORD[record_id]
            is not TRANSLATIONS_BY_RECORD[canonical]
            for record_id in group[1:]
        ):
            raise RuntimeError(f"segment 985 exact group drifted: {group}")
    if any(
        SUPPORT.morphology_operands(EXPECTED_BASE_GAPS[record_id][1])
        != (688, 598)
        or SUPPORT.morphology_operands(EXPECTED_PK_JP_GAPS[record_id][1])
        != (700, 610)
        for record_id in range(2309, 2328)
    ):
        raise RuntimeError("segment 985 goal proposal morphology drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "가신",
        "정책",
        "성하",
        "영내",
        "석고",
        "상업 진흥",
        "공략 목표",
        "합전",
        "판도",
        "사기",
        "가신단",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 985 terminology drifted: {required}")
    for forbidden in ("당가", "영국", "의기", "가중", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 985 forbidden wording retained: {forbidden}")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 985 visible decision count drifted")


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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 985 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 985 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S985",
                "source_literal_count": sum(RECORD_ARITIES.values()),
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": list(range(2309, 2328)),
                "pristine_current_gap_divergence_records": [],
                "exact_source_gap_korean_tuple_groups": [
                    [2308, 2309, 2310],
                    *[list(group) for group in EXACT_GROUPS[1:]],
                ],
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": {
                    line_count: sum(
                        text.count("\n") + 1 == line_count
                        for text in translations.values()
                    )
                    for line_count in (1, 2, 3)
                },
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
