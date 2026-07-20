#!/usr/bin/env python3
"""Contract tests for the private Wave 92 PK regional/policy candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave92_pk_regional_policy_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave92_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 92 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W92 = load_builder()


class Wave92StaticRegionalPolicyTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_static_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W92.CHANGES],
            [(15, 1619), (15, 1622), (15, 1627), (15, 1665)],
        )
        self.assertEqual(len({change.coordinate for change in W92.CHANGES}), 4)
        for change in W92.CHANGES:
            self.assertEqual(change.target_literal.count("\n"), 2)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W92.PC_SOURCE_FILE_SHA256))

    def test_targets_and_semantic_three_line_layouts_are_exact(self) -> None:
        expected = {
            (15, 1619): "무사시는 간토의 중심이며\n인접국도 많은 땅입니다.\n일대 장악은 타국 진출의 발판입니다.",
            (15, 1622): "오와리는 동국과 서국의 경계에 있고,\n기나이까지 시야에 두는 요충지입니다.\n이 지역을 제압한 의의는 매우 큽니다.",
            (15, 1627): "반슈는 서국과 교토를 잇는 요지입니다.\n하리마노카미와 이요노카미는\n각국 국사 중 가장 격이 높습니다.",
            (15, 1665): "강적을 이기려면 국력을 키워야 합니다.\n여유 자금이 있다면\n성하 시설 증축을 제안합니다.",
        }
        self.assertEqual({change.coordinate: change.target_literal for change in W92.CHANGES}, expected)
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W92.CHANGES},
            {
                (15, 1619): (576, 552, 840),
                (15, 1622): (840, 864, 864),
                (15, 1627): (888, 648, 768),
                (15, 1665): (888, 432, 672),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave91_identical(self) -> None:
        bundle = W92.prepare_candidate()
        self.assertEqual(
            W92.sha256_bytes(bundle.packed[W92.BASE_RESOURCE]),
            W92.INPUT_PROFILES[W92.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W92.sha256_bytes(bundle.packed[W92.PK_RESOURCE]),
            W92.TARGET_PROFILES[W92.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W92.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        self.assertEqual(bundle.audit["non_target_record_byte_identity"], "PASS")
        for row in bundle.audit["records"]:
            self.assertEqual(row["display_line_count"], 3)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(set(row["pc_source_anchor"]), set(W92.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W92.prepare_candidate()
        output = W92.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W92.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave91"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
