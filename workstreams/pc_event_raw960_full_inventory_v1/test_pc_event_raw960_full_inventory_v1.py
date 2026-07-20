#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_raw960_full_inventory_v1.py")
spec = importlib.util.spec_from_file_location("raw960_inventory_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class Raw960InventoryTests(unittest.TestCase):
    def test_static_line_metrics(self) -> None:
        row = module.rendered_line(4000, "가나다라마바사 abc!")
        self.assertEqual(row["display_string"], "가나다라마바사 abc!")
        self.assertEqual(row["full_width_character_count"], 7)
        self.assertEqual(row["half_width_character_count"], 5)
        self.assertEqual(row["raw_g1n_width_px"], 456)
        self.assertEqual(row["effective_width_px"], 285)
        self.assertFalse(row["over_live_raw_960px"])

    def test_unresolved_runtime_is_hold_not_guess(self) -> None:
        row = module.rendered_line(4509, "[b1448]의 출병")
        self.assertIsNone(row["display_string"])
        self.assertIsNone(row["raw_g1n_width_px"])
        self.assertEqual(row["runtime_tokens"][0]["status"], "unresolved_runtime_hold")

    def test_anegawa_runtime_is_scene_specific(self) -> None:
        row = module.rendered_line(5785, "[b1871]의 군")
        self.assertEqual(row["display_string"], "도쿠가와 이에야스의 군")
        self.assertEqual(row["runtime_tokens"][0]["status"], "scene_specific_reservation")

    def test_live_scope_and_topology(self) -> None:
        rows, summary = module.build_inventory()
        self.assertEqual(len(rows), module.EXPECTED_BODY_ROW_COUNT)
        self.assertEqual(summary["input"]["packed_sha256"], module.EXPECTED_PACKED_SHA256)
        self.assertEqual(sum(summary["manual_line_topology"].values()), module.EXPECTED_BODY_ROW_COUNT)
        self.assertFalse(summary["semantic_completion"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
