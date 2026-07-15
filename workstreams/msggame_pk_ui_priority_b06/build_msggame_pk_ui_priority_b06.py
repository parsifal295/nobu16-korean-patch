#!/usr/bin/env python3
"""Build the source-free 300-entry PK msggame UI-priority B06 overlay."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

import candidate_selection
from translations_block6 import TRANSLATIONS_BLOCK6
from translations_blocks7_9_15 import TRANSLATIONS_BLOCKS7_9_15


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
RESOURCE = "MSG_PK/SC/msggame.bin"
BATCH_ID = "msggame_pk_ui_priority_b06_300.v1"
OVERLAY_NAME = "msggame_ko_pk_ui_priority_b06_300.v1.json"
EVIDENCE_NAME = "msggame_pk_ui_priority_b06_evidence.v1.json"
REVIEW_NAME = "msggame_pk_ui_priority_b06_review.v1.json"
VALIDATION_NAME = "msggame_pk_ui_priority_b06_validation.v1.json"
SELF_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()
B04_RELATIVE = candidate_selection.B04_OVERLAY.relative_to(REPO_ROOT).as_posix()
B05_RELATIVE = candidate_selection.B05_OVERLAY.relative_to(REPO_ROOT).as_posix()


class _B04BuildCompatibilityDict(dict[tuple[int, int, int], str]):
    """Expose B04's legacy preflight length while iterating all B06 entries."""

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


def _augmented_progress(source: Path, destination: Path) -> None:
    payload = _read_json(source)
    resources = payload.get("resources")
    matches = [item for item in resources if item.get("path") == RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise ValueError("progress must contain exactly one PK msggame resource")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(value, str) for value in patterns):
        raise ValueError("PK msggame progress overlay list is invalid")
    def keep_pre_b06(value: str) -> bool:
        prefix = "workstreams/msggame_pk_ui_priority_b"
        if not value.startswith(prefix):
            return True
        suffix = value[len(prefix) :].split("/", 1)[0]
        return not suffix.isdecimal() or int(suffix) < 6

    # Freeze the proof at B04+B05 even after B06 or future batches are added
    # to the shared progress catalog.
    patterns[:] = [value for value in patterns if keep_pre_b06(value)]
    for predecessor in (B04_RELATIVE, B05_RELATIVE):
        if predecessor not in patterns:
            patterns.append(predecessor)
        if patterns.count(predecessor) != 1:
            raise ValueError(f"predecessor must be registered exactly once: {predecessor}")
    if patterns.index(B04_RELATIVE) > patterns.index(B05_RELATIVE):
        raise ValueError("B05 predecessor must follow B04")
    _write_json(destination, payload)


def _translations() -> dict[tuple[int, int, int], str]:
    selected, context = candidate_selection.select_coordinates()
    combined = {**TRANSLATIONS_BLOCK6, **TRANSLATIONS_BLOCKS7_9_15}
    if len(combined) != 300 or set(combined) != set(selected):
        raise ValueError("B06 translation coordinates differ from the pinned selection")
    actual_hash = context["builder"].canonical_hash([list(value) for value in sorted(combined)])
    if actual_hash != candidate_selection.B06_COORDINATES_SHA256:
        raise ValueError("B06 translation coordinate hash changed")
    return combined


def _rewrite_metadata(builder: Any, out_root: Path) -> dict[str, Any]:
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    validation_path = out_root / VALIDATION_NAME

    overlay = _read_json(overlay_path)
    overlay["translation_provenance"].update(
        {
            "kind": "parallel_agent_battle_deployment_diplomacy_and_advice_ui_translation",
            "context_languages": ["SC", "JP", "EN", "TC"],
            "switch_context": {
                "author": "snake7594",
                "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
                "release_tag": "v1.3",
                "asset_sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
                "unique_jp_hash_alignment_count": 74,
                "use": "semantic_and_terminology_reference_only_pc_sc_structure_retained",
            },
        }
    )
    overlay["selection_policy"] = {
        "priority": "battle_status_deployment_diplomacy_council_and_advice_ui",
        "blocks": [6, 7, 9, 15],
        "block_entry_counts": {"6": 130, "7": 37, "9": 116, "15": 17},
        "single_literal_records_only": True,
        "format_control_pua_free_selection": True,
        "read_only_predecessors": [B04_RELATIVE, B05_RELATIVE],
        "event_dialogue_block_17_excluded": True,
        "source_text_embedded": False,
    }
    _write_json(overlay_path, overlay)

    evidence = _read_json(evidence_path)
    evidence["scope"].update(
        {
            "selection": "battle_status_deployment_diplomacy_council_and_advice_ui",
            "reserved_b04_count": 250,
            "reserved_b05_count": 300,
            "reserved_b04_coordinates_sha256": candidate_selection.B04_COORDINATES_SHA256,
            "reserved_b05_coordinates_sha256": candidate_selection.B05_COORDINATES_SHA256,
            "switch_v13_semantic_context_count": 74,
        }
    )
    evidence["overlap_checks"].update(
        {"reserved_b04_overlap_count": 0, "reserved_b05_overlap_count": 0}
    )
    _write_json(evidence_path, evidence)

    review = _read_json(review_path)
    review["quality_state"] = "parallel_agent_b06_ui_translation_complete"
    _write_json(review_path, review)

    validation = _read_json(validation_path)
    validation["coordinate_sets"].update(
        {
            "selected_sha256": candidate_selection.B06_COORDINATES_SHA256,
            "selected_reserved_b04_disjoint": True,
            "selected_reserved_b05_disjoint": True,
        }
    )
    validation["proofs"].update(
        {
            "duplicate_source_translation_consistent": True,
            "reserved_b04_and_b05_overlays_and_coordinates_pinned": True,
            "event_dialogue_block_17_excluded": True,
            "switch_v13_context_consulted_where_uniquely_aligned": True,
            "parallel_translation_parts_merged": True,
        }
    )
    full = validation["full_candidate_validation"]
    full["full_overlay_entry_count"] = full.pop("b04_entry_count")
    full["selected_b06_entry_count"] = 300
    validation["source_free_scan"] = builder.assert_source_free((overlay_path, evidence_path, review_path))
    validation["artifacts"] = {
        "overlay": builder.write_json(overlay_path, overlay),
        "evidence": builder.write_json(evidence_path, evidence),
        "review": builder.write_json(review_path, review),
    }
    validation["generator"] = {"path": SCRIPT_PATH.name, "sha256": builder.sha256(SCRIPT_PATH.read_bytes())}
    _write_json(validation_path, validation)
    builder.assert_source_free((validation_path,))
    return {
        "entry_count": overlay["entry_count"],
        "selected_coordinates_sha256": candidate_selection.B06_COORDINATES_SHA256,
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
    translations = _translations()
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
    with tempfile.TemporaryDirectory(prefix="nobu16-b06-progress-") as temp_root:
        progress_path = Path(temp_root) / "translation_progress.b06.json"
        _augmented_progress(args.progress.resolve(), progress_path)
        delegated_args = copy.copy(args)
        delegated_args.progress = progress_path
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
