#!/usr/bin/env python3
"""Contract tests for the private Wave 84 B2 static completion candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave84_b2_static_completion_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave84_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 84 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W84 = load_builder()


class Wave84StaticCompletionTests(unittest.TestCase):
    def test_scope_is_exactly_the_nine_base_b2_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W84.CHANGES],
            [(2, 215), (2, 220), (2, 225), (2, 241), (2, 484), (2, 485), (2, 514), (2, 536), (2, 550)],
        )
        self.assertEqual(len({change.coordinate for change in W84.CHANGES}), 9)
        for change in W84.CHANGES:
            expected_break_count = 2 if change.coordinate == (2, 215) else 1
            self.assertEqual(change.target_literal.count("\n"), expected_break_count)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W84.PC_SOURCES))

    def test_prepare_candidate_is_surgical_and_pk_is_unchanged(self) -> None:
        bundle = W84.prepare_candidate()
        self.assertEqual(
            W84.sha256_bytes(bundle.packed[W84.BASE_RESOURCE]),
            W84.TARGET_PROFILES[W84.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W84.sha256_bytes(bundle.packed[W84.PK_RESOURCE]),
            W84.INPUT_PROFILES[W84.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 9)
        self.assertEqual(bundle.manifest["resources"][W84.PK_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        self.assertEqual(bundle.audit["source_policy"]["layout_baseline"]["max_lines"], 4)
        rows = {row["coordinate"]: row for row in bundle.audit["records"]}
        self.assertEqual(rows["2:215"]["display_line_count"], 3)
        for row in rows.values():
            self.assertFalse(row["target_any_effective_line_exceeds_912px"])
            self.assertEqual(len(row["display_lines"]), row["display_line_count"])
            for line in row["display_lines"]:
                self.assertEqual(
                    set(line),
                    {
                        "display_string",
                        "raw_g1n_width_px",
                        "effective_width_px",
                        "full_width_character_count",
                        "half_width_character_count",
                        "exceeds_912px",
                    },
                )

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W84.prepare_candidate()
        output = W84.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W84.verify_private()
        self.assertEqual(result["changed_record_count"], 9)
        self.assertTrue(result["pk_byte_identical"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
