#!/usr/bin/env python3
"""Build Base authoring segment 955 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment954 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S955.private.v1.jsonl"
)
SEGMENT = 955
ACTION_TOKEN = PREVIOUS.ACTION_TOKEN
CASTLE_TOKEN = "026432"
WARTIME_OPPORTUNITY_TRANSLATION = (
    "전시로 분주하신 때에 실례",
    "\n",
    "을(를) 시행할 때라고 여기옵니다",
)
CIVILIAN_CONSIDERATION_TRANSLATION = (
    "전장 밖에도 백성이 살아가고 있으니\n",
    "을(를) 건의",
)
TRANSLATIONS_BY_RECORD = {
    1989: WARTIME_OPPORTUNITY_TRANSLATION,
    1990: (
        "싸움이 한창인 때에 실례하오\n",
        "을(를) 건의",
    ),
    1991: (
        "현재 벌이는 싸움 이후를 내다보고\n",
        "을(를) 시행하는 게 어떻겠소?",
    ),
    1992: WARTIME_OPPORTUNITY_TRANSLATION,
    1993: (
        "싸움이 한창인데 이런 말씀을 드리기 송구하오…\n",
        "을(를) 추진하고자 하오",
    ),
    1994: CIVILIAN_CONSIDERATION_TRANSLATION,
    1995: (
        "전시이지만 양해해 주시오\n",
        "을(를) 추진하고자 하오",
    ),
    1996: CIVILIAN_CONSIDERATION_TRANSLATION,
    1997: PREVIOUS.WARTIME_PROPOSAL_TRANSLATION,
    1998: (
        "을(를) 공략하기 위해서라도\n지금은",
        "을(를)\n내게 맡겨 주지 않겠나?",
    ),
    1999: (
        "을(를) 공략할 준비를 위해\n",
        "의 시행을 건의",
    ),
    2000: (
        "",
        "을(를) 공략하지 않는 지금\n대비책으로",
        "을(를)\n시행해 두는 것이 좋을 듯하옵니다",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1989:1": "\n",
    "15:1992:1": "\n",
    "15:1997:1": "\n",
    "15:2000:0": "",
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1989: ("戦にて多忙の折失礼", "\n", "の機と存じます"),
    1990: ("戦の最中なれど御免\n", "を具申"),
    1991: ("現在の戦の先を見据え\n", "を実行しては"),
    1992: ("戦にて多忙の折失礼", "\n", "の機と存じます"),
    1993: ("戦の最中に言うも心苦しいが…\n", "を進めたく存ずる"),
    1994: ("戦地以外にも人はおりますれば\n", "を具申"),
    1995: ("戦時なれど御免\n", "を進めたく存ずる"),
    1996: ("戦地以外にも人はおりますれば\n", "を具申"),
    1997: ("戦時なれど具申", "\n", "を進めたく存ずる"),
    1998: ("を攻めるためにも\nここは", "を\nやらせてはくれねえか？"),
    1999: ("攻略準備のため\n", "の実行を具申"),
    2000: ("", "攻めを控えた今\n備えとして", "を\n実行しておくべきかと"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1989: ("", "01438E000000", ACTION_TOKEN, "050505"),
    1990: ("", ACTION_TOKEN, "01438E000000050505"),
    1991: ("", ACTION_TOKEN, "050505"),
    1992: ("", "01438E000000", ACTION_TOKEN, "050505"),
    1993: ("", ACTION_TOKEN, "050505"),
    1994: ("", ACTION_TOKEN, "01438E000000050505"),
    1995: ("", ACTION_TOKEN, "050505"),
    1996: ("", ACTION_TOKEN, "01438E000000050505"),
    1997: ("", "01438E000000", ACTION_TOKEN, "050505"),
    1998: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    1999: (
        CASTLE_TOKEN,
        ACTION_TOKEN,
        "0143CC010000050505",
    ),
    2000: ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1999: (
        CASTLE_TOKEN,
        ACTION_TOKEN,
        "0143D2010000050505",
    ),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:1993:0"}
ACTION_AUX_GAPS = ("", ACTION_TOKEN, "050505")
SHARED_AUXILIARY = {
    ("SC", 1989): (
        ("在您忙于战事时打扰您了，\n窃以为现在是", "的良机。"),
        ACTION_AUX_GAPS,
    ),
    ("TC", 1989): (
        ("戰事繁忙中且容稟告，\n現為", "之機。"),
        ACTION_AUX_GAPS,
    ),
    ("SC", 1990): (
        ("抱歉在战事中打扰您了，\n容我呈报", "。"),
        ACTION_AUX_GAPS,
    ),
    ("TC", 1990): (
        ("陣中打擾，望請見諒。\n微臣奏請", "。"),
        ACTION_AUX_GAPS,
    ),
    ("SC", 1994): (
        ("战地以外也有人在，\n容我呈报", "。"),
        ACTION_AUX_GAPS,
    ),
    ("TC", 1994): (
        ("戰場之外亦有百姓，\n微臣奏請", "。"),
        ACTION_AUX_GAPS,
    ),
    ("SC", 2000): (
        ("现在要攻打", "，\n为了备战，\n似乎应当实行", "。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2000): (
        ("攻略現且斂戢，\n應當執行", "以備戰。"),
        (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1989: (
        (
            "I am sorry to interfere in the midst of battle, "
            "but I believe this may be a good opportunity to perform ",
            ".",
        ),
        ACTION_AUX_GAPS,
    ),
    1990: (
        (
            "I apologize for asking in the middle of battle, "
            "but I have a submission for ",
            ".",
        ),
        ACTION_AUX_GAPS,
    ),
    1994: (
        (
            "As we also have personnel outside of the battlefield, "
            "I wanted to make a submission for ",
            ".",
        ),
        ACTION_AUX_GAPS,
    ),
    2000: (
        (
            "Now that we are not attacking ",
            ", I think it would be good to make preparations by executing ",
            ".",
        ),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B114_C_pristine_base_pc_jp_authoritative_"
    "wartime_dynamic_action_policy_proposals_and_attack_preparation_with_"
    "explicit_base1989_2000_to_pk2019_2030_mapping_exact_base_pk_jp_sc_"
    "tc_and_actual_pk_en_auxiliary_context_dynamic_action_policy_token_"
    "1b434d_023c_1b435a_and_target_castle_token_026432_direction_current_"
    "korean_morphology_terminal_corpora_and_base_pk_opcode_divergence_"
    "recorded_hidden_1989_1992_1997_lf_and_2000_empty_excluded_exact_"
    "1989_1992_1994_1996_and_cross_segment_1987_1997_tuple_object_reuse_"
    "project_ellipsis_pair_current_line_counts_and_protected_skeleton_"
    "preserved_runtime_fragment_pending"
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
    if (
        TRANSLATIONS_BY_RECORD[1989] is not WARTIME_OPPORTUNITY_TRANSLATION
        or TRANSLATIONS_BY_RECORD[1992]
        is not WARTIME_OPPORTUNITY_TRANSLATION
        or TRANSLATIONS_BY_RECORD[1994]
        is not CIVILIAN_CONSIDERATION_TRANSLATION
        or TRANSLATIONS_BY_RECORD[1996]
        is not CIVILIAN_CONSIDERATION_TRANSLATION
        or TRANSLATIONS_BY_RECORD[1997]
        is not PREVIOUS.WARTIME_PROPOSAL_TRANSLATION
    ):
        raise RuntimeError("segment 955 canonical tuple object reuse drifted")
    for first, second in ((1989, 1992), (1994, 1996)):
        if (
            EXPECTED_BASE_JP[first] != EXPECTED_BASE_JP[second]
            or EXPECTED_BASE_GAPS[first] != EXPECTED_BASE_GAPS[second]
        ):
            raise RuntimeError(
                f"segment 955 Base{first}/{second} source reuse drifted"
            )
    if (
        EXPECTED_BASE_JP[1997] != PREVIOUS.EXPECTED_BASE_JP[1987]
        or EXPECTED_BASE_GAPS[1997] != PREVIOUS.EXPECTED_BASE_GAPS[1987]
    ):
        raise RuntimeError("segment 955 Base1987/1997 source reuse drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 955 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {1999}:
        raise RuntimeError("segment 955 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 955 pristine-to-current gap drifted")
    expected_hidden = {
        "15:1989:1": "\n",
        "15:1992:1": "\n",
        "15:1997:1": "\n",
        "15:2000:0": "",
    }
    if EXCLUDED_NONVISIBLE_COORDINATES != expected_hidden:
        raise RuntimeError("segment 955 hidden literal exclusion drifted")
    if (
        raw_translations["15:1993:0"].count("…") != 1
        or translations["15:1993:0"].count("…") != 2
    ):
        raise RuntimeError("segment 955 project ellipsis pair drifted")
    joined = "\n".join(translations.values())
    for required in (
        "전시",
        "싸움이 한창",
        "전장 밖",
        "백성",
        "공략",
        "대비책",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 955 required meaning drifted: {required}")
    for forbidden in ("전중", "기회라", "이곳은", "공격을 삼가는 지금"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 955 forbidden phrasing retained: {forbidden}"
            )
    if len(raw_translations) != 24 or len(translations) != 24:
        raise RuntimeError("segment 955 visible decision count drifted")


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
    if len(rows) != 24 or len(validated) != len(translations):
        raise RuntimeError("segment 955 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 955 runtime classification drifted")
    line_distribution = {
        line_count: sum(
            text.count("\n") + 1 == line_count
            for text in translations.values()
        )
        for line_count in (1, 2)
    }
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S955",
                "source_literal_count": 28,
                "decision_count": len(rows),
                "hidden_non_display_count": 4,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "dynamic_action_policy_token": ACTION_TOKEN,
                "target_castle_token": CASTLE_TOKEN,
                "canonical_reuse": {
                    "1987=1997": True,
                    "1989=1992": True,
                    "1994=1996": True,
                },
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [1999],
                "pristine_current_gap_divergence_records": [],
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": line_distribution,
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
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
