#!/usr/bin/env python3
"""Contract tests for the private Wave 87 PK assignment candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave87_pk_assignment_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave87_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 87 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W87 = load_builder()


class Wave87StaticAssignmentTests(unittest.TestCase):
    def test_scope_is_exactly_three_fixed_pk_assignment_records(self) -> None:
        self.assertEqual([change.coordinate for change in W87.CHANGES], [(6, 4471), (6, 4479), (6, 4482)])
        self.assertEqual(len({change.coordinate for change in W87.CHANGES}), 3)
        for change in W87.CHANGES:
            self.assertEqual(change.target_literal.count("\n"), 2)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W87.PC_SOURCE_FILE_SHA256))

    def test_semantic_three_line_targets_are_exact_and_within_person_dialogue_cap(self) -> None:
        expected = {
            (6, 4471): "싸움과는 다소 먼 땅이니\n그야말로 내 정무 솜씨를 보일 곳\n기꺼이 배속을 받겠습니다.",
            (6, 4479): "제 특성은 바로 그 땅과 같은\n전선에서야말로 빛나는 것이라…\n활약을 기대하셔도 실망시키지 않겠소.",
            (6, 4482): "적지에 접한 그 땅이라면\n내 조략 솜씨를 선보일 기회도\n있을지 모르겠소.",
        }
        self.assertEqual({change.coordinate: change.target_literal for change in W87.CHANGES}, expected)
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W87.CHANGES},
            {(6, 4471): (552, 744, 600), (6, 4479): (648, 720, 864), (6, 4482): (552, 672, 384)},
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave86_identical(self) -> None:
        bundle = W87.prepare_candidate()
        self.assertEqual(
            W87.sha256_bytes(bundle.packed[W87.BASE_RESOURCE]),
            W87.INPUT_PROFILES[W87.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W87.sha256_bytes(bundle.packed[W87.PK_RESOURCE]),
            W87.TARGET_PROFILES[W87.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 3)
        self.assertEqual(bundle.manifest["resources"][W87.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        for row in bundle.audit["records"]:
            self.assertEqual(row["display_line_count"], 3)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(len(row["display_lines"]), 3)
            self.assertEqual(set(row["pc_source_anchor"]), set(W87.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W87.prepare_candidate()
        output = W87.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W87.verify_private()
        self.assertEqual(result["changed_record_count"], 3)
        self.assertTrue(result["base_byte_identical_from_wave86"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
