#!/usr/bin/env python3
"""Build Base authoring segment 831 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment830 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S831.private.v1.jsonl"
SEGMENT = 831
RAW_TRANSLATIONS: dict[str, str] = {
    "15:593:0": (
        "의 회유가 진척되었사옵니다\n"
        "모두 주군을 자비로운 분이라 칭송했사옵니다\n"
        "전쟁이 나면 국인중 일동이 달려와 참전하겠다고도 했사옵니다"
    ),
    "15:594:0": (
        "의 회유를 진행해 왔사옵니다\n"
        "모두 물자를 받고 기뻐했사옵니다\n"
        "다음 전투부터는 국인중 모두가 참전할 듯합니다"
    ),
    "15:595:0": (
        "을(를) 한층 더 회유했소\n"
        "온갖 것이 부족한 난세라… 모두 기뻐하더이다\n"
        "다음부터는 국인중 모두가 참전한다고 하오"
    ),
    "15:596:0": (
        "을(를) 더욱 회유하고 왔사옵니다\n"
        "주군께서 보내신 물자에 모두 감격해 눈물을 흘렸사옵니다\n"
        "다음부터는 거의 전원이 우리 가문을 위해 참전할 듯하옵니다"
    ),
    "15:597:0": (
        "을(를) 진심으로 따르게 했사옵니다\n"
        "전원이 우리 가문을 위해 참전하고 싶다 하였사옵니다\n"
        "전투 때에는 의지하도록 하시지요"
    ),
    "15:598:0": "허허,",
    "15:598:1": (
        "의 사람들\n"
        "우리 가문에 완전히 마음을 두어, 더욱더\n"
        "힘이 되고 싶다…며 기특한 말을 하옵니다"
    ),
    "15:599:0": (
        "을(를) 더욱 회유했습니다\n"
        "다음 전투에서는 상당한 병력을\n"
        "보내 줄 것입니다"
    ),
    "15:600:0": (
        "와의 관계를 돈독히 하고 왔다!\n"
        "다음 전투에는 대군을 보내 주겠지"
    ),
    "15:601:0": (
        "을(를) 한층 더 회유했습니다\n"
        "모두 주군께 진심으로 감사하는 모습\n"
        "전투에는 총출동하여 달려오겠다며 의욕을 보였습니다"
    ),
    "15:602:0": "다시",
    "15:602:1": (
        "을(를) 회유하고 왔습니다\n"
        "이만큼 금품을 들였으니\n"
        "전투 때에는 의지하도록 하시지요"
    ),
    "15:603:0": (
        "의 회유가 끝났다!\n"
        "이제 그 땅에서 주군의 이름을 듣지 않는 날이 없지\n"
        "아예 편입해 버려도 좋지 않겠나?"
    ),
    "15:604:0": (
        "의 회유를 완료했사옵니다\n"
        "모두 주군께 충성을 맹세하고 있사옵니다\n"
        "편입하여 휘하에 두는 것도 한 방법일 듯하옵니다"
    ),
    "15:605:0": (
        "의 회유, 무사히 끝났사옵니다\n"
        "국인중은 모두 주군을 신뢰하고 있사옵니다\n"
        "부디 우리 가문에 편입하시옵소서"
    ),
    "15:606:0": (
        "의 회유는 이제 충분합니다\n"
        "누구나 주군께 감사드리는 지금\n"
        "우리 가문에 편입할 수도 있을 것입니다"
    ),
    "15:607:0": (
        "의 회유 마무리, 훌륭한 성과이옵니다\n"
        "모두 주군을 더없이 칭송하고 있사옵니다\n"
        "우리 가문에 편입할 수도 있겠사옵니다"
    ),
    "15:608:0": (
        "은(는) 이것으로 회유가 완료되었습니다\n"
        "주군에 대한 기대는 더없이 높으니\n"
        "우리 가문에 편입할 수도 있을 듯합니다"
    ),
    "15:609:0": "이로써,",
    "15:609:1": (
        "을(를) 편입하는 것도\n"
        "가능하게 되었사옵니다\n"
        "이제 결정은 주군의 재량에 맡기겠사옵니다"
    ),
    "15:610:0": "이거 참,",
    "15:610:1": (
        "의 사람들\n"
        "완전히 마음이 기울어, 주군의 직속 가신으로 일하고 싶다\n"
        "…며 기특한 말을 하는 자도 나왔사옵니다"
    ),
}
RECORD_ARITIES = {
    593: 1,
    594: 1,
    595: 1,
    596: 1,
    597: 1,
    598: 2,
    599: 1,
    600: 1,
    601: 1,
    602: 2,
    603: 1,
    604: 1,
    605: 1,
    606: 1,
    607: 1,
    608: 1,
    609: 2,
    610: 2,
}
EXPECTED_JP = {
    593: (
        "の懐柔が進みましたぞ\n"
        "皆、殿を慈悲深い方だと申しておりました\n"
        "戦があれば国衆一同、馳せ参じるとも",
    ),
    594: (
        "の懐柔を進めてまいりました\n"
        "物資に皆、喜んでおりました\n"
        "次の参陣よりは国衆皆で参じるようです",
    ),
    595: (
        "をさらに懐柔いたした\n"
        "何かと事欠く乱世…喜んでおりましたわ\n"
        "次よりは、国衆皆で参陣するとのこと",
    ),
    596: (
        "を進めてまいりましたぞ\n"
        "殿からのお志に皆、感涙にむせぶ始末\n"
        "次よりはほぼ全員が、当家に参陣するかと",
    ),
    597: (
        "を心服させてございます\n"
        "全員が、当家に参陣いたしたいと申しました\n"
        "戦の際は頼りにさせてもらいましょう",
    ),
    598: (
        "ほっほっ、",
        "の者ども\n"
        "当家にすっかり気をようして、いや増して\n"
        "お力になりたい…と殊勝なことを申しまする",
    ),
    599: ("をさらに懐柔してきました\n次の戦ではかなりの兵を\n送ってくれるはずです",),
    600: ("との関係を深めてまいった！\n次の戦では大戦力を派遣してくれるだろう",),
    601: (
        "をさらに懐柔いたしました\n"
        "皆、殿に心から感謝している様子\n"
        "戦には総出で駆けつけると勇んでおりました",
    ),
    602: (
        "再度",
        "を懐柔してまいりました\n"
        "これだけ金品を積んだのです\n"
        "戦の際は頼りにさせてもらいましょう",
    ),
    603: (
        "の懐柔が終わったぞ！\n"
        "今や、かの地で殿の名を聞かぬ日はねえ\n"
        "取り込んじまっても、いいんじゃねえか？",
    ),
    604: (
        "懐柔、完了いたしました\n"
        "皆、殿に忠誠を誓っております\n"
        "取り込んで傘下とするも手かと",
    ),
    605: (
        "懐柔、恙なく済みましたぞ\n"
        "国衆は皆、殿を信頼しておりまする\n"
        "是非、当家へ取り込みなされ",
    ),
    606: (
        "の懐柔はもはや十分です\n"
        "誰もが殿への感謝を口にする今\n"
        "当家に取り込むこともできるかと",
    ),
    607: (
        "懐柔の仕上げ、上々の首尾にて\n"
        "これ以上ないほど、殿を褒めており申す\n"
        "当家に取り込むこともかないましょう",
    ),
    608: (
        "はこれにて懐柔完了です\n"
        "殿への期待は、これ以上ないほど高く\n"
        "当家へ取り込むことも可能かと",
    ),
    609: (
        "これにて、",
        "を取り込むことも\n"
        "可能となりましてございます\n"
        "あとは、ご裁量にお任せいたしまする",
    ),
    610: (
        "いやはや、",
        "の者ども\n"
        "完全に気をようして、殿直参として働きたい\n"
        "…などと可愛いことを申す者も出てござる",
    ),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("028c32", "050505") for record_id in range(593, 598)},
    598: ("", "028c32", "050505"),
    **{record_id: ("028c32", "050505") for record_id in range(599, 602)},
    602: ("", "028c32", "050505"),
    **{record_id: ("028c32", "050505") for record_id in range(603, 609)},
    609: ("", "028c32", "050505"),
    610: ("", "028c32", "050505"),
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES = {"15:595:0", "15:598:1", "15:610:1"}
SC_AUXILIARY = {
    593: (
        ("怀柔", "之事有进展了。\n众人都说大人十分仁慈，\n又说若有战事，愿与国众一同奔赴战场。"),
        ("", "028c32", "050505"),
    ),
    594: (
        ("对", "的怀柔有进展了。\n众人见到物资，都喜形于色。\n看来下次开战，国众会一同参战。"),
        ("", "028c32", "050505"),
    ),
    595: (
        ("我等进一步怀柔了", "。\n乱世什么都缺……他们喜不自胜。\n据报，往后国众会一同参战。"),
        ("", "028c32", "050505"),
    ),
    599: (
        ("我们进一步怀柔了", "。\n下次开战时，\n他们应该会派不少士兵过来。"),
        ("", "028c32", "050505"),
    ),
    605: (
        ("顺利怀柔了", "。\n国众都对大人十分信服。\n请务必将他们拉拢到本家来。"),
        ("", "028c32", "050505"),
    ),
    606: (
        ("对", "的怀柔已经做到位了。\n如今人人都对大人齐声感激，\n应当可以拉拢至本家了。"),
        ("", "028c32", "050505"),
    ),
    607: (
        ("怀柔完成得十分顺利。\n他们对大人称赞已极。\n现在可以拉拢到本家来了吧。",),
        ("028c32", "050505"),
    ),
}
TC_AUXILIARY = {
    593: (
        ("懷柔一切順利。\n國眾對大人的菩薩心腸頌聲載道，\n亦表示會於戰時火速助陣。",),
        ("028c32", "050505"),
    ),
    594: (
        ("懷柔無往不利。\n物資令國眾皆大歡喜，\n日後征戰似乎會全體助陣。",),
        ("028c32", "050505"),
    ),
    595: (
        ("已進一步懷柔。\n時值亂世，物資匱乏……國眾皆大歡喜，\n並表示日後會全體助陣。",),
        ("028c32", "050505"),
    ),
    599: (("已加深懷柔。\n下次征戰應會送來眾多兵力。",), ("028c32", "050505")),
    605: (
        ("懷柔諸凡順遂。\n國眾對大人相當信賴，\n務必加以籠絡入本家。",),
        ("028c32", "050505"),
    ),
    606: (
        ("懷柔已十分充足。\n如今國眾無不感謝大人，\n應可籠絡入本家。",),
        ("028c32", "050505"),
    ),
    607: (
        ("懷柔成效驚人，\n國眾皆對大人讚譽有加，\n籠絡入本家亦可行之。",),
        ("028c32", "050505"),
    ),
}
EN_AUXILIARY = {
    593: (
        (
            "WeÖve appeased the ",
            ". They say the lord is a benevolent man. "
            "If war comes, the entire tribe will ride out.",
        ),
        ("", "028c32", "050505"),
    ),
    594: (
        (
            "WeÖve appeased the ",
            ". They were very pleased with the provided goods. "
            "It seems the whole tribe will be willing to aid us during the next campaign.",
        ),
        ("", "028c32", "050505"),
    ),
    595: (
        (
            "WeÖve further appeased the ",
            ". They were short on supplies, so they were pleased to receive our offerings. "
            "The whole tribe will surely join us for our next battle.",
        ),
        ("", "028c32", "050505"),
    ),
    599: (
        (
            "WeÖve further appeased the ",
            ". They will certainly send many men for our next battle.",
        ),
        ("", "028c32", "050505"),
    ),
    605: (
        (
            "Appeasing the ",
            " went without a hitch. Their tribe is extremely loyal. "
            "You should consider having them join the clan.",
        ),
        ("", "028c32", "050505"),
    ),
    606: (
        (
            "We have appeased the ",
            " enough. Now that everyone is feeling grateful, "
            "you should consider adopting them into the clan.",
        ),
        ("", "028c32", "050505"),
    ),
    607: (
        (
            "Winning over the ",
            " was a great success. They speak very highly of you "
            "and will most certainly join the clan if asked.",
        ),
        ("", "028c32", "050505"),
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
    "pristine_base_pc_jp_authoritative_kunishu_full_reinforcement_and_final_"
    "incorporation_results_with_exact_uniform_plus_7_pk_jp_sc_tc_mapping_pk_"
    "en_auxiliary_context_dynamic_kunishu_particles_historical_speaker_voice_"
    "central_kunishu_placation_incorporation_house_and_battle_terms_current_"
    "pc_layout_and_token_skeleton_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    dynamic_boundaries = {
        593: "의 회유",
        594: "의 회유",
        595: "을(를) 한층 더 회유",
        596: "을(를) 더욱 회유",
        597: "을(를) 진심으로 따르게",
        599: "을(를) 더욱 회유",
        600: "와의 관계",
        601: "을(를) 한층 더 회유",
        603: "의 회유",
        604: "의 회유",
        605: "의 회유",
        606: "의 회유",
        607: "의 회유",
        608: "은(는) 이것으로",
    }
    for record_id, prefix in dynamic_boundaries.items():
        if not translations[f"15:{record_id}:0"].startswith(prefix):
            raise RuntimeError(
                f"segment 831 dynamic kunishu-name particle drifted: {record_id}"
            )
    for coordinate, prefix in {
        "15:598:1": "의 사람들\n",
        "15:602:1": "을(를) 회유",
        "15:609:1": "을(를) 편입",
        "15:610:1": "의 사람들\n",
    }.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(
                f"segment 831 dynamic kunishu-name particle drifted: {coordinate}"
            )

    if "진심으로 따르게" not in translations["15:597:0"]:
        raise RuntimeError("segment 831 15:597 心服 meaning drifted")
    if "온갖 것이 부족한 난세라…… 모두 기뻐하더이다" not in translations["15:595:0"]:
        raise RuntimeError("segment 831 15:595 old-speaker おりましたわ register drifted")
    if not translations["15:609:1"].endswith(
        "이제 결정은 주군의 재량에 맡기겠사옵니다"
    ):
        raise RuntimeError("segment 831 15:609 あとは、ご裁量に decision handoff drifted")
    if "직속 가신" not in translations["15:610:1"]:
        raise RuntimeError("segment 831 15:610 direct-retainer meaning drifted")
    joined = "\n".join(translations.values())
    for required in (
        "국인중",
        "회유",
        "편입",
        "참전",
        "우리 가문",
        "직속 가신",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 831 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in (
            "호족",
            "당가",
            "참진",
            "심복",
            "거두어들",
            "끌어들이는 것도 가능",
        )
    ):
        raise RuntimeError("segment 831 retains forbidden legacy terminology")


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
        raise RuntimeError("segment 831 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S831",
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
