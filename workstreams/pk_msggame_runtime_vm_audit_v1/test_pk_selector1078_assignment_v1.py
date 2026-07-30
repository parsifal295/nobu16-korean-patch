#!/usr/bin/env python3
"""Focused tests for the immutable two-chunk selector-1078 assignment."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("build_pk_selector1078_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location("selector1078_assignment_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector1078AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_content, cls.public_content, cls.private, cls.public = (
            BUILDER.build_outputs()
        )

    def test_exact_root_disjoint_balanced_partition(self) -> None:
        coverage = self.public["coverage"]
        self.assertEqual(
            (
                coverage["candidate_call_site_count"],
                coverage["candidate_call_root_count"],
                coverage["source_call_site_count"],
                coverage["source_only_repair_site_count"],
                coverage["direct_pending_call_site_count"],
                coverage["potential_current_pending_rows"],
                coverage["owned_overlap_root_count"],
                coverage["completed_selector_overlap_relation_count"],
                coverage["owned_overlap_pending_rows"],
            ),
            (43, 43, 44, 1, 20, 43, 8, 13, 21),
        )
        chunks = self.private["chunks"]
        self.assertEqual(len(chunks), 2)
        self.assertFalse(set(chunks[0]["roots"]) & set(chunks[1]["roots"]))
        self.assertEqual(
            tuple(
                (
                    row["site_count"],
                    row["root_count"],
                    row["pending_root_count"],
                    row["pending_row_upper_bound"],
                    row["owned_overlap_root_count"],
                    row["workload_weight"],
                )
                for row in chunks
            ),
            BUILDER.EXPECTED_CHUNK_METRICS,
        )

    def test_atomic_groups_are_never_split(self) -> None:
        assignment = self.public["assignment"]
        coverage = self.public["coverage"]
        self.assertEqual(
            (
                assignment["assignment_atom_union_root_count"],
                assignment["assignment_atom_union_pending_rows"],
                assignment["identical_template_atom_count"],
                assignment["identical_template_root_count"],
            ),
            (10, 25, 1, 2),
        )
        self.assertEqual(
            (
                coverage["same_gap_root_count"],
                coverage["same_gap_relation_count"],
                coverage["same_gap_pending_rows"],
                coverage["repeated_template_pending_rows"],
            ),
            (5, 5, 15, 4),
        )
        self.assertFalse(assignment["same_gap_atom_split"])
        atom_roots = set(self.private["assignment_atom_union"]["roots"])
        chunks = [
            set(chunk["roots"]) & atom_roots
            for chunk in self.private["chunks"]
        ]
        self.assertEqual(sorted(map(len, chunks)), [0, 10])

    def test_prior_evidence_terminal_and_exclusion_contracts(self) -> None:
        coverage = self.public["coverage"]
        self.assertEqual(
            (
                coverage["prior_assembly_evidence_pending_root_count"],
                coverage["prior_assembly_evidence_pending_row_count"],
                coverage["terminal_prior_evidence_pending_count"],
                coverage["candidate_non_display_root_count"],
                coverage["direct_pending_non_display_root_count"],
                coverage["source_only_action_count"],
            ),
            (17, 29, 7, 0, 0, 0),
        )
        evidence = self.private["prior_pending_evidence"]
        self.assertFalse(evidence["automatic_status_promotion_authorized"])
        self.assertEqual(evidence["terminal_runtime_review"], "pending")
        ownership = self.private["shared_terminal_ownership"]
        self.assertEqual(ownership["owner"], "assignment_scope")
        self.assertEqual(ownership["chunk_ids"], [])
        self.assertEqual(len(ownership["terminal_coordinates"]), 7)
        BUILDER.assert_source_free(self.public)
        self.assertFalse(self.public["steam_write_performed"])

    def test_outputs_are_reproducible_and_frozen(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        repeated = BUILDER.build_outputs()
        self.assertEqual(repeated[0], self.private_content)
        self.assertEqual(repeated[1], self.public_content)


if __name__ == "__main__":
    unittest.main()
