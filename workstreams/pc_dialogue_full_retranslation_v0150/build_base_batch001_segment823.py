#!/usr/bin/env python3
"""Build Base authoring segment 823 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment821 as COMMON
import build_base_batch001_segment824 as B100_B


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S823.private.v1.jsonl"
SEGMENT = 823
RAW_TRANSLATIONS: dict[str, str] = {
    "15:492:0": "적의 편에 설지, 우리 편이 될지…\n",
    "15:492:1": "의 동향이 마음에 걸리오\n금품으로 환심을 사 두는 것이 좋겠소",
    "15:493:0": "밑천이 조금 들겠습니다만\n",
    "15:493:1": "의 분들에게\n선물을 보내 두지 않으시겠습니까?",
    "15:494:0": "을(를) 회유합시다\n금품을 요구하겠지만\n전시에는 도움을 기대할 수 있습니다",
    "15:495:0": "국인중과는 친하게 지내는 것이 상책\n전시에 의지할 수 있으니 말이다!\n금전을 조금 내주어도 상관없겠지",
    "15:496:0": "금전을 보내 국인중을 회유\n합시다! 그들의 환심을\n사면 원군을 보내 줄 것입니다!",
    "15:497:0": "전시에 원군을 바라는 것은\n아니지만, 평소부터 국인중에게 금전을\n보내 회유해 두어야지…",
    "15:498:0": "금전을 보내\n국인중을 회유합시다… 성공하면\n전시에 든든한 힘이 될 것이옵니다",
    "15:499:0": "거금을 들여서라도 국인중을\n회유해야 하옵니다. 적의 편에\n붙게 두면 모든 수고가 헛됩니다!",
    "15:500:0": "국인중은 든든하면서도 성가신\n존재… 지금 금품을 보내서라도\n우리 편으로 끌어들일 국인중은…",
    "15:501:0": "국인중 회유책을 추진합시다\n금전이 다소 들겠습니다만\n그들의 힘은 전시에 꼭 필요합니다",
    "15:502:0": "금품을 조금 빌려 주실 수 없겠소?\n",
    "15:502:1": "의 무리를\n회유할 수 없을까 싶어서 말이오…",
    "15:503:0": "국인중 분들도 고생이 많군요\n적의 편에 섰다가 우리 편이 되었다가…\n선물로 달랠 수 없을까요?",
    "15:504:0": "원군으로 믿음직한 국인중에게는\n평소부터 물품을 보내 유대를\n이어 두어야 할까…",
    "15:505:0": "국인중에게 선물을 보냅시다\n다음 싸움에서는 우리 편이 되어\n주면 좋겠습니다만…",
    "15:506:0": "국인중이 적의 편에 서면 성가십니다\n평소부터 선물을 건네\n회유해 둡시다",
    "15:507:0": "을(를) 회유해 두",
    "15:507:1": "까\n적과 맞댄 경계에도 가까우니\n전시에는 부리기 좋은 패가 되",
}
RECORD_ARITIES = {
    492: 2,
    493: 2,
    494: 1,
    **{record_id: 1 for record_id in range(495, 502)},
    502: 2,
    **{record_id: 1 for record_id in range(503, 507)},
    507: 2,
}
EXPECTED_JP = {
    492: (
        "敵につくか、味方となるか…\n",
        "の動向が気になる\n金品で歓心を買うが良いかと",
    ),
    493: (
        "少々元手が必要になりますが\n",
        "の皆さんに\n贈り物をしておきませんか？",
    ),
    494: (
        "を懐柔しましょう\n金品を要求されるでしょうが\n戦時には助力が期待できます",
    ),
    495: (
        "国衆は仲良くしておくに限る\n戦の時に頼れるからな！\n多少金銭を与えても構うまい",
    ),
    496: (
        "金銭を贈って国衆を懐柔\nしましょう！　彼らの歓心を\n買えば援軍を出してくれます！",
    ),
    497: (
        "戦時の援軍に期待する訳でも\nないが、普段から国衆には金銭\nを贈って手懐けておくに限る…",
    ),
    498: (
        "金銭を贈って国衆を懐柔\nいたしましょう…成功すれば\n戦時に頼れる存在になりますぞ",
    ),
    499: (
        "大枚を叩いてでも国衆を\n手懐けねばなりませぬ。敵方に\n付かれては元も子もない！",
    ),
    500: (
        "国衆は頼もしくもあり厄介でも\nある存在…今、金品を贈ってで\nも味方につけたい国衆は…",
    ),
    501: (
        "国衆懐柔の方策を進めましょう\n多少金銭は入用となりますが\n彼らの力は戦時に欠かせません",
    ),
    502: (
        "ちと金品を拝借できませぬか？\n",
        "の連中を\n懐柔できんかと思ってのう…",
    ),
    503: (
        "国衆の方々も大変ですね\n敵についたり味方になったり…\n贈り物で何とかできませんか？",
    ),
    504: (
        "援軍で頼りになる国衆には\n普段から物品を贈って絆を\nつないでおくべきか…",
    ),
    505: (
        "国衆の方に贈り物をしましょう\n次の戦の時、味方になって\nくれると良いのですけれど…",
    ),
    506: (
        "国衆は敵に回られると厄介です\n普段から贈り物を渡して\n懐柔しておきましょう",
    ),
    507: (
        "を懐柔してお",
        "か\n敵との境にも近いため\n戦では扱いやすい駒とな",
    ),
}
EXPECTED_BASE_GAPS = {
    492: ("", "028c32", "050505"),
    493: ("", "028c32", "050505"),
    494: ("028c32", "050505"),
    **{record_id: ("", "050505") for record_id in range(495, 502)},
    502: ("", "028c32", "050505"),
    **{record_id: ("", "050505") for record_id in range(503, 507)},
    507: ("028c32", "01432a010000", "01435a040000050505"),
}
EXPECTED_PK_JP_GAPS = {
    **{record_id: gaps for record_id, gaps in EXPECTED_BASE_GAPS.items() if record_id < 507},
    507: ("028c32", "01432a010000", "014366040000050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:492:0",
    "15:497:0",
    "15:498:0",
    "15:500:0",
    "15:502:1",
    "15:503:0",
    "15:504:0",
    "15:505:0",
}
AUXILIARY_OVERRIDES = {
    ("base", "SC", 507): (
        ("要不先来怀柔一下", "吧。\n由于很接近敌方边境，\n应该会有利于战势吧。"),
        ("", "028c32", "050505"),
    ),
    ("pk", "SC", 507): (
        ("要不先来怀柔一下", "吧。\n由于很接近敌方边境，\n应该会有利于战势吧。"),
        ("", "028c32", "050505"),
    ),
    ("base", "TC", 507): (
        (
            "要不先來懷柔一下",
            "吧。\n因為它也很接近敵方邊境，\n所以應該也有利於運用在戰事上吧。",
        ),
        ("", "028c32", "050505"),
    ),
    ("pk", "TC", 507): (
        (
            "要不先來懷柔一下",
            "吧。\n因為它也很接近敵方邊境，\n所以應該也有利於運用在戰事上吧。",
        ),
        ("", "028c32", "050505"),
    ),
    ("pk", "EN", 507): (
        (
            "Should we try to placate the ",
            "? Their close proximity to the enemy may make them a valuable pawn in the war.",
        ),
        ("", "028c32", "050505"),
    ),
}
BASIS = (
    "pristine_base_pc_jp_authoritative_kunishu_placation_dialogue_with_exact_"
    "uniform_plus_7_pk_jp_sc_tc_mapping_pk_en_auxiliary_context_dynamic_"
    "kunishu_name_particles_central_kunishu_terminology_historical_speaker_"
    "register_current_pc_layout_and_opcode_skeleton_preserved_runtime_"
    "assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if (
        COMMON.source_literals(source_records, 492)[0]
        != COMMON.source_literals(source_records, 511)[0]
    ):
        raise RuntimeError("segment 823 492:0/511:0 cross-boundary source repeat drifted")
    if (
        raw_translations["15:492:0"] != "적의 편에 설지, 우리 편이 될지…\n"
        or raw_translations["15:492:0"] != B100_B.RAW_TRANSLATIONS["15:511:0"]
    ):
        raise RuntimeError("segment 823 492:0 cross-boundary translation anchor drifted")
    dynamic_boundaries = {
        "15:492:1": "의 동향",
        "15:493:1": "의 분들에게\n",
        "15:494:0": "을(를) 회유",
        "15:502:1": "의 무리를\n",
        "15:507:0": "을(를) 회유해 두",
    }
    for coordinate, prefix in dynamic_boundaries.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(
                f"segment 823 dynamic kunishu-name particle drifted: {coordinate}"
            )
    if not translations["15:507:1"].startswith("까\n"):
        raise RuntimeError("segment 823 15:507 imperative-question stem drifted")
    if not translations["15:507:1"].endswith("패가 되"):
        raise RuntimeError("segment 823 15:507 historical pawn stem drifted")
    if not translations["15:498:0"].startswith(
        "금전을 보내\n국인중을 회유합시다"
    ):
        raise RuntimeError("segment 823 15:498 natural placation phrasing drifted")
    if "보내 회유해 두어야지" not in translations["15:497:0"]:
        raise RuntimeError("segment 823 15:497 placation-stage meaning drifted")
    if not translations["15:502:0"].startswith("금품을 조금 빌려 주실 수 없겠소?"):
        raise RuntimeError("segment 823 15:502 elder request voice drifted")
    if not translations["15:503:0"].startswith("국인중 분들도 고생이 많군요"):
        raise RuntimeError("segment 823 15:503 respectful modern voice drifted")
    if not translations["15:504:0"].startswith(
        "원군으로 믿음직한 국인중에게는\n"
    ):
        raise RuntimeError("segment 823 15:504 reliable-reinforcement meaning drifted")
    joined = "\n".join(translations.values())
    for required in ("국인중", "회유", "원군", "금전", "금품", "전시"):
        if required not in joined:
            raise RuntimeError(
                f"segment 823 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in (
            "호족",
            "용병",
            "스카우트",
            "길들이다",
            "길들여",
            "다루기 쉬운 말",
        )
    ):
        raise RuntimeError("segment 823 retains forbidden legacy terminology")


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
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 823 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S823",
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
