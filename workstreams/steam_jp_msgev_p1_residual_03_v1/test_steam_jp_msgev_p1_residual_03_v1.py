from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_msgev_p1_residual_03_v1_under_test",
    ROOT / "build_steam_jp_msgev_p1_residual_03_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class SteamJPMsgevP1Residual03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.source_path, cls.packed, cls.raw, cls.table = BUILD.load_stock(BUILD.DEFAULT_STOCK_ROOT)
        except BUILD.MsgevP1Residual03Error as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_01_audit_scope_and_runtime_preservation_are_exact(self) -> None:
        ids, hashes = BUILD.load_audit()
        self.assertEqual(len(ids), 183)
        self.assertEqual(BUILD.canonical_hash([{ "id": entry_id } for entry_id in ids]), BUILD.EXPECTED_AUDIT_SHA256)
        self.assertTrue(set(BUILD.RUNTIME_STRUCTURAL_KEYS).issubset(ids))
        for entry_id, expected_hash in BUILD.RUNTIME_STRUCTURAL_KEYS.items():
            self.assertEqual(hashes[entry_id], expected_hash)

    def test_02_safe_partition_is_complete_and_disjoint(self) -> None:
        entries, manual_holds, runtime_holds = BUILD.resolve_safe_entries(self.table)
        self.assertEqual(len(entries), BUILD.EXPECTED_APPLIED_COUNT)
        self.assertEqual(len(manual_holds), BUILD.EXPECTED_MANUAL_REVIEW_HOLD_COUNT)
        self.assertEqual(len(runtime_holds), BUILD.EXPECTED_RUNTIME_PRESERVATION_COUNT)
        applied_ids = {entry["id"] for entry in entries}
        manual_ids = {entry["id"] for entry in manual_holds}
        runtime_ids = {entry["id"] for entry in runtime_holds}
        self.assertFalse(applied_ids & manual_ids)
        self.assertFalse(applied_ids & runtime_ids)
        self.assertFalse(manual_ids & runtime_ids)
        self.assertEqual(len(applied_ids | manual_ids | runtime_ids), 183)
        self.assertEqual(runtime_ids, set(BUILD.RUNTIME_STRUCTURAL_KEYS))

    def test_03_all_safe_entries_match_the_target_jp_token_profile(self) -> None:
        entries, _manual_holds, _runtime_holds = BUILD.resolve_safe_entries(self.table)
        operations = [entry["provenance"]["operation"] for entry in entries]
        self.assertEqual(operations.count("literal_committed_korean_reuse"), BUILD.EXPECTED_LITERAL_COUNT)
        self.assertEqual(operations.count("replace_equal_length_esc_lexemes_in_target_order"), BUILD.EXPECTED_ESC_REBASED_COUNT)
        for entry in entries:
            source = self.table.texts[entry["id"]]
            self.assertEqual(BUILD.text_hash(source), entry["source_jp_utf16le_sha256"])
            self.assertEqual(BUILD.message_profile(source), BUILD.message_profile(entry["ko"]))

    def test_04_special_exact_donors_have_the_actual_target_control_contract(self) -> None:
        entries, _manual_holds, _runtime_holds = BUILD.resolve_safe_entries(self.table)
        by_id = {entry["id"]: entry for entry in entries}
        self.assertEqual(by_id[9826]["ko_utf16le_sha256"], "3B59124465A8ED9C60CBB906689F43E817180A05D1A795DE939C298E5F74876B")
        self.assertEqual(
            BUILD.message_profile(by_id[9826]["ko"])["esc"],
            ["\x1bCA", "\x1bCZ", "\x1bCB", "\x1bCZ"],
        )
        self.assertEqual(BUILD.message_profile(by_id[9826]["ko"])["line_breaks"], ["\n", "\n"])
        expected = {
            10888: "B9F69492D642C8F1295CCD65A7130F20E24658ADFBD72E1EA3205B6D9594917A",
            10889: "11267E5ED7BC828CC7F31FEE7B8EB4E3B7E5C427B3889A7AE320A067113D1F6D",
            10890: "4D89C396EEE20B144960CD6F93D9FF52AAA77EEDF6B0BED2AF7271C3C495E3F0",
        }
        for entry_id, korean_hash in expected.items():
            self.assertEqual(by_id[entry_id]["ko_utf16le_sha256"], korean_hash)
            self.assertEqual(
                BUILD.message_profile(by_id[entry_id]["ko"]),
                BUILD.message_profile(self.table.texts[entry_id]),
            )
        expected_catalog_ids = {10888: 7827, 10889: 7828, 10890: 7829, 15420: 15190, 16219: 15989}
        for entry_id, catalog_entry_id in expected_catalog_ids.items():
            self.assertEqual(by_id[entry_id]["provenance"]["catalog_entry_id"], catalog_entry_id)
        validation, _blob = BUILD.read_json(BUILD.VALIDATION)
        special = validation["special_exact_donor_evidence"]
        self.assertEqual({row["id"] for row in special}, {9826, 10888, 10889, 10890, 15420, 16219})

    def test_05_frozen_artifacts_are_source_free_and_hold_only_metadata(self) -> None:
        contract, entries, _packed, _raw, _table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STOCK_ROOT)
        self.assertEqual(len(entries), BUILD.EXPECTED_APPLIED_COUNT)
        self.assertEqual(contract["overlay"]["entry_count"], BUILD.EXPECTED_APPLIED_COUNT)
        validation, _blob = BUILD.read_json(BUILD.VALIDATION)
        holds = validation["manual_review_holds"]
        self.assertEqual(len(holds), BUILD.EXPECTED_MANUAL_REVIEW_HOLD_COUNT + BUILD.EXPECTED_RUNTIME_PRESERVATION_COUNT)
        for hold in holds:
            self.assertNotIn("ko", hold)
            self.assertIn("source_jp_utf16le_sha256", hold)
        for path in (BUILD.PUBLIC_OVERLAY, BUILD.VALIDATION, BUILD.CONTRACT):
            BUILD.assert_source_free(path)

    def test_06_candidate_is_deterministic_and_preserves_all_holds(self) -> None:
        _contract, entries, packed, raw, table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STOCK_ROOT)
        before = self.source_path.read_bytes()
        candidate_a, raw_a, changed_a = BUILD.candidate_from_entries(packed, raw, table, entries)
        candidate_b, raw_b, changed_b = BUILD.candidate_from_entries(packed, raw, table, entries)
        self.assertEqual(candidate_a, candidate_b)
        self.assertEqual(raw_a, raw_b)
        self.assertEqual(changed_a, changed_b)
        self.assertEqual(len(changed_a), BUILD.EXPECTED_APPLIED_COUNT)
        _header, checked_raw = BUILD.decompress_wrapper(candidate_a)
        checked = BUILD.parse_message_table(checked_raw)
        for entry_id in BUILD.RUNTIME_STRUCTURAL_KEYS:
            self.assertEqual(checked.texts[entry_id], table.texts[entry_id])
        self.assertEqual(self.source_path.read_bytes(), before)

    def test_07_tampered_profile_or_private_output_root_is_rejected(self) -> None:
        entries, _manual_holds, _runtime_holds = BUILD.resolve_safe_entries(self.table)
        tampered = copy.deepcopy(entries)
        tampered[0]["ko"] += "\n"
        tampered[0]["ko_utf16le_sha256"] = BUILD.text_hash(tampered[0]["ko"])
        with self.assertRaises(BUILD.MsgevP1Residual03Error):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, tampered)
        with self.assertRaises(BUILD.MsgevP1Residual03Error):
            BUILD.require_private_output_root(BUILD.WORKSTREAM / "candidate")
        with tempfile.TemporaryDirectory(dir=BUILD.REPO / "tmp") as temporary:
            root = BUILD.require_private_output_root(Path(temporary))
            self.assertTrue(root.is_relative_to(BUILD.REPO / "tmp"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
