#!/usr/bin/env python3
"""Build source-redacted PK B068 segment 1208 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch066_segment1203.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B068_S1208.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B068_S1209.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B068_S1210.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1208
QUEUE_BATCH_ID = "pk_msggame-B068"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2595:0",
    "7:2595:1",
    "7:2597:0",
    "7:2598:0",
    "7:2603:0",
    "7:2605:0",
    "7:2607:0",
    "7:2608:1",
    "7:2611:0",
    "7:2612:0",
)
TRANSLATIONS = {
    "7:2595:0": "의",
    "7:2595:1": "이 전사",
    "7:2597:0": "일번창,",
    "7:2598:0": "일번창,",
    "7:2603:0": "일번창,",
    "7:2605:0": "일번창,",
    "7:2607:0": "일번창,",
    "7:2608:1": "다!\n모두,",
    "7:2611:0": "일번창은",
    "7:2612:0": "일번창은",
}
TARGET_RECORD_IDS = (
    2595,
    2597,
    2598,
    2603,
    2605,
    2607,
    2608,
    2611,
    2612,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2595: 2,
    2597: 2,
    2598: 2,
    2603: 2,
    2605: 2,
    2607: 2,
    2608: 3,
    2611: 2,
    2612: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:2597:1",
    "7:2598:1",
    "7:2603:1",
    "7:2605:1",
    "7:2607:1",
    "7:2608:0",
    "7:2608:2",
    "7:2611:1",
    "7:2612:1",
)
PREFILL_COMPANION_DONOR = {
    "7:2597:1": "7:2531:1",
    "7:2598:1": "7:2532:1",
    "7:2603:1": "7:2537:1",
    "7:2605:1": "7:2539:1",
    "7:2607:1": "7:2541:1",
    "7:2608:0": "7:2540:0",
    "7:2608:2": "7:2542:2",
    "7:2611:1": "7:2545:1",
    "7:2612:1": "7:2546:1",
}
EXACT_BASE_DONOR = {
    2595: (7, 2529),
    2597: (7, 2531),
    2598: (7, 2532),
    2603: (7, 2537),
    2605: (7, 2539),
    2607: (7, 2541),
    2608: (7, 2542),
    2611: (7, 2545),
    2612: (7, 2546),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (base_coordinate,)
    for record_id, base_coordinate in EXACT_BASE_DONOR.items()
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        2528, 2529, 2530, 2531, 2532, 2533,
        2536, 2537, 2538, 2539, 2540, 2541,
        2542, 2543, 2544, 2545, 2546, 2547,
        2579, 2580, 2594, 2595, 2596, 2597,
        2598, 2599, 2602, 2603, 2604, 2605,
        2606, 2607, 2608, 2609, 2610, 2611,
        2612, 2613, 2628, 2629, 2732, 2733,
    )
)
SOURCE_CALL_ROOTS = (1,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2595: ((), ("025032", "024633")),
    2597: ((1,), ()),
    2598: ((1,), ()),
    2603: ((1,), ()),
    2605: ((1,), ()),
    2607: ((1,), ()),
    2608: ((1, 1), ()),
    2611: ((1,), ()),
    2612: ((1,), ()),
}
SPEAKER_STYLE = (
    (2595, "house_officer_battle_death_notification"),
    (2597, "humble_first_spear_boast"),
    (2598, "mikawa_warrior_first_spear_boast"),
    (2603, "peace_seeking_first_spear_resolution"),
    (2605, "loyal_warrior_first_spear_boast"),
    (2607, "strategist_first_spear_report"),
    (2608, "commander_first_spear_example"),
    (2611, "elder_first_spear_boast"),
    (2612, "modest_first_spear_credit"),
)
TERMINOLOGY_POLICY = (
    ("first spear distinction", "일번창"),
    ("fallen in battle", "전사"),
    ("lord", "주군"),
    ("Mikawa warrior", "미카와 무사"),
    ("peaceful age", "태평성대"),
    ("battle demon", "수라"),
    ("loyalty and righteousness", "충의"),
    ("stratagem", "계책"),
    ("break enemy momentum", "기세를 꺾다"),
    ("experience overcomes youth", "연륜은 못 당하다"),
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "0B0152048629FD60899400061AE97E285150CC2C63EC3D6E9CA7FB4153AE1127"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "0381E2DC236BBE813AC1564DB53DB8D253DCB42A3B88E291106C09D232DD92CF"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "8EB4EA64206947AF9F07AAC6C5DD4778DE0A0CB2CA35AE454711DD6B5C181205"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "7D60CDCDCBE7B9FA90303510D93AE05DB60DBB9787E5450A49D7D2FFEE14C39B"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "6A4E812FE04016ADF2853631FBCCF49F551C6C8FC3A7E72DE15AA4F32D2E2300"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C1689EDC579E211D80547E55813F743736E4CEB8D510093EC3A8EA5148969863"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "BAF90D1A07135C16B8F35D8D0440E68670795116530345C89DA903ACFC5A9407"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "AC249CC38FA4F88DA00D4FD62026083DBA327ED469131FE3793978E21B859EFB"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "0DB5441343A21928915B1A883E179BE2661990F81ECFF272A6D5A79448E0C552"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C4E2F0113EB1A37922EAD13F43A97E80E65AB9C9D9828BCABF9062D0E1432C47"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "C3BFD19FC235716CA3D5346EF8CB366025E18E78A21FED4D7396E21F136313EE"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "14810E679897DFE25DADE8EDFDFA01F3D5F550EF80EF6B79F85A2B2B978B1373"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "D6687C660238C2B219DF49CF9F898BEC29D396C999FC0534E4BF11D39395A985"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "413EA21B13C49DFD7139BBFDF3ADE6AEC824ACD19A7B76AAECBD9418D220F69A"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "C23A1B89F79E1EA3F1F3284F7C3E1F1E535F65DA85C665D4A12EA435C3733986"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "EBDA2AC42F6E88AE85DCBE075E1D8126E6D4F0F2F70E951BBAB78A9EFFE22629"
)
EXPECTED_CANDIDATE_SHA256 = (
    "6BAAD6A2302FD9D5A70F8409DD8409CEEBBB30E9F3E194D34E9139F311084474"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "FBF89F57E15E8B62D89A3CE120ACE8B23378B7D1F74C2EB1CD86B530C1E29CC1"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 61

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; complete PC English, "
    "Simplified Chinese and Traditional Chinese context was manually "
    "reviewed where present; all nine complete PK source records have one "
    "raw, literal and call-operand-exact completed Base donor, whose final "
    "Korean was reused only after manual semantic, terminology and "
    "speaker-register review; the ten residual fragments and nine "
    "approved same-record prefills reproduce every complete donor "
    "translation, including the project historical first-spear term; "
    "house, officer and call operands, newlines, protected outer "
    "whitespace, source and current gaps and inline tokens are guarded; "
    "all fifty-seven prefills in the sixty-seven-row slice are validated "
    "and the combined slice is rebuilt in both orders and reversed byte-"
    "exactly; two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; completed Base "
    "runtime and VM state are never inherited and all residual fragments "
    "remain PK runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1208_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ENGINE = PARENT.ENGINE
CORE = PARENT.CORE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = queue_rows(prepared)
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 154
        or len(visible) != 200
        or visible[0] != "7:2580:0"
        or visible[-1] != "7:2733:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B068 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:2580:0"
        or queue_slice[-1] != "7:2628:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in prefill_rows
    )
    if len(prefilled) != 57 or residual != TARGET_COORDINATES:
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and CORE.mask_call_operands(record)
                == CORE.mask_call_operands(source)
            )
        )
        donor_key = EXACT_BASE_DONOR[record_id]
        donor_coordinates = tuple(
            f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        donor_rows: list[dict[str, Any]] = []
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id, donor_coordinate in enumerate(donor_coordinates):
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review") not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base donor: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(donor)
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owners.append("segment_manual_exact_base_reuse")
                seen_target.add(coordinate)
            else:
                prefill = prefill_rows.get(coordinate)
                if (
                    coordinate not in PREFILL_COMPANION_COORDINATES
                    or prefill is None
                    or prefill.get("semantic_review") != "approved"
                    or prefill.get("runtime_review") != "pending"
                    or prefill["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} companion drifted: {coordinate}"
                    )
                translation = str(prefill["translation"])
                owners.append("base_exact_prefill_runtime_pending")
                seen_prefill.add(coordinate)
            assembled.append(translation)
        donor_translations = tuple(
            str(row["translation"]) for row in donor_rows
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
            or tuple(assembled) != donor_translations
        ):
            raise RuntimeError(
                f"segment {SEGMENT} exact Base assembly drifted: {record_id}"
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                donor_coordinates,
                tuple(
                    (
                        coordinate,
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for coordinate, row in zip(donor_coordinates, donor_rows)
                ),
                "complete_exact_manual_semantic_review",
                "base_runtime_state_not_inherited",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                donor_translations,
                CORE.runtime_controls(source),
                CORE.runtime_controls(current),
                "complete_translation_equals_completed_base_donor",
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 67
        or len(prefilled) != 57
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256 != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if (
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_COMBINED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined changed count drifted: {changed}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "PREFILL_COMPANION_DONOR": PREFILL_COMPANION_DONOR,
        "EXACT_BASE_DONOR": EXACT_BASE_DONOR,
        "SEMANTIC_BASE_CONTEXT": SEMANTIC_BASE_CONTEXT,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256": EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT":
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.base_and_assembly_evidence = base_and_assembly_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    PARENT.patch_parent_globals()
    CORE.queue_evidence = queue_evidence
    CORE.base_and_assembly_evidence = base_and_assembly_evidence


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    str,
    int,
    tuple[str, ...],
]:
    patch_parent_globals()
    return PARENT.build_rows()


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    if DISCOVERED_PINS:
        print(json.dumps(
            DISCOVERED_PINS,
            sort_keys=True,
            separators=(",", ":"),
        ))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 10
        or len(validated) != 10
        or counts != Counter({"runtime_fragment_pending": 10})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    patch_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B068_S1208",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 57,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count":
        len(EXACT_BASE_DONOR),
        "masked_complete_base_donor_record_count": 0,
        "semantic_base_context_record_count":
        len(SEMANTIC_BASE_CONTEXT),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
        "candidate_sha256": candidate_sha256,
        "combined_slice_candidate_sha256": combined_sha256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "steam_sha256_before": steam_before,
        "steam_sha256_after": steam_after,
        "base_runtime_state_inherited": False,
        "source_current_gap_equality_guarded": True,
        "inline_token_controls_guarded": True,
        "direct_call_graphs_guarded": True,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
