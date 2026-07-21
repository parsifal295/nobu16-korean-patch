#!/usr/bin/env python3
"""Structural tests for the manual compact coverage ledger."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_manual_compact_full_coverage_ledger_v1.py")
spec = importlib.util.spec_from_file_location("manual_compact_coverage_ledger", BUILDER)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {BUILDER}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ManualCompactCoverageLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = module.build_ledger()

    def test_historical_inventory_is_complete(self) -> None:
        self.assertEqual(self.ledger["summary"]["target_count"], 1553)
        self.assertEqual(len(self.ledger["rows"]), 1553)
        self.assertEqual(len({row["entry_id"] for row in self.ledger["rows"]}), 1553)

    def test_static_patch_007_contract_is_authoritative(self) -> None:
        contract = self.ledger["static_patch_007_layout_contract"]
        self.assertTrue(contract["inventory_contract_matches"])
        self.assertEqual(contract["raw_g1n_limit_px"], 1440)
        self.assertEqual(contract["effective_limit_px"], 912)
        self.assertEqual(contract["max_lines"], 4)

    def test_every_row_has_an_explicit_state(self) -> None:
        states = {row["status"] for row in self.ledger["rows"]}
        self.assertNotIn(None, states)
        resolution_states = {row["resolution_status"] for row in self.ledger["rows"]}
        self.assertNotIn(None, resolution_states)
        self.assertTrue(
            all(
                state.startswith("resolved_") or state.startswith("pending_")
                for state in resolution_states
            )
        )
        self.assertFalse(self.ledger["candidate_action_conflicts"])

    def test_3000_range_is_the_expected_historical_size(self) -> None:
        check = self.ledger["three_xxx_coverage_check"]
        self.assertEqual(check["historical_target_count"], 191)
        self.assertEqual(check["expected_historical_target_count"], 191)

    def test_final_coverage_gate_has_no_pending_rows(self) -> None:
        self.assertTrue(self.ledger["summary"]["all_1553_resolved"])
        self.assertEqual(self.ledger["summary"]["unresolved_or_pending_count"], 0)
        module.validate(self.ledger, require_finished_review=True)


if __name__ == "__main__":
    unittest.main()
