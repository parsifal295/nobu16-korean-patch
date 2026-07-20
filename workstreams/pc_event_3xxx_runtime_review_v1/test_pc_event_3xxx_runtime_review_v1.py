#!/usr/bin/env python3
"""Private tests for the 3xxx runtime-token source-complete review."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_3xxx_runtime_review_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_3xxx_runtime_review", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class PcEvent3xxxRuntimeReviewTests(unittest.TestCase):
    def test_targets_are_complete_and_static007_safe_after_name_substitution(self) -> None:
        builder.validate_authored_targets()
        self.assertEqual(len(builder.MANUAL_RUNTIME_IDS), 26)
        self.assertEqual(tuple(builder.TARGETS), builder.MANUAL_RUNTIME_IDS)
        self.assertEqual(builder.SOURCE_SEQUENCE_REORDER_IDS, (3_767,))
        self.assertEqual(builder.SOURCE_MEANING_CORRECTION_IDS, (3_713, 3_767, 3_789))

        korean, profile, _audit = builder.load_strict_input()
        full_korean, _profiles = builder.load_full_korean_sources()
        reservations, _provenance = builder.load_reservations()
        direct, _direct_profiles = builder.base.load_direct_contexts()

        for entry_id in builder.MANUAL_RUNTIME_IDS:
            row = builder.target_row(
                entry_id,
                korean=korean,
                direct=direct,
                full_korean=full_korean,
                reservations=reservations,
            )
            self.assertEqual(
                row["change_mode"],
                "SOURCE_COMPLETE_RUNTIME_TOKEN_RESTORATION_WITH_SEMANTIC_REFLOW",
            )
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertFalse(row["korean_sentence_shortened_or_deleted"])
            self.assertGreaterEqual(row["line_count"], 1)
            self.assertLessEqual(row["line_count"], 4)
            self.assertTrue(row["all_static_patch_007_lines_pass"])
            self.assertEqual(row["target_control_signature"], row["direct_control_signatures"]["jp"])
            self.assertTrue(row["runtime_token_reservations"])
            self.assertTrue(all(line["passes_static_patch_007"] for line in row["displayed_lines"]))
            self.assertTrue(all("strict_korean_name" in token for token in row["runtime_token_reservations"]))

        self.assertEqual(profile, builder.batch07.EXPECTED_OUTPUT_PROFILE)

    def test_report_is_read_only_and_has_full_runtime_evidence(self) -> None:
        report = builder.build_report()
        self.assertFalse(report["candidate_created"])
        self.assertFalse(report["source_policy"]["steam_game_resource_written"])
        self.assertFalse(report["source_policy"]["git_operation_performed"])
        self.assertFalse(report["source_policy"]["network_operation_performed"])
        self.assertFalse(report["source_policy"]["release_published"])
        self.assertEqual(report["coverage"]["manual_source_complete_runtime_target_count"], 26)
        self.assertEqual(report["coverage"]["batch07_runtime_row_count"], 48)
        self.assertEqual(len(report["rows"]), 26)
        self.assertEqual(len(report["current_runtime_name_substitution_scan"]), 48)
        self.assertTrue(report["summary"]["all_26_targets_ready_for_followup_candidate"])
        self.assertTrue(report["summary"]["all_48_current_runtime_rows_fit_with_strict_name_substitution"])
        self.assertEqual(builder.canonical_json(report), builder.canonical_json(builder.build_report()))

        scan_ids = {row["entry_id"] for row in report["current_runtime_name_substitution_scan"]}
        self.assertTrue(set(builder.MANUAL_RUNTIME_IDS).issubset(scan_ids))
        self.assertTrue(
            all(row["current_rendered_static_patch_007_passes"] for row in report["current_runtime_name_substitution_scan"])
        )

    def test_source_word_integrity_policy(self) -> None:
        full_korean, _profiles = builder.load_full_korean_sources()
        for entry_id in builder.MANUAL_RUNTIME_IDS:
            target = builder.TARGETS[entry_id]
            complete = full_korean[entry_id]
            if entry_id == 3_713:
                self.assertIn("원복시켜", target)
                self.assertIn("공이라 이름하게 했다", target)
            elif entry_id == 3_767:
                self.assertIn("불만을 품은 많은", target)
                self.assertIn("많은", target)
            elif entry_id == 3_789:
                self.assertIn("가문 내에 따르는 이도 많은", target)
                self.assertIn("중재에 나서", target)
                self.assertIn("간곡히 거듭 권했다", target)
            else:
                self.assertEqual(
                    builder.normalized_source_visible(target),
                    builder.normalized_source_visible(complete),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
