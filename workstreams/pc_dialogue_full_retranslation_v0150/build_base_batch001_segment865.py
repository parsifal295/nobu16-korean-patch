#!/usr/bin/env python3
"""Build Base authoring segment 865 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment863 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S865.private.v1.jsonl"
SEGMENT = 865
SUCCESS_OPCODE_STEM = ", 기어이 해내"
SUCCESS_REPORT = (
    SUCCESS_OPCODE_STEM,
    "와(과)",
    "의 사이에 반목이 생겨\n"
    "이제 원군은 도저히 기대할 수 없는 모양입니다",
)
FAILURE_REPORT = (
    "송구하",
    "…조략이 드러나\n",
    "·",
    "두 가문의\n우리 가문에 대한 인상이 나빠진 모양입니다…",
)
SEVER_ALLIANCE_REPORT = (
    "후후후, 내 이간 공작이 성공하여\n",
    "와(과)",
    "이(가) 단교하였사옵니다\n"
    "자, 다음에는 어떤 수를 써 볼까요?",
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1090:0": "은(는)",
    "15:1090:1": (
        "의 원군을\n"
        "믿고 있는 모양입니다\n"
        "이참에 서로 반목하게 만드는 것이 좋을 듯합니다"
    ),
    "15:1091:0": "와(과) 싸울 때 골칫거리가 될 것은\n",
    "15:1091:1": "에서 오는 원군",
    "15:1091:2": "\n미리 두 가문 사이를 틀어놓아야 할지도 모르겠습니다…",
    "15:1092:0": "와(과)",
    "15:1092:1": "의 동맹이 파기",
    "15:1093:0": "에서",
    "15:1093:1": "에게 보내는 원군 요청이",
    "15:1093:2": "일간 불가",
    "15:1094:0": "와(과)의 우호도 하락\n",
    "15:1094:1": "와(과)의 우호도 하락\n우리 가문의 악명",
    "15:1094:2": "→",
    "15:1095:0": SUCCESS_REPORT[0],
    "15:1095:2": SUCCESS_REPORT[1],
    "15:1095:3": SUCCESS_REPORT[2],
    "15:1096:0": FAILURE_REPORT[0],
    "15:1096:1": FAILURE_REPORT[1],
    "15:1096:2": FAILURE_REPORT[2],
    "15:1096:3": FAILURE_REPORT[3],
    "15:1097:0": SEVER_ALLIANCE_REPORT[0],
    "15:1097:1": SEVER_ALLIANCE_REPORT[1],
    "15:1097:2": SEVER_ALLIANCE_REPORT[2],
}
RECORD_ARITIES = {
    1090: 2,
    1091: 3,
    1092: 2,
    1093: 3,
    1094: 3,
    1095: 4,
    1096: 4,
    1097: 3,
}
EXPECTED_JP = {
    1090: (
        "は",
        "の援軍を\n頼みとしておる様子\nここは仲違いさせるのが良き手かと",
    ),
    1091: (
        "との戦で厄介になるのは\n",
        "からの援軍",
        "\n前もって仲違いを図るべきやも…",
    ),
    1092: ("と", "の同盟が破棄"),
    1093: ("から", "への援軍要請が", "日間不可"),
    1094: ("との友好度が低下\n", "との友好度が低下\n当家の悪名", "→"),
    1095: (
        "、成し遂げてみせ",
        "\n",
        "と",
        "の間には不和が生じ\n援軍など到底望めぬといった様子",
    ),
    1096: (
        "申し訳",
        "…調略が露呈し\n",
        "・",
        "両家の\n当家に対する心証が悪化した様子…",
    ),
    1097: (
        "ふふふ、我が離間工作が為り\n",
        "と",
        "は手を切りましたぞ\nさあ、次はいかな手を打ちましょう？",
    ),
}
EXPECTED_BASE_GAPS = {
    1090: ("025032", "025132", "050505"),
    1091: ("025032", "025132", "0143560200000143ce020000", "050505"),
    1092: ("025032", "025132", "050505"),
    1093: ("025032", "025132", "023c", "050505"),
    1094: ("025032", "025132", "0232", "0233050505"),
    1095: (
        "023c",
        "014314020000014360040000",
        "025032",
        "025132",
        "01432c020000050505",
    ),
    1096: ("", "0143da020000", "025032", "025132", "050505"),
    1097: ("", "025032", "025132", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1091: ("025032", "025132", "0143620200000143da020000", "050505"),
    1095: (
        "023c",
        "01431a02000001436c040000",
        "025032",
        "025132",
        "014338020000050505",
    ),
    1096: ("", "0143e6020000", "025032", "025132", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1091:2",
    "15:1096:1",
    "15:1096:3",
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1095:1": "\n"}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1090): (
            ("看来打算向", "请求援军。\n现在应该出手离间他们。"),
            ("025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1090): (
            ("欲向", "請求援軍。\n此時正是離間雙方的好時機。"),
            ("025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1090): (
        (
            "The ",
            " seem to be relying on the ",
            " for reinforcements. Sowing discord between them might be to our advantage.",
        ),
        ("", "025032", "025132", "050505"),
    ),
    **{
        (side, "SC", 1091): (
            (
                "与",
                "之战，\n是因为来自",
                "的援军而变得棘手吧。\n应该事先图谋离间才是……",
            ),
            ("", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1091): (
            ("的援軍若介入我方和\n", "的交戰，勢必造成不利。\n應趁早離間雙方……"),
            ("025132", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1091): (
        (
            "Ös reinforcements will prove troublesome in our fight against the ",
            ". We should try to break up their alliance somehow...",
        ),
        ("025132", "025032", "050505"),
    ),
    **{
        (side, "SC", 1093): (
            ("在", "日内，", "不能向", "提出请求援军。"),
            ("", "023c", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1093): (
            ("天內，", "無法向", "請求援軍。"),
            ("023c", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1093): (
        (
            "Ös reinforcement request to the ",
            " will be unavailable for ",
            " day(s).",
        ),
        ("025032", "025132", "023c", "050505"),
    ),
    **{
        (side, "SC", 1095): (
            (
                "成功了。\n",
                "与",
                "之间产生了不和，\n看来援军什么的完全没指望了。",
            ),
            ("023c", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1095): (
            ("成功了。\n", "與", "之間產生嫌隙，\n請求援軍終究是無望了。"),
            ("023c", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1095): (
        (
            "We managed to ",
            ". The ",
            " and the ",
            " are now at odds with each other and will no longer provide reinforcements to one another.",
        ),
        ("", "023c", "025032", "025132", "050505"),
    ),
    **{
        (side, "SC", 1096): (
            (
                "万分抱歉……因用计暴露，\n",
                "与",
                "两家\n对主家的印象似乎已恶化……",
            ),
            ("", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1096): (
            (
                "萬分抱歉……因用計暴露，\n",
                "與",
                "兩家\n對主家的印象似乎已惡化……",
            ),
            ("", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1096): (
        (
            "I apologize... Our scheme was exposed, and now we have lost face with both the ",
            " and the ",
            "...",
        ),
        ("", "025032", "025132", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B104_pristine_base_pc_jp_authoritative_"
    "reinforcement_alliance_sowing_discord_proposal_effect_success_failure_"
    "reports_with_uniform_plus_8_pk_jp_sc_tc_exact_mapping_pk_en_auxiliary_"
    "context_dynamic_house_day_and_infamy_tokens_1095_1_newline_preserved_"
    "0143_korean_verb_stems_historical_register_project_diplomacy_terminology_"
    "and_heart_impression_semantics_current_layout_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if "15:1095:1" in raw_translations or "15:1095:1" in translations:
        raise RuntimeError("segment 865 excluded 1095 newline received a decision")
    if raw_translations["15:1095:0"] != SUCCESS_OPCODE_STEM:
        raise RuntimeError("segment 865 1095 success opcode stem drifted")
    if raw_translations["15:1095:0"].endswith(
        ("다", "요", "오", "니다", "사옵니다", "습니다")
    ):
        raise RuntimeError("segment 865 completed verb precedes 1095 live 0143 opcode")
    if tuple(
        raw_translations[f"15:1096:{literal_id}"] for literal_id in range(4)
    ) != FAILURE_REPORT:
        raise RuntimeError("segment 865 failure report canonical drifted")
    if tuple(
        raw_translations[f"15:1097:{literal_id}"] for literal_id in range(3)
    ) != SEVER_ALLIANCE_REPORT:
        raise RuntimeError("segment 865 alliance-severance canonical drifted")

    joined = "\n".join(translations.values())
    for required in (
        "원군",
        "반목",
        "단교",
        "이간 공작",
        "우호도",
        "악명",
        "조략",
        "인상",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 865 diplomacy terminology drifted: {required}")
    if any(
        forbidden in joined
        for forbidden in ("심증", "당가", "이간계", "손을 끊", "사이를 갈라놓")
    ):
        raise RuntimeError("segment 865 retained forbidden diplomacy terminology")

    if not raw_translations["15:1090:1"].endswith("좋을 듯합니다"):
        raise RuntimeError("segment 865 sowing-discord proposal register drifted")
    if raw_translations["15:1093:1"] != "에게 보내는 원군 요청이":
        raise RuntimeError("segment 865 reinforcement-request direction drifted")
    if translations["15:1096:3"] != (
        "두 가문의\n우리 가문에 대한 인상이 나빠진 모양입니다……"
    ):
        raise RuntimeError("segment 865 1096 心証 impression semantics drifted")


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
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 865 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S865",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "excluded_nonvisible_decisions": len(
                    EXCLUDED_NONVISIBLE_COORDINATES
                ),
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
