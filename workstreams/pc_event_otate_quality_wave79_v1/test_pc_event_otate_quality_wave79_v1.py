from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_otate_quality_wave79_v1.py")
spec = importlib.util.spec_from_file_location("otate_wave79_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class OtateWave79Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7214, 7239)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 13)
        self.assertEqual(len(module.RETAINED_IDS), 12)

    def test_predecessor_is_strict_on_disk_w78_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W78_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(predecessor["workstream"], "pc_event_echigo_quality_wave78_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_echigo_quality_wave78_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_reviewed_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 25)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertTrue(all(not line["over_static_patch_912px"] for line in row["target_lines"]))
            self.assertFalse(row["japanese_source_line_breaks_used"])
        self.assertFalse(self.bundle.audit["semantic_completion"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_runtime_reservations_are_scene_limited_and_never_proven(self) -> None:
        policy = self.bundle.audit["layout_policy"]
        self.assertTrue(policy["runtime_reservations_scene_limited"])
        self.assertFalse(policy["runtime_proven"])
        self.assertEqual(set(policy["runtime_reservations"]), {"[b1448]", "[b1672]", "[bs1672]"})
        for reservation in policy["runtime_reservations"].values():
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])
        self.assertTrue(all(row["runtime_proven"] is False for row in self.bundle.rows))

    def test_exact_reviewed_targets_and_metrics(self) -> None:
        expected_raw_widths = {
            7214: [624, 672, 600],
            7215: [600, 528, 960, 528],
            7216: [672, 552, 600, 696],
            7217: [600, 720, 696],
            7219: [264, 864, 504],
            7221: [672, 552],
            7222: [624, 576, 840, 888],
            7226: [816, 816, 576, 456],
            7228: [768, 336, 912, 864],
            7234: [840, 888, 912],
            7236: [576, 456, 936, 936],
            7237: [408, 576, 960, 768],
            7238: [888, 792, 888],
        }
        for entry_id, raw_widths in expected_raw_widths.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertEqual(
            module.TARGETS[7236],
            "하지만 \x1bCA가쓰요리\x1bCZ의 계획은\n"
            "보기 좋게 빗나갔다.\n"
            "\x1bCB다케다 가문\x1bCZ의 애매한 태도에 불신을 품은\n"
            "\x1bCB호조 가문\x1bCZ은 \x1bCB다케다\x1bCZ와의 절연을 선언했다…",
        )
        self.assertEqual(
            module.TARGETS[7237],
            "당황한 \x1bCA가쓰요리\x1bCZ는\n"
            "\x1bCB호조가\x1bCZ의 공격에 대비하려\n"
            "여동생 \x1bCA기쿠히메\x1bCZ를 \x1bCA가게카쓰\x1bCZ의 정실로 삼아\n"
            "\x1bCB우에스기가\x1bCZ와 혼인 동맹을 맺었다.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
