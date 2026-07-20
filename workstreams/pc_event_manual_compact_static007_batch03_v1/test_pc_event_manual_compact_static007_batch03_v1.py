#!/usr/bin/env python3
"""Private tests for the PC event manual_compact Static Patch 007 batch 03."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_manual_compact_static007_batch03_v1.py")
SPEC = importlib.util.spec_from_file_location("manual_compact_static007_batch03", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class ManualCompactStatic007Batch03Tests(unittest.TestCase):
    def test_static007_target_layouts(self) -> None:
        builder.validate_authored_targets()
        for entry_id, target in builder.TARGETS.items():
            metrics = builder.base.base.line_metrics(target)
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

    def test_strict_batch02_context_and_exact_two_diff(self) -> None:
        _event, before, _raw, predecessor_profile, _audit = builder.load_predecessor()
        self.assertEqual(predecessor_profile, builder.EXPECTED_PREDECESSOR_PROFILE)
        for entry_id in builder.CHANGED_IDS:
            self.assertNotEqual(before.texts[entry_id], builder.TARGETS[entry_id])
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(bundle.audit["actual_changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(bundle.audit["actual_changed_row_count"], 2)
        self.assertEqual(len(bundle.audit["exact_two_row_diff"]), 2)
        self.assertEqual(bundle.audit["coverage"]["reviewed_row_ids"], list(builder.SCENE_IDS))
        self.assertFalse(bundle.audit["source_policy"]["korean_sentence_shortened_or_deleted"])

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
