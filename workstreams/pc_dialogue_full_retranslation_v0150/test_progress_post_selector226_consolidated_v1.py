#!/usr/bin/env python3
"""Scaffold tests for the selector-226 progress delta."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_progress_post_selector226_consolidated_delta_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector226_progress_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector226ProgressScaffoldTest(unittest.TestCase):
    def test_expected_delta_contract(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_ROWS, 52_803)
        self.assertEqual(BUILDER.EXPECTED_DECISIONS, 37)
        self.assertEqual(BUILDER.EXPECTED_PROMOTIONS, 37)
        self.assertEqual(BUILDER.EXPECTED_RENEWALS, 0)
        self.assertEqual(BUILDER.EXPECTED_OVERRIDES, 3)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PENDING, 6_246)
        self.assertEqual(BUILDER.EXPECTED_FINAL_ELIGIBLE, 46_557)
        self.assertEqual(BUILDER.EXPECTED_FINAL_RETRANSLATED, 46_212)
        self.assertEqual(BUILDER.EXPECTED_CONFIRMED_NON_DISPLAY, 345)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PROMOTED_TOTAL, 30_088)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PK_PROMOTIONS, 14_437)
        self.assertEqual(BUILDER.EXPECTED_TARGETED_AFFECTED_ROWS, 37)
        self.assertEqual(BUILDER.EXPECTED_UNAFFECTED_ROWS, 52_766)
        self.assertFalse(BUILDER.EXPECTED_FULL_DIALOGUE_REBUILD)

    def test_unresolved_scaffold_cannot_materialize(self) -> None:
        if not BUILDER.unresolved_checkpoint_pins():
            self.skipTest("checkpoint pins have been resolved")
        self.assertEqual(
            BUILDER.unresolved_checkpoint_pins(),
            BUILDER.CHECKPOINT_PIN_NAMES,
        )
        with self.assertRaisesRegex(RuntimeError, "unresolved checkpoint pins"):
            BUILDER.main(["--write"])

    def test_frozen_predecessor_inputs(self) -> None:
        self.assertEqual(
            BUILDER.BASE.sha256_file(BUILDER.BASE_BUILDER_PATH),
            BUILDER.EXPECTED_BASE_BUILDER_SHA256,
        )
        self.assertEqual(
            BUILDER.BASE.sha256_file(BUILDER.DEFAULT_PREDECESSOR_PROGRESS),
            BUILDER.EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        )

    def test_tracked_scaffold_is_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        for path in (BUILDER_PATH, SCRIPT):
            self.assertIsNone(cjk.search(path.read_text(encoding="utf-8")))

    @unittest.skipUnless(BUILDER.pins_resolved(), "final pins unresolved")
    def test_frozen_delta_after_materialization(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        before = json.loads(
            BUILDER.DEFAULT_PREDECESSOR_PROGRESS.read_text("ascii")
        )
        after = json.loads(BUILDER.IMMUTABLE_PROGRESS_OUTPUT.read_text("ascii"))
        self.assertEqual(before["totals"]["runtime_review_pending"], 6_283)
        self.assertEqual(after["totals"]["runtime_review_pending"], 6_246)
        self.assertEqual(after["totals"]["fully_candidate_eligible"], 46_557)
        self.assertEqual(
            after["totals"]["scope_classification_counts"]["retranslated"],
            46_212,
        )
        integration = after["runtime_vm_integration"]
        self.assertTrue(integration["selector226_consolidated_layer_included"])
        self.assertEqual(integration["promoted_total"], 30_088)
        delta = integration["selector226_targeted_progress_delta"]
        self.assertFalse(delta["full_dialogue_rebuild_performed"])

    @unittest.skipUnless(BUILDER.pins_resolved(), "final pins unresolved")
    def test_targeted_checkpoint_after_materialization(self) -> None:
        checkpoint = json.loads(BUILDER.CHECKPOINT_PUBLIC_PATH.read_text("ascii"))
        result = checkpoint["result"]
        validation = checkpoint["validation"]
        policy = checkpoint["distribution_policy"]
        self.assertEqual(result["pk_msggame_promotion_count"], 14_437)
        self.assertEqual(result["affected_row_count"], 37)
        self.assertEqual(result["unaffected_raw_line_copy_count"], 52_766)
        self.assertFalse(validation["full_integration_engine_invoked"])
        self.assertEqual(validation["targeted_affected_rows_rechecked"], 37)
        self.assertEqual(validation["unaffected_rows_byte_copied"], 52_766)
        self.assertTrue(validation["steam_archives_read_only"])
        self.assertFalse(
            policy["tracked_report_contains_commercial_source_text"]
        )
        self.assertFalse(
            policy["tracked_report_contains_translated_dialogue_text"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
