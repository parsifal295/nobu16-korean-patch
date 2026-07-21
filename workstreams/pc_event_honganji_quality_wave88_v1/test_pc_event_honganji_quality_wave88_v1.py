from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_honganji_quality_wave88_v1.py")
spec = importlib.util.spec_from_file_location("honganji_wave88_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class HonganjiWave88Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(5938, 5956)))
        self.assertEqual(module.CHANGED_IDS, (5939, 5944, 5946, 5947, 5952))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.SCENE_IDS), 18)
        self.assertEqual(len(module.CHANGED_IDS), 5)
        self.assertEqual(len(module.RETAINED_IDS), 13)

    def test_strict_w87_predecessor(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["workstream"], module.PREDECESSOR_WORKSTREAM)
        self.assertEqual(predecessor["profile"], module.EXPECTED_W87_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])

    def test_all_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 18)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertFalse(row["runtime_proven"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])
        self.assertFalse(self.bundle.audit["source_policy"]["git_operation_performed"])
        self.assertFalse(self.bundle.audit["source_policy"]["release_published"])

    def test_exact_changed_targets_and_raw_metrics(self) -> None:
        for entry_id, raw_widths in module.TARGET_RAW_WIDTHS.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], list(raw_widths))
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )

        self.assertIn("쇼군이 된", module.TARGETS[5939])
        self.assertIn("뒤에서 조종하는", module.TARGETS[5939])
        self.assertIn("미요시 나가요시", module.TARGETS[5944])
        self.assertIn("구보님", module.TARGETS[5944])
        self.assertIn("탄압받기 전에", module.TARGETS[5946])
        self.assertIn("봉기하는 편이", module.TARGETS[5946])
        self.assertIn("아직 건재하다", module.TARGETS[5947])
        self.assertIn("미연에", module.TARGETS[5947])
        self.assertIn("반기를 들다니", module.TARGETS[5952])
        self.assertIn("인망이 없는", module.TARGETS[5952])

    def test_scene_limited_runtime_reservation(self) -> None:
        reservation = module.SCENE_RUNTIME_RESERVATIONS["[bm75]"]
        self.assertEqual(reservation["display"], "아시카가 요시테루")
        self.assertEqual(reservation["source_slot_id"], 75)
        self.assertEqual(reservation["reserved_raw_g1n_width_px"], 408)
        self.assertTrue(reservation["scene_limited"])
        self.assertFalse(reservation["runtime_proven"])

        row = next(row for row in self.bundle.rows if row["entry_id"] == 5944)
        self.assertEqual(row["runtime_tokens"], ["[bm75]"])
        self.assertEqual(len(row["runtime_reservations"]), 1)
        self.assertEqual(row["runtime_reservations"][0]["reserved_raw_g1n_width_px"], 408)
        self.assertEqual(
            row["target_lines"][0]["display_string"],
            "아시카가 요시테루 공·미요시 나가요시와는",
        )
        self.assertEqual(row["target_lines"][0]["raw_g1n_width_px"], 960)
        self.assertEqual(row["target_lines"][2]["raw_g1n_width_px"], 960)


if __name__ == "__main__":
    unittest.main(verbosity=2)
