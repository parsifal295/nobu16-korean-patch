#!/usr/bin/env python3
"""Build source-redacted PK B112 segment 1341 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

TARGET_COORDINATES = (
    "15:442:1",
    "15:444:0",
    "15:471:0",
    "15:472:0",
    "15:473:0",
)
TRANSLATIONS = {
    "15:442:1": "(이)라네\n",
    "15:444:0": "(이)다\n",
    "15:471:0": "·",
    "15:472:0": "·",
    "15:473:0": "큰일",
}
TARGET_RECORD_IDS = (
    442,
    444,
    471,
    472,
    473,
)
EXPECTED_ARITY = {
    442: 3,
    444: 2,
    471: 2,
    472: 2,
    473: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "15:442:0",
    "15:442:2",
    "15:444:1",
    "15:471:1",
    "15:472:1",
)
PREFILL_COMPANION_DONOR = {
    "15:442:0": "15:435:0",
    "15:442:2": "15:435:2",
    "15:444:1": "15:437:1",
    "15:471:1": "15:464:1",
    "15:472:1": "15:464:1",
}
CROSS_SEGMENT_TRANSLATIONS = {
    "15:473:1": "!\n",
    "15:473:2": "의",
    "15:473:3": "이(가)\n",
    "15:473:4": "에 귀순하",
    "15:473:5": "!",
}
EXACT_BASE_DONOR = {
    442: (15, 435),
    444: (15, 437),
    471: (15, 464),
    472: (15, 464),
    473: (15, 466),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    442: ((15, 435),),
    444: ((15, 437),),
    471: ((15, 464), (15, 465)),
    472: ((15, 464), (15, 465)),
    473: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    473: ((15, 466),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    442: ((17,), ("024633",)),
    444: ((17,), ("024633",)),
    471: ((), ("024633",)),
    472: ((), ("024633",)),
    473: ((562, 628), ("023C", "024833", "025032")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1341,
    queue_start=67,
    queue_stop=134,
    slice_first="15:440:2",
    slice_last="15:473:0",
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
    source_call_roots=(17, 562, 628),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(430, 485)
    ),
    speaker_style=(
        (442, "male_archaic_service_pledge"),
        (444, "male_confident_service_pledge"),
        (471, "neutral_recruitment_failure_log"),
        (472, "neutral_recruitment_failure_log"),
        (473, "urgent_defection_report"),
    ),
    terminology_policy=(
        ("enter service", "신세를 지다"),
        ("dynamic copula", "(이)라네"),
        ("dynamic copula plain", "(이)다"),
        ("placate", "회유"),
        ("defect", "귀순"),
        ("urgent report", "큰일"),
        ("project middle dot", "·"),
        ("project exclamation mark", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; all "
        "five complete records reuse approved completed Base Korean "
        "assemblies, including the split record whose remaining five literals "
        "belong to S1342; Base runtime and VM state are never inherited; "
        "dynamic person and faction calls retain their source ordering, "
        "copulas and particles remain explicit, and service, placation, "
        "defection, urgent-report, middle-dot and exclamation wording retains "
        "the completed Base register and project punctuation; calls, inline "
        "tokens, leading and trailing newlines, terminators, complete record "
        "arity, all sixty-two slice prefills, the S1342 reciprocal companion "
        "contract, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, optional neighbor decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=3,
    pins={
        "expected_queue_universe_sha256": (
            "00816F7C9CDC6EEFA665DCA237BA363079B38464F390EAA2965D45F824A7B70F"
        ),
        "expected_queue_slice_sha256": (
            "EEA157E1EAC56AE26C1F28DD5E5E84785E6E3DA63BDE07FDD5BCD8AB70269167"
        ),
        "expected_prefilled_coordinate_sha256": (
            "F521763AA016AF4C00CEF03C942DE31978F4AE8314BFBC1DCB1835D36D07F9AD"
        ),
        "expected_prefill_slice_context_sha256": (
            "7A78757DD1476D98BDCE19CA564904F7F2F041AE7F12BF7EF61A8003B7AE9927"
        ),
        "expected_target_coordinate_sha256": (
            "6DE2FED3D398D9E7DABB17B239754874873A4C4B10CF764B6B1E6F1ADDC20C80"
        ),
        "expected_source_target_sha256": (
            "CE1E4342AF02CAA7086BB94D2BF08FDCFB350C149CBEAAC32153C1A733A0CAE1"
        ),
        "expected_current_target_sha256": (
            "8BAA735F65281524812AF84122339E708C35B023D855FCC42970E0660C111188"
        ),
        "expected_context_corpus_sha256": (
            "832A97B189A998FB791066F3824D741370CF822E6BF32123E42917B9ED92B763"
        ),
        "expected_gap_contract_sha256": (
            "E833BFFA06B79A853B4BA7E92A1CA6603EB1979A958A0B17DC96A00CDD1BE7A1"
        ),
        "expected_boundary_sha256": (
            "161B6CEDDB929A191D9A1008A3074949E597344C1FC12D83D196FDC56B4A2574"
        ),
        "expected_runtime_control_sha256": (
            "2E518D8646B253E1133B14E081587E1DA5884322211102EBE2155AB877A12C13"
        ),
        "expected_base_search_sha256": (
            "D54B2C26A90D4B0D9E4C5B05FD597F28E95010743290504C13D209A5BB805AD6"
        ),
        "expected_complete_assembly_sha256": (
            "6E650328B23916BD3639563D2F6493F8352258AC4CAE750223F3DC985925BA71"
        ),
        "expected_call_graph_sha256": (
            "B93F5C555312305119CE434269CD63254A73F602BC0148A738075B405D038ED0"
        ),
        "expected_speaker_style_sha256": (
            "EEE6AACB389526CB1DBC935C1D48A8797F74968B713B181974E55118DCD1FAA0"
        ),
        "expected_terminology_policy_sha256": (
            "D2A680E7AF0FC426D62C41E5F06BF96075EED6251B5C4F8545368926198D7CF0"
        ),
        "expected_translation_policy_sha256": (
            "53AB6CF28A0FF1CC26D41C1BC212B236A5AB611C47CEEE0A76C93A5904CF076B"
        ),
        "expected_candidate_sha256": (
            "2E613C3FDF0D697AA946F6FC5FE0D55EAB082F60FE955245F92FE8B4B85F54E2"
        ),
        "expected_combined_slice_candidate_sha256": (
            "00E65BF00342AB0849ACBD84DD3B790EEA2F26B483CC0D3F5A13E8753B740FC5"
        ),
        "expected_combined_changed_literal_count": 53,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B112_S1341",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1341.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1340.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1342.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B112",
    "queue_row_count": 89,
    "queue_visible_count": 199,
    "queue_first": "15:395:0",
    "queue_last": "15:483:5",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard exact Base assemblies and the split S1341/S1342 record."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1341 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1342.private.v1.jsonl"
    )
    if neighbor_path.is_file():
        neighbor_rows = {
            str(row["coordinate"]): row
            for row in COMMON.read_jsonl(neighbor_path)
        }
        for coordinate, translation in CROSS_SEGMENT_TRANSLATIONS.items():
            neighbor = neighbor_rows.get(coordinate)
            if (
                neighbor is None
                or neighbor.get("semantic_review") != "approved"
                or str(neighbor.get("translation")) != translation
                or neighbor.get("base_runtime_state_inherited") is not False
            ):
                raise RuntimeError(
                    "segment 1341 reciprocal S1342 companion drifted: "
                    f"{coordinate}"
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
    cross_set = set(CROSS_SEGMENT_TRANSLATIONS)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_cross: set[str] = set()
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
            if COMMON.literal_texts(base_source, coordinate) == source_literals
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
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1341 Base search drifted: {record_id}"
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
                    "segment 1341 Base context drifted: "
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
                owners.append("segment_manual_exact_base_semantic_reuse")
                seen_target.add(coordinate)
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
                        f"segment 1341 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in cross_set:
                assembled.append(CROSS_SEGMENT_TRANSLATIONS[coordinate])
                owners.append("neighbor_segment_manual_runtime_pending")
                seen_cross.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1341 incomplete record: {coordinate}"
                )
        if tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1341 exact assembly drifted: {record_id}"
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
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_cross != cross_set
    ):
        raise RuntimeError("segment 1341 assembly ownership drifted")
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
