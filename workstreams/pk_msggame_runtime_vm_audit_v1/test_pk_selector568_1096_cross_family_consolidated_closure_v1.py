#!/usr/bin/env python3
"""Regression tests for selector-568/1096 cross-family consolidation."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = (
    SCRIPT.parent
    / "build_pk_selector568_1096_cross_family_consolidated_closure_v1.py"
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
    "pk_selector568_1096_cross_family_consolidated_test_builder_v1",
)


class Selector5681096CrossFamilyConsolidatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = BUILDER.build_outputs()
        BUILDER.validate_frozen(cls.bundle)

    def test_frozen_inputs_and_outputs_match(self) -> None:
        inputs = {
            BUILDER.OFFICIAL_PRIVATE_PATH:
                BUILDER.EXPECTED_OFFICIAL_PRIVATE_SHA256,
            BUILDER.OFFICIAL_PUBLIC_PATH:
                BUILDER.EXPECTED_OFFICIAL_PUBLIC_SHA256,
            BUILDER.CROSS_DEFERRED_PATH:
                BUILDER.EXPECTED_CROSS_DEFERRED_SHA256,
            BUILDER.FAMILY568_BUILDER_PATH:
                BUILDER.EXPECTED_FAMILY568_BUILDER_SHA256,
            BUILDER.FAMILY1096_BUILDER_PATH:
                BUILDER.EXPECTED_FAMILY1096_BUILDER_SHA256,
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

    def test_family_union_and_conflict_partition_are_exact(self) -> None:
        union = self.bundle["union"]
        self.assertEqual(len(union["family568_decisions"]), 503)
        self.assertEqual(len(union["family1096_decisions"]), 425)
        self.assertEqual(len(union["overlap"]), 8)
        self.assertEqual(len(union["union"]), 920)
        self.assertEqual(len(union["translation_differences"]), 2)
        self.assertEqual(
            BUILDER.coordinate_digest(union["overlap"]),
            BUILDER.EXPECTED_FAMILY_OVERLAP_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(union["translation_differences"]),
            BUILDER.EXPECTED_FAMILY_TRANSLATION_DIFF_SHA256,
        )

    def test_current81b4_rebase_and_actions_are_exact(self) -> None:
        union = self.bundle["union"]
        self.assertEqual(len(union["actual_promotions"]), 431)
        self.assertEqual(len(union["renewals"]), 489)
        self.assertEqual(len(union["overrides"]), 285)
        self.assertEqual(
            union["action_counts"], BUILDER.EXPECTED_ACTION_COUNTS
        )
        result = self.bundle["audit"]["result"]
        self.assertEqual(result["pending_rows_before"], 7896)
        self.assertEqual(result["pending_rows_after"], 7465)
        self.assertEqual(
            result["final_candidate_sha256"],
            BUILDER.EXPECTED_FINAL_CANDIDATE_SHA256,
        )

    def test_all_family_and_cross_assemblies_are_bound(self) -> None:
        candidate = self.bundle["candidate"]
        self.assertEqual(
            len(candidate["accepted_assembly_manifest"]), 2114
        )
        self.assertEqual(
            candidate["accepted_assembly_sha256"],
            BUILDER.EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        )
        self.assertEqual(
            len(candidate["cross_branch_manifest"]), 14
        )
        self.assertEqual(
            candidate["cross_branch_sha256"],
            BUILDER.EXPECTED_CROSS_BRANCH_SHA256,
        )
        self.assertEqual(
            candidate["final_sha256"],
            BUILDER.EXPECTED_FINAL_CANDIDATE_SHA256,
        )

    def test_two_full_records_use_correlated_seven_branch_proof(
        self,
    ) -> None:
        cross = self.bundle["cross"]
        self.assertEqual(cross["case_count"], 2)
        self.assertEqual(len(self.bundle["union"]["cross_coordinates"]), 4)
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
        proof = self.bundle["audit"]["proof"][
            "sequential_multi_selector_resolution"
        ]
        self.assertFalse(proof["cartesian_branch_matrix_required"])
        self.assertEqual(proof["ordinal_correlated_branch_rows"], 14)
        self.assertTrue(
            proof["ordinal_correlated_branches_nonexpanding"]
        )

    def test_cross_coordinates_are_exactly_bound_to_private_candidates(
        self,
    ) -> None:
        rows = {
            str(row["coordinate"]): row
            for row in self.bundle["updated_rows"]
        }
        evidence = {
            str(row["coordinate"]): row
            for row in self.bundle["evidence_rows"]
        }
        expected = {}
        for case in self.bundle["cross"]["cases"]:
            expected[str(case["coordinate1096"])] = str(
                case["candidate_left1096"]
            )
            expected[str(case["coordinate568"])] = str(
                case["candidate_left568"]
            )
        self.assertEqual(set(expected), self.bundle["union"]["cross_coordinates"])
        for coordinate, translation in expected.items():
            self.assertEqual(rows[coordinate]["translation"], translation)
            proof = evidence[coordinate][
                "sequential_multi_selector_resolution"
            ]
            self.assertEqual(
                proof["candidate_utf16le_sha256"],
                BUILDER.sha256_text(translation),
            )
            self.assertTrue(
                proof[
                    "seven_corresponding_register_branches_nonexpanding"
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
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+)?\b", combined)
        )
        self.assertNotIn('"translation"', combined)
        self.assertFalse(self.bundle["audit"]["steam_write_performed"])
        self.assertEqual(
            self.bundle["steam_before"],
            self.bundle["steam_after"],
        )
        self.assertEqual(BUILDER.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
