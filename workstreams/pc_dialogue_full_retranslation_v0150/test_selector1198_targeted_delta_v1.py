#!/usr/bin/env python3
"""Minimal immutable-checkpoint checks for selector 1198."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_runtime_vm_post_selector1198_consolidated_checkpoint_v1.py"
)
spec = importlib.util.spec_from_file_location("selector1198_delta_tested", BUILDER_PATH)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector1198TargetedDeltaTest(unittest.TestCase):
    def test_written_checkpoint(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        report = json.loads(BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text("ascii"))
        self.assertEqual(report["result"]["runtime_review_pending"], 6464)
        self.assertEqual(report["result"]["fully_candidate_eligible"], 46339)
        self.assertEqual(
            report["selector1198_consolidated"]["promotion_count"], 25
        )
        self.assertFalse(report["validation"]["full_integration_engine_invoked"])
        self.assertFalse(report["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
