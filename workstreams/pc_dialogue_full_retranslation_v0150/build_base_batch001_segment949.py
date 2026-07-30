#!/usr/bin/env python3
"""Build Base authoring segment 949 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment948 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S949.private.v1.jsonl"
)
SEGMENT = 949
CAPTURE_TARGET_ACTION = PREVIOUS.CAPTURE_TARGET_ACTION
BATTLE_VICTORY_ACTION = "합전에서 승리"
TRANSLATIONS_BY_RECORD = {
    1932: (
        CAPTURE_TARGET_ACTION,
        "\n",
        "년",
        "개월 안에 목표:",
        "회\n현재:",
        "회",
    ),
    1933: (
        CAPTURE_TARGET_ACTION,
        "\n",
        "일 안에 목표:",
        "회\n현재:",
        "회",
    ),
    1934: (
        BATTLE_VICTORY_ACTION,
        "\n",
        "개월 안에 목표:",
        "회\n현재:",
        "회",
    ),
    1935: (
        BATTLE_VICTORY_ACTION,
        "\n",
        "년",
        "개월 안에 목표:",
        "회\n현재:",
        "회",
    ),
    1936: (
        BATTLE_VICTORY_ACTION,
        "\n",
        "일 안에 목표:",
        "회\n현재:",
        "회",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    f"15:{record_id}:1": "\n" for record_id in TRANSLATIONS_BY_RECORD
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
    1932: ("攻略目標とした城を落と", "\n", "年", "カ月以内に目指すは", "回\n今は", "回"),
    1933: ("攻略目標とした城を落と", "\n", "日以内に目指すは", "回\n今は", "回"),
    1934: ("合戦にて勝利を収め", "\n", "カ月以内に目指すは", "回\n今は", "回"),
    1935: ("合戦にて勝利を収め", "\n", "年", "カ月以内に目指すは", "回\n今は", "回"),
    1936: ("合戦にて勝利を収め", "\n", "日以内に目指すは", "回\n今は", "回"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1932: ("", "01437E040000", "0234", "0235", "0232", "0233", "01431A020000050505"),
    1933: ("", "01437E040000", "0236", "0232", "0233", "01431A020000050505"),
    1934: ("", "01431E040000", "0235", "0232", "0233", "01431A020000050505"),
    1935: ("", "01431E040000", "0234", "0235", "0232", "0233", "01431A020000050505"),
    1936: ("", "01431E040000", "0236", "0232", "0233", "01431A020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1932: ("", "01438A040000", "0234", "0235", "0232", "0233", "014326020000050505"),
    1933: ("", "01438A040000", "0236", "0232", "0233", "014326020000050505"),
    1934: ("", "01432A040000", "0235", "0232", "0233", "014326020000050505"),
    1935: ("", "01432A040000", "0234", "0235", "0232", "0233", "014326020000050505"),
    1936: ("", "01432A040000", "0236", "0232", "0233", "014326020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
SHARED_AUXILIARY = {
    ("SC", 1932): (
        ("攻陷攻略目标的城吧。\n在", "年", "个月以内，\n以", "次为目标，目前是", "次。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1933): (
        ("攻陷攻略目标的城吧。\n在", "天以内，\n以", "次为目标，目前是", "次。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("SC", 1934): (
        ("在会战中收获胜利吧。\n在", "个月以内，\n以", "次为目标，目前是", "次。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1935): (
        ("在会战中收获胜利吧。\n在", "年", "个月以内，\n以", "次为目标，目前是", "次。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("SC", 1936): (
        ("在会战中收获胜利吧。\n在", "天以内，\n以", "次为目标，目前是", "次。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("TC", 1932): (
        ("目標是攻陷作為攻略目標的城。\n攻陷次數需在", "年", "個月內達到", "次，\n目前為", "次。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1933): (
        ("目標是攻陷作為攻略目標的城。\n攻陷次數需在", "日內達到", "次，\n目前為", "次。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
    ("TC", 1934): (
        ("目標是在會戰中取勝。\n勝利次數需在", "個月內達到", "次，\n目前為", "次。"),
        ("", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1935): (
        ("目標是在會戰中取勝。\n勝利次數需在", "年", "個月內達到", "次，\n目前為", "次。"),
        ("", "0234", "0235", "0232", "0233", "050505"),
    ),
    ("TC", 1936): (
        ("目標是在會戰中取勝。\n勝利次數需在", "日內達到", "次，\n目前為", "次。"),
        ("", "0236", "0232", "0233", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1932: (
        (
            "We need to capture target castles. We have captured castles ",
            " time(s), but our goal is to have captured ",
            " time(s) within ",
            " year(s) and ",
            " month(s).",
        ),
        ("", "0233", "0232", "0234", "0235", "050505"),
    ),
    1933: (
        (
            "We need to capture target castles. We have captured castles ",
            " time(s), but our goal is to have captured ",
            " time(s) within ",
            " day(s).",
        ),
        ("", "0233", "0232", "0236", "050505"),
    ),
    1934: (
        (
            "We must achieve more victories in battle. WeÖve currently won ",
            " time(s), but our goal is to win ",
            " time(s) within ",
            " month(s).",
        ),
        ("", "0233", "0232", "0235", "050505"),
    ),
    1935: (
        (
            "We must achieve more victories in battle. WeÖve currently won ",
            " time(s), but our goal is to win ",
            " time(s) within ",
            " year(s) and ",
            " month(s).",
        ),
        ("", "0233", "0232", "0234", "0235", "050505"),
    ),
    1936: (
        (
            "We must achieve more victories in battle. WeÖve currently won ",
            " time(s), but our goal is to win ",
            " time(s) within ",
            " day(s).",
        ),
        ("", "0233", "0232", "0236", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B114_A_pristine_base_pc_jp_authoritative_"
    "capture_campaign_target_castle_and_battle_victory_deadline_goal_"
    "current_ui_with_explicit_base1932_1936_to_pk1962_1966_mapping_exact_"
    "base_pk_jp_sc_tc_and_pk_en_meaning_context_jp_authoritative_period_"
    "target_current_token_order_0234_years_0235_months_0236_days_0232_"
    "target_0233_current_korean_gongnyak_mokpyo_hamrak_hapjeon_terms_"
    "current_korean_morphology_terminal_corpora_and_all_base_pk_opcode_"
    "divergences_recorded_five_hidden_lfs_excluded_current_line_counts_"
    "and_protected_skeleton_preserved_runtime_fragment_pending_base_"
    "912px_not_applied"
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
    if CAPTURE_TARGET_ACTION != PREVIOUS.CAPTURE_TARGET_ACTION:
        raise RuntimeError("segment 949 capture-action continuity drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 949 Base-to-PK mapping drifted")
    if any(
        EXPECTED_BASE_GAPS[record_id] == EXPECTED_PK_JP_GAPS[record_id]
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 949 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 949 pristine/current gap drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {
        f"15:{record_id}:1": "\n" for record_id in RECORD_ARITIES
    }:
        raise RuntimeError("segment 949 hidden LF exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "공략 목표",
        "함락",
        "합전",
        "승리",
        "개월 안에 목표:",
        "일 안에 목표:",
        "회\n현재:",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 949 required meaning drifted: {required}")
    for forbidden in ("（", "）", "개월 이내", "일 이내", "지금은", "회전"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 949 forbidden phrasing retained: {forbidden}"
            )
    if len(translations) != 22:
        raise RuntimeError("segment 949 visible decision count drifted")


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
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 949 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 949 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S949",
                "source_literal_count": 27,
                "decision_count": len(rows),
                "hidden_literals_excluded": 5,
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
