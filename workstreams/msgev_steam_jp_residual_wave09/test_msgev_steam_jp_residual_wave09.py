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
MODULE_PATH = HERE / "build_msgev_steam_jp_residual_wave09.py"
SPEC = importlib.util.spec_from_file_location("msgev_steam_jp_residual_wave09", MODULE_PATH)
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


def has_japanese_source_characters(value: str) -> bool:
    return any(
        "\u3040" <= character <= "\u30ff" or "\u3400" <= character <= "\u9fff"
        for character in value
    )


class MsgEvSteamJpResidualWave09Test(unittest.TestCase):
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
            self.skipTest("pinned pristine Steam 1.1.7 JP msgev is unavailable")

    def test_bounded_scope_is_exact_and_nonoverlapping(self) -> None:
        self.require_stock()
        assert self.context is not None
        self.assertEqual(50, len(module.EVENT_STORY_IDS))
        self.assertEqual(16, len(module.EVENT_LABEL_IDS))
        self.assertEqual(66, len(module.TARGET_IDS))
        self.assertEqual(module.EVENT_STORY_IDS + module.EVENT_LABEL_IDS, module.TARGET_IDS)
        self.assertEqual(tuple(sorted(module.TARGET_IDS)), module.TARGET_IDS)
        self.assertNotIn(10961, module.TARGET_IDS)
        self.assertEqual(
            module.EVENT_STORY_IDS_SHA256,
            module.COMMON.canonical_hash(list(module.EVENT_STORY_IDS)),
        )
        self.assertEqual(
            module.EVENT_LABEL_IDS_SHA256,
            module.COMMON.canonical_hash(list(module.EVENT_LABEL_IDS)),
        )
        self.assertEqual(
            module.TARGET_IDS_SHA256,
            module.COMMON.canonical_hash(list(module.TARGET_IDS)),
        )
        self.assertFalse(set(module.TARGET_IDS) & module.owned_wave08_ids())
        module.validate_target_domain(self.context)

    def test_all_target_sources_are_pristine_residuals_and_preserve_format(self) -> None:
        self.require_stock()
        assert self.context is not None
        for entry_id in module.TARGET_IDS:
            source = self.context.stock.table.texts[entry_id]
            baseline = self.context.table.texts[entry_id]
            replacement = module.TARGET_TRANSLATIONS[entry_id]
            self.assertEqual(source, baseline, entry_id)
            self.assertEqual([], module.COMMON.common.invariant_mismatches(source, replacement), entry_id)
            self.assertEqual(
                module.COMMON.text_hash(source),
                module.trace_entry(self.context, entry_id)["source_jp_utf16le_sha256"],
            )
            self.assertEqual(
                module.COMMON.text_hash(baseline),
                module.trace_entry(self.context, entry_id)["wave08_baseline_utf16le_sha256"],
            )

    def test_public_artifacts_are_source_free_and_match_deterministic_models(self) -> None:
        self.require_stock()
        assert self.context is not None
        trace = module.expected_trace(self.context)
        overlay = module.expected_overlay(self.context)
        self.assertEqual(module.COMMON.pretty_bytes(trace), module.TRACE_PATH.read_bytes())
        self.assertEqual(module.COMMON.pretty_bytes(overlay), module.OVERLAY_PATH.read_bytes())
        self.assertEqual(66, trace["entry_count"])
        self.assertEqual(66, overlay["entry_count"])
        self.assertFalse(trace["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(overlay["provenance"]["sc_binary_used"])
        self.assertFalse(overlay["provenance"]["sc_runtime_path_used"])
        for path in (module.TRACE_PATH, module.OVERLAY_PATH, module.VALIDATION_PATH):
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(any(has_japanese_source_characters(text) for text in string_values(value)))
        self.assertEqual([], list(HERE.rglob("*.bin")))

    def test_candidate_replaces_only_the_66_entries(self) -> None:
        self.require_stock()
        assert self.context is not None
        self.assertIsNotNone(module.OUTPUT_CANDIDATE_PIN)
        candidate, metrics = module.build_blob(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(module.OUTPUT_CANDIDATE_PIN, module.packed_spec(candidate))
        self.assertEqual(66, metrics["residual_delta_count"])
        self.assertEqual(50, metrics["residual_event_story_delta_count"])
        self.assertEqual(16, metrics["residual_event_label_delta_count"])
        self.assertTrue(metrics["format_invariants_preserved"])
        self.assertTrue(metrics["non_target_texts_preserved"])
        self.assertTrue(metrics["opaque_non_string_metadata_preserved"])
        self.assertTrue(metrics["wrapper_prefix_preserved"])
        _header, raw = module.COMMON.decompress_wrapper(candidate)
        reparsed = module.COMMON.parse_message_table(raw)
        self.assertEqual(self.context.table.string_count, reparsed.string_count)
        for entry_id in module.TARGET_IDS:
            self.assertEqual(module.TARGET_TRANSLATIONS[entry_id], reparsed.texts[entry_id])
        for entry_id, baseline in enumerate(self.context.table.texts):
            if entry_id not in module.TARGET_IDS:
                self.assertEqual(baseline, reparsed.texts[entry_id], entry_id)

    def test_verify_is_read_only_and_matches_validation(self) -> None:
        self.require_stock()
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        self.assertEqual("PASS", result["status"])
        self.assertTrue(result["deterministic_ab_equal"])
        self.assertEqual(self.before, (self.stock.stat().st_size, digest(self.stock)))
        validation, validation_blob = module.COMMON.read_json(module.VALIDATION_PATH)
        self.assertEqual(module.validation_model(result), validation)
        self.assertEqual(module.COMMON.pretty_bytes(validation), validation_blob)

    def test_build_writes_only_to_an_explicit_tmp_candidate(self) -> None:
        self.require_stock()
        scratch = Path(tempfile.mkdtemp(prefix="msgev-wave09-", dir=module.REPO / "tmp"))
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


if __name__ == "__main__":
    unittest.main()
