#!/usr/bin/env python3
"""Regression tests for the private Steam-PC event semantic reflow candidate."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_semantic_reflow_wave54_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_event_semantic_reflow_wave54_v1", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SemanticReflowCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()

    def test_scope_is_exactly_the_eight_reviewed_ids(self):
        self.assertEqual(
            tuple(change.entry_id for change in self.builder.CHANGES),
            (3202, 3900, 3934, 4140, 8510, 8723, 9359, 10045),
        )
        self.assertEqual(set(self.builder.PC_JP_INDEX_MAP), {change.entry_id for change in self.builder.CHANGES})

    def test_literals_have_complete_color_spans_and_external_line_breaks(self):
        for change in self.builder.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                self.assertEqual(change.target.count("\n"), 2)
                self.builder.assert_color_spans_complete_and_lf_external(change.target, change.entry_id)
                self.assertEqual(self.builder.text_hash(change.target), change.target_utf16le_sha256)

    def test_prepare_candidate_reparses_and_changes_only_declared_rows(self):
        bundle = self.builder.prepare_candidate()
        self.assertEqual(bundle.audit["changed_ids"], [3202, 3900, 3934, 4140, 8510, 8723, 9359, 10045])
        self.assertEqual(bundle.audit["changed_cell_count"], 8)
        self.assertTrue(bundle.audit["layout_validation"]["all_manual_lf_outside_color_spans"])
        self.assertEqual(bundle.output_profile, self.builder.EXPECTED_OUTPUT_PROFILE)

    def test_private_write_and_verify(self):
        self.builder.TMP_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".wave54-test-", dir=self.builder.TMP_ROOT) as temporary:
            candidate = Path(temporary) / "candidate"
            bundle = self.builder.prepare_candidate()
            result = self.builder.write_candidate(bundle, candidate)
            self.assertFalse(result["steam_game_resource_written"])
            verified = self.builder.verify_private(candidate)
            self.assertFalse(verified["steam_game_resource_written"])
            self.assertEqual(verified["changed_cell_count"], 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
