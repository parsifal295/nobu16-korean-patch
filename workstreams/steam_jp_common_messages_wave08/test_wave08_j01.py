#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_wave08_j01.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_common_messages_wave08_j01", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)
JP_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Wave08J01Test(unittest.TestCase):
    def test_triage_covers_the_exact_96_unresolved_coordinates_without_overlap(self) -> None:
        triage = json.loads(module.TRIAGE_PATH.read_text(encoding="utf-8"))
        review_path = module.REPO / triage["provenance"]["legacy_unresolved_review"]
        self.assertEqual(sha256(review_path), triage["provenance"]["legacy_unresolved_review_sha256"])
        review = json.loads(review_path.read_text(encoding="utf-8"))
        expected: dict[str, set[int]] = {}
        for resource in review["resources"]:
            expected[resource["resource"]] = {
                int(row["legacy_jp_id"])
                for row in resource["entries"]
                if row["coverage"] == "unresolved"
            }
        actual: dict[str, set[int]] = {resource: set() for resource in expected}
        current: set[tuple[str, int]] = set()
        causes: Counter[str] = Counter()
        semantic = 0
        for batch in triage["batches"]:
            resource = batch["resource"]
            legacy_ids = batch["legacy_ids"]
            current_ids = batch["current_ids"]
            self.assertEqual(len(legacy_ids), len(current_ids))
            self.assertEqual(module.COMMON.canonical_hash(current_ids), batch["current_ids_sha256"])
            for legacy_id in legacy_ids:
                self.assertNotIn(legacy_id, actual[resource])
                actual[resource].add(legacy_id)
            for current_id in current_ids:
                key = (resource, current_id)
                self.assertNotIn(key, current)
                current.add(key)
            causes.update(batch["cause_counts"])
            semantic += batch["semantic_entry_count"]
        self.assertEqual(actual, expected)
        self.assertEqual(sum(map(len, actual.values())), 96)
        self.assertEqual(len(current), 96)
        self.assertEqual(semantic, 94)
        self.assertEqual(dict(causes), triage["aggregate"]["cause_counts"])
        vector = [{"resource": resource, "id": entry_id} for resource, entry_id in sorted(current)]
        self.assertEqual(
            module.COMMON.canonical_hash(vector),
            triage["aggregate"]["current_coordinates_sha256"],
        )

    def test_public_delta_is_exact_source_free_and_sc_free(self) -> None:
        overlay, _blob = module.load_overlay()
        self.assertEqual([row["id"] for row in overlay["entries"]], module.EXPECTED_IDS)
        self.assertEqual(overlay["entry_count"], 5)
        payload = "\n".join(
            path.read_text(encoding="utf-8")
            for path in HERE.rglob("*.json")
        )
        self.assertIsNone(JP_SCRIPT_RE.search(payload))
        self.assertNotIn("/SC/", payload)
        self.assertNotIn('"source_jp"', payload)
        self.assertEqual(list(HERE.rglob("*.bin")), [])

    def test_pinned_pristine_build_and_validation_pass(self) -> None:
        stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if not stock.is_file():
            self.skipTest("local pinned pristine Steam 1.1.7 JP stock is unavailable")
        before = (stock.stat().st_size, sha256(stock))
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        after = (stock.stat().st_size, sha256(stock))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["delta_applied_count"], 5)
        self.assertEqual(result["total_common_applied_count"], 39_512)
        self.assertEqual(result["remaining_legacy_unresolved_count"], 91)
        self.assertEqual(before, after)

    def test_modified_stock_fails_closed(self) -> None:
        stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if not stock.is_file():
            self.skipTest("local pinned pristine Steam 1.1.7 JP stock is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / Path(module.RESOURCE)
            target.parent.mkdir(parents=True)
            shutil.copyfile(stock, target)
            blob = bytearray(target.read_bytes())
            blob[-1] ^= 1
            target.write_bytes(blob)
            with self.assertRaises(module.COMMON.SteamJpCommonError):
                module.build_blob(root)


if __name__ == "__main__":
    unittest.main()
