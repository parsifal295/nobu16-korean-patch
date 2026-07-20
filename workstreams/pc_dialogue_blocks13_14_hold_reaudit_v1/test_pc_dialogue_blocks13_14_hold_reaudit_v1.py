#!/usr/bin/env python3
"""Tests for the read-only Wave 51 block 13–14 hold re-audit."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_blocks13_14_hold_reaudit_v1.py")
spec = importlib.util.spec_from_file_location("blocks13_14_hold_reaudit", BUILDER)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {BUILDER}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class Blocks1314HoldReauditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = module.build_report()
        module.validate(cls.report)
        cls.rows = {(row["resource"], row["coordinate"]): row for row in cls.report["rows"]}

    def test_inventory_and_classification_counts_are_complete(self) -> None:
        summary = self.report["summary"]
        self.assertEqual(summary["unique_hold_row_count"], 95)
        self.assertEqual(
            summary["classification_counts"],
            {
                "a_static_high_confidence": 20,
                "b_semantic_retranslation": 3,
                "c_runtime_or_real_game_ui_evidence": 72,
            },
        )
        self.assertEqual(summary["static_text_correction_ready_count"], 5)
        self.assertEqual(summary["static_policy_retain_current_ko_count"], 15)
        self.assertTrue(summary["all_rows_have_direct_pc_jp"])
        self.assertTrue(summary["all_rows_have_direct_pc_en_sc_tc_context"])

    def test_key_static_and_semantic_findings_are_pinned(self) -> None:
        pk = module.RESOURCE_PK
        base = module.RESOURCE_BASE
        self.assertEqual(self.rows[(base, "13:213")]["classification"], "a_static_high_confidence")
        self.assertIn("성하 시설", self.rows[(base, "13:213")]["proposed_ko_without_shortening"])
        for coordinate in ("13:563", "13:573", "13:590"):
            row = self.rows[(pk, coordinate)]
            self.assertEqual(row["classification"], "a_static_high_confidence")
            self.assertTrue(row["proposed_ko_without_shortening"])
            self.assertFalse(row["current_structure"]["runtime_02xx_opcodes"])
            self.assertFalse(row["current_structure"]["complete_0143_commands"])
        for coordinate in ("14:97", "14:98", "14:221"):
            self.assertEqual(self.rows[(pk, coordinate)]["classification"], "b_semantic_retranslation")

    def test_runtime_ui_and_source_conflict_remain_evidence_gated(self) -> None:
        pk = module.RESOURCE_PK
        base = module.RESOURCE_BASE
        self.assertEqual(self.rows[(base, "14:57")]["classification"], "c_runtime_or_real_game_ui_evidence")
        self.assertEqual(self.rows[(pk, "14:81")]["classification"], "c_runtime_or_real_game_ui_evidence")
        self.assertEqual(self.rows[(pk, "14:156")]["classification"], "c_runtime_or_real_game_ui_evidence")
        self.assertIn("아시가루대장", self.rows[(pk, "14:156")]["proposed_ko_without_shortening"])
        self.assertIn("사무라이대장", self.rows[(pk, "14:157")]["proposed_ko_without_shortening"])
        for resource, coordinate in ((base, "14:112"), (pk, "14:154"), (pk, "14:155")):
            self.assertEqual(self.rows[(resource, coordinate)]["classification"], "c_runtime_or_real_game_ui_evidence")
        self.assertEqual(self.rows[(base, "14:112")]["direct_pc_sources"]["cross_locale_coordinate"], "14:154")

    def test_report_is_deterministic_and_read_only(self) -> None:
        again = module.build_report()
        self.assertEqual(module.canonical_json(self.report), module.canonical_json(again))
        self.assertTrue(self.report["read_only_audit"])
        self.assertFalse(self.report["candidate_binary_created_by_this_workstream"])
        self.assertFalse(self.report["steam_game_resource_written"])
        self.assertFalse(self.report["git_operation_performed"])
        self.assertFalse(self.report["release_published"])
        self.assertFalse(self.report["network_operation_performed"])


if __name__ == "__main__":
    unittest.main()
