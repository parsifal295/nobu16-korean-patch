#!/usr/bin/env python3
"""Regression checks for the private W94 Ōtomo/Tachibana candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_otomo_tachibana_quality_wave94_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave94_under_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class Wave94Tests(unittest.TestCase):
    def test_scope_targets_and_reservations_are_exact(self) -> None:
        builder.validate_static_targets()
        self.assertEqual(builder.SCENE_IDS, tuple(range(8383, 8392)))
        self.assertEqual(builder.CHANGED_IDS, (8384, 8385, 8387, 8388, 8389, 8390, 8391))
        self.assertEqual(builder.RETAINED_IDS, (8383, 8386))
        self.assertEqual(set(builder.SCENE_RAW_WIDTHS), set(builder.SCENE_IDS))
        self.assertEqual(builder.SCENE_RUNTIME_RESERVATIONS["[bm1222]"]["display"], "다카하시 무네토라")
        self.assertEqual(builder.SCENE_RUNTIME_RESERVATIONS["[bm1222]"]["reserved_raw_g1n_width_px"], 408)
        self.assertEqual(builder.SCENE_RUNTIME_RESERVATIONS["[bm1730]"]["display"], "벳키 아키츠라")
        self.assertEqual(builder.SCENE_RUNTIME_RESERVATIONS["[bm1730]"]["reserved_raw_g1n_width_px"], 312)
        for reservation in builder.SCENE_RUNTIME_RESERVATIONS.values():
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])

    def test_all_nine_rows_are_reservation_aware_and_within_gate(self) -> None:
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(tuple(bundle.changed), builder.CHANGED_IDS)
        self.assertEqual(len(bundle.rows), 9)
        for row in bundle.rows:
            entry_id = row["entry_id"]
            self.assertEqual(
                tuple(line["raw_g1n_width_px"] for line in row["target_lines"]),
                builder.SCENE_RAW_WIDTHS[entry_id],
            )
            self.assertGreaterEqual(row["target_manual_line_count"], 1)
            self.assertLessEqual(row["target_manual_line_count"], 4)
            self.assertFalse(row["runtime_proven"])
            for line in row["target_lines"]:
                self.assertLessEqual(line["raw_g1n_width_px"], 960)
                self.assertFalse(line["over_live_raw_960px"])
        rows = {row["entry_id"]: row for row in bundle.rows}
        self.assertEqual(rows[8383]["target_lines"][0]["display_string"], "무슨 일이냐, 다카하시 무네토라.")
        self.assertEqual(rows[8385]["runtime_reservations"][0]["reserved_raw_g1n_width_px"], 312)
        self.assertEqual(rows[8387]["runtime_reservations"][0]["reserved_raw_g1n_width_px"], 408)
        self.assertEqual(rows[8391]["runtime_reservations"][0]["reserved_raw_g1n_width_px"], 408)

    def test_predecessor_output_and_candidate_are_pinned(self) -> None:
        self.assertIsNotNone(builder.EXPECTED_OUTPUT_PROFILE)
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["runtime_proven"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
