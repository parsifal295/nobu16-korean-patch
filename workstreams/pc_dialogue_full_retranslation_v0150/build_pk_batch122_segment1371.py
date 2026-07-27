#!/usr/bin/env python3
"""Build source-redacted PK B122 segment 1371 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

CROSS_TRANSLATIONS = {
    "15:1493:0": "에 의해",
    "15:1493:1": "에서",
}
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B122_S1370"

TARGET_COORDINATES = (
    "15:1493:2",
    "15:1495:0",
    "15:1495:1",
    "15:1495:2",
    "15:1496:0",
    "15:1497:1",
    "15:1497:2",
    "15:1497:3",
    "15:1498:1",
    "15:1498:2",
    "15:1498:3",
    "15:1499:1",
    "15:1499:2",
    "15:1499:3",
    "15:1500:2",
    "15:1504:0",
    "15:1505:0",
    "15:1505:1",
    "15:1505:2",
    "15:1506:0",
    "15:1507:0",
    "15:1507:1",
    "15:1507:2",
    "15:1510:5",
    "15:1511:0",
    "15:1511:3",
    "15:1512:3",
    "15:1513:4",
)
TRANSLATIONS = {
    "15:1493:2": "이(가) 발생",
    "15:1495:0": "을(를) 비롯한",
    "15:1495:1": "명에게 벌인",
    "15:1495:2": "에 성공",
    "15:1496:0": "을(를) 비롯한",
    "15:1497:1": "에서",
    "15:1497:2": "님께서\n",
    "15:1497:3": "에게 의심을 품고 있는 모양……",
    "15:1498:1": "에서",
    "15:1498:2": "님께서\n",
    "15:1498:3": "에게 의심을 품고 있는 모양……",
    "15:1499:1": "님을 비롯한",
    "15:1499:2": "명이\n",
    "15:1499:3": "에게 의심을 품고 있는 모양……",
    "15:1500:2": "이(가) 벌인",
    "15:1504:0": "전방의",
    "15:1505:0": "에서",
    "15:1505:1": "(으)로 병량",
    "15:1505:2": "을 이송",
    "15:1506:0": "전방의",
    "15:1507:0": "에서",
    "15:1507:1": "(으)로 병력",
    "15:1507:2": "을 이송",
    "15:1510:5": "?",
    "15:1511:0": "우리 가문의",
    "15:1511:3": "?",
    "15:1512:3": "인가?",
    "15:1513:4": "인가?",
}
TARGET_RECORD_IDS = (
    1493,
    1495,
    1496,
    1497,
    1498,
    1499,
    1500,
    1504,
    1505,
    1506,
    1507,
    1510,
    1511,
    1512,
    1513,
)
EXPECTED_ARITY = {
    1493: 3,
    1495: 3,
    1496: 2,
    1497: 4,
    1498: 4,
    1499: 4,
    1500: 4,
    1504: 3,
    1505: 3,
    1506: 3,
    1507: 3,
    1510: 6,
    1511: 4,
    1512: 4,
    1513: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1496:1",
    "15:1497:0",
    "15:1498:0",
    "15:1499:0",
    "15:1500:0",
    "15:1500:3",
    "15:1504:1",
    "15:1504:2",
    "15:1506:1",
    "15:1506:2",
    "15:1510:0",
    "15:1510:1",
    "15:1510:3",
    "15:1510:4",
    "15:1511:1",
    "15:1511:2",
    "15:1512:0",
    "15:1512:1",
    "15:1512:2",
    "15:1513:0",
    "15:1513:1",
    "15:1513:3",
    *tuple(CROSS_TRANSLATIONS),
)
PREFILL_COMPANION_DONOR = {
    "15:1496:1": "15:1481:1",
    "15:1497:0": "15:1482:0",
    "15:1498:0": "15:1482:0",
    "15:1499:0": "15:1484:0",
    "15:1500:0": "15:973:0",
    "15:1500:3": "15:973:3",
    "15:1504:1": "15:1489:1",
    "15:1504:2": "15:1489:2",
    "15:1506:1": "15:1491:1",
    "15:1506:2": "15:1491:2",
    "15:1510:0": "15:1495:0",
    "15:1510:1": "15:1495:1",
    "15:1510:3": "15:1495:3",
    "15:1510:4": "15:1495:4",
    "15:1511:1": "15:1496:1",
    "15:1511:2": "15:1496:2",
    "15:1512:0": "15:1497:0",
    "15:1512:1": "15:1497:1",
    "15:1512:2": "15:1497:2",
    "15:1513:0": "15:1498:0",
    "15:1513:1": "15:1498:1",
    "15:1513:3": "15:1498:3",
    **{
        coordinate: CROSS_DONOR_LABEL
        for coordinate in CROSS_TRANSLATIONS
    },
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:1500:1",
    "15:1510:2",
    "15:1513:2",
)
EXACT_BASE_DONOR = {
    1493: (15, 1478),
    1495: (15, 1480),
    1496: (15, 1481),
    1497: (15, 1482),
    1498: (15, 1483),
    1499: (15, 1484),
    1500: (15, 1485),
    1504: (15, 1489),
    1505: (15, 1490),
    1506: (15, 1491),
    1507: (15, 1492),
    1510: (15, 1495),
    1511: (15, 1496),
    1512: (15, 1497),
    1513: (15, 1498),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    1493: ((15, 1478),),
    1495: ((15, 1480),),
    1496: ((15, 1481),),
    1497: ((15, 1482),),
    1498: ((15, 1483),),
    1499: ((15, 1484),),
    1500: (),
    1504: (),
    1505: ((15, 1490),),
    1506: ((15, 1491),),
    1507: ((15, 1492),),
    1510: (),
    1511: ((15, 1496),),
    1512: (),
    1513: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1497: ((15, 1482), (15, 1483)),
    1498: ((15, 1482), (15, 1483)),
    1500: (
        (15, 907),
        (15, 973),
        (15, 1276),
        (15, 1365),
        (15, 1444),
        (15, 1485),
    ),
    1504: ((15, 1489),),
    1510: ((15, 1495),),
    1512: ((15, 1497),),
    1513: ((15, 1498),),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    1500: (
        (15, 973),
        (15, 1276),
        (15, 1365),
        (15, 1444),
        (15, 1485),
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    1493: ((), ("025032", "026432", "023C")),
    1495: ((), ("024833", "0232", "023C")),
    1496: ((), ("024833", "0232")),
    1497: ((8,), ("025032", "026432", "024833")),
    1498: ((13,), ("025032", "026432", "024833")),
    1499: ((8,), ("025032", "024833", "0232")),
    1500: ((538, 592), ("026432", "025032", "023C")),
    1504: ((700, 292), ("026432", "026532")),
    1505: ((), ("026532", "026432", "0232")),
    1506: ((), ("026432", "026532")),
    1507: ((), ("026532", "026432", "0232")),
    1510: ((598, 1, 148, 292), ("023C",)),
    1511: ((1, 292), ("023C",)),
    1512: ((1, 610), ("023C",)),
    1513: ((550, 1, 1138), ("023C",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1371,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1493:2",
    slice_last="15:1514:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(
        HIDDEN_CURRENT_COMPANION_COORDINATES
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        8,
        13,
        538,
        592,
        700,
        292,
        598,
        1,
        148,
        610,
        550,
        1138,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1460, 1546)
    ),
    speaker_style=(
        (1493, "system_event_occurrence"),
        (1495, "system_group_operation_success"),
        (1496, "system_group_loyalty_decrease"),
        (1497, "formal_individual_suspicion_report"),
        (1498, "formal_individual_suspicion_report"),
        (1499, "formal_group_suspicion_report"),
        (1500, "male_spy_capture_report"),
        (1504, "formal_provisions_transport_proposal"),
        (1505, "system_provisions_transport"),
        (1506, "formal_troop_transport_proposal"),
        (1507, "system_troop_transport"),
        (1510, "casual_talent_mentoring_proposal"),
        (1511, "formal_talent_mentoring_proposal"),
        (1512, "rough_talent_training_proposal"),
        (1513, "polite_talent_teaching_proposal"),
    ),
    terminology_policy=(
        ("spy", "간자"),
        ("covert work", "공작"),
        ("suspicion", "의심"),
        ("loyalty", "충성"),
        ("provisions", "병량"),
        ("troop strength", "병력"),
        ("transport", "이송"),
        ("morale", "사기"),
        ("talent", "인재"),
        ("mentoring", "지도"),
        ("training", "단련"),
        ("teaching a secret", "비결 전수"),
        ("clan", "우리 가문"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic directional particle", "(으)로"),
        ("project long ellipsis", "……"),
        ("project question mark", "?"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B122 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all fifteen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity, with "
        "explicit donors fixing duplicate candidates; record 1493 "
        "reciprocally pins the S1370 opening fragments and three source-"
        "identical hidden newline companions remain non-translatable while "
        "participating in exact complete-record assembly; Base runtime and "
        "VM state are never inherited; spies, covert work, suspicion, "
        "loyalty, provisions, troop strength, transport, morale, talent, "
        "mentoring, training and secret teaching retain established "
        "historical project wording and system, formal, rough, casual or "
        "polite registers; calls, inline officer, castle, faction, count, "
        "operation and resource tokens, protected outer whitespace, line "
        "breaks, ellipses, question marks, terminators, complete record "
        "arity, all thirty-nine slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=18,
    pins={
        "expected_queue_universe_sha256": (
            "681287EB7B080C5886E75BAC2DFCF0131969FF940310C498FEFB86748B5D8244"
        ),
        "expected_queue_slice_sha256": (
            "FFCB9FE14DCFCE8DA0C655E7F8CD907D28A2845240DA4E1A1E8E4EE4BB6E2716"
        ),
        "expected_prefilled_coordinate_sha256": (
            "92994079330429BDFD4F91EF95C4315336E4815E9936BCF68B9DAA420E52A331"
        ),
        "expected_prefill_slice_context_sha256": (
            "02E4C1DED80A95B457CCB2A4E6EA738E87E3D8CA275466861E7CAEB0F14F1BC7"
        ),
        "expected_target_coordinate_sha256": (
            "CFDAFD82AD3843919B29814B3255EBC679049B2FB0645902D79424AFA6CF62DC"
        ),
        "expected_source_target_sha256": (
            "16619351FC91835F35B4BAAA1F19C498737DFFC5574CCDAFF86A66D3AB703852"
        ),
        "expected_current_target_sha256": (
            "8D96EEE23D2CCD4789F992E0DB89F5B98F9291C837323948A318DEE744E7967B"
        ),
        "expected_context_corpus_sha256": (
            "11432A15C4EE5D21CE9924C01FB10A2BE8B8C482F0F7149C0F63A727520B20DB"
        ),
        "expected_gap_contract_sha256": (
            "EC5C0E543D827ACF4D452598238D40560B93ABAC96B8DAC73C5C49632AE0F7CA"
        ),
        "expected_boundary_sha256": (
            "9411B3877C583393D4E6A7055A94AD3D5166B6DB25FB454728ECA2DE5944258F"
        ),
        "expected_runtime_control_sha256": (
            "CEF2B9CF95E775B6D51966E0BD1BD423D4C6993C842FC7AE409177D766A5BABE"
        ),
        "expected_base_search_sha256": (
            "8A278959E038BE7ADF365D853BAEC1E243FAF9B9FCE24AF16C70F26FDB55E071"
        ),
        "expected_complete_assembly_sha256": (
            "7FED77E2291476AD8C452ED6B59AC31AACCBED57338D3FE0DC70014244C2E04B"
        ),
        "expected_call_graph_sha256": (
            "3C137C103EAB66BDB63961E5A6EE99C0400349D0DEA6FFC016AF16AE738E9FBD"
        ),
        "expected_speaker_style_sha256": (
            "02C2F6A25D7ABB893DB947258D3E6A4110032C1555AAF5BC24FD5700ABB891A5"
        ),
        "expected_terminology_policy_sha256": (
            "3DCF389567662909AC9D431DBE1B9B7AAC3AEDBC0DA3EEB3CF8F1BBF0EDA88B0"
        ),
        "expected_translation_policy_sha256": (
            "A8B0A7040BC3BC86AE365E7446A6CADD9A46B28AB56DC431E636CD8BFD660273"
        ),
        "expected_candidate_sha256": (
            "2A9C7ECD3C3FC971DF90110CA5387B20B9A2BBF0B3A32903112A6B17F8A9402D"
        ),
        "expected_combined_slice_candidate_sha256": (
            "8F7DE4C6175E43A17EF013DE451661134C6D489E978D58A127387C05DD0F4AA9"
        ),
        "expected_combined_changed_literal_count": 45,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B122_S1371",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1371.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1370.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1372.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B122",
    "queue_row_count": 69,
    "queue_visible_count": 199,
    "queue_first": "15:1467:0",
    "queue_last": "15:1535:0",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard completed Base assemblies, hidden newlines and S1370 split."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1371 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1370.private.v1.jsonl"
    )
    if neighbor_path.is_file():
        neighbor_rows = {
            str(row["coordinate"]): row
            for row in COMMON.read_jsonl(neighbor_path)
        }
        for coordinate, translation in CROSS_TRANSLATIONS.items():
            neighbor = neighbor_rows.get(coordinate)
            if (
                neighbor is None
                or neighbor.get("resource") != "pk_msggame"
                or neighbor.get("semantic_review") != "approved"
                or neighbor.get("runtime_review") != "pending"
                or str(neighbor.get("translation")) != translation
            ):
                raise RuntimeError(
                    "segment 1371 reciprocal S1370 fragment drifted"
                )
    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (15, record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(
            records_by_label["jp"], key
        )
        current_literals = COMMON.literal_texts(
            records_by_label["current"], key
        )
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
            )
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
                and COMMON.CORE.mask_call_operands(record)
                == COMMON.CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches
            != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches
            != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1371 Base search drifted: {record_id}"
            )
        donor_key = EXACT_BASE_DONOR[record_id]
        donor_coordinates = tuple(
            f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        references: list[tuple[Any, ...]] = []
        donor_translations: list[str] = []
        for literal_id, donor_coordinate in enumerate(donor_coordinates):
            target_coordinate = f"15:{record_id}:{literal_id}"
            donor = base_rows.get(donor_coordinate)
            if donor is None and target_coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment 1371 hidden donor drifted: "
                        f"{target_coordinate}"
                    )
                donor_translations.append("\n")
                references.append((
                    donor_coordinate,
                    "\n",
                    "source_identical_hidden_newline",
                    "not_translatable_blank",
                    "complete_exact_assembly",
                    "runtime_vm_not_inherited",
                ))
                continue
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1371 Base context drifted: "
                    f"{donor_coordinate}"
                )
            donor_translation = str(donor["translation"])
            donor_translations.append(donor_translation)
            references.append((
                donor_coordinate,
                donor_translation,
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "complete_exact_assembly",
                "runtime_vm_not_inherited",
            ))
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append(
                    "segment_manual_exact_base_semantic_reuse"
                )
                seen_target.add(coordinate)
            elif coordinate in CROSS_TRANSLATIONS:
                assembled.append(CROSS_TRANSLATIONS[coordinate])
                owners.append(
                    "neighbor_segment_manual_runtime_pending"
                )
                seen_companion.add(coordinate)
            elif coordinate in companion_set:
                prefill = prefill_rows.get(coordinate)
                if (
                    prefill is None
                    or prefill.get("semantic_review") != "approved"
                    or prefill.get("runtime_review")
                    not in {"pending", "not_required"}
                    or prefill["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or prefill["base_exact_reuse_prefill"][
                        "base_coordinate"
                    ]
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment 1371 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment 1371 hidden newline drifted: {coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1371 incomplete record: {coordinate}"
                )
        if tuple(assembled) != tuple(donor_translations):
            raise RuntimeError(
                f"segment 1371 exact assembly drifted: {record_id}"
            )
        base_evidence.append((
            record_id,
            COMMON.sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(source)
            ),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(references),
            "complete_exact_semantic_review",
        ))
        assembly_evidence.append((
            record_id,
            tuple(owners),
            tuple(assembled),
            tuple(donor_translations),
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError("segment 1371 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
