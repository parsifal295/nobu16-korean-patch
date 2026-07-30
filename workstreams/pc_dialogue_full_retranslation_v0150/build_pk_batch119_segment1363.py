#!/usr/bin/env python3
"""Build source-redacted PK B119 segment 1363 residual decisions."""

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
    "15:1283:0": "에게서",
    "15:1283:1": "을(를) 받아\n",
}
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B119_S1362"

TARGET_COORDINATES = (
    "15:1283:3",
    "15:1284:2",
    "15:1285:0",
    "15:1285:2",
    "15:1286:0",
    "15:1286:2",
    "15:1287:0",
    "15:1288:0",
    "15:1289:1",
    "15:1290:1",
    "15:1291:1",
    "15:1293:1",
    "15:1294:0",
    "15:1294:1",
    "15:1294:2",
)
TRANSLATIONS = {
    "15:1283:3": "……",
    "15:1284:2": "이(가) 벌인",
    "15:1285:0": "·",
    "15:1285:2": "감소",
    "15:1286:0": "·",
    "15:1286:2": "감소",
    "15:1287:0": "·",
    "15:1288:0": "·",
    "15:1289:1": "의 내구-",
    "15:1290:1": "의 내구-",
    "15:1291:1": "이(가) 부상",
    "15:1293:1": "감소",
    "15:1294:0": "에서",
    "15:1294:1": "이(가) 벌인",
    "15:1294:2": "을(를) 저지",
}
TARGET_RECORD_IDS = (
    1283,
    1284,
    1285,
    1286,
    1287,
    1288,
    1289,
    1290,
    1291,
    1293,
    1294,
)
EXPECTED_ARITY = {
    1283: 4,
    1284: 4,
    1285: 3,
    1286: 3,
    1287: 2,
    1288: 2,
    1289: 2,
    1290: 2,
    1291: 2,
    1293: 2,
    1294: 3,
}
PREFILL_COMPANION_COORDINATES = (
    *tuple(CROSS_TRANSLATIONS),
    "15:1283:2",
    "15:1284:0",
    "15:1284:3",
    "15:1285:1",
    "15:1286:1",
    "15:1287:1",
    "15:1288:1",
    "15:1289:0",
    "15:1290:0",
    "15:1291:0",
    "15:1293:0",
)
PREFILL_COMPANION_DONOR = {
    **{
        coordinate: CROSS_DONOR_LABEL
        for coordinate in CROSS_TRANSLATIONS
    },
    "15:1283:2": "15:1275:2",
    "15:1284:0": "15:973:0",
    "15:1284:3": "15:973:3",
    "15:1285:1": "15:1277:1",
    "15:1286:1": "15:1277:1",
    "15:1287:1": "15:1279:1",
    "15:1288:1": "15:1279:1",
    "15:1289:0": "15:1281:0",
    "15:1290:0": "15:1282:0",
    "15:1291:0": "15:1283:0",
    "15:1293:0": "15:1285:0",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:1284:1",)
EXACT_BASE_DONOR = {
    1283: (15, 1275),
    1285: (15, 1277),
    1286: (15, 1277),
    1287: (15, 1279),
    1288: (15, 1279),
    1289: (15, 1281),
    1290: (15, 1282),
    1291: (15, 1283),
    1293: (15, 1285),
    1294: (15, 1286),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id != 1284
    },
    1284: (
        "15:1276:0",
        "15:1276:2",
        "15:1276:3",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    1283: ((15, 1275),),
    1284: (),
    1285: ((15, 1277), (15, 1278)),
    1286: ((15, 1277), (15, 1278)),
    1287: ((15, 1279), (15, 1280)),
    1288: ((15, 1279), (15, 1280)),
    1289: ((15, 1281),),
    1290: ((15, 1282),),
    1291: ((15, 1283),),
    1293: ((15, 1285),),
    1294: (
        (15, 811),
        (15, 980),
        (15, 1286),
        (15, 1362),
        (15, 1454),
    ),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1284: (
        (15, 907),
        (15, 973),
        (15, 1276),
        (15, 1365),
        (15, 1444),
        (15, 1485),
    ),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    1284: (
        (15, 973),
        (15, 1276),
        (15, 1365),
        (15, 1444),
        (15, 1485),
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    1283: ((178,), ("025032", "023C", "026432")),
    1284: ((538, 592), ("026432", "025032", "023C")),
    1285: ((), ("026432", "0232")),
    1286: ((), ("026432", "0232")),
    1287: ((), ("026432",)),
    1288: ((), ("026432",)),
    1289: ((), ("024633", "026432", "0232050505")),
    1290: ((), ("024633", "026432", "0232050505")),
    1291: ((), ("024633",)),
    1293: ((), ("026432", "0232")),
    1294: ((), ("026432", "025032", "023C")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1363,
    queue_start=134,
    queue_stop=200,
    slice_first="15:1283:2",
    slice_last="15:1325:0",
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
    source_call_roots=(178, 538, 592),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1270, 1338)
    ),
    speaker_style=(
        (1283, "system_tunnel_damage_result"),
        (1284, "male_spy_capture_report"),
        (1285, "system_durability_damage_bullet"),
        (1286, "system_durability_damage_bullet"),
        (1287, "system_tunnel_failure_bullet"),
        (1288, "system_tunnel_failure_bullet"),
        (1289, "system_tunnel_damage_result"),
        (1290, "system_tunnel_damage_result"),
        (1291, "system_tunnel_injury_failure"),
        (1293, "system_durability_damage_result"),
        (1294, "system_operation_prevention"),
    ),
    terminology_policy=(
        ("tunnel assault", "땅굴 공략"),
        ("durability", "내구"),
        ("defense", "방비"),
        ("spy", "간자"),
        ("secret order", "밀명"),
        ("injury", "부상"),
        ("prevent", "저지"),
        ("dynamic source particle", "에게서"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("project middle dot", "·"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B119 queue ordinals 134 through 199 "
        "and the approved Base prefill; pristine PK JP is authoritative "
        "and every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; ten complete records reuse approved "
        "completed Base Korean assemblies selected by raw, literal and "
        "operand-masked identity, while the spy-capture record uses the "
        "completed Base visible wording semantically and preserves its "
        "source-identical hidden newline; record 1283 reciprocally pins the "
        "S1362 source and object fragments and must reproduce completed "
        "Base record 1275; Base runtime and VM state are never inherited; "
        "tunnel assaults, durability, defenses, spies, secret orders, "
        "injuries, prevention, dynamic particles and system or male speaker "
        "registers retain established project wording; calls, inline "
        "castle, faction, stratagem, spy, officer and damage-value tokens, "
        "protected outer whitespace, line breaks, the hidden newline, "
        "middle dots, ellipses, terminators, complete record arity, all "
        "fifty-one slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, reciprocal "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=5,
    pins={
        "expected_queue_universe_sha256": (
            "DC944BC6399C29C866DF74A3798EC8CF6197780D468D34FB2B3777B5BE629D99"
        ),
        "expected_queue_slice_sha256": (
            "F46FD789206307AE0E8C925378343A77FA3775E465AD8B18DC3BED4541F205C8"
        ),
        "expected_prefilled_coordinate_sha256": (
            "E015DEA8DDB84ABA80E8E87C35E2AFA4DB97E68CC6B114C2A689AC44A71EEA28"
        ),
        "expected_prefill_slice_context_sha256": (
            "F557E4C614CA24F465D8D8D80B3CF5C918D77369EAD9795004D1FF51209FF51B"
        ),
        "expected_target_coordinate_sha256": (
            "C2407F785D5E3535AA2D69C97DBA421A2D80AF90278E37D23FFEEA494E352EF2"
        ),
        "expected_source_target_sha256": (
            "CEEBD4C0A4C3F9169F1FE1F2E65739A2B11EA69F6363A94D3DC383813BA57752"
        ),
        "expected_current_target_sha256": (
            "70D7BBA81641BBC3488F1C2DB1895F4371477A0D08962F05F2B23F20EBB14054"
        ),
        "expected_context_corpus_sha256": (
            "D2986D691DE08C2C978E09ADA920896A94DE82CA761A6FC64625FDDCD496284B"
        ),
        "expected_gap_contract_sha256": (
            "AC6478AC0FAC2A5027A0DA8D31FCF8B25A1C1F1A2B1F3C0992A2A463D0DB96E3"
        ),
        "expected_boundary_sha256": (
            "706DF439A2231E22032CEA9637AF21D933A0FDADD702345EA5437C470FD56C8C"
        ),
        "expected_runtime_control_sha256": (
            "8EE6E0136A9E48704A7B234AA12FA8A0FE359A9C4641B76C7432895AE2C2F774"
        ),
        "expected_base_search_sha256": (
            "3EE8AC2BD58E0322601A053142AAEC402393D6B4852874347C247F7ABB747452"
        ),
        "expected_complete_assembly_sha256": (
            "B949346BC37658D46CF8E0E4B1E6921C45D79E790DACF59BFF21F9BEEF57436D"
        ),
        "expected_call_graph_sha256": (
            "1C11407775D2B1A203E17C36B578A5676A28ED15117675CF7728BAE9FA9CE045"
        ),
        "expected_speaker_style_sha256": (
            "7577FE1B9950CA11D288E4EA475E81732365EF1C0F7660D6DFDF7EF1A4301A8F"
        ),
        "expected_terminology_policy_sha256": (
            "E31FBB66A062F41FE88344A1B5FB47095C7CEECC23BC7F84E6264EA443DF126E"
        ),
        "expected_translation_policy_sha256": (
            "9979B670A015183855B68B523D1953DDE8B9E34571A9A4CFACB7D6431DA53422"
        ),
        "expected_candidate_sha256": (
            "2BB82E8F69BC54ABD54A821099742EAFB8A17BAF4400D656AA33ED897B63A34C"
        ),
        "expected_combined_slice_candidate_sha256": (
            "697B8A4B334934B6F59F05FBE5A13BB274C00B877A0708234CBFC1E486C2827D"
        ),
        "expected_combined_changed_literal_count": 48,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B119_S1363",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1363.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1361.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B119_S1362.private.v1.jsonl",
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
        raise RuntimeError("segment 1363 Base promoted input drifted")
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
                    "segment 1363 reciprocal S1362 fragment drifted"
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
                f"segment 1363 Base search drifted: {record_id}"
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
                    "segment 1363 Base context drifted: "
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
                        f"segment 1363 companion drifted: {coordinate}"
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
                        f"segment 1363 hidden newline drifted: "
                        f"{coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1363 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1363 exact assembly drifted: {record_id}"
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
        raise RuntimeError("segment 1363 assembly ownership drifted")
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
