#!/usr/bin/env python3
"""Build source-redacted PK B115 segment 1350 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

CROSS_COORDINATE = "15:817:2"
CROSS_TRANSLATION = "이(가) 부상"
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B115_S1351"
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:779:2",)

TARGET_COORDINATES = (
    "15:777:0",
    "15:777:2",
    "15:778:0",
    "15:778:2",
    "15:779:0",
    "15:780:1",
    "15:781:0",
    "15:806:0",
    "15:813:0",
    "15:813:1",
    "15:813:2",
    "15:814:0",
    "15:814:1",
    "15:814:2",
    "15:815:0",
    "15:815:1",
    "15:815:2",
    "15:816:0",
    "15:816:1",
    "15:816:2",
    "15:817:0",
)
TRANSLATIONS = {
    "15:777:0": "·",
    "15:777:2": "상승\n·",
    "15:778:0": "·",
    "15:778:2": "상승\n·",
    "15:779:0": "의",
    "15:780:1": "상승",
    "15:781:0": "을(를) 비롯해 총",
    "15:806:0": "지금이야말로",
    "15:813:0": "이(가)",
    "15:813:1": "에서 벌인",
    "15:813:2": "에 성공",
    "15:814:0": "이(가)",
    "15:814:1": "을(를) 비롯한 여러 성에서 벌인",
    "15:814:2": "에 성공",
    "15:815:0": "을(를) 비롯한 총",
    "15:815:1": "개 성에서",
    "15:815:2": "에 성공",
    "15:816:0": "이(가)",
    "15:816:1": "에서 벌인",
    "15:816:2": "에 실패",
    "15:817:0": "에서 벌인",
}
TARGET_RECORD_IDS = (
    777,
    778,
    779,
    780,
    781,
    806,
    813,
    814,
    815,
    816,
    817,
)
EXPECTED_ARITY = {
    777: 4,
    778: 4,
    779: 3,
    780: 2,
    781: 2,
    806: 2,
    813: 3,
    814: 3,
    815: 3,
    816: 3,
    817: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:777:1",
    "15:777:3",
    "15:778:1",
    "15:778:3",
    "15:779:1",
    "15:780:0",
    "15:781:1",
    "15:806:1",
    "15:817:1",
    CROSS_COORDINATE,
)
PREFILL_COMPANION_DONOR = {
    "15:777:1": "15:770:1",
    "15:777:3": "15:770:3",
    "15:778:1": "15:770:1",
    "15:778:3": "15:770:3",
    "15:779:1": "15:772:1",
    "15:780:0": "15:773:0",
    "15:781:1": "15:774:1",
    "15:806:1": "15:799:1",
    "15:817:1": "15:810:1",
    CROSS_COORDINATE: CROSS_DONOR_LABEL,
}
EXACT_BASE_DONOR = {
    777: (15, 770),
    778: (15, 770),
    779: (15, 772),
    780: (15, 773),
    781: (15, 774),
    806: (15, 799),
    813: (15, 806),
    814: (15, 807),
    815: (15, 808),
    816: (15, 809),
    817: (15, 810),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    777: ((15, 770), (15, 771)),
    778: ((15, 770), (15, 771)),
    779: (),
    780: ((15, 773),),
    781: ((15, 774),),
    806: (),
    813: ((15, 806), (15, 1357), (15, 1445)),
    814: ((15, 807),),
    815: ((15, 808),),
    816: ((15, 809),),
    817: ((15, 810), (15, 1358), (15, 1447)),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    779: ((15, 772),),
    806: ((15, 799),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    777: ((), ("026432", "0232", "026432", "0233050505")),
    778: ((), ("026432", "0232", "026432", "0233050505")),
    779: ((568,), ("026433", "026432")),
    780: ((), ("026432", "0232")),
    781: ((), ("029632", "0232")),
    806: ((1126,), ("026432",)),
    813: ((), ("024633", "026432", "023C")),
    814: ((), ("024633", "026432", "023C")),
    815: ((), ("026432", "0232", "023C")),
    816: ((), ("024633", "026432", "023C")),
    817: ((), ("026432", "023C", "024633")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1350,
    queue_start=67,
    queue_stop=134,
    slice_first="15:774:0",
    slice_last="15:817:0",
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
    source_call_roots=(568, 1126),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(760, 829)
    ),
    speaker_style=(
        (777, "system_mobilization_effect"),
        (778, "system_mobilization_effect"),
        (779, "formal_conscription_report"),
        (780, "system_troop_increase"),
        (781, "system_settlement_control_release"),
        (806, "forceful_agitation_proposal"),
        (813, "system_operation_success"),
        (814, "system_multi_castle_operation_success"),
        (815, "system_counted_castle_operation_success"),
        (816, "system_operation_failure"),
        (817, "system_operation_failure_with_injury"),
    ),
    terminology_policy=(
        ("troops", "병력"),
        ("county", "군"),
        ("popular loyalty", "민충"),
        ("conscription", "징병"),
        ("settlement", "취락"),
        ("control", "장악"),
        ("castle", "성"),
        ("agitate", "선동"),
        ("enemy territory", "적 영지"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic counter", "총"),
        ("project middle dot", "·"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; all "
        "eleven complete records reuse approved completed Base Korean "
        "assemblies selected by raw, literal and operand-masked source "
        "identity; Base runtime and VM state are never inherited; the record "
        "779 assembly preserves its source-identical hidden empty terminator "
        "fragment, and record 817 includes the manually reviewed S1351 "
        "injury fragment; ambiguous duplicate operation records select the "
        "natural completed Base assemblies that place operations at castles "
        "and retain general dynamic particles; troops, counties, popular "
        "loyalty, conscription, settlements, control, castles, agitation, "
        "enemy territory, counters and system punctuation retain established "
        "historical terminology; calls, inline person, county, castle, "
        "operation and number tokens, whitespace, newlines, terminators, "
        "complete record arity, all forty-six slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=10,
    pins={
        "expected_queue_universe_sha256": (
            "D9F766CAA805AA167D8C09773CD0A666B92E68767EAD94B3AA2EC0B9284AE4AD"
        ),
        "expected_queue_slice_sha256": (
            "C7BD268B24AFEA17E63D52E3F0B946CBA5715D2A85C6FE5F89952252644FE469"
        ),
        "expected_prefilled_coordinate_sha256": (
            "120F10E3AFD4556A7A52185C21DF5920CF1B1EA26F112B4E82A2FDB98C65CDA4"
        ),
        "expected_prefill_slice_context_sha256": (
            "60F2A82F58FB2E039CBF79EC587137B0F60B9BC618ED652DECE9D9C6ADC06699"
        ),
        "expected_target_coordinate_sha256": (
            "979B7DF9E5F297810FDE214115464FB5871CFA203A17B214EE1EFE2E49C264B1"
        ),
        "expected_source_target_sha256": (
            "5114988BA456E3D292D4BE6E8E839A90D91E95E0CC417E7024B9EFEA30A586F5"
        ),
        "expected_current_target_sha256": (
            "7076D9644C642EC69390838EDCB93A113D5005C68DA98095AB68573A91278EE8"
        ),
        "expected_context_corpus_sha256": (
            "772FD0363F937E84A0616D73BFBFA06C5A93975F5B62740B948226EAF9D84722"
        ),
        "expected_gap_contract_sha256": (
            "E7AA379792EDAEC5CE8D5C26F10A346ACDEEC308FA87A3F60C6F632BF76040D8"
        ),
        "expected_boundary_sha256": (
            "34C2E440B74B169F2103C84FBE58715FE278D6490F6976670D709FBB1B37C9A7"
        ),
        "expected_runtime_control_sha256": (
            "2EFF570688F3F187992301CFF0B43A3EA1F4EE5EC1222308CDC7A2A179F4773A"
        ),
        "expected_base_search_sha256": (
            "192A8C365D52BB63299B05B97082D69407F81BC4C5DDCCB742DB086E1984DC95"
        ),
        "expected_complete_assembly_sha256": (
            "2FF5E6754B46D7D17545AA71B692FF08962569CB40A5BFADD638A24B2C736877"
        ),
        "expected_call_graph_sha256": (
            "C196AF14C68F9CB6FB892F9EB0A415870C799957F701CF0D0D5B765283D822B3"
        ),
        "expected_speaker_style_sha256": (
            "FE0C9A08B12C24083DF367295BC047663C008D1B89C523A985F5E7E6970C88AE"
        ),
        "expected_terminology_policy_sha256": (
            "F49F0595CFECA6E88367A87040289D6BC6F6838BAAA556B0A79D3CCC5F3C15DB"
        ),
        "expected_translation_policy_sha256": (
            "65433BBCBB1059607AE489F31AC32FA222453398E2EE92D9712EF40AF0AF0F76"
        ),
        "expected_candidate_sha256": (
            "935DE8511D1670E5924E0D0085B22FEFCA6D61BA677F541C6D78339FB2F60EA2"
        ),
        "expected_combined_slice_candidate_sha256": (
            "31DFB78770546CCC214701660735D7567A8D2526EE5868CF2391899EBB24407B"
        ),
        "expected_combined_changed_literal_count": 48,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B115_S1350",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1350.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1349.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1351.private.v1.jsonl",
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
    """Guard exact Base assemblies and split or invisible fragments."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1350 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B115_S1351.private.v1.jsonl"
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
                "segment 1350 reciprocal S1351 fragment drifted"
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
                f"segment 1350 Base search drifted: {record_id}"
            )
        donor_key = EXACT_BASE_DONOR[record_id]
        donor_coordinates = tuple(
            f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        references: list[tuple[Any, ...]] = []
        donor_translations: list[str] = []
        for literal_id, donor_coordinate in enumerate(
            donor_coordinates
        ):
            donor = base_rows.get(donor_coordinate)
            if donor is not None:
                if (
                    donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        "segment 1350 Base context drifted: "
                        f"{donor_coordinate}"
                    )
                donor_translation = str(donor["translation"])
                references.append((
                    donor_coordinate,
                    donor_translation,
                    str(donor["semantic_review"]),
                    str(donor["runtime_review"]),
                    "complete_exact_assembly",
                    "runtime_vm_not_inherited",
                ))
                donor_translations.append(donor_translation)
            elif (
                record_id == 779
                and literal_id == 2
                and source_literals[literal_id] == ""
                and current_literals[literal_id] == ""
            ):
                references.append((
                    donor_coordinate,
                    "",
                    "not_translatable_blank",
                    "not_required",
                    "source_identical_hidden_empty",
                    "runtime_vm_not_inherited",
                ))
                donor_translations.append("")
            else:
                raise RuntimeError(
                    "segment 1350 Base donor drifted: "
                    f"{donor_coordinate}"
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
                        f"segment 1350 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in hidden_set:
                if (
                    source_literals[literal_id] != ""
                    or current_literals[literal_id] != ""
                ):
                    raise RuntimeError(
                        f"segment 1350 hidden empty drifted: {coordinate}"
                    )
                assembled.append("")
                owners.append("source_identical_hidden_empty")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1350 incomplete record: {coordinate}"
                )
        if tuple(assembled) != tuple(donor_translations):
            raise RuntimeError(
                f"segment 1350 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1350 assembly ownership drifted")
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
