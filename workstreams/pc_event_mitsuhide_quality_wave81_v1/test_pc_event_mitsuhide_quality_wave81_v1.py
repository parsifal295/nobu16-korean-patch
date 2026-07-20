from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_mitsuhide_quality_wave81_v1.py")
spec = importlib.util.spec_from_file_location("mitsuhide_wave81_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class MitsuhideWave81Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_exact_scene_scope_and_changed_retained_partition(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7651, 7675)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in self.bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(module.CHANGED_IDS), 10)
        self.assertEqual(len(module.RETAINED_IDS), 14)

    def test_predecessor_is_strict_on_disk_w80_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W80_PROFILE)
        self.assertTrue(predecessor["strict_on_disk"])
        self.assertEqual(predecessor["workstream"], "pc_event_naomasa_quality_wave80_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_naomasa_quality_wave80_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_reviewed_rows_fit_raw960_max4_and_ignore_jp_lf(self) -> None:
        self.assertEqual(len(self.bundle.rows), 24)
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertEqual(row["runtime_tokens"], [])
        self.assertFalse(self.bundle.audit["semantic_completion"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])

    def test_runtime_contract_is_explicitly_empty_and_unproven(self) -> None:
        policy = self.bundle.audit["layout_policy"]
        self.assertEqual(policy["runtime_reservations"], {})
        self.assertTrue(policy["runtime_reservations_scene_limited"])
        self.assertFalse(policy["runtime_proven"])
        self.assertTrue(all(row["runtime_proven"] is False for row in self.bundle.rows))

    def test_exact_changed_targets_and_raw_metrics(self) -> None:
        expected_raw_widths = {
            7652: [960, 600, 768, 576],
            7661: [720, 408],
            7664: [864, 840, 600],
            7665: [576],
            7667: [504, 504],
            7668: [648, 384],
            7669: [528, 480, 672, 336],
            7671: [936, 432],
            7672: [480, 840],
            7673: [408, 864],
        }
        for entry_id, raw_widths in expected_raw_widths.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertTrue(row["changed"])
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )
        self.assertIn("섬겼다는 설", module.TARGETS[7652])
        self.assertIn("대흑천상이옵니다", module.TARGETS[7665])
        self.assertIn("마음속에 높은 이상", module.TARGETS[7673])


if __name__ == "__main__":
    unittest.main(verbosity=2)
