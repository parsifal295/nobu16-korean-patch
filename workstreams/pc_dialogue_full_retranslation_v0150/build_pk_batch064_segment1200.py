#!/usr/bin/env python3
"""Build source-redacted PK B064 segment 1200 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch056_segment1179.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B064_S1200.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B064_S1199.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B064_S1201.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1200
QUEUE_BATCH_ID = "pk_msggame-B064"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2027:1",
    "7:2028:1",
    "7:2029:0", "7:2029:1",
    "7:2031:0", "7:2031:1",
    "7:2032:1",
    "7:2033:1",
    "7:2034:0",
    "7:2038:1",
    "7:2061:1",
    "7:2070:1",
)
TRANSLATIONS = {
    "7:2027:1": "을(를) 친다",
    "7:2028:1": "을(를) 쳐라",
    "7:2029:0": "을(를) 쳐라\n",
    "7:2029:1": "을(를) 지켜야 한다",
    "7:2031:0": "을(를) 지킨다!\n",
    "7:2031:1": ", 각오해라!",
    "7:2032:1": "을(를) 쳐라!",
    "7:2033:1": "을(를) 요격한다",
    "7:2034:0": "전선을 방어하고자\n",
    "7:2038:1": "(으)로 돌아가자!",
    "7:2061:1": "까지 후퇴하라!",
    "7:2070:1": "까지 물러나라!",
}
TARGET_RECORD_IDS = (
    2027, 2028, 2029, 2031, 2032,
    2033, 2034, 2038, 2061, 2070,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {record_id: 2 for record_id in TARGET_RECORD_IDS}
PREFILL_COMPANION_COORDINATES = (
    "7:2027:0",
    "7:2028:0",
    "7:2032:0",
    "7:2033:0",
    "7:2034:1",
    "7:2038:0",
    "7:2061:0",
    "7:2070:0",
)
PREFILL_COMPANION_DONOR = {
    "7:2027:0": "7:1987:0",
    "7:2028:0": "7:1988:0",
    "7:2032:0": "7:1992:0",
    "7:2033:0": "7:1993:0",
    "7:2034:1": "7:1963:1",
    "7:2038:0": "7:1997:0",
    "7:2061:0": "7:2020:0",
    "7:2070:0": "7:2029:0",
}
EXACT_BASE_DONOR = {
    2027: (7, 1987),
    2028: (7, 1988),
    2029: (7, 1989),
    2031: (7, 1991),
    2032: (7, 1992),
    2033: (7, 1993),
    2038: (7, 1997),
    2061: (7, 2020),
    2070: (7, 2029),
}
SEMANTIC_BASE_CONTEXT = {
    2034: ("7:1963:0", "7:1963:1", "7:1994:0"),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (
        (EXACT_BASE_DONOR[record_id],)
        if record_id in EXACT_BASE_DONOR
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        1989, 1990, 2026, 2027, 2028, 2029, 2030, 2031,
        2032, 2033, 2034, 2035, 2037, 2038, 2039,
        2060, 2061, 2062, 2069, 2070, 2071, 2116, 2117,
    )
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2027: ((), ("026432", "026E32")),
    2028: ((), ("026432", "026E32")),
    2029: ((), ("026E32", "026432")),
    2031: ((), ("026432", "026E32")),
    2032: ((), ("026432", "026E32")),
    2033: ((), ("026432", "026E32")),
    2034: ((), ("029632",)),
    2038: ((), ("026432",)),
    2061: ((), ("026432",)),
    2070: ((), ("026432",)),
}
SPEAKER_STYLE = (
    (2027, "attack_force_core_target_command"),
    (2028, "defend_and_strike_command"),
    (2029, "strike_and_defend_command"),
    (2031, "defense_challenge_command"),
    (2032, "urgent_defense_command"),
    (2033, "interception_command"),
    (2034, "front_line_defense_march"),
    (2038, "stratagem_detected_return"),
    (2061, "hopeless_retreat_command"),
    (2070, "elder_low_odds_retreat_command"),
)
TERMINOLOGY_POLICY = (
    ("attack force", "공략군"),
    ("core", "핵심"),
    ("defend", "지키다"),
    ("strike", "치다"),
    ("intercept", "요격"),
    ("front line", "전선"),
    ("defend the front", "전선을 방어하다"),
    ("return", "돌아가다"),
    ("retreat", "후퇴하다"),
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
    "EF6669436AF3F074CEA34129DC31D3E67E59D102A7127DB1D64B297B36C5E217"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "D1A56ACC32214827D89B5DA8CC30250468F6A1492ED78D21273CE2A40A4471D6"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "605BCB099A02E82E94C9F74558CF66848C4627752947A8D91B6F7FFDEE2A68F2"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "0C5C671394C535633048C5D998EA8CC146BF1274C97379EF978175126227E444"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "457E1D1379847681A5BE9BE92D92CDE131CADFD3FE127E3B38421535EC4ABCE4"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "E931BA48240B1C5DF8264B76AF6ECD1094586090F53C0C6F70DCD021EC594C29"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "4A085C9652E7AF62FF2545BEDE9C133A928894F0E6930532A92C42A070CE0986"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "551201C95B3F8C970CE46BED4CBF4D3579766A7BD524FCE512A0406F4B18F7B3"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "0343371953D3B68CD0A567C2EEDDB1F27C7A1980DEFDED755F807736096259C4"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1E780FF25F692857D68D8662573F7271CA591C036084EB3248C6490E0AF0A04B"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "F3EBE494E917883013AB7969C03CBB48FE8FDF862941B5C781D84807C5A33D4D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "95A6F5F776347F6FBEB35B53402FF57DC10F96DD717E59C17D7342B3C952F42B"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "018DAD579195D77E69D40DDDE3D9AA17A53CB9703864C198900F8061FA1B0CF1"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "D9B9AC90D1BB63141E0B12E09F4CBBC7EF2B9DBF389EC7A4F84B79ABF46EC368"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "551B138E7400AFA8144C0BB973D8A875264C1E366B88597ABD95B77DFC65DB8C"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "0BACDCC5E76BA10B9A83E1DE4D510770968EA15103E78FC3736135881A540619"
)
EXPECTED_CANDIDATE_SHA256 = (
    "EE10C02C124289F4C1C1CACBD47643F8C53C10B65516A1740E20DD04E1FE5BE3"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "5E0CE3A1E4150D51D7A2E37A21E98205E41AC690FB87663A229D7BFAEAA86B89"
)
EXPECTED_CHANGED_LITERAL_COUNT = 9
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 52

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; nine complete records use raw-exact completed "
    "Base minus-forty donors, while the PK-only front-line defense record "
    "uses completed Base defense-march wording as manual semantic context "
    "and an exact Base-prefilled destination companion; all fifty-five "
    "slice prefills and eight same-record companions are validated; Base "
    "runtime and VM state are never inherited; complete records, castle and "
    "enemy-force tokens, protected outer whitespace, source and current "
    "gaps, queue and segment boundaries, two-run reproduction, tamper "
    "rejection, reverse overlays, outside-scope identity, and Steam "
    "read-only state are guarded"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1200_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
CORE = PARENT.CORE
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 128
        or len(visible) != 200
        or visible[0] != "7:1990:0"
        or visible[-1] != "7:2117:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B064 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:2027:1"
        or queue_slice[-1] != "7:2070:1"
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
    if len(prefilled) != 55 or residual != TARGET_COORDINATES:
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
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
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
        donor_rows: list[dict[str, Any]] = []
        for donor_coordinate in donor_coordinates:
            row = base_rows.get(donor_coordinate)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(row)
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual")
                seen_target.add(coordinate)
                continue
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
            assembled.append(str(prefill["translation"]))
            owners.append("base_exact_prefill_runtime_pending")
            seen_prefill.add(coordinate)
        donor_translations = tuple(
            str(row["translation"]) for row in donor_rows
        )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment {SEGMENT} exact donor assembly drifted: "
                f"{record_id}"
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
                        str(row["runtime_review"]),
                    )
                    for coordinate, row in zip(
                        donor_coordinates,
                        donor_rows,
                    )
                ),
                "complete_exact" if exact else "semantic_context_only",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                donor_translations,
                CORE.runtime_controls(source),
                CORE.runtime_controls(records_by_label["current"][key]),
                (
                    "complete_translation_equals_completed_base_donor"
                    if exact
                    else "manual_pk_semantic_adaptation"
                ),
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
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
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
        or len(prefilled) != 55
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
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
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
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
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
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        EXPECTED_QUEUE_UNIVERSE_SHA256,
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
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 12
        or len(validated) != 12
        or counts != Counter({"runtime_fragment_pending": 12})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
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
        "segment": "pk_msggame_B064_S1200",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 55,
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
