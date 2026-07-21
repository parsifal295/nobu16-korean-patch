#!/usr/bin/env python3
"""Contract tests for the private Wave 95 PK court-and-assignment candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave95_pk_court_assignment_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave95_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 95 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W95 = load_builder()


class Wave95CourtAssignmentTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_static_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W95.CHANGES],
            [(6, 4253), (6, 4441), (6, 4507), (6, 4511)],
        )
        self.assertEqual(len({change.coordinate for change in W95.CHANGES}), 4)
        for change in W95.CHANGES:
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W95.PC_SOURCE_FILE_SHA256))
            self.assertEqual(change.target_literal.count("\n"), 1)

    def test_targets_preserve_full_meaning_and_semantic_two_line_layouts(self) -> None:
        self.assertEqual(
            {change.coordinate: change.target_literal for change in W95.CHANGES},
            {
                (6, 4253): "조정의 후원을 얻기 위해\n빈틈없이 교섭하겠습니다.",
                (6, 4441): "그렇군요…\n상황에 맞춰 적절히 처리하겠습니다.",
                (6, 4507): "오랜 세월 이 가문에서 갈고닦은 역량을\n마음껏 발휘하겠습니다.",
                (6, 4511): "그곳은 가까운 곳이니\n당장이라도 부임할 수 있습니다.",
            },
        )
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W95.CHANGES},
            {
                (6, 4253): (552, 576),
                (6, 4441): (240, 816),
                (6, 4507): (888, 528),
                (6, 4511): (480, 720),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave94_identical(self) -> None:
        bundle = W95.prepare_candidate()
        self.assertEqual(
            W95.sha256_bytes(bundle.packed[W95.BASE_RESOURCE]),
            W95.INPUT_PROFILES[W95.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W95.sha256_bytes(bundle.packed[W95.PK_RESOURCE]),
            W95.TARGET_PROFILES[W95.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W95.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertEqual(bundle.audit["source_policy"]["sentence_shortening"], "forbidden")
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        self.assertEqual(bundle.audit["non_target_record_byte_identity"], "PASS")
        for row in bundle.audit["records"]:
            self.assertEqual(row["display_line_count"], 2)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(set(row["pc_source_anchor"]), set(W95.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)
            self.assertEqual(
                row["manual_line_break_policy"],
                "preserved semantic two-line layout without sentence shortening",
            )

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W95.prepare_candidate()
        output = W95.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W95.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave94"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
