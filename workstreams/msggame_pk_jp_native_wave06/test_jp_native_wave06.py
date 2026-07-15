#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CATALOG = json.loads((ROOT / "catalog.v1.json").read_text(encoding="utf-8"))
PARTITION = json.loads((ROOT / "partition.v1.json").read_text(encoding="utf-8"))
PRIOR_PATH = ROOT / "public" / "msggame_ko_pk_jp_native_steam_prior_rebased_9386.v1.json"
SWITCH_PATH = ROOT / "public" / "msggame_ko_pk_jp_native_steam_switch_v13_exact_14825.v1.json"
PRIOR = json.loads(PRIOR_PATH.read_text(encoding="utf-8"))
SWITCH = json.loads(SWITCH_PATH.read_text(encoding="utf-8"))
CJK = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HEX64 = re.compile(r"[0-9A-F]{64}\Z")


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


class JpNativeWave06Tests(unittest.TestCase):
    def test_steam_jp_stock_and_coverage_contract(self) -> None:
        self.assertEqual("MSG_PK/JP/msggame.bin", CATALOG["resource"])
        self.assertEqual("JP", CATALOG["base_language"])
        self.assertEqual(721_304, CATALOG["stock_jp"]["packed_size"])
        self.assertEqual(
            "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
            CATALOG["stock_jp"]["packed_sha256"],
        )
        self.assertEqual(28_272, CATALOG["semantic_target"]["coordinate_count"])
        self.assertEqual(24_211, CATALOG["foundation"]["semantic_coverage_count"])
        self.assertEqual(4_061, CATALOG["remaining"]["coordinate_count"])
        self.assertFalse(CATALOG["proofs"]["sc_container_used"])
        self.assertFalse(CATALOG["proofs"]["sc_coordinates_used"])

    def test_five_batches_are_disjoint_and_exact(self) -> None:
        expected_counts = {"j01": 970, "j02": 969, "j03": 761, "j04": 680, "j05": 681}
        union: set[tuple[int, int, int]] = set()
        for batch in PARTITION["batches"]:
            coordinates = [tuple(value) for value in batch["coordinates"]]
            self.assertEqual(expected_counts[batch["batch_id"]], len(coordinates))
            self.assertEqual(
                batch["coordinates_sha256"],
                canonical_hash([list(value) for value in coordinates]),
            )
            self.assertTrue(union.isdisjoint(coordinates))
            union.update(coordinates)
        self.assertEqual(4_061, len(union))
        self.assertEqual(
            "8B039DF39C0A69F5A6119E52331D10B3F183C388A302FBAF32A3E55131889085",
            canonical_hash([list(value) for value in sorted(union)]),
        )

    def test_foundation_overlays_are_jp_native_and_disjoint(self) -> None:
        coordinates: list[set[tuple[int, int, int]]] = []
        for overlay, count in ((PRIOR, 9_386), (SWITCH, 14_825)):
            self.assertEqual("MSG_PK/JP/msggame.bin", overlay["resource"])
            self.assertEqual("JP", overlay["base_language"])
            self.assertEqual(count, overlay["entry_count"])
            current: set[tuple[int, int, int]] = set()
            for entry in overlay["entries"]:
                self.assertEqual(
                    {"block_id", "record_id", "literal_id", "source_jp_utf16le_sha256", "ko"},
                    set(entry),
                )
                self.assertRegex(entry["source_jp_utf16le_sha256"], HEX64)
                current.add((entry["block_id"], entry["record_id"], entry["literal_id"]))
            self.assertEqual(count, len(current))
            coordinates.append(current)
        self.assertTrue(coordinates[0].isdisjoint(coordinates[1]))
        self.assertEqual(24_211, len(coordinates[0] | coordinates[1]))

    def test_public_artifacts_contain_no_japanese_or_sc_source(self) -> None:
        for path in (ROOT / "catalog.v1.json", ROOT / "partition.v1.json", PRIOR_PATH, SWITCH_PATH):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(CJK.search(text), path)
            self.assertIsNone(KANA.search(text), path)
            self.assertNotIn("source_sc", text, path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
