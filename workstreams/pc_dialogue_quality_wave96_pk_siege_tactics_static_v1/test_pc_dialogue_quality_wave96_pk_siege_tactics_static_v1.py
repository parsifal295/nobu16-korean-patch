#!/usr/bin/env python3
"""Contract tests for the private Wave 96 PK siege-tactics candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave96_pk_siege_tactics_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave96_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 96 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W96 = load_builder()


class Wave96SiegeTacticsTests(unittest.TestCase):
    def test_scope_is_exactly_five_fixed_pk_static_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W96.CHANGES],
            [(9, 3987), (9, 3989), (9, 3990), (9, 3991), (9, 3992)],
        )
        self.assertEqual(len({change.coordinate for change in W96.CHANGES}), 5)
        for change in W96.CHANGES:
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W96.PC_SOURCE_FILE_SHA256))
            self.assertEqual(change.target_literal.count("\n"), 1)

    def test_targets_preserve_full_meaning_and_semantic_two_line_layouts(self) -> None:
        self.assertEqual(
            {change.coordinate: change.target_literal for change in W96.CHANGES},
            {
                (9, 3987): "퇴로를 파괴하는 것이야말로\n승리로 가는 지름길입니다.",
                (9, 3989): "요충지를 많이 제압하여\n지리의 이점을 얻도록 합시다.",
                (9, 3990): "수비를 중시하여\n견실하게 싸웁시다.",
                (9, 3991): "맞설 만한 적수와 싸울 날을\n벌써부터 기다릴 수 없군.",
                (9, 3992): "고전 중인 아군이 있으면\n즉시 지원하겠습니다.",
            },
        )
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W96.CHANGES},
            {
                (9, 3987): (624, 600),
                (9, 3989): (528, 672),
                (9, 3990): (360, 432),
                (9, 3991): (624, 576),
                (9, 3992): (552, 480),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave95_identical(self) -> None:
        bundle = W96.prepare_candidate()
        self.assertEqual(
            W96.sha256_bytes(bundle.packed[W96.BASE_RESOURCE]),
            W96.INPUT_PROFILES[W96.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W96.sha256_bytes(bundle.packed[W96.PK_RESOURCE]),
            W96.TARGET_PROFILES[W96.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 5)
        self.assertEqual(bundle.manifest["resources"][W96.BASE_RESOURCE]["changed_coordinates"], [])
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
            self.assertEqual(set(row["pc_source_anchor"]), set(W96.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)
            self.assertEqual(
                row["manual_line_break_policy"],
                "preserved semantic two-line layout without sentence shortening",
            )

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W96.prepare_candidate()
        output = W96.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W96.verify_private()
        self.assertEqual(result["changed_record_count"], 5)
        self.assertTrue(result["base_byte_identical_from_wave95"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
