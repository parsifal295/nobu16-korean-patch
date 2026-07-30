#!/usr/bin/env python3
"""Build Base authoring segment 988 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment987 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMPACT = PREVIOUS.PREVIOUS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S988.private.v1.jsonl"
)
SEGMENT = 988
RICH_PREFIX = (
    "우리 가문은 그리 풍족하지",
    "\n특히",
    "의 수입은 다른 가문보다 부족",
)
AMPLE_PREFIX = (
    "다행히 우리 가문은",
    "의 수입이\n다른 가문보다 넉넉한 상태",
)


def specific_resource_advice(place: str) -> tuple[str, str, str, str]:
    return (
        RICH_PREFIX[0],
        RICH_PREFIX[1],
        RICH_PREFIX[2],
        (
            "\n자원이 풍부한 다른 가문과 외교하거나\n"
            f"{place}을 갖춘 군을 유능한 무장에게 맡기는 등\n"
            "알맞게 운용하는 편이"
        ),
    )


TRANSLATIONS_BY_RECORD = {
    2359: specific_resource_advice("농촌"),
    2360: specific_resource_advice("상인 마을"),
    2361: specific_resource_advice("목장"),
    2362: specific_resource_advice("대장간 마을"),
    2364: (
        AMPLE_PREFIX[0],
        AMPLE_PREFIX[1],
        "\n전쟁이나 흉작에 대비하려면 아무리 많아도 곤란",
        "만,\n필요에 따라 거래에 쓰는 것도 한 방법일 듯합니다",
    ),
    2365: (
        AMPLE_PREFIX[0],
        AMPLE_PREFIX[1],
        "\n외교나 정책 강화에 이용하는 등\n요긴하게 활용",
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
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
JP_GAP_DIVERGENCES = {2359, 2360, 2361, 2362, 2364, 2365}
STATIC_RECORD_IDS: set[int] = set()
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
ARCHIVE_DIGESTS = {
    "base_jp": "24F0E401630A3E40A7039E6D199DCB8268983239A540B17CB2198898140102C6",
    "base_current": "6FC5F6E62621AD4D78D1DD59BBCF2E8C59E570E403D5601BB3FFDE42856419F0",
    "base_sc": "84A099D911BEB851F0115805BCB211A4A48911E1892C942025134782FB7699EB",
    "base_tc": "36A2C63EB9969636795208CF71C859EBF4C21547BB9108A4BBB7904B265878AA",
    "pk_jp": "3BFCF1E04A4E496B0108C97290487A96CC75D8E5C9F31F0F1ECCCCC609BBF426",
    "pk_current": "287F3B1AE607CD72862E46DA6F759E32E710EF1432B28782996CB46229210D29",
    "pk_sc": "84A099D911BEB851F0115805BCB211A4A48911E1892C942025134782FB7699EB",
    "pk_tc": "36A2C63EB9969636795208CF71C859EBF4C21547BB9108A4BBB7904B265878AA",
    "pk_en": "80C89CEE7CDEE4F2372A002E9D88C0EFA4EE17E815FED6007DFCBB883C9E1613",
}
BASIS = (
    "review_queue_base_msggame_B118_B_pristine_base_pc_jp_authoritative_"
    "comparative_resource_income_trade_diplomacy_county_assignment_and_"
    "policy_investment_advice_with_exact_plus31_pk_mapping_aggregate_pc_"
    "jp_en_sc_tc_record_digests_dynamic_resource_morphology_boundaries_"
    "current_line_counts_preserved_no_korean_build_authority"
)


def assert_semantics(translations: dict[str, str]) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "다른 가문",
        "농촌",
        "상인 마을",
        "목장",
        "대장간 마을",
        "전쟁",
        "흉작",
        "거래",
        "외교",
        "정책 강화",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 988 required meaning drifted: {required}")
    for forbidden in ("당가", "타가", "싸움이나 흉작", "鍛", "。"):
        if forbidden in joined:
            raise RuntimeError(f"segment 988 forbidden wording retained: {forbidden}")
    if any(
        TRANSLATIONS_BY_RECORD[record_id][index] is not RICH_PREFIX[index]
        for record_id in range(2359, 2363)
        for index in range(3)
    ):
        raise RuntimeError("segment 988 comparative-income frame drifted")
    if (
        not RICH_PREFIX[0].endswith("풍족하지")
        or "풍족하다고는 하나" in joined
    ):
        raise RuntimeError("segment 988 comparative-income polarity drifted")
    if any(
        TRANSLATIONS_BY_RECORD[record_id][index] is not AMPLE_PREFIX[index]
        for record_id in (2364, 2365)
        for index in range(2)
    ):
        raise RuntimeError("segment 988 ample-income frame drifted")
    ample_variants = {
        f"{AMPLE_PREFIX[1]}{ending}".splitlines()[-1]
        for ending in ("입니다", "다", "이니라", "이오", "이옵니다")
    }
    if ample_variants != {
        "다른 가문보다 넉넉한 상태입니다",
        "다른 가문보다 넉넉한 상태다",
        "다른 가문보다 넉넉한 상태이니라",
        "다른 가문보다 넉넉한 상태이오",
        "다른 가문보다 넉넉한 상태이옵니다",
    }:
        raise RuntimeError("segment 988 ample-income morphology drifted")
    if (
        f"{TRANSLATIONS_BY_RECORD[2364][2]}하지 않습니다"
        f"{TRANSLATIONS_BY_RECORD[2364][3]}"
    ).splitlines()[-2:] != [
        "전쟁이나 흉작에 대비하려면 아무리 많아도 곤란하지 않습니다만,",
        "필요에 따라 거래에 쓰는 것도 한 방법일 듯합니다",
    ]:
        raise RuntimeError("segment 988 formal trade-advice assembly drifted")


def main() -> int:
    prepared, translations, rows = COMPACT.build_compact_rows(
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
        raise RuntimeError("segment 988 decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S988",
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
