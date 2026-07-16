#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_wave08_j05.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_common_messages_wave08_j05", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)
JP_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Wave08J05Test(unittest.TestCase):
    def test_triage_batch_is_the_exact_live_revision_assignment(self) -> None:
        batch = module.load_triage_batch()
        self.assertEqual(batch["batch_id"], module.BATCH_ID)
        self.assertEqual(batch["resource"], module.RESOURCE)
        self.assertEqual(batch["current_ids"], module.EXPECTED_IDS)
        self.assertEqual(batch["legacy_ids"], module.EXPECTED_LEGACY_IDS)
        self.assertEqual(batch["semantic_entry_count"], 6)
        self.assertEqual(batch["translation_action"], "translate")
        self.assertEqual(
            batch["current_ids_sha256"],
            "C83177BF2468E12B2AA62F75FDA3E50657A934548405AC9E3C1E2169BCAFB035",
        )
        self.assertEqual(
            batch["source_rows_sha256"],
            "2444099BD0948840E866A13FEE364D0AE4A6E30D04C3E055E2304F6817C5EAFF",
        )

    def test_public_delta_is_exact_source_free_and_jp_runtime_only(self) -> None:
        overlay, _blob = module.load_overlay()
        self.assertEqual([row["id"] for row in overlay["entries"]], module.EXPECTED_IDS)
        self.assertEqual(overlay["entry_count"], 6)
        payload = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (module.OVERLAY_PATH, module.VALIDATION_PATH)
        )
        self.assertIsNone(JP_SCRIPT_RE.search(payload))
        self.assertNotIn('"source_jp"', payload)
        self.assertNotIn("/SC/", MODULE_PATH.read_text(encoding="utf-8"))
        self.assertNotIn("/TC/", MODULE_PATH.read_text(encoding="utf-8"))
        self.assertNotIn("/EN/", MODULE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(Path(module.RESOURCE).parts[1], "JP")
        self.assertEqual(list(HERE.rglob("*.bin")), [])

    def test_korean_revisions_preserve_live_format_contract(self) -> None:
        expected = {
            15021: "삿사",
            22663: "아군 세력 하나마다 부대 능력+%d（최대 +%d）",
            23164: "성 개발률 25％마다 부대 능력 상승",
            25208: "혼란 부여",
            25463: "혼란 부여",
            25900: "세력 목표를 달성한 증표",
        }
        overlay, _blob = module.load_overlay()
        self.assertEqual({row["id"]: row["ko"] for row in overlay["entries"]}, expected)
        stock_path = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if not stock_path.is_file():
            self.skipTest("local pinned pristine Steam 1.1.7 JP stock is unavailable")
        stock = module.COMMON.load_pinned(
            stock_path,
            module.COMMON.STEAM_PINS[module.NAME],
            "Steam 1.1.7 pristine JP msgdata",
        )
        for entry in overlay["entries"]:
            source = stock.table.texts[entry["id"]]
            self.assertIsNotNone(HANGUL_RE.search(entry["ko"]), entry["id"])
            self.assertIsNone(JP_SCRIPT_RE.search(entry["ko"]), entry["id"])
            self.assertEqual(
                module.COMMON.common.invariant_mismatches(source, entry["ko"]),
                [],
                entry["id"],
            )

    def test_pinned_pristine_build_and_validation_pass(self) -> None:
        stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if not stock.is_file():
            self.skipTest("local pinned pristine Steam 1.1.7 JP stock is unavailable")
        before = (stock.stat().st_size, sha256(stock))
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        after = (stock.stat().st_size, sha256(stock))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["delta_applied_count"], 6)
        self.assertEqual(result["total_common_applied_count"], 39_513)
        self.assertEqual(result["remaining_legacy_unresolved_count"], 90)
        self.assertTrue(result["non_delta_texts_preserved"])
        self.assertTrue(result["wrapper_prefix_preserved"])
        self.assertTrue(result["deterministic_ab_equal"])
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
