#!/usr/bin/env python3
"""Build Base authoring segment 946 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment945 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S946.private.v1.jsonl"
)
SEGMENT = 946
TRANSLATIONS_BY_RECORD = {
    1913: (
        "지배하는 성을 더 확보",
        "\n",
        "개월 안에 목표:",
        "성\n현재:",
        "성",
    ),
    1914: (
        "지배하는 성을 더 확보",
        "\n",
        "년",
        "개월 안에 목표:",
        "성\n현재:",
        "성",
    ),
    1915: (
        "지배하는 성을 더 확보",
        "\n",
        "일 안에 목표:",
        "성\n현재:",
        "성",
    ),
    1916: (
        "가신을 더 등용",
        "\n",
        "개월 안에 목표:",
        "명\n현재:",
        "명",
    ),
    1917: (
        "가신을 더 등용",
        "\n",
        "년",
        "개월 안에 목표:",
        "명\n현재:",
        "명",
    ),
    1918: (
        "가신을 더 등용",
        "\n",
        "일 안에 목표:",
        "명\n현재:",
        "명",
    ),
    1919: (
        "정책 발령 수준을 제고",
        "\n",
        "개월 안에 목표 합계:",
        "(LV)\n현재 합계:",
        "(LV)",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
    if literal_id != 1
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1913: ("支配する城を増や", "\n", "カ月以内に目指すは", "城\n今は", "城"),
    1914: ("支配する城を増や", "\n", "年", "カ月以内に目指すは", "城\n今は", "城"),
    1915: ("支配する城を増や", "\n", "日以内に目指すは", "城\n今は", "城"),
    1916: ("家臣を増や", "\n", "カ月以内に目指すは", "名\n今は", "名"),
    1917: ("家臣を増や", "\n", "年", "カ月以内に目指すは", "名\n今は", "名"),
    1918: ("家臣を増や", "\n", "日以内に目指すは", "名\n今は", "名"),
    1919: ("政策発令水準を上げ", "\n", "カ月以内に目指すは合計", "（LV）\n今は合計", "（LV）"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1913: ("", "01437E040000", "0235", "0232", "0233", "01431A020000050505"),
    1914: ("", "01437E040000", "0234", "0235", "0232", "0233", "01431A020000050505"),
    1915: ("", "01437E040000", "0236", "0232", "0233", "01431A020000050505"),
    1916: ("", "01437E040000", "0235", "0232", "0233", "01431A020000050505"),
    1917: ("", "01437E040000", "0234", "0235", "0232", "0233", "01431A020000050505"),
    1918: ("", "01437E040000", "0236", "0232", "0233", "01431A020000050505"),
    1919: ("", "01431E040000", "0235", "0232", "0233", "01431A020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1913: ("", "01438A040000", "0235", "0232", "0233", "014326020000050505"),
    1914: ("", "01438A040000", "0234", "0235", "0232", "0233", "014326020000050505"),
    1915: ("", "01438A040000", "0236", "0232", "0233", "014326020000050505"),
    1916: ("", "01438A040000", "0235", "0232", "0233", "014326020000050505"),
    1917: ("", "01438A040000", "0234", "0235", "0232", "0233", "014326020000050505"),
    1918: ("", "01438A040000", "0236", "0232", "0233", "014326020000050505"),
    1919: ("", "01432A040000", "0235", "0232", "0233", "014326020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {
    f"15:{record_id}:1": "\n" for record_id in RECORD_ARITIES
}
SHARED_AUXILIARY = {
    ("SC", 1913): (
        ("增加统治城的数量吧。\n在", "个月以内，\n以", "座城为目标，目前有", "座城。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1914): (
        ("增加统治城的数量吧。\n在", "年", "个月以内，\n以", "座城为目标，目前有", "座城。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1915): (
        ("增加统治城的数量吧。。\n在", "天以内，\n以", "座城为目标，目前有", "座城。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("SC", 1916): (
        ("增加家臣的数量吧。\n目标是在", "个月以内达到", "人。\n目前家中有", "人。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1917): (
        ("增加家臣的数量吧。\n目标是在", "年", "个月以内达到", "人。\n目前家中有", "人。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1918): (
        ("增加家臣的数量吧。\n目标是在", "日以内", "名。\n目前家中有", "名。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("SC", 1919): (
        ("提高政策的颁布标准吧。\n在", "个月以内，\n以", "（LV）为目标，目前是", "（LV）。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1913): (
        ("目標是增加統治城數。\n統治城數需在", "個月內增加至", "座，\n目前擁有", "座。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1914): (
        ("目標是增加統治城數。\n統治城數需在", "年", "個月內增加至", "座，\n目前擁有", "座。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1915): (
        ("目標是增加統治城數。\n統治城數需在", "日內增加至", "座，\n目前擁有", "座。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("TC", 1916): (
        ("目標是增加家臣人數。\n家臣人數需在", "個月內增加至", "名，\n目前共有", "名。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1917): (
        ("目標是增加家臣人數。\n家臣人數需在", "年", "個月內增加至", "名，\n目前共有", "名。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1918): (
        ("目標是增加家臣人數。\n家臣人數需在", "日內增加至", "名，\n目前擁有", "名。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("TC", 1919): (
        ("目標是提升頒布政策的水準。水準需在\n", "個月內合計提升至", "（LV），\n目前合計為", "（LV）。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1913: (
        (
            "WeÖre looking to increase our number of controlled castles. We currently possess ",
            ", but our goal is to have ",
            " within ",
            " month(s).",
        ),
        ("", "0233", "0232", "0235", "050505"),
    ),
    1914: (
        (
            "WeÖre looking to increase our number of controlled castles. We currently possess ",
            ", but our goal is to have ",
            " within ",
            " year(s) and ",
            " month(s).",
        ),
        ("", "0233", "0232", "0234", "0235", "050505"),
    ),
    1915: (
        (
            "WeÖre looking to increase our number of controlled castles. We currently possess ",
            ", but our goal is to have ",
            " within ",
            " day(s).",
        ),
        ("", "0233", "0232", "0236", "050505"),
    ),
    1916: (
        (
            "We need to increase our number of retainers. There are presently ",
            ", but our goal is to have ",
            " within ",
            " month(s).",
        ),
        ("", "0233", "0232", "0235", "050505"),
    ),
    1917: (
        (
            "We need to increase our number of retainers. There are presently ",
            ", but our goal is to have ",
            " within ",
            " year(s) and ",
            " month(s).",
        ),
        ("", "0233", "0232", "0234", "0235", "050505"),
    ),
    1918: (
        (
            "We need to increase our number of retainers. There are presently ",
            ", but our goal is to have ",
            " within ",
            " day(s).",
        ),
        ("", "0233", "0232", "0236", "050505"),
    ),
    1919: (
        (
            "We should increase our issued policy standard. The current level total is ",
            ", but our goal is to achieve a level total of ",
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
    "review_queue_base_msggame_B113_C_pristine_base_pc_jp_authoritative_"
    "controlled_castle_retainer_count_and_policy_issue_level_deadline_goal_"
    "ui_with_explicit_base1913_1919_to_pk1943_1949_mapping_exact_base_pk_"
    "jp_sc_tc_and_actual_pk_en_auxiliary_context_jp_authoritative_token_"
    "order_0234_years_0235_months_0236_days_0232_target_0233_current_en_"
    "reordering_context_only_korean_colon_delimited_numeric_assembly_castle_"
    "seong_retainer_myeong_and_ascii_lv_units_preserved_current_korean_"
    "morphology_terminal_corpora_and_base_pk_opcode_divergences_recorded_"
    "seven_hidden_lfs_excluded_current_line_counts_and_protected_skeleton_"
    "preserved_runtime_fragment_pending"
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
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 946 Base-to-PK mapping drifted")
    if any(
        EXPECTED_BASE_GAPS[record_id] == EXPECTED_PK_JP_GAPS[record_id]
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 946 Base-to-PK gap divergence drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {
        f"15:{record_id}:1": "\n" for record_id in RECORD_ARITIES
    }:
        raise RuntimeError("segment 946 hidden LF exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "지배하는 성",
        "가신",
        "정책 발령 수준",
        "개월 안에 목표:",
        "일 안에 목표:",
        "성\n현재:",
        "명\n현재:",
        "(LV)\n현재 합계:",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 946 required meaning drifted: {required}")
    for forbidden in ("（", "）", "개월 이내에 목표는", "지금은", "늘"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 946 forbidden phrasing retained: {forbidden}"
            )
    if (
        sum("(LV)" in text for text in translations.values()) != 2
        or len(translations) != 30
    ):
        raise RuntimeError("segment 946 unit/count drifted")


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
    if len(rows) != 30 or len(validated) != len(translations):
        raise RuntimeError("segment 946 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 946 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S946",
                "source_literal_count": 37,
                "decision_count": len(rows),
                "hidden_lf_excluded": 7,
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
                "ascii_lv_unit_preserved": True,
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
