#!/usr/bin/env python3
"""Contract tests for the private Wave 86 PK assessment candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave86_pk_assessment_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave86_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 86 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W86 = load_builder()


class Wave86StaticAssessmentTests(unittest.TestCase):
    def test_scope_is_exactly_the_eight_fixed_pk_assessment_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W86.CHANGES],
            [(15, 231), (15, 232), (15, 235), (15, 236), (15, 239), (15, 240), (15, 243), (15, 244)],
        )
        self.assertEqual(len({change.coordinate for change in W86.CHANGES}), 8)
        for change in W86.CHANGES:
            self.assertEqual(change.target_literal.count("\n"), 1)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W86.PC_SOURCE_PROFILES))

    def test_repeated_assessment_variants_remain_textually_consistent(self) -> None:
        positive = [change for change in W86.CHANGES if change.coordinate[1] in (231, 235, 239, 243)]
        adequate = [change for change in W86.CHANGES if change.coordinate[1] in (232, 236, 240, 244)]
        self.assertEqual({change.target_literal for change in positive}, {"이거라면 좋은 성과를\n얻을 수 있습니다."})
        self.assertEqual({change.target_literal for change in adequate}, {"그럭저럭의 성과는\n거둘 수 있습니다."})

    def test_prepare_candidate_is_surgical_and_base_remains_wave85_identical(self) -> None:
        bundle = W86.prepare_candidate()
        self.assertEqual(
            W86.sha256_bytes(bundle.packed[W86.BASE_RESOURCE]),
            W86.INPUT_PROFILES[W86.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W86.sha256_bytes(bundle.packed[W86.PK_RESOURCE]),
            W86.TARGET_PROFILES[W86.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 8)
        self.assertEqual(bundle.manifest["resources"][W86.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        self.assertEqual(bundle.audit["source_policy"]["layout_baseline"]["max_lines"], 3)
        for row in bundle.audit["records"]:
            self.assertEqual(row["display_line_count"], 2)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(len(row["display_lines"]), 2)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W86.prepare_candidate()
        output = W86.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W86.verify_private()
        self.assertEqual(result["changed_record_count"], 8)
        self.assertTrue(result["base_byte_identical_from_wave85"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
