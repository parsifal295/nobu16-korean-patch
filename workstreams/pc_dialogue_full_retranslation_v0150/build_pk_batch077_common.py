#!/usr/bin/env python3
"""Shared configuration layer for PK batch 077 residual segments."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch074_common as COMMON


run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals


def _install_b077_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(
        COMMON.BASE,
        "HIDDEN_CURRENT_COMPANION_COORDINATES",
        COMMON.CONFIG.get("hidden_current_companion_coordinates", ()),
    )


COMMON.install_globals = _install_b077_globals


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
    hidden_current_companion_coordinates: tuple[str, ...],
    semantic_base_context: dict[int, tuple[str, ...]],
    expected_base_raw_matches:
    dict[int, tuple[tuple[int, int], ...]],
    expected_base_literal_matches:
    dict[int, tuple[tuple[int, int], ...]],
    expected_base_masked_matches:
    dict[int, tuple[tuple[int, int], ...]],
    expected_controls_by_record:
    dict[int, tuple[tuple[int, ...], tuple[str, ...]]],
    source_call_roots: tuple[int, ...],
    boundary_record_keys: tuple[tuple[int, int], ...],
    speaker_style: tuple[tuple[int, str], ...],
    terminology_policy: tuple[tuple[str, str], ...],
    basis: str,
    expected_changed_literal_count: int,
    pins: dict[str, Any] | None = None,
) -> dict[str, Any]:
    segment_name = f"pk_msggame_B077_S{segment}"
    decision_root = COMMON.DECISIONS_ROOT
    cfg: dict[str, Any] = {
        "script": script.resolve(),
        "output": decision_root / f"{segment_name}.private.v1.jsonl",
        "optional_neighbors": tuple(
            decision_root / f"pk_msggame_B077_S{neighbor}.private.v1.jsonl"
            for neighbor in (1235, 1236, 1237)
            if neighbor != segment
        ),
        "segment": segment,
        "segment_name": segment_name,
        "queue_batch_id": "pk_msggame-B077",
        "queue_start": queue_start,
        "queue_stop": queue_stop,
        "queue_row_count": 107,
        "queue_visible_count": 199,
        "queue_first": "8:995:0",
        "queue_last": "8:1101:3",
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
        "hidden_current_companion_coordinates":
        hidden_current_companion_coordinates,
        "semantic_base_context": semantic_base_context,
        "expected_base_raw_matches": expected_base_raw_matches,
        "expected_base_literal_matches": expected_base_literal_matches,
        "expected_base_masked_matches": expected_base_masked_matches,
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
        "expected_changed_literal_count": expected_changed_literal_count,
        "expected_combined_changed_literal_count": -1,
    }
    if pins:
        cfg.update(pins)
    return cfg
