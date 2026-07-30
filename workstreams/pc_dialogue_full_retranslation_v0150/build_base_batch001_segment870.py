#!/usr/bin/env python3
"""Build Base authoring segment 870 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment856 as CAPTURE
import build_base_batch001_segment869 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S870.private.v1.jsonl"
SEGMENT = 870
ROAD_1136 = (
    "에 가도를 놓는 게 어떠냐?\n"
    "군을 이으면 사람이 오가고 문화도 자라니\n"
    "좋은 일뿐이지 않으냐"
)
ROAD_1137 = (
    "을(를) 가도로 이어 보시지요\n"
    "그 땅은 장차 교통의 요지가 될 군이니\n"
    "가도를 정비해 두어 손해 볼 일은 없사옵니다"
)
ROAD_1138 = (
    "에 가도를 놓는 것이 좋겠소\n"
    "사람과 물자가 풍부한 군을 이어 두면\n"
    "장차 우리 가문에 이익이 될 터이니"
)
ROAD_1139 = (
    "에서 가도를 내도록 합시다\n"
    "발전한 군끼리 이어 놓으면\n"
    "반드시 우리 가문에도 이익이 될 것입니다"
)
ROAD_1140 = (
    "을(를) 가도로 이읍시다\n"
    "풍요로운 군을 길로 이으면\n"
    "병력도 영내에서 움직이기 쉬워질 것이오"
)
ROAD_1141 = (
    "에서 가도를 놓도록 합시다\n"
    "그 땅은 발전하여 교통의 요지가 될 만합니다\n"
    "분명 우리 가문에 이익을 가져다줄 것입니다"
)
ROAD_1142 = (
    "을(를) 가도로 이읍시다\n"
    "풍요로운 군을 잇는 것은\n"
    "전술상 병력을 운용하는 데 이점이 있습니다"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1129:0": "영내에서 간자를 붙잡아",
    "15:1129:2": CAPTURE.CAPTURE_TRANSLATIONS["15:973:2"],
    "15:1129:3": CAPTURE.CAPTURE_TRANSLATIONS["15:973:3"],
    "15:1130:0": "의 이간 공작으로 인해",
    "15:1130:1": "와(과) 교섭 불가",
    "15:1131:0": "의 이간 공작으로 인해",
    "15:1131:1": "와(과) 교섭 불가",
    "15:1132:0": "이(가) 벌인 이간 공작을 저지",
    "15:1133:0": (
        "은(는) 공격로가 제한되어 있어\n"
        "그 때문에 견고한 성이라는 평판"
    ),
    "15:1133:1": "이(가)…\n뭐, 뒷문이 없다면 만들면 될 일",
    "15:1134:0": "의 뒤로 통하는 산길이\n",
    "15:1134:1": "에 있다고 들었",
    "15:1134:2": "\n공격하려면 반드시 정비해 두고 싶사옵니다",
    "15:1135:0": (
        "은(는) 산지에 둘러싸인 요해\n"
        "함락하려면 묘책이 필요"
    ),
    "15:1135:1": "\n예컨대 뒷산으로 부대를 우회시킨다든가…",
    "15:1136:0": ROAD_1136,
    "15:1137:0": ROAD_1137,
    "15:1138:0": ROAD_1138,
    "15:1139:0": ROAD_1139,
    "15:1140:0": ROAD_1140,
    "15:1141:0": ROAD_1141,
    "15:1142:0": ROAD_1142,
}
RECORD_ARITIES = {
    1129: 4,
    1130: 2,
    1131: 2,
    1132: 1,
    1133: 2,
    1134: 3,
    1135: 2,
    **{record_id: 1 for record_id in range(1136, 1143)},
}
EXPECTED_BASE_JP = {
    1129: (
        "領内にて間者を捕らえ",
        "\n",
        "による",
        "が密命とか…\n危ないところ",
    ),
    1130: ("の離間計により", "との交渉不可"),
    1131: ("の離間計により", "との交渉不可"),
    1132: ("による離間計を阻止",),
    1133: (
        "は攻め口が限られており\nそれゆえ堅城との評判",
        "が…\nなに、勝手口がなければ作るまで",
    ),
    1134: (
        "の裏に通ずる山道が\n",
        "にあると耳にし",
        "\n攻め込むならば、ぜひ整備したく",
    ),
    1135: (
        "は山地に囲まれた要害\n攻め落とすには一工夫要",
        "\n例えば、裏山から部隊を回すとか…",
    ),
    1136: (
        "に街道を引くのはどうだ？\n"
        "郡を繋げば、人が行き交い文化も育つ\n"
        "いいことづくめじゃねえか",
    ),
    1137: (
        "を街道で繋いでみては\n"
        "かの地はいずれ交通の要所となる郡\n"
        "街道を整備して損はございませぬ",
    ),
    1138: (
        "に街道を引くが良し\n"
        "人と物が豊かな郡を繋いでおけば\n"
        "いずれ当家の利となりますからな",
    ),
    1139: (
        "より街道を開きましょう\n"
        "発展が進む郡と郡を繋げば\n"
        "必ず当家にも利となりましょう",
    ),
    1140: (
        "を街道にて結びましょうぞ\n"
        "豊かな郡を道で繋がば\n"
        "兵も領内を動きやすくなり申そう",
    ),
    1141: (
        "より街道を引きましょう\n"
        "かの地は発展が進み、交通の要所たりえます\n"
        "きっと当家に利をもたらしてくれるでしょう",
    ),
    1142: (
        "を街道にて繋げましょう\n"
        "豊かな郡を結ぶことは\n"
        "戦術上、兵を動かすのに利がございます",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    1133: (
        "は攻め口が限られ\n落としがたしとの評判",
        "が…\nなに、勝手口がなければ作るまで",
    ),
}
EXPECTED_BASE_GAPS = {
    1129: (
        "",
        "014314020000",
        "025032",
        "023c",
        "014344020000050505",
    ),
    1130: ("025032", "025132", "050505"),
    1131: ("025032", "025132", "050505"),
    1132: ("025032", "050505"),
    1133: ("026532", "01432c020000", "050505"),
    1134: ("026532", "029632", "014314020000", "050505"),
    1135: ("026532", "01435a040000", "050505"),
    **{record_id: ("029632", "050505") for record_id in range(1136, 1143)},
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1129: (
        "",
        "01431a020000",
        "025032",
        "023c",
        "014350020000050505",
    ),
    1133: ("026532", "014338020000", "050505"),
    1134: ("026532", "029632", "01431a020000", "050505"),
    1135: ("026532", "014366040000", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1129:3",
    "15:1133:1",
    "15:1135:1",
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1129:1": "\n"}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1129): (
            ("已于领地内逮捕间谍。\n据说是", "的", "发出密令……\n差点就有麻烦了。"),
            ("", "025032", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1129): (
            ("已於領地內逮捕間諜。\n據說是", "的", "發出密令……\n差點就有麻煩了。"),
            ("", "025032", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1129): (
        (
            "WeÖve captured spies in our territory. They had the ",
            "Ös ",
            " secret orders... That could have been bad.",
        ),
        ("", "025032", "023c", "050505"),
    ),
    **{
        (side, "SC", record_id): (
            ("因", "的离间计，无法与", "進行交涉。"),
            ("", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
        for record_id in (1130, 1131)
    },
    **{
        (side, "TC", record_id): (
            ("由於", "的離間計，無法與", "進行交涉。"),
            ("", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
        for record_id in (1130, 1131)
    },
    **{
        ("pk", "EN", record_id): (
            (
                "Negotiation with the ",
                " is unavailable because of the ",
                "Ös bondbreaker ploy.",
            ),
            ("", "025132", "025032", "050505"),
        )
        for record_id in (1130, 1131)
    },
    **{
        (side, "SC", 1132): (
            ("阻止了", "的离间计。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1132): (("阻止離間計。",), ("025032", "050505"))
        for side in ("base", "pk")
    },
    ("pk", "EN", 1132): (
        ("The ", "Ös bondbreaker ploy has been prevented."),
        ("", "025032", "050505"),
    ),
    **{
        (side, "SC", 1133): (
            ("虽因进攻的方法受到限制，\n才被认为固若金汤……\n那样的话，造出一个后门便可。",),
            ("026532", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1133): (
            ("因", "可攻之處鮮少，\n享有堅城之美譽……\n既然如此，造出一個後門便可啊。"),
            ("", "026532", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1133): (
        (
            "There are only a few angles we can attack ",
            " from. It is reputed to be in a tough location after all... Well, if there isnÖt a good way in, weÖll just have to create our own.",
        ),
        ("", "026532", "050505"),
    ),
    **{
        (side, "SC", 1134): (
            ("听闻", "有条\n通往", "后方的山道。\n要攻打的话，一定要做好准备。"),
            ("", "029632", "026532", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1134): (
            ("聽說在", "有一條\n可通往", "後方的山路。\n若欲進攻則務必進行整備。"),
            ("", "029632", "026532", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1134): (
        (
            "I heard thereÖs a mountain road in ",
            " that leads up behind ",
            ". If we want to attack them, we ought to do some roadwork.",
        ),
        ("", "029632", "026532", "050505"),
    ),
    **{
        (side, "SC", 1135): (
            ("是被山地环绕的要地。\n想攻打的话要花不少心思吧。\n比如让部队从后山迂回什么的……",),
            ("026532", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1135): (
            ("乃四面環山地的要地。\n若欲攻奪則須慎擬對策。\n例如，部隊從後山進攻等等……",),
            ("026532", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1135): (
        (" is located in a strategic position surrounded by mountains. ItÖll take some creative thinking to attack it. For example, sending troops over the mountains from behind...",),
        ("026532", "050505"),
    ),
    **{
        (side, "SC", 1138): (
            ("从", "修建道路吧。\n通到人力发达、物资丰富的郡，\n以后会对本家有利的。"),
            ("", "029632", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1138): (
            ("造路通往", "乃良策。\n該郡物阜民豐，\n必將利於本家。"),
            ("", "029632", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "SC", 1139): (
            ("自", "修路吧。\n连通发达的两郡，\n定会对本家有利的。"),
            ("", "029632", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1139): (
            ("為", "開拓街道吧！\n該郡高度發展，\n建構交通網必將利於本家。"),
            ("", "029632", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "SC", 1140): (
            ("用道路联通", "吧。\n用路连起富裕的郡，\n士兵在领内来往也会方便些。"),
            ("", "029632", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1140): (
            ("利用街道連結", "吧！\n該郡繁榮富足，\n有助於領內兵力調度。"),
            ("", "029632", "050505"),
        )
        for side in ("base", "pk")
    },
}
BASIS = (
    "review_queue_base_msggame_B105_pristine_base_pc_jp_authoritative_spy_"
    "capture_sowing_discord_negotiation_lockout_limited_attack_approaches_"
    "rear_mountain_route_and_road_proposals_with_uniform_plus_8_pk_mapping_"
    "explicit_1133_base_pk_jp_variant_base_authority_base_pk_sc_tc_exact_pk_"
    "en_auxiliary_1129_hidden_newline_preserved_b103_capture_token_canonical_"
    "historical_speaker_register_current_layout_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if "15:1129:1" in raw_translations or "15:1129:1" in translations:
        raise RuntimeError("segment 870 excluded 1129 newline received a decision")
    if COMMON.CORE.source_literals(source_records, 1129)[1:] != (
        "\n",
        "による",
        "が密命とか…\n危ないところ",
    ):
        raise RuntimeError("segment 870 1129 capture token source structure drifted")
    for coordinate, prior_coordinate in (
        ("15:1129:2", "15:973:2"),
        ("15:1129:3", "15:973:3"),
    ):
        if raw_translations[coordinate] != CAPTURE.CAPTURE_TRANSLATIONS[
            prior_coordinate
        ]:
            raise RuntimeError(
                f"segment 870 B103 capture canonical drifted: {coordinate}"
            )
    if COMMON.CORE.source_literals(
        source_records, 1130
    ) != COMMON.CORE.source_literals(source_records, 1131):
        raise RuntimeError("segment 870 1130/1131 exact source pair drifted")
    for literal_id in range(2):
        if raw_translations[f"15:1130:{literal_id}"] != raw_translations[
            f"15:1131:{literal_id}"
        ]:
            raise RuntimeError(
                f"segment 870 1130/1131 exact translation pair drifted: {literal_id}"
            )
    if EXPECTED_BASE_JP[1133] == EXPECTED_PK_JP[1133]:
        raise RuntimeError("segment 870 1133 Base/PK JP variant collapsed")
    if "공격로가 제한되어 있어" not in raw_translations["15:1133:0"]:
        raise RuntimeError("segment 870 1133 limited attack-route meaning drifted")
    if "견고한 성이라는 평판" not in raw_translations["15:1133:0"]:
        raise RuntimeError("segment 870 1133 Base 堅城 reputation meaning drifted")
    if not raw_translations["15:1134:1"].endswith("에 있다고 들었"):
        raise RuntimeError("segment 870 1134 hearsay opcode stem drifted")
    if "뒷문" not in translations["15:1133:1"]:
        raise RuntimeError("segment 870 1133 勝手口 back-door meaning drifted")
    if "뒷산으로 부대를 우회" not in translations["15:1135:1"]:
        raise RuntimeError("segment 870 1135 rear-mountain detour meaning drifted")
    joined = "\n".join(translations.values())
    for required in ("간자", "이간 공작", "가도", "교통의 요지", "함락"):
        if required not in joined:
            raise RuntimeError(f"segment 870 terminology drifted: {required}")
    if any(term in joined for term in ("첩자", "이간계", "당가", "본가")):
        raise RuntimeError("segment 870 retained forbidden terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 870 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S870",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "excluded_nonvisible_decisions": len(
                    EXCLUDED_NONVISIBLE_COORDINATES
                ),
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "base_pk_jp_variant_records": 1,
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
