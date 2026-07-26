#!/usr/bin/env python3
"""Shared configuration layer for PK batch 079 residual segments."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch074_common as COMMON


run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals


def _record_key(record_id: int) -> tuple[int, int]:
    return (
        int(COMMON.CONFIG["target_record_blocks"][record_id]),
        record_id,
    )


def _context_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    cfg = COMMON.CONFIG
    _, _, _, _, record_keys = COMMON.queue_evidence(prepared)
    source_target = tuple(
        (
            coordinate,
            COMMON.literal_texts(
                records_by_label["jp"],
                COMMON.coordinate_key(coordinate)[:2],
            )[COMMON.coordinate_key(coordinate)[2]],
        )
        for coordinate in cfg["target_coordinates"]
    )
    current_target = tuple(
        (
            coordinate,
            COMMON.literal_texts(
                records_by_label["current"],
                COMMON.coordinate_key(coordinate)[:2],
            )[COMMON.coordinate_key(coordinate)[2]],
        )
        for coordinate in cfg["target_coordinates"]
    )
    corpus = tuple(
        (
            label,
            key,
            COMMON.sha256_bytes(records[key].data),
            COMMON.literal_texts(records, key),
        )
        for label, records in records_by_label.items()
        for key in record_keys
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(
                    records_by_label["jp"][_record_key(record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(
                    records_by_label["current"][_record_key(record_id)]
                )
            ),
        )
        for record_id in cfg["target_record_ids"]
    )
    boundary = tuple(
        (
            label,
            key,
            COMMON.sha256_bytes(records_by_label[label][key].data),
            COMMON.literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for key in cfg["boundary_record_keys"]
    )
    controls = tuple(
        (
            label,
            record_id,
            COMMON.CORE.runtime_controls(
                records_by_label[label][_record_key(record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in cfg["target_record_ids"]
    )
    return {
        "source_target": source_target,
        "current_target": current_target,
        "corpus": corpus,
        "gaps": gaps,
        "boundary": boundary,
        "controls": controls,
    }


def _base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    cfg = COMMON.CONFIG
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {cfg['segment']} Base promoted input drifted"
        )
    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    target_set = set(cfg["target_coordinates"])
    companion_set = set(cfg["prefill_companion_coordinates"])
    hidden_set = set(cfg["hidden_current_companion_coordinates"])
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in cfg["target_record_ids"]:
        key = _record_key(record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(records_by_label["jp"], key)
        current_literals = COMMON.literal_texts(
            records_by_label["current"],
            key,
        )
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if COMMON.literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
                and COMMON.CORE.mask_call_operands(record)
                == COMMON.CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != cfg["expected_arity"][record_id]
            or raw_matches != cfg["expected_base_raw_matches"][record_id]
            or literal_matches
            != cfg["expected_base_literal_matches"][record_id]
            or masked_matches
            != cfg["expected_base_masked_matches"][record_id]
        ):
            raise RuntimeError(
                f"segment {cfg['segment']} Base search drifted: "
                f"{key[0]}:{record_id}"
            )
        references: list[tuple[Any, ...]] = []
        donor_coordinates = cfg["semantic_base_context"][record_id]
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {cfg['segment']} Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "semantic_only",
                "runtime_vm_not_inherited",
            ))
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(cfg["expected_arity"][record_id]):
            coordinate = f"{key[0]}:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(cfg["translations"][coordinate])
                owners.append("segment_manual_multilingual")
                seen_target.add(coordinate)
            elif coordinate in companion_set:
                prefill = prefill_rows.get(coordinate)
                if (
                    prefill is None
                    or prefill.get("semantic_review") != "approved"
                    or prefill.get("runtime_review") != "pending"
                    or prefill["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                    != cfg["prefill_companion_donor"][coordinate]
                ):
                    raise RuntimeError(
                        f"segment {cfg['segment']} companion drifted: "
                        f"{coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append("base_exact_prefill_runtime_pending")
                seen_companion.add(coordinate)
            elif coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment {cfg['segment']} hidden newline drifted: "
                        f"{coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {cfg['segment']} incomplete record: "
                    f"{coordinate}"
                )
        base_evidence.append((
            (key[0], record_id),
            COMMON.sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(
                value.hex().upper() for value in COMMON.gap_bytes(source)
            ),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(references),
            "semantic_context_only",
        ))
        assembly_evidence.append((
            (key[0], record_id),
            tuple(owners),
            tuple(assembled),
            None,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError(
            f"segment {cfg['segment']} assembly ownership drifted"
        )
    return tuple(base_evidence), tuple(assembly_evidence)


def _runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    cfg = COMMON.CONFIG
    key = _record_key(record_id)
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_controls = COMMON.CORE.runtime_controls(source)
    current_controls = COMMON.CORE.runtime_controls(current)
    references = cfg["semantic_base_context"][record_id]
    return {
        "runtime_category": dict(cfg["speaker_style"])[record_id],
        "source_record_gap_sha256": COMMON.CORE.canonical_sha256(
            tuple(
                value.hex().upper() for value in COMMON.gap_bytes(source)
            )
        ),
        "current_record_gap_sha256": COMMON.CORE.canonical_sha256(
            tuple(
                value.hex().upper() for value in COMMON.gap_bytes(current)
            )
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        COMMON.gap_bytes(source) == COMMON.gap_bytes(current),
        "base_complete_record_match_kind": "none_semantic_context_only",
        "base_context_reference_coordinates": references,
        "base_complete_record_match_coordinates": tuple(
            f"{match[0]}:{match[1]}"
            for match in cfg["expected_base_literal_matches"][record_id]
        ),
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed": any(
            coordinate.startswith(f"{key[0]}:{record_id}:")
            for coordinate in cfg["prefill_companion_coordinates"]
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_donor_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def _unchecked_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    cfg = COMMON.CONFIG
    current = records_by_label["current"]
    replacements = {
        COMMON.coordinate_key(coordinate): translation
        for coordinate, translation in cfg["translations"].items()
    }
    reverse = {
        key: COMMON.literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = COMMON.ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order_candidate = COMMON.ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if candidate != reverse_order_candidate:
        raise RuntimeError(
            f"segment {cfg['segment']} reverse-order overlay drifted"
        )
    candidate_records = COMMON.ENGINE.archive_records(
        COMMON.ENGINE.parse_packed_msggame(candidate).archive
    )
    target_record_keys = {
        COMMON.coordinate_key(coordinate)[:2]
        for coordinate in cfg["target_coordinates"]
    }
    if (
        len(current) != 21_751
        or len(candidate_records) != 21_751
        or set(replacements) != {
            COMMON.coordinate_key(coordinate)
            for coordinate in cfg["target_coordinates"]
        }
    ):
        raise RuntimeError(
            f"segment {cfg['segment']} candidate universe drifted"
        )
    for key, current_record in current.items():
        if (
            key not in target_record_keys
            and candidate_records[key].data != current_record.data
        ):
            raise RuntimeError(
                f"segment {cfg['segment']} changed out-of-scope record: "
                f"{key}"
            )
    for record_id in cfg["target_record_ids"]:
        key = _record_key(record_id)
        expected = list(COMMON.literal_texts(current, key))
        for literal_id in range(cfg["expected_arity"][record_id]):
            coordinate = f"{key[0]}:{record_id}:{literal_id}"
            if coordinate in cfg["translations"]:
                expected[literal_id] = cfg["translations"][coordinate]
        if (
            COMMON.gap_bytes(candidate_records[key])
            != COMMON.gap_bytes(current[key])
            or COMMON.literal_texts(candidate_records, key)
            != tuple(expected)
        ):
            raise RuntimeError(
                f"segment {cfg['segment']} target record drifted: {key}"
            )
    if (
        COMMON.ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(
            f"segment {cfg['segment']} reverse overlay is not byte-exact"
        )
    changed = sum(
        translation
        != COMMON.literal_texts(
            current,
            COMMON.coordinate_key(coordinate)[:2],
        )[COMMON.coordinate_key(coordinate)[2]]
        for coordinate, translation in cfg["translations"].items()
    )
    return candidate, COMMON.sha256_bytes(candidate), changed


def _install_b079_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    cfg = COMMON.CONFIG
    setattr(COMMON.BASE, "BLOCK_ID", cfg["default_block_id"])
    setattr(
        COMMON.BASE,
        "HIDDEN_CURRENT_COMPANION_COORDINATES",
        cfg["hidden_current_companion_coordinates"],
    )
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        _base_and_assembly_evidence,
    )
    setattr(COMMON.CORE, "context_evidence", _context_evidence)
    setattr(COMMON.CORE, "runtime_evidence", _runtime_evidence)
    setattr(COMMON.CORE.PARENT, "unchecked_candidate", _unchecked_candidate)
    setattr(
        COMMON.CORE,
        "base_and_assembly_evidence",
        _base_and_assembly_evidence,
    )


COMMON.install_globals = _install_b079_globals


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
    target_record_blocks: dict[int, int],
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
    segment_name = f"pk_msggame_B079_S{segment}"
    decision_root = COMMON.DECISIONS_ROOT
    cfg: dict[str, Any] = {
        "script": script.resolve(),
        "output": decision_root / f"{segment_name}.private.v1.jsonl",
        "optional_neighbors": tuple(
            decision_root / f"pk_msggame_B079_S{neighbor}.private.v1.jsonl"
            for neighbor in (1241, 1242, 1243)
            if neighbor != segment
        ),
        "segment": segment,
        "segment_name": segment_name,
        "queue_batch_id": "pk_msggame-B079",
        "queue_start": queue_start,
        "queue_stop": queue_stop,
        "queue_row_count": 141,
        "queue_visible_count": 199,
        "queue_first": "8:1233:0",
        "queue_last": "9:486:0",
        "slice_visible_count": queue_stop - queue_start,
        "slice_prefill_count":
        (queue_stop - queue_start) - len(target_coordinates),
        "slice_first": slice_first,
        "slice_last": slice_last,
        "target_coordinates": target_coordinates,
        "translations": translations,
        "target_record_ids": target_record_ids,
        "target_record_blocks": target_record_blocks,
        "default_block_id": next(iter(target_record_blocks.values())),
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
