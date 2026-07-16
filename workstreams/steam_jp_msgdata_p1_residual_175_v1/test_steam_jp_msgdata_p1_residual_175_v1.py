from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_steam_jp_msgdata_p1_residual_175_v1.py")
SPEC = importlib.util.spec_from_file_location("steam_jp_msgdata_p1_residual", MODULE_PATH)
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class SteamJpMsgdataP1ResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.source_path, cls.packed, cls.raw, cls.table = BUILD.load_stock(BUILD.DEFAULT_STEAM_ROOT)
        except BUILD.MsgdataP1Error as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_01_catalog_reuse_and_direct_coverage_are_exact(self) -> None:
        reuse = BUILD.exact_reuse_values(self.table)
        self.assertEqual(tuple(sorted(reuse)), BUILD.EXPECTED_REUSE_IDS)
        self.assertEqual(len(reuse), 21)
        self.assertEqual(len(BUILD.DIRECT_TRANSLATIONS), 154)
        self.assertEqual(set(reuse) | set(BUILD.DIRECT_TRANSLATIONS), set(BUILD.BUNDLE_IDS))
        self.assertFalse(set(reuse) & set(BUILD.DIRECT_TRANSLATIONS))

    def test_02_frozen_public_artifacts_are_source_free_and_exact(self) -> None:
        contract, entries, _packed, _raw, _table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STEAM_ROOT)
        self.assertEqual(len(entries), 175)
        self.assertEqual(contract["active_v6_baseline"], BUILD.STOCK)
        self.assertEqual(contract["audit_bundle"]["coordinate_sha256"], BUILD.BUNDLE_COORDINATE_SHA256)
        self.assertFalse(contract["runtime_route"]["sc_container_used"])
        for path in (BUILD.PUBLIC_OVERLAY, BUILD.VALIDATION, BUILD.CONTRACT):
            BUILD.assert_source_free(path)

    def test_03_candidate_is_deterministic_and_clears_selected_residuals(self) -> None:
        contract, entries, packed, raw, table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STEAM_ROOT)
        before = self.source_path.read_bytes()
        candidate_a, raw_a, changed_a, residual_a = BUILD.candidate_from_entries(packed, raw, table, entries)
        candidate_b, raw_b, changed_b, residual_b = BUILD.candidate_from_entries(packed, raw, table, entries)
        self.assertEqual(candidate_a, candidate_b)
        self.assertEqual(raw_a, raw_b)
        self.assertEqual(changed_a, changed_b)
        self.assertEqual(residual_a, residual_b)
        self.assertEqual(len(changed_a), 175)
        self.assertEqual(BUILD.sha256_bytes(candidate_a), contract["expected_candidate"]["packed_sha256"])
        _header, checked_raw = BUILD.decompress_wrapper(candidate_a)
        checked = BUILD.parse_message_table(checked_raw)
        self.assertFalse(any(BUILD.is_high_confidence_japanese(checked.texts[entry_id]) for entry_id in BUILD.BUNDLE_IDS))
        self.assertEqual(self.source_path.read_bytes(), before)

    def test_04_source_hash_tamper_is_rejected(self) -> None:
        entries = BUILD.build_entries(self.table)
        tampered = copy.deepcopy(entries)
        tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaisesRegex(BUILD.MsgdataP1Error, "JP source hash mismatch"):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, tampered)

    def test_05_token_tamper_is_rejected(self) -> None:
        entries = BUILD.build_entries(self.table)
        target = next(entry for entry in entries if "\n" in entry["ko"])
        tampered = copy.deepcopy(entries)
        tampered_entry = next(entry for entry in tampered if entry["id"] == target["id"])
        tampered_entry["ko"] = tampered_entry["ko"].replace("\n", "", 1)
        tampered_entry["ko_utf16le_sha256"] = BUILD.text_hash(tampered_entry["ko"])
        with self.assertRaisesRegex(BUILD.MsgdataP1Error, "format/token mismatch"):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, tampered)

    def test_06_private_output_root_is_enforced(self) -> None:
        with self.assertRaises(BUILD.MsgdataP1Error):
            BUILD.require_private_output_root(BUILD.WORKSTREAM_ROOT / "candidate")
        with tempfile.TemporaryDirectory(dir=BUILD.REPO_ROOT / "tmp") as temporary:
            self.assertTrue(BUILD.require_private_output_root(Path(temporary)).is_relative_to(BUILD.REPO_ROOT / "tmp"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
