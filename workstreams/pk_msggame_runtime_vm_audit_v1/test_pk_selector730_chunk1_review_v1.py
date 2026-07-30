#!/usr/bin/env python3
"""Targeted checks for the frozen selector-730 chunk-1 review."""

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
    "build_pk_selector730_chunk1_review_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector730_chunk1_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector730Chunk1ReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = BUILDER.build_output()
        cls.report = json.loads(cls.content.decode("ascii"))
        cls.evidence = BUILDER.load_json(BUILDER.PRIVATE_EVIDENCE_PATH)
        cls.decisions = BUILDER.load_jsonl(BUILDER.PRIVATE_DECISIONS_PATH)

    def test_exact_partition(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["accepted_pending_rows"],
                result["blocked_pending_rows"],
                result["decision_rows"],
                result["translation_overrides"],
                result["same_gap_pending_branches_reused"],
                result["same_gap_total_branches_reused"],
            ),
            (3, 22, 3, 1, 441, 882),
        )
        self.assertEqual(
            Counter(row["action"] for row in self.decisions),
            Counter({
                "runtime_promotion": 2,
                "translation_override_and_runtime_promotion": 1,
            }),
        )

    def test_decision_metadata(self) -> None:
        for row in self.decisions:
            self.assertEqual(row["resource"], "pk_msggame")
            self.assertEqual(
                row["layout_review"],
                "current_relative_raw_g1n_nonexpanding",
            )
            self.assertEqual(row["root_rewrite_attempt_count"], 1)
            self.assertEqual(row["runtime_review"], "verified")
        BUILDER.validate_decisions(self.decisions, self.evidence)

    def test_cartesian_reuse_and_terminal_guard(self) -> None:
        proof = self.report["proof"]
        self.assertEqual(proof["cartesian_branches_recomputed"], 0)
        self.assertTrue(proof["shared_cartesian_manifest_reused"])
        self.assertTrue(proof["same_gap_roots_blocked_atomically"])
        self.assertTrue(proof["terminal_rows_pending_read_only"])
        self.assertEqual(self.report["result"]["source_only_actions"], 0)

    def test_frozen_output_and_source_free(self) -> None:
        self.assertEqual(
            BUILDER.sha256_bytes(self.content),
            BUILDER.EXPECTED_PUBLIC_SHA256,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            self.content,
        )
        decoded = self.content.decode("ascii")
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
                r"\uf900-\ufaff]",
                decoded,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+){0,2}\b", decoded))
        self.assertFalse(self.report["steam_write_performed"])

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
