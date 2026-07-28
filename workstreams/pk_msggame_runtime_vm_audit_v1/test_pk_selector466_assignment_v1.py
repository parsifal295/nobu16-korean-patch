#!/usr/bin/env python3
"""Focused tests for the immutable selector-466 two-chunk assignment."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("build_pk_selector466_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location("selector466_assignment_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector466AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_content, cls.public_content, cls.private, cls.public = (
            BUILDER.build_outputs()
        )

    def test_exact_coverage_and_root_disjoint_balance(self) -> None:
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
            (79, 79, 94, 15, 20, 41, 3, 4, 5),
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

    def test_template_and_same_gap_atoms_are_not_split(self) -> None:
        self.assertEqual(
            sorted(map(len, self.private["identical_template_atoms"])),
            [2, 3, 4, 8, 8],
        )
        root_to_chunk = {
            root: chunk["chunk_id"]
            for chunk in self.private["chunks"] for root in chunk["roots"]
        }
        for atom in self.private["identical_template_atoms"]:
            self.assertEqual(len({root_to_chunk[root] for root in atom}), 1)
        same_gap = self.private["same_gap_control_atom"]
        self.assertEqual(len(same_gap["atom_roots"]), 2)
        self.assertEqual(
            len({root_to_chunk[root] for root in same_gap["atom_roots"]}), 1
        )
        self.assertEqual(
            [len(row["ordered_siblings"]) for row in same_gap["manifest"]],
            [2, 2],
        )
        self.assertTrue(all(
            not row["cartesian_runtime_validation_complete"]
            and row["assignment_mode"]
                == "block_all_ordered_sibling_controls"
            for row in same_gap["manifest"]
        ))
        self.assertEqual(
            (
                self.public["coverage"]["same_gap_root_count"],
                self.public["coverage"]["same_gap_relation_count"],
                self.public["coverage"]["same_gap_pending_rows"],
            ),
            (2, 2, 4),
        )
        self.assertFalse(self.public["assignment"]["same_gap_atom_split"])

    def test_evidence_terminals_and_exclusions_are_read_only(self) -> None:
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
            (18, 35, 7, 0, 0, 0),
        )
        evidence = self.private["prior_pending_evidence"]
        self.assertFalse(evidence["automatic_status_promotion_authorized"])
        self.assertEqual(evidence["terminal_runtime_review"], "verified_read_only")
        ownership = self.private["shared_terminal_ownership"]
        self.assertEqual(ownership["owner"], "assignment_scope")
        self.assertEqual(ownership["chunk_ids"], [])
        self.assertFalse(ownership["automatic_status_promotion_authorized"])
        self.assertEqual(len(ownership["terminal_manifest"]), 7)
        self.assertTrue(all(
            row["runtime_review"] == "verified"
            and len(row["raw_record_sha256"]) == 64
            and len(row["component_signature_sha256"]) == 64
            and len(row["control_signature_sha256"]) == 64
            for row in ownership["terminal_manifest"]
        ))
        self.assertEqual(self.private["source_only_repair"]["action_count"], 0)
        self.assertEqual(len(self.private["source_only_repair"]["sites"]), 15)
        BUILDER.assert_source_free(self.public)
        self.assertFalse(self.public["steam_write_performed"])

    def test_outputs_are_reproducible_and_frozen(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        repeated = BUILDER.build_outputs()
        self.assertEqual(repeated[0], self.private_content)
        self.assertEqual(repeated[1], self.public_content)


if __name__ == "__main__":
    unittest.main()
