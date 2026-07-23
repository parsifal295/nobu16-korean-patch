#!/usr/bin/env python3
"""Build Base authoring segment 853 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment851 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S853.private.v1.jsonl"
SEGMENT = 853
CASTLE_ASSAULT_CANONICAL_893_925 = (
    "다가올 공성에 대비하여\n"
    "미리 적의 힘을 깎아 둔다면\n"
    "손쉽게 공략할 수 있을 터…"
)
REPEATED_WEAK_POINT_TRANSLATION = (
    "우리의 적,",
    "의 급소는\n",
    "(이)라 추측하옵는바\n미리 성벽을 무너뜨려 두고자 하옵니다",
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:916:0": "지금이라면",
    "15:916:1": "에 간자를 보내\n그 방비를 무너뜨릴 수도 있사오니\n부디,",
    "15:916:2": "허가를…",
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in (917, 922)
        for literal_id, translation in enumerate(REPEATED_WEAK_POINT_TRANSLATION)
    },
    "15:918:0": "이번에 공격할",
    "15:918:1": "의 성벽을 무너뜨리는 일\n부디 이",
    "15:918:2": "에게",
    "15:918:3": "\n시노비를 다루는 데는 자신이",
    "15:919:0": "견고한 성을 함락하려면 먼저 뒤쪽의 허점부터…\n",
    "15:919:1": "의 성벽에 공작을 벌여\n그곳 공략에 도움이",
    "15:920:0": "의 성주는",
    "15:920:1": "…\n이런 난적을 상대할 때는\n사전 공작이 진가를 발휘하",
    "15:921:0": "은(는) 해이한 보초뿐\n수하를 잠입시키기도 쉽다",
    "15:921:1": "\n공략을 위해 방비를 무너뜨려 두고자 하옵니다",
    "15:923:0": "싸움은 머리를 써야지!\n먼저 성벽이라도 부숴 두면\n편해지는 법이지",
    "15:924:0": "공성에 앞서 공작이오?\n그렇군, 이러면 병력 소모도\n막을 수 있겠구려",
    "15:925:0": CASTLE_ASSAULT_CANONICAL_893_925,
}
RECORD_ARITIES = {
    916: 3,
    917: 3,
    918: 4,
    919: 2,
    920: 2,
    921: 2,
    922: 3,
    923: 1,
    924: 1,
    925: 1,
}
EXPECTED_JP = {
    916: (
        "今ならば",
        "に間者を放ち\nその防備を崩すも可能にて\nどうか、",
        "許可を…",
    ),
    917: (
        "我らが敵、",
        "の急所は\n",
        "と推察する次第なれば\n先んじて城壁を崩しておこうかと",
    ),
    918: (
        "この度攻める",
        "の城壁崩し\nぜひこの",
        "に",
        "\n忍びの扱いには自信が",
    ),
    919: (
        "堅城を落とすにはまず搦手から…\n",
        "の城壁に細工を仕掛け\n同地攻略の助けと",
    ),
    920: (
        "の城主は",
        "…\nこのような難敵を相手取るときは\n事前の工作が物を言",
    ),
    921: (
        "は気の抜けた歩哨ばかり\n手の者を忍ばせるのも容易",
        "\n攻略のため、防備を壊しておきたく",
    ),
    922: (
        "我らが敵、",
        "の急所は\n",
        "と推察する次第なれば\n先んじて城壁を崩しておこうかと",
    ),
    923: (
        "戦は頭を使わねえとなあ！\n先に城壁でも壊しておきゃ\n楽できるってもんよ",
    ),
    924: (
        "城攻めに先駆けて工作ですか\nなるほど、これで兵力の消耗も\n防げましょうな",
    ),
    925: (
        "来るべき城攻めに備えて\n事前に敵の力を削いでおけば\n容易に攻め込めるはず…",
    ),
}
EXPECTED_BASE_GAPS = {
    916: ("", "026432", "01438a040000", "050505"),
    917: ("", "025032", "026432", "050505"),
    918: ("", "026432", "024635", "0143b2030000", "014352000000050505"),
    919: ("", "026432", "014394000000050505"),
    920: ("026432", "024833", "0143ca000000050505"),
    921: ("026432", "01432c020000", "050505"),
    922: ("", "025032", "026432", "050505"),
    923: ("", "050505"),
    924: ("", "050505"),
    925: ("", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    916: ("", "026432", "014396040000", "050505"),
    918: ("", "026432", "024635", "0143be030000", "014352000000050505"),
    921: ("026432", "014338020000", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:916:2",
    "15:919:0",
    "15:920:1",
    "15:925:0",
}
SC_AUXILIARY = {
    916: (
        ("现在向", "放出间谍的话，\n也应能瓦解其防备。\n请予以准许……"),
        ("", "026432", "050505"),
    ),
    917: (
        ("我等之敌", "的要害在于", "，\n应该首先摧毁城墙。"),
        ("", "025032", "026432", "050505"),
    ),
    918: (
        (
            "此次攻打",
            "的破坏城墙任务，\n还请交给我",
            "。\n本人对潜伏谍报很有自信。",
        ),
        ("", "026432", "024635", "050505"),
    ),
    919: (
        (
            "要攻下坚固的城首先要从其弱点开始……\n对",
            "的城墙用点花招，\n来帮助该地的攻略。",
        ),
        ("", "026432", "050505"),
    ),
    920: (
        ("的城主是", "……\n以此等强敌为对手时，\n有必要事先搞点小动作。"),
        ("026432", "024833", "050505"),
    ),
    921: (
        ("里净是些松懈的哨兵，\n派部下潜入是很容易的。\n为了攻略，破坏其防备。",),
        ("026432", "050505"),
    ),
    922: (
        ("我等之敌", "的要害\n便在于", "，\n应该首先摧毁城墙。"),
        ("", "025032", "026432", "050505"),
    ),
}
TC_AUXILIARY_COMMON = {
    916: (
        ("現在向", "放出間諜的話，\n也應能瓦解其防備。\n請予以准許……"),
        ("", "026432", "050505"),
    ),
    917: (
        ("我方敵人", "的要害\n推測應是", "，\n首先摧毀其城牆吧。"),
        ("", "025032", "026432", "050505"),
    ),
    918: (
        (
            "此次進攻",
            "的破壞城牆任務，\n還請交給",
            "效勞。\n潛伏諜報我有自信。",
        ),
        ("", "026432", "024635", "050505"),
    ),
    919: (
        (
            "要攻下堅城首先要從其弱點開始……\n對",
            "的城牆用點花招，\n來幫助該地的攻略。",
        ),
        ("", "026432", "050505"),
    ),
    920: (
        ("的城主是", "……\n以此等強敵為對手時，\n有必要事先搞點小動作。"),
        ("026432", "024833", "050505"),
    ),
    921: (
        ("裡盡是鬆懈懶散的哨兵，\n派部下潛入易如反掌。\n為了攻略，破壞其防備。",),
        ("026432", "050505"),
    ),
}
TC_BASE_922 = (
    ("已確定我方敵人", "的\n要害是", "，\n首先摧毀其城牆。"),
    ("", "025032", "026432", "050505"),
)
TC_PK_922 = (
    ("敵方", "的要害大抵就是", "，\n不如先摧毀其城牆吧。"),
    ("", "025032", "026432", "050505"),
)
EN_AUXILIARY = {
    916: (
        (
            "Let me send my spies to ",
            " to break down its defenses. Just give me the word.",
        ),
        ("", "026432", "050505"),
    ),
    917: (
        (
            "If I had to guess, IÖd say that ",
            " is the ",
            "Ös weak point. As such, IÖd like to smash down its walls.",
        ),
        ("", "026432", "025032", "050505"),
    ),
    918: (
        (
            "Please entrust the task of bringing down ",
            "Ös walls to me. I, ",
            ", have the utmost faith in my ninja arts.",
        ),
        ("", "026432", "024635", "050505"),
    ),
    919: (
        (
            "To take down a strong castle, one must attack its weakest points. "
            "I will carry out my handiwork on ",
            "Ös walls to aid your assault.",
        ),
        ("", "026432", "050505"),
    ),
    920: (
        (
            " is the lord of ",
            ". WeÖd better be well prepared when dealing with such a formidable foe.",
        ),
        ("024833", "026432", "050505"),
    ),
    921: (
        (
            " is full of distracted sentries, so itÖll be easy to sneak in. "
            "Let me sabotage their defenses from within so you may capture it.",
        ),
        ("026432", "050505"),
    ),
    922: (
        (
            "If I had to guess, IÖd say that ",
            " is the ",
            "Ös weak point. As such, IÖd like to smash down its walls.",
        ),
        ("", "026432", "025032", "050505"),
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
        for record_id, value in TC_AUXILIARY_COMMON.items()
    },
    ("base", "TC", 922): TC_BASE_922,
    ("pk", "TC", 922): TC_PK_922,
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
BASIS = (
    "pristine_base_pc_jp_authoritative_siege_wall_sabotage_weak_point_spy_"
    "infiltration_and_preparation_with_uniform_plus_7_pk_jp_mapping_pc_sc_"
    "tc_and_pk_en_auxiliary_context_dynamic_castle_force_officer_action_"
    "tokens_historical_speaker_register_current_layout_opcode_skeleton_"
    "exact_repeated_source_canonicals_and_isolated_reverse_overlay_verified_"
    "runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if COMMON.COMMON.CORE.source_literals(
        source_records, 917
    ) != COMMON.COMMON.CORE.source_literals(source_records, 922):
        raise RuntimeError("segment 853 917/922 exact source group drifted")
    for literal_id in range(3):
        if raw_translations[f"15:917:{literal_id}"] != raw_translations[
            f"15:922:{literal_id}"
        ]:
            raise RuntimeError(
                f"segment 853 917/922 raw translation drifted: {literal_id}"
            )
        if translations[f"15:917:{literal_id}"] != translations[
            f"15:922:{literal_id}"
        ]:
            raise RuntimeError(
                f"segment 853 917/922 resolved translation drifted: {literal_id}"
            )
    if COMMON.COMMON.CORE.source_literals(
        source_records, 925
    ) != COMMON.COMMON.CORE.source_literals(source_records, 893):
        raise RuntimeError("segment 853 893/925 exact source canonical drifted")
    if raw_translations["15:925:0"] != CASTLE_ASSAULT_CANONICAL_893_925:
        raise RuntimeError("segment 853 893/925 translation canonical drifted")
    if "시노비" not in translations["15:918:3"]:
        raise RuntimeError("segment 853 15:918 忍び terminology drifted")
    if "뒤쪽의 허점" not in translations["15:919:0"]:
        raise RuntimeError("segment 853 15:919 搦手 context translation drifted")
    joined = "\n".join(translations.values())
    for required in ("공성", "공작", "성벽", "방비", "간자", "시노비"):
        if required not in joined:
            raise RuntimeError(
                f"segment 853 siege/sabotage terminology drifted: {required}"
            )
    if any(term in joined for term in ("닌자", "뒷문", "세공", "첩자")):
        raise RuntimeError("segment 853 retained forbidden legacy terminology")


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
        excluded_blank_literals={},
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 853 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S853",
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
