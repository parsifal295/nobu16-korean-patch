#!/usr/bin/env python3
"""Regression tests for the read-only B17 v3 pre-applied coverage audit."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("audit_pc_dialogue_b17_direct_static_quality_v3.py")


def load_module() -> object:
    spec = importlib.util.spec_from_file_location("b17_v3_test_module", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load B17 v3 audit module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B17 = load_module()


class B17PreAppliedCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit, cls.manifest = B17.prepare_artifacts()

    def test_exact_44_static_rows_are_already_present(self) -> None:
        self.assertEqual(self.audit["pre_applied_verified_literal_count"], 44)
        self.assertEqual(self.audit["pre_applied_verified_record_count"], 44)
        self.assertEqual(self.audit["missing_static_literal_count"], 0)
        self.assertEqual(self.audit["binary_replacement_count"], 0)
        self.assertEqual(self.audit["scope"]["static_high_confidence_count_by_resource"], {
            B17.BASE_RESOURCE: 4,
            B17.PK_RESOURCE: 40,
        })
        self.assertEqual(self.audit["scope"]["missing_static_slots"], [])
        self.assertEqual(self.audit["scope"]["binary_replacement_slots_required"], [])
        self.assertEqual(
            self.audit["scope"]["expected_static_slots"],
            self.audit["scope"]["pre_applied_verified_slots"],
        )

    def test_every_row_is_static_and_preserves_its_structure(self) -> None:
        for row in self.audit["records"]:
            self.assertTrue(row["pre_applied"], row["slot"])
            self.assertEqual(row["strict_wave97_ko"], row["expected_static_target_ko"], row["slot"])
            self.assertNotEqual(row["strict_wave97_ko"], row["historical_preimage_ko"], row["slot"])
            self.assertTrue(row["opaque_skeleton_preserved"], row["slot"])
            self.assertTrue(row["token_marker_topology_preserved"], row["slot"])
            self.assertTrue(row["terminator_tail_preserved"], row["slot"])
            self.assertTrue(row["line_count_preserved_from_historical_preimage"], row["slot"])
            self.assertTrue(row["strict_width_preserved_exactly_as_expected_target"], row["slot"])
            self.assertEqual(
                row["historical_preimage_layout"]["manual_line_break_count"],
                row["strict_wave97_layout"]["manual_line_break_count"],
                row["slot"],
            )
            self.assertEqual(
                row["direct_pc_jp"],
                row["direct_pc_evidence"]["JP"]["literal_index_text"],
                row["slot"],
            )

    def test_runtime_color_and_global_lf_scope_are_excluded(self) -> None:
        selected = set(self.audit["scope"]["pre_applied_verified_slots"])
        holds = set(self.audit["excluded_holds"]["all_slots"])
        self.assertTrue(selected.isdisjoint(holds))
        self.assertIn(f"{B17.PK_RESOURCE}:17:282:0", self.audit["excluded_holds"]["color_blue"])
        for required in (
            f"{B17.PK_RESOURCE}:17:226:0",
            f"{B17.PK_RESOURCE}:17:510:0",
            f"{B17.PK_RESOURCE}:17:920:0",
        ):
            self.assertIn(required, self.audit["excluded_holds"]["runtime_name_or_particle"])
        lf = self.audit["excluded_holds"]["global_manual_lf"]
        self.assertTrue(lf["excluded"])
        self.assertEqual(lf["b17_literal_with_lf_count"], 839)
        self.assertEqual(lf["b17_total_lf_count"], 849)
        self.assertTrue(lf["direct_pc_jp_topology_match"])
        layout_holds = self.audit["excluded_holds"]["preexisting_layout_warning_holds"]
        self.assertFalse(layout_holds["binary_change_allowed_in_this_artifact"])
        self.assertEqual(len(layout_holds["slots"]), 6)

    def test_direct_pc_jp_en_sc_tc_evidence_has_explicit_base_en_boundary(self) -> None:
        for row in self.audit["records"]:
            evidence = row["direct_pc_evidence"]
            self.assertEqual(set(evidence), {"JP", "EN", "SC", "TC"})
            self.assertTrue(evidence["JP"]["available"], row["slot"])
            if row["resource"] == B17.BASE_RESOURCE:
                self.assertFalse(evidence["EN"]["available"], row["slot"])
                self.assertIn("not substituted", evidence["EN"]["reason"])
            else:
                for language in ("EN", "SC", "TC"):
                    self.assertTrue(evidence[language]["available"], f"{row['slot']} {language}")
                    self.assertIn("record_sha256", evidence[language])

    def test_complete_b17_topology_and_lf_census_match_direct_pc_jp(self) -> None:
        expected = {
            B17.BASE_RESOURCE: (33, 66, 25, 25),
            B17.PK_RESOURCE: (1159, 2256, 814, 824),
        }
        for resource, (records, literals, lf_literals, lfs) in expected.items():
            report = self.audit["complete_b17_topology"][resource]
            self.assertEqual(report["record_count"], records)
            self.assertEqual(report["literal_count"], literals)
            self.assertEqual(report["literal_with_manual_lf_count"], lf_literals)
            self.assertEqual(report["manual_lf_total"], lfs)
            self.assertTrue(report["opaque_skeleton_all_records_match_direct_pc_jp"])
            self.assertTrue(report["marker_topology_all_records_match_direct_pc_jp"])
            self.assertTrue(report["terminator_tail_all_records_match_direct_pc_jp"])
            self.assertTrue(report["manual_lf_topology_all_literals_match_direct_pc_jp"])

    def test_preexisting_overwidth_is_recorded_without_reflow_or_shortening(self) -> None:
        review = self.audit["layout_review"]
        self.assertTrue(review["strict_input_widths_preserved_without_reflow"])
        self.assertEqual(review["preexisting_overwidth_row_count"], 6)
        self.assertEqual(
            [(item["resource"], item["slot"]) for item in review["preexisting_overwidth_rows"]],
            [
                (B17.PK_RESOURCE, "17:54:0"),
                (B17.PK_RESOURCE, "17:504:0"),
                (B17.PK_RESOURCE, "17:852:0"),
                (B17.PK_RESOURCE, "17:971:0"),
                (B17.PK_RESOURCE, "17:1073:0"),
                (B17.PK_RESOURCE, "17:1093:0"),
            ],
        )
        self.assertIn("does not shorten text", review["disposition"])

    def test_checked_in_artifacts_are_exact_and_no_binary_writer_exists(self) -> None:
        result = B17.verify_artifacts()
        self.assertEqual(result["pre_applied_verified_literal_count"], 44)
        self.assertEqual(result["missing_static_literal_count"], 0)
        self.assertEqual(result["binary_replacement_count"], 0)
        self.assertFalse(result["candidate_binary_created"])
        self.assertFalse(result["steam_game_resource_written"])
        source = BUILDER.read_text(encoding="utf-8")
        self.assertNotIn("write_bytes", source)
        self.assertNotIn("os.replace", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
