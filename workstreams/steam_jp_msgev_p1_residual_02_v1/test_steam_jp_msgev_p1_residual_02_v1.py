from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_msgev_p1_residual_02_v1_under_test",
    ROOT / "build_steam_jp_msgev_p1_residual_02_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class SteamJPMsgevP1Residual02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.source_path, cls.packed, cls.raw, cls.table = BUILD.load_stock(BUILD.DEFAULT_STEAM_ROOT)
        except BUILD.MsgevP1Residual02Error as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_01_audit_scope_and_manual_remainder_are_exact(self) -> None:
        ids = BUILD.load_audit_bundle()
        self.assertEqual(len(ids), BUILD.EXPECTED_COORDINATE_COUNT)
        self.assertEqual(BUILD.canonical_hash([{ "id": value } for value in ids]), BUILD.EXPECTED_COORDINATE_SHA256)
        self.assertTrue(set(BUILD.EXPECTED_MANUAL_IDS).issubset(ids))
        self.assertEqual(tuple(sorted(BUILD.MANUAL_TRANSLATIONS)), BUILD.EXPECTED_MANUAL_IDS)

    def test_02_reuse_and_manual_resolution_are_exact_and_format_safe(self) -> None:
        entries, inputs = BUILD.resolve_entries(self.table)
        self.assertEqual(len(entries), BUILD.EXPECTED_COORDINATE_COUNT)
        self.assertEqual(len(inputs), 2)
        reused = [entry for entry in entries if entry["provenance"]["kind"] == "base_ev_strdata_exact_source_hash_reuse"]
        manual = [entry for entry in entries if entry["provenance"]["kind"] == "project_authored_manual_korean"]
        self.assertEqual(len(reused), BUILD.EXPECTED_REUSE_COUNT)
        self.assertEqual([entry["id"] for entry in manual], list(BUILD.EXPECTED_MANUAL_IDS))
        for entry in entries:
            self.assertEqual(BUILD.text_hash(self.table.texts[entry["id"]]), entry["source_jp_utf16le_sha256"])
            self.assertEqual(BUILD.text_hash(entry["ko"]), entry["ko_utf16le_sha256"])
            self.assertEqual(BUILD.mismatch_keys(self.table.texts[entry["id"]], entry["ko"]), [])

    def test_03_frozen_artifacts_are_source_free_and_exact(self) -> None:
        contract, entries, _packed, _raw, _table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STEAM_ROOT)
        self.assertEqual(len(entries), BUILD.EXPECTED_COORDINATE_COUNT)
        self.assertEqual(contract["runtime_route"]["language"], "JP")
        self.assertFalse(contract["runtime_route"]["sc_container_used"])
        for path in (BUILD.PUBLIC_OVERLAY, BUILD.VALIDATION, BUILD.CONTRACT):
            BUILD.assert_source_free(path)

    def test_04_candidate_is_deterministic_and_source_is_unchanged(self) -> None:
        contract, entries, packed, raw, table = BUILD.load_frozen_inputs(BUILD.DEFAULT_STEAM_ROOT)
        before = self.source_path.read_bytes()
        candidate_a, raw_a, changed_a = BUILD.candidate_from_entries(packed, raw, table, entries)
        candidate_b, raw_b, changed_b = BUILD.candidate_from_entries(packed, raw, table, entries)
        self.assertEqual(candidate_a, candidate_b)
        self.assertEqual(raw_a, raw_b)
        self.assertEqual(changed_a, changed_b)
        self.assertEqual(len(changed_a), BUILD.EXPECTED_COORDINATE_COUNT)
        self.assertEqual(BUILD.sha256_bytes(candidate_a), contract["expected_candidate"]["packed_sha256"])
        self.assertEqual(self.source_path.read_bytes(), before)

    def test_05_source_hash_and_token_tampering_are_rejected(self) -> None:
        entries, _inputs = BUILD.resolve_entries(self.table)
        hash_tampered = copy.deepcopy(entries)
        hash_tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaises(BUILD.MsgevP1Residual02Error):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, hash_tampered)
        token_tampered = copy.deepcopy(entries)
        token_tampered[-1]["ko"] += "\n"
        token_tampered[-1]["ko_utf16le_sha256"] = BUILD.text_hash(token_tampered[-1]["ko"])
        with self.assertRaises(BUILD.MsgevP1Residual02Error):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, token_tampered)

    def test_06_private_output_root_is_enforced(self) -> None:
        with self.assertRaises(BUILD.MsgevP1Residual02Error):
            BUILD.require_private_output_root(BUILD.WORKSTREAM / "candidate")
        with tempfile.TemporaryDirectory(dir=BUILD.REPO / "tmp") as temporary:
            root = BUILD.require_private_output_root(Path(temporary))
            self.assertTrue(root.is_relative_to(BUILD.REPO / "tmp"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
