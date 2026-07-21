#!/usr/bin/env python3
"""Regression checks for the private Wave 98 block-13/14 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave98_blocks13_14_static_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("wave98_test_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W98 = load_builder()


class Wave98CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = W98.prepare_candidate()
        cls.audit = cls.bundle.audit
        cls.rows = {
            (row["resource"], row["coordinate"]): row
            for row in cls.audit["records"]
        }

    def test_exact_scope_is_five_records_and_five_literals(self) -> None:
        self.assertEqual(len(W98.CHANGES), 5)
        self.assertEqual(self.audit["changed_record_count"], 5)
        self.assertEqual(self.audit["changed_literal_slot_count"], 5)
        self.assertEqual(
            set(self.rows),
            {
                (W98.BASE_RESOURCE, "13:213"),
                (W98.PK_RESOURCE, "13:213"),
                (W98.PK_RESOURCE, "13:563"),
                (W98.PK_RESOURCE, "13:573"),
                (W98.PK_RESOURCE, "13:590"),
            },
        )

    def test_county_facility_rows_obey_fixed_person_contract(self) -> None:
        for resource in (W98.BASE_RESOURCE, W98.PK_RESOURCE):
            row = self.rows[(resource, "13:213")]
            self.assertEqual(row["layout_kind"], "fixed_person_3line_888px")
            self.assertEqual(
                row["target_layout_report"]["raw_g1n_line_widths_px"], [768, 672, 720]
            )
            self.assertEqual(row["target_layout_report"]["line_count"], 3)
            self.assertFalse(row["target_layout_report"]["any_line_exceeds_888px"])
            self.assertTrue(row["fixed_person_3line_888px_contract"]["applied"])
            self.assertTrue(row["fixed_person_3line_888px_contract"]["passes"])
            self.assertIn("성하 시설", row["target_record"]["visible_literals"][0])
            self.assertNotIn("가능해\n집니다", row["target_record"]["visible_literals"][0])

    def test_help_rows_preserve_manual_topology_and_require_ui_qa(self) -> None:
        expected = {
            "13:563": {"manual_line_count": 4, "blank_line_indexes_zero_based": [1]},
            "13:573": {"manual_line_count": 4, "blank_line_indexes_zero_based": [1]},
            "13:590": {"manual_line_count": 8, "blank_line_indexes_zero_based": [5]},
        }
        for coordinate, topology in expected.items():
            row = self.rows[(W98.PK_RESOURCE, coordinate)]
            self.assertEqual(row["layout_kind"], "tutorial_help_manual_lines_preserved")
            self.assertEqual(row["current_manual_layout"], row["target_manual_layout"])
            self.assertEqual(
                row["target_manual_layout"]["manual_line_count"], topology["manual_line_count"]
            )
            self.assertEqual(
                row["target_manual_layout"]["blank_line_indexes_zero_based"],
                topology["blank_line_indexes_zero_based"],
            )
            self.assertFalse(row["fixed_person_3line_888px_contract"]["applied"])
            self.assertTrue(
                row["fixed_person_3line_888px_contract"]["steam_pre_release_ui_qa_required"]
            )
        self.assertIn(
            "판단을 구해 오기도 합니다.",
            self.rows[(W98.PK_RESOURCE, "13:563")]["target_record"]["visible_literals"][0],
        )
        self.assertIn(
            "위풍이 발생합니다.",
            self.rows[(W98.PK_RESOURCE, "13:590")]["target_record"]["visible_literals"][0],
        )
        self.assertIn(
            "적 성의 배반이 일어나지 않습니다.",
            self.rows[(W98.PK_RESOURCE, "13:590")]["target_record"]["visible_literals"][0],
        )

    def test_control_structure_and_direct_locale_evidence_are_preserved(self) -> None:
        for key, row in self.rows.items():
            self.assertEqual(
                row["current_record"]["marker_topology_hex"],
                row["target_record"]["marker_topology_hex"],
                key,
            )
            self.assertEqual(
                row["current_record"]["opaque_spans_hex"],
                row["target_record"]["opaque_spans_hex"],
                key,
            )
            self.assertTrue(row["target_record"]["terminator"], key)
            self.assertEqual(row["target_record"]["complete_0143_commands"], [], key)
            self.assertEqual(row["target_record"]["runtime_02xx_opcodes"], [], key)
            context = row["direct_pc_jp_en_sc_tc_context"]
            if key[0] == W98.BASE_RESOURCE:
                self.assertTrue({"JP_BASE", "JP_PK", "EN", "SC", "TC"}.issubset(context))
                self.assertIn("cross_resource_locale_context", context)
            else:
                self.assertTrue({"JP_PK", "EN", "SC", "TC"}.issubset(context))

    def test_output_profiles_and_private_artifacts_are_pinned(self) -> None:
        self.assertEqual(dict(self.audit["target"]), dict(W98.TARGET_PROFILES))
        self.assertEqual(
            self.audit["source_policy"]["steam_game_resource_written"], False
        )
        self.assertEqual(self.audit["source_policy"]["git_operation"], "absent")
        self.assertEqual(self.audit["source_policy"]["network_operation"], "absent")
        self.assertEqual(self.audit["source_policy"]["release_operation"], "absent")

        output = W98.TMP_ROOT / "candidate"
        self.assertTrue(output.is_dir())
        self.assertTrue(output.resolve().is_relative_to(W98.TMP_ROOT.resolve()))
        self.assertEqual(
            (output / "audit.v1.json").read_bytes(), W98.canonical_json(self.bundle.audit)
        )
        self.assertEqual(
            (output / "build_manifest.v1.json").read_bytes(),
            W98.canonical_json(self.bundle.manifest),
        )
        disk_manifest = json.loads((output / "build_manifest.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(disk_manifest["changed_literal_slot_count"], 5)


if __name__ == "__main__":
    unittest.main()
