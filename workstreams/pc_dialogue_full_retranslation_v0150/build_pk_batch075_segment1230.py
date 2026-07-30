#!/usr/bin/env python3
"""Build source-redacted PK B075 segment 1230 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch072_segment1220.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B075_S1230.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B075_S1231.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1230
QUEUE_BATCH_ID = "pk_msggame-B075"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_ROW_COUNT = 158
QUEUE_VISIBLE_COUNT = 200
SLICE_VISIBLE_COUNT = 67
SLICE_PREFILL_COUNT = 55
PRIOR_START = 0
PRIOR_STOP = 67
PRIOR_PREFILL_COUNT = 67
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    f"8:{record_id}:0" for record_id in range(842, 854)
)
TRANSLATIONS = {
    coordinate: "「" for coordinate in TARGET_COORDINATES
}
TARGET_RECORD_IDS = tuple(range(842, 854))
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {record_id: 2 for record_id in TARGET_RECORD_IDS}
PREFILL_COMPANION_COORDINATES = tuple(
    f"8:{record_id}:1" for record_id in TARGET_RECORD_IDS
)
PREFILL_COMPANION_DONOR = {
    f"8:{record_id}:1": f"8:{record_id - 12}:1"
    for record_id in TARGET_RECORD_IDS
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        f"8:{record_id - 12}:0",
        f"8:{record_id - 12}:1",
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ((8, record_id - 12),)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (
        742, 743, 744, 805, 806, 807, 808,
        *range(829, 855),
        860, 861, 862, 863, 899, 900,
    )
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ("02BE32",))
    for record_id in TARGET_RECORD_IDS
}
SPEAKER_STYLE = (
    (842, "formal_retainer_maximum_report"),
    (843, "brash_young_maximum_boast"),
    (844, "warrior_formal_maximum_report"),
    (845, "authoritative_warrior_maximum_report"),
    (846, "polite_maximum_development_report"),
    (847, "archaic_samurai_maximum_report"),
    (848, "elder_maximum_observation"),
    (849, "polite_maximum_achievement_exclamation"),
    (850, "archaic_samurai_achievement_exclamation"),
    (851, "polite_maximum_arrival_exclamation"),
    (852, "blunt_lordly_maximum_achievement"),
    (853, "formal_polite_maximum_achievement"),
)
TERMINOLOGY_POLICY = (
    ("opening project-name quote", "「"),
    ("maximum level", "최대 수준"),
    ("reach maximum", "최대 수준에 이르다"),
    ("develop to maximum", "최대 수준까지 발전하다"),
    ("raise to maximum", "최대 수준까지 끌어올리다"),
    ("formal humble report", "사옵니다"),
    ("archaic warrior register", "하였소이다"),
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
    "C1C3D00184B03F64E4A6F7351F4759A70A585AB8089A622C6180C93A883C6E21"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "7E6F88F18DC5CBF6A4DDFA1F931B20D2BA74A4F7FC0A2008CE23311A7BD1D844"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "20FBEBADE51A38EA2F040163E656F63F0FD46C61BA7F72E301DD8521554B6C39"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "4A69CD3304B809FAE52410E6D9CAE6CB73947A7D9E0A3F76DE5C55EDA0ECA56E"
)
EXPECTED_PRIOR_PREFILL_COORDINATE_SHA256 = (
    "CE9063D505ADADB5B9094A961280A2E8162DA259F15DCFA26879632A047BDA2E"
)
EXPECTED_PRIOR_PREFILL_CONTEXT_SHA256 = (
    "0B33D36C19014A63FDCE5980191542226FF7250979DA2C107F4727CA7B282E57"
)
EXPECTED_PRIOR_PREFILL_BOUNDARY_SHA256 = (
    "7A3F93F54E02CD6758E45DCDAF3EAE9B129C454647D6F93D7A68A078774C1309"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "1AC0B7E500B5DF9B34E1F270389AD8D4F1A78FC2CE2D5124837BB4B4CEDFDFDD"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "E552CB61A1A88035FF999C4F26EEE9161E48F16DEB55B639602A901D68786626"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E552CB61A1A88035FF999C4F26EEE9161E48F16DEB55B639602A901D68786626"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "01D87EE3D7792A561ED0B36BF9C75AA1FB9F38630FBB572A9020F92258E8A57B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "5CD6DD89C6CD0E2F51764F169C608E13DD47D8D0472ABDD4AFAF6E44231B5756"
)
EXPECTED_BOUNDARY_SHA256 = (
    "A283585E864B1838408091DC2A1BFD52F4CEDFD5AFEEB858902278AB2195C382"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "F228E7D774AB818476A4CD0EC300F27F2B3A1BF6D2F6AB0A6CAFD04C1303CB80"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "059C20E20CAC261FC68E80A8906FCD73F04BC1FDE69AEAF52D358B7F7E43DE12"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "7331A1BB490BBE44BEDFBCE3C3AAF8F8FE49DE9FD03F9DB323DA791722199EE4"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "66D0F822662B02278B6308F5BBA11763D07603AC7375BE44D454EF252D74D546"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "25386BD0D9380E5AAEA5E1289ACCA845895B036AB75FB75E52B86B2C6188D9F4"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "E552CB61A1A88035FF999C4F26EEE9161E48F16DEB55B639602A901D68786626"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "4E826D80757CD19BBE61F692A75B06848F3AE86B327A3F1E9B6E6EDE732E3AA0"
)
EXPECTED_CHANGED_LITERAL_COUNT = 0
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 47

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK Japanese is authoritative and complete PK English, "
    "Simplified Chinese and Traditional Chinese context was manually "
    "reviewed, including explicitly empty localized records; all twelve "
    "maximum-development records use completed Base wording only as "
    "manually reviewed semantic context despite observed raw matches, "
    "without inheriting completed Base runtime or VM state; the twelve "
    "opening quote residuals and twelve same-record exact-prefill companions "
    "were reviewed as complete assemblies across formal, brash, warrior, "
    "elder and polite registers; project-name quote and maximum development "
    "terminology, inline project token, punctuation, newlines, protected "
    "outer whitespace and gaps are guarded; the preceding zero-residual "
    "slice has all sixty-seven prefills, their full decision context and "
    "both sides of its queue boundary separately pinned; all fifty-five "
    "current-slice prefills, optional boundary output, two-run reproduction, "
    "tamper rejection, reverse overlays, outside-scope identity and Steam "
    "read-only state are guarded; all residuals remain PK runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_b075_s1230_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
ENGINE = BASE.ENGINE
CORE = BASE.CORE
sha256_bytes = BASE.sha256_bytes
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl


def prefill_context_row(
    coordinate: str,
    prefill_rows: dict[str, dict[str, Any]],
) -> tuple[Any, ...]:
    row = prefill_rows[coordinate]
    return (
        coordinate,
        str(row["translation"]),
        str(row["source_record_raw_sha256"]),
        str(row["current_ko_utf16le_sha256"]),
        str(row["semantic_review"]),
        str(row["runtime_review"]),
        str(row["layout_review"]),
        str(row["base_exact_reuse_prefill"]["base_coordinate"]),
        str(
            row["base_exact_reuse_prefill"]["translation_utf16le_sha256"]
        ),
        bool(
            row["base_exact_reuse_prefill"][
                "runtime_promotion_authorized"
            ]
        ),
    )


def prior_prefill_boundary_evidence(
    prepared: Any,
    visible: tuple[str, ...],
) -> tuple[Any, ...]:
    source = ENGINE.archive_records(
        prepared.resources["pk_msggame"].pristine_archive
    )
    current = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    for ordinal in (0, 1, 65, 66, 67, 68):
        coordinate = visible[ordinal]
        key = coordinate_key(coordinate)[:2]
        evidence.append(
            (
                ordinal,
                coordinate,
                key,
                sha256_bytes(source[key].data),
                sha256_bytes(current[key].data),
                literal_texts(source, key),
                literal_texts(current, key),
                tuple(value.hex().upper() for value in gap_bytes(source[key])),
                tuple(value.hex().upper() for value in gap_bytes(current[key])),
                CORE.runtime_controls(source[key]),
                CORE.runtime_controls(current[key]),
            )
        )
    return tuple(evidence)


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
        len(rows) != QUEUE_ROW_COUNT
        or len(visible) != QUEUE_VISIBLE_COUNT
        or visible[0] != "8:743:0"
        or visible[-1] != "8:900:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B075 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != SLICE_VISIBLE_COUNT
        or queue_slice[0] != "8:807:0"
        or queue_slice[-1] != "8:861:0"
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
        len(prefilled) != SLICE_PREFILL_COUNT
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")

    prior_slice = visible[PRIOR_START:PRIOR_STOP]
    if (
        len(prior_slice) != PRIOR_PREFILL_COUNT
        or prior_slice[0] != "8:743:0"
        or prior_slice[-1] != "8:806:0"
        or visible[PRIOR_STOP] != "8:807:0"
        or any(coordinate not in prefill_rows for coordinate in prior_slice)
    ):
        raise RuntimeError(f"segment {SEGMENT} prior prefill slice drifted")
    prior_context = tuple(
        prefill_context_row(coordinate, prefill_rows)
        for coordinate in prior_slice
    )
    if any(
        row[4] != "approved"
        or row[5] not in {"pending", "not_required"}
        or row[6] != "unchanged_from_current"
        or row[9] is not False
        for row in prior_context
    ):
        raise RuntimeError(f"segment {SEGMENT} prior prefill state drifted")
    CORE.guarded_digest(
        "prior full prefill coordinate",
        prior_slice,
        EXPECTED_PRIOR_PREFILL_COORDINATE_SHA256,
    )
    CORE.guarded_digest(
        "prior full prefill context",
        prior_context,
        EXPECTED_PRIOR_PREFILL_CONTEXT_SHA256,
    )
    CORE.guarded_digest(
        "prior full prefill boundary",
        prior_prefill_boundary_evidence(prepared, visible),
        EXPECTED_PRIOR_PREFILL_BOUNDARY_SHA256,
    )

    prefill_context = tuple(
        prefill_context_row(coordinate, prefill_rows)
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
        len(replacements) != SLICE_VISIBLE_COUNT
        or len(prefilled) != SLICE_PREFILL_COUNT
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
            f"segment {SEGMENT} combined candidate drifted: {candidate_sha256}"
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


OVERRIDES = (
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
    "TARGET_RECORD_IDS",
    "STATIC_RECORD_IDS",
    "DYNAMIC_RECORD_IDS",
    "STATIC_COORDINATES",
    "DYNAMIC_COORDINATES",
    "EXPECTED_ARITY",
    "PREFILL_COMPANION_COORDINATES",
    "PREFILL_COMPANION_DONOR",
    "EXACT_BASE_DONOR",
    "SEMANTIC_BASE_CONTEXT",
    "EXPECTED_BASE_RAW_MATCHES",
    "EXPECTED_BASE_LITERAL_MATCHES",
    "EXPECTED_BASE_MASKED_MATCHES",
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
    "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT",
    "DISCOVERED_PINS",
    "BASIS",
    "queue_evidence",
    "build_combined_slice_candidate",
)


def install_base_globals() -> None:
    for name in OVERRIDES:
        setattr(BASE, name, globals()[name])


def propagate_for_tamper() -> None:
    install_base_globals()
    BASE.propagate_base_globals()


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    return BASE.build_rows()


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
        len(rows) != len(TARGET_COORDINATES)
        or len(validated) != len(TARGET_COORDINATES)
        or counts != Counter({
            "runtime_fragment_pending": len(TARGET_COORDINATES)
        })
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
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    propagate_for_tamper()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B075_S1230",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": SLICE_VISIBLE_COUNT,
        "exact_reuse_prefill_count": SLICE_PREFILL_COUNT,
        "prior_zero_residual_prefill_count": PRIOR_PREFILL_COUNT,
        "prior_zero_residual_prefill_guarded": True,
        "prior_prefill_coordinates_separately_pinned": True,
        "prior_prefill_context_separately_pinned": True,
        "prior_prefill_boundary_separately_pinned": True,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "automatic_complete_base_donor_record_count": 0,
        "observed_raw_base_match_record_count":
        sum(bool(EXPECTED_BASE_RAW_MATCHES[x]) for x in TARGET_RECORD_IDS),
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
        "base_vm_state_inherited": False,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "discovered_pins": DISCOVERED_PINS,
        "steam_write_performed": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
