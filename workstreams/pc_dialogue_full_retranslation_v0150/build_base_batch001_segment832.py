#!/usr/bin/env python3
"""Build Base authoring segment 832 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment831 as PRIOR
import build_base_batch001_segment833 as B101_NEXT


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S832.private.v1.jsonl"
SEGMENT = 832
REPEATED_FAILURE = (
    "의 회유는 실패로 끝났습니다\n"
    "녀석들도 꽤 고집이 세군요"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:611:0": (
        "와의 관계도 더할 나위 없이 좋습니다\n"
        "여기까지 왔으니 우리 가문으로의 편입도\n"
        "고려할 수 있겠군요"
    ),
    "15:612:0": (
        "의 회유는 끝났소\n"
        "이제 우리 가문의 일부라 할 수 있을 것이오\n"
        "편입도 검토해 주시구려"
    ),
    "15:613:0": (
        "의 회유도 드디어 끝났습니다\n"
        "여기까지 왔으니 우리 가문으로의 편입도\n"
        "고려해야 할 것입니다"
    ),
    "15:614:0": (
        "의 회유도 완료되었소\n"
        "제법 순종하게 되었으니\n"
        "편입해 버리는 것도 한 방법이오"
    ),
    "15:615:0": "을(를) 회유하여",
    "15:615:1": (
        "\n유사시에는 기꺼이 협력하고 싶다고 하니\n"
        "이만하면 전력으로 삼을 수 있을 듯"
    ),
    **{
        f"15:{record_id}:0": REPEATED_FAILURE
        for record_id in range(616, 628)
    },
    "15:628:0": "·",
    "15:628:1": "의 종속 단계: 낮음 → 보통",
    "15:629:0": "·",
    "15:629:1": "의 종속 단계: 보통 → 높음",
}
RECORD_ARITIES = {
    611: 1,
    612: 1,
    613: 1,
    614: 1,
    615: 2,
    **{record_id: 1 for record_id in range(616, 628)},
    628: 2,
    629: 2,
}
REPEATED_FAILURE_JP = (
    "の懐柔ですが失敗に終わりました\n"
    "奴らもなかなかに強情でありますな",
)
EXPECTED_JP = {
    611: (
        "との関係も最良と言えます\n"
        "ここまで来れば当家への取り込みも\n"
        "視野に入ってきますね",
    ),
    612: (
        "の懐柔は終わった\n"
        "もはや我らの一部と言えるだろう\n"
        "取り込みも検討くだされ",
    ),
    613: (
        "の懐柔もようやく終わりました\n"
        "ここまで来れば当家への取り込みも\n"
        "視野に入れるべきでしょう",
    ),
    614: (
        "の懐柔も完了といったところ\n"
        "なかなか従順となりましたので\n"
        "取り込んでしまうのも手ですな",
    ),
    615: (
        "を懐柔して",
        "\n"
        "有事にはぜひとも協力したいとのこと\n"
        "これなら戦力として見込めそう",
    ),
    **{
        record_id: REPEATED_FAILURE_JP
        for record_id in range(616, 628)
    },
    628: ("・", "の従属段階：低 → 中"),
    629: ("・", "の従属段階：中 → 高"),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("028c32", "050505") for record_id in range(611, 615)},
    615: (
        "028c32",
        "014308020000",
        "01432c0200000143c8020000050505",
    ),
    **{record_id: ("028c32", "050505") for record_id in range(616, 628)},
    628: ("", "028c32", "050505"),
    629: ("", "028c32", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **{
        record_id: gaps
        for record_id, gaps in EXPECTED_BASE_GAPS.items()
        if record_id != 615
    },
    615: (
        "028c32",
        "01430e020000",
        "0143380200000143d4020000050505",
    ),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
SC_AUXILIARY = {
    611: (
        ("与", "的关系算得上好到极点了。\n走到这一步，可以考虑\n拉拢其至本家了吧。"),
        ("", "028c32", "050505"),
    ),
    615: (
        ("已成功怀柔", "，\n若发生兵事，对方愿意挺身相助。\n应该能够成为战力吧。"),
        ("", "028c32", "050505"),
    ),
}
TC_AUXILIARY = {
    611: (
        ("與", "之間的關係可謂絕佳。\n到這地步，籠絡入本家\n亦可列入考量。"),
        ("", "028c32", "050505"),
    ),
    615: (
        ("已成功懷柔", "，\n據說若發生兵事，其將挺立相助。\n如此應能期待成為戰力吧。"),
        ("", "028c32", "050505"),
    ),
}
EN_AUXILIARY = {
    611: (
        (
            "Our relations with the ",
            " are excellent. Considering how we already get along so well, "
            "inviting them into our clan could be a possibility.",
        ),
        ("", "028c32", "050505"),
    ),
    615: (
        (
            "Appeasing the ",
            " went well. If the need arises, theyÖll be willing to help us. "
            "We should expect great things from them in battle.",
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
    "pristine_base_pc_jp_authoritative_kunishu_incorporation_consideration_"
    "placation_success_failure_and_submission_stage_results_with_exact_"
    "uniform_plus_7_pk_jp_sc_tc_mapping_pk_en_auxiliary_context_dynamic_"
    "kunishu_particles_historical_speaker_register_central_kunishu_"
    "placation_incorporation_and_submission_terms_current_pc_layout_and_"
    "base_pk_opcode_skeletons_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    dynamic_boundaries = {
        611: "와의 관계",
        612: "의 회유",
        613: "의 회유",
        614: "의 회유",
        **{record_id: "의 회유" for record_id in range(616, 628)},
    }
    for record_id, prefix in dynamic_boundaries.items():
        if not translations[f"15:{record_id}:0"].startswith(prefix):
            raise RuntimeError(
                f"segment 832 dynamic kunishu-name particle drifted: {record_id}"
            )
    if not translations["15:615:0"].startswith("을(를) 회유하여"):
        raise RuntimeError("segment 832 15:615 dynamic kunishu particle drifted")
    for record_id in (628, 629):
        if translations[f"15:{record_id}:0"] != "·":
            raise RuntimeError(
                f"segment 832 submission-stage bullet drifted: {record_id}"
            )
        if not translations[f"15:{record_id}:1"].startswith("의 종속 단계:"):
            raise RuntimeError(
                f"segment 832 submission-stage particle drifted: {record_id}"
            )

    if len(
        {
            COMMON.source_literals(source_records, record_id)
            for record_id in range(616, 628)
        }
    ) != 1:
        raise RuntimeError("segment 832 616-627 repeated failure source drifted")
    for record_id in range(616, 628):
        if raw_translations[f"15:{record_id}:0"] != REPEATED_FAILURE:
            raise RuntimeError(
                f"segment 832 616-627 repeated failure translation drifted: {record_id}"
            )

    if "우리 가문으로의 편입" not in translations["15:611:0"]:
        raise RuntimeError("segment 832 15:611 incorporation stage drifted")
    if not translations["15:615:1"].endswith("전력으로 삼을 수 있을 듯"):
        raise RuntimeError("segment 832 15:615 runtime result stem drifted")
    if translations["15:628:1"] != "의 종속 단계: 낮음 → 보통":
        raise RuntimeError("segment 832 15:628 submission stage drifted")
    if translations["15:629:1"] != "의 종속 단계: 보통 → 높음":
        raise RuntimeError("segment 832 15:629 submission stage drifted")
    if COMMON.source_literals(source_records, 630) != (
        "・",
        "の従属段階：高 → 最高",
    ):
        raise RuntimeError("segment 832/833 15:630 submission source continuity drifted")
    if (
        translations["15:628:1"],
        translations["15:629:1"],
        B101_NEXT.RAW_TRANSLATIONS["15:630:1"],
    ) != (
        "의 종속 단계: 낮음 → 보통",
        "의 종속 단계: 보통 → 높음",
        "의 종속 단계: 높음 → 최고",
    ):
        raise RuntimeError("segment 832/833 15:628-630 submission-stage ladder drifted")

    joined = "\n".join(translations.values())
    for required in ("회유", "편입", "우리 가문", "종속 단계", "전력"):
        if required not in joined:
            raise RuntimeError(
                f"segment 832 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in (
            "호족",
            "당가",
            "참진",
            "심복",
            "거두어들",
            "끌어들이",
        )
    ):
        raise RuntimeError("segment 832 retains forbidden legacy terminology")


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
        raise RuntimeError("segment 832 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S832",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
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
