#!/usr/bin/env python3
"""Focused tests for the immutable two-chunk selector-268 assignment."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("build_pk_selector268_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location("selector268_assignment_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector268AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_content, cls.public_content, cls.private, cls.public = (
            BUILDER.build_outputs()
        )

    def test_exact_root_disjoint_two_way_partition(self) -> None:
        coverage = self.public["coverage"]
        self.assertEqual(self.public["assignment"]["chunk_count"], 2)
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
            (26, 25, 27, 1, 16, 44, 7, 10, 25),
        )
        chunks = self.private["chunks"]
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

    def test_atomic_scope_and_pending_evidence(self) -> None:
        ownership = self.private["shared_terminal_ownership"]
        self.assertEqual(ownership["owner"], "assignment_scope")
        self.assertEqual(ownership["chunk_ids"], [])
        self.assertEqual(len(ownership["terminal_coordinates"]), 7)
        self.assertEqual(self.private["identical_template_atoms"], [])
        self.assertFalse(self.public["assignment"]["same_gap_atom_split"])
        self.assertEqual(self.public["assignment"]["same_gap_atom_count"], 1)
        self.assertEqual(
            self.public["assignment"]["same_gap_neighbor_relation_count"], 2
        )
        evidence = self.private["prior_pending_evidence"]
        self.assertFalse(evidence["automatic_status_promotion_authorized"])
        self.assertEqual(evidence["terminal_evidence_count"], 7)
        self.assertEqual(
            (
                self.public["coverage"][
                    "prior_assembly_evidence_pending_root_count"
                ],
                self.public["coverage"][
                    "prior_assembly_evidence_pending_row_count"
                ],
            ),
            (15, 41),
        )

    def test_source_only_terminal_and_privacy_contracts(self) -> None:
        self.assertEqual(self.public["coverage"]["source_only_action_count"], 0)
        terminal = self.public["terminal_compatibility"]
        self.assertEqual(
            terminal["candidate_terminal_multiplicity_sorted"], [1, 2, 4]
        )
        self.assertFalse(terminal["context_terminals_authoritative"])
        self.assertFalse(terminal["automatic_status_promotion_authorized"])
        BUILDER.assert_source_free(self.public)
        self.assertFalse(self.public["steam_write_performed"])

    def test_outputs_are_reproducible_and_frozen(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        repeated = BUILDER.build_outputs()
        self.assertEqual(repeated[0], self.private_content)
        self.assertEqual(repeated[1], self.public_content)


if __name__ == "__main__":
    unittest.main()
