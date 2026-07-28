#!/usr/bin/env python3
"""Boundary tests for the targeted selector-610 immutable checkpoint."""

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
REPO = WORKSTREAM.parents[1]
BUILDER_PATH = (
    WORKSTREAM
    / "build_runtime_vm_post_selector610_consolidated_checkpoint_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("selector610_delta_checkpoint_test_builder", BUILDER_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


class Selector610DeltaCheckpointTests(unittest.TestCase):
    def test_frozen_inputs_and_targeted_counts_are_exact(self) -> None:
        coverage, promotion = BUILDER.validate_frozen_inputs()
        BUILDER.validate_closure_reports(coverage, promotion)
        decisions = BUILDER.load_closure_decisions()
        self.assertEqual(len(decisions), 314)
        self.assertEqual(
            sum(
                "runtime_promotion"
                in row[BUILDER.UPDATE_ACTION_FIELD]
                for row in decisions.values()
            ),
            167,
        )
        self.assertEqual(BUILDER.EXPECTED_RENEWALS, 147)
        self.assertEqual(BUILDER.EXPECTED_OVERRIDES, 193)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PENDING, 7_101)

    def test_checkpoint_outputs_are_frozen_and_source_free(self) -> None:
        self.assertEqual(
            sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_OUTPUT_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_OUTPUT_SHA256,
        )
        report = json.loads(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(
            report["result"],
            {
                "semantic_review_approved": 52_803,
                "runtime_review_pending": 7_101,
                "fully_candidate_eligible": 45_702,
                "promoted_total": 29_233,
                "pk_msggame_promotion_count": 13_582,
                "private_integrated_decision_sha256":
                    BUILDER.EXPECTED_PRIVATE_OUTPUT_SHA256,
                "row_count": 52_803,
                "affected_row_count": 314,
                "unaffected_raw_line_copy_count": 52_489,
            },
        )
        raw = BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
        self.assertIsNone(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", raw))
        self.assertNotIn('"translation":', raw)
        self.assertNotRegex(raw, r'"\d+:\d+:\d+"')

    def test_historical_checkpoints_and_live_steam_are_unchanged(self) -> None:
        self.assertEqual(
            sha256_file(BUILDER.BASELINE_PRIVATE_PATH),
            BUILDER.EXPECTED_BASELINE_PRIVATE_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.BASELINE_PUBLIC_PATH),
            BUILDER.EXPECTED_BASELINE_PUBLIC_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.PREDECESSOR_PRIVATE_PATH),
            BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.PREDECESSOR_PUBLIC_PATH),
            BUILDER.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        )
        if BUILDER.LIVE_BASE_PATH.is_file():
            self.assertEqual(
                sha256_file(BUILDER.LIVE_BASE_PATH),
                BUILDER.EXPECTED_LIVE_BASE_SHA256,
            )
        if BUILDER.LIVE_PK_PATH.is_file():
            self.assertEqual(
                sha256_file(BUILDER.LIVE_PK_PATH),
                BUILDER.EXPECTED_LIVE_PK_SHA256,
            )

    def test_output_paths_cannot_escape_or_replace_predecessors(self) -> None:
        with self.assertRaises(BUILDER.DeltaCheckpointError):
            BUILDER.validate_output_paths(
                BUILDER.PREDECESSOR_PRIVATE_PATH,
                BUILDER.DEFAULT_PUBLIC_OUTPUT,
            )
        with self.assertRaises(BUILDER.DeltaCheckpointError):
            BUILDER.validate_output_paths(
                BUILDER.DEFAULT_PRIVATE_OUTPUT,
                BUILDER.PREDECESSOR_PUBLIC_PATH,
            )

    def test_deterministic_targeted_check(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
