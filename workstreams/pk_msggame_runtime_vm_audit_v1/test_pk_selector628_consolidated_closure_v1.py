#!/usr/bin/env python3
"""Targeted checks for the frozen selector-628 closure."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_pk_selector628_consolidated_closure_v1.py"
)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("selector628_closure_tested", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_module(BUILDER_PATH)


class Selector628ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = B.build_outputs()
        cls.evidence = json.loads(
            cls.outputs[B.PRIVATE_EVIDENCE_OUTPUT].decode("utf-8")
        )
        cls.coverage = json.loads(
            cls.outputs[B.PUBLIC_COVERAGE_OUTPUT].decode("ascii")
        )
        cls.promotion = json.loads(
            cls.outputs[B.PUBLIC_PROMOTION_OUTPUT].decode("ascii")
        )

    def test_exact_delta(self) -> None:
        self.assertEqual(
            self.evidence["counts"],
            {
                "action_counts": B.EXPECTED_ACTION_COUNTS,
                "changed_roots": 48,
                "decision_roots": 50,
                "decision_rows": 100,
                "overrides": 60,
                "predecessor_overlaps": 1,
                "predecessor_supersessions": 1,
                "promotions": 58,
                "renewals": 42,
                "reviewed_sites": 145,
                "source_only_actions": 0,
                "source_only_sites": 21,
            },
        )
        self.assertEqual(
            self.promotion["result"]["pending_after"],
            6_489,
        )

    def test_candidate_and_reverse(self) -> None:
        guards = self.evidence["guards"]
        self.assertEqual(
            guards["candidate_sha256"],
            B.EXPECTED_OUTPUT_SHA256["final_candidate"],
        )
        self.assertEqual(
            guards["reverse_candidate_sha256"],
            B.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        )

    def test_single_union_and_source_only(self) -> None:
        proof = self.coverage["proof"]
        self.assertTrue(proof["all_owner_permutations_identical"])
        self.assertTrue(proof["all_145_candidate_sites_reviewed"])
        self.assertTrue(
            proof["source_only_21_absent_from_current_and_candidate"]
        )
        self.assertEqual(
            self.evidence["source_only_runtime_delta_proof"]["actions"],
            0,
        )

    def test_public_artifacts_are_source_free(self) -> None:
        for path in (B.PUBLIC_COVERAGE_OUTPUT, B.PUBLIC_PROMOTION_OUTPUT):
            text = self.outputs[path].decode("ascii")
            self.assertIsNone(
                re.search(
                    r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                    r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                    text,
                )
            )
            self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+){0,2}\b", text))

    def test_outputs_match_frozen_hashes(self) -> None:
        labels = {
            B.PRIVATE_DECISIONS_OUTPUT: "private_decisions",
            B.PRIVATE_EVIDENCE_OUTPUT: "private_evidence",
            B.PUBLIC_COVERAGE_OUTPUT: "public_coverage",
            B.PUBLIC_PROMOTION_OUTPUT: "public_promotion",
        }
        for path, label in labels.items():
            self.assertEqual(
                B.BASE.sha256_bytes(self.outputs[path]),
                B.EXPECTED_OUTPUT_SHA256[label],
            )


if __name__ == "__main__":
    unittest.main()
