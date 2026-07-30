#!/usr/bin/env python3
"""Scaffold and frozen checks for the selector-1168 targeted checkpoint."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_runtime_vm_post_selector1168_consolidated_checkpoint_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector1168_delta_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector1168TargetedDeltaContractTest(unittest.TestCase):
    def test_checkpoint_pins_are_frozen(self) -> None:
        self.assertTrue(BUILDER.is_frozen())
        self.assertEqual(BUILDER.unresolved_pins(), [])

    def test_predecessor_checkpoint_is_exact(self) -> None:
        self.assertEqual(
            BUILDER.BASE.sha256_file(BUILDER.PREDECESSOR_BUILDER_PATH),
            BUILDER.EXPECTED_PREDECESSOR_BUILDER_SHA256,
        )
        self.assertEqual(
            BUILDER.BASE.sha256_file(BUILDER.PREDECESSOR_PRIVATE_PATH),
            BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )
        self.assertEqual(
            BUILDER.BASE.sha256_file(BUILDER.PREDECESSOR_PUBLIC_PATH),
            BUILDER.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        )

    def test_targeted_delta_contract_is_frozen(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_ROWS, 52_803)
        self.assertEqual(BUILDER.EXPECTED_DECISIONS, 19)
        self.assertEqual(BUILDER.EXPECTED_OWNER_ROWS, 19)
        self.assertEqual(BUILDER.EXPECTED_PROMOTIONS, 19)
        self.assertEqual(BUILDER.EXPECTED_RENEWALS, 0)
        self.assertEqual(BUILDER.EXPECTED_OVERRIDES, 5)
        self.assertEqual(BUILDER.EXPECTED_UNAFFECTED_ROWS, 52_784)
        self.assertEqual(BUILDER.EXPECTED_PREDECESSOR_PENDING, 6_302)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PENDING, 6_283)
        self.assertEqual(
            BUILDER.EXPECTED_ACTION_COUNTS,
            {
                "runtime_promotion": 14,
                "translation_override_and_runtime_promotion": 5,
            },
        )

    def test_tracked_scaffold_is_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r'["\']\d+:\d+(?::\d+){0,2}["\']')
        for path in (BUILDER_PATH, SCRIPT):
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(content), path)
            self.assertIsNone(coordinate.search(content), path)


@unittest.skipUnless(
    BUILDER.is_frozen(), "selector1168 final closure pins are not frozen"
)
class Selector1168TargetedDeltaFrozenTest(unittest.TestCase):
    def report(self) -> dict:
        return json.loads(BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text("ascii"))

    def test_written_checkpoint_and_reverse_overlay(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        report = self.report()
        self.assertEqual(report["result"]["row_count"], 52_803)
        self.assertEqual(report["result"]["affected_row_count"], 19)
        self.assertEqual(
            report["result"]["unaffected_raw_line_copy_count"], 52_784
        )
        self.assertEqual(report["result"]["runtime_review_pending"], 6_283)
        self.assertEqual(report["result"]["fully_candidate_eligible"], 46_520)
        selector = report["selector1168_consolidated"]
        self.assertEqual(selector["promotion_count"], 19)
        self.assertEqual(selector["semantic_override_count"], 5)
        self.assertEqual(
            selector["reverse_overlay_sha256"],
            BUILDER.EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
        )
        self.assertFalse(report["validation"]["full_integration_engine_invoked"])
        self.assertFalse(report["steam_write_performed"])

    def test_check_is_deterministic(self) -> None:
        before = (
            BUILDER.BASE.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.BASE.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
        )
        self.assertEqual(BUILDER.main(["--check"]), 0)
        self.assertEqual(BUILDER.main(["--check"]), 0)
        after = (
            BUILDER.BASE.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.BASE.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
        )
        self.assertEqual(before, after)

    def test_predecessor_tamper_is_rejected(self) -> None:
        original = BUILDER.PREDECESSOR_PRIVATE_PATH
        raw = original.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "predecessor.jsonl"
            tampered.write_bytes(raw[:-1] + b" \n")
            BUILDER.PREDECESSOR_PRIVATE_PATH = tampered
            try:
                with self.assertRaises(BUILDER.BASE.DeltaCheckpointError):
                    BUILDER.main(["--check"])
            finally:
                BUILDER.PREDECESSOR_PRIVATE_PATH = original

    def test_closure_decision_tamper_is_rejected(self) -> None:
        original = BUILDER.CLOSURE_DECISIONS_PATH
        raw = original.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "decisions.jsonl"
            tampered.write_bytes(raw[:-1] + b" \n")
            BUILDER.CLOSURE_DECISIONS_PATH = tampered
            try:
                with self.assertRaises(BUILDER.BASE.DeltaCheckpointError):
                    BUILDER.main(["--check"])
            finally:
                BUILDER.CLOSURE_DECISIONS_PATH = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
