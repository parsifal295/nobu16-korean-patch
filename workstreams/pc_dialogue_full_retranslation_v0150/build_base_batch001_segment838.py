#!/usr/bin/env python3
"""Build Base authoring segment 838 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment837 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S838.private.v1.jsonl"
SEGMENT = 838
REPEATED_FAILURE_698_709 = PRIOR.REPEATED_FAILURE_698_709
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:0": REPEATED_FAILURE_698_709
        for record_id in range(699, 710)
    },
    "15:710:0": "·",
    "15:710:1": "의 편입으로",
    "15:710:2": "을(를) 지배\n·",
    "15:710:3": "을(를) 등용",
    "15:711:0": "·",
    "15:711:1": "의 편입으로",
    "15:711:2": "을(를) 지배",
    "15:712:0": "·",
    "15:712:1": "의 편입에 실패",
    "15:713:0": "이(가)",
    "15:713:1": "의 편입에 성공",
    "15:714:0": "을(를) 비롯한 총",
    "15:714:1": "명을 등용",
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(699, 710)},
    710: 4,
    711: 3,
    712: 2,
    713: 2,
    714: 2,
}
REPEATED_FAILURE_JP = (
    "の取込は失敗しました\nいましばらく様子を見るといたしましょう",
)
EXPECTED_JP = {
    **{record_id: REPEATED_FAILURE_JP for record_id in range(699, 710)},
    710: ("・", "取込により", "を支配\n・", "を登用"),
    711: ("・", "取込により", "を支配"),
    712: ("・", "の取込に失敗"),
    713: ("が", "の取込に成功"),
    714: ("ら", "名を登用"),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("028c32", "050505") for record_id in range(699, 710)},
    710: ("", "023c", "029632", "024633", "050505"),
    711: ("", "023c", "029632", "050505"),
    712: ("", "028c32", "050505"),
    713: ("024633", "028c32", "050505"),
    714: ("024633", "0232", "050505"),
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
SC_AUXILIARY = {
    713: (
        ("成功拉拢了", "。"),
        ("024633", "028c32", "050505"),
    ),
    714: (
        ("登用了", "等", "人。"),
        ("", "024633", "0232", "050505"),
    ),
}
TC_AUXILIARY = {
    713: (
        ("對", "籠絡成功。"),
        ("024633", "028c32", "050505"),
    ),
    714: (
        ("登庸", "等", "人。"),
        ("", "024633", "0232", "050505"),
    ),
}
EN_AUXILIARY = {
    713: (
        (" has assimilated the ", "."),
        ("024633", "028c32", "050505"),
    ),
    714: (
        (" of ", "Ös people have been employed."),
        ("0232", "024633", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): value
        for side in ("base", "pk")
        for record_id, value in SC_AUXILIARY.items()
    },
    **{
        (side, "TC", record_id): value
        for side in ("base", "pk")
        for record_id, value in TC_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
BASIS = (
    "pristine_base_pc_jp_authoritative_kunishu_incorporation_failure_and_"
    "result_summary_fragments_with_exact_uniform_plus_7_pk_jp_sc_tc_mapping_"
    "pk_en_auxiliary_context_dynamic_actor_kunishu_territory_officer_and_"
    "count_tokens_historical_terminology_current_pc_layout_and_opcode_"
    "skeleton_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if len(
        {
            COMMON.source_literals(source_records, record_id)
            for record_id in range(698, 710)
        }
    ) != 1:
        raise RuntimeError("segment 838 698-709 repeated failure source drifted")
    for record_id in range(699, 710):
        if raw_translations[f"15:{record_id}:0"] != REPEATED_FAILURE_698_709:
            raise RuntimeError(
                f"segment 838 699-709 repeated failure translation drifted: {record_id}"
            )
    if COMMON.source_literals(source_records, 710)[1] != COMMON.source_literals(
        source_records, 711
    )[1]:
        raise RuntimeError("segment 838 710/711 exact incorporation source drifted")
    if raw_translations["15:710:1"] != raw_translations["15:711:1"]:
        raise RuntimeError("segment 838 710/711 exact incorporation translation drifted")

    for record_id in (710, 711, 712):
        if translations[f"15:{record_id}:0"] != "·":
            raise RuntimeError(
                f"segment 838 result bullet marker drifted: {record_id}"
            )
    if translations["15:710:1"] != "의 편입으로":
        raise RuntimeError("segment 838 incorporation result terminology drifted")
    if not translations["15:710:2"].startswith("을(를) 지배"):
        raise RuntimeError("segment 838 territory token object particle drifted")
    if not translations["15:710:3"].startswith("을(를) 등용"):
        raise RuntimeError("segment 838 officer token object particle drifted")
    if translations["15:713:0"] != "이(가)":
        raise RuntimeError("segment 838 actor subject particle drifted")
    if not translations["15:713:1"].startswith("의 편입에 성공"):
        raise RuntimeError("segment 838 kunishu incorporation success drifted")
    if not translations["15:714:0"].startswith("을(를) 비롯한 총"):
        raise RuntimeError("segment 838 employed-person token boundary drifted")
    if translations["15:714:1"] != "명을 등용":
        raise RuntimeError("segment 838 employed-count boundary drifted")

    joined = "\n".join(translations.values())
    for required in ("편입", "지배", "등용"):
        if required not in joined:
            raise RuntimeError(
                f"segment 838 result terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("호족", "당가", "참진", "심복", "포섭", "거두어들")
    ):
        raise RuntimeError("segment 838 retains forbidden legacy terminology")


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
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 838 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S838",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
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
