from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_echigo_quality_wave78_v1.py")
spec = importlib.util.spec_from_file_location("echigo_wave78_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class EchigoWave78Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(4280, 4315)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 13)
        self.assertEqual(len(module.RETAINED_IDS), 22)

    def test_predecessor_is_strict_on_disk_w77_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W77_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(predecessor["workstream"], "pc_event_komaki_nagakute_quality_wave77_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_komaki_nagakute_quality_wave77_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_reviewed_rows_fit_raw960_max4_and_keep_source_policy(self) -> None:
        self.assertEqual(len(self.bundle.rows), 35)
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
        self.assertEqual(set(policy["runtime_reservations"]), {"[b1448]", "[bm1448]", "[bs1448]"})
        for reservation in policy["runtime_reservations"].values():
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])
        self.assertTrue(all(row["runtime_proven"] is False for row in self.bundle.rows))

    def test_key_targets_and_metrics_match_the_review(self) -> None:
        expected = {
            4281: [792, 552, 528, 744],
            4289: [912, 960, 792, 528],
            4290: [960, 600, 960, 336],
            4296: [816, 528, 816, 552],
            4298: [960, 840, 792],
            4302: [576, 816, 936, 888],
            4303: [768, 768, 744, 504],
            4313: [960, 672, 648, 936],
            4314: [960, 720, 504],
        }
        for entry_id, raw_widths in expected.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertEqual(
            module.TARGETS[4302],
            "\x1bCA[bm1448]\x1bCZ는 지금의\n"
            "\x1bCB[bs1448] 가문\x1bCZ에서 그 유대를\n"
            "느끼지 못하기에 출가하겠다고 한 것이오.\n"
            "소승이 무슨 간언을 해도 소용없을 터……",
        )
        self.assertEqual(
            module.TARGETS[4313],
            "\x1bCA[bm1448]\x1bCZ의 결사적인 출가 선언으로\n"
            "단결을 다진 \x1bCC에치고\x1bCZ 무사들은,\n"
            "\x1bCA[bm1448]\x1bCZ의 지휘 아래\n"
            "\x1bCA오쿠마 도모히데\x1bCZ를 꺾어 \x1bCC엣추\x1bCZ로 내쫓았다.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
