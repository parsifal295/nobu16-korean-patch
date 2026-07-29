#!/usr/bin/env python3
"""Bootstrap checks for the post-selector292 wave1 targeted checkpoint."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_runtime_vm_post_selector292_wave1_consolidated_checkpoint_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "post292_wave1_checkpoint_tested", BUILDER_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {BUILDER_PATH}")
B = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = B
SPEC.loader.exec_module(B)


class PostSelector292Wave1CheckpointTests(unittest.TestCase):
    def test_predecessor_is_the_frozen_selector292_checkpoint(self) -> None:
        self.assertEqual(
            B.BASE.sha256_file(B.PREDECESSOR_BUILDER_PATH),
            B.EXPECTED_PREDECESSOR_BUILDER_SHA256,
        )
        self.assertEqual(
            B.BASE.sha256_file(B.PREDECESSOR_PRIVATE_PATH),
            B.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )
        self.assertEqual(
            B.BASE.sha256_file(B.PREDECESSOR_PUBLIC_PATH),
            B.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        )
        self.assertEqual(B.EXPECTED_PREDECESSOR_PENDING, 6_130)
        self.assertEqual(B.EXPECTED_PREDECESSOR_ELIGIBLE, 46_673)
        self.assertEqual(B.EXPECTED_PREDECESSOR_PK_PROMOTIONS, 14_553)
        self.assertEqual(B.EXPECTED_PREDECESSOR_PROMOTED_TOTAL, 30_204)

    def test_wave_closure_paths_are_reserved(self) -> None:
        self.assertEqual(
            B.CLOSURE_BUILDER_PATH.name,
            "build_pk_dialogue_wave_post_selector292_consolidated_closure_v1.py",
        )
        self.assertEqual(
            B.CLOSURE_DECISIONS_PATH.name,
            "pk_dialogue_wave_post_selector292_consolidated_closure_"
            "decisions.private.v1.jsonl",
        )
        self.assertEqual(
            B.CLOSURE_EVIDENCE_PATH.name,
            "pk_dialogue_wave_post_selector292_consolidated_closure_"
            "evidence.private.v1.json",
        )
        self.assertEqual(
            B.CLOSURE_COVERAGE_PATH.name,
            "pk_dialogue_wave_post_selector292_consolidated_closure_"
            "coverage.v1.json",
        )
        self.assertEqual(
            B.CLOSURE_PROMOTION_PATH.name,
            "pk_dialogue_wave_post_selector292_consolidated_closure_"
            "promotion.v1.json",
        )

    def test_frozen_wave_contract(self) -> None:
        self.assertTrue(B.is_frozen())
        self.assertFalse(B.unresolved_pins())
        self.assertEqual(B.EXPECTED_DECISIONS, 46)
        self.assertEqual(B.EXPECTED_PROMOTIONS, 46)
        self.assertEqual(B.EXPECTED_RENEWALS, 0)
        self.assertEqual(B.EXPECTED_OVERRIDES, 29)
        self.assertEqual(
            B.EXPECTED_ACTION_COUNTS,
            {
                "runtime_promotion": 17,
                "translation_override_and_runtime_promotion": 29,
            },
        )
        self.assertEqual(
            B.EXPECTED_OWNER_CHUNK_COUNTS,
            {0: 21, 1: 16, 2: 9},
        )
        self.assertEqual(B.EXPECTED_FINAL_PENDING, 6_084)
        self.assertEqual(B.EXPECTED_FINAL_ELIGIBLE, 46_719)
        self.assertEqual(B.EXPECTED_FINAL_PK_PROMOTIONS, 14_599)
        self.assertEqual(B.EXPECTED_FINAL_PROMOTED_TOTAL, 30_250)
        self.assertEqual(B.EXPECTED_UNAFFECTED_ROWS, 52_757)

    def test_pin_loss_refuses_all_writes(self) -> None:
        private_before = (
            B.DEFAULT_PRIVATE_OUTPUT.read_bytes()
            if B.DEFAULT_PRIVATE_OUTPUT.is_file()
            else None
        )
        public_before = (
            B.DEFAULT_PUBLIC_OUTPUT.read_bytes()
            if B.DEFAULT_PUBLIC_OUTPUT.is_file()
            else None
        )
        original = B.EXPECTED_CLOSURE_EVIDENCE_SHA256
        try:
            B.EXPECTED_CLOSURE_EVIDENCE_SHA256 = None
            with self.assertRaisesRegex(
                Exception,
                "wave1 targeted checkpoint input pins unresolved",
            ):
                B.main(["--write", "--bootstrap-output-pins"])
        finally:
            B.EXPECTED_CLOSURE_EVIDENCE_SHA256 = original
        self.assertEqual(
            (
                B.DEFAULT_PRIVATE_OUTPUT.read_bytes()
                if B.DEFAULT_PRIVATE_OUTPUT.is_file()
                else None
            ),
            private_before,
        )
        self.assertEqual(
            (
                B.DEFAULT_PUBLIC_OUTPUT.read_bytes()
                if B.DEFAULT_PUBLIC_OUTPUT.is_file()
                else None
            ),
            public_before,
        )

    def test_legacy_runtime_integration_alias_is_forbidden(self) -> None:
        protected = B.WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
        before = protected.read_bytes() if protected.is_file() else None
        self.assertNotIn(
            '"runtime_vm_integration.source_free.v1.json"',
            BUILDER_PATH.read_text(encoding="utf-8"),
        )
        self.assertEqual(B.main(["--check"]), 0)
        self.assertEqual(
            protected.read_bytes() if protected.is_file() else None,
            before,
        )

    def test_frozen_targeted_checkpoint(self) -> None:
        self.assertEqual(B.main(["--check"]), 0)
        checkpoint = json.loads(B.DEFAULT_PUBLIC_OUTPUT.read_text("ascii"))
        result = checkpoint["result"]
        validation = checkpoint["validation"]
        policy = checkpoint["distribution_policy"]
        layer = checkpoint[
            "dialogue_wave_post_selector292_consolidated"
        ]
        self.assertEqual(result["affected_row_count"], 46)
        self.assertEqual(result["unaffected_raw_line_copy_count"], 52_757)
        self.assertEqual(result["runtime_review_pending"], 6_084)
        self.assertEqual(result["fully_candidate_eligible"], 46_719)
        self.assertEqual(result["pk_msggame_promotion_count"], 14_599)
        self.assertEqual(result["promoted_total"], 30_250)
        self.assertEqual(layer["promotion_count"], 46)
        self.assertEqual(layer["verification_renewal_count"], 0)
        self.assertEqual(layer["semantic_override_count"], 29)
        self.assertFalse(validation["full_integration_engine_invoked"])
        self.assertEqual(validation["targeted_affected_rows_rechecked"], 46)
        self.assertEqual(validation["unaffected_rows_byte_copied"], 52_757)
        self.assertTrue(validation["steam_archives_read_only"])
        self.assertFalse(
            policy["tracked_report_contains_commercial_source_text"]
        )
        self.assertFalse(
            policy["tracked_report_contains_translated_dialogue_text"]
        )

    def test_targeted_outputs_are_named_and_no_steam_path_exists(self) -> None:
        self.assertIn(
            "post_selector292_wave1_consolidated_checkpoint",
            B.DEFAULT_PRIVATE_OUTPUT.name,
        )
        self.assertIn(
            "post_selector292_wave1_consolidated_checkpoint",
            B.DEFAULT_PUBLIC_OUTPUT.name,
        )
        self.assertFalse(hasattr(B, "DEFAULT_STEAM_ROOT"))


if __name__ == "__main__":
    unittest.main()
