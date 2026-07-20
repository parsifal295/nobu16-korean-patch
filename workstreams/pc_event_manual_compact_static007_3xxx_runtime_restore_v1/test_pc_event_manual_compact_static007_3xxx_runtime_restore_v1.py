#!/usr/bin/env python3
"""Private tests for the final 43-row runtime-token restoration candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_manual_compact_static007_3xxx_runtime_restore_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_3xxx_runtime_restore", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class PcEvent3xxxRuntimeRestoreTests(unittest.TestCase):
    def test_43_proposals_are_pinned_and_resolved(self) -> None:
        bundle = builder.build_bundle(require_output_profile=True)
        coverage = bundle.audit["coverage"]
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(coverage["proposal_row_count"], 43)
        self.assertEqual(coverage["changed_row_count"], 43)
        self.assertEqual(coverage["proposal_row_ids"], list(builder.EXPECTED_TARGET_IDS))
        self.assertEqual(coverage["changed_row_ids"], list(builder.EXPECTED_TARGET_IDS))
        self.assertEqual(coverage["unresolved_runtime_hold_ids"], [])
        self.assertEqual(coverage["runtime_proven_false_ids"], list(builder.EXPECTED_TARGET_IDS))
        self.assertTrue(coverage["all_artifact_baselines_equal_latest_strict"])
        self.assertTrue(coverage["all_rows_static_patch_007_pass"])
        self.assertTrue(coverage["all_rows_four_or_fewer_lines"])
        self.assertTrue(coverage["all_rows_sentence_shortened_or_deleted_false"])
        self.assertEqual(coverage["quality_correction_ids"], list(builder.QUALITY_CORRECTION_IDS))

        for row in bundle.audit["rows"]:
            self.assertTrue(row["artifact_baseline_equals_latest_strict"])
            self.assertFalse(row["runtime_proven"])
            self.assertFalse(row["runtime_hold_excluded"])
            self.assertFalse(row["korean_sentence_shortened_or_deleted"])
            self.assertTrue(row["all_static_patch_007_lines_pass"])
            self.assertGreaterEqual(row["line_count"], 1)
            self.assertLessEqual(row["line_count"], 4)
            self.assertTrue(row["runtime_tokens"])
            self.assertTrue(row["runtime_name_reservations"])
            self.assertTrue(all(item["runtime_proven"] is False for item in row["runtime_name_reservations"]))
            self.assertTrue(all(line["passes_static_patch_007"] for line in row["displayed_lines"]))
            self.assertTrue(all(line["raw_g1n_width_px"] <= 1440 for line in row["displayed_lines"]))
            self.assertTrue(all(line["effective_width_px"] <= 912 for line in row["displayed_lines"]))

    def test_quality_corrections_and_no_shortening_are_in_the_canonical_candidate(self) -> None:
        bundle = builder.build_bundle(require_output_profile=True)
        rows = {row["entry_id"]: row for row in bundle.audit["rows"]}
        self.assertIn("또한", rows[3442]["target_ko"])
        self.assertIn("또한", rows[3443]["target_ko"])
        self.assertIn("[b790]", rows[3524]["target_ko"])
        self.assertNotIn("일행", rows[3524]["target_ko"])
        self.assertIn("지방 호족들의 원성도 컸습니다", rows[3579]["target_ko"])
        self.assertIn("원복시켜", rows[3713]["target_ko"])
        self.assertIn("공이라 이름하게 했다", rows[3713]["target_ko"])
        self.assertIn("불만을 품은 많은", rows[3767]["target_ko"])
        self.assertIn("가문 내에 따르는 이도 많은", rows[3789]["target_ko"])
        self.assertIn("중재에 나서", rows[3789]["target_ko"])
        self.assertIn("간곡히 거듭 권했다", rows[3789]["target_ko"])
        self.assertEqual(
            {entry_id for entry_id, row in rows.items() if row["quality_correction"]},
            set(builder.QUALITY_CORRECTION_IDS),
        )

    def test_build_is_deterministic_and_has_no_external_side_effect_record(self) -> None:
        first = builder.build_bundle(require_output_profile=True)
        second = builder.build_bundle(require_output_profile=True)
        self.assertEqual(first.event, second.event)
        self.assertEqual(builder.canonical_json(first.audit), builder.canonical_json(second.audit))
        self.assertEqual(builder.canonical_json(first.manifest), builder.canonical_json(second.manifest))
        self.assertTrue(first.audit["candidate_only"])
        self.assertFalse(first.audit["source_policy"]["candidate_binary_written_to_steam"])
        self.assertFalse(first.audit["source_policy"]["git_operation_performed"])
        self.assertFalse(first.audit["source_policy"]["release_published"])
        self.assertFalse(first.audit["source_policy"]["network_operation_performed"])
        self.assertEqual(first.manifest["unresolved_runtime_hold_ids"], [])
        self.assertEqual(first.manifest["quality_correction_ids"], list(builder.QUALITY_CORRECTION_IDS))


if __name__ == "__main__":
    unittest.main(verbosity=2)
