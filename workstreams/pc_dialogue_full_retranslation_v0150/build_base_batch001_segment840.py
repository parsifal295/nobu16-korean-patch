#!/usr/bin/env python3
"""Build Base authoring segment 840 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment839 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = PRIOR.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S840.private.v1.jsonl"
SEGMENT = 840
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:0": PRIOR.REPEATED_WARNING_730_741
        for record_id in range(734, 742)
    },
    "15:742:0": "서둘러 병사를 긁어모은다!\n",
    "15:742:1": "에 적이 바짝 다가오고 있어\n맞아 싸우려면 병력이 필요해!",
    "15:743:0": "급히 병사를 모으시오\n",
    "15:743:1": "이(가) 적의 손에 넘어가기 전에\n무슨 수를 써서라도 맞아 싸워야 하오",
    "15:744:0": "서둘러 병사를 모으시지요\n",
    "15:744:1": "으로(로) 몰려오는 적을\n맞아 싸우기에는 병력이 부족하옵니다",
    "15:745:0": "급작스럽사오나 무리해서라도 병사를 모으시지요\n",
    "15:745:1": "으로(로) 적이 진군하는 지금\n맞아 싸울 병사는 아무리 많아도 지나치지 않사옵니다",
    "15:746:0": "무엇보다 우선하여 서둘러 병사를 모으시오\n",
    "15:746:1": "을(를) 노리고 적이 움직이고 있소\n병사는 많으면 많을수록 좋소",
    "15:747:0": "급히 병사를 모으시옵소서\n",
    "15:747:1": "에 적이 진군 중이옵니다\n맞아 싸울 병력은 아무리 많아도 모자라옵니다",
    "15:748:0": "서둘러 병사를 모으셔야 하옵니다\n",
    "15:748:1": (
        "에 적이 다가오고 있다 하옵니다\n"
        "잃는 것이 많겠으나, 성을 잃는 것보다는…"
    ),
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(734, 742)},
    **{record_id: 2 for record_id in range(742, 749)},
}
EXPECTED_JP = {
    **{record_id: PRIOR.REPEATED_WARNING_JP for record_id in range(734, 742)},
    742: (
        "急いで兵をかき集めるぞ！\n",
        "に敵が迫ってんだ\n迎撃するには人手が要る！",
    ),
    743: (
        "至急、兵を集められよ\n",
        "が敵の手に落ちる前に\n何としても迎撃しなければ",
    ),
    744: (
        "急ぎ兵を集めましょうぞ\n",
        "に寄せる敵を\n迎え撃つには兵が足りませぬ",
    ),
    745: (
        "急ですが無理にでも兵を集めましょう\n",
        "へ敵が進軍している今\n迎撃の兵は、いくらいても困りません",
    ),
    746: (
        "何にも優先して、急ぎ兵を集められよ\n",
        "目がけて敵が動いておる\n兵は多ければ多いほどよい",
    ),
    747: (
        "急遽兵を集められませ\n",
        "に敵が進軍中です\n迎撃の兵力に十分という数はありませぬ",
    ),
    748: (
        "急ぎ兵をお集めになるべきでしょう\n",
        "に敵が迫っておる由\n失うものも多いですが、城を失うよりは…",
    ),
}
EXPECTED_PK_JP = {
    **{record_id: EXPECTED_JP[record_id] for record_id in range(734, 744)},
    744: (
        "急ぎ兵を集め",
        "ぞ\n",
        "に寄せる敵を\n迎え撃つには兵が足",
    ),
    745: (
        "無理にでも兵を集め",
        "\n",
        "へ敵が進軍している今\n城兵はいくらいても困",
    ),
    746: (
        "すぐに兵を招集いた",
        "\n",
        "を確実に守り切るには\n兵は多ければ多いほどよい",
    ),
    747: (
        "に敵が進軍中…\n急ぎ兵を集めるべき",
        "\nこれでは迎撃の駒が足",
    ),
    748: (
        "に敵が迫って",
        "\n民心を失うやもしれ",
        "が\nここは急ぎ兵を集めるべきかと",
    ),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("", "050505") for record_id in range(734, 742)},
    **{record_id: ("", "026432", "050505") for record_id in range(742, 749)},
}
EXPECTED_PK_JP_GAPS = {
    **{record_id: EXPECTED_BASE_GAPS[record_id] for record_id in range(734, 744)},
    744: ("", "01432a040000", "026432", "014336040000050505"),
    745: ("", "01432a040000", "026432", "014336040000050505"),
    746: ("", "01438a040000", "026432", "014362020000050505"),
    747: ("026432", "014362020000", "014336040000050505"),
    748: ("026432", "0143b2000000", "0143ec020000", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {"15:748:1"}
SC_AUXILIARY = {
    744: (
        ("火速召集士兵吧。\n要迎击逼近", "的敌人，\n兵力尚嫌不足。"),
        ("", "026432", "050505"),
    ),
    745: (
        ("事出突然，但还请勉力召集士兵。\n眼下敌人正向", "进军，\n迎击的士兵越多越好。"),
        ("", "026432", "050505"),
    ),
    746: (
        ("先放下其他事，火速召集士兵吧。\n敌人正朝", "进发，\n士兵多多益善。"),
        ("", "026432", "050505"),
    ),
}
TC_AUXILIARY = {
    744: (
        ("趕緊募兵吧！\n敵軍直逼", "，\n依目前兵力難以迎擊。"),
        ("", "026432", "050505"),
    ),
    745: (
        ("募兵乃當務之急！\n敵人正朝著", "進軍，\n迎擊的兵力自然不嫌多。"),
        ("", "026432", "050505"),
    ),
    746: (
        ("火速募兵應為第一優先！\n敵軍衝著", "而來，\n兵力當然越多越好。"),
        ("", "026432", "050505"),
    ),
}
EN_AUXILIARY = {
    744: (
        (
            "Hurry and gather the troops, or we wonÖt have enough men to stop "
            "the enemy from marching on ",
            ".",
        ),
        ("", "026432", "050505"),
    ),
    745: (
        (
            "It may be last-minute, but we must gather troops no matter the cost. "
            "We cannot run low on forces with the enemy getting ready to launch "
            "an ambush on ",
            ".",
        ),
        ("", "026432", "050505"),
    ),
    746: (
        (
            "We must prioritize gathering troops! The enemyÖs set their sights on ",
            "; the more men we have the better.",
        ),
        ("", "026432", "050505"),
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
    "with_explicit_plus_7_pk_jp_744_748_wording_segmentation_and_opcode_"
    "divergence_exact_pc_sc_tc_and_pk_en_context_dynamic_territory_token_"
    "popular_support_cost_historical_speaker_hierarchy_current_pc_layout_"
    "and_skeleton_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    warning_source = COMMON.source_literals(source_records, 734)
    if any(
        COMMON.source_literals(source_records, record_id) != warning_source
        for record_id in range(735, 742)
    ):
        raise RuntimeError("segment 840 734-741 exact warning source drifted")
    if any(
        raw_translations[f"15:{record_id}:0"] != PRIOR.REPEATED_WARNING_730_741
        for record_id in range(734, 742)
    ):
        raise RuntimeError("segment 840 734-741 exact warning translation drifted")
    if raw_translations["15:734:0"] != PRIOR.RAW_TRANSLATIONS["15:733:0"]:
        raise RuntimeError("segment 840 730-741 cross-segment translation drifted")

    for record_id in range(744, 749):
        if EXPECTED_PK_JP[record_id] == EXPECTED_JP[record_id]:
            raise RuntimeError(
                f"segment 840 Base-priority PK divergence lost: {record_id}"
            )
    if "병력이 필요해" not in translations["15:742:1"]:
        raise RuntimeError("segment 840 combat-manpower meaning drifted")
    if "아무리 많아도 모자라옵니다" not in translations["15:747:1"]:
        raise RuntimeError("segment 840 insufficient-force nuance drifted")
    if not translations["15:744:1"].startswith("으로(로) 몰려오는"):
        raise RuntimeError("segment 840 744 variable destination particle drifted")
    if not translations["15:745:1"].startswith("으로(로) 적이 진군"):
        raise RuntimeError("segment 840 745 variable destination particle drifted")
    if not translations["15:746:1"].startswith("을(를) 노리고"):
        raise RuntimeError("segment 840 target territory particle drifted")
    if not translations["15:748:1"].startswith("에 적이 다가오고"):
        raise RuntimeError("segment 840 approaching-enemy location particle drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return PRIOR.build_extended_segment_rows(
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
        raise RuntimeError("segment 840 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S840",
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
