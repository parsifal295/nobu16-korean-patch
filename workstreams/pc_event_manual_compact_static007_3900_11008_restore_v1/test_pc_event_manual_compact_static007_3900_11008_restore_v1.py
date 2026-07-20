#!/usr/bin/env python3
"""Private deterministic checks for the 3900/8000--11008 restoration candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_manual_compact_static007_3900_11008_restore_v1.py")
SPEC = importlib.util.spec_from_file_location("manual_compact_3900_11008", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class ManualCompact3900To11008Tests(unittest.TestCase):
    def test_reviewed_scope_and_layout(self) -> None:
        _event, _header, strict, _profile, _record = builder.load_strict()
        rows, _artifacts = builder.load_reviews(strict)
        self.assertEqual(len(rows), 640)
        self.assertEqual(sum(row.current_ko != row.proposed_ko for row in rows), 607)
        self.assertEqual(sum(row.current_ko == row.proposed_ko for row in rows), 33)
        for row in rows:
            self.assertLessEqual(row.layout["line_count"], 4)
            self.assertTrue(row.layout["all_lines_pass_static_patch_007"])

    def test_private_candidate_exactness(self) -> None:
        self.assertIsNotNone(builder.EXPECTED_OUTPUT_PROFILE)
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["reviewed_row_count"], 640)
        self.assertEqual(result["changed_row_count"], 607)
        self.assertEqual(result["preserved_row_count"], 33)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["release_published"])
        self.assertFalse(result["network_operation_performed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
