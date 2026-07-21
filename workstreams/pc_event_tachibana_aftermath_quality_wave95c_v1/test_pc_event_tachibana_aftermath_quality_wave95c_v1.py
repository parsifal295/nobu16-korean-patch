#!/usr/bin/env python3
"""Regression checks for the private W95c ten-row correction."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_tachibana_aftermath_quality_wave95c_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave95c_under_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class Wave95cTests(unittest.TestCase):
    def test_scope_and_layout_contract(self) -> None:
        self.assertEqual(
            builder.CHANGED_IDS,
            (8400, 8405, 8411, 8417, 8419, 8421, 8422, 8432, 8435, 8438),
        )
        self.assertEqual(builder.LF_ONLY_IDS, (8400,))
        self.assertIsNotNone(builder.TARGET_RAW_WIDTHS)
        builder.validate_targets()
        for entry_id in builder.CHANGED_IDS:
            metrics = builder.line_metrics(builder.TARGETS[entry_id])
            self.assertLessEqual(len(metrics), 4)
            self.assertEqual(
                tuple(line["raw_g1n_width_px"] for line in metrics),
                builder.TARGET_RAW_WIDTHS[entry_id],
            )
            for line in metrics:
                self.assertLessEqual(line["raw_g1n_width_px"], 960)
                self.assertFalse(line["over_live_raw_960px"])

    def test_exact_profile_context_and_candidate(self) -> None:
        self.assertIsNotNone(builder.EXPECTED_OUTPUT_PROFILE)
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(bundle.audit["coverage"]["changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(len(bundle.audit["rows"]), len(builder.CHANGED_IDS))
        self.assertEqual(set(bundle.audit["direct_pc_context_profiles"]), {"jp", "en", "sc", "tc"})
        row8400 = next(row for row in bundle.audit["rows"] if row["entry_id"] == 8400)
        self.assertTrue(row8400["lf_only_reflow"])
        self.assertTrue(row8400["normalized_visible_text_equal"])
        self.assertEqual(row8400["runtime_reservations"][0]["reserved_raw_g1n_width_px"], 312)
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["network_operation_performed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
