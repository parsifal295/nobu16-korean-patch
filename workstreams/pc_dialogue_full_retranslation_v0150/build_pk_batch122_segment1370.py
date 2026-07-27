#!/usr/bin/env python3
"""Build source-redacted PK B122 segment 1370 residual decisions."""

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
    "15:1493:2": "이(가) 발생",
}
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B122_S1371"

TARGET_COORDINATES = (
    "15:1467:1",
    "15:1467:2",
    "15:1468:1",
    "15:1468:2",
    "15:1469:0",
    "15:1469:1",
    "15:1469:2",
    "15:1471:0",
    "15:1475:1",
    "15:1480:1",
    "15:1481:2",
    "15:1483:0",
    "15:1483:4",
    "15:1484:0",
    "15:1485:0",
    "15:1485:2",
    "15:1487:0",
    "15:1487:1",
    "15:1487:2",
    "15:1488:0",
    "15:1488:1",
    "15:1488:2",
    "15:1489:0",
    "15:1489:1",
    "15:1490:0",
    "15:1490:1",
    "15:1490:2",
    "15:1491:0",
    "15:1491:1",
    "15:1491:2",
    "15:1492:0",
    "15:1492:1",
    "15:1492:2",
    "15:1492:3",
    "15:1493:0",
    "15:1493:1",
)
TRANSLATIONS = {
    "15:1467:1": "→",
    "15:1467:2": "에",
    "15:1468:1": "→",
    "15:1468:2": "에",
    "15:1469:0": "에서",
    "15:1469:1": "이(가) 벌인",
    "15:1469:2": "을(를) 저지",
    "15:1471:0": "유언비어를",
    "15:1475:1": "의 성주\u00b7",
    "15:1480:1": "이……",
    "15:1481:2": "\n우선은",
    "15:1483:0": "에게 벌인",
    "15:1483:4": "듯",
    "15:1484:0": "을(를) 비롯한",
    "15:1485:0": "을(를) 벌인 대상",
    "15:1485:2": "을(를) 비롯한",
    "15:1487:0": "이(가)",
    "15:1487:1": "에게 벌인",
    "15:1487:2": "에 성공",
    "15:1488:0": "에게 벌인",
    "15:1488:1": "에 실패하여,",
    "15:1488:2": "이(가) 부상",
    "15:1489:0": "에게 벌인",
    "15:1489:1": "에 실패",
    "15:1490:0": "이(가) 벌인",
    "15:1490:1": "을(를) 대상으로 한",
    "15:1490:2": "을(를) 저지",
    "15:1491:0": "을(를) 비롯한",
    "15:1491:1": "명에게 벌인",
    "15:1491:2": "에 실패",
    "15:1492:0": "이(가) 벌인",
    "15:1492:1": "을(를) 비롯한",
    "15:1492:2": "명 대상의",
    "15:1492:3": "을(를) 저지",
    "15:1493:0": "에 의해",
    "15:1493:1": "에서",
}
TARGET_RECORD_IDS = (
    1467,
    1468,
    1469,
    1471,
    1475,
    1480,
    1481,
    1483,
    1484,
    1485,
    1487,
    1488,
    1489,
    1490,
    1491,
    1492,
    1493,
)
EXPECTED_ARITY = {
    1467: 3,
    1468: 3,
    1469: 3,
    1471: 2,
    1475: 3,
    1480: 2,
    1481: 4,
    1483: 5,
    1484: 3,
    1485: 5,
    1487: 3,
    1488: 3,
    1489: 2,
    1490: 3,
    1491: 3,
    1492: 4,
    1493: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1467:0",
    "15:1468:0",
    "15:1471:1",
    "15:1475:0",
    "15:1475:2",
    "15:1480:0",
    "15:1481:0",
    "15:1481:1",
    "15:1481:3",
    "15:1483:1",
    "15:1483:2",
    "15:1483:3",
    "15:1484:1",
    "15:1484:2",
    "15:1485:1",
    "15:1485:3",
    "15:1485:4",
    *tuple(CROSS_TRANSLATIONS),
)
PREFILL_COMPANION_DONOR = {
    "15:1467:0": "15:1452:0",
    "15:1468:0": "15:716:0",
    "15:1471:1": "15:1456:1",
    "15:1475:0": "15:1460:0",
    "15:1475:2": "15:1460:2",
    "15:1480:0": "15:1465:0",
    "15:1481:0": "15:1466:0",
    "15:1481:1": "15:1466:1",
    "15:1481:3": "15:1466:3",
    "15:1483:1": "15:1468:1",
    "15:1483:2": "15:1468:2",
    "15:1483:3": "15:1468:3",
    "15:1484:1": "15:1469:1",
    "15:1484:2": "15:1469:2",
    "15:1485:1": "15:1470:1",
    "15:1485:3": "15:1470:3",
    "15:1485:4": "15:1470:4",
    **{
        coordinate: CROSS_DONOR_LABEL
        for coordinate in CROSS_TRANSLATIONS
    },
}
EXACT_BASE_DONOR = {
    1467: (15, 1452),
    1468: (15, 1453),
    1469: (15, 1454),
    1471: (15, 1456),
    1475: (15, 1460),
    1480: (15, 1465),
    1481: (15, 1466),
    1483: (15, 1468),
    1484: (15, 1469),
    1485: (15, 1470),
    1487: (15, 1472),
    1488: (15, 1473),
    1489: (15, 1474),
    1490: (15, 1475),
    1491: (15, 1476),
    1492: (15, 1477),
    1493: (15, 1478),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    1467: ((15, 1452),),
    1468: ((15, 716), (15, 979), (15, 1453)),
    1469: ((15, 811), (15, 980), (15, 1286), (15, 1362), (15, 1454)),
    1471: (),
    1475: ((15, 1460),),
    1480: (),
    1481: (),
    1483: (),
    1484: (),
    1485: (),
    1487: ((15, 1472),),
    1488: ((15, 1473),),
    1489: ((15, 1474),),
    1490: ((15, 1475),),
    1491: ((15, 1476),),
    1492: ((15, 1477),),
    1493: ((15, 1478),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1468: (
        (15, 716),
        (15, 979),
        (15, 1337),
        (15, 1338),
        (15, 1453),
    ),
    1471: ((15, 1456),),
    1480: ((15, 1465),),
    1481: ((15, 1466),),
    1483: ((15, 1468),),
    1484: ((15, 1469),),
    1485: ((15, 1470),),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    1468: ((15, 716), (15, 979), (15, 1453)),
}
EXPECTED_CONTROLS_BY_RECORD = {
    1467: ((), ("026432", "0232", "0233")),
    1468: ((), ("026432", "0232", "0233")),
    1469: ((), ("026432", "025032", "023C")),
    1471: ((1066,), ("026432",)),
    1475: ((), ("026432", "024833")),
    1480: ((1090,), ("024833",)),
    1481: ((1168, 1096), ("024833",)),
    1483: ((538, 178, 184, 604), ("024833", "023C")),
    1484: ((604, 178), ("024833", "0232")),
    1485: ((604, 178), ("023C", "0233", "024833", "0232")),
    1487: ((), ("024633", "024833", "023C")),
    1488: ((), ("024833", "023C", "024633")),
    1489: ((), ("024833", "023C")),
    1490: ((), ("025032", "024833", "023C")),
    1491: ((), ("024833", "0232", "023C")),
    1492: ((), ("025032", "024833", "0232", "023C")),
    1493: ((), ("025032", "026432", "023C")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1370,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1467:0",
    slice_last="15:1493:1",
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
    source_call_roots=(1066, 1090, 1168, 1096, 538, 178, 184, 604),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1442, 1505)
    ),
    speaker_style=(
        (1467, "system_provisions_change"),
        (1468, "system_troop_strength_change"),
        (1469, "system_covert_operation_prevented"),
        (1471, "formal_rumor_operation_proposal"),
        (1475, "formal_castle_officer_loyalty_assessment"),
        (1480, "formal_talent_recruitment_groundwork"),
        (1481, "confident_rumor_specialist_proposal"),
        (1483, "formal_rumor_operation_success_report"),
        (1484, "formal_group_rumor_success_report"),
        (1485, "formal_partial_group_rumor_success_report"),
        (1487, "system_covert_operation_success"),
        (1488, "system_covert_operation_failure_injury"),
        (1489, "system_covert_operation_failure"),
        (1490, "system_covert_operation_prevented"),
        (1491, "system_group_operation_failure"),
        (1492, "system_group_operation_prevented"),
        (1493, "system_event_occurrence"),
    ),
    terminology_policy=(
        ("provisions", "병량"),
        ("troop strength", "병력"),
        ("rumor", "유언비어"),
        ("castle lord", "성주"),
        ("castle officer", "성을 지키는 장수"),
        ("loyalty", "충의"),
        ("clan", "가문"),
        ("talent", "인재"),
        ("injury", "부상"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("project middle dot", "\u00b7"),
        ("project ellipsis", "……"),
        ("project arrow", "→"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B122 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all seventeen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity, with "
        "explicit exact donors fixing duplicate candidates; Base runtime "
        "and VM state are never inherited; the record split at the slice "
        "boundary is completed by the matching S1371 event-occurrence "
        "fragment and checked reciprocally when that neighbor is present; "
        "provisions, troop strength, "
        "rumors, castle officers, loyalty, clan, talent and injury retain "
        "established historical project wording and formal, confident or "
        "system registers; calls, inline officer, castle, faction, count, "
        "old and new value and operation tokens, protected outer whitespace, "
        "line breaks, middle dots, ellipses, arrows, terminators, complete "
        "record arity, all thirty-one slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=23,
    pins={
        "expected_queue_universe_sha256": (
            "681287EB7B080C5886E75BAC2DFCF0131969FF940310C498FEFB86748B5D8244"
        ),
        "expected_queue_slice_sha256": (
            "7F1E9792C52C7A9E1BD3326A979B9553699C9A3A7903F0BE2D5A5093C42CDC57"
        ),
        "expected_prefilled_coordinate_sha256": (
            "4740BB279BB06A24EAA7CA27982B28BD98004BD7BE9093A58492BA12FA4D1BA6"
        ),
        "expected_prefill_slice_context_sha256": (
            "6584FC060D7BF5DE1C7BBFDA1D012DAB64931F787F0E23AD4FF3EE3BECF3BE8D"
        ),
        "expected_target_coordinate_sha256": (
            "DA0F6A5B83A46AD81792226422E66D334C5432FED1C66C13B115E87012E55727"
        ),
        "expected_source_target_sha256": (
            "98320C8BF9CEF37A2047E5EA6CE05000C7C7438EF1EEF4583070890A40F5381B"
        ),
        "expected_current_target_sha256": (
            "8DA6B82F9484C8EF8E05CCD99359ACDFDC03FE8D3C39976E16D41E622F00F5B0"
        ),
        "expected_context_corpus_sha256": (
            "11432A15C4EE5D21CE9924C01FB10A2BE8B8C482F0F7149C0F63A727520B20DB"
        ),
        "expected_gap_contract_sha256": (
            "D40040F5DE83793EDDA508AAED49F523230B6C9E7E996A91844A7ACB33745256"
        ),
        "expected_boundary_sha256": (
            "ECFA6E68DCE93D669D5BF69E955BB51B89C5372775DF38F4E8628FEE6C8A252C"
        ),
        "expected_runtime_control_sha256": (
            "22A4426E9AAD161EFF13CBCF542AF41EAE2099A200CFB3723326C99D76B59B01"
        ),
        "expected_base_search_sha256": (
            "AA130BDC2BFB9D7ACC82B4BDB02F8F91074CA50D49AE40A26AB31E33916CE8A1"
        ),
        "expected_complete_assembly_sha256": (
            "3DFA31A6C4AAC04351DE4003CCED49224C94163DBD9D92BBC42125456EDF5661"
        ),
        "expected_call_graph_sha256": (
            "E28E9BC7F532CEBC6108AEDE52B832ACE9F3031F704BCA2797257FA3441A1B48"
        ),
        "expected_speaker_style_sha256": (
            "AF80FF1E4C9DA0BE68D0A56DA789ACFF17722850BB94A328F65159C220F0A430"
        ),
        "expected_terminology_policy_sha256": (
            "7CF1E31C59AB40E50D4487183A236A6421795BB36FF5434A73205F07B4249956"
        ),
        "expected_translation_policy_sha256": (
            "A8EDD540EE6B099BC623A145B8EA00D1AD815F3565846027CBD2935913D3BBFC"
        ),
        "expected_candidate_sha256": (
            "B3A9E532A0B1936B1F890FFB9F4F942352F03288EED2B527CA8465251B0C761C"
        ),
        "expected_combined_slice_candidate_sha256": (
            "4CFBD85981C5E01175C4D74D865AA578D933F5495A5EB5412CBF5CEA4014BEFD"
        ),
        "expected_combined_changed_literal_count": 46,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B122_S1370",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1370.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1371.private.v1.jsonl",
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
    """Guard complete Base assemblies and the S1371 split record."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1370 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B122_S1371.private.v1.jsonl"
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
                    "segment 1370 reciprocal S1371 fragment drifted"
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
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
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
                f"segment 1370 Base search drifted: {record_id}"
            )
        donor_key = EXACT_BASE_DONOR[record_id]
        donor_coordinates = tuple(
            f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        references: list[tuple[Any, ...]] = []
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1370 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "complete_exact_assembly",
                "runtime_vm_not_inherited",
            ))
        donor_translations = tuple(
            str(base_rows[coordinate]["translation"])
            for coordinate in donor_coordinates
        )
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
                        f"segment 1370 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1370 incomplete record: {coordinate}"
                )
        if tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1370 exact assembly drifted: {record_id}"
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
            donor_translations,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if seen_target != target_set or seen_companion != companion_set:
        raise RuntimeError("segment 1370 assembly ownership drifted")
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
