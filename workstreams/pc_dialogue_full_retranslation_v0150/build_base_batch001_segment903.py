#!/usr/bin/env python3
"""Build Base authoring segment 903 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment902 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S903.private.v1.jsonl"
)
SEGMENT = 903
make_auxiliary_overrides = PREVIOUS.make_auxiliary_overrides
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1468:0": "에게 벌인",
    "15:1468:1": "은(는) 성공하",
    "15:1468:2": "\n그자의 충성이 흔들리고 있",
    "15:1468:3": "\n우리가 퍼뜨린 유언비어를 철석같이 믿고",
    "15:1468:4": "듯",
    "15:1469:0": "을(를) 비롯한",
    "15:1469:1": "명이\n우리가 퍼뜨린 유언비어를 믿은 듯",
    "15:1469:2": "\n그자들의 충성이 흔들리고 있",
    "15:1470:0": "을(를) 벌인 대상 ",
    "15:1470:1": "명 중,\n",
    "15:1470:2": "을(를) 비롯한",
    "15:1470:3": "명이 유언비어를 믿은 듯",
    "15:1470:4": "\n그자들의 충성이 흔들리고 있",
    "15:1471:0": (
        "은(는) 유언비어에 현혹되어\n"
        "제 거취를 망설이는 모양\n"
        "이참에 그자를 빼내자고 건의드리"
    ),
    "15:1472:0": "이(가)",
    "15:1472:1": "에게 벌인",
    "15:1472:2": "에 성공",
    "15:1473:0": "에게 벌인",
    "15:1473:1": "에 실패하여,",
    "15:1473:2": "이(가) 부상",
    "15:1474:0": "에게 벌인",
    "15:1474:1": "에 실패",
    "15:1475:0": "이(가) 벌인",
    "15:1475:1": "을(를) 대상으로 한",
    "15:1475:2": "을(를) 저지",
    "15:1476:0": "을(를) 비롯한",
    "15:1476:1": "명에게 벌인",
    "15:1476:2": "에 실패",
    "15:1477:0": "이(가) 벌인",
    "15:1477:1": "을(를) 비롯한",
    "15:1477:2": "명 대상의",
    "15:1477:3": "을(를) 저지",
}
RECORD_ARITIES = {
    1468: 5,
    1469: 3,
    1470: 5,
    1471: 1,
    1472: 3,
    1473: 3,
    1474: 2,
    1475: 3,
    1476: 3,
    1477: 4,
}
EXPECTED_BASE_JP = {
    1468: (
        "への",
        "は成功し",
        "\n彼の者の忠誠は揺らいで",
        "\n我らが流した噂を信じ切って",
        "よう",
    ),
    1469: (
        "ら",
        "名が\n我らの流した噂を信じたよう",
        "\n彼の者らの忠誠は揺らいで",
    ),
    1470: (
        "をしかけた",
        "名のうち、\n",
        "ら",
        "名が噂を信じたよう",
        "\n彼の者らの忠誠は揺らいで",
    ),
    1471: (
        "は流言に惑わされ\n"
        "我が身の去就に迷っている様子\n"
        "ここは彼の者への引抜を具申してお",
    ),
    1472: ("が", "への", "に成功"),
    1473: ("への", "に失敗、", "が負傷"),
    1474: ("への", "に失敗"),
    1475: ("から", "への", "を阻止"),
    1476: ("ら", "名への", "に失敗"),
    1477: ("から", "ら", "名への", "を阻止"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1468: (
        "024833",
        "023C",
        "014314020000",
        "0143B2000000",
        "0143B8000000",
        "014350020000050505",
    ),
    1469: (
        "024833",
        "0232",
        "014350020000",
        "0143B2000000050505",
    ),
    1470: (
        "023C",
        "0233",
        "024833",
        "0232",
        "014350020000",
        "0143B2000000050505",
    ),
    1471: ("024833", "014336010000050505"),
    1472: ("024633", "024833", "023C", "050505"),
    1473: ("024833", "023C", "024633", "050505"),
    1474: ("024833", "023C", "050505"),
    1475: ("025032", "024833", "023C", "050505"),
    1476: ("024833", "0232", "023C", "050505"),
    1477: ("025032", "024833", "0232", "023C", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1468: (
        "024833",
        "023C",
        "01431A020000",
        "0143B2000000",
        "0143B8000000",
        "01435C020000050505",
    ),
    1469: (
        "024833",
        "0232",
        "01435C020000",
        "0143B2000000050505",
    ),
    1470: (
        "023C",
        "0233",
        "024833",
        "0232",
        "01435C020000",
        "0143B2000000050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1468): (
        ("对", "的", "成功了。\n", "的忠诚出现了动摇。\n看来完全相信了我等散布的传言。"),
        ("", "024833", "023C", "014315000000", "050505"),
    ),
    ("TC", 1468): (
        ("對", "的", "成功了。\n", "的忠誠出現了動搖。\n看來完全相信了我等散布的傳言。"),
        ("", "024833", "023C", "014315000000", "050505"),
    ),
    ("SC", 1469): (
        ("等", "人\n看来是听信了我等放出的谣言，\n忠诚开始出现动摇。"),
        ("024833", "0232", "050505"),
    ),
    ("TC", 1469): (
        ("等", "人似乎\n已經相信我等散布的流言，\n其等的忠誠心已經動搖。"),
        ("024833", "0232", "050505"),
    ),
    ("SC", 1470): (
        ("在施加了", "的", "人之中，\n", "等", "人看来相信了谣言。\n忠诚出现动摇。"),
        ("", "023C", "0233", "024833", "0232", "050505"),
    ),
    ("TC", 1470): (
        ("進行", "的", "名當中，\n", "等", "人已相信散布的流言，\n其等的忠誠心已經動搖。"),
        ("", "023C", "0233", "024833", "0232", "050505"),
    ),
    ("SC", 1471): (
        ("貌似受到传言的影响，\n对自身的进退抱有迷茫。\n在此呈报向那位大人引荐。",),
        ("024833", "050505"),
    ),
    ("TC", 1471): (
        ("看來", "已被傳言影響，\n對自身的去留感到徬徨。\n這就建議大人進行招攬。"),
        ("", "024833", "050505"),
    ),
    ("SC", 1472): (
        ("对", "的", "成功。"),
        ("024633", "024833", "023C", "050505"),
    ),
    ("TC", 1472): (
        ("對", "的", "成功。"),
        ("024633", "024833", "023C", "050505"),
    ),
    ("SC", 1473): (
        ("对", "的", "失败，", "负伤。"),
        ("", "024833", "023C", "024633", "050505"),
    ),
    ("TC", 1473): (
        ("對", "的", "失敗，", "負傷。"),
        ("", "024833", "023C", "024633", "050505"),
    ),
    ("SC", 1474): (
        ("对", "的", "失败。"),
        ("", "024833", "023C", "050505"),
    ),
    ("TC", 1474): (
        ("對", "的", "失敗。"),
        ("", "024833", "023C", "050505"),
    ),
    ("SC", 1475): (
        ("阻止", "对", "的", "。"),
        ("", "025032", "024833", "023C", "050505"),
    ),
    ("TC", 1475): (
        ("阻止", "對", "的", "。"),
        ("", "025032", "024833", "023C", "050505"),
    ),
    ("SC", 1476): (
        ("对", "等", "人的", "失败。"),
        ("", "024833", "0232", "023C", "050505"),
    ),
    ("TC", 1476): (
        ("對", "等", "人的", "失敗。"),
        ("", "024833", "0232", "023C", "050505"),
    ),
    ("SC", 1477): (
        ("被", "阻止了", "等", "人的", "。"),
        ("", "025032", "024833", "0232", "023C", "050505"),
    ),
    ("TC", 1477): (
        ("阻止", "對", "等", "人進行", "。"),
        ("", "025032", "024833", "0232", "023C", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1468: (
        (
            "We were successful with the ",
            " of ",
            ". His loyalty was shaken. It appears that he believed our rumors.",
        ),
        ("", "023C", "024833", "050505"),
    ),
    1469: (
        (
            "It appears that ",
            " of ",
            "Ös people believed the rumors we spread. Their loyalty was shaken.",
        ),
        ("", "0232", "024833", "050505"),
    ),
    1470: (
        (
            "Of the ",
            " people we attempted ",
            " with, it appears that ",
            " of ",
            "Ös people believed the rumors. Their loyalty was shaken.",
        ),
        ("", "0233", "023C", "0232", "024833", "050505"),
    ),
    1471: (
        (
            " was swayed by our rumors. It seems he is at a complete loss. "
            "This would be the perfect time to draw him to our side.",
        ),
        ("024833", "050505"),
    ),
    1472: (
        (" successfully completed the ", " of ", "."),
        ("024633", "023C", "024833", "050505"),
    ),
    1473: (
        ("The ", " of ", " was a failure. ", " was injured."),
        ("", "023C", "024833", "024633", "050505"),
    ),
    1474: (
        ("The ", " of ", " was a failure."),
        ("", "023C", "024833", "050505"),
    ),
    1475: (
        ("The ", "Ös ", " of ", " was prevented."),
        ("", "025032", "023C", "024833", "050505"),
    ),
    1476: (
        ("The ", " of ", " of ", "Ös people was a failure."),
        ("", "023C", "0232", "024833", "050505"),
    ),
    1477: (
        ("The ", "Ös ", " of ", " of ", "Ös people was prevented."),
        ("", "025032", "023C", "0232", "024833", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "rumor_loyalty_results_luring_recommendation_and_single_plural_operation_"
    "ui_with_uniform_plus_15_pk_mapping_exact_base_pk_jp_sc_tc_and_actual_"
    "pk_en_context_dynamic_actor_target_officer_house_action_and_count_tokens_"
    "ryugen_yuuenbieo_hikinuki_bbaenaegi_gushin_geonui_chuseong_terminology_"
    "live_0143_stems_current_layout_and_opcode_skeleton_preserved_runtime_"
    "fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    del translations
    stem_expectations = {
        "15:1468:1": "성공하",
        "15:1468:2": "흔들리고 있",
        "15:1468:3": "철석같이 믿고",
        "15:1468:4": "듯",
        "15:1469:1": "유언비어를 믿은 듯",
        "15:1469:2": "흔들리고 있",
        "15:1470:3": "유언비어를 믿은 듯",
        "15:1470:4": "흔들리고 있",
        "15:1471:0": "빼내자고 건의드리",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 903 dynamic opcode boundary drifted: {coordinate}"
            )
    single_relations = {
        1472: ("이(가)", "에게 벌인", "에 성공"),
        1473: ("에게 벌인", "에 실패하여,", "이(가) 부상"),
        1474: ("에게 벌인", "에 실패"),
        1475: (
            "이(가) 벌인",
            "을(를) 대상으로 한",
            "을(를) 저지",
        ),
    }
    for record_id, expected in single_relations.items():
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        )
        if actual != expected:
            raise RuntimeError(
                f"segment 903 single-target relation drifted: {record_id}"
            )
    plural_relations = {
        1469: ("을(를) 비롯한", "명이\n"),
        1470: ("을(를) 비롯한", "명이 유언비어를"),
        1476: ("을(를) 비롯한", "명에게 벌인"),
        1477: ("을(를) 비롯한", "명 대상의"),
    }
    for record_id, (first, second) in plural_relations.items():
        if (
            first not in tuple(
                raw_translations[
                    f"15:{record_id}:{literal_id}"
                ]
                for literal_id in range(RECORD_ARITIES[record_id])
            )
            or not any(
                text.startswith(second)
                for text in (
                    raw_translations[
                        f"15:{record_id}:{literal_id}"
                    ]
                    for literal_id in range(RECORD_ARITIES[record_id])
                )
            )
        ):
            raise RuntimeError(
                f"segment 903 plural target relation drifted: {record_id}"
            )
    if raw_translations["15:1470:0"] != "을(를) 벌인 대상 ":
        raise RuntimeError(
            "segment 903 record 1470 action-target population drifted"
        )
    if (
        tuple(
            raw_translations[f"15:1477:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[1477])
        )
        != (
            "이(가) 벌인",
            "을(를) 비롯한",
            "명 대상의",
            "을(를) 저지",
        )
    ):
        raise RuntimeError(
            "segment 903 record 1477 actor-target-prevention relation drifted"
        )
    joined = "\n".join(raw_translations.values())
    for required in ("유언비어", "충성", "빼내", "건의"):
        if required not in joined:
            raise RuntimeError(
                f"segment 903 required terminology drifted: {required}"
            )
    if any(term in joined for term in ("루머", "인발", "구신", "뽑아내기")):
        raise RuntimeError("segment 903 retained forbidden terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
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
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != len(translations):
        raise RuntimeError("segment 903 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S903",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "rumor_result_records": 3,
                "operation_ui_records": 6,
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
