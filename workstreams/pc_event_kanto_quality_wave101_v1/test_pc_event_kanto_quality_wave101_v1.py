#!/usr/bin/env python3
"""Regression tests for the Wave 101 Kanto event quality candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_event_kanto_quality_wave101_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_kanto_wave101_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class KantoQualityWave101Tests(unittest.TestCase):
    def test_scope_is_pinned(self) -> None:
        self.assertEqual(
            MODULE.APPLIED_IDS,
            (3489, 3490, 3491, 3493, 3497, 3500, 3502, 3505, 3506, 3508, 3510, 3514, 3516, 3522, 3526),
        )
        self.assertEqual(MODULE.RUNTIME_RESERVATION_IDS, (3514, 3522, 3526))

    def test_deterministic_bundle(self) -> None:
        event, audit, manifest = MODULE.build_bundle(require_output_profile=True)
        self.assertEqual(audit["output_event_profile"], MODULE.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(manifest["output"], MODULE.EXPECTED_OUTPUT_PROFILE)
        self.assertEqual(audit["coverage"]["applied_row_ids"], list(MODULE.APPLIED_IDS))
        self.assertEqual(audit["coverage"]["runtime_reservation_ids"], list(MODULE.RUNTIME_RESERVATION_IDS))
        self.assertTrue(audit["coverage"]["all_rows_static_patch_007_pass"])
        self.assertTrue(audit["coverage"]["all_rows_four_or_fewer_lines"])
        self.assertTrue(audit["coverage"]["all_rows_sentence_shortened_or_deleted_false"])
        self.assertEqual(len(event), MODULE.EXPECTED_OUTPUT_PROFILE["size"])
        rows = {row["entry_id"]: row for row in audit["rows"]}
        for entry_id in MODULE.RUNTIME_RESERVATION_IDS:
            self.assertFalse(rows[entry_id]["runtime_token_policy"]["runtime_proven"])
            self.assertTrue(rows[entry_id]["runtime_token_policy"]["strict_full_name_reservation_preserved_from_kanto_audit"])

    def test_private_candidate_matches_after_build(self) -> None:
        result = MODULE.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["release_published"])
        self.assertFalse(result["network_operation_performed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
