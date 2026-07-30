#!/usr/bin/env python3
"""Build Base authoring segment 848 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment847 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S848.private.v1.jsonl"
SEGMENT = 848
CONTROL_ADVANCE_TRANSLATION = (
    "의 지배력을 확대했사옵니다\n"
    "이로써 수입과 병력도 늘었사옵니다"
)
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in range(858, 865)
        for literal_id, translation in enumerate(PRIOR.DOMAIN_TRANSLATIONS)
    },
    **{
        f"15:{record_id}:0": CONTROL_ADVANCE_TRANSLATION
        for record_id in range(865, 873)
    },
}
RECORD_ARITIES = {
    **{record_id: 2 for record_id in range(858, 865)},
    **{record_id: 1 for record_id in range(865, 873)},
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("", "029632", "050505") for record_id in range(858, 865)},
    **{record_id: ("029632", "050505") for record_id in range(865, 873)},
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_EN_ARITIES = {
    **{record_id: 1 for record_id in range(858, 873)},
    861: 2,
}
EXPECTED_PK_EN_GAPS = {
    **{record_id: ("", "050505") for record_id in range(858, 873)},
    861: ("", "029632", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
BASIS = (
    "base_msggame_B103_pristine_base_pc_jp_authoritative_exact_cross_batch_"
    "domain_control_assistance_request_and_control_advance_result_groups_"
    "uniform_plus_7_pk_jp_sc_arrays_base_pk_sc_tc_exact_pk_en_auxiliary_"
    "context_dynamic_territory_token_historical_deferential_register_current_"
    "pc_line_gap_outer_signature_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    domain_source = (
        "我が領地",
        "の支配を進める\n援助をお願いできませぬか",
    )
    if any(
        COMMON.source_literals(source_records, record_id) != domain_source
        for record_id in range(853, 865)
    ):
        raise RuntimeError("segment 848 853-864 cross-batch domain source drifted")
    for record_id in range(858, 865):
        for literal_id, canonical in enumerate(PRIOR.DOMAIN_TRANSLATIONS):
            if raw_translations[f"15:{record_id}:{literal_id}"] != canonical:
                raise RuntimeError(
                    f"segment 848 B102 domain canonical drifted: "
                    f"15:{record_id}:{literal_id}"
                )

    advance_source = (
        "の支配を進めました\nこれで収入や兵も増えましたぞ",
    )
    if any(
        COMMON.source_literals(source_records, record_id) != advance_source
        for record_id in range(865, 877)
    ):
        raise RuntimeError("segment 848 865-876 exact control source drifted")
    if any(
        raw_translations[f"15:{record_id}:0"] != CONTROL_ADVANCE_TRANSLATION
        for record_id in range(865, 873)
    ):
        raise RuntimeError("segment 848 865-872 exact control translation drifted")

    joined = "\n".join(translations.values())
    for required in ("제 영지", "지배력을 확대", "원조", "수입", "병력"):
        if required not in joined:
            raise RuntimeError(f"segment 848 terminology/register drifted: {required}")
    if any(term in joined for term in ("내 영지", "지배를 진행", "병사도 늘")):
        raise RuntimeError("segment 848 retained forbidden legacy phrasing")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_en_arities=EXPECTED_PK_EN_ARITIES,
        pk_en_gaps=EXPECTED_PK_EN_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 848 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S848",
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
