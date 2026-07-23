#!/usr/bin/env python3
"""Build Base authoring segment 836 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment835 as B_PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S836.private.v1.jsonl"
SEGMENT = 836
RAW_TRANSLATIONS: dict[str, str] = {
    "15:677:0": (
        "의 분들을 가신단에 편입하시지요\n"
        "가신단에서 우리와 어깨를 나란히 하기를\n"
        "그들도 바라고 있을 것입니다"
    ),
    "15:678:0": (
        "을(를) 편입하심이 어떻겠습니까\n"
        "국인중으로서 잘 협력해 주었으나\n"
        "이 힘은 역시 주군의 지휘 아래에서라야 빛날 것이옵니다"
    ),
    "15:679:0": (
        "의 분들을 가신으로\n"
        "맞이하는 것이 어떻겠습니까?\n"
        "이제 한 식구나 다름없는 사이이니까요"
    ),
    "15:680:0": "이제는",
    "15:680:1": (
        "의 사람들을\n"
        "휘하에 들일 때가 되었으리라\n"
        "그들도 이를 바랄 터"
    ),
    "15:681:0": (
        "의 분들을 가신으로\n"
        "맞이하는 것이 어떻겠습니까?\n"
        "그들에게도 나쁘지 않은 제안일 듯합니다…"
    ),
    "15:682:0": (
        "을(를) 휘하에 들이시지요\n"
        "그편이 부리기에도 수월할 듯하옵니다"
    ),
    "15:683:0": "이제부터",
    "15:683:1": "은(는)\n",
    "15:683:2": "에게 충성을 다하",
    "15:683:3": "\n마음껏 부려 주",
    "15:684:0": "을(를) 편입해 줬다!\n…그런 셈이니\n",
    "15:684:1": "은(는)",
    "15:684:2": "의 것이야!",
    "15:685:0": "의 편입이 완료되었사옵니다\n",
    "15:685:1": "은(는) 우리 가문의 것이 되었사옵니다",
    "15:686:0": "이(가) 편입에 응했사옵니다\n이제부터,",
    "15:686:1": "은(는) 우리 가문의 영토이옵니다",
    "15:687:0": "은(는) 편입에 응했습니다\n",
    "15:687:1": (
        "은(는) 우리 가문의 영토에 편입됩니다\n"
        "…이로써 그들에게 가신단과 같은 대우를 할 수 있습니다"
    ),
    "15:688:0": "을(를) 편입했사옵니다\n",
    "15:688:1": (
        "은(는) 우리 가문의 것이옵니다… 다만…\n"
        "지금껏 있던 것이 없어지니 허전하구려"
    ),
}
RECORD_ARITIES = {
    677: 1,
    678: 1,
    679: 1,
    680: 2,
    681: 1,
    682: 1,
    683: 4,
    684: 3,
    685: 2,
    686: 2,
    687: 2,
    688: 2,
}
EXPECTED_JP = {
    677: (
        "の方々を取り込みましょう\n"
        "家中にて我らと肩を並べることを\n"
        "彼らも望んでいるはずです",
    ),
    678: (
        "を取り込まれてはいかが\n"
        "国衆としてよく協力してくれたが\n"
        "やはりこの力は殿の采配の下でこそ",
    ),
    679: (
        "の方々を家臣として\n"
        "お迎えできませんか？\n"
        "もう同胞とも言える関係ですから",
    ),
    680: (
        "そろそろ",
        "の面々を\n"
        "傘下に加えるべき時であろう\n"
        "彼らもそれを望むはずだ",
    ),
    681: (
        "の方々を家臣として\n"
        "迎えてはいかがでしょう？\n"
        "あちらにとっても悪くない話かと…",
    ),
    682: ("を傘下に加えましょう\nその方が使い勝手がよろしいかと",),
    683: ("これより", "は\n", "に忠誠を尽く", "\nいかようにも用いて"),
    684: ("を取り込んでやったぞ\n…ってことで\n", "は", "のもんだ！"),
    685: ("の取り込み、完了いたしました\n", "は当家のものとなりましたぞ"),
    686: ("が取り込みに応じましたぞ\nこれより、", "は当家の領土にござる"),
    687: (
        "は取り込みに応じました\n",
        "は当家の領土に編入されます\n"
        "…これで彼らに家中並の待遇を与えられる",
    ),
    688: (
        "を取り込み申した\n",
        "は当家のものです…ただ…\n"
        "今まであったものがないのも、寂しいですな",
    ),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("028c32", "050505") for record_id in (677, 678, 679, 681, 682)},
    680: ("", "028c32", "050505"),
    683: (
        "",
        "028c32",
        "025032",
        "0143b4010000",
        "014342010000050505",
    ),
    684: ("023c", "029632", "014307000000", "050505"),
    **{
        record_id: ("023c", "029632", "050505")
        for record_id in range(685, 689)
    },
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    683: (
        "",
        "028c32",
        "025032",
        "0143ba010000",
        "014342010000050505",
    ),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:681:0",
    "15:684:0",
    "15:687:1",
    "15:688:1",
}
SC_AUXILIARY = {
    679: (
        (
            "可否接纳",
            "的各位\n为家臣？\n我们的关系已称得上是同胞了。",
        ),
        ("", "028c32", "050505"),
    ),
    683: (
        ("从现在开始，\n", "将效忠", "。\n请随意吩咐。"),
        ("", "028c32", "025032", "050505"),
    ),
    686: (
        ("接受拉拢啦。\n往后", "就是本家的领土了。"),
        ("023c", "029632", "050505"),
    ),
    687: (
        (
            "接受拉拢了。\n",
            "会被编入本家的领土。\n"
            "……如此一来，他们也可以获得与家臣一样的待遇了。",
        ),
        ("023c", "029632", "050505"),
    ),
    688: (
        (
            "拉拢了",
            "。\n",
            "归本家所有了……只是……\n"
            "以往一直存在的东西要消失了，还真叫人寂寞。",
        ),
        ("", "023c", "029632", "050505"),
    ),
}
TC_AUXILIARY = {
    679: (
        ("能否將", "諸位納入家臣？\n如今關係密切，可謂同胞。"),
        ("", "028c32", "050505"),
    ),
    683: (
        ("從現在開始，\n", "將效忠", "。\n請儘管吩咐。"),
        ("", "028c32", "025032", "050505"),
    ),
    686: (
        ("順利籠絡囉。\n", "從今以後就是本家的領土。"),
        ("023c", "029632", "050505"),
    ),
    687: (
        (
            "已順利籠絡。\n",
            "則納入本家的領土。\n"
            "……如此一來，彼等就能享有家中同等待遇。",
        ),
        ("023c", "029632", "050505"),
    ),
    688: (
        (
            "已成功籠絡。\n",
            "歸本家所有……只是……\n"
            "少了個過招的對手，亦令人頗感空虛。",
        ),
        ("023c", "029632", "050505"),
    ),
}
EN_AUXILIARY = {
    679: (
        (
            "Why donÖt we welcome the ",
            " as our retainers? WeÖre already close enough to call them our brothers in arms.",
        ),
        ("", "028c32", "050505"),
    ),
    683: (
        (
            "From now on the ",
            " will swear fealty to the ",
            ". You may direct us as you see fit.",
        ),
        ("", "028c32", "025032", "050505"),
    ),
    686: (
        (
            "The ",
            " are willing to join you. ",
            " will be added to your territory.",
        ),
        ("", "023c", "029632", "050505"),
    ),
    687: (
        (
            "The ",
            " have agreed to join. ",
            " will be added to the clanÖs territory. "
            "Please treat our men as if they were your own.",
        ),
        ("", "023c", "029632", "050505"),
    ),
    688: (
        (
            "The ",
            " have joined your clan. ",
            " is now yours...but IÖll miss what we had.",
        ),
        ("", "023c", "029632", "050505"),
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
    "pristine_base_pc_jp_authoritative_kunishu_final_incorporation_proposals_"
    "and_success_results_with_exact_uniform_plus_7_pk_jp_sc_tc_mapping_pk_"
    "en_auxiliary_context_dynamic_kunishu_territory_lord_and_faction_tokens_"
    "historical_speaker_register_kunishu_household_territory_and_retainer_"
    "distinctions_current_pc_layout_and_opcode_skeleton_preserved_runtime_"
    "assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    exact_source_groups = {
        677: (662, 665, 674),
        678: (663, 666, 675),
        679: (667,),
        680: (668,),
        681: (669,),
        682: (670,),
    }
    for record_id, prior_ids in exact_source_groups.items():
        anchor = COMMON.source_literals(source_records, record_id)
        if any(COMMON.source_literals(source_records, prior_id) != anchor for prior_id in prior_ids):
            raise RuntimeError(
                f"segment 836 B/C exact source group drifted: {record_id}"
            )
    exact_translation_groups = {
        "15:677:0": "15:662:0",
        "15:678:0": "15:663:0",
        "15:679:0": "15:667:0",
        "15:680:0": "15:668:0",
        "15:680:1": "15:668:1",
        "15:681:0": "15:669:0",
        "15:682:0": "15:670:0",
    }
    for coordinate, prior_coordinate in exact_translation_groups.items():
        if raw_translations[coordinate] != B_PRIOR.RAW_TRANSLATIONS[prior_coordinate]:
            raise RuntimeError(
                f"segment 836 B/C exact translation drifted: {coordinate}"
            )

    dynamic_boundaries = {
        677: "의 분들을 가신단에 편입",
        678: "을(를) 편입",
        679: "의 분들을 가신",
        681: "의 분들을 가신",
        682: "을(를) 휘하",
        685: "의 편입",
        686: "이(가) 편입",
        687: "은(는) 편입",
        688: "을(를) 편입",
    }
    for record_id, prefix in dynamic_boundaries.items():
        if not translations[f"15:{record_id}:0"].startswith(prefix):
            raise RuntimeError(
                f"segment 836 dynamic kunishu boundary drifted: {record_id}"
            )
    if translations["15:680:0"] != "이제는":
        raise RuntimeError("segment 836 15:680 lead fragment drifted")
    if not translations["15:680:1"].startswith("의 사람들을\n"):
        raise RuntimeError("segment 836 15:680 kunishu possessive drifted")
    if translations["15:684:1"] != "은(는)":
        raise RuntimeError("segment 836 15:684 territory topic particle drifted")
    for record_id in (685, 686, 687, 688):
        literal_id = 1
        if not translations[f"15:{record_id}:{literal_id}"].startswith("은(는)"):
            raise RuntimeError(
                f"segment 836 territory token subject drifted: {record_id}"
            )

    joined = "\n".join(translations.values())
    for required in ("국인중", "편입", "가신단", "영토", "휘하", "충성"):
        if required not in joined:
            raise RuntimeError(
                f"segment 836 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("호족", "당가", "참진", "심복", "포섭", "거두어들")
    ):
        raise RuntimeError("segment 836 retains forbidden legacy terminology")


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
        raise RuntimeError("segment 836 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S836",
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
