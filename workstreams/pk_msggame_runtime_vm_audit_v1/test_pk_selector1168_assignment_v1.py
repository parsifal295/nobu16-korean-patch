#!/usr/bin/env python3
"""Focused tests for the immutable two-chunk selector-1168 assignment."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("build_pk_selector1168_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location("selector1168_assignment_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector1168AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_content, cls.public_content, cls.private, cls.public = (
            BUILDER.build_outputs()
        )

    def test_exact_two_way_partition(self) -> None:
        self.assertEqual(self.public["assignment"]["chunk_count"], 2)
        self.assertEqual(
            (
                self.public["coverage"]["candidate_call_site_count"],
                self.public["coverage"]["candidate_call_root_count"],
                self.public["coverage"]["source_call_site_count"],
                self.public["coverage"]["source_only_repair_site_count"],
                self.public["coverage"]["direct_pending_call_site_count"],
                self.public["coverage"]["potential_current_pending_rows"],
                self.public["coverage"]["owned_overlap_root_count"],
                self.public["coverage"]["owned_overlap_pending_rows"],
            ),
            (53, 52, 58, 5, 14, 48, 7, 25),
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
        self.assertEqual(
            sum(chunk["site_count"] for chunk in chunks),
            53,
        )
        self.assertEqual(
            sum(chunk["root_count"] for chunk in chunks),
            52,
        )
        self.assertEqual(
            {chunk["workload_weight"] for chunk in chunks},
            {557},
        )

    def test_shared_terminals_and_templates_have_single_ownership(self) -> None:
        ownership = self.private["shared_terminal_ownership"]
        terminals = ownership["terminal_coordinates"]
        chunk_roots = {
            root
            for chunk in self.private["chunks"]
            for root in chunk["roots"]
        }
        self.assertEqual(ownership["owner"], "assignment_scope")
        self.assertEqual(ownership["chunk_ids"], [])
        self.assertEqual(ownership["group_count"], 1)
        self.assertEqual(len(terminals), 7)
        self.assertEqual(len(set(terminals)), 7)
        self.assertFalse(
            {":".join(value.split(":")[:2]) for value in terminals}
            & chunk_roots
        )
        self.assertEqual(self.private["identical_template_atoms"], [])
        self.assertEqual(
            self.public["assignment"]["identical_template_root_count"], 0
        )
        self.assertFalse(
            self.public["assignment"]["shared_terminal_group_split"]
        )
        self.assertFalse(
            self.public["assignment"]["identical_template_atoms_split"]
        )

    def test_source_only_and_terminal_compatibility_are_frozen(self) -> None:
        self.assertTrue(
            self.public["assignment"][
                "source_only_calls_separate_from_candidate_chunks"
            ]
        )
        self.assertEqual(self.public["coverage"]["source_only_action_count"], 0)
        compatibility = self.public["terminal_compatibility"]
        self.assertEqual(compatibility["candidate_terminal_nonempty_count"], 0)
        self.assertTrue(
            compatibility["dispatch_source_candidate_identical"]
        )
        self.assertTrue(
            compatibility["caller_complete_form_review_required"]
        )
        self.assertEqual(
            self.public["assignment"]["site_risk_matrix_sha256"],
            BUILDER.EXPECTED_SITE_ROW_SHA256,
        )

    def test_outputs_are_reproducible_frozen_and_source_free(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        BUILDER.assert_source_free(self.public)
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertFalse(self.public["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
