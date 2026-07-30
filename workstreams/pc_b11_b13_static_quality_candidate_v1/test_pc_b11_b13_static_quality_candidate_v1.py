#!/usr/bin/env python3
"""Focused invariants for the private PC-only B11~B13 candidate."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_pc_b11_b13_static_quality_candidate_v1 as candidate  # noqa: E402


class PcB11B13StaticQualityCandidateTests(unittest.TestCase):
    def test_exact_eight_record_scope_and_output_pins(self) -> None:
        bundle = candidate.prepare_candidate()
        self.assertEqual(candidate.TARGET_OUTPUT_PROFILES, bundle.output_profiles)
        self.assertEqual(
            {(13, 258), (13, 260)},
            set(bundle.resources["base"].changed_records),
        )
        self.assertEqual(
            {(13, 260), (13, 262), (13, 353), (13, 452), (13, 575), (13, 615)},
            set(bundle.resources["pk"].changed_records),
        )
        self.assertEqual(8, sum(len(item.changed_records) for item in bundle.resources.values()))

    def test_targets_preserve_lf_controls_and_source_pair_topology(self) -> None:
        bundle = candidate.prepare_candidate()
        self.assertEqual(candidate.PAIR_EXPECTED, bundle.pair_profiles)
        for proposal in candidate.PROPOSALS:
            resource = bundle.resources[proposal.scope]
            before = resource.current.archive.blocks[13].records[proposal.record_id]
            after = resource.candidate_archive.blocks[13].records[proposal.record_id]
            self.assertEqual((proposal.old,), candidate.literal_texts(before))
            self.assertEqual((proposal.new,), candidate.literal_texts(after))
            self.assertEqual(proposal.old.count("\n"), proposal.new.count("\n"))
            self.assertEqual(candidate.opaque_skeleton(before), candidate.opaque_skeleton(after))


if __name__ == "__main__":
    unittest.main()
