from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_takamatsu_quality_wave83_v1.py")
spec = importlib.util.spec_from_file_location("takamatsu_wave83_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TakamatsuWave83Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7752, 7779)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 9)
        self.assertEqual(len(module.RETAINED_IDS), 18)

    def test_predecessor_is_strict_on_disk_w82_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W82_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(predecessor["workstream"], "pc_event_tenmokuzan_quality_wave82_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_tenmokuzan_quality_wave82_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_reviewed_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 27)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertEqual(row["runtime_tokens"], [])
            self.assertFalse(row["runtime_proven"])
        self.assertEqual(self.bundle.audit["layout_policy"]["runtime_reservations"], {})
        self.assertFalse(self.bundle.audit["semantic_completion"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_exact_changed_targets_and_raw_metrics(self) -> None:
        expected_raw_widths = {
            7753: [792, 648, 840],
            7754: [576, 816, 696, 384],
            7761: [696, 768, 720, 768],
            7762: [936, 768, 816],
            7768: [504, 576, 600],
            7770: [888, 888],
            7772: [648, 816, 720, 792],
            7774: [648, 888, 528, 480],
            7776: [648, 912],
        }
        for entry_id, raw_widths in expected_raw_widths.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("원군", module.TARGETS[7753])
        self.assertIn("대합전", module.TARGETS[7761])
        self.assertIn("내가 할복하겠다고", module.TARGETS[7768])
        self.assertIn("일련의 모습", module.TARGETS[7772])


if __name__ == "__main__":
    unittest.main(verbosity=2)
