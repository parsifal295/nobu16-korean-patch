#!/usr/bin/env python3
"""Regression tests for the independent terminal-boundary detector."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
DETECTOR_PATH = WORKSTREAM / "terminal_boundary_detector_v1.py"


def load_detector() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_terminal_boundary_detector_test_v1",
        DETECTOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {DETECTOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DETECTOR = load_detector()


class TerminalBoundaryClassifierTests(unittest.TestCase):
    def assert_boundary(self, prefix: str, suffix: str) -> None:
        self.assertIsNotNone(
            DETECTOR.classify_completed_prefix(prefix),
            prefix,
        )
        self.assertIsNotNone(
            DETECTOR.classify_terminal_suffix(suffix),
            suffix,
        )

    def test_known_family1096_regressions_are_classified(self) -> None:
        self.assert_boundary("있다", "합니다")
        self.assert_boundary("전하겠습니다", "합니다")
        self.assert_boundary("하라", "합니다")

    def test_plain_and_formal_call_variants_are_terminal_suffixes(self) -> None:
        for suffix in (
            "다",
            "한다",
            "했다",
            "했습니다",
            "하겠다",
            "하겠소",
        ):
            with self.subTest(suffix=suffix):
                self.assertIsNotNone(
                    DETECTOR.classify_terminal_suffix(suffix)
                )

    def test_nonterminal_stem_and_full_called_sentence_are_ignored(self) -> None:
        self.assertIsNone(DETECTOR.classify_completed_prefix("전하겠"))
        self.assertIsNone(
            DETECTOR.classify_terminal_suffix("명령을 전합니다")
        )
        self.assertIsNone(
            DETECTOR.classify_terminal_suffix("라고 합니다")
        )
        self.assertIsNone(
            DETECTOR.classify_terminal_suffix(" 때문에")
        )

    def test_private_text_output_cannot_escape_tmp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary) / "private.json"
            with self.assertRaises(DETECTOR.TerminalBoundaryError):
                DETECTOR.validate_private_output(
                    include_text=True,
                    output=outside,
                )
        DETECTOR.validate_private_output(
            include_text=True,
            output=DETECTOR.REPO / "tmp" / "private.json",
        )


class TerminalBoundaryArchiveRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = DETECTOR.detect_resource(
            "base_msggame",
            DETECTOR.AUDIT.DEFAULT_BASE,
        )
        cls.pk = DETECTOR.detect_resource(
            "pk_msggame",
            DETECTOR.AUDIT.DEFAULT_PK,
        )

    def issues_at(
        self,
        resource: Any,
        coordinate: tuple[int, int, int],
    ) -> tuple[Any, ...]:
        block_id, record_id, literal_id = coordinate
        return tuple(
            issue
            for issue in resource.issues
            if (
                issue.block_id,
                issue.record_id,
                issue.literal_id,
            )
            == coordinate
        )

    def test_every_record_decodes_and_every_call_site_is_scanned(self) -> None:
        self.assertEqual(
            self.base.record_count,
            self.base.decoded_record_count,
        )
        self.assertEqual(
            self.pk.record_count,
            self.pk.decoded_record_count,
        )
        self.assertEqual(self.base.call_site_count, 4406)
        self.assertEqual(self.pk.call_site_count, 5771)

    def test_root376_mixed_terminal_variants_are_detected(self) -> None:
        issues = self.issues_at(self.pk, (15, 1545, 0))
        self.assertTrue(issues)
        self.assertEqual(
            {issue.call_target for issue in issues},
            {"0:376"},
        )
        self.assertTrue(
            {"copula", "exist"}.issubset(
                {issue.suffix_family for issue in issues}
            )
        )

    def test_family1096_runtime_boundary_is_detected(self) -> None:
        issues = self.issues_at(self.pk, (9, 3967, 0))
        self.assertTrue(issues)
        self.assertEqual(
            {issue.call_target for issue in issues},
            {"0:1096"},
        )

    def test_hara_plus_hamnida_runtime_boundary_is_detected(self) -> None:
        issues = self.issues_at(self.pk, (7, 2834, 1))
        self.assertTrue(issues)
        self.assertIn(
            "imperative",
            {issue.prefix_family for issue in issues},
        )
        self.assertEqual(
            {issue.call_target for issue in issues},
            {"0:466"},
        )

    def test_default_report_is_source_free(self) -> None:
        report = DETECTOR.build_report((self.base, self.pk))
        self.assertTrue(
            report["detector_contract"]["tracked_output_is_source_free"]
        )
        for issue in report["issues"]:
            self.assertNotIn("prefix", issue)
            self.assertNotIn("suffix", issue)
            self.assertNotIn("combined", issue)

    def test_current_candidate_issue_counts_are_bound_to_hashes(self) -> None:
        self.assertEqual(
            self.base.sha256,
            "44828B27368FB74EF906DC167DCAF1BA"
            "54129A4313F7EDA3C0668777BB86E276",
        )
        self.assertEqual(
            self.pk.sha256,
            "0330917524A47974618317A8EC56C4B"
            "471672DA5AD07000A8C5D8A7CCFB8A05F",
        )
        self.assertEqual(len(self.base.issues), 254)
        self.assertEqual(len(self.pk.issues), 201)


if __name__ == "__main__":
    unittest.main()
