from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_amago_quality_wave76_v1.py")
spec = importlib.util.spec_from_file_location("amago_wave76_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class AmagoWave76Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = module.prepare(require_output_profile=True)

    def test_scope_is_exact_and_retains_reviewed_rows(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(7199, 7214)))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(tuple(sorted(self.bundle.changed)), module.CHANGED_IDS)
        unchanged = [row["entry_id"] for row in self.bundle.rows if not row["changed"]]
        self.assertEqual(unchanged, [7204, 7206, 7208, 7209, 7210])

    def test_predecessor_is_strict_on_disk_w75_candidate(self) -> None:
        predecessor = self.bundle.manifest["predecessor"]
        self.assertEqual(predecessor["profile"], module.EXPECTED_W75_PROFILE)
        self.assertEqual(predecessor["workstream"], "pc_event_toyotomi_quality_wave75_v1")
        self.assertEqual(
            predecessor["candidate_relative"],
            "tmp/pc_event_toyotomi_quality_wave75_v1/candidate-final/MSG_PK/JP/msgev.bin",
        )

    def test_all_rows_fit_raw960_max4_and_preserve_controls(self) -> None:
        self.assertEqual(len(self.bundle.rows), len(module.SCENE_IDS))
        for row in self.bundle.rows:
            self.assertLessEqual(row["target_manual_line_count"], module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))
            self.assertTrue(all(not line["over_static_patch_912px"] for line in row["target_lines"]))
            self.assertFalse(row["japanese_source_line_breaks_used"])
        self.assertFalse(self.bundle.audit["semantic_completion"])
        self.assertFalse(self.bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])

    def test_changed_line_metrics_match_review_report(self) -> None:
        expected = {
            7199: [624, 648, 336],
            7200: [768, 768, 840, 816],
            7201: [672, 744, 864],
            7202: [768, 744, 432],
            7203: [912, 840, 624, 528],
            7205: [384],
            7207: [744, 840, 528, 408],
            7211: [792, 840, 888, 288],
            7212: [576, 720, 816, 336],
            7213: [600, 792, 552, 672],
        }
        for entry_id, raw_widths in expected.items():
            row = next(row for row in self.bundle.rows if row["entry_id"] == entry_id)
            self.assertEqual([line["raw_g1n_width_px"] for line in row["target_lines"]], raw_widths)
            self.assertEqual(
                [line["effective_width_px"] for line in row["target_lines"]],
                [(raw * 30 + 47) // 48 for raw in raw_widths],
            )

    def test_key_source_faithful_targets_are_exact(self) -> None:
        self.assertEqual(
            module.TARGETS[7203],
            "당주 \x1bCA모리 데루모토\x1bCZ를 알현하러 호송되던\n"
            "도중, \x1bCC다카하시강\x1bCZ 나루에 이르렀을 때\n"
            "\x1bCA시카노스케\x1bCZ는 \x1bCA모토하루\x1bCZ 휘하\n"
            "무사들에게 습격당했다.",
        )
        self.assertEqual(
            module.TARGETS[7207],
            "그토록 진지하게 맞서 온 적에게…\n"
            "사관까지 권해 놓고 목숨을 빼앗다니,\n"
            "비열하다는 말을 들어도\n"
            "할 말이 없겠구나…",
        )
        self.assertEqual(
            module.TARGETS[7213],
            "하지만 그의 불굴의 정신은\n"
            "후세 사람들에게 큰 감동을 주었고,\n"
            "그 충절의 마음은 지금도\n"
            "많은 이들에게 칭송받고 있다…",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
