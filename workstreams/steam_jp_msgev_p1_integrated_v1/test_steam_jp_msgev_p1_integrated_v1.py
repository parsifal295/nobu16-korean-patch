from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_msgev_p1_integrated_v1_under_test",
    ROOT / "build_steam_jp_msgev_p1_integrated_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class SteamJPMsgevP1IntegratedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.source_path, cls.packed, cls.raw, cls.table = BUILD.load_stock(BUILD.DEFAULT_STEAM_ROOT)
        except BUILD.IntegratedP1Error as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_01_inputs_share_exact_active_v6_baseline_and_are_disjoint(self) -> None:
        entries, inputs = BUILD.resolve_entries(self.table)
        self.assertEqual(len(inputs), 2)
        self.assertEqual(len(entries), BUILD.EXPECTED_TOTAL)
        self.assertEqual(sum(entry["input_overlay"] == "p1_01" for entry in entries), BUILD.EXPECTED_PER_OVERLAY)
        self.assertEqual(sum(entry["input_overlay"] == "p1_02" for entry in entries), BUILD.EXPECTED_PER_OVERLAY)
        self.assertEqual(len({entry["id"] for entry in entries}), BUILD.EXPECTED_TOTAL)

    def test_02_frozen_source_free_artifacts_are_exact(self) -> None:
        contract, entries, _packed, _raw, _table = BUILD.load_frozen(BUILD.DEFAULT_STEAM_ROOT)
        self.assertEqual(len(entries), BUILD.EXPECTED_TOTAL)
        self.assertEqual(contract["active_v6_baseline"], BUILD.STOCK)
        for path in (BUILD.PUBLIC_OVERLAY, BUILD.VALIDATION, BUILD.CONTRACT):
            BUILD.assert_source_free(path)

    def test_03_candidate_is_deterministic_and_preserves_source(self) -> None:
        contract, entries, packed, raw, table = BUILD.load_frozen(BUILD.DEFAULT_STEAM_ROOT)
        before = self.source_path.read_bytes()
        candidate_a, raw_a, changed_a = BUILD.candidate_from_entries(packed, raw, table, entries)
        candidate_b, raw_b, changed_b = BUILD.candidate_from_entries(packed, raw, table, entries)
        self.assertEqual(candidate_a, candidate_b)
        self.assertEqual(raw_a, raw_b)
        self.assertEqual(changed_a, changed_b)
        self.assertEqual(len(changed_a), BUILD.EXPECTED_TOTAL)
        self.assertEqual(BUILD.sha256_bytes(candidate_a), contract["expected_candidate"]["packed_sha256"])
        self.assertEqual(self.source_path.read_bytes(), before)

    def test_04_source_hash_and_format_tampering_are_rejected(self) -> None:
        entries, _inputs = BUILD.resolve_entries(self.table)
        hash_tampered = copy.deepcopy(entries)
        hash_tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaises(BUILD.IntegratedP1Error):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, hash_tampered)
        format_tampered = copy.deepcopy(entries)
        format_tampered[-1]["ko"] += "\n"
        format_tampered[-1]["ko_utf16le_sha256"] = BUILD.text_hash(format_tampered[-1]["ko"])
        with self.assertRaises(BUILD.IntegratedP1Error):
            BUILD.candidate_from_entries(self.packed, self.raw, self.table, format_tampered)

    def test_05_private_output_root_is_enforced(self) -> None:
        with self.assertRaises(BUILD.IntegratedP1Error):
            BUILD.private_output_root(BUILD.WORKSTREAM / "candidate")
        with tempfile.TemporaryDirectory(dir=BUILD.REPO / "tmp") as temporary:
            self.assertTrue(BUILD.private_output_root(Path(temporary)).is_relative_to(BUILD.REPO / "tmp"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
