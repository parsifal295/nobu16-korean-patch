#!/usr/bin/env python3
"""Build Base authoring segment 945 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment944 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S945.private.v1.jsonl"
)
SEGMENT = 945
POLITE_COMPLETION_TRANSLATION = (
    "오래 기다리셨습니다\n남은",
    "일 정도면\n작업이 완료될 전망입니다",
)
TRANSLATIONS_BY_RECORD = {
    1904: POLITE_COMPLETION_TRANSLATION,
    1905: (
        "후우… 작업은\n앞으로:",
        "일이면 끝날 것이다",
    ),
    1906: (
        "남은 일은 얼마 되지 않으니\n완료까지\n앞으로:",
        "일 정도 걸릴 것입니다",
    ),
    1907: POLITE_COMPLETION_TRANSLATION,
    1908: (
        "이런이런…\n앞으로:",
        "일이면\n작업을 마칠 수 있으리라",
    ),
    1909: (
        "조금만 더 기다려 주십시오\n작업 완료까지\n남은",
        "일 정도입니다",
    ),
    1910: (
        "성과를 낼 자신이 있다\n앞으로:",
        "일이면\n작업을 마칠 수 있으리라",
    ),
    1911: (
        "오래 기다리게 해 송구합니다\n작업은\n앞으로:",
        "일 정도면 마칠 수 있을 듯합니다",
    ),
    1912: (
        "작업은 막바지에 접어들어\n앞으로:",
        "일이면\n완료할 수 있을 것이오",
    ),
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
    1904: ("お待たせしました\n残り", "日ほどで\n作業は完了する見込みです"),
    1905: ("ふう…作業は\nあと", "日もあれば終わるだろう"),
    1906: ("残務はわずか\n完了には\nあと", "日程度を要すでしょう"),
    1907: ("お待たせしました\n残り", "日ほどで\n作業は完了する見込みです"),
    1908: ("やれやれ…\nあと", "日もあれば\n作業を終えられよう"),
    1909: ("あと少しだけ、お待ちください\n作業の完了までは\n残り", "日ほどです"),
    1910: ("手応え十分だ\nあと", "日もあれば\n作業は終えられよう"),
    1911: ("お待たせしております\n作業につきましては\nあと", "日ほどで終えられるかと"),
    1912: ("作業は終盤にさしかかり\nあと", "日もあれば\n完了できましょう"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
DAY_TOKEN_GAPS = ("", "0232", "050505")
EXPECTED_BASE_GAPS = {
    record_id: DAY_TOKEN_GAPS for record_id in RECORD_ARITIES
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:1905:0", "15:1908:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1904): (
        ("让您久等了。\n预测大约", "天后，\n工作就会完成。"),
        DAY_TOKEN_GAPS,
    ),
    ("SC", 1905): (
        ("呼……工作\n再过", "天就会结束了吧。"),
        DAY_TOKEN_GAPS,
    ),
    ("SC", 1909): (
        ("请再稍等些时日。\n距离工作结束，\n还有", "天左右。"),
        DAY_TOKEN_GAPS,
    ),
    ("TC", 1904): (
        ("唔嗯……\n預計再", "天就可完成工作吧。"),
        DAY_TOKEN_GAPS,
    ),
    ("TC", 1905): (
        ("唔嗯……\n預計再", "天就可完成工作吧。"),
        DAY_TOKEN_GAPS,
    ),
    ("TC", 1909): (
        ("請再稍等一下。\n再", "天左右便可完成工作。"),
        DAY_TOKEN_GAPS,
    ),
}
AUXILIARY_OVERRIDES = PREVIOUS.SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    {},
)
BASIS = (
    "review_queue_base_msggame_B113_C_pristine_base_pc_jp_authoritative_"
    "near_completion_speaker_report_variants_with_explicit_base1904_1912_"
    "to_pk1934_1942_mapping_exact_base_pk_jp_and_actual_sc_tc_auxiliary_"
    "context_blank_pk_en_numeric_remaining_days_token_0232_after_jp_"
    "authoritative_literal_order_speaker_specific_polite_weary_confident_"
    "and_formal_registers_1904_1907_exact_tuple_object_reuse_tegotae_"
    "rendered_as_confidence_in_results_project_ellipsis_pair_current_line_"
    "counts_and_protected_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if (
        TRANSLATIONS_BY_RECORD[1904] is not POLITE_COMPLETION_TRANSLATION
        or TRANSLATIONS_BY_RECORD[1907] is not POLITE_COMPLETION_TRANSLATION
    ):
        raise RuntimeError("segment 945 Base1904/1907 canonical tuple split")
    if EXPECTED_BASE_JP[1904] != EXPECTED_BASE_JP[1907]:
        raise RuntimeError("segment 945 Base1904/1907 source reuse drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 945 Base-to-PK mapping drifted")
    if (
        set(EXPECTED_BASE_GAPS.values()) != {DAY_TOKEN_GAPS}
        or EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS
        or EXPECTED_PK_JP_GAPS != EXPECTED_BASE_GAPS
    ):
        raise RuntimeError("segment 945 day-token skeleton drifted")
    joined = "\n".join(translations.values())
    for required in (
        "오래 기다리셨습니다",
        "후우",
        "이런이런",
        "기다려 주십시오",
        "성과를 낼 자신",
        "송구합니다",
        "막바지",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 945 required meaning drifted: {required}")
    for forbidden in ("잔무", "반응은 충분", "기다리시게 하여", "요할 것입니다"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 945 forbidden phrasing retained: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 945 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(translations) != 18:
        raise RuntimeError("segment 945 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows_with_current_gaps(
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


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 18 or len(validated) != len(translations):
        raise RuntimeError("segment 945 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 945 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S945",
                "source_literal_count": 18,
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "canonical_base1904_1907_reuse": True,
                "numeric_token_direction": {"0232": "remaining_days"},
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [],
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
