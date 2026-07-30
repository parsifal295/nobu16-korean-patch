#!/usr/bin/env python3
"""Build source-redacted PK B064 segment 1201 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch056_segment1179.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B064_S1201.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B064_S1199.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B064_S1200.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1201
QUEUE_BATCH_ID = "pk_msggame-B064"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2078:1",
    "7:2079:1",
    "7:2080:0",
    "7:2084:1",
    "7:2087:1",
    "7:2088:0",
    "7:2089:0",
    "7:2093:0",
    "7:2095:0",
    "7:2095:1",
)
TRANSLATIONS = {
    "7:2078:1": "(으)로 돌아가라",
    "7:2079:1": "을(를) 방어하러 돌아간다",
    "7:2080:0": "걱정되는 곳은—",
    "7:2084:1": "(으)로 돌아간다",
    "7:2087:1": "을(를) 방어하러 돌아간다",
    "7:2088:0": "서둘러—",
    "7:2089:0": "이런—",
    "7:2093:0": "어머—",
    "7:2095:0": "군량이 부족하군……\n",
    "7:2095:1": "(으)로 돌아간다",
}
TARGET_RECORD_IDS = (
    2078,
    2079,
    2080,
    2084,
    2087,
    2088,
    2089,
    2093,
    2095,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {record_id: 2 for record_id in TARGET_RECORD_IDS}
PREFILL_COMPANION_COORDINATES = (
    "7:2078:0",
    "7:2079:0",
    "7:2080:1",
    "7:2084:0",
    "7:2087:0",
    "7:2088:1",
    "7:2089:1",
    "7:2093:1",
)
EXACT_BASE_DONOR = {
    2078: (7, 2037),
    2079: (7, 2038),
    2080: (7, 2039),
    2084: (7, 2043),
    2087: (7, 2046),
    2088: (7, 2047),
    2089: (7, 2048),
    2093: (7, 2052),
}
SEMANTIC_BASE_CONTEXT = {
    2095: (
        "14:101:1",
        "7:2043:1",
    ),
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
        2071,
        2077,
        2078,
        2079,
        2080,
        2081,
        2083,
        2084,
        2085,
        2086,
        2087,
        2088,
        2089,
        2090,
        2092,
        2093,
        2094,
        2095,
        2096,
        2116,
        2117,
    )
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ("026432",))
    for record_id in TARGET_RECORD_IDS
}
SPEAKER_STYLE = (
    (2078, "measured_partial_victory_return_command"),
    (2079, "enemy_repulsed_defense_return"),
    (2080, "watchful_defense_assessment"),
    (2084, "pursuit_overextension_return"),
    (2087, "deep_pursuit_defense_return"),
    (2088, "urgent_return_after_possible_lure"),
    (2089, "terse_realization_and_return"),
    (2093, "feminine_realization_and_return"),
    (2095, "supply_shortage_return_order"),
)
TERMINOLOGY_POLICY = (
    ("six-tenths victory", "6할의 승리"),
    ("defend", "방어하다"),
    ("return", "돌아가다"),
    ("pursuit", "추격"),
    ("lure", "유인"),
    ("provisions", "군량"),
    ("insufficient supplies", "군량이 부족하다"),
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
    "EB015D291C1941BDAC41D20B4C93FFA16939002A392DF0361BD8D8F43AAC2B66"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "6E5C24855DEFC1915E0BDB48D5E176B1D56B3B12FAF186519EB3E4017B8DA5CD"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "109C25990EF032D03484D70E0A0BA2A201200F2D1C205615946443F632555E7A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "5662D9A850A43BA0034F35CD3A45D5713CC9B08EA946D8437A73EE1159A6F33F"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "168396FF5757CFFC4B9D0CF0EDBF63398F69581B5C32E32E8B15140B5D849EAC"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "88160A2FB8C09F8794530D900A31F3A371942707F89A10E03956233EF6600079"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "551201C95B3F8C970CE46BED4CBF4D3579766A7BD524FCE512A0406F4B18F7B3"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "1750A3DA302883D99FE7B6AB103FD3D1F667A7CC2E4749ABE3B1820A089BE117"
)
EXPECTED_BOUNDARY_SHA256 = (
    "FC4DA8F8106C51203A5F1EDF1FD0AE4F2FD63F5B0D832E4FDC939803C1D2323D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "468A7FD1D2CC86322B00CCFB9E2DB0FD1022137562EFD2EFEF5BF31267D6BA80"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "1FAEC67591407DFFB81C790D2A6212142D494300D1C5CF0DB8E722B298800015"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "625EEBB4F9AA240F2B6403A352D53FE94A5D5695A6250DE6885813B9F35CBAB4"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "F11FBD31F3F62ED9D020D5DD201DE060E087D4E326ABB4F3FBD09DCD8353B38C"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "273F06C35E917A2275045E2C88865C60497ACD3F7751ED074C7E9C85ED2E8501"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "BAB5C7CD0CEEF44BAFE0CA5A019184D2948D1EB990EE4BF411430BA0FF1BAD22"
)
EXPECTED_CANDIDATE_SHA256 = (
    "972697E926FAD610FA7C2CDD4AFEA4D1E1E198E3EA409A585AF491A42F801000"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "F30415DF61E01B548673FB75EA501FE223A0006A859B0AC0C88EAD08A254B889"
)
EXPECTED_CHANGED_LITERAL_COUNT = 10
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 54

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; eight complete records use raw-exact completed "
    "Base donors and the PK-only supply-shortage record uses completed Base "
    "provisions and return wording as manually reviewed semantic context; "
    "all fifty-six slice prefills and eight same-record companions are "
    "validated; Base runtime and VM state are never inherited; complete "
    "records, destination tokens, protected outer whitespace, source and "
    "current gaps, queue and segment boundaries, two-run reproduction, "
    "tamper rejection, reverse overlays, outside-scope identity, and Steam "
    "read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1201_base",
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
        len(rows) != 128
        or len(visible) != 200
        or visible[0] != "7:1990:0"
        or visible[-1] != "7:2117:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B064 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "7:2071:0"
        or queue_slice[-1] != "7:2117:0"
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
    if len(prefilled) != 56 or residual != TARGET_COORDINATES:
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
        len(replacements) != 66
        or len(prefilled) != 56
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


def patch_base_globals() -> None:
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
    patch_base_globals()
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
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    patch_base_globals()
    BASE.patch_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B064_S1201",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 56,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
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
