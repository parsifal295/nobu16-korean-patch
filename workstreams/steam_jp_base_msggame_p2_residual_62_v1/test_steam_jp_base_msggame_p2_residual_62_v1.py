"""Regression tests for the base Steam-JP msggame P2 residual staging set."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from collections import Counter
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_steam_jp_base_msggame_p2_residual_62_v1.py")
SPEC = importlib.util.spec_from_file_location("steam_jp_base_msggame_p2_residual_62", MODULE_PATH)
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class SteamJpBaseMsggameP2Residual62Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.stock = BUILD.stock_context(BUILD.DEFAULT_STEAM_ROOT)
            cls.entries = BUILD.build_entries(cls.stock)
            BUILD.freeze(BUILD.DEFAULT_STEAM_ROOT)
        except BUILD.P2Error as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_01_exact_source_hash_reuse_covers_all_active_residuals(self) -> None:
        self.assertEqual(len(self.stock["selected"]), 62)
        self.assertEqual(BUILD.coordinate_hash(self.stock["selected"]), BUILD.BUNDLE_COORDINATE_SHA256)
        self.assertEqual(len(self.entries), 62)
        self.assertEqual({entry["translation_origin"] for entry in self.entries}, {"exact_source_hash_catalog_reuse"})
        hashes = Counter(entry["source_jp_utf16le_sha256"] for entry in self.entries)
        self.assertEqual(set(hashes), set(BUILD.EXPECTED_REUSE_BY_SOURCE_HASH))
        self.assertEqual(sum(hashes.values()), 62)

    def test_02_frozen_public_artifacts_are_source_free_and_exact(self) -> None:
        contract, entries, stock = BUILD.load_frozen_inputs(BUILD.DEFAULT_STEAM_ROOT)
        self.assertEqual(contract["audit_bundle"], BUILD.AUDIT_BUNDLE)
        self.assertEqual(entries, self.entries)
        self.assertEqual(stock["packed"], self.stock["packed"])
        for path in (BUILD.PUBLIC_OVERLAY, BUILD.VALIDATION, BUILD.CONTRACT):
            BUILD.assert_source_free_path(path)

    def test_03_candidate_is_deterministic_and_clears_all_62_residuals(self) -> None:
        left = BUILD.candidate_from_entries(self.stock, self.entries)
        right = BUILD.candidate_from_entries(self.stock, self.entries)
        self.assertEqual(left, right)
        _candidate, _raw, changed, residual_after = left
        self.assertEqual(changed, self.stock["selected"])
        self.assertEqual(residual_after, 0)

    def test_04_source_hash_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.entries)
        tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaises(BUILD.P2Error):
            BUILD.validate_entries(self.stock, tampered)

    def test_05_newline_and_format_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.entries)
        index = next(index for index, entry in enumerate(tampered) if entry["ko"].startswith("\n"))
        tampered[index]["ko"] = tampered[index]["ko"].lstrip("\n")
        tampered[index]["ko_utf16le_sha256"] = BUILD.text_hash(tampered[index]["ko"])
        with self.assertRaises(BUILD.P2Error):
            BUILD.validate_entries(self.stock, tampered)

    def test_06_private_output_root_is_enforced(self) -> None:
        with self.assertRaises(BUILD.P2Error):
            BUILD.require_private_output_root(BUILD.REPO_ROOT / "release_candidate")


if __name__ == "__main__":
    unittest.main(verbosity=2)
