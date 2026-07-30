#!/usr/bin/env python3
"""Build Base authoring segment 878 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment863 as COMMON
import build_base_batch001_segment877 as PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S878.private.v1.jsonl"
)
SEGMENT = 878
TUNNEL_FALL_SOURCE = (
    "金堀衆の土竜攻めにより\n",
    "が",
    "の\n手に落ち",
    "ぞ！",
)
APPROVED_TUNNEL_FALL_REPORT = (
    "광부대의 땅굴 공략으로\n",
    "이(가)",
    "의\n손에 넘어가",
    "다!",
)
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id in range(1241, 1246)
    for literal_id, translation in enumerate(APPROVED_TUNNEL_FALL_REPORT)
}
RECORD_ARITIES = {record_id: 4 for record_id in range(1241, 1246)}
EXPECTED_JP = {
    record_id: TUNNEL_FALL_SOURCE for record_id in RECORD_ARITIES
}
EXPECTED_BASE_GAPS = {
    record_id: ("", "026432", "025032", "014314020000", "050505")
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = {
    record_id: ("", "026432", "025032", "01431a020000", "050505")
    for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "kanahorishu_mining_corps_tunnel_assault_castle_fall_reports_with_uniform_"
    "plus_8_pk_jp_exact_mapping_blank_sc_tc_pk_en_auxiliary_context_exact_"
    "1239_1250_source_token_and_translation_group_base_pk_past_inflection_"
    "opcode_difference_project_siege_terminology_current_layout_and_opcode_"
    "skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if PRIOR.TUNNEL_FALL_REPORT != APPROVED_TUNNEL_FALL_REPORT:
        raise RuntimeError("segment 878 S877 tunnel-fall canonical drifted")
    if PRIOR.TUNNEL_FALL_SOURCE != TUNNEL_FALL_SOURCE:
        raise RuntimeError("segment 878 S877 tunnel-fall source drifted")
    if tuple(PRIOR.TUNNEL_FALL_RECORD_IDS) != tuple(range(1239, 1251)):
        raise RuntimeError("segment 878 S877 tunnel-fall family drifted")
    for record_id in range(1239, 1251):
        if (
            COMMON.CORE.source_literals(source_records, record_id)
            != TUNNEL_FALL_SOURCE
        ):
            raise RuntimeError(
                f"segment 878 exact tunnel-fall source group drifted: {record_id}"
            )
    for record_id in RECORD_ARITIES:
        raw_group = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(4)
        )
        resolved_group = tuple(
            translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(4)
        )
        if (
            raw_group != APPROVED_TUNNEL_FALL_REPORT
            or resolved_group != APPROVED_TUNNEL_FALL_REPORT
        ):
            raise RuntimeError(
                f"segment 878 exact tunnel-fall translation group drifted: "
                f"{record_id}"
            )

    joined = "\n".join(translations.values())
    for required in ("광부대", "땅굴 공략"):
        if required not in joined:
            raise RuntimeError(
                f"segment 878 siege terminology drifted: {required}"
            )
    if any(
        term in joined
        for term in ("광부 부대", "두더지 공격", "갱도 공격", "땅굴 공격")
    ):
        raise RuntimeError("segment 878 retained forbidden tunnel terminology")


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
        raise RuntimeError("segment 878 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S878",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": 0,
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
