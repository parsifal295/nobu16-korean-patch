#!/usr/bin/env python3
"""Build Base authoring segment 833 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment824 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S833.private.v1.jsonl"
SEGMENT = 833
RAW_TRANSLATIONS: dict[str, str] = {
    "15:630:0": "·",
    "15:630:1": "의 종속 단계: 높음 → 최고",
    "15:631:0": "회유로,",
    "15:631:1": "의 출진이 가능해짐",
    "15:632:0": "국인중 회유로,",
    "15:632:1": "의 종속도가 상승",
    "15:633:0": "이(가)",
    "15:633:1": "의 회유에 실패",
    "15:634:0": "에 원군 요청 가능, 국인중 회유 중지",
    "15:635:0": (
        "의 무리는 이제 남이라고\n"
        "생각되지 않는다! 차라리 우리 가문\n"
        "휘하에 들여야 하지 않겠는가?"
    ),
    "15:636:0": "우리와",
    "15:636:1": (
        "은(는) 이제\n"
        "운명을 함께하는 사이이옵니다\n"
        "속히 휘하에 들여야 할 듯하옵니다"
    ),
    "15:637:0": "우리 가문과",
    "15:637:1": (
        "의 이해관계는 일치하오\n"
        "거절당할지도 모르나…\n"
        "가신으로 맞아들이는 것이 어떻겠소?"
    ),
    "15:638:0": "거절당할 수도 있사오나\n",
    "15:638:1": (
        "을(를) 가신으로 편입하기 위한 교섭을\n"
        "시도해 보지 않겠사옵니까?"
    ),
    "15:639:0": (
        "은(는) 이미 가신이나 다름없다\n"
        "교섭해 보는 것이 어떻겠는가?\n"
        "우리 가문만 그리 여기는지도 모르나…"
    ),
    "15:640:0": (
        "은(는) 우리 가문의 영향권에\n"
        "있음이 누구에게나 명백할 것이오\n"
        "차라리 휘하에 들도록 교섭을…"
    ),
    "15:641:0": "반감을 살 수도 있습니다만\n한 번",
    "15:641:1": "에게 우리 가문\n휘하에 들도록 교섭을…",
    "15:642:0": "에잇, 이제 번거롭다!\n",
    "15:642:1": "의 사람들을 우리 가문\n휘하에 들이는 편이 낫다!",
}
RECORD_ARITIES = {
    630: 2,
    631: 2,
    632: 2,
    633: 2,
    634: 1,
    635: 1,
    636: 2,
    637: 2,
    638: 2,
    639: 1,
    640: 1,
    641: 2,
    642: 2,
}
EXPECTED_BASE_GAPS = {
    630: ("", "028c32", "050505"),
    631: ("", "028c32", "050505"),
    632: ("", "028c32", "050505"),
    633: ("024633", "028c32", "050505"),
    634: ("028c32", "050505"),
    635: ("028c32", "050505"),
    636: ("", "028c32", "050505"),
    637: ("", "028c32", "050505"),
    638: ("", "028c32", "050505"),
    639: ("028c32", "050505"),
    640: ("028c32", "050505"),
    641: ("", "028c32", "050505"),
    642: ("", "028c32", "050505"),
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_EN_ARITIES = {
    630: 1,
    631: 2,
    632: 2,
    633: 2,
    634: 2,
    **{record_id: 1 for record_id in range(635, 643)},
}
EXPECTED_PK_EN_GAPS = {
    630: ("", "050505"),
    631: ("", "028c32", "050505"),
    632: ("", "028c32", "050505"),
    633: ("024633", "028c32", "050505"),
    634: ("", "028c32", "050505"),
    **{record_id: ("", "050505") for record_id in range(635, 643)},
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:637:1",
    "15:639:0",
    "15:640:0",
    "15:641:1",
}
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_kokujin_highest_subordination_"
    "system_notices_and_household_integration_negotiation_proposals_with_exact_"
    "uniform_plus_7_pk_jp_sc_tc_arrays_pk_en_sc_tc_auxiliary_context_current_"
    "pc_line_token_gap_boundaries_preserved_kokujin_reinforcement_to_retainer_"
    "stage_historical_register_person_voice_and_dynamic_particles_verified_"
    "runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if not (
        COMMON.source_literals(source_records, 635)
        == COMMON.source_literals(source_records, 659)
        == COMMON.source_literals(source_records, 671)
    ):
        raise RuntimeError("segment 833 635/659/671 exact source group drifted")
    if raw_translations["15:635:0"] != (
        "의 무리는 이제 남이라고\n"
        "생각되지 않는다! 차라리 우리 가문\n"
        "휘하에 들여야 하지 않겠는가?"
    ):
        raise RuntimeError("segment 833 15:635 canonical exact translation drifted")

    particle_expectations = {
        "15:630:1": "의 ",
        "15:631:1": "의 ",
        "15:632:1": "의 ",
        "15:633:0": "이(가)",
        "15:633:1": "의 ",
        "15:634:0": "에 ",
        "15:635:0": "의 ",
        "15:636:1": "은(는) ",
        "15:637:1": "의 ",
        "15:638:1": "을(를) ",
        "15:639:0": "은(는) ",
        "15:640:0": "은(는) ",
        "15:641:1": "에게 ",
        "15:642:1": "의 ",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(f"segment 833 dynamic name particle drifted: {coordinate}")

    joined = "\n".join(translations.values())
    for required in ("국인중 회유", "원군 요청", "휘하", "가신", "편입", "교섭"):
        if required not in joined:
            raise RuntimeError(f"segment 833 stage/terminology drifted: {required}")
    if any(term in joined for term in ("호족", "산하", "당가", "거두어들", "가신화")):
        raise RuntimeError("segment 833 retained forbidden legacy terminology")


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
        raise RuntimeError("segment 833 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S833",
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
