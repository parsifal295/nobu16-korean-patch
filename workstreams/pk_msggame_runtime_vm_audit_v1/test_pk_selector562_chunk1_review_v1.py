#!/usr/bin/env python3
"""Focused regressions for the selector-562 chunk-1 checkpoint."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_pk_selector562_chunk1_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector562_chunk1_review_tested", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector562Chunk1ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = B.build_report()

    def test_builder_check(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILDER_PATH), "--check"],
            cwd=B.REPO, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(
            (payload["accepted_pending"], payload["blocked_pending"]),
            (5, 20),
        )
        self.assertFalse(payload["steam_write_performed"])

    def test_exact_partition(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (result["sites"], result["accepted_sites"], result["blocked_sites"]),
            (26, 3, 23),
        )
        self.assertEqual(
            (result["promoted_pending_rows"], result["blocked_pending_rows"]),
            (5, 20),
        )
        self.assertEqual(
            (result["translation_overrides"], result["rewrite_attempt_roots"]),
            (3, 5),
        )

    def test_nominal_copula_and_cross_selector_guards(self) -> None:
        proof = self.report["proof"]
        self.assertTrue(proof["all_seven_nominal_copula_ordinals_reviewed"])
        self.assertEqual(proof["cross_selector754_branches_reviewed"], 7)
        self.assertEqual(proof["same_gap_branch_count"], 0)
        self.assertEqual(
            proof["terminal_register_counts"],
            {"archaic": 3, "formal": 2, "plain": 2},
        )

    def test_prior_and_terminal_evidence_are_not_automatic(self) -> None:
        proof = self.report["proof"]
        self.assertEqual(
            proof["prior_pending_evidence_automatic_promotion_count"], 0
        )
        self.assertEqual(proof["owned_overlap_automatic_promotion_count"], 0)
        self.assertFalse(proof["context_terminals_authoritative"])
        self.assertFalse(proof["shared_terminal_modified"])
        self.assertEqual(proof["verification_renewal_rows"], 0)

    def test_decision_actions(self) -> None:
        rows = B.load_decisions()
        self.assertEqual(len(rows), 5)
        self.assertEqual(
            Counter(row["action"] for row in rows),
            Counter(B.EXPECTED_ACTION_COUNTS),
        )

    def test_runtime_and_reverse_proofs(self) -> None:
        proof, guards = self.report["proof"], self.report["guards"]
        self.assertTrue(
            proof["accepted_assemblies_current_relative_raw_g1n_nonexpanding"]
        )
        self.assertTrue(proof["reverse_overlay_recovers_official_candidate"])
        self.assertEqual(
            guards["steam_archive_sha256_before"],
            guards["steam_archive_sha256_after"],
        )

    def test_tracked_artifacts_are_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r'["\']\d+:\d+(?::\d+){0,2}["\']')
        for path in (BUILDER_PATH, SCRIPT, B.DEFAULT_PUBLIC_OUTPUT):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(text), path)
            self.assertIsNone(coordinate.search(text), path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
