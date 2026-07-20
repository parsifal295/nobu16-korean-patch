#!/usr/bin/env python3
"""Contract tests for the private Wave 90 PK fixed-counsel candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave90_pk_counsel_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave90_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 90 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W90 = load_builder()


class Wave90StaticCounselTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_block15_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W90.CHANGES],
            [(15, 2421), (15, 2439), (15, 2443), (15, 2448)],
        )
        self.assertEqual(len({change.coordinate for change in W90.CHANGES}), 4)
        for change in W90.CHANGES:
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W90.PC_SOURCE_FILE_SHA256))

    def test_counsel_goal_and_retribution_targets_are_exact(self) -> None:
        expected = {
            (15, 2421): "이미 저쪽은 당가를 노리는 모양새…\n서둘러 무언가 손을 써야 합니다.",
            (15, 2439): "목표를 제안한 보람이 있구나\n앞으로 한층 더 힘쓰겠다.",
            (15, 2443): "가까운 목표가 있어야\n평소의 임무에도 힘이 나는 법…\n그래서 한 가지 생각해 보았습니다.",
            (15, 2448): "당가를 얕보고 조략한 대가\n치르게 해 주겠소.",
        }
        self.assertEqual({change.coordinate: change.target_literal for change in W90.CHANGES}, expected)
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W90.CHANGES},
            {
                (15, 2421): (816, 744),
                (15, 2439): (648, 576),
                (15, 2443): (480, 720, 792),
                (15, 2448): (600, 408),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave89_identical(self) -> None:
        bundle = W90.prepare_candidate()
        self.assertEqual(
            W90.sha256_bytes(bundle.packed[W90.BASE_RESOURCE]),
            W90.INPUT_PROFILES[W90.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W90.sha256_bytes(bundle.packed[W90.PK_RESOURCE]),
            W90.TARGET_PROFILES[W90.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W90.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        self.assertEqual(bundle.audit["non_target_record_byte_identity"], "PASS")
        for row in bundle.audit["records"]:
            self.assertLessEqual(row["display_line_count"], 3)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(set(row["pc_source_anchor"]), set(W90.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W90.prepare_candidate()
        output = W90.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W90.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave89"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
