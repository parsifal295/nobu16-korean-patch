#!/usr/bin/env python3
"""Build Base authoring segment 954 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment953 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S954.private.v1.jsonl"
)
SEGMENT = 954
ACTION_TOKEN = PREVIOUS.ACTION_TOKEN
WARTIME_PROPOSAL_TRANSLATION = (
    "전시이지만 건의",
    "\n",
    "을(를) 추진하고자 하오",
)
TRANSLATIONS_BY_RECORD = {
    1978: ("의 시행을\n건의",),
    1979: (
        "시급한 사안은",
        "만\n",
        "을(를) 시행하는 편이 어떻겠소?",
    ),
    1980: PREVIOUS.CURRENT_ACTION_TIME_TRANSLATION,
    1981: ("의 시행을\n검토해 보는 것이 어떻겠소?",),
    1982: (
        "서두를 일은 아닙니다만\n",
        "을(를) 시행하는 건 어떨까요?",
    ),
    1983: (
        "꼭\n",
        "을(를) 시행해 주기를 바라오",
    ),
    1984: (
        "어떻습니까?\n",
        "을(를) 시행해 보시겠습니까?",
    ),
    1985: PREVIOUS.ACTION_TIME_TRANSLATION,
    1986: (
        "싸움이 한창인데 미안하네\n",
        "을(를) 내가 맡게 해 주게",
    ),
    1987: WARTIME_PROPOSAL_TRANSLATION,
    1988: (
        "싸움만이 전략의 전부는 아니니\n",
        "의 시행을 허락해 주셨으면 하오",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1987:1": "\n"}
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
    1978: ("の執行を\n具申",),
    1979: ("急ぎでは", "が\n", "を実行すべきでは？"),
    1980: ("今は", "を\n行うべき時かと"),
    1981: ("の実行を\n検討してみてはいかがじゃ？",),
    1982: ("急ぎではありませんが\n", "などはどうかしら？"),
    1983: ("ぜひとも\n", "の実行を願いたい"),
    1984: ("どうでしょう？\n", "を行ってみては？"),
    1985: ("ここは", "を\n行うべき時かと"),
    1986: ("戦の最中にすまねえ\n", "をやらせてくれ"),
    1987: ("戦時なれど具申", "\n", "を進めたく存ずる"),
    1988: ("戦のみが戦略にあらず\n", "の許可をいただきたい"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1978: (ACTION_TOKEN, "01438E000000050505"),
    1979: ("", "0143DA020000", ACTION_TOKEN, "050505"),
    1980: ("", ACTION_TOKEN, "0143E2000000050505"),
    1981: (ACTION_TOKEN, "050505"),
    1982: ("", ACTION_TOKEN, "050505"),
    1983: ("", ACTION_TOKEN, "050505"),
    1984: ("", ACTION_TOKEN, "050505"),
    1985: ("", ACTION_TOKEN, "0143E2000000050505"),
    1986: ("", ACTION_TOKEN, "050505"),
    1987: ("", "01438E000000", ACTION_TOKEN, "050505"),
    1988: ("", ACTION_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1979: ("", "0143E6020000", ACTION_TOKEN, "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
ACTION_AUX_GAPS = ("", ACTION_TOKEN, "050505")
SHARED_AUXILIARY = {
    ("SC", 1978): (("我来呈报\n", "的执行。"), ACTION_AUX_GAPS),
    ("TC", 1978): (("微臣奏請執行", "。"), ACTION_AUX_GAPS),
    ("SC", 1982): (
        ("虽然不算紧急，\n但", "等如何？"),
        ACTION_AUX_GAPS,
    ),
    ("TC", 1982): (
        ("此事不急，\n", "等是否要進行？"),
        ACTION_AUX_GAPS,
    ),
    ("SC", 1988): (
        ("战略并不仅限于战争，\n我想请您批准", "。"),
        ACTION_AUX_GAPS,
    ),
    ("TC", 1988): (
        ("戰略並非僅限於打仗，\n盼大人允准", "。"),
        ACTION_AUX_GAPS,
    ),
}
PK_EN_AUXILIARY = {
    1978: (
        ("I have a submission concerning the execution of ", "."),
        ACTION_AUX_GAPS,
    ),
    1982: (
        ("This is far from urgent, but how would you feel about ", "?"),
        ACTION_AUX_GAPS,
    ),
    1988: (
        (
            "War is not won by fighting alone. "
            "I would ask your permission to perform ",
            ".",
        ),
        ACTION_AUX_GAPS,
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B114_C_pristine_base_pc_jp_authoritative_"
    "peacetime_and_wartime_dynamic_action_policy_proposal_speaker_variants_"
    "with_explicit_base1978_1988_to_pk2008_2018_mapping_exact_base_pk_jp_"
    "sc_tc_and_actual_pk_en_auxiliary_context_dynamic_action_policy_token_"
    "1b434d_023c_1b435a_direction_current_korean_morphology_terminal_"
    "corpora_and_base_pk_opcode_divergence_recorded_1987_hidden_lf_"
    "excluded_cross_segment_exact_1977_1980_and_1969_1976_1985_tuple_"
    "object_reuse_current_line_counts_and_protected_skeleton_preserved_"
    "runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    142: ("하다", "하겠습니다", "하겠사옵니다"),
    226: (
        "생각합니다",
        "생각한다",
        "생각하오",
        "생각하옵니다",
        "생각하옵나이다",
    ),
    730: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    142: EXPECTED_BASE_MORPHOLOGY_TERMINALS[142],
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    742: EXPECTED_BASE_MORPHOLOGY_TERMINALS[730],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if (
        TRANSLATIONS_BY_RECORD[1980]
        is not PREVIOUS.CURRENT_ACTION_TIME_TRANSLATION
        or TRANSLATIONS_BY_RECORD[1985]
        is not PREVIOUS.ACTION_TIME_TRANSLATION
        or TRANSLATIONS_BY_RECORD[1987] is not WARTIME_PROPOSAL_TRANSLATION
    ):
        raise RuntimeError("segment 954 canonical tuple object reuse drifted")
    if (
        EXPECTED_BASE_JP[1980] != PREVIOUS.EXPECTED_BASE_JP[1977]
        or EXPECTED_BASE_GAPS[1980] != PREVIOUS.EXPECTED_BASE_GAPS[1977]
        or EXPECTED_BASE_JP[1985] != PREVIOUS.EXPECTED_BASE_JP[1969]
        or EXPECTED_BASE_GAPS[1985] != PREVIOUS.EXPECTED_BASE_GAPS[1969]
    ):
        raise RuntimeError("segment 954 cross-segment source reuse drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 954 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {1979}:
        raise RuntimeError("segment 954 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 954 pristine-to-current gap drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:1987:1": "\n"}:
        raise RuntimeError("segment 954 hidden LF exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "시급한 사안",
        "서두를 일",
        "전시",
        "싸움이 한창",
        "전략의 전부",
        "허락",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 954 required meaning drifted: {required}")
    for forbidden in ("전중", "하게 해다오", "행하는 것이 어떻겠소"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 954 forbidden phrasing retained: {forbidden}"
            )
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 954 visible decision count drifted")


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
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 954 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 954 runtime classification drifted")
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
                "segment": "base_msggame_B001_S954",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "dynamic_action_policy_token": ACTION_TOKEN,
                "canonical_reuse": {
                    "1977=1980": True,
                    "1969=1976=1985": True,
                    "1987_local_canonical": True,
                },
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [1979],
                "pristine_current_gap_divergence_records": [],
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": line_distribution,
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
