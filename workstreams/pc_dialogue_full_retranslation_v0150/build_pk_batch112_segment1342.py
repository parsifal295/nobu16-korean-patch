#!/usr/bin/env python3
"""Build source-redacted PK B112 segment 1342 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

CROSS_COORDINATE = "15:473:0"
CROSS_TRANSLATION = "큰일"
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B112_S1341"

TARGET_COORDINATES = (
    "15:473:1",
    "15:473:2",
    "15:473:3",
    "15:473:4",
    "15:473:5",
    "15:474:1",
    "15:474:2",
    "15:474:5",
    "15:475:1",
    "15:475:2",
    "15:475:5",
    "15:476:1",
    "15:476:2",
    "15:476:5",
    "15:477:1",
    "15:477:2",
    "15:477:5",
    "15:478:1",
    "15:478:2",
    "15:478:5",
    "15:479:1",
    "15:479:2",
    "15:479:5",
    "15:480:1",
    "15:480:2",
    "15:480:5",
    "15:481:1",
    "15:481:2",
    "15:481:5",
    "15:482:1",
    "15:482:2",
    "15:482:5",
    "15:483:1",
    "15:483:2",
    "15:483:5",
)
TRANSLATIONS = {
    "15:473:1": "!\n",
    "15:473:2": "의",
    "15:473:3": "이(가)\n",
    "15:473:4": "에 귀순하",
    "15:473:5": "!",
    "15:474:1": "!\n",
    "15:474:2": "의",
    "15:474:5": "!",
    "15:475:1": "!\n",
    "15:475:2": "의",
    "15:475:5": "!",
    "15:476:1": "!\n",
    "15:476:2": "의",
    "15:476:5": "!",
    "15:477:1": "!\n",
    "15:477:2": "의",
    "15:477:5": "!",
    "15:478:1": "!\n",
    "15:478:2": "의",
    "15:478:5": "!",
    "15:479:1": "!\n",
    "15:479:2": "의",
    "15:479:5": "!",
    "15:480:1": "!\n",
    "15:480:2": "의",
    "15:480:5": "!",
    "15:481:1": "!\n",
    "15:481:2": "의",
    "15:481:5": "!",
    "15:482:1": "!\n",
    "15:482:2": "의",
    "15:482:5": "!",
    "15:483:1": "!\n",
    "15:483:2": "의",
    "15:483:5": "!",
}
TARGET_RECORD_IDS = tuple(range(473, 484))
EXPECTED_ARITY = {record_id: 6 for record_id in TARGET_RECORD_IDS}
PREFILL_COMPANION_COORDINATES = (
    CROSS_COORDINATE,
    *tuple(
        f"15:{record_id}:{literal_id}"
        for record_id in range(474, 484)
        for literal_id in (0, 3, 4)
    ),
)
PREFILL_COMPANION_DONOR = {
    CROSS_COORDINATE: CROSS_DONOR_LABEL,
    **{
        f"15:{record_id}:{literal_id}": f"15:467:{literal_id}"
        for record_id in range(474, 484)
        for literal_id in (0, 3, 4)
    },
}
EXACT_BASE_DONOR = {
    473: (15, 466),
    **{record_id: (15, 467) for record_id in range(474, 484)},
}
SEMANTIC_BASE_CONTEXT = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
REPEATED_BASE_MATCHES = tuple(
    (15, record_id) for record_id in range(467, 478)
)
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    473: ((15, 466),),
    **{
        record_id: REPEATED_BASE_MATCHES
        for record_id in range(474, 484)
    },
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    473: ((562, 628), ("023C", "024833", "025032")),
    **{
        record_id: ((82, 550), ("023C", "024833", "025032"))
        for record_id in range(474, 484)
    },
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1342,
    queue_start=134,
    queue_stop=199,
    slice_first="15:473:1",
    slice_last="15:483:5",
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
    source_call_roots=(82, 550, 562, 628),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(462, 495)
    ),
    speaker_style=(
        (473, "urgent_defection_alert"),
        *tuple(
            (record_id, "urgent_betrayal_report")
            for record_id in range(474, 484)
        ),
    ),
    terminology_policy=(
        ("grave event", "큰일"),
        ("clan", "우리 가문"),
        ("abandon", "저버리다"),
        ("defect", "귀순"),
        ("dynamic possessive particle", "의"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic destination particle", "에"),
        ("project exclamation mark", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; all "
        "eleven complete records reuse approved completed Base Korean "
        "assemblies selected by literal and operand-masked source identity; "
        "Base runtime and VM state are never inherited; the record 473 "
        "assembly includes the manually reviewed S1341 opening fragment and "
        "is required to reproduce the complete Base record 466 assembly; "
        "the ten repeated betrayal reports reproduce completed Base record "
        "467 with their own PK call operands and inline tokens preserved; "
        "grave event, clan, abandonment, defection, possessive, subject and "
        "destination particles and punctuation retain completed Base usage; "
        "calls, inline person and faction tokens, newlines, terminators, "
        "complete record arity, all thirty slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=24,
    pins={
        "expected_queue_universe_sha256": (
            "00816F7C9CDC6EEFA665DCA237BA363079B38464F390EAA2965D45F824A7B70F"
        ),
        "expected_queue_slice_sha256": (
            "E68C1A3A79716238CDBFE3652C1BE194C97B4373F6CB08AF8C3A7E5DC60828CB"
        ),
        "expected_prefilled_coordinate_sha256": (
            "473AF33DBD2D8B5B9CB12E57D34EF230340C25213158009BF423C85BC231D47E"
        ),
        "expected_prefill_slice_context_sha256": (
            "5C577DB3AF5B77C75653DBDF7B260A30D582E5D7E3F7CA5A6EEE709C91578E13"
        ),
        "expected_target_coordinate_sha256": (
            "0E78303ECBFA640485F4E6D45B86F259122FF01DB7D5442F41E05744ADD9D06C"
        ),
        "expected_source_target_sha256": (
            "0ECE50EC29A6EEE79CA1A0EB94AE6C9A8B3A32A398AFCD93D1B82718F3E120B3"
        ),
        "expected_current_target_sha256": (
            "8A8DB5166DC9EF96886793C5BAC57310C61D15A23E9EC4F6E849F61F79D456A8"
        ),
        "expected_context_corpus_sha256": (
            "832A97B189A998FB791066F3824D741370CF822E6BF32123E42917B9ED92B763"
        ),
        "expected_gap_contract_sha256": (
            "EC599DAEA0154CA8DBA95B1A17420EE239E18F87EF5F1A5194F15F62B4B626D0"
        ),
        "expected_boundary_sha256": (
            "86438D3E5DD83884F3A7018F58D726A6D398D41434BB908BFE3594B438A878FA"
        ),
        "expected_runtime_control_sha256": (
            "228D838AA2BD3017716CECCDAD57E692DABE9065C57F16E2BB2814596C3DE477"
        ),
        "expected_base_search_sha256": (
            "89E0E49AFB6F78DC656BB854966E53FE4B5610880EFB07DD84B76B3B41D700C6"
        ),
        "expected_complete_assembly_sha256": (
            "CBF6F0C43F7F5F41125136C34B3EE981CA27AFA6C8114D5D4CA9F99FA5629F53"
        ),
        "expected_call_graph_sha256": (
            "11CD390B2E6DD123F3DC4901C029D549B3B1C1162ABC7E2D0BCA6643CF3C470E"
        ),
        "expected_speaker_style_sha256": (
            "66A2796C5321342BF4D460766C68F3C18E41DEA64F9D0BBE4DB3EB60EF74DC28"
        ),
        "expected_terminology_policy_sha256": (
            "5EAABE28AECBCA9383949500DA74C25397EF342CC69E5EAAD44ED8D3BD0B95AD"
        ),
        "expected_translation_policy_sha256": (
            "A7C2571B11885EBAE499CE690AE4F0613E5472D9307A788975BE096E9F33C874"
        ),
        "expected_candidate_sha256": (
            "617A8B62D06BB8B0D3CDBDF2C757BA347EC296B9242B47CE52FD073531583DF4"
        ),
        "expected_combined_slice_candidate_sha256": (
            "7E556B7D31DFCDEBC9004D9438605BE830974433836758112DA8C0173A4E77E1"
        ),
        "expected_combined_changed_literal_count": 54,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B112_S1342",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1342.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1340.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1341.private.v1.jsonl",
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
    """Guard exact Base assemblies and the S1341 boundary fragment."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1342 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B112_S1341.private.v1.jsonl"
    )
    if neighbor_path.is_file():
        neighbor_rows = {
            str(row["coordinate"]): row
            for row in COMMON.read_jsonl(neighbor_path)
        }
        neighbor = neighbor_rows.get(CROSS_COORDINATE)
        if (
            neighbor is None
            or neighbor.get("resource") != "pk_msggame"
            or neighbor.get("semantic_review") != "approved"
            or neighbor.get("runtime_review") != "pending"
            or str(neighbor.get("translation")) != CROSS_TRANSLATION
        ):
            raise RuntimeError(
                "segment 1342 reciprocal S1341 fragment drifted"
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
                f"segment 1342 Base search drifted: {record_id}"
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
                    "segment 1342 Base context drifted: "
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
            elif coordinate == CROSS_COORDINATE:
                assembled.append(CROSS_TRANSLATION)
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
                        f"segment 1342 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1342 incomplete record: {coordinate}"
                )
        if tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1342 exact assembly drifted: {record_id}"
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
    ):
        raise RuntimeError("segment 1342 assembly ownership drifted")
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
