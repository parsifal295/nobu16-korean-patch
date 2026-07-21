#!/usr/bin/env python3
"""Contract tests for the private Wave 88 PK person-dialogue candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave88_pk_obedience_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave88_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 88 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W88 = load_builder()


class Wave88StaticPersonDialogueTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_block8_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W88.CHANGES],
            [(8, 398), (8, 1022), (8, 1233), (8, 1235)],
        )
        self.assertEqual(len({change.coordinate for change in W88.CHANGES}), 4)
        for change in W88.CHANGES:
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W88.PC_SOURCE_FILE_SHA256))

    def test_semantic_targets_and_manual_line_breaks_are_exact(self) -> None:
        expected = {
            (8, 398): "명령이라면 따르겠습니다.",
            (8, 1022): "내 지혜로 성을 다스리고\n적을 타도할 방도를 세워\n가문 패업의 초석이 되겠습니다.",
            (8, 1233): "영내가 황폐해져, 피해를 입은 군에서는\n문제가 일어날지도 모릅니다.",
            (8, 1235): "…명령이라면, 따르겠습니다.",
        }
        self.assertEqual({change.coordinate: change.target_literal for change in W88.CHANGES}, expected)
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W88.CHANGES},
            {(8, 398): (576,), (8, 1022): (552, 552, 720), (8, 1233): (888, 648), (8, 1235): (648,)},
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave87_identical(self) -> None:
        bundle = W88.prepare_candidate()
        self.assertEqual(
            W88.sha256_bytes(bundle.packed[W88.BASE_RESOURCE]),
            W88.INPUT_PROFILES[W88.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W88.sha256_bytes(bundle.packed[W88.PK_RESOURCE]),
            W88.TARGET_PROFILES[W88.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W88.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        self.assertEqual(bundle.audit["non_target_record_byte_identity"], "PASS")
        for row in bundle.audit["records"]:
            self.assertLessEqual(row["display_line_count"], 3)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(set(row["pc_source_anchor"]), set(W88.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W88.prepare_candidate()
        output = W88.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W88.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave87"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
