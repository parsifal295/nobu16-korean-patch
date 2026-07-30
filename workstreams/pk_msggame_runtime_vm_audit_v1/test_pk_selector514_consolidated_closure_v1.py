#!/usr/bin/env python3
"""Focused checks for the selector-514 two-chunk closure."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_pk_selector514_consolidated_closure_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("selector514_closure_tested", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load selector514 closure")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Selector514ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_builder()
        cls.outputs = cls.module.build_outputs()

    def test_frozen_outputs(self) -> None:
        mapping = {
            self.module.PRIVATE_DECISIONS_OUTPUT: "private_decisions",
            self.module.PRIVATE_EVIDENCE_OUTPUT: "private_evidence",
            self.module.PUBLIC_COVERAGE_OUTPUT: "public_coverage",
            self.module.PUBLIC_PROMOTION_OUTPUT: "public_promotion",
        }
        for path, label in mapping.items():
            self.assertEqual(
                self.module.BASE.sha256_bytes(self.outputs[path]),
                self.module.EXPECTED_OUTPUT_SHA256[label],
            )

    def test_single_union_counts_and_reverse(self) -> None:
        coverage = json.loads(
            self.outputs[self.module.PUBLIC_COVERAGE_OUTPUT].decode("ascii")
        )
        promotion = json.loads(
            self.outputs[self.module.PUBLIC_PROMOTION_OUTPUT].decode("ascii")
        )
        self.assertEqual(coverage["result"]["decision_rows"], 108)
        self.assertEqual(coverage["result"]["reviewed_sites"], 56)
        self.assertEqual(coverage["result"]["source_only_sites"], 30)
        self.assertEqual(coverage["result"]["source_only_actions"], 0)
        self.assertEqual(promotion["result"]["promotions"], 98)
        self.assertEqual(promotion["result"]["renewals"], 10)
        self.assertEqual(promotion["result"]["overrides"], 29)
        self.assertEqual(
            promotion["candidate"]["reviewed_sha256"],
            self.module.EXPECTED_FINAL_CANDIDATE_SHA256,
        )
        self.assertEqual(
            promotion["candidate"]["reverse_overlay_sha256"],
            self.module.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        )

    def test_public_outputs_are_source_free(self) -> None:
        for path in (
            self.module.PUBLIC_COVERAGE_OUTPUT,
            self.module.PUBLIC_PROMOTION_OUTPUT,
        ):
            text = self.outputs[path].decode("ascii")
            self.assertIsNone(re.search(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]", text))
            self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+){0,2}\b", text))
            self.assertNotIn('"reviewed_translation"', text)


if __name__ == "__main__":
    unittest.main()
