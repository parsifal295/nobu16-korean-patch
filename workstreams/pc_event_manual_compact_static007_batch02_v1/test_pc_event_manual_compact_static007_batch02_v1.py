#!/usr/bin/env python3
"""Regression tests for the private manual_compact Static Patch 007 batch 02."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_event_manual_compact_static007_batch02_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("manual_compact_static007_batch02_under_test", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class ManualCompactStatic007Batch02Tests(unittest.TestCase):
    def test_static007_target_layouts(self) -> None:
        builder.validate_authored_targets()
        for entry_id, target in builder.TARGETS.items():
            lines = builder.base.line_metrics(target)
            expected_raw, expected_effective = builder.TARGET_LAYOUTS[entry_id]
            self.assertLessEqual(len(lines), 4)
            self.assertEqual(tuple(line["raw_g1n_width_px"] for line in lines), expected_raw)
            self.assertEqual(tuple(line["effective_width_px"] for line in lines), expected_effective)
            for line in lines:
                self.assertLessEqual(line["raw_g1n_width_px"], 1440)
                self.assertLessEqual(line["effective_width_px"], 912)
                self.assertTrue(line["passes_static_patch_007"])

    def test_strict_batch01_context_and_exact_two_diff(self) -> None:
        _event, before, _raw, predecessor_profile, _audit = builder.load_predecessor()
        self.assertEqual(predecessor_profile, builder.EXPECTED_PREDECESSOR_PROFILE)
        for entry_id in builder.CHANGED_IDS:
            self.assertNotEqual(before.texts[entry_id], builder.TARGETS[entry_id])
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(bundle.audit["actual_changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(bundle.audit["actual_changed_row_count"], 2)
        self.assertEqual(len(bundle.audit["exact_two_row_diff"]), 2)
        self.assertEqual(len(bundle.audit["rows"]), len(builder.SCENE_IDS))
        self.assertEqual(set(bundle.audit["source_profiles"]["direct_pc_contexts"]), {"jp", "en", "sc", "tc"})
        for row in bundle.audit["rows"]:
            self.assertTrue(row["target_lines"])
            self.assertTrue(row["target_static_patch_007_passes"])
            if row["changed"]:
                self.assertEqual(row["current_quality_conflict_check"]["status"], "PASS")
                self.assertIsNotNone(row["historical_vs_current"])

    def test_private_candidate_exactness(self) -> None:
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["network_operation_performed"])
        self.assertFalse(result["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
