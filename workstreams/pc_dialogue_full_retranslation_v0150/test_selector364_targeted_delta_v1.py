#!/usr/bin/env python3
"""Immutable targeted-checkpoint checks for selector 364."""

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
    "build_runtime_vm_post_selector364_consolidated_checkpoint_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector364_delta_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector364TargetedDeltaTest(unittest.TestCase):
    def report(self) -> dict:
        return json.loads(BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text("ascii"))

    def test_written_checkpoint_and_reverse_overlay(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        report = self.report()
        self.assertEqual(report["result"]["row_count"], 52_803)
        self.assertEqual(report["result"]["affected_row_count"], 5)
        self.assertEqual(
            report["result"]["unaffected_raw_line_copy_count"], 52_798
        )
        self.assertEqual(report["result"]["runtime_review_pending"], 6_302)
        self.assertEqual(report["result"]["fully_candidate_eligible"], 46_501)
        self.assertEqual(
            report["selector364_consolidated"]["promotion_count"], 5
        )
        self.assertEqual(
            report["selector364_consolidated"]["semantic_override_count"], 2
        )
        self.assertEqual(
            report["selector364_consolidated"]["reverse_overlay_sha256"],
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

    def test_tracked_outputs_are_source_free(self) -> None:
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
    unittest.main()
