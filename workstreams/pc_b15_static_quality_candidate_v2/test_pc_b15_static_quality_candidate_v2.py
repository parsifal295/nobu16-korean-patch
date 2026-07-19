"""Unittest coverage for the private PC B15 static-quality candidate v2."""

from __future__ import annotations

import unittest

from build_pc_b15_static_quality_candidate_v2 import (
    PRIVATE_OUTPUT_ROOT,
    SPECS,
    build_private_candidate,
    diff_check_private_candidate,
    verify_private_candidate,
)


class PcB15StaticQualityCandidateV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.build_report = build_private_candidate(PRIVATE_OUTPUT_ROOT)

    def test_builder_writes_the_two_expected_private_files(self) -> None:
        self.assertEqual(set(self.build_report), {"Base", "PK"})
        for spec in SPECS:
            self.assertTrue(
                (PRIVATE_OUTPUT_ROOT / spec.output_relative_path).is_file(),
                spec.name,
            )

    def test_verify_private_checks_w45_profile_and_ten_literal_scope(self) -> None:
        report = verify_private_candidate(PRIVATE_OUTPUT_ROOT)
        self.assertEqual(len(report["Base"]["changed_literals"]), 6)
        self.assertEqual(len(report["PK"]["changed_literals"]), 4)
        self.assertTrue(report["Base"]["parser_rebuild_exact"])
        self.assertTrue(report["PK"]["parser_rebuild_exact"])
        self.assertEqual(report["Base"]["outside_target_raw_diff_bytes"], 0)
        self.assertEqual(report["PK"]["outside_target_raw_diff_bytes"], 0)

    def test_diff_check_preserves_hold_and_non_target_raw_bytes(self) -> None:
        report = diff_check_private_candidate(PRIVATE_OUTPUT_ROOT)
        self.assertEqual(report["Base"]["raw_diff_bytes"], 22)
        self.assertEqual(report["PK"]["raw_diff_bytes"], 14)
        self.assertEqual(report["Base"]["outside_target_raw_diff_bytes"], 0)
        self.assertEqual(report["PK"]["outside_target_raw_diff_bytes"], 0)
        self.assertEqual(len(report["Base"]["hold_literals_unchanged"]), 4)
        self.assertEqual(len(report["PK"]["hold_literals_unchanged"]), 2)


if __name__ == "__main__":
    unittest.main()
