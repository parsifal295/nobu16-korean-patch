#!/usr/bin/env python3
"""Regression tests for progress after the PK 2546 full-caller layer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_progress_source_free_v0150.py"
PROGRESS_PATH = WORKSTREAM / "progress.source_free.v1.json"
EXPECTED_PROGRESS_SHA256 = (
    "7B35B09FB119CFDF4AC27311FADAB6F6817E17588DD3993E96987652710F81DC"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("progress_post_bound_terminal_2546_builder", BUILDER_PATH)


class ProgressPostBoundTerminal2546Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = PROGRESS_PATH.read_bytes()
        cls.progress = json.loads(cls.raw.decode("utf-8"))

    def test_progress_is_frozen_source_free_and_non_deploying(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.raw).hexdigest().upper(),
            EXPECTED_PROGRESS_SHA256,
        )
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3130-\u318f\u3400-\u4dbf"
                r"\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                self.raw.decode("utf-8"),
            )
        )

        steam_flags: list[bool] = []

        def collect(value: Any) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "steam_write_performed":
                        steam_flags.append(child)
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)

        collect(self.progress)
        self.assertTrue(steam_flags)
        self.assertTrue(all(flag is False for flag in steam_flags))

    def test_totals_match_integrated_decision_universe(self) -> None:
        self.assertEqual(
            self.progress["totals"],
            {
                "semantic_review_approved": 52_803,
                "runtime_review_pending": 8_213,
                "fully_candidate_eligible": 44_590,
                "scope_classification_counts": {
                    "confirmed_non_display": 345,
                    "retranslated": 44_245,
                    "runtime_fragment_pending": 8_213,
                },
                "semantic_completion": True,
                "candidate_build_complete": False,
            },
        )

    def test_2546_layer_and_override_consumption_are_published(self) -> None:
        integration = self.progress["runtime_vm_integration"]
        self.assertEqual(
            integration["sha256"],
            BUILDER.EXPECTED_RUNTIME_VM_INTEGRATION_REPORT_SHA256,
        )
        self.assertEqual(
            integration["private_integrated_decision_sha256"],
            BUILDER.EXPECTED_RUNTIME_VM_INTEGRATED_PRIVATE_SHA256,
        )
        self.assertTrue(
            integration[
                "bound_terminal_2546_full_caller_layer_included"
            ]
        )
        layer = integration["bound_terminal_2546_full_caller"]
        self.assertEqual(layer["translation_override_count"], 216)
        self.assertEqual(layer["promotion_count"], 364)
        self.assertEqual(layer["verification_renewal_count"], 292)
        self.assertEqual(
            layer["action_counts"],
            BUILDER.BOUND_TERMINAL_2546_EXPECTED_ACTION_COUNTS,
        )
        self.assertEqual(
            integration["bound_terminal_2546_full_caller_override_count"],
            216,
        )
        self.assertEqual(
            integration[
                "bound_terminal_2546_superseded_terminal_override_count"
            ],
            7,
        )
        self.assertEqual(
            integration[
                "bound_terminal_2546_superseded_thought_override_count"
            ],
            3,
        )
        self.assertEqual(
            integration[
                "bound_terminal_2546_superseded_caller_override_count"
            ],
            14,
        )
        self.assertEqual(
            integration[
                "bound_terminal_2546_prior_caller_override_overlap_count"
            ],
            5,
        )

    def test_runtime_immutable_row_excludes_new_mutable_layer_fields(
        self,
    ) -> None:
        row = {
            "translation": "sentinel",
            "bound_terminal_2546_full_caller_update_action":
            "runtime_promotion",
            "bound_terminal_2546_exact_override_evidence": {"x": 1},
        }
        self.assertEqual(
            BUILDER.runtime_immutable_row(row),
            {"translation": "sentinel"},
        )


if __name__ == "__main__":
    unittest.main()
