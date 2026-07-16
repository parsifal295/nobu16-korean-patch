#!/usr/bin/env python3
"""Focused contract tests for the source-free P1-03 manual-layout overlay."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
MODULE_PATH = WORKSTREAM / "build_steam_jp_msgev_p1_residual_03_manual_layout_v1.py"
SPEC = importlib.util.spec_from_file_location("manual_layout_builder", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class ManualLayoutContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock_root = BUILDER.DEFAULT_STOCK_ROOT
        if not (cls.stock_root / Path(BUILDER.RESOURCE)).is_file():
            raise unittest.SkipTest("pinned v0.9 JP msgev baseline is unavailable")

    def test_freeze_and_verify_all_manual_rows(self) -> None:
        frozen = BUILDER.freeze(self.stock_root)
        self.assertEqual(frozen["status"], "PASS")
        self.assertEqual(frozen["manual_layout_entry_count"], 23)
        self.assertEqual(frozen["line_layout_entry_count"], 21)
        self.assertEqual(frozen["entity_layout_entry_count"], 2)
        verified = BUILDER.verify(self.stock_root)
        self.assertEqual(verified["status"], "PASS")
        self.assertEqual(verified["manual_layout_entry_count"], 23)

    def test_profiles_and_nonselected_preservation_are_exercised(self) -> None:
        _source, packed, raw, table = BUILDER.load_stock(self.stock_root)
        entries, _inputs = BUILDER.resolve_entries(table)
        candidate, candidate_raw, changed = BUILDER.candidate_from_entries(packed, raw, table, entries)
        self.assertEqual(tuple(changed), BUILDER.MANUAL_IDS)
        self.assertGreater(len(candidate), 0)
        self.assertGreater(len(candidate_raw), 0)
        self.assertEqual(len(entries), 23)

    def test_private_build_never_targets_the_stock_root(self) -> None:
        private_root = Path(tempfile.mkdtemp(prefix="manual-layout-test-", dir=BUILDER.REPO / "tmp"))
        result = BUILDER.build_staging_candidate(self.stock_root, private_root)
        candidate = Path(result["candidate_path"])
        self.assertTrue(candidate.is_file())
        self.assertTrue(candidate.is_relative_to(private_root.resolve()))
        self.assertFalse(result["installed_game_file_modified"])


if __name__ == "__main__":
    unittest.main()
