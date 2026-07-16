#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_steam_jp_officer_surnames_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_officer_surnames_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class SteamJpOfficerSurnamesV1Test(unittest.TestCase):
    def test_partition_is_exact_source_free_and_preserves_conflicts(self) -> None:
        overlay = module.expected_overlay(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(980, overlay["entry_count"])
        self.assertEqual(859, overlay["primary_surname_count"])
        self.assertEqual(
            module.OVERLAY_PATH.read_bytes(), module.COMMON.pretty_bytes(overlay)
        )
        self.assertEqual(1_050, overlay["provenance"]["catalog_surname_count"])
        self.assertEqual(70, overlay["provenance"]["base_owned_conflict_count"])
        self.assertFalse(overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(overlay["distribution_policy"]["contains_complete_game_resource"])
        self.assertFalse(overlay["provenance"]["sc_binary_used"])
        self.assertFalse(overlay["provenance"]["sc_runtime_path_used"])
        for entry in overlay["entries"]:
            self.assertEqual(entry["ko"].rstrip() + " ", entry["ko"])
            self.assertTrue(entry["allow_edge_whitespace_change"])
            self.assertNotIn("source_jp", entry.get("ko", ""))

    def test_oda_nobunaga_recomposes_with_required_separator(self) -> None:
        overlay = module.expected_overlay(module.DEFAULT_STOCK_ROOT)
        rows = {entry["id"]: entry for entry in overlay["entries"]}
        self.assertEqual("오다 ", rows[84]["ko"])
        self.assertEqual(module.ODA_SOURCE_HASH, rows[84]["source_jp_utf16le_sha256"])
        candidate, metrics = module.build_blob(module.DEFAULT_STOCK_ROOT)
        _wrapper, raw = module.COMMON.decompress_wrapper(candidate)
        table = module.COMMON.parse_message_table(raw)
        self.assertEqual("오다 노부나가", table.texts[84] + table.texts[1266])
        self.assertEqual("오다 노부나가", metrics["oda_nobunaga_recomposition"])

    def test_pinned_build_is_deterministic_and_read_only(self) -> None:
        stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if not stock.is_file():
            self.skipTest("pinned pristine Steam 1.1.7 JP msgdata is unavailable")
        before = (stock.stat().st_size, digest(stock))
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        after = (stock.stat().st_size, digest(stock))
        self.assertEqual("PASS", result["status"])
        self.assertEqual(980, result["surname_delta_count"])
        self.assertEqual(730, result["format_contract_backlog_after"])
        self.assertTrue(result["deterministic_ab_equal"])
        self.assertTrue(result["id_domain_preserved"])
        self.assertTrue(result["non_delta_texts_preserved"])
        self.assertEqual(before, after)
        self.assertEqual([], list(HERE.glob("*.bin")))

    def test_validation_matches_generated_model(self) -> None:
        _candidate, metrics = module.build_blob(module.DEFAULT_STOCK_ROOT)
        expected = module.validation_model(metrics)
        self.assertEqual(
            module.VALIDATION_PATH.read_bytes(), module.COMMON.pretty_bytes(expected)
        )
        for path in (MODULE_PATH, module.OVERLAY_PATH, module.VALIDATION_PATH):
            self.assertNotIn("/SC/", path.read_text(encoding="utf-8"), path)

    def test_modified_stock_fails_closed(self) -> None:
        stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if not stock.is_file():
            self.skipTest("pinned pristine Steam 1.1.7 JP msgdata is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / Path(module.RESOURCE)
            target.parent.mkdir(parents=True)
            shutil.copyfile(stock, target)
            blob = bytearray(target.read_bytes())
            blob[-1] ^= 1
            target.write_bytes(blob)
            with self.assertRaises(module.COMMON.SteamJpCommonError):
                module.build_blob(root)


if __name__ == "__main__":
    unittest.main()
