from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_koshu_campaign_quality_wave84_v1.py")
spec = importlib.util.spec_from_file_location("koshu_campaign_wave84_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class KoshuCampaignWave84Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7779, 7793)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 6)
        self.assertEqual(len(module.RETAINED_IDS), 8)

    def test_predecessor_is_strict_on_disk_w83_candidate(self) -> None:
        self.assertIsNotNone(module.W83_WORKSTREAM_NAME)
        self.assertIsNotNone(module.W83_BUILDER)
        self.assertIsNotNone(module.EXPECTED_W83_PROFILE)
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W83_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(predecessor["workstream"], module.W83_WORKSTREAM_NAME)

    def test_all_reviewed_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 14)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
        self.assertFalse(self.bundle.audit["semantic_completion"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_runtime_reservations_are_scene_limited_and_unproven(self) -> None:
        policy = self.bundle.audit["layout_policy"]
        self.assertTrue(policy["runtime_reservations_scene_limited"])
        self.assertFalse(policy["runtime_proven"])
        self.assertEqual(
            set(policy["runtime_reservations"]),
            {"[bm1251]", "[bs1871]", "[bm1871]", "[b1871]"},
        )
        for reservation in policy["runtime_reservations"].values():
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])
        expected_tokens = {
            7781: ["[bm1251]"],
            7784: ["[bs1871]"],
            7787: ["[bm1871]"],
            7792: ["[b1871]"],
        }
        for row in self.bundle.rows:
            self.assertEqual(row["runtime_tokens"], expected_tokens.get(row["entry_id"], []))
            self.assertFalse(row["runtime_proven"])

    def test_exact_changed_targets_and_raw_metrics(self) -> None:
        expected_raw_widths = {
            7779: [672, 744, 216],
            7780: [432, 912, 648, 648],
            7781: [720, 744, 792, 696],
            7782: [792, 888, 936],
            7791: [744, 912, 792],
            7792: [840, 624, 720, 576],
        }
        for entry_id, raw_widths in expected_raw_widths.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("중앙집권화를 추진하려 했다", module.TARGETS[7780])
        self.assertIn("성곽에 집착하지 않았던", module.TARGETS[7781])
        self.assertIn("사방의 적을 맞게 되었다", module.TARGETS[7792])


if __name__ == "__main__":
    unittest.main(verbosity=2)
