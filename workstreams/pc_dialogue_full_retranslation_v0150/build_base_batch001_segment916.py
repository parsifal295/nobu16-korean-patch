#!/usr/bin/env python3
"""Build Base authoring segment 916 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment914 as COMMON


ENGINE = COMMON.ENGINE
FRAMEWORK = COMMON.FRAMEWORK
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S916.private.v1.jsonl"
)
SEGMENT = 916
CANONICAL_TRANSLATIONS = {
    1573: COMMON.ENEMY_APPROACH_KO,
    1574: COMMON.OUR_HOLDING_INVASION_KO,
    1575: COMMON.SEIZURE_MARCH_KO,
    1576: COMMON.ARMY_ATTACK_COUNCIL_KO,
    1577: COMMON.UNIT_MARCH_COUNCIL_KO,
    1578: COMMON.INVASION_SORTIE_ORDER_KO,
    1579: COMMON.MARCH_COUNCIL_PREP_KO,
    1580: COMMON.ARMY_SORTIE_COUNCIL_KO,
}
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id, canonical in CANONICAL_TRANSLATIONS.items()
        for literal_id, translation in enumerate(canonical)
    },
    "15:1581:0": "…본의는 아니",
    "15:1581:1": "나\n이번",
    "15:1581:2": "공략은\n중단해야 하",
    "15:1581:3": "…",
    "15:1582:0": (
        "의 공략은 승산이 희박하니\n"
        "헛되이 피해를 키우기 전에\n"
        "철수를 진언하"
    ),
    "15:1583:0": "이제 여기까지…\n",
    "15:1583:1": (
        "의 공략은 가망이 희박하니\n"
        "지금이 철수할 때라 생각하"
    ),
}
RECORD_ARITIES = {
    1573: 2,
    1574: 3,
    1575: 2,
    1576: 2,
    1577: 2,
    1578: 2,
    1579: 2,
    1580: 2,
    1581: 4,
    1582: 1,
    1583: 2,
}
EXPECTED_BASE_JP = {
    1573: COMMON.ENEMY_APPROACH_JP,
    1574: COMMON.OUR_HOLDING_INVASION_JP,
    1575: COMMON.SEIZURE_MARCH_JP,
    1576: COMMON.ARMY_ATTACK_COUNCIL_JP,
    1577: COMMON.UNIT_MARCH_COUNCIL_JP,
    1578: COMMON.INVASION_SORTIE_ORDER_JP,
    1579: COMMON.MARCH_COUNCIL_PREP_JP,
    1580: COMMON.ARMY_SORTIE_COUNCIL_JP,
    1581: (
        "…不本意ではあ",
        "が\n此度の",
        "攻めは\n中断するべき",
        "…",
    ),
    1582: (
        "攻めの勝機は遠く\nいたずらに被害を増す前に\n撤退を進言",
    ),
    1583: (
        "もはやこれまで…\n",
        "攻略の見込みは薄く\n今が潮時かと",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("029632", "025032", "050505")
        for record_id in (1573, 1575, 1576, 1577, 1578, 1579, 1580)
    },
    1574: ("", "029632", "025032", "050505"),
    1581: (
        "",
        "014336040000",
        "026432",
        "01431e010000",
        "050505",
    ),
    1582: ("026432", "01438e000000050505"),
    1583: ("", "026432", "0143e2000000050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1581: (
        "",
        "014342040000",
        "026432",
        "01431e010000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    1573: 1603,
    1574: 1604,
    1575: 1605,
    1576: 1606,
    1577: 1607,
    1578: 1608,
    1579: 1609,
    1580: 1610,
    1581: 1611,
    1582: 1612,
    1583: 1613,
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1581:0",
    "15:1581:3",
    "15:1583:0",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

SHARED_AUXILIARY = {
    ("SC", 1573): (
        (
            "敌对势力正朝着",
            "前进。\n以",
            "做对手真叫人跃跃欲试啊。\n那么，请下令出阵吧！",
        ),
        ("", "029632", "025032", "050505"),
    ),
    ("TC", 1573): (
        (
            "敵對勢力正朝著",
            "前進。\n以",
            "做對手真叫人躍躍欲試啊。\n那麼，請下令出陣吧！",
        ),
        ("", "029632", "025032", "050505"),
    ),
    ("SC", 1577): (
        ("的部队\n正朝着", "进军！\n紧急召开军事会议吧！"),
        ("025032", "029632", "050505"),
    ),
    ("TC", 1577): (
        ("的部隊\n已向", "進軍！\n請緊急召開軍事會議吧！"),
        ("025032", "029632", "050505"),
    ),
    ("SC", 1581): (
        ("……虽然这并非我的本意，\n但此次攻略", "\n需要中断了……"),
        ("", "026432", "050505"),
    ),
    ("TC", 1581): (
        ("……情非得已，\n本次的", "攻略\n或許該中斷……"),
        ("", "026432", "050505"),
    ),
    ("SC", 1582): (
        ("攻下", "的机会遥遥无期。\n在白白增加损失之前，\n还请考虑撤退。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1582): (
        ("攻打", "的制勝機會很小，\n在白白增加損傷之前，\n還請考慮撤退。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1583): (
        ("到此为止了……\n看来攻不下", "，\n该撤退了。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1583): (
        ("到此為止了……\n", "攻略希望渺茫，\n或許該適可而止。"),
        ("", "026432", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1573: (
        (
            "The enemy is marching on ",
            ". The ",
            " are not to be underestimated. We await your orders!",
        ),
        ("", "029632", "025032", "050505"),
    ),
    1577: (
        (
            "The ",
            " has marched for ",
            ". We must hurry and hold a war council!",
        ),
        ("", "025032", "029632", "050505"),
    ),
    1581: (
        (
            "I say this with a heavy heart, but we must pause our attack on ",
            ".",
        ),
        ("", "026432", "050505"),
    ),
    1582: (
        (
            "Our odds of victory at ",
            " are simply too low. We should retreat before we senselessly "
            "incur more wounded.",
        ),
        ("", "026432", "050505"),
    ),
    1583: (
        (
            "Our odds of victory at ",
            " are slim. LetÖs wait for a better moment.",
        ),
        ("", "026432", "050505"),
    ),
}
AUXILIARY_OVERRIDES = COMMON.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B110_pristine_base_pc_jp_authoritative_"
    "county_target_invasion_sortie_war_council_alerts_and_attack_pause_"
    "retreat_proposals_with_content_and_sequence_verified_explicit_base_"
    "to_pk_plus_30_map_exact_base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_"
    "context_exact_cross_record_canonical_reuse_koryak_cheolsu_gunui_"
    "chimgong_shutsujin_hamyeong_terms_shiodoki_as_contextual_time_to_"
    "retreat_live_inflection_stems_current_layout_and_token_skeleton_"
    "preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    explicit_map = {
        1573: 1603,
        1574: 1604,
        1575: 1605,
        1576: 1606,
        1577: 1607,
        1578: 1608,
        1579: 1609,
        1580: 1610,
        1581: 1611,
        1582: 1612,
        1583: 1613,
    }
    if PK_RECORD_MAP != explicit_map:
        raise RuntimeError("segment 916 explicit content-derived PK map drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 916 verified PK offset drifted from +30")

    source_canonicals = {
        1573: COMMON.ENEMY_APPROACH_JP,
        1574: COMMON.OUR_HOLDING_INVASION_JP,
        1575: COMMON.SEIZURE_MARCH_JP,
        1576: COMMON.ARMY_ATTACK_COUNCIL_JP,
        1577: COMMON.UNIT_MARCH_COUNCIL_JP,
        1578: COMMON.INVASION_SORTIE_ORDER_JP,
        1579: COMMON.MARCH_COUNCIL_PREP_JP,
        1580: COMMON.ARMY_SORTIE_COUNCIL_JP,
    }
    for record_id, canonical_source in source_canonicals.items():
        if COMMON.source_tuple(source_records, record_id) != canonical_source:
            raise RuntimeError(
                f"segment 916 exact-source canonical drifted: {record_id}"
            )
    for record_id, canonical in CANONICAL_TRANSLATIONS.items():
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(len(canonical))
        )
        if actual != canonical:
            raise RuntimeError(
                f"segment 916 Korean canonical reuse drifted: {record_id}"
            )

    joined = "\n".join(translations.values())
    for required in (
        "공략",
        "철수",
        "출진",
        "하명",
        "군의",
        "출진령",
        "침공",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 916 required terminology drifted: {required}")
    for forbidden in ("공격", "퇴각", "군사 회의", "출진 명령"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 916 forbidden terminology retained: {forbidden}"
            )
    if (
        "潮時" not in EXPECTED_BASE_JP[1583][1]
        or "철수할 때" not in raw_translations["15:1583:1"]
    ):
        raise RuntimeError("segment 916 contextual 潮時 meaning drifted")
    for coordinate, ending in {
        "15:1581:0": "아니",
        "15:1581:2": "하",
        "15:1582:0": "진언하",
        "15:1583:1": "생각하",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 916 live inflection stem drifted: {coordinate}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 916 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(raw_translations) != 24 or len(translations) != 24:
        raise RuntimeError("segment 916 fixed visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return FRAMEWORK.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
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
    if len(rows) != 24 or len(validated) != len(translations):
        raise RuntimeError("segment 916 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S916",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "explicit_base_to_pk_map": PK_RECORD_MAP,
                "verified_base_to_pk_offset": 30,
                "decision_sha256": ENGINE.sha256_bytes(OUTPUT.read_bytes()),
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
