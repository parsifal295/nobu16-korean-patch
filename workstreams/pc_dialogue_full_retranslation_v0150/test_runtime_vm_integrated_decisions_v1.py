#!/usr/bin/env python3
"""Regression tests for the v0.15.0 runtime VM integration boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
INTEGRATED = OUTPUT_ROOT / "runtime_vm_integrated.private.v1.jsonl"
REPORT = WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
PROGRESS = WORKSTREAM / "progress.source_free.v1.json"
SHADOW_STEAM_ROOT = (
    OUTPUT_ROOT / "development_steam_root_pre_base_runtime_apply_13a404f"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("runtime_vm_integration_test_engine", ENGINE_PATH)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


class RuntimeVmIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prepared = ENGINE.prepare_artifacts(
            SHADOW_STEAM_ROOT,
            ENGINE.DEFAULT_BASE_PRISTINE,
            (
                SHADOW_STEAM_ROOT
                / "KR_PATCH_BACKUP"
                / "file_only_transaction"
                / "steam-jp-1.1.7-v0.6.0"
                / "originals"
                / "MSG_PK"
                / "JP"
                / "msggame.bin"
            ),
        )
        cls.rows = read_jsonl(INTEGRATED)

    def validate_rows(self, rows: list[dict[str, Any]]) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "decisions.private.v1.jsonl"
            path.write_text(ENGINE.jsonl(rows), encoding="utf-8", newline="\n")
            ENGINE.validate_decisions(
                self.prepared,
                path,
                require_complete=False,
            )

    def test_integrated_universe_and_source_free_counts(self) -> None:
        self.assertEqual(len(self.rows), 52_803)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["promotions"]["promoted_total"], 27_545)
        self.assertEqual(report["result"]["runtime_review_pending"], 8_789)
        self.assertEqual(
            report["promotions"]["pk_msggame"]["promotion_count"],
            11_894,
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"]["residual"][
                "promotion_count"
            ],
            2_908,
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"]["pk_only_exact_blocked"][
                "promotion_count"
            ],
            1_533,
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"]["full_candidate_bound"]
        )
        self.assertFalse(report["steam_write_performed"])
        self.assertEqual(
            progress["totals"]["runtime_review_pending"],
            8_789,
        )
        self.assertEqual(
            progress["runtime_vm_integration"][
                "private_integrated_decision_sha256"
            ],
            report["result"]["private_integrated_decision_sha256"],
        )

    def test_pk_verified_row_is_bound_to_exact_overlay(self) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["runtime_review"] == "verified"
            and row["runtime_vm_verification"]["method"]
            == "reversed_vm_full_candidate_static_analysis"
        )
        self.validate_rows([source])

        missing = copy.deepcopy(source)
        missing.pop("runtime_vm_verification")
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([missing])

        tampered = copy.deepcopy(source)
        tampered["runtime_vm_verification"][
            "translation_utf16le_sha256"
        ] = "0" * 64
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered])

    def test_pk_residual_row_binds_runtime_and_layout_transitions(self) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["runtime_review"] == "verified"
            and row["runtime_vm_verification"]["method"]
            == "reversed_vm_residual_full_closure_nonexpansion_analysis"
        )
        self.assertEqual(source["layout_review"], "runtime_verified")
        self.validate_rows([source])

        bad_layout = copy.deepcopy(source)
        bad_layout["layout_review"] = "runtime_pending"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_layout])

        bad_evidence = copy.deepcopy(source)
        bad_evidence["runtime_vm_verification"]["layout_transition"][
            "to"
        ] = "runtime_pending"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_evidence])

    def test_pk_only_exact_blocked_row_preserves_layout_binding(self) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["runtime_review"] == "verified"
            and row["runtime_vm_verification"]["method"]
            == "reversed_vm_pk_only_exact_blocked_closure_nonexpansion_analysis"
        )
        self.assertEqual(source["layout_review"], "unchanged_from_current")
        self.assertEqual(
            source["runtime_vm_verification"]["layout_review_binding"],
            {"status": "unchanged_from_current"},
        )
        self.validate_rows([source])

        bad_layout = copy.deepcopy(source)
        bad_layout["layout_review"] = "runtime_verified"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_layout])

        bad_binding = copy.deepcopy(source)
        bad_binding["runtime_vm_verification"]["layout_review_binding"][
            "status"
        ] = "runtime_verified"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_binding])


if __name__ == "__main__":
    unittest.main()
