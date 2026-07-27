#!/usr/bin/env python3
"""Boundary tests for the frozen post-honorific checkpoint wrapper."""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_dynamic_honorific_checkpoint_v1.py"
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
    "runtime_vm_post_dynamic_honorific_checkpoint_test_builder",
    BUILDER_PATH,
)


class PostDynamicHonorificCheckpointTests(unittest.TestCase):
    def test_later_terminal_layer_is_disabled_for_frozen_checkpoint(
        self,
    ) -> None:
        parameter = inspect.signature(
            BUILDER.INTEGRATION.build_outputs
        ).parameters["include_bound_terminal_family"]
        self.assertIs(parameter.default, False)
        self.assertEqual(
            BUILDER.INTEGRATION.EXPECTED_FINAL_PENDING_AFTER,
            8_645,
        )
        self.assertEqual(
            BUILDER.INTEGRATION.EXPECTED_BOUND_TERMINAL_FINAL_PENDING_AFTER,
            8_641,
        )

    def test_default_paths_preserve_private_public_boundary(self) -> None:
        args = argparse.Namespace(
            private_output=BUILDER.DEFAULT_PRIVATE_OUTPUT,
            public_output=BUILDER.DEFAULT_PUBLIC_OUTPUT,
        )
        BUILDER.validate_output_paths(args)

    def test_private_output_cannot_escape_tmp_output_root(self) -> None:
        args = argparse.Namespace(
            private_output=WORKSTREAM / "private.jsonl",
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


if __name__ == "__main__":
    unittest.main()
