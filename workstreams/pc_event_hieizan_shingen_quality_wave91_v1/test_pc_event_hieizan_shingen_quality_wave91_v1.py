from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_hieizan_shingen_quality_wave91_v1.py")
spec = importlib.util.spec_from_file_location("hieizan_shingen_wave91_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class HieizanShingenWave91Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_complete_self_contained_scene_scope(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(5956, 5977)))
        self.assertEqual(module.RETAINED_IDS, (5970,))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(len(self.bundle.rows), 21)

    def test_strict_w90_predecessor_and_direct_pc_context(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["workstream"], module.PREDECESSOR_WORKSTREAM)
        self.assertEqual(predecessor["profile"], module.EXPECTED_W90_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(self.bundle.audit["direct_pc_context_profiles"], module.EXPECTED_CONTEXT_PROFILES)

    def test_all_rows_fit_raw960_max4_and_preserve_control_structure(self) -> None:
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertFalse(row["runtime_proven"])
        self.assertTrue(self.bundle.audit["layout_policy"]["effective_width_is_report_only"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_changed_line_metrics_and_scene_reservations(self) -> None:
        for entry_id, raw_widths in module.TARGET_RAW_WIDTHS.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], list(raw_widths))
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        for token in ("[b1251]", "[bm1251]"):
            reservation = module.SCENE_RUNTIME_RESERVATIONS[token]
            self.assertEqual(reservation["display"], "다케다 하루노부")
            self.assertEqual(reservation["reserved_raw_g1n_width_px"], 360)
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])

    def test_key_semantic_repairs_and_retained_row(self) -> None:
        self.assertIn("히에이산을 불태운 일의 충격은", module.TARGETS[5956])
        self.assertIn("그 목을 취하겠다", module.TARGETS[5961])
        self.assertIn("다케다 하루노부", module.SCENE_RUNTIME_RESERVATIONS["[bm1251]"]["display"])
        self.assertIn("제육천마왕", module.TARGETS[5974])
        retained = next(row for row in self.bundle.rows if row["entry_id"] == 5970)
        self.assertFalse(retained["changed"])
        self.assertEqual(retained["review_disposition"], "retained_after_review")
        self.assertEqual(retained["runtime_tokens"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
