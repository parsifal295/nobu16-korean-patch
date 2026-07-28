#!/usr/bin/env python3
"""Exact checks for the frozen selector-292 assignment."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pk_selector292_assignment_v1.py")
spec = importlib.util.spec_from_file_location(
    "selector292_assignment_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector292AssignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_content,
            cls.public_content,
            cls.private,
            cls.public,
        ) = BUILDER.build_outputs()

    def test_exact_scope_and_partition(self) -> None:
        coverage = self.public["coverage"]
        review = self.public["review_partition"]
        self.assertEqual(
            (
                coverage["candidate_call_site_count"],
                coverage["source_call_site_count"],
                coverage["source_only_repair_site_count"],
                coverage["potential_current_pending_rows"],
                coverage["direct_pending_call_site_count"],
            ),
            (26, 31, 5, 33, 11),
        )
        self.assertEqual(
            (
                review["hard_block_root_count"],
                review["hard_block_pending_row_count"],
                review["rewrite_candidate_root_count"],
                review["rewrite_candidate_pending_row_count"],
            ),
            (2, 5, 9, 28),
        )

    def test_balanced_root_disjoint_chunks(self) -> None:
        chunks = self.public["assignment"]["chunks"]
        self.assertEqual(
            [
                (
                    row["site_count"],
                    row["root_count"],
                    row["pending_root_count"],
                    row["pending_row_upper_bound"],
                    row["owned_overlap_root_count"],
                    row["workload_weight"],
                )
                for row in chunks
            ],
            [
                (13, 13, 5, 13, 0, 343),
                (13, 13, 6, 20, 1, 342),
            ],
        )
        roots = [
            {
                tuple(map(int, value.split(":")))
                for value in chunk["roots"]
            }
            for chunk in self.private["chunks"]
        ]
        self.assertTrue(roots[0].isdisjoint(roots[1]))

    def test_structural_atoms_and_reused_layout(self) -> None:
        assignment = self.public["assignment"]
        self.assertEqual(
            (
                assignment["identical_template_atom_count"],
                assignment["register_atom_count"],
                assignment["same_gap_atom_count"],
                assignment["same_gap_cartesian_branch_count"],
                assignment["maximum_assignment_atom_root_count"],
            ),
            (2, 2, 8, 392, 2),
        )
        self.assertFalse(assignment["same_gap_atom_split"])
        self.assertFalse(assignment["shared_terminal_group_split"])
        self.assertEqual(
            self.public["reused_private_evidence"][
                "cartesian_branches_recomputed"
            ],
            0,
        )

    def test_read_only_guards(self) -> None:
        terminals = self.public["terminal_compatibility"]
        coverage = self.public["coverage"]
        self.assertEqual(
            (
                terminals["read_only_verified_terminal_count"],
                terminals["read_only_pending_terminal_count"],
                coverage["source_only_action_count"],
            ),
            (6, 1, 0),
        )
        self.assertFalse(
            terminals["automatic_status_promotion_authorized"]
        )

    def test_frozen_outputs_and_source_free_public(self) -> None:
        self.assertEqual(
            BUILDER.ASSIGNMENT.sha256_bytes(
                self.private_content.encode("utf-8")
            ),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.ASSIGNMENT.sha256_bytes(
                self.public_content.encode("ascii")
            ),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PRIVATE_OUTPUT.read_text(encoding="utf-8"),
            self.private_content,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii"),
            self.public_content,
        )
        BUILDER.assert_source_free(json.loads(self.public_content))

    def test_check_and_tamper_rejection(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        original = BUILDER.EXPECTED_LAYOUT_MANIFEST_SHA256
        try:
            BUILDER.EXPECTED_LAYOUT_MANIFEST_SHA256 = "0" * 64
            with self.assertRaises(BUILDER.AssignmentError):
                BUILDER.build_outputs()
        finally:
            BUILDER.EXPECTED_LAYOUT_MANIFEST_SHA256 = original


if __name__ == "__main__":
    unittest.main()
