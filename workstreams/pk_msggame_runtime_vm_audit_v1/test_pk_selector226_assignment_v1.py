#!/usr/bin/env python3
"""Focused tests for the immutable two-chunk selector-226 assignment."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("build_pk_selector226_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location("selector226_assignment_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector226AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_content, cls.public_content, cls.private, cls.public = (
            BUILDER.build_outputs()
        )

    def test_exact_two_way_partition(self) -> None:
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
            ),
            (70, 70, 75, 5, 33, 46, 9, 10),
        )
        self.assertEqual(
            tuple(
                (
                    chunk["site_count"],
                    chunk["root_count"],
                    chunk["pending_root_count"],
                    chunk["pending_row_upper_bound"],
                    chunk["owned_overlap_root_count"],
                    chunk["workload_weight"],
                )
                for chunk in self.public["assignment"]["chunks"]
            ),
            BUILDER.EXPECTED_CHUNK_METRICS,
        )
        chunks = self.private["chunks"]
        self.assertFalse(set(chunks[0]["roots"]) & set(chunks[1]["roots"]))
        self.assertEqual(sum(row["site_count"] for row in chunks), 70)
        self.assertEqual(
            abs(chunks[0]["workload_weight"] - chunks[1]["workload_weight"]),
            1,
        )

    def test_prior_caller_evidence_is_complete_and_chunk_local(self) -> None:
        overlap = self.private["prior_caller_evidence_overlap"]
        self.assertEqual(
            (overlap["root_count"], overlap["relation_count"]), (33, 33)
        )
        self.assertEqual(
            (
                self.public["coverage"][
                    "prior_caller_evidence_overlap_root_count"
                ],
                self.public["coverage"][
                    "prior_caller_evidence_overlap_relation_count"
                ],
            ),
            (33, 33),
        )
        chunks = self.public["assignment"]["chunks"]
        self.assertEqual(
            [
                row["prior_caller_evidence_overlap_root_count"]
                for row in chunks
            ],
            [15, 18],
        )
        self.assertEqual(
            [
                row["completed_selector_overlap_relation_count"]
                for row in chunks
            ],
            [5, 5],
        )

    def test_shared_terminals_and_template_atoms_are_never_split(self) -> None:
        ownership = self.private["shared_terminal_ownership"]
        self.assertEqual(ownership["owner"], "assignment_scope")
        self.assertEqual(ownership["chunk_ids"], [])
        self.assertEqual(ownership["group_count"], 1)
        self.assertEqual(len(ownership["terminal_coordinates"]), 7)
        self.assertEqual(
            sorted(len(group) for group in self.private["identical_template_atoms"]),
            [2, 3, 5],
        )
        root_to_chunk = {
            root: chunk["chunk_id"]
            for chunk in self.private["chunks"]
            for root in chunk["roots"]
        }
        for group in self.private["identical_template_atoms"]:
            self.assertEqual({root_to_chunk[root] for root in group}, {
                root_to_chunk[group[0]]
            })
        assignment = self.public["assignment"]
        self.assertEqual(assignment["identical_template_atom_count"], 3)
        self.assertEqual(assignment["identical_template_root_count"], 10)
        self.assertFalse(assignment["identical_template_atoms_split"])
        self.assertFalse(assignment["shared_terminal_group_split"])

    def test_source_only_terminal_and_privacy_contracts(self) -> None:
        self.assertEqual(self.public["coverage"]["source_only_action_count"], 0)
        self.assertTrue(
            self.public["assignment"][
                "source_only_calls_separate_from_candidate_chunks"
            ]
        )
        terminal = self.public["terminal_compatibility"]
        self.assertTrue(terminal["terminal_registers_frozen"])
        self.assertTrue(terminal["dispatch_source_candidate_identical"])
        self.assertTrue(terminal["caller_complete_form_review_required"])
        BUILDER.assert_source_free(self.public)
        self.assertFalse(self.public["steam_write_performed"])

    def test_outputs_are_reproducible_and_frozen(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        repeated = BUILDER.build_outputs()
        self.assertEqual(repeated[0], self.private_content)
        self.assertEqual(repeated[1], self.public_content)


if __name__ == "__main__":
    unittest.main()
