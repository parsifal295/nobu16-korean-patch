#!/usr/bin/env python3
"""Focused tests for the immutable selector-562 two-chunk assignment."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path


PATH = Path(__file__).with_name("build_pk_selector562_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location("selector562_assignment_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector562AssignmentTests(unittest.TestCase):
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
                coverage["source_only_action_count"],
                coverage["direct_pending_call_site_count"],
                coverage["prior_assembly_evidence_pending_root_count"],
                coverage["potential_current_pending_rows"],
            ),
            (54, 54, 60, 6, 0, 25, 25, 38),
        )
        self.assertEqual(
            (
                coverage["owned_overlap_root_count"],
                coverage["completed_selector_overlap_relation_count"],
                coverage["owned_overlap_pending_rows"],
                coverage["candidate_non_display_root_count"],
                coverage["direct_pending_non_display_root_count"],
            ),
            (3, 3, 6, 0, 0),
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

    def test_templates_and_completed_owned_roots_form_one_atom(self) -> None:
        atoms = self.private["identical_template_atoms"]
        self.assertEqual(sorted(map(len, atoms)), [2, 2, 3, 4, 8])
        template_roots = {root for atom in atoms for root in atom}
        self.assertEqual(len(template_roots), 19)
        root_to_chunk = {
            root: chunk["chunk_id"]
            for chunk in self.private["chunks"] for root in chunk["roots"]
        }
        for atom in atoms:
            self.assertEqual(len({root_to_chunk[root] for root in atom}), 1)

        union = self.private["assignment_atom_union"]
        union_roots = set(union["roots"])
        self.assertEqual((len(union_roots), len(union["pending_coordinates"])), (22, 10))
        self.assertEqual(len({root_to_chunk[root] for root in union_roots}), 1)
        owned = {
            row["root"] for row in self.private["completed_selector_overlap"]["relations"]
        }
        self.assertEqual(len(owned), 3)
        self.assertFalse(template_roots & owned)
        self.assertEqual(union_roots, template_roots | owned)
        self.assertEqual(
            (
                self.public["coverage"]["template_pending_root_count"],
                self.public["coverage"]["template_pending_row_count"],
            ),
            (4, 4),
        )
        self.assertFalse(self.public["assignment"]["assignment_atom_union_split"])

    def test_evidence_terminals_and_exclusions_are_read_only(self) -> None:
        coverage = self.public["coverage"]
        self.assertEqual(
            (
                coverage["prior_assembly_evidence_pending_root_count"],
                coverage["prior_assembly_evidence_pending_row_count"],
                coverage["terminal_prior_evidence_pending_count"],
            ),
            (25, 36, 7),
        )
        evidence = self.private["prior_pending_evidence"]
        self.assertFalse(evidence["automatic_status_promotion_authorized"])
        self.assertEqual(evidence["terminal_runtime_review"], "verified_read_only")

        ownership = self.private["shared_terminal_ownership"]
        self.assertEqual(ownership["owner"], "assignment_scope")
        self.assertEqual(ownership["chunk_ids"], [])
        self.assertFalse(ownership["automatic_status_promotion_authorized"])
        manifest = ownership["terminal_manifest"]
        self.assertEqual(len(manifest), 7)
        self.assertTrue(all(
            row["candidate_current_identical"]
            and row["runtime_review"] == "verified"
            and len(row["raw_record_sha256"]) == 64
            for row in manifest
        ))
        compatibility = self.public["terminal_compatibility"]
        self.assertEqual(
            compatibility["ordered_register_counts"],
            {"archaic": 1, "high_formal": 2, "plain": 2, "polite": 2},
        )
        self.assertEqual(
            Counter(compatibility["context_terminal_nonempty_counts"].values()),
            Counter({0: 3}),
        )
        self.assertFalse(compatibility["context_terminals_authoritative"])

        repair = self.private["source_only_repair"]
        self.assertEqual(repair["action_count"], 0)
        self.assertEqual(len(repair["sites"]), 6)
        self.assertEqual(self.public["assignment"]["same_gap_atom_count"], 0)
        BUILDER.assert_source_free(self.public)
        self.assertFalse(self.public["steam_write_performed"])

    def test_outputs_are_reproducible_and_frozen(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        repeated = BUILDER.build_outputs()
        self.assertEqual(repeated[0], self.private_content)
        self.assertEqual(repeated[1], self.public_content)


if __name__ == "__main__":
    unittest.main()
