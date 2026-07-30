#!/usr/bin/env python3
"""Scaffold tests for the selector-562 progress delta."""

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
    "build_progress_post_selector562_consolidated_delta_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector562_progress_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector562ProgressScaffoldTest(unittest.TestCase):
    def test_expected_delta_contract(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_ROWS, 52_803)
        self.assertEqual(BUILDER.EXPECTED_DECISIONS, 10)
        self.assertEqual(BUILDER.EXPECTED_PROMOTIONS, 10)
        self.assertEqual(BUILDER.EXPECTED_RENEWALS, 0)
        self.assertEqual(BUILDER.EXPECTED_OVERRIDES, 7)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PENDING, 6_181)
        self.assertEqual(BUILDER.EXPECTED_FINAL_ELIGIBLE, 46_622)
        self.assertEqual(BUILDER.EXPECTED_FINAL_RETRANSLATED, 46_277)
        self.assertEqual(BUILDER.EXPECTED_CONFIRMED_NON_DISPLAY, 345)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PROMOTED_TOTAL, 30_153)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PK_PROMOTIONS, 14_502)
        self.assertEqual(BUILDER.EXPECTED_TARGETED_AFFECTED_ROWS, 10)
        self.assertEqual(BUILDER.EXPECTED_UNAFFECTED_ROWS, 52_793)
        self.assertFalse(BUILDER.EXPECTED_FULL_DIALOGUE_REBUILD)

    def test_checkpoint_and_output_pins_are_frozen(self) -> None:
        self.assertFalse(BUILDER.unresolved_checkpoint_pins())
        self.assertTrue(BUILDER.pins_resolved())
        self.assertEqual(
            BUILDER.EXPECTED_CLOSURE_DECISIONS_SHA256,
            "51CA681BCE819F41B1D7B69BE6AD906BFCD519BC463BF8EEBAA08DACA5C5BD26",
        )
        self.assertEqual(
            BUILDER.EXPECTED_FINAL_CANDIDATE_SHA256,
            "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815",
        )
        self.assertEqual(
            BUILDER.EXPECTED_PROGRESS_OUTPUT_SHA256,
            "A21048F29A17FF7FF17149E55913ACC15F36F0C9CC7BB16CD24231F83088111F",
        )

    def test_pin_loss_cannot_materialize(self) -> None:
        alias_before = BUILDER.DEFAULT_PROGRESS_OUTPUT.read_bytes()
        immutable_before = BUILDER.IMMUTABLE_PROGRESS_OUTPUT.read_bytes()
        original = BUILDER.EXPECTED_CHECKPOINT_PRIVATE_SHA256
        try:
            BUILDER.EXPECTED_CHECKPOINT_PRIVATE_SHA256 = None
            with self.assertRaisesRegex(
                RuntimeError, "unresolved checkpoint pins"
            ):
                BUILDER.main(["--write"])
        finally:
            BUILDER.EXPECTED_CHECKPOINT_PRIVATE_SHA256 = original
        self.assertEqual(BUILDER.DEFAULT_PROGRESS_OUTPUT.read_bytes(), alias_before)
        self.assertEqual(
            BUILDER.IMMUTABLE_PROGRESS_OUTPUT.read_bytes(),
            immutable_before,
        )

    def test_frozen_predecessor_inputs(self) -> None:
        self.assertEqual(
            BUILDER.BASE.sha256_file(BUILDER.BASE_BUILDER_PATH),
            BUILDER.EXPECTED_BASE_BUILDER_SHA256,
        )
        self.assertEqual(
            BUILDER.BASE.sha256_file(BUILDER.DEFAULT_PREDECESSOR_PROGRESS),
            BUILDER.EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        )
        self.assertEqual(
            BUILDER.BASE.sha256_file(
                BUILDER.PREVIOUS.CHECKPOINT_PRIVATE_PATH
            ),
            BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )
        self.assertEqual(
            BUILDER.BASE.sha256_file(
                BUILDER.PREVIOUS.CHECKPOINT_PUBLIC_PATH
            ),
            BUILDER.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        )

    def test_predecessor_progress_contract(self) -> None:
        progress = json.loads(
            BUILDER.DEFAULT_PREDECESSOR_PROGRESS.read_text("ascii")
        )
        BUILDER.validate_baseline_progress(progress)

    def test_frozen_delta_after_materialization(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        before = json.loads(
            BUILDER.DEFAULT_PREDECESSOR_PROGRESS.read_text("ascii")
        )
        after = json.loads(
            BUILDER.IMMUTABLE_PROGRESS_OUTPUT.read_text("ascii")
        )
        self.assertEqual(before["totals"]["runtime_review_pending"], 6_191)
        self.assertEqual(after["totals"]["runtime_review_pending"], 6_181)
        self.assertEqual(after["totals"]["fully_candidate_eligible"], 46_622)
        self.assertEqual(
            after["totals"]["scope_classification_counts"]["retranslated"],
            46_277,
        )
        integration = after["runtime_vm_integration"]
        self.assertTrue(integration["selector562_consolidated_layer_included"])
        self.assertEqual(integration["promoted_total"], 30_153)
        delta = integration["selector562_targeted_progress_delta"]
        self.assertFalse(delta["full_dialogue_rebuild_performed"])

    def test_targeted_checkpoint_after_materialization(self) -> None:
        checkpoint = json.loads(
            BUILDER.CHECKPOINT_PUBLIC_PATH.read_text("ascii")
        )
        result = checkpoint["result"]
        validation = checkpoint["validation"]
        policy = checkpoint["distribution_policy"]
        self.assertEqual(result["pk_msggame_promotion_count"], 14_502)
        self.assertEqual(result["affected_row_count"], 10)
        self.assertEqual(result["unaffected_raw_line_copy_count"], 52_793)
        self.assertFalse(validation["full_integration_engine_invoked"])
        self.assertEqual(validation["targeted_affected_rows_rechecked"], 10)
        self.assertEqual(validation["unaffected_rows_byte_copied"], 52_793)
        self.assertTrue(validation["steam_archives_read_only"])
        self.assertFalse(
            policy["tracked_report_contains_commercial_source_text"]
        )
        self.assertFalse(
            policy["tracked_report_contains_translated_dialogue_text"]
        )

    def test_outputs_are_progress_only(self) -> None:
        self.assertEqual(
            BUILDER.DEFAULT_PROGRESS_OUTPUT.name,
            "progress.source_free.v1.json",
        )
        self.assertEqual(
            BUILDER.IMMUTABLE_PROGRESS_OUTPUT.name,
            "progress.post_selector562_consolidated.source_free.v1.json",
        )
        self.assertNotIn(
            "runtime_vm_integration.source_free.v1.json",
            {
                str(BUILDER.DEFAULT_PROGRESS_OUTPUT),
                str(BUILDER.IMMUTABLE_PROGRESS_OUTPUT),
            },
        )

    def test_tracked_scaffold_is_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        for path in (BUILDER_PATH, SCRIPT):
            self.assertIsNone(cjk.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
