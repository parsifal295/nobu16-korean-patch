#!/usr/bin/env python3
"""Regression tests for the source-free base MSG/JP msggame Wave 11 overlay."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "build_base_msggame_wave11.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("base_msggame_wave11_test_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import Wave 11 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BaseMsgGameWave11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()

    def test_inventory_partition_is_complete_and_disjoint(self) -> None:
        safe, manual, tokens = self.builder.load_inventory_partition()
        self.assertEqual(len(safe), 270)
        self.assertEqual(len(manual), 3)
        self.assertEqual(len(tokens), 59)
        all_coordinates = (
            self.builder.coordinates(safe)
            + self.builder.coordinates(manual)
            + self.builder.coordinates(tokens)
        )
        self.assertEqual(len(all_coordinates), 332)
        self.assertEqual(len(set(all_coordinates)), 332)

    def test_safe_contracts_match_the_inventory(self) -> None:
        safe, _manual, _tokens = self.builder.load_inventory_partition()
        contracts = self.builder.load_safe_contracts(safe)
        self.assertEqual(len(contracts), 270)
        self.assertEqual(self.builder.coordinates(contracts), self.builder.coordinates(safe))
        self.assertEqual(
            self.builder.coordinate_sha256(self.builder.coordinates(contracts)),
            "34B073BE510E567132BC24C8B908E56130F29BF2B2922D877C72BC4CA85FEF6A",
        )

    def test_public_artifacts_are_source_free_and_leave_deferred_rows_out(self) -> None:
        overlay = json.loads(self.builder.OVERLAY_PATH.read_text(encoding="utf-8"))
        deferred = json.loads(self.builder.DEFERRED_PATH.read_text(encoding="utf-8"))
        self.builder.assert_source_free(overlay, "test overlay")
        self.builder.assert_source_free(deferred, "test deferred")
        self.assertEqual(overlay["entry_count"], 270)
        self.assertEqual(len(overlay["entries"]), 270)
        self.assertEqual(deferred["summary"]["manual_hanja_gloss_entries"], 3)
        self.assertEqual(deferred["summary"]["nonsemantic_format_token_entries"], 59)
        safe_coordinates = set(self.builder.coordinates(overlay["entries"]))
        deferred_coordinates = set(
            self.builder.coordinates(deferred["manual_hanja_gloss_entries"])
            + self.builder.coordinates(deferred["nonsemantic_format_token_entries"])
        )
        self.assertFalse(safe_coordinates & deferred_coordinates)

    def test_pinned_stock_verification_is_read_only_and_deterministic(self) -> None:
        result = self.builder.verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["prior_switch_v13_entries"], 22924)
        self.assertEqual(result["wave11_safe_entries"], 270)
        self.assertEqual(result["manual_hanja_gloss_deferred"], 3)
        self.assertEqual(result["nonsemantic_format_token_retained"], 59)
        self.assertEqual(result["combined_changed_entries"], 23194)
        self.assertEqual(result["entry_count"], 23194)
        self.assertTrue(result["non_selected_literals_preserved"])
        self.assertTrue(result["wrapper_header_preserved"])
        self.assertFalse(result["candidate_written"])
        self.assertFalse(result["steam_file_written"])
        self.assertEqual(result["candidate"], self.builder.EXPECTED_CANDIDATE)
        self.assertTrue(self.builder.DEFAULT_SWITCH_ZIP.is_file())


if __name__ == "__main__":
    unittest.main()
