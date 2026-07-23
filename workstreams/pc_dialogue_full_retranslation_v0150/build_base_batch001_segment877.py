#!/usr/bin/env python3
"""Build Base authoring segment 877 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment876 as PREVIOUS


COMMON = PREVIOUS.COMMON
ENGINE = COMMON.ENGINE
CORE = COMMON.CORE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S877.private.v1.jsonl"
SEGMENT = 877
TUNNEL_SUCCESS_RECORD_IDS = PREVIOUS.TUNNEL_SUCCESS_RECORD_IDS
TUNNEL_SUCCESS_SOURCE = PREVIOUS.TUNNEL_SUCCESS_SOURCE
TUNNEL_SUCCESS_REPORT = PREVIOUS.TUNNEL_SUCCESS_REPORT
TUNNEL_FALL_RECORD_IDS = tuple(range(1239, 1251))
TUNNEL_FALL_SOURCE = (
    "金堀衆の土竜攻めにより\n",
    "が",
    "の\n手に落ち",
    "ぞ！",
)
TUNNEL_FALL_REPORT = (
    "광부대의 땅굴 공략으로\n",
    "이(가)",
    "의\n손에 넘어가",
    "다!",
)
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:{literal_id}": text
        for record_id in range(1233, 1239)
        for literal_id, text in enumerate(TUNNEL_SUCCESS_REPORT)
    },
    **{
        f"15:{record_id}:{literal_id}": text
        for record_id in range(1239, 1241)
        for literal_id, text in enumerate(TUNNEL_FALL_REPORT)
    },
}
RECORD_ARITIES = {
    **{record_id: 3 for record_id in range(1233, 1239)},
    1239: 4,
    1240: 4,
}
EXPECTED_JP = {
    **{
        record_id: TUNNEL_SUCCESS_SOURCE
        for record_id in range(1233, 1239)
    },
    1239: TUNNEL_FALL_SOURCE,
    1240: TUNNEL_FALL_SOURCE,
}
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("", "026432", "014314020000", "050505")
        for record_id in range(1233, 1239)
    },
    1239: ("", "026432", "025032", "014314020000", "050505"),
    1240: ("", "026432", "025032", "014314020000", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **{
        record_id: ("", "026432", "01431a020000", "050505")
        for record_id in range(1233, 1239)
    },
    1239: ("", "026432", "025032", "01431a020000", "050505"),
    1240: ("", "026432", "025032", "01431a020000", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "gold_miner_corps_tunnel_siege_success_and_castle_fall_report_families_"
    "with_uniform_plus_8_pk_jp_sc_tc_exact_mapping_dynamic_castle_house_"
    "and_speaker_tokens_historical_mining_engineer_siege_context_project_"
    "tunnel_siege_and_miner_corps_terminology_shared_1230_1238_success_"
    "canonical_and_exported_1239_1250_fall_canonical_current_layout_runtime_"
    "fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(1233, 1239):
        if CORE.source_literals(source_records, record_id) != TUNNEL_SUCCESS_SOURCE:
            raise RuntimeError(
                f"segment 877 tunnel success source canonical drifted: {record_id}"
            )
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(3)
        )
        if actual != TUNNEL_SUCCESS_REPORT:
            raise RuntimeError(
                f"segment 877 tunnel success translation drifted: {record_id}"
            )
    for record_id in range(1239, 1241):
        if CORE.source_literals(source_records, record_id) != TUNNEL_FALL_SOURCE:
            raise RuntimeError(
                f"segment 877 tunnel fall source canonical drifted: {record_id}"
            )
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(4)
        )
        if actual != TUNNEL_FALL_REPORT:
            raise RuntimeError(
                f"segment 877 tunnel fall translation drifted: {record_id}"
            )

    prior_success = tuple(
        PREVIOUS.RAW_TRANSLATIONS[f"15:1230:{literal_id}"]
        for literal_id in range(3)
    )
    if prior_success != TUNNEL_SUCCESS_REPORT:
        raise RuntimeError("segment 877 preceding success canonical drifted")
    if tuple(TUNNEL_SUCCESS_RECORD_IDS) != tuple(range(1230, 1239)):
        raise RuntimeError("segment 877 shared success family coordinates drifted")
    if tuple(TUNNEL_FALL_RECORD_IDS) != tuple(range(1239, 1251)):
        raise RuntimeError("segment 877 exported fall family coordinates drifted")

    joined = "\n".join(translations.values())
    for required in ("땅굴 공략", "광부대", "함락", "손에 넘어가"):
        if required not in joined:
            raise RuntimeError(f"segment 877 siege terminology drifted: {required}")
    if any(term in joined for term in ("두더지", "땅굴 공격", "광부 부대")):
        raise RuntimeError("segment 877 retained forbidden terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 877 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S877",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "exact_tunnel_success_records": 6,
                "exact_tunnel_fall_records": 2,
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
