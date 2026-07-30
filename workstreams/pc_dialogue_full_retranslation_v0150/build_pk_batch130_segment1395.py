#!/usr/bin/env python3
"""Build source-redacted PK B130 segment 1395 residual decisions."""

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
    "15:2224:2",
    "15:2225:1",
    "15:2233:0",
    "15:2240:1",
    "15:2257:0",
    "15:2257:1",
    "15:2258:0",
    "15:2258:1",
    "15:2261:0",
)
TRANSLATIONS = {
    "15:2224:2": "거두어 보이겠습니다",
    "15:2225:1": "\n좋은 소식을 기다려 주십시오",
    "15:2233:0": "이번 일은,",
    "15:2240:1": "\n이 또한",
    "15:2257:0": "지금이라면",
    "15:2257:1": "을(를) 함락시킬 수 있",
    "15:2258:0": "지금이라면",
    "15:2258:1": "을(를) 함락시킬 수 있",
    "15:2261:0": "을(를) 공략할 절호의 기회",
}
TARGET_RECORD_IDS = (2224, 2225, 2233, 2240, 2257, 2258, 2261)
EXPECTED_ARITY = {
    2224: 3,
    2225: 2,
    2233: 2,
    2240: 3,
    2257: 3,
    2258: 3,
    2261: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2225:0",
    "15:2233:1",
    "15:2240:0",
    "15:2240:2",
    "15:2257:2",
    "15:2258:2",
    "15:2261:2",
)
PREFILL_COMPANION_DONOR = {
    "15:2225:0": "15:2195:0",
    "15:2233:1": "15:2203:1",
    "15:2240:0": "15:2210:0",
    "15:2240:2": "15:2210:2",
    "15:2257:2": "15:2227:2",
    "15:2258:2": "15:2227:2",
    "15:2261:2": "15:2231:2",
}
NEIGHBOR_COMPANION_COORDINATES = (
    "15:2224:0",
    "15:2224:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2261:1",
)
EXACT_BASE_DONOR = {
    2224: (15, 2194),
    2225: (15, 2195),
    2233: (15, 2203),
    2240: (15, 2210),
    2257: (15, 2227),
    2258: (15, 2228),
    2261: (15, 2231),
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
    2224: ((15, 2194),),
    2225: ((15, 2195),),
    2233: ((15, 2203),),
    2240: ((15, 2210),),
    2257: ((15, 2227), (15, 2228)),
    2258: ((15, 2227), (15, 2228)),
    2261: ((15, 2231),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2224: ((538, 1174, 412), ()),
    2225: ((442, 922), ()),
    2233: ((1, 412), ()),
    2240: ((628,), ("024635",)),
    2257: ((1096,), ("026432",)),
    2258: ((1096,), ("026432",)),
    2261: ((568, 1066), ("026432", "025032")),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    2224: ((), ()),
    2225: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1395,
    queue_start=67,
    queue_stop=134,
    slice_first="15:2224:2",
    slice_last="15:2261:2",
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
        538, 1174, 412, 442, 922, 1, 628, 1096, 568, 1066
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2180, 2300)
    ),
    speaker_style=(
        (2224, "formal_confident_acceptance"),
        (2225, "formal_humble_acceptance"),
        (2233, "formal_deliberation_request"),
        (2240, "formal_apology_for_prior_remonstrance"),
        (2257, "urgent_sortie_recommendation"),
        (2258, "urgent_sortie_recommendation"),
        (2261, "confident_attack_opportunity_assessment"),
    ),
    terminology_policy=(
        ("achievement", "성과"),
        ("good news", "좋은 소식"),
        ("deliberation", "생각"),
        ("remonstrance", "상신"),
        ("lord clan", "주군 가문"),
        ("war council", "군의"),
        ("sortie", "출진"),
        ("capture", "함락"),
        ("siege", "공략"),
        ("elite troops", "정예병"),
        ("dynamic object particle", "을(를)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B130 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all seven "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by literal and operand-masked source identity with "
        "explicit exact donors; split boundary record 2224 is assembled "
        "from two exact Base companions owned by optional prior segment "
        "1394 and the in-slice target, and any landed neighbor translations "
        "must equal the Base assembly; one source-identical hidden newline "
        "remains non-translatable while participating in complete assembly; "
        "Base runtime and VM state are never inherited; achievements, good "
        "news, deliberation, remonstrance, the lord clan, war councils, "
        "sorties, captures, sieges and elite troops retain established "
        "historical project wording and formal, humble, urgent or confident "
        "registers; calls, inline person, castle and force tokens, protected "
        "outer whitespace, line breaks, particles, ellipses, terminators, "
        "complete record arity, all fifty-eight slice prefills, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, outside-"
        "scope identity, optional neighbor decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=7,
    pins={
        "expected_queue_universe_sha256": "71C7EBC3AABF0AAB3370592930BE4C339E6E63D3343A8F498ED5901F3682AB2F",
        "expected_queue_slice_sha256": "7B1366F1093ED3AD9CA9A4D5924E4AD848B1B7B0F6C9B64A8E036472E3557851",
        "expected_prefilled_coordinate_sha256": "59D607D3AE1DB057557DAA4E9418C5F84748624EE246CD2AE9C3DEA2D17A87B2",
        "expected_prefill_slice_context_sha256": "7B2D6DD5FABE32BDB94C19A0DA716678909434D8F8E9B6C990AEE59D9934893E",
        "expected_target_coordinate_sha256": "04DB8AA5D85D1F37EE800D32FE1C684D94D39E8CD81B0F70EDDD72341C18C6DD",
        "expected_source_target_sha256": "F8D9B37A8DBB1B4E629FE1E38F7B369FF0D738DC759B19748B34A4B3CE77CA4F",
        "expected_current_target_sha256": "F83C555A1FCCA86E6723CE5D481A699FC2458CBF7A09A99A6C6226F35BA57D6C",
        "expected_context_corpus_sha256": "03DC62C7A0C8C3AC07AF97A148F0BBDD47026D2571EEED897A543B68CCA58C0C",
        "expected_gap_contract_sha256": "80B8910AFE7598B4C468333FFD2ADF7B9A52B405CE0E38E0FC92E9DFF08F93B0",
        "expected_boundary_sha256": "1FF2FD154F176D7EE7E459A6AAC4BFA4E7D335592BD9D7B70EDB0373CBC4546F",
        "expected_runtime_control_sha256": "6942D6036E6FE9AB37A6212CF43EAED76F4A957A821DEC47424BA8AC3466F563",
        "expected_base_search_sha256": "EA2ED44D2562E30671B185FD50AD8122BA32B5AFFAD805F6E614FF9F13A4C29C",
        "expected_complete_assembly_sha256": "06BF1A0F3315AF62E31612C00CC0E7BC284512A36B6C455998DCAD8FC745B246",
        "expected_call_graph_sha256": "1FF58AC7869651983C051C20C145DDC681DBD5590E79C52C75A1DDA790E562ED",
        "expected_speaker_style_sha256": "F9E954D8EF707282107B7EBFA3C7388B8318F9C234AD64124890CED7E18E541B",
        "expected_terminology_policy_sha256": "A23365203D2849258E164485E561E4250CFC07F96FC81476AF18942AA1293A49",
        "expected_translation_policy_sha256": "081A3D3E576B14A7796BF44A0C5A6887EBE4ECCE2562BBA8685C313D20A5645B",
        "expected_candidate_sha256": "E11CFD4B226A6D2A96F54936B3D79B16717A3721DB777ED558357B5145072A60",
        "expected_combined_slice_candidate_sha256": "1C5BAD8ACC8F6942CF40CBC61707DB0319575792D92DF3C235037115AE69B8B2",
        "expected_combined_changed_literal_count": 60,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B130_S1395",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1395.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1394.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1396.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B130",
    "queue_row_count": 97,
    "queue_visible_count": 199,
    "queue_first": "15:2193:0",
    "queue_last": "15:2289:1",
})


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    """Guard the two known current records whose legacy calls are absent."""
    values = COMMON.CORE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        (
            "source target",
            values["source_target"],
            CONFIG["expected_source_target_sha256"],
        ),
        (
            "current target",
            values["current_target"],
            CONFIG["expected_current_target_sha256"],
        ),
        (
            "multilingual context",
            values["corpus"],
            CONFIG["expected_context_corpus_sha256"],
        ),
        (
            "gap contract",
            values["gaps"],
            CONFIG["expected_gap_contract_sha256"],
        ),
        (
            "boundary",
            values["boundary"],
            CONFIG["expected_boundary_sha256"],
        ),
        (
            "runtime control",
            values["controls"],
            CONFIG["expected_runtime_control_sha256"],
        ),
    ):
        COMMON.CORE.guarded_digest(label, value, expected)
    expected_controls = tuple(
        (
            label,
            record_id,
            (
                EXPECTED_CONTROLS_BY_RECORD[record_id]
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    mismatched_gap_records = {
        record_id
        for record_id, source, current in values["gaps"]
        if source != current
    }
    if (
        values["controls"] != expected_controls
        or mismatched_gap_records != {2224, 2225}
        or any(
            ("pk_msggame", *COMMON.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError("segment 1395 runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard exact Base assemblies plus optional prior-segment companions."""
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
    neighbor_rows = {
        str(row["coordinate"]): row
        for path in CONFIG["optional_neighbors"]
        if path.is_file()
        for row in COMMON.read_jsonl(path)
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    neighbor_set = set(NEIGHBOR_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_neighbor: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (15, record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(records_by_label["jp"], key)
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
                COMMON.literal_texts(base_source, coordinate) == source_literals
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
                f"segment 1395 Base search drifted: {record_id}"
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
                value = source_literals[literal_id]
                if value not in {"", "\n"} or current_literals[literal_id] != value:
                    raise RuntimeError(
                        f"segment 1395 hidden donor drifted: {target_coordinate}"
                    )
                donor_translations.append(value)
                references.append((
                    donor_coordinate, value, "source_identical_hidden_literal",
                    "not_translatable_blank", "complete_exact_assembly",
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
                    f"segment 1395 Base context drifted: {donor_coordinate}"
                )
            translation = str(donor["translation"])
            donor_translations.append(translation)
            references.append((
                donor_coordinate, translation, str(donor["semantic_review"]),
                str(donor["runtime_review"]), "complete_exact_assembly",
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
                    or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment 1395 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append("base_exact_prefill_runtime_pending")
                seen_companion.add(coordinate)
            elif coordinate in neighbor_set:
                expected = donor_translations[literal_id]
                neighbor = neighbor_rows.get(coordinate)
                if (
                    neighbor is not None
                    and (
                        str(neighbor.get("translation")) != expected
                        or neighbor.get("semantic_review") != "approved"
                        or neighbor.get("runtime_review") != "pending"
                    )
                ):
                    raise RuntimeError(
                        f"segment 1395 neighbor companion drifted: {coordinate}"
                    )
                assembled.append(expected)
                owners.append("optional_prior_segment_exact_base_companion")
                seen_neighbor.add(coordinate)
            elif coordinate in hidden_set:
                value = source_literals[literal_id]
                if value not in {"", "\n"} or current_literals[literal_id] != value:
                    raise RuntimeError(
                        f"segment 1395 hidden literal drifted: {coordinate}"
                    )
                assembled.append(value)
                owners.append("source_identical_hidden_literal")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1395 incomplete record: {coordinate}"
                )
        if tuple(assembled) != tuple(donor_translations):
            raise RuntimeError(
                f"segment 1395 exact assembly drifted: {record_id}"
            )
        base_evidence.append((
            record_id,
            COMMON.sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(value.hex().upper() for value in COMMON.gap_bytes(source)),
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
        or seen_neighbor != neighbor_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError("segment 1395 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.assert_context_contracts = assert_context_contracts
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.assert_context_contracts = assert_context_contracts
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
