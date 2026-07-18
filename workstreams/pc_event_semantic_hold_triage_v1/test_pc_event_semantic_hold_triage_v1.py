#!/usr/bin/env python3
"""Regression tests for the PC-only event semantic-hold triage ledger."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_pc_event_semantic_hold_triage_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_event_semantic_hold_triage_v1", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PcEventSemanticHoldTriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows, cls.summary = MODULE.build()
        cls.validation = MODULE.load_validation()

    def test_live_hold_counts_and_classification_contract(self) -> None:
        MODULE.validate_contract(self.rows, self.summary, self.validation)
        self.assertEqual(self.summary["row_count"], 1074)
        self.assertEqual(
            self.summary["classification_counts"]["total"],
            {
                "runtime_printf_esc_structural": 763,
                "linebreak_or_whitespace_layout": 95,
                "pure_static_wording": 216,
            },
        )

    def test_static_anchor_contract(self) -> None:
        self.assertEqual(
            self.summary["static_anchor_counts"]["cross_resource_jp_sc_tc"],
            {"consensus": 25, "conflict": 183, "no_anchor": 8},
        )
        static_rows = [row for row in self.rows if row["triage_class"] == "pure_static_wording"]
        self.assertEqual(len(static_rows), 216)
        self.assertTrue(all(row["static_anchor"]["eligible"] for row in static_rows))

    def test_rows_and_validation_are_source_free(self) -> None:
        payload = MODULE.canonical_jsonl(self.rows)
        self.assertTrue(payload.isascii())
        self.assertNotIn(b'"current_ko"', payload)
        self.assertNotIn(b'"source_jp"', payload)
        self.assertNotIn(b'"translation"', payload)
        MODULE.source_free_row_check(self.rows)
        self.assertTrue((HERE / "validation.v1.json").read_bytes().isascii())
        self.assertTrue(json.loads((HERE / "validation.v1.json").read_text(encoding="utf-8"))["source_free"])

    def test_deterministic_source_free_output_hashes(self) -> None:
        built_payloads = MODULE.payloads(self.rows, self.summary)
        expected = self.validation["expected_output_sha256"]
        self.assertEqual(MODULE.sha256_bytes(built_payloads["ledger"]), expected["ledger"])
        self.assertEqual(MODULE.sha256_bytes(built_payloads["summary"]), expected["summary"])

    def test_triage_does_not_claim_steam_write_or_semantic_completion(self) -> None:
        self.assertFalse(self.summary["scope"]["steam_game_resource_written"])
        self.assertFalse(self.summary["scope"]["semantic_completion"])
        self.assertFalse(self.summary["source_text_emitted"])


if __name__ == "__main__":
    unittest.main()
