from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_naomasa_quality_wave80_v1.py")
spec = importlib.util.spec_from_file_location("naomasa_wave80_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class NaomasaWave80Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7675, 7714)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 24)
        self.assertEqual(len(module.RETAINED_IDS), 15)

    def test_predecessor_is_strict_on_disk_w79_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W79_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(predecessor["workstream"], "pc_event_otate_quality_wave79_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_otate_quality_wave79_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_reviewed_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 39)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
        self.assertFalse(self.bundle.audit["semantic_completion"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_runtime_reservations_are_scene_limited_and_never_proven(self) -> None:
        policy = self.bundle.audit["layout_policy"]
        self.assertTrue(policy["runtime_reservations_scene_limited"])
        self.assertFalse(policy["runtime_proven"])
        self.assertEqual(
            set(policy["runtime_reservations"]),
            {"[b1871]", "[bm1871]", "[bs1871]", "[bm1251]", "[b1448]", "[bm1448]"},
        )
        for reservation in policy["runtime_reservations"].values():
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])
        self.assertTrue(all(row["runtime_proven"] is False for row in self.bundle.rows))

    def test_exact_changed_targets_and_raw_metrics(self) -> None:
        expected_raw_widths = {
            7675: [840, 816, 744],
            7676: [936, 504, 624],
            7677: [912, 936, 960, 552],
            7679: [456, 816, 816, 288],
            7680: [768, 840, 432],
            7682: [528, 864, 600],
            7683: [72, 768],
            7684: [672, 624, 816, 480],
            7685: [816, 600, 864, 744],
            7688: [288, 624, 456],
            7690: [600, 696, 792, 792],
            7691: [456, 840, 432],
            7692: [480, 864, 720],
            7693: [816, 648],
            7695: [888, 792, 912, 432],
            7696: [960, 840, 552, 432],
            7699: [792, 912, 672],
            7703: [888, 792, 168],
            7706: [960, 816, 648, 624],
            7707: [288, 840, 480],
            7710: [888, 696, 480, 504],
            7711: [840, 936, 696, 888],
            7712: [768, 744, 792, 336],
            7713: [936, 624],
        }
        for entry_id, raw_widths in expected_raw_widths.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("훌륭한 적수", module.TARGETS[7684])
        self.assertIn("크게 패한 적이 없었다", module.TARGETS[7685])
        self.assertIn("확고한 기반", module.TARGETS[7711])


if __name__ == "__main__":
    unittest.main(verbosity=2)
