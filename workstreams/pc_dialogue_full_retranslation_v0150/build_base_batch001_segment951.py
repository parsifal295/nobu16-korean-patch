#!/usr/bin/env python3
"""Build Base authoring segment 951 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment950 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S951.private.v1.jsonl"
)
SEGMENT = 951
TRANSLATIONS_BY_RECORD = {
    1946: (
        "제 짐작으로는 작업 완료까지\n대략:",
        "일 정도 걸리겠사오니\n지금 잠시 기다려 주시옵소서",
    ),
    1947: (
        "조급함은 금물이옵니다\n작업 완료까지는\n대략:",
        "일 정도 걸릴 전망입니다",
    ),
    1948: (
        "차분히 마음을 다잡고 작업에 착수했사옵니다\n작업 완료까지:",
        "일\n그리 서두르지 말고 기다려 주시옵소서",
    ),
    1949: (
        "임무는 순조롭게 진행되고 있으나\n작업은 아직 절반쯤 남았으므로\n"
        "앞으로:",
        "일 정도 걸릴 것이옵니다",
    ),
    1950: (
        "성과를 서두르면 일을 그르치는 법이옵니다\n작업 완료까지는\n",
        "일 정도 걸릴 전망이옵니다",
    ),
    1951: (
        "작업에 힘쓰고 있습니다\n앞으로:",
        "일 정도 더 걸릴 듯하니\n조금만 더 기다려 주십시오",
    ),
    1952: (
        "작업에 착수했습니다\n완료까지 앞으로:",
        "일 정도 걸릴 듯하니\n잠시 기다려 주십시오",
    ),
    1953: (
        "아직 시작한 지 얼마 되지 않았으니\n잠시 기다려 주시기를 바랍니다\n"
        "대략:",
        "일 정도 걸린다고 예상",
    ),
    1954: (
        "이 임무는\n반드시 완수",
        "\n",
        "일 정도는 기다려 주시옵소서",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1954:1": "\n"}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1946: (
        "見立てでは作業完了まで\nおよそ",
        "日はかかりまする\n今しばしお待ちあれ",
    ),
    1947: (
        "焦りは禁物にございます\n作業完了まで\nおよそ",
        "日は要する見込みです",
    ),
    1948: (
        "腰を据えて着手しておりまする\n作業完了まで",
        "日\nそう慌てずにお待ちくだされ",
    ),
    1949: (
        "任は順調に進んでおりますが\n作業はまだ半ばにあり\nまだ",
        "日はかかりましょう",
    ),
    1950: (
        "成果を急いでは仕損じまする\n作業の完了までは\n",
        "日はかかる見込みにて",
    ),
    1951: (
        "作業に励んでいます\nまだ",
        "日ほどかかりそうなので\n今しばしお待ちください",
    ),
    1952: (
        "作業に着手しています\n完了まで、あと",
        "日はかかるかと\nしばしお待ちください",
    ),
    1953: (
        "まだ始めたばかりゆえ\n今しばしお待ちを\nおよそ",
        "日ほどはかか",
    ),
    1954: (
        "この任\n必ずや成し遂げ",
        "\n",
        "日ほどはお待ちあれ",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
DAY_TOKEN_GAPS = ("", "0232", "050505")
EXPECTED_BASE_GAPS = {
    1946: DAY_TOKEN_GAPS,
    1947: DAY_TOKEN_GAPS,
    1948: DAY_TOKEN_GAPS,
    1949: DAY_TOKEN_GAPS,
    1950: DAY_TOKEN_GAPS,
    1951: DAY_TOKEN_GAPS,
    1952: DAY_TOKEN_GAPS,
    1953: ("", "0232", "01435A040000050505"),
    1954: ("", "01431E040000", "0232", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1946: DAY_TOKEN_GAPS,
    1947: DAY_TOKEN_GAPS,
    1948: DAY_TOKEN_GAPS,
    1949: DAY_TOKEN_GAPS,
    1950: DAY_TOKEN_GAPS,
    1951: DAY_TOKEN_GAPS,
    1952: DAY_TOKEN_GAPS,
    1953: ("", "0232", "014366040000050505"),
    1954: ("", "01432A040000", "0232", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXPECTED_AUXILIARY_DIGESTS = {
    "base_SC": "4FF2A40A43EC1FB1313B927A4E352D95843C44FD8A32BCD560DD59089A634332",
    "base_TC": "B65DE8329C07BB4BB40D4F9BAA5CCB1AA14C954A31D26A29A0CA4AB90F506459",
    "pk_SC": "4FF2A40A43EC1FB1313B927A4E352D95843C44FD8A32BCD560DD59089A634332",
    "pk_TC": "B65DE8329C07BB4BB40D4F9BAA5CCB1AA14C954A31D26A29A0CA4AB90F506459",
    "pk_EN": "21438B81512B182CB9024898374B4A10F407F14DD0EB37C7739D84B1A24CB81C",
}
BASIS = (
    "review_queue_base_msggame_B114_B_pristine_base_pc_jp_authoritative_"
    "work_progress_and_completion_estimate_reports_with_explicit_base_"
    "1946_1954_to_pk1976_1984_mapping_exact_base_pk_jp_sc_tc_literals_"
    "and_pk_en_context_guarded_by_combined_record_sha256_numeric_remaining_"
    "days_token_0232_current_korean_morphology_terminal_corpora_and_base_"
    "pk_opcode_divergences_recorded_1954_hidden_lf_excluded_midpoint_and_"
    "just_started_stages_kept_distinct_speaker_specific_formal_polite_"
    "archaic_and_plain_registers_current_line_counts_outer_whitespace_and_"
    "runtime_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    1054: ("합시다", "듯"),
    1114: ("합시다", "하리라"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1126: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records, raw_translations
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 951 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {1953, 1954}:
        raise RuntimeError("segment 951 Base-to-PK gap divergence drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:1954:1": "\n"}:
        raise RuntimeError("segment 951 hidden LF exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "주시옵소서",
        "절반쯤",
        "일을 그르치는",
        "작업에 힘쓰고",
        "시작한 지 얼마 되지",
        "반드시 완수",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 951 required register/progress drifted: {required}"
            )
    for forbidden in (
        "성과를 급히",
        "도중",
        "바로 그 임무",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 951 forbidden phrasing retained: {forbidden}"
            )
    if len(translations) != 18:
        raise RuntimeError("segment 951 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    auxiliary_overrides = PREVIOUS.FOUNDATION.make_guarded_auxiliary_overrides(
        tuple(RECORD_ARITIES),
        PK_RECORD_MAP,
        EXPECTED_AUXILIARY_DIGESTS,
    )
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
        auxiliary_overrides=auxiliary_overrides,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    PREVIOUS.ANNOTATE_MORPHOLOGY(
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
        raise RuntimeError("segment 951 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 951 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S951",
                "source_literal_count": 19,
                "decision_count": len(rows),
                "hidden_lf_excluded": 1,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "numeric_token_direction": {"0232": "remaining_days"},
                "progress_stages": ["midpoint", "just_started"],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [1953, 1954],
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
