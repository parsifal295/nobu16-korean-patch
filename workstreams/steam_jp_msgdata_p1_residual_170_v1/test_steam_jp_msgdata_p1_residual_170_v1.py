"""Regression checks for the remaining Steam-JP msgdata P1 bundle."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_steam_jp_msgdata_p1_residual_170_v1.py")
SPEC = importlib.util.spec_from_file_location("steam_jp_msgdata_p1_residual_170", MODULE_PATH)
assert SPEC and SPEC.loader
subject = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(subject)


STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")


class SteamJpMsgdataP1Residual170Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_path, cls.packed, cls.raw, cls.table = subject.load_stock(STEAM_ROOT)
        cls.entries = subject.build_entries(cls.table)
        subject.freeze(STEAM_ROOT)

    def test_01_catalog_reuse_and_direct_coverage_are_exact(self) -> None:
        self.assertEqual(len(subject.BUNDLE_IDS), 170)
        self.assertEqual(len(subject.EXPECTED_REUSE), 22)
        self.assertEqual(len(subject.DIRECT_TRANSLATIONS), 148)
        self.assertEqual(set(subject.EXPECTED_REUSE) | set(subject.DIRECT_TRANSLATIONS), set(subject.BUNDLE_IDS))
        self.assertFalse(set(subject.EXPECTED_REUSE) & set(subject.DIRECT_TRANSLATIONS))
        origins = {entry["id"]: entry["translation_origin"] for entry in self.entries}
        self.assertEqual(sum(origin == "exact_source_hash_catalog_reuse" for origin in origins.values()), 22)
        self.assertEqual(sum(origin == "project_direct_translation" for origin in origins.values()), 148)

    def test_02_frozen_public_artifacts_are_source_free_and_exact(self) -> None:
        contract, entries, _packed, _raw, table = subject.load_frozen_inputs(STEAM_ROOT)
        self.assertEqual(contract["audit_bundle"], subject.AUDIT_BUNDLE)
        self.assertEqual(entries, self.entries)
        self.assertEqual(table.texts, self.table.texts)
        for path in (subject.PUBLIC_OVERLAY, subject.VALIDATION, subject.CONTRACT):
            subject.assert_source_free(path)

    def test_03_candidate_is_deterministic_and_clears_selected_residuals(self) -> None:
        candidate_a, raw_a, changed_a, residual_a = subject.candidate_from_entries(self.packed, self.raw, self.table, self.entries)
        candidate_b, raw_b, changed_b, residual_b = subject.candidate_from_entries(self.packed, self.raw, self.table, self.entries)
        self.assertEqual((candidate_a, raw_a, changed_a, residual_a), (candidate_b, raw_b, changed_b, residual_b))
        self.assertEqual(changed_a, list(subject.BUNDLE_IDS))
        self.assertEqual(residual_a, 175)
        self.assertEqual(sum(subject.is_high_confidence_japanese(self.table.texts[item]) for item in subject.BUNDLE_IDS), 170)

    def test_04_source_hash_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.entries)
        tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaises(subject.MsgdataP1Residual170Error):
            subject.validate_entries(self.table, tampered)

    def test_05_token_tamper_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.entries)
        index = next(index for index, entry in enumerate(tampered) if entry["id"] == 22633)
        tampered[index]["ko"] = tampered[index]["ko"].replace("%+d", "")
        tampered[index]["ko_utf16le_sha256"] = subject.text_hash(tampered[index]["ko"])
        with self.assertRaises(subject.MsgdataP1Residual170Error):
            subject.validate_entries(self.table, tampered)

    def test_06_private_output_root_is_enforced(self) -> None:
        with self.assertRaises(subject.MsgdataP1Residual170Error):
            subject.require_private_output_root(subject.REPO_ROOT / "release_candidate")


if __name__ == "__main__":
    unittest.main(verbosity=2)
