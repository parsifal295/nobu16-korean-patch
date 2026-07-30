#!/usr/bin/env python3
"""Build Base authoring segment 841 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment840 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = PRIOR.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S841.private.v1.jsonl"
SEGMENT = 841
RAW_TRANSLATIONS: dict[str, str] = {
    "15:749:0": "서둘러 병사를 긁어모아야겠소이다…\n",
    "15:749:1": (
        "을(를) 적이 노리고 있소이다\n"
        "다소의 희생은 눈감고 결행할 수밖에 없겠소이다"
    ),
    "15:750:0": "서둘러 병사를 모아야 하옵니다!\n",
    "15:750:1": "에 다가오는 적을\n막아 내야 하옵니다!",
    "15:751:0": "어서 병사를 모아야 한다!\n이대로는",
    "15:751:1": "에 다가오는 적을\n맞아 싸울 수 없다!",
    "15:752:0": "서둘러 병사를 모으시지요\n",
    "15:752:1": (
        "에 다가오는 적을 막기 위해\n"
        "무리를 무릅쓰고라도 강행해야만 하겠습니다…"
    ),
    "15:753:0": (
        "에 적이 진군 중입니다!\n"
        "맞아 싸우려면 무리한 수를 써서라도\n"
        "병사를 모아야 하옵니다!"
    ),
    "15:754:0": PRIOR.RAW_TRANSLATIONS["15:743:0"],
    "15:754:1": PRIOR.RAW_TRANSLATIONS["15:743:1"],
    "15:755:0": "에 적이 다가와",
    "15:755:1": "\n민심을 잃을지도 모르",
    "15:755:2": "지만\n지금은 서둘러 병사를 모아야 할 줄로 아옵니다",
    "15:756:0": "민심은 다소 잃게 되",
    "15:756:1": "지만\n",
    "15:756:2": "에 전란이 닥쳐오는 지금\n긴급 징병을 진언",
    "15:757:0": "에서 긴급 징병을 실시하여\n병사 총",
    "15:757:1": "명을 모으",
    "15:758:0": (
        "의 인근 군에서 급히 병사를 모아 왔다\n"
        "잃은 게 많지만, 어쩔 수 없지\n"
        "우선 눈앞의 싸움부터 이겨서 끝내자!"
    ),
    "15:759:0": (
        "의 인근 군에서 급히 병사를 모았습니다\n"
        "이 또한 모두 우리 가문의 존속을 위한 일\n"
        "부득이한 일이었다고 사료되옵니다…"
    ),
    "15:760:0": (
        "의 인근 군에서 병사를 모았습니다\n"
        "많은 것을 잃은 긴급 징병이었으나\n"
        "이로써 급한 고비는 넘길 수 있겠군요"
    ),
}
RECORD_ARITIES = {
    **{record_id: 2 for record_id in range(749, 753)},
    753: 1,
    754: 2,
    755: 3,
    756: 3,
    757: 2,
    758: 1,
    759: 1,
    760: 1,
}
EXPECTED_JP = {
    749: (
        "急いで兵をかき集めねばなりませぬな…\n",
        "を敵が狙うておる\n多少のことは目をつぶって、やるしかないわ",
    ),
    750: (
        "急ぎ兵を集めなくては！\n",
        "に迫る敵を\n防がねばなりません！",
    ),
    751: (
        "早急に兵を集めねば！\nこのままでは",
        "に迫る敵を\n迎え撃てぬ！",
    ),
    752: (
        "急ぎ兵を集めましょう\n",
        "に迫る敵を防ぐため\n無理を押してやらなければ…",
    ),
    753: (
        "に敵が進軍中！\n"
        "迎え撃つには強引な手を使っても\n"
        "兵を集めねばなりませんぞ！",
    ),
    754: PRIOR.EXPECTED_JP[743],
    755: (
        "に敵が迫って",
        "\n民心を失うやもしれ",
        "が\nここは急ぎ兵を集めるべきかと",
    ),
    756: (
        "民心は多少失うこととな",
        "が\n",
        "に戦火が近付くいま\n兵の緊急徴集を進言",
    ),
    757: ("にて急ぎ徴兵を実施\n兵", "を集め"),
    758: (
        "の近隣郡から急ぎ兵を集めたぜ\n"
        "失ったもんは多いが、仕方ねえ\n"
        "まずは当面の戦、勝って終わらせるぞ！",
    ),
    759: (
        "の近隣郡より急ぎ兵を集めました\n"
        "これもすべて当家存続のため\n"
        "やむを得ぬことかと…",
    ),
    760: (
        "の近隣郡から兵を集めました\n"
        "様々な物を失っての徴集でしたが\n"
        "これにて急場はしのげそうですな",
    ),
}
EXPECTED_PK_JP = {
    749: (
        "村々から兵を集めるべき",
        "\n",
        "に敵が迫ってお",
        "\n無理を通してでも、城を守らねば…",
    ),
    750: (
        "急ぎ兵を集めなくては！\n",
        "に迫る敵を\n防がねばな",
        "！",
    ),
    751: (
        "早急に兵を集め",
        "！\nこのままでは",
        "に迫る敵を\n迎え撃つことができ",
        "！",
    ),
    752: (
        "急ぎ兵を集め",
        "\n",
        "に迫る敵を防ぐため\n無理を押してやらなければ…",
    ),
    753: (
        "無理にでも兵を集め",
        "\n",
        "へ敵が進軍している今\n城兵はいくらいても困",
    ),
    **{record_id: EXPECTED_JP[record_id] for record_id in range(754, 761)},
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("", "026432", "050505") for record_id in range(749, 753)},
    753: ("026432", "050505"),
    754: ("", "026432", "050505"),
    755: ("026432", "0143b2000000", "0143e0020000", "050505"),
    756: ("", "014336040000", "026432", "0143cc010000050505"),
    757: ("026432", "0232", "014314020000050505"),
    758: ("026432", "050505"),
    759: ("026432", "050505"),
    760: ("026432", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    749: ("", "014362020000", "026432", "014342040000", "050505"),
    750: ("", "026432", "014336040000", "050505"),
    751: ("", "01432a040000", "026432", "0143ec020000", "050505"),
    752: ("", "01432a040000", "026432", "050505"),
    753: ("", "01432a040000", "026432", "014336040000050505"),
    754: ("", "026432", "050505"),
    755: ("026432", "0143b2000000", "0143ec020000", "050505"),
    756: ("", "014342040000", "026432", "0143d2010000050505"),
    757: ("026432", "0232", "01431a020000050505"),
    758: ("026432", "050505"),
    759: ("026432", "050505"),
    760: ("026432", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {"15:749:0", "15:752:1", "15:759:0"}
SC_AUXILIARY = {
    750: (
        ("必须火速召集士兵了！\n得防住逼近", "的敌人\n才行！"),
        ("", "026432", "050505"),
    ),
    754: (
        ("火速招募兵马。\n无论如何也要\n在", "落入敌人手中之前迎击才行。"),
        ("", "026432", "050505"),
    ),
    755: (
        ("敌人正在逼近", "。\n虽然有可能会失去民心，\n但此时应该火速招募兵马才是。"),
        ("", "026432", "050505"),
    ),
    756: (
        ("虽然多少会失去一些民心，\n但当下战火正在逼近", "，\n还请紧急进行征兵。"),
        ("", "026432", "050505"),
    ),
    757: (
        ("急于徵兵，\n已召集士兵", "。"),
        ("026432", "0232", "050505"),
    ),
}
TC_AUXILIARY = {
    750: (
        ("得趕緊募兵！\n直逼", "而來的敵軍\n千萬得擋住！"),
        ("", "026432", "050505"),
    ),
    754: (
        ("緊急召集士兵！\n為避免", "落入敵手，\n務必全力應戰！"),
        ("", "026432", "050505"),
    ),
    755: (
        ("遭敵人猛攻。\n雖有民心盡失之虞，\n也務必立刻召集士兵！",),
        ("026432", "050505"),
    ),
    756: (
        ("雖有失去民心之虞，\n但", "即將遭受攻擊，\n仍須進言緊急徵收士兵。"),
        ("", "026432", "050505"),
    ),
    757: (
        ("急於徵兵，\n已召集士兵", "。"),
        ("026432", "0232", "050505"),
    ),
}
EN_AUXILIARY = {
    750: (
        (
            "We must gather our troops quickly! ",
            " must be defended against the approaching enemy!",
        ),
        ("", "026432", "050505"),
    ),
    754: (
        (
            "Hurry and gather the troops! We have to ambush the enemy before ",
            " falls into their hands.",
        ),
        ("", "026432", "050505"),
    ),
    755: (
        (
            "The enemy is advancing on ",
            ". This may not be popular with the citizens, but we must gather "
            "troops to fight back.",
        ),
        ("", "026432", "050505"),
    ),
    756: (
        (
            "The citizenry wonÖt be fond of the choice, but with the enemy "
            "encroaching on ",
            ", youÖll want to conscript more troops quickly.",
        ),
        ("", "026432", "050505"),
    ),
    757: (
        (
            " soldier(s) were recruited through the emergency conscription at ",
            ".",
        ),
        ("0232", "026432", "050505"),
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
    "pristine_base_pc_jp_authoritative_emergency_levy_personality_proposals_"
    "and_results_with_explicit_plus_7_pk_jp_749_753_wording_segmentation_"
    "opcode_divergence_exact_pc_sc_tc_and_pk_en_context_dynamic_territory_"
    "count_and_conjugation_stems_popular_support_cost_defensive_outcome_"
    "causality_historical_hierarchy_current_pc_layout_preserved_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if COMMON.source_literals(source_records, 754) != COMMON.source_literals(
        source_records, 743
    ):
        raise RuntimeError("segment 841 743/754 exact source drifted")
    for literal_id in range(2):
        if raw_translations[f"15:754:{literal_id}"] != PRIOR.RAW_TRANSLATIONS[
            f"15:743:{literal_id}"
        ]:
            raise RuntimeError(
                f"segment 841 743/754 exact translation drifted: {literal_id}"
            )
    for record_id in range(749, 754):
        if EXPECTED_PK_JP[record_id] == EXPECTED_JP[record_id]:
            raise RuntimeError(
                f"segment 841 Base-priority PK divergence lost: {record_id}"
            )

    stem_expectations = {
        "15:755:0": "다가와",
        "15:755:1": "모르",
        "15:756:0": "되",
        "15:756:2": "진언",
        "15:757:1": "모으",
    }
    for coordinate, suffix in stem_expectations.items():
        if not raw_translations[coordinate].endswith(suffix):
            raise RuntimeError(
                f"segment 841 dynamic conjugation stem drifted: {coordinate}"
            )
    if not raw_translations["15:755:2"].startswith("지만\n"):
        raise RuntimeError("segment 841 755 dynamic contrast continuation drifted")
    if raw_translations["15:756:1"] != "지만\n":
        raise RuntimeError("segment 841 756 dynamic contrast continuation drifted")
    if (
        not raw_translations["15:749:0"].endswith("겠소이다…\n")
        or not raw_translations["15:749:1"].endswith("없겠소이다")
    ):
        raise RuntimeError("segment 841 749 old-speaker ending drifted")
    if "강행해야만 하겠습니다…" not in raw_translations["15:752:1"]:
        raise RuntimeError("segment 841 752 polite deliberative ending drifted")
    if "긴급 징병을 실시하여" not in raw_translations["15:757:0"]:
        raise RuntimeError("segment 841 757 emergency-conscription result drifted")
    if any(
        "긴급 징병" not in translations[coordinate]
        for coordinate in ("15:756:2", "15:757:0", "15:760:0")
    ):
        raise RuntimeError("segment 841 emergency levy terminology drifted")
    if "잃은 게 많지만" not in translations["15:758:0"]:
        raise RuntimeError("segment 841 758 civilian-cost causality drifted")
    if "가문의 존속" not in translations["15:759:0"]:
        raise RuntimeError("segment 841 759 defensive necessity drifted")
    if "급한 고비는 넘길" not in translations["15:760:0"]:
        raise RuntimeError("segment 841 760 defensive outcome drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return PRIOR.PRIOR.build_extended_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        expected_pk_jp=EXPECTED_PK_JP,
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
        raise RuntimeError("segment 841 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S841",
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
