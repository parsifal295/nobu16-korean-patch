from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_mikatagahara_quality_wave89_v1.py")
spec = importlib.util.spec_from_file_location("mikatagahara_wave89_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class MikatagaharaWave89Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_full_changed_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(3261, 3277)))
        self.assertEqual(module.CHANGED_IDS, module.SCENE_IDS)
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(module.RETAINED_IDS, ())
        self.assertEqual(len(module.CHANGED_IDS), 16)
        self.assertEqual(len(self.bundle.rows), 16)
        self.assertTrue(all(row["changed"] for row in self.bundle.rows))

    def test_strict_w88_predecessor(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["workstream"], module.PREDECESSOR_WORKSTREAM)
        self.assertEqual(predecessor["profile"], module.EXPECTED_W88_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])

    def test_all_rows_fit_raw960_max4_and_preserve_structure(self) -> None:
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertEqual(row["runtime_tokens"], [])
            self.assertEqual(row["runtime_reservations"], [])
            self.assertFalse(row["runtime_proven"])
        self.assertEqual(self.bundle.audit["layout_policy"]["runtime_reservations"], {})
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_exact_target_metrics_and_key_semantic_repairs(self) -> None:
        for entry_id, raw_widths in module.TARGET_RAW_WIDTHS.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], list(raw_widths))
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("상락한다니", module.TARGETS[3261])
        self.assertIn("최대 난적이자 가장 성가신", module.TARGETS[3262])
        self.assertIn("둘도 없는", module.TARGETS[3263])
        self.assertIn("추격전을 벌여", module.TARGETS[3270])
        self.assertIn("여러 충신", module.TARGETS[3273])
        self.assertIn("충복들", module.TARGETS[3274])


if __name__ == "__main__":
    unittest.main(verbosity=2)
