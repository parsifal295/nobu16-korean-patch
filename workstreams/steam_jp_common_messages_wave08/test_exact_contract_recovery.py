#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_exact_contract_recovery.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_common_exact_contract_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)
JP_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class ExactContractRecoveryTest(unittest.TestCase):
    _stock_result: dict[str, object] | None = None

    @classmethod
    def stock_result(cls) -> dict[str, object]:
        if cls._stock_result is None:
            cls._stock_result = module.verify_stock(module.DEFAULT_STOCK_ROOT)
        return cls._stock_result

    def test_seven_shards_are_source_free_disjoint_and_exact(self) -> None:
        contracts, artifacts = module.load_contracts()
        self.assertEqual([row["entry_count"] for row in artifacts], module.EXPECTED_SHARD_COUNTS)
        self.assertEqual({name: len(rows) for name, rows in contracts.items()}, module.EXPECTED_COUNTS)
        self.assertEqual(sum(map(len, contracts.values())), 1796)
        payload = "\n".join(
            (module.PUBLIC_ROOT / filename).read_text(encoding="utf-8")
            for filename in module.SHARDS
        )
        self.assertIsNone(JP_SCRIPT_RE.search(payload))
        self.assertNotIn('"source_jp"', payload)
        self.assertEqual(list(module.PUBLIC_ROOT.rglob("*.bin")), [])

    def test_pinned_stock_mapping_hashes_invariants_and_zero_overlap(self) -> None:
        stock_paths = [
            module.DEFAULT_STOCK_ROOT / "MSG_PK" / "JP" / name
            for name in module.EXPECTED_COUNTS
        ]
        if not all(path.is_file() for path in stock_paths):
            self.skipTest("pinned pristine Steam 1.1.7 JP stocks are unavailable")
        result = self.stock_result()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["exact_contract_entry_count"], 1796)
        self.assertEqual(result["total_common_contract_coverage_count"], 41303)
        self.assertEqual(result["effective_korean_change_count"], 39507)
        self.assertTrue(
            all(
                value
                for key, value in result["proofs"].items()
                if key != "sc_binary_used"
            )
        )
        self.assertFalse(result["proofs"]["sc_binary_used"])
        self.assertEqual(result["resources"]["msgev.bin"]["existing_v1_overlap_count"], 0)
        self.assertEqual(result["resources"]["msgdata.bin"]["existing_v1_overlap_count"], 0)

    def test_tracked_validation_passes(self) -> None:
        if not all(
            (module.DEFAULT_STOCK_ROOT / "MSG_PK" / "JP" / name).is_file()
            for name in module.EXPECTED_COUNTS
        ):
            self.skipTest("pinned pristine Steam 1.1.7 JP stocks are unavailable")
        result = self.stock_result()
        validation = json.loads(module.VALIDATION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(
            validation["expected"]["coordinates_sha256"],
            result["coordinates_sha256"],
        )
        self.assertEqual(
            validation["expected"]["evidence"],
            module.path_spec(module.EVIDENCE_PATH),
        )

    def test_a_source_union_ko_hashes_match_without_reading_a_binary(self) -> None:
        if os.environ.get("NOBU16_AUDIT_SOURCE_UNION") != "1":
            self.skipTest("set NOBU16_AUDIT_SOURCE_UNION=1 for the heavyweight provenance audit")
        completed = subprocess.run(
            [sys.executable, "-B", str(MODULE_PATH), "audit-source-union"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result, {
            "status": "PASS",
            "audited_entry_count": 1796,
            "source_binary_used": False,
        })


if __name__ == "__main__":
    unittest.main()
