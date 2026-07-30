#!/usr/bin/env python3
"""Build Base authoring segment 887 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment881 as CAPTURE_S881
import build_base_batch001_segment882 as CAPTURE_S882
import build_base_batch001_segment884 as COMMON
import build_base_batch001_segment857 as DAMAGE_S857


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S887.private.v1.jsonl"
)
SEGMENT = 887
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1356:0": "·",
    "15:1356:1": "의 몸 상태가 회복",
    "15:1357:0": "이(가)",
    "15:1357:1": "의",
    "15:1357:2": "에 성공",
    "15:1358:0": "에서 벌인",
    "15:1358:1": "에 실패하여,",
    "15:1358:2": "이(가) 부상",
    "15:1359:0": "에서 벌인",
    "15:1359:1": "에 실패",
    "15:1360:0": "이(가)",
    "15:1360:1": "의",
    "15:1360:2": "으로 피해 발생",
    "15:1361:0": "의 성주",
    "15:1361:1": "이(가) 부상",
    "15:1362:0": CAPTURE_S882.RAW_TRANSLATIONS["15:1286:0"],
    "15:1362:1": CAPTURE_S882.RAW_TRANSLATIONS["15:1286:1"],
    "15:1362:2": CAPTURE_S882.RAW_TRANSLATIONS["15:1286:2"],
    "15:1363:0": "성주·",
    "15:1363:1": "님께서\n",
    "15:1363:2": "의 간자에게",
    "15:1363:3": "을(를) 받아\n부상했습니다!",
}
RECORD_ARITIES = {
    1356: 2,
    1357: 3,
    1358: 3,
    1359: 2,
    1360: 3,
    1361: 2,
    1362: 3,
    1363: 4,
}
EXPECTED_BASE_JP = {
    1356: ("・", "の体調が回復"),
    1357: ("が", "の", "に成功"),
    1358: ("の", "に失敗し、", "が負傷"),
    1359: ("の", "に失敗"),
    1360: ("が", "の", "により、損害が発生"),
    1361: ("の城主", "が負傷"),
    1362: ("にて", "からの", "を阻止"),
    1363: ("城主・", "様が\n", "の間者に", "を受け\n負傷しました！"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1356: ("", "024633", "050505"),
    1357: ("024633", "026432", "023C", "050505"),
    1358: ("026432", "023C", "024633", "050505"),
    1359: ("026432", "023C", "050505"),
    1360: ("026432", "025032", "023C", "050505"),
    1361: ("026432", "024833", "050505"),
    1362: ("026432", "025032", "023C", "050505"),
    1363: ("026432", "024833", "025032", "023C", "050505"),
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {
    **{record_id: record_id + 10 for record_id in range(1356, 1362)},
    **{record_id: record_id + 14 for record_id in range(1362, 1364)},
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1357): (
        ("对", "的", "成功。"),
        ("024633", "026432", "023C", "050505"),
    ),
    ("TC", 1357): (
        ("對", "的", "成功。"),
        ("024633", "026432", "023C", "050505"),
    ),
    ("SC", 1358): (
        ("的", "失败，", "负伤。"),
        ("026432", "023C", "024633", "050505"),
    ),
    ("TC", 1358): (
        ("對", "的", "失敗，", "負傷。"),
        ("", "026432", "023C", "024633", "050505"),
    ),
    ("SC", 1359): (
        ("对", "的", "失败。"),
        ("", "026432", "023C", "050505"),
    ),
    ("TC", 1359): (
        ("對", "的", "失敗。"),
        ("", "026432", "023C", "050505"),
    ),
    ("SC", 1360): (
        ("因", "的", "，受到损伤。"),
        ("026432", "025032", "023C", "050505"),
    ),
    ("TC", 1360): (
        ("因", "的", "發生損害。"),
        ("026432", "025032", "023C", "050505"),
    ),
    ("SC", 1361): (
        ("的城主", "负伤。"),
        ("026432", "024833", "050505"),
    ),
    ("TC", 1361): (
        ("城主", "負傷。"),
        ("026432", "024833", "050505"),
    ),
    ("SC", 1362): (
        ("于", "阻止", "的", "。"),
        ("", "026432", "025032", "023C", "050505"),
    ),
    ("TC", 1362): (
        ("於", "阻止", "的", "。"),
        ("", "026432", "025032", "023C", "050505"),
    ),
    ("SC", 1363): (
        ("因为", "的手下受到了", "，\n", "的城主", "负伤了。"),
        ("", "025032", "023C", "026432", "024833", "050505"),
    ),
    ("TC", 1363): (
        ("在", "人馬的", "下，\n", "城主", "負傷。"),
        ("", "025032", "023C", "026432", "024833", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1357: (
        (" successfully completed the ", " of ", "."),
        ("024633", "023C", "026432", "050505"),
    ),
    1358: (
        ("The ", " of ", " was a failure. ", " was injured."),
        ("", "023C", "026432", "024633", "050505"),
    ),
    1359: (
        ("The ", " of ", " was a failure."),
        ("", "023C", "026432", "050505"),
    ),
    1360: (
        (" was damaged by the ", "Ös ", "."),
        ("026432", "025032", "023C", "050505"),
    ),
    1361: (
        ("The lord of ", ", ", ", was injured."),
        ("", "026432", "024833", "050505"),
    ),
    1362: (
        ("The ", "Ös ", " at ", " was prevented."),
        ("", "025032", "023C", "026432", "050505"),
    ),
    1363: (
        ("Ös lord, ", ", was injured by the ", " from the ", " spy!"),
        ("026432", "024833", "023C", "025032", "050505"),
    ),
}
AUXILIARY_OVERRIDES = CAPTURE_S881.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B107_pristine_base_pc_jp_authoritative_"
    "operation_success_failure_damage_injury_spy_attack_and_prevention_"
    "reports_with_explicit_nonuniform_plus_10_plus_14_base_to_pk_mapping_"
    "exact_base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_B106_"
    "prevention_canonical_and_B104_S857_damage_result_canonical_reused_"
    "dynamic_person_castle_house_action_tokens_current_layout_opcode_"
    "skeleton_runtime_fragment_pending"
)


def source_literals(
    source_records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, record_id)])
    )


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if 1364 in RECORD_ARITIES or any(
        coordinate.startswith("15:1364:") for coordinate in raw_translations
    ):
        raise RuntimeError("segment 887 crossed the excluded Base record 1364")
    if PK_RECORD_MAP != {
        1356: 1366,
        1357: 1367,
        1358: 1368,
        1359: 1369,
        1360: 1370,
        1361: 1371,
        1362: 1376,
        1363: 1377,
    }:
        raise RuntimeError("segment 887 explicit Base-to-PK insertion map drifted")
    for literal_id in range(3):
        coordinate = f"15:1362:{literal_id}"
        canonical = CAPTURE_S882.RAW_TRANSLATIONS[f"15:1286:{literal_id}"]
        if raw_translations[coordinate] != canonical:
            raise RuntimeError(
                f"segment 887 B106 prevention canonical drifted: {coordinate}"
            )
    if source_literals(source_records, 1362) != CAPTURE_S882.EXPECTED_BASE_JP[1286]:
        raise RuntimeError("segment 887 B106 prevention source equivalence drifted")
    if (
        raw_translations["15:1360:0"]
        != DAMAGE_S857.RAW_TRANSLATIONS["15:977:0"]
        or raw_translations["15:1360:1"] != "의"
        or raw_translations["15:1360:2"] != "으로 피해 발생"
        or DAMAGE_S857.RAW_TRANSLATIONS["15:977:1"]
        != "의 공작으로 피해 발생"
    ):
        raise RuntimeError(
            "segment 887 B104 S857 damage-result canonical drifted"
        )
    joined = "\n".join(translations.values())
    for required in (
        "몸 상태가 회복",
        "에 성공",
        "에 실패",
        "피해 발생",
        "의 성주",
        "이(가) 벌인",
        "을(를) 저지",
        "의 간자에게",
        "부상했습니다!",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 887 meaning or terminology drifted: {required}")
    if "첩자" in joined:
        raise RuntimeError("segment 887 間者 terminology regressed from 간자")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_record_map=PK_RECORD_MAP,
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
        raise RuntimeError("segment 887 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S887",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offsets": [10, 14],
                "excluded_base_record_1364": True,
                "b106_prevention_canonical_reused": True,
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
