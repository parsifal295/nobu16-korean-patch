#!/usr/bin/env python3
"""Checks for the unfrozen selector-466 targeted-checkpoint scaffold."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_runtime_vm_post_selector466_consolidated_checkpoint_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector466_delta_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector466TargetedDeltaScaffoldTest(unittest.TestCase):
    def test_expected_targeted_delta_contract(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_ROWS, 52_803)
        self.assertEqual(BUILDER.EXPECTED_DECISIONS, 24)
        self.assertEqual(BUILDER.EXPECTED_PROMOTIONS, 24)
        self.assertEqual(BUILDER.EXPECTED_RENEWALS, 0)
        self.assertEqual(BUILDER.EXPECTED_OVERRIDES, 13)
        self.assertEqual(BUILDER.EXPECTED_UNAFFECTED_ROWS, 52_779)
        self.assertEqual(BUILDER.EXPECTED_PREDECESSOR_PENDING, 6_215)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PENDING, 6_191)
        self.assertEqual(BUILDER.EXPECTED_FINAL_ELIGIBLE, 46_612)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PROMOTED_TOTAL, 30_143)
        self.assertEqual(BUILDER.EXPECTED_FINAL_PK_PROMOTIONS, 14_492)
        self.assertEqual(
            BUILDER.EXPECTED_ACTION_COUNTS,
            {
                "runtime_promotion": 11,
                "translation_override_and_runtime_promotion": 13,
            },
        )
        self.assertEqual(BUILDER.EXPECTED_OWNER_CHUNK_COUNTS, {0: 3, 1: 21})

    def test_checkpoint_pins_are_frozen(self) -> None:
        self.assertTrue(BUILDER.is_frozen())
        self.assertEqual(BUILDER.unresolved_pins(), [])
        self.assertEqual(BUILDER.blocking_pins(), [])

    def test_predecessor_inputs_are_frozen(self) -> None:
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

    def test_frozen_checkpoint_after_materialization(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        report = json.loads(BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text("ascii"))
        result = report["result"]
        selector = report["selector466_consolidated"]
        self.assertEqual(result["affected_row_count"], 24)
        self.assertEqual(result["unaffected_raw_line_copy_count"], 52_779)
        self.assertEqual(result["runtime_review_pending"], 6_191)
        self.assertEqual(result["fully_candidate_eligible"], 46_612)
        self.assertEqual(selector["promotion_count"], 24)
        self.assertEqual(selector["semantic_override_count"], 13)
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

    def test_tracked_scaffold_is_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r'["\']\d+:\d+(?::\d+){0,2}["\']')
        for path in (BUILDER_PATH, SCRIPT, BUILDER.DEFAULT_PUBLIC_OUTPUT):
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(content), path)
            self.assertIsNone(coordinate.search(content), path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
