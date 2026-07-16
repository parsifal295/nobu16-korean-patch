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
MODULE_PATH = HERE / "build_wave08_integration.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_common_wave08_integration", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Wave08IntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock_paths = [
            module.DEFAULT_STOCK_ROOT / "MSG_PK" / "JP" / name for name in module.COMMON.FILES
        ]
        if all(path.is_file() for path in cls.stock_paths):
            cls.before = [(path.stat().st_size, digest(path)) for path in cls.stock_paths]
            cls.candidates, cls.metrics = module.build_all(module.DEFAULT_STOCK_ROOT)
        else:
            cls.before = []
            cls.candidates = {}
            cls.metrics = {}

    def require_stock(self) -> None:
        if not self.before:
            self.skipTest("pinned pristine Steam 1.1.7 JP resources are unavailable")

    def test_semantic_batches_are_exact_disjoint_and_source_free(self) -> None:
        by_resource, artifacts = module.load_semantic_overlays()
        self.assertEqual(9, len(artifacts))
        self.assertEqual(94, sum(len(rows) for rows in by_resource.values()))
        self.assertEqual(
            {"MSG_PK/JP/msgev.bin": 69, "MSG_PK/JP/msgdata.bin": 24, "MSG_PK/JP/msgstf.bin": 1},
            {resource: len(rows) for resource, rows in by_resource.items()},
        )
        coordinates = [
            (resource, int(entry["id"]))
            for resource, entries in by_resource.items()
            for entry in entries
        ]
        self.assertEqual(len(coordinates), len(set(coordinates)))
        for spec in module.BATCHES:
            overlay, _blob = module.COMMON.read_json(spec["path"])
            self.assertFalse(overlay["distribution_policy"]["contains_commercial_source_text"])
            self.assertFalse(overlay["distribution_policy"]["contains_complete_game_resource"])
            self.assertNotIn("source_jp", overlay)

    def test_source_equal_catalog_and_internal_dummies_are_excluded(self) -> None:
        summary = module._validate_excluded_catalogs()
        self.assertEqual(1_796, summary["entry_count"])
        self.assertEqual(0, summary["runtime_translation_added_count"])
        _triage, hold, _blob = module._load_triage()
        self.assertEqual([15_420, 16_219], hold["current_ids"])
        semantic, _artifacts = module.load_semantic_overlays()
        semantic_msgev_ids = {int(entry["id"]) for entry in semantic["MSG_PK/JP/msgev.bin"]}
        self.assertFalse(semantic_msgev_ids & set(hold["current_ids"]))

    def test_integrated_candidate_accounting_and_structure(self) -> None:
        self.require_stock()
        self.assertEqual(set(module.COMMON.FILES), set(self.candidates))
        self.assertEqual(40_581, self.metrics["applied_entries"])
        self.assertEqual(94, self.metrics["wave08_semantic_delta_entries"])
        self.assertEqual(980, self.metrics["surname_recovery_delta_entries"])
        self.assertEqual(0, self.metrics["wave08_reviewed_semantic_gap_remaining"])
        self.assertEqual(792, self.metrics["review_backlog_entries"])
        self.assertEqual(730, self.metrics["format_contract_blocked_entries"])
        self.assertEqual(62, self.metrics["alignment_gap_entries"])
        self.assertEqual(43_169, self.metrics["source_union_effective_coordinate_entries"])
        self.assertEqual(2, self.metrics["retained_internal_dummy_entries"])
        self.assertEqual(1_796, self.metrics["excluded_source_equal_contract_entries"])
        self.assertTrue(self.metrics["deterministic_ab_equal"])
        semantic_deltas = {
            Path(row["resource"]).name: row["wave08_semantic_delta_count"]
            for row in self.metrics["resources"]
        }
        self.assertEqual(module.EXPECTED_SEMANTIC_DELTAS, semantic_deltas)
        total_deltas = {
            Path(row["resource"]).name: (
                row["wave08_semantic_delta_count"] + row["surname_recovery_delta_count"]
            )
            for row in self.metrics["resources"]
        }
        self.assertEqual(module.EXPECTED_RESOURCE_DELTAS, total_deltas)
        for row in self.metrics["resources"]:
            self.assertEqual(
                row["source_union_effective_coordinate_count"],
                row["applied_count"]
                + row["excluded_source_equal_contract_count"]
                + row["format_contract_blocked_count"]
                + row["alignment_gap_count"],
            )
            self.assertTrue(row["id_domain_preserved"])
            self.assertTrue(row["string_count_preserved"])
            self.assertTrue(row["opaque_non_string_metadata_preserved"])
            self.assertTrue(row["non_delta_texts_preserved"])
            self.assertTrue(row["wrapper_prefix_preserved"])

    def test_surname_recovery_recomposes_oda_nobunaga(self) -> None:
        self.require_stock()
        overlay, _blob = module.SURNAMES.load_overlay(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(980, overlay["entry_count"])
        self.assertFalse(overlay["distribution_policy"]["contains_commercial_source_text"])
        _header, raw = module.COMMON.decompress_wrapper(self.candidates["msgdata.bin"])
        texts = module.COMMON.parse_message_table(raw).texts
        self.assertEqual("오다 ", texts[84])
        self.assertEqual("노부나가", texts[1_266])
        self.assertEqual("오다 노부나가", texts[84] + texts[1_266])

    def test_validation_model_and_individual_builders_verify(self) -> None:
        self.require_stock()
        validation, blob = module.COMMON.read_json(module.VALIDATION_PATH)
        expected = module.validation_model(self.metrics)
        self.assertEqual(expected, validation)
        self.assertEqual(module.COMMON.pretty_bytes(expected), blob)
        individual = module.verify_individual_builders(module.DEFAULT_STOCK_ROOT)
        self.assertEqual([5, 2, 31, 31, 6, 19], [row["delta_applied_count"] for row in individual])
        exact = module.verify_excluded_exact_contracts(module.DEFAULT_STOCK_ROOT)
        self.assertTrue(exact["candidate_bytes_unchanged"])
        self.assertEqual(0, exact["runtime_translation_added_count"])

    def test_build_is_read_only_and_tracks_no_complete_binary(self) -> None:
        self.require_stock()
        after = [(path.stat().st_size, digest(path)) for path in self.stock_paths]
        self.assertEqual(self.before, after)
        self.assertEqual([], list(HERE.glob("*.bin")))
        self.assertFalse(self.metrics["installed_game_files_modified"])
        self.assertFalse(self.metrics["candidate_binaries_tracked"])

    def test_modified_stock_fails_closed(self) -> None:
        self.require_stock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in self.stock_paths:
                target = root / "MSG_PK" / "JP" / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            target = root / "MSG_PK" / "JP" / "msgev.bin"
            blob = bytearray(target.read_bytes())
            blob[-1] ^= 1
            target.write_bytes(blob)
            with self.assertRaises(module.COMMON.SteamJpCommonError):
                module.build_all(root)


if __name__ == "__main__":
    unittest.main()
