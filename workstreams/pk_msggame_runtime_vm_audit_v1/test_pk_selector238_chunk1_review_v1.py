#!/usr/bin/env python3
"""Targeted checks for the frozen selector-238 chunk-1 review."""

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
    "build_pk_selector238_chunk1_review_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector238_chunk1_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector238Chunk1ReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = BUILDER.build_output()
        cls.report = json.loads(cls.content.decode("utf-8"))
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
                result["promoted_pending_rows"],
                result["rewrite_attempt_roots"],
            ),
            (16, 6, 16, 12, 16, 5),
        )
        self.assertEqual(
            Counter(row["action"] for row in self.decisions),
            Counter({
                "runtime_promotion": 4,
                "translation_override_and_runtime_promotion": 12,
            }),
        )

    def test_branch_and_downstream_proofs(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["selector238_total_branches"],
                result["selector238_accepted_branches"],
                result["selector238_blocked_pending_branches"],
                result["selector238_read_only_nonpending_branches"],
                result["selector238_all_current_relative_pass_branches"],
                result["downstream_cartesian_branches"],
            ),
            (91, 35, 21, 35, 70, 49),
        )
        proof = self.report["proof"]
        self.assertTrue(
            proof[
                "accepted_assemblies_current_relative_raw_g1n_nonexpanding"
            ]
        )
        self.assertTrue(proof["selector_branches_computed_once"])
        self.assertTrue(
            proof["downstream_cartesian_branches_computed_once"]
        )

    def test_terminal_and_automatic_promotion_guards(self) -> None:
        proof = self.report["proof"]
        self.assertTrue(proof["terminal_rows_pending_read_only"])
        self.assertEqual(proof["terminal_automatic_promotion_count"], 0)
        self.assertEqual(
            proof["owned_overlap_automatic_promotion_count"], 0
        )
        self.assertEqual(
            proof["prior_pending_evidence_automatic_promotion_count"], 0
        )
        self.assertEqual(proof["source_only_action_count"], 0)
        self.assertEqual(proof["non_display_action_count"], 0)

    def test_reverse_overlay_and_steam_guards(self) -> None:
        guards = self.report["guards"]
        self.assertEqual(
            guards["reverse_overlay_sha256"],
            guards["official_candidate_sha256"],
        )
        self.assertEqual(
            guards["steam_archive_sha256_before"],
            guards["steam_archive_sha256_after"],
        )
        self.assertFalse(self.report["steam_write_performed"])

    def test_frozen_output_and_source_free(self) -> None:
        self.assertEqual(
            BUILDER.sha256_bytes(self.content),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
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
