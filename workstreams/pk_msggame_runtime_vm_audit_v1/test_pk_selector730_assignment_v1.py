#!/usr/bin/env python3
"""Regression tests for the immutable selector-730 two-chunk assignment."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pk_selector730_assignment_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "test_selector730_assignment_builder", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Selector730AssignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        private_text, public_text, private, public = cls.builder.build_outputs()
        cls.private_text = private_text
        cls.public_text = public_text
        cls.private = private
        cls.public = public

    def test_outputs_are_pinned_and_current(self) -> None:
        b = self.builder
        self.assertEqual(
            b.ASSIGNMENT.sha256_bytes(self.private_text.encode("utf-8")),
            b.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            b.ASSIGNMENT.sha256_bytes(self.public_text.encode("utf-8")),
            b.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(
            b.DEFAULT_PRIVATE_OUTPUT.read_text(encoding="utf-8"),
            self.private_text,
        )
        self.assertEqual(
            b.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii"),
            self.public_text,
        )

    def test_exact_selector730_scope(self) -> None:
        p = self.public
        self.assertEqual(p["scope"]["selector"], 730)
        self.assertEqual(p["scope"]["terminal_count"], 7)
        self.assertEqual(p["scope"]["official_pending_rows"], 6_181)
        self.assertEqual(
            (
                p["coverage"]["candidate_call_site_count"],
                p["coverage"]["candidate_call_root_count"],
                p["coverage"]["source_call_site_count"],
                p["coverage"]["source_only_repair_site_count"],
                p["coverage"]["direct_pending_call_site_count"],
                len(self.private["scope"]["potential_current_pending_coordinates"]),
            ),
            (41, 41, 46, 5, 18, 37),
        )
        self.assertEqual(p["coverage"]["candidate_non_display_root_count"], 0)
        self.assertEqual(p["coverage"]["direct_pending_non_display_root_count"], 0)

    def test_chunks_are_balanced_root_disjoint_atoms(self) -> None:
        chunks = self.private["chunks"]
        roots = [set(row["roots"]) for row in chunks]
        self.assertEqual(len(chunks), 2)
        self.assertFalse(roots[0] & roots[1])
        self.assertEqual(
            [(row["site_count"], row["pending_row_upper_bound"],
              row["workload_weight"]) for row in chunks],
            [(21, 12, 503), (20, 25, 504)],
        )
        template = set(self.private["identical_template_atoms"][0])
        self.assertEqual(len(template), 2)
        self.assertTrue(any(template <= chunk_roots for chunk_roots in roots))
        assignment = self.public["assignment"]
        self.assertFalse(assignment["giant_atom_created"])
        self.assertEqual(assignment["maximum_assignment_atom_root_count"], 2)
        self.assertFalse(assignment["same_gap_atom_split"])
        self.assertEqual(assignment["atomic_sensitive_root_count"], 38)

    def test_same_gap_and_overlap_guards(self) -> None:
        coverage = self.public["coverage"]
        assignment = self.public["assignment"]
        self.assertEqual(len(self.private["same_gap_root_atoms"]), 37)
        self.assertEqual(assignment["same_gap_atom_count"], 37)
        self.assertEqual(assignment["same_gap_sibling_family_count"], 17)
        self.assertEqual(assignment["same_gap_cartesian_branch_count"], 1_813)
        self.assertEqual(coverage["same_gap_pending_root_count"], 17)
        self.assertEqual(coverage["same_gap_pending_row_count"], 34)
        overlap = self.private["completed_selector_overlap"]
        self.assertEqual(
            (overlap["root_count"], overlap["relation_count"],
             overlap["pending_row_count"]),
            (10, 10, 23),
        )

    def test_prior_evidence_remains_read_only(self) -> None:
        coverage = self.public["coverage"]
        self.assertEqual(
            (
                coverage["prior_assembly_evidence_pending_root_count"],
                coverage["prior_assembly_evidence_pending_row_count"],
            ),
            (15, 32),
        )
        terminals = self.private["shared_terminal_ownership"]
        self.assertFalse(terminals["automatic_status_promotion_authorized"])
        self.assertEqual(len(terminals["terminal_manifest"]), 7)
        self.assertTrue(
            all(row["runtime_review"] == "pending"
                for row in terminals["terminal_manifest"])
        )
        self.assertEqual(
            self.public["terminal_compatibility"],
            {
                "automatic_status_promotion_authorized": False,
                "candidate_current_different_terminal_count": 3,
                "candidate_current_identical_terminal_count": 4,
                "context_terminals_authoritative": False,
                "read_only_pending_terminal_count": 7,
            },
        )

    def test_risk_source_only_privacy_and_no_deployment(self) -> None:
        rows = self.private["site_assignments"]
        self.assertEqual(
            sum(row["flags"]["layout_relative_expansion"] for row in rows), 27
        )
        self.assertEqual(
            sum(row["flags"]["grammar_right_boundary"] for row in rows), 21
        )
        self.assertEqual(
            max(row["maximum_positive_raw_g1n_delta_px"] for row in rows), 480
        )
        self.assertEqual(self.private["source_only_repair"]["action_count"], 0)
        self.assertEqual(len(self.private["source_only_repair"]["sites"]), 5)
        self.assertFalse(self.private["steam_write_performed"])
        self.assertFalse(self.public["steam_write_performed"])
        self.assertFalse(
            self.public["privacy"]["contains_commercial_source_text"]
        )
        self.assertFalse(self.public["privacy"]["contains_translations"])
        json.loads(self.public_text)


if __name__ == "__main__":
    unittest.main()
