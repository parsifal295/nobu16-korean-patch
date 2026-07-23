#!/usr/bin/env python3
"""Build Base authoring segment 944 decisions for the v0.15.0 retranslation."""

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
    / "base_msggame_B001_S944.private.v1.jsonl"
)
SEGMENT = 944
TRANSLATIONS_BY_RECORD = {
    1897: (
        "남은 일은 얼마 되지 않으니\n결과를 정리하",
        "보고하기까지\n앞으로:",
        "일 정도 걸릴 것",
    ),
    1898: (
        "조금만 더",
        "\n결과가 나오기까지\n남은",
        "일 정도",
    ),
    1899: (
        "앞으로:",
        "일이면\n결과를 정리하",
        "보고할 수 있을",
    ),
    1900: (
        "남은 일이 얼마 없다고 전해 들었다고 보고",
        "\n",
        "일이면\n결과가 나올",
    ),
    1901: (
        "성과는 훌륭해!\n작업 완료까지\n남은",
        "일 정도인가",
    ),
    1902: (
        "앞으로:",
        "일이면\n진행해 온 작업을\n마칠 수 있을 듯하다",
    ),
    1903: (
        "임무는 고비를 넘겼다\n앞으로:",
        "일이면\n작업이 끝날 것이다",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
    if not (record_id == 1900 and literal_id == 1)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1897: ("残務はわずか\n結果を", "報告するには\nあと", "日程度を要す"),
    1898: ("あと少し", "\n結果が出るまで\n残り", "日ほど"),
    1899: ("あと", "日もあれば\n結果を", "報告でき"),
    1900: ("残務はわずかと聞", "\n", "日もあれば\n結果がで"),
    1901: ("成果は上々！\n作業完了まで\n残り", "日ってところか"),
    1902: ("あと", "日もあれば\n進めてきた作業は\n完了できそうだ"),
    1903: ("任務は峠は越えたぞ\nあと", "日もあれば\n作業は終わるだろう"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1897: ("", "01438A040000", "0232", "014356020000050505"),
    1898: ("", "014382030000", "0232", "01432C020000050505"),
    1899: ("", "0232", "01438A040000", "01431E040000050505"),
    1900: ("", "014336010000", "0232", "01431E040000050505"),
    1901: ("", "0232", "050505"),
    1902: ("", "0232", "050505"),
    1903: ("", "0232", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1897: ("", "014396040000", "0232", "014362020000050505"),
    1898: ("", "01438E030000", "0232", "014338020000050505"),
    1899: ("", "0232", "014396040000", "01432A040000050505"),
    1900: ("", "014336010000", "0232", "01432A040000050505"),
    1901: ("", "0232", "050505"),
    1902: ("", "0232", "050505"),
    1903: ("", "0232", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1900:1": "\n"}
SHARED_AUXILIARY = {
    ("SC", 1897): (
        ("些许整理善后，\n尚需", "日左右，\n方能报告结果。"),
        ("", "0232", "050505"),
    ),
    ("SC", 1898): (
        ("请稍待，\n还需", "日左右，\n才会有结果。"),
        ("", "0232", "050505"),
    ),
    ("SC", 1899): (("日后，\n方能报告结果吧。",), ("0232", "050505")),
    ("SC", 1900): (
        ("听闻残留工作所剩无几，\n再有", "天的话，\n便会有结果了。"),
        ("", "0232", "050505"),
    ),
    ("SC", 1903): (
        ("任务已经度过难关了。\n再过上", "天，\n工作就会结束了吧。"),
        ("", "0232", "050505"),
    ),
    ("TC", 1897): (
        ("些許整理善後，\n尚需", "日左右，\n方能報告結果。"),
        ("", "0232", "050505"),
    ),
    ("TC", 1898): (
        ("請稍待，\n還需", "日左右，\n才會有結果。"),
        ("", "0232", "050505"),
    ),
    ("TC", 1899): (("日後，\n方能報告結果吧。",), ("0232", "050505")),
    ("TC", 1900): (
        ("聽聞殘留工作所剩無幾，\n再有", "天的話，\n便會有結果了。"),
        ("", "0232", "050505"),
    ),
    ("TC", 1903): (
        ("任務已順利達成。\n再", "天就能完成工作。"),
        ("", "0232", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1897: (
        (
            "There is little left to be done. I require only about ",
            " day(s) before I am ready to report the results.",
        ),
        ("", "0232", "050505"),
    ),
    1898: (
        (
            "Please wait a bit longer. You will see the results in about ",
            " day(s).",
        ),
        ("", "0232", "050505"),
    ),
    1899: (
        ("I will be able to report the results in ", " day(s)."),
        ("", "0232", "050505"),
    ),
    1900: (
        (
            "I hear the work is nearing completion. You should be able to observe the results in ",
            " day(s).",
        ),
        ("", "0232", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B113_C_pristine_base_pc_jp_authoritative_"
    "remaining_work_result_report_and_near_completion_speaker_reports_with_"
    "explicit_base1897_1903_to_pk1927_1933_mapping_exact_base_pk_jp_sc_"
    "tc_and_actual_pk_en_auxiliary_context_numeric_days_token_0232_after_"
    "jp_authoritative_literal_order_current_korean_morphology_terminal_"
    "corpora_and_base_pk_opcode_divergences_recorded_1900_hidden_lf_"
    "excluded_natural_seonggwa_gobi_completion_wording_current_line_counts_"
    "and_protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    310: ("합니다", "다", "하나이다"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    898: (
        "기다려 주십시오",
        "기다려 다오",
        "기다려 주셨으면 하오",
        "기다려 주시오",
        "기다려 주시게",
    ),
    1054: ("합시다", "듯"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    310: EXPECTED_BASE_MORPHOLOGY_TERMINALS[310],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    910: EXPECTED_BASE_MORPHOLOGY_TERMINALS[898],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records, raw_translations
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 944 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {1897, 1898, 1899, 1900}:
        raise RuntimeError("segment 944 Base-to-PK gap divergence drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:1900:1": "\n"}:
        raise RuntimeError("segment 944 hidden LF exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "남은 일",
        "결과",
        "앞으로:",
        "성과는 훌륭해",
        "고비를 넘겼다",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 944 required meaning drifted: {required}")
    for forbidden in ("잔무", "상등", "요함", "진행해 온 작업을\n완료"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 944 forbidden phrasing retained: {forbidden}"
            )
    if len(translations) != 17:
        raise RuntimeError("segment 944 visible decision count drifted")


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
    if len(rows) != 17 or len(validated) != len(translations):
        raise RuntimeError("segment 944 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 944 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S944",
                "source_literal_count": 18,
                "decision_count": len(rows),
                "hidden_lf_excluded": 1,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "numeric_token_direction": {"0232": "remaining_days"},
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1897,
                    1898,
                    1899,
                    1900,
                ],
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
