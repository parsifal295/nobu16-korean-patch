#!/usr/bin/env python3
"""Build Base authoring segment 987 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment986 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S987.private.v1.jsonl"
)
SEGMENT = 987
RESOURCE_PREFIX = (
    "우리 가문은 다른 가문에 비해\n",
    "의 수입이 부족한 상태",
)


def resource_advice(place: str) -> tuple[str, str, str]:
    return (
        RESOURCE_PREFIX[0],
        RESOURCE_PREFIX[1],
        (
            "\n자원이 풍부한 다른 가문과 외교하거나\n"
            f"{place}을 갖춘 군을 유능한 무장에게 맡기는 등\n"
            "알맞게 운용하는 편이"
        ),
    )


TRANSLATIONS_BY_RECORD = {
    2350: (
        "우선 가까운",
        "을(를) 설정해 두",
        "\n평정에서 공략 방침을 선택하면\n언제든 변경할 수 있",
    ),
    2351: (
        "당분간은",
        "을(를) 목표로 삼",
        "\n변경하고 싶다면 평정에서 공략 방침을 선택해\n언제든 변경할 수 있",
    ),
    2352: (
        "우선",
        "의",
        "을(를) 목표로 삼아\n일을 추진하는 것이 좋을 듯하옵니다",
    ),
    2353: (
        "이는 주제넘은 말씀을 드",
        "\n공략 방침은 화면 하단의 점프 버튼에서\n언제든 설정할 수 있",
    ),
    2355: resource_advice("농촌"),
    2356: resource_advice("상인 마을"),
    2357: resource_advice("목장"),
    2358: resource_advice("대장간 마을"),
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
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
JP_GAP_DIVERGENCES = {2350, 2351, 2353, 2355, 2356, 2357, 2358}
STATIC_RECORD_IDS: set[int] = set()
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
ARCHIVE_DIGESTS = {
    "base_jp": "BC4A13C3D4882CDD302F66454325E4A0F5A2950FF3A986CF69049E07ABFA4F17",
    "base_current": "99C6A1BAA79354F7676E62D6C987E6D71FA594067914B4ACF8C063690095B340",
    "base_sc": "E6B344A87760317FF3949FE5412235B2AF27E77CB0E44B5B32E6170A9DDD96F3",
    "base_tc": "A2F1DFC90B31ED4251B3680046C6C231B20CF369C012F1DD210121DF1052EA4E",
    "pk_jp": "5157CE8FF8F0D0A90B58CDFEFCA3A8973F2C7765887DE9E55799C232B2634B69",
    "pk_current": "4AC33B0C085462AADA7A62412DDA8074E63E25201BB109146BB4689CE831912C",
    "pk_sc": "E6B344A87760317FF3949FE5412235B2AF27E77CB0E44B5B32E6170A9DDD96F3",
    "pk_tc": "A2F1DFC90B31ED4251B3680046C6C231B20CF369C012F1DD210121DF1052EA4E",
    "pk_en": "A33DD9A381D6D5FAE66DB6A42284119F8986E9595F7C640B0CCB8F7674BEC002",
}
BASIS = (
    "review_queue_base_msggame_B118_B_pristine_base_pc_jp_authoritative_"
    "invasion_target_policy_ui_guidance_and_resource_income_advice_with_"
    "exact_plus31_pk_mapping_aggregate_pc_jp_en_sc_tc_record_digests_"
    "dynamic_force_resource_and_morphology_boundaries_current_line_counts_"
    "preserved_no_korean_build_authority"
)


def assert_semantics(translations: dict[str, str]) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "공략 방침",
        "평정",
        "점프 버튼",
        "우리 가문",
        "다른 가문",
        "농촌",
        "상인 마을",
        "목장",
        "대장간 마을",
        "유능한 무장",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 987 required meaning drifted: {required}")
    for forbidden in ("당가", "타가", "우수한 무장", "鍛", "。"):
        if forbidden in joined:
            raise RuntimeError(f"segment 987 forbidden wording retained: {forbidden}")
    if any(
        TRANSLATIONS_BY_RECORD[record_id][0] is not RESOURCE_PREFIX[0]
        or TRANSLATIONS_BY_RECORD[record_id][1] is not RESOURCE_PREFIX[1]
        for record_id in range(2355, 2359)
    ):
        raise RuntimeError("segment 987 resource-income common frame drifted")
    income_state_variants = {
        f"{RESOURCE_PREFIX[1]}{ending}"
        for ending in ("입니다", "다", "이니라", "이오", "이옵니다")
    }
    if income_state_variants != {
        "의 수입이 부족한 상태입니다",
        "의 수입이 부족한 상태다",
        "의 수입이 부족한 상태이니라",
        "의 수입이 부족한 상태이오",
        "의 수입이 부족한 상태이옵니다",
    }:
        raise RuntimeError("segment 987 resource-income morphology drifted")


def main() -> int:
    prepared, translations, rows = PREVIOUS.build_compact_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        archive_digests=ARCHIVE_DIGESTS,
        jp_gap_divergences=JP_GAP_DIVERGENCES,
        static_record_ids=STATIC_RECORD_IDS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 987 decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S987",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": sorted(
                    JP_GAP_DIVERGENCES
                ),
                "pristine_current_gap_divergence_records": [],
                "lf_count": sum(
                    text.count("\n") for text in translations.values()
                ),
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
