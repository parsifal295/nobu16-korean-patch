#!/usr/bin/env python3
"""Tests for the source-free selector-610 targeted progress delta."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = (
    WORKSTREAM / "build_progress_post_selector610_consolidated_delta_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("selector610_progress_delta_test_builder", BUILDER_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


class Selector610ProgressDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.before = json.loads(
            BUILDER.DEFAULT_PREDECESSOR_PROGRESS.read_text(encoding="ascii")
        )
        cls.after = json.loads(
            BUILDER.DEFAULT_PROGRESS_OUTPUT.read_text(encoding="ascii")
        )

    def test_progress_artifacts_are_frozen(self) -> None:
        self.assertEqual(
            sha256_file(BUILDER.DEFAULT_PREDECESSOR_PROGRESS),
            BUILDER.EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.DEFAULT_PROGRESS_OUTPUT),
            BUILDER.EXPECTED_PROGRESS_OUTPUT_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.CHECKPOINT_PRIVATE_PATH),
            BUILDER.EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.CHECKPOINT_PUBLIC_PATH),
            BUILDER.EXPECTED_CHECKPOINT_PUBLIC_SHA256,
        )

    def test_totals_advance_by_promotions_only(self) -> None:
        before = self.before["totals"]
        after = self.after["totals"]
        self.assertEqual(
            before["runtime_review_pending"]
            - after["runtime_review_pending"],
            167,
        )
        self.assertEqual(
            after["fully_candidate_eligible"]
            - before["fully_candidate_eligible"],
            167,
        )
        self.assertEqual(after["runtime_review_pending"], 7_101)
        self.assertEqual(after["fully_candidate_eligible"], 45_702)
        self.assertEqual(
            after["scope_classification_counts"],
            {
                "confirmed_non_display": 345,
                "retranslated": 45_357,
                "runtime_fragment_pending": 7_101,
            },
        )

    def test_exact_segment_and_batch_deltas_sum_to_167(self) -> None:
        before_segments = {
            row["segment_id"]: row for row in self.before["segments"]
        }
        after_segments = {
            row["segment_id"]: row for row in self.after["segments"]
        }
        segment_deltas = {
            key: (
                before_segments[key]["runtime_review_pending"]
                - row["runtime_review_pending"]
            )
            for key, row in after_segments.items()
            if before_segments[key] != row
        }
        self.assertEqual(len(segment_deltas), 36)
        self.assertEqual(sum(segment_deltas.values()), 167)
        self.assertTrue(all(value > 0 for value in segment_deltas.values()))
        for key, delta in segment_deltas.items():
            self.assertEqual(
                after_segments[key]["runtime_review_verified"]
                - before_segments[key]["runtime_review_verified"],
                delta,
            )

        before_batches = {
            row["batch_id"]: row
            for row in self.before["queue_batch_coverage"]
        }
        after_batches = {
            row["batch_id"]: row
            for row in self.after["queue_batch_coverage"]
        }
        batch_deltas = {
            key: (
                before_batches[key]["runtime_review_pending"]
                - row["runtime_review_pending"]
            )
            for key, row in after_batches.items()
            if before_batches[key] != row
        }
        self.assertEqual(len(batch_deltas), 25)
        self.assertEqual(sum(batch_deltas.values()), 167)
        self.assertTrue(all(value > 0 for value in batch_deltas.values()))
        for key, delta in batch_deltas.items():
            self.assertEqual(
                after_batches[key]["fully_candidate_eligible"]
                - before_batches[key]["fully_candidate_eligible"],
                delta,
            )

    def test_runtime_metadata_uses_new_immutable_checkpoint(self) -> None:
        integration = self.after["runtime_vm_integration"]
        self.assertEqual(
            integration["private_integrated_decision_sha256"],
            BUILDER.EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        )
        self.assertEqual(
            integration["sha256"],
            BUILDER.EXPECTED_CHECKPOINT_PUBLIC_SHA256,
        )
        self.assertEqual(integration["promoted_total"], 29_233)
        self.assertEqual(integration["runtime_review_pending_after"], 7_101)
        self.assertTrue(
            integration["selector610_consolidated_layer_included"]
        )
        self.assertEqual(
            integration["selector610_targeted_progress_delta"],
            {
                "promotion_count": 167,
                "changed_segment_count": 36,
                "changed_batch_count": 25,
                "full_dialogue_rebuild_performed": False,
                "steam_write_performed": False,
            },
        )

    def test_progress_is_source_free_and_reproducible(self) -> None:
        raw = BUILDER.DEFAULT_PROGRESS_OUTPUT.read_text(encoding="ascii")
        self.assertIsNone(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", raw))
        self.assertNotIn('"translation":', raw)
        self.assertEqual(BUILDER.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
