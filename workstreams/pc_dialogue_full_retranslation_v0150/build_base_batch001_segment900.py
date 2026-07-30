#!/usr/bin/env python3
"""Build Base authoring segment 900 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment888 as CANONICAL_B107
import build_base_batch001_segment884 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S900.private.v1.jsonl"
)
SEGMENT = 900
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1444:0": CANONICAL_B107.RAW_TRANSLATIONS["15:1365:0"],
    "15:1444:2": CANONICAL_B107.RAW_TRANSLATIONS["15:1365:2"],
    "15:1444:3": CANONICAL_B107.RAW_TRANSLATIONS["15:1365:3"],
    "15:1445:0": "이(가)",
    "15:1445:1": "에 대한",
    "15:1445:2": "에 성공",
    "15:1446:0": "이(가)",
    "15:1446:1": "을(를) 비롯한",
    "15:1446:2": "개 성의",
    "15:1446:3": "에 성공",
    "15:1447:0": "에 대한",
    "15:1447:1": "에 실패하여,",
    "15:1447:2": "이(가) 부상",
    "15:1448:0": "에 대한",
    "15:1448:1": "에 실패",
    "15:1449:0": "을(를) 비롯한",
    "15:1449:1": "개 성의",
    "15:1449:2": "에 실패",
    "15:1450:0": "의",
    "15:1450:1": "으로 인해,",
    "15:1450:2": "에 피해가 발생",
    "15:1451:0": "의",
    "15:1451:1": "으로 인해,",
    "15:1451:2": "을(를) 비롯한",
    "15:1451:3": "개 성에 피해가 발생",
}
RECORD_ARITIES = {
    1444: 4,
    1445: 3,
    1446: 4,
    1447: 3,
    1448: 2,
    1449: 3,
    1450: 3,
    1451: 4,
}
EXPECTED_BASE_JP = {
    1444: (
        "にて間者を捕らえ",
        "\n",
        "による",
        "が密命とか…\n危ないところ",
    ),
    1445: ("が", "の", "に成功"),
    1446: ("が", "ら", "城の", "に成功"),
    1447: ("の", "に失敗し、", "が負傷"),
    1448: ("の", "に失敗"),
    1449: ("ら", "城の", "に失敗"),
    1450: ("の", "により、", "に損害が発生"),
    1451: ("の", "により、", "ら", "城に損害が発生"),
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    1444: (
        "026432",
        "014314020000",
        "025032",
        "023c",
        "014344020000050505",
    ),
    1445: ("024633", "026432", "023c", "050505"),
    1446: ("024633", "026432", "0232", "023c", "050505"),
    1447: ("026432", "023c", "024633", "050505"),
    1448: ("026432", "023c", "050505"),
    1449: ("026432", "0232", "023c", "050505"),
    1450: ("025032", "023c", "026432", "050505"),
    1451: ("025032", "023c", "026432", "0232", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1444: (
        "026432",
        "01431a020000",
        "025032",
        "023c",
        "014350020000050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1444:3"}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1444:1": "\n"}

SHARED_AUXILIARY = {
    ("SC", 1444): (
        ("已于", "逮捕间谍。\n据说是", "的", "发出密令……\n差点就没命了。"),
        ("", "026432", "025032", "023c", "050505"),
    ),
    ("TC", 1444): (
        ("已於", "逮捕間諜。\n據說是", "的", "發出密令……\n差點就沒命了。"),
        ("", "026432", "025032", "023c", "050505"),
    ),
    ("SC", 1445): (
        ("对", "的", "成功。"),
        ("024633", "026432", "023c", "050505"),
    ),
    ("TC", 1445): (
        ("對", "的", "成功。"),
        ("024633", "026432", "023c", "050505"),
    ),
    ("SC", 1446): (
        ("成功向", "等", "城", "。"),
        ("024633", "026432", "0232", "023c", "050505"),
    ),
    ("TC", 1446): (
        ("向", "等", "城進行的", "成功。"),
        ("024633", "026432", "0232", "023c", "050505"),
    ),
    ("SC", 1447): (
        ("的", "失败，", "负伤。"),
        ("026432", "023c", "024633", "050505"),
    ),
    ("TC", 1447): (
        ("對", "的", "失敗，", "負傷。"),
        ("", "026432", "023c", "024633", "050505"),
    ),
    ("SC", 1448): (
        ("的", "失败。"),
        ("026432", "023c", "050505"),
    ),
    ("TC", 1448): (
        (" ", "失敗。"),
        ("026432", "023c", "050505"),
    ),
    ("SC", 1449): (
        ("对", "等", "城的", "失败。"),
        ("", "026432", "0232", "023c", "050505"),
    ),
    ("TC", 1449): (
        ("於", "等", "城的", "失敗。"),
        ("", "026432", "0232", "023c", "050505"),
    ),
    ("SC", 1450): (
        ("因", "的", "，受到损伤。"),
        ("026432", "025032", "023c", "050505"),
    ),
    ("TC", 1450): (
        ("因", "的", "發生損害。"),
        ("026432", "025032", "023c", "050505"),
    ),
    ("SC", 1451): (
        ("等", "城因", "的", "而受损。"),
        ("026432", "0232", "025032", "023c", "050505"),
    ),
    ("TC", 1451): (
        ("等", "城因", "的", "發生損害。"),
        ("026432", "0232", "025032", "023c", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1444: (
        (
            "WeÖve captured spies in ",
            ". They had the ",
            "Ös ",
            " secret orders... That could have been bad.",
        ),
        ("", "026432", "025032", "023c", "050505"),
    ),
    1445: (
        (" successfully completed the ", " of ", "."),
        ("024633", "023c", "026432", "050505"),
    ),
    1446: (
        (
            " successfully completed the ",
            " of ",
            " castle(s), including ",
            ".",
        ),
        ("024633", "023c", "0232", "026432", "050505"),
    ),
    1447: (
        ("The ", " of ", " was a failure. ", " was injured."),
        ("", "023c", "026432", "024633", "050505"),
    ),
    1448: (
        ("The ", " of ", " was a failure."),
        ("", "023c", "026432", "050505"),
    ),
    1449: (
        (
            "The ",
            " of ",
            " castle(s), including ",
            ", was a failure.",
        ),
        ("", "023c", "0232", "026432", "050505"),
    ),
    1450: (
        (" was damaged by the ", "Ös ", "."),
        ("026432", "025032", "023c", "050505"),
    ),
    1451: (
        (
            " castle(s), including ",
            ", were damaged by the ",
            "Ös ",
            ".",
        ),
        ("0232", "026432", "025032", "023c", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): expected
        for (language, record_id), expected in SHARED_AUXILIARY.items()
        for side in ("base", "pk")
    },
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "spy_capture_operation_success_failure_injury_and_single_plural_castle_"
    "damage_ui_with_uniform_plus_15_pk_mapping_base_pk_sc_tc_exact_pk_en_"
    "auxiliary_context_b107_spy_capture_canonical_hidden_lf_preserved_"
    "operation_actor_target_and_attacker_victim_perspective_ra_plural_"
    "count_relations_current_layout_and_opcode_skeleton_preserved_runtime_"
    "fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    canonical_coordinates = {
        "15:1444:0": "15:1365:0",
        "15:1444:2": "15:1365:2",
        "15:1444:3": "15:1365:3",
    }
    for coordinate, canonical_coordinate in canonical_coordinates.items():
        if raw_translations[coordinate] != (
            CANONICAL_B107.RAW_TRANSLATIONS[canonical_coordinate]
        ):
            raise RuntimeError(
                f"segment 900 B107 spy-capture canonical drifted: "
                f"{coordinate}"
            )
    if EXPECTED_BASE_JP[1444] != CANONICAL_B107.EXPECTED_BASE_JP[1365]:
        raise RuntimeError("segment 900 B107 spy-capture source drifted")
    if (
        raw_translations["15:1444:3"].count("…") != 1
        or translations["15:1444:3"].count("…") != 2
    ):
        raise RuntimeError("segment 900 capture ellipsis seed/pair drifted")
    plural_expectations = {
        "15:1446:1": "을(를) 비롯한",
        "15:1446:2": "개 성의",
        "15:1449:0": "을(를) 비롯한",
        "15:1449:1": "개 성의",
        "15:1451:2": "을(를) 비롯한",
        "15:1451:3": "개 성에 피해가 발생",
    }
    for coordinate, expected in plural_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 900 plural castle relation drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "간자를 붙잡아",
        "에 대한",
        "에 성공",
        "에 실패",
        "이(가) 부상",
        "으로 인해",
        "피해가 발생",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 900 operation-result semantics drifted: {required}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
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
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != len(translations):
        raise RuntimeError("segment 900 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S900",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "hidden_lf_slots_preserved": 1,
                "operation_result_records": 8,
                "explicit_pk_mapping": True,
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
