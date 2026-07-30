#!/usr/bin/env python3
"""Build source-redacted PK B070 segment 1215 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch069_segment1213.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B070_S1215.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B070_S1214.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B070_S1216.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1215
QUEUE_BATCH_ID = "pk_msggame-B070"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("8:181:0",)
TRANSLATIONS = {"8:181:0": "은(는) 「"}
TARGET_RECORD_IDS = (181,)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {181: 2}
PREFILL_COMPANION_COORDINATES = ("8:181:1",)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {181: (8, 175)}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {181: ((8, 175),)}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = (
    (8, 124),
    (8, 125),
    (8, 174),
    (8, 175),
    (8, 176),
    (8, 180),
    (8, 181),
    (8, 182),
    (8, 189),
    (8, 190),
)
SOURCE_CALL_ROOTS = (8, 1)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {181: ((8, 1), ())}
SPEAKER_STYLE = ((181, "officer_evaluation_reflection"),)
TERMINOLOGY_POLICY = (
    ("evaluate highly", "높이 평가하다"),
    ("quoted dynamic title", "「…」"),
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
    "AEA7C7F12C56EE973DF4761FE00037B3CED06F9B2FCA0E0ABBB35D4AF1A9190A"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E84292ACA59FF36B1B1808155606984BAC9BBCFC49C1081CFD4946ED8FE4B63F"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "002CD200609EA5D42D7D153B4ABADE1DED7459FFB9AD2ED634DDF9C668F993A9"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "5E1C93C37ED70C63003C98CA42314F901850E783EDA451B20AA01FF58C62DA89"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "770876AB024486D98A21BA382682E2C66A64274D29C4AA150A3958BAB0E6518F"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "BCD822FF6D9D1FF5BF121709807A663CF9F807E6827D0E9147A20110F7926068"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "62BAB4883FB4E08D4B19B5360C141AB04DA0038475EED9CBA0AB77B4EAAB1D83"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "C7F5DE16C15EFEC9908081B036DDC70F6F9B7E193479371432246DAE9C30EAE0"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "848B2B1B7C2A63004F4BA0D3904F980B472FF893977F32F71EBA98B7E2536BF4"
)
EXPECTED_BOUNDARY_SHA256 = (
    "0687509A6E4701F69CBB730857522C4CE5BC72199325AFA4B78BBBCCB12F5631"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "86F2151108F965914AA96AE5A0436F27C25678776A8D8DFF54B0374E8A2C78FF"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "D12126506688F5ADA49340AB6816FEC6AD67D5F3641990D81BC36D3CD39B29D9"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "D28D3D2DFFD28F803030A60246E74CE4749C2AFEB6613CEC141E0BA8B86570BD"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "1B3866CBE43B1909CE5551E2342FFF1192EE02E9D508768E4073B564E186B2FA"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B6D37C9F51E8C7F39B8EAB76567AB72E0D4A41731E2394F5A0D8BDF325662204"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "FEFD2E1AD808D22DFF918DF16F1C6A5934C9AEA7BFEF8136B64410C9C5C45FE6"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "77902C31C74D7A24D05E92D4F6783CEBFDF69B41AF39353E4C310830254EB7A4"
)
EXPECTED_CANDIDATE_SHA256 = (
    "CCAD0D1DE302E11047E3C9FDEB673158D26C94346310B8FEB7F7D5412CF8744B"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "78E1F609321B44F2A688A3F3E014029838750250744814CFAC4597075E04ABBA"
)
EXPECTED_CHANGED_LITERAL_COUNT = 1
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 56

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and the complete PK record was reviewed; "
    "the complete record is raw-exact to a completed Base donor and its "
    "same-record exact prefill companion is validated; Base runtime and VM "
    "state are never inherited; direct calls, protected outer whitespace, "
    "source and current gaps, queue and segment boundaries, two-run "
    "reproduction, tamper rejection, reverse overlays, outside-scope "
    "identity, and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1215_base",
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
        len(rows) != 146
        or len(visible) != 200
        or visible[0] != "7:2859:0"
        or visible[-1] != "8:237:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B070 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "8:125:0"
        or queue_slice[-1] != "8:189:1"
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
        len(prefilled) != 66
        or len(residual) != 1
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
        or len(prefilled) != 66
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
    "HIDDEN_CURRENT_COMPANION_COORDINATES",
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
        len(rows) != 1
        or len(validated) != 1
        or counts != Counter({"runtime_fragment_pending": 1})
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
    BASE.install_base_globals()
    BASE.BASE.install_base_globals()
    BASE.BASE.BASE.propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B070_S1215",
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
                "exact_reuse_prefill_count": 66,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count": 1,
                "masked_complete_base_donor_record_count": 0,
                "semantic_base_context_record_count": 0,
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
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
