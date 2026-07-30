#!/usr/bin/env python3
"""Build Base authoring segment 948 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment947 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S948.private.v1.jsonl"
)
SEGMENT = 948
KOKUDAKA_ACTION = PREVIOUS.KOKUDAKA_ACTION
COMMERCE_ACTION = "상업을 증대"
CAPTURE_TARGET_ACTION = "공략 목표로 삼은 성을 함락"
TRANSLATIONS_BY_RECORD = {
    1926: (
        KOKUDAKA_ACTION,
        "\n",
        "년",
        "개월 안에 목표 석고:",
        "\n현재 석고:",
        "",
    ),
    1927: (
        KOKUDAKA_ACTION,
        "\n",
        "일 안에 목표 석고:",
        "\n현재 석고:",
        "",
    ),
    1928: (
        COMMERCE_ACTION,
        "\n",
        "개월 안에 목표 상업:",
        "\n현재 상업:",
        "",
    ),
    1929: (
        COMMERCE_ACTION,
        "\n",
        "년",
        "개월 안에 목표 상업:",
        "\n현재 상업:",
        "",
    ),
    1930: (
        COMMERCE_ACTION,
        "\n",
        "일 안에 목표 상업:",
        "\n현재 상업:",
        "",
    ),
    1931: (
        CAPTURE_TARGET_ACTION,
        "\n",
        "개월 안에 목표:",
        "회\n현재:",
        "회",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1926:1": "\n",
    "15:1926:5": "",
    "15:1927:1": "\n",
    "15:1927:4": "",
    "15:1928:1": "\n",
    "15:1928:4": "",
    "15:1929:1": "\n",
    "15:1929:5": "",
    "15:1930:1": "\n",
    "15:1930:4": "",
    "15:1931:1": "\n",
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
    1926: ("石高を増や", "\n", "年", "カ月以内に目指すは", "\n今は", ""),
    1927: ("石高を増や", "\n", "日以内に目指すは", "\n今は", ""),
    1928: ("商業を増や", "\n", "カ月以内に目指すは", "\n今は", ""),
    1929: ("商業を増や", "\n", "年", "カ月以内に目指すは", "\n今は", ""),
    1930: ("商業を増や", "\n", "日以内に目指すは", "\n今は", ""),
    1931: ("攻略目標とした城を落と", "\n", "カ月以内に目指すは", "回\n今は", "回"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1926: ("", "01437E040000", "0234", "0235", "0232", "0233", "01431A020000050505"),
    1927: ("", "01437E040000", "0236", "0232", "0233", "01431A020000050505"),
    1928: ("", "01437E040000", "0235", "0232", "0233", "01431A020000050505"),
    1929: ("", "01437E040000", "0234", "0235", "0232", "0233", "01431A020000050505"),
    1930: ("", "01437E040000", "0236", "0232", "0233", "01431A020000050505"),
    1931: ("", "01437E040000", "0235", "0232", "0233", "01431A020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1926: ("", "01438A040000", "0234", "0235", "0232", "0233", "014326020000050505"),
    1927: ("", "01438A040000", "0236", "0232", "0233", "014326020000050505"),
    1928: ("", "01438A040000", "0235", "0232", "0233", "014326020000050505"),
    1929: ("", "01438A040000", "0234", "0235", "0232", "0233", "014326020000050505"),
    1930: ("", "01438A040000", "0236", "0232", "0233", "014326020000050505"),
    1931: ("", "01438A040000", "0235", "0232", "0233", "014326020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
MORPHOLOGY_SKIP_RECORD_IDS = set(range(1926, 1931))
SHARED_AUXILIARY = {
    ("SC", 1926): (
        ("增加石高吧。\n在", "年", "个月以内，\n以", "为目标，目前是", "。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1927): (
        ("增加石高吧。\n在", "天以内，\n以", "为目标，目前是", "。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("SC", 1928): (
        ("提高商业吧。\n在", "年", "个月以内，\n以", "为目标，目前是", "。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1929): (
        ("提高商业吧。\n在", "年", "个月以内，\n以", "为目标，目前是", "。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1930): (
        ("提高商业吧。\n在", "天以内，\n以", "为目标，目前是", "。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("SC", 1931): (
        ("攻陷攻略目标的城吧。\n在", "个月以内，\n以", "次为目标，目前是", "次。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1926): (
        ("目標是增加石高的數量。\n石高數量需在", "年", "個月內增加至", "，\n目前為", "。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1927): (
        ("目標是增加石高的數量。\n石高數量需在", "日內增加至", "，\n目前為", "。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("TC", 1928): (
        ("目標是增加商業的數值。\n商業數值需在", "個月內增加至", "，\n目前為", "。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1929): (
        ("目標是增加商業的數值。\n商業數值需在", "年", "個月內增加至", "，\n目前為", "。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1930): (
        ("目標是增加商業的數值。\n商業數值需在", "日內增加至", "，\n目前為", "。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("TC", 1931): (
        ("目標是攻陷作為攻略目標的城。\n攻陷次數需在", "個月內達到", "次，\n目前為", "次。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1926: (
        (
            "We should increase our crops. Our present yield is ",
            ", but our goal is a yield of ",
            " within ",
            " year(s) and ",
            " month(s).",
        ),
        ("", "0233", "0232", "0234", "0235", "050505"),
    ),
    1927: (
        (
            "We should increase our crops. Our present yield is ",
            ", but our goal is a yield of ",
            " within ",
            " day(s).",
        ),
        ("", "0233", "0232", "0236", "050505"),
    ),
    1928: (
        (
            "We should increase commerce. We currently make ",
            ", but our goal is to be making ",
            " within ",
            " month(s).",
        ),
        ("", "0233", "0232", "0235", "050505"),
    ),
    1929: (
        (
            "We should increase commerce. We currently make ",
            ", but our goal is to be making ",
            " within ",
            " year(s) and ",
            " month(s).",
        ),
        ("", "0233", "0232", "0234", "0235", "050505"),
    ),
    1930: (
        (
            "We should increase commerce. We currently make ",
            ", but our goal is to be making ",
            " within ",
            " day(s).",
        ),
        ("", "0233", "0232", "0236", "050505"),
    ),
    1931: (
        (
            "We need to capture target castles. We have captured castles ",
            " time(s), but our goal is to have captured ",
            " time(s) within ",
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
    "kokudaka_commerce_and_capture_campaign_target_castle_deadline_goal_"
    "current_ui_with_explicit_base1926_1931_to_pk1956_1961_mapping_exact_"
    "base_pk_jp_sc_tc_and_pk_en_meaning_context_jp_authoritative_period_"
    "target_current_token_order_0234_years_0235_months_0236_days_0232_"
    "target_0233_current_korean_seokgo_sangeop_gongnyak_mokpyo_hamrak_"
    "terms_current_korean_morphology_terminal_corpora_and_all_base_pk_"
    "opcode_divergences_recorded_eleven_hidden_literals_excluded_current_"
    "line_counts_and_protected_skeleton_preserved_runtime_fragment_pending_"
    "base_912px_not_applied"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    1150: ("합시다", "그렇군"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    1162: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1150],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records, raw_translations
    if KOKUDAKA_ACTION != PREVIOUS.KOKUDAKA_ACTION:
        raise RuntimeError("segment 948 kokudaka-action continuity drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 948 Base-to-PK mapping drifted")
    if any(
        EXPECTED_BASE_GAPS[record_id] == EXPECTED_PK_JP_GAPS[record_id]
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 948 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 948 pristine/current gap drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {
        "15:1926:1": "\n",
        "15:1926:5": "",
        "15:1927:1": "\n",
        "15:1927:4": "",
        "15:1928:1": "\n",
        "15:1928:4": "",
        "15:1929:1": "\n",
        "15:1929:5": "",
        "15:1930:1": "\n",
        "15:1930:4": "",
        "15:1931:1": "\n",
    }:
        raise RuntimeError("segment 948 hidden literal exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "석고",
        "상업",
        "공략 목표",
        "함락",
        "목표 석고:",
        "목표 상업:",
        "회\n현재:",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 948 required meaning drifted: {required}")
    for forbidden in ("（", "）", "개월 이내", "일 이내", "지금은", "공략대상"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 948 forbidden phrasing retained: {forbidden}"
            )
    if len(translations) != 21:
        raise RuntimeError("segment 948 visible decision count drifted")


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
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 948 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 948 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S948",
                "source_literal_count": 32,
                "decision_count": len(rows),
                "hidden_literals_excluded": 11,
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
