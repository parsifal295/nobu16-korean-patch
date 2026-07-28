#!/usr/bin/env python3
"""Focused immutable-checkpoint and progress checks for selector 628."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name: str):
    path = HERE / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Selector628TargetedDeltaTests(unittest.TestCase):
    def test_checkpoint_and_progress_are_frozen(self) -> None:
        checkpoint = load(
            "build_runtime_vm_post_selector628_consolidated_checkpoint_v1.py"
        )
        progress = load(
            "build_progress_post_selector628_consolidated_delta_v1.py"
        )
        self.assertEqual(
            checkpoint.BASE.sha256_file(checkpoint.DEFAULT_PRIVATE_OUTPUT),
            checkpoint.EXPECTED_PRIVATE_OUTPUT_SHA256,
        )
        self.assertEqual(
            checkpoint.BASE.sha256_file(checkpoint.DEFAULT_PUBLIC_OUTPUT),
            checkpoint.EXPECTED_PUBLIC_OUTPUT_SHA256,
        )
        self.assertEqual(
            progress.BASE.sha256_file(progress.DEFAULT_PROGRESS_OUTPUT),
            progress.EXPECTED_PROGRESS_OUTPUT_SHA256,
        )
        self.assertEqual(
            progress.BASE.sha256_file(progress.IMMUTABLE_PROGRESS_OUTPUT),
            progress.EXPECTED_PROGRESS_OUTPUT_SHA256,
        )

    def test_public_counts_and_lineage(self) -> None:
        checkpoint = json.loads(
            (
                HERE
                / "runtime_vm_integration.post_selector628_consolidated_checkpoint.source_free.v1.json"
            ).read_text(encoding="ascii")
        )
        progress = json.loads(
            (HERE / "progress.source_free.v1.json").read_text(encoding="ascii")
        )
        self.assertEqual(checkpoint["result"]["runtime_review_pending"], 6_489)
        self.assertEqual(checkpoint["result"]["promoted_total"], 29_845)
        self.assertEqual(progress["totals"]["runtime_review_pending"], 6_489)
        self.assertEqual(progress["totals"]["fully_candidate_eligible"], 46_314)
        self.assertEqual(
            progress["runtime_vm_integration"]["sha256"],
            "D75600A25C086D41190589DA21C8B389ACD9A9BAD561B920F9BB25F5FB9E5B88",
        )
        self.assertFalse(checkpoint["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
