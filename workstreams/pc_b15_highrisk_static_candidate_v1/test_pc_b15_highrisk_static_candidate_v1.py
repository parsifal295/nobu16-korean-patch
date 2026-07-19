"""Unittest coverage for the isolated PC B15 highrisk grammar candidate v1."""

from __future__ import annotations

import unittest

from build_pc_b15_highrisk_static_candidate_v1 import (
    PRIVATE_OUTPUT_ROOT,
    SPECS,
    build_private_candidate,
    diff_check_private_candidate,
    verify_private_candidate,
)


class PcB15HighriskStaticCandidateV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.build_report = build_private_candidate(PRIVATE_OUTPUT_ROOT)

    def test_builder_creates_the_two_expected_private_files(self) -> None:
        self.assertEqual(set(self.build_report), {"Base", "PK"})
        for spec in SPECS:
            self.assertTrue(
                (PRIVATE_OUTPUT_ROOT / spec.output_relative_path).is_file(),
                spec.name,
            )

    def test_verify_private_enforces_one_target_per_pc_file(self) -> None:
        report = verify_private_candidate(PRIVATE_OUTPUT_ROOT)
        self.assertEqual(report["Base"]["changed_literals"], [[15, 2348, 0]])
        self.assertEqual(report["PK"]["changed_literals"], [[15, 2379, 0]])
        self.assertTrue(report["Base"]["target_opaque_skeleton_preserved"])
        self.assertTrue(report["PK"]["target_opaque_skeleton_preserved"])
        self.assertTrue(report["Base"]["parser_rebuild_exact"])
        self.assertTrue(report["PK"]["parser_rebuild_exact"])

    def test_diff_check_preserves_holds_and_expected_size_delta(self) -> None:
        report = diff_check_private_candidate(PRIVATE_OUTPUT_ROOT)
        self.assertEqual(report["Base"]["literal_byte_delta"], -8)
        self.assertEqual(report["PK"]["literal_byte_delta"], -8)
        self.assertEqual(report["Base"]["raw_size_delta"], -8)
        self.assertEqual(report["PK"]["raw_size_delta"], -8)
        self.assertEqual(len(report["Base"]["hold_records_unchanged"]), 3)
        self.assertEqual(len(report["PK"]["hold_records_unchanged"]), 3)


if __name__ == "__main__":
    unittest.main()
