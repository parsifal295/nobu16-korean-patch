#!/usr/bin/env python3
"""Build source-redacted PK B119 segment 1362 residual decisions."""

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
    "15:1248:1": "이(가)",
    "15:1283:3": "……",
}
CROSS_DONOR_LABEL = {
    "15:1248:1": "manual-neighbor:pk_msggame_B119_S1361",
    "15:1283:3": "manual-neighbor:pk_msggame_B119_S1363",
}

TARGET_COORDINATES = (
    "15:1248:3",
    *tuple(
        f"15:{record_id}:{literal_id}"
        for record_id in range(1249, 1259)
        for literal_id in (1, 3)
    ),
    "15:1283:0",
    "15:1283:1",
)
TRANSLATIONS = {
    "15:1248:3": "다!",
    **{
        f"15:{record_id}:{literal_id}": (
            "이(가)" if literal_id == 1 else "다!"
        )
        for record_id in range(1249, 1259)
        for literal_id in (1, 3)
    },
    "15:1283:0": "에게서",
    "15:1283:1": "을(를) 받아\n",
}
TARGET_RECORD_IDS = (
    *tuple(range(1248, 1259)),
    1283,
)
EXPECTED_ARITY = {
    record_id: 4
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = (
    *tuple(
        f"15:{record_id}:{literal_id}"
        for record_id in range(1248, 1259)
        for literal_id in (0, 2)
    ),
    "15:1283:2",
    *tuple(CROSS_TRANSLATIONS),
)
PREFILL_COMPANION_DONOR = {
    **{
        f"15:{record_id}:0": "15:1239:0"
        for record_id in range(1248, 1259)
    },
    **{
        f"15:{record_id}:2": "15:1239:2"
        for record_id in range(1248, 1259)
    },
    "15:1283:2": "15:1275:2",
    **CROSS_DONOR_LABEL,
}
EXACT_BASE_DONOR = {
    **{
        record_id: (15, 1239)
        for record_id in range(1248, 1259)
    },
    1283: (15, 1275),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
TUNNEL_TRANSFER_MATCHES = tuple(
    (15, record_id) for record_id in range(1239, 1251)
)
EXPECTED_BASE_RAW_MATCHES = {
    **{
        record_id: ()
        for record_id in range(1248, 1259)
    },
    1283: ((15, 1275),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{
        record_id: TUNNEL_TRANSFER_MATCHES
        for record_id in range(1248, 1259)
    },
    1283: ((15, 1275),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    **{
        record_id: ((538,), ("026432", "025032"))
        for record_id in range(1248, 1259)
    },
    1283: ((178,), ("025032", "023C", "026432")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1362,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1248:3",
    slice_last="15:1283:1",
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
    source_call_roots=(538, 178),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1220, 1321)
    ),
    speaker_style=(
        *tuple(
            (
                record_id,
                "emphatic_tunnel_transfer_report",
            )
            for record_id in range(1248, 1259)
        ),
        (1283, "system_tunnel_attack_defense_weakened"),
    ),
    terminology_policy=(
        ("miner corps", "광부대"),
        ("tunnel assault", "땅굴 공략"),
        ("capture", "손에 넘어가다"),
        ("defense", "방비"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic source particle", "에게서"),
        ("dynamic object particle", "을(를)"),
        ("project emphatic ending", "다!"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B119 queue coordinates sixty-seven through "
        "one hundred thirty-three and the approved Base prefill; pristine "
        "PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary context; "
        "all twelve complete records reuse approved completed Base Korean "
        "assemblies selected by raw, literal and operand-masked source "
        "identity; record 1248 reciprocally pins the S1361 subject fragment "
        "and must reproduce completed Base record 1239, while record 1283 "
        "reciprocally pins the S1363 closing ellipsis and must reproduce "
        "completed Base record 1275; Base runtime and VM state are never "
        "inherited; the historical miner corps, tunnel assaults, capture, "
        "defense, dynamic particles, emphatic endings and system register "
        "retain established project wording; calls, inline castle, faction "
        "and tactic tokens, protected outer whitespace, line breaks, "
        "ellipsis, punctuation, terminators, complete record arity, all "
        "forty-four slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, reciprocal "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256": (
            "DC944BC6399C29C866DF74A3798EC8CF6197780D468D34FB2B3777B5BE629D99"
        ),
        "expected_queue_slice_sha256": (
            "DD5250E28C5F78EBF6A9B80345FF9F9369144EB102E901CBDC411987F490D7A9"
        ),
        "expected_prefilled_coordinate_sha256": (
            "301F5E8AC167668093EDC77354A0FA1D0A34B362C7A681AEE4434A0F8F034B2F"
        ),
        "expected_prefill_slice_context_sha256": (
            "0D1949D63C69C7C3F9118C1930494C1A07E6E5F5EBF6BA9CDA12B92DF350C618"
        ),
        "expected_target_coordinate_sha256": (
            "A88C6A70F726149B56218DD183F1EBE4DF38FDF1F4B1B0152FB7F71604A4B8DA"
        ),
        "expected_source_target_sha256": (
            "273BC1C2E4FAAE421079E9008979E653980F2C5EB3F710FF22D1480FEFECD24B"
        ),
        "expected_current_target_sha256": (
            "C8081E6D34DB9A73C41E98B67C2751ECF679BADD1976B9EAC703EA6E22F1271B"
        ),
        "expected_context_corpus_sha256": (
            "D2986D691DE08C2C978E09ADA920896A94DE82CA761A6FC64625FDDCD496284B"
        ),
        "expected_gap_contract_sha256": (
            "AD1C222205145C850DC2DDC5370A7266B2086B1485DAA21EDC57A3A9956AC1C5"
        ),
        "expected_boundary_sha256": (
            "83F8B3D6E0B787967F7B53DF200E1CFE82F046B06411F9CC7EC314D95654B0A6"
        ),
        "expected_runtime_control_sha256": (
            "E2501ED089BC6A90D25CFF5784E6058C4523D983F69251B1740EF00064DED709"
        ),
        "expected_base_search_sha256": (
            "9BBA281122EF2B0E18DD07C6925C5D0388A0B3DBA5834DD30EBF5D274D5E26C8"
        ),
        "expected_complete_assembly_sha256": (
            "82B43FA4CDFFA231E1268A69ACB6C778C407F5E1AFBDE1956FFB8DDE3FDC5319"
        ),
        "expected_call_graph_sha256": (
            "29A7C799DF4FE346841517C3BB5FA45346ACA60F1F4BB574BA56E809FDD080FB"
        ),
        "expected_speaker_style_sha256": (
            "FEC53B4E0E798B7B69F6D1FA00410F4CD38ABC9BB3691EE53A7658C581544AA0"
        ),
        "expected_terminology_policy_sha256": (
            "0928C8BF494E5CC5397C4E4CDA79F935C72F8C96E6BBC45844F37814E293FC6E"
        ),
        "expected_translation_policy_sha256": (
            "AFA2FB32159C364DDA4B55B9E091898849D9372B7D711BA07C8F5E3CF8774821"
        ),
        "expected_candidate_sha256": (
            "74A4E1A62C49D4BC99F16515E9CA7249F25377DE786E86EFE650944149D69561"
        ),
        "expected_combined_slice_candidate_sha256": (
            "149AC146A6DF98A71E8A9FF48148D183F202955C2BF3EF8D9F1D093C318B9963"
        ),
        "expected_combined_changed_literal_count": 45,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B119_S1362",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1362.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1361.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1363.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B119",
    "queue_row_count": 109,
    "queue_visible_count": 200,
    "queue_first": "15:1217:0",
    "queue_last": "15:1325:0",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard complete Base assemblies and both split boundary records."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1362 Base promoted input drifted")
    neighbor_specs = (
        (
            "pk_msggame_B119_S1361.private.v1.jsonl",
            "15:1248:1",
            "이(가)",
        ),
        (
            "pk_msggame_B119_S1363.private.v1.jsonl",
            "15:1283:3",
            "……",
        ),
    )
    for filename, coordinate, translation in neighbor_specs:
        neighbor_path = COMMON.DECISIONS_ROOT / filename
        if not neighbor_path.is_file():
            continue
        neighbor_rows = {
            str(row["coordinate"]): row
            for row in COMMON.read_jsonl(neighbor_path)
        }
        neighbor = neighbor_rows.get(coordinate)
        if (
            neighbor is None
            or neighbor.get("resource") != "pk_msggame"
            or neighbor.get("semantic_review") != "approved"
            or neighbor.get("runtime_review") != "pending"
            or str(neighbor.get("translation")) != translation
        ):
            raise RuntimeError(
                f"segment 1362 reciprocal neighbor drifted: {coordinate}"
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
                f"segment 1362 Base search drifted: {record_id}"
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
                    "segment 1362 Base context drifted: "
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
                        f"segment 1362 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1362 incomplete record: {coordinate}"
                )
        if tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1362 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1362 assembly ownership drifted")
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
