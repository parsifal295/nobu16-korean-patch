#!/usr/bin/env python3
"""Build Base authoring segment 844 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment843 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S844.private.v1.jsonl"
SEGMENT = 844
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:0": PRIOR.REPEATED_INCITEMENT
        for record_id in range(795, 798)
    },
    "15:798:0": (
        "이(가) 거느린 여러 군은\n"
        "모략에 대한 대비가 허술한 모양\n"
        "잇키로 영내를 뒤흔들어 주"
    ),
    "15:799:0": "지금이야말로",
    "15:799:1": (
        "을(를) 공격할 호기\n"
        "백성을 선동해 우리 가문에 동조시키면\n"
        "적 영지로 진군하기도 수월해지느니"
    ),
    "15:800:0": "대군을 거느린",
    "15:800:1": (
        "이(가)\n"
        "언젠가 우리 가문에 위협이 될 것은 틀림없으니\n"
        "이참에 잇키로 움직임을 봉쇄하고자"
    ),
    "15:801:0": "이(가) 위협이 되어\n인근의",
    "15:801:1": (
        "아군이 출병하기 어려운 모양\n"
        "하지만 백성이 들고일어나면 그들도 움직이지 못할 터"
    ),
    "15:802:0": "적 영지에는 불만을 품은 백성이 많은 모양\n",
    "15:802:1": (
        "일대에서 잇키를 부추기면\n"
        "주변 여러 성에서도 궐기를 기대할 수 있"
    ),
    "15:803:0": (
        "일대에서 잇키를 부추기겠습니다\n"
        "문도의 궐기에 맞추어 진군하여\n"
        "학정에 신음하는 이들을 구"
    ),
    "15:804:0": (
        "을(를) 공격하는 데 걸림돌은 길목의 요새…\n"
        "허나 수비병마저 배반하게 하면\n"
        "요새도 한낱 장식일 뿐"
    ),
    "15:805:0": "제 군단에 선동을",
    "15:805:1": "\n영내 각지에서 잇키가 일어난다면\n",
    "15:805:2": "도 제대로 움직이지 못한다",
    "15:806:0": "이(가)",
    "15:806:1": "에서 벌인",
    "15:806:2": "에 성공",
    "15:807:0": "이(가)",
    "15:807:1": "을(를) 비롯한 여러 성에서 벌인",
    "15:807:2": "에 성공",
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(795, 799)},
    799: 2,
    800: 2,
    801: 2,
    802: 2,
    803: 1,
    804: 1,
    805: 3,
    806: 3,
    807: 3,
}
EXPECTED_JP = {
    **{
        record_id: ("にて民を煽動して\n支配を解かせ",)
        for record_id in range(795, 798)
    },
    798: (
        "が従える諸郡は\n"
        "謀略への備えが乏しい様子\n"
        "一揆にて領内を乱してや",
    ),
    799: (
        "今こそ",
        "攻めの好機\n"
        "民を煽動し、当家に同調させれば\n"
        "敵領の進軍も容易とな",
    ),
    800: (
        "大兵を抱える",
        "が\n"
        "いずれ当家の脅威となるは必定\n"
        "ここは一揆にて動きを封じたく",
    ),
    801: (
        "が脅威となって\n近辺の",
        "味方が兵を出しにくい様子\n"
        "ただ、民が叛けば奴らも動けぬはず",
    ),
    802: (
        "敵領では不満を持つ民が多い様子\n",
        "一帯で一揆を促せば\n周辺の諸城でも決起が望め",
    ),
    803: (
        "一帯で一揆を促します\n"
        "門徒の決起に合わせて進軍し\n"
        "苛政に喘ぐ者らを救",
    ),
    804: (
        "攻めの障害は道中の砦…\n"
        "なれど、守兵さえ叛かせてしまえば\n"
        "砦とてただの置物で",
    ),
    805: (
        "我が軍団に煽動を",
        "\n領国の各地で一揆が起きたとなれば\n",
        "も満足に動けぬ",
    ),
    806: ("が", "の", "に成功"),
    807: ("が", "などの", "に成功"),
}
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("029632", "01431e040000050505")
        for record_id in range(795, 798)
    },
    798: ("026432", "01435a040000050505"),
    799: ("", "026432", "01435a040000050505"),
    800: ("", "026432", "050505"),
    801: ("026432", "014384040000", "050505"),
    802: ("", "026432", "01431e040000050505"),
    803: ("026432", "0143ca000000050505"),
    804: ("026432", "014378010000050505"),
    805: ("", "0143b2030000", "025032", "014356020000050505"),
    806: ("024633", "026432", "023c", "050505"),
    807: ("024633", "026432", "023c", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **{
        record_id: ("029632", "01432a040000050505")
        for record_id in range(795, 798)
    },
    798: ("026432", "014366040000050505"),
    799: ("", "026432", "014366040000050505"),
    800: ("", "026432", "050505"),
    801: ("026432", "014390040000", "050505"),
    802: ("", "026432", "01432a040000050505"),
    803: ("026432", "0143ca000000050505"),
    804: ("026432", "014378010000050505"),
    805: ("", "0143be030000", "025032", "014362020000050505"),
    806: ("024633", "026432", "023c", "050505"),
    807: ("024633", "026432", "023c", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {"15:804:0"}
SC_AUXILIARY = {
    798: (
        (
            "管辖的各郡，\n"
            "看来并未对谋略做出防范。\n"
            "就引发暴乱使领内变得混乱不堪吧。",
        ),
        ("026432", "050505"),
    ),
    799: (
        (
            "如今正是攻打",
            "的大好时机。\n"
            "若配合本家煽动百姓的话，\n"
            "向敌人领地进军可谓轻而易举。",
        ),
        ("", "026432", "050505"),
    ),
    800: (
        (
            "拥有大军的",
            "\n日后必成为本家的威胁。\n现在应发动暴乱将其制约。",
        ),
        ("", "026432", "050505"),
    ),
    801: (
        (
            "的大军正窥伺时机蠢蠢欲动，\n"
            "因此附近的守城士兵只得按兵不动。\n"
            "但若是百姓造反，那他们也动弹不得。",
        ),
        ("026432", "050505"),
    ),
    802: (
        (
            "看来敌领地内有不少百姓抱有不满。\n若促使",
            "一带发生暴乱的话，\n那么周围的各城也会奋起吧。",
        ),
        ("", "026432", "050505"),
    ),
    803: (
        (
            "促使",
            "一带发生暴乱，\n"
            "配合奋起的信徒而进军，\n"
            "拯救受苛政压迫的人们吧。",
        ),
        ("", "026432", "050505"),
    ),
    804: (
        (
            "攻打",
            "的障碍便是要塞。\n"
            "若让守军叛变的话，\n"
            "要塞也不过是个摆设而已。",
        ),
        ("", "026432", "050505"),
    ),
    805: (
        (
            "如果同时多座城发生暴动，\n那么",
            "也没法随心所欲出动了吧。\n请向我军团下达煽动命令。",
        ),
        ("", "025032", "050505"),
    ),
    806: (
        ("对", "的", "成功。"),
        ("024633", "026432", "023c", "050505"),
    ),
    807: (
        ("对", "等的", "成功。"),
        ("024633", "026432", "023c", "050505"),
    ),
}
TC_AUXILIARY = {
    798: (
        (
            "看來",
            "管轄的各郡\n"
            "並未積極籌劃謀略。\n"
            "發動一揆，進攻領內吧。",
        ),
        ("", "026432", "050505"),
    ),
    799: (
        (
            "如今正是攻打",
            "的大好時機。\n"
            "若配合本家煽動百姓的話，\n"
            "向敵人領地進軍可謂輕而易舉。",
        ),
        ("", "026432", "050505"),
    ),
    800: (
        (
            "擁有大軍的",
            "\n日後對本家必造成威脅。\n應趁早發動一揆，加以約束。",
        ),
        ("", "026432", "050505"),
    ),
    801: (
        (
            "由於",
            "大軍正伺機蠢蠢欲動，\n"
            "附近的友方城兵只得按兵不動。\n"
            "但百姓若造反，想必他們也動彈不得吧。",
        ),
        ("", "026432", "050505"),
    ),
    802: (
        (
            "看來敵領地內民怨四起。\n若促使",
            "一帶發生一揆，\n將可能促使周邊各城參戰。",
        ),
        ("", "026432", "050505"),
    ),
    803: (
        (
            "促使",
            "一帶發生一揆。\n"
            "待信徒響應參戰後進軍，\n"
            "拯救飽受苛政壓迫的百姓。",
        ),
        ("", "026432", "050505"),
    ),
    804: (
        (
            "攻打",
            "的障礙便是要塞。\n"
            "若讓守軍叛變的話，\n"
            "要塞也不過是個擺設而已。",
        ),
        ("", "026432", "050505"),
    ),
    805: (
        (
            "若同時讓多個城爆發一揆，\n就能讓",
            "難以抽身了吧。\n還請命令我的軍團執行煽動。",
        ),
        ("", "025032", "050505"),
    ),
    806: (
        ("對", "的", "成功。"),
        ("024633", "026432", "023c", "050505"),
    ),
    807: (
        ("對", "等的", "成功。"),
        ("024633", "026432", "023c", "050505"),
    ),
}
EN_AUXILIARY = {
    798: (
        (
            "The counties under ",
            "Ös rule are ill prepared for unrest. "
            "LetÖs incite a revolt to take them down.",
        ),
        ("", "026432", "050505"),
    ),
    799: (
        (
            "This is the perfect time to attack ",
            ". WeÖll sow unrest among the people. "
            "If we can earn the peopleÖs sympathy, taking their territory will be a breeze.",
        ),
        ("", "026432", "050505"),
    ),
    800: (
        (
            " has a large army. If we ignore them, theyÖll surely become a threat. "
            "We should cut their growth short with a revolt.",
        ),
        ("026432", "050505"),
    ),
    801: (
        (
            " is a threat, it seems that even our allies are hesitant to send troops "
            "into that area. If their people were to turn against them, however, "
            "they wouldnÖt be able to fight back.",
        ),
        ("026432", "050505"),
    ),
    802: (
        (
            "There are many in the enemy territory who feel dissatisfied. "
            "If we incite a revolt around ",
            ", that may kick off rebellion in the surrounding castles too.",
        ),
        ("", "026432", "050505"),
    ),
    803: (
        (
            "I urge you to incite a revolt around ",
            ". When their own clan rises against them, we will march to save them "
            "from their tyranny.",
        ),
        ("", "026432", "050505"),
    ),
    804: (
        (
            "A fortress stands between us and an attack on ",
            ". But if we make short work of the defenders, a fortress is merely "
            "a pile of stone and wood.",
        ),
        ("", "026432", "050505"),
    ),
    805: (
        (
            "LetÖs incite a revolt in the province. If we start rebellions in various "
            "territories, then the ",
            " wonÖt be able to move as they please.",
        ),
        ("", "025032", "050505"),
    ),
    806: (
        (" successfully completed the ", " of ", "."),
        ("024633", "023c", "026432", "050505"),
    ),
    807: (
        (" successfully completed the ", " of ", " and others."),
        ("024633", "023c", "026432", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): value
        for side in ("base", "pk")
        for record_id, value in SC_AUXILIARY.items()
    },
    **{
        (side, "TC", record_id): value
        for side in ("base", "pk")
        for record_id, value in TC_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
BASIS = (
    "pristine_base_pc_jp_authoritative_popular_and_ikki_incitement_proposals_"
    "runtime_stems_and_success_ui_with_uniform_plus_7_pk_jp_sc_tc_mapping_"
    "pk_en_auxiliary_context_dynamic_enemy_location_action_corps_and_list_"
    "tokens_historical_terminology_subject_object_particle_and_opcode_order_"
    "verified_current_pc_layout_and_isolated_reverse_overlay_runtime_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    source_anchor = COMMON.CORE.source_literals(source_records, 775)
    for record_id in range(775, 798):
        if COMMON.CORE.source_literals(source_records, record_id) != source_anchor:
            raise RuntimeError(
                f"segment 844 repeated incitement source drifted: {record_id}"
            )
    for record_id in range(795, 798):
        if raw_translations[f"15:{record_id}:0"] != PRIOR.REPEATED_INCITEMENT:
            raise RuntimeError(
                f"segment 844 B/C repeated incitement translation drifted: {record_id}"
            )

    particle_expectations = {
        "15:798:0": "이(가) ",
        "15:799:1": "을(를) ",
        "15:800:1": "이(가)\n",
        "15:801:0": "이(가) ",
        "15:802:1": "일대에서 ",
        "15:803:0": "일대에서 ",
        "15:804:0": "을(를) ",
        "15:805:2": "도 ",
        "15:806:0": "이(가)",
        "15:806:1": "에서 벌인",
        "15:807:0": "이(가)",
        "15:807:1": "을(를) 비롯한 여러 성에서 벌인",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(
                f"segment 844 dynamic subject/object particle drifted: {coordinate}"
            )
    if not translations["15:800:0"].endswith("거느린"):
        raise RuntimeError("segment 844 15:800 dynamic enemy prenominal assembly drifted")
    if not translations["15:801:1"].startswith("아군이 출병하기 어려운"):
        raise RuntimeError("segment 844 15:801 nearby allied sortie subject drifted")
    if "주변 여러 성에서도 궐기" not in translations["15:802:1"]:
        raise RuntimeError("segment 844 15:802 surrounding-castle uprising drifted")
    if (
        "문도의 궐기" not in translations["15:803:0"]
        or "학정에 신음하는 이들" not in translations["15:803:0"]
    ):
        raise RuntimeError("segment 844 15:803 門徒/苛政 meaning drifted")
    if raw_translations["15:805:0"] != "제 군단에 선동을":
        raise RuntimeError("segment 844 15:805 opcode-completed corps command drifted")
    if raw_translations["15:805:1"] != "\n영내 각지에서 잇키가 일어난다면\n":
        raise RuntimeError("segment 844 15:805 domain revolt condition drifted")

    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "잇키",
        "선동",
        "군",
        "아군",
        "문도",
        "학정",
        "궐기",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 844 incitement terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("당가", "일규", "봉기", "민심", "지배를 풀게 하")
    ):
        raise RuntimeError("segment 844 retained forbidden legacy terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_blank_coordinates=set(),
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 844 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S844",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
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
