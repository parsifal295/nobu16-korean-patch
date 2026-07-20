from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_xavier_quality_wave90_v1.py")
spec = importlib.util.spec_from_file_location("xavier_wave90_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class XavierWave90Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_complete_self_contained_scene_scope(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(3277, 3287)))
        self.assertEqual(module.CHANGED_IDS, (3280, 3282, 3285, 3286))
        self.assertEqual(module.RETAINED_IDS, (3277, 3278, 3279, 3281, 3283, 3284))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(len(self.bundle.rows), 10)

    def test_strict_w89_predecessor_and_direct_pc_context(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["workstream"], module.PREDECESSOR_WORKSTREAM)
        self.assertEqual(predecessor["profile"], module.EXPECTED_W89_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(self.bundle.audit["direct_pc_context_profiles"], module.EXPECTED_CONTEXT_PROFILES)

    def test_all_reviewed_rows_fit_raw960_max4_and_preserve_structure(self) -> None:
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

    def test_changed_line_metrics_and_key_semantic_repairs(self) -> None:
        for entry_id, raw_widths in module.CHANGED_TARGET_RAW_WIDTHS.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], list(raw_widths))
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("“나는 길이다”", module.TARGETS[3280])
        self.assertIn("일본의 존재를", module.TARGETS[3282])
        self.assertIn("2년 남짓 머무는 동안", module.TARGETS[3285])
        self.assertIn("더디게나마", module.TARGETS[3286])

    def test_retained_rows_are_documented_after_review(self) -> None:
        retained = [row for row in self.bundle.rows if not row["changed"]]
        self.assertEqual([row["entry_id"] for row in retained], list(module.RETAINED_IDS))
        self.assertTrue(all(row["review_disposition"] == "retained_after_review" for row in retained))


if __name__ == "__main__":
    unittest.main(verbosity=2)
