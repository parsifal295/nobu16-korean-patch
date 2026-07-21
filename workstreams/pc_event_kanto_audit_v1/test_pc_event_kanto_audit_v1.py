#!/usr/bin/env python3
"""Regression checks for the read-only 3485–3526 Kanto event audit."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_event_kanto_audit_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_kanto_audit_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class KantoEventAuditTests(unittest.TestCase):
    def test_authored_scope(self) -> None:
        MODULE.validate_authored_scope()
        self.assertEqual(MODULE.TARGET_IDS, tuple(range(3485, 3527)))
        self.assertEqual(set(MODULE.PROPOSALS), set(MODULE.REFLOW_ONLY_IDS) | set(MODULE.SEMANTIC_CHANGE_IDS))

    def test_in_memory_report(self) -> None:
        report, validation = MODULE.build_bundle()
        self.assertEqual(report["schema"], "nobu16.kr.pc-event-kanto-audit.v1")
        self.assertEqual(report["scope"]["target_row_count"], 42)
        self.assertTrue(report["scope"]["wave100_rebase_range_identical_to_wave98"])
        self.assertEqual(len(report["entries"]), 42)
        self.assertEqual(report["coverage"]["static_high_confidence_ids"], list(MODULE.PROPOSALS))
        self.assertEqual(report["coverage"]["runtime_or_ui_hold_ids"], [])
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
        self.assertIn("가와고에성", by_id[3506]["proposed_ko"])
        self.assertIn("양 우에스기", by_id[3505]["proposed_ko"])
        self.assertIn("고가 공방", by_id[3508]["proposed_ko"])
        for entry in report["entries"]:
            self.assertFalse(entry["review_policy"]["sentence_shortened_or_deleted"])
            self.assertLessEqual(entry["proposed_layout"]["line_count"], 4)
            for line in entry["proposed_layout"]["lines"]:
                self.assertLessEqual(line["effective_width_px"], 912)
                self.assertFalse(line["exceeds_912px"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
