from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "nobu16_test_steam_jp_msggame_v1",
    WORKSTREAM / "build_steam_jp_msggame_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJPMsgGameTests(unittest.TestCase):
    def test_runtime_and_stock_pins(self) -> None:
        self.assertEqual(builder.RUNTIME_VERSION, "1.1.7")
        self.assertEqual(builder.STEAM_BUILD_ID, 18_823_764)
        self.assertEqual(builder.STOCK_PIN["record_count"], 21_751)
        self.assertEqual(builder.STOCK_PIN["literal_count"], 29_524)

    def test_default_overlays_are_source_free_jp(self) -> None:
        total = 0
        for spec in builder.DEFAULT_OVERLAYS:
            value = json.loads(spec["path"].read_text(encoding="utf-8"))
            self.assertEqual(value["schema"], builder.OVERLAY_SCHEMA)
            self.assertEqual(value["resource"], builder.RESOURCE)
            self.assertEqual(value["base_language"], "JP")
            self.assertNotIn("source_sc", spec["path"].read_text(encoding="utf-8").lower())
            self.assertEqual(value["entry_count"], spec["entry_count"])
            self.assertEqual(builder.sha256(spec["path"].read_bytes()), spec["sha256"])
            total += value["entry_count"]
        self.assertEqual(total, builder.EXPECTED_FOUNDATION)

    def test_real_steam_stock_structure_when_available(self) -> None:
        if not builder.DEFAULT_STOCK.is_file():
            self.skipTest("Steam 1.1.7 JP stock is not installed")
        stock = builder.stock_context(builder.DEFAULT_STOCK.read_bytes())
        self.assertEqual(len(stock["parsed"].archive.blocks), 18)
        self.assertEqual(len(stock["literals"]), 29_524)
        self.assertEqual(stock["parsed"].archive.record_count, 21_751)

    def test_real_foundation_candidate_preserves_structure_when_available(self) -> None:
        if not builder.DEFAULT_STOCK.is_file():
            self.skipTest("Steam 1.1.7 JP stock is not installed")
        candidate, manifest = builder.build_blob(
            builder.DEFAULT_STOCK.read_bytes(), builder.default_overlay_specs()
        )
        self.assertTrue(candidate)
        self.assertEqual(manifest["translation"]["applied_entry_count"], 24_211)
        self.assertEqual(manifest["translation"]["remaining_jp_semantic_count"], 4_061)
        self.assertTrue(manifest["checks"]["non_literal_structure_preserved"])
        self.assertFalse(manifest["checks"]["sc_container_used"])
        expected = json.loads(
            (WORKSTREAM / "verification.v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest, expected)


if __name__ == "__main__":
    unittest.main()
