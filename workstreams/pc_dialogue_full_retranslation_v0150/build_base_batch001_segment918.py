#!/usr/bin/env python3
"""Build Base authoring segment 918 decisions for the v0.15.0 retranslation."""

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
    / "base_msggame_B001_S918.private.v1.jsonl"
)
SEGMENT = 918
CHIGYO_REQUEST_FRAME = (
    "아무도 다스리지 않는 군은\n"
    "영지로 가신인 저희에게 맡겨 주십시오\n"
    "반드시 풍요롭게 만들어 보이겠습니다"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1598:0": (
        "앞으로 우리 가문이 나아갈 길입니다만\n"
        "위신을 높이려면,"
    ),
    "15:1598:1": "의 신용을 높여\n역직을 받는 것도 한 방법이옵니다",
    "15:1599:0": (
        "또 조정에 금전을 헌상해 관직을 받고\n"
        "위신을 높이는 방법도 있사옵니다"
    ),
    "15:1600:0": "어쨌든, 일국을 다스리는 다이묘가 되신",
    "15:1600:1": (
        "님이라면\n"
        "어지러운 전국 난세를 아우르는 일도 꿈이 아니옵니다\n"
        "저희도,"
    ),
    "15:1600:2": "님을 위해 더욱 힘쓰겠나이다!",
    "15:1601:0": "을(를) 통일하여\n우리 가문의 위신이",
    "15:1601:1": "상승했습니다",
    "15:1602:0": "빈 군이 있거든\n",
    "15:1602:1": "에게 내려 주게\n황폐한 군을 보고만 있자니 못 견디겠어!",
    "15:1603:0": (
        "빈 군이 있다면\n"
        "가신인 우리에게 맡겨 주시옵소서\n"
        "그리하면 우리 가문은 더욱 커질 것이옵니다"
    ),
    "15:1604:0": (
        "아무도 다스리지 않는 군은\n"
        "가신인 저희에게 맡겨 주시옵소서\n"
        "풍요로운 땅으로 만들어 보이겠나이다"
    ),
    "15:1605:0": CHIGYO_REQUEST_FRAME,
    "15:1606:0": (
        "빈 군은 가신인 저희에게 맡겨 주시옵소서\n"
        "전쟁이 나면\n"
        "그 땅에서 병사를 이끌고 참전하겠사옵니다"
    ),
    "15:1607:0": (
        "군은 가신인 저희에게 영지로 내려 주시옵소서\n"
        "그러지 않으면 돌보는 이 하나 없이\n"
        "황폐해지고 말 것이옵니다"
    ),
    "15:1608:0": (
        "아무도 다스리지 않는 군이 있사옵니다\n"
        "가신인 저희에게 지행지로 내려 주신다면\n"
        "제대로 다스려 풍요롭게 하겠나이다"
    ),
    "15:1609:0": (
        "빈 군이 있는 듯하구나\n"
        "가신인 우리에게 맡겨 두시게\n"
        "지행지로 맡은 이상 잘 다스려 보이겠네"
    ),
    "15:1610:0": (
        "아무도 다스리지 않는 군이 있습니다\n"
        "부디 가신인 저희에게 맡겨 주시지 않겠습니까?\n"
        "제대로 다스려 보이겠습니다"
    ),
    "15:1611:0": (
        "아무도 다스리지 않는 군이 있는 듯하군\n"
        "누군가에게 맡겨 다스리게 하는 게 어떻겠나\n"
        "틀림없이 잘 다스릴 것이네"
    ),
    "15:1612:0": (
        "아무도 다스리지 않는 군이 있군요\n"
        "부디 저희에게 맡겨 주시지 않겠습니까?\n"
        "제대로 다스려 보이겠습니다"
    ),
    "15:1613:0": f"{CHIGYO_REQUEST_FRAME}!",
}
RECORD_ARITIES = {
    1598: 2,
    1599: 1,
    1600: 3,
    1601: 2,
    1602: 2,
    **{record_id: 1 for record_id in range(1603, 1614)},
}
EXPECTED_BASE_JP = {
    1598: (
        "これからの当家の立ち回りですが\n威信を高めるため、",
        "の信用を高め\n役職をいただくも一手でございます",
    ),
    1599: (
        "また、朝廷に金銭を献じて官職をいただき\n"
        "威信を高めてもよいでしょう",
    ),
    1600: (
        "とまれ、国持ち大名となった",
        "なら\n乱れた戦国の世を束ねるも夢ではありませぬ\n我らも、",
        "のためさらに励みまする！",
    ),
    1601: (
        "を統一したことにより、\n当家の威信が",
        "上昇しました",
    ),
    1602: (
        "空いている郡があったら\n",
        "に与えてくれ\n荒れ放題の郡を見るのは忍びねえ！",
    ),
    1603: (
        "空いている郡あらば\n我ら家臣にお任せくだされ\n"
        "されば、当家はさらに大きくなりましょうぞ",
    ),
    1604: (
        "誰も治めておらぬ郡は\n我ら家臣にお任せを\n"
        "豊かな地にしてみせまするぞ",
    ),
    1605: (
        "誰も治めていない郡は\n知行として我ら家臣に任せてください\n"
        "きっと豊かにしてみせますよ",
    ),
    1606: (
        "空いておる郡は、我ら家臣にお任せあれ\n戦のおりには\n"
        "その地より兵を率いて参陣いたそうぞ",
    ),
    1607: (
        "郡は我ら家臣に知行としてお与えあれ\n"
        "さもなくば、誰も顧みる者もなく\n荒れ放題になってしまいますぞ",
    ),
    1608: (
        "誰も治めておらぬ郡がございます\n"
        "我ら家臣に知行地としてお与えくだされば\n"
        "きちんと治め、豊かにいたします",
    ),
    1609: (
        "空き郡があるようじゃのう\n我ら家臣にお任せあれ\n"
        "知行地として預かった上は、良う治めようぞ",
    ),
    1610: (
        "誰も治めていない郡があります\n"
        "どうか我々家臣に預けてくださいませんか？\n"
        "きちんと治めてご覧に入れます",
    ),
    1611: (
        "誰も治めていない郡があるようだ\n"
        "誰かに統治を任せてはどうだろう\n"
        "きっと良く治めてくれよう",
    ),
    1612: (
        "誰も治めていない郡がありますね\n"
        "どうか我々に預けてくださいませんか？\n"
        "きちんと治めてご覧に入れましょう",
    ),
    1613: (
        "誰も治めていない郡は\n知行として我ら家臣に任せてください\n"
        "きっと豊かにしてみせますぞ！",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1598: ("", "025032", "050505"),
    1599: ("", "050505"),
    1600: ("", "014308000000", "014308000000", "050505"),
    1601: ("023c", "0232", "050505"),
    1602: ("", "014307000000", "050505"),
    **{
        record_id: ("", "050505")
        for record_id in range(1603, 1614)
    },
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {
    1598: 1628,
    1599: 1629,
    1600: 1630,
    1601: 1631,
    1602: 1632,
    1603: 1633,
    1604: 1634,
    1605: 1635,
    1606: 1636,
    1607: 1637,
    1608: 1638,
    1609: 1639,
    1610: 1640,
    1611: 1641,
    1612: 1642,
    1613: 1643,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_RECORD_IDS = {1599, *range(1603, 1614)}

SHARED_AUXILIARY = {
    ("SC", 1598): (
        (
            "关于本家往后的行动，\n为了提升威信，也可以考虑\n加强",
            "的信赖，获取职务。",
        ),
        ("", "025032", "050505"),
    ),
    ("TC", 1598): (
        (
            "關於本家今後的周旋方式，\n不妨加深",
            "的信用以取得職位，\n藉此提高威信亦為手段之一。",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1599): (
        ("可以再向朝廷进献金钱，获取官职，\n提升威信吧。",),
        ("", "050505"),
    ),
    ("TC", 1599): (
        ("或是向朝廷進獻金錢，取得官職來提高威信。",),
        ("", "050505"),
    ),
    ("SC", 1600): (
        (
            "不管怎么说，",
            "已是有国家的大名了，\n统一动乱的战国之世也不是遥不可及了。\n我们也会为",
            "再接再厉的！",
        ),
        ("", "014308000000", "014308000000", "050505"),
    ),
    ("TC", 1600): (
        (
            "總之，",
            "既坐上一國大名，\n大力整頓戰國亂世絕非夢想。\n我等亦樂意為",
            "勵精圖治！",
        ),
        ("", "014308000000", "014308000000", "050505"),
    ),
    ("SC", 1601): (
        ("由于统一了", "，\n本家的威信上升了", "。"),
        ("", "023c", "0232", "050505"),
    ),
    ("TC", 1601): (
        ("由於統一了", "，\n本家的威信上升了", "。"),
        ("", "023c", "0232", "050505"),
    ),
    ("SC", 1604): (
        ("无人治理的郡\n就交给我们家臣吧，\n我们会将它变成富裕之地的。",),
        ("", "050505"),
    ),
    ("TC", 1604): (
        ("無人治理之郡\n就交給我等家臣，\n保證使其化為豐饒之地。",),
        ("", "050505"),
    ),
    ("SC", 1605): (
        ("没有人治理的郡\n请用知行交予我等家臣吧。\n我们会让它变得更加富裕的。",),
        ("", "050505"),
    ),
    ("TC", 1605): (
        ("無人治理之郡\n就作為知行交給我等家臣，\n誓必使其繁榮富足。",),
        ("", "050505"),
    ),
    ("SC", 1606): (
        ("空闲的郡就交给我等家臣吧。\n若有战事，\n我们会率兵出郡，参加战役的。",),
        ("", "050505"),
    ),
    ("TC", 1606): (
        ("無人看管之郡就交給我等家臣。\n打仗時，我等自會從該地率兵助陣。",),
        ("", "050505"),
    ),
    ("SC", 1610): (
        ("有郡没有人治理。\n可以请您交给我等家臣吗？\n我们定会好好治理的。",),
        ("", "050505"),
    ),
    ("TC", 1610): (
        ("有個無人治理之郡\n能否交給我等家臣代管？\n日後誓必讓大人見到治理成效。",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1598: (
        (
            "One way to increase our clanÖs prestige is by gaining the ",
            "Ös trust and receiving a title.",
        ),
        ("", "025032", "050505"),
    ),
    1599: (
        (
            "Or you could bribe the imperial court to obtain the prestige "
            "of an official post.",
        ),
        ("", "050505"),
    ),
    1600: (
        (
            "Either way, now that youÖve become a daimyª in control of a "
            "country, I believe your ambition of uniting the nation is no mere "
            "dream! We, too, will work hard for your sake!",
        ),
        ("", "050505"),
    ),
    1601: (
        (
            "Unifying ",
            " has increased your own clanÖs prestige by ",
            ".",
        ),
        ("", "023c", "0232", "050505"),
    ),
    1604: (
        (
            "Leave the counties with no rulers to us retainers. WeÖll whip "
            "those lands into shape.",
        ),
        ("", "050505"),
    ),
    1605: (
        (
            "Let the retainers govern the counties with no ruler, and weÖll "
            "make the land flourish.",
        ),
        ("", "050505"),
    ),
    1606: (
        (
            "Leave the empty counties to us retainers. TheyÖll make fine "
            "outposts to lead our troops from in times of war.",
        ),
        ("", "050505"),
    ),
    1610: (
        (
            "There are counties without leadership at present. Would you "
            "consider entrusting them to a retainerÖs care?",
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
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B110_C_pristine_base_pc_jp_authoritative_"
    "prestige_court_title_country_holding_daimyo_and_county_fief_requests_"
    "with_explicit_base1598_to1613_pk1628_to1643_mapping_exact_base_pk_"
    "sc_tc_and_pk_en_auxiliary_context_court_official_post_prestige_trust_"
    "role_title_fief_and_chigyouchi_terminology_country_holding_daimyo_"
    "meaning_made_explicit_repeated_1605_1613_frame_exact_reuse_speaker_"
    "voice_and_current_layout_preserved_static_and_runtime_split"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "위신",
        "신용",
        "역직",
        "조정",
        "관직",
        "일국을 다스리는 다이묘",
        "가신인",
        "영지",
        "지행지",
        "군",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 918 required terminology drifted: {required}")
    for forbidden in (
        "국지",
        "국주",
        "지행으로",
        "우리 가신에게",
        "저희 가신에게",
        "郡",
        "。",
        "、",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 918 retained opaque or forbidden term: {forbidden}"
            )
    if raw_translations["15:1605:0"] != CHIGYO_REQUEST_FRAME:
        raise RuntimeError("segment 918 record 1605 fief frame drifted")
    if raw_translations["15:1613:0"] != f"{CHIGYO_REQUEST_FRAME}!":
        raise RuntimeError("segment 918 record 1613 fief frame reuse drifted")
    if (
        EXPECTED_BASE_JP[1605][0].removesuffix("よ")
        != EXPECTED_BASE_JP[1613][0].removesuffix("ぞ！")
    ):
        raise RuntimeError("segment 918 repeated source frame drifted")
    if raw_translations["15:1600:0"].endswith("되었다"):
        raise RuntimeError("segment 918 person-token honorific direction drifted")
    if raw_translations["15:1600:1"][:4] != "님이라면":
        raise RuntimeError("segment 918 first person-token suffix drifted")
    if raw_translations["15:1600:2"][:2] != "님을":
        raise RuntimeError("segment 918 second person-token suffix drifted")
    if set(PK_RECORD_MAP.items()) != {
        (1598, 1628),
        (1599, 1629),
        (1600, 1630),
        (1601, 1631),
        (1602, 1632),
        (1603, 1633),
        (1604, 1634),
        (1605, 1635),
        (1606, 1636),
        (1607, 1637),
        (1608, 1638),
        (1609, 1639),
        (1610, 1640),
        (1611, 1641),
        (1612, 1642),
        (1613, 1643),
    }:
        raise RuntimeError("segment 918 explicit Base-to-PK mapping drifted")


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
    if len(rows) != 21 or len(translations) != 21:
        raise RuntimeError("segment 918 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 918 validated count drifted")
    static_count = sum(
        row["scope_classification"] == "retranslated" for row in rows
    )
    if static_count != 12:
        raise RuntimeError("segment 918 static decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S918",
                "decision_count": len(rows),
                "retranslated": static_count,
                "runtime_fragment_pending": len(rows) - static_count,
                "explicit_pk_mapping": True,
                "canonical_1605_1613_frame_reuse": True,
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
