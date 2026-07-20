#!/usr/bin/env python3
"""Contract tests for the private Wave 91 PK regional-commentary candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave91_pk_regional_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave91_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 91 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W91 = load_builder()


class Wave91StaticRegionalTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_regional_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W91.CHANGES],
            [(15, 1620), (15, 1621), (15, 1625), (15, 1626)],
        )
        self.assertEqual(len({change.coordinate for change in W91.CHANGES}), 4)
        for change in W91.CHANGES:
            self.assertEqual(change.target_literal.count("\n"), 2)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W91.PC_SOURCE_FILE_SHA256))

    def test_regional_targets_and_semantic_three_line_reflows_are_exact(self) -> None:
        expected = {
            (15, 1620): "사가미는 가마쿠라 도노의 치세부터,\n무가에게 특별한 의미를 지닌 요충지\n모두의 사기도 오를 것입니다.",
            (15, 1621): "남북으로 긴 신슈를 한 다이묘 가문이\n다스림은 무가의 세상이 된 뒤로\n모두의 사기를 높일 드문 위업입니다.",
            (15, 1625): "셋쓰는 내해를 배로 실어 온 산물과\n교에서 내려온 짐이 거래되는\n교역상의 요지입니다.",
            (15, 1626): "옛 도읍이자, 지금도 많은 상인이\n모이는 남도를 품은 야마토국을 제압한\n의미는 크다고 하겠습니다.",
        }
        self.assertEqual({change.coordinate: change.target_literal for change in W91.CHANGES}, expected)
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W91.CHANGES},
            {
                (15, 1620): (816, 816, 672),
                (15, 1621): (840, 720, 840),
                (15, 1625): (792, 648, 480),
                (15, 1626): (744, 864, 600),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave90_identical(self) -> None:
        bundle = W91.prepare_candidate()
        self.assertEqual(
            W91.sha256_bytes(bundle.packed[W91.BASE_RESOURCE]),
            W91.INPUT_PROFILES[W91.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W91.sha256_bytes(bundle.packed[W91.PK_RESOURCE]),
            W91.TARGET_PROFILES[W91.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W91.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        self.assertEqual(bundle.audit["non_target_record_byte_identity"], "PASS")
        for row in bundle.audit["records"]:
            self.assertEqual(row["display_line_count"], 3)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(set(row["pc_source_anchor"]), set(W91.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W91.prepare_candidate()
        output = W91.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W91.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave90"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
