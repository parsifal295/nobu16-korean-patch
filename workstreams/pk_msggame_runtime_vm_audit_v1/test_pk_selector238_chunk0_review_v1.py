#!/usr/bin/env python3
"""Targeted checks for the frozen selector-238 chunk-0 review."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_pk_selector238_chunk0_review_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector238_chunk0_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector238Chunk0ReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = BUILDER.build_output()
        cls.report = json.loads(cls.content.decode("utf-8"))
        cls.decisions = BUILDER.load_jsonl(BUILDER.PRIVATE_DECISIONS_PATH)

    def test_exact_partition(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["accepted_pending_rows"],
                result["blocked_pending_rows"],
                result["decision_rows"],
                result["translation_overrides"],
                result["promoted_pending_rows"],
                result["rewrite_attempt_roots"],
            ),
            (11, 3, 11, 10, 11, 4),
        )
        self.assertEqual(
            Counter(row["action"] for row in self.decisions),
            Counter({
                "runtime_promotion": 1,
                "translation_override_and_runtime_promotion": 10,
            }),
        )

    def test_branch_proof(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["conservative_assembly_branches"],
                result["selector238_total_branches"],
                result["selector238_accepted_branches"],
                result["selector238_blocked_pending_branches"],
                result["selector238_read_only_nonpending_branches"],
            ),
            (170469, 98, 28, 21, 49),
        )
        proof = self.report["proof"]
        self.assertTrue(
            proof["conservative_runtime_assembly_superset_nonexpanding"]
        )
        self.assertTrue(proof["current_relative_raw_g1n_gate_applied"])

    def test_protected_rows_and_no_automatic_promotion(self) -> None:
        proof = self.report["proof"]
        self.assertTrue(proof["terminal_rows_pending_read_only"])
        self.assertTrue(proof["automatic_promotion_count_zero"])
        self.assertTrue(proof["source_only_action_count_zero"])
        self.assertEqual(self.report["result"]["non_display_actions"], 0)

    def test_reverse_overlay_and_steam_guards(self) -> None:
        guards = self.report["guards"]
        self.assertEqual(
            guards["reverse_overlay_sha256"],
            guards["official_candidate_sha256"],
        )
        self.assertFalse(self.report["steam_write_performed"])

    def test_frozen_output_and_source_free(self) -> None:
        self.assertEqual(
            BUILDER.sha256_bytes(self.content),
            BUILDER.EXPECTED_PUBLIC_SHA256,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes(), self.content
        )
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r"\b\d+:\d+(?::\d+){0,2}\b")
        for path in (
            BUILDER_PATH,
            SCRIPT,
            BUILDER.DEFAULT_PUBLIC_OUTPUT,
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(text))
            self.assertIsNone(coordinate.search(text))

    def test_determinism_and_tamper_rejection(self) -> None:
        self.assertEqual(BUILDER.build_output(), self.content)
        original = BUILDER.EXPECTED_SHA256["private_decisions"]
        try:
            BUILDER.EXPECTED_SHA256["private_decisions"] = "0" * 64
            with self.assertRaises(BUILDER.ReviewError):
                BUILDER.build_output()
        finally:
            BUILDER.EXPECTED_SHA256["private_decisions"] = original


if __name__ == "__main__":
    unittest.main()
