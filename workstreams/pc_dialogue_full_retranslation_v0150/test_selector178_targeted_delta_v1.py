#!/usr/bin/env python3
"""Minimal immutable-checkpoint checks for selector 178."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_runtime_vm_post_selector178_consolidated_checkpoint_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector178_delta_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector178TargetedDeltaTest(unittest.TestCase):
    def test_written_checkpoint(self) -> None:
        self.assertEqual(BUILDER.main(["--check"]), 0)
        report = json.loads(BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text("ascii"))
        self.assertEqual(report["result"]["row_count"], 52_803)
        self.assertEqual(report["result"]["affected_row_count"], 70)
        self.assertEqual(
            report["result"]["unaffected_raw_line_copy_count"], 52_733
        )
        self.assertEqual(report["result"]["runtime_review_pending"], 6_432)
        self.assertEqual(
            report["result"]["fully_candidate_eligible"], 46_371
        )
        self.assertEqual(report["result"]["confirmed_non_display"], 345)
        self.assertEqual(
            report["selector178_consolidated"]["promotion_count"], 32
        )
        self.assertEqual(
            report["selector178_consolidated"][
                "verification_renewal_count"
            ],
            38,
        )
        self.assertEqual(
            report["selector178_consolidated"]["semantic_override_count"],
            47,
        )
        self.assertFalse(report["validation"]["full_integration_engine_invoked"])
        self.assertTrue(
            report["validation"]["confirmed_non_display_rows_preserved"]
        )
        self.assertFalse(report["steam_write_performed"])

    def test_tracked_outputs_are_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r'["\']\d+:\d+(?::\d+){0,2}["\']')
        for path in (
            BUILDER_PATH,
            SCRIPT,
            BUILDER.DEFAULT_PUBLIC_OUTPUT,
        ):
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(content), path)
            self.assertIsNone(coordinate.search(content), path)


if __name__ == "__main__":
    unittest.main()
