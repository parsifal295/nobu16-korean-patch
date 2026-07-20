#!/usr/bin/env python3
"""Focused tests for the private W70 Anegawa static-patch-007 candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
MODULE_PATH = SCRIPT.with_name("build_pc_event_anegawa_static007_wave70_v1.py")


def load_builder() -> object:
    spec = importlib.util.spec_from_file_location("wave70_test_builder", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Wave70Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        # One pinned preparation supplies every test with the same source and
        # layout result, avoiding repeat decompression/recompression passes.
        cls.bundle = cls.builder.prepare(require_output_profiles=True)

    def test_anegawa_scope_is_exact_and_title_is_retained(self) -> None:
        builder = self.builder
        self.assertEqual(builder.scene_ids(), tuple(range(5777, 5803)) + tuple(range(5885, 5915)))
        self.assertEqual(len(builder.scene_ids()), 56)
        self.assertEqual(
            builder.EXPECTED_TARGET_IDS,
            (5780, 5784, 5785, 5790, 5792, 5795, 5802, 5885, 5886, 5887, 5906, 5909, 5912, 5913),
        )
        self.assertEqual(builder.EXPECTED_CLASS_COUNTS, {"fresh": 14, "already": 0, "override": 0})
        self.assertEqual(builder.EXPECTED_PK_BODY_NONEMPTY_COUNT, 8006)
        self.assertNotIn(13482, builder.EXPECTED_TARGET_IDS)

    def test_every_changed_line_uses_the_static007_four_line_contract(self) -> None:
        builder = self.builder
        rows = {row["entry_id"]: row for row in self.bundle.rows}
        targets = {target.entry_id: target for target in builder.TARGETS}
        self.assertEqual(set(rows), set(targets))
        for entry_id, target in targets.items():
            row = rows[entry_id]
            self.assertEqual(row["target_ko"], target.target_ko)
            self.assertEqual(row["direct_pc_jp"], target.direct_pc_jp)
            self.assertEqual(row["control_signature"], builder.control_signature(target.target_ko))
            self.assertLessEqual(row["target_line_count"], 4)
            self.assertEqual(row["target_line_count"], len(row["target_lines"]))
            for line in row["target_lines"]:
                self.assertEqual(
                    line["raw_g1n_width_px"],
                    line["full_width_character_count"] * 48 + line["half_width_character_count"] * 24,
                )
                self.assertEqual(
                    line["effective_width_px"],
                    (line["raw_g1n_width_px"] * 30 + 47) // 48,
                )
                self.assertEqual(
                    line["full_width_character_count"] + line["half_width_character_count"],
                    len(line["display_string"]),
                )
                self.assertLessEqual(line["raw_g1n_width_px"], 1440)
                self.assertLessEqual(line["effective_width_px"], 912)
                self.assertFalse(line["over_912px"])

    def test_pinned_candidate_profile_and_review_coverage(self) -> None:
        builder = self.builder
        bundle = self.bundle
        self.assertEqual(set(bundle.effective), set(builder.EXPECTED_TARGET_IDS))
        self.assertEqual(
            {name: len(values) for name, values in bundle.classifications.items()},
            {"fresh": 14, "already": 0, "override": 0},
        )
        self.assertEqual(bundle.final_record_counts, builder.expected_final_record_counts())
        self.assertEqual(sum(bundle.final_record_counts.values()), builder.EXPECTED_TOTAL_RECORDS)
        self.assertEqual(
            {resource: builder.profile_dict(value) for resource, value in bundle.profiles.items()},
            builder.expected_final_profile_dicts(),
        )
        coverage = bundle.audit["coverage"]
        self.assertFalse(coverage["semantic_completion"])
        self.assertEqual(coverage["reviewed_scene_rows"], 56)
        self.assertEqual(coverage["corrected_reviewed_rows"], list(builder.EXPECTED_TARGET_IDS))
        self.assertEqual(coverage["remaining_full_pk_event_body_rows"], 7950)


if __name__ == "__main__":
    unittest.main()
