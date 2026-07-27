#!/usr/bin/env python3
"""Build source-redacted PK B115 segment 1351 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

CROSS_COORDINATE = "15:817:0"
CROSS_TRANSLATION = "에서 벌인"

TARGET_RECORD_IDS = (
    817,
    818,
    819,
    821,
    831,
    832,
    834,
    847,
)
TARGET_COORDINATES = (
    "15:817:2",
    "15:818:0",
    "15:818:1",
    "15:818:2",
    "15:819:3",
    "15:821:1",
    "15:821:2",
    "15:831:0",
    "15:831:1",
    "15:832:0",
    "15:832:1",
    "15:832:2",
    "15:832:3",
    "15:834:0",
    "15:834:1",
    "15:834:2",
    "15:847:0",
)
TRANSLATIONS = {
    "15:817:2": "이(가) 부상",
    "15:818:0": "에서",
    "15:818:1": "이(가) 벌인",
    "15:818:2": "을(를) 저지",
    "15:819:3": "까 하옵니다",
    "15:821:1": "곳이며,\n",
    "15:821:2": "을(를) 비롯해 총",
    "15:831:0": "로부터",
    "15:831:1": "을(를) 받아\n",
    "15:832:0": "로부터",
    "15:832:1": "을(를) 받아\n",
    "15:832:2": "을(를) 비롯한 총",
    "15:832:3": "개 성에서\n잇키가 발생하여",
    "15:834:0": "의",
    "15:834:1": "으로(로)",
    "15:834:2": "을(를) 비롯한 총",
    "15:847:0": "·",
}
EXPECTED_ARITY = {
    817: 3,
    818: 3,
    819: 4,
    821: 5,
    831: 3,
    832: 4,
    834: 4,
    847: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:817:1",
    "15:819:0",
    "15:819:1",
    "15:819:2",
    "15:821:0",
    "15:821:3",
    "15:821:4",
    "15:831:2",
    "15:834:3",
    "15:847:1",
)
PREFILL_COMPANION_DONOR = {
    "15:817:1": "15:810:1",
    "15:819:0": "15:812:0",
    "15:819:1": "15:812:1",
    "15:819:2": "15:812:2",
    "15:821:0": "15:814:0",
    "15:821:3": "15:814:3",
    "15:821:4": "15:814:4",
    "15:831:2": "15:824:2",
    "15:834:3": "15:827:3",
    "15:847:1": "15:840:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ()
BASE_CONTEXT_DONOR = {
    817: (15, 810),
    818: (15, 811),
    819: (15, 812),
    821: (15, 814),
    831: (15, 824),
    832: (15, 825),
    834: (15, 827),
    847: (15, 840),
}
EXACT_BASE_DONOR = {
    record_id: donor
    for record_id, donor in BASE_CONTEXT_DONOR.items()
    if record_id not in {832, 834}
}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, donor in BASE_CONTEXT_DONOR.items()
}
EXPECTED_BASE_RAW_MATCHES = {
    817: ((15, 810), (15, 1358), (15, 1447)),
    818: (
        (15, 811),
        (15, 980),
        (15, 1286),
        (15, 1362),
        (15, 1454),
    ),
    819: (),
    821: (),
    831: (),
    832: (),
    834: (),
    847: ((15, 840),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    819: ((15, 812),),
    821: ((15, 814),),
    831: ((15, 824),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    817: ((), ("026432", "023C", "024633")),
    818: ((), ("026432", "025032", "023C")),
    819: ((538, 1126, 1048), ("026432",)),
    821: ((538, 1126), ("0233", "026432", "0232")),
    831: ((538,), ("025032", "023C", "026432")),
    832: ((538,), ("025032", "023C", "026432", "0232")),
    834: ((), ("025032", "023C", "026432", "0232")),
    847: ((), ("029632",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1351,
    queue_start=134,
    queue_stop=199,
    slice_first="15:817:1",
    slice_last="15:866:1",
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
        538,
        1048,
        1126,
    ),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(805, 875)
    ),
    speaker_style=(
        (817, "system_operation_failure_with_injury"),
        (818, "system_operation_prevention"),
        (819, "formal_uprising_incitement_proposal"),
        (821, "formal_multi_castle_incitement_report"),
        (831, "system_uprising_trigger_report"),
        (832, "system_multi_castle_uprising_trigger_report"),
        (834, "system_multi_castle_uprising_summary"),
        (847, "concise_bulleted_uprising_report"),
    ),
    terminology_policy=(
        ("castle", "성"),
        ("uprising", "잇키"),
        ("agitation or incitement", "선동"),
        ("suppression", "진압"),
        ("operation prevention", "저지"),
        ("operation failure", "실패"),
        ("injury", "부상"),
        ("including counted castles", "을(를) 비롯한 총"),
        ("castle counter", "개 성"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic directional particle", "으로(로)"),
        ("project middle dot", "·"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B115 queue ordinals 134 through 198 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; six records reuse approved completed "
        "Base Korean assemblies selected by raw, literal and operand-masked "
        "source identity, while records 832 and 834 adapt completed Base "
        "multi-castle wording to their distinct count tokens and line break; "
        "record 817 is completed with the manually reviewed S1350 operation "
        "fragment and is reciprocally validated when that decision exists; "
        "Base runtime and VM state are never inherited; castles, uprisings, "
        "incitement, suppression, prevention, injury, counted-castle "
        "phrasing and formal proposal registers retain established project "
        "terminology; direct calls, inline castle, faction, operation, "
        "person and number tokens, protected outer whitespace, newlines, "
        "gaps, literal arity, terminators, all ten same-record prefills, all "
        "forty-eight slice prefills, complete assemblies, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=12,
    pins={
        "expected_queue_universe_sha256": (
            "D9F766CAA805AA167D8C09773CD0A666B92E68767EAD94B3AA2EC0B9284AE4AD"
        ),
        "expected_queue_slice_sha256": (
            "9D7721C0213426F140DCE645C309C172AD7E09C8DF8AE16BC60D4A47A64F07A8"
        ),
        "expected_prefilled_coordinate_sha256": (
            "A06CBD4ED5009BEA90D6F77D82152FEBC02FB9255146B5DF2ECD1731CD312C9F"
        ),
        "expected_prefill_slice_context_sha256": (
            "45534850178FB3C3DE1B9B839BABE5AF41537E8D9163691FA965C9E494A3A022"
        ),
        "expected_target_coordinate_sha256": (
            "7EBFB85BEBA0BAF5099B9CCC7CFB269647F3D0CA34FDEF8832D37659AE9C98F2"
        ),
        "expected_source_target_sha256": (
            "4164E911EFA4D8EE29F01557CC4474718B42AA46BDF28C536584A8A4AE06DDAB"
        ),
        "expected_current_target_sha256": (
            "982CC72A00564064D4A4B861C8BC3CA0015DFA9BD30F078664570B3ACFEFD3C9"
        ),
        "expected_context_corpus_sha256": (
            "772FD0363F937E84A0616D73BFBFA06C5A93975F5B62740B948226EAF9D84722"
        ),
        "expected_gap_contract_sha256": (
            "D527A22B79D23FBCD03D9B5671EDA239645DE27B4C53C6587A4C7C5249A1D118"
        ),
        "expected_boundary_sha256": (
            "E0E22A34C2B8783513601212EB6D982D7E3DA546D5C3DF79657E55952DBDA828"
        ),
        "expected_runtime_control_sha256": (
            "901E86C5E6403DA12BC53E65D18111CBD47044B244A39698B142EAD498BE3F83"
        ),
        "expected_base_search_sha256": (
            "6A7F38E24A7BC6E85249CD1A84DE82791D1EF7007183149EFC096AE2BC07128D"
        ),
        "expected_complete_assembly_sha256": (
            "D40CC34CE1B57890FFA1FBDB6FAE51D596F4601915328BA6C07EBADEF50E012F"
        ),
        "expected_call_graph_sha256": (
            "978F84828D6A5DE83A684ABC15BA6FB169F873148B46A4013AA17AA262970FC9"
        ),
        "expected_speaker_style_sha256": (
            "52B1C78695A1C461DCBEBF38A8E24B950B9A87A8BD7D0240EAC8784BF522400E"
        ),
        "expected_terminology_policy_sha256": (
            "B8C30A922572C75DA54D497221DA4D63E23BC0F4275A3A4BD078A0436DA999BD"
        ),
        "expected_translation_policy_sha256": (
            "386F67B55AD683CAEB6D1A133BEADE5D86A53DB35B77A9397B8F929F47453146"
        ),
        "expected_candidate_sha256": (
            "842167822CC508121ADDA99D7CDC41FC564A20AF62F05F6918866F4154996402"
        ),
        "expected_combined_slice_candidate_sha256": (
            "E84DBCAB1DAF7A81285167622845067A879EB388B426A9981A72853B2B021CBD"
        ),
        "expected_combined_changed_literal_count": 52,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B115_S1351",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1351.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1349.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1350.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B115",
    "queue_row_count": 136,
    "queue_visible_count": 199,
    "queue_first": "15:731:0",
    "queue_last": "15:866:1",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard exact, adapted and cross-segment complete assemblies."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1351 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1350.private.v1.jsonl"
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
                "segment 1351 reciprocal S1350 fragment drifted"
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
    seen_cross = False
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
                f"segment 1351 Base search drifted: {record_id}"
            )
        exact = record_id in EXACT_BASE_DONOR
        donor_coordinates = SEMANTIC_BASE_CONTEXT[record_id]
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
                    "segment 1351 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "complete_exact_assembly" if exact else "semantic_only",
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
            elif coordinate == CROSS_COORDINATE:
                assembled.append(CROSS_TRANSLATION)
                owners.append(
                    "neighbor_segment_manual_runtime_pending"
                )
                seen_cross = True
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
                        f"segment 1351 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1351 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1351 exact assembly drifted: {record_id}"
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
        or not seen_cross
    ):
        raise RuntimeError("segment 1351 assembly ownership drifted")
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
