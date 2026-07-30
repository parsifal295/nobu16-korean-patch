#!/usr/bin/env python3
"""Build Base authoring segment 904 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment900 as CAPTURE_S900
import build_base_batch001_segment903 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S904.private.v1.jsonl"
)
SEGMENT = 904
make_auxiliary_overrides = PREVIOUS.make_auxiliary_overrides
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1478:0": "에 의해",
    "15:1478:1": "에서",
    "15:1478:2": "이(가) 발생",
    "15:1479:0": "의 충성이 저하",
    "15:1480:0": "을(를) 비롯한",
    "15:1480:1": "명에게 벌인",
    "15:1480:2": "에 성공",
    "15:1481:0": "을(를) 비롯한",
    "15:1481:1": "명의 충성이 저하",
    "15:1482:0": "의 간자가 벌인 공작으로\n",
    "15:1482:1": "에서",
    "15:1482:2": "님께서\n",
    "15:1482:3": "에게 의심을 품고 있는 모양…",
    "15:1483:0": "의 간자가 벌인 공작으로\n",
    "15:1483:1": "에서",
    "15:1483:2": "님께서\n",
    "15:1483:3": "에게 의심을 품고 있는 모양…",
    "15:1484:0": "의 간자가 벌인 공작으로\n",
    "15:1484:1": "님을 비롯한",
    "15:1484:2": "명이\n",
    "15:1484:3": "에게 의심을 품고 있는 모양…",
    "15:1485:0": CAPTURE_S900.RAW_TRANSLATIONS["15:1444:0"],
    "15:1485:2": CAPTURE_S900.RAW_TRANSLATIONS["15:1444:2"],
    "15:1485:3": CAPTURE_S900.RAW_TRANSLATIONS["15:1444:3"],
}
RECORD_ARITIES = {
    1478: 3,
    1479: 1,
    1480: 3,
    1481: 2,
    1482: 4,
    1483: 4,
    1484: 4,
    1485: 4,
}
EXPECTED_BASE_JP = {
    1478: ("により", "で", "が発生"),
    1479: ("の忠誠が低下",),
    1480: ("ら", "名への", "に成功"),
    1481: ("ら", "名の忠誠が低下"),
    1482: (
        "の間者による工作で\n",
        "において",
        "様が\n",
        "に疑念を抱いている模様…",
    ),
    1483: (
        "の間者による工作で\n",
        "において",
        "様が\n",
        "に疑念を抱いている模様…",
    ),
    1484: (
        "の間者による工作で\n",
        "様ら",
        "名が\n",
        "に疑念を抱いている模様…",
    ),
    1485: CAPTURE_S900.EXPECTED_BASE_JP[1444],
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1478: ("025032", "026432", "023C", "050505"),
    1479: ("024833", "050505"),
    1480: ("024833", "0232", "023C", "050505"),
    1481: ("024833", "0232", "050505"),
    1482: (
        "025032",
        "026432",
        "024833",
        "014308000000",
        "050505",
    ),
    1483: (
        "025032",
        "026432",
        "024833",
        "01430D000000",
        "050505",
    ),
    1484: (
        "025032",
        "024833",
        "0232",
        "014308000000",
        "050505",
    ),
    1485: CAPTURE_S900.EXPECTED_BASE_GAPS[1444],
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1485: CAPTURE_S900.EXPECTED_PK_JP_GAPS[1444],
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1482:3",
    "15:1483:3",
    "15:1484:3",
    "15:1485:3",
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1485:1": "\n"}
SHARED_AUXILIARY = {
    ("SC", 1478): (
        ("因", "于", "发生", "。"),
        ("", "025032", "026432", "023C", "050505"),
    ),
    ("TC", 1478): (
        ("因", "於", "發生", "。"),
        ("", "025032", "026432", "023C", "050505"),
    ),
    ("SC", 1479): (
        ("的忠诚降低。",),
        ("024833", "050505"),
    ),
    ("TC", 1479): (
        ("的忠誠降低。",),
        ("024833", "050505"),
    ),
    ("SC", 1480): (
        ("对", "等", "人的", "成功。"),
        ("", "024833", "0232", "023C", "050505"),
    ),
    ("TC", 1480): (
        ("對", "等", "人執行", "成功。"),
        ("", "024833", "0232", "023C", "050505"),
    ),
    ("SC", 1481): (
        ("等", "人的忠诚下降。"),
        ("024833", "0232", "050505"),
    ),
    ("TC", 1481): (
        ("等", "人的忠誠下降。"),
        ("024833", "0232", "050505"),
    ),
    ("SC", 1482): (
        ("由于", "间谍的工作，\n", "的", "大人\n对", "产生了猜疑……"),
        ("", "025032", "026432", "024833", "014308000000", "050505"),
    ),
    ("TC", 1482): (
        ("由於", "間諜的工作，\n", "的", "大人\n對", "產生了猜疑……"),
        ("", "025032", "026432", "024833", "014308000000", "050505"),
    ),
    ("SC", 1483): (
        ("由于", "间谍的工作，\n", "的", "大人\n对", "产生了猜疑……"),
        ("", "025032", "026432", "024833", "01430D000000", "050505"),
    ),
    ("TC", 1483): (
        ("由於", "間諜的工作，\n", "的", "大人\n對", "產生了猜疑……"),
        ("", "025032", "026432", "024833", "01430D000000", "050505"),
    ),
    ("SC", 1484): (
        ("由于", "间谍的工作，\n", "大人等", "人对", "产生了猜疑……"),
        ("", "025032", "024833", "0232", "014308000000", "050505"),
    ),
    ("TC", 1484): (
        ("由於", "間諜的工作，\n", "大人等", "人對", "產生了猜疑……"),
        ("", "025032", "024833", "0232", "014308000000", "050505"),
    ),
    ("SC", 1485): CAPTURE_S900.SHARED_AUXILIARY[("SC", 1444)],
    ("TC", 1485): CAPTURE_S900.SHARED_AUXILIARY[("TC", 1444)],
}
PK_EN_AUXILIARY = {
    1478: (
        (" was started at ", " by the ", "."),
        ("023C", "026432", "025032", "050505"),
    ),
    1479: (
        ("Ös loyalty has decreased.",),
        ("024833", "050505"),
    ),
    1480: (
        ("The ", " of ", " of ", "Ös people was a success."),
        ("", "023C", "0232", "024833", "050505"),
    ),
    1481: (
        ("The loyalty of ", " of ", "Ös people has decreased."),
        ("", "0232", "024833", "050505"),
    ),
    1482: (
        (
            "It seems that ",
            " has grown suspicious of you after the ",
            "Ös spies destabilized ",
            ".",
        ),
        ("", "024833", "025032", "026432", "050505"),
    ),
    1483: (
        (
            "It seems that ",
            " has grown suspicious of you after the ",
            "Ös spies destabilized ",
            ".",
        ),
        ("", "024833", "025032", "026432", "050505"),
    ),
    1484: (
        (
            "It seems that ",
            " of ",
            "Ös people have grown suspicious of you after the ",
            "Ös spiesÖ destabilization.",
        ),
        ("", "0232", "024833", "025032", "050505"),
    ),
    1485: CAPTURE_S900.PK_EN_AUXILIARY[1444],
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "operation_occurrence_loyalty_decline_single_plural_success_and_spy_"
    "destabilization_results_with_uniform_plus_15_pk_mapping_exact_base_"
    "pk_jp_sc_tc_and_actual_pk_en_context_dynamic_action_castle_actor_"
    "officer_count_and_target_tokens_kanja_ganja_chusei_chungseong_"
    "b108_spy_capture_canonical_exact_import_hidden_lf_preserved_current_"
    "layout_and_opcode_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if (
        raw_translations["15:1478:0"] != "에 의해"
        or raw_translations["15:1478:1"] != "에서"
        or raw_translations["15:1478:2"] != "이(가) 발생"
    ):
        raise RuntimeError(
            "segment 904 operation-actor-location relation drifted"
        )
    if (
        raw_translations["15:1479:0"] != "의 충성이 저하"
        or raw_translations["15:1481:1"] != "명의 충성이 저하"
    ):
        raise RuntimeError("segment 904 loyalty relation drifted")
    if (
        tuple(
            raw_translations[f"15:1480:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[1480])
        )
        != ("을(를) 비롯한", "명에게 벌인", "에 성공")
    ):
        raise RuntimeError("segment 904 plural success relation drifted")
    if (
        tuple(
            raw_translations[f"15:1482:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[1482])
        )
        != tuple(
            raw_translations[f"15:1483:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[1483])
        )
    ):
        raise RuntimeError(
            "segment 904 paired spy-operation wording drifted"
        )
    if (
        raw_translations["15:1484:1"] != "님을 비롯한"
        or raw_translations["15:1484:2"] != "명이\n"
    ):
        raise RuntimeError(
            "segment 904 plural suspicious-officer relation drifted"
        )
    canonical_coordinates = {
        "15:1485:0": "15:1444:0",
        "15:1485:2": "15:1444:2",
        "15:1485:3": "15:1444:3",
    }
    for coordinate, canonical_coordinate in canonical_coordinates.items():
        if raw_translations[coordinate] != (
            CAPTURE_S900.RAW_TRANSLATIONS[canonical_coordinate]
        ):
            raise RuntimeError(
                f"segment 904 S900 capture canonical drifted: {coordinate}"
            )
    if (
        "15:1485:1" in raw_translations
        or "15:1485:1" in translations
        or EXCLUDED_NONVISIBLE_COORDINATES["15:1485:1"] != "\n"
    ):
        raise RuntimeError(
            "segment 904 hidden capture LF handling drifted"
        )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 904 ellipsis seed/pair drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "충성이 저하",
        "간자가 벌인 공작",
        "의심을 품고 있는 모양",
        "간자를 붙잡아",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 904 required terminology drifted: {required}"
            )
    if "첩자" in joined:
        raise RuntimeError("segment 904 retained forbidden spy terminology")


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
        raise RuntimeError("segment 904 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S904",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "spy_operation_records": 3,
                "capture_canonical_imported": True,
                "hidden_lf_preserved": True,
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
