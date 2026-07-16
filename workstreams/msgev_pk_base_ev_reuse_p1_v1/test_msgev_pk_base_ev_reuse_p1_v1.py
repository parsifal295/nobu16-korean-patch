from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("msgev_p1", HERE / "build_msgev_pk_base_ev_reuse_p1_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MsgEvPkBaseEvReuseP1Tests(unittest.TestCase):
    def test_bundle_scope_is_fixed(self) -> None:
        ids, vector_hash = MODULE.load_bundle_ids()
        self.assertEqual(len(ids), 185)
        self.assertEqual(vector_hash, "FBB7FB41E107FF298545A1BA0F2C25E78A73E336F3B8BAC4E2BADAEC1852AB44")
        self.assertEqual(tuple(sorted(MODULE.MANUAL_KO)), MODULE.EXPECTED_MANUAL_IDS)

    def test_reuse_and_manual_partition_is_complete(self) -> None:
        target, metadata = MODULE.replacements()
        self.assertEqual(len(target), 185)
        self.assertEqual(metadata["reused_exact_source_hash_count"], 182)
        self.assertEqual(metadata["project_authored_manual_count"], 3)

    def test_overlay_is_source_free_and_pinned(self) -> None:
        overlay = MODULE.expected_overlay()
        self.assertEqual(overlay["selection"]["entry_count"], 185)
        self.assertFalse(any(MODULE.JAPANESE_RE.search(row["ko"]) for row in overlay["entries"]))
        self.assertTrue(all(MODULE.HANGUL_RE.search(row["ko"]) for row in overlay["entries"]))

    def test_candidate_is_deterministic_and_narrow(self) -> None:
        first, first_metrics = MODULE.build_blob()
        second, second_metrics = MODULE.build_blob()
        self.assertEqual(first, second)
        self.assertEqual(first_metrics, second_metrics)
        self.assertEqual(first_metrics["entry_count"], 185)
        self.assertTrue(first_metrics["non_target_texts_preserved"])


if __name__ == "__main__":
    unittest.main()
