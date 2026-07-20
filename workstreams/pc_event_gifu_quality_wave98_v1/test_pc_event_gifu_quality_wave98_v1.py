#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_event_gifu_quality_wave98_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_gifu_quality_wave98_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class EventGifuQualityWave98Tests(unittest.TestCase):
    def test_authored_scope_and_layout(self) -> None:
        MODULE.validate_authored_scope()

    def test_deterministic_private_candidate(self) -> None:
        event, output_profile, audit, manifest = MODULE.build_bundle(require_output_profile=True)
        self.assertEqual(output_profile, MODULE.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(audit["output_event_profile"], output_profile)
        self.assertEqual(manifest["output"], output_profile)
        self.assertEqual(audit["coverage"]["changed_row_ids"], list(MODULE.CHANGED_IDS))
        self.assertEqual(audit["coverage"]["reviewed_scene_ids"], list(MODULE.SCENE_IDS))
        self.assertTrue(all(not row["over_912px"] for row in audit["rows"]))
        self.assertTrue(all(row["line_count"] <= 4 for row in audit["rows"]))
        self.assertEqual(len(event), output_profile["size"])

    def test_private_candidate_matches_after_build(self) -> None:
        result = MODULE.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
