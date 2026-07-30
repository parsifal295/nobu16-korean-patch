#!/usr/bin/env python3
"""Build Base authoring segment 909 decisions for the v0.15.0 retranslation."""

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
    / "base_msggame_B001_S909.private.v1.jsonl"
)
SEGMENT = 909
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1514:0": (
        "우리 군단의 전황은 열세라\n"
        "자력으로 헤쳐 나갈 수 있을지…\n"
    ),
    "15:1514:1": "의 지원을 청하고자 하옵니다",
    "15:1515:0": "궁지를 벗어나고자",
    "15:1515:1": (
        "을(를)\n"
        "우리 군단의 지원에 투입하도록\n"
        "부디 허락해 주"
    ),
    "15:1516:0": "적을 상대하기에는 전력이 부족하옵니다…\n",
    "15:1516:1": (
        "의 방침을\n"
        "우리 군단 지원으로 바꾸는 것이 어떻겠습니까"
    ),
    "15:1517:0": "국경에 가까운",
    "15:1517:1": "을(를) 지키고자\n싸움에 능하다고 이름난",
    "15:1517:2": (
        "을(를)\n"
        "성주로 우리 군단에 보내 주실 수 없을지…"
    ),
    "15:1518:0": (
        "은(는) 발전시킬 보람이 있는 땅\n"
        "이곳에는 정무에 능한"
    ),
    "15:1518:1": (
        "을(를)\n"
        "성주로 우리 군단에 맞이하고자 하옵니다"
    ),
    "15:1519:0": (
        "군을 장악할 일손이 부족합니다\n"
        "영지를 맡길 만한 자를 우리 군단에\n"
        "보내 주실 수 없겠습니까"
    ),
    "15:1520:0": (
        "을(를) 공격할 준비를 갖추고자 합니다만\n"
        "적이 강대하여 상당한 피해가 예상됩니다\n"
        "어찌하면 좋겠습니까"
    ),
    "15:1521:0": "인접한 세력이 여럿 있으니\n우선은",
    "15:1521:1": "와 친선을 도모하여\n손을 잡는 것이 어떻겠습니까",
    "15:1522:0": "성하를 샅샅이 뒤진 결과\n",
    "15:1522:1": (
        "이(가) 우리 가문에 사관해도 좋다고 하옵니다\n"
    ),
    "15:1522:2": "인가?",
}
RECORD_ARITIES = {
    1514: 2,
    1515: 2,
    1516: 2,
    1517: 3,
    1518: 2,
    1519: 1,
    1520: 1,
    1521: 2,
    1522: 3,
}
EXPECTED_BASE_JP = {
    1514: (
        "我が軍団の戦況は劣勢にて\n"
        "独力で切り抜けられるかどうか…\n",
        "の支援を願いたく",
    ),
    1515: (
        "窮地脱出がため",
        "を\n我が軍団の支援に回すこと\nどうか、許可して",
    ),
    1516: (
        "敵への対応に戦力が心許なく…\n",
        "の方針を\n我が軍団の支援に変更しては",
    ),
    1517: (
        "国の境に近い",
        "を守るため\n戦上手と評判の",
        "を\n城主として我が軍団に頂けぬかと…",
    ),
    1518: (
        "は発展させ甲斐のある地\nここは施政に長けた",
        "を\n城主として我が軍団に迎えたく",
    ),
    1519: (
        "郡の掌握に人手が足りません\n"
        "知行を任せられる者を我が軍団に\n"
        "いただけないでしょうか",
    ),
    1520: (
        "への軍備を進めたいと考えていますが\n"
        "敵は強大であり相応の被害が予想されます\n"
        "いかがいたしましょうか",
    ),
    1521: (
        "隣接する勢力が複数あるため\nひとまず",
        "と親善し\n手を組むのはいかがでしょうか",
    ),
    1522: (
        "城下をくまなく探し回った結果\n",
        "が当家に仕官してもよいとのこと\n",
        "か？",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    1522: (
        "城下をくまなく探し回ったところ\n",
        "が当家に仕官してくれそう",
        "\n",
        "か？",
    ),
}
EXPECTED_BASE_GAPS = {
    1514: ("", "025a32", "050505"),
    1515: ("", "025a32", "014342010000050505"),
    1516: ("", "025a32", "050505"),
    1517: ("", "026432", "024833", "050505"),
    1518: ("026432", "024833", "050505"),
    1519: ("", "050505"),
    1520: ("025032", "050505"),
    1521: ("", "025032", "050505"),
    1522: (
        "",
        "014325000000",
        "0143b002000001438e000000",
        "050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1522: (
        "",
        "014325000000",
        "014338020000",
        "0143bc0200000143a8010000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1514:0",
    "15:1516:0",
    "15:1517:2",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

SHARED_AUXILIARY = {
    ("SC", 1514): (
        (
            "我军团的战况处于劣势，\n不知能否独立度过危机……\n愿",
            "予以支援。",
        ),
        ("", "025a32", "050505"),
    ),
    ("TC", 1514): (
        (
            "我軍團的戰況處於劣勢，\n能否單獨闖過危機……\n願",
            "予以支援。",
        ),
        ("", "025a32", "050505"),
    ),
    ("SC", 1515): (
        ("为脱离窘境，请准许\n让", "\n援助我军团。"),
        ("", "025a32", "050505"),
    ),
    ("TC", 1515): (
        ("為脫離窘境，請准許\n讓", "\n援助我軍團。"),
        ("", "025a32", "050505"),
    ),
    ("SC", 1516): (
        ("战力不足以抗敌……\n将", "的方针\n变更为对我军团的支援如何？"),
        ("", "025a32", "050505"),
    ),
    ("TC", 1516): (
        ("戰力不足以抗敵……\n將", "的方針\n變更為對我軍團的支援如何？"),
        ("", "025a32", "050505"),
    ),
    ("SC", 1517): (
        (
            "为了保卫离国境很近的",
            "，\n应该让骁勇善战的",
            "\n来我军担任城主……",
        ),
        ("", "026432", "024833", "050505"),
    ),
    ("TC", 1517): (
        (
            "為了防守近於國境的",
            "，\n希望能將作戰高手",
            "\n作為城主配屬至我的軍團……",
        ),
        ("", "026432", "024833", "050505"),
    ),
    ("SC", 1518): (
        (
            "我军团的",
            "远离敌方，\n我想拥立其他军团的政治高手",
            "\n作为城主，来推进政策。",
        ),
        ("", "026432", "024833", "050505"),
    ),
    ("TC", 1518): (
        (
            "我軍團的",
            "遠於敵方，\n我想擁立他軍團擅於政治的",
            "\n作為城主，以推進政策。",
        ),
        ("", "026432", "024833", "050505"),
    ),
    ("SC", 1519): (
        ("掌控郡的人手不足。\n让能够委托知行的人\n加入我军如何？",),
        ("", "050505"),
    ),
    ("TC", 1519): (
        ("掌控郡的人手不足。\n能否指派可委任知行之人\n加入我軍？",),
        ("", "050505"),
    ),
    ("SC", 1520): (
        (
            "考虑进行对",
            "的军备，\n但强敌带来的损害也不可避免。\n意下如何呢？",
        ),
        ("", "025032", "050505"),
    ),
    ("TC", 1520): (
        (
            "考慮進行對",
            "的軍備，\n但強敵帶來的損害也不可避免。\n意下如何呢？",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1521): (
        ("邻接势力有好几个，\n所以先与", "进行亲善，\n并且联手如何？"),
        ("", "025032", "050505"),
    ),
    ("TC", 1521): (
        ("鄰接勢力有好幾個，\n所以先與", "進行親善，\n並且聯手如何？"),
        ("", "025032", "050505"),
    ),
}
BASE_1522_AUXILIARY = {
    ("SC", 1522): (
        ("在城下四处寻找的结果，\n让", "为本家仕官如何？"),
        ("", "014325000000", "050505"),
    ),
    ("TC", 1522): (
        ("在城下四處尋找的結果，\n讓", "為本家做官如何？"),
        ("", "014325000000", "050505"),
    ),
}
PK_1522_AUXILIARY = {
    ("SC", 1522): (
        ("在城下四处寻找时，\n", "提出愿意为本家所用。\n该如何回应？"),
        ("", "014325000000", "050505"),
    ),
    ("TC", 1522): (
        ("在城下四處尋找時，\n", "提出願意為本家所用，\n該如何回應？"),
        ("", "014325000000", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1514: (
        (
            "My province is shorthanded. I donÖt think weÖll be able to survive "
            "without aid. IÖd like to ask for ",
            "Ös assistance.",
        ),
        ("", "025a32", "050505"),
    ),
    1515: (
        ("WeÖre in a tight spot. Please allow me to ask ", " for aid."),
        ("", "025a32", "050505"),
    ),
    1516: (
        (
            "Our forces arenÖt sufficient to deal with the enemy. Please change ",
            "Ös plan to assist my troops.",
        ),
        ("", "025a32", "050505"),
    ),
    1517: (
        (
            " is very close to the border. In order to protect it, could you appoint ",
            " as its lord? IÖve heard theyÖre a very capable fighter.",
        ),
        ("026432", "024833", "050505"),
    ),
    1518: (
        (
            "ItÖll be worth it to develop the area around ",
            ". I would like to request the skilled governor, ",
            ", join my province as a lord.",
        ),
        ("", "026432", "024833", "050505"),
    ),
    1519: (
        (
            "We lack the manpower to seize the county. Is there anyone who could "
            "take over governing my province?",
        ),
        ("", "050505"),
    ),
    1520: (
        (
            "IÖd like to lead an attack against the ",
            ". But their forces are strong, so weÖre likely to incur a lot of "
            "damage. What do you think?",
        ),
        ("", "025032", "050505"),
    ),
    1521: (
        (
            "WeÖre surrounded by many different clans. Perhaps we could show some "
            "goodwill and form an alliance with the ",
            " for the time being?",
        ),
        ("", "025032", "050505"),
    ),
    1522: (
        (
            "We searched the castle town and learned that he is willing to serve "
            "our clan. What do you say?",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): expected
        for (language, record_id), expected in SHARED_AUXILIARY.items()
        for side in ("base", "pk")
    },
    **{
        ("base", language, record_id): expected
        for (language, record_id), expected in BASE_1522_AUXILIARY.items()
    },
    **{
        ("pk", language, record_id): expected
        for (language, record_id), expected in PK_1522_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "corps_support_castle_lord_requests_county_governance_war_preparation_"
    "diplomacy_and_officer_search_with_explicit_plus_15_pk_mapping_base_"
    "pk_sc_tc_and_pk_en_auxiliary_context_base1522_authoritative_despite_"
    "explicit_jp_sc_tc_pk_divergence_jaryeok_yeongji_our_clan_terminology_"
    "speaker_register_live_inflection_stems_current_layout_and_skeleton_"
    "preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if EXPECTED_BASE_JP[1522] == EXPECTED_PK_JP[1522]:
        raise RuntimeError("segment 909 Base/PK JP 1522 divergence collapsed")
    for language in ("SC", "TC"):
        base_expected = BASE_1522_AUXILIARY[(language, 1522)]
        pk_expected = PK_1522_AUXILIARY[(language, 1522)]
        if base_expected == pk_expected:
            raise RuntimeError(
                f"segment 909 Base/PK {language} 1522 divergence collapsed"
            )
    if tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, 1522)])
    ) != EXPECTED_BASE_JP[1522]:
        raise RuntimeError("segment 909 Base-authoritative 1522 source drifted")
    if (
        "우리 가문에 사관해도 좋다고"
        not in raw_translations["15:1522:1"]
    ):
        raise RuntimeError("segment 909 Base-authoritative 1522 meaning drifted")

    joined = "\n".join(translations.values())
    for required in (
        "자력",
        "영지",
        "우리 가문",
        "우리 군단",
        "성주",
        "사관",
        "친선",
        "정무",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 909 required terminology drifted: {required}")
    for forbidden in ("독력", "지행", "당가", "시정"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 909 retained forbidden terminology: {forbidden}"
            )
    if not raw_translations["15:1515:1"].endswith("주"):
        raise RuntimeError("segment 909 support permission opcode stem drifted")
    if raw_translations["15:1522:2"] != "인가?":
        raise RuntimeError(
            "segment 909 Base1522 proven opaque-question split drifted"
        )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 909 ellipsis seed/pair drifted: {coordinate}"
            )


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
    if len(rows) != 18 or len(translations) != 18:
        raise RuntimeError("segment 909 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 909 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S909",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "explicit_pk_mapping": True,
                "base_authoritative_pk_divergence_record": 1522,
                "base_pk_divergent_languages": ["JP", "SC", "TC"],
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
