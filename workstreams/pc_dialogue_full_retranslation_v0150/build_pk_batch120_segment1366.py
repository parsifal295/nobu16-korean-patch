#!/usr/bin/env python3
"""Build source-redacted PK B120 segment 1366 residual decisions."""

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
    "15:1386:0": "에서",
}
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B120_S1365"

TARGET_COORDINATES = (
    "15:1386:4",
    *tuple(
        f"15:{record_id}:{literal_id}"
        for record_id in range(1387, 1400)
        for literal_id in (0, 4)
    ),
)
TRANSLATIONS = {
    "15:1386:4": "의 인망",
    **{
        f"15:{record_id}:{literal_id}": (
            "에서" if literal_id == 0 else "의 인망"
        )
        for record_id in range(1387, 1400)
        for literal_id in (0, 4)
    },
}
TARGET_RECORD_IDS = tuple(range(1386, 1400))
EXPECTED_ARITY = {
    record_id: 5
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = (
    *tuple(
        f"15:{record_id}:{literal_id}"
        for record_id in range(1386, 1400)
        for literal_id in (1, 2, 3)
    ),
    *tuple(CROSS_TRANSLATIONS),
)
PREFILL_COMPANION_DONOR = {
    **{
        f"15:{record_id}:{literal_id}": f"15:1370:{literal_id}"
        for record_id in range(1386, 1400)
        for literal_id in (1, 2, 3)
    },
    **{
        coordinate: CROSS_DONOR_LABEL
        for coordinate in CROSS_TRANSLATIONS
    },
}
EXACT_BASE_DONOR = {
    record_id: (15, 1370)
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
DEVELOPMENT_REPORT_MATCHES = tuple(
    (15, record_id) for record_id in range(1370, 1394)
)
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: DEVELOPMENT_REPORT_MATCHES
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: (
        (538, 628, 1, 610),
        ("029632", "02BE32"),
    )
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1366,
    queue_start=134,
    queue_stop=200,
    slice_first="15:1386:4",
    slice_last="15:1399:4",
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
    source_call_roots=(538, 628, 1, 610),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1340, 1421)
    ),
    speaker_style=tuple(
        (
            record_id,
            "formal_development_success_report",
        )
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("development", "개척"),
        ("people", "백성"),
        ("local rule", "다스리다"),
        ("public esteem", "인망"),
        ("dynamic object particle", "을(를)"),
        ("dynamic locative particle", "에서"),
        ("formal emphatic ending", "다!"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B120 queue coordinates one hundred thirty-four "
        "through one hundred ninety-nine and the approved Base prefill; "
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary context; all "
        "fourteen complete records reuse the approved completed Base Korean "
        "assembly at record 1370 selected by literal and operand-masked "
        "source identity; record 1386 reciprocally pins the S1365 opening "
        "locative fragment and must reproduce that completed Base assembly; "
        "Base runtime and VM state are never inherited; development, the "
        "people, local rule, public esteem, dynamic particles and the formal "
        "emphatic register retain established historical project wording; "
        "calls, inline settlement and development tokens, protected outer "
        "whitespace, line breaks, punctuation, terminators, complete record "
        "arity, all thirty-nine slice prefills and three earlier same-record "
        "prefills, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, S1364 and S1365 optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=0,
    pins={
        "expected_queue_universe_sha256": (
            "F31FED1CD112AA0ADB2BFBEEC7F459040B9E5892A5E59BE751060D0B8D50E138"
        ),
        "expected_queue_slice_sha256": (
            "08F5F7272573204D22A57D85EC14685C78A45A494DB7A24CE57EA93B64D41C6B"
        ),
        "expected_prefilled_coordinate_sha256": (
            "19775BDE94E3D6FA95D641C3E4677D508731EA061F88E61ACD99AE712B2D7499"
        ),
        "expected_prefill_slice_context_sha256": (
            "3390F7D79B919F288B6E5688202D2C7A78B1AE2C0750601D7535B15A62E85B06"
        ),
        "expected_target_coordinate_sha256": (
            "E522F80BBD026458A47E458DA7F17A341816D79E30761518ED9B3BB83B0D7104"
        ),
        "expected_source_target_sha256": (
            "CB7303EEBB25838ADFD9B37A807722CA05A3B740FB0B3AE4A219E4520E9F6285"
        ),
        "expected_current_target_sha256": (
            "2F9F9216F796281C8D5BE6DB24034656EB2B3607575C1AC2AE09ADE88864CF77"
        ),
        "expected_context_corpus_sha256": (
            "BC631B3C918EB592932A4ACEA0AFB6AA32A42B3FD7E4BDA644E3B6AA6F607FA1"
        ),
        "expected_gap_contract_sha256": (
            "66C40FE0E83D871652F4AF9E9DD3826777D7A253A6DF35D57A2E79CE8CB32C95"
        ),
        "expected_boundary_sha256": (
            "DB69F74ABA2A5C6AF6F5C53D96D797EA0211BD8FFD9D34972048BD3A709FFBCD"
        ),
        "expected_runtime_control_sha256": (
            "BF44E94D78A62031449253E5361C702001F92ED627BDCDCFA4AEE2A7901FEBC6"
        ),
        "expected_base_search_sha256": (
            "3D6BD77ACA8B490D12EC468B06EA5F08FAB6C17F510D3215E7717E125D14FC1D"
        ),
        "expected_complete_assembly_sha256": (
            "63DE809746BE9C43AA465463F25A4233C0DA3BC1EFA6C8DEF1CA7AEDAAFB0F58"
        ),
        "expected_call_graph_sha256": (
            "6B09012A82CDE9098F8F1D1C3FC109D3E7922D53AF9BB148DE56796157225C73"
        ),
        "expected_speaker_style_sha256": (
            "95CA3F5797BDC40CAD54E27D3BD76142D5B5D150F138E99BC8991E62CDAA2B4F"
        ),
        "expected_terminology_policy_sha256": (
            "6F6272F21B462ADF91672E35AFA72F4236C8C02338F1FF7DB5BADCF3FF542487"
        ),
        "expected_translation_policy_sha256": (
            "2F9F9216F796281C8D5BE6DB24034656EB2B3607575C1AC2AE09ADE88864CF77"
        ),
        "expected_candidate_sha256": (
            "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
        ),
        "expected_combined_slice_candidate_sha256": (
            "71838D391BF500B328E19B82527B9C6F7B9EB986EB94053C4F413E66AB2C23BF"
        ),
        "expected_combined_changed_literal_count": 39,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B120_S1366",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1366.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1364.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1365.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B120",
    "queue_row_count": 72,
    "queue_visible_count": 200,
    "queue_first": "15:1326:0",
    "queue_last": "15:1399:4",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard completed Base assemblies and the S1365 split record."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1366 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1365.private.v1.jsonl"
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
                    "segment 1366 reciprocal S1365 fragment drifted"
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
                f"segment 1366 Base search drifted: {record_id}"
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
                    "segment 1366 Base context drifted: "
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
                        f"segment 1366 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1366 incomplete record: {coordinate}"
                )
        if tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1366 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1366 assembly ownership drifted")
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
