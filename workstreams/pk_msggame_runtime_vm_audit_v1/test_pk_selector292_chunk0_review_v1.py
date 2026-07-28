#!/usr/bin/env python3
"""Targeted checks for the frozen selector-292 chunk-0 review."""

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
    "build_pk_selector292_chunk0_review_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector292_chunk0_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector292Chunk0ReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = BUILDER.build_output()
        cls.report = json.loads(cls.content.decode("utf-8"))
        cls.decisions = BUILDER.load_jsonl(
            BUILDER.PRIVATE_DECISIONS_PATH
        )
        cls.evidence = BUILDER.load_json(BUILDER.PRIVATE_EVIDENCE_PATH)

    def test_exact_partition_and_actions(self) -> None:
        self.assertEqual(
            self.report["result"], BUILDER.EXPECTED_COUNTS
        )
        self.assertEqual(
            Counter(row["action"] for row in self.decisions),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            (
                self.report["result"]["accepted_pending_rows"],
                self.report["result"]["blocked_pending_rows"],
                self.report["result"]["promoted_pending_rows"],
                self.report["result"]["shared_override_rows"],
            ),
            (11, 2, 11, 1),
        )

    def test_targeted_branch_gate(self) -> None:
        rows = self.evidence["assembly_manifest"]
        passing = [
            row
            for row in rows
            if row["grammar_pass"]
            and row["current_relative_nonexpanding"]
            and row["topology_pass"]
        ]
        self.assertEqual((len(rows), len(passing)), (28, 21))
        self.assertEqual(
            self.report["result"]["full_layout_recomputed_branches"], 0
        )
        self.assertEqual(
            self.report["result"]["ordinary_verified_branches"], 21
        )

    def test_semantic_and_protected_scope(self) -> None:
        proof = self.report["proof"]
        self.assertTrue(proof["historical_factuality_reviewed"])
        self.assertTrue(
            proof["jp_authoritative_other_languages_advisory"]
        )
        self.assertTrue(proof["speaker_register_reviewed"])
        self.assertTrue(proof["nonpending_roots_read_only"])
        self.assertTrue(proof["prior_and_owned_evidence_read_only"])
        self.assertTrue(proof["terminal_rows_read_only"])
        self.assertTrue(proof["source_only_action_count_zero"])
        self.assertEqual(
            (
                self.report["result"]["terminal_read_only_rows"],
                self.report["result"]["terminal_decision_rows"],
                self.report["result"]["source_only_actions"],
            ),
            (7, 0, 0),
        )

    def test_reverse_overlay_and_steam_guards(self) -> None:
        guards = self.report["guards"]
        self.assertEqual(
            guards["reverse_overlay_sha256"],
            guards["official_candidate_sha256"],
        )
        self.assertEqual(
            guards["reviewed_candidate_sha256"],
            BUILDER.EXPECTED_SHA256["reviewed_candidate"],
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
