#!/usr/bin/env python3
"""Regression tests for the private PC Block-17 static candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_b17_static_quality_candidate_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_b17_static_candidate_under_test", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PcB17StaticQualityCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.bundle = cls.builder.prepare_candidate()
        cls.rows = {row["slot"]: row for row in cls.bundle.rows}

    def test_pc_input_hashes_and_block17_topology_are_pinned(self) -> None:
        self.assertEqual(4, len(self.builder.INPUTS))
        self.assertEqual("F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB", self.bundle.input_profiles["base_ko_w45"]["packed_sha256"])
        self.assertEqual("EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4", self.bundle.input_profiles["base_jp_pc"]["packed_sha256"])
        self.assertEqual("0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092", self.bundle.input_profiles["pk_ko_w45"]["packed_sha256"])
        self.assertEqual("31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210", self.bundle.input_profiles["pk_jp_pc"]["packed_sha256"])
        self.assertEqual(33, self.bundle.input_profiles["base_ko_w45"]["block17_records"])
        self.assertEqual(1_159, self.bundle.input_profiles["pk_ko_w45"]["block17_records"])
        self.assertEqual(2_256, self.bundle.input_profiles["pk_ko_w45"]["block17_literals"])

    def test_exact_31_literal_scope_and_root_revised_targets(self) -> None:
        proposals = self.builder.proposal_map()
        self.assertEqual(31, len(proposals))
        self.assertEqual(31, len(self.builder.EXPECTED_APPLY_RECORDS))
        self.assertEqual(31, len(self.rows))
        self.assertEqual("으로 돌아서", proposals[(17, 510, 2)].new)
        self.assertEqual("는 아군이다. 피아를 혼동하지 마라!", proposals[(17, 872, 1)].new)
        self.assertNotIn((17, 920, 0), proposals)
        self.assertNotIn((17, 920, 1), proposals)
        self.assertEqual({(17, 920, 0), (17, 920, 1)}, set(self.builder.HOLD_SLOTS))

    def test_all_unselected_literals_and_opaque_controls_are_unchanged(self) -> None:
        proposals = self.builder.proposal_map()
        before_block = self.bundle.current_archive.blocks[17]
        after_block = self.bundle.candidate_archive.blocks[17]
        for before, after in zip(before_block.records, after_block.records):
            targeted = {(17, before.record_id, p.literal_id): p for p in self.builder.APPLY_PROPOSALS if p.record_id == before.record_id}
            if targeted:
                self.assertEqual(self.builder.opaque_skeleton(before), self.builder.opaque_skeleton(after))
            else:
                self.assertEqual(before.data, after.data)
            for literal_id, (old, new) in enumerate(zip(self.builder.literal_texts(before), self.builder.literal_texts(after))):
                proposal = proposals.get((17, before.record_id, literal_id))
                if proposal is None:
                    self.assertEqual(old, new)
                else:
                    self.assertEqual(proposal.new, new)
                    self.assertEqual(proposal.old, old)

    def test_manual_lf_and_placeholder_control_topology_are_preserved(self) -> None:
        for proposal in self.builder.APPLY_PROPOSALS:
            row = self.rows[proposal.slot]
            self.assertEqual(proposal.old.count("\n"), proposal.new.count("\n"))
            self.assertEqual(row["manual_lf_count"], proposal.old.count("\n"))
            self.assertTrue(row["opaque_skeleton_unchanged"])
            self.assertEqual(
                row["current_record"]["opaque_skeleton_sha256"],
                row["candidate_record"]["opaque_skeleton_sha256"],
            )

    def test_raw_and_packed_roundtrips_and_output_profile_are_pinned(self) -> None:
        self.assertEqual(self.builder.TARGET_OUTPUT_PROFILE, self.bundle.output_profile)
        self.assertEqual(
            self.builder.rebuild_raw_msggame(self.bundle.candidate_archive),
            self.bundle.candidate_raw,
        )
        self.assertEqual(
            self.builder.decompress_wrapper(self.builder.rebuild_packed_msggame(self.bundle.candidate_packed))[1],
            self.bundle.candidate_raw,
        )


if __name__ == "__main__":
    unittest.main()
