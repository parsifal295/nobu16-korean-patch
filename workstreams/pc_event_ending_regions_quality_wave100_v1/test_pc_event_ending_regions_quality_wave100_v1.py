#!/usr/bin/env python3
"""Verify the private W100 ending-region event candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_event_ending_regions_quality_wave100_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_ending_regions_wave100_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class EventEndingRegionsQualityWave100Tests(unittest.TestCase):
    def test_audit_scope_and_static_patch_layout(self) -> None:
        event, output_profile, audit, manifest = MODULE.build_bundle(require_output_profile=True)
        self.assertEqual(output_profile, MODULE.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(audit["output_event_profile"], output_profile)
        self.assertEqual(manifest["output"], output_profile)
        self.assertEqual(audit["coverage"]["applied_row_ids"], list(MODULE.TARGET_IDS))
        self.assertEqual(audit["coverage"]["applied_row_count"], 6)
        self.assertEqual(audit["coverage"]["unresolved_runtime_hold_ids"], [])
        self.assertTrue(all(not row["over_912px"] for row in audit["rows"]))
        self.assertTrue(all(row["line_count"] <= 4 for row in audit["rows"]))
        self.assertTrue(all(not row["korean_sentence_shortened_or_deleted"] for row in audit["rows"]))
        self.assertEqual(len(event), output_profile["size"])

    def test_private_candidate_matches_deterministic_build(self) -> None:
        result = MODULE.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["applied_row_ids"], list(MODULE.TARGET_IDS))
        self.assertEqual(result["unresolved_runtime_hold_count"], 0)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["release_published"])
        self.assertFalse(result["network_operation_performed"])

    def test_only_the_six_audit_rows_change(self) -> None:
        strict, _strict_record = MODULE.load_strict_input()
        event, _profile, audit, _manifest = MODULE.build_bundle(require_output_profile=True)
        _header, raw = MODULE.decompress_wrapper(event)
        rebuilt = MODULE.parse_message_table(raw)
        changed = [index for index, (before, after) in enumerate(zip(strict.texts, rebuilt.texts)) if before != after]
        self.assertEqual(changed, list(MODULE.TARGET_IDS))
        self.assertEqual([row["entry_id"] for row in audit["rows"]], list(MODULE.TARGET_IDS))
        for row in audit["rows"]:
            self.assertEqual(set(row["direct_pc_sources"]), {"jp", "en", "sc", "tc"})
            self.assertTrue(row["all_static_patch_007_lines_pass"])
            self.assertFalse(row["tag_internal_line_break_inserted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
