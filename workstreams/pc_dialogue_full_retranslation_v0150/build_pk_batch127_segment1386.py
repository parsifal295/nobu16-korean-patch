#!/usr/bin/env python3
"""Build source-redacted PK B127 segment 1386 residual decisions."""

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
    "15:1951:4",
    "15:1952:2",
    "15:1953:2",
    "15:1953:3",
    "15:1954:2",
    "15:1955:2",
    "15:1955:3",
    "15:1956:2",
    "15:1956:3",
    "15:1956:4",
    "15:1957:2",
    "15:1957:3",
    "15:1958:2",
    "15:1958:3",
    "15:1959:2",
    "15:1959:3",
    "15:1959:4",
    "15:1960:2",
    "15:1960:3",
    "15:1961:2",
    "15:1961:3",
    "15:1961:4",
    "15:1962:2",
    "15:1962:3",
    "15:1962:4",
    "15:1962:5",
    "15:1963:2",
    "15:1963:3",
    "15:1963:4",
    "15:1964:2",
    "15:1964:3",
    "15:1964:4",
    "15:1965:2",
    "15:1965:3",
    "15:1965:4",
    "15:1965:5",
    "15:1966:2",
    "15:1966:3",
    "15:1966:4",
    "15:1969:1",
)
TRANSLATIONS = {
    "15:1951:4": "(LV)",
    "15:1952:2": "개월 안에 목표 시설 수:",
    "15:1953:2": "년",
    "15:1953:3": "개월 안에 목표 시설 수:",
    "15:1954:2": "일 안에 목표 시설 수:",
    "15:1955:2": "개월 안에 목표 석고:",
    "15:1955:3": "\n현재 석고:",
    "15:1956:2": "년",
    "15:1956:3": "개월 안에 목표 석고:",
    "15:1956:4": "\n현재 석고:",
    "15:1957:2": "일 안에 목표 석고:",
    "15:1957:3": "\n현재 석고:",
    "15:1958:2": "개월 안에 목표 상업:",
    "15:1958:3": "\n현재 상업:",
    "15:1959:2": "년",
    "15:1959:3": "개월 안에 목표 상업:",
    "15:1959:4": "\n현재 상업:",
    "15:1960:2": "일 안에 목표 상업:",
    "15:1960:3": "\n현재 상업:",
    "15:1961:2": "개월 안에 목표:",
    "15:1961:3": "회\n현재:",
    "15:1961:4": "회",
    "15:1962:2": "년",
    "15:1962:3": "개월 안에 목표:",
    "15:1962:4": "회\n현재:",
    "15:1962:5": "회",
    "15:1963:2": "일 안에 목표:",
    "15:1963:3": "회\n현재:",
    "15:1963:4": "회",
    "15:1964:2": "개월 안에 목표:",
    "15:1964:3": "회\n현재:",
    "15:1964:4": "회",
    "15:1965:2": "년",
    "15:1965:3": "개월 안에 목표:",
    "15:1965:4": "회\n현재:",
    "15:1965:5": "회",
    "15:1966:2": "일 안에 목표:",
    "15:1966:3": "회\n현재:",
    "15:1966:4": "회",
    "15:1969:1": "\n결과를 정리하",
}
TARGET_RECORD_IDS = (
    1951,
    1952,
    1953,
    1954,
    1955,
    1956,
    1957,
    1958,
    1959,
    1960,
    1961,
    1962,
    1963,
    1964,
    1965,
    1966,
    1969,
)
EXPECTED_ARITY = {
    1951: 5,
    1952: 4,
    1953: 5,
    1954: 4,
    1955: 5,
    1956: 6,
    1957: 5,
    1958: 5,
    1959: 6,
    1960: 5,
    1961: 5,
    1962: 6,
    1963: 5,
    1964: 5,
    1965: 6,
    1966: 5,
    1969: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1951:0",
    "15:1951:2",
    "15:1951:3",
    "15:1952:0",
    "15:1952:3",
    "15:1953:0",
    "15:1953:4",
    "15:1954:0",
    "15:1954:3",
    "15:1955:0",
    "15:1956:0",
    "15:1957:0",
    "15:1958:0",
    "15:1959:0",
    "15:1960:0",
    "15:1961:0",
    "15:1962:0",
    "15:1963:0",
    "15:1964:0",
    "15:1965:0",
    "15:1966:0",
    "15:1969:0",
    "15:1969:2",
    "15:1969:3",
)
PREFILL_COMPANION_DONOR = {
    "15:1951:0": "15:1921:0",
    "15:1951:2": "15:1921:2",
    "15:1951:3": "15:1921:3",
    "15:1952:0": "15:1922:0",
    "15:1952:3": "15:1922:3",
    "15:1953:0": "15:1923:0",
    "15:1953:4": "15:1923:4",
    "15:1954:0": "15:1924:0",
    "15:1954:3": "15:1924:3",
    "15:1955:0": "15:1925:0",
    "15:1956:0": "15:1926:0",
    "15:1957:0": "15:1927:0",
    "15:1958:0": "15:1928:0",
    "15:1959:0": "15:1929:0",
    "15:1960:0": "15:1930:0",
    "15:1961:0": "15:1931:0",
    "15:1962:0": "15:1932:0",
    "15:1963:0": "15:1933:0",
    "15:1964:0": "15:1934:0",
    "15:1965:0": "15:1935:0",
    "15:1966:0": "15:1936:0",
    "15:1969:0": "15:1939:0",
    "15:1969:2": "15:1939:2",
    "15:1969:3": "15:1939:3",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:1951:1",
    "15:1952:1",
    "15:1953:1",
    "15:1954:1",
    "15:1955:1",
    "15:1955:4",
    "15:1956:1",
    "15:1956:5",
    "15:1957:1",
    "15:1957:4",
    "15:1958:1",
    "15:1958:4",
    "15:1959:1",
    "15:1959:5",
    "15:1960:1",
    "15:1960:4",
    "15:1961:1",
    "15:1962:1",
    "15:1963:1",
    "15:1964:1",
    "15:1965:1",
    "15:1966:1",
)
EXACT_BASE_DONOR = {
    record_id: (15, record_id - 30)
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    1951: ((1066, 550), ("0236", "0232", "0233")),
    1952: (
        (1162, 550),
        ("0235", "0232", "0233014326020000050505"),
    ),
    1953: (
        (1162, 550),
        ("0234", "0235", "0232", "0233014326020000050505"),
    ),
    1954: (
        (1162, 550),
        ("0236", "0232", "0233014326020000050505"),
    ),
    1955: ((1162, 550), ("0235", "0232", "0233")),
    1956: ((1162, 550), ("0234", "0235", "0232", "0233")),
    1957: ((1162, 550), ("0236", "0232", "0233")),
    1958: ((1162, 550), ("0235", "0232", "0233")),
    1959: ((1162, 550), ("0234", "0235", "0232", "0233")),
    1960: ((1162, 550), ("0236", "0232", "0233")),
    1961: ((1162, 550), ("0235", "0232", "0233")),
    1962: ((1162, 550), ("0234", "0235", "0232", "0233")),
    1963: ((1162, 550), ("0236", "0232", "0233")),
    1964: ((1066, 550), ("0235", "0232", "0233")),
    1965: ((1066, 550), ("0234", "0235", "0232", "0233")),
    1966: ((1066, 550), ("0236", "0232", "0233")),
    1969: ((178, 1174, 910), ("0232",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1386,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1951:0",
    slice_last="15:1969:1",
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
    source_call_roots=(1066, 550, 1162, 178, 1174, 910),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1915, 2010)
    ),
    speaker_style=(
        (1951, "system_policy_issue_level_objective"),
        (1952, "system_facility_month_objective"),
        (1953, "system_facility_year_month_objective"),
        (1954, "system_facility_day_objective"),
        (1955, "system_kokudaka_month_objective"),
        (1956, "system_kokudaka_year_month_objective"),
        (1957, "system_kokudaka_day_objective"),
        (1958, "system_commerce_month_objective"),
        (1959, "system_commerce_year_month_objective"),
        (1960, "system_commerce_day_objective"),
        (1961, "system_target_castle_month_objective"),
        (1962, "system_target_castle_year_month_objective"),
        (1963, "system_target_castle_day_objective"),
        (1964, "system_battle_victory_month_objective"),
        (1965, "system_battle_victory_year_month_objective"),
        (1966, "system_battle_victory_day_objective"),
        (1969, "formal_work_progress_eta"),
    ),
    terminology_policy=(
        ("policy issue level", "정책 발령 수준"),
        ("castle-town facility", "성하 시설"),
        ("kokudaka", "석고"),
        ("commerce", "상업"),
        ("target castle", "공략 목표로 삼은 성"),
        ("battle", "합전"),
        ("victory", "승리"),
        ("objective", "목표"),
        ("current", "현재"),
        ("level", "LV"),
        ("month", "개월"),
        ("year", "년"),
        ("day", "일"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B127 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all seventeen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by literal and operand-masked source identity with "
        "explicit exact donors; twenty-two source-identical hidden newline "
        "or empty companions remain non-translatable while participating in "
        "complete-record assembly; Base runtime and VM state are never "
        "inherited; policy issue levels, castle-town facilities, kokudaka, "
        "commerce, target castles, battles, victories, objectives and "
        "current values retain established historical project wording and "
        "system objective or formal progress registers; calls, duration, "
        "count, level, facility and value tokens, protected outer "
        "whitespace, line breaks, labels, colons, terminators, complete "
        "record arity, the right split record at 1969, all twenty-seven "
        "slice prefills, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=29,
    pins={
        "expected_queue_universe_sha256": (
            "E1A8B7C31AFD7CD33800E1FE68E170AEA554354C2299B03ED08B73C6FD95E060"
        ),
        "expected_queue_slice_sha256": (
            "1F86ED7AD10540DC7B7C3612C29235DCF9E7861946D6883735BBE0FD297AC837"
        ),
        "expected_prefilled_coordinate_sha256": (
            "4D9FB96A19BC6AD339678926936E519671715A4DD531D8E7EECEFD325BF74D1C"
        ),
        "expected_prefill_slice_context_sha256": (
            "909FAB11BC83DF64B072B06EF86511A95F4227209314D2A3FC0EE1EBA868074D"
        ),
        "expected_target_coordinate_sha256": (
            "FB6184A4E52757721E8B3CFA7DC3530EC5710E2FB50763D1F799FFFD142B984C"
        ),
        "expected_source_target_sha256": (
            "CB7BC7DB89B54C17AD5029D6CC23D9FC958ECBDAB692AD9B5EF865083958DF93"
        ),
        "expected_current_target_sha256": (
            "C4969BF073C6948BD65A378465B31892E91C567B0FC6AE631491A7B27D25A4A0"
        ),
        "expected_context_corpus_sha256": (
            "0E0A0B7D02FDF30847036712F1F4A5AE2366187E8C63CD48F3DA5300D602E45E"
        ),
        "expected_gap_contract_sha256": (
            "64D7C75BF9FA1B5C3E9F3878D452BC108C6038A1BA8B047FEFDC886E5BC5CCC8"
        ),
        "expected_boundary_sha256": (
            "F8E267BB83A84F592800226EDE7361DEA2BCF91EB737863D6BEFB11878D5581C"
        ),
        "expected_runtime_control_sha256": (
            "38D2F1770733ACC5B7A65A94EEC515B01EE3CA18F1C34830920EF144B14170E9"
        ),
        "expected_base_search_sha256": (
            "7B0BD62D82CE98B28E0F1A566F0B071B51B707D3A51D943C868CFF9314938CEC"
        ),
        "expected_complete_assembly_sha256": (
            "47F36315D5DE00963BC7B4AAADA189866EFB63F5A12E8DBBB3496137B22904C1"
        ),
        "expected_call_graph_sha256": (
            "280E75783B95DEE828FF78A7F48691D784A71A533C655D1D20FB9F1AD01F2244"
        ),
        "expected_speaker_style_sha256": (
            "EDD3FE66A97D831CFE1A7BDD27662E1BEF958CAA8E58D7A259BD142D4F2FCDBB"
        ),
        "expected_terminology_policy_sha256": (
            "DA66B6ABB2226D0DDB5D897A9EC3F2CB2849E5B6E6742E626E72E84A4B9CCA9D"
        ),
        "expected_translation_policy_sha256": (
            "A4E8D53971AAF9A70F6111037C5BE11D96488B445F95BBBEF80A53E26AC0B2F4"
        ),
        "expected_candidate_sha256": (
            "3EF7D02C261341F30660A6967055E5021594AFAC60442B257BC964C188752120"
        ),
        "expected_combined_slice_candidate_sha256": (
            "7B22AB37F7603FBE3612EB157606E43409FFE734B6BD976757FCD615EBC6EC2E"
        ),
        "expected_combined_changed_literal_count": 52,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B127_S1386",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1386.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1385.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B127_S1387.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B127",
    "queue_row_count": 71,
    "queue_visible_count": 199,
    "queue_first": "15:1928:0",
    "queue_last": "15:1998:1",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard exact Base assemblies including hidden newline/empty literals."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1386 Base promoted input drifted")
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
                f"segment 1386 Base search drifted: {record_id}"
            )
        donor_key = EXACT_BASE_DONOR[record_id]
        donor_coordinates = tuple(
            f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        references: list[tuple[Any, ...]] = []
        donor_translations: list[str] = []
        for literal_id, donor_coordinate in enumerate(donor_coordinates):
            donor = base_rows.get(donor_coordinate)
            target_coordinate = f"15:{record_id}:{literal_id}"
            if donor is None and target_coordinate in hidden_set:
                source_literal = source_literals[literal_id]
                if (
                    source_literal not in {"", "\n"}
                    or current_literals[literal_id] != source_literal
                ):
                    raise RuntimeError(
                        f"segment 1386 hidden donor drifted: "
                        f"{target_coordinate}"
                    )
                donor_translations.append(source_literal)
                references.append((
                    donor_coordinate,
                    source_literal,
                    "source_identical_hidden_literal",
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
                    "segment 1386 Base context drifted: "
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
                        f"segment 1386 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in hidden_set:
                source_literal = source_literals[literal_id]
                if (
                    source_literal not in {"", "\n"}
                    or current_literals[literal_id] != source_literal
                ):
                    raise RuntimeError(
                        f"segment 1386 hidden literal drifted: {coordinate}"
                    )
                assembled.append(source_literal)
                owners.append("source_identical_hidden_literal")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1386 incomplete record: {coordinate}"
                )
        if tuple(assembled) != tuple(donor_translations):
            raise RuntimeError(
                f"segment 1386 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1386 assembly ownership drifted")
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
