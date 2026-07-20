#!/usr/bin/env python3
"""Regression checks for the private W93 Mōri Motonari candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_mori_motonari_quality_wave93_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave93_under_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class Wave93Tests(unittest.TestCase):
    def test_scope_and_static_layout_contract(self) -> None:
        builder.validate_static_targets()
        self.assertEqual(builder.SCENE_IDS, tuple(range(5977, 6000)))
        self.assertEqual(len(builder.CHANGED_IDS), 15)
        self.assertEqual(len(builder.RETAINED_IDS), 8)
        self.assertEqual(set(builder.CHANGED_IDS) | set(builder.RETAINED_IDS), set(builder.SCENE_IDS))
        self.assertFalse(set(builder.CHANGED_IDS) & set(builder.RETAINED_IDS))
        self.assertFalse(builder.SCENE_RUNTIME_RESERVATIONS)
        self.assertFalse(builder.ROW_RUNTIME_TOKENS)

    def test_predecessor_and_output_profile_are_pinned(self) -> None:
        self.assertIsNotNone(builder.EXPECTED_OUTPUT_PROFILE)
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(tuple(bundle.changed), builder.CHANGED_IDS)
        self.assertEqual(bundle.audit["coverage"]["changed_row_count"], 15)
        self.assertEqual(bundle.audit["coverage"]["unchanged_after_review_count"], 8)

    def test_candidate_is_byte_exact(self) -> None:
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["runtime_proven"])

    def test_each_reported_line_obeys_static_patch_007_gate(self) -> None:
        bundle = builder.prepare(require_output_profile=True)
        for row in bundle.rows:
            self.assertGreaterEqual(row["target_manual_line_count"], 1)
            self.assertLessEqual(row["target_manual_line_count"], 4)
            self.assertEqual(row["runtime_tokens"], [])
            self.assertEqual(row["runtime_reservations"], [])
            self.assertFalse(row["runtime_proven"])
            for line in row["target_lines"]:
                self.assertLessEqual(line["raw_g1n_width_px"], 960)
                self.assertFalse(line["over_live_raw_960px"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
