#!/usr/bin/env python3
"""Build Base authoring segment 953 decisions for the v0.15.0 retranslation."""

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
    / "base_msggame_B001_S953.private.v1.jsonl"
)
SEGMENT = 953
ACTION_TOKEN = "1B434D023C1B435A"
DAY_TOKEN_GAPS = ("", "0232", "050505")
ACTION_TIME_TRANSLATION = (
    "이때는",
    "을(를)\n실행할 때라고",
)
CURRENT_ACTION_TIME_TRANSLATION = (
    "지금은",
    "을(를)\n실행할 때라고",
)
TRANSLATIONS_BY_RECORD = {
    1966: (
        "작업에 착수한다\n완료까지 예상 기간은",
        "일 정도다\n성과를 기대하시오",
    ),
    1967: (
        "작업 예상 기간을 물으셨습니까?\n완료까지는\n대략",
        "일로 보고 있습니다",
    ),
    1968: (
        "작업에 착수하겠습니다\n",
        "일가량 걸릴 전망이나\n반드시 성과를 내겠습니다",
    ),
    1969: ACTION_TIME_TRANSLATION,
    1970: ("에 관해\n건의",),
    1971: (
        "을(를) 시행하는 것이\n좋을 것",
        "?",
    ),
    1972: (
        "을(를) 시행하",
        "자 하여\n허락을 청해야 한다고",
    ),
    1973: (
        "현 정세를 살피건대\n",
        "을(를) 건의",
    ),
    1974: (
        "문득 생각이 들었는데",
        "을(를)\n시행해 보는 건 어떻겠소?",
    ),
    1975: (
        "지금 해야 할 일은",
        "\n일 가능성이 없지는",
    ),
    1976: ACTION_TIME_TRANSLATION,
    1977: CURRENT_ACTION_TIME_TRANSLATION,
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1966: ("作業に着手する\n完了までの見込みは", "日ほど\n成果にご期待あれ"),
    1967: (
        "作業の見積もりにございますか？\n完了までは\nおよそ",
        "日を見ております",
    ),
    1968: (
        "作業に着手します\n",
        "日ほどかかる見込みなれど\n必ずや成果を残しましょう",
    ),
    1969: ("ここは", "を\n行うべき時かと"),
    1970: ("について\n具申",),
    1971: ("を行っては\nいかが", "か"),
    1972: ("の", "許可を\n願いたく"),
    1973: ("今の情勢を見るに\n", "を進言"),
    1974: ("ふと思ったが", "を\n行うのはいかがか？"),
    1975: ("今、なすべきは", "\nかもしれ"),
    1976: ("ここは", "を\n行うべき時かと"),
    1977: ("今は", "を\n行うべき時かと"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1966: DAY_TOKEN_GAPS,
    1967: DAY_TOKEN_GAPS,
    1968: DAY_TOKEN_GAPS,
    1969: ("", ACTION_TOKEN, "0143E2000000050505"),
    1970: (ACTION_TOKEN, "01438E000000050505"),
    1971: (ACTION_TOKEN, "014356020000", "050505"),
    1972: (ACTION_TOKEN, "01438A040000", "0143E2000000050505"),
    1973: ("", ACTION_TOKEN, "0143CC010000050505"),
    1974: ("", ACTION_TOKEN, "050505"),
    1975: ("", ACTION_TOKEN, "0143E0020000050505"),
    1976: ("", ACTION_TOKEN, "0143E2000000050505"),
    1977: ("", ACTION_TOKEN, "0143E2000000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1971: (ACTION_TOKEN, "014362020000", "050505"),
    1972: (ACTION_TOKEN, "014396040000", "0143E2000000050505"),
    1973: ("", ACTION_TOKEN, "0143D2010000050505"),
    1975: ("", ACTION_TOKEN, "0143EC020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
ACTION_AUX_GAPS = ("", ACTION_TOKEN, "050505")
SHARED_AUXILIARY = {
    ("SC", 1969): (("此时此刻应执行\n", "。"), ACTION_AUX_GAPS),
    ("TC", 1969): (("此刻應為進行", "之時。"), ACTION_AUX_GAPS),
    ("SC", 1970): (("关于", "\n属下有事呈报。"), ACTION_AUX_GAPS),
    ("TC", 1970): (("微臣奏請", "。"), ACTION_AUX_GAPS),
    ("SC", 1971): (("进行", "，\n怎么样呢？"), ACTION_AUX_GAPS),
    ("TC", 1971): (("不妨進行", "。"), ACTION_AUX_GAPS),
    ("SC", 1972): (("希望可以准许\n", "。"), ACTION_AUX_GAPS),
    ("TC", 1972): (("望請大人批准", "。"), ACTION_AUX_GAPS),
    ("SC", 1973): (("考虑到目前的情势，\n建议", "。"), ACTION_AUX_GAPS),
    ("TC", 1973): (("依當今情勢來看，\n微臣建議", "。"), ACTION_AUX_GAPS),
    ("SC", 1976): (("窃以为眼下应当实行\n", "。"), ACTION_AUX_GAPS),
    ("TC", 1976): (("此刻應為進行", "之時。"), ACTION_AUX_GAPS),
    ("SC", 1977): (("我认为现在应当实行\n", "。"), ACTION_AUX_GAPS),
    ("TC", 1977): (("目前方為進行", "之時。"), ACTION_AUX_GAPS),
}
PK_EN_AUXILIARY = {
    1969: (("I think it is time we conduct ", "."), ACTION_AUX_GAPS),
    1970: (("I have a submission concerning ", "."), ACTION_AUX_GAPS),
    1971: (("What do you think of conducting ", "?"), ACTION_AUX_GAPS),
    1972: (("I was hoping to ask permission for ", "."), ACTION_AUX_GAPS),
    1973: (
        ("Considering the current situation, I would counsel for ", "."),
        ACTION_AUX_GAPS,
    ),
    1976: (
        ("I believe this would be a good time to conduct ", "."),
        ACTION_AUX_GAPS,
    ),
    1977: (("I think now is a good time to conduct ", "."), ACTION_AUX_GAPS),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B114_C_pristine_base_pc_jp_authoritative_"
    "work_start_estimate_and_peacetime_dynamic_action_policy_proposals_"
    "with_explicit_base1966_1977_to_pk1996_2007_mapping_exact_base_pk_jp_"
    "sc_tc_and_actual_pk_en_auxiliary_context_numeric_days_token_0232_"
    "dynamic_action_policy_token_1b434d_023c_1b435a_direction_current_"
    "korean_morphology_terminal_corpora_and_base_pk_opcode_divergences_"
    "recorded_1969_1976_exact_tuple_object_reuse_current_line_counts_and_"
    "protected_skeleton_preserved_runtime_fragment_pending"
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
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
    598: ("이겠지요", "이리라", "이겠지"),
    736: ("않습니다", "않는다"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    142: EXPECTED_BASE_MORPHOLOGY_TERMINALS[142],
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    748: EXPECTED_BASE_MORPHOLOGY_TERMINALS[736],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if (
        TRANSLATIONS_BY_RECORD[1969] is not ACTION_TIME_TRANSLATION
        or TRANSLATIONS_BY_RECORD[1976] is not ACTION_TIME_TRANSLATION
    ):
        raise RuntimeError("segment 953 Base1969/1976 canonical tuple split")
    if (
        EXPECTED_BASE_JP[1969] != EXPECTED_BASE_JP[1976]
        or EXPECTED_BASE_GAPS[1969] != EXPECTED_BASE_GAPS[1976]
    ):
        raise RuntimeError("segment 953 Base1969/1976 source reuse drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 953 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {1971, 1972, 1973, 1975}:
        raise RuntimeError("segment 953 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 953 pristine-to-current gap drifted")
    joined = "\n".join(translations.values())
    for required in (
        "작업에 착수",
        "예상 기간",
        "성과를 기대",
        "현 정세",
        "허락을 청",
        "건의",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 953 required meaning drifted: {required}")
    for forbidden in ("전중", "기회라", "여기는"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 953 forbidden phrasing retained: {forbidden}"
            )
    for record_id in (1969, 1976, 1977):
        if TRANSLATIONS_BY_RECORD[record_id][1].endswith("생각"):
            raise RuntimeError(
                f"segment 953 morphology terminal duplicates 생각: {record_id}"
            )
    if TRANSLATIONS_BY_RECORD[1975][1] != "\n일 가능성이 없지는":
        raise RuntimeError("segment 953 かもしれない polarity drifted")
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 953 visible decision count drifted")


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
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 953 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 953 runtime classification drifted")
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
                "segment": "base_msggame_B001_S953",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "numeric_token_direction": {"0232": "estimated_days"},
                "dynamic_action_policy_token": ACTION_TOKEN,
                "canonical_reuse": {"1969=1976": True},
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1971,
                    1972,
                    1973,
                    1975,
                ],
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
