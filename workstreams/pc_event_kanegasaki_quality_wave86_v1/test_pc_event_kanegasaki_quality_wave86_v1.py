from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILD = SCRIPT.with_name("build_pc_event_kanegasaki_quality_wave86_v1.py")
spec = importlib.util.spec_from_file_location("kanegasaki_wave86_test_target", BUILD)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class KanegasakiWave86Tests(unittest.TestCase):
    def test_authored_scope_targets_and_raw960_metrics(self) -> None:
        self.assertEqual(module.SCENE_IDS, tuple(range(3230, 3245)))
        self.assertEqual(module.CHANGED_IDS, (3231, 3234, 3238))
        self.assertEqual(tuple(module.TARGETS), module.CHANGED_IDS)
        self.assertEqual(len(module.RETAINED_IDS), 12)
        self.assertFalse(module.SCENE_RUNTIME_RESERVATIONS)
        module.validate_static_targets()
        for entry_id, raw_widths in module.TARGET_RAW_WIDTHS.items():
            metrics = module.line_metrics(module.TARGETS[entry_id])
            self.assertEqual(
                tuple(line["raw_g1n_width_px"] for line in metrics),
                raw_widths,
            )
            self.assertLessEqual(len(metrics), module.MAX_LINES)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in metrics))

    @unittest.skipUnless(
        module.predecessor_configured() and module.EXPECTED_OUTPUT_PROFILE is not None,
        "W85 predecessor and W86 output profile are intentionally pending",
    )
    def test_strict_w85_predecessor_and_private_candidate_contract(self) -> None:
        bundle = module.prepare(require_output_profile=True)
        self.assertEqual(tuple(sorted(bundle.changed)), module.CHANGED_IDS)
        self.assertEqual(
            tuple(row["entry_id"] for row in bundle.rows if not row["changed"]),
            module.RETAINED_IDS,
        )
        self.assertEqual(len(bundle.rows), 15)
        self.assertFalse(bundle.audit["semantic_completion"])
        self.assertFalse(bundle.audit["source_policy"]["korean_text_shortened_or_deleted"])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        for row in bundle.rows:
            self.assertEqual(row["jp_lf_policy"], "ignored")
            self.assertFalse(row["japanese_source_line_breaks_used"])
            self.assertFalse(row["runtime_tokens"])
            self.assertFalse(row["runtime_proven"])
            self.assertLessEqual(row["target_manual_line_count"], 4)
            self.assertTrue(all(not line["over_live_raw_960px"] for line in row["target_lines"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
