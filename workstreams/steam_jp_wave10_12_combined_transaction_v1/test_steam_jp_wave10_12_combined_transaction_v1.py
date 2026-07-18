#!/usr/bin/env python3
"""Regression tests for the private Steam Wave 10--12 text transaction."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_steam_jp_wave10_12_combined_transaction_v1.py"
WRITER_PATH = WORKSTREAM / "invoke_steam_jp_wave10_12_combined_transaction_v1.ps1"


def load_builder():
    spec = importlib.util.spec_from_file_location("steam_w10_12_test_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Wave10To12CombinedTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.input_files = cls.builder.validate_wave9_profile(cls.builder.WAVE9_INPUT_ROOT)
        cls.bundle = cls.builder.prepare_candidate(cls.builder.WAVE9_INPUT_ROOT)
        cls.wave10, cls.wave11, cls.wave12 = cls.builder.load_components()

    def test_full_wave9_profile_is_the_only_input_and_full_target_is_pinned(self) -> None:
        self.assertEqual(tuple(self.input_files), self.builder.PROFILE_PATHS)
        self.assertEqual(self.bundle.input_sha256, self.builder.INPUT_SHA256)
        self.assertEqual(self.bundle.output_sha256, self.builder.TARGET_SHA256)
        self.assertEqual(len(self.bundle.files), 11)
        self.assertEqual(
            self.bundle.output_sha256["MSG/JP/msggame.bin"],
            "C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347",
        )
        self.assertEqual(
            self.bundle.output_sha256["MSG_PK/JP/msggame.bin"],
            "6557733B50CBA6435FB51EC71472FF4B06A321AF92F825EAA3C531DE7722E0A6",
        )
        self.assertEqual(len(self.bundle.files["MSG/JP/msggame.bin"]), 1_504_643)
        self.assertEqual(len(self.bundle.files["MSG_PK/JP/msggame.bin"]), 1_806_851)

    def test_only_the_two_declared_paths_change(self) -> None:
        self.assertEqual(
            self.builder.CHANGED_PATHS,
            ("MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin"),
        )
        for relative in self.builder.PROFILE_PATHS:
            if relative in self.builder.CHANGED_PATHS:
                self.assertNotEqual(self.bundle.files[relative], self.input_files[relative])
            else:
                self.assertEqual(self.bundle.files[relative], self.input_files[relative])

    def test_pk_component_coordinates_are_disjoint_and_all_21_records_change(self) -> None:
        wave10_coordinates = {(6, record_id) for record_id in self.wave10.PK_RECORD_IDS}
        wave11_coordinates = {change.record_coordinate for change in self.wave11.CHANGES}
        wave12_coordinates = {self.wave12.COORDINATE}
        self.builder.assert_disjoint_coordinate_sets(
            wave10_coordinates, wave11_coordinates, wave12_coordinates
        )
        self.assertFalse(wave10_coordinates & wave11_coordinates)
        self.assertFalse(wave10_coordinates & wave12_coordinates)
        self.assertFalse(wave11_coordinates & wave12_coordinates)
        expected = wave10_coordinates | wave11_coordinates | wave12_coordinates
        actual = self.builder.changed_coordinates(
            self.input_files["MSG_PK/JP/msggame.bin"],
            self.bundle.files["MSG_PK/JP/msggame.bin"],
            self.wave10.records_by_coordinate,
        )
        self.assertEqual(len(expected), 21)
        self.assertEqual(actual, expected)

    def test_overlap_guard_rejects_any_pk_record_overlap(self) -> None:
        with self.assertRaises(self.builder.TransactionError):
            self.builder.assert_disjoint_coordinate_sets({(1, 1)}, {(1, 1)}, set())

    def test_each_component_record_contract_survives_the_union_rebuild(self) -> None:
        pk_records = self.wave10.records_by_coordinate(
            self.bundle.files["MSG_PK/JP/msggame.bin"]
        )
        for record_id in self.wave10.PK_RECORD_IDS:
            self.assertEqual(
                self.wave10.sha256_bytes(pk_records[(6, record_id)].data),
                self.wave10.TARGET_RECORD_SHA256,
            )
        for change in self.wave11.CHANGES:
            self.assertEqual(
                self.wave11.sha256_bytes(pk_records[change.record_coordinate].data),
                change.output_record_sha256,
            )
        self.assertEqual(
            self.wave12.sha256_bytes(pk_records[self.wave12.COORDINATE].data),
            self.wave12.TARGET_RECORD_SHA256,
        )
        base_records = self.wave12.records_by_coordinate(
            self.bundle.files["MSG/JP/msggame.bin"]
        )
        self.assertEqual(
            self.wave12.sha256_bytes(base_records[self.wave12.COORDINATE].data),
            self.wave12.TARGET_RECORD_SHA256,
        )

    def test_manifest_contract_is_full_profile_and_two_path_writer_scope(self) -> None:
        manifest = self.builder.build_manifest(self.bundle, "A" * 64)
        self.assertEqual(manifest["schema"], self.builder.SCHEMA)
        self.assertEqual(manifest["transaction_id"], self.builder.TRANSACTION_ID)
        self.assertEqual(manifest["profile_paths"], list(self.builder.PROFILE_PATHS))
        self.assertEqual(manifest["changed_paths"], list(self.builder.CHANGED_PATHS))
        self.assertEqual(manifest["input_sha256"], self.builder.INPUT_SHA256)
        self.assertEqual(manifest["output_sha256"], self.builder.TARGET_SHA256)
        self.assertEqual(manifest["pinned_output_sha256"], self.builder.TARGET_SHA256)
        self.assertEqual(manifest["component_contract"]["pk_record_overlap"], 0)
        self.assertEqual(manifest["component_contract"]["wave10_pk_records"], 12)
        self.assertEqual(manifest["component_contract"]["wave11_pk_records"], 8)
        self.assertEqual(manifest["component_contract"]["wave12_pk_records"], 1)

    def test_private_candidate_writer_outputs_full_profile_and_json_contracts(self) -> None:
        self.builder.TMP_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="test_", dir=self.builder.TMP_ROOT) as directory:
            root = Path(directory)
            candidate_root = root / "candidate"
            audit_path = root / "audit.json"
            manifest_path = root / "manifest.json"
            self.builder.write_candidate(self.bundle, candidate_root)
            audit_hash = self.builder.write_json(audit_path, self.bundle.audit)
            manifest_hash = self.builder.write_json(
                manifest_path, self.builder.build_manifest(self.bundle, audit_hash)
            )
            self.assertEqual(len(audit_hash), 64)
            self.assertEqual(len(manifest_hash), 64)
            self.assertEqual(
                self.builder.validate_wave9_profile(self.builder.WAVE9_INPUT_ROOT),
                self.input_files,
            )
            self.assertEqual(
                {
                    relative: self.builder.sha256_path(candidate_root / Path(relative))
                    for relative in self.builder.PROFILE_PATHS
                },
                self.builder.TARGET_SHA256,
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["changed_paths"], list(self.builder.CHANGED_PATHS))

    def test_writer_retains_transaction_safety_and_has_no_extra_write_paths(self) -> None:
        text = WRITER_PATH.read_text(encoding="utf-8")
        for required in (
            "Assert-Game-Stopped",
            "Replace-Atomically",
            "Write-State",
            "Restore-Written",
            "post-apply full profile mismatch",
            "post-restore full profile mismatch",
            "apply_dry_run",
            "restore_dry_run",
            "rolled_back_after_failure",
            "rollback_failed",
            "File]::Replace",
        ):
            self.assertIn(required, text)
        self.assertIn("'MSG/JP/msggame.bin'", text)
        self.assertIn("'MSG_PK/JP/msggame.bin'", text)
        self.assertNotIn("'MSG/JP/ev_strdata.bin',\n    'MSG_PK/JP", text)
        self.assertNotIn("'RES_JP/", text)
        self.assertNotIn("'HUD/", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
