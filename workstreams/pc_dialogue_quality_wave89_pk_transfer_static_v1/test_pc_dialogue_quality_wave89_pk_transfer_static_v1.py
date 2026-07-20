#!/usr/bin/env python3
"""Contract tests for the private Wave 89 PK reassignment candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave89_pk_transfer_static_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave89_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 89 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W89 = load_builder()


class Wave89StaticTransferTests(unittest.TestCase):
    def test_scope_is_exactly_four_fixed_pk_reassignment_records(self) -> None:
        self.assertEqual(
            [change.coordinate for change in W89.CHANGES],
            [(15, 2319), (15, 2320), (15, 2322), (15, 2323)],
        )
        self.assertEqual(len({change.coordinate for change in W89.CHANGES}), 4)
        for change in W89.CHANGES:
            self.assertEqual(change.target_literal.count("\n"), 2)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(set(change.source_record_sha256), set(W89.PC_SOURCE_FILE_SHA256))

    def test_frontline_and_rear_targets_are_exact_and_within_layout_cap(self) -> None:
        expected = {
            (15, 2319): "설마 소망이 이뤄질 줄이야…\n전선에서 무용을 떨치며\n더욱 충성을 다하겠습니다.",
            (15, 2320): "진작부터 바라던 전선의 영지\n이 한 몸 바쳐 다스리고 지키며\n화려한 전공을 세우겠습니다.",
            (15, 2322): "설마 소망이 이뤄질 줄이야…\n후방에서 정무 솜씨를 발휘하여\n더욱 충성을 다하겠습니다.",
            (15, 2323): "진작부터 바라던 후방의 영지\n이 한 몸 바쳐 다스리고 지키며\n착실한 성과를 보여 드리겠습니다.",
        }
        self.assertEqual({change.coordinate: change.target_literal for change in W89.CHANGES}, expected)
        self.assertEqual(
            {change.coordinate: change.target_raw_g1n_line_widths_px for change in W89.CHANGES},
            {
                (15, 2319): (648, 528, 600),
                (15, 2320): (648, 696, 648),
                (15, 2322): (648, 696, 600),
                (15, 2323): (648, 696, 768),
            },
        )

    def test_prepare_candidate_is_surgical_and_base_remains_wave88_identical(self) -> None:
        bundle = W89.prepare_candidate()
        self.assertEqual(
            W89.sha256_bytes(bundle.packed[W89.BASE_RESOURCE]),
            W89.INPUT_PROFILES[W89.BASE_RESOURCE]["sha256"],
        )
        self.assertEqual(
            W89.sha256_bytes(bundle.packed[W89.PK_RESOURCE]),
            W89.TARGET_PROFILES[W89.PK_RESOURCE]["sha256"],
        )
        self.assertEqual(bundle.audit["changed_record_count"], 4)
        self.assertEqual(bundle.manifest["resources"][W89.BASE_RESOURCE]["changed_coordinates"], [])
        self.assertFalse(bundle.audit["source_policy"]["steam_game_resource_written"])
        baseline = bundle.audit["source_policy"]["layout_baseline"]
        self.assertEqual(baseline["max_lines"], 3)
        self.assertEqual(baseline["max_raw_g1n_line_width_px"], 888)
        self.assertEqual(baseline["event_msgev_30px_4line_rule"], "not applied")
        self.assertEqual(bundle.audit["non_target_record_byte_identity"], "PASS")
        for row in bundle.audit["records"]:
            self.assertEqual(row["display_line_count"], 3)
            self.assertFalse(row["target_any_static_person_dialogue_line_exceeds_888px"])
            self.assertEqual(set(row["pc_source_anchor"]), set(W89.PC_SOURCE_FILE_SHA256))
            self.assertIn("semantic_repair", row)

    def test_private_build_and_verify_are_candidate_only(self) -> None:
        bundle = W89.prepare_candidate()
        output = W89.write_candidate(bundle)
        self.assertTrue(output.is_dir())
        result = W89.verify_private()
        self.assertEqual(result["changed_record_count"], 4)
        self.assertTrue(result["base_byte_identical_from_wave88"])
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
