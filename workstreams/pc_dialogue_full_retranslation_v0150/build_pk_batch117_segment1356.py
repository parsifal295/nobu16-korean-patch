#!/usr/bin/env python3
"""Build source-redacted PK B117 segment 1356 residual decisions."""

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
    "15:1069:2": "→",
    "15:1069:3": ")",
}
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B117_S1357"

TARGET_COORDINATES = (
    "15:1040:0",
    "15:1041:0",
    "15:1042:0",
    "15:1043:0",
    "15:1043:1",
    "15:1045:0",
    "15:1046:0",
    "15:1047:0",
    "15:1048:0",
    "15:1049:0",
    "15:1049:1",
    "15:1050:0",
    "15:1050:1",
    "15:1052:0",
    "15:1052:1",
    "15:1053:0",
    "15:1053:1",
    "15:1067:2",
    "15:1069:1",
)
TRANSLATIONS = {
    "15:1040:0": "실패 시,",
    "15:1041:0": "·",
    "15:1042:0": "·",
    "15:1043:0": "이(가)",
    "15:1043:1": "을(를) 편입",
    "15:1045:0": "을(를) 비롯한 총",
    "15:1046:0": "을(를) 등용",
    "15:1047:0": "을(를) 비롯한 총",
    "15:1048:0": "이(가) 우리 가문의 휘하로",
    "15:1049:0": "의 금전",
    "15:1049:1": "을(를) 접수",
    "15:1050:0": "의 병량",
    "15:1050:1": "을(를) 접수",
    "15:1052:0": "가보·",
    "15:1052:1": "을(를) 접수",
    "15:1053:0": "을(를) 편입하면\n",
    "15:1053:1": (
        "은(는) 도자마 가재에서 해임됩니다\n"
        "계속하시겠습니까?"
    ),
    "15:1067:2": "인가",
    "15:1069:1": "회복(",
}
TARGET_RECORD_IDS = (
    1040,
    1041,
    1042,
    1043,
    1045,
    1046,
    1047,
    1048,
    1049,
    1050,
    1052,
    1053,
    1067,
    1069,
)
EXPECTED_ARITY = {
    1040: 2,
    1041: 2,
    1042: 2,
    1043: 2,
    1045: 2,
    1046: 1,
    1047: 2,
    1048: 1,
    1049: 2,
    1050: 2,
    1052: 2,
    1053: 2,
    1067: 3,
    1069: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1040:1",
    "15:1041:1",
    "15:1042:1",
    "15:1045:1",
    "15:1047:1",
    "15:1067:0",
    "15:1067:1",
    "15:1069:0",
    *tuple(CROSS_TRANSLATIONS),
)
PREFILL_COMPANION_DONOR = {
    "15:1040:1": "15:1033:1",
    "15:1041:1": "15:1034:1",
    "15:1042:1": "15:1035:1",
    "15:1045:1": "15:714:1",
    "15:1047:1": "15:1040:1",
    "15:1067:0": "15:1059:0",
    "15:1067:1": "15:1059:1",
    "15:1069:0": "15:1061:0",
    **{
        coordinate: CROSS_DONOR_LABEL
        for coordinate in CROSS_TRANSLATIONS
    },
}
EXACT_BASE_DONOR = {
    1040: (15, 1033),
    1041: (15, 1034),
    1042: (15, 1035),
    1043: (15, 1036),
    1045: (15, 714),
    1046: (15, 715),
    1047: (15, 1040),
    1048: (15, 1041),
    1049: (15, 1042),
    1050: (15, 1043),
    1052: (15, 1045),
    1067: (15, 1059),
    1069: (15, 1061),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id != 1053
    },
    1053: (
        "6:4655:0",
        "6:4656:1",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    1040: ((15, 1033),),
    1041: ((15, 1034),),
    1042: ((15, 1035),),
    1043: ((15, 1036),),
    1045: ((15, 714), (15, 1038)),
    1046: ((15, 715), (15, 1039)),
    1047: ((15, 1040),),
    1048: ((15, 1041),),
    1049: ((15, 1042),),
    1050: ((15, 1043),),
    1052: ((15, 1045),),
    1053: (),
    1067: (),
    1069: ((15, 1061),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1048: ((6, 2786), (15, 1041)),
    1067: ((15, 1059),),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1067: ((15, 1059),),
}
EXPECTED_CONTROLS_BY_RECORD = {
    1040: ((), ("025032",)),
    1041: ((), ("023C",)),
    1042: ((), ("025032",)),
    1043: ((), ("025032", "025132")),
    1045: ((), ("024633", "0232")),
    1046: ((), ("024633",)),
    1047: ((), ("026432", "0232")),
    1048: ((), ("026432",)),
    1049: ((), ("025032", "0232")),
    1050: ((), ("025032", "0232")),
    1052: ((), ("028232",)),
    1053: ((), ("025032", "024833")),
    1067: ((178, 1138), ("026432",)),
    1069: ((), ("026432", "0232", "0233", "0234")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1356,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1029:0",
    slice_last="15:1069:1",
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
    source_call_roots=(178, 1138),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1020, 1082)
    ),
    speaker_style=(
        (1040, "system_integration_failure_warning"),
        (1041, "system_integration_success"),
        (1042, "system_integration_failure"),
        (1043, "system_faction_integration"),
        (1045, "system_employment_summary"),
        (1046, "system_employment_result"),
        (1047, "system_castle_submission_summary"),
        (1048, "system_castle_submission_result"),
        (1049, "system_gold_receipt"),
        (1050, "system_provisions_receipt"),
        (1052, "system_treasure_receipt"),
        (1053, "system_outside_conservator_warning"),
        (1067, "formal_castle_repair_proposal"),
        (1069, "system_durability_recovery"),
    ),
    terminology_policy=(
        ("integration", "편입"),
        ("territory", "영토"),
        ("employ", "등용"),
        ("subordinate", "휘하"),
        ("gold", "금전"),
        ("provisions", "병량"),
        ("treasure", "가보"),
        ("receive", "접수"),
        ("outside conservator", "도자마 가재"),
        ("durability", "내구"),
        ("restore", "회복"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("project middle dot", "·"),
        ("project arrow", "→"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; "
        "thirteen complete records reuse approved completed Base Korean "
        "assemblies selected by raw, literal and operand-masked source "
        "identity, while the PK-only outside-conservator warning is reviewed "
        "against completed Base conservator appointment terminology and the "
        "completed PK institutional corpus; Base runtime and VM state are "
        "never inherited; record 1069 includes the manually reviewed S1357 "
        "arrow and closing fragment and must reproduce completed Base record "
        "1061; integration, territory, employment, subordination, gold, "
        "provisions, treasures, receipts, the historical outside-conservator "
        "office, durability, recovery and dynamic particles retain project "
        "terminology; calls, inline person, faction, castle, number and "
        "treasure tokens, whitespace, newlines, terminators, complete record "
        "arity, all forty-eight slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "reciprocal optional neighbor decisions and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256": (
            "6178B2BC5D4B62D163E7C89A3D7BCBB80D5797E1E57C34FFFD1BA1B718D17558"
        ),
        "expected_queue_slice_sha256": (
            "81675D7CC3CF9E9F280A6A3CBD7ACCE35D464AD4BD9CC480A89BC1A0456454D5"
        ),
        "expected_prefilled_coordinate_sha256": (
            "316E1507F2D95E88E815A4F4401F08F0534A716BF89CAF00FE9435A41427D5CC"
        ),
        "expected_prefill_slice_context_sha256": (
            "89540E451F4B712DD9BCC054A4818CA56AEFBC71FB956D8B65487EFAD00BA6A9"
        ),
        "expected_target_coordinate_sha256": (
            "6A32B4AE08BCD0E82FB8192A46DEE1F0D9107C60A7184263C7B50838EDAA533D"
        ),
        "expected_source_target_sha256": (
            "A52578282A8961F0319250649B779A6F77CB56EE9AEC9465B4092CDF0E198D69"
        ),
        "expected_current_target_sha256": (
            "4C91167F679011EEFB034CBC6BD0B916E23B480EB1FAC3807EE8633991877237"
        ),
        "expected_context_corpus_sha256": (
            "D020BE9FCDAD08931F7FB9B3649273964303C7207D776E53561B29097BE3E246"
        ),
        "expected_gap_contract_sha256": (
            "49DD7E4F948AB3EBD687BA21BE26909667E5D71A8792FC4AD513F6015CDBD33E"
        ),
        "expected_boundary_sha256": (
            "4CC72DF78012873F54E29561D16BF80D0CB39E9E27D6AD4BF9C7A5557CDF8A09"
        ),
        "expected_runtime_control_sha256": (
            "EBE6BC8628E742257799D451645716703FBF4E9E8DAB78A743803A83F40B3E83"
        ),
        "expected_base_search_sha256": (
            "2FC5196C27E813D1438F68067D13578AA52C78D435854C2D59C67C78CD486FAF"
        ),
        "expected_complete_assembly_sha256": (
            "39C4B871BF2F272E1B806FAEBB040ABD27B23EA12275C8A588E3A6A46559A037"
        ),
        "expected_call_graph_sha256": (
            "4194BE7BA60316A8015E776005691CB38A6BC0C44D6C886E2299B7790C220FFF"
        ),
        "expected_speaker_style_sha256": (
            "4E99B543C8F69C9724EF23C932094377A3985FEA07B28E3658D32B76501033E9"
        ),
        "expected_terminology_policy_sha256": (
            "F0AC1B06D953318E10014857490E77B27DB2D9D1EE293305511A70D2AC620B4C"
        ),
        "expected_translation_policy_sha256": (
            "ECF5C0D8E0C84467787398075B2535EED63D5AF65407ECFC808ADD2BD52BDC2A"
        ),
        "expected_candidate_sha256": (
            "D95C530D63623DBB0D60A771D5CA60E99053F594163E40E1056BCDA82826CEFD"
        ),
        "expected_combined_slice_candidate_sha256": (
            "48E18E51F55D2066E12028A16F4B374317AB95EF093E9C411ED097CD448EA6C0"
        ),
        "expected_combined_changed_literal_count": 44,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B117_S1356",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1356.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1355.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1357.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B117",
    "queue_row_count": 121,
    "queue_visible_count": 198,
    "queue_first": "15:985:0",
    "queue_last": "15:1105:2",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard complete Base assemblies and the S1357 split record."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1356 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1357.private.v1.jsonl"
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
                    "segment 1356 reciprocal S1357 fragment drifted"
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
                f"segment 1356 Base search drifted: {record_id}"
            )
        exact = record_id in EXACT_BASE_DONOR
        donor_coordinates = (
            tuple(
                f"{EXACT_BASE_DONOR[record_id][0]}:"
                f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
            if exact
            else SEMANTIC_BASE_CONTEXT[record_id]
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
                    "segment 1356 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                (
                    "complete_exact_assembly"
                    if exact
                    else "semantic_only"
                ),
                "runtime_vm_not_inherited",
            ))
        donor_translations = (
            tuple(
                str(base_rows[coordinate]["translation"])
                for coordinate in donor_coordinates
            )
            if exact
            else None
        )
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append(
                    "segment_manual_exact_base_semantic_reuse"
                    if exact
                    else "segment_manual_multilingual"
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
                        f"segment 1356 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1356 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1356 exact assembly drifted: {record_id}"
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
            (
                "complete_exact_semantic_review"
                if exact
                else "semantic_context_only"
            ),
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
    if (
        seen_target != target_set
        or seen_companion != companion_set
    ):
        raise RuntimeError("segment 1356 assembly ownership drifted")
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
