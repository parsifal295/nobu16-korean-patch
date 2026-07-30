#!/usr/bin/env python3
"""Build source-redacted PK B125 segment 1381 residual decisions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_QUEUE_EVIDENCE = COMMON.queue_evidence
_ORIGINAL_BUILD_COMBINED_SLICE_CANDIDATE = (
    COMMON.build_combined_slice_candidate
)

EXPECTED_LEADING_PREFILL_CONTEXT_SHA256 = (
    "2B45EFCACDB10257561DC4ECDA8D17FBCB068948127CD610696628FB1288203E"
)
EXPECTED_FULL_BATCH_CANDIDATE_SHA256 = (
    "42C0E2EEFB27CC183F9393B7952262ECE34D18AF2791974F39E75F849E75B34C"
)
EXPECTED_FULL_BATCH_CHANGED_LITERAL_COUNT = 193

TARGET_COORDINATES = (
    "15:1795:1",
    "15:1799:0",
    "15:1800:0",
    "15:1801:0",
    "15:1802:0",
    "15:1803:0",
    "15:1804:0",
    "15:1805:1",
    "15:1806:1",
    "15:1815:1",
    "15:1816:1",
    "15:1818:1",
    "15:1819:1",
    "15:1820:1",
    "15:1821:1",
)
TRANSLATIONS = {
    "15:1795:1": "인가?",
    "15:1799:0": "알겠사",
    "15:1800:0": "먼저,",
    "15:1801:0": "다음으로,",
    "15:1802:0": "이어서,",
    "15:1803:0": "그다음으로,",
    "15:1804:0": "마지막으로,",
    "15:1805:1": "만……",
    "15:1806:1": "만……",
    "15:1815:1": "만……",
    "15:1816:1": "만……",
    "15:1818:1": "만……",
    "15:1819:1": "만……",
    "15:1820:1": "만……",
    "15:1821:1": "만……",
}
TARGET_RECORD_IDS = (
    1795,
    1799,
    1800,
    1801,
    1802,
    1803,
    1804,
    1805,
    1806,
    1815,
    1816,
    1818,
    1819,
    1820,
    1821,
)
EXPECTED_ARITY = {
    **{record_id: 2 for record_id in TARGET_RECORD_IDS},
    1800: 1,
    1801: 1,
    1802: 1,
    1803: 1,
    1804: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1795:0",
    "15:1799:1",
    "15:1805:0",
    "15:1806:0",
    "15:1815:0",
    "15:1816:0",
    "15:1818:0",
    "15:1819:0",
    "15:1820:0",
    "15:1821:0",
)
PREFILL_COMPANION_DONOR = {
    "15:1795:0": "15:1765:0",
    "15:1799:1": "15:1769:1",
    "15:1805:0": "15:1775:0",
    "15:1806:0": "15:1776:0",
    "15:1815:0": "15:1785:0",
    "15:1816:0": "15:1786:0",
    "15:1818:0": "15:1788:0",
    "15:1819:0": "15:1788:0",
    "15:1820:0": "15:1790:0",
    "15:1821:0": "15:1790:0",
}
EXACT_BASE_DONOR = {
    1795: (15, 1765),
    1799: (15, 1769),
    1800: (15, 1770),
    1801: (15, 1771),
    1802: (15, 1772),
    1803: (15, 1773),
    1804: (15, 1774),
    1805: (15, 1775),
    1806: (15, 1776),
    1815: (15, 1785),
    1816: (15, 1786),
    1818: (15, 1788),
    1819: (15, 1788),
    1820: (15, 1790),
    1821: (15, 1790),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    1800: ((15, 1770),),
    1801: ((15, 1771),),
    1802: ((15, 1772),),
    1803: ((15, 1773),),
    1804: ((15, 1774),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1795: ((15, 1765),),
    1799: ((15, 1769),),
    1805: ((15, 1775),),
    1806: ((15, 1776),),
    1815: ((15, 1785),),
    1816: ((15, 1786),),
    1818: ((15, 1788), (15, 1789)),
    1819: ((15, 1788), (15, 1789)),
    1820: ((15, 1790), (15, 1791)),
    1821: ((15, 1790), (15, 1791)),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1795: ((610,), ()),
    1799: ((538, 304), ()),
    1800: ((), ()),
    1801: ((), ()),
    1802: ((), ()),
    1803: ((), ()),
    1804: ((), ()),
    1805: ((150114, 562), ()),
    1806: ((150114, 562), ()),
    1815: ((150114, 562), ()),
    1816: ((150114, 550), ()),
    1818: ((150114, 562), ()),
    1819: ((150114, 562), ()),
    1820: ((150114, 562), ()),
    1821: ((150114, 562), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1381,
    queue_start=134,
    queue_stop=200,
    slice_first="15:1782:0",
    slice_last="15:1822:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(610, 538, 304, 562, 550),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1755, 1833)
    ),
    speaker_style=(
        (1795, "formal_situation_explanation_prompt"),
        (1799, "formal_counsel_help_instruction"),
        (1800, "system_first_topic_transition"),
        (1801, "system_second_topic_transition"),
        (1802, "system_following_topic_transition"),
        (1803, "system_next_topic_transition"),
        (1804, "system_final_topic_transition"),
        (1805, "formal_overlord_vassalage_assessment"),
        (1806, "formal_subordinate_force_assessment"),
        (1815, "formal_future_attack_target_assessment"),
        (1816, "formal_regional_position_assessment"),
        (1818, "formal_finance_assessment"),
        (1819, "formal_finance_assessment"),
        (1820, "formal_assets_assessment"),
        (1821, "formal_assets_assessment"),
    ),
    terminology_policy=(
        ("our clan", "우리 가문"),
        ("council", "평정"),
        ("strategy policy", "공략 방침"),
        ("counsel", "진언"),
        ("vassalage", "종속"),
        ("force", "세력"),
        ("money", "금전"),
        ("assets", "자산"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B125 queue ordinals one hundred "
        "thirty-four through one hundred ninety-nine and the approved Base "
        "prefill; the first one hundred thirty-four visible B125 coordinates "
        "are independently required to be fully prefilled and all two "
        "hundred coordinates are rebuilt together under a full-batch "
        "candidate, reverse overlay, gap and outside-scope guard; pristine "
        "PK JP is authoritative and every populated EN, SC and TC same-"
        "record fragment array was reviewed as auxiliary context; all "
        "fifteen complete records reuse approved completed Base Korean "
        "assemblies selected by raw, literal and operand-masked source "
        "identity with explicit exact donors; Base runtime and VM state are "
        "never inherited; our clan, councils, strategy policy, counsel, "
        "vassalage, forces, money and assets retain established historical "
        "project wording and formal advisory or system transition registers; "
        "calls, speaker and topic tokens, protected outer whitespace, line "
        "breaks, ellipses, terminators, complete record arity, all fifty-one "
        "slice prefills, the leading one hundred thirty-four prefills, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, outside-"
        "scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=10,
    pins={
        "expected_queue_universe_sha256": (
            "2A7C6A73240F5641F9683B4E42D3D6207EAA2A724A2B8101CA47CB7E4B452AC7"
        ),
        "expected_queue_slice_sha256": (
            "B401C95E0B559E6DF864AC133F46AF533451E2E5CC7FA47C38F74D249C6EDC71"
        ),
        "expected_prefilled_coordinate_sha256": (
            "056C1AFA6308AA58C245DD6FB1F9598A76BE368812676326CF405D11AF8D24BF"
        ),
        "expected_prefill_slice_context_sha256": (
            "1298B80B0BBE18151F16D0CFA5315AC4B45F8B7B81B8DE6AFF2FB61D4C3379F6"
        ),
        "expected_target_coordinate_sha256": (
            "907E0D738694D8925FE2F103866EE329072AFF9493636DE7B409523E9FA8C03A"
        ),
        "expected_source_target_sha256": (
            "82F05EB939E301DECE61EB145728332A485F9E3B68C8AB815172443ABF0DC580"
        ),
        "expected_current_target_sha256": (
            "4733284BCB9E67DEA096B23DAEC315C706B04CBDDF50B852C40D8722D9240B9D"
        ),
        "expected_context_corpus_sha256": (
            "318D78EF898E8207847F859B86DCE345A0139CFD10114F989853ADD194634C16"
        ),
        "expected_gap_contract_sha256": (
            "76B715B49F0D812909642E9D5164E513735FCF46F2E59AFED09589C4E5BD8A21"
        ),
        "expected_boundary_sha256": (
            "61FD6A9E8D885F19700CFE7C51CB82C4EB79B266312AB03615D2829443D4B5BB"
        ),
        "expected_runtime_control_sha256": (
            "4D8622C01F41B54A1C223DB13480A9C9D337B65294FD6A279DE2F866C95C55AE"
        ),
        "expected_base_search_sha256": (
            "4957841D9B99D4347386C73F0AFA0187420DE6BB36CEC4ACDD76864F40002BE4"
        ),
        "expected_complete_assembly_sha256": (
            "6ADF92E8711CAFCC3E4B64C197E0E4836180BDFE7EEC20E51A03DE16E331ECA0"
        ),
        "expected_call_graph_sha256": (
            "21258FBF6EEBC9AD04700FB50644F0C12B5A2E2C4AFFF401CCB1D2C7659FF700"
        ),
        "expected_speaker_style_sha256": (
            "0B95B098B2954B9D7B7BC34306E32DFF84946C614179F36F061FAEDF722002AA"
        ),
        "expected_terminology_policy_sha256": (
            "D5A7C6D55A481C5093612B5DD552BAF21279EFB606E1E9778C9A872F338DC4C0"
        ),
        "expected_translation_policy_sha256": (
            "13E02F2F155F8042899F6EBA92DFB1BCFD3648AF882C88EF46E0EF0A98DC0D4A"
        ),
        "expected_candidate_sha256": (
            "858511999258D79EB38F26889F7C2671BB6A44EB78D686BC16E13358C9785AC0"
        ),
        "expected_combined_slice_candidate_sha256": (
            "3C44061F47BA5E794A85BAEA7C142B209128C50F065D573EA5376AFEC19A7841"
        ),
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B125_S1381",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B125_S1381.private.v1.jsonl"
    ),
    "optional_neighbors": (),
    "queue_batch_id": "pk_msggame-B125",
    "queue_row_count": 108,
    "queue_visible_count": 200,
    "queue_first": "15:1715:0",
    "queue_last": "15:1822:0",
})


def _guard_custom_digest(
    label: str,
    value: Any,
    expected: str,
) -> str:
    actual = COMMON.CORE.canonical_sha256(value)
    if expected == "TO_PIN":
        COMMON.DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment 1381 {label} drifted: {actual}")
    return actual


def queue_evidence(prepared: Any) -> tuple[Any, ...]:
    result = _ORIGINAL_QUEUE_EVIDENCE(prepared)
    visible = result[0]
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    leading = visible[:134]
    if (
        len(leading) != 134
        or any(coordinate not in prefill_rows for coordinate in leading)
    ):
        raise RuntimeError("segment 1381 leading prefill drifted")
    context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in leading
    )
    _guard_custom_digest(
        "leading 134 prefill context",
        context,
        EXPECTED_LEADING_PREFILL_CONTEXT_SHA256,
    )
    return result


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    standard = _ORIGINAL_BUILD_COMBINED_SLICE_CANDIDATE(
        prepared,
        records_by_label,
    )
    visible = queue_evidence(prepared)[0]
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    replacements = {
        COMMON.coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in visible
    }
    current = records_by_label["current"]
    reverse = {
        key: COMMON.literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = COMMON.ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = COMMON.ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or COMMON.ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError("segment 1381 full-batch overlay drifted")
    candidate_records = COMMON.ENGINE.archive_records(
        COMMON.ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 200
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            COMMON.gap_bytes(candidate_records[key])
            != COMMON.gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError("segment 1381 full-batch scope drifted")
    changed = sum(
        translation != COMMON.literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = COMMON.sha256_bytes(candidate)
    if EXPECTED_FULL_BATCH_CANDIDATE_SHA256 == "TO_PIN":
        COMMON.DISCOVERED_PINS[
            "full B125 candidate"
        ] = candidate_sha256
        COMMON.DISCOVERED_PINS[
            "full B125 changed count"
        ] = str(changed)
    elif (
        candidate_sha256 != EXPECTED_FULL_BATCH_CANDIDATE_SHA256
        or changed != EXPECTED_FULL_BATCH_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            "segment 1381 full-batch candidate drifted: "
            f"{candidate_sha256}:{changed}"
        )
    return standard


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.queue_evidence = queue_evidence
COMMON.build_combined_slice_candidate = build_combined_slice_candidate
COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
