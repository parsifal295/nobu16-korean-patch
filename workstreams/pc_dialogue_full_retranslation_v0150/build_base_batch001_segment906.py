#!/usr/bin/env python3
"""Build Base authoring segment 906 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment905 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S906.private.v1.jsonl"
)
SEGMENT = 906
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1493:0": "뭐야, 제법 기개가 있어 보이는",
    "15:1493:1": "이(가) 있는 모양이군\n",
    "15:1493:2": (
        "이(가) 한번 단련시켜 줄까 하는데\n"
        "어때, 괜찮겠지?"
    ),
    "15:1494:0": "눈여겨볼 만한",
    "15:1494:1": "이(가) 있다고 들었소",
    "15:1494:3": "이(가) 기량을 조금 단련시켜",
    "15:1494:4": "\n제게 맡겨 주시겠습니까?",
    "15:1495:0": "기개가 엿보이는",
    "15:1495:1": "이(가) 있는 듯",
    "15:1495:3": "이(가) 조금 지도해 주면",
    "15:1495:4": "\n좋다",
    "15:1495:5": "?",
    "15:1496:0": "우리 가문의",
    "15:1496:1": "중에 인재가 있다 하더이다…\n외람되오나",
    "15:1496:2": (
        "이(가) 지도하고자\n"
        "하옵니다만, 괜찮으신지"
    ),
    "15:1496:3": "?",
    "15:1497:0": "호오, 우리 가문에 이런",
    "15:1497:1": "이(가) 있을 줄이야\n",
    "15:1497:2": (
        "이(가) 한번 단련시켜 주고 싶다만\n"
        "괜찮은"
    ),
    "15:1497:3": "인가?",
    "15:1498:0": "우리 가문에는 뛰어난",
    "15:1498:1": "이(가) 있는 듯",
    "15:1498:3": (
        "의 비결을 전수하고 싶사옵니다만\n"
        "괜찮"
    ),
    "15:1498:4": "인가?",
}
RECORD_ARITIES = {
    1493: 3,
    1494: 5,
    1495: 6,
    1496: 4,
    1497: 4,
    1498: 5,
}
EXPECTED_BASE_JP = {
    1493: (
        "なんだ、骨のありそうな",
        "がいるみたいだな\n",
        "がちょいともんでやるとするか\nなぁ、いいだろう？",
    ),
    1494: (
        "見どころのある",
        "がいると聞いた",
        "\n",
        "が少し技量を叩き込んで",
        "\n任せていただけますか？",
    ),
    1495: (
        "良い面構えの",
        "がいるよう",
        "\n",
        "が少し手ほどきすると",
        "\nよろしい",
        "？",
    ),
    1496: (
        "当家の",
        "中に逸材がいるとか…\n僭越ながら",
        "が指南しようと\n存じますが、よろしい",
        "？",
    ),
    1497: (
        "ほう、当家にこのような",
        "がいるとはな\n",
        "がいっちょ、鍛えてやりたいのだが\nよい",
        "か？",
    ),
    1498: (
        "当家には優れた",
        "がいるよう",
        "\n",
        "の心得を仕込みたいのですが\n構",
        "か？",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1493: ("", "023C", "014301000000", "050505"),
    1494: (
        "",
        "023C",
        "0143F6010000",
        "014301000000",
        "014300040000",
        "050505",
    ),
    1495: (
        "",
        "023C",
        "01434A020000",
        "014301000000",
        "014394000000",
        "014324010000",
        "050505",
    ),
    1496: (
        "",
        "023C",
        "014301000000",
        "014324010000",
        "050505",
    ),
    1497: (
        "",
        "023C",
        "014301000000",
        "014356020000",
        "050505",
    ),
    1498: (
        "",
        "023C",
        "01431A020000",
        "014301000000",
        "014366040000",
        "050505",
    ),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1494: (
        "",
        "023C",
        "0143FC010000",
        "014301000000",
        "01430C040000",
        "050505",
    ),
    1495: (
        "",
        "023C",
        "014356020000",
        "014301000000",
        "014394000000",
        "014324010000",
        "050505",
    ),
    1497: (
        "",
        "023C",
        "014301000000",
        "014362020000",
        "050505",
    ),
    1498: (
        "",
        "023C",
        "014326020000",
        "014301000000",
        "014372040000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1496:1"}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1494:2": "\n",
    "15:1495:2": "\n",
    "15:1498:2": "\n",
}
SHARED_AUXILIARY = {
    ("SC", 1495): (
        (
            "似乎有位相貌堂堂的",
            "。\n",
            "来稍微指点一下吧，\n意下如何？",
        ),
        ("", "023C", "014301000000", "050505"),
    ),
    ("TC", 1495): (
        (
            "似乎有位相貌堂堂的",
            "吧。\n",
            "來稍微指點一下吧，\n如何？",
        ),
        ("", "023C", "014301000000", "050505"),
    ),
    ("SC", 1496): (
        (
            "听说本家的",
            "中有人才……\n有些冒昧，",
            "想来指点一下。\n不知可否？",
        ),
        ("", "023C", "014301000000", "050505"),
    ),
    ("TC", 1496): (
        (
            "據說本家的",
            "中有逸材……\n不好意思，",
            "想來指導指導。\n可否？",
        ),
        ("", "023C", "014301000000", "050505"),
    ),
    ("SC", 1497): (
        (
            "哦，没想到本家中有这样的",
            "。\n",
            "想锻炼他一下，\n可以吗？",
        ),
        ("", "023C", "014301000000", "050505"),
    ),
    ("TC", 1497): (
        (
            "哦，沒想到本家中有這樣的",
            "。\n",
            "想給他鍛煉一下，\n可以嗎？",
        ),
        ("", "023C", "014301000000", "050505"),
    ),
}
AUXILIARY_OVERRIDES = PREVIOUS.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    {},
)
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "six_of_eleven_talent_training_proposals_with_uniform_plus_15_pk_jp_"
    "mapping_exact_base_pk_sc_tc_context_and_blank_training_pk_en_"
    "auxiliary_records_面構え_naturalized_as_기개_not_관상_当家_as_우리_가문_"
    "僭越_as_외람_dynamic_candidate_and_instructor_tokens_three_hidden_lf_"
    "slots_preserved_fullwidth_punctuation_removed_live_inflection_stems_"
    "and_current_line_counts_preserved_runtime_fragment_pending"
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
                f"segment 906 hidden LF received a decision: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "기개",
        "우리 가문",
        "외람",
        "인재",
        "기량",
        "지도",
        "비결",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 906 meaning or terminology drifted: {required}"
            )
    for forbidden in ("관상", "당가", "、", "？"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 906 forbidden term or punctuation retained: "
                f"{forbidden}"
            )
    stem_expectations = {
        "15:1493:1": "모양이군\n",
        "15:1493:2": "괜찮겠지?",
        "15:1494:1": "들었소",
        "15:1494:3": "단련시켜",
        "15:1494:4": "주시겠습니까?",
        "15:1495:1": "듯",
        "15:1495:3": "주면",
        "15:1495:4": "좋다",
        "15:1496:2": "괜찮으신지",
        "15:1497:2": "괜찮은",
        "15:1498:1": "듯",
        "15:1498:3": "괜찮",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 906 live inflection stem drifted: {coordinate}"
            )
    instructor_subject_coordinates = (
        "15:1493:2",
        "15:1494:3",
        "15:1495:3",
        "15:1496:2",
        "15:1497:2",
    )
    if any(
        not raw_translations[coordinate].startswith("이(가)")
        for coordinate in instructor_subject_coordinates
    ):
        raise RuntimeError(
            "segment 906 instructor subject-token relation drifted"
        )
    if not raw_translations["15:1498:3"].startswith("의 비결을"):
        raise RuntimeError(
            "segment 906 instructor possessive-token relation drifted"
        )
    candidate_relation_expectations = {
        "15:1493:1": "이(가)",
        "15:1494:1": "이(가)",
        "15:1495:1": "이(가)",
        "15:1496:1": "중에",
        "15:1497:1": "이(가)",
        "15:1498:1": "이(가)",
    }
    for coordinate, prefix in candidate_relation_expectations.items():
        if not raw_translations[coordinate].startswith(prefix):
            raise RuntimeError(
                f"segment 906 candidate token relation drifted: {coordinate}"
            )
    if translations["15:1496:1"].count("…") != 2:
        raise RuntimeError("segment 906 ellipsis pair drifted")
    if any(
        ("pk", "EN", record_id) in AUXILIARY_OVERRIDES
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 906 training PK EN was not blank")
    if len(raw_translations) != 24:
        raise RuntimeError("segment 906 visible decision count drifted")


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
        raise RuntimeError("segment 906 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S906",
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
