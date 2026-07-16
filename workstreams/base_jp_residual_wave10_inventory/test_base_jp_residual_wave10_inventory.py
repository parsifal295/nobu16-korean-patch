#!/usr/bin/env python3
"""Regression checks for the base JP residual Wave 10 inventory."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_base_jp_residual_wave10_inventory.py"
SPEC = importlib.util.spec_from_file_location("base_jp_residual_wave10_tested", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class BaseJpResidualWave10InventoryTests(unittest.TestCase):
    def test_public_artifacts_are_source_free_and_canonical(self) -> None:
        for path in (builder.INVENTORY_PATH, builder.CONTRACTS_PATH, builder.VALIDATION_PATH):
            value, blob = builder.load_json(path)
            self.assertEqual(blob, builder.canonical_json_bytes(value))
            builder.ensure_source_free(value, str(path))

        inventory, _blob = builder.load_json(builder.INVENTORY_PATH)
        contracts, _blob = builder.load_json(builder.CONTRACTS_PATH)
        validation, _blob = builder.load_json(builder.VALIDATION_PATH)
        self.assertEqual(inventory["schema"], builder.INVENTORY_SCHEMA)
        self.assertEqual(contracts["schema"], builder.CONTRACT_SCHEMA)
        self.assertEqual(validation["schema"], builder.VALIDATION_SCHEMA)
        self.assertEqual(inventory["summary"]["total_residual"], builder.EXPECTED["total"])
        self.assertEqual(contracts["entry_count"], builder.EXPECTED["safe_contract"])
        self.assertEqual(validation["status"], "PASS")

    def test_private_pins_rederive_the_tracked_inventory_without_writing_game_files(self) -> None:
        msg_builder = builder.load_module("base_jp_residual_wave10_test_msg", builder.MSGGAME_BUILDER)
        ev_builder = builder.load_module("base_jp_residual_wave10_test_ev", builder.EV_BUILDER)
        if not msg_builder.DEFAULT_GAME_ROOT.is_dir() or not msg_builder.DEFAULT_SWITCH_ZIP.is_file():
            self.skipTest("pinned Steam or Switch input is unavailable")
        if not ev_builder.DEFAULT_GAME_ROOT.is_dir() or not ev_builder.DEFAULT_SWITCH_ZIP.is_file():
            self.skipTest("pinned event input is unavailable")
        result = builder.verify()
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["proofs"]["strict_transfer_domains_remain_disjoint"])
        self.assertFalse(result["safety"]["installed_game_files_modified"])

    def test_workstream_contains_no_game_binary(self) -> None:
        forbidden = {".bin", ".g1n", ".ttf", ".otf", ".zip", ".pixels"}
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
