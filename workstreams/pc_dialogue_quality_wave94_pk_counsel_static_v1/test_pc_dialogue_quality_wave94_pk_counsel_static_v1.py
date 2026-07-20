#!/usr/bin/env python3
"""Contract tests for the private Wave 94 PK counsel candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave94_pk_counsel_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave94_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 94 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W94 = load_builder()


class Wave94StaticCounselTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_static_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W94.CHANGES],
            [(15, 2281), (15, 2364), (15, 2373), (15, 2374)],
        )
        self.assertEqual(len({change.coordinate for change in W94.CHANGES}), 4)
        for change in W94.CHANGES:
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W94.PC_SOURCE_FILE_SHA256))
        self.assertEqual(
            {change.coordinate: change.target_literal.count("\n") for change in W94.CHANGES},
            {(15, 2281): 2, (15, 2364): 2, (15, 2373): 1, (15, 2374): 1},
        )

    def test_targets_and_semantic_layouts_are_exact(self) -> None:
        expected = {
            (15, 2281): "본거지 개발도 아직 진행 중이니\n군 개발을 추진하면서\n호기를 놓치지 않도록 하십시오.",
            (15, 2364): "각지의 상업을 장려해\n금전 수입을 늘리면\n우리 가문의 힘이 될 것입니다.",
            (15, 2373): "적 다이묘는 뛰어난 지략가이니\n이번 일은 쉽지 않을 듯합니다.",
            (15, 2374): "목표한 영주는 뛰어난 지략가이니\n이번 일은 쉽지 않을 듯하옵니다.",
        }
        self.assertEqual({change.coordinate: change.target_literal for change in W94.CHANGES}, expected)
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W94.CHANGES},
            {
                (15, 2281): (720, 480, 720),
                (15, 2364): (480, 432, 696),
                (15, 2373): (696, 696),
                (15, 2374): (744, 744),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave93_identical(self) -> None:
        bundle = W94.prepare_candidate()
        self.assertEqual(
            W94.sha256_bytes(bundle.packed[W94.BASE_RESOURCE]),
            W94.INPUT_PROFILES[W94.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W94.sha256_bytes(bundle.packed[W94.PK_RESOURCE]),
            W94.TARGET_PROFILES[W94.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W94.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        self.assertEqual(bundle.audit["non_target_record_byte_identity"], "PASS")
        expected_lines = {(15, 2281): 3, (15, 2364): 3, (15, 2373): 2, (15, 2374): 2}
        for row in bundle.audit["records"]:
            coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
            self.assertEqual(row["display_line_count"], expected_lines[coordinate])
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(set(row["pc_source_anchor"]), set(W94.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W94.prepare_candidate()
        output = W94.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W94.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave93"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
