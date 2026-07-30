#!/usr/bin/env python3
"""Build Base authoring segment 845 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S845.private.v1.jsonl"
SEGMENT = 845
RAW_TRANSLATIONS: dict[str, str] = {
    "15:808:0": "을(를) 비롯한 총",
    "15:808:1": "개 성에서",
    "15:808:2": "에 성공",
    "15:809:0": "이(가)",
    "15:809:1": "에서 벌인",
    "15:809:2": "에 실패",
    "15:810:0": "에서 벌인",
    "15:810:1": "에 실패하여,",
    "15:810:2": "이(가) 부상",
    "15:811:0": "에서",
    "15:811:1": "이(가) 벌인",
    "15:811:2": "을(를) 저지",
    "15:812:0": "에서 잇키 선동에 성공하여",
    "15:812:1": "!\n진압에는 얼마간의 시간이 걸리",
    "15:812:2": "\n잇키에 호응하여 출진해 보는 것도",
    "15:812:3": "까 하옵니다",
    "15:813:0": "에서 잇키 선동에 성공하여",
    "15:813:1": (
        "!\n"
        "잇키는 규모가 커 인근 성까지 번진 듯하옵니다\n"
        "진압에는 상당한 시간이 걸리"
    ),
    "15:814:0": "잇키 선동을 시도한 성은 총",
    "15:814:1": "곳이며,\n",
    "15:814:2": "을(를) 비롯해 총",
    "15:814:3": "곳에서 성공하여",
    "15:814:4": "!\n진압에는 상당한 시간이 걸리",
}
RECORD_ARITIES = {
    808: 3,
    809: 3,
    810: 3,
    811: 3,
    812: 4,
    813: 2,
    814: 5,
}
EXPECTED_BASE_GAPS = {
    808: ("026432", "0232", "023c", "050505"),
    809: ("024633", "026432", "023c", "050505"),
    810: ("026432", "023c", "024633", "050505"),
    811: ("026432", "025032", "023c", "050505"),
    812: (
        "026432",
        "014314020000",
        "01435a040000",
        "01430c040000",
        "050505",
    ),
    813: ("026432", "014314020000", "01435a040000050505"),
    814: (
        "",
        "0233",
        "026432",
        "0232",
        "014314020000",
        "01435a040000050505",
    ),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    812: (
        "026432",
        "01431a020000",
        "014366040000",
        "014318040000",
        "050505",
    ),
    813: ("026432", "01431a020000", "014366040000050505"),
    814: (
        "",
        "0233",
        "026432",
        "0232",
        "01431a020000",
        "014366040000050505",
    ),
}
EXPECTED_PK_EN_ARITIES = {
    808: 4,
    809: 3,
    810: 4,
    811: 4,
    812: 2,
    813: 2,
    814: 4,
}
EXPECTED_PK_EN_GAPS = {
    808: ("", "023c", "0232", "026432", "050505"),
    809: ("024633", "023c", "026432", "050505"),
    810: ("", "023c", "026432", "024633", "050505"),
    811: ("", "025032", "023c", "026432", "050505"),
    812: ("", "026432", "050505"),
    813: ("", "026432", "050505"),
    814: ("", "0233", "0232", "026432", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
BASIS = (
    "pristine_base_pc_jp_authoritative_ikki_incitation_success_failure_"
    "multi_castle_count_agent_faction_plot_and_ui_fragments_with_exact_"
    "base_to_pk_plus_7_jp_sc_tc_mapping_pk_en_sc_tc_auxiliary_context_"
    "current_pc_line_token_gap_outer_whitespace_and_switch_stem_boundaries_"
    "preserved_safe_dynamic_particles_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    expected_jp = {
        808: ("ら", "城の", "に成功"),
        809: ("が", "の", "に失敗"),
        810: ("の", "に失敗し、", "が負傷"),
        811: ("にて", "からの", "を阻止"),
        812: (
            "にて一揆の煽動に成功し",
            "！\n鎮圧にはいくばくかの時がかか",
            "\n一揆に呼応して出陣してみても",
            "かと",
        ),
        813: (
            "にて一揆の煽動に成功し",
            "！\n一揆は大規模で周辺の城にも広がった様子\n鎮圧にはかなりの時がかか",
        ),
        814: (
            "一揆の煽動をしかけた",
            "城のうち、\n",
            "ら",
            "城にて成功し",
            "！\n鎮圧にはかなりの時がかか",
        ),
    }
    for record_id, expected in expected_jp.items():
        if COMMON.source_literals(source_records, record_id) != expected:
            raise RuntimeError(f"segment 845 authoritative Base JP drifted: {record_id}")

    exact_expectations = {
        "15:808:0": "을(를) 비롯한 총",
        "15:808:1": "개 성에서",
        "15:809:0": "이(가)",
        "15:809:1": "에서 벌인",
        "15:810:0": "에서 벌인",
        "15:810:2": "이(가) 부상",
        "15:811:1": "이(가) 벌인",
        "15:811:2": "을(를) 저지",
        "15:812:3": "까 하옵니다",
        "15:814:0": "잇키 선동을 시도한 성은 총",
        "15:814:1": "곳이며,\n",
        "15:814:2": "을(를) 비롯해 총",
        "15:814:3": "곳에서 성공하여",
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(f"segment 845 token role/particle drifted: {coordinate}")

    if not (
        translations["15:812:0"].startswith("에서 ")
        and translations["15:813:0"].startswith("에서 ")
        and translations["15:814:2"].startswith("을(를) ")
    ):
        raise RuntimeError("segment 845 castle/operation assembly drifted")
    joined = "\n".join(translations.values())
    for required in ("잇키 선동", "진압", "출진", "저지", "부상"):
        if required not in joined:
            raise RuntimeError(f"segment 845 terminology drifted: {required}")
    if any(term in joined for term in ("폭동", "반란 선동", "첩자")):
        raise RuntimeError("segment 845 retained forbidden terminology")


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
        raise RuntimeError("segment 845 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S845",
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
