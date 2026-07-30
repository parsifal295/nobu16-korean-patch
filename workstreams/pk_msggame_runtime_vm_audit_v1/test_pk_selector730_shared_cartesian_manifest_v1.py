#!/usr/bin/env python3
"""Exact checks for the selector-730 shared Cartesian evidence."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_selector730_shared_cartesian_manifest_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "selector730_shared_cartesian_test", PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector730SharedCartesianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_content,
            cls.public_content,
            cls.private,
            cls.public,
        ) = BUILDER.build_outputs()

    def test_exact_scope_and_cartesian_coverage(self) -> None:
        scope = self.public["scope"]
        self.assertEqual(
            (
                scope["candidate_call_sites"],
                scope["source_call_sites"],
                scope["source_only_sites"],
                scope["same_gap_sites"],
                scope["same_gap_roots"],
                scope["pending_same_gap_roots"],
                scope["pending_same_gap_rows"],
                scope["controls_per_same_gap"],
                scope["sibling_seven_way_families"],
                scope["ordered_cartesian_branches"],
            ),
            (41, 46, 5, 37, 37, 17, 34, 2, 17, 1_813),
        )
        roots = self.private["cartesian_roots"]
        self.assertEqual(len(roots), 37)
        self.assertEqual(sum(row["branch_count"] for row in roots), 1_813)
        self.assertTrue(all(
            row["branch_count"] == 49
            and row["control_count"] == 2
            and len(row["ordered_controls"]) == 2
            and len(row["branches"]) == 49
            for row in roots
        ))
        for row in roots:
            ordinals = {
                (
                    branch["selector730_ordinal"],
                    branch["sibling_ordinal"],
                )
                for branch in row["branches"]
            }
            self.assertEqual(
                ordinals,
                {(left, right) for left in range(7) for right in range(7)},
            )
            self.assertTrue(all(
                len(branch["ordered_selected_terminal_roots"]) == 2
                and branch["candidate_line_widths_raw_g1n_px"]
                and branch["current_line_widths_raw_g1n_px"]
                for branch in row["branches"]
            ))

    def test_terminal_families_are_fixed_read_only_identifiers(self) -> None:
        families = self.private["terminal_families"]
        self.assertEqual(len(families), 18)
        self.assertEqual(
            len({row["family_identifier_sha256"] for row in families}),
            18,
        )
        self.assertTrue(all(
            row["terminal_count"] == 7
            and len(row["terminal_roots"]) == 7
            and row["source_candidate_dispatch_identical"]
            and row["read_only"]
            for row in families
        ))
        selector730 = next(
            row for row in families if row["selector"] == 730
        )
        self.assertEqual(
            (
                selector730["candidate_terminal_sha256"],
                selector730["current_terminal_sha256"],
                selector730["source_terminal_sha256"],
            ),
            (
                BUILDER.EXPECTED_SELECTOR_TERMINAL_CANDIDATE_SHA256,
                BUILDER.EXPECTED_SELECTOR_TERMINAL_CURRENT_SHA256,
                BUILDER.EXPECTED_SELECTOR_TERMINAL_SOURCE_SHA256,
            ),
        )

    def test_assignment_matches_root_atomic_partition(self) -> None:
        partition = self.public["assignment_partition"]
        self.assertEqual(
            (
                partition["status"],
                partition["assignment_chunk_count"],
                partition["candidate_sites_partitioned"],
                partition["same_gap_roots_partitioned"],
                partition["root_split_count"],
                partition["same_gap_root_to_chunk_sha256"],
            ),
            (
                "validated",
                2,
                41,
                37,
                0,
                "DC099FAF416D8EC82E495E050832350E780CD3638279016A96056A711EC6C4A3",
            ),
        )
        candidate_sites = self.private["scope"]["candidate_sites"]
        same_gap_roots = {
            row["root"] for row in self.private["cartesian_roots"]
        }
        assignment = json.loads(
            BUILDER.OPTIONAL_ASSIGNMENT_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(
            BUILDER.validate_assignment_partition(
                assignment, candidate_sites, same_gap_roots
            )["same_gap_root_to_chunk_sha256"],
            partition["same_gap_root_to_chunk_sha256"],
        )

        split = copy.deepcopy(assignment)
        duplicated_root = next(iter(same_gap_roots))
        owner = next(
            chunk
            for chunk in split["chunks"]
            if duplicated_root in chunk["roots"]
        )
        other = next(chunk for chunk in split["chunks"] if chunk is not owner)
        other["roots"].append(duplicated_root)
        with self.assertRaisesRegex(
            BUILDER.CartesianManifestError, "assignment root split"
        ):
            BUILDER.validate_assignment_partition(
                split, candidate_sites, same_gap_roots
            )

        omitted = copy.deepcopy(assignment)
        omitted["chunks"][0]["sites"].pop()
        with self.assertRaisesRegex(
            BUILDER.CartesianManifestError,
            "assignment candidate-site partition drifted",
        ):
            BUILDER.validate_assignment_partition(
                omitted, candidate_sites, same_gap_roots
            )

    def test_risk_is_evidence_only_and_public_is_source_free(self) -> None:
        proof = self.public["proof"]
        self.assertEqual(proof["semantic_decision_rows"], 0)
        self.assertEqual(proof["source_only_action_count"], 0)
        self.assertTrue(proof["terminal_records_read_only"])
        self.assertTrue(proof["same_gap_root_atomicity_required"])
        self.assertFalse(proof["automatic_space_or_grammar_repair_by_vm"])
        self.assertFalse(proof["full_dialogue_rebuild_performed"])
        self.assertFalse(proof["steam_write_performed"])
        self.assertEqual(
            self.public["risk"],
            {
                "linebreak_change_branches": 0,
                "maximum_positive_raw_g1n_delta_px": 480,
                "outer_space_protected_sites": 0,
                "positive_expansion_branches": 870,
                "right_boundary_sites": 18,
            },
        )
        BUILDER.assert_source_free(self.public)
        public_text = self.public_content.decode("utf-8")
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+){0,2}\b", public_text))
        self.assertNotIn('"translation"', public_text.lower())

    def test_outputs_are_frozen_and_reproducible(self) -> None:
        self.assertEqual(
            {
                name: BUILDER.sha256_file(path)
                for name, path in {
                    "selector730_assignment_builder":
                        BUILDER.ASSIGNMENT_BUILDER_PATH,
                    "selector730_assignment_private":
                        BUILDER.OPTIONAL_ASSIGNMENT_PATH,
                    "selector730_assignment_public":
                        BUILDER.ASSIGNMENT_PUBLIC_PATH,
                }.items()
            },
            {
                name: BUILDER.EXPECTED_INPUT_SHA256[name]
                for name in (
                    "selector730_assignment_builder",
                    "selector730_assignment_private",
                    "selector730_assignment_public",
                )
            },
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.private_content),
            BUILDER.EXPECTED_PRIVATE_OUTPUT_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.public_content),
            BUILDER.EXPECTED_PUBLIC_OUTPUT_SHA256,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PRIVATE_OUTPUT.read_bytes(),
            self.private_content,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            self.public_content,
        )
        self.assertEqual(BUILDER.main(["--check"]), 0)
        repeated = BUILDER.build_outputs()
        self.assertEqual(repeated[0], self.private_content)
        self.assertEqual(repeated[1], self.public_content)


if __name__ == "__main__":
    unittest.main()
