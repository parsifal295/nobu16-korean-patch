#!/usr/bin/env python3
"""Build Base authoring segment 942 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment941 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S942.private.v1.jsonl"
)
SEGMENT = 942
SUPPLY_TRANSLATION = (
    "에서 병량을 확보하면\n싸움이 길어져도\n병력을 유지할 수 있을",
)
MONEY_PROPOSAL_TRANSLATION = (
    "무슨 일을 하든 먼저 필요한 것은 금전…\n",
    "에서 수입을 늘려 보는 것은",
)
CROP_TRANSLATION = (
    "에서 석고를 늘리면\n싸움이 길어져도\n병력을 유지할 수 있을",
)
SUPPLY_LIMIT_TRANSLATION = (
    "에서 병량 상한을 늘려 두면\n연전에도 대비할 수 있을",
)
DEFENSIVE_CONSTRUCTION_TRANSLATION = (
    "수비를 굳혀 두면\n만일의 사태에도 안심",
    "\n",
    "의 건설도 한 방법",
)
TRANSLATIONS_BY_RECORD = {
    1866: (
        "의 성하에\n",
        "을(를) 건설하는 것이 상책이라고 생각합니다",
    ),
    1867: (
        "을(를) 건설한 뒤에는\n병력과 병량을 확인해 군비를 갖추고\n"
        "다음 싸움에 대비해야 합니다",
    ),
    1868: (
        "지금은 수입을 늘리는 것이 긴요합니다\n"
        "싸움에 대비하는 것은 그다음입니다",
    ),
    1869: SUPPLY_TRANSLATION,
    1870: MONEY_PROPOSAL_TRANSLATION,
    1871: MONEY_PROPOSAL_TRANSLATION,
    1872: CROP_TRANSLATION,
    1873: (
        "공격도 수비도 병력에 달린 일",
        "\n",
        "에서 병력을 늘려 보는 것은",
    ),
    1874: (
        "의 건설 준비가 끝나 있",
        "\n포술 훈련을 실시해\n병사를 강화",
    ),
    1875: (
        "의 건설 준비가 끝나 있",
        "\n기마술 훈련을 실시해\n병사를 강화",
    ),
    1876: SUPPLY_LIMIT_TRANSLATION,
    1877: DEFENSIVE_CONSTRUCTION_TRANSLATION,
    1878: DEFENSIVE_CONSTRUCTION_TRANSLATION,
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1873:1": "\n",
    "15:1877:1": "\n",
    "15:1878:1": "\n",
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1866: ("の城下に\n", "を建設するが上策かと"),
    1867: (
        "建設の後は\n兵力と兵糧を確認して軍備を整え\n"
        "次なる戦に臨むべきかと",
    ),
    1868: ("今は収入を伸ばすが肝要\n戦支度はその後かと",),
    1869: ("で兵糧を確保すれば\n戦が長引いても\n兵力を保て",),
    1870: (
        "何をするにも先立つものは金銭…\n",
        "で収入を増やしては",
    ),
    1871: (
        "何をするにも先立つものは金銭…\n",
        "で収入を増やしては",
    ),
    1872: ("で石高を増強すれば\n戦が長引いても\n兵力を保て",),
    1873: ("攻めるも守るも兵力次第", "\n", "で兵力を増強しては"),
    1874: (
        "建設の準備は整ってい",
        "\n砲術の訓練を行い\n兵を強化し",
    ),
    1875: (
        "建設の準備は整ってい",
        "\n馬術の訓練を行い\n兵を強化し",
    ),
    1876: ("で兵糧上限を増やしておけば\n連戦にも備えられ",),
    1877: (
        "守りを固めておけば\nいざというときも安心",
        "\n",
        "の建設はいかが",
    ),
    1878: (
        "守りを固めておけば\nいざというときも安心",
        "\n",
        "の建設はいかが",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1866: ("026432", "1B4349023C1B435A", "050505"),
    1867: ("023C", "050505"),
    1868: ("", "050505"),
    1869: ("023C", "01431E040000050505"),
    1870: ("", "023C", "0143B0020000014356020000050505"),
    1871: ("", "023C", "0143B0020000014356020000050505"),
    1872: ("023C", "01431E040000050505"),
    1873: (
        "",
        "01432C020000",
        "023C",
        "0143B0020000014356020000050505",
    ),
    1874: ("023C", "01433C040000", "01431E040000050505"),
    1875: ("023C", "01433C040000", "01431E040000050505"),
    1876: ("023C", "01431E040000050505"),
    1877: ("", "01432C020000", "023C", "014324010000050505"),
    1878: ("", "01432C020000", "023C", "014324010000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1866: ("026432", "1B4349023C1B435A", "050505"),
    1867: ("023C", "050505"),
    1868: ("", "050505"),
    1869: ("023C", "01432A040000050505"),
    1870: ("", "023C", "0143BC020000014362020000050505"),
    1871: ("", "023C", "0143BC020000014362020000050505"),
    1872: ("023C", "01432A040000050505"),
    1873: (
        "",
        "014338020000",
        "023C",
        "0143BC020000014362020000050505",
    ),
    1874: ("023C", "014348040000", "01432A040000050505"),
    1875: ("023C", "014348040000", "01432A040000050505"),
    1876: ("023C", "01432A040000050505"),
    1877: ("", "014338020000", "023C", "014324010000050505"),
    1878: ("", "014338020000", "023C", "014324010000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:1870:0", "15:1871:0"}
STATIC_RECORD_IDS = {1868}
EXPECTED_AUXILIARY_DIGESTS = {
    "base_SC": "754245920E6F160ADDD395D4E06A4AB0E90BCC0A318D5869C0A543E47B1DA480",
    "base_TC": "E46F7D7CB5841A0F4DAC95AF49656C3D4CCB744B3EDE5D6A318C75D0402B6580",
    "pk_SC": "754245920E6F160ADDD395D4E06A4AB0E90BCC0A318D5869C0A543E47B1DA480",
    "pk_TC": "E46F7D7CB5841A0F4DAC95AF49656C3D4CCB744B3EDE5D6A318C75D0402B6580",
    "pk_EN": "F418AEC9BC46DD1EC53BED98C286A9311F6F426B02F04C7882B5A0DD8F075BF9",
}
BASIS = (
    "review_queue_base_msggame_B113_B_pristine_base_pc_jp_authoritative_"
    "castle_town_facility_income_supplies_crop_yield_troops_gunnery_"
    "horsemanship_and_defensive_facility_proposals_with_explicit_base_"
    "1866_1878_to_pk1896_1908_mapping_exact_base_pk_jp_sc_tc_and_pk_en_"
    "context_guarded_by_combined_record_sha256_dynamic_castle_facility_"
    "tokens_026432_023c_and_policy_colour_wrappers_current_korean_"
    "morphology_terminal_corpora_and_base_pk_opcode_divergences_recorded_"
    "1873_1877_1878_hidden_lf_excluded_exact_repeated_1870_1871_and_"
    "1877_1878_reuse_kotobank_kokudaka_land_productivity_tax_basis_"
    "hojutsu_firearm_operation_and_bajutsu_military_horsemanship_basis_"
    "project_seongha_facility_seokgo_byeongnyang_posul_gimasul_terms_"
    "current_line_counts_ellipsis_pair_and_runtime_skeleton_preserved"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    292: ("일까요", "일까", "입니까"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    1054: ("합시다", "듯"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    292: EXPECTED_BASE_MORPHOLOGY_TERMINALS[292],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if TRANSLATIONS_BY_RECORD[1869] is not SUPPLY_TRANSLATION:
        raise RuntimeError("segment 942 Base1869 supply canonical tuple split")
    if TRANSLATIONS_BY_RECORD[1870] is not MONEY_PROPOSAL_TRANSLATION:
        raise RuntimeError("segment 942 Base1870 money canonical tuple split")
    if TRANSLATIONS_BY_RECORD[1871] is not MONEY_PROPOSAL_TRANSLATION:
        raise RuntimeError("segment 942 Base1871 money canonical tuple split")
    if TRANSLATIONS_BY_RECORD[1872] is not CROP_TRANSLATION:
        raise RuntimeError("segment 942 Base1872 crop canonical tuple split")
    if TRANSLATIONS_BY_RECORD[1876] is not SUPPLY_LIMIT_TRANSLATION:
        raise RuntimeError("segment 942 Base1876 supply-limit tuple split")
    if TRANSLATIONS_BY_RECORD[1877] is not DEFENSIVE_CONSTRUCTION_TRANSLATION:
        raise RuntimeError("segment 942 Base1877 defense tuple split")
    if TRANSLATIONS_BY_RECORD[1878] is not DEFENSIVE_CONSTRUCTION_TRANSLATION:
        raise RuntimeError("segment 942 Base1878 defense tuple split")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 942 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {
        1869,
        1870,
        1871,
        1872,
        1873,
        1874,
        1875,
        1876,
        1877,
        1878,
    }:
        raise RuntimeError("segment 942 Base-to-PK gap divergence drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {
        "15:1873:1": "\n",
        "15:1877:1": "\n",
        "15:1878:1": "\n",
    }:
        raise RuntimeError("segment 942 hidden LF exclusion drifted")
    joined = "\n".join(translations.values())
    for required in (
        "성하",
        "병량",
        "석고",
        "포술",
        "기마술",
        "군비",
        "연전",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 942 required terminology drifted: {required}"
            )
    for forbidden in ("당가", "호족", "승마 훈련"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 942 forbidden terminology retained: {forbidden}"
            )
    for record_id in (1874, 1875):
        if not TRANSLATIONS_BY_RECORD[record_id][0].endswith("준비가 끝나 있"):
            raise RuntimeError(
                f"segment 942 completed-preparation state drifted: {record_id}"
            )
    if re.search(r"(?<!기)마술", joined):
        raise RuntimeError("segment 942 standalone 마술 terminology retained")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 942 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(translations) != 21:
        raise RuntimeError("segment 942 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    auxiliary_overrides = PREVIOUS.make_guarded_auxiliary_overrides(
        tuple(RECORD_ARITIES),
        PK_RECORD_MAP,
        EXPECTED_AUXILIARY_DIGESTS,
    )
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=auxiliary_overrides,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    for row in rows:
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
        skip_records=STATIC_RECORD_IDS,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 942 validated count drifted")
    static_rows = [
        row
        for row in rows
        if row["scope_classification"] == "retranslated"
        and row["runtime_review"] == "not_required"
    ]
    if len(static_rows) != 1:
        raise RuntimeError("segment 942 static classification count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S942",
                "source_literal_count": 24,
                "decision_count": len(rows),
                "hidden_lf_excluded": len(EXCLUDED_NONVISIBLE_COORDINATES),
                "retranslated": len(static_rows),
                "runtime_fragment_pending": len(rows) - len(static_rows),
                "static_record_ids": sorted(STATIC_RECORD_IDS),
                "canonical_reuse_groups": [
                    [1870, 1871],
                    [1877, 1878],
                ],
                "cross_segment_exports": [
                    1869,
                    1872,
                    1876,
                ],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": sorted(
                    record_id
                    for record_id in RECORD_ARITIES
                    if EXPECTED_BASE_GAPS[record_id]
                    != EXPECTED_PK_JP_GAPS[record_id]
                ),
                "historical_term_basis": {
                    "石高": "Kotobank land productivity and tax basis",
                    "砲術": "Kotobank firearm operation skill",
                    "馬術": "Kotobank military horsemanship skill",
                },
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
