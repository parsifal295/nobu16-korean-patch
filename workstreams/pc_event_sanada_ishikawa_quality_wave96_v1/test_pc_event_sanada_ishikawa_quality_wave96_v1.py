#!/usr/bin/env python3
"""Regression checks for the private W96 Sanada/Ishikawa candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_sanada_ishikawa_quality_wave96_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave96_under_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class Wave96Tests(unittest.TestCase):
    def test_scene_scope_reservations_and_layout_contract(self) -> None:
        self.assertEqual(builder.SCENE_IDS, tuple(range(8442, 8492)))
        self.assertEqual(len(builder.SCENE_IDS), 50)
        self.assertEqual(len(builder.CHANGED_IDS), 18)
        self.assertEqual(len(builder.RETAINED_IDS), 32)
        self.assertIsNotNone(builder.TARGET_RAW_WIDTHS)
        builder.validate_static_targets()
        event = (builder.PREDECESSOR_CANDIDATE_ROOT / builder.MSGEV).read_bytes()
        _header, _raw, before = builder.parse_table("strict W95c test source", event)
        for entry_id in builder.SCENE_IDS:
            metrics = builder.line_metrics(builder.TARGETS.get(entry_id, before.texts[entry_id]))
            self.assertLessEqual(len(metrics), 4)
            self.assertEqual(
                tuple(line["raw_g1n_width_px"] for line in metrics),
                builder.TARGET_RAW_WIDTHS[entry_id],
            )
            for line in metrics:
                self.assertLessEqual(line["raw_g1n_width_px"], 960)
                self.assertFalse(line["over_live_raw_960px"])
        for token, reservation in builder.SCENE_RUNTIME_RESERVATIONS.items():
            self.assertTrue(reservation["scene_limited"], token)
            self.assertFalse(reservation["runtime_proven"], token)

    def test_exact_profile_full_audit_and_candidate(self) -> None:
        self.assertIsNotNone(builder.EXPECTED_OUTPUT_PROFILE)
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        coverage = bundle.audit["coverage"]
        self.assertEqual(coverage["reviewed_scene_ids"], list(builder.SCENE_IDS))
        self.assertEqual(coverage["changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(coverage["unchanged_after_review_ids"], list(builder.RETAINED_IDS))
        self.assertEqual(len(bundle.audit["rows"]), 50)
        self.assertEqual(set(bundle.audit["direct_pc_context_profiles"]), {"jp", "en", "sc", "tc"})
        self.assertTrue(
            all(
                {"display_string", "raw_g1n_width_px", "effective_width_px", "full_width_character_count", "half_width_character_count"}.issubset(line)
                for row in bundle.audit["rows"]
                for line in row["target_lines"]
            )
        )
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["changed_row_ids"], list(builder.CHANGED_IDS))
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["network_operation_performed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
