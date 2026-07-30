#!/usr/bin/env python3
"""Build Base authoring segment 828 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment827 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S828.private.v1.jsonl"
SEGMENT = 828
REPEATED_549_554 = (
    "을(를) 회유하는 것이 어떠하옵니까?\n"
    "우리 가문과 관계가 좋아지면 전시에는 원군을 기대할 수 있사옵니다"
)
REPEATED_561_566 = (
    "은(는) 아직 진심으로 우리를 따르지 않는 듯하옵니다\n"
    "우리에게 원군을 보내는 것도 꺼리는 듯하옵니다\n"
    "그들의 힘을 온전히 쓰려면 회유책을 펴지 않으시겠사옵니까?"
)
RAW_TRANSLATIONS: dict[str, str] = {
    **{f"15:{record_id}:0": "의" for record_id in range(553, 564)},
    **{
        f"15:{record_id}:1": REPEATED_549_554
        for record_id in range(553, 555)
    },
    "15:555:1": (
        "회유를 계속하겠다는 건가\n"
        "지금 우리를 따르는 자가 절반뿐인 건 사실이지\n"
        "나머지 놈들도 내버려 둘 수는 없겠군"
    ),
    "15:556:1": (
        "회유를 계속하라는 뜻, 알겠사옵니다\n"
        "우리 편은 많을수록 든든한 법\n"
        "남은 절반도 모두 따르게 해 보이겠사옵니다"
    ),
    "15:557:1": (
        "회유를 계속한다…\n"
        "흠, 절반의 원군으로는 아직 부족하다는 말씀이시로군\n"
        "나도 꼭 같은 생각을 하고 있었소"
    ),
    "15:558:1": (
        "회유를 더 진행하라는 말씀이시군요\n"
        "지금 우리 가문 편에 선 자는 과연 절반가량\n"
        "성공하면 국인중 전원이 원군으로 나설 것이옵니다"
    ),
    "15:559:1": (
        "회유를 한층 더하라는 말씀이시군요\n"
        "지금 참전하겠다는 자는 어림잡아 절반\n"
        "나머지 절반도 편입하라는 명이시옵니다"
    ),
    "15:560:1": (
        "에게 한층 더 회유를…\n"
        "맡겨 주시옵소서!\n"
        "지금의 두 배가 우리 가문을 위해 참전하게 하겠사옵니다!"
    ),
    **{
        f"15:{record_id}:1": REPEATED_561_566
        for record_id in range(561, 564)
    },
}
RECORD_ARITIES = {record_id: 2 for record_id in range(553, 564)}
EXPECTED_JP = {
    **{
        record_id: (
            "の",
            "を懐柔いたしませんか？\n"
            "当家との関係をより良くすれば、戦時には援軍が期待できましょう",
        )
        for record_id in range(553, 555)
    },
    555: (
        "の",
        "懐柔を続けるのか\n"
        "確かに今、俺らに従っているのは半数だ\n"
        "残りの連中も放ってはおけねえよな",
    ),
    556: (
        "の",
        "懐柔続行の旨、承知\n"
        "味方は多いほど頼もしゅうござる\n"
        "残り半数、すべて従えてみせましょうぞ",
    ),
    557: (
        "の",
        "懐柔の続行…\n"
        "ふむ、半数の援軍ではまだ足りぬと\n"
        "わしも全く同じことを考えておりましたぞ",
    ),
    558: (
        "の",
        "懐柔を進めよと\n"
        "確かに今、当家に味方する者は半数程度\n"
        "成功すれば国衆総員で援軍に参りましょう",
    ),
    559: (
        "の",
        "懐柔をさらに、と\n"
        "今、参陣せんという者は、見立てでは半数\n"
        "残る半数も取り込めとの命でござるな",
    ),
    560: (
        "の",
        "にさらなる懐柔を…\n"
        "お任せくだされ！\n"
        "今の倍、当家に参陣させてみせましょう！",
    ),
    **{
        record_id: (
            "の",
            "は心から我らに服してはいない様子\n"
            "我らへの援軍も出し渋っておるようです\n"
            "彼らの力をすべて用いるため、懐柔策を実行いたしませんか",
        )
        for record_id in range(561, 564)
    },
}
EXPECTED_BASE_GAPS = {
    record_id: ("029632", "028c32", "050505")
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES = {"15:557:1", "15:560:1"}
SC_AUXILIARY = {
    557: (
        (
            "继续怀柔",
            "的",
            "……\n嗯，一半的援军还不够，\n老夫方才也这么想了。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    558: (
        (
            "要推进对",
            "的",
            "的怀柔啊。\n"
            "如今追随本家之人的确只有一半，\n"
            "若是成功，国众想必会全部加入援军。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    559: (
        (
            "要进一步怀柔",
            "的",
            "啊。\n"
            "如今看来，愿意参战者不过半数。\n"
            "您是命令我们继续拉拢剩下的一半吧。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    563: (
        (
            "的",
            "看起来并未诚心臣服于我们。\n"
            "他们似乎并不甘愿派兵救援我们。\n"
            "为了彻底使用他们的兵力，不如实行怀柔之计吧。",
        ),
        ("029632", "028c32", "050505"),
    ),
}
TC_AUXILIARY = {
    557: (
        (
            "的",
            "懷柔續行……\n"
            "嗯，半數援軍仍嫌不足的話，\n"
            "我亦完全贊同。",
        ),
        ("029632", "028c32", "050505"),
    ),
    558: (
        (
            "的",
            "懷柔繼續……\n"
            "目前來看，順從本家者約莫半數。\n"
            "若能成事，國眾應該會全體參加援軍。",
        ),
        ("029632", "028c32", "050505"),
    ),
    559: (
        (
            "的",
            "懷柔更進一步……\n"
            "依微臣之見，目前願助陣者為半數，\n"
            "意在籠絡其餘半數是吧。",
        ),
        ("029632", "028c32", "050505"),
    ),
    563: (
        (
            "的",
            "似乎未真心服從我方，\n"
            "派出援軍似乎也不情不願。\n"
            "為了完全運用彼等之力，是否要施行懷柔政策？",
        ),
        ("029632", "028c32", "050505"),
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
}
BASIS = (
    "pristine_base_pc_jp_authoritative_kunishu_placation_half_to_full_"
    "reinforcement_progress_dialogue_with_exact_uniform_plus_7_pk_jp_sc_tc_"
    "mapping_pk_en_auxiliary_context_dynamic_house_and_kunishu_name_"
    "particles_historical_speaker_register_current_pc_layout_and_opcode_"
    "skeleton_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in RECORD_ARITIES:
        if translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(
                f"segment 828 exact dynamic possessive drifted: 15:{record_id}:0"
            )
    if REPEATED_549_554 != PRIOR.RAW_TRANSLATIONS["15:549:1"]:
        raise RuntimeError("segment 828 cross-segment 549-554 translation drifted")
    for record_id in range(553, 555):
        if raw_translations[f"15:{record_id}:1"] != REPEATED_549_554:
            raise RuntimeError(
                f"segment 828 553-554 repeated translation drifted: {record_id}"
            )
    if len(
        {
            COMMON.source_literals(source_records, record_id)
            for record_id in range(549, 555)
        }
    ) != 1:
        raise RuntimeError("segment 828 549-554 repeated source drifted")

    if len(
        {
            COMMON.source_literals(source_records, record_id)
            for record_id in range(561, 567)
        }
    ) != 1:
        raise RuntimeError("segment 828 561-566 repeated source drifted")
    for record_id in range(561, 564):
        if raw_translations[f"15:{record_id}:1"] != REPEATED_561_566:
            raise RuntimeError(
                f"segment 828 561-563 repeated translation drifted: {record_id}"
            )

    dynamic_boundaries = {
        553: "을(를) 회유",
        554: "을(를) 회유",
        **{record_id: "회유" for record_id in range(555, 560)},
        560: "에게 한층 더 회유",
        **{record_id: "은(는) 아직" for record_id in range(561, 564)},
    }
    for record_id, prefix in dynamic_boundaries.items():
        if not translations[f"15:{record_id}:1"].startswith(prefix):
            raise RuntimeError(
                f"segment 828 dynamic kunishu-name boundary drifted: {record_id}"
            )
    if not translations["15:557:1"].endswith(
        "나도 꼭 같은 생각을 하고 있었소"
    ):
        raise RuntimeError("segment 828 15:557 elderly first-person voice drifted")
    if not translations["15:559:1"].endswith(
        "나머지 절반도 편입하라는 명이시옵니다"
    ):
        raise RuntimeError("segment 828 15:559 incorporation terminology drifted")

    joined = "\n".join(translations.values())
    for required in ("국인중", "원군", "우리 가문", "참전", "진심으로 우리를 따르지"):
        if required not in joined:
            raise RuntimeError(
                f"segment 828 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("호족", "당가", "참진", "심복", "포섭")
    ):
        raise RuntimeError("segment 828 retains forbidden legacy terminology")


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
        raise RuntimeError("segment 828 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S828",
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
