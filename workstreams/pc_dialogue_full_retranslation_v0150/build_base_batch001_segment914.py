#!/usr/bin/env python3
"""Build Base authoring segment 914 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment884 as FRAMEWORK


ENGINE = FRAMEWORK.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S914.private.v1.jsonl"
)
SEGMENT = 914

# B110 exact-source canonical objects. Later segments reuse these objects even
# when the dynamic target token changes from castle (026432) to county (029632).
ENEMY_APPROACH_JP = (
    "へ敵勢が向かってござる\n",
    "相手とは腕が鳴りますな\nさあ、陣触れを！",
)
INVASION_INTERCEPT_JP = (
    "に向けて\n",
    "が侵攻を始めた様子\n今こそ、迎撃の下知を",
)
UNIT_SORTIE_COUNCIL_JP = (
    "に向けて\n",
    "の部隊が出陣しました\n急ぎ軍議のご命令を",
)
OUR_HOLDING_INVASION_JP = (
    "我らが",
    "を目指し\n",
    "が侵攻を始めましたな\n急ぎ撃退の方策を練るといたそう",
)
SEIZURE_MARCH_JP = (
    "奪取を目論み\n",
    "が進軍を開始いたしました\nどうか、軍議のご用意を",
)
ARMY_ATTACK_COUNCIL_JP = (
    "へ指して\n",
    "の軍が攻めてまいった\n急ぎ軍議を開きましょうぞ",
)
UNIT_MARCH_COUNCIL_JP = (
    "に向けて\n",
    "の部隊が進軍しております\n至急、軍議を開きましょう！",
)
INVASION_SORTIE_ORDER_JP = (
    "に向けて\n",
    "が侵攻を始めた様子\nすぐにでも出陣する！　下知を！",
)
MARCH_COUNCIL_PREP_JP = (
    "に向けて\n",
    "が進軍しております\n至急、軍議の支度を始めましょう",
)
ARMY_SORTIE_COUNCIL_JP = (
    "に向けて\n",
    "の軍が出陣しましたぞ！\nすぐ軍議を開かなくては！",
)

ENEMY_APPROACH_KO = (
    "(으)로 적군이 향하고 있사옵니다\n",
    "을(를) 상대할 생각에 팔이 근질거리는구려\n"
    "자, 출진령을 내려 주시옵소서!",
)
INVASION_INTERCEPT_KO = (
    "을(를) 향해\n",
    "이(가) 침공을 시작한 모양\n"
    "지금이야말로 요격을 하명해 주시옵소서",
)
UNIT_SORTIE_COUNCIL_KO = (
    "을(를) 향해\n",
    "의 부대가 출진했사옵니다\n"
    "어서 군의를 열도록 하명해 주시옵소서",
)
OUR_HOLDING_INVASION_KO = (
    "아군의",
    "을(를) 노리고\n",
    "이(가) 침공을 시작했구려\n"
    "서둘러 격퇴할 방책을 세우도록 합시다",
)
SEIZURE_MARCH_KO = (
    "을(를) 빼앗고자\n",
    "이(가) 진군을 시작했사옵니다\n"
    "부디 군의를 준비해 주시옵소서",
)
ARMY_ATTACK_COUNCIL_KO = (
    "(으)로 향해\n",
    "의 군이 쳐들어왔소\n"
    "서둘러 군의를 열도록 하십시다",
)
UNIT_MARCH_COUNCIL_KO = (
    "을(를) 향해\n",
    "의 부대가 진군하고 있습니다\n"
    "어서 군의를 여시지요!",
)
INVASION_SORTIE_ORDER_KO = (
    "을(를) 향해\n",
    "이(가) 침공을 시작한 모양\n"
    "당장 출진하겠습니다! 하명해 주십시오!",
)
MARCH_COUNCIL_PREP_KO = (
    "을(를) 향해\n",
    "이(가) 진군하고 있사옵니다\n"
    "어서 군의 준비를 시작하시지요",
)
ARMY_SORTIE_COUNCIL_KO = (
    "을(를) 향해\n",
    "의 군이 출진했소이다!\n"
    "어서 군의를 열어야 하오!",
)

RAW_TRANSLATIONS: dict[str, str] = {
    "15:1553:0": "간자가",
    "15:1553:1": (
        "의 산하 군에 들어와\n"
        "수상한 움직임을 보인다 하옵니다…\n"
        "병사를 보내면 견제할 수 있"
    ),
    "15:1554:0": "지금이야말로",
    "15:1554:1": "공략의 호기\n출진을 하명해 주",
    "15:1555:0": "만반의 준비를 갖추",
    "15:1555:2": "공략의 호기",
    "15:1556:0": "승기는 바로 지금",
    "15:1556:2": "공략에 나서",
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in (1557, 1558, 1561)
        for literal_id, translation in enumerate(ENEMY_APPROACH_KO)
    },
    **{
        f"15:1559:{literal_id}": translation
        for literal_id, translation in enumerate(INVASION_INTERCEPT_KO)
    },
    **{
        f"15:1560:{literal_id}": translation
        for literal_id, translation in enumerate(UNIT_SORTIE_COUNCIL_KO)
    },
    **{
        f"15:1562:{literal_id}": translation
        for literal_id, translation in enumerate(OUR_HOLDING_INVASION_KO)
    },
}
RECORD_ARITIES = {
    1553: 2,
    1554: 2,
    1555: 3,
    1556: 3,
    1557: 2,
    1558: 2,
    1559: 2,
    1560: 2,
    1561: 2,
    1562: 3,
}
EXPECTED_BASE_JP = {
    1553: (
        "間者が",
        "下の郡に入り\n良からぬ動きを見せているとか…\n兵を向ければ牽制でき",
    ),
    1554: ("今こそ", "攻略の好機\n出陣の下知を"),
    1555: ("準備万端、整", "\n", "攻めの好機"),
    1556: ("勝機は今", "\n", "攻略に乗り出"),
    1557: ENEMY_APPROACH_JP,
    1558: ENEMY_APPROACH_JP,
    1559: INVASION_INTERCEPT_JP,
    1560: UNIT_SORTIE_COUNCIL_JP,
    1561: ENEMY_APPROACH_JP,
    1562: OUR_HOLDING_INVASION_JP,
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1553: ("", "026432", "01431e040000050505"),
    1554: ("", "026432", "014342010000050505"),
    1555: (
        "",
        "01436e020000",
        "026432",
        "01431a020000050505",
    ),
    1556: (
        "",
        "01431a020000",
        "026432",
        "01437e040000050505",
    ),
    **{
        record_id: ("026432", "025032", "050505")
        for record_id in (1557, 1558, 1559, 1560, 1561)
    },
    1562: ("", "026432", "025032", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1553: ("", "026432", "01432a040000050505"),
    1555: (
        "",
        "01437a020000",
        "026432",
        "014326020000050505",
    ),
    1556: (
        "",
        "014326020000",
        "026432",
        "01438a040000050505",
    ),
}
PK_RECORD_MAP = {
    1553: 1583,
    1554: 1584,
    1555: 1585,
    1556: 1586,
    1557: 1587,
    1558: 1588,
    1559: 1589,
    1560: 1590,
    1561: 1591,
    1562: 1592,
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1553:1"}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1555:1": "\n",
    "15:1556:1": "\n",
}


def make_auxiliary_overrides(
    shared: dict[
        tuple[str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    pk_en: dict[int, tuple[tuple[str, ...], tuple[str, ...]]],
) -> dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
]:
    return {
        **{
            (side, language, record_id): expected
            for (language, record_id), expected in shared.items()
            for side in ("base", "pk")
        },
        **{
            ("pk", "EN", record_id): expected
            for record_id, expected in pk_en.items()
        },
    }


SHARED_AUXILIARY = {
    ("SC", 1553): (
        (
            "听闻有间谍潜入",
            "下的郡，\n做些偷偷摸摸的勾当……\n若出兵的话，便可制约其行动。",
        ),
        ("", "026432", "050505"),
    ),
    ("TC", 1553): (
        (
            "據報，在",
            "的郡中\n發現間諜暗中活動。\n應派遣士兵加以牽制……",
        ),
        ("", "026432", "050505"),
    ),
    ("SC", 1554): (
        ("现在正是攻下", "的好时机，\n请下令进军吧。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1554): (
        ("現為", "攻略良機，\n請下令出陣！"),
        ("", "026432", "050505"),
    ),
    ("SC", 1555): (
        ("准备就绪，\n正是攻击", "的好机会。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1555): (
        ("一切準備就緒，\n現乃", "攻略良機。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1556): (
        ("现在正是致胜的机会，\n开始攻略", "吧。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1556): (
        ("勝機不待人，\n投入", "攻略吧！"),
        ("", "026432", "050505"),
    ),
    ("SC", 1559): (
        (
            "的部队似乎对",
            "\n展开了进攻。\n您若有令，我愿即刻去歼灭他们。",
        ),
        ("025032", "026432", "050505"),
    ),
    ("TC", 1559): (
        (
            "部隊似乎\n朝著",
            "開始進攻。\n且待大人下令，吾當迅速前往殲滅。",
        ),
        ("025032", "026432", "050505"),
    ),
    ("SC", 1560): (
        ("的部队对", "\n出阵了。\n请您火速下令举行军议。"),
        ("025032", "026432", "050505"),
    ),
    ("TC", 1560): (
        ("部隊已朝著", "出陣。\n請大人緊急召開軍議下令。"),
        ("025032", "026432", "050505"),
    ),
    ("SC", 1561): (
        (
            "敌军正朝",
            "进发。\n要对付",
            "，真叫人摩拳擦掌。\n请您下令出战吧！",
        ),
        ("", "026432", "025032", "050505"),
    ),
    ("TC", 1561): (
        (
            "敵軍正朝著",
            "進攻，\n對上",
            "真教人躍躍欲試。\n請大人快下軍令！",
        ),
        ("", "026432", "025032", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1553: (
        (
            "Spies have infiltrated a county under ",
            " and are up to no good. You can restrain them by sending in troops.",
        ),
        ("", "026432", "050505"),
    ),
    1554: (
        (
            "This is a great chance to attack ",
            ". ItÖs time to order the troops to march.",
        ),
        ("", "026432", "050505"),
    ),
    1555: (
        ("WeÖre all set to go. This is a great chance to attack ", "."),
        ("", "026432", "050505"),
    ),
    1556: (
        ("This is our moment. LetÖs set out for ", "."),
        ("", "026432", "050505"),
    ),
    1559: (
        (
            "The ",
            " have launched their invasion on ",
            ". This would be a good time to ambush them.",
        ),
        ("", "025032", "026432", "050505"),
    ),
    1560: (
        (
            "The ",
            " are marching for ",
            ". We must assemble a war council immediately.",
        ),
        ("", "025032", "026432", "050505"),
    ),
    1561: (
        (
            "The enemy is marching on ",
            ". The ",
            " are not to be underestimated. We await your orders!",
        ),
        ("", "026432", "025032", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B110_pristine_base_pc_jp_authoritative_"
    "spy_warning_attack_opportunity_and_enemy_invasion_sortie_alerts_"
    "with_content_and_sequence_verified_explicit_base_to_pk_plus_30_map_"
    "exact_base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_kanja_"
    "koryak_shutsujin_hamyeong_chimgong_gunui_terms_jinbure_as_historical_"
    "sortie_order_two_hidden_lf_slots_exact_source_canonical_reuse_live_"
    "inflection_stems_current_layout_and_token_skeleton_preserved_"
    "runtime_fragment_pending"
)


def source_tuple(
    source_records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(
            source_records[(15, record_id)]
        )
    )


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    explicit_map = {
        1553: 1583,
        1554: 1584,
        1555: 1585,
        1556: 1586,
        1557: 1587,
        1558: 1588,
        1559: 1589,
        1560: 1590,
        1561: 1591,
        1562: 1592,
    }
    if PK_RECORD_MAP != explicit_map:
        raise RuntimeError("segment 914 explicit content-derived PK map drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 914 verified PK offset drifted from +30")

    repeated_ids = (1557, 1558, 1561, 1569, 1570, 1573)
    if any(source_tuple(source_records, record_id) != ENEMY_APPROACH_JP for record_id in repeated_ids):
        raise RuntimeError("segment 914 enemy-approach source canonical drifted")
    for record_id in (1557, 1558, 1561):
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual != ENEMY_APPROACH_KO:
            raise RuntimeError(
                f"segment 914 enemy-approach Korean canonical drifted: {record_id}"
            )

    joined = "\n".join(translations.values())
    for required in (
        "간자",
        "공략",
        "출진",
        "하명",
        "침공",
        "군의",
        "출진령",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 914 required terminology drifted: {required}")
    for forbidden in ("첩자", "공격의 호기", "출진 명령", "명령을 내려"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 914 forbidden terminology retained: {forbidden}"
            )
    if "陣触れ" not in ENEMY_APPROACH_JP[1]:
        raise RuntimeError("segment 914 陣触れ source guard drifted")
    if "출진령" not in ENEMY_APPROACH_KO[1]:
        raise RuntimeError("segment 914 historical 陣触れ meaning drifted")
    for coordinate, ending in {
        "15:1553:1": "있",
        "15:1554:1": "주",
        "15:1555:0": "갖추",
        "15:1556:2": "나서",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 914 live inflection stem drifted: {coordinate}"
            )
    if EXCLUDED_NONVISIBLE_COORDINATES != {
        "15:1555:1": "\n",
        "15:1556:1": "\n",
    }:
        raise RuntimeError("segment 914 hidden LF universe drifted")
    if (
        raw_translations["15:1553:1"].count("…") != 1
        or translations["15:1553:1"].count("…") != 2
    ):
        raise RuntimeError("segment 914 ellipsis seed/pair drifted")
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 914 fixed visible decision count drifted")


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
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 914 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S914",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "explicit_base_to_pk_map": PK_RECORD_MAP,
                "verified_base_to_pk_offset": 30,
                "hidden_lf_slots_preserved": 2,
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
