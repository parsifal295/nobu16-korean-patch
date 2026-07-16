from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_steam_jp_msgui_p0_residual_125_v1.py")
SPEC = importlib.util.spec_from_file_location("steam_jp_msgui_p0_residual", MODULE_PATH)
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class SteamJpMsguiP0ResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.source_path, cls.packed, cls.raw, cls.table = BUILD.load_stock(BUILD.DEFAULT_STEAM_ROOT)
        except BUILD.MsguiP0Error as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_01_frozen_public_artifacts_are_source_free_and_exact(self) -> None:
        contract, entries, _packed, _raw, _table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STEAM_ROOT)
        self.assertEqual(len(entries), 125)
        self.assertEqual(contract["active_v6_baseline"], BUILD.STOCK)
        self.assertEqual(contract["runtime_route"]["language"], "JP")
        self.assertFalse(contract["runtime_route"]["sc_container_used"])
        for path in (BUILD.PUBLIC_OVERLAY, BUILD.VALIDATION, BUILD.CONTRACT):
            BUILD.assert_source_free(path)

    def test_02_translation_table_exactly_covers_current_p0_residuals(self) -> None:
        self.assertEqual(sorted(BUILD.TRANSLATIONS), BUILD.residual_ids(self.table))
        entries = BUILD.build_entries(self.table)
        self.assertEqual(len(entries), 125)
        for entry in entries:
            self.assertEqual(BUILD.text_hash(self.table.texts[entry["id"]]), entry["source_jp_utf16le_sha256"])
            self.assertEqual(BUILD.text_hash(entry["ko"]), entry["ko_utf16le_sha256"])
            self.assertEqual(BUILD.mismatch_keys(self.table.texts[entry["id"]], entry["ko"]), [])

    def test_03_candidate_is_deterministic_and_source_is_unchanged(self) -> None:
        contract, entries, packed, raw, table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STEAM_ROOT)
        before = self.source_path.read_bytes()
        candidate_a, raw_a, changed_a = BUILD.candidate_from_entries(packed, raw, table, entries)
        candidate_b, raw_b, changed_b = BUILD.candidate_from_entries(packed, raw, table, entries)
        self.assertEqual(candidate_a, candidate_b)
        self.assertEqual(raw_a, raw_b)
        self.assertEqual(changed_a, changed_b)
        self.assertEqual(len(changed_a), 125)
        self.assertEqual(BUILD.sha256_bytes(candidate_a), contract["expected_candidate"]["packed_sha256"])
        self.assertEqual(BUILD.sha256_bytes(raw_a), contract["expected_candidate"]["raw_sha256"])
        _header, checked_raw = BUILD.decompress_wrapper(candidate_a)
        self.assertEqual(BUILD.residual_ids(BUILD.parse_message_table(checked_raw)), [])
        self.assertEqual(self.source_path.read_bytes(), before)

    def test_04_source_hash_tamper_is_rejected(self) -> None:
        entries = BUILD.build_entries(self.table)
        tampered = copy.deepcopy(entries)
        tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaisesRegex(BUILD.MsguiP0Error, "JP source hash mismatch"):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, tampered)

    def test_05_token_tamper_is_rejected(self) -> None:
        entries = BUILD.build_entries(self.table)
        tampered = copy.deepcopy(entries)
        tampered[0]["ko"] += "\n"
        tampered[0]["ko_utf16le_sha256"] = BUILD.text_hash(tampered[0]["ko"])
        with self.assertRaisesRegex(BUILD.MsguiP0Error, "format/token mismatch"):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, tampered)

    def test_06_private_output_root_is_enforced(self) -> None:
        with self.assertRaises(BUILD.MsguiP0Error):
            BUILD.require_private_output_root(BUILD.WORKSTREAM_ROOT / "candidate")
        with tempfile.TemporaryDirectory(dir=BUILD.REPO_ROOT / "tmp") as temporary:
            self.assertTrue(BUILD.require_private_output_root(Path(temporary)).is_relative_to(BUILD.REPO_ROOT / "tmp"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
