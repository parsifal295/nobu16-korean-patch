#!/usr/bin/env python3
"""Contract tests for the private Wave 85 Base B2 completion candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave85_b2_static_completion_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave85_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 85 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W85 = load_builder()


class Wave85StaticCompletionTests(unittest.TestCase):
    def test_scope_is_exactly_the_six_base_b2_terminal_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W85.CHANGES],
            [(2, 315), (2, 331), (2, 335), (2, 340), (2, 343), (2, 538)],
        )
        self.assertEqual(len({change.coordinate for change in W85.CHANGES}), 6)
        for change in W85.CHANGES:
            self.assertEqual(change.target_literal.count("\n"), 1)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W85.PC_SOURCE_PROFILES))

    def test_prepare_candidate_is_surgical_and_pk_remains_wave83_identical(self) -> None:
        bundle = W85.prepare_candidate()
        self.assertEqual(
            W85.sha256_bytes(bundle.packed[W85.BASE_RESOURCE]),
            W85.TARGET_PROFILES[W85.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W85.sha256_bytes(bundle.packed[W85.PK_RESOURCE]),
            W85.INPUT_PROFILES[W85.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 6)
        self.assertEqual(bundle.manifest["resources"][W85.PK_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        self.assertEqual(bundle.audit["source_policy"]["layout_baseline"]["max_lines"], 4)
        for row in bundle.audit["records"]:
            self.assertEqual(row["display_line_count"], 2)
            self.assertFalse(row["target_any_effective_line_exceeds_912px"])
            self.assertEqual(len(row["display_lines"]), 2)
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
        bundle = W85.prepare_candidate()
        output = W85.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W85.verify_private()
        self.assertEqual(result["changed_record_count"], 6)
        self.assertTrue(result["pk_byte_identical_from_wave83"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
