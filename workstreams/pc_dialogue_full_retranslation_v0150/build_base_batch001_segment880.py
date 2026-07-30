#!/usr/bin/env python3
"""Build Base authoring segment 880 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment879 as PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S880.private.v1.jsonl"
)
SEGMENT = 880
FAILURE_GROUPS = {
    1251: (1251, 1263),
    1252: (1252, 1262, 1264, 1274),
    1253: (1253, 1265),
    1254: (1254, 1266),
    1255: (1255, 1267),
    1256: (1256, 1268),
    1257: (1257, 1269),
    1258: (1258, 1270),
    1259: (1259, 1271),
    1260: (1260, 1272),
    1261: (1261, 1273),
}
RECORD_TO_CANONICAL = {
    record_id: canonical_id
    for canonical_id, record_ids in FAILURE_GROUPS.items()
    for record_id in record_ids
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:0": PRIOR.FAILURE_CANONICALS[
        RECORD_TO_CANONICAL[record_id]
    ]
    for record_id in range(1252, 1275)
}
RECORD_ARITIES = {record_id: 1 for record_id in range(1252, 1275)}
EXPECTED_JP = {
    record_id: (
        PRIOR.FAILURE_SOURCES[RECORD_TO_CANONICAL[record_id]],
    )
    for record_id in RECORD_ARITIES
}
EXPECTED_BASE_GAPS = {
    record_id: ("", "050505") for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "tunnel_assault_failure_reports_with_uniform_plus_8_pk_jp_exact_mapping_"
    "blank_sc_tc_pk_en_auxiliary_context_exact_speaker_pairs_and_repeated_"
    "source_translation_groups_force_assault_one_rope_idiom_kanahorishu_"
    "survival_semantics_project_siege_terminology_speaker_register_current_"
    "layout_and_opcode_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for canonical_id, record_ids in FAILURE_GROUPS.items():
        expected_source = (PRIOR.FAILURE_SOURCES[canonical_id],)
        expected_translation = PRIOR.FAILURE_CANONICALS[canonical_id]
        for record_id in record_ids:
            if COMMON.CORE.source_literals(
                source_records, record_id
            ) != expected_source:
                raise RuntimeError(
                    f"segment 880 exact failure source group drifted: "
                    f"{canonical_id}/{record_id}"
                )
            if record_id == 1251:
                if (
                    PRIOR.RAW_TRANSLATIONS["15:1251:0"]
                    != expected_translation
                ):
                    raise RuntimeError(
                        "segment 880 cross-segment 1251 canonical drifted"
                    )
                continue
            coordinate = f"15:{record_id}:0"
            if (
                raw_translations[coordinate] != expected_translation
                or translations[coordinate] != expected_translation
            ):
                raise RuntimeError(
                    f"segment 880 exact failure translation group drifted: "
                    f"{canonical_id}/{record_id}"
                )

    joined = "\n".join(translations.values())
    for required in (
        "땅굴 공략",
        "강공",
        "호락호락하지 않",
        "광부대 사람들은 모두 무사",
    ):
        combined = joined + "\n" + PRIOR.FAILURE_CANONICALS[1251]
        if required not in combined:
            raise RuntimeError(
                f"segment 880 siege terminology drifted: {required}"
            )
    if any(
        term in joined
        for term in ("광부 부대", "두더지 공격", "갱도 공격", "땅굴 공격")
    ):
        raise RuntimeError("segment 880 retained forbidden tunnel terminology")


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
        raise RuntimeError("segment 880 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S880",
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
