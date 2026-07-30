#!/usr/bin/env python3
"""Build Base authoring segment 950 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment941 as FOUNDATION


ENGINE = FOUNDATION.ENGINE
COMMON = FOUNDATION.COMMON
ANNOTATE_MORPHOLOGY = FOUNDATION.SUPPORT.annotate_morphology_evidence
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S950.private.v1.jsonl"
)
SEGMENT = 950
TRANSLATIONS_BY_RECORD = {
    1937: (
        "임무는 순조롭게 진행되고",
        ". 하지만\n갈 길은 아직 절반이나 남아\n앞으로:",
        "일은 더 걸린다고 예상",
    ),
    1938: (
        "끝이 보이기 시작했지만\n갈 길은 아직 절반쯤 남았습니다\n"
        "남은 기간은:",
        "일 정도로 봅니다",
    ),
    1939: (
        "차분히 마음을 다잡고 작업에 착수하고",
        "\n결과를 정리하",
        ", 보고하기까지",
        "일\n그리 서두르지 말고,",
    ),
    1940: (
        "임무는 순조롭게 진행되고",
        ". 순조롭게 보이는 상태",
        ". 하지만\n갈 길은 아직 절반이라고 들었",
        "\n앞으로:",
        "일은 더 걸린다고 예상",
    ),
    1941: (
        "작업은 아직 시간이 더 걸리겠군\n대략 앞으로:",
        "일은\n필요할 것 같다",
    ),
    1942: (
        "지금 임무를 수행하고 있사오니\n완료까지는\n대략:",
        "일 정도 걸릴 것으로 사료되옵니다",
    ),
    1943: (
        "작업은 아직 중반입니다\n남은 기간은:",
        "일 정도로 예상합니다",
    ),
    1944: (
        "이제 막 작업에 착수했사오니\n완료까지는\n",
        "일 정도 걸릴 것이옵니다",
    ),
    1945: (
        "끝이 보이기 시작했지만\n작업은 아직 절반쯤 남았습니다\n"
        "남은 기간은:",
        "일 정도로 봅니다",
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
    1937: (
        "任は順調に進んで",
        "が\n道程はまだ半ばにあり\nまだ",
        "日はかか",
    ),
    1938: (
        "先が見えてきたとはいえ\n道程はまだ半ば\n残りは",
        "日ほどかと",
    ),
    1939: (
        "腰を据えて着手して",
        "\n結果を",
        "報告するまで",
        "日\nそう慌てず",
    ),
    1940: (
        "任は順調に進んで",
        "よう",
        "が\n道程はまだ半ばと聞",
        "\nまだ",
        "日はかか",
    ),
    1941: (
        "作業はまだかかるぞ\nそうだな、あと",
        "日は\n欲しいところだ",
    ),
    1942: (
        "まさに任にあたっておりますれば\n完了までは\nざっと",
        "日はかかるかと",
    ),
    1943: ("作業はまだ中途\nあと", "日はかかるかと"),
    1944: (
        "ただ今着手しておりますれば\n作業完了まで\n",
        "日はかかりましょう",
    ),
    1945: (
        "先が見えてきたとはいえ\n作業はまだ半ば\n残りは",
        "日ほどかと",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1937: ("", "0143B2000000", "0232", "01435A040000050505"),
    1938: ("", "0232", "050505"),
    1939: (
        "",
        "0143B2000000",
        "01438A040000",
        "0232",
        "014382030000050505",
    ),
    1940: (
        "",
        "0143B2000000",
        "01432C020000",
        "014336010000",
        "0232",
        "01435A040000050505",
    ),
    1941: ("", "0232", "050505"),
    1942: ("", "0232", "050505"),
    1943: ("", "0232", "050505"),
    1944: ("", "0232", "050505"),
    1945: ("", "0232", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1937: ("", "0143B2000000", "0232", "014366040000050505"),
    1938: ("", "0232", "050505"),
    1939: (
        "",
        "0143B2000000",
        "014396040000",
        "0232",
        "01438E030000050505",
    ),
    1940: (
        "",
        "0143B2000000",
        "014338020000",
        "014336010000",
        "0232",
        "014366040000050505",
    ),
    1941: ("", "0232", "050505"),
    1942: ("", "0232", "050505"),
    1943: ("", "0232", "050505"),
    1944: ("", "0232", "050505"),
    1945: ("", "0232", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
EXPECTED_AUXILIARY_DIGESTS = {
    "base_SC": "39B0CE57AD4E6F31AB3031D887AA2F3FE92EC303BC7AA6057D766A4811001B00",
    "base_TC": "B31B90D558B95EEA6B8BA0E8321824C36750EE49342CD14083BB7A7A9E45DB9C",
    "pk_SC": "39B0CE57AD4E6F31AB3031D887AA2F3FE92EC303BC7AA6057D766A4811001B00",
    "pk_TC": "B31B90D558B95EEA6B8BA0E8321824C36750EE49342CD14083BB7A7A9E45DB9C",
    "pk_EN": "FCD8652A88E8EE89402444B18926F5795CE792F8EE58D0B9C86B38B6B5488B80",
}
BASIS = (
    "review_queue_base_msggame_B114_B_pristine_base_pc_jp_authoritative_"
    "mission_and_work_midpoint_progress_remaining_days_reports_with_"
    "explicit_base1937_1945_to_pk1967_1975_mapping_exact_base_pk_jp_sc_"
    "tc_literals_and_pk_en_context_guarded_by_combined_record_sha256_"
    "numeric_remaining_days_token_0232_current_korean_morphology_terminal_"
    "corpora_and_base_pk_opcode_divergences_recorded_smooth_progress_"
    "halfway_and_just_started_stages_kept_distinct_speaker_specific_plain_"
    "polite_rough_and_archaic_registers_current_line_counts_outer_"
    "whitespace_and_runtime_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    178: ("있습니다", "있다", "있사옵니다"),
    310: ("합니다", "다", "하나이다"),
    556: ("입니다", "다", "이오"),
    898: (
        "기다려 주십시오",
        "기다려 다오",
        "기다려 주셨으면 하오",
        "기다려 주시오",
        "기다려 주시게",
    ),
    1114: ("합시다", "하리라"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    310: EXPECTED_BASE_MORPHOLOGY_TERMINALS[310],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    910: EXPECTED_BASE_MORPHOLOGY_TERMINALS[898],
    1126: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records, raw_translations
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 950 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {1937, 1939, 1940}:
        raise RuntimeError("segment 950 Base-to-PK gap divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "순조롭게 진행",
        "절반",
        "마음을 다잡고",
        "중반",
        "막 작업에 착수",
        "남은 기간은:",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 950 required progress meaning drifted: {required}"
            )
    for forbidden in (
        "순조로이",
        "작업은 아직 도중",
        "잔무",
        "요할 것입니다",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 950 forbidden phrasing retained: {forbidden}"
            )
    if len(translations) != 24:
        raise RuntimeError("segment 950 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    auxiliary_overrides = FOUNDATION.make_guarded_auxiliary_overrides(
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
    ANNOTATE_MORPHOLOGY(
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
        raise RuntimeError("segment 950 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 950 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S950",
                "source_literal_count": 24,
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "numeric_token_direction": {"0232": "remaining_days"},
                "progress_stages": [
                    "smooth_midpoint",
                    "halfway",
                    "just_started",
                ],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [1937, 1939, 1940],
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
