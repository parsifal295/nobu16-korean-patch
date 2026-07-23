#!/usr/bin/env python3
"""Build Base authoring segment 866 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment865 as PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S866.private.v1.jsonl"
)
SEGMENT = 866
SEVER_SOURCE = (
    "ふふふ、我が離間工作が為り\n",
    "と",
    "は手を切りましたぞ\nさあ、次はいかな手を打ちましょう？",
)
SEVER_CANONICAL = (
    "후후후, 내 이간 공작이 성공하여\n",
    "와(과)",
    "이(가) 단교하였사옵니다\n자, 다음에는 어떤 수를 써 볼까요?",
)
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id in range(1098, 1105)
    for literal_id, translation in enumerate(SEVER_CANONICAL)
}
RECORD_ARITIES = {record_id: 3 for record_id in range(1098, 1105)}
EXPECTED_JP = {record_id: SEVER_SOURCE for record_id in RECORD_ARITIES}
EXPECTED_BASE_GAPS = {
    record_id: ("", "025032", "025132", "050505")
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B105_pristine_base_pc_jp_authoritative_"
    "sowing_discord_alliance_severance_success_reports_with_uniform_plus_8_"
    "pk_jp_exact_mapping_blank_sc_tc_pk_en_auxiliary_context_exact_1097_1108_"
    "source_and_token_group_approved_canonical_diplomacy_terminology_current_"
    "layout_and_opcode_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if PRIOR.SEVER_ALLIANCE_REPORT != SEVER_CANONICAL:
        raise RuntimeError("segment 866 approved B104 canonical drifted")
    if COMMON.CORE.source_literals(source_records, 1097) != SEVER_SOURCE:
        raise RuntimeError("segment 866 B104 1097 source boundary drifted")

    for record_id in RECORD_ARITIES:
        if COMMON.CORE.source_literals(source_records, record_id) != SEVER_SOURCE:
            raise RuntimeError(
                f"segment 866 exact alliance-severance source group drifted: "
                f"{record_id}"
            )
        raw_group = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(3)
        )
        resolved_group = tuple(
            translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(3)
        )
        if raw_group != SEVER_CANONICAL or resolved_group != SEVER_CANONICAL:
            raise RuntimeError(
                f"segment 866 approved canonical group drifted: {record_id}"
            )

    joined = "\n".join(translations.values())
    for required in ("이간 공작", "단교"):
        if required not in joined:
            raise RuntimeError(
                f"segment 866 diplomacy terminology drifted: {required}"
            )
    if any(term in joined for term in ("이간계", "손을 끊", "나의 이간")):
        raise RuntimeError("segment 866 retained forbidden alliance phrasing")


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
        raise RuntimeError("segment 866 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S866",
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
