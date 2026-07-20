#!/usr/bin/env python3
"""Private tests for the PC event manual-linebreak Static Patch 007 batch 06."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_manual_compact_static007_batch06_v1.py")
SPEC = importlib.util.spec_from_file_location("manual_compact_static007_batch06", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class ManualCompactStatic007Batch06Tests(unittest.TestCase):
    def test_static007_target_layouts(self) -> None:
        builder.validate_authored_targets()
        self.assertEqual(len(builder.CHANGED_IDS), 35)
        self.assertFalse(set(builder.CHANGED_IDS) & set(builder.RUNTIME_HOLD_IDS))
        self.assertEqual(len(builder.RUNTIME_HOLD_IDS), 18)
        for entry_id, target in builder.TARGETS.items():
            metrics = builder.engine.base.base.line_metrics(target)
            self.assertGreaterEqual(len(metrics), 1)
            self.assertLessEqual(len(metrics), 4)
            self.assertTrue(all(line["passes_static_patch_007"] for line in metrics))
            self.assertEqual(
                tuple(line["raw_g1n_width_px"] for line in metrics),
                builder.TARGET_LAYOUTS[entry_id][0],
            )
            self.assertEqual(
                tuple(line["effective_width_px"] for line in metrics),
                builder.TARGET_LAYOUTS[entry_id][1],
            )

    def test_strict_batch05_context_and_layout_only_diff(self) -> None:
        _event, before, _raw, predecessor_profile, _audit = builder.load_predecessor()
        self.assertEqual(predecessor_profile, builder.EXPECTED_PREDECESSOR_PROFILE)
        for entry_id in builder.CHANGED_IDS:
            self.assertEqual(
                builder.non_whitespace(before.texts[entry_id]),
                builder.non_whitespace(builder.TARGETS[entry_id]),
            )
            self.assertNotEqual(before.texts[entry_id], builder.TARGETS[entry_id])
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(bundle.audit["actual_changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(bundle.audit["actual_changed_row_count"], 35)
        self.assertEqual(len(bundle.audit["exact_multi_row_diff"]), 35)
        self.assertEqual(bundle.audit["coverage"]["reviewed_row_ids"], list(builder.SCENE_IDS))
        self.assertEqual(len(bundle.audit["coverage"]["scene_groups"]), 7)
        self.assertEqual(bundle.audit["coverage"]["runtime_hold_excluded_ids"], list(builder.RUNTIME_HOLD_IDS))
        self.assertEqual(bundle.audit["coverage"]["static_retained_manual_ids"], list(builder.STATIC_RETAINED_MANUAL_IDS))
        self.assertTrue(bundle.audit["source_policy"]["layout_only_non_whitespace_integrity_verified"])
        self.assertFalse(bundle.audit["source_policy"]["korean_sentence_shortened_or_deleted"])

    def test_private_candidate_exactness(self) -> None:
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(result["runtime_hold_excluded_ids"], list(builder.RUNTIME_HOLD_IDS))
        self.assertEqual(result["static_retained_manual_ids"], list(builder.STATIC_RETAINED_MANUAL_IDS))
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["network_operation_performed"])
        self.assertFalse(result["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
