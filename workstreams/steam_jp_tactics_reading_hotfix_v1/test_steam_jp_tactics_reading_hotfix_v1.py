#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_steam_jp_tactics_reading_hotfix_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_tactics_reading_hotfix_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [part for item in value for part in string_values(item)]
    if isinstance(value, dict):
        return [part for item in value.values() for part in string_values(item)]
    return []


class SteamJpTacticsReadingHotfixV1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if cls.stock.is_file():
            cls.before = (cls.stock.stat().st_size, digest(cls.stock))
            cls.context = module.build_clan_normalized_baseline(module.DEFAULT_STOCK_ROOT)
        else:
            cls.before = None
            cls.context = None

    def require_stock(self) -> None:
        if self.before is None:
            self.skipTest("pinned pristine Steam 1.1.7 JP msgdata is unavailable")

    def test_trace_and_overlay_are_source_free_and_target_domain_is_exact(self) -> None:
        self.require_stock()
        assert self.context is not None
        self.assertEqual(
            (15520, 15521, 15522, 15524, 15525, 15526, 15527, 15528, 15529, 15530),
            module.TARGET_IDS,
        )
        self.assertEqual(10, len(module.TARGET_IDS))
        self.assertEqual(
            module.TARGET_IDS_SHA256,
            module.COMMON.canonical_hash(list(module.TARGET_IDS)),
        )
        active = module.active_reading_ids(self.context.table.texts)
        self.assertEqual(62, len(active))
        self.assertEqual(15485, active[0])
        self.assertEqual(15550, active[-1])
        self.assertEqual(module.TACTICS_READING_SLOT_IDS_SHA256, module.COMMON.canonical_hash(list(active)))
        self.assertFalse(set(module.EMPTY_READING_IDS) & set(active))

        trace = module.expected_trace(self.context)
        overlay = module.expected_overlay(self.context)
        self.assertEqual(module.COMMON.pretty_bytes(trace), module.TRACE_PATH.read_bytes())
        self.assertEqual(module.COMMON.pretty_bytes(overlay), module.OVERLAY_PATH.read_bytes())
        self.assertFalse(trace["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(overlay["provenance"]["sc_binary_used"])
        self.assertFalse(overlay["provenance"]["sc_runtime_path_used"])
        for entry in overlay["entries"]:
            self.assertNotIn("source_jp", entry)
            self.assertNotRegex(entry["ko"], module.LATIN_RE)
        for value in string_values(trace):
            self.assertFalse(any("\u3040" <= character <= "\u30ff" or "\u4e00" <= character <= "\u9fff" for character in value))

    def test_jp_trace_and_post_clan_baseline_hash_anchors_fail_closed(self) -> None:
        self.require_stock()
        assert self.context is not None
        active = module.validate_anchor_domain(self.context)
        self.assertEqual(62, len(active))
        self.assertEqual(module.CLAN_NORMALIZED_BASELINE_PIN, module.packed_spec(self.context.packed))
        self.assertEqual(module.CLAN_NORMALIZED_BASELINE_PIN, self.context.clan_metrics["candidate"])
        baseline_latin_ids = tuple(
            entry_id
            for entry_id in active
            if module.LATIN_RE.search(self.context.table.texts[entry_id])
        )
        self.assertEqual(module.TARGET_IDS, baseline_latin_ids)
        for entry_id in module.TARGET_IDS:
            self.assertEqual(
                module.JP_READING_HASH_ANCHORS[entry_id],
                module.COMMON.text_hash(self.context.stock.table.texts[entry_id]),
            )
            self.assertEqual(
                module.BASELINE_KO_HASH_ANCHORS[entry_id],
                module.COMMON.text_hash(self.context.table.texts[entry_id]),
            )
            self.assertEqual(
                module.KOREAN_OUTPUT_HASHES[entry_id],
                module.COMMON.text_hash(module.TARGET_READINGS[entry_id]),
            )

    def test_candidate_eliminates_pinyin_and_preserves_every_non_target(self) -> None:
        self.require_stock()
        candidate, metrics = module.build_blob(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(module.OUTPUT_CANDIDATE_PIN, module.packed_spec(candidate))
        self.assertEqual(10, metrics["tactics_reading_delta_count"])
        self.assertEqual(list(module.TARGET_IDS), metrics["pinyin_latin_slot_ids_eliminated"])
        self.assertTrue(metrics["all_active_tactics_reading_slots_no_latin"])
        self.assertTrue(metrics["non_target_texts_preserved"])
        self.assertTrue(metrics["opaque_non_string_metadata_preserved"])
        self.assertTrue(metrics["wrapper_prefix_preserved"])

        _header, raw = module.COMMON.decompress_wrapper(candidate)
        reparsed = module.COMMON.parse_message_table(raw)
        assert self.context is not None
        self.assertEqual(self.context.table.string_count, reparsed.string_count)
        self.assertTrue(
            module.COMMON._opaque_structure_preserved(self.context.table, reparsed, raw)
        )
        self.assertEqual(self.context.packed[:8], candidate[:8])
        for entry_id in module.TARGET_IDS:
            self.assertEqual(module.TARGET_READINGS[entry_id], reparsed.texts[entry_id])
            self.assertNotRegex(reparsed.texts[entry_id], module.LATIN_RE)
        for entry_id in module.active_reading_ids(reparsed.texts):
            self.assertNotRegex(reparsed.texts[entry_id], module.LATIN_RE)
        for entry_id, baseline_text in enumerate(self.context.table.texts):
            if entry_id not in module.TARGET_IDS:
                self.assertEqual(baseline_text, reparsed.texts[entry_id], entry_id)

    def test_verify_is_read_only_and_matches_validation(self) -> None:
        self.require_stock()
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        self.assertEqual("PASS", result["status"])
        self.assertTrue(result["deterministic_ab_equal"])
        self.assertEqual(self.before, (self.stock.stat().st_size, digest(self.stock)))
        self.assertEqual([], list(HERE.rglob("*.bin")))
        validation, blob = module.COMMON.read_json(module.VALIDATION_PATH)
        self.assertEqual(module.validation_model(result), validation)
        self.assertEqual(module.COMMON.pretty_bytes(validation), blob)

    def test_build_writes_only_an_explicit_tmp_candidate(self) -> None:
        self.require_stock()
        scratch = Path(tempfile.mkdtemp(prefix="tactics-reading-v1-", dir=module.REPO / "tmp"))
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

    def test_modified_pristine_stock_fails_closed(self) -> None:
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

    def test_public_trace_values_are_valid_json_without_raw_jp_text(self) -> None:
        self.require_stock()
        trace = json.loads(module.TRACE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(module.TRACE_SCHEMA, trace["schema"])
        self.assertEqual(list(module.TARGET_IDS), [entry["id"] for entry in trace["entries"]])
        self.assertEqual(
            list(module.TARGET_IDS), trace["tactics_reading_domain"]["pinyin_latin_slot_ids"]
        )


if __name__ == "__main__":
    unittest.main()
