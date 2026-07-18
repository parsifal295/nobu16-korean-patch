#!/usr/bin/env python3
"""Deterministic checks for the private Wave9 combined transaction."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_steam_jp_wave9_combined_transaction_v1.py")
WRITER_PATH = SCRIPT.with_name("invoke_steam_jp_wave9_combined_transaction_v1.ps1")


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "steam_jp_wave9_combined_transaction", BUILDER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load combined builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE9 = load_builder()


class CombinedWave9TransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = WAVE9.construct_payload()
        cls.profile = {
            relative: WAVE9.sha256_bytes(value)
            for relative, value in cls.payload.files.items()
        }

    def test_full_profile_is_pinned_and_changes_only_three_paths(self) -> None:
        self.assertEqual(tuple(self.payload.files), WAVE9.PROFILE_PATHS)
        self.assertEqual(self.profile, WAVE9.TARGET_SHA256)
        changed = {
            relative
            for relative in WAVE9.PROFILE_PATHS
            if self.profile[relative] != WAVE9.INPUT_SHA256[relative]
        }
        self.assertEqual(changed, set(WAVE9.CHANGED_PATHS))

    def test_component_contracts_start_from_wave8_and_compose_target(self) -> None:
        runtime = self.payload.component_contract["runtime"]
        event = self.payload.component_contract["event"]
        self.assertEqual(runtime["input_profile_sha256"], WAVE9.INPUT_SHA256)
        self.assertEqual(
            runtime["output_profile_sha256"], WAVE9.RUNTIME_COMPONENT_OUTPUT_SHA256
        )
        self.assertEqual(
            event["input_sha256"],
            {
                "MSG/JP/ev_strdata.bin": WAVE9.INPUT_SHA256[
                    "MSG/JP/ev_strdata.bin"
                ],
                "MSG_PK/JP/msgev.bin": WAVE9.INPUT_SHA256["MSG_PK/JP/msgev.bin"],
            },
        )
        self.assertEqual(event["output_sha256"], WAVE9.EVENT_COMPONENT_TARGET_SHA256)
        self.assertEqual(
            self.profile["MSG_PK/JP/msggame.bin"],
            WAVE9.RUNTIME_COMPONENT_OUTPUT_SHA256["MSG_PK/JP/msggame.bin"],
        )

    def test_manifest_has_exact_input_output_and_writer_contract(self) -> None:
        manifest = WAVE9.build_manifest(self.payload)
        self.assertEqual(manifest["schema"], WAVE9.SCHEMA)
        self.assertEqual(manifest["transaction_id"], WAVE9.TRANSACTION_ID)
        self.assertEqual(manifest["profile_paths"], list(WAVE9.PROFILE_PATHS))
        self.assertEqual(manifest["changed_paths"], list(WAVE9.CHANGED_PATHS))
        self.assertEqual(manifest["input_sha256"], WAVE9.INPUT_SHA256)
        self.assertEqual(manifest["output_sha256"], WAVE9.TARGET_SHA256)
        self.assertEqual(manifest["pinned_output_sha256"], WAVE9.TARGET_SHA256)

    def test_writer_exposes_profile_process_backup_rollback_and_dry_run_guards(self) -> None:
        source = WRITER_PATH.read_text(encoding="utf-8")
        for required in (
            "Get-ProfileState",
            "Assert-Game-Stopped",
            "Replace-Atomically",
            "Restore-Written",
            "[System.IO.File]::Replace",
            "backup hash mismatch",
            "post-apply full profile mismatch",
            "apply_dry_run",
            "restore_dry_run",
            "a non-dry-run transaction may not target a tmp candidate directory",
        ):
            with self.subTest(required=required):
                self.assertIn(required, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
