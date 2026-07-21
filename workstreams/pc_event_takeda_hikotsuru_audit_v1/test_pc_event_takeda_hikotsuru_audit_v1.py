#!/usr/bin/env python3
"""Regression checks for the read-only 3527–3564 Takeda/Hikotsuru event audit."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_event_takeda_hikotsuru_audit_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_takeda_hikotsuru_audit_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TakedaHikotsuruEventAuditTests(unittest.TestCase):
    def test_authored_scope(self) -> None:
        MODULE.validate_authored_scope()
        self.assertEqual(MODULE.TARGET_IDS, tuple(range(3527, 3565)))
        self.assertEqual(
            set(MODULE.PROPOSALS),
            set(MODULE.REFLOW_ONLY_IDS)
            | set(MODULE.TYPOGRAPHIC_REFLOW_IDS)
            | set(MODULE.SEMANTIC_PROPOSAL_IDS),
        )
        self.assertTrue(set(MODULE.W101_REBASE_CHANGED_IDS).isdisjoint(MODULE.TARGET_IDS))

    def test_in_memory_report(self) -> None:
        report, validation = MODULE.build_bundle()
        self.assertEqual(report["schema"], "nobu16.kr.pc-event-takeda-hikotsuru-audit.v1")
        self.assertEqual(report["scope"]["target_row_count"], 38)
        self.assertTrue(report["scope"]["strict_input_rebased_from_wave100_to_wave101"])
        self.assertTrue(report["scope"]["target_range_identical_between_wave100_and_wave101"])
        self.assertEqual(len(report["entries"]), 38)
        self.assertEqual(report["coverage"]["static_high_confidence_ids"], list(MODULE.PROPOSALS))
        self.assertEqual(report["coverage"]["static_high_confidence_count"], 20)
        self.assertEqual(report["coverage"]["runtime_reservation_proposal_ids"], [3548])
        self.assertEqual(report["coverage"]["runtime_or_ui_hold_ids"], [])
        self.assertTrue(report["coverage"]["all_current_lines_within_static_patch_007"])
        self.assertTrue(report["coverage"]["all_proposed_lines_within_static_patch_007"])
        self.assertTrue(report["coverage"]["all_current_and_proposed_rows_within_four_lines"])
        self.assertFalse(report["scope"]["candidate_binary_created"])
        self.assertFalse(report["scope"]["steam_game_resource_written"])
        self.assertFalse(report["scope"]["git_operation_performed"])
        self.assertEqual(validation["status"], "PASS")

    def test_checked_in_report(self) -> None:
        result = MODULE.verify_report()
        self.assertEqual(result["status"], "PASS")
        report = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
        by_id = {entry["entry_id"]: entry for entry in report["entries"]}
        self.assertIn("내조의 공으로 뒷받침", by_id[3550]["proposed_ko"])
        self.assertIn("첫눈에 반했다고", by_id[3551]["proposed_ko"])
        self.assertIn("재치를 발휘해", by_id[3563]["proposed_ko"])
        self.assertIn("전국시대에는", by_id[3564]["proposed_ko"])
        self.assertIn("[bm1251]", by_id[3548]["proposed_ko"])
        for entry in report["entries"]:
            self.assertFalse(entry["review_policy"]["sentence_shortened_or_deleted"])
            self.assertLessEqual(entry["current_layout"]["line_count"], 4)
            self.assertLessEqual(entry["proposed_layout"]["line_count"], 4)
            for layout_name in ("current_layout", "proposed_layout"):
                for line in entry[layout_name]["lines"]:
                    self.assertLessEqual(line["effective_width_px"], 912)
                    self.assertFalse(line["exceeds_912px"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
