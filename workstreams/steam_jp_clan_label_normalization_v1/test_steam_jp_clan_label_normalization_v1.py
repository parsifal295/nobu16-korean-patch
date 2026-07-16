#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_steam_jp_clan_label_normalization_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_clan_label_normalization_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class SteamJpClanLabelNormalizationV1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if cls.stock.is_file():
            cls.before = (cls.stock.stat().st_size, digest(cls.stock))
            cls.context = module.build_wave08_baseline(module.DEFAULT_STOCK_ROOT)
        else:
            cls.before = None
            cls.context = None

    def require_stock(self) -> None:
        if self.before is None:
            self.skipTest("pinned pristine Steam 1.1.7 JP msgdata is unavailable")

    def test_selection_is_exact_and_public_overlay_is_source_free(self) -> None:
        self.require_stock()
        assert self.context is not None
        selected = module.selected_ids(self.context.table.texts)
        self.assertEqual(159, len(selected))
        self.assertEqual(module.NORMALIZED_IDS_SHA256, module.COMMON.canonical_hash(selected))
        self.assertEqual(14519, selected[0])
        self.assertEqual(14763, selected[-1])
        overlay = module.expected_overlay(module.DEFAULT_STOCK_ROOT, self.context)
        self.assertEqual(159, overlay["entry_count"])
        self.assertEqual(module.NORMALIZED_IDS_SHA256, overlay["normalization"]["selected_ids_sha256"])
        self.assertFalse(overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(overlay["distribution_policy"]["contains_complete_game_resource"])
        self.assertFalse(overlay["provenance"]["sc_binary_used"])
        self.assertFalse(overlay["provenance"]["sc_runtime_path_used"])
        self.assertEqual(module.COMMON.pretty_bytes(overlay), module.OVERLAY_PATH.read_bytes())
        for entry in overlay["entries"]:
            self.assertNotIn("source_jp", entry)
            self.assertTrue(entry["ko"].endswith(" 가문"))

    def test_wave08_baseline_and_anchors_are_pinned(self) -> None:
        self.require_stock()
        assert self.context is not None
        self.assertEqual(module.WAVE08_MSGDATA_BASELINE_PIN, module.packed_spec(self.context.packed))
        self.assertEqual("오다 가문", self.context.table.texts[14542])
        self.assertEqual("아라키가", self.context.table.texts[14692])
        selected = module.selected_ids(self.context.table.texts)
        self.assertNotIn(14542, selected)
        self.assertNotIn(14603, selected)
        self.assertFalse(set(selected) & set(range(14767, 14777)))
        self.assertFalse(set(selected) & set(range(14777, 15035)))

    def test_candidate_is_deterministic_and_preserves_non_targets(self) -> None:
        self.require_stock()
        candidate, metrics = module.build_blob(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(module.OUTPUT_CANDIDATE_PIN, module.packed_spec(candidate))
        self.assertEqual(159, metrics["normalization_delta_count"])
        self.assertEqual("오다 가문", metrics["anchors"]["14542"])
        self.assertEqual("아라키 가문", metrics["anchors"]["14692"])
        _header, raw = module.COMMON.decompress_wrapper(candidate)
        texts = module.COMMON.parse_message_table(raw).texts
        assert self.context is not None
        self.assertEqual("오다 가문", texts[14542])
        self.assertEqual("아라키 가문", texts[14692])
        for entry_id in (14603, *range(14767, 14777), *range(14777, 15035)):
            self.assertEqual(self.context.table.texts[entry_id], texts[entry_id])
        self.assertTrue(metrics["preservation"]["non_delta_texts_preserved"])
        self.assertTrue(metrics["wrapper_prefix_preserved"])

    def test_verify_is_read_only_and_matches_validation(self) -> None:
        self.require_stock()
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        self.assertEqual("PASS", result["status"])
        self.assertTrue(result["deterministic_ab_equal"])
        self.assertEqual(self.before, (self.stock.stat().st_size, digest(self.stock)))
        self.assertEqual([], list(HERE.glob("*.bin")))
        validation, blob = module.COMMON.read_json(module.VALIDATION_PATH)
        self.assertEqual(module.validation_model(result), validation)
        self.assertEqual(module.COMMON.pretty_bytes(validation), blob)

    def test_build_writes_only_an_explicit_tmp_candidate(self) -> None:
        self.require_stock()
        scratch = Path(tempfile.mkdtemp(prefix="clan-label-v1-", dir=module.REPO / "tmp"))
        target_root = scratch / "candidate"
        try:
            destination = module.build(module.DEFAULT_STOCK_ROOT, target_root)
            self.assertEqual(target_root.resolve(), destination)
            candidate = destination / Path(module.RESOURCE)
            self.assertTrue(candidate.is_file())
            self.assertEqual(module.OUTPUT_CANDIDATE_PIN, module.packed_spec(candidate.read_bytes()))
            self.assertTrue((destination / "private_manifest.json").is_file())
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_modified_stock_fails_closed(self) -> None:
        self.require_stock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / Path(module.RESOURCE)
            target.parent.mkdir(parents=True)
            shutil.copyfile(self.stock, target)
            blob = bytearray(target.read_bytes())
            blob[-1] ^= 1
            target.write_bytes(blob)
            with self.assertRaises(module.COMMON.SteamJpCommonError):
                module.build_blob(root)


if __name__ == "__main__":
    unittest.main()
