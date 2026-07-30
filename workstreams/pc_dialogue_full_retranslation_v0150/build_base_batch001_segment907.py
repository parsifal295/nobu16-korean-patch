#!/usr/bin/env python3
"""Build Base authoring segment 907 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment906 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S907.private.v1.jsonl"
)
SEGMENT = 907
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1499:0": "아직 재능을 꽃피우지 못한",
    "15:1499:1": "이(가) 있는 듯",
    "15:1499:2": "\n그렇다면,",
    "15:1499:3": (
        "이(가) 가르쳐 보도록 하지\n"
        "괜찮은가"
    ),
    "15:1499:4": "?",
    "15:1500:0": "흠, 재주 있는",
    "15:1500:1": "이(가) 있는 듯",
    "15:1500:2": "\n어디,",
    "15:1500:3": "이(가) 요령을 조금 일러주고",
    "15:1500:4": "\n상관없",
    "15:1500:5": "일까?",
    "15:1501:0": "아무래도 우리 가문에 뛰어난",
    "15:1501:1": "이(가) 있는 듯",
    "15:1501:3": "이(가) 조금 지도해 주면",
    "15:1501:4": "\n좋다",
    "15:1501:5": "?",
    "15:1502:0": "우리 가문을 떠받칠 뛰어난",
    "15:1502:1": "이(가) 있다 하오니\n",
    "15:1502:2": "이(가) 조금이나마 가르침을",
    "15:1502:3": "\n제게 맡겨 주시지 않겠습니까?",
    "15:1503:0": "힘과 재능을 갖춘",
    "15:1503:1": "이(가) 있는 듯",
    "15:1503:3": (
        "이(가) 지도하고자 하옵니다만\n"
        "괜찮으신지"
    ),
    "15:1503:4": "?",
}
RECORD_ARITIES = {
    1499: 5,
    1500: 6,
    1501: 6,
    1502: 4,
    1503: 5,
}
EXPECTED_BASE_JP = {
    1499: (
        "まだ花開かぬ",
        "がいるよう",
        "\nここは一つ、",
        "が教え込むとしよう\nよろしい",
        "？",
    ),
    1500: (
        "ふむ、才ある",
        "がいるよう",
        "\nどれ、",
        "が少しコツを授け",
        "\n構",
        "かな？",
    ),
    1501: (
        "どうやら当家に優秀な",
        "がいるよう",
        "\n",
        "が少し手ほどきすると",
        "\nよろしい",
        "？",
    ),
    1502: (
        "当家を支えんとする優れた",
        "がいるとか\n",
        "が僅かばかり手ほどきを",
        "\n任せてもらえませぬか？",
    ),
    1503: (
        "力のある、良き",
        "がいるよう",
        "\n",
        "が手ほどきをしようと思うのですが\nよろしい",
        "？",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1499: (
        "",
        "023C",
        "014340030000",
        "014301000000",
        "014324010000",
        "050505",
    ),
    1500: (
        "",
        "023C",
        "014340030000",
        "014301000000",
        "01431E040000",
        "014366040000",
        "050505",
    ),
    1501: (
        "",
        "023C",
        "014340030000",
        "014301000000",
        "014394000000",
        "014324010000",
        "050505",
    ),
    1502: (
        "",
        "023C",
        "014301000000",
        "014394000000",
        "050505",
    ),
    1503: (
        "",
        "023C",
        "014340030000",
        "014301000000",
        "014324010000",
        "050505",
    ),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1499: (
        "",
        "023C",
        "01434C030000",
        "014301000000",
        "014324010000",
        "050505",
    ),
    1500: (
        "",
        "023C",
        "01434C030000",
        "014301000000",
        "01432A040000",
        "014372040000",
        "050505",
    ),
    1501: (
        "",
        "023C",
        "01434C030000",
        "014301000000",
        "014394000000",
        "014324010000",
        "050505",
    ),
    1503: (
        "",
        "023C",
        "01434C030000",
        "014301000000",
        "014324010000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1501:2": "\n",
    "15:1503:2": "\n",
}
SHARED_AUXILIARY = {
    ("SC", 1501): (
        (
            "好像本家里有个优秀的",
            "吧。\n",
            "来稍微指点一下吧，\n可以吗？",
        ),
        ("", "023C", "014301000000", "050505"),
    ),
    ("TC", 1501): (
        (
            "好像本家裡有個優秀的",
            "吧。\n",
            "來稍微指點一下吧，\n可以嗎？",
        ),
        ("", "023C", "014301000000", "050505"),
    ),
}
AUXILIARY_OVERRIDES = PREVIOUS.PREVIOUS.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    {},
)
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "remaining_five_of_eleven_talent_training_proposals_with_uniform_plus_"
    "15_pk_jp_mapping_exact_base_pk_sc_tc_context_and_blank_training_pk_en_"
    "auxiliary_records_当家_as_우리_가문_dynamic_candidate_and_instructor_"
    "tokens_two_hidden_lf_slots_preserved_fullwidth_punctuation_removed_"
    "live_inflection_stems_speaker_register_and_current_line_counts_"
    "preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for coordinate, hidden in EXCLUDED_NONVISIBLE_COORDINATES.items():
        if (
            coordinate in raw_translations
            or coordinate in translations
            or hidden != "\n"
        ):
            raise RuntimeError(
                f"segment 907 hidden LF received a decision: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "재능을 꽃피우지 못한",
        "요령",
        "우리 가문",
        "떠받칠",
        "가르침",
        "지도",
        "힘과 재능",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 907 meaning or terminology drifted: {required}"
            )
    for forbidden in ("당가", "、", "？"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 907 forbidden term or punctuation retained: "
                f"{forbidden}"
            )
    stem_expectations = {
        "15:1499:1": "듯",
        "15:1499:3": "괜찮은가",
        "15:1500:1": "듯",
        "15:1500:3": "일러주고",
        "15:1500:4": "상관없",
        "15:1501:1": "듯",
        "15:1501:3": "주면",
        "15:1501:4": "좋다",
        "15:1502:2": "가르침을",
        "15:1503:1": "듯",
        "15:1503:3": "괜찮으신지",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 907 live inflection stem drifted: {coordinate}"
            )
    instructor_subject_coordinates = (
        "15:1499:3",
        "15:1500:3",
        "15:1501:3",
        "15:1502:2",
        "15:1503:3",
    )
    if any(
        not raw_translations[coordinate].startswith("이(가)")
        for coordinate in instructor_subject_coordinates
    ):
        raise RuntimeError(
            "segment 907 instructor subject-token relation drifted"
        )
    candidate_relation_expectations = {
        "15:1499:1": "이(가)",
        "15:1500:1": "이(가)",
        "15:1501:1": "이(가)",
        "15:1502:1": "이(가)",
        "15:1503:1": "이(가)",
    }
    for coordinate, prefix in candidate_relation_expectations.items():
        if not raw_translations[coordinate].startswith(prefix):
            raise RuntimeError(
                f"segment 907 candidate token relation drifted: {coordinate}"
            )
    if "우리 가문을 받들" in joined:
        raise RuntimeError(
            "segment 907 retained awkward 当家を支えん wording"
        )
    if any(
        ("pk", "EN", record_id) in AUXILIARY_OVERRIDES
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 907 training PK EN was not blank")
    if len(raw_translations) != 24:
        raise RuntimeError("segment 907 visible decision count drifted")


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
        raise RuntimeError("segment 907 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S907",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "training_proposal_records": len(RECORD_ARITIES),
                "hidden_lf_slots_preserved": len(
                    EXCLUDED_NONVISIBLE_COORDINATES
                ),
                "blank_training_pk_en_verified": True,
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
