#!/usr/bin/env python3
"""Boundary tests for the frozen selector568/1096/1174 checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = (
    WORKSTREAM
    / "build_runtime_vm_post_selector568_1096_1174_"
    "consolidated_checkpoint_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


BUILDER = load_module(
    "runtime_vm_post_selector568_1096_1174_checkpoint_test_builder",
    BUILDER_PATH,
)


class PostSelector56810961174CheckpointTests(unittest.TestCase):
    def test_all_required_closure_flags_are_explicit_and_default_off(
        self,
    ) -> None:
        parameters = inspect.signature(
            BUILDER.INTEGRATION.build_outputs
        ).parameters
        for name in (
            "include_dynamic_honorific_spacing",
            "include_bound_terminal_family",
            "include_thought_predicate_family",
            "include_bound_terminal_caller",
            "include_bound_terminal_2546_full_caller",
            "include_bound_terminal_2546_simple_caller",
            "include_bound_terminal_2546_category_b_immediate",
            "include_selector538_chunk0",
            "include_bound_terminal_2546_category_b_deferred",
            "include_selector538_family",
            "include_selector568_1096_1174_consolidated",
        ):
            self.assertIs(parameters[name].default, False)

    def test_frozen_counts_and_digests_match_final_integration(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_ROWS, 52_803)
        self.assertEqual(BUILDER.EXPECTED_PENDING, 7_268)
        self.assertEqual(BUILDER.EXPECTED_ELIGIBLE, 45_535)
        self.assertEqual(BUILDER.EXPECTED_PK_PROMOTIONS, 13_415)
        self.assertEqual(BUILDER.EXPECTED_PROMOTED_TOTAL, 29_066)
        self.assertEqual(BUILDER.EXPECTED_UPDATED_ROWS, 1_173)
        self.assertEqual(BUILDER.EXPECTED_LAYER_PROMOTIONS, 628)
        self.assertEqual(BUILDER.EXPECTED_LAYER_RENEWALS, 545)
        self.assertEqual(BUILDER.EXPECTED_LAYER_OVERRIDES, 440)
        self.assertEqual(
            BUILDER.EXPECTED_PRIVATE_SHA256,
            (
                "FC157A9907686D0EA6DC6C61C7785E81"
                "AC7F750100F2E1CDDE02DBF4F09F2DCA"
            ),
        )
        self.assertEqual(
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
            (
                "07E65E6338D32C1FD13F17408F82A413"
                "3E55541C722874632948C7B36C909805"
            ),
        )

    def test_frozen_inputs_are_exactly_bound(self) -> None:
        BUILDER.validate_frozen_inputs()
        self.assertEqual(
            sha256_file(BUILDER.INTEGRATION_PATH),
            BUILDER.EXPECTED_INTEGRATION_BUILDER_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.PREDECESSOR_PRIVATE_PATH),
            BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )
        self.assertEqual(
            sha256_file(BUILDER.PREDECESSOR_PUBLIC_PATH),
            BUILDER.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
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

    def test_private_output_cannot_escape_or_change_checkpoint(self) -> None:
        for private_output in (
            WORKSTREAM / "private.jsonl",
            BUILDER.OUTPUT_ROOT,
            BUILDER.OUTPUT_ROOT / "different.private.v1.jsonl",
        ):
            args = argparse.Namespace(
                private_output=private_output,
                public_output=BUILDER.DEFAULT_PUBLIC_OUTPUT,
            )
            with self.assertRaises(BUILDER.CheckpointError):
                BUILDER.validate_output_paths(args)

    def test_public_output_is_fixed(self) -> None:
        args = argparse.Namespace(
            private_output=BUILDER.DEFAULT_PRIVATE_OUTPUT,
            public_output=BUILDER.OUTPUT_ROOT / "public.json",
        )
        with self.assertRaises(BUILDER.CheckpointError):
            BUILDER.validate_output_paths(args)

    def test_private_checkpoint_is_frozen_below_tmp(self) -> None:
        self.assertTrue(BUILDER.DEFAULT_PRIVATE_OUTPUT.is_file())
        self.assertEqual(
            sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_SHA256,
        )

    def test_tracked_report_is_source_free_and_frozen(self) -> None:
        raw = BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="utf-8")
        report = json.loads(raw)
        BUILDER.validate_checkpoint_report(report)
        self.assertEqual(
            hashlib.sha256(raw.encode("utf-8")).hexdigest().upper(),
            BUILDER.EXPECTED_PUBLIC_SHA256,
        )
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
        self.assertNotRegex(
            raw,
            re.compile(
                r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
                r"\uac00-\ud7a3]"
            ),
        )
        for forbidden in (
            '"translation":',
            '"source_text":',
            '"dialogue_text":',
        ):
            self.assertNotIn(forbidden, raw)


if __name__ == "__main__":
    unittest.main()
