#!/usr/bin/env python3
"""Independent source/candidate tests for the NPC name-component repair."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
SPEC = importlib.util.spec_from_file_location("npc_builder", SCRIPT.with_name("build_npc_name_component_quality_v1.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load NPC builder")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class NpcNameComponentQualityTests(unittest.TestCase):
    def test_inventory_is_unique_and_complete(self) -> None:
        BUILDER.assert_unique_ids()
        self.assertEqual(len(BUILDER.COMPONENT_FIXES), 19)
        self.assertEqual(len(BUILDER.STATIC_FIXES), 10)
        self.assertEqual(len(BUILDER.COMPOSITIONS), 16)
        self.assertEqual(BUILDER.AUDITED_COMPOSITION_ROUTE_COUNT, 39)

    def test_build_and_reparse_candidate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="unit-", dir=BUILDER.BUILD_ROOT) as root_name:
            root = Path(root_name)
            output = root / "candidate"
            manifest = root / "manifest.json"
            report = BUILDER.build(BUILDER.DEFAULT_STEAM_ROOT, output, manifest)
            self.assertEqual(report["status"], "PASS")
            self.assertTrue(manifest.is_file())
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["status"], "PASS")
            checked = BUILDER.verify_candidate(BUILDER.DEFAULT_STEAM_ROOT, output)
            self.assertEqual(checked["composition_route_count"], 16)


if __name__ == "__main__":
    unittest.main()
