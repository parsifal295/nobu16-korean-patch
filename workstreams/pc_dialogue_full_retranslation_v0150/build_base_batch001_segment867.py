#!/usr/bin/env python3
"""Build Base authoring segment 867 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment866 as PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S867.private.v1.jsonl"
)
SEGMENT = 867
FAILURE_SOURCE = (
    "すみませぬ、",
    "、",
    "に\n離間工作を勘づかれてしまいました\n"
    "他の勢力も当家を非難しておりまする…",
)
FAILURE_RAW_CANONICAL = (
    "송구하옵니다,",
    "와(과)",
    "에게\n이간 공작이 발각되고 말았습니다\n"
    "다른 세력도 우리 가문을 비난하고 있사옵니다…",
)
FAILURE_RESOLVED_CANONICAL = (
    FAILURE_RAW_CANONICAL[0],
    FAILURE_RAW_CANONICAL[1],
    FAILURE_RAW_CANONICAL[2][:-1] + "……",
)
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in range(1105, 1109)
        for literal_id, translation in enumerate(PRIOR.SEVER_CANONICAL)
    },
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in range(1109, 1112)
        for literal_id, translation in enumerate(FAILURE_RAW_CANONICAL)
    },
}
RECORD_ARITIES = {record_id: 3 for record_id in range(1105, 1112)}
EXPECTED_JP = {
    **{record_id: PRIOR.SEVER_SOURCE for record_id in range(1105, 1109)},
    **{record_id: FAILURE_SOURCE for record_id in range(1109, 1112)},
}
EXPECTED_BASE_GAPS = {
    record_id: ("", "025032", "025132", "050505")
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES = {
    f"15:{record_id}:2" for record_id in range(1109, 1112)
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B105_pristine_base_pc_jp_authoritative_"
    "sowing_discord_alliance_severance_success_and_exposure_failure_reports_"
    "with_uniform_plus_8_pk_jp_exact_mapping_blank_sc_tc_pk_en_auxiliary_"
    "context_exact_repeated_source_token_and_translation_groups_dynamic_"
    "faction_tokens_diplomacy_terminology_current_layout_and_opcode_skeleton_"
    "preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(1105, 1109):
        if (
            COMMON.CORE.source_literals(source_records, record_id)
            != PRIOR.SEVER_SOURCE
        ):
            raise RuntimeError(
                f"segment 867 exact alliance-severance source group drifted: "
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
        if (
            raw_group != PRIOR.SEVER_CANONICAL
            or resolved_group != PRIOR.SEVER_CANONICAL
        ):
            raise RuntimeError(
                f"segment 867 approved success canonical drifted: {record_id}"
            )

    for record_id in range(1109, 1112):
        if COMMON.CORE.source_literals(source_records, record_id) != FAILURE_SOURCE:
            raise RuntimeError(
                f"segment 867 exact exposure-failure source group drifted: "
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
        if raw_group != FAILURE_RAW_CANONICAL:
            raise RuntimeError(
                f"segment 867 raw failure canonical drifted: {record_id}"
            )
        if resolved_group != FAILURE_RESOLVED_CANONICAL:
            raise RuntimeError(
                f"segment 867 resolved failure canonical drifted: {record_id}"
            )

    if PRIOR.SEVER_SOURCE == FAILURE_SOURCE:
        raise RuntimeError("segment 867 distinct success/failure sources collapsed")
    joined = "\n".join(translations.values())
    for required in (
        "이간 공작",
        "단교",
        "발각",
        "다른 세력",
        "우리 가문",
        "비난",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 867 diplomacy terminology drifted: {required}"
            )
    if any(term in joined for term in ("이간계", "당가", "들키", "손을 끊")):
        raise RuntimeError("segment 867 retained forbidden diplomacy phrasing")


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
        raise RuntimeError("segment 867 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S867",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
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
