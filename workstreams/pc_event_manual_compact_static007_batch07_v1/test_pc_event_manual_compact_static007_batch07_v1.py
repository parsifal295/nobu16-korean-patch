#!/usr/bin/env python3
"""Private tests for the PC event Static Patch 007 batch07 candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_manual_compact_static007_batch07_v1.py")
SPEC = importlib.util.spec_from_file_location("manual_compact_static007_batch07", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class ManualCompactStatic007Batch07Tests(unittest.TestCase):
    def test_static007_target_layouts(self) -> None:
        builder.validate_authored_targets()
        self.assertEqual(len(builder.CHANGED_IDS), 28)
        self.assertEqual(len(builder.RUNTIME_HOLD_IDS), 48)
        self.assertEqual(len(builder.STATIC_RETAINED_MANUAL_IDS), 7)
        self.assertEqual(builder.SOURCE_COMPLETE_RESTORATION_IDS, (3_820,))
        self.assertFalse(set(builder.CHANGED_IDS) & set(builder.RUNTIME_HOLD_IDS))
        for entry_id, target in builder.TARGETS.items():
            metrics = builder.base.line_metrics(target)
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

    def test_strict_restore_context_and_layout_only_diff(self) -> None:
        _event, before, _raw, predecessor_profile, _audit = builder.load_predecessor()
        self.assertEqual(predecessor_profile, builder.EXPECTED_PREDECESSOR_PROFILE)
        for entry_id in builder.LAYOUT_ONLY_CHANGED_IDS:
            self.assertEqual(
                builder.non_whitespace(before.texts[entry_id]),
                builder.non_whitespace(builder.TARGETS[entry_id]),
            )
            self.assertNotEqual(before.texts[entry_id], builder.TARGETS[entry_id])
        self.assertNotEqual(before.texts[3_820], builder.TARGETS[3_820])
        self.assertEqual(
            builder.base.control_signature(before.texts[3_820]),
            builder.base.control_signature(builder.TARGETS[3_820]),
        )
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(bundle.audit["actual_changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(bundle.audit["actual_changed_row_count"], 28)
        self.assertEqual(len(bundle.audit["exact_multi_row_diff"]), 28)
        self.assertEqual(bundle.audit["coverage"]["reviewed_row_ids"], list(builder.SCENE_IDS))
        self.assertEqual(len(bundle.audit["coverage"]["scene_groups"]), 10)
        self.assertEqual(bundle.audit["coverage"]["runtime_hold_excluded_ids"], list(builder.RUNTIME_HOLD_IDS))
        self.assertEqual(bundle.audit["coverage"]["static_retained_manual_ids"], list(builder.STATIC_RETAINED_MANUAL_IDS))
        self.assertFalse(bundle.audit["source_policy"]["layout_only_non_whitespace_integrity_verified"])
        self.assertEqual(
            bundle.audit["source_policy"]["layout_only_non_whitespace_integrity_verified_ids"],
            list(builder.LAYOUT_ONLY_CHANGED_IDS),
        )
        self.assertEqual(bundle.audit["source_policy"]["source_complete_restoration_ids"], [3_820])
        self.assertFalse(bundle.audit["source_policy"]["korean_sentence_shortened_or_deleted"])
        row_3820 = next(row for row in bundle.audit["rows"] if row["entry_id"] == 3_820)
        self.assertEqual(row_3820["change_mode"], "SOURCE_COMPLETE_RESTORATION_WITH_SEMANTIC_REFLOW")
        self.assertEqual(
            row_3820["source_complete_restoration_evidence"]["complete_korean_utf16le_sha256"],
            builder.EXPECTED_COMPLETE_KO_3820_UTF16LE_SHA256,
        )

    def test_private_candidate_exactness(self) -> None:
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(result["source_complete_restoration_ids"], [3_820])
        self.assertEqual(result["runtime_hold_excluded_ids"], list(builder.RUNTIME_HOLD_IDS))
        self.assertEqual(result["static_retained_manual_ids"], list(builder.STATIC_RETAINED_MANUAL_IDS))
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["network_operation_performed"])
        self.assertFalse(result["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
