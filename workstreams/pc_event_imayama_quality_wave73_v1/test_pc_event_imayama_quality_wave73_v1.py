#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_imayama_quality_wave73_v1.py")
spec = importlib.util.spec_from_file_location("imayama_wave73_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ImayamaWave73Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_scope_is_complete_and_fixed(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(5915, 5938)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)

    def test_predecessor_is_w72_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W72_PROFILE)
        self.assertEqual(predecessor["workstream"], "pc_event_okehazama_quality_wave72_v1")

    def test_all_reviewed_rows_fit_and_preserve_controls(self) -> None:
        self.assertEqual(len(self.bundle.rows), len(module.SCENE_IDS))
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertFalse(row["japanese_source_line_breaks_used"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
