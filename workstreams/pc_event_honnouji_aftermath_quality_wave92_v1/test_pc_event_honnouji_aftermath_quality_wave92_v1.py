from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_honnouji_aftermath_quality_wave92_v1.py")
spec = importlib.util.spec_from_file_location("honnouji_aftermath_wave92_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class HonnoujiAftermathWave92Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_complete_self_contained_scene_scope(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7816, 7850)))
        self.assertEqual(len(module.SCENE_IDS), 34)
        self.assertEqual(len(module.CHANGED_IDS), 26)
        self.assertEqual(module.RETAINED_IDS, (7816, 7822, 7826, 7832, 7837, 7840, 7843, 7844))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(len(self.bundle.rows), 34)

    def test_strict_w91_predecessor_and_direct_pc_context(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["workstream"], module.PREDECESSOR_WORKSTREAM)
        self.assertEqual(predecessor["profile"], module.EXPECTED_W91_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(self.bundle.audit["direct_pc_context_profiles"], module.EXPECTED_CONTEXT_PROFILES)

    def test_every_reviewed_row_fits_and_preserves_structure(self) -> None:
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertFalse(row["runtime_proven"])
        self.assertTrue(self.bundle.audit["layout_policy"]["effective_width_is_report_only"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_changed_line_metrics_and_scene_limited_reservations(self) -> None:
        for entry_id, raw_widths in module.TARGET_RAW_WIDTHS.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], list(raw_widths))
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertEqual(module.SCENE_RUNTIME_RESERVATIONS["[b754]"]["display"], "기노시타 히데요시")
        self.assertEqual(module.SCENE_RUNTIME_RESERVATIONS["[bs754]"]["display"], "기노시타")
        for reservation in module.SCENE_RUNTIME_RESERVATIONS.values():
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])
        dynamic_rows = {row["entry_id"]: row for row in self.bundle.rows if row["runtime_tokens"]}
        self.assertEqual(set(dynamic_rows), {7816, 7827, 7830, 7841})
        self.assertFalse(dynamic_rows[7816]["changed"])

    def test_key_semantic_repairs_and_correct_retention(self) -> None:
        first_7823_line = module.rendered_display_line(module.TARGETS[7823].split("\n")[0])
        self.assertIn("교토를 되찾겠다", first_7823_line)
        self.assertIn("차츰", module.TARGETS[7834])
        self.assertIn("삼일천하", module.TARGETS[7847])
        self.assertIn("히데요시", module.TARGETS[7849])
        retained = next(row for row in self.bundle.rows if row["entry_id"] == 7843)
        self.assertFalse(retained["changed"])
        self.assertEqual(retained["target_ko"], "윽!?")
        self.assertEqual(retained["review_disposition"], "retained_after_review")


if __name__ == "__main__":
    unittest.main(verbosity=2)
