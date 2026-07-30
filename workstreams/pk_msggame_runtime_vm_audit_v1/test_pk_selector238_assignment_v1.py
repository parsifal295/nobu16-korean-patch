#!/usr/bin/env python3
"""Regression tests for the immutable selector-238 assignment."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pk_selector238_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location(
    "test_selector238_assignment_builder", BUILDER_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector238AssignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_text,
            cls.public_text,
            cls.private,
            cls.public,
        ) = BUILDER.build_outputs()

    def test_outputs_are_pinned_current_and_checkable(self) -> None:
        self.assertEqual(
            BUILDER.ASSIGNMENT.sha256_bytes(
                self.private_text.encode("utf-8")
            ),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.ASSIGNMENT.sha256_bytes(
                self.public_text.encode("utf-8")
            ),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PRIVATE_OUTPUT.read_text(encoding="utf-8"),
            self.private_text,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii"),
            self.public_text,
        )
        self.assertEqual(BUILDER.main(["--check"]), 0)

    def test_exact_selector238_scope(self) -> None:
        coverage = self.public["coverage"]
        self.assertEqual(self.public["scope"]["selector"], 238)
        self.assertEqual(self.public["scope"]["terminal_count"], 7)
        self.assertEqual(self.public["scope"]["official_pending_rows"], 6_178)
        self.assertEqual(
            (
                coverage["candidate_call_site_count"],
                coverage["candidate_call_root_count"],
                coverage["source_call_site_count"],
                coverage["source_only_repair_site_count"],
                coverage["direct_pending_call_site_count"],
                len(self.private["scope"][
                    "potential_current_pending_coordinates"
                ]),
            ),
            (27, 27, 28, 1, 15, 36),
        )
        self.assertEqual(coverage["candidate_non_display_root_count"], 0)
        self.assertEqual(coverage["direct_pending_non_display_root_count"], 0)

    def test_chunks_are_balanced_root_disjoint_singletons(self) -> None:
        chunks = self.private["chunks"]
        roots = [set(row["roots"]) for row in chunks]
        sites = [set(row["sites"]) for row in chunks]
        self.assertEqual(len(chunks), 2)
        self.assertFalse(roots[0] & roots[1])
        self.assertFalse(sites[0] & sites[1])
        self.assertEqual(len(roots[0] | roots[1]), 27)
        self.assertEqual(len(sites[0] | sites[1]), 27)
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
                (14, 14, 7, 14, 4, 271),
                (13, 13, 8, 22, 4, 261),
            ],
        )
        assignment = self.public["assignment"]
        self.assertEqual(self.private["identical_template_atoms"], [])
        self.assertFalse(assignment["giant_atom_created"])
        self.assertEqual(assignment["maximum_assignment_atom_root_count"], 1)
        self.assertEqual(assignment["atomic_sensitive_root_count"], 14)

    def test_no_same_gap_and_owned_prior_guards(self) -> None:
        coverage = self.public["coverage"]
        assignment = self.public["assignment"]
        self.assertEqual(self.private["same_gap_root_atoms"], [])
        self.assertEqual(assignment["same_gap_atom_count"], 0)
        self.assertEqual(assignment["multi_control_atom_count"], 0)
        self.assertEqual(assignment["same_gap_cartesian_branch_count"], 0)
        self.assertFalse(assignment["same_gap_atom_split"])
        overlap = self.private["completed_selector_overlap"]
        self.assertEqual(
            (
                overlap["root_count"],
                overlap["relation_count"],
                overlap["pending_row_count"],
            ),
            (8, 8, 18),
        )
        self.assertEqual(
            (
                coverage["prior_assembly_evidence_pending_root_count"],
                coverage["prior_assembly_evidence_pending_row_count"],
            ),
            (14, 26),
        )
        self.assertFalse(
            self.private["prior_pending_evidence"][
                "automatic_status_promotion_authorized"
            ]
        )

    def test_terminals_and_source_only_are_read_only(self) -> None:
        terminals = self.private["shared_terminal_ownership"]
        self.assertFalse(terminals["automatic_status_promotion_authorized"])
        self.assertEqual(len(terminals["terminal_manifest"]), 7)
        self.assertTrue(all(
            row["runtime_review"] == "pending"
            for row in terminals["terminal_manifest"]
        ))
        self.assertEqual(
            (
                sum(
                    row["candidate_current_identical"]
                    for row in terminals["terminal_manifest"]
                ),
                sum(
                    not row["candidate_current_identical"]
                    for row in terminals["terminal_manifest"]
                ),
            ),
            (6, 1),
        )
        self.assertEqual(self.private["source_only_repair"]["action_count"], 0)
        self.assertEqual(len(self.private["source_only_repair"]["sites"]), 1)
        self.assertEqual(
            self.public["coverage"]["source_only_repair_site_sha256"],
            BUILDER.EXPECTED_SOURCE_ONLY_SHA256,
        )

    def test_risk_privacy_and_no_deployment(self) -> None:
        rows = self.private["site_assignments"]
        self.assertEqual(
            sum(row["flags"]["layout_relative_expansion"] for row in rows),
            15,
        )
        self.assertEqual(
            sum(row["flags"]["grammar_right_boundary"] for row in rows),
            25,
        )
        self.assertEqual(
            sum(row["flags"]["multi_control_gap"] for row in rows),
            0,
        )
        self.assertEqual(
            max(row["maximum_positive_raw_g1n_delta_px"] for row in rows),
            408,
        )
        BUILDER.assert_source_free(self.public)
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+){0,2}\b", self.public_text)
        )
        self.assertFalse(self.private["steam_write_performed"])
        self.assertFalse(self.public["steam_write_performed"])
        json.loads(self.public_text)

    def test_unresolved_pins_and_refreeze_are_write_blocked(self) -> None:
        with self.assertRaisesRegex(
            BUILDER.AssignmentError,
            "bootstrap forbidden after assignment freeze",
        ):
            BUILDER.main(["--bootstrap"])

        original = BUILDER.EXPECTED_PUBLIC_FILE_SHA256
        try:
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256 = None
            with mock.patch.object(Path, "write_text") as write_text:
                with self.assertRaisesRegex(
                    BUILDER.AssignmentError,
                    "assignment bootstrap pins unresolved",
                ):
                    BUILDER.main([])
                write_text.assert_not_called()
        finally:
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256 = original


if __name__ == "__main__":
    unittest.main()
