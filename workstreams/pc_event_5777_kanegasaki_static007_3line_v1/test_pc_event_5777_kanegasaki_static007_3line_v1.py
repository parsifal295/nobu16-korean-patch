#!/usr/bin/env python3
"""Regression tests for the event-5777 Static Patch 007 candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_event_5777_kanegasaki_static007_3line_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("event_5777_static007_under_test", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class Event5777Static007Tests(unittest.TestCase):
    def test_authoritative_static007_three_line_layout(self) -> None:
        builder.validate_authored_target()
        lines = builder.line_metrics(builder.TARGET_KO)
        self.assertEqual(len(lines), 3)
        self.assertLessEqual(len(lines), 4)
        self.assertEqual(tuple(line["raw_g1n_width_px"] for line in lines), (1056, 816, 912))
        self.assertEqual(tuple(line["effective_width_px"] for line in lines), (660, 510, 570))
        for line in lines:
            self.assertLessEqual(line["raw_g1n_width_px"], 1440)
            self.assertLessEqual(line["effective_width_px"], 912)
            self.assertFalse(line["over_raw_1440px"])
            self.assertFalse(line["over_effective_912px"])
            self.assertTrue(line["passes_static_patch_007"])

    def test_strict_w97_source_evidence_and_one_row_diff(self) -> None:
        _event, before, _raw, predecessor_profile = builder.load_predecessor()
        self.assertEqual(predecessor_profile, builder.EXPECTED_PREDECESSOR_PROFILE)
        self.assertEqual(before.texts[5777], builder.EXPECTED_PREDECESSOR_KO)
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(bundle.audit["actual_changed_row_ids"], [5777])
        self.assertEqual(bundle.audit["actual_changed_row_count"], 1)
        row = bundle.audit["exact_one_row_diff"]
        self.assertEqual(row["line_count"], 3)
        self.assertEqual(row["target_ko"], builder.TARGET_KO)
        self.assertEqual(row["semantic_term_choice"]["selected_term"], "의지")
        self.assertFalse(row["over_raw_1440px"])
        self.assertFalse(row["over_effective_912px"])
        self.assertEqual(set(bundle.audit["source_profiles"]["direct_pc_contexts"]), {"jp", "en", "sc", "tc"})
        self.assertEqual(bundle.audit["layout_policy"]["raw_hard_limit_px"], 1440)
        self.assertEqual(bundle.audit["layout_policy"]["effective_width_hard_limit_px"], 912)

    def test_private_candidate_exactness(self) -> None:
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["changed_row_ids"], [5777])
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["network_operation_performed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
