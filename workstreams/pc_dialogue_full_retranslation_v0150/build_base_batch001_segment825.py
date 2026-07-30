#!/usr/bin/env python3
"""Build Base authoring segment 825 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S825.private.v1.jsonl"
SEGMENT = 825
RAW_TRANSLATIONS: dict[str, str] = {
    "15:521:0": "의",
    "15:521:1": "을(를) 회유하는 것이 상책이옵니다\n",
    "15:521:2": "께서 먼저 인덕을 보이시면\n상대도 온 힘을 다해 보답하는 법이옵니다",
    "15:522:0": "의",
    "15:522:1": (
        "에 대한 회유를 더 진척시키시지요\n"
        "국인중이 하나로 뭉쳐 원군으로 참전하도록\n"
        "물자를 보내 두루 환심을 사는 것이옵니다"
    ),
    "15:523:0": "의",
    "15:523:1": (
        "을(를) 한층 더 회유하시지요\n"
        "아직 우리 가문을 위해 참전하기를 꺼리는 자도 있는 듯하니\n"
        "물자를 보내 그들까지 우리 편으로 끌어들이는 것이옵니다"
    ),
    "15:524:0": "의",
    "15:524:1": (
        "을(를) 회유하시옵소서\n"
        "우리 가문에 가담하는 것이 이롭다는 것을 알면\n"
        "원군으로 전장에 나설 자도 늘 것이옵니다"
    ),
    "15:525:0": "의",
    "15:525:1": (
        "은(는) 아직 진심으로 따르지 않는군\n"
        "금품을 보내 주면\n"
        "더 다루기 쉬워지겠지"
    ),
    "15:526:0": "의",
    "15:526:1": (
        "에게 한층 더 회유책을 펼치시지요\n"
        "금품을 보내 환심을 사면\n"
        "더 기꺼이 힘을 보탤 것이옵니다"
    ),
    "15:527:0": "의",
    "15:527:1": (
        "와(과) 맺은 친교를\n"
        "더욱 깊이 다지시는 것이 어떻겠사옵니까\n"
        "전쟁이 벌어지면 많은 병력을 보내 줄 듯하옵니다"
    ),
    "15:528:0": "의",
    "15:528:1": "을(를) 진심으로 따르게 하라\n금품을 조금 더 내주면\n",
    "15:528:2": "을(를) 믿고 따르리라",
    "15:529:0": "의",
    "15:529:1": (
        "을(를)\n"
        "더욱 회유해 보는 것이 어떻겠사옵니까?\n"
        "전시에는 많은 병력을 보내올 것이옵니다"
    ),
    "15:530:0": "의",
    "15:530:1": (
        "에 대한 회유를 더 진척시키시지요\n"
        "금품을 더 보내 환심을 사면\n"
        "아낌없는 협력을 얻을 수 있을 듯하옵니다"
    ),
}
RECORD_ARITIES = {
    521: 3,
    522: 2,
    523: 2,
    524: 2,
    525: 2,
    526: 2,
    527: 2,
    528: 3,
    529: 2,
    530: 2,
}
EXPECTED_BASE_GAPS = {
    521: ("029632", "028c32", "014307000000", "050505"),
    522: ("029632", "028c32", "050505"),
    523: ("029632", "028c32", "050505"),
    524: ("029632", "028c32", "050505"),
    525: ("029632", "028c32", "050505"),
    526: ("029632", "028c32", "050505"),
    527: ("029632", "028c32", "050505"),
    528: ("029632", "028c32", "014307000000", "050505"),
    529: ("029632", "028c32", "050505"),
    530: ("029632", "028c32", "050505"),
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_EN_ARITIES = {record_id: 1 for record_id in RECORD_ARITIES}
EXPECTED_PK_EN_GAPS = {record_id: ("", "050505") for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_kokujin_deeper_conciliation_"
    "and_full_reinforcement_participation_fragments_with_exact_uniform_plus_7_"
    "pk_jp_sc_tc_arrays_pk_en_sc_tc_auxiliary_context_current_pc_line_token_"
    "gap_boundaries_preserved_historical_kokujin_reinforcement_stage_"
    "heartfelt_allegiance_person_voice_and_dynamic_particles_verified_"
    "runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    possessive_source = COMMON.source_literals(source_records, 512)[0]
    if possessive_source != "の":
        raise RuntimeError("segment 825 possessive exact-source anchor drifted")
    for record_id in range(519, 542):
        if COMMON.source_literals(source_records, record_id)[0] != possessive_source:
            raise RuntimeError(
                f"segment 825 cross-boundary possessive source drifted: {record_id}"
            )
    for record_id in RECORD_ARITIES:
        if raw_translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(f"segment 825 possessive raw reuse drifted: {record_id}")
        if translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(f"segment 825 possessive particle drifted: {record_id}")

    particle_expectations = {
        "15:521:1": "을(를) ",
        "15:521:2": "께서 ",
        "15:522:1": "에 대한 ",
        "15:523:1": "을(를) ",
        "15:524:1": "을(를) ",
        "15:525:1": "은(는) ",
        "15:526:1": "에게 ",
        "15:527:1": "와(과) ",
        "15:528:1": "을(를) ",
        "15:528:2": "을(를) ",
        "15:529:1": "을(를)\n",
        "15:530:1": "에 대한 ",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(f"segment 825 dynamic name particle drifted: {coordinate}")

    joined = "\n".join(translations.values())
    for required in (
        "국인중",
        "회유",
        "원군으로 참전",
        "우리 편으로 끌어들이",
        "전장에 나설",
        "진심으로 따르",
        "우리 가문",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 825 stage/terminology drifted: {required}")
    if any(
        term in joined
        for term in ("호족", "길들이", "심복", "당가", "가신단", "우리 가문에 편입")
    ):
        raise RuntimeError("segment 825 retained a forbidden term or premature final integration")


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
        raise RuntimeError("segment 825 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S825",
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
