#!/usr/bin/env python3
"""Regression checks for the read-only msgstf_ce credits audit."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "build_msgstf_ce_credits_audit.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("msgstf_ce_credits_audit_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import credits audit builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MsgStfCeCreditsAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()

    def test_all_language_tables_have_the_expected_credits_page_slots(self) -> None:
        value = self.builder.verify()
        variants = value["language_variants"]
        self.assertEqual(set(variants), {"JP", "EN", "SC", "TC"})
        for language, row in variants.items():
            with self.subTest(language=language):
                self.assertEqual(row["string_count"], 20)
                self.assertEqual(row["nonempty_ids"], list(range(8)))
                self.assertEqual(row["empty_ids"], list(range(8, 20)))
                self.assertEqual(row["nonempty_multiline_page_count"], 8)
                self.assertEqual(row["container"], "raw-lz4-single-message-table")

    def test_cross_language_findings_do_not_claim_a_safe_transplant(self) -> None:
        value = self.builder.verify()
        structure = value["cross_language_structure"]
        self.assertTrue(structure["all_languages_same_string_count"])
        self.assertTrue(structure["all_languages_same_nonempty_slot_vector"])
        self.assertTrue(structure["sc_tc_raw_payload_identical"])
        self.assertFalse(structure["automatic_cross_language_transplant_safe"])
        self.assertEqual(
            structure["jp_to_other_format_comparisons"]["EN"]["format_mismatch_entry_ids"],
            [5, 6],
        )
        self.assertEqual(
            structure["jp_to_other_format_comparisons"]["SC"]["format_mismatch_entry_ids"],
            [5],
        )
        self.assertEqual(
            structure["jp_to_other_format_comparisons"]["TC"]["format_mismatch_entry_ids"],
            [5],
        )

    def test_runtime_and_candidate_boundary_are_explicitly_unproven_and_excluded(self) -> None:
        value = self.builder.verify()
        route = value["static_runtime_route_evidence"]
        candidate = value["candidate_boundary"]
        decision = value["decision"]
        self.assertFalse(route["runtime_file_open_trace_completed"])
        self.assertFalse(route["runtime_file_open_proven"])
        self.assertFalse(candidate["resource_in_v5_candidate_paths"])
        self.assertFalse(decision["translation_module_created"])
        self.assertEqual(
            decision["next_candidate_inclusion"],
            "exclude_pending_runtime_file_open_trace_and_ending_screen_validation",
        )

    def test_tracked_public_audit_is_source_free_and_read_only(self) -> None:
        before = {
            language: self.builder.path_spec(
                self.builder.resource_path(self.builder.DEFAULT_STEAM_ROOT, language)
            )
            for language in self.builder.LANGUAGES
        }
        value = json.loads(self.builder.AUDIT_PATH.read_text(encoding="utf-8"))
        self.builder.assert_source_free(value, "test tracked audit")
        self.assertFalse(value["safety"]["installed_game_files_modified"])
        self.assertFalse(value["safety"]["candidate_v5_modified"])
        after = {
            language: self.builder.path_spec(
                self.builder.resource_path(self.builder.DEFAULT_STEAM_ROOT, language)
            )
            for language in self.builder.LANGUAGES
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
