#!/usr/bin/env python3
"""Build Base authoring segment 829 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment828 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S829.private.v1.jsonl"
SEGMENT = 829
REPEATED_561_566 = PRIOR.REPEATED_561_566
REPEATED_573_575 = (
    "와 우리 가문의 관계는 아주 좋사옵니다만\n"
    "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
    "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
)
RAW_TRANSLATIONS: dict[str, str] = {
    **{f"15:{record_id}:0": "의" for record_id in range(564, 576)},
    **{
        f"15:{record_id}:1": REPEATED_561_566
        for record_id in range(564, 567)
    },
    "15:567:1": (
        "회유를 끝까지 밀고 나가겠다는 거군\n"
        "나쁘지 않아. 이로써 놈들을 완전히 편입할 수 있겠어\n"
        "에둘러 왔지만, 결국 가장 빠른 길이었군"
    ),
    "15:568:1": (
        "회유를 끝까지 완수하라는 말씀이시군요\n"
        "국인중을 가신으로 편입하는 것이옵니다\n"
        "가문의 힘이 커진다면 더없이 반가운 일이지요"
    ),
    "15:569:1": (
        "회유를 완수하셨군요\n"
        "이제 국인중 편입도 가능할 것이옵니다\n"
        "참으로 훌륭한 조략이었사옵니다"
    ),
    "15:570:1": (
        "회유가 마무리되었군요\n"
        "가신단 못지않은 충성을 보이는 이들입니다\n"
        "이들을 가신단처럼 편입할 기반을 마련합시다"
    ),
    "15:571:1": (
        "회유를 마무리하라는 말씀이시군요\n"
        "근래에는 모두 참전하는 등 가상하게 힘쓰고 있으니\n"
        "이번 회유로 국인중 편입도 가능해질 것이옵니다"
    ),
    "15:572:1": (
        "회유를 최종 단계로 끌어올리시겠사옵니까?\n"
        "과연 주군이시옵니다. 현명하신 판단…\n"
        "편입을 내다보고 회유하겠사옵니다… 철저하게"
    ),
    **{
        f"15:{record_id}:1": REPEATED_573_575
        for record_id in range(573, 576)
    },
}
RECORD_ARITIES = {record_id: 2 for record_id in range(564, 576)}
EXPECTED_JP = {
    **{
        record_id: (
            "の",
            "は心から我らに服してはいない様子\n"
            "我らへの援軍も出し渋っておるようです\n"
            "彼らの力をすべて用いるため、懐柔策を実行いたしませんか",
        )
        for record_id in range(564, 567)
    },
    567: (
        "の",
        "懐柔をやり通すんだな\n"
        "悪くねえ。これで連中を完全に取り込める\n"
        "遠回りだが、一番の近道だったな",
    ),
    568: (
        "の",
        "懐柔をやり通せと\n"
        "国衆を家臣として召し抱えるのですな\n"
        "家の力が増すならば、願ってもなきこと",
    ),
    569: (
        "の",
        "懐柔の完遂ですな\n"
        "これで取り込みも可能となるでしょう\n"
        "天晴な調略にござった",
    ),
    570: (
        "の",
        "懐柔の完遂ですね\n"
        "家中に劣らぬ忠誠を示す彼らです\n"
        "家中同様に取り立てる下地を作りましょう",
    ),
    571: (
        "の",
        "懐柔を仕上げよと\n"
        "近頃は皆での参陣などかいがいしき働きぶり\n"
        "此度の懐柔で取り込みも可能となりましょう",
    ),
    572: (
        "の",
        "懐柔を最終段階へ？\n"
        "さすがは殿、賢明なるご判断…\n"
        "取り込みを見すえ懐柔いたします…完全に",
    ),
    **{
        record_id: (
            "の",
            "と当家の関係は上々ですが\n"
            "我らの傘下に収まるのに抵抗を示す者がおるとか\n"
            "最終的に彼らを取り込むならば、今一度懐柔が必要かと",
        )
        for record_id in range(573, 576)
    },
}
EXPECTED_BASE_GAPS = {
    record_id: ("029632", "028c32", "050505")
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES = {"15:572:1"}
SC_AUXILIARY = {
    569: (
        (
            "完成对",
            "的",
            "的怀柔了。\n如此也可笼络他们。\n好精彩的谋略。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    570: (
        (
            "完成对",
            "的",
            "怀柔了啊。\n"
            "他们展示的忠诚已不亚于家臣。\n"
            "做好和家臣一样提拔的准备吧。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    571: (
        (
            "完成对",
            "的",
            "怀柔啊。\n"
            "近来他们全员参战，十分卖力，\n"
            "这次怀柔也可笼络他们了吧。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    575: (
        (
            "的",
            "与本家关系极好，\n"
            "但似乎还有人不愿被纳入我们麾下。\n"
            "窃以为最后若要笼络他们，还需要再次怀柔。",
        ),
        ("029632", "028c32", "050505"),
    ),
}
TC_AUXILIARY = {
    569: (
        (
            "的",
            "懷柔準備收網是吧。\n"
            "如此一來即可加以籠絡，\n"
            "好謀善斷令人佩服。",
        ),
        ("029632", "028c32", "050505"),
    ),
    570: (
        (
            "的",
            "懷柔將大功告成。\n"
            "彼等忠心耿耿，不比家中遜色，\n"
            "不妨備個等同家中的位子。",
        ),
        ("029632", "028c32", "050505"),
    ),
    571: (
        (
            "的",
            "懷柔要驗收成果……\n"
            "近來彼等助陣孜孜不怠，\n"
            "本次懷柔後應可加以籠絡。",
        ),
        ("029632", "028c32", "050505"),
    ),
    575: (
        (
            "的",
            "與本家關係良好，\n"
            "但聽說仍有人抗拒入我方旗下。\n"
            "若最終欲籠絡彼等，懷柔尚須一次。",
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
    "pristine_base_pc_jp_authoritative_kunishu_final_placation_and_"
    "incorporation_dialogue_with_exact_uniform_plus_7_pk_jp_sc_tc_mapping_"
    "pk_en_auxiliary_context_dynamic_house_and_kunishu_name_particles_"
    "historical_speaker_register_kunishu_vassal_household_and_incorporation_"
    "stage_distinctions_current_pc_layout_and_opcode_skeleton_preserved_"
    "runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in RECORD_ARITIES:
        if translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(
                f"segment 829 exact dynamic possessive drifted: 15:{record_id}:0"
            )
    if len(
        {
            COMMON.source_literals(source_records, record_id)
            for record_id in range(561, 567)
        }
    ) != 1:
        raise RuntimeError("segment 829 561-566 repeated source drifted")
    for record_id in range(564, 567):
        if raw_translations[f"15:{record_id}:1"] != PRIOR.REPEATED_561_566:
            raise RuntimeError(
                f"segment 829 564-566 repeated translation drifted: {record_id}"
            )

    if len(
        {
            COMMON.source_literals(source_records, record_id)
            for record_id in range(573, 576)
        }
    ) != 1:
        raise RuntimeError("segment 829 573-575 repeated source drifted")
    for record_id in range(573, 576):
        if raw_translations[f"15:{record_id}:1"] != REPEATED_573_575:
            raise RuntimeError(
                f"segment 829 573-575 repeated translation drifted: {record_id}"
            )

    dynamic_boundaries = {
        **{record_id: "은(는) 아직" for record_id in range(564, 567)},
        **{record_id: "회유" for record_id in range(567, 573)},
        **{record_id: "와 우리 가문" for record_id in range(573, 576)},
    }
    for record_id, prefix in dynamic_boundaries.items():
        if not translations[f"15:{record_id}:1"].startswith(prefix):
            raise RuntimeError(
                f"segment 829 dynamic kunishu-name boundary drifted: {record_id}"
            )
    if not translations["15:567:1"].endswith(
        "에둘러 왔지만, 결국 가장 빠른 길이었군"
    ):
        raise RuntimeError("segment 829 15:567 detour idiom drifted")
    if "국인중을 가신으로 편입하는 것" not in translations["15:568:1"]:
        raise RuntimeError("segment 829 15:568 vassal incorporation stage drifted")
    if "이들을 가신단처럼 편입할 기반" not in translations["15:570:1"]:
        raise RuntimeError("segment 829 15:570 household incorporation stage drifted")
    if "모두 참전하는 등 가상하게 힘쓰고" not in translations["15:571:1"]:
        raise RuntimeError("segment 829 15:571 commendable service meaning drifted")

    joined = "\n".join(translations.values())
    for required in ("국인중", "원군", "가신", "가신단", "편입", "휘하", "참전"):
        if required not in joined:
            raise RuntimeError(
                f"segment 829 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("호족", "당가", "참진", "심복", "포섭", "등용")
    ):
        raise RuntimeError("segment 829 retains forbidden legacy terminology")


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
        raise RuntimeError("segment 829 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S829",
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
