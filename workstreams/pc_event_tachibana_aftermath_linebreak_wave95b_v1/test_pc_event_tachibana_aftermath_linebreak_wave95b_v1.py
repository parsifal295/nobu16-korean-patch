#!/usr/bin/env python3
"""Regression checks for the private W95b one-row LF correction."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_tachibana_aftermath_linebreak_wave95b_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave95b_under_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class Wave95bTests(unittest.TestCase):
    def test_exact_lf_only_target_and_metrics(self) -> None:
        builder.validate_target()
        self.assertEqual(builder.ENTRY_ID, 8438)
        self.assertEqual(builder.TARGET_RAW_WIDTHS, (816, 648, 312))
        bundle = builder.prepare(require_output_profile=True)
        row = bundle.audit["row"]
        self.assertTrue(row["lf_only_reflow"])
        self.assertTrue(row["normalized_visible_text_equal"])
        self.assertEqual(tuple(line["raw_g1n_width_px"] for line in row["target_lines"]), (816, 648, 312))
        for line in row["target_lines"]:
            self.assertLessEqual(line["raw_g1n_width_px"], 960)
            self.assertFalse(line["over_live_raw_960px"])

    def test_profile_and_candidate_are_exact(self) -> None:
        self.assertIsNotNone(builder.EXPECTED_OUTPUT_PROFILE)
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["changed_row_ids"], [8438])
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["network_operation_performed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
