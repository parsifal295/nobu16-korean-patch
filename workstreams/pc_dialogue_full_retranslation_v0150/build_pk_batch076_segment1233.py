#!/usr/bin/env python3
"""Build source-redacted PK B076 segment 1233 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch076_segment1232.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B076_S1233.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B076_S1232.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B076_S1234.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1233
QUEUE_BATCH_ID = "pk_msggame-B076"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:938:2",
    "8:939:0",
    "8:940:0",
    "8:940:1",
    "8:940:2",
    "8:941:0",
    "8:941:1",
    "8:941:2",
    "8:942:0",
    "8:942:1",
    "8:942:2",
    "8:948:0",
    "8:948:1",
    "8:949:0",
    "8:951:0",
    "8:952:0",
    "8:953:0",
    "8:954:0",
    "8:955:0",
    "8:956:0",
    "8:957:0",
    "8:958:0",
    "8:959:0",
    "8:960:0",
    "8:961:0",
    "8:962:0",
    "8:963:0",
)
TRANSLATIONS = {
    "8:938:2": "」을(를) 시작",
    "8:939:0": "이(가) 「",
    "8:940:0": "이(가) 「",
    "8:940:1": "」에서 「",
    "8:940:2": "」을(를) 시작",
    "8:941:0": "이(가) 「",
    "8:941:1": "」의 성하로 「",
    "8:941:2": "」을(를) 시작",
    "8:942:0": "이(가) 「",
    "8:942:1": "」에서 「",
    "8:942:2": "」을(를) 시작",
    "8:948:0": "에 「",
    "8:948:1": "」을(를) 건설하",
    "8:949:0": "의 건설지를 「",
    **{
        f"8:{record_id}:0": "에 「"
        for record_id in range(951, 963)
    },
    "8:963:0": "에서 「",
}
TARGET_RECORD_IDS = (938, 939, 940, 941, 942, 948, 949, *range(951, 964))
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    938: 3,
    939: 2,
    940: 3,
    941: 3,
    942: 3,
    948: 3,
    949: 3,
    **{record_id: 3 for record_id in range(951, 963)},
    963: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "8:939:1",
    "8:948:2",
    "8:949:1",
    "8:949:2",
    *tuple(
        coordinate
        for record_id in range(951, 963)
        for coordinate in (
            f"8:{record_id}:1",
            f"8:{record_id}:2",
        )
    ),
    "8:963:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES = (
    "8:938:0",
    "8:938:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    938: (8, 926),
    939: (8, 927),
    940: (8, 928),
    941: (8, 929),
    942: (8, 930),
    948: (8, 936),
    949: (8, 937),
    **{record_id: (8, record_id - 12) for record_id in range(951, 964)},
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
CONSTRUCTION_MATCHES = tuple((8, record_id) for record_id in range(939, 951))
EXPECTED_BASE_RAW_MATCHES = {
    938: (),
    939: ((8, 927),),
    940: ((8, 928),),
    941: ((8, 929),),
    942: ((8, 925), (8, 930)),
    948: (),
    949: (),
    **{record_id: () for record_id in range(951, 963)},
    963: ((8, 951),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    938: ((8, 925), (8, 926), (8, 928), (8, 930)),
    939: ((8, 927),),
    940: ((8, 925), (8, 926), (8, 928), (8, 930)),
    941: ((8, 929),),
    942: ((8, 925), (8, 926), (8, 928), (8, 930)),
    948: ((8, 936),),
    949: ((8, 937),),
    **{
        record_id: CONSTRUCTION_MATCHES
        for record_id in range(951, 963)
    },
    963: ((8, 951),),
}
EXPECTED_BASE_MASKED_MATCHES = {
    938: ((8, 926),),
    939: ((8, 927),),
    940: ((8, 928),),
    941: ((8, 929),),
    942: ((8, 925), (8, 930)),
    948: ((8, 936),),
    949: ((8, 937),),
    **{
        record_id: CONSTRUCTION_MATCHES
        for record_id in range(951, 963)
    },
    963: ((8, 951),),
}
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id) for record_id in range(925, 968)
)
SOURCE_CALL_ROOTS = (8, 466, 472, 424, 1162, 1066)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    938: ((80943,), ("029632", "023C")),
    939: ((), ("024633", "029632")),
    940: ((), ("024633", "029633", "023C")),
    941: ((), ("024633", "026432", "023C")),
    942: ((), ("024633", "029632", "023C")),
    948: ((466,), ("029632", "023C")),
    949: ((472, 424), ("023C", "029632")),
    **{
        record_id: ((1162, 1066), ("029632", "023C"))
        for record_id in range(951, 963)
    },
    963: ((), ("029632", "023C")),
}
SPEAKER_STYLE = tuple(
    (record_id, "construction_and_work_ui")
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("castle town", "성하"),
    ("construction site", "건설지"),
    ("construction proclamation", "건설하라는 포고"),
    ("start", "시작"),
    ("begin immediately", "즉시 착수"),
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
    "57B3BAF28C7DF0DA3799CF1A2FD0DA674BC07C5AA8BB6DB1A809B8B71F9931D2"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "AEE03B208DF7C605D73C381B6FFA5E6A259126FEF9257CF5F332D9C912D3F265"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "1F46D8A9337119B40202C709F85B7D50E92D12FF4F86D94C25F61F69AA660581"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "FDB4194C2D9AD120D98126690BE944FB7C28BBDA27037B5C7BFBCB478C6371DF"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "54EBF0446B4B5DC3086CAD150D7CD89EF06B594FDF0B1DE49BF828CC964D3A1E"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "2ABB5A546A4A88D5A435A2F3106A4F6878BA436ECB44A0CE5AA480C1D3E2A6C8"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "2E5069B6668E518A339D4CB61CBC57BBEA26ADEA7678914A6884EE6915A42B67"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "2D6A941B2DA8E250A440BAF54617D686376FF924005831AFBB7F74934502993C"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "81F3287A21FE3ED1D18527A94D5ABE9227ADCADFECFAF1059B5D666279FB620D"
)
EXPECTED_BOUNDARY_SHA256 = (
    "81CE388EBD3F52EEB043AE03F345B66CDF1931AD977AF4C45D27755FA458BAF6"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "C67FBB3337DE509C17797E7EA81654A6E33EC5FCC576DFA63F9EF1E7FB8042C4"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "A616E65C7127F79A0292C0B872D1C2C430C7C0DF13E099F3B25648EF5D472D1D"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "F0F5A8A2FE6338B18547E0FA0CF16307E3120B3A7157A1159EC6B30BBB281F95"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "210A85035997B37C1DC407E6A0E0308FD9F71C12E3485674347E1718B80B876B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "524466711B5A299BB8C55C1D1E0528B77E1A3F0EB9F62665086C27356109AE72"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "B2BA5C73E7034713091D32D41BDD15391488865DDBFB8C41A7AC8EA2290CCC2C"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "770E9DEEF6DC1F7E7D8CED42F1ABDFA04BEE97935F9D28F98295EF6FBB9C06C5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "845E2C5AED628963C12B327BF7CAEC1DDAA805955780FFCD7664FDCBACCAFF25"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "CA42EFD3CC28409099BF48FB76AD9167CAB1DFCA91B12960FFABB57541996644"
)
EXPECTED_CHANGED_LITERAL_COUNT = 27
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 60

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and all twenty complete records use "
    "raw- or call-masked exact completed Base donors; all twenty-nine "
    "same-record prefill companions and two cross-segment exact donor "
    "companions are validated; Base runtime and VM state are never inherited; "
    "work-start and construction-proclamation terminology, dynamic person, "
    "place and action tokens, calls, gaps, protected whitespace, mutual "
    "three-way segment boundaries, two-run reproduction, tamper rejection, "
    "reverse overlays, outside-scope identity and Steam read-only state are "
    "guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1233_base",
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
        len(rows) != 94
        or len(visible) != 200
        or visible[0] != "8:901:0"
        or visible[-1] != "8:994:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B076 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "8:938:2"
        or queue_slice[-1] != "8:966:0"
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
        len(prefilled) != 40
        or len(residual) != 27
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
        or len(prefilled) != 40
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


OVERRIDES = BASE.OVERRIDES


def install_base_globals() -> None:
    for name in OVERRIDES:
        setattr(BASE, name, globals()[name])


def propagate_for_tamper() -> None:
    install_base_globals()
    BASE.propagate_for_tamper()


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
        print(json.dumps(DISCOVERED_PINS, sort_keys=True, separators=(",", ":")))
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
        len(rows) != 27
        or len(validated) != 27
        or counts != Counter({"runtime_fragment_pending": 27})
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
    propagate_for_tamper()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    if DISCOVERED_PINS:
        raise RuntimeError(f"segment {SEGMENT} pins remained mutable")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B076_S1233",
                "approved": len(rows),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 40,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "cross_segment_donor_companion_count":
                len(CROSS_SEGMENT_DONOR_COMPANION_COORDINATES),
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
                "cross_segment_complete_record_guarded": True,
                "three_way_segment_boundaries_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "discovered_pins_empty": True,
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
