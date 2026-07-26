#!/usr/bin/env python3
"""Build source-redacted PK B080 segment 1245 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch080_segment1246.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B080_S1245.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B080_S1244.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B080_S1246.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1245
QUEUE_BATCH_ID = "pk_msggame-B080"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_SLICE_FIRST = "9:543:0"
QUEUE_SLICE_LAST = "9:607:0"
QUEUE_SLICE_VISIBLE_COUNT = 67
QUEUE_SLICE_PREFILL_COUNT = 63
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:552:0",
    "9:552:1",
    "9:554:0",
    "9:571:0",
)
TRANSLATIONS = {
    "9:552:0": "!\n",
    "9:552:1": "이(가) 상대해 주마!",
    "9:554:0": "상대할 자는―",
    "9:571:0": "쏴라!",
}
TARGET_RECORD_IDS = (552, 554, 571)
STATIC_RECORD_IDS = (571,)
DYNAMIC_RECORD_IDS = (552, 554)
STATIC_COORDINATES = {"9:571:0"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {552: 2, 554: 2, 571: 1}
PREFILL_COMPANION_COORDINATES = ("9:554:1",)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    552: (9, 498),
    554: (9, 500),
    571: (9, 517),
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    552: ("9:498:0", "9:498:1"),
    554: ("9:500:0", "9:500:1"),
    571: ("9:517:0",),
}
PREFILL_COMPANION_DONOR = {"9:554:1": "9:500:1"}
EXPECTED_BASE_RAW_MATCHES = {
    552: ((9, 498),),
    554: ((9, 500),),
    571: ((9, 517),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = (
    (9, 497), (9, 498), (9, 499), (9, 500), (9, 501),
    (9, 516), (9, 517), (9, 518), (9, 542), (9, 543),
    (9, 551), (9, 552), (9, 553), (9, 554), (9, 555),
    (9, 570), (9, 571), (9, 572), (9, 607), (9, 608),
)
SOURCE_CALL_ROOTS = (1, 4, 17)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    552: ((17, 1), ()),
    554: ((4,), ()),
    571: ((), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (552, "bold_single_combat_challenge"),
    (554, "lordly_single_combat_challenge"),
    (571, "battlefield_fire_command"),
)
TERMINOLOGY_POLICY = (
    ("opponent", "상대"),
    ("face in combat", "상대해 주다"),
    ("fire command", "쏴라"),
    ("ASCII exclamation", "!"),
    ("project em dash", "―"),
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
    "E797F5045EF74D1A9675A9AC5541647B60BC4D6A6E9D15478D77B4EB17727800"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E125BB7550DAC7EDA1D6500EB75F16ED004A0711F948EAB574AE8ECDF6D33C52"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5D6383AF4E9E9E87C51AEE09FC6871EFFC3E6157E91D4EE34250FC9B3C96C3C2"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "40AEA5FD472AC06BD38B6C7C25D7DD19767B11D13C1E538DC3E976EB506E6408"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "AA109B4C46DBA4BC9A913DE31C1CC2B1CDD45BF371E29039196A82B6CD23B4F7"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "8F489B3CE9306D67B3569564C604089004626D8F1535C48701214EA1EE9CDBB3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "202B439F238372A65788DD63E9FF025CA23BBF684FBD47EAEA313497CE432FF4"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "F9F8B7AB0AB216707519CE4BA6AD504D42321E7D7D60D47E39661FAEEC9E1026"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "A9FB7E4055D55086F8A559EF32933D94140BD72CC736CEC9D1A5268FD10C4991"
)
EXPECTED_BOUNDARY_SHA256 = (
    "83D8627B52352AA5A478A098BBB9EC83757A2D3FD8D285800655884F2643FF92"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "19BBB566BD8E9D6B30CC2B624C65ABD3D1FBD5BB32F248339F4A61ADD433BF69"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "C5DC85523D88917914869308EDDDDC2AD0B56FAB2A1CEEA0D6E85217F9969F05"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "EF75731D1AA9B6FC215D073D157262A0C38AF00A36E50023DA652FDF37C1D284"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "F932D76575D950C4206CBD2C2DA1F9A7CCC4E218E56E0CEEF8209EDFD4DF88CF"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "5570BC937A9051FA8EFFDEBFC713FD2A1F161C6EF0BC6E36CCE8A72FAA70D135"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "DFCD7FBF714F381FE90E385181AE3F5E6BF89E85C068A53A9AD5DB4CA6A15B9A"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "DE0884A8206E2B96A501FA7BDD1646269EECBBC42F9B67E8A6C9D36DAADD6314"
)
EXPECTED_CANDIDATE_SHA256 = (
    "61585EEE92BE379061E5E01016CF3AE18DEA2BB3E01A1C1733EA947BBD374129"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "EF146E2B438C7E1F91E44326E4CBE4A2077340DE2CBD8F2753861C1E3C2A70AE"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 55

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; PC English, Simplified "
    "Chinese and Traditional Chinese emptiness or populated auxiliaries "
    "were reviewed; completed Base records were used only as semantic, "
    "terminology and speaker-register context without inheriting Base "
    "runtime or VM state; two dynamic single-combat challenges preserve "
    "bold and lordly voices, dynamic speaker calls, ASCII punctuation and "
    "the project em dash, while the static battlefield fire command is "
    "verified as already correct and runtime-not-required; four residual "
    "translations plus one approved prefill companion assemble all three "
    "complete records; all sixty-three prefills in the sixty-seven-row "
    "middle slice, source/current gaps, controls, protected whitespace and "
    "complete assemblies are guarded; both overlay orders, byte-exact "
    "reversal, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are verified; discovered pins are "
    "immutable and Base runtime state is never inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1245_parent",
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
        len(rows) != 186
        or len(visible) != 200
        or visible[0] != "9:487:0"
        or visible[-1] != "9:672:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B080 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != QUEUE_SLICE_VISIBLE_COUNT
        or queue_slice[0] != QUEUE_SLICE_FIRST
        or queue_slice[-1] != QUEUE_SLICE_LAST
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
        len(prefilled) != QUEUE_SLICE_PREFILL_COUNT
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
        len(replacements) != QUEUE_SLICE_VISIBLE_COUNT
        or len(prefilled) != QUEUE_SLICE_PREFILL_COUNT
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
        "SCRIPT": SCRIPT, "OUTPUT": OUTPUT, "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS, "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT, "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START, "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID, "PK_RECORD_COUNT": PK_RECORD_COUNT,
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
        "SEMANTIC_BASE_RECORD": SEMANTIC_BASE_RECORD,
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
        "EXPECTED_SOURCE_CONTROLS_BY_RECORD":
        EXPECTED_SOURCE_CONTROLS_BY_RECORD,
        "EXPECTED_CURRENT_CONTROLS_BY_RECORD":
        EXPECTED_CURRENT_CONTROLS_BY_RECORD,
        "SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS":
        SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
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
        setattr(PARENT, name, value)


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, str, int, tuple[str, ...],
]:
    patch_parent_globals()
    return PARENT.build_rows()


def propagate_parent_globals() -> None:
    patch_parent_globals()
    PARENT.propagate_parent_globals()


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared, rows, candidate, candidate_sha256, changed,
        combined_sha256, combined_changed, optional_present,
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
            DISCOVERED_PINS, sort_keys=True, separators=(",", ":"),
        ))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 4
        or len(validated) != 4
        or counts != Counter({"runtime_fragment_pending": 4})
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    propagate_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    if DISCOVERED_PINS:
        raise RuntimeError(f"segment {SEGMENT} pins remained mutable")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B080_S1245",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 63,
        "residual_count": len(rows),
        "reviewed_complete_record_count": 3,
        "same_record_prefill_companion_count": 1,
        "raw_exact_complete_base_donor_record_count": 0,
        "masked_complete_base_donor_record_count": 0,
        "semantic_base_context_record_count": 3,
        "source_call_root_count": 3,
        "current_call_root_count": 3,
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
        "source_current_gap_contract_guarded": True,
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
        "discovered_pins_empty": True,
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
