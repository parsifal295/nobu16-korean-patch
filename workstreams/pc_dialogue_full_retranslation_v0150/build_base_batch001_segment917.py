#!/usr/bin/env python3
"""Build Base authoring segment 917 decisions for the v0.15.0 retranslation."""

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
UTIL = COMMON.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S917.private.v1.jsonl"
)
SEGMENT = 917
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1584:0": "병량이 이제 곧 바닥나",
    "15:1584:1": "\n내키지는 않",
    "15:1584:2": "만\n여기서는 철수해야 할",
    "15:1584:3": "…",
    "15:1585:0": "지금 우리의 전력으로는\n",
    "15:1585:1": "을(를) 공략하기 어렵",
    "15:1585:2": "\n지금이 물러날 때인지도 모르옵니다",
    "15:1586:0": "일국 통일, 참으로 경하드리옵니다",
    "15:1586:1": "\n이에 한 말씀 진언드리고자 하옵니다…",
    "15:1587:0": "주군, 이로써",
    "15:1587:1": "을(를) 통일하셨습니다!\n경하드리옵니다!",
    "15:1588:0": "일국을 지배한 데 만족해서는 안 됩니다.",
    "15:1588:1": (
        "\n다음 구니를 공략할 거점으로\n"
        "계속 발전시켜야 합니다."
    ),
    "15:1589:0": (
        "무사시는 반도의 중심이며 이웃한 구니도 많은 땅\n"
        "다른 구니로 진출하려면 무사시 일대를 지배한\n"
        "의미가 크다고"
    ),
    "15:1590:0": (
        "사가미는 가마쿠라 막부 이래\n"
        "무가에 특별한 의미를 지닌 요충지\n"
        "모두의 사기도 오르"
    ),
    "15:1591:0": (
        "남북으로 긴 신슈를 한 다이묘 가문이 다스리는 것은\n"
        "무가의 세상이 열린 뒤로도 보기 드문 위업\n"
        "모두의 사기도 오르"
    ),
    "15:1592:0": (
        "오와리는 동국과 서국의 경계에 있으며\n"
        "기나이까지 넘볼 수 있는 요충지\n"
        "이 구니를 제압한 의의는 크다고"
    ),
    "15:1593:0": (
        "오미는 가도와 수운의 요충지. 그 중요성 때문에\n"
        '"오미를 지배하는 자가 천하를 지배한다"고까지\n'
        "말하는 이도 있다 하오"
    ),
    "15:1594:0": (
        "야마시로는 예로부터 천황의 도읍\n"
        "이 땅이야말로 천하라고도 불리"
    ),
    "15:1594:1": "\n천하인이 되는 첫걸음",
    "15:1595:0": (
        "셋쓰는 내해에서 배로 실어 온 산물과\n"
        "교토에서 내려온 물자가 거래되는\n"
        "교역의 요지"
    ),
    "15:1596:0": (
        "옛 도읍 나라에는 지금도 많은 상인이 모이니\n"
        "그곳을 품은 야마토국을 제압한 의미는\n"
        "크다고"
    ),
    "15:1597:0": (
        "이 반슈는 서국과 교토를 잇는 요충지\n"
        "구니별 지방관직 가운데 하리마노카미는 이요노카미와 함께\n"
        "가장 격이 높다고 일컬어져"
    ),
}
RECORD_ARITIES = {
    1584: 4,
    1585: 3,
    1586: 2,
    1587: 2,
    1588: 2,
    **{record_id: 1 for record_id in range(1589, 1594)},
    1594: 2,
    **{record_id: 1 for record_id in range(1595, 1598)},
}
EXPECTED_BASE_JP = {
    1584: (
        "兵糧がもう直ぐ底を突",
        "\n不本意では",
        "が\nここは撤退すべき",
        "…",
    ),
    1585: (
        "今の我らの戦力では\n",
        "攻略は難しい",
        "\n撤退の潮時やもしれませぬ",
    ),
    1586: (
        "一国の統一、祝着至極",
        "\nついては一言進言したく…",
    ),
    1587: (
        "殿、これで",
        "を統一できましたぞ！\nおめでとうございます！",
    ),
    1588: (
        "一国の支配に満足してはい",
        "\n次の国を攻めるための拠点として\n発展させてい",
    ),
    1589: (
        "武蔵は坂東の中心にして、隣接国も多い地\n"
        "他国に進出する上でも、武蔵一円を支配した\n"
        "意味は大きいかと",
    ),
    1590: (
        "相模は鎌倉殿の御時より、\n"
        "武家にとっては特別な意味を持つ枢要の地\n"
        "皆の意気も上が",
    ),
    1591: (
        "南北に長い信州を一大名家が治めるのは\n"
        "武家の世になってからは稀有な偉業\n"
        "皆の意気も上が",
    ),
    1592: (
        "尾張は東国と西国の境に当たり、\n"
        "畿内もうかがえる枢要の地\n"
        "この国を制した意義は大きいかと",
    ),
    1593: (
        "近江は街道・水運の要衝。その重要性ゆえ\n"
        "「近江を制する者は天下を制す」とまで\n"
        "申す者もいるとか",
    ),
    1594: (
        "山城といえば、いにしえよりの王城の地\n"
        "この地こそが天下とも呼ばれ",
        "\n天下人への第一歩",
    ),
    1595: (
        "摂津は、内海を船で運んできた産物や\n"
        "京から下ってきた荷物が商われる\n"
        "交易上の要地",
    ),
    1596: (
        "かつての都であり、今でも多くの商人が集う\n"
        "南都を擁する大和国を制した意味は\n"
        "大きいと",
    ),
    1597: (
        "この播州は西国と京を結ぶ枢要の地\n"
        "諸国の国司の中でも播磨守は、伊予守と並び\n"
        "最も格上といわれて",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1584: (
        "",
        "014336010000",
        "014378010000",
        "01431e010000",
        "050505",
    ),
    1585: ("", "026432", "01431e010000", "050505"),
    1586: ("", "01431a020000", "050505"),
    1587: ("", "023c", "050505"),
    1588: ("", "014330040000", "01436c010000050505"),
    1589: ("", "0143e2000000050505"),
    1590: ("", "01435a040000050505"),
    1591: ("", "01435a040000050505"),
    1592: ("", "0143e2000000050505"),
    1593: ("", "050505"),
    1594: ("", "01433c040000", "01434a020000050505"),
    1595: ("", "01434a020000050505"),
    1596: ("", "0143e2000000050505"),
    1597: ("", "0143b2000000050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    1588: ("", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1586: ("", "014326020000", "050505"),
    1588: ("", "01433c040000", "01436c010000050505"),
    1590: ("", "014366040000050505"),
    1591: ("", "014366040000050505"),
    1594: ("", "014348040000", "014356020000050505"),
    1595: ("", "014356020000050505"),
}
PK_RECORD_MAP = {
    1584: 1614,
    1585: 1615,
    1586: 1616,
    1587: 1617,
    1588: 1618,
    1589: 1619,
    1590: 1620,
    1591: 1621,
    1592: 1622,
    1593: 1623,
    1594: 1624,
    1595: 1625,
    1596: 1626,
    1597: 1627,
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1584:3",
    "15:1586:1",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_RECORD_IDS = {1593}

SHARED_AUXILIARY = {
    1584: (
        ("军粮已经所剩无几了。\n在耗尽前撤退吧。",),
        ("軍糧已經所剩無幾了。\n在耗盡前撤退吧。",),
        (
            "WeÖll soon run out of supplies. I canÖt believe IÖm saying "
            "this, but we may need to retreat.",
        ),
    ),
    1585: (
        ("以现在的兵力，\n完全无法攻陷", "。\n再持续下去也是白白送死。"),
        ("以現在的兵力，\n完全無法攻陷", "。\n再持續下去也是白白送死。"),
        (
            "ItÖll be hard to capture ",
            " with our current strength. We should retreat and wait for a better chance.",
        ),
    ),
    1586: (
        ("统一一国，可喜可贺。\n不过在下还有一件事想进言……",),
        ("統一一國實在可喜可賀，\n且容微臣進諫……",),
        (
            "Congratulations on unifying the country. If I could offer you "
            "one piece of counsel...",
        ),
    ),
    1587: (
        ("大人，如此便成功统一", "了！\n恭喜您！"),
        ("終於完成統一！\n恭喜大人！",),
        (
            "You did it! YouÖve united ",
            "! From the bottom of my heart, congratulations.",
        ),
    ),
    1588: (
        (
            "不可满足于统治一国，rarenu\n"
            "好好发展它，\n用作进攻下一个国家的据点吧。",
        ),
        (
            "統治一國無以自滿，\n當以此地為據點向外擴展，\n"
            "逐步攻打下個國家！",
        ),
        (
            "One cannot be content with dominance over a single country. "
            "LetÖs improve this area to serve as a base of operations to attack the next one.",
        ),
    ),
    1589: (
        (
            "武藏乃坂东中心，邻国又多。\n在向他国扩张时，统治武藏一带\n"
            "应当也颇具意义。",
        ),
        (
            "武藏地處│東的中心，鄰國眾多，\n利於進軍他國，統治武藏一帶\n"
            "可謂意義重大。",
        ),
        (
            "Musashi lies at the heart of Bandª and is surrounded by many "
            "countries. Gaining control of it will be most significant.",
        ),
    ),
    1590: (
        (
            "与镰仓时相比，相模这一枢要之地\n对武家的意义更为特别了，\n"
            "大家的士气也会高涨的。",
        ),
        (
            "相模自鐮倉時代起，\n對武家而言乃別具意義的樞要之地，\n"
            "眾將士想必也會鬥志昂揚。",
        ),
        (
            "Sagami has been a significant location for samurai since the "
            "reign of Kamakura. It will bolster the menÖs spirits.",
        ),
    ),
    1591: (
        (
            "由一家大名来统治南北纵长的信州，\n这是武家掌权后的罕见伟业，\n"
            "大家的士气也会高涨的。",
        ),
        (
            "南北縱長的信州由一大名家治理，\n自武門治世以來乃罕見偉業，\n"
            "眾將士想必也會鬥志昂揚。",
        ),
        (
            "It is a rare feat for a single daimyª to govern all of Shinsh¨, "
            "a region that stretches far to the north and south. The people will be pleased.",
        ),
    ),
    1592: (
        (
            "尾张是东国与西国的分界线，\n也是可以窥见畿内的枢要之地，\n"
            "压制此国应当意义不小。",
        ),
        (
            "尾張相當於東國與西國之境，\n亦為放眼畿內的樞要之地，\n"
            "掌控此國可謂意義重大。",
        ),
        (
            "Owari is located on the border between east and west Japan and "
            "is also of great importance to the capital. Conquering this area "
            "will be a significant achievement.",
        ),
    ),
    1593: (
        (
            "近江是道路与水运的要地。据说由于它意义重大，\n甚至有人称\n"
            "“得近江者得天下”。",
        ),
        ("近江乃水陸要衝，重要性不言而喻，\n甚而有「得近江者得天下」一說。",),
        (
            "¥mi is a key location for the nationÖs roads and waterways. "
            "ItÖs why some even say that he who rules ¥mi rules the nation.",
        ),
    ),
    1594: (
        (
            "虽说是山城，但这片土地是自古以来的\n王城之地，又被称为天下，\n"
            "是成为天下人的第一步啊。",
        ),
        (
            "山城乃自古以來的王城之地，\n亦有此地為天下之說，\n"
            "是謂邁向天下人的第一步。",
        ),
        (
            "Yamashiro has been home to the imperial castle since time "
            "immemorial; it could well be considered the heart of the nation. "
            "If you mean to unite these lands, that would be the first step.",
        ),
    ),
    1595: (
        (
            "摄津是交易要地，\n会买卖用船从内海运来的产物\n"
            "和来自京都的货物。",
        ),
        (
            "攝津乃交易要地，無論是內海船運的物產、\n京都南下的貨物，\n"
            "皆會在此進行買賣。",
        ),
        (
            "Settsu is where goods are brought by boat through the inland sea "
            "and where products from the capital are traded. It is an extremely "
            "important trading hub.",
        ),
    ),
    1596: (
        (
            "大和国是古都，\n如今也拥有商人云集的南都，\n"
            "压制它想来意义不小。",
        ),
        ("南都乃昔日古都，至今仍有許多商人聚集，\n掌控南都所在的大和國可謂意義重大。",),
        (
            "The former capital, Yamato, still attracts many merchants. "
            "Taking this region would hold great significance.",
        ),
    ),
    1597: (
        (
            "播州此地乃连接西国与京都的枢要，\n在诸国国司中，播磨守也是与伊予守\n"
            "并称为最高位的。",
        ),
        (
            "播州乃西國連結京都的樞要之地，\n而在諸國國司當中，世人更將播磨守及\n"
            "伊予守並列最高等。",
        ),
        (
            "Bansh¨ is an important location that connects the capital with "
            "western Japan. The Harima regionÖs governor is said to be just as "
            "highly ranked as the Iyo prefect.",
        ),
    ),
}
SHARED_AUXILIARY_GAPS = {
    1584: (("", "050505"), ("", "050505"), ("", "050505")),
    1585: (
        ("", "026432", "050505"),
        ("", "026432", "050505"),
        ("", "026432", "050505"),
    ),
    1586: (("", "050505"), ("", "050505"), ("", "050505")),
    1587: (
        ("", "023c", "050505"),
        ("023c", "050505"),
        ("", "023c", "050505"),
    ),
    **{
        record_id: (("", "050505"), ("", "050505"), ("", "050505"))
        for record_id in range(1588, 1598)
    },
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): (
            SHARED_AUXILIARY[record_id][language_index],
            SHARED_AUXILIARY_GAPS[record_id][language_index],
        )
        for record_id in RECORD_ARITIES
        for side in ("base", "pk")
        for language_index, language in enumerate(("SC", "TC"))
    },
    **{
        ("pk", "EN", record_id): (
            SHARED_AUXILIARY[record_id][2],
            SHARED_AUXILIARY_GAPS[record_id][2],
        )
        for record_id in RECORD_ARITIES
    },
}
HISTORICAL_REFERENCE_URLS = (
    "https://www.daito.ac.jp/exten/26/spring/104.html",
    "https://www.tama.ac.jp/cooperation/img/tamagaku/01_morohashi.pdf",
    "https://www.city.kamakura.kanagawa.jp/rekibun-rekishi.html",
    "https://150th.pref.nagano.lg.jp/feature/553/",
    "https://www.pref.aichi.jp/uploaded/life/383424_1675548_misc.pdf",
    "https://www.pref.shiga.lg.jp/ippan/kendoseibi/machizukuri/19795.html",
    "https://www.city.kyoto.lg.jp/sogo/page/0000035742.html",
    "https://kobe-rekishiisan.city.kobe.lg.jp/history/chusei/",
    "https://www.narahaku.go.jp/exhibition/special/202607_nantobutsuga/",
    "https://ndlsearch.ndl.go.jp/rnavi/humanities/post_101126",
    "https://sitereports.nabunken.go.jp/ja/article/113/pdf_page",
)
BASIS = (
    "review_queue_base_msggame_B110_C_pristine_base_pc_jp_authoritative_"
    "retreat_country_unification_and_historical_province_commentary_with_"
    "explicit_base1584_to1597_pk1614_to1627_mapping_exact_base_pk_sc_tc_"
    "and_pk_en_auxiliary_context_bando_kamakura_shinshu_omi_yamashiro_"
    "nanto_kokushi_history_research_king_city_and_south_capital_meanings_"
    "made_explicit_current1588_flattened_runtime_skeleton_recorded_source_"
    "opcode_stems_and_current_layout_preserved_static_and_runtime_split"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "병량",
        "철수",
        "반도",
        "가마쿠라 막부",
        "기나이",
        "천황의 도읍",
        "옛 도읍 나라",
        "구니별 지방관직",
        "하리마노카미",
        "이요노카미",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 917 required meaning drifted: {required}")
    for forbidden in ("간토", "왕성", "남도", "국사", "「", "」", "。", "、"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 917 retained opaque or forbidden term: {forbidden}"
            )
    for coordinate, ending in {
        "15:1584:0": "바닥나",
        "15:1584:1": "않",
        "15:1584:2": "해야 할",
        "15:1585:1": "어렵",
        "15:1589:0": "다고",
        "15:1590:0": "오르",
        "15:1591:0": "오르",
        "15:1592:0": "다고",
        "15:1594:0": "불리",
        "15:1596:0": "다고",
        "15:1597:0": "일컬어져",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 917 live inflection stem drifted: {coordinate}"
            )
    if RAW_TRANSLATIONS["15:1588:0"].endswith(("않", "말")):
        raise RuntimeError("segment 917 flattened record 1588 was left as a stem")
    if RAW_TRANSLATIONS["15:1588:1"].endswith(("하", "시키")):
        raise RuntimeError("segment 917 flattened record 1588 was left as a stem")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 917 ellipsis seed/pair drifted: {coordinate}"
            )
    if set(PK_RECORD_MAP.items()) != {
        (1584, 1614),
        (1585, 1615),
        (1586, 1616),
        (1587, 1617),
        (1588, 1618),
        (1589, 1619),
        (1590, 1620),
        (1591, 1621),
        (1592, 1622),
        (1593, 1623),
        (1594, 1624),
        (1595, 1625),
        (1596, 1626),
        (1597, 1627),
    }:
        raise RuntimeError("segment 917 explicit Base-to-PK mapping drifted")
    if len(HISTORICAL_REFERENCE_URLS) != 11:
        raise RuntimeError("segment 917 historical reference set drifted")


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
    for row in rows:
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 23 or len(translations) != 23:
        raise RuntimeError("segment 917 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 917 validated count drifted")
    static_count = sum(
        row["scope_classification"] == "retranslated" for row in rows
    )
    if static_count != 1:
        raise RuntimeError("segment 917 static decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S917",
                "decision_count": len(rows),
                "retranslated": static_count,
                "runtime_fragment_pending": len(rows) - static_count,
                "explicit_pk_mapping": True,
                "current_flattened_opcode_records": [1588],
                "historical_reference_count": len(HISTORICAL_REFERENCE_URLS),
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
