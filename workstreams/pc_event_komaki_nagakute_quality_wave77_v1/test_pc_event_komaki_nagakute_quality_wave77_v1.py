from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_komaki_nagakute_quality_wave77_v1.py")
spec = importlib.util.spec_from_file_location("komaki_wave77_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class KomakiNagakuteWave77Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(8235, 8303)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 26)
        self.assertEqual(len(module.RETAINED_IDS), 42)

    def test_predecessor_is_strict_on_disk_w76_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W76_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(predecessor["workstream"], "pc_event_amago_quality_wave76_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_amago_quality_wave76_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_rows_fit_raw960_max4_and_preserve_controls(self) -> None:
        self.assertEqual(len(self.bundle.rows), 68)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertTrue(all(not line["over_static_patch_912px"] for line in row["target_lines"]))
            self.assertFalse(row["japanese_source_line_breaks_used"])
        self.assertFalse(self.bundle.audit["semantic_completion"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])

    def test_runtime_reservations_are_scene_limited_and_not_runtime_proven(self) -> None:
        policy = self.bundle.audit["layout_policy"]
        self.assertTrue(policy["runtime_reservations_scene_limited"])
        self.assertFalse(policy["runtime_reservations_runtime_proven"])
        self.assertEqual(
            set(policy["runtime_reservations"]),
            {"[b1871]", "[bm1871]", "[bs1871]", "[b754]", "[bs754]", "[b1976]"},
        )
        for reservation in policy["runtime_reservations"].values():
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])

    def test_key_targets_and_line_widths_match_the_review(self) -> None:
        expected = {
            8236: [744, 600, 696, 960],
            8241: [768, 840, 960, 720],
            8243: [672, 720, 600, 456],
            8256: [456, 840, 840, 744],
            8268: [672, 936, 840, 624],
            8278: [960, 912, 768],
            8283: [744, 432, 912, 936],
            8284: [360, 936, 672, 600],
            8292: [624, 624, 816, 912],
            8300: [888, 960, 312, 816],
            8302: [768, 840, 720, 336],
        }
        for entry_id, raw_widths in expected.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertEqual(
            module.TARGETS[8284],
            "대치가 길어지며\n"
            "전쟁을 꺼리는 분위기가 짙어지는 가운데,\n"
            "\x1bCA[b1871]\x1bCZ의 진영에\n"
            "충격적인 소식이 전해졌다…",
        )
        self.assertEqual(
            module.TARGETS[8302],
            "\x1bCA노부카쓰\x1bCZ·\x1bCA[bm1871]\x1bCZ라는\n"
            "반대파를 억누른 \x1bCA[b754]\x1bCZ는\n"
            "이후 더욱 천하인의 높은 곳으로\n"
            "올라가게 된다.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
