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
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_wave08_j02.py"
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_common_messages_wave08_j02", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)
JP_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Wave08J02Test(unittest.TestCase):
    def test_triage_scope_is_the_exact_disjoint_two_name_batch(self) -> None:
        _triage, batch = module.read_triage_batch()
        self.assertEqual(module.EXPECTED_IDS, batch["current_ids"])
        self.assertEqual([301, 1584], batch["legacy_ids"])
        self.assertEqual({"meaning_or_identity_revision": 2}, batch["cause_counts"])
        self.assertEqual("translate", batch["translation_action"])
        j01_ids = {4370, 4640, 8839, 17361, 17689}
        j03_ids = {*range(13_808, 13_830), *range(13_848, 13_857)}
        self.assertFalse(set(module.EXPECTED_IDS) & j01_ids)
        self.assertFalse(set(module.EXPECTED_IDS) & j03_ids)

    def test_overlay_is_exact_source_free_and_uses_reviewed_project_names(self) -> None:
        overlay, blob = module.load_overlay(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(module.COMMON.pretty_bytes(overlay), blob)
        self.assertEqual(2, overlay["entry_count"])
        self.assertEqual(
            {301: "겐코 에탄", 1584: "오후지 노부모토"},
            {row["id"]: row["ko"] for row in overlay["entries"]},
        )
        self.assertFalse(overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(overlay["distribution_policy"]["contains_complete_game_resource"])
        for path in (MODULE_PATH, module.OVERLAY_PATH, module.VALIDATION_PATH):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(JP_SCRIPT_RE.search(text), path)
            self.assertNotIn("/SC/", text, path)
        self.assertEqual([], list(HERE.glob("*.bin")))

    def test_pinned_pristine_ab_build_preserves_v1_baseline_and_stock(self) -> None:
        stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if not stock.is_file():
            self.skipTest("pinned pristine Steam 1.1.7 JP msgev is unavailable")
        before = (stock.stat().st_size, digest(stock))
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        after = (stock.stat().st_size, digest(stock))
        self.assertEqual("PASS", result["status"])
        self.assertEqual(13_794, result["baseline_applied_count"])
        self.assertEqual(2, result["delta_applied_count"])
        self.assertEqual(39_509, result["total_common_applied_count"])
        self.assertEqual(94, result["remaining_legacy_unresolved_count"])
        self.assertTrue(result["deterministic_ab_equal"])
        self.assertTrue(result["id_domain_preserved"])
        self.assertTrue(result["non_delta_texts_preserved"])
        self.assertEqual(before, after)

    def test_generated_models_match_tracked_overlay_and_validation(self) -> None:
        overlay = module.expected_overlay(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(module.OVERLAY_PATH.read_bytes(), module.COMMON.pretty_bytes(overlay))
        _candidate, metrics = module.build_blob(module.DEFAULT_STOCK_ROOT)
        validation = module.validation_model(metrics)
        self.assertEqual(
            module.VALIDATION_PATH.read_bytes(), module.COMMON.pretty_bytes(validation)
        )

    def test_modified_stock_fails_closed(self) -> None:
        stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if not stock.is_file():
            self.skipTest("pinned pristine Steam 1.1.7 JP msgev is unavailable")
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
