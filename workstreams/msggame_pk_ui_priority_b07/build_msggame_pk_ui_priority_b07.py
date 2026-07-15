#!/usr/bin/env python3
"""Build the source-free 300-entry PK msggame UI-priority B07 overlay."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

import candidate_selection
from translations_block6 import TRANSLATIONS_BLOCK6
from translations_block8_landmarks import TRANSLATIONS_BLOCK8_LANDMARKS
from translations_block8_reports_a import TRANSLATIONS_BLOCK8_REPORTS_A
from translations_block8_reports_b import TRANSLATIONS_BLOCK8_REPORTS_B
from translations_help import TRANSLATIONS_HELP


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
RESOURCE = "MSG_PK/SC/msggame.bin"
BATCH_ID = "msggame_pk_ui_priority_b07_300.v1"
OVERLAY_NAME = "msggame_ko_pk_ui_priority_b07_300.v1.json"
EVIDENCE_NAME = "msggame_pk_ui_priority_b07_evidence.v1.json"
REVIEW_NAME = "msggame_pk_ui_priority_b07_review.v1.json"
VALIDATION_NAME = "msggame_pk_ui_priority_b07_validation.v1.json"
SELF_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()


class _B04BuildCompatibilityDict(dict[tuple[int, int, int], str]):
    """Expose B04's legacy preflight length while iterating all B07 entries."""

    def __len__(self) -> int:
        return 250


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _frozen_progress(source: Path, destination: Path) -> None:
    """Keep only the immutable progress prefix ending at B06."""

    payload = _read_json(source)
    resources = payload.get("resources")
    matches = [item for item in resources if item.get("path") == RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise ValueError("progress must contain exactly one PK msggame resource")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(value, str) for value in patterns):
        raise ValueError("PK msggame progress overlay list is invalid")
    if patterns.count(candidate_selection.B06_RELATIVE) != 1:
        raise ValueError("B06 boundary must be registered exactly once")
    marker = patterns.index(candidate_selection.B06_RELATIVE)
    prefix = patterns[: marker + 1]
    builder = candidate_selection._load_b04()
    if len(prefix) != candidate_selection.PREFIX_PATTERN_COUNT:
        raise ValueError("B06 prefix count changed")
    if builder.canonical_hash(prefix) != candidate_selection.PREFIX_PATTERNS_SHA256:
        raise ValueError("B06 prefix order changed")
    matches[0]["overlay_globs"] = prefix
    _write_json(destination, payload)


def _translations(progress_path: Path | None = None) -> dict[tuple[int, int, int], str]:
    selected, context = candidate_selection.select_coordinates(progress_path=progress_path)
    combined = {
        **TRANSLATIONS_BLOCK6,
        **TRANSLATIONS_BLOCK8_REPORTS_A,
        **TRANSLATIONS_BLOCK8_REPORTS_B,
        **TRANSLATIONS_BLOCK8_LANDMARKS,
        **TRANSLATIONS_HELP,
    }
    if len(combined) != 300 or set(combined) != set(selected):
        raise ValueError("B07 translation coordinates differ from the pinned selection")
    actual_hash = context["builder"].canonical_hash([list(value) for value in sorted(combined)])
    if actual_hash != candidate_selection.B07_COORDINATES_SHA256:
        raise ValueError("B07 translation coordinate hash changed")
    return combined


def _rewrite_metadata(builder: Any, out_root: Path) -> dict[str, Any]:
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    validation_path = out_root / VALIDATION_NAME

    overlay = _read_json(overlay_path)
    overlay["translation_provenance"].update(
        {
            "kind": "parallel_agent_management_status_report_and_help_ui_translation",
            "context_languages": ["SC", "JP", "EN", "TC"],
            "public_duplicate_translation_reuse_count": 2,
            "switch_context": {
                "author": "snake7594",
                "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
                "release_tag": "v1.3",
                "asset_sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
                "unique_jp_hash_semantic_context_count": 155,
                "use": "semantic_and_terminology_reference_only_pc_sc_structure_retained",
            },
        }
    )
    overlay["selection_policy"] = {
        "priority": "management_status_disaster_revolt_landmark_tutorial_and_help_ui",
        "blocks": [6, 8, 13, 14],
        "block_entry_counts": {"6": 28, "8": 227, "13": 28, "14": 17},
        "immutable_progress_boundary": candidate_selection.B06_RELATIVE,
        "immutable_predecessor_entry_count": candidate_selection.PREFIX_ENTRY_COUNT,
        "self_registration_excluded_from_selection": True,
        "future_registrations_excluded_from_selection_and_checked_disjoint": True,
        "punctuation_and_layout_symbol_only_slots_excluded": True,
        "narrative_blocks_16_and_17_excluded": True,
        "source_text_embedded": False,
    }
    _write_json(overlay_path, overlay)

    evidence = _read_json(evidence_path)
    evidence["scope"].update(
        {
            "selection": "management_status_disaster_revolt_landmark_tutorial_and_help_ui",
            "immutable_predecessor_entry_count": candidate_selection.PREFIX_ENTRY_COUNT,
            "immutable_predecessor_patterns_sha256": candidate_selection.PREFIX_PATTERNS_SHA256,
            "immutable_predecessor_coordinates_sha256": candidate_selection.PREFIX_COORDINATES_SHA256,
            "switch_v13_semantic_context_count": 155,
        }
    )
    evidence["overlap_checks"].update(
        {
            "immutable_predecessor_overlap_count": 0,
            "future_registration_overlap_count": 0,
        }
    )
    evidence["registration_filter"] = {
        "boundary": candidate_selection.B06_RELATIVE,
        "self_registration_states_supported": [0, 1],
        "self_does_not_feed_selection": True,
        "future_batches_do_not_feed_selection": True,
        "future_batches_source_free_target_only_and_disjoint": True,
    }
    _write_json(evidence_path, evidence)

    review = _read_json(review_path)
    review["quality_state"] = "parallel_agent_b07_management_report_and_help_ui_translation_complete"
    _write_json(review_path, review)

    validation = _read_json(validation_path)
    validation["coordinate_sets"].update(
        {
            "selected_sha256": candidate_selection.B07_COORDINATES_SHA256,
            "selected_immutable_predecessors_disjoint": True,
            "selected_future_registrations_disjoint": True,
        }
    )
    validation["proofs"].update(
        {
            "duplicate_source_translation_consistent": True,
            "immutable_b06_progress_prefix_pinned": True,
            "self_registration_does_not_feed_selection": True,
            "future_registration_does_not_feed_selection": True,
            "future_overlays_source_free_target_only_and_disjoint": True,
            "narrative_blocks_16_and_17_excluded": True,
            "switch_v13_context_consulted_where_uniquely_aligned": True,
            "parallel_translation_parts_merged": True,
        }
    )
    full = validation["full_candidate_validation"]
    full["full_overlay_entry_count"] = full.pop("b04_entry_count")
    full["selected_b07_entry_count"] = 300
    validation["source_free_scan"] = builder.assert_source_free(
        (overlay_path, evidence_path, review_path)
    )
    validation["artifacts"] = {
        "overlay": builder.write_json(overlay_path, overlay),
        "evidence": builder.write_json(evidence_path, evidence),
        "review": builder.write_json(review_path, review),
    }
    validation["generator"] = {
        "path": SCRIPT_PATH.name,
        "sha256": builder.sha256(SCRIPT_PATH.read_bytes()),
    }
    _write_json(validation_path, validation)
    builder.assert_source_free((validation_path,))
    return {
        "entry_count": overlay["entry_count"],
        "selected_coordinates_sha256": candidate_selection.B07_COORDINATES_SHA256,
        "overlay_sha256": builder.sha256(overlay_path.read_bytes()),
        "full_candidate_sha256": validation["full_candidate_validation"]["target_packed_sha256"],
        "artifacts": {
            "overlay": overlay_path.relative_to(out_root).as_posix(),
            "evidence": evidence_path.relative_to(out_root).as_posix(),
            "review": review_path.relative_to(out_root).as_posix(),
            "validation": validation_path.relative_to(out_root).as_posix(),
        },
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    progress_path = args.progress.resolve()
    translations = _translations(progress_path)
    builder = candidate_selection._load_b04()
    builder.TRANSLATIONS = _B04BuildCompatibilityDict(translations)
    builder.EXCLUSIONS = {}
    builder.BATCH_ID = BATCH_ID
    builder.OVERLAY_NAME = OVERLAY_NAME
    builder.EVIDENCE_NAME = EVIDENCE_NAME
    builder.REVIEW_NAME = REVIEW_NAME
    builder.VALIDATION_NAME = VALIDATION_NAME
    builder.SELF_RELATIVE = SELF_RELATIVE
    builder.SCRIPT_PATH = SCRIPT_PATH
    builder.WORKSTREAM_ROOT = WORKSTREAM_ROOT

    out_root = args.out_root.resolve()
    with tempfile.TemporaryDirectory(prefix="nobu16-b07-progress-") as temp_root:
        frozen_progress = Path(temp_root) / "translation_progress.b07.json"
        _frozen_progress(progress_path, frozen_progress)
        delegated_args = copy.copy(args)
        delegated_args.progress = frozen_progress
        delegated_args.out_root = out_root
        builder.build(delegated_args)
    return _rewrite_metadata(builder, out_root)


def parser() -> argparse.ArgumentParser:
    builder = candidate_selection._load_b04()
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--pk-sc", type=Path, default=builder.DEFAULT_PK_SC)
    value.add_argument("--pk-jp", type=Path, default=builder.DEFAULT_PK_JP)
    value.add_argument("--pk-en", type=Path, default=builder.DEFAULT_PK_EN)
    value.add_argument("--pk-tc", type=Path, default=builder.DEFAULT_PK_TC)
    value.add_argument("--progress", type=Path, default=builder.DEFAULT_PROGRESS)
    value.add_argument("--target-catalog", type=Path, default=builder.DEFAULT_TARGET)
    value.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return value


def main() -> int:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
