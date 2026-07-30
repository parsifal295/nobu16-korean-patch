#!/usr/bin/env python3
"""Build Base authoring segment 957 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment935 as SUPPORT


ENGINE = SUPPORT.ENGINE
COMMON = SUPPORT.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S957.private.v1.jsonl"
)
SEGMENT = 957
ACTION_TOKEN = "1B434D023C1B435A"
CASTLE_TOKEN = "026432"
TRANSLATIONS_BY_RECORD = {
    2010: (
        "을(를) 공략하려면 비축이 부족하니…\n",
        "을(를) 실행해 보는 게 어떻겠소?",
    ),
    2011: (
        "공략에 대비하여\n",
        "을(를) 거행하여\n군비를 갖추겠노라",
    ),
    2012: (
        "을(를) 실행하여\n",
        "공략에 대비하는 것이 어떠하겠소",
    ),
    2013: (
        "공략에는 비축도 필요할 듯하니\n",
        "을(를) 추진하고자 하옵니다",
    ),
    2014: (
        "공략에 대비하여\n",
        "을(를) 시행하고 싶소",
    ),
    2015: (
        "공략에 필요한 비축이 넉넉지 않으니\n지금은",
        "이야말로 필요하다고 사료되옵니다",
    ),
    2016: (
        "공략을 위해\n",
        "도 필요하다고 사료되옵니다",
    ),
    2017: (
        "",
        "공략은 아직 시기상조인 듯하니\n지금은",
        "을(를) 통해 대비를 갖추어야 하오",
    ),
    2018: (
        "공략에는 대비가 필요합니다\n",
        "을(를) 시행하여 만전을 기합시다",
    ),
    2019: (
        "",
        "공략에 앞서\n",
        "을(를) 시행해 대비를 갖추리라",
    ),
    2020: (
        "",
        "공략에는\n많은 비축이 필요할 것이옵니다\n",
        "을(를) 시행해 보심이 어떠하옵니까",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:2017:0": "",
    "15:2019:0": "",
    "15:2020:0": "",
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if f"15:{record_id}:{literal_id}"
    not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2010: ("を攻めるには蓄えがな…\n", "をしてはどうだ？"),
    2011: ("攻略に向け\n", "を執り行い\n軍備を整えん"),
    2012: ("を実行し\n", "攻めへ備えては"),
    2013: ("攻めには蓄えも必要かと\n", "を進めたく存じます"),
    2014: ("攻略に備え\n", "を行いたい"),
    2015: ("攻略には蓄えが心許なく\nここは", "こそが必要かと"),
    2016: ("攻略のため\n", "も必要かと存じます"),
    2017: ("", "攻めは時期尚早かと\nここは", "により備えを進めるべし"),
    2018: ("攻略には備えが必要です\n", "にて万全を期しましょう"),
    2019: ("", "攻略に先駆け\n", "にて備えを蓄えん"),
    2020: (
        "",
        "攻略には\n多くの蓄えが必要となりましょう\n",
        "はいかがでしょうか",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2010: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2011: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2012: (ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    2013: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2014: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2015: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2016: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2017: ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2018: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2019: ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2020: ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2010:0"}
SHARED_AUXILIARY = {
    ("SC", 2012): (
        ("不如实行", "，\n为进攻", "做准备吧。"),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2012): (
        ("不妨執行", "\n以備", "攻略。"),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2013): (
        ("攻打", "也需要储备，\n请您推进", "。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2013): (
        ("攻略亦須養威蓄銳，\n盼能進行", "。"),
        (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2014): (
        ("为了替攻略", "做准备，\n我想执行", "。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2014): (
        ("盼能進行", "\n以備", "攻略。"),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2018): (
        ("攻略需要准备，\n期待", "做到万全。"),
        (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2018): (
        ("攻略須做好準備。\n利用", "以求萬無一失吧！"),
        (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2012: (
        ("Executing ", " would be useful as preparation for capturing ", "."),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2013: (
        (
            "We must ready ourselves for the attack on ",
            ". I would recommend executing ",
            ".",
        ),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2014: (
        ("I want to perform ", " in preparation for our attack on ", "."),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2018: (
        (
            "We need to prepare for our attack on ",
            ". ",
            " should provide all we need.",
        ),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B115_A_pristine_base_pc_jp_authoritative_"
    "castle_capture_stockpile_armament_and_dynamic_action_preparation_"
    "proposals_with_explicit_base2010_2020_to_pk2040_2050_mapping_exact_"
    "base_pk_jp_sc_tc_literals_gaps_and_pk_en_auxiliary_context_dynamic_"
    "castle_026432_and_colour_wrapped_action_1b434d_023c_1b435a_tokens_"
    "speaker_specific_plain_formal_and_historical_register_project_pair_"
    "ellipsis_2010_0_three_hidden_empty_literals_excluded_current_line_"
    "counts_and_protected_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 957 Base-to-PK mapping drifted")
    if EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 957 Base-to-PK gap drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 957 pristine/current gap drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {
        "15:2017:0": "",
        "15:2019:0": "",
        "15:2020:0": "",
    }:
        raise RuntimeError("segment 957 hidden exclusion drifted")
    if (
        raw_translations["15:2010:0"].count("…") != 1
        or translations["15:2010:0"].count("…") != 2
    ):
        raise RuntimeError("segment 957 ellipsis seed/pair drifted")
    joined = "\n".join(translations.values())
    for required in (
        "비축",
        "군비",
        "시기상조",
        "만전을 기합시다",
        "사료되옵니다",
        "갖추겠노라",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 957 required meaning/register drifted: {required}"
            )
    for forbidden in ("여기는", "비축이 말이오", "진행해야", "공격에는"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 957 forbidden wording retained: {forbidden}"
            )
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 957 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
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
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 957 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"]
        or row["switch_korean_used"]
        for row in rows
    ):
        raise RuntimeError("segment 957 classification/authority drifted")
    line_distribution = {
        line_count: sum(
            text.count("\n") + 1 == line_count
            for text in translations.values()
        )
        for line_count in (1, 2, 3)
    }
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S957",
                "source_literal_count": 25,
                "decision_count": len(rows),
                "hidden_non_display_count": 3,
                "runtime_fragment_pending": len(rows),
                "dynamic_action_policy_token": ACTION_TOKEN,
                "dynamic_castle_token": CASTLE_TOKEN,
                "ellipsis_pair_coordinates": sorted(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [],
                "pristine_current_gap_divergence_records": [],
                "lf_count": sum(
                    text.count("\n") for text in translations.values()
                ),
                "line_distribution": line_distribution,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
