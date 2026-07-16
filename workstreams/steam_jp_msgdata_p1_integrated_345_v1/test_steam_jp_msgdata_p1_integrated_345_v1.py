"""Regression tests for the merged Steam-JP msgdata P1 staging candidate."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_steam_jp_msgdata_p1_integrated_345_v1.py")
SPEC = importlib.util.spec_from_file_location("steam_jp_msgdata_p1_integrated_345", MODULE_PATH)
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class SteamJpMsgdataP1Integrated345Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.source_path, cls.packed, cls.raw, cls.table = BUILD.load_stock(BUILD.DEFAULT_STEAM_ROOT)
            cls.entries, cls.expected_by_id = BUILD.load_merged_input_entries(cls.table)
            BUILD.freeze(BUILD.DEFAULT_STEAM_ROOT)
        except BUILD.MsgdataP1IntegratedError as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_01_input_overlays_are_nonoverlapping_and_source_gated(self) -> None:
        self.assertEqual(len(self.entries), 345)
        self.assertEqual(len(self.expected_by_id), 345)
        self.assertEqual(sum(entry["source_bundle"] == BUILD.INPUTS[0]["bundle_id"] for entry in self.entries), 175)
        self.assertEqual(sum(entry["source_bundle"] == BUILD.INPUTS[1]["bundle_id"] for entry in self.entries), 170)
        self.assertEqual(BUILD.canonical_hash([{"id": entry["id"]} for entry in self.entries]), BUILD.BUNDLE_COORDINATE_SHA256)
        self.assertEqual(BUILD.validate_merged_entries(self.table, self.entries, self.expected_by_id), self.entries)

    def test_02_frozen_artifacts_are_source_free_and_pin_inputs(self) -> None:
        contract, entries, expected_by_id, _packed, _raw, table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STEAM_ROOT)
        self.assertEqual(contract["merged_audit_bundle"], BUILD.MERGED_BUNDLE)
        self.assertEqual(entries, self.entries)
        self.assertEqual(expected_by_id, self.expected_by_id)
        self.assertEqual(table.texts, self.table.texts)
        for path in (BUILD.PUBLIC_OVERLAY, BUILD.VALIDATION, BUILD.CONTRACT):
            BUILD.assert_source_free_path(path)

    def test_03_candidate_is_deterministic_and_clears_all_345_residuals(self) -> None:
        left = BUILD.candidate_from_entries(self.packed, self.raw, self.table, self.entries, self.expected_by_id)
        right = BUILD.candidate_from_entries(self.packed, self.raw, self.table, self.entries, self.expected_by_id)
        self.assertEqual(left, right)
        _candidate, _raw, changed_ids, residual_after = left
        self.assertEqual(changed_ids, [entry["id"] for entry in self.entries])
        self.assertEqual(residual_after, 0)

    def test_04_source_hash_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.entries)
        tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaises(BUILD.MsgdataP1IntegratedError):
            BUILD.validate_merged_entries(self.table, tampered, self.expected_by_id)

    def test_05_format_token_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.entries)
        index = next(index for index, entry in enumerate(tampered) if "%+d" in entry["ko"])
        tampered[index]["ko"] = tampered[index]["ko"].replace("%+d", "")
        tampered[index]["ko_utf16le_sha256"] = BUILD.text_hash(tampered[index]["ko"])
        with self.assertRaises(BUILD.MsgdataP1IntegratedError):
            BUILD.validate_merged_entries(self.table, tampered)

    def test_06_private_output_root_is_enforced(self) -> None:
        with self.assertRaises(BUILD.MsgdataP1IntegratedError):
            BUILD.require_private_output_root(BUILD.REPO_ROOT / "release_candidate")


if __name__ == "__main__":
    unittest.main(verbosity=2)
