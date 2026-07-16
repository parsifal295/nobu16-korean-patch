#!/usr/bin/env python3
"""Regression tests for the source-free base-event residual wave."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM = TEST_PATH.parent
REPO = TEST_PATH.parents[2]
sys.path.insert(0, str(WORKSTREAM))
MODULE_PATH = WORKSTREAM / "build_base_ev_strdata_jp_residual_wave11.py"
SPEC = importlib.util.spec_from_file_location("base_ev_strdata_jp_residual_wave11", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


EXPECTED_ARTIFACT_SHA256 = {
    builder.OVERLAY_PATH: "5F8207E5D5E0ECDA39D39C8B15EE2F1707E7A68E1FADAF70FBFF5595F552108D",
    builder.HOLD_PATH: "1E5A435C95C730E96D2A56E321B27A8184485954303053EDEC85501E64C2D405",
    builder.VALIDATION_PATH: "640A3582CAE2EDC68F01FACDC8A8219F44142C7F1DE913B832D321C71A29648C",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class BaseEvStrdataJpResidualWave11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock_root = builder.ensure_stock_root(builder.DEFAULT_STOCK_ROOT)
        cls.stock_path = cls.stock_root / Path(builder.RESOURCE)
        cls.before_stock_digest = digest(cls.stock_path)
        cls.base = builder.load_base_builder()
        _packed, _wrapper, _raw, cls.stock = cls.base.load_steam_jp(cls.stock_root)
        _switch_packed, _switch_wrapper, _switch_raw, cls.switch = cls.base.load_switch_v13(
            cls.base.DEFAULT_SWITCH_ZIP
        )
        cls.overlay = builder.read_json(builder.OVERLAY_PATH)
        cls.holds = builder.read_json(builder.HOLD_PATH)
        cls.validation = builder.read_json(builder.VALIDATION_PATH)

    def test_public_artifacts_are_pinned_canonical_and_source_free(self) -> None:
        for path, expected_hash in EXPECTED_ARTIFACT_SHA256.items():
            with self.subTest(path=path.name):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(path.read_bytes(), builder.canonical_json_bytes(builder.read_json(path)))
                self.assertIsNone(builder.SOURCE_SCRIPT_RE.search(path.read_text(encoding="utf-8")))
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_complete_game_resource"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_switch_binary"])

    def test_safe_and_manual_partitions_are_complete_and_disjoint(self) -> None:
        _selected, residual, _count = self.base.select_transfer_entries(self.stock, self.switch)
        residual_ids = {row["id"] for row in residual}
        safe_ids = {row["id"] for row in self.overlay["entries"]}
        hold_ids = {row["id"] for row in self.holds["entries"]}
        self.assertEqual(40, len(safe_ids))
        self.assertEqual(5, len(hold_ids))
        self.assertFalse(safe_ids & hold_ids)
        self.assertEqual(residual_ids, safe_ids | hold_ids)
        self.assertEqual(tuple(sorted(hold_ids)), builder.MANUAL_HOLD_IDS)
        self.assertEqual("관백", self.overlay["policy"]["display_title_7240"])
        self.assertEqual("간레이", self.overlay["policy"]["reading_style"])

    def test_every_safe_target_matches_the_documented_private_transform(self) -> None:
        contracts = {row["id"]: row for row in builder.contract_rows()}
        for row in self.overlay["entries"]:
            entry_id = row["id"]
            with self.subTest(entry_id=entry_id):
                self.assertEqual(contracts[entry_id]["source_jp_utf16le_sha256"], row["source_jp_utf16le_sha256"])
                self.assertEqual(contracts[entry_id]["planned_ko_utf16le_sha256"], row["switch_ko_utf16le_sha256"])
                self.assertEqual(
                    builder.normalise_switch_target(entry_id, self.switch.texts[entry_id]),
                    row["ko"],
                )
                self.assertEqual(builder.text_hash(row["ko"]), row["planned_ko_utf16le_sha256"])
                self.assertFalse(builder.SOURCE_SCRIPT_RE.search(row["ko"]))
                self.assertEqual([], self.base.invariant_mismatches(self.stock.texts[entry_id], row["ko"]))

    def test_candidate_is_deterministic_and_holds_remain_stock(self) -> None:
        first, first_manifest = builder.build_blob(self.stock_root, self.base.DEFAULT_SWITCH_ZIP)
        second, second_manifest = builder.build_blob(self.stock_root, self.base.DEFAULT_SWITCH_ZIP)
        self.assertEqual(first, second)
        self.assertEqual(builder.canonical_json_bytes(first_manifest), builder.canonical_json_bytes(second_manifest))
        self.assertEqual(builder.TARGET_PIN, {
            key: first_manifest["candidate"][key] for key in builder.TARGET_PIN
        })
        _wrapper, raw = self.base.decompress_wrapper(first)
        candidate = self.base.parse_message_table(raw)
        for row in self.overlay["entries"]:
            self.assertEqual(row["ko"], candidate.texts[row["id"]])
        for entry_id in builder.MANUAL_HOLD_IDS:
            self.assertEqual(self.stock.texts[entry_id], candidate.texts[entry_id])

    def test_public_composition_interface_is_explicit_and_pinned(self) -> None:
        self.assertEqual(builder.RESOURCE, "MSG/JP/ev_strdata.bin")
        self.assertEqual(builder.DEFAULT_GAME_ROOT, builder.DEFAULT_STOCK_ROOT)
        self.assertEqual(builder.DEFAULT_SWITCH_ZIP, self.base.DEFAULT_SWITCH_ZIP)
        self.assertEqual(builder.EXPECTED_CANDIDATE, builder.TARGET_PIN)
        candidate, manifest = builder.build_blob()
        self.assertEqual(builder.EXPECTED_CANDIDATE["packed_sha256"], builder.sha256(candidate))
        self.assertEqual(builder.EXPECTED_CANDIDATE, {
            key: manifest["candidate"][key] for key in builder.EXPECTED_CANDIDATE
        })

    def test_tampering_and_live_root_fail_closed(self) -> None:
        bad_overlay = copy.deepcopy(self.overlay)
        bad_overlay["entries"][0]["ko"] += chr(0x65E5)
        with self.assertRaises(builder.WaveError):
            builder.validate_public_models(self.base, self.stock, self.switch, bad_overlay, self.holds)

        bad_holds = copy.deepcopy(self.holds)
        bad_holds["entries"][0]["action"] = "apply"
        with self.assertRaises(builder.WaveError):
            builder.validate_public_models(self.base, self.stock, self.switch, self.overlay, bad_holds)

        with self.assertRaisesRegex(builder.WaveError, "live Steam root"):
            builder.ensure_stock_root(builder.LIVE_STEAM_ROOT)

    def test_verification_is_read_only_for_the_stock_backup(self) -> None:
        result = builder.verify(self.stock_root, self.base.DEFAULT_SWITCH_ZIP)
        self.assertEqual("PASS", result["status"])
        self.assertTrue(result["deterministic_ab_equal"])
        self.assertEqual(self.before_stock_digest, digest(self.stock_path))
        self.assertFalse(result["checks"]["installed_game_file_written"])
        self.assertFalse(result["checks"]["current_v5_candidate_modified"])
        self.assertFalse(result["checks"]["release_asset_written"])


if __name__ == "__main__":
    unittest.main()
