#!/usr/bin/env python3
"""Build Base authoring segment 834 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment833 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S834.private.v1.jsonl"
SEGMENT = 834
RAW_TRANSLATIONS: dict[str, str] = {
    "15:643:0": (
        "의 분들을 가신으로\n"
        "맞이할 수 없을까요? 화를\n"
        "내실지도 모르지만…"
    ),
    "15:644:0": "이제는",
    "15:644:1": (
        "의 사람들을\n"
        "휘하에 들일 때인지도 모르오\n"
        "거세게 저항할지도 모르지만…"
    ),
    "15:645:0": "이런 말씀을 드리면 꾸중을 들을지도\n모르겠습니다만",
    "15:645:1": "의 분들을\n가신으로 맞아들이지 않겠습니까?",
    "15:646:0": "진노하실 수도 있사오나\n",
    "15:646:1": "을(를) 휘하에 들여\n우리 가문만의 힘으로 삼지 않겠사옵니까?",
    "15:647:0": (
        "의 녀석들이 우리 가문\n"
        "휘하에 들고 싶다는군!\n"
        "받아들이지 않을 이유가 없지!"
    ),
    "15:648:0": "아무래도",
    "15:648:1": (
        "은(는) 우리 가문 휘하에\n"
        "들 각오가 된 듯하오…\n"
        "받아들여야 하지 않겠소?"
    ),
    "15:649:0": (
        "은(는) 아무래도 우리 가문\n"
        "휘하에 드는 데 거리낌이 없는 모양\n"
        "가신 편입을 타진해 보심이 어떻겠습니까?"
    ),
    "15:650:0": (
        "이(가) 우리 가문의 가신 반열에\n"
        "들고 싶어 하는 듯하옵니다\n"
        "어찌하시겠사옵니까?"
    ),
    "15:651:0": (
        "에서 우리 가문 휘하에\n"
        "들고 싶다 청해 왔사옵니다\n"
        "어찌하시겠사옵니까"
    ),
    "15:652:0": (
        "을(를) 어떻게 생각하십니까\n"
        "국인중으로 남겨 두면 성가시니… 차라리\n"
        "가신으로 편입하는 것이 어떻겠습니까?"
    ),
    "15:653:0": "이(가) 보기에는\n",
    "15:653:1": "은(는) 우리 가문 휘하에 있는\n편이 어울릴 듯하옵니다만",
    "15:654:0": (
        "을(를) 가신으로 편입해야 할 듯하옵니다\n"
        "노할지도 모르오나\n"
        "교섭해 볼 가치는 있사옵니다…"
    ),
    "15:655:0": (
        "의 분들은 이제 남처럼\n"
        "느껴지지 않습니다. 차라리\n"
        "가신이 되어 주신다면…"
    ),
    "15:656:0": (
        "은(는) 오히려 우리 가문의 가신이\n"
        "되고 싶어 하는 듯 보이는군\n"
        "교섭해 봐야 할까…"
    ),
    "15:657:0": (
        "의 분들은 가족이나 다름없어요\n"
        "휘하에 들도록 교섭하면\n"
        "제안에 응해 주지 않을까요…"
    ),
    "15:658:0": (
        "은(는) 우리 가문의 가신단에\n"
        "합류하고 싶어 하는 듯하옵니다\n"
        "어찌하시겠사옵니까"
    ),
    "15:659:0": (
        "의 무리는 이제 남이라고\n"
        "생각되지 않는다! 차라리 우리 가문\n"
        "휘하에 들여야 하지 않겠는가?"
    ),
}
RECORD_ARITIES = {
    643: 1,
    644: 2,
    645: 2,
    646: 2,
    647: 1,
    648: 2,
    649: 1,
    650: 1,
    651: 1,
    652: 1,
    653: 2,
    654: 1,
    655: 1,
    656: 1,
    657: 1,
    658: 1,
    659: 1,
}
EXPECTED_BASE_GAPS = {
    643: ("028c32", "050505"),
    644: ("", "028c32", "050505"),
    645: ("", "028c32", "050505"),
    646: ("", "028c32", "050505"),
    647: ("028c32", "050505"),
    648: ("", "028c32", "050505"),
    649: ("028c32", "050505"),
    650: ("028c32", "050505"),
    651: ("028c32", "050505"),
    652: ("028c32", "050505"),
    653: ("014301000000", "028c32", "050505"),
    **{record_id: ("028c32", "050505") for record_id in range(654, 660)},
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_EN_ARITIES = {record_id: 1 for record_id in RECORD_ARITIES}
EXPECTED_PK_EN_GAPS = {record_id: ("", "050505") for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:643:0",
    "15:644:1",
    "15:648:1",
    "15:652:0",
    "15:654:0",
    "15:655:0",
    "15:656:0",
    "15:657:0",
}
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_kokujin_household_integration_"
    "negotiation_and_willingness_reports_with_exact_uniform_plus_7_pk_jp_sc_"
    "tc_arrays_pk_en_sc_tc_auxiliary_context_current_pc_line_token_gap_"
    "boundaries_preserved_proposal_negotiation_stage_historical_register_"
    "person_voice_and_dynamic_particles_verified_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if not (
        COMMON.COMMON.source_literals(source_records, 635)
        == COMMON.COMMON.source_literals(source_records, 659)
        == COMMON.COMMON.source_literals(source_records, 671)
    ):
        raise RuntimeError("segment 834 635/659/671 exact source group drifted")
    if raw_translations["15:659:0"] != COMMON.RAW_TRANSLATIONS["15:635:0"]:
        raise RuntimeError("segment 834 15:659 exact translation reuse drifted")
    if (
        COMMON.COMMON.source_literals(source_records, 644)
        == COMMON.COMMON.source_literals(source_records, 668)
    ):
        raise RuntimeError("segment 834 644/668 resistance distinction collapsed")
    if "거세게 저항할지도" not in translations["15:644:1"]:
        raise RuntimeError("segment 834 15:644 resistance risk drifted")

    particle_expectations = {
        "15:643:0": "의 ",
        "15:644:1": "의 ",
        "15:645:1": "의 ",
        "15:646:1": "을(를) ",
        "15:647:0": "의 ",
        "15:648:1": "은(는) ",
        "15:649:0": "은(는) ",
        "15:650:0": "이(가) ",
        "15:651:0": "에서 ",
        "15:652:0": "을(를) ",
        "15:653:0": "이(가) ",
        "15:653:1": "은(는) ",
        "15:654:0": "을(를) ",
        "15:655:0": "의 ",
        "15:656:0": "은(는) ",
        "15:657:0": "의 ",
        "15:658:0": "은(는) ",
        "15:659:0": "의 ",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(f"segment 834 dynamic name particle drifted: {coordinate}")

    if translations["15:648:0"] != "아무래도":
        raise RuntimeError("segment 834 15:648 opening adverb drifted")
    joined = "\n".join(translations.values())
    for required in ("국인중", "휘하", "가신", "가신단", "편입", "교섭"):
        if required not in joined:
            raise RuntimeError(f"segment 834 stage/terminology drifted: {required}")
    if any(term in joined for term in ("호족", "산하", "당가", "가신화", "거두어들")):
        raise RuntimeError("segment 834 retained forbidden legacy terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.COMMON.build_segment_rows(
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
        raise RuntimeError("segment 834 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S834",
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
