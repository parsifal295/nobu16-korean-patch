#!/usr/bin/env python3
"""Regression tests for the consolidated selector-1096 family closure."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = (
    SCRIPT.parent
    / "build_pk_selector1096_family_consolidated_closure_v1.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    BUILDER_PATH,
    "pk_selector1096_family_consolidated_closure_test_builder_v1",
)


class Selector1096FamilyConsolidatedClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = BUILDER.build_outputs()
        BUILDER.validate_frozen(cls.bundle)

    def test_frozen_input_and_output_hashes_match(self) -> None:
        inputs = {
            BUILDER.OFFICIAL_PRIVATE_PATH:
                BUILDER.EXPECTED_OFFICIAL_PRIVATE_SHA256,
            BUILDER.OFFICIAL_PUBLIC_PATH:
                BUILDER.EXPECTED_OFFICIAL_PUBLIC_SHA256,
            BUILDER.CROSS568_PRIVATE_PATH:
                BUILDER.EXPECTED_CROSS568_PRIVATE_SHA256,
        }
        for path, digest in inputs.items():
            self.assertEqual(BUILDER.sha256_file(path), digest)
        outputs = {
            BUILDER.DEFAULT_AUDIT_OUTPUT: (
                BUILDER.EXPECTED_AUDIT_OUTPUT_SHA256,
                self.bundle["audit_content"],
            ),
            BUILDER.DEFAULT_PROMOTION_OUTPUT: (
                BUILDER.EXPECTED_PROMOTION_OUTPUT_SHA256,
                self.bundle["promotion_content"],
            ),
            BUILDER.DEFAULT_DECISION_OUTPUT: (
                BUILDER.EXPECTED_DECISION_OUTPUT_SHA256,
                self.bundle["decision_content"],
            ),
            BUILDER.DEFAULT_EVIDENCE_OUTPUT: (
                BUILDER.EXPECTED_EVIDENCE_OUTPUT_SHA256,
                self.bundle["evidence_content"],
            ),
        }
        for path, (digest, content) in outputs.items():
            self.assertEqual(BUILDER.sha256_file(path), digest)
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_family_union_and_shared_conflicts_are_exact(self) -> None:
        family = self.bundle["family"]
        self.assertEqual(len(family["decisions"]), 425)
        self.assertEqual(len(family["promotions"]), 222)
        self.assertEqual(len(family["renewals"]), 203)
        self.assertEqual(len(family["overrides"]), 127)
        self.assertEqual(
            [row["translation_difference_rows"]
             for row in family["pairwise"]],
            [38, 37, 51],
        )
        self.assertEqual(
            [row["decision_overlap_rows"] for row in family["pairwise"]],
            [203, 203, 203],
        )
        self.assertEqual(
            family["translation_variants"],
            {1: 140, 2: 63},
        )
        self.assertEqual(len(family["translation_owner"]), 203)
        self.assertEqual(len(family["evidence_owner"]), 203)

    def test_current_81b4_rebase_is_exact(self) -> None:
        family = self.bundle["family"]
        self.assertEqual(len(family["actual_promotions"]), 206)
        self.assertEqual(len(family["superseded_promotions"]), 16)
        self.assertEqual(len(family["effective_renewals"]), 219)
        actions = Counter(family["action_by_coordinate"].values())
        self.assertEqual(dict(actions), BUILDER.EXPECTED_ACTION_COUNTS)
        result = self.bundle["audit"]["result"]
        self.assertEqual(result["pending_rows_before"], 7896)
        self.assertEqual(result["pending_rows_after"], 7690)
        self.assertEqual(
            result["family_candidate_sha256"],
            BUILDER.EXPECTED_FAMILY_CANDIDATE_SHA256,
        )

    def test_all_931_accepted_assemblies_are_bound(self) -> None:
        manifest = self.bundle["candidate"][
            "accepted_assembly_manifest"
        ]
        self.assertEqual(len(manifest), 931)
        self.assertEqual(
            BUILDER.canonical_sha256(manifest),
            BUILDER.EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.bundle["candidate"]["family_blob"]),
            BUILDER.EXPECTED_FAMILY_CANDIDATE_SHA256,
        )
        proof = self.bundle["audit"]["proof"]
        self.assertTrue(
            proof["all_accepted_current_relative_raw_g1n_nonexpanding"]
        )

    def test_cross568_conflicts_are_correlated_but_deferred(self) -> None:
        cross = self.bundle["cross568"]
        self.assertEqual(cross["case_count"], 2)
        correlation = cross["correlation_proof"]
        self.assertTrue(
            correlation[
                "control_flow_and_selector_components_identical"
            ]
        )
        self.assertTrue(
            correlation["selector_expression_source_identical"]
        )
        self.assertTrue(
            correlation["ordinal_branch_correlation_proven"]
        )
        self.assertEqual(len(correlation["terminal_pairs"]), 7)
        self.assertTrue(
            all(
                len(case["branches"]) == 7
                and all(
                    branch[
                        "current_relative_raw_g1n_nonexpanding"
                    ]
                    for branch in case["branches"]
                )
                for case in cross["cases"]
            )
        )
        cross_coordinates = {
            str(case["coordinate568"]) for case in cross["cases"]
        }
        self.assertFalse(
            cross_coordinates & self.bundle["family"]["overrides"]
        )
        cross_evidence = [
            row for row in self.bundle["evidence_rows"]
            if row["coordinate"] in cross_coordinates
        ]
        self.assertEqual(len(cross_evidence), 2)
        for row in cross_evidence:
            proof = row["sequential_multi_selector_resolution"]
            self.assertTrue(proof["external_conflict_matrix"])
            self.assertTrue(
                proof[
                    "deferred_to_selector568_1096_full_record_resolver"
                ]
            )
            self.assertTrue(
                proof[
                    "selector1096_family_does_not_override_cross568_coordinate"
                ]
            )

    def test_reports_are_source_free_steam_unchanged_and_check_passes(
        self,
    ) -> None:
        combined = (
            self.bundle["audit_content"]
            + self.bundle["promotion_content"]
        )
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
                r"\uf900-\ufaff]",
                combined,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+)?\b", combined))
        self.assertNotIn('"translation"', combined)
        self.assertFalse(self.bundle["audit"]["steam_write_performed"])
        self.assertEqual(
            self.bundle["steam_before"], self.bundle["steam_after"]
        )
        self.assertEqual(BUILDER.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
