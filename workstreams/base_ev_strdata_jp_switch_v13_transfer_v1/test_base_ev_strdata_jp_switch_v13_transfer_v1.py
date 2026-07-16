#!/usr/bin/env python3
"""Regression tests for the isolated base-JP event-text transfer overlay."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM = TEST_PATH.parent
REPO = TEST_PATH.parents[2]
MODULE_PATH = WORKSTREAM / "build_base_ev_strdata_jp_switch_v13_transfer_v1.py"
SPEC = importlib.util.spec_from_file_location("base_ev_strdata_jp_switch_v13_transfer_v1", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


EXPECTED_ARTIFACT_SHA256 = {
    builder.OVERLAY_PATH: "1A79E514616C284C140FB8A6618BA48AD648BA88EBE4D81F618B4C551C038B2A",
    builder.RESIDUAL_PATH: "56437884F38B30E3AB9E0E7E30FFCB639EF819FAA7A2CD2FD0CFF4674DCD83E5",
    builder.VALIDATION_PATH: "516BCF7C52A3152E4B5BE819D4B92218B6CD564B159125B5077407E46BFB0B0B",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class BaseEvStrdataJpSwitchV13TransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock_path = builder.STEAM_ROOT / Path(builder.RESOURCE)
        cls.before_stock_digest = digest(cls.stock_path)
        cls.stock, cls.wrapper, cls.raw, cls.steam = builder.load_steam_jp(builder.STEAM_ROOT)
        _packed, _wrapper, _raw, cls.switch = builder.load_switch_v13(builder.SWITCH_ZIP)
        cls.overlay = builder.read_json(builder.OVERLAY_PATH)
        cls.residual = builder.read_json(builder.RESIDUAL_PATH)
        cls.validation = builder.read_json(builder.VALIDATION_PATH)

    def test_public_artifacts_are_pinned_and_source_script_free(self) -> None:
        for path, expected_hash in EXPECTED_ARTIFACT_SHA256.items():
            with self.subTest(path=path.name):
                self.assertEqual(expected_hash, digest(path))
                self.assertIsNone(builder.SOURCE_SCRIPT_RE.search(path.read_text(encoding="utf-8")))
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_complete_game_resource"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_switch_binary"])

    def test_partition_is_complete_disjoint_and_matches_the_pinned_vectors(self) -> None:
        selected, residual, hangul_candidates = builder.select_transfer_entries(self.steam, self.switch)
        self.assertEqual(builder.EXPECTED_SWITCH_HANGUL_CANDIDATES, hangul_candidates)
        self.assertEqual(builder.EXPECTED_SELECTED_COUNT, len(selected))
        self.assertEqual(builder.EXPECTED_RESIDUAL_COUNT, len(residual))
        self.assertEqual(self.overlay["entries"], selected)
        self.assertEqual(self.residual["entries"], residual)
        selected_ids = {row["id"] for row in selected}
        residual_ids = {row["id"] for row in residual}
        self.assertFalse(selected_ids & residual_ids)
        self.assertEqual(
            builder.EXPECTED_SELECTED_IDS_SHA256,
            builder.ids_sha256(row["id"] for row in selected),
        )
        self.assertEqual(
            builder.EXPECTED_RESIDUAL_IDS_SHA256,
            builder.ids_sha256(row["id"] for row in residual),
        )

    def test_candidate_is_deterministic_and_preserves_every_unselected_slot(self) -> None:
        first, manifest = builder._build_blob_from_overlay(
            self.stock, self.wrapper, self.raw, self.steam, self.overlay, self.residual
        )
        second, second_manifest = builder._build_blob_from_overlay(
            self.stock, self.wrapper, self.raw, self.steam, self.overlay, self.residual
        )
        self.assertEqual(first, second)
        self.assertEqual(builder.json_bytes(manifest), builder.json_bytes(second_manifest))
        self.assertEqual(builder.TARGET_PIN["packed_sha256"], builder.sha256(first))
        self.assertEqual(builder.TARGET_PIN["packed_size"], len(first))
        _candidate_wrapper, candidate_raw = builder.decompress_wrapper(first)
        candidate = builder.parse_message_table(candidate_raw)
        replacements = builder.validate_public_artifacts(self.overlay, self.residual, self.steam)
        self.assertEqual(builder.TARGET_PIN["string_count"], candidate.string_count)
        self.assertEqual(builder.EXPECTED_SELECTED_COUNT, len(replacements))
        for entry_id, source in enumerate(self.steam.texts):
            with self.subTest(entry_id=entry_id):
                self.assertEqual(replacements.get(entry_id, source), candidate.texts[entry_id])

    def test_tampering_fails_closed(self) -> None:
        bad_hash = copy.deepcopy(self.overlay)
        bad_hash["entries"][0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaisesRegex(builder.TransferError, "source hash"):
            builder._build_blob_from_overlay(
                self.stock, self.wrapper, self.raw, self.steam, bad_hash, self.residual
            )

        bad_script = copy.deepcopy(self.overlay)
        bad_script["entries"][0]["ko"] += chr(0x65E5)
        with self.assertRaisesRegex(builder.TransferError, "source-script"):
            builder.validate_public_artifacts(bad_script, self.residual, self.steam)

        bad_layout = copy.deepcopy(self.overlay)
        bad_layout["entries"][0]["ko"] += "\n"
        with self.assertRaisesRegex(builder.TransferError, "invariant mismatch"):
            builder.validate_public_artifacts(bad_layout, self.residual, self.steam)

    def test_public_candidate_loader_interface_and_ab_verification(self) -> None:
        self.assertIs(builder.DEFAULT_GAME_ROOT, builder.STEAM_ROOT)
        self.assertIsInstance(builder.DEFAULT_SWITCH_ZIP, Path)
        self.assertEqual(builder.TARGET_PIN, builder.EXPECTED_CANDIDATE)
        first, metrics = builder.build_blob(
            builder.DEFAULT_GAME_ROOT, builder.DEFAULT_SWITCH_ZIP
        )
        second, second_metrics = builder.build_blob(
            builder.DEFAULT_GAME_ROOT, builder.DEFAULT_SWITCH_ZIP
        )
        self.assertEqual(first, second)
        self.assertEqual(builder.json_bytes(metrics), builder.json_bytes(second_metrics))
        self.assertEqual(builder.EXPECTED_CANDIDATE["packed_sha256"], builder.sha256(first))
        self.assertEqual(builder.RESOURCE, metrics["resource"])
        self.assertEqual(builder.EXPECTED_CANDIDATE, {
            key: metrics["candidate"][key] for key in builder.EXPECTED_CANDIDATE
        })
        verified = builder.verify(builder.DEFAULT_GAME_ROOT, builder.DEFAULT_SWITCH_ZIP)
        self.assertEqual("PASS", verified["status"])
        self.assertTrue(verified["deterministic_ab_equal"])

    def test_no_installed_game_file_write_occurred(self) -> None:
        self.assertEqual(self.before_stock_digest, digest(self.stock_path))
        self.assertFalse(self.validation["checks"]["installed_game_file_written"])
        self.assertFalse(self.validation["checks"]["sc_container_used"])
        self.assertEqual(builder.TARGET_PIN | {"changed_entry_count": 13_045}, self.validation["candidate"])


if __name__ == "__main__":
    unittest.main()
