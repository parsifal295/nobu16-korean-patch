from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_hieizan_quality_wave87_v1.py")
spec = importlib.util.spec_from_file_location("hieizan_wave87_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class HieiZanWave87Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(3245, 3261)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 12)
        self.assertEqual(len(module.RETAINED_IDS), 4)

    def test_strict_w86_predecessor(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["workstream"], module.PREDECESSOR_WORKSTREAM)
        self.assertEqual(predecessor["profile"], module.EXPECTED_W86_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])

    def test_all_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 16)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertEqual(row["runtime_tokens"], [])
            self.assertFalse(row["runtime_proven"])
        self.assertEqual(self.bundle.audit["layout_policy"]["runtime_reservations"], {})
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_exact_changed_targets_and_raw_metrics(self) -> None:
        for entry_id, raw_widths in module.TARGET_RAW_WIDTHS.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], list(raw_widths))
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("강소", module.TARGETS[3247])
        self.assertIn("멈추라고", module.TARGETS[3253])
        self.assertIn("주군을 귀신이라 부르게 하느니", module.TARGETS[3257])
        self.assertIn("아이러니하게도", module.TARGETS[3260])


if __name__ == "__main__":
    unittest.main(verbosity=2)
