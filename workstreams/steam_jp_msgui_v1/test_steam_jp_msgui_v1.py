#!/usr/bin/env python3
"""Regression tests for the Steam JP-native PK msgui contract."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_steam_jp_msgui_v1 as build  # noqa: E402


class SteamJpMsguiV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock_path = build.DEFAULT_GAME_ROOT / Path(build.RESOURCE)
        if not cls.stock_path.is_file():
            raise unittest.SkipTest(f"pinned Steam JP stock is unavailable: {cls.stock_path}")

    def test_01_frozen_source_free_contract_and_overlay(self) -> None:
        contract_value, _ = build.read_json(build.DEFAULT_CONTRACT)
        contract = build.validate_contract(contract_value, build.DEFAULT_CONTRACT)
        overlay_value, overlay_blob = build.read_json(build.DEFAULT_PUBLIC_OVERLAY)
        entries = build.validate_public_overlay(overlay_value)

        self.assertEqual(len(entries), 3693)
        self.assertEqual(overlay_value["effective_change_count"], 3614)
        self.assertEqual(overlay_value["no_op_count"], 79)
        self.assertEqual(overlay_value["rejected_entry_count"], 344)
        self.assertEqual(build.sha256_bytes(overlay_blob), contract["overlay"]["sha256"])
        self.assertTrue(contract["source_free"])
        self.assertFalse(contract["contains_commercial_source_text"])
        self.assertFalse(contract["contains_complete_game_resource"])
        self.assertEqual(contract["runtime_route"]["language"], "JP")
        self.assertFalse(contract["runtime_route"]["sc_container_used"])
        self.assertFalse(contract["runtime_route"]["legacy_candidate_binary_used"])

    def test_02_remap_is_byte_reproducible(self) -> None:
        _path, _packed, _raw, table = build.load_stock(build.DEFAULT_GAME_ROOT)
        source_entries, source_blob = build.load_source_overlay(build.DEFAULT_SOURCE_OVERLAY)
        accepted, rejected = build.remap_entries(source_entries, table)
        overlay = build.make_public_overlay(accepted, len(rejected), source_blob, table)
        audit = build.make_audit(accepted, rejected, source_blob)

        self.assertEqual(build.pretty_bytes(overlay), build.DEFAULT_PUBLIC_OVERLAY.read_bytes())
        self.assertEqual(build.pretty_bytes(audit), build.DEFAULT_AUDIT.read_bytes())
        self.assertEqual(len(accepted), 3693)
        self.assertEqual(len(rejected), 344)

    def test_03_candidate_build_is_reproducible_and_private(self) -> None:
        tmp_root = REPO_ROOT / "tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        stock_before = self.stock_path.read_bytes()
        with tempfile.TemporaryDirectory(prefix="steam_jp_msgui_test_a_", dir=tmp_root) as a_name:
            with tempfile.TemporaryDirectory(prefix="steam_jp_msgui_test_b_", dir=tmp_root) as b_name:
                first = build.build_candidate(
                    build.DEFAULT_GAME_ROOT, build.DEFAULT_CONTRACT, Path(a_name)
                )
                second = build.build_candidate(
                    build.DEFAULT_GAME_ROOT, build.DEFAULT_CONTRACT, Path(b_name)
                )
                first_blob = Path(first["candidate_path"]).read_bytes()
                second_blob = Path(second["candidate_path"]).read_bytes()
                self.assertEqual(first_blob, second_blob)
                self.assertEqual(
                    hashlib.sha256(first_blob).hexdigest().upper(),
                    "3D790A1F28199265260B6C1529956D686480C7181A1EA65097E0C6F624005DFF",
                )
                self.assertEqual(first["mapped_entry_count"], 3693)
                self.assertEqual(first["effective_change_count"], 3614)
                self.assertEqual(first["unmapped_entry_count"], 344)
                self.assertFalse(first["installed_game_file_modified"])
        self.assertEqual(self.stock_path.read_bytes(), stock_before)

    def test_04_output_outside_repo_tmp_is_rejected(self) -> None:
        with self.assertRaises(build.SteamJpMsguiError):
            build.require_private_output_root(WORKSTREAM_ROOT / "candidate")

    def test_05_per_entry_jp_hash_tamper_is_rejected(self) -> None:
        _contract, entries, _blob = build.load_frozen_inputs(build.DEFAULT_CONTRACT)
        _path, packed, raw, table = build.load_stock(build.DEFAULT_GAME_ROOT)
        tampered = copy.deepcopy(entries)
        tampered[0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaisesRegex(build.SteamJpMsguiError, "JP source hash mismatch"):
            build.candidate_from_entries(packed, raw, table, tampered)

    def test_06_format_profile_tamper_is_rejected(self) -> None:
        _contract, entries, _blob = build.load_frozen_inputs(build.DEFAULT_CONTRACT)
        _path, packed, raw, table = build.load_stock(build.DEFAULT_GAME_ROOT)
        tampered = copy.deepcopy(entries)
        tampered[0]["ko"] += "\n"
        with self.assertRaisesRegex(build.SteamJpMsguiError, "format profile mismatch"):
            build.candidate_from_entries(packed, raw, table, tampered)

    def test_07_public_artifacts_have_no_jp_source_text_or_sc_paths(self) -> None:
        for path in (
            build.DEFAULT_PUBLIC_OVERLAY,
            build.DEFAULT_AUDIT,
            build.DEFAULT_CONTRACT,
        ):
            text = path.read_text(encoding="utf-8")
            self.assertFalse(build.has_cjk_or_kana(text), path)
            self.assertNotIn("MSG_PK/SC", text, path)
            self.assertNotIn("RES_SC", text, path)
            self.assertNotIn("source_sc", text.casefold(), path)

    def test_08_candidate_is_neither_stock_nor_legacy_mirror(self) -> None:
        contract, _ = build.read_json(build.DEFAULT_CONTRACT)
        candidate_hash = contract["expected_candidate"]["packed_sha256"]
        self.assertNotEqual(candidate_hash, build.STOCK_PACKED_SHA256)
        self.assertNotEqual(
            candidate_hash,
            "C683AE9355A43F9A2104E49A6179363727CE0A550682F906C224A44F506826AC",
        )

    def test_09_audit_exhaustively_partitions_source_overlay(self) -> None:
        audit, _ = build.read_json(build.DEFAULT_AUDIT)
        result = audit["result"]
        self.assertEqual(result["input_entry_count"], 4037)
        self.assertEqual(result["mapped_entry_count"], 3693)
        self.assertEqual(result["unmapped_entry_count"], 344)
        self.assertEqual(3693 + 344, 4037)
        self.assertEqual(len(result["unmapped_entries"]), 344)
        self.assertEqual(
            result["reason_counts"],
            {
                "esc": 22,
                "leading_whitespace": 1,
                "line_breaks": 156,
                "printf": 252,
                "pua": 20,
                "trailing_whitespace": 3,
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
