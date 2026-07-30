#!/usr/bin/env python3
"""Minimal tests for the selector-760 progress delta."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_progress_post_selector760_consolidated_delta_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector760_progress_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector760ProgressTest(unittest.TestCase):
    def test_frozen_delta(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        before = json.loads(
            BUILDER.DEFAULT_PREDECESSOR_PROGRESS.read_text("ascii")
        )
        after = json.loads(BUILDER.IMMUTABLE_PROGRESS_OUTPUT.read_text("ascii"))
        before_totals = before["totals"]
        after_totals = after["totals"]
        self.assertEqual(
            before_totals["runtime_review_pending"]
            - after_totals["runtime_review_pending"],
            27,
        )
        self.assertEqual(after_totals["runtime_review_pending"], 6341)
        self.assertEqual(after_totals["fully_candidate_eligible"], 46462)
        self.assertEqual(
            after_totals["scope_classification_counts"]["retranslated"],
            46117,
        )
        self.assertEqual(
            after_totals["scope_classification_counts"]["retranslated"],
            before_totals["scope_classification_counts"]["retranslated"] + 27,
        )
        integration = after["runtime_vm_integration"]
        self.assertTrue(integration["selector760_consolidated_layer_included"])
        self.assertEqual(integration["promoted_total"], 29993)
        self.assertFalse(
            integration["selector760_targeted_progress_delta"][
                "full_dialogue_rebuild_performed"
            ]
        )

    def test_targeted_checkpoint_and_source_free_guards(self) -> None:
        checkpoint = json.loads(
            BUILDER.CHECKPOINT_PUBLIC_PATH.read_text("ascii")
        )
        validation = checkpoint["validation"]
        policy = checkpoint["distribution_policy"]
        self.assertFalse(validation["full_integration_engine_invoked"])
        self.assertEqual(validation["targeted_affected_rows_rechecked"], 30)
        self.assertEqual(validation["unaffected_rows_byte_copied"], 52773)
        self.assertTrue(validation["steam_archives_read_only"])
        self.assertFalse(
            policy["tracked_report_contains_commercial_source_text"]
        )
        self.assertFalse(
            policy["tracked_report_contains_translated_dialogue_text"]
        )
        self.assertNotIn(
            "\\u",
            BUILDER.IMMUTABLE_PROGRESS_OUTPUT.read_text("ascii").lower(),
        )


if __name__ == "__main__":
    unittest.main()
