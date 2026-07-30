#!/usr/bin/env python3
"""Build Base authoring segment 947 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment946 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S947.private.v1.jsonl"
)
SEGMENT = 947
POLICY_ACTION = PREVIOUS.TRANSLATIONS_BY_RECORD[1919][0]
FACILITY_ACTION = "성하 시설을 증설"
KOKUDAKA_ACTION = "석고를 증대"
TRANSLATIONS_BY_RECORD = {
    1920: (
        POLICY_ACTION,
        "\n",
        "년",
        "개월 안에 목표 합계:",
        "(LV)\n현재 합계:",
        "(LV)",
    ),
    1921: (
        POLICY_ACTION,
        "\n",
        "일 안에 목표 합계:",
        "(LV)\n현재 합계:",
        "(LV)",
    ),
    1922: (
        FACILITY_ACTION,
        "\n",
        "개월 안에 목표 시설 수:",
        "\n현재 시설 수:",
    ),
    1923: (
        FACILITY_ACTION,
        "\n",
        "년",
        "개월 안에 목표 시설 수:",
        "\n현재 시설 수:",
    ),
    1924: (
        FACILITY_ACTION,
        "\n",
        "일 안에 목표 시설 수:",
        "\n현재 시설 수:",
    ),
    1925: (
        KOKUDAKA_ACTION,
        "\n",
        "개월 안에 목표 석고:",
        "\n현재 석고:",
        "",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1920:1": "\n",
    "15:1921:1": "\n",
    "15:1922:1": "\n",
    "15:1923:1": "\n",
    "15:1924:1": "\n",
    "15:1925:1": "\n",
    "15:1925:4": "",
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
    1920: (
        "政策発令水準を上げ",
        "\n",
        "年",
        "カ月以内に目指すは合計",
        "（LV）\n今は合計",
        "（LV）",
    ),
    1921: (
        "政策発令水準を上げ",
        "\n",
        "日以内に目指すは合計",
        "（LV）\n今は合計",
        "（LV）",
    ),
    1922: ("城下施設を増や", "\n", "カ月以内に目指すは", "\n今の施設数は"),
    1923: ("城下施設を増や", "\n", "年", "カ月以内に目指すは", "\n今の施設数は"),
    1924: ("城下施設を増や", "\n", "日以内に目指すは", "\n今の施設数は"),
    1925: ("石高を増や", "\n", "カ月以内に目指すは", "\n今は", ""),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1920: ("", "01431E040000", "0234", "0235", "0232", "0233", "01431A020000050505"),
    1921: ("", "01431E040000", "0236", "0232", "0233", "01431A020000050505"),
    1922: ("", "01437E040000", "0235", "0232", "023301431A020000050505"),
    1923: ("", "01437E040000", "0234", "0235", "0232", "023301431A020000050505"),
    1924: ("", "01437E040000", "0236", "0232", "023301431A020000050505"),
    1925: ("", "01437E040000", "0235", "0232", "0233", "01431A020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1920: ("", "01432A040000", "0234", "0235", "0232", "0233", "014326020000050505"),
    1921: ("", "01432A040000", "0236", "0232", "0233", "014326020000050505"),
    1922: ("", "01438A040000", "0235", "0232", "0233014326020000050505"),
    1923: ("", "01438A040000", "0234", "0235", "0232", "0233014326020000050505"),
    1924: ("", "01438A040000", "0236", "0232", "0233014326020000050505"),
    1925: ("", "01438A040000", "0235", "0232", "0233", "014326020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
MORPHOLOGY_SKIP_RECORD_IDS = {1925}
SHARED_AUXILIARY = {
    ("SC", 1920): (
        ("提高政策的颁布标准吧。\n在", "年", "个月以内，\n以", "（LV）为目标，目前是", "（LV）。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1921): (
        ("提高政策的颁布标准吧。\n在", "天以内，\n以", "（LV）为目标，目前是", "（LV）。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("SC", 1922): (
        ("增加城下设施吧。\n在", "个月以内，\n以", "为目标，目前是", "。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1923): (
        ("增加城下设施吧。。\n在", "年", "个月以内，\n以", "为目标，目前是", "。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1924): (
        ("增加城下设施吧。\n在", "天以内，\n以", "为目标，目前是", "。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("SC", 1925): (
        ("增加石高吧。\n在", "个月以内，\n以", "为目标，目前是", "。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1920): (
        ("目標是提升頒布政策的水準。水準需在\n", "年", "個月內合計提升至", "（LV），\n目前合計為", "（LV）。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1921): (
        ("目標是提升頒布政策的水準。水準需在\n", "日內合計提升至", "（LV），\n目前合計為", "（LV）。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("TC", 1922): (
        ("目標是增加城下設施。\n城下設施需在", "個月內增加至", "座，\n目前擁有", "座。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1923): (
        ("目標是增加城下設施。\n城下設施需在", "年", "個月內增加至", "座，\n目前擁有", "座。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1924): (
        ("目標是增加城下設施。\n城下設施需在", "日內增加至", "座，\n目前擁有", "座。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("TC", 1925): (
        ("目標是增加石高的數量。\n石高數量需在", "個月內增加至", "，\n目前為", "。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1920: (
        (
            "We should increase our issued policy standard. The current level total is ",
            ", but our goal is to achieve a level total of ",
            " within ",
            " year(s) and ",
            " month(s).",
        ),
        ("", "0233", "0232", "0234", "0235", "050505"),
    ),
    1921: (
        (
            "We should increase our issued policy standard. The current level total is ",
            ", but our goal is to achieve a level total of ",
            " within ",
            " day(s).",
        ),
        ("", "0233", "0232", "0236", "050505"),
    ),
    1922: (
        (
            "WeÖre looking to increase our number of castle town facilities. We currently possess ",
            ", but our goal is to have ",
            " within ",
            " month(s).",
        ),
        ("", "0233", "0232", "0235", "050505"),
    ),
    1923: (
        (
            "WeÖre looking to increase our number of castle town facilities. We currently possess ",
            ", but our goal is to have ",
            " within ",
            " year(s) and ",
            " month(s).",
        ),
        ("", "0233", "0232", "0234", "0235", "050505"),
    ),
    1924: (
        (
            "WeÖre looking to increase our number of castle town facilities. We currently possess ",
            ", but our goal is to have ",
            " within ",
            " day(s).",
        ),
        ("", "0233", "0232", "0236", "050505"),
    ),
    1925: (
        (
            "We should increase our crops. Our present yield is ",
            ", but our goal is a yield of ",
            " within ",
            " month(s).",
        ),
        ("", "0233", "0232", "0235", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B114_A_pristine_base_pc_jp_authoritative_"
    "policy_issue_level_castle_town_facility_count_and_kokudaka_deadline_"
    "goal_current_ui_with_explicit_base1920_1925_to_pk1950_1955_mapping_"
    "exact_base_pk_jp_sc_tc_and_pk_en_meaning_context_jp_authoritative_"
    "period_target_current_token_order_0234_years_0235_months_0236_days_"
    "0232_target_0233_current_korean_policy_balryeong_sujun_seongha_"
    "facility_seokgo_terms_ascii_parentheses_current_korean_morphology_"
    "terminal_corpora_and_all_base_pk_opcode_divergences_recorded_seven_"
    "hidden_literals_excluded_current_line_counts_and_protected_skeleton_"
    "preserved_runtime_fragment_pending_base_912px_not_applied"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    1054: ("합시다", "듯"),
    1150: ("합시다", "그렇군"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1162: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1150],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records, raw_translations
    if POLICY_ACTION != PREVIOUS.TRANSLATIONS_BY_RECORD[1919][0]:
        raise RuntimeError("segment 947 policy-action continuity drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 947 Base-to-PK mapping drifted")
    if any(
        EXPECTED_BASE_GAPS[record_id] == EXPECTED_PK_JP_GAPS[record_id]
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 947 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 947 pristine/current gap drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {
        "15:1920:1": "\n",
        "15:1921:1": "\n",
        "15:1922:1": "\n",
        "15:1923:1": "\n",
        "15:1924:1": "\n",
        "15:1925:1": "\n",
        "15:1925:4": "",
    }:
        raise RuntimeError("segment 947 hidden literal exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "정책 발령 수준",
        "성하 시설",
        "석고",
        "목표 합계:",
        "목표 시설 수:",
        "목표 석고:",
        "현재",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 947 required meaning drifted: {required}")
    for forbidden in ("（", "）", "개월 이내", "일 이내", "지금은", "성하 마을"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 947 forbidden phrasing retained: {forbidden}"
            )
    if (
        sum("(LV)" in text for text in translations.values()) != 4
        or len(translations) != 22
    ):
        raise RuntimeError("segment 947 unit/count drifted")


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
        skip_records=MORPHOLOGY_SKIP_RECORD_IDS,
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
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 947 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 947 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S947",
                "source_literal_count": 29,
                "decision_count": len(rows),
                "hidden_literals_excluded": 7,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "numeric_token_direction": {
                    "0232": "target_value",
                    "0233": "current_value",
                    "0234": "years",
                    "0235": "months",
                    "0236": "days",
                },
                "jp_token_order_authoritative": True,
                "pk_en_reordered_for_english": True,
                "ascii_parentheses_preserved": True,
                "base_912px_applied": False,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": sorted(RECORD_ARITIES),
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
