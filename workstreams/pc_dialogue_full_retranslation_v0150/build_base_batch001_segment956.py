#!/usr/bin/env python3
"""Build Base authoring segment 956 decisions for the v0.15.0 retranslation."""

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
    / "base_msggame_B001_S956.private.v1.jsonl"
)
SEGMENT = 956
ACTION_TOKEN = "1B434D023C1B435A"
CASTLE_TOKEN = "026432"
TRANSLATIONS_BY_RECORD = {
    2001: (
        "공략을 위한 한 수로\n",
        "을(를) 실행해 보심이 어떠하신지요",
    ),
    2002: (
        "을(를) 공략하기 위해서도\n",
        "을(를) 추진하고자 하옵니다",
    ),
    2003: (
        "이야말로\n",
        "공략을 위한 최선책이라 사료되옵니다",
    ),
    2004: (
        "공략에 대비하여\n",
        "을(를) 건의",
    ),
    2005: (
        "을(를) 추진한다면\n",
        "공략으로 이어질 것이옵니다",
    ),
    2006: (
        "공략을 준비하며\n",
        "을(를) 실행하여\n채비를 갖추고자 하옵니다",
    ),
    2007: (
        "공략에 대비하여\n",
        "의 실행을 허락해 주시옵소서",
    ),
    2008: (
        "을(를) 허락해 주시옵소서\n",
        "공략을 위한\n대비도 될 것이옵니다",
    ),
    2009: (
        "공략 준비를 위해\n",
        "의 실행을 건의",
    ),
}
# S964(Base2082-2093) may import these source/gap-bound Korean tuples.
CANONICAL_TRANSLATION_TUPLES = {
    record_id: TRANSLATIONS_BY_RECORD[record_id]
    for record_id in range(2001, 2010)
}
CANONICAL_REUSE_GROUPS = {
    2001: (2001, 2085),
    2002: (2002, 2086),
    2003: (2003, 2087),
    2004: (2004, 2088),
    2005: (2005, 2089),
    2006: (2006, 2090),
    2007: (2007, 2091),
    2008: (2008, 2092),
    2009: (2009, 2083, 2093),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2001: ("攻略への一手として\n", "を実行してはいかが"),
    2002: ("を攻めるためにも\n", "を進めたく存ずる"),
    2003: ("こそ\n", "攻略への最善手かと"),
    2004: ("攻略に備え\n", "を具申"),
    2005: ("を進めれば\n", "攻めに繋がりましょうぞ"),
    2006: ("攻略へ向け\n", "を実行して\n支度を進めたく存じます"),
    2007: ("攻略に向け\n", "のお許しを"),
    2008: ("をお許しください\n", "攻略に向け\n備えともなりましょう"),
    2009: ("攻略準備のため\n", "の実行を具申"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2001: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2002: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2003: (ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    2004: (CASTLE_TOKEN, ACTION_TOKEN, "01438E000000050505"),
    2005: (ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    2006: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2007: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2008: (ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    2009: (CASTLE_TOKEN, ACTION_TOKEN, "0143CC010000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2009: (CASTLE_TOKEN, ACTION_TOKEN, "0143D2010000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2001): (
        ("作为攻略", "的方法，\n不如实行", "吧。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2001): (
        ("不妨執行", "，\n可作為", "攻略的一環。"),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2002): (
        ("为了攻打", "，\n我想推进", "吧。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2002): (
        ("盼能進行", "\n亦不失為", "攻略之要。"),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2006): (
        ("为了攻略", "，\n我想实行", "，\n推进准备工作。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2006): (
        ("針對", "攻略，\n盼能執行", "做好準備。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2001: (
        ("As a means of capturing ", ", what would you think of executing ", "?"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2002: (
        ("I believe we should execute ", " to aid with our attack on ", "."),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2006: (
        ("I would like to execute ", " in preparation for our attack on ", "."),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B115_A_pristine_base_pc_jp_authoritative_"
    "castle_capture_preparation_and_dynamic_action_policy_proposals_with_"
    "explicit_base2001_2009_to_pk2031_2039_mapping_exact_base_pk_jp_sc_"
    "tc_literals_and_pk_en_auxiliary_context_dynamic_castle_026432_and_"
    "colour_wrapped_action_1b434d_023c_1b435a_tokens_具申_as_geonui_"
    "speaker_specific_historical_register_current_korean_morphology_"
    "terminal_corpora_base_pk_2009_opcode_divergence_recorded_canonical_"
    "tuples_exposed_for_2083_2085_2093_reuse_current_line_counts_and_"
    "protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    142: ("하다", "하겠습니다", "하겠사옵니다"),
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    142: EXPECTED_BASE_MORPHOLOGY_TERMINALS[142],
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if CANONICAL_TRANSLATION_TUPLES != TRANSLATIONS_BY_RECORD:
        raise RuntimeError("segment 956 canonical Korean tuple export drifted")
    if CANONICAL_REUSE_GROUPS != {
        **{
            record_id: (record_id, record_id + 84)
            for record_id in range(2001, 2009)
        },
        2009: (2009, 2083, 2093),
    }:
        raise RuntimeError("segment 956 canonical reuse group drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 956 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2009}:
        raise RuntimeError("segment 956 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 956 pristine/current gap drifted")
    joined = "\n".join(translations.values())
    for required in (
        "공략",
        "최선책",
        "건의",
        "채비",
        "허락해 주시옵소서",
        "사료되옵니다",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 956 required meaning/register drifted: {required}"
            )
    for forbidden in ("당가", "진행하고자", "공격으로 이어", "여기는"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 956 forbidden wording retained: {forbidden}"
            )
    if len(raw_translations) != 18 or len(translations) != 18:
        raise RuntimeError("segment 956 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
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
    SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 18 or len(validated) != len(translations):
        raise RuntimeError("segment 956 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"]
        or row["switch_korean_used"]
        for row in rows
    ):
        raise RuntimeError("segment 956 classification/authority drifted")
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
                "segment": "base_msggame_B001_S956",
                "source_literal_count": 18,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "dynamic_action_policy_token": ACTION_TOKEN,
                "dynamic_castle_token": CASTLE_TOKEN,
                "canonical_translation_tuple_count": len(
                    CANONICAL_TRANSLATION_TUPLES
                ),
                "canonical_reuse_groups": CANONICAL_REUSE_GROUPS,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2009],
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
