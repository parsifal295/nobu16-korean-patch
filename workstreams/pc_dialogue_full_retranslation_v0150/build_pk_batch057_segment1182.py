#!/usr/bin/env python3
"""Build source-redacted PK B057 segment 1182 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B057_S1182.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B057_S1183.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B057_S1184.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1182
QUEUE_BATCH_ID = "pk_msggame-B057"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:891:1",
    "7:892:0", "7:892:2",
    "7:893:2",
    "7:894:1",
    "7:895:0", "7:896:0", "7:897:0", "7:898:0",
    "7:899:0", "7:900:0", "7:901:0",
    "7:909:0",
)
TRANSLATIONS = {
    "7:891:1": "인가……",
    "7:892:0": "·",
    "7:892:2": "란……",
    "7:893:2": "……",
    "7:894:1": "」의\n",
    "7:895:0": "이(가) 병력 「",
    "7:896:0": "이(가) 병력 「",
    "7:897:0": "이(가) 병력 「",
    "7:898:0": "이(가) 병력 「",
    "7:899:0": "이(가) 병력 「",
    "7:900:0": "이(가) 병력 「",
    "7:901:0": "이(가) 병력 「",
    "7:909:0": "이(가) 「",
}
TARGET_RECORD_IDS = tuple(
    dict.fromkeys(
        int(coordinate.split(":")[1])
        for coordinate in TARGET_COORDINATES
    )
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    891: 2,
    892: 3,
    893: 3,
    894: 5,
    895: 3,
    896: 3,
    897: 3,
    898: 3,
    899: 3,
    900: 3,
    901: 3,
    909: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:891:0",
    "7:892:1",
    "7:893:0", "7:893:1",
    "7:894:0", "7:894:2", "7:894:3", "7:894:4",
    "7:895:1", "7:895:2",
    "7:896:1", "7:896:2",
    "7:897:1", "7:897:2",
    "7:898:1", "7:898:2",
    "7:899:1", "7:899:2",
    "7:900:1", "7:900:2",
    "7:901:1", "7:901:2",
    "7:909:1",
)
EXACT_BASE_DONOR = {
    891: (7, 880),
    892: (7, 881),
    893: (7, 882),
    894: (7, 883),
    895: (7, 884),
    896: (7, 884),
    897: (7, 884),
    898: (7, 884),
    899: (7, 884),
    900: (7, 884),
    901: (7, 884),
    909: (7, 898),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
REPEATED_ARMY_BASE_MATCHES = tuple((7, value) for value in range(884, 891))
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (
        (EXACT_BASE_DONOR[record_id],)
        if record_id in {891, 909}
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (
        REPEATED_ARMY_BASE_MATCHES
        if 895 <= record_id <= 901
        else (EXACT_BASE_DONOR[record_id],)
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        890, 891, 892, 893, 894, 895, 901, 902, 908, 909, 910,
        932, 933, 934, 1001, 1002,
    )
)
SOURCE_CALL_ROOTS = (202, 538, 784, 1096, 1126)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    891: ((202,), ("023C",)),
    892: ((1126,), ("023C", "024833")),
    893: ((784,), ("023C",)),
    894: ((538,), ("025032", "024833", "023C", "026432")),
    895: ((1096,), ("025032", "023C", "026432")),
    896: ((1096,), ("025032", "023C", "026432")),
    897: ((1096,), ("025032", "023C", "026432")),
    898: ((1096,), ("025032", "023C", "026432")),
    899: ((1096,), ("025032", "023C", "026432")),
    900: ((1096,), ("025032", "023C", "026432")),
    901: ((1096,), ("025032", "023C", "026432")),
    909: ((), ("025032", "026432")),
}
SPEAKER_STYLE = (
    (891, "historical_castle_defense_reaction"),
    (892, "oniwakako_spear_reaction"),
    (893, "historical_survival_reaction"),
    (894, "enemy_sortie_report"),
    (895, "army_targeting_ui"),
    (896, "army_targeting_ui"),
    (897, "army_targeting_ui"),
    (898, "army_targeting_ui"),
    (899, "army_targeting_ui"),
    (900, "army_targeting_ui"),
    (901, "army_targeting_ui"),
    (909, "march_start_ui"),
)
TERMINOLOGY_POLICY = (
    ("oniwakako", "오니와코"),
    ("future course and allegiance", "앞으로의 거취"),
    ("troop strength", "병력"),
    ("our faction", "우리 세력"),
    ("sortie", "출진"),
    ("march", "진군"),
    ("dynamic name and place delimiters", "「」"),
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
    "C7672FD65769644061BE1F6911D867BC7E6E01F33131BFFF1178321DB7982BAA"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "7FBC1B5D79DF22E9A56CF01BF17AC8598B4C69903F226FB84F44E43F9B34275D"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "DA46E5C5A4C45B56E297BBEE400AEBF2C5C6451EBC3E821115E422A2F11E434A"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "484364CA6CE7F496C6536052D3FFD8A48E6FF2555168ACF42E0795CED74DD980"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "D71BEF9A8C4707DB6A4384B22EC0206299A6FAAFBF3C2E19F2DEB00E8F988736"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "FFF3592E29E450EAF8893C787131D0278A5DA07ED3F2FC07736CA3A524220BB6"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "9F224D57A1D387C9C07B1555F3FD534B612685C27639C43551B461EE1814E3E9"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "9F482B37FCF2D75438195AFC24978C669E3A477F73FC638ECEA4745C149BC7DF"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "1C568015DDEA87C04C6ED2CD788F374430738DC168CDF6908AD6176BBF249456"
)
EXPECTED_BOUNDARY_SHA256 = (
    "E20252044124D948378088FFEEA5E8AE837BEBF26EDE43D3746755787C2E9BAC"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "DD639282A9E774BBBD49C591265249C64F807551ACE1D489104D7C4AB0B1BE62"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "8B8CD0ECE5B540D28007ECE6C28A4FF5DD6A0FF4714935E479FAEA9FF1363D46"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "8949C7F2830C96200C94B73A933484AB2E285A5CD5D13EA559DA9391100237E5"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F756231865E0AE07D0397F7FFE45E2A3C21F20B1DFE4685CC5C7C8E613CCE3A"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "8F31525631B3E94C5B195B53C550E4FE720D90865E16CA61E3ADFA6BF2A32CAB"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "E3F0FE6F0B557DC0DB0252A52459C9AF3A6D2BEA2871CC9D7B2660444B8EFFE5"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "D582CFBB9D287DDAA07200053FFAC5DF5047F75BB9F55D612EE53AC472CB809C"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F6528C0CD9F804FB741578EEE32C1CDD870B88CB6F4CD49B66E19AA010E49010"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "2FD91DDA6D8D65DA16179B436473982ECE394ED118330619857E87E71BBD4D48"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 59

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; all twelve complete PK records use manually "
    "selected completed Base literal donors, including ten call-operand-"
    "masked matches and two raw-exact matches; Base runtime and VM state "
    "are never inherited; all fifty-four queue prefills and twenty-three "
    "same-record companions are validated; complete records, direct calls, "
    "person, faction, troop-count, castle and place tokens, protected outer "
    "whitespace, queue and segment boundaries, two-run reproduction, tamper "
    "rejection, reverse overlays, outside-scope identity, and Steam read-only "
    "state are guarded"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1182_parent",
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
context_records = PARENT.context_records


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
        len(rows) != 112
        or len(visible) != 200
        or visible[0] != "7:891:0"
        or visible[-1] != "7:1002:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B057 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:891:0"
        or queue_slice[-1] != "7:933:0"
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
    if len(prefilled) != 54 or residual != TARGET_COORDINATES:
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
        or len(prefilled) != 54
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
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    PARENT.patch_parent_globals()
    CORE.queue_evidence = queue_evidence
    CORE.base_and_assembly_evidence = PARENT.base_and_assembly_evidence


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
        len(rows) != 13
        or len(validated) != 13
        or counts != Counter({"runtime_fragment_pending": 13})
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
        "segment": "pk_msggame_B057_S1182",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 54,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count":
        sum(bool(value) for value in EXPECTED_BASE_RAW_MATCHES.values()),
        "masked_complete_base_donor_record_count":
        sum(not bool(value) for value in EXPECTED_BASE_RAW_MATCHES.values()),
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
