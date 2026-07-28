#!/usr/bin/env python3
"""Minimal tests for the selector-1198 progress delta."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_progress_post_selector1198_consolidated_delta_v1.py"
)
spec = importlib.util.spec_from_file_location("selector1198_progress_tested", BUILDER_PATH)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector1198ProgressTest(unittest.TestCase):
    def test_frozen_delta(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        before = json.loads(
            BUILDER.DEFAULT_PREDECESSOR_PROGRESS.read_text("ascii")
        )
        after = json.loads(BUILDER.IMMUTABLE_PROGRESS_OUTPUT.read_text("ascii"))
        self.assertEqual(
            before["totals"]["runtime_review_pending"]
            - after["totals"]["runtime_review_pending"],
            25,
        )
        self.assertEqual(after["totals"]["runtime_review_pending"], 6464)
        self.assertEqual(after["totals"]["fully_candidate_eligible"], 46339)
        integration = after["runtime_vm_integration"]
        self.assertTrue(integration["selector1198_consolidated_layer_included"])
        self.assertEqual(integration["promoted_total"], 29870)
        self.assertFalse(
            integration["selector1198_targeted_progress_delta"][
                "full_dialogue_rebuild_performed"
            ]
        )


if __name__ == "__main__":
    unittest.main()
