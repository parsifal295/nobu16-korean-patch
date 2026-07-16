#!/usr/bin/env python3
"""Regression gates for the three small Steam-JP residual candidates."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

import build_steam_jp_tail_message_tables_v1 as build


class SteamJpTailMessageTablesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.steam_root = build.DEFAULT_STEAM_ROOT

    def test_frozen_contract_and_overlay_validate_for_every_target(self) -> None:
        for spec in build.selected_specs("all"):
            contract, entries, packed, raw, table = build.load_frozen_inputs(spec, self.steam_root)
            self.assertEqual(contract["resource"], spec["resource"])
            self.assertEqual(len(entries), len(spec["ids"]))
            self.assertEqual(len(packed), spec["stock"]["packed_size"])
            self.assertEqual(len(raw), spec["stock"]["raw_size"])
            self.assertEqual(table.string_count, spec["stock"]["string_count"])

    def test_every_candidate_is_deterministic_and_clears_the_global_residual(self) -> None:
        for spec in build.selected_specs("all"):
            _contract, entries, packed, raw, table = build.load_frozen_inputs(spec, self.steam_root)
            first = build.candidate_from_entries(spec, packed, raw, table, entries)
            second = build.candidate_from_entries(spec, packed, raw, table, entries)
            self.assertEqual(first[0], second[0])
            self.assertEqual(first[1], second[1])
            self.assertEqual(first[3], 0)

    def test_catalog_reuse_and_direct_partitions_are_exact(self) -> None:
        for spec in build.selected_specs("all"):
            _contract, entries, _packed, _raw, _table = build.load_frozen_inputs(spec, self.steam_root)
            origins = {entry["id"]: entry["translation_origin"] for entry in entries}
            self.assertEqual(set(origins), set(spec["ids"]))
            self.assertEqual(
                {entry_id for entry_id, origin in origins.items() if origin == "exact_source_hash_catalog_reuse"},
                set(spec["reuse"]),
            )
            self.assertEqual(
                {entry_id for entry_id, origin in origins.items() if origin == "project_direct_translation"},
                set(spec["direct"]),
            )

    def test_public_artifacts_are_source_free(self) -> None:
        for spec in build.selected_specs("all"):
            for path in build.spec_paths(spec):
                build.assert_source_free(path)

    def test_tampered_source_hash_is_rejected(self) -> None:
        spec = build.SPECS["ev"]
        _contract, entries, _packed, _raw, table = build.load_frozen_inputs(spec, self.steam_root)
        tampered = copy.deepcopy(entries)
        tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaises(build.TailMessageTablesError):
            build.validate_entries(spec, table, tampered)

    def test_tampered_credits_linebreak_is_rejected(self) -> None:
        spec = build.SPECS["stf"]
        _contract, entries, _packed, _raw, table = build.load_frozen_inputs(spec, self.steam_root)
        tampered = copy.deepcopy(entries)
        tampered[0]["ko"] = tampered[0]["ko"].rstrip("\n")
        tampered[0]["ko_utf16le_sha256"] = build.text_hash(tampered[0]["ko"])
        with self.assertRaises(build.TailMessageTablesError):
            build.validate_entries(spec, table, tampered)

    def test_complete_output_policy_rejects_non_private_root(self) -> None:
        with self.assertRaises(build.TailMessageTablesError):
            build.require_private_output_root(build.REPO_ROOT)
        allowed = build.require_private_output_root(build.DEFAULT_OUTPUT_BASE / "ev" / "candidate")
        self.assertTrue(allowed.is_relative_to((build.REPO_ROOT / "tmp").resolve()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
