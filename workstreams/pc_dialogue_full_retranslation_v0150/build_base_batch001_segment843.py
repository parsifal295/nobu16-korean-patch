#!/usr/bin/env python3
"""Build Base authoring segment 843 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment842 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S843.private.v1.jsonl"
SEGMENT = 843
REPEATED_INCITEMENT = "에서 백성을 선동하여\n적의 지배에서 벗어나게 하"
RAW_TRANSLATIONS: dict[str, str] = {
    "15:774:0": "을(를) 비롯해 총",
    "15:774:1": "개 군에서 일부 취락의 장악 상태 해제",
    **{
        f"15:{record_id}:0": REPEATED_INCITEMENT
        for record_id in range(775, 795)
    },
}
RECORD_ARITIES = {774: 2, **{record_id: 1 for record_id in range(775, 795)}}
EXPECTED_JP = {
    774: ("など", "郡で一部集落の掌握状態解除"),
    **{
        record_id: ("にて民を煽動して\n支配を解かせ",)
        for record_id in range(775, 795)
    },
}
EXPECTED_BASE_GAPS = {
    774: ("029632", "0232", "050505"),
    **{
        record_id: ("029632", "01431e040000050505")
        for record_id in range(775, 795)
    },
}
EXPECTED_PK_JP_GAPS = {
    774: ("029632", "0232", "050505"),
    **{
        record_id: ("029632", "01432a040000050505")
        for record_id in range(775, 795)
    },
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
SC_AUXILIARY = {
    774: (
        ("等", "郡的部分聚落的掌控状态解除。"),
        ("029632", "0232", "050505"),
    ),
}
TC_AUXILIARY = {
    774: (
        ("等", "郡部分聚落的掌控狀態解除"),
        ("029632", "0232", "050505"),
    ),
}
EN_AUXILIARY = {
    774: (
        (" county(ies), including ", ", relinquished control of part of their settlements."),
        ("0232", "029632", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): value
        for side in ("base", "pk")
        for record_id, value in SC_AUXILIARY.items()
    },
    **{
        (side, "TC", record_id): value
        for side in ("base", "pk")
        for record_id, value in TC_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
BASIS = (
    "pristine_base_pc_jp_authoritative_settlement_control_release_ui_and_"
    "popular_incitement_runtime_stems_with_uniform_plus_7_pk_jp_sc_tc_mapping_"
    "pk_en_auxiliary_context_dynamic_county_list_count_and_location_tokens_"
    "cross_segment_23_record_exact_source_translation_group_current_pc_layout_"
    "opcode_skeleton_and_isolated_reverse_overlay_verified_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    source_anchor = COMMON.CORE.source_literals(source_records, 775)
    if source_anchor != ("にて民を煽動して\n支配を解かせ",):
        raise RuntimeError("segment 843 incitement source anchor drifted")
    for record_id in range(775, 798):
        if COMMON.CORE.source_literals(source_records, record_id) != source_anchor:
            raise RuntimeError(
                f"segment 843/844 repeated incitement source drifted: {record_id}"
            )
    for record_id in range(775, 795):
        if raw_translations[f"15:{record_id}:0"] != REPEATED_INCITEMENT:
            raise RuntimeError(
                f"segment 843 repeated incitement translation drifted: {record_id}"
            )
        if not translations[f"15:{record_id}:0"].startswith("에서 백성을 선동하여\n"):
            raise RuntimeError(
                f"segment 843 dynamic incitement location particle drifted: {record_id}"
            )
        if not translations[f"15:{record_id}:0"].endswith(
            "적의 지배에서 벗어나게 하"
        ):
            raise RuntimeError(
                f"segment 843 支配を解かせ causative meaning drifted: {record_id}"
            )

    if raw_translations["15:774:0"] != "을(를) 비롯해 총":
        raise RuntimeError("segment 843 15:774 list/count UI assembly drifted")
    if not raw_translations["15:774:1"].startswith("개 군에서 "):
        raise RuntimeError("segment 843 15:774 county-count suffix drifted")
    joined = "\n".join(translations.values())
    for required in ("군", "취락", "장악 상태 해제", "백성", "선동", "적의 지배"):
        if required not in joined:
            raise RuntimeError(
                f"segment 843 control/incitement terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("따위", "지배를 풀게 하", "현", "민중을 부추겨")
    ):
        raise RuntimeError("segment 843 retained forbidden legacy wording")


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
        excluded_blank_coordinates=set(),
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 843 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S843",
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
