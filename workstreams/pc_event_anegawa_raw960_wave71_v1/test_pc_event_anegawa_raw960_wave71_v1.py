#!/usr/bin/env python3
"""Focused tests for the private W71 Anegawa semantic-linebreak candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
MODULE_PATH = SCRIPT.with_name("build_pc_event_anegawa_raw960_wave71_v1.py")


def load_builder() -> object:
    spec = importlib.util.spec_from_file_location("wave71_test_builder", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Wave71Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.bundle = cls.builder.prepare(require_output_profiles=True)

    def test_all_anegawa_rows_have_a_manual_semantic_reflow(self) -> None:
        builder = self.builder
        expected = tuple(range(5777, 5803)) + tuple(range(5885, 5915))
        self.assertEqual(builder.scene_ids(), expected)
        self.assertEqual(len(builder.REFLOW_UNIT_COUNTS), 56)
        rows = {row["entry_id"]: row for row in self.bundle.rows}
        self.assertEqual(tuple(rows), expected)
        for entry_id in expected:
            row = rows[entry_id]
            self.assertTrue(row["korean_visible_text_preserved"])
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertEqual(
                builder.normalized_text(row["w70_current_ko"]),
                builder.normalized_text(row["target_ko"]),
            )
            self.assertEqual(
                row["control_signature"],
                builder.w70.control_signature(row["w70_current_ko"]),
            )
            self.assertLessEqual(row["target_line_count"], 4)
            self.assertGreaterEqual(row["target_line_count"], 1)
            builder.assert_no_break_inside_tag(row["target_ko"])

    def test_every_live_line_stays_inside_the_observed_raw_960px_limit(self) -> None:
        for row in self.bundle.rows:
            for line in row["target_lines"]:
                self.assertEqual(
                    line["raw_g1n_width_px"],
                    line["full_width_character_count"] * 48 + line["half_width_character_count"] * 24,
                )
                self.assertEqual(
                    line["effective_width_px"],
                    (line["raw_g1n_width_px"] * 30 + 47) // 48,
                )
                self.assertLessEqual(line["raw_g1n_width_px"], 960)
                self.assertFalse(line["over_live_raw_960px"])

    def test_pinned_candidate_profile_and_full_scene_scope(self) -> None:
        builder = self.builder
        bundle = self.bundle
        self.assertEqual(bundle.final_record_counts, builder.expected_final_record_counts())
        self.assertEqual(sum(bundle.final_record_counts.values()), builder.EXPECTED_TOTAL_RECORDS)
        self.assertEqual(
            {resource: builder.profile_dict(value) for resource, value in bundle.profiles.items()},
            builder.expected_final_profile_dicts(),
        )
        coverage = bundle.audit["coverage"]
        self.assertEqual(coverage["reviewed_scene_rows"], 56)
        self.assertEqual(coverage["manual_linebreak_reviewed_rows"], list(builder.scene_ids()))
        self.assertEqual(coverage["remaining_full_pk_event_body_rows"], 7950)


if __name__ == "__main__":
    unittest.main()
