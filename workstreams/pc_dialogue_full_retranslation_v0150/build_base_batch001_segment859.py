#!/usr/bin/env python3
"""Build Base authoring segment 859 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment858 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S859.private.v1.jsonl"
SEGMENT = 859
TRANSFER_SOURCE_1008_1018 = (
    "もはやこれまで\n以後",
    "の一武将として\n生きることといたそう",
)
TRANSFER_CANONICAL_1008_1018 = (
    "이제는 여기까지로군\n앞으로는",
    "의 일개 무장으로서\n살아가기로 하겠소",
)
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in range(1008, 1019)
        for literal_id, translation in enumerate(TRANSFER_CANONICAL_1008_1018)
    },
    "15:1019:0": "와(과)의 교섭이 완료되어\n이후 정식으로 우리",
    "15:1019:1": "의\n가신단에 편입되",
}
RECORD_ARITIES = {
    **{record_id: 2 for record_id in range(1008, 1019)},
    1019: 2,
}
EXPECTED_JP = {
    **{
        record_id: TRANSFER_SOURCE_1008_1018
        for record_id in range(1008, 1019)
    },
    1019: (
        "との折衝が完了し\n以後は正式に我ら",
        "の\n家中として働く運びとな",
    ),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("", "025032", "050505") for record_id in range(1008, 1019)},
    1019: ("025032", "02463e", "014368020000050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1019: ("025032", "02463e", "014374020000050505"),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
TRANSFER_SC = (
    ("看来到此为止了。\n从今以后，\n将作为", "的一员武将而活。"),
    ("", "025032", "050505"),
)
TRANSFER_TC = (
    ("看來到此為止了。\n從今以後，\n將作為", "的一員武將而活。"),
    ("", "025032", "050505"),
)
TRANSFER_EN = (
    (
        "I guess thereÖs no other way. I will continue to live as officers of the ",
        ".",
    ),
    ("", "025032", "050505"),
)
SC_1019 = (
    (
        "与",
        "的交涉结束，\n以后将正式作为我等",
        "的\n臣下，为我等效力。",
    ),
    ("", "025032", "02463e", "050505"),
)
TC_1019 = (
    (
        "與",
        "的交涉結束，\n以後將正式作為我等",
        "的\n臣下，為我等效力。",
    ),
    ("", "025032", "02463e", "050505"),
)
EN_1019 = (
    (
        "Now that negotiations with the ",
        " are complete, they wish to become formal members of the ",
        ".",
    ),
    ("", "025032", "02463e", "050505"),
)
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): TRANSFER_SC
        for side in ("base", "pk")
        for record_id in (1009, 1010, 1011, 1015)
    },
    **{
        (side, "TC", record_id): TRANSFER_TC
        for side in ("base", "pk")
        for record_id in (1009, 1010, 1011, 1015)
    },
    **{
        ("pk", "EN", record_id): TRANSFER_EN
        for record_id in (1009, 1010, 1011, 1015)
    },
    **{
        (side, "SC", 1019): SC_1019
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1019): TC_1019
        for side in ("base", "pk")
    },
    ("pk", "EN", 1019): EN_1019,
}
BASIS = (
    "review_queue_base_msggame_B104_pristine_base_pc_jp_authoritative_"
    "kokujin_lord_to_single_officer_transfer_and_negotiated_household_"
    "incorporation_with_uniform_plus_7_pk_jp_mapping_base_pk_sc_tc_exact_"
    "pk_en_auxiliary_context_exact_1008_1018_group_distinct_1007_dynamic_"
    "conjugation_stem_household_terminology_current_layout_opcode_skeleton_"
    "preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(1008, 1019):
        if COMMON.COMMON.CORE.source_literals(
            source_records, record_id
        ) != TRANSFER_SOURCE_1008_1018:
            raise RuntimeError(
                f"segment 859 exact transfer source group drifted: {record_id}"
            )
        for literal_id, expected in enumerate(TRANSFER_CANONICAL_1008_1018):
            coordinate = f"15:{record_id}:{literal_id}"
            if raw_translations[coordinate] != expected:
                raise RuntimeError(
                    f"segment 859 exact transfer raw group drifted: {coordinate}"
                )
            if translations[coordinate] != expected:
                raise RuntimeError(
                    f"segment 859 exact transfer resolved group drifted: {coordinate}"
                )
    if COMMON.COMMON.CORE.source_literals(
        source_records, 1007
    ) == TRANSFER_SOURCE_1008_1018:
        raise RuntimeError("segment 859 distinct 1007 conjugation source collapsed")
    if PRIOR.TRANSFER_STEM_1007[0] != TRANSFER_CANONICAL_1008_1018[0]:
        raise RuntimeError("segment 859 1007/1008 shared leading fragment drifted")
    if TRANSFER_CANONICAL_1008_1018[1] != PRIOR.TRANSFER_STEM_1007[1] + "겠소":
        raise RuntimeError("segment 859 1007 dynamic stem/full-form relation drifted")
    if raw_translations["15:1019:1"] != "의\n가신단에 편입되":
        raise RuntimeError("segment 859 1019 家中 incorporation stem drifted")
    joined = "\n".join(translations.values())
    for required in ("일개 무장", "교섭", "가신단", "편입"):
        if required not in joined:
            raise RuntimeError(f"segment 859 terminology drifted: {required}")
    if any(term in joined for term in ("가신으로", "흡수", "거두어들")):
        raise RuntimeError("segment 859 retained forbidden household terminology")


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
        excluded_blank_literals={},
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 859 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S859",
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
