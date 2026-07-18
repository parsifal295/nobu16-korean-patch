#!/usr/bin/env python3
"""Regression tests for the private PC Block 15 candidate builder."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from dataclasses import replace
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_block15_runtime_candidate_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("block15_candidate_under_test", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Block15RuntimeCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        # Read-only preparation validates every W45/JP/record/output pin.
        cls.bundle = cls.builder.prepare_candidate()
        cls.rows = {row["slot"]: row for row in cls.bundle.rows}

    def test_scope_and_preimage_pin_coverage_are_exact(self) -> None:
        self.assertEqual(17, len(self.builder.APPLY_PROPOSALS))
        self.assertEqual(1, len(self.builder.HOLD_PROPOSALS))
        self.assertEqual(18, len(self.builder.PROPOSALS))
        self.assertEqual(18, len(self.bundle.rows))
        for resource in self.builder.RESOURCE_ORDER:
            expected = {proposal.coordinate_text for proposal in self.builder.PROPOSALS if proposal.resource == resource}
            self.assertEqual(expected, set(self.builder.RECORD_PREIMAGE_PINS[resource]))

    def test_all_applied_rows_preserve_nonliteral_runtime_structure(self) -> None:
        for proposal in self.builder.APPLY_PROPOSALS:
            row = self.rows[proposal.slot_text]
            self.assertEqual("apply", row["disposition"])
            self.assertEqual(1, row["replacement"]["current_slot_occurrences"])
            before = row["current_record"]
            after = row["proposed_target_record"]
            self.assertEqual(before["literal_count"], after["literal_count"])
            self.assertEqual(before["marker_topology_hex"], after["marker_topology_hex"])
            self.assertEqual(before["opaque_spans_hex"], after["opaque_spans_hex"])
            self.assertEqual(before["terminator_hex"], after["terminator_hex"])
            self.assertEqual(before["has_record_terminator"], after["has_record_terminator"])
            self.assertEqual(before["manual_lf_count"], after["manual_lf_count"])
            self.assertEqual(before["manual_lf_count_by_literal"], after["manual_lf_count_by_literal"])
            self.assertEqual(before["runtime_02xx_tokens"], after["runtime_02xx_tokens"])
            self.assertEqual(before["complete_0143_commands"], after["complete_0143_commands"])
            self.assertTrue(row["width_eaw"]["eligible_for_apply"])

    def test_width_hold_is_explicit_and_not_written(self) -> None:
        hold = self.builder.HOLD_PROPOSALS[0]
        row = self.rows[hold.slot_text]
        self.assertEqual("hold_width_excess", row["disposition"])
        self.assertFalse(row["width_eaw"]["eligible_for_apply"])
        self.assertEqual(720, row["width_eaw"]["current"]["max_width_px"])
        self.assertEqual(1152, row["width_eaw"]["proposed"]["max_width_px"])
        self.assertEqual(30, row["width_eaw"]["current"]["max_eaw_units"])
        self.assertEqual(48, row["width_eaw"]["proposed"]["max_eaw_units"])
        self.assertNotIn(hold.coordinate, {proposal.coordinate for proposal in self.builder.APPLY_PROPOSALS})

    def test_conflict_guards_fail_for_every_named_predecessor(self) -> None:
        seed = self.builder.APPLY_PROPOSALS[0]
        forbidden = (
            replace(seed, resource=self.builder.BASE_RESOURCE, coordinate=(15, 220)),  # W46 exact
            replace(seed, resource=self.builder.BASE_RESOURCE, coordinate=(6, 4146)),  # W48
            replace(seed, resource=self.builder.BASE_RESOURCE, coordinate=(9, 341)),  # W50
            replace(seed, resource=self.builder.BASE_RESOURCE, coordinate=(13, 83)),  # W51
            replace(seed, resource=self.builder.PK_RESOURCE, coordinate=(17, 42)),  # static composite
        )
        for proposal in forbidden:
            with self.subTest(proposal=proposal.coordinate):
                with self.assertRaises(self.builder.CandidateError):
                    self.builder.assert_no_scope_overlap((proposal,))

    def test_packed_output_profiles_and_evidence_are_pinned(self) -> None:
        self.assertEqual(
            self.builder.RECORD_EVIDENCE_SHA256,
            self.builder.sha256_bytes(self.builder.canonical_json(self.bundle.rows)),
        )
        for resource in self.builder.RESOURCE_ORDER:
            actual = self.builder.observed_profile(self.bundle.packed[resource], self.bundle.raw[resource])
            self.assertEqual(self.builder.TARGET_OUTPUT_PROFILES[resource], actual)


if __name__ == "__main__":
    unittest.main()
