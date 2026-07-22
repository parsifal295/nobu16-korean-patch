#!/usr/bin/env python3
"""Build and validate the source-free v0.15.0 retranslation progress ledger."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
DECISIONS_DIR = OUTPUT_ROOT / "decisions"
QUEUE_PATH = OUTPUT_ROOT / "review_queue.private.v1.jsonl"
BATCHES_PATH = OUTPUT_ROOT / "review_batches.source_free.v1.json"
CANDIDATE_MANIFEST = OUTPUT_ROOT / "candidate" / "candidate_manifest.source_free.v1.json"
PROGRESS_PATH = WORKSTREAM / "progress.source_free.v1.json"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_progress_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RuntimeError(f"required JSONL is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"{path}:{line_number} is not a JSON object")
        rows.append(value)
    return rows


def coordinate_key(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    if len(parts) != 3:
        raise RuntimeError(f"invalid decision coordinate: {value}")
    return parts


def batch_key(value: str) -> tuple[str, int]:
    resource, ordinal = value.rsplit("-B", 1)
    return resource, int(ordinal)


def segment_id(path: Path) -> str:
    suffix = ".private.v1.jsonl"
    if not path.name.endswith(suffix):
        raise RuntimeError(f"unexpected decision filename: {path.name}")
    return path.name[: -len(suffix)]


def build_progress() -> dict[str, Any]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    decision_paths = sorted(DECISIONS_DIR.glob("*.private.v1.jsonl"))
    if not decision_paths:
        raise RuntimeError(f"no private decision segments found below {DECISIONS_DIR}")

    queue_rows = load_jsonl(QUEUE_PATH)
    batch_catalog_raw = json.loads(BATCHES_PATH.read_text(encoding="utf-8"))
    batch_catalog = {row["batch_id"]: row for row in batch_catalog_raw["batches"]}
    target_to_batch: dict[tuple[str, str], str] = {}
    for queue_row in queue_rows:
        resource = str(queue_row["resource"])
        batch_id = str(queue_row["batch_id"])
        for target in queue_row["target_literals"]:
            if target["visible"]:
                target_to_batch[(resource, str(target["coordinate"]))] = batch_id

    all_rows: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    batch_decisions: Counter[str] = Counter()
    batch_pending: Counter[str] = Counter()
    batch_eligible: Counter[str] = Counter()
    scope_classification_counts: Counter[str] = Counter()
    batch_scope_classifications: defaultdict[str, Counter[str]] = defaultdict(Counter)

    for path in decision_paths:
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        rows = load_jsonl(path)
        if not rows:
            raise RuntimeError(f"decision segment is empty: {path}")
        resources = {str(row["resource"]) for row in rows}
        if len(resources) != 1:
            raise RuntimeError(f"decision segment mixes resources: {path}")
        resource = next(iter(resources))
        coordinates = sorted((str(row["coordinate"]) for row in rows), key=coordinate_key)
        queue_batch_ids: set[str] = set()
        runtime_counts = Counter(str(row["runtime_review"]) for row in rows)
        segment_scope_counts = Counter(str(row["scope_classification"]) for row in rows)

        for row in rows:
            key = (resource, str(row["coordinate"]))
            if key in seen:
                raise RuntimeError(f"duplicate decision across segments: {key}")
            seen.add(key)
            if row["semantic_review"] != "approved":
                raise RuntimeError(f"unapproved decision in {path}: {key}")
            if row["switch_korean_used"] or row["historic_korean_used"]:
                raise RuntimeError(f"prohibited Korean authority flag in {path}: {key}")
            classification = str(row["scope_classification"])
            if classification not in ENGINE.SCOPE_CLASSIFICATIONS:
                raise RuntimeError(f"invalid scope classification in {path}: {key}")
            batch_id = target_to_batch.get(key)
            if batch_id is None:
                raise RuntimeError(f"decision target is absent from private queue: {key}")
            queue_batch_ids.add(batch_id)
            batch_decisions[batch_id] += 1
            scope_classification_counts[classification] += 1
            batch_scope_classifications[batch_id][classification] += 1
            if row["runtime_review"] == "pending":
                batch_pending[batch_id] += 1
            else:
                batch_eligible[batch_id] += 1
            all_rows.append(row)

        segments.append(
            {
                "segment_id": segment_id(path),
                "resource": resource,
                "first_coordinate": coordinates[0],
                "last_coordinate": coordinates[-1],
                "decision_count": len(rows),
                "semantic_review_approved": len(rows),
                "runtime_review_not_required": runtime_counts["not_required"],
                "runtime_review_verified": runtime_counts["verified"],
                "runtime_review_pending": runtime_counts["pending"],
                "scope_classification_counts": {
                    classification: segment_scope_counts[classification]
                    for classification in sorted(ENGINE.SCOPE_CLASSIFICATIONS)
                },
                "queue_batch_ids": sorted(queue_batch_ids, key=batch_key),
                "switch_korean_used": False,
                "historic_korean_used": False,
                "steam_write_performed": False,
            }
        )

    touched_batch_ids = sorted(batch_decisions, key=batch_key)
    queue_batch_coverage: list[dict[str, Any]] = []
    for batch_id in touched_batch_ids:
        catalog = batch_catalog[batch_id]
        visible_count = int(catalog["visible_current_literal_count"])
        decision_count = batch_decisions[batch_id]
        if decision_count > visible_count:
            raise RuntimeError(f"decision count exceeds visible target count for {batch_id}")
        queue_batch_coverage.append(
            {
                "batch_id": batch_id,
                "resource": catalog["resource"],
                "first_record_coordinate": catalog["first_record_coordinate"],
                "last_record_coordinate": catalog["last_record_coordinate"],
                "visible_target_count": visible_count,
                "decision_count": decision_count,
                "runtime_review_pending": batch_pending[batch_id],
                "fully_candidate_eligible": batch_eligible[batch_id],
                "scope_classification_counts": {
                    classification: batch_scope_classifications[batch_id][classification]
                    for classification in sorted(ENGINE.SCOPE_CLASSIFICATIONS)
                },
                "semantic_complete": decision_count == visible_count,
            }
        )

    total_targets = len(prepared.visible_targets)
    approved = len(all_rows)
    pending = sum(row["runtime_review"] == "pending" for row in all_rows)
    eligible = approved - pending
    semantic_complete = approved == total_targets
    candidate_complete = semantic_complete and pending == 0 and CANDIDATE_MANIFEST.is_file()
    return {
        "schema": "nobu16.kr.pc-dialogue-full-retranslation-progress.v1",
        "release_target": "0.15.0",
        "mechanical_candidate_universe": total_targets,
        "scope_classification": {
            "status": "complete" if semantic_complete else "in_progress",
            "categories": [
                "retranslated",
                "runtime_fragment_pending",
                "confirmed_non_display",
            ],
        },
        "segment_naming_note": (
            "segment B-numbers are authoring work-package identifiers; "
            "queue_batch_ids records the generated review-queue batches"
        ),
        "segments": segments,
        "queue_batch_coverage": queue_batch_coverage,
        "totals": {
            "semantic_review_approved": approved,
            "runtime_review_pending": pending,
            "fully_candidate_eligible": eligible,
            "scope_classification_counts": {
                classification: scope_classification_counts[classification]
                for classification in sorted(ENGINE.SCOPE_CLASSIFICATIONS)
            },
            "semantic_completion": semantic_complete,
            "candidate_build_complete": candidate_complete,
        },
    }


def serialized_progress() -> str:
    return json.dumps(build_progress(), ensure_ascii=False, indent=2) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--validate", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.write and not args.validate:
        raise RuntimeError("choose --write, --validate, or both")
    content = serialized_progress()
    if args.write:
        ENGINE.atomic_write(PROGRESS_PATH, content)
    if args.validate:
        if not PROGRESS_PATH.is_file():
            raise RuntimeError(f"progress ledger is absent: {PROGRESS_PATH}")
        if PROGRESS_PATH.read_text(encoding="utf-8") != content:
            raise RuntimeError(f"progress ledger drift: {PROGRESS_PATH}")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment_count": len(json.loads(content)["segments"]),
                "semantic_review_approved": json.loads(content)["totals"]["semantic_review_approved"],
                "steam_write_performed": False,
                "output": str(PROGRESS_PATH),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
