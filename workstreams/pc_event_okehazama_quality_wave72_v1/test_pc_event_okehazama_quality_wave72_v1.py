#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_okehazama_quality_wave72_v1.py")
spec = importlib.util.spec_from_file_location("okehazama_wave72_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class OkehazamaWave72Tests(unittest.TestCase):
    def test_scope_is_complete_and_fixed(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(4494, 4511)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)

    def test_4509_reserves_only_scene_name(self) -> None:
        metrics = module.line_metrics(4509, module.TARGETS[4509])
        self.assertEqual([row["raw_g1n_width_px"] for row in metrics], [720, 840, 840, 192])
        self.assertTrue(all(not row["over_live_raw_960px"] for row in metrics))

    def test_all_reviewed_rows_fit_and_preserve_controls(self) -> None:
        bundle = module.prepare(require_output_profile=False)
        self.assertEqual(tuple(sorted(bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(len(bundle.rows), len(module.SCENE_IDS))
        for row in bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
