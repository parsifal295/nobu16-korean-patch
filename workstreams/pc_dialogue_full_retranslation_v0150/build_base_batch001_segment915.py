#!/usr/bin/env python3
"""Build Base authoring segment 915 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment914 as COMMON


ENGINE = COMMON.ENGINE
FRAMEWORK = COMMON.FRAMEWORK
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S915.private.v1.jsonl"
)
SEGMENT = 915
CANONICAL_TRANSLATIONS = {
    1563: COMMON.SEIZURE_MARCH_KO,
    1564: COMMON.ARMY_ATTACK_COUNCIL_KO,
    1565: COMMON.UNIT_MARCH_COUNCIL_KO,
    1566: COMMON.INVASION_SORTIE_ORDER_KO,
    1567: COMMON.MARCH_COUNCIL_PREP_KO,
    1568: COMMON.ARMY_SORTIE_COUNCIL_KO,
    1569: COMMON.ENEMY_APPROACH_KO,
    1570: COMMON.ENEMY_APPROACH_KO,
    1571: COMMON.INVASION_INTERCEPT_KO,
    1572: COMMON.UNIT_SORTIE_COUNCIL_KO,
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, canonical in CANONICAL_TRANSLATIONS.items()
    for literal_id, translation in enumerate(canonical)
}
RECORD_ARITIES = {
    record_id: 2 for record_id in range(1563, 1573)
}
EXPECTED_BASE_JP = {
    1563: COMMON.SEIZURE_MARCH_JP,
    1564: COMMON.ARMY_ATTACK_COUNCIL_JP,
    1565: COMMON.UNIT_MARCH_COUNCIL_JP,
    1566: COMMON.INVASION_SORTIE_ORDER_JP,
    1567: COMMON.MARCH_COUNCIL_PREP_JP,
    1568: COMMON.ARMY_SORTIE_COUNCIL_JP,
    1569: COMMON.ENEMY_APPROACH_JP,
    1570: COMMON.ENEMY_APPROACH_JP,
    1571: COMMON.INVASION_INTERCEPT_JP,
    1572: COMMON.UNIT_SORTIE_COUNCIL_JP,
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("026432", "025032", "050505")
        for record_id in range(1563, 1569)
    },
    **{
        record_id: ("029632", "025032", "050505")
        for record_id in range(1569, 1573)
    },
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {
    1563: 1593,
    1564: 1594,
    1565: 1595,
    1566: 1596,
    1567: 1597,
    1568: 1598,
    1569: 1599,
    1570: 1600,
    1571: 1601,
    1572: 1602,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

SHARED_AUXILIARY = {
    ("SC", 1565): (
        ("的部队在向", "\n进军！\n立刻召开军议吧！"),
        ("025032", "026432", "050505"),
    ),
    ("TC", 1565): (
        ("部隊正朝著", "進軍！\n趕緊召開軍議吧！"),
        ("025032", "026432", "050505"),
    ),
    ("SC", 1571): (
        ("的部队\n好像开始入侵了", "了呢。\n若有命令，便迅速前去歼灭。"),
        ("025032", "029632", "050505"),
    ),
    ("TC", 1571): (
        ("的部隊\n好像已開始入侵", "。\n上級若下達命令，必速往殲滅。"),
        ("025032", "029632", "050505"),
    ),
    ("SC", 1572): (
        ("的部队朝着", "出阵了。\n请立即下令召开军事会议。"),
        ("025032", "029632", "050505"),
    ),
    ("TC", 1572): (
        ("的部隊已向", "出陣。\n請緊急召開軍事會議。"),
        ("025032", "029632", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1565: (
        (
            "The ",
            " has marched for ",
            ". We must hurry and hold a war council!",
        ),
        ("", "025032", "026432", "050505"),
    ),
    1571: (
        (
            "The ",
            " have launched their invasion on ",
            ". This would be a good time to ambush them.",
        ),
        ("", "025032", "029632", "050505"),
    ),
    1572: (
        (
            "The ",
            " are marching for ",
            ". We must assemble a war council immediately.",
        ),
        ("", "025032", "029632", "050505"),
    ),
}
AUXILIARY_OVERRIDES = COMMON.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B110_pristine_base_pc_jp_authoritative_"
    "enemy_march_invasion_sortie_and_war_council_alert_speaker_variants_"
    "with_content_and_sequence_verified_explicit_base_to_pk_plus_30_map_"
    "exact_base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_exact_"
    "cross_record_canonical_reuse_castle_and_county_target_token_types_"
    "invasion_sortie_hamyeong_gunui_historical_sortie_order_terminology_"
    "current_layout_and_token_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    explicit_map = {
        1563: 1593,
        1564: 1594,
        1565: 1595,
        1566: 1596,
        1567: 1597,
        1568: 1598,
        1569: 1599,
        1570: 1600,
        1571: 1601,
        1572: 1602,
    }
    if PK_RECORD_MAP != explicit_map:
        raise RuntimeError("segment 915 explicit content-derived PK map drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 915 verified PK offset drifted from +30")

    cross_record_groups = {
        (1563, 1575): COMMON.SEIZURE_MARCH_JP,
        (1564, 1576): COMMON.ARMY_ATTACK_COUNCIL_JP,
        (1565, 1577): COMMON.UNIT_MARCH_COUNCIL_JP,
        (1566, 1578): COMMON.INVASION_SORTIE_ORDER_JP,
        (1567, 1579): COMMON.MARCH_COUNCIL_PREP_JP,
        (1568, 1580): COMMON.ARMY_SORTIE_COUNCIL_JP,
        (1569, 1570, 1573): COMMON.ENEMY_APPROACH_JP,
        (1571, 1559): COMMON.INVASION_INTERCEPT_JP,
        (1572, 1560): COMMON.UNIT_SORTIE_COUNCIL_JP,
    }
    for record_ids, canonical_source in cross_record_groups.items():
        if any(
            COMMON.source_tuple(source_records, record_id) != canonical_source
            for record_id in record_ids
        ):
            raise RuntimeError(
                f"segment 915 exact-source group drifted: {record_ids}"
            )
    for record_id, canonical in CANONICAL_TRANSLATIONS.items():
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(2)
        )
        if actual != canonical:
            raise RuntimeError(
                f"segment 915 Korean canonical reuse drifted: {record_id}"
            )

    joined = "\n".join(translations.values())
    for required in (
        "침공",
        "출진",
        "하명",
        "군의",
        "출진령",
        "진군",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 915 required terminology drifted: {required}")
    for forbidden in ("출진 명령", "군사 회의", "동원령"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 915 forbidden terminology retained: {forbidden}"
            )
    if len(raw_translations) != 20 or len(translations) != 20:
        raise RuntimeError("segment 915 fixed visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return FRAMEWORK.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
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
    if len(rows) != 20 or len(validated) != len(translations):
        raise RuntimeError("segment 915 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S915",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "explicit_base_to_pk_map": PK_RECORD_MAP,
                "verified_base_to_pk_offset": 30,
                "decision_sha256": ENGINE.sha256_bytes(OUTPUT.read_bytes()),
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
