#!/usr/bin/env python3
"""Build Base authoring segment 826 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S826.private.v1.jsonl"
SEGMENT = 826
RAW_TRANSLATIONS: dict[str, str] = {
    "15:531:0": "의",
    "15:531:1": "에 대한 회유도 막바지로군!\n그들이",
    "15:531:2": "께 진심으로 복종하도록\n다시 한번 선심을 써서 우리에게 빚지게 하자고",
    "15:532:0": "의",
    "15:532:1": (
        "에 대한 회유도 마지막 단계이옵니다\n"
        "그들이 우리 가문의 가신이 되기로 결심하도록\n"
        "마지막으로 등을 밀어 주시지요"
    ),
    "15:533:0": "의",
    "15:533:1": (
        "에 대한 회유도 이제 한 걸음 남았사옵니다\n"
        "국인중이 편입 제안을 받아들이기 쉽도록\n"
        "우리 쪽에서 먼저 다가가도록 하지요"
    ),
    "15:534:0": "의",
    "15:534:1": (
        "에 대한 회유를 완수하고자 하옵니다\n"
        "그들과의 관계는 더없이 좋사오니… 한 걸음 더 나아가\n"
        "국인중을 발탁하여 가신단에 편입할 토대를 마련하시지요"
    ),
    "15:535:0": "의",
    "15:535:1": (
        "에 대한 회유를 마무리하시옵소서\n"
        "국인중은 언젠가 우리 가문에 편입해야 할 이들\n"
        "이번 회유로 그 준비를 갖추시지요"
    ),
    "15:536:0": "의",
    "15:536:1": (
        "에 대한 회유도 최종 단계이옵니다\n"
        "지금은 잘 협력하고 있으나… 아직은 독립된 국인중일 뿐\n"
        "장차 편입할 때를 내다보고 지금 한 번 더 다가가시지요"
    ),
    "15:537:0": "의",
    "15:537:1": (
        "와(과) 우리 가문의 관계는 더없이 좋사옵니다\n"
        "그러나 완전히 따르게 하려면 한 걸음 더 필요하옵니다\n"
        "이번 회유로 그들을 복종시킬 수도 있을 것이옵니다"
    ),
    "15:538:0": "의",
    "15:538:1": (
        "와(과) 사이가 좋기는 하나\n"
        "완전히 복종시키려면 한 번 더 마음을 얻어야 하옵니다\n"
        "금품을 더 보내 환심을 사시지요"
    ),
    "15:539:0": "의",
    "15:539:1": (
        "와(과) 우리 가문의 관계는 좋사옵니다\n"
        "그러나 완전하다고는 할 수 없사오니\n"
        "회유를 더 진척시켜야 할 듯하옵니다"
    ),
    "15:540:0": "의",
    "15:540:1": (
        "와(과) 우호 관계에 있다\n"
        "하지만 그들을 복종시키기에는 아직 부족하다\n"
        "회유책을 더 펼쳐야 한다"
    ),
    "15:541:0": "의",
    "15:541:1": (
        "와(과) 우리 가문의 관계는 좋사옵니다\n"
        "한 걸음만 더 나아가면\n"
        "우리 가문에 편입하는 것도 가능할 것이옵니다"
    ),
}
RECORD_ARITIES = {531: 3, **{record_id: 2 for record_id in range(532, 542)}}
EXPECTED_BASE_GAPS = {
    531: ("029632", "028c32", "014307000000", "050505"),
    **{record_id: ("029632", "028c32", "050505") for record_id in range(532, 542)},
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_EN_ARITIES = {record_id: 1 for record_id in RECORD_ARITIES}
EXPECTED_PK_EN_GAPS = {record_id: ("", "050505") for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:534:1", "15:536:1"}
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_kokujin_final_conciliation_"
    "subordination_and_household_integration_preparation_fragments_with_exact_"
    "uniform_plus_7_pk_jp_sc_tc_arrays_pk_en_sc_tc_auxiliary_context_current_"
    "pc_line_token_gap_boundaries_preserved_historical_kokujin_household_"
    "integration_stage_heartfelt_submission_person_voice_and_dynamic_particles_"
    "verified_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    possessive_source = COMMON.source_literals(source_records, 512)[0]
    if possessive_source != "の":
        raise RuntimeError("segment 826 possessive exact-source anchor drifted")
    for record_id in range(519, 542):
        if COMMON.source_literals(source_records, record_id)[0] != possessive_source:
            raise RuntimeError(
                f"segment 826 cross-boundary possessive source drifted: {record_id}"
            )
    for record_id in RECORD_ARITIES:
        if raw_translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(f"segment 826 possessive raw reuse drifted: {record_id}")
        if translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(f"segment 826 possessive particle drifted: {record_id}")

    particle_expectations = {
        "15:531:1": "에 대한 ",
        "15:531:2": "께 ",
        "15:532:1": "에 대한 ",
        "15:533:1": "에 대한 ",
        "15:534:1": "에 대한 ",
        "15:535:1": "에 대한 ",
        "15:536:1": "에 대한 ",
        "15:537:1": "와(과) ",
        "15:538:1": "와(과) ",
        "15:539:1": "와(과) ",
        "15:540:1": "와(과) ",
        "15:541:1": "와(과) ",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(f"segment 826 dynamic name particle drifted: {coordinate}")

    joined = "\n".join(translations.values())
    for required in (
        "국인중",
        "회유",
        "진심으로 복종",
        "우리 가문의 가신",
        "편입 제안",
        "발탁하여 가신단에 편입",
        "우리 가문에 편입",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 826 final-integration terminology drifted: {required}")
    if any(term in joined for term in ("호족", "길들이", "심복", "당가", "거두어들")):
        raise RuntimeError("segment 826 retained forbidden legacy terminology")


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
        raise RuntimeError("segment 826 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S826",
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
