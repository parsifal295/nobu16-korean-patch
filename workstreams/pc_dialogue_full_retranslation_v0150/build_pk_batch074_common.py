#!/usr/bin/env python3
"""Shared source-redacted runner for PK batch 074 residual segments."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch071_segment1218.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
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


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_b074_common_base",
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

CONFIG: dict[str, Any] = {}
DISCOVERED_PINS: dict[str, str] = {}


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    cfg = CONFIG
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == cfg["queue_batch_id"]
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != cfg["queue_row_count"]
        or len(visible) != cfg["queue_visible_count"]
        or visible[0] != cfg["queue_first"]
        or visible[-1] != cfg["queue_last"]
    ):
        raise RuntimeError(
            f"segment {cfg['segment']} B074 queue universe drifted"
        )
    queue_slice = visible[cfg["queue_start"]:cfg["queue_stop"]]
    if (
        len(queue_slice) != cfg["slice_visible_count"]
        or queue_slice[0] != cfg["slice_first"]
        or queue_slice[-1] != cfg["slice_last"]
    ):
        raise RuntimeError(f"segment {cfg['segment']} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != cfg["slice_prefill_count"]
        or residual != cfg["target_coordinates"]
    ):
        raise RuntimeError(f"segment {cfg['segment']} prefill slice drifted")
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
        raise RuntimeError(f"segment {cfg['segment']} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    cfg = CONFIG
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            cfg["translations"][coordinate]
            if coordinate in cfg["translations"]
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
        raise RuntimeError(
            f"segment {cfg['segment']} combined overlay drifted"
        )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != cfg["slice_visible_count"]
        or len(prefilled) != cfg["slice_prefill_count"]
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
        raise RuntimeError(f"segment {cfg['segment']} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    expected_sha256 = cfg["expected_combined_slice_candidate_sha256"]
    if expected_sha256 != "TO_PIN" and candidate_sha256 != expected_sha256:
        raise RuntimeError(
            f"segment {cfg['segment']} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    expected_changed = cfg["expected_combined_changed_literal_count"]
    if expected_changed >= 0 and changed != expected_changed:
        raise RuntimeError(
            f"segment {cfg['segment']} combined changed count drifted: "
            f"{changed}"
        )
    if expected_sha256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def install_globals() -> None:
    cfg = CONFIG
    values = {
        "SCRIPT": cfg["script"],
        "OUTPUT": cfg["output"],
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": cfg["optional_neighbors"],
        "STEAM_PK": STEAM_PK,
        "SEGMENT": cfg["segment"],
        "QUEUE_BATCH_ID": cfg["queue_batch_id"],
        "QUEUE_START": cfg["queue_start"],
        "QUEUE_STOP": cfg["queue_stop"],
        "QUEUE_ROW_COUNT": cfg["queue_row_count"],
        "QUEUE_VISIBLE_COUNT": cfg["queue_visible_count"],
        "SLICE_VISIBLE_COUNT": cfg["slice_visible_count"],
        "SLICE_PREFILL_COUNT": cfg["slice_prefill_count"],
        "BLOCK_ID": 8,
        "PK_RECORD_COUNT": 21_751,
        "TARGET_COORDINATES": cfg["target_coordinates"],
        "TRANSLATIONS": cfg["translations"],
        "TARGET_RECORD_IDS": cfg["target_record_ids"],
        "STATIC_RECORD_IDS": (),
        "DYNAMIC_RECORD_IDS": cfg["target_record_ids"],
        "STATIC_COORDINATES": set(),
        "DYNAMIC_COORDINATES": set(cfg["target_coordinates"]),
        "EXPECTED_ARITY": cfg["expected_arity"],
        "PREFILL_COMPANION_COORDINATES":
        cfg["prefill_companion_coordinates"],
        "PREFILL_COMPANION_DONOR": cfg["prefill_companion_donor"],
        "HIDDEN_CURRENT_COMPANION_COORDINATES": (),
        "EXACT_BASE_DONOR": {},
        "SEMANTIC_BASE_CONTEXT": cfg["semantic_base_context"],
        "EXPECTED_BASE_RAW_MATCHES": cfg["expected_base_raw_matches"],
        "EXPECTED_BASE_LITERAL_MATCHES":
        cfg["expected_base_literal_matches"],
        "EXPECTED_BASE_MASKED_MATCHES":
        cfg["expected_base_masked_matches"],
        "BOUNDARY_RECORD_KEYS": cfg["boundary_record_keys"],
        "SOURCE_CALL_ROOTS": cfg["source_call_roots"],
        "CURRENT_CALL_ROOTS": cfg["source_call_roots"],
        "EXPECTED_CONTROLS_BY_RECORD":
        cfg["expected_controls_by_record"],
        "SPEAKER_STYLE": cfg["speaker_style"],
        "TERMINOLOGY_POLICY": cfg["terminology_policy"],
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        cfg["expected_queue_universe_sha256"],
        "EXPECTED_QUEUE_SLICE_SHA256":
        cfg["expected_queue_slice_sha256"],
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        cfg["expected_prefilled_coordinate_sha256"],
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        cfg["expected_prefill_slice_context_sha256"],
        "EXPECTED_TARGET_COORDINATE_SHA256":
        cfg["expected_target_coordinate_sha256"],
        "EXPECTED_SOURCE_TARGET_SHA256":
        cfg["expected_source_target_sha256"],
        "EXPECTED_CURRENT_TARGET_SHA256":
        cfg["expected_current_target_sha256"],
        "EXPECTED_CONTEXT_CORPUS_SHA256":
        cfg["expected_context_corpus_sha256"],
        "EXPECTED_GAP_CONTRACT_SHA256":
        cfg["expected_gap_contract_sha256"],
        "EXPECTED_BOUNDARY_SHA256": cfg["expected_boundary_sha256"],
        "EXPECTED_RUNTIME_CONTROL_SHA256":
        cfg["expected_runtime_control_sha256"],
        "EXPECTED_BASE_SEARCH_SHA256":
        cfg["expected_base_search_sha256"],
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        cfg["expected_complete_assembly_sha256"],
        "EXPECTED_CALL_GRAPH_SHA256":
        cfg["expected_call_graph_sha256"],
        "EXPECTED_SPEAKER_STYLE_SHA256":
        cfg["expected_speaker_style_sha256"],
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        cfg["expected_terminology_policy_sha256"],
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        cfg["expected_translation_policy_sha256"],
        "EXPECTED_CANDIDATE_SHA256": cfg["expected_candidate_sha256"],
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        cfg["expected_combined_slice_candidate_sha256"],
        "EXPECTED_CHANGED_LITERAL_COUNT":
        cfg["expected_changed_literal_count"],
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT":
        cfg["expected_combined_changed_literal_count"],
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": cfg["basis"],
        "queue_evidence": queue_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)


def build_rows() -> tuple[Any, ...]:
    install_globals()
    return BASE.build_rows()


def make_config(
    *,
    script: Path,
    segment: int,
    queue_start: int,
    queue_stop: int,
    slice_first: str,
    slice_last: str,
    target_coordinates: tuple[str, ...],
    translations: dict[str, str],
    target_record_ids: tuple[int, ...],
    expected_arity: dict[int, int],
    prefill_companion_coordinates: tuple[str, ...],
    prefill_companion_donor: dict[str, str],
    semantic_base_context: dict[int, tuple[str, ...]],
    expected_base_raw_matches:
    dict[int, tuple[tuple[int, int], ...]],
    expected_controls_by_record:
    dict[int, tuple[tuple[int, ...], tuple[str, ...]]],
    source_call_roots: tuple[int, ...],
    boundary_record_keys: tuple[tuple[int, int], ...],
    speaker_style: tuple[tuple[int, str], ...],
    terminology_policy: tuple[tuple[str, str], ...],
    basis: str,
    pins: dict[str, Any] | None = None,
) -> dict[str, Any]:
    segment_name = f"pk_msggame_B074_S{segment}"
    cfg: dict[str, Any] = {
        "script": script.resolve(),
        "output": DECISIONS_ROOT / f"{segment_name}.private.v1.jsonl",
        "optional_neighbors": tuple(
            DECISIONS_ROOT / f"pk_msggame_B074_S{neighbor}.private.v1.jsonl"
            for neighbor in (1226, 1227, 1228)
            if neighbor != segment
        ),
        "segment": segment,
        "segment_name": segment_name,
        "queue_batch_id": "pk_msggame-B074",
        "queue_start": queue_start,
        "queue_stop": queue_stop,
        "queue_row_count": 176,
        "queue_visible_count": 200,
        "queue_first": "8:567:0",
        "queue_last": "8:742:0",
        "slice_visible_count": queue_stop - queue_start,
        "slice_prefill_count":
        (queue_stop - queue_start) - len(target_coordinates),
        "slice_first": slice_first,
        "slice_last": slice_last,
        "target_coordinates": target_coordinates,
        "translations": translations,
        "target_record_ids": target_record_ids,
        "expected_arity": expected_arity,
        "prefill_companion_coordinates": prefill_companion_coordinates,
        "prefill_companion_donor": prefill_companion_donor,
        "semantic_base_context": semantic_base_context,
        "expected_base_raw_matches": expected_base_raw_matches,
        "expected_base_literal_matches": expected_base_raw_matches,
        "expected_base_masked_matches": expected_base_raw_matches,
        "expected_controls_by_record": expected_controls_by_record,
        "source_call_roots": source_call_roots,
        "boundary_record_keys": boundary_record_keys,
        "speaker_style": speaker_style,
        "terminology_policy": terminology_policy,
        "basis": basis,
        "expected_queue_universe_sha256": "TO_PIN",
        "expected_queue_slice_sha256": "TO_PIN",
        "expected_prefilled_coordinate_sha256": "TO_PIN",
        "expected_prefill_slice_context_sha256": "TO_PIN",
        "expected_target_coordinate_sha256": "TO_PIN",
        "expected_source_target_sha256": "TO_PIN",
        "expected_current_target_sha256": "TO_PIN",
        "expected_context_corpus_sha256": "TO_PIN",
        "expected_gap_contract_sha256": "TO_PIN",
        "expected_boundary_sha256": "TO_PIN",
        "expected_runtime_control_sha256": "TO_PIN",
        "expected_base_search_sha256": "TO_PIN",
        "expected_complete_assembly_sha256": "TO_PIN",
        "expected_call_graph_sha256": "TO_PIN",
        "expected_speaker_style_sha256": "TO_PIN",
        "expected_terminology_policy_sha256": "TO_PIN",
        "expected_translation_policy_sha256": "TO_PIN",
        "expected_candidate_sha256": "TO_PIN",
        "expected_combined_slice_candidate_sha256": "TO_PIN",
        "expected_changed_literal_count": len(target_coordinates),
        "expected_combined_changed_literal_count": -1,
    }
    if pins:
        cfg.update(pins)
    return cfg


def run(config: dict[str, Any]) -> int:
    global CONFIG, DISCOVERED_PINS
    CONFIG = config
    DISCOVERED_PINS = {}
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
        raise RuntimeError(
            f"segment {config['segment']} second-run reproduction drifted"
        )
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
            f"segment {config['segment']} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(config["output"], ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        config["output"],
        require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    target_count = len(config["target_coordinates"])
    if (
        len(rows) != target_count
        or len(validated) != target_count
        or counts != Counter({"runtime_fragment_pending": target_count})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {config['segment']} decision validation drifted"
        )
    install_globals()
    BASE.propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {config['segment']} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": config["segment_name"],
        "queue": config["queue_batch_id"],
        "queue_zero_based_ordinals": [
            config["queue_start"],
            config["queue_stop"] - 1,
        ],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": config["slice_visible_count"],
        "exact_reuse_prefill_count": config["slice_prefill_count"],
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(config["target_record_ids"]),
        "same_record_prefill_companion_count":
        len(config["prefill_companion_coordinates"]),
        "raw_exact_base_context_record_count":
        sum(bool(config["expected_base_raw_matches"][record_id])
            for record_id in config["target_record_ids"]),
        "semantic_base_context_record_count": len(config["target_record_ids"]),
        "source_call_root_count": len(config["source_call_roots"]),
        "current_call_root_count": len(config["source_call_roots"]),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
        "candidate_sha256": candidate_sha256,
        "combined_slice_candidate_sha256": combined_sha256,
        "decision_sha256": sha256_bytes(config["output"].read_bytes()),
        "builder_sha256": sha256_bytes(config["script"].read_bytes()),
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
