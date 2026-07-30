#!/usr/bin/env python3
"""Build Base authoring segment 835 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S835.private.v1.jsonl"
SEGMENT = 835
RAW_TRANSLATIONS: dict[str, str] = {
    "15:660:0": "우리와",
    "15:660:1": (
        "은(는)\n"
        "이제 한배를 탄 사이\n"
        "속히 휘하에 들여야 할 듯하옵니다"
    ),
    "15:661:0": "우리 가문과",
    "15:661:1": (
        "\n서로의 이해관계가 일치하옵니다\n"
        "차라리 가신으로 맞아들이시지요"
    ),
    "15:662:0": (
        "의 분들을 가신단에 편입하시지요\n"
        "가신단에서 우리와 어깨를 나란히 하기를\n"
        "그들도 바라고 있을 것입니다"
    ),
    "15:663:0": (
        "을(를) 편입하심이 어떻겠습니까\n"
        "국인중으로서 잘 협력해 주었으나\n"
        "이 힘은 역시 주군의 지휘 아래에서라야 빛날 것이옵니다"
    ),
    "15:664:0": (
        "을(를) 편입하시지요\n"
        "협력적이라 해도 국인중임은 틀림없으니\n"
        "영내에 이질적인 세력을 남기지 않는 편이 좋을 듯하옵니다"
    ),
    "15:665:0": (
        "의 분들을 가신단에 편입하시지요\n"
        "가신단에서 우리와 어깨를 나란히 하기를\n"
        "그들도 바라고 있을 것입니다"
    ),
    "15:666:0": (
        "을(를) 편입하심이 어떻겠습니까\n"
        "국인중으로서 잘 협력해 주었으나\n"
        "이 힘은 역시 주군의 지휘 아래에서라야 빛날 것이옵니다"
    ),
    "15:667:0": (
        "의 분들을 가신으로\n"
        "맞이하는 것이 어떻겠습니까?\n"
        "이제 한 식구나 다름없는 사이이니까요"
    ),
    "15:668:0": "이제는",
    "15:668:1": (
        "의 사람들을\n"
        "휘하에 들일 때가 되었으리라\n"
        "그들도 이를 바랄 터"
    ),
    "15:669:0": (
        "의 분들을 가신으로\n"
        "맞이하는 것이 어떻겠습니까?\n"
        "그들에게도 나쁘지 않은 제안일 듯합니다…"
    ),
    "15:670:0": (
        "을(를) 휘하에 들이시지요\n"
        "그편이 부리기에도 수월할 듯하옵니다"
    ),
    "15:671:0": COMMON.RAW_TRANSLATIONS["15:635:0"],
    "15:672:0": "우리와",
    "15:672:1": (
        "은(는)\n"
        "이제 한배를 탄 사이\n"
        "속히 휘하에 들여야 할 듯하옵니다"
    ),
    "15:673:0": "우리 가문과",
    "15:673:1": (
        "\n서로의 이해관계가 일치하옵니다\n"
        "차라리 가신으로 맞아들이시지요"
    ),
    "15:674:0": (
        "의 분들을 가신단에 편입하시지요\n"
        "가신단에서 우리와 어깨를 나란히 하기를\n"
        "그들도 바라고 있을 것입니다"
    ),
    "15:675:0": (
        "을(를) 편입하심이 어떻겠습니까\n"
        "국인중으로서 잘 협력해 주었으나\n"
        "이 힘은 역시 주군의 지휘 아래에서라야 빛날 것이옵니다"
    ),
    "15:676:0": (
        "을(를) 편입하시지요\n"
        "협력적이라 해도 국인중임은 틀림없으니\n"
        "영내에 이질적인 세력을 남기지 않는 편이 좋을 듯하옵니다"
    ),
}
RECORD_ARITIES = {
    660: 2,
    661: 2,
    662: 1,
    663: 1,
    664: 1,
    665: 1,
    666: 1,
    667: 1,
    668: 2,
    669: 1,
    670: 1,
    671: 1,
    672: 2,
    673: 2,
    674: 1,
    675: 1,
    676: 1,
}
EXPECTED_BASE_GAPS = {
    660: ("", "028c32", "050505"),
    661: ("", "028c32", "050505"),
    668: ("", "028c32", "050505"),
    672: ("", "028c32", "050505"),
    673: ("", "028c32", "050505"),
    **{
        record_id: ("028c32", "050505")
        for record_id in RECORD_ARITIES
        if record_id not in {660, 661, 668, 672, 673}
    },
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_EN_TWO_LITERAL_RECORDS = {661, 662, 663, 667, 673, 674, 675}
EXPECTED_PK_EN_ARITIES = {
    record_id: 2 if record_id in PK_EN_TWO_LITERAL_RECORDS else 1
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_EN_GAPS = {
    record_id: (
        ("", "028c32", "050505")
        if record_id in PK_EN_TWO_LITERAL_RECORDS
        else ("", "050505")
    )
    for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {"15:669:0"}
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_kokujin_household_integration_"
    "proposal_stage_with_exact_repeated_source_groups_and_uniform_plus_7_pk_"
    "jp_sc_tc_arrays_pk_en_sc_tc_auxiliary_context_current_pc_line_token_gap_"
    "boundaries_preserved_historical_register_person_voice_dynamic_particles_"
    "and_cross_segment_canonical_reuse_verified_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    source_literals = COMMON.COMMON.source_literals
    exact_source_groups = (
        (635, 659, 671),
        (660, 672),
        (661, 673),
        (662, 665, 674, 677),
        (663, 666, 675, 678),
        (664, 676),
        (667, 679),
        (668, 680),
        (669, 681),
        (670, 682),
    )
    for group in exact_source_groups:
        if len({source_literals(source_records, record_id) for record_id in group}) != 1:
            raise RuntimeError(f"segment 835 exact source group drifted: {group}")

    if source_literals(source_records, 636) == source_literals(source_records, 660):
        raise RuntimeError("segment 835 636/660 운명공동체/일련탁생 distinction collapsed")
    if source_literals(source_records, 637) == source_literals(source_records, 661):
        raise RuntimeError("segment 835 637/661 refusal-risk/direct-acceptance distinction collapsed")
    if source_literals(source_records, 644) == source_literals(source_records, 668):
        raise RuntimeError("segment 835 644/668 resistance/willingness distinction collapsed")

    exact_translation_groups = (
        ("15:660:0", "15:672:0"),
        ("15:660:1", "15:672:1"),
        ("15:661:0", "15:673:0"),
        ("15:661:1", "15:673:1"),
        ("15:662:0", "15:665:0", "15:674:0"),
        ("15:663:0", "15:666:0", "15:675:0"),
        ("15:664:0", "15:676:0"),
    )
    for group in exact_translation_groups:
        if len({raw_translations[coordinate] for coordinate in group}) != 1:
            raise RuntimeError(f"segment 835 exact translation reuse drifted: {group}")
    if raw_translations["15:671:0"] != COMMON.RAW_TRANSLATIONS["15:635:0"]:
        raise RuntimeError("segment 835 15:671 cross-segment translation reuse drifted")

    cross_segment_canonicals = {
        "15:667:0": (
            "의 분들을 가신으로\n"
            "맞이하는 것이 어떻겠습니까?\n"
            "이제 한 식구나 다름없는 사이이니까요"
        ),
        "15:668:0": "이제는",
        "15:668:1": (
            "의 사람들을\n"
            "휘하에 들일 때가 되었으리라\n"
            "그들도 이를 바랄 터"
        ),
        "15:669:0": (
            "의 분들을 가신으로\n"
            "맞이하는 것이 어떻겠습니까?\n"
            "그들에게도 나쁘지 않은 제안일 듯합니다…"
        ),
        "15:670:0": (
            "을(를) 휘하에 들이시지요\n"
            "그편이 부리기에도 수월할 듯하옵니다"
        ),
    }
    for coordinate, expected in cross_segment_canonicals.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(f"segment 835 cross-segment canonical drifted: {coordinate}")

    particle_expectations = {
        "15:660:1": "은(는)\n",
        "15:661:1": "\n서로의 ",
        "15:662:0": "의 ",
        "15:663:0": "을(를) ",
        "15:664:0": "을(를) ",
        "15:665:0": "의 ",
        "15:666:0": "을(를) ",
        "15:667:0": "의 ",
        "15:668:1": "의 ",
        "15:669:0": "의 ",
        "15:670:0": "을(를) ",
        "15:671:0": "의 ",
        "15:672:1": "은(는)\n",
        "15:673:1": "\n서로의 ",
        "15:674:0": "의 ",
        "15:675:0": "을(를) ",
        "15:676:0": "을(를) ",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(f"segment 835 dynamic name particle drifted: {coordinate}")

    joined = "\n".join(translations.values())
    for required in ("국인중", "휘하", "가신", "가신단", "편입"):
        if required not in joined:
            raise RuntimeError(f"segment 835 stage/terminology drifted: {required}")
    if any(term in joined for term in ("호족", "산하", "당가", "가신화", "거두어들")):
        raise RuntimeError("segment 835 retained forbidden legacy terminology")


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
        raise RuntimeError("segment 835 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S835",
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
