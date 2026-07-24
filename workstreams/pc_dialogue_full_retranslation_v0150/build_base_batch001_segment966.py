#!/usr/bin/env python3
"""Build Base authoring segment 966 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment965 as PREVIOUS
import build_base_batch001_segment958 as CANONICAL_A


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S966.private.v1.jsonl"
)
SEGMENT = 966
ACTION_TOKEN = CANONICAL_A.ACTION_TOKEN
CANONICAL_RECORD_MAP = {
    record_id: record_id - 84
    for record_id in range(2105, 2116)
}
TRANSLATIONS_BY_RECORD = {
    record_id: CANONICAL_A.TRANSLATIONS_BY_RECORD[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:2108:0": ""}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    record_id: CANONICAL_A.EXPECTED_BASE_JP[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: CANONICAL_A.EXPECTED_BASE_GAPS[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    record_id: CANONICAL_A.EXPECTED_PK_JP_GAPS[canonical_id]
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2113:0"}
AUXILIARY_OVERRIDES = {
    (side, language, record_id): expected
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items()
    for (side, language, source_id), expected
    in CANONICAL_A.AUXILIARY_OVERRIDES.items()
    if source_id == canonical_id
}
BASIS = (
    "review_queue_base_msggame_B116_A_pristine_base_pc_jp_authoritative_"
    "enemy_force_battle_preparation_permission_foothold_and_dynamic_action_"
    "proposals_exactly_reusing_final_S958_canonical_Korean_tuple_objects_"
    "with_live_base2105_2115_to_2021_2031_plus84_exact_source_assertions_"
    "explicit_base_to_pk_plus30_mapping_exact_jp_sc_tc_literals_and_actual_"
    "pk_en_auxiliary_context_base_pk_2107_morphology_opcode_divergence_"
    "dynamic_castle_force_and_colour_wrapped_action_tokens_gushin_geonui_"
    "shingen_jineon_capture_attack_and_battle_distinctions_hidden_empty_"
    "literal_excluded_project_ellipsis_pair_current_line_counts_and_"
    "protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    460: CANONICAL_A.EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    466: CANONICAL_A.EXPECTED_PK_MORPHOLOGY_TERMINALS[466],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id, canonical_id in CANONICAL_RECORD_MAP.items():
        if (
            TRANSLATIONS_BY_RECORD[record_id]
            is not CANONICAL_A.TRANSLATIONS_BY_RECORD[canonical_id]
        ):
            raise RuntimeError(
                f"segment 966 canonical Korean tuple alias drifted: {record_id}"
            )
        source = source_records[(15, record_id)]
        canonical = source_records[(15, canonical_id)]
        if (
            tuple(x.text for x in ENGINE.parse_record_literals(source))
            != tuple(x.text for x in ENGINE.parse_record_literals(canonical))
            or COMMON.UTIL.record_gaps(source)
            != COMMON.UTIL.record_gaps(canonical)
        ):
            raise RuntimeError(
                f"segment 966 live +84 exact source reuse drifted: "
                f"{canonical_id}/{record_id}"
            )
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 966 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 966 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2107}:
        raise RuntimeError("segment 966 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 966 pristine/current gap drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:2108:0": ""}:
        raise RuntimeError("segment 966 hidden exclusion drifted")
    if any(
        sum(gap.count(ACTION_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 966 action-token cardinality drifted")
    if (
        raw_translations["15:2113:0"].count("…") != 1
        or translations["15:2113:0"].count("…") != 2
    ):
        raise RuntimeError("segment 966 project ellipsis pair drifted")
    required_by_coordinate = {
        "15:2105:1": "시행",
        "15:2107:1": "건의",
        "15:2111:1": "실행",
        "15:2115:1": "진언",
    }
    for coordinate, required in required_by_coordinate.items():
        if required not in translations[coordinate]:
            raise RuntimeError(
                f"segment 966 terminology drifted: {coordinate}/{required}"
            )
    if any("진행" in translation for translation in translations.values()):
        raise RuntimeError("segment 966 forbidden 진행 wording retained")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 966 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
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
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    SUPPORT.annotate_morphology_evidence(
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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 966 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 966 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S966",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "canonical_record_map": CANONICAL_RECORD_MAP,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2107],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": {
                    line_count: sum(
                        text.count("\n") + 1 == line_count
                        for text in translations.values()
                    )
                    for line_count in (1, 2, 3)
                },
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
