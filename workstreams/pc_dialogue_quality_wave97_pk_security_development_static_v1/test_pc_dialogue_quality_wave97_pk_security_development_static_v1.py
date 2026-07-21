#!/usr/bin/env python3
"""Contract tests for the private Wave 97 PK security-and-development candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave97_pk_security_development_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave97_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 97 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W97 = load_builder()


class Wave97SecurityDevelopmentTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_static_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W97.CHANGES],
            [(8, 982), (8, 983), (8, 1012), (8, 1036)],
        )
        self.assertEqual(len({change.coordinate for change in W97.CHANGES}), 4)
        for change in W97.CHANGES:
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W97.PC_SOURCE_FILE_SHA256))
            self.assertEqual(change.target_literal.count("\n"), 1)

    def test_targets_preserve_full_meaning_and_semantic_two_line_layouts(self) -> None:
        self.assertEqual(
            {change.coordinate: change.target_literal for change in W97.CHANGES},
            {
                (8, 982): "필요하다면 간자 놈들을 쫓아내도록\n출병 명령을 내리십시오.",
                (8, 983): "병사를 내어 간자를 몰아내면\n조략을 미연에 막을 수 있습니다.",
                (8, 1012): "이 땅을 풍요롭게 하기 위해\n미력하나마 진력하겠습니다.",
                (8, 1036): "군이 안정되었으니\n석고도 늘어날 것입니다.",
            },
        )
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W97.CHANGES},
            {
                (8, 982): (792, 552),
                (8, 983): (648, 744),
                (8, 1012): (624, 624),
                (8, 1036): (408, 552),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave96_identical(self) -> None:
        bundle = W97.prepare_candidate()
        self.assertEqual(
            W97.sha256_bytes(bundle.packed[W97.BASE_RESOURCE]),
            W97.INPUT_PROFILES[W97.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W97.sha256_bytes(bundle.packed[W97.PK_RESOURCE]),
            W97.TARGET_PROFILES[W97.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W97.BASE_RESOURCE]["changed_coordinates"], [])
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
            self.assertEqual(set(row["pc_source_anchor"]), set(W97.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)
            self.assertEqual(
                row["manual_line_break_policy"],
                "preserved semantic two-line layout without sentence shortening",
            )

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W97.prepare_candidate()
        output = W97.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W97.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave96"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
