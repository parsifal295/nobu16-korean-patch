#!/usr/bin/env python3
"""Build Base authoring segment 861 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment860 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S861.private.v1.jsonl"
SEGMENT = 861
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1032:0": "을(를) 편입하여 성, 병력, 가신을 접수할 수 있다",
    "15:1033:0": "실패 시,",
    "15:1033:1": "의 편입이 당분간 불가능",
    "15:1034:0": "·",
    "15:1034:1": "의 편입에 성공하여 영토가 확대",
    "15:1035:0": "·",
    "15:1035:1": "의 편입에 실패",
    "15:1036:0": "이(가)",
    "15:1036:1": "을(를) 편입",
    "15:1037:0": "의 편입에 실패",
    "15:1038:0": "을(를) 비롯한 총",
    "15:1038:1": "명을 등용",
    "15:1039:0": "을(를) 등용",
    "15:1040:0": "을(를) 비롯한 총",
    "15:1040:1": "개 성이 우리 가문의 휘하로",
    "15:1041:0": "이(가) 우리 가문의 휘하로",
    "15:1042:0": "의 금전",
    "15:1042:1": "을(를) 접수",
    "15:1043:0": "의 병량",
    "15:1043:1": "을(를) 접수",
    "15:1044:0": "을(를) 비롯한 가보 총",
    "15:1044:1": "점을 접수",
}
RECORD_ARITIES = {
    1032: 1,
    1033: 2,
    1034: 2,
    1035: 2,
    1036: 2,
    1037: 1,
    1038: 2,
    1039: 1,
    1040: 2,
    1041: 1,
    1042: 2,
    1043: 2,
    1044: 2,
}
EXPECTED_JP = {
    1032: ("を吸収し、城や兵、家臣を接収できる",),
    1033: ("失敗時、", "の吸収が当面不可能"),
    1034: ("・", "の吸収に成功し、領土が拡大"),
    1035: ("・", "の吸収に失敗"),
    1036: ("が", "を吸収"),
    1037: ("の吸収に失敗",),
    1038: ("ら", "名を登用"),
    1039: ("を登用",),
    1040: ("など", "城が当家の傘下に"),
    1041: ("が当家の傘下に",),
    1042: ("の金銭", "を接収"),
    1043: ("の兵糧", "を接収"),
    1044: ("など家宝", "点を接収"),
}
EXPECTED_BASE_GAPS = {
    1032: ("025032", "050505"),
    1033: ("", "025032", "050505"),
    1034: ("", "023c", "050505"),
    1035: ("", "025032", "050505"),
    1036: ("025032", "025132", "050505"),
    1037: ("025132", "050505"),
    1038: ("024633", "0232", "050505"),
    1039: ("024633", "050505"),
    1040: ("026432", "0232", "050505"),
    1041: ("026432", "050505"),
    1042: ("025032", "0232", "050505"),
    1043: ("025032", "0232", "050505"),
    1044: ("028232", "0232", "050505"),
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {record_id: record_id + 7 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
SC_AUXILIARY = {
    1036: (
        ("吸收了", "。"),
        ("025032", "025132", "050505"),
    ),
    1038: (
        ("登用了", "等", "人。"),
        ("", "024633", "0232", "050505"),
    ),
    1039: (
        ("登用了", "。"),
        ("", "024633", "050505"),
    ),
    1040: (
        ("等", "城归属于本家了。"),
        ("026432", "0232", "050505"),
    ),
    1041: (
        ("归属于本家了。",),
        ("026432", "050505"),
    ),
    1042: (
        ("接收了", "的", "金钱。"),
        ("", "025032", "0232", "050505"),
    ),
    1043: (
        ("接收了", "的", "军粮。"),
        ("", "025032", "0232", "050505"),
    ),
    1044: (
        ("接收了", "等", "样家宝。"),
        ("", "028232", "0232", "050505"),
    ),
}
TC_AUXILIARY = {
    1036: (
        ("接收", "。"),
        ("025032", "025132", "050505"),
    ),
    1038: (
        ("登庸", "等", "人。"),
        ("", "024633", "0232", "050505"),
    ),
    1039: (
        ("登庸", "。"),
        ("", "024633", "050505"),
    ),
    1040: (
        ("等", "城入本家旗下。"),
        ("026432", "0232", "050505"),
    ),
    1041: (
        ("入本家旗下。",),
        ("026432", "050505"),
    ),
    1042: (
        ("接收", "的資金", "。"),
        ("", "025032", "0232", "050505"),
    ),
    1043: (
        ("接收", "的軍糧", "。"),
        ("", "025032", "0232", "050505"),
    ),
    1044: (
        ("接收", "等家寶", "件。"),
        ("", "028232", "0232", "050505"),
    ),
}
EN_AUXILIARY = {
    1036: (
        ("The ", " have absorbed the ", "."),
        ("", "025032", "025132", "050505"),
    ),
    1038: (
        (" of ", "Ös people have been employed."),
        ("0232", "024633", "050505"),
    ),
    1039: (
        (" has been employed.",),
        ("024633", "050505"),
    ),
    1040: (
        (" castle(s), including ", ", were brought under your clanÖs banner."),
        ("0232", "026432", "050505"),
    ),
    1041: (
        (" was brought under your clanÖs banner.",),
        ("026432", "050505"),
    ),
    1042: (
        ("Seized ", " of the ", "Ös gold."),
        ("", "0232", "025032", "050505"),
    ),
    1043: (
        ("Seized ", " of the ", "Ös supplies."),
        ("", "0232", "025032", "050505"),
    ),
    1044: (
        ("Seized ", " treasure(s), including ", "."),
        ("", "0232", "028232", "050505"),
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
    "pristine_base_pc_jp_authoritative_incorporation_effect_failure_success_"
    "employment_castle_gold_supplies_and_treasure_receipt_ui_with_explicit_"
    "base_to_pk_record_map_exact_pc_sc_tc_mapping_pk_en_auxiliary_context_"
    "dynamic_force_officer_castle_count_and_treasure_tokens_current_layout_"
    "opcode_skeleton_prior_numeric_canonical_and_isolated_reverse_overlay_"
    "verified_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if raw_translations["15:1038:0"] != "을(를) 비롯한 총":
        raise RuntimeError("segment 861 1038 leading officer/count canonical drifted")
    if raw_translations["15:1038:1"] != "명을 등용":
        raise RuntimeError("segment 861 1038 numeric employment canonical drifted")
    if raw_translations["15:1040:0"] != "을(를) 비롯한 총":
        raise RuntimeError("segment 861 1040 leading castle/count canonical drifted")
    for coordinate in ("15:1040:1", "15:1041:0"):
        if "휘하" not in translations[coordinate] or "산하" in translations[coordinate]:
            raise RuntimeError(
                f"segment 861 傘下 approved terminology drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in ("편입", "등용", "휘하", "접수", "금전", "병량", "가보"):
        if required not in joined:
            raise RuntimeError(
                f"segment 861 incorporation/receipt terminology drifted: {required}"
            )
    if any(term in joined for term in ("흡수", "산하", "고용")):
        raise RuntimeError("segment 861 retained forbidden legacy terminology")
    if any(coordinate.startswith("15:1095:") for coordinate in translations):
        raise RuntimeError("segment 861 hidden 1095 entered visible decision scope")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_record_map=PK_RECORD_MAP,
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
        raise RuntimeError("segment 861 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S861",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "record_count": 19152,
                "explicit_pk_record_mapping_verified": True,
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
