from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_tenmokuzan_quality_wave82_v1.py")
spec = importlib.util.spec_from_file_location("tenmokuzan_wave82_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TenmokuzanWave82Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7732, 7752)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 8)
        self.assertEqual(len(module.RETAINED_IDS), 12)

    def test_predecessor_is_strict_on_disk_w81_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W81_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(predecessor["workstream"], "pc_event_mitsuhide_quality_wave81_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_mitsuhide_quality_wave81_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_reviewed_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 20)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
        self.assertFalse(self.bundle.audit["semantic_completion"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_7732_runtime_reservation_is_scene_limited_and_unproven(self) -> None:
        policy = self.bundle.audit["layout_policy"]
        self.assertTrue(policy["runtime_reservations_scene_limited"])
        self.assertFalse(policy["runtime_proven"])
        self.assertEqual(set(policy["runtime_reservations"]), {"[bs1871]"})
        reservation = policy["runtime_reservations"]["[bs1871]"]
        self.assertEqual(reservation["display"], "마쓰다이라")
        self.assertTrue(reservation["scene_limited"])
        self.assertFalse(reservation["runtime_proven"])
        row_7732 = next(row for row in self.bundle.rows if row["entry_id"] == 7732)
        self.assertEqual(row_7732["runtime_tokens"], ["[bs1871]"])
        self.assertFalse(row_7732["runtime_proven"])
        self.assertTrue(all(row["runtime_proven"] is False for row in self.bundle.rows))

    def test_exact_changed_targets_and_raw_metrics(self) -> None:
        expected_raw_widths = {
            7733: [864, 912, 888],
            7735: [912, 528, 480],
            7739: [576, 528, 696, 384],
            7741: [888, 672, 768],
            7744: [600, 840, 480],
            7746: [600, 888, 624],
            7749: [552, 768, 696, 480],
            7750: [384, 384, 696, 528],
        }
        for entry_id, raw_widths in expected_raw_widths.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("일문중·후다이중", module.TARGETS[7733])
        self.assertIn("이슬 같은 목숨", module.TARGETS[7749])
        self.assertIn("이 \x1bCC덴모쿠산\x1bCZ에서", module.TARGETS[7750])


if __name__ == "__main__":
    unittest.main(verbosity=2)
