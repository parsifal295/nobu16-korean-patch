#!/usr/bin/env python3
"""Build Base authoring segment 837 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment836 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S837.private.v1.jsonl"
SEGMENT = 837
REPEATED_FAILURE_698_709 = (
    "의 편입은 실패했습니다\n"
    "당분간 상황을 지켜보도록 하지요"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:689:0": "의 편입이 완료되었습니다\n",
    "15:689:1": (
        "이(가) 우리 가문의 영토에 편입됩니다\n"
        "…영내의 이물 하나를 제거했군요"
    ),
    "15:690:0": "의 편입이\n순조롭게 이루어져 무엇보다 다행이옵니다\n",
    "15:690:1": "도 얻게 되어 더없이 경사스럽사옵니다",
    "15:691:0": "기뻐하시옵소서!\n",
    "15:691:1": "의 편입이 잘 이루어졌사옵니다\n이제부터,",
    "15:691:2": "도 우리 가문의 일부이옵니다",
    "15:692:0": "이(가) 우리 가문에 귀순했습니다!\n이로써",
    "15:692:1": "은(는)\n우리 영지가 되겠군요",
    "15:693:0": "은(는) 편입에 응했다\n이제부터",
    "15:693:1": "은(는) 우리 가문의 것이야",
    "15:694:0": "은(는) 편입에 응했습니다\n이로써",
    "15:694:1": "은(는)",
    "15:694:2": "의 영지입니다\n여러모로 수월해지겠군요",
    "15:695:0": "이(가) 우리 가문에 귀순했사옵니다\n해냈군요!\n",
    "15:695:1": "은(는) 우리 가문의 것이옵니다",
    "15:696:0": "은(는) 편입에 응하",
    "15:696:1": "\n이후 그 병력은 군의 병력으로 계상되\n",
    "15:696:2": "님이 우리 가문의 가신단에 합류하",
    "15:697:0": "은(는) 편입에 응하",
    "15:697:1": "\n이후 그 병력은 군의 병력으로\n계상되",
    "15:698:0": REPEATED_FAILURE_698_709,
}
RECORD_ARITIES = {
    689: 2,
    690: 2,
    691: 3,
    692: 2,
    693: 2,
    694: 3,
    695: 2,
    696: 3,
    697: 2,
    698: 1,
}
EXPECTED_JP = {
    689: (
        "の取り込みが完了しました\n",
        "が当家の領土に組み込まれます\n"
        "…領内の異物が一つ、排除できましたな",
    ),
    690: (
        "取り込みの儀\nうまく運びましてなによりにございます\n",
        "も得られ、祝着至極に存じまする",
    ),
    691: (
        "お喜びくだされい！\n",
        "の取り込みがうまくいきましたわ\nこれよりは、",
        "も当家の内じゃ",
    ),
    692: ("が当家に降りました！\nこれで", "は\n我らの領地となりますね"),
    693: ("は取り込みに応じた\nこれより", "は当家のものよ"),
    694: (
        "は取り込みに応じました\nこれで",
        "は",
        "の領地です\n何かとやりやすくなりますね",
    ),
    695: ("が当家に降りました\nやりましたな！\n", "は当家のものですぞ"),
    696: (
        "は取り込みに応じ",
        "\n以後、その兵力は郡のものとして計上され\n",
        "殿が当家の家中に加わ",
    ),
    697: (
        "は取り込みに応じ",
        "\n以後、その兵力は郡のものとして\n計上され",
    ),
    698: ("の取込は失敗しました\nいましばらく様子を見るといたしましょう",),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("023c", "029632", "050505") for record_id in (689, 690, 692, 693, 695)},
    691: ("", "023c", "029632", "050505"),
    694: ("023c", "029632", "014307000000", "050505"),
    696: (
        "028c32",
        "014314020000",
        "024833",
        "014336040000050505",
    ),
    697: ("028c32", "014314020000", "01433c040000050505"),
    698: ("028c32", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    696: (
        "028c32",
        "01431a020000",
        "024833",
        "014342040000050505",
    ),
    697: ("028c32", "01431a020000", "014348040000050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {"15:689:1"}
SC_AUXILIARY = {
    692: (
        ("归顺本家了！\n如此一来，", "\n就是我们的领地了。"),
        ("023c", "029632", "050505"),
    ),
    696: (
        (
            "已响应笼络。\n之后该兵力将计入郡中，\n",
            "大人将加入主家家中。",
        ),
        ("028c32", "024833", "050505"),
    ),
    697: (
        ("已响应笼络。\n之后该兵力将计入郡中。",),
        ("028c32", "050505"),
    ),
}
TC_AUXILIARY = {
    692: (
        ("已向本家投降！\n如此一來，", "\n就成為我方領地了。"),
        ("023c", "029632", "050505"),
    ),
    696: (
        (
            "已響應籠絡。\n之後該兵力將計入郡中，\n",
            "大人將加入主家家中。",
        ),
        ("028c32", "024833", "050505"),
    ),
    697: (
        ("已響應籠絡。\n之後該兵力將計入郡中。",),
        ("028c32", "050505"),
    ),
}
EN_AUXILIARY = {
    692: (
        ("The ", " have submitted to us! ", " is ours now!"),
        ("", "023c", "029632", "050505"),
    ),
    696: (
        (
            "The ",
            " have responded to our request. From here on, their forces will be "
            "added to the countyÖs and Lord ",
            " will serve as our retainer.",
        ),
        ("", "028c32", "024833", "050505"),
    ),
    697: (
        (
            "The ",
            " have responded to our request. From here on, their forces will be added to the countyÖs.",
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
    "pristine_base_pc_jp_authoritative_kunishu_incorporation_success_"
    "territory_result_retainer_accession_county_force_accounting_and_"
    "failure_fragments_with_exact_uniform_plus_7_pk_jp_sc_tc_mapping_pk_en_"
    "auxiliary_context_dynamic_kunishu_territory_lord_house_and_faction_"
    "tokens_historical_speaker_register_current_pc_layout_and_opcode_"
    "skeleton_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if COMMON.source_literals(source_records, 684)[1] != "は":
        raise RuntimeError("segment 837 15:684 topic source anchor drifted")
    if COMMON.source_literals(source_records, 694)[1] != "は":
        raise RuntimeError("segment 837 15:694 topic source drifted")
    if raw_translations["15:694:1"] != PRIOR.RAW_TRANSLATIONS["15:684:1"]:
        raise RuntimeError("segment 837 684/694 exact topic translation drifted")
    if COMMON.source_literals(source_records, 696)[0] != COMMON.source_literals(
        source_records, 697
    )[0]:
        raise RuntimeError("segment 837 696/697 exact source stem drifted")
    if raw_translations["15:696:0"] != raw_translations["15:697:0"]:
        raise RuntimeError("segment 837 696/697 exact translation stem drifted")
    if "영내의 이물 하나" not in raw_translations["15:689:1"]:
        raise RuntimeError("segment 837 689 dehumanizing foreign-element voice drifted")
    if not raw_translations["15:693:1"].endswith("우리 가문의 것이야"):
        raise RuntimeError("segment 837 693 assertive personality ending drifted")
    if "\n해냈군요!\n" not in raw_translations["15:695:0"]:
        raise RuntimeError("segment 837 695 congratulatory personality ending drifted")

    dynamic_boundaries = {
        689: "의 편입",
        693: "은(는) 편입",
        694: "은(는) 편입",
        696: "은(는) 편입",
        697: "은(는) 편입",
        698: "의 편입",
    }
    for record_id, prefix in dynamic_boundaries.items():
        if not translations[f"15:{record_id}:0"].startswith(prefix):
            raise RuntimeError(
                f"segment 837 dynamic incorporation boundary drifted: {record_id}"
            )
    for record_id in (692, 695):
        if not translations[f"15:{record_id}:0"].startswith("이(가) 우리 가문"):
            raise RuntimeError(
                f"segment 837 dynamic submission boundary drifted: {record_id}"
            )
    if not translations["15:696:2"].startswith("님이 우리 가문의 가신단"):
        raise RuntimeError("segment 837 officer retainer token subject drifted")
    if "군의 병력으로 계상" not in translations["15:696:1"]:
        raise RuntimeError("segment 837 county force accounting drifted")
    if "군의 병력으로\n계상" not in translations["15:697:1"]:
        raise RuntimeError("segment 837 county force accounting stem drifted")

    joined = "\n".join(translations.values())
    for required in ("편입", "영토", "영지", "가신단", "군의 병력", "귀순"):
        if required not in joined:
            raise RuntimeError(
                f"segment 837 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("호족", "당가", "참진", "심복", "포섭", "거두어들")
    ):
        raise RuntimeError("segment 837 retains forbidden legacy terminology")


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
        raise RuntimeError("segment 837 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S837",
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
