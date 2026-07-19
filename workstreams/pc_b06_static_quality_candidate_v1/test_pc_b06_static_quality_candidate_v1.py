#!/usr/bin/env python3
"""Focused invariants for the private PC-only B06 candidate."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_pc_b06_static_quality_candidate_v1 as candidate  # noqa: E402


class PcB06StaticQualityCandidateTests(unittest.TestCase):
    def test_prepared_candidate_has_exact_two_slot_scope(self) -> None:
        bundle = candidate.prepare_candidate()
        self.assertEqual(
            candidate.TARGET_OUTPUT_PROFILE,
            bundle.output_profile,
        )
        changed = []
        for block_id, (before_block, after_block) in enumerate(
            zip(bundle.current.archive.blocks, bundle.candidate_archive.blocks)
        ):
            for before, after in zip(before_block.records, after_block.records):
                if before.data != after.data:
                    changed.append((block_id, before.record_id))
        self.assertEqual([(6, 3144), (6, 3455)], changed)
        self.assertEqual(
            ["6:3144:0", "6:3455:0"],
            [proposal.slot for proposal in candidate.PROPOSALS],
        )

    def test_targets_keep_manual_breaks_and_controls(self) -> None:
        bundle = candidate.prepare_candidate()
        for proposal in candidate.PROPOSALS:
            before = bundle.current.archive.blocks[6].records[proposal.record_id]
            after = bundle.candidate_archive.blocks[6].records[proposal.record_id]
            self.assertEqual(proposal.old.count("\n"), proposal.new.count("\n"))
            self.assertEqual(candidate.opaque_skeleton(before), candidate.opaque_skeleton(after))
            self.assertEqual(proposal.old, candidate.texts(before)[0])
            self.assertEqual(proposal.new, candidate.texts(after)[0])


if __name__ == "__main__":
    unittest.main()
