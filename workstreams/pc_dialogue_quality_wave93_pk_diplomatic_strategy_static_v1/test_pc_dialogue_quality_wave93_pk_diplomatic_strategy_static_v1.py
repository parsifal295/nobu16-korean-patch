#!/usr/bin/env python3
"""Contract tests for the private Wave 93 PK diplomatic/strategy candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave93_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 93 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W93 = load_builder()


class Wave93StaticDiplomaticStrategyTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_static_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W93.CHANGES],
            [(15, 1850), (15, 1851), (15, 1860), (15, 1888)],
        )
        self.assertEqual(len({change.coordinate for change in W93.CHANGES}), 4)
        for change in W93.CHANGES:
            self.assertEqual(change.target_literal.count("\n"), 1)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W93.PC_SOURCE_FILE_SHA256))

    def test_targets_and_semantic_two_line_layouts_are_exact(self) -> None:
        expected = {
            (15, 1850): "우리 가문과 규모가 크게 다르지 않아\n서로에게 이로운 관계입니다.",
            (15, 1851): "우리 가문보다 규모가 크니\n마음 놓고 의지하셔도 좋겠습니다.",
            (15, 1860): "공격과 수비의 양립은 몹시 어렵습니다.\n어느 한쪽은 빨리 결판을 내야 합니다.",
            (15, 1888): "주변 세력을 보면 싸울 때는 아직 멀고,\n우리 가문은 지금 힘을 쌓아야 합니다.",
        }
        self.assertEqual({change.coordinate: change.target_literal for change in W93.CHANGES}, expected)
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W93.CHANGES},
            {
                (15, 1850): (840, 648),
                (15, 1851): (600, 768),
                (15, 1860): (888, 864),
                (15, 1888): (888, 864),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave92_identical(self) -> None:
        bundle = W93.prepare_candidate()
        self.assertEqual(
            W93.sha256_bytes(bundle.packed[W93.BASE_RESOURCE]),
            W93.INPUT_PROFILES[W93.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W93.sha256_bytes(bundle.packed[W93.PK_RESOURCE]),
            W93.TARGET_PROFILES[W93.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W93.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        self.assertEqual(bundle.audit["non_target_record_byte_identity"], "PASS")
        for row in bundle.audit["records"]:
            self.assertEqual(row["display_line_count"], 2)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(set(row["pc_source_anchor"]), set(W93.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W93.prepare_candidate()
        output = W93.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W93.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave92"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
