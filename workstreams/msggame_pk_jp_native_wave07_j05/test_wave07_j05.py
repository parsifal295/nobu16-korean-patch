#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
import unittest
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))

import build_wave07_j05 as build  # noqa: E402


PRIVATE = build.PRIVATE_CONTEXT
OVERLAY = build.OVERLAY_PATH
STOCK = Path(
    r"F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/"
    r"file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin"
)
EXPECTED_OVERLAY_SHA256 = "A2026459F9B4DBEB02712493C1745F291940FE960AD9715E319E74C0671F7A08"
EXPECTED_CANDIDATE_SHA256 = "064D9EF05AA03EAF9D7C5DE32B8EDF6024A00F5A6119D4B77122AA5EB773E478"
SOURCE_SCRIPT = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Wave07J05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_entries, cls.private_map = build.load_private(PRIVATE)
        cls.support = build.load_block15_support(build.BLOCK15_SUPPORT, cls.private_map)
        cls.translations, cls.origins, cls.stats = build.assemble(
            cls.private_entries, cls.support
        )
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

    def test_exact_partition_and_standard_overlay_schema(self) -> None:
        self.assertEqual(681, len(self.private_map))
        self.assertEqual(set(self.private_map), set(self.translations))
        self.assertEqual(681, self.overlay["entry_count"])
        self.assertEqual("MSG_PK/JP/msggame.bin", self.overlay["resource"])
        self.assertEqual("JP", self.overlay["base_language"])
        self.assertEqual(build.COORDINATES_SHA256, self.overlay["coordinates_sha256"])
        coordinates = set()
        for entry in self.overlay["entries"]:
            self.assertEqual(
                {
                    "block_id",
                    "record_id",
                    "literal_id",
                    "source_jp_utf16le_sha256",
                    "ko",
                },
                set(entry),
            )
            coordinate = (entry["block_id"], entry["record_id"], entry["literal_id"])
            coordinates.add(coordinate)
        self.assertEqual(set(self.private_map), coordinates)

    def test_hashes_invariants_and_repeated_sources(self) -> None:
        by_hash: dict[str, set[str]] = defaultdict(set)
        for entry in self.overlay["entries"]:
            coordinate = (entry["block_id"], entry["record_id"], entry["literal_id"])
            source = self.private_map[coordinate]["jp"]
            self.assertEqual(build.text_hash(source), entry["source_jp_utf16le_sha256"])
            self.assertEqual([], build.common.invariant_mismatches(source, entry["ko"]))
            self.assertIsNone(SOURCE_SCRIPT.search(entry["ko"]))
            by_hash[entry["source_jp_utf16le_sha256"]].add(entry["ko"])
        self.assertEqual(575, len(by_hash))
        self.assertTrue(all(len(values) == 1 for values in by_hash.values()))
        self.assertEqual(409, self.stats["invariant_profile_count"])

    def test_disjoint_manual_and_verified_block15_support(self) -> None:
        manual = {coordinate for coordinate in self.translations if coordinate[0] != 15}
        supported = {coordinate for coordinate in self.translations if coordinate[0] == 15}
        self.assertEqual(313, len(manual))
        self.assertEqual(368, len(supported))
        self.assertEqual(supported, set(self.support))
        self.assertEqual(build.BLOCK15_SUPPORT_SHA256, digest(build.BLOCK15_SUPPORT))

    def test_tracked_overlay_is_deterministic_builder_output(self) -> None:
        expected = build.json_bytes(
            build.make_overlay(self.private_entries, self.translations, self.stats)
        )
        self.assertEqual(expected, OVERLAY.read_bytes())
        self.assertEqual(EXPECTED_OVERLAY_SHA256, digest(OVERLAY))

    def test_public_workstream_has_no_source_script(self) -> None:
        scanned = 0
        for path in ROOT.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix.lower() not in {".py", ".json", ".md"}:
                continue
            scanned += 1
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(SOURCE_SCRIPT.search(text), path)
        self.assertGreaterEqual(scanned, 7)
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_commercial_source_text"]
        )

    def test_validation_and_review_evidence(self) -> None:
        validation = json.loads(build.VALIDATION_PATH.read_text(encoding="utf-8"))
        review = json.loads(build.REVIEW_PATH.read_text(encoding="utf-8"))
        self.assertEqual(681, validation["entry_count"])
        self.assertEqual(2_411, validation["candidate"]["remaining_jp_semantic_count"])
        self.assertTrue(
            all(value == "PASS" for value in validation["checks"].values() if isinstance(value, str))
        )
        self.assertFalse(validation["checks"]["steam_game_file_written"])
        self.assertEqual("PASS", review["status"])
        self.assertEqual(681, review["evidence"]["reviewed_coordinate_count"])
        self.assertEqual(313, review["manual_coordinate_count"])
        self.assertEqual(368, review["verified_support_coordinate_count"])
        self.assertFalse(review["commercial_source_text_in_public_artifacts"])

    @unittest.skipUnless(STOCK.exists(), "exact Steam 1.1.7 stock backup is unavailable")
    def test_steam_stock_loader_and_ab_candidate(self) -> None:
        before = STOCK.read_bytes()
        _stock, replacements = build.validate_overlay_with_stock(OVERLAY, STOCK)
        self.assertEqual(681, len(replacements))
        first, first_meta = build.build_candidate(STOCK, OVERLAY)
        second, second_meta = build.build_candidate(STOCK, OVERLAY)
        self.assertEqual(first, second)
        self.assertEqual(first_meta, second_meta)
        self.assertEqual(EXPECTED_CANDIDATE_SHA256, build.sha256(first))
        self.assertEqual(25_861, first_meta["applied_entry_count"])
        self.assertEqual(2_411, first_meta["remaining_jp_semantic_count"])
        self.assertTrue(first_meta["non_literal_structure_preserved"])
        self.assertEqual(before, STOCK.read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
