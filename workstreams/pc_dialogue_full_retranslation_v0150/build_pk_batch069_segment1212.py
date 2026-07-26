#!/usr/bin/env python3
"""Build source-redacted PK B069 segment 1212 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch067_segment1205.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B069_S1212.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B069_S1211.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B069_S1213.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1212
QUEUE_BATCH_ID = "pk_msggame-B069"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2799:0",
    "7:2799:1",
    "7:2802:0",
    "7:2805:0",
    "7:2806:0",
    "7:2807:0",
    "7:2808:0",
    "7:2809:0",
    "7:2820:0",
    "7:2821:0",
    "7:2822:0",
    "7:2823:0",
    "7:2824:0",
    "7:2830:0",
    "7:2831:3",
)
TRANSLATIONS = {
    "7:2799:0": "이(가)",
    "7:2799:1": "을(를) 편입",
    "7:2802:0": "간자에게",
    "7:2805:0": "이제",
    "7:2806:0": "이제",
    "7:2807:0": "이제",
    "7:2808:0": "이제",
    "7:2809:0": "이제",
    "7:2820:0": "이제",
    "7:2821:0": "이제",
    "7:2822:0": "이제",
    "7:2823:0": "이제",
    "7:2824:0": "이제",
    "7:2830:0": "은(는) 통과할 수",
    "7:2831:3": "이지만",
}
TARGET_RECORD_IDS = (
    2799,
    2802,
    2805,
    2806,
    2807,
    2808,
    2809,
    2820,
    2821,
    2822,
    2823,
    2824,
    2830,
    2831,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    record_id: 4 if record_id == 2831 else 2
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = (
    "7:2802:1",
    "7:2805:1",
    "7:2806:1",
    "7:2807:1",
    "7:2808:1",
    "7:2809:1",
    "7:2820:1",
    "7:2821:1",
    "7:2822:1",
    "7:2823:1",
    "7:2824:1",
    "7:2830:1",
    "7:2831:0",
    "7:2831:1",
    "7:2831:2",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
RETURN_RECORD_IDS = (
    2805,
    2806,
    2807,
    2808,
    2809,
    2820,
    2821,
    2822,
    2823,
    2824,
)
RETURN_BASE_MATCHES = (
    (7, 2739),
    (7, 2740),
    (7, 2741),
    (7, 2742),
    (7, 2743),
    (7, 2754),
    (7, 2755),
    (7, 2756),
    (7, 2757),
    (7, 2758),
)
EXACT_BASE_DONOR = {
    2799: (7, 2733),
    2802: (7, 2736),
    **{record_id: (7, 2739) for record_id in RETURN_RECORD_IDS},
    2830: (7, 2764),
    2831: (7, 2765),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    2799: ((7, 2733),),
    2802: ((7, 2736),),
    **{
        record_id: RETURN_BASE_MATCHES
        for record_id in RETURN_RECORD_IDS
    },
    2830: (),
    2831: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    2830: ((7, 2764),),
    2831: ((7, 2765),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        2733,
        2736,
        2739,
        2764,
        2765,
        2785,
        2786,
        2798,
        2799,
        2800,
        2801,
        2802,
        2803,
        2804,
        2805,
        2806,
        2807,
        2808,
        2809,
        2810,
        2819,
        2820,
        2821,
        2822,
        2823,
        2824,
        2825,
        2829,
        2830,
        2831,
        2832,
        2833,
    )
)
SOURCE_CALL_ROOTS = (7, 568, 610, 748, 1090)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2799: ((), ("025032", "028C32")),
    2802: ((), ("029632",)),
    **{
        record_id: ((), ("029632",))
        for record_id in RETURN_RECORD_IDS
    },
    2830: ((748, 1090), ("026432",)),
    2831: ((7, 610, 568), ("023C",)),
}
SPEAKER_STYLE = (
    (2799, "faction_absorption_announcement"),
    (2802, "spy_disruption_defiance"),
    *tuple(
        (record_id, "mission_complete_castle_return")
        for record_id in RETURN_RECORD_IDS
    ),
    (2830, "blocked_route_castle_return"),
    (2831, "enemy_count_reinforcement_assessment"),
)
TERMINOLOGY_POLICY = (
    ("assimilate", "편입"),
    ("spy", "간자"),
    ("disrupt", "어지럽히다"),
    ("no more business", "더 볼일이 없다"),
    ("return to castle", "성으로 돌아가다"),
    ("pass through", "통과하다"),
    ("enemy troops", "적병"),
    ("reinforcements", "원군"),
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
    "354BFB11CF3F62EFFFDDDA9AF4C66A8876A027D6DF273DBF6496ACEC50DB6C53"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "B59005C800AA260EE1BE2EBDD93423EFD64A5EB5E15C5FABC5D9C105B0D4EF7A"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "6B1FF899F4E93E1ABD892096612941C3EC7CD7A006639915AAB4A79A1A88494C"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "5D4F0400091760CAA6D32D5A270415DD4E2DF176A209A7F6E8D106A640BA583D"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "B1DC267760374713A83183C90B504DAC868D6094EDB2FF28A45C4A9D5F15F46B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "553174B6005645721C0530196AFBA76E6BB3ED95DCADB89778EC3BCD4CFFD292"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D4FEF68CFAF291A2A4DADB2ED35E5D79E1154D12053B2C432931BE560E390352"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "AF8A1FE16C106E5C16663F0AFA81C3287B33C4F28EE72F120EBA2E455F2FB1F3"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B42C858A01F7E2A0AB82F7F8576E46A94F25126AD35AC6515A75B52894F14C73"
)
EXPECTED_BOUNDARY_SHA256 = (
    "E6DD937E93CB378E65C1D9941A75A10DA9DE465550468F06BBD953FD16A04B89"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "F55647E252688771FF03E7C69D7C8EB8DEB1A0927366B3B1B02F1B0343AC7577"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "5216211C3B47BD5CC9DF4007FCA1B2A1FA0EBCE4CF501B88A6CAAF93A1AA4BF9"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BF9EE990D08F72FBAA4A481B717D3CF44E9655A02A1FA222242CAF583D808BAD"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "5572675AE9DA1B4710AA393B9AA02C797B559723DA6A11974512F9AAE28A440E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "E95AF1869538C09E78CD9DB51B99FA4E0EADE2970C7021D73E0FC227B25E0D78"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "842FE92418843DC119EA3D283A8DF2352349500784DB7F68BC867FB2CF3E509C"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "0B9156D3F96000D68DDFC52D8BA52D31BAA1B9CD01F091B8718773AEC514EF3C"
)
EXPECTED_CANDIDATE_SHA256 = (
    "CD899933DA49FDFFDC37FAD91FC4DC07551725A3EDE40191F6C84154B67F3F26"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "5684477F6F82765E4786A494863E53CD08445D3624953E5B5555C6C3A4B0543E"
)
EXPECTED_CHANGED_LITERAL_COUNT = 4
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 42

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; twelve complete records use raw-exact completed "
    "Base donors and two complete records use literal-and-call-masked exact "
    "completed Base donors; all fifty-two slice prefills and fifteen same-"
    "record companions are validated; Base runtime and VM state are never "
    "inherited; complete records, calls, faction, force, castle and count "
    "tokens, protected outer whitespace, source and current gaps, queue and "
    "segment boundaries, two-run reproduction, tamper rejection, reverse "
    "overlays, outside-scope identity, and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1212_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
CORE = BASE.CORE
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl


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
        len(rows) != 125
        or len(visible) != 200
        or visible[0] != "7:2734:0"
        or visible[-1] != "7:2858:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B069 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:2786:0"
        or queue_slice[-1] != "7:2833:0"
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
    if (
        len(prefilled) != 52
        or len(residual) != 15
        or residual != TARGET_COORDINATES
    ):
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
        or len(prefilled) != 52
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


def install_base_globals() -> None:
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
        "HIDDEN_CURRENT_COMPANION_COORDINATES":
        HIDDEN_CURRENT_COMPANION_COORDINATES,
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
        "queue_evidence": queue_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)


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
    install_base_globals()
    return BASE.build_rows()


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
        print(
            json.dumps(
                DISCOVERED_PINS,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
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
        len(rows) != 15
        or len(validated) != 15
        or counts != Counter({"runtime_fragment_pending": 15})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    install_base_globals()
    BASE.propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    raw_exact_count = sum(
        bool(EXPECTED_BASE_RAW_MATCHES[record_id])
        for record_id in TARGET_RECORD_IDS
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B069_S1212",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 52,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                raw_exact_count,
                "masked_complete_base_donor_record_count":
                len(EXACT_BASE_DONOR) - raw_exact_count,
                "semantic_base_context_record_count": 0,
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count":
                combined_changed,
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
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
