#!/usr/bin/env python3
"""Build source-redacted PK B117 segment 1357 residual decisions."""

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
    "15:1069:1": "회복(",
}
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B117_S1356"

TARGET_COORDINATES = (
    "15:1069:2",
    "15:1069:3",
    "15:1094:0",
    "15:1094:2",
    "15:1096:0",
    "15:1096:1",
    "15:1097:1",
    "15:1097:2",
    "15:1097:3",
    "15:1098:0",
    "15:1100:0",
    "15:1101:0",
    "15:1102:2",
    "15:1103:2",
    "15:1104:0",
    "15:1104:2",
    "15:1105:1",
)
TRANSLATIONS = {
    "15:1069:2": "→",
    "15:1069:3": ")",
    "15:1094:0": "·",
    "15:1094:2": "회복",
    "15:1096:0": "의",
    "15:1096:1": "에서\n",
    "15:1097:1": "회복(",
    "15:1097:2": "→",
    "15:1097:3": ")",
    "15:1098:0": "은(는)",
    "15:1100:0": "와(과)",
    "15:1101:0": "에서",
    "15:1102:2": "→",
    "15:1103:2": "와(과)",
    "15:1104:0": "송구하",
    "15:1104:2": "·",
    "15:1105:1": "와(과)",
}
TARGET_RECORD_IDS = (
    1069,
    1094,
    1096,
    1097,
    1098,
    1100,
    1101,
    1102,
    1103,
    1104,
    1105,
)
EXPECTED_ARITY = {
    1069: 4,
    1094: 3,
    1096: 4,
    1097: 4,
    1098: 2,
    1100: 2,
    1101: 3,
    1102: 3,
    1103: 4,
    1104: 4,
    1105: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1069:0",
    *tuple(CROSS_TRANSLATIONS),
    "15:1094:1",
    "15:1096:2",
    "15:1096:3",
    "15:1097:0",
    "15:1098:1",
    "15:1100:1",
    "15:1101:1",
    "15:1101:2",
    "15:1102:0",
    "15:1102:1",
    "15:1103:0",
    "15:1103:3",
    "15:1104:1",
    "15:1104:3",
    "15:1105:0",
    "15:1105:2",
)
PREFILL_COMPANION_DONOR = {
    "15:1069:0": "15:1061:0",
    **{
        coordinate: CROSS_DONOR_LABEL
        for coordinate in CROSS_TRANSLATIONS
    },
    "15:1094:1": "15:1086:1",
    "15:1096:2": "15:1088:2",
    "15:1096:3": "15:1088:3",
    "15:1097:0": "15:1089:0",
    "15:1098:1": "15:1090:1",
    "15:1100:1": "15:1092:1",
    "15:1101:1": "15:1093:1",
    "15:1101:2": "15:1093:2",
    "15:1102:0": "15:1094:0",
    "15:1102:1": "15:1094:1",
    "15:1103:0": "15:1095:0",
    "15:1103:3": "15:1095:3",
    "15:1104:1": "15:1096:1",
    "15:1104:3": "15:1096:3",
    "15:1105:0": "15:1097:0",
    "15:1105:2": "15:1097:2",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:1103:1",)
EXACT_BASE_DONOR = {
    1069: (15, 1061),
    1094: (15, 1086),
    1096: (15, 1088),
    1097: (15, 1089),
    1098: (15, 1090),
    1100: (15, 1092),
    1101: (15, 1093),
    1102: (15, 1094),
    1104: (15, 1096),
    1105: (15, 1097),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id != 1103
    },
    1103: (
        "15:1095:0",
        "15:1095:2",
        "15:1095:3",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    1069: ((15, 1061),),
    1094: ((15, 1086),),
    1096: (),
    1097: ((15, 1089), (15, 1513)),
    1098: ((15, 1090),),
    1100: ((15, 1092),),
    1101: ((15, 1093),),
    1102: ((15, 1094),),
    1103: (),
    1104: (),
    1105: tuple((15, record_id) for record_id in range(1097, 1109)),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1096: ((15, 1088),),
    1103: ((15, 1095),),
    1104: ((15, 1096),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    1069: ((), ("026432", "0232", "0233", "0234")),
    1094: ((), ("026432",)),
    1096: ((538, 178), ("025032", "026432", "023C")),
    1097: ((), ("026432", "0232", "0233", "0234")),
    1098: ((), ("025032", "025132")),
    1100: ((), ("025032", "025132")),
    1101: ((), ("025032", "025132", "023C")),
    1102: ((), ("025032", "025132", "0232", "0233050505")),
    1103: ((538, 1132, 568), ("023C", "025032", "025132")),
    1104: ((742,), ("025032", "025132")),
    1105: ((), ("025032", "025132")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1357,
    queue_start=134,
    queue_stop=198,
    slice_first="15:1069:2",
    slice_last="15:1105:2",
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
    source_call_roots=(538, 178, 1132, 568, 742),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1055, 1118)
    ),
    speaker_style=(
        (1069, "system_durability_recovery"),
        (1094, "system_durability_recovery_bullet"),
        (1096, "hostile_defense_reinforcement_report"),
        (1097, "system_durability_recovery"),
        (1098, "formal_reinforcement_discord_proposal"),
        (1100, "system_alliance_termination"),
        (1101, "system_reinforcement_request_cooldown"),
        (1102, "system_discord_operation_penalty"),
        (1103, "formal_discord_operation_success"),
        (1104, "apologetic_discord_operation_failure"),
        (1105, "confident_discord_operation_success"),
    ),
    terminology_policy=(
        ("durability", "내구"),
        ("restore", "회복"),
        ("defense", "방비"),
        ("reinforcement", "원군"),
        ("discord", "반목"),
        ("alliance", "동맹"),
        ("request", "요청"),
        ("friendship", "우호도"),
        ("infamy", "악명"),
        ("scheme", "조략"),
        ("house", "우리 가문"),
        ("dynamic conjunction particle", "와(과)"),
        ("project middle dot", "·"),
        ("project ellipsis", "……"),
        ("project arrow", "→"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B117 queue ordinals 134 through 197 "
        "and the approved Base prefill; pristine PK JP is authoritative "
        "and every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; ten complete records reuse approved "
        "completed Base Korean assemblies selected by raw, literal and "
        "operand-masked identity, while the split discord-result record "
        "uses the completed Base visible wording semantically and preserves "
        "its source-identical hidden newline; record 1069 reciprocally pins "
        "the S1356 recovery prefix and must reproduce completed Base record "
        "1061; Base runtime and VM state are never inherited; durability, "
        "recovery, defense, reinforcements, discord, alliances, requests, "
        "friendship, infamy, schemes, house references, dynamic particles "
        "and historical speaker registers retain established project "
        "wording; calls, inline castle, faction, operation, day-count, old "
        "and new number tokens, protected outer whitespace, line breaks, "
        "the hidden newline, punctuation, terminators, complete record "
        "arity, all forty-seven slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "reciprocal optional neighbor decisions and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=5,
    pins={
        "expected_queue_universe_sha256": (
            "6178B2BC5D4B62D163E7C89A3D7BCBB80D5797E1E57C34FFFD1BA1B718D17558"
        ),
        "expected_queue_slice_sha256": (
            "E8BCDFA4292EFECAABF23CA77E17BE08552763FEE450B1C9EFDE544FF1874705"
        ),
        "expected_prefilled_coordinate_sha256": (
            "55E88BB3659681419FE26FEF86E599B16FA8BE830B5858031E50512CD0DCB1B7"
        ),
        "expected_prefill_slice_context_sha256": (
            "813E8FCC4393A24D38A376D007FA86D43B922FF57326A91571E96E4B89B459D7"
        ),
        "expected_target_coordinate_sha256": (
            "676DE5C28119581CA2AF2BE2CC10832E4DEEAF2046300E7433BBDC12CAB074C6"
        ),
        "expected_source_target_sha256": (
            "CFAE324A95E39D79252A54AB5AE1521ABE54468FE4964881DB0BFC0DFFEBDF14"
        ),
        "expected_current_target_sha256": (
            "1F23508948C6672E20189E857D29BA6FEA5EBBDD72335D83A3A99F89AFB2BE2B"
        ),
        "expected_context_corpus_sha256": (
            "D020BE9FCDAD08931F7FB9B3649273964303C7207D776E53561B29097BE3E246"
        ),
        "expected_gap_contract_sha256": (
            "EA98CDB1B604907BC3A7074D2FBD5F025722E5BEC6250881299DC0E9619369F8"
        ),
        "expected_boundary_sha256": (
            "C494E46987CDE2EE2BEAD758A5722C71B05E68A85E32CA74FA14D9779078833D"
        ),
        "expected_runtime_control_sha256": (
            "1456B5C9EA4F40139B4D6AF66984B417738CAE6ECD20652D6D4541C6D1FCF8C8"
        ),
        "expected_base_search_sha256": (
            "8F627D5EBF694C7AF8451C8EC264EC1C55159BA98603D64E859D310F2888DEBD"
        ),
        "expected_complete_assembly_sha256": (
            "FBCD9DEEC22C942CFBEB708DE96EDBAAE21DE9987251AB94B85DB94E1C38ADA5"
        ),
        "expected_call_graph_sha256": (
            "066E43805B530272DA21CA70CAD33E8B05B9DF0EAA9224A68A738B58AB9D1EF2"
        ),
        "expected_speaker_style_sha256": (
            "849BADDE4FB72F11298477425C2128507B86B7CD84A9F81C5390EF007734BF70"
        ),
        "expected_terminology_policy_sha256": (
            "4F25A9A05CE7B60BFC2E25F05E3576DD382811F34F4BC6275FACB6058F7E4775"
        ),
        "expected_translation_policy_sha256": (
            "D7977D503DBBE5115EEBE343A5F64ABC516BD588EFAD9A2270498B8B2E333BBB"
        ),
        "expected_candidate_sha256": (
            "14756C650A6917B1E906DADA61442F78F2ED283DEB8CEE08A66FB0837AEC822D"
        ),
        "expected_combined_slice_candidate_sha256": (
            "A15938319C3C0259EF869429D99332DA96F58095CEDF697F064A57D30CDF24A2"
        ),
        "expected_combined_changed_literal_count": 48,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B117_S1357",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1357.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1355.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1356.private.v1.jsonl",
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
    """Guard complete Base assemblies and the S1356 split record."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1357 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B117_S1356.private.v1.jsonl"
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
                    "segment 1357 reciprocal S1356 fragment drifted"
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
                f"segment 1357 Base search drifted: {record_id}"
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
                    "segment 1357 Base context drifted: "
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
                        f"segment 1357 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            elif coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment 1357 hidden newline drifted: "
                        f"{coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1357 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1357 exact assembly drifted: {record_id}"
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
        or seen_hidden != hidden_set
    ):
        raise RuntimeError("segment 1357 assembly ownership drifted")
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
