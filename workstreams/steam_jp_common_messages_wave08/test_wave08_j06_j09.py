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
MODULE_PATH = HERE / "build_wave08_j06_j09.py"
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_common_messages_wave08_j06_j09", MODULE_PATH
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


class Wave08J06J09Test(unittest.TestCase):
    def test_triage_scope_is_exact_and_disjoint(self) -> None:
        rows = module.triage_batches()
        all_ids: dict[str, set[int]] = {}
        self.assertEqual(4, len(rows))
        for spec in module.BATCHES:
            row = rows[spec["batch_id"]]
            self.assertEqual(spec["ids"], row["current_ids"])
            self.assertEqual(len(spec["ids"]), row["semantic_entry_count"])
            current = set(spec["ids"])
            self.assertFalse(current & all_ids.setdefault(spec["resource"], set()))
            all_ids[spec["resource"]].update(current)

    def test_overlays_are_source_free_and_preserve_semantic_roles(self) -> None:
        for spec in module.BATCHES:
            overlay = module.expected_overlay(spec, module.DEFAULT_STOCK_ROOT)
            self.assertEqual(
                spec["overlay_path"].read_bytes(), module.COMMON.pretty_bytes(overlay)
            )
            self.assertEqual(len(spec["ids"]), overlay["entry_count"])
            self.assertFalse(
                overlay["distribution_policy"]["contains_commercial_source_text"]
            )
            self.assertFalse(
                overlay["distribution_policy"]["contains_complete_game_resource"]
            )
            self.assertNotIn("source_jp", str(overlay["entries"][0].get("ko", "")))

        self.assertTrue(
            all(" " not in value for value in module.TEXT.J07_MSGDATA_LEGEND_READING_KEYS.values())
        )
        self.assertTrue(
            all(value.count("%s") == 1 for value in module.TEXT.J08_MSGDATA_LEGEND_DESCRIPTIONS.values())
        )
        credit = module.TEXT.J09_MSGSTF_CREDIT_UPDATE[7]
        self.assertIn("PTW Japan Co., Ltd.", credit)
        self.assertIn("SIDE London", credit)
        self.assertIn("<FTB>", credit)
        self.assertIsNone(JP_SCRIPT_RE.search(credit))

    def test_pinned_ab_build_preserves_baselines_and_stock(self) -> None:
        stock_paths = [
            module.DEFAULT_STOCK_ROOT / Path(resource)
            for resource in ("MSG_PK/JP/msgdata.bin", "MSG_PK/JP/msgstf.bin")
        ]
        if not all(path.is_file() for path in stock_paths):
            self.skipTest("pinned pristine Steam 1.1.7 JP resources are unavailable")
        before = [(path.stat().st_size, digest(path)) for path in stock_paths]
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        after = [(path.stat().st_size, digest(path)) for path in stock_paths]
        self.assertEqual("PASS", result["status"])
        self.assertEqual(19, result["delta_applied_count"])
        self.assertEqual(39_526, result["total_common_applied_count"])
        self.assertEqual(77, result["remaining_legacy_unresolved_count"])
        self.assertTrue(result["deterministic_ab_equal"])
        self.assertTrue(all(row["id_domain_preserved"] for row in result["resources"]))
        self.assertTrue(all(row["non_delta_texts_preserved"] for row in result["resources"]))
        self.assertEqual(before, after)

    def test_generated_models_match_tracked_files(self) -> None:
        _candidates, metrics = module.build_candidates(module.DEFAULT_STOCK_ROOT)
        expected = module.validation_model(metrics)
        self.assertEqual(
            module.VALIDATION_PATH.read_bytes(), module.COMMON.pretty_bytes(expected)
        )
        for path in (
            MODULE_PATH,
            HERE / "translations_j06_j09.py",
            module.VALIDATION_PATH,
            *(spec["overlay_path"] for spec in module.BATCHES),
        ):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("/SC/", text, path)
        self.assertEqual([], list(HERE.glob("*.bin")))

    def test_modified_stock_fails_closed(self) -> None:
        resources = ("MSG_PK/JP/msgdata.bin", "MSG_PK/JP/msgstf.bin")
        if not all((module.DEFAULT_STOCK_ROOT / Path(row)).is_file() for row in resources):
            self.skipTest("pinned pristine Steam 1.1.7 JP resources are unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for resource in resources:
                source = module.DEFAULT_STOCK_ROOT / Path(resource)
                target = root / Path(resource)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            target = root / Path(resources[0])
            blob = bytearray(target.read_bytes())
            blob[-1] ^= 1
            target.write_bytes(blob)
            with self.assertRaises(module.COMMON.SteamJpCommonError):
                module.build_candidates(root)


if __name__ == "__main__":
    unittest.main()
