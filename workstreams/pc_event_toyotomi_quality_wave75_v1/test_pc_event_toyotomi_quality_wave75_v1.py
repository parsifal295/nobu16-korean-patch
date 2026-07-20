#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_toyotomi_quality_wave75_v1.py")
spec = importlib.util.spec_from_file_location("toyotomi_wave75_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ToyotomiWave75Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_scope_is_complete_fixed_and_retains_8495(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(8484, 8521)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        unchanged = [row["entry_id"] for row in self.bundle.rows if not row["changed"]]
        self.assertEqual(
            unchanged,
            [
                8484,
                8485,
                8486,
                8487,
                8488,
                8489,
                8490,
                8492,
                8493,
                8494,
                8495,
                8497,
                8500,
                8501,
                8502,
                8504,
                8505,
                8507,
                8509,
                8511,
                8517,
                8518,
            ],
        )

    def test_predecessor_is_strict_on_disk_w74_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W74_PROFILE)
        self.assertEqual(predecessor["workstream"], "pc_event_honnouji_quality_wave74_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_honnouji_quality_wave74_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_rows_fit_raw960_and_preserve_controls(self) -> None:
        self.assertEqual(len(self.bundle.rows), len(module.SCENE_IDS))
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertTrue(all(not line["over_static_patch_912px"] for line in row["target_lines"]))
            self.assertFalse(row["japanese_source_line_breaks_used"])

    def test_conservative_runtime_capacity_metrics(self) -> None:
        expected = {
            8512: [936, 864, 840, 552],
            8513: [696, 936, 936, 816],
            8520: [936, 720, 672, 792],
        }
        for entry_id, raw_widths in expected.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertEqual(
                [line["raw_g1n_width_px"] for line in row["target_lines"]],
                raw_widths,
            )

    def test_key_unabridged_targets_are_exact(self) -> None:
        self.assertEqual(
            module.TARGETS[8513],
            "천하인을 목표로 한 \x1bCA히데요시\x1bCZ는\n"
            "거대한 존재감을 유지하는 \x1bCB[bs1871]가\x1bCZ를\n"
            "그대로 둘 수 없었다. 수단을 가리지 않고\n"
            "\x1bCB[bm1871]\x1bCZ 포섭을 꾀했다.",
        )
        self.assertEqual(
            module.TARGETS[8520],
            "친족을 거듭 보낸 \x1bCA히데요시\x1bCZ에게 질렸는지,\n"
            "\x1bCA히데요시\x1bCZ의 성의에 꺾인 것인지,\n"
            "\x1bCA[bm1871]\x1bCZ는 마침내\n"
            "\x1bCA히데요시\x1bCZ에게 신종하기로 결심했다.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
