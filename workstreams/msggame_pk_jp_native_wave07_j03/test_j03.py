#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from collections import defaultdict
from pathlib import Path

import build_j03 as builder


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
SOURCE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
ENTRY_FIELDS = {
    "block_id",
    "record_id",
    "literal_id",
    "source_jp_utf16le_sha256",
    "ko",
}
PRISTINE_STOCK_CANDIDATES = (
    Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
        r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
        r"\MSG_PK\JP\msggame.bin"
    ),
    Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"),
)


def load_steam_builder():
    path = (
        REPO_ROOT
        / "workstreams"
        / "steam_jp_msggame_v1"
        / "build_steam_jp_msggame_v1.py"
    )
    spec = importlib.util.spec_from_file_location("steam_jp_msggame_v1_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Steam JP msggame builder import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Wave07J03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private, cls.private_blob = builder.load_private()
        cls.translations, cls.translation_blob = builder.load_translations()
        cls.values = builder.build_values()

    def test_partition_pin_and_translation_coverage_are_exact(self) -> None:
        self.assertEqual(builder.PRIVATE_SHA256, builder.sha256(self.private_blob))
        self.assertEqual(builder.COORDINATE_COUNT, len(self.private))
        self.assertEqual(builder.COORDINATE_COUNT, len(self.translations))
        self.assertEqual(set(self.private), set(self.translations))
        self.assertEqual({6}, {coordinate[0] for coordinate in self.translations})
        ordered = [list(coordinate) for coordinate in self.private]
        self.assertEqual(builder.COORDINATES_SHA256, builder.canonical_hash(ordered))

    def test_all_message_invariants_and_repeated_sources_are_consistent(self) -> None:
        by_source_hash: dict[str, set[str]] = defaultdict(set)
        by_source_coordinate: dict[str, dict[tuple[int, int, int], str]] = defaultdict(dict)
        for coordinate, private_entry in self.private.items():
            source = private_entry["jp"]
            korean = self.translations[coordinate]
            self.assertEqual([], builder.common.invariant_mismatches(source, korean))
            digest = builder.text_hash(source)
            by_source_hash[digest].add(korean)
            by_source_coordinate[digest][coordinate] = korean
        observed = {
            digest: by_source_coordinate[digest]
            for digest, values in by_source_hash.items()
            if len(values) > 1
        }
        reviewed = {
            digest: {
                coordinate: korean
                for coordinate, korean in coordinate_map.items()
                if coordinate in self.private
            }
            for digest, coordinate_map in builder.load_contextual_variants().items()
            if any(coordinate in self.private for coordinate in coordinate_map)
        }
        self.assertEqual(reviewed, observed)

    def test_public_overlay_has_loader_exact_entry_shape(self) -> None:
        overlay = self.values["overlay"][0]
        self.assertEqual(builder.OVERLAY_SCHEMA, overlay["schema"])
        self.assertEqual(builder.RESOURCE, overlay["resource"])
        self.assertEqual("JP", overlay["base_language"])
        self.assertEqual(builder.STOCK_JP, overlay["stock_jp"])
        self.assertEqual(builder.COORDINATE_COUNT, overlay["entry_count"])
        self.assertEqual(builder.COORDINATE_COUNT, len(overlay["entries"]))
        self.assertTrue(all(set(entry) == ENTRY_FIELDS for entry in overlay["entries"]))
        coordinates = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in overlay["entries"]
        }
        self.assertEqual(set(self.private), coordinates)

    def test_review_and_validation_evidence_are_complete(self) -> None:
        review = self.values["review"][0]
        validation = self.values["validation"][0]
        self.assertEqual({"translated": 761}, review["status_counts"])
        self.assertEqual({"PASS": 761}, review["invariant_status_counts"])
        self.assertEqual(
            {"context_reviewed": 761}, review["fragment_grammar_status_counts"]
        )
        self.assertFalse(review["runtime_reviewed"])
        self.assertEqual("PASS", validation["status"])
        self.assertTrue(all(validation["checks"].values()))
        self.assertEqual(761, validation["coordinate_count"])

    def test_generated_artifacts_are_byte_reproducible(self) -> None:
        targets = {
            "overlay": builder.PUBLIC_OVERLAY,
            "review": builder.REVIEW_EVIDENCE,
            "validation": builder.VALIDATION,
        }
        for name, path in targets.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(self.values[name][1], path.read_bytes(), path)

    def test_tracked_payloads_are_source_free(self) -> None:
        payloads = [builder.TRANSLATIONS, builder.PUBLIC_OVERLAY, builder.REVIEW_EVIDENCE, builder.VALIDATION]
        for path in payloads:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(SOURCE_SCRIPT_RE.search(text), path)
            self.assertNotIn('"jp":', text, path)
            self.assertNotIn('"en_record":', text, path)
            self.assertNotIn('"tc_record":', text, path)
        self.assertEqual([], list(ROOT.rglob("*.bin")))

    def test_steam_117_loader_accepts_overlay_when_pristine_stock_exists(self) -> None:
        steam = load_steam_builder()
        stock_blob = None
        for path in PRISTINE_STOCK_CANDIDATES:
            if path.is_file():
                candidate = path.read_bytes()
                if steam.sha256(candidate) == steam.STOCK_PIN["packed_sha256"]:
                    stock_blob = candidate
                    break
        if stock_blob is None:
            self.skipTest("exact Steam 1.1.7 JP stock msggame is unavailable")
        stock = steam.stock_context(stock_blob)
        replacements, evidence = steam.load_overlay(
            builder.PUBLIC_OVERLAY,
            expected_sha256=None,
            expected_entry_count=builder.COORDINATE_COUNT,
            stock=stock,
        )
        self.assertEqual(builder.COORDINATE_COUNT, len(replacements))
        self.assertEqual(builder.COORDINATE_COUNT, evidence["entry_count"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
