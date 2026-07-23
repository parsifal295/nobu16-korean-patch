#!/usr/bin/env python3
"""Build Base authoring segment 952 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment951 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S952.private.v1.jsonl"
)
SEGMENT = 952
TRANSLATIONS_BY_RECORD = {
    1955: (
        "결과가 나오기까지\n대략:",
        "일 정도는 더 걸린다고 예상",
        ". 그러니\n잠시,",
    ),
    1956: (
        "방금 작업에 착수했다고 들었",
        "\n앞으로:",
        "일 정도 걸린다고 예상",
    ),
    1957: (
        "방금 작업에 착수한 참이다\n앞으로:",
        "일 정도 걸릴 것이다",
    ),
    1958: (
        "작업을 이제 막 시작했으니\n잠시 기다려 다오\n적어도:",
        "일 정도는 걸릴 것이다",
    ),
    1959: (
        "부임한 지 얼마 되지 않아\n작업 완료에는 시간이 걸릴 듯합니다\n"
        "대략:",
        "일 정도 기다려 주십시오",
    ),
    1960: (
        "임무는 이제 막 시작하려는 참…\n작업을 마치려면\n대략:",
        "일 정도 걸릴 것으로 봅니다",
    ),
    1961: (
        "이 임무는\n반드시 완수하겠습니다\n",
        "일 정도 기다려 주시옵소서",
    ),
    1962: (
        "이 임무는\n그리 빨리 끝나지는 않을 것이옵니다\n",
        "일 안에 마칠 예정이옵니다",
    ),
    1963: (
        "작업에 착수했습니다\n대략:",
        "일 정도 걸릴 터이니\n잠시 기다려 주십시오",
    ),
    1964: (
        "부임한 지 얼마 되지 않았사오니\n작업은 아직 시간이 걸리옵니다\n",
        "일 정도는 느긋하게 기다려 주시옵소서",
    ),
    1965: (
        "작업 완료까지는\n",
        "일 정도로 예상하고 있습니다\n느긋하게 기다려 주십시오",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1955: (
        "結果が出るまで\nおよそ",
        "日ほどはかか",
        "ゆえ\nしばし",
    ),
    1956: ("今しがた着手したばかりと聞", "\nあと", "日ほどはかか"),
    1957: (
        "今しがた作業に着手したばかりだ\nあと",
        "日はかかるだろう",
    ),
    1958: (
        "作業は始めたばかりゆえ\n今しばしお待ちを\n少なくとも",
        "日ほどはかかろう",
    ),
    1959: (
        "着任したばかりのため\n作業は完了に時を要すかと\nおよそ",
        "日はお待ちあれ",
    ),
    1960: (
        "任を進めるはまだこれから…\n作業を終えるには\n日数にして",
        "日はかかるかと",
    ),
    1961: (
        "この任\n必ずや成し遂げましょう\n",
        "日ほどはお待ちあれ",
    ),
    1962: (
        "この任\nそうすぐには完了しますまい\n",
        "日で終える運びにて",
    ),
    1963: (
        "作業に着手しました\nおよそ",
        "日ほどはかかりますゆえ\nしばしお待ちください",
    ),
    1964: (
        "着任したばかりにございますれば\n作業はまだかかりまする\n",
        "日ほどは腰を据えてお待ちあれ",
    ),
    1965: (
        "作業の完了には\n",
        "日ほどを見ております\n気を長くお待ちください",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
DAY_TOKEN_GAPS = ("", "0232", "050505")
EXPECTED_BASE_GAPS = {
    1955: ("", "0232", "014336040000", "014382030000050505"),
    1956: ("", "014336010000", "0232", "01435A040000050505"),
    1957: DAY_TOKEN_GAPS,
    1958: DAY_TOKEN_GAPS,
    1959: DAY_TOKEN_GAPS,
    1960: DAY_TOKEN_GAPS,
    1961: DAY_TOKEN_GAPS,
    1962: DAY_TOKEN_GAPS,
    1963: DAY_TOKEN_GAPS,
    1964: DAY_TOKEN_GAPS,
    1965: DAY_TOKEN_GAPS,
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1955: ("", "0232", "014342040000", "01438E030000050505"),
    1956: ("", "014336010000", "0232", "014366040000050505"),
    1957: DAY_TOKEN_GAPS,
    1958: DAY_TOKEN_GAPS,
    1959: DAY_TOKEN_GAPS,
    1960: DAY_TOKEN_GAPS,
    1961: DAY_TOKEN_GAPS,
    1962: DAY_TOKEN_GAPS,
    1963: DAY_TOKEN_GAPS,
    1964: DAY_TOKEN_GAPS,
    1965: DAY_TOKEN_GAPS,
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:1960:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
EXPECTED_AUXILIARY_DIGESTS = {
    "base_SC": "296184F4CE7419B618C36790D85F21126BEF7438441A91677B2F39EEC4ECE185",
    "base_TC": "C2293519D9F2621064FE82830099403CED5B6BD567A23E18C2B8A8C2E726EDF8",
    "pk_SC": "296184F4CE7419B618C36790D85F21126BEF7438441A91677B2F39EEC4ECE185",
    "pk_TC": "C2293519D9F2621064FE82830099403CED5B6BD567A23E18C2B8A8C2E726EDF8",
    "pk_EN": "A67E7861F4B3454234FA9CD1481E9339D71FBB662400D58A0917931597371A2C",
}
BASIS = (
    "review_queue_base_msggame_B114_B_pristine_base_pc_jp_authoritative_"
    "just_started_assignment_and_work_completion_estimate_reports_with_"
    "explicit_base1955_1965_to_pk1985_1995_mapping_exact_base_pk_jp_sc_"
    "tc_literals_and_pk_en_context_guarded_by_combined_record_sha256_"
    "numeric_remaining_days_token_0232_current_korean_morphology_terminal_"
    "corpora_and_base_pk_opcode_divergences_recorded_all_records_kept_in_"
    "just_started_or_early_work_stage_speaker_specific_plain_polite_rough_"
    "formal_and_archaic_registers_project_ellipsis_pair_current_line_"
    "counts_outer_whitespace_and_runtime_skeleton_preserved_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    310: ("합니다", "다", "하나이다"),
    898: (
        "기다려 주십시오",
        "기다려 다오",
        "기다려 주셨으면 하오",
        "기다려 주시오",
        "기다려 주시게",
    ),
    1078: ("합니다", "다"),
    1114: ("합시다", "하리라"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    310: EXPECTED_BASE_MORPHOLOGY_TERMINALS[310],
    910: EXPECTED_BASE_MORPHOLOGY_TERMINALS[898],
    1090: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1078],
    1126: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 952 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {1955, 1956}:
        raise RuntimeError("segment 952 Base-to-PK gap divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "결과가 나오기까지",
        "방금 작업에 착수",
        "이제 막 시작",
        "부임한 지 얼마 되지",
        "이제 막 시작하려는 참",
        "반드시 완수",
        "주시옵소서",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 952 required early-stage/register drifted: {required}"
            )
    for forbidden in ("날수로", "방금 막", "바로 그 임무", "부임한지"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 952 forbidden phrasing retained: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 952 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(translations) != 24:
        raise RuntimeError("segment 952 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    auxiliary_overrides = (
        PREVIOUS.PREVIOUS.FOUNDATION.make_guarded_auxiliary_overrides(
            tuple(RECORD_ARITIES),
            PK_RECORD_MAP,
            EXPECTED_AUXILIARY_DIGESTS,
        )
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
    PREVIOUS.PREVIOUS.ANNOTATE_MORPHOLOGY(
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
        raise RuntimeError("segment 952 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 952 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S952",
                "source_literal_count": 24,
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "numeric_token_direction": {"0232": "remaining_days"},
                "progress_stages": ["just_started", "early_work"],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [1955, 1956],
                "contextual_ellipsis_normalized_to_project_pair": 1,
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
