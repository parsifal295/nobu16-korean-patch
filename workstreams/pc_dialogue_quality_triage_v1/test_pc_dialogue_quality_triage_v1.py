#!/usr/bin/env python3
"""Regression checks for the PC-only dialogue quality triage catalogue."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
MODULE_PATH = WORKSTREAM / "build_pc_dialogue_quality_triage_v1.py"


def load_module():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_triage_v1", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load triage module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class PcDialogueQualityTriageTests(unittest.TestCase):
    def test_regenerated_catalog_has_exact_scope(self) -> None:
        rows, validation = MODULE.candidate_rows()
        self.assertEqual(MODULE.EXPECTED_CANDIDATE_COUNT, len(rows))
        self.assertEqual(30, validation["candidate_count"])
        self.assertFalse(validation["source_policy"]["switch_korean_translation_used"])
        self.assertFalse(validation["source_policy"]["steam_game_resource_written"])
        self.assertFalse(validation["wave7_coordinate_reintroduced"])

    def test_each_recommendation_preserves_manual_line_count_and_is_static(self) -> None:
        rows, _validation = MODULE.candidate_rows()
        for row in rows:
            contract = row["safe_apply_contract"]
            self.assertEqual(contract["manual_line_count_before"], contract["manual_line_count_after"])
            self.assertFalse(contract["runtime_tokens_present"])
            self.assertEqual("050505", contract["required_remaining_opaque_bytes"])
            self.assertIn("pk", row["targets"])
            for target in row["targets"].values():
                self.assertTrue(target["current_0143_commands"])
                self.assertTrue(target["pc_reference_texts"])

    def test_okehazama_priority_range_keeps_intentional_question_out_of_candidates(self) -> None:
        report, validation = MODULE.event_priority_report()
        self.assertEqual([4494, 4510], report["reviewed_id_range"])
        self.assertEqual([4495, 4502, 4506, 4508, 4509], validation["candidate_ids"])
        self.assertEqual([4504], validation["explicitly_excluded_ids"])
        self.assertTrue(validation["range_fully_read"])
        self.assertFalse(validation["switch_korean_translation_used"])
        for row in report["candidates"]:
            contract = row["safe_apply_contract"]
            self.assertEqual(contract["manual_line_count_before"], contract["manual_line_count_after"])
            self.assertTrue(contract["esc_runtime_printf_and_edge_whitespace_unchanged"])


if __name__ == "__main__":
    unittest.main()
