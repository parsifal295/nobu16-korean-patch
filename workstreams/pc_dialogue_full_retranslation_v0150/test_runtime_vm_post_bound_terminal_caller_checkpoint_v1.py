#!/usr/bin/env python3
"""Boundary tests for the frozen post-bound-terminal-caller checkpoint."""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = (
    WORKSTREAM
    / "build_runtime_vm_post_bound_terminal_caller_checkpoint_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    "runtime_vm_post_bound_terminal_caller_checkpoint_test_builder",
    BUILDER_PATH,
)


class PostBoundTerminalCallerCheckpointTests(unittest.TestCase):
    def test_all_closure_flags_are_explicit_and_default_off(self) -> None:
        parameters = inspect.signature(
            BUILDER.INTEGRATION.build_outputs
        ).parameters
        for name in (
            "include_dynamic_honorific_spacing",
            "include_bound_terminal_family",
            "include_thought_predicate_family",
            "include_bound_terminal_caller",
        ):
            self.assertIs(parameters[name].default, False)

    def test_frozen_counts_and_digest_match_integration_constants(self) -> None:
        integration = BUILDER.INTEGRATION
        self.assertEqual(BUILDER.EXPECTED_ROWS, 52_803)
        self.assertEqual(BUILDER.EXPECTED_PENDING, 8_577)
        self.assertEqual(BUILDER.EXPECTED_PK_PROMOTIONS, 12_106)
        self.assertEqual(
            BUILDER.EXPECTED_PRIVATE_SHA256,
            (
                "54B4255C29F256B84E1CA4EE8A9B5D21"
                "FE254100A2A71CA28657F7EF6EB34E45"
            ),
        )
        self.assertEqual(
            BUILDER.EXPECTED_PENDING,
            integration.EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PENDING_AFTER,
        )
        self.assertEqual(
            BUILDER.EXPECTED_PK_PROMOTIONS,
            integration.EXPECTED_PK_BOUND_TERMINAL_CALLER_FINAL_PROMOTIONS,
        )
        self.assertEqual(
            BUILDER.EXPECTED_PRIVATE_SHA256,
            integration.EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PRIVATE_SHA256,
        )

    def test_default_paths_preserve_private_public_boundary(self) -> None:
        args = argparse.Namespace(
            private_output=BUILDER.DEFAULT_PRIVATE_OUTPUT,
            public_output=BUILDER.DEFAULT_PUBLIC_OUTPUT,
        )
        BUILDER.validate_output_paths(args)
        self.assertIn(
            BUILDER.OUTPUT_ROOT.resolve(strict=False),
            BUILDER.DEFAULT_PRIVATE_OUTPUT.resolve(strict=False).parents,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.parent.resolve(strict=False),
            WORKSTREAM.resolve(strict=False),
        )

    def test_private_output_cannot_escape_tmp_output_root(self) -> None:
        args = argparse.Namespace(
            private_output=WORKSTREAM / "private.jsonl",
            public_output=BUILDER.DEFAULT_PUBLIC_OUTPUT,
        )
        with self.assertRaises(BUILDER.CheckpointError):
            BUILDER.validate_output_paths(args)

    def test_private_output_cannot_equal_output_root(self) -> None:
        args = argparse.Namespace(
            private_output=BUILDER.OUTPUT_ROOT,
            public_output=BUILDER.DEFAULT_PUBLIC_OUTPUT,
        )
        with self.assertRaises(BUILDER.CheckpointError):
            BUILDER.validate_output_paths(args)

    def test_public_output_is_fixed_to_tracked_source_free_path(self) -> None:
        args = argparse.Namespace(
            private_output=BUILDER.DEFAULT_PRIVATE_OUTPUT,
            public_output=BUILDER.OUTPUT_ROOT / "public.json",
        )
        with self.assertRaises(BUILDER.CheckpointError):
            BUILDER.validate_output_paths(args)

    def test_tracked_report_is_source_free_and_frozen(self) -> None:
        report = json.loads(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="utf-8")
        )
        BUILDER.validate_checkpoint_report(report)
        self.assertFalse(report["steam_write_performed"])
        self.assertFalse(
            report["distribution_policy"][
                "tracked_report_contains_commercial_source_text"
            ]
        )
        self.assertFalse(
            report["distribution_policy"][
                "tracked_report_contains_translated_dialogue_text"
            ]
        )


if __name__ == "__main__":
    unittest.main()
