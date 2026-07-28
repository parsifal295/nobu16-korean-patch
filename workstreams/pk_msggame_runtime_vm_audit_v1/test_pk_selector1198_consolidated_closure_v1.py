#!/usr/bin/env python3
"""Targeted checks for the frozen selector-1198 closure."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_pk_selector1198_consolidated_closure_v1.py"
)
spec = importlib.util.spec_from_file_location("selector1198_closure_tested", BUILDER_PATH)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector1198ClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = BUILDER.build_outputs()
        cls.coverage = json.loads(
            cls.outputs[BUILDER.PUBLIC_COVERAGE_OUTPUT].decode("ascii")
        )
        cls.promotion = json.loads(
            cls.outputs[BUILDER.PUBLIC_PROMOTION_OUTPUT].decode("ascii")
        )

    def test_exact_union_counts(self) -> None:
        self.assertEqual(
            self.promotion["result"],
            {
                "action_counts": {
                    "runtime_promotion": 21,
                    "translation_override_and_runtime_promotion": 4,
                    "translation_override_and_verification_renewal": 2,
                },
                "decision_rows": 27,
                "overrides": 6,
                "pending_after": 6464,
                "pending_before": 6489,
                "promotions": 25,
                "renewals": 2,
                "source_only_actions": 0,
            },
        )

    def test_site_and_lineage_proofs(self) -> None:
        self.assertEqual(self.coverage["result"]["reviewed_sites"], 46)
        self.assertEqual(self.coverage["result"]["source_only_sites"], 0)
        self.assertEqual(self.coverage["result"]["predecessor_overlaps"], 0)
        self.assertTrue(self.coverage["proof"]["all_owner_permutations_identical"])
        self.assertTrue(self.coverage["proof"]["reverse_overlay_exact"])

    def test_frozen_candidate(self) -> None:
        self.assertEqual(
            self.promotion["candidate"]["reviewed_sha256"],
            "74E30E798B82129565518FA04F35DC73220974CFC6E1E7E61BCEC2D8008671DA",
        )
        self.assertEqual(
            self.promotion["candidate"]["reverse_overlay_sha256"],
            "28267B6928CBDBF3E98FBB8E13A4733947A4EAC6A2BF04812A848C1091F9B186",
        )


if __name__ == "__main__":
    unittest.main()
