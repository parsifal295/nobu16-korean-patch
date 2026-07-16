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
MODULE_PATH = HERE / "build_wave08_j03.py"
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_common_messages_wave08_j03", MODULE_PATH
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


class Wave08J03Test(unittest.TestCase):
    def test_triage_scope_is_the_exact_disjoint_title_batch(self) -> None:
        _triage, batch = module.read_triage_batch()
        self.assertEqual(module.EXPECTED_IDS, batch["current_ids"])
        self.assertEqual(31, batch["semantic_entry_count"])
        self.assertEqual({"previous_dummy_slot_now_semantic": 31}, batch["cause_counts"])
        self.assertEqual("translate", batch["translation_action"])
        self.assertFalse(
            set(module.EXPECTED_IDS) & {301, 1584, 4370, 4640, 8839, 17361, 17689}
        )

    def test_overlay_is_exact_source_free_and_uses_consistent_title_terms(self) -> None:
        overlay, blob = module.load_overlay(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(module.COMMON.pretty_bytes(overlay), blob)
        self.assertEqual(31, overlay["entry_count"])
        values = {row["id"]: row["ko"] for row in overlay["entries"]}
        self.assertEqual("혼노지 탈출", values[13_808])
        self.assertEqual("도키 요리노리 추방", values[13_818])
        self.assertEqual("덴쇼 진고의 난", values[13_822])
        self.assertEqual("야마자키 전투·아케치 승리", values[13_824])
        self.assertEqual("미카와 나카이리", values[13_829])
        self.assertEqual("시대 개요（덴쇼１０년）", values[13_849])
        self.assertEqual("시대 개요（위가해내）", values[13_856])
        self.assertEqual(values[13_848], values[13_851])
        self.assertEqual(values[13_849], values[13_852])
        self.assertEqual(values[13_850], values[13_853])
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
        self.assertEqual(31, result["delta_applied_count"])
        self.assertEqual(39_538, result["total_common_applied_count"])
        self.assertEqual(65, result["remaining_legacy_unresolved_count"])
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
