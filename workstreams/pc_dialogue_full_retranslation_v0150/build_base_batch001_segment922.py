#!/usr/bin/env python3
"""Build Base authoring segment 922 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment921 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S922.private.v1.jsonl"
)
SEGMENT = 922
make_auxiliary_overrides = PREVIOUS.make_auxiliary_overrides
INTERMEDIARY_PROPOSAL_KO = (
    "의 힘은 얕볼 수 없으니\n"
    "누군가를 중개자로 임명해\n"
    "친선을 다져 보는 것은"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1645:0": (
        "은(는) 전쟁을 지휘하시기에는\n"
        "너무 멀리 떨어져 있을지도 모르"
    ),
    "15:1645:1": "\n우리 가문도 제법 커졌",
    "15:1645:2": "까닭에",
    "15:1646:0": "본거지인 ",
    "15:1646:1": (
        "도 좋은 성이오나\n"
        "옮기기에 알맞은 더 넓은 성도\n"
        "우리 세력 안에 있는 듯하옵니다"
    ),
    "15:1647:0": "성주가 없는 성이",
    "15:1647:1": (
        "\n영내를 발전시키기 위해서라도\n"
        "성주를 임명해 보시는 것은"
    ),
    "15:1647:2": "인가",
    "15:1648:0": "외람되오나,",
    "15:1648:1": "을(를)\n성주로 임명해",
    "15:1648:2": "\n반드시 훌륭한 성과를 올리",
    "15:1649:0": (
        "성대에게 성을 맡기기에는\n"
        "아무래도 불안이 너무 크옵니다\n"
        "이 성은 부디"
    ),
    "15:1649:1": "에게…",
    "15:1650:0": (
        "앞으로의 전황을 유리하게 이끌려면\n"
        "맹우인"
    ),
    "15:1650:1": (
        "와(과)의 연계가 중요하옵니다\n"
        "지금 친선을 다져 두시는 것이 어떠하옵니까?"
    ),
    "15:1651:0": "앞으로의 전황에서\n",
    "15:1651:1": (
        "와(과)의 연계가 반드시 필요하고\n"
        "누군가를 중개자로 임명해야 할 때"
    ),
    "15:1652:0": INTERMEDIARY_PROPOSAL_KO,
    "15:1653:0": INTERMEDIARY_PROPOSAL_KO,
    "15:1654:0": "주군 가문인",
    "15:1654:1": "의 힘이 있다면\n영지를 넓힐 수도 있",
    "15:1654:2": (
        "\n그러기 위해 문안드리는 것쯤은 작은 대가이옵니다"
    ),
    "15:1655:0": (
        "와(과)의 친선을 다져 보시지요\n"
        "앞뒤로 적을 둔 우리 가문이오나\n"
        "싸울 상대가 적을수록 이득"
    ),
    "15:1656:0": (
        "막부와 친분을 다져 두면\n"
        "역직 임명도 기대할 수 있"
    ),
    "15:1656:1": "\n권위가 있어 문제",
}
RECORD_ARITIES = {
    1645: 3,
    1646: 2,
    1647: 3,
    1648: 3,
    1649: 2,
    1650: 2,
    1651: 2,
    1652: 1,
    1653: 1,
    1654: 3,
    1655: 1,
    1656: 2,
}
EXPECTED_BASE_JP = {
    1645: (
        "は戦のお指図をするのに\n少々遠すぎるやもし",
        "\n当家も随分大きくな",
        "ゆえ",
    ),
    1646: (
        "本拠・",
        "も良き城なれど\n移転に適した、より広き城も\n"
        "勢力下にはあるよう",
    ),
    1647: (
        "城主がおらぬ城が",
        "\n領内を発展させるためにも\n城主を任じては",
        "か",
    ),
    1648: (
        "不躾ながら、",
        "を\n城主に任じて",
        "\n必ずや良き成果を挙げ",
    ),
    1649: (
        "城代に城を預けるのは\nいささか不安が過ぎるというもの\n"
        "ここは、是非",
        "に…",
    ),
    1650: (
        "今後の戦局を有利に運ぶには\n盟友",
        "との連携が肝心\n今のうちに親睦を深めては？",
    ),
    1651: (
        "今後の戦局において\n",
        "との連携は不可欠かと\n誰かを取次に任命すべき",
    ),
    1652: (
        "の力は侮れず\n誰かに取次を命じて\n親睦を深めては",
    ),
    1653: (
        "の力は侮れず\n誰かに取次を命じて\n親睦を深めては",
    ),
    1654: (
        "主家である",
        "の力があれば\n領地を広げることもでき",
        "\nそのためのご機嫌伺いなら安いもの",
    ),
    1655: (
        "との親睦を深めませぬか\n腹背に敵を抱える当家なれど\n"
        "戦の相手は少ない方がよい",
    ),
    1656: (
        "幕府と懇意にしておれば\n役職の任命も期待でき",
        "\n権威があって困ることは",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1645: (
        "02473F",
        "01434E0400000143C8020000",
        "014368020000",
        "050505",
    ),
    1646: (
        "",
        "02473F",
        "01432C020000050505",
    ),
    1647: (
        "",
        "014352000000",
        "0143B0020000014356020000",
        "050505",
    ),
    1648: (
        "",
        "014301000000",
        "014342010000",
        "01431E040000050505",
    ),
    1649: ("", "014301000000", "050505"),
    1650: ("", "025032", "050505"),
    1651: (
        "",
        "025032",
        "01432C020000050505",
    ),
    1652: (
        "025032",
        "0143B0020000014356020000050505",
    ),
    1653: (
        "025032",
        "0143B0020000014356020000050505",
    ),
    1654: (
        "",
        "025032",
        "01431E040000",
        "050505",
    ),
    1655: (
        "025032",
        "014356020000050505",
    ),
    1656: (
        "",
        "01431E040000",
        "0143E6020000050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1645: (
        "02473F",
        "01435A0400000143D4020000",
        "014374020000",
        "050505",
    ),
    1646: (
        "",
        "02473F",
        "014338020000050505",
    ),
    1647: (
        "",
        "014352000000",
        "0143BC020000014362020000",
        "050505",
    ),
    1648: (
        "",
        "014301000000",
        "014342010000",
        "01432A040000050505",
    ),
    1651: (
        "",
        "025032",
        "014338020000050505",
    ),
    1652: (
        "025032",
        "0143BC020000014362020000050505",
    ),
    1653: (
        "025032",
        "0143BC020000014362020000050505",
    ),
    1654: (
        "",
        "025032",
        "01432A040000",
        "050505",
    ),
    1655: (
        "025032",
        "014362020000050505",
    ),
    1656: (
        "",
        "01432A040000",
        "0143F2020000050505",
    ),
}
PK_RECORD_MAP = {
    1645: 1675,
    1646: 1676,
    1647: 1677,
    1648: 1678,
    1649: 1679,
    1650: 1680,
    1651: 1681,
    1652: 1682,
    1653: 1683,
    1654: 1684,
    1655: 1685,
    1656: 1686,
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1649:1"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    1: ("이 몸", "소인", "나", "저", "소승"),
    82: ("있다", "있습니다", "이옵니다", "입니다", "있사옵니다"),
    322: ("다오", "주시오", "주소서"),
    556: ("다", "입니다", "이오"),
    598: ("이리라", "이겠지요", "이겠지"),
    616: ("었다", "했습니다"),
    688: ("어떻게", "어떠하오"),
    712: ("군", "와", "네"),
    742: ("없다", "없습니다", "없사옵니다"),
    1054: ("듯", "합시다"),
    1102: ("할 수 없", "할 수 없습니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    1: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1],
    82: EXPECTED_BASE_MORPHOLOGY_TERMINALS[82],
    322: EXPECTED_BASE_MORPHOLOGY_TERMINALS[322],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    724: EXPECTED_BASE_MORPHOLOGY_TERMINALS[712],
    754: EXPECTED_BASE_MORPHOLOGY_TERMINALS[742],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1114: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1102],
}

SHARED_AUXILIARY = {
    ("SC", 1645): (
        (
            "明明是战场上的指挥，\n却离得稍微有点远啊。\n"
            "是因为本家也更加辽阔了吧。",
        ),
        ("02473F", "050505"),
    ),
    ("TC", 1645): (
        (
            "要",
            "指揮作戰，\n或許過於遙遠。\n因為本家的勢力已擴大了許多。",
        ),
        ("", "02473F", "050505"),
    ),
    ("SC", 1646): (
        (
            "根据地",
            "虽然是座不错的城，\n但适于迁移的更宽敞的城\n"
            "似乎也在势力下。",
        ),
        ("", "02473F", "050505"),
    ),
    ("TC", 1646): (
        (
            "根據地",
            "雖然是座不錯的城，\n但適於遷移的更寬敞的城\n"
            "似乎也在勢力下。",
        ),
        ("", "02473F", "050505"),
    ),
    ("SC", 1647): (
        ("有个无主之城。\n为了领内的发展，\n任命一位城主如何？",),
        ("", "050505"),
    ),
    ("TC", 1647): (
        ("有個無主之城。\n為了領內的發展，\n任命一位城主如何？",),
        ("", "050505"),
    ),
    ("SC", 1648): (
        ("在下不才，请让", "\n当城主吧。\n一定会立下好成果的。"),
        ("", "014301000000", "050505"),
    ),
    ("TC", 1648): (
        ("在下不才，請讓", "\n當城主吧。\n一定會立下好成果的。"),
        ("", "014301000000", "050505"),
    ),
    ("SC", 1649): (
        (
            "把城交给城代\n有些过于不安啊。\n这儿一定要让",
            "来……",
        ),
        ("", "014301000000", "050505"),
    ),
    ("TC", 1649): (
        (
            "把城交給城代\n有些過於不安啊。\n這兒一定要讓",
            "來……",
        ),
        ("", "014301000000", "050505"),
    ),
    ("SC", 1650): (
        (
            "为了将今后的战局变得有利，\n与盟友",
            "的协作至关重要。\n趁现在加深友好关系如何？",
        ),
        ("", "025032", "050505"),
    ),
    ("TC", 1650): (
        (
            "為了將今後的戰局變得有利，\n與盟友",
            "的協作至關重要。\n趁現在加深友好關系如何？",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1651): (
        (
            "于今后的战局中，\n与",
            "的联合不可或缺吧。\n应任命某人为代理。",
        ),
        ("", "025032", "050505"),
    ),
    ("TC", 1651): (
        (
            "於今後的戰局中，\n與",
            "的聯合不可或缺。\n應任命某人為聯繫者。",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1652): (
        (
            "不可小看",
            "的实力，\n任命某人为代理，\n加深和睦如何？",
        ),
        ("", "025032", "050505"),
    ),
    ("TC", 1652): (
        (
            "不可小看",
            "的實力，\n任命某人為聯繫者，\n加深和睦如何？",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1653): (
        (
            "不可小看",
            "的实力，\n任命某人为代理，\n加深和睦如何？",
        ),
        ("", "025032", "050505"),
    ),
    ("TC", 1653): (
        (
            "不可小看",
            "的實力，\n任命某人為聯繫者，\n加深和睦如何？",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1654): (
        (
            "有主家",
            "的力量，\n扩张领土也并非不可能。\n"
            "为此请个安也不算难事。",
        ),
        ("", "025032", "050505"),
    ),
    ("TC", 1654): (
        (
            "有主家",
            "的力量，\n擴張領土也並非不可能。\n"
            "為此請個安也不算難事。",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1655): (
        (
            "不与",
            "加深友好关系吗？\n虽然本家腹背受敌，\n"
            "但战场上的敌人还是越少越好。",
        ),
        ("", "025032", "050505"),
    ),
    ("TC", 1655): (
        (
            "不與",
            "加深友好關系嗎？\n雖然本家腹背受敵，\n"
            "但戰場上的敵人還是越少越好。",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1656): (
        (
            "手握权势便少困扰。\n若与幕府交好的话，\n"
            "或许可以期待求个官职。",
        ),
        ("", "050505"),
    ),
    ("TC", 1656): (
        (
            "手握權勢便少困擾。\n若與幕府交好的話，\n"
            "或許可以期待求個官職。 ",
        ),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1645: (
        (
            " may be a little too far from the battlefield. Our clanÖs grown "
            "rather large after all.",
        ),
        ("02473F", "050505"),
    ),
    1646: (
        (
            "As great as our current main base at ",
            " is, I think there is a more spacious castle in our territory "
            "that would be more appropriate.",
        ),
        ("", "02473F", "050505"),
    ),
    1647: (
        (
            "There is a castle without a lord. Why not appoint one and task "
            "them with improving the territory?",
        ),
        ("", "050505"),
    ),
    1648: (
        (
            "I would humbly ask that you bestow upon me the title of lord. "
            "I promise you excellent results.",
        ),
        ("", "050505"),
    ),
    1649: (
        (
            "IÖm ill at ease with the thought of entrusting the castle to a "
            "chamberlain. Please, leave it in my hands instead.",
        ),
        ("", "050505"),
    ),
    1650: (
        (
            "In order to gain the upper hand in battle, we should cooperate "
            "closely with our allies, the ",
            ". Why donÖt we deepen our friendship with them?",
        ),
        ("", "025032", "050505"),
    ),
    1651: (
        (
            "A connection with the ",
            " could be vitally important to our battlefield capabilities. "
            "LetÖs appoint an emissary.",
        ),
        ("", "025032", "050505"),
    ),
    1652: (
        (
            "We canÖt underestimate the ",
            ". We should send an emissary to deepen our bonds.",
        ),
        ("", "025032", "050505"),
    ),
    1653: (
        (
            "We canÖt underestimate the ",
            ". We should send an emissary to deepen our bonds.",
        ),
        ("", "025032", "050505"),
    ),
    1654: (
        (
            "With the power of the ",
            " on our side, we could further expand our domain. It wouldnÖt "
            "hurt to pay them a courtesy call.",
        ),
        ("", "025032", "050505"),
    ),
    1655: (
        (
            "How about deepening our bonds with the ",
            "? The fewer enemies we have to face, the better off weÖll be.",
        ),
        ("", "025032", "050505"),
    ),
    1656: (
        (
            "If your standing with the shªgunate is good enough, youÖll likely "
            "be appointed a title. Having a bit of extra authority doesnÖt "
            "hurt.",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B111_A_pristine_base_pc_jp_authoritative_"
    "main_base_relocation_castle_lord_appointment_diplomatic_intermediary_"
    "master_house_and_shogunate_friendship_with_explicit_base1645_1656_"
    "to_pk1675_1686_mapping_exact_base_pk_jp_sc_tc_and_actual_pk_en_"
    "auxiliary_context_pk_opcode_divergences_recorded_project_main_base_"
    "castle_lord_chamberlain_intermediary_master_house_office_authority_"
    "terms_exact_1652_1653_reuse_dynamic_tokens_live_inflection_stems_"
    "current_ko_morphology_terminal_corpus_recorded_current_layout_and_"
    "skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 922 direct Base/PK map drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 922 unexpected Base/PK JP literal divergence")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {
        1645,
        1646,
        1647,
        1648,
        1651,
        1652,
        1653,
        1654,
        1655,
        1656,
    }:
        raise RuntimeError("segment 922 Base/PK opcode divergence set drifted")
    source_1652 = tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, 1652)])
    )
    source_1653 = tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, 1653)])
    )
    if source_1652 != source_1653:
        raise RuntimeError("segment 922 pristine 1652/1653 source equality drifted")
    if (
        raw_translations["15:1652:0"]
        is not raw_translations["15:1653:0"]
    ):
        raise RuntimeError(
            "segment 922 Korean 1652/1653 canonical object reuse drifted"
        )
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "본거지",
        "성주",
        "성대",
        "중개자",
        "주군 가문",
        "막부",
        "역직",
        "권위",
        "친선",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 922 required terminology drifted: {required}")
    for forbidden in (
        "본거·",
        "취차",
        "주가인",
        "주가의",
        "직책",
        "성주에 임명",
        "비위 맞추기",
        "친목",
        "「",
        "」",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 922 forbidden terminology retained: {forbidden}"
            )
    for coordinate, ending in {
        "15:1645:0": "모르",
        "15:1645:1": "커졌",
        "15:1647:1": "것은",
        "15:1648:1": "임명해",
        "15:1648:2": "올리",
        "15:1651:1": "때",
        "15:1652:0": "것은",
        "15:1653:0": "것은",
        "15:1654:1": "있",
        "15:1656:0": "있",
        "15:1656:1": "문제",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 922 live inflection stem drifted: {coordinate}"
            )
    composed_suffix_corpora = {
        "15:1648:1": {
            raw_translations["15:1648:1"] + suffix
            for suffix in EXPECTED_BASE_MORPHOLOGY_TERMINALS[322]
        },
        "15:1651:1": {
            raw_translations["15:1651:1"] + suffix
            for suffix in EXPECTED_BASE_MORPHOLOGY_TERMINALS[556]
        },
        "15:1655:0": {
            raw_translations["15:1655:0"] + suffix
            for suffix in EXPECTED_BASE_MORPHOLOGY_TERMINALS[598]
        },
        "15:1656:1": {
            raw_translations["15:1656:1"] + suffix
            for suffix in EXPECTED_BASE_MORPHOLOGY_TERMINALS[742]
        },
    }
    if composed_suffix_corpora != {
        "15:1648:1": {
            "을(를)\n성주로 임명해다오",
            "을(를)\n성주로 임명해주시오",
            "을(를)\n성주로 임명해주소서",
        },
        "15:1651:1": {
            "와(과)의 연계가 반드시 필요하고\n"
            "누군가를 중개자로 임명해야 할 때다",
            "와(과)의 연계가 반드시 필요하고\n"
            "누군가를 중개자로 임명해야 할 때입니다",
            "와(과)의 연계가 반드시 필요하고\n"
            "누군가를 중개자로 임명해야 할 때이오",
        },
        "15:1655:0": {
            "와(과)의 친선을 다져 보시지요\n"
            "앞뒤로 적을 둔 우리 가문이오나\n"
            "싸울 상대가 적을수록 이득이리라",
            "와(과)의 친선을 다져 보시지요\n"
            "앞뒤로 적을 둔 우리 가문이오나\n"
            "싸울 상대가 적을수록 이득이겠지요",
            "와(과)의 친선을 다져 보시지요\n"
            "앞뒤로 적을 둔 우리 가문이오나\n"
            "싸울 상대가 적을수록 이득이겠지",
        },
        "15:1656:1": {
            "\n권위가 있어 문제없다",
            "\n권위가 있어 문제없습니다",
            "\n권위가 있어 문제없사옵니다",
        },
    }:
        raise RuntimeError("segment 922 composed suffix corpus drifted")
    if (
        raw_translations["15:1649:1"].count("…") != 1
        or translations["15:1649:1"].count("…") != 2
    ):
        raise RuntimeError("segment 922 ellipsis seed/pair drifted")
    if len(raw_translations) != 25 or len(translations) != 25:
        raise RuntimeError("segment 922 fixed visible decision count drifted")


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
    PREVIOUS.PREVIOUS.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_BASE_GAPS,
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
    if len(rows) != 25 or len(validated) != len(translations):
        raise RuntimeError("segment 922 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 922 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S922",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1645,
                    1646,
                    1647,
                    1648,
                    1651,
                    1652,
                    1653,
                    1654,
                    1655,
                    1656,
                ],
                "canonical_base1652_1653_reuse": True,
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
