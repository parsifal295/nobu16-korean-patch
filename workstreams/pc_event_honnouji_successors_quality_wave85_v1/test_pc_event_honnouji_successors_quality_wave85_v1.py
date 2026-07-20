from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_honnouji_successors_quality_wave85_v1.py")
spec = importlib.util.spec_from_file_location("honnouji_successors_wave85_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class HonnoujiSuccessorsWave85Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7793, 7816)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 14)
        self.assertEqual(len(module.RETAINED_IDS), 9)

    def test_predecessor_is_strict_on_disk_w84_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["workstream"], module.W84_WORKSTREAM_NAME)
        self.assertEqual(predecessor["profile"], module.EXPECTED_W84_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])

    def test_all_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 23)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertEqual(row["runtime_tokens"], [])
            self.assertFalse(row["runtime_proven"])
        self.assertEqual(self.bundle.audit["layout_policy"]["runtime_reservations"], {})
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_exact_changed_targets_and_raw_metrics(self) -> None:
        expected_raw_widths = {
            7794: [624, 744, 936],
            7796: [744, 792, 888],
            7797: [744, 744, 720, 888],
            7800: [648, 936, 864],
            7801: [912, 696, 288],
            7802: [720, 624, 672],
            7803: [240, 720, 648, 792],
            7806: [840, 648, 576],
            7808: [576, 768, 552],
            7810: [576, 840, 816, 648],
            7811: [504, 720, 360, 456],
            7812: [552, 504, 744, 960],
            7813: [936, 960, 600, 408],
            7814: [792, 720, 648, 672],
        }
        for entry_id, raw_widths in expected_raw_widths.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("기량으로", module.TARGETS[7797])
        self.assertIn("잇코잇키", module.TARGETS[7810])
        self.assertIn("천하의 평온", module.TARGETS[7813])
        self.assertIn("필사의 싸움", module.TARGETS[7814])


if __name__ == "__main__":
    unittest.main(verbosity=2)
