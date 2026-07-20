#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_honnouji_quality_wave74_v1.py")
spec = importlib.util.spec_from_file_location("honnouji_wave74_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class HonnoujiWave74Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_scope_is_complete_and_fixed(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(10990, 11010)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            [row["entry_id"] for row in self.bundle.rows if not row["changed"]],
            [10991, 10992, 10993, 10994, 10997, 11001, 11002, 11005, 11007],
        )

    def test_predecessor_is_pinned_w73_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W73_PROFILE)
        self.assertEqual(predecessor["workstream"], "pc_event_imayama_quality_wave73_v1")

    def test_all_reviewed_rows_fit_and_preserve_controls(self) -> None:
        self.assertEqual(len(self.bundle.rows), len(module.SCENE_IDS))
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertTrue(all(not line["over_static_patch_912px"] for line in row["target_lines"]))
            self.assertFalse(row["japanese_source_line_breaks_used"])

    def test_11000_reflows_without_deleting_content(self) -> None:
        row = next(row for row in self.bundle.rows if row["entry_id"] == 11000)
        self.assertEqual(
            [line["display_string"] for line in row["target_lines"]],
            ["아케치 미쓰히데의 배신으로부터", "며칠 뒤, 아즈치성―"],
        )
        self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], [720, 432])


if __name__ == "__main__":
    unittest.main(verbosity=2)
