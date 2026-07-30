#!/usr/bin/env python3
"""Build source-redacted PK B068 segment 1209 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch062_segment1194.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B068_S1209.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B068_S1208.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B068_S1210.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1209
QUEUE_BATCH_ID = "pk_msggame-B068"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("7:2650:0", "7:2651:0")
TRANSLATIONS = {
    "7:2650:0": "오오……",
    "7:2651:0": "호호오—",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (2650, 2651)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {2650: 2, 2651: 2}
PREFILL_COMPANION_COORDINATES = ("7:2650:1", "7:2651:1")
INVISIBLE_COMPANION_COORDINATES: tuple[str, ...] = ()
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
PRIMARY_BASE_MATCH = {2650: (7, 2584), 2651: (7, 2585)}
EXPECTED_BASE_MATCHES = {
    record_id: (coordinate,)
    for record_id, coordinate in PRIMARY_BASE_MATCH.items()
}
EXPECTED_RAW_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_BASE_DONOR_COORDINATES = {
    2650: ("7:2584:0", "7:2584:1"),
    2651: ("7:2585:0", "7:2585:1"),
}
BOUNDARY_RECORD_KEYS = (
    (7, 2579),
    (7, 2580),
    (7, 2628),
    (7, 2629),
    (7, 2649),
    (7, 2650),
    (7, 2651),
    (7, 2652),
    (7, 2685),
    (7, 2686),
    (7, 2733),
    (7, 2734),
)
SOURCE_CALL_ROOTS = (1,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2650: ((1,), ()),
    2651: ((1,), ()),
}
SPEAKER_STYLE = (
    (2650, "battle_merit_key_position_reflection"),
    (2651, "battle_merit_key_position_acclamation"),
)
TERMINOLOGY_POLICY = (
    ("battle merit", "전공"),
    ("key position", "요지"),
    ("seize", "장악하다"),
    ("suppression", "제압"),
    ("battle", "싸움"),
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
    "B7235540FEE3FD99A6D7C7F39849CE109204ED33FCB422F46EC7D70E5C0DC392"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "90953A486F73674C0F5C41B8FDDB21F213AF9E558FBFC6F0AA27BFAAC76C40D4"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "6407BFAA1E4364967D03CF6ABAEC9196396E50DF72C73D1950880ED8C70FE6C9"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "A8C85F014CD0FB4847DDB0CBFF5A331D96F85FC083C59C32FC4B61BC2BF7B957"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "726366018B9F7AB927AA7A2EF9E7467EADAB200C4C9DDA2379C94C849736E5C8"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E074A1F66AC4BFCA7DFBC9A94F50DADD314104D70A1DF1714008588951963D13"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "AC249CC38FA4F88DA00D4FD62026083DBA327ED469131FE3793978E21B859EFB"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B88EF3D69FEE20E8F0DB1621BA2DE15E9BA7614D6C2CA3948021CA86268EC57E"
)
EXPECTED_BOUNDARY_SHA256 = (
    "A2B2735FAB3821DBC6B1BC994DD19DC3B37C75B049F4FD7CDE4EC1D7E4D96184"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "3CEC681CC185051519B134B27B0B66EB685261A9A39E2936C5A62E6C4381AFB6"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "DFA24C7A2BEE71F3AE2006372A293A3E3F0281F1315D609F8906DDC56CCFAF12"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "25C213D744C7E6747CC7271C17E4E9B4E17A3BCAA3B99D358F9E7D99B9FE1A3E"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "0630670580CEB50B38FF74AD3E5F674C0A27E3388D390C5FEC425F264CF3A4A9"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "311F41C290A564F771768882995B705D922E7A9DB6723E07D56C5D9392C1272C"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "8DD8F3FC474B35D5B0F02A5430BFB2DFE387DE7C12B1A37D01AB8CD00309AF47"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "ED4699A45759D9BD6A6BDE7D53F9A5EC8EFAF0B2F9DFBA56508EEB1917285502"
)
EXPECTED_CANDIDATE_SHA256 = (
    "666B5219E2120379F3C43339B1FFE8B14C0A16E53E68A42A7523CD724D629C44"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "90D0F096B6BDD9CEB7A22FD55D070EAD5F460089A39993CB7441107593289BDE"
)
EXPECTED_CHANGED_LITERAL_COUNT = 2

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; complete PC English, "
    "Simplified Chinese and Traditional Chinese records are empty and "
    "were checked as such; both complete PK source records have one "
    "byte-exact completed Base donor, whose final Korean was reused only "
    "after manual semantic, terminology and speaker-register review; "
    "each residual opening exclamation is assembled with its approved "
    "same-record Base-prefilled three-line companion; the shared record-1 "
    "call graph, punctuation, line counts, complete records and gaps are "
    "guarded; all sixty-five prefills in the sixty-seven-row middle queue "
    "slice are validated and the combined slice is rebuilt in both orders "
    "and reversed byte-exactly; two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are guarded; Base "
    "runtime and VM state are not inherited and both residuals remain "
    "runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1209_parent",
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
        or queue_slice[0] != "7:2629:0"
        or queue_slice[-1] != "7:2685:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != 65
        or len(residual) != 2
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} queue residual drifted")
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
        or len(prefilled) != 65
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
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def configure_parent() -> None:
    names = (
        "SCRIPT",
        "OUTPUT",
        "PREFILL",
        "BASE_PROMOTED",
        "OPTIONAL_NEIGHBORS",
        "STEAM_PK",
        "SEGMENT",
        "QUEUE_BATCH_ID",
        "QUEUE_START",
        "QUEUE_STOP",
        "BLOCK_ID",
        "PK_RECORD_COUNT",
        "TARGET_COORDINATES",
        "TRANSLATIONS",
        "DYNAMIC_COORDINATES",
        "STATIC_COORDINATES",
        "TARGET_RECORD_IDS",
        "DYNAMIC_RECORD_IDS",
        "EXPECTED_ARITY",
        "PREFILL_COMPANION_COORDINATES",
        "INVISIBLE_COMPANION_COORDINATES",
        "FUTURE_COMPANION_COORDINATES",
        "PRIMARY_BASE_MATCH",
        "EXPECTED_BASE_MATCHES",
        "EXPECTED_RAW_BASE_MATCHES",
        "EXPECTED_LITERAL_BASE_MATCHES",
        "EXPECTED_MASKED_BASE_MATCHES",
        "EXPECTED_BASE_DONOR_COORDINATES",
        "BOUNDARY_RECORD_KEYS",
        "SOURCE_CALL_ROOTS",
        "CURRENT_CALL_ROOTS",
        "EXPECTED_CONTROLS_BY_RECORD",
        "SPEAKER_STYLE",
        "TERMINOLOGY_POLICY",
        "EXPECTED_STEAM_PK_SHA256",
        "EXPECTED_PRISTINE_PK_SHA256",
        "EXPECTED_PREFILL_SHA256",
        "EXPECTED_BASE_PROMOTED_SHA256",
        "EXPECTED_QUEUE_UNIVERSE_SHA256",
        "EXPECTED_QUEUE_SLICE_SHA256",
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
        "EXPECTED_TARGET_COORDINATE_SHA256",
        "EXPECTED_SOURCE_TARGET_SHA256",
        "EXPECTED_CURRENT_TARGET_SHA256",
        "EXPECTED_CONTEXT_CORPUS_SHA256",
        "EXPECTED_GAP_CONTRACT_SHA256",
        "EXPECTED_BOUNDARY_SHA256",
        "EXPECTED_RUNTIME_CONTROL_SHA256",
        "EXPECTED_BASE_SEARCH_SHA256",
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256",
        "EXPECTED_CALL_GRAPH_SHA256",
        "EXPECTED_SPEAKER_STYLE_SHA256",
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        "EXPECTED_TRANSLATION_POLICY_SHA256",
        "EXPECTED_CANDIDATE_SHA256",
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256",
        "EXPECTED_CHANGED_LITERAL_COUNT",
        "DISCOVERED_PINS",
        "BASIS",
    )
    for name in names:
        setattr(PARENT, name, globals()[name])
    PARENT.queue_evidence = queue_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate


def build_rows() -> tuple[Any, ...]:
    configure_parent()
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
        len(rows) != 2
        or len(validated) != 2
        or counts != Counter({"runtime_fragment_pending": 2})
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
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        PARENT.PARENT.PARENT.engine_builder().assert_tamper_rejection(
            prepared,
            rows,
            candidate,
        )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B068_S1209",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 65,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                len(EXPECTED_BASE_MATCHES),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "base_vm_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduced": True,
                "outside_scope_identity_guarded": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
