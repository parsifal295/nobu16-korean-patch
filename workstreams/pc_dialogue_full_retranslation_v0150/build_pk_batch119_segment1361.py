#!/usr/bin/env python3
"""Build source-redacted PK B119 segment 1361 residual decisions."""

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
    "15:1248:3": "다!",
}
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B119_S1362"

TARGET_COORDINATES = (
    "15:1217:0",
    "15:1217:1",
    "15:1219:1",
    "15:1219:2",
    "15:1235:1",
    "15:1237:0",
    "15:1237:2",
    "15:1238:2",
    "15:1239:2",
    "15:1240:2",
    "15:1241:2",
    "15:1242:2",
    "15:1243:2",
    "15:1244:2",
    "15:1245:2",
    "15:1246:2",
    "15:1247:1",
    "15:1247:3",
    "15:1248:1",
)
TRANSLATIONS = {
    "15:1217:0": "의 신용 ",
    "15:1217:1": "→",
    "15:1219:1": "→",
    "15:1219:2": "(으)로 개선",
    "15:1235:1": "인가",
    "15:1237:0": "에",
    "15:1237:2": "!",
    **{
        f"15:{record_id}:2": "다!"
        for record_id in range(1238, 1247)
    },
    "15:1247:1": "이(가)",
    "15:1247:3": "다!",
    "15:1248:1": "이(가)",
}
TARGET_RECORD_IDS = (
    1217,
    1219,
    1235,
    1237,
    *tuple(range(1238, 1249)),
)
EXPECTED_ARITY = {
    **{
        record_id: 3
        for record_id in (
            1219,
            1237,
            *tuple(range(1238, 1247)),
        )
    },
    1217: 2,
    1235: 2,
    1247: 4,
    1248: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1219:0",
    "15:1235:0",
    "15:1237:1",
    *tuple(
        f"15:{record_id}:{literal_id}"
        for record_id in range(1238, 1247)
        for literal_id in (0, 1)
    ),
    "15:1247:0",
    "15:1247:2",
    "15:1248:0",
    "15:1248:2",
    *tuple(CROSS_TRANSLATIONS),
)
PREFILL_COMPANION_DONOR = {
    "15:1219:0": "15:1211:0",
    "15:1235:0": "15:1227:0",
    "15:1237:1": "15:1229:1",
    **{
        f"15:{record_id}:{literal_id}": f"15:1230:{literal_id}"
        for record_id in range(1238, 1247)
        for literal_id in (0, 1)
    },
    "15:1247:0": "15:1239:0",
    "15:1247:2": "15:1239:2",
    "15:1248:0": "15:1239:0",
    "15:1248:2": "15:1239:2",
    **{
        coordinate: CROSS_DONOR_LABEL
        for coordinate in CROSS_TRANSLATIONS
    },
}
EXACT_BASE_DONOR = {
    1217: (15, 1208),
    1219: (15, 1211),
    1235: (15, 1227),
    1237: (15, 1229),
    **{
        record_id: (15, 1230)
        for record_id in range(1238, 1247)
    },
    1247: (15, 1239),
    1248: (15, 1239),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
TUNNEL_CAPTURE_MATCHES = tuple(
    (15, record_id) for record_id in range(1230, 1239)
)
TUNNEL_TRANSFER_MATCHES = tuple(
    (15, record_id) for record_id in range(1239, 1251)
)
EXPECTED_BASE_RAW_MATCHES = {
    1217: ((15, 1208), (15, 1209)),
    1219: ((15, 1211),),
    1235: (),
    1237: (),
    **{
        record_id: ()
        for record_id in range(1238, 1249)
    },
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1235: ((15, 1227),),
    1237: ((15, 1229),),
    **{
        record_id: TUNNEL_CAPTURE_MATCHES
        for record_id in range(1238, 1247)
    },
    1247: TUNNEL_TRANSFER_MATCHES,
    1248: TUNNEL_TRANSFER_MATCHES,
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    1217: ((), ("025032", "0232", "0233050505")),
    1219: ((), ("025032", "023C", "023D")),
    1235: ((700, 616), ("026432",)),
    1237: ((538,), ("026432", "023C")),
    **{
        record_id: ((538,), ("026432",))
        for record_id in range(1238, 1247)
    },
    1247: ((538,), ("026432", "025032")),
    1248: ((538,), ("026432", "025032")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1361,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1217:0",
    slice_last="15:1248:2",
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
    source_call_roots=(700, 616, 538),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1200, 1261)
    ),
    speaker_style=(
        (1217, "system_diplomatic_credit_change"),
        (1219, "system_diplomatic_stance_improvement"),
        (1235, "formal_tunnel_assault_proposal"),
        (1237, "formal_tunnel_assault_success"),
        *tuple(
            (
                record_id,
                "emphatic_tunnel_capture_report",
            )
            for record_id in range(1238, 1247)
        ),
        (1247, "emphatic_tunnel_transfer_report"),
        (1248, "emphatic_tunnel_transfer_report"),
    ),
    terminology_policy=(
        ("credit", "신용"),
        ("diplomatic stance", "외교 자세"),
        ("improve", "개선"),
        ("tunnel assault", "땅굴 공략"),
        ("miner corps", "광부대"),
        ("defense", "방비"),
        ("capture", "함락"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic directional particle", "(으)로"),
        ("project arrow", "→"),
        ("project exclamation mark", "!"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B119 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all fifteen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity; "
        "record 1248 reciprocally pins the S1362 closing fragment and must "
        "reproduce completed Base record 1239; Base runtime and VM state "
        "are never inherited; diplomatic credit and stance, the historical "
        "miner corps, tunnel assaults, defenses, capture terminology, "
        "dynamic particles and formal or emphatic speaker registers retain "
        "established project wording; calls, inline castle, faction, "
        "diplomatic stance and numeric tokens, protected outer whitespace, "
        "line breaks, arrows, punctuation, terminators, complete record "
        "arity, all forty-eight slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "reciprocal optional neighbor decisions and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=4,
    pins={
        "expected_queue_universe_sha256": (
            "DC944BC6399C29C866DF74A3798EC8CF6197780D468D34FB2B3777B5BE629D99"
        ),
        "expected_queue_slice_sha256": (
            "85210E9229278C78C691DE2A14CFAEA7C82615F32A3E4DE0CE4D3AE9A1E29891"
        ),
        "expected_prefilled_coordinate_sha256": (
            "45DA643C2069B6C75E6B3A8AFA0E7A3E331D625F8864F66E7A2874D4F1F21D21"
        ),
        "expected_prefill_slice_context_sha256": (
            "8536245370E93D3CD5A6B62B59BB0340FBA11369B1C535772F7E7726DA677B7E"
        ),
        "expected_target_coordinate_sha256": (
            "C8F58B9EAC9015D8CA19ACA5029BBD3A2B2C37E19B10AA18A6CF299E04900FF4"
        ),
        "expected_source_target_sha256": (
            "0950CE1AC9D7FC38BEBC6EB2D2BA73D1651CBBB9610C10EF59EDC1ABE2EDF4E3"
        ),
        "expected_current_target_sha256": (
            "3514B4977E1873EC347A8285B5027130859B3388737B115D9D0EFFF177346FFC"
        ),
        "expected_context_corpus_sha256": (
            "D2986D691DE08C2C978E09ADA920896A94DE82CA761A6FC64625FDDCD496284B"
        ),
        "expected_gap_contract_sha256": (
            "15FCC68D49631E51A77B55E4E6C904288F9B924F4D8925F8A0CE03E6827255AE"
        ),
        "expected_boundary_sha256": (
            "F51E3D90D6D94C2DF0A8DC7E6D5692B99A77E710A9ABCD9A10CBB5A3C2BF0FA7"
        ),
        "expected_runtime_control_sha256": (
            "B7206C218F2C980968A21C37C7E47AD45355B5AAF3516525B4F0FAB7D438F7BA"
        ),
        "expected_base_search_sha256": (
            "25E6AB382B7E3E84E74C151130AF87F6E0B904702CB4F867C6DD043ED59C84A3"
        ),
        "expected_complete_assembly_sha256": (
            "72996545F8C2827BD0C65794FF995A94C0295F42AE1C8EB826468192F5CE1166"
        ),
        "expected_call_graph_sha256": (
            "303913DD87BCCD387A4FF91D7C79AB20E3231A46E6C691F852B229DB2D17DDB3"
        ),
        "expected_speaker_style_sha256": (
            "7117723349850A82D06BE299124143FB0379F2A3744DADE7E6D3C09584977627"
        ),
        "expected_terminology_policy_sha256": (
            "558C70C51735C5EF036831A107E78AE0B8325686677F6591C4DDDC69A5929EE8"
        ),
        "expected_translation_policy_sha256": (
            "B2F494BD800FBADF79F2F6EDF0C9B732E6A26D5EE7EE964E56FA21E352B5ED5B"
        ),
        "expected_candidate_sha256": (
            "18429D56416CBB511788C6DB63F0F777C168250DBB7303CE16B9716B2CE0F49C"
        ),
        "expected_combined_slice_candidate_sha256": (
            "22A59D5835B123125293B9F61DCEF0FFD1EEB8BDD48B03399AA7D5EFEBCF3A75"
        ),
        "expected_combined_changed_literal_count": 46,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B119_S1361",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1361.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1362.private.v1.jsonl",
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
    """Guard complete Base assemblies and the S1362 split record."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1361 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1362.private.v1.jsonl"
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
                    "segment 1361 reciprocal S1362 fragment drifted"
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
                f"segment 1361 Base search drifted: {record_id}"
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
                    "segment 1361 Base context drifted: "
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
                        f"segment 1361 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1361 incomplete record: {coordinate}"
                )
        if tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1361 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1361 assembly ownership drifted")
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
