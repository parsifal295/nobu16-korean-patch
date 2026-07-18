#!/usr/bin/env python3
"""Regression tests for the private PC-only Wave 13 Base-event candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "build_pc_event_linebreak_wave13_candidate_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_event_linebreak_wave13", BUILDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load Wave13 builder: {BUILDER_PATH}")
WAVE13 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = WAVE13
SPEC.loader.exec_module(WAVE13)


class Wave13CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packed_a, cls.summary_a, cls.details_a = WAVE13.build()
        cls.packed_b, cls.summary_b, cls.details_b = WAVE13.build()

    def test_exact_scope_and_profile_contract(self) -> None:
        self.assertEqual(WAVE13.RESOURCE, "MSG/JP/ev_strdata.bin")
        self.assertEqual(WAVE13.candidate_ids(), (3280, 4066, 5299, 6960, 7380, 8140, 8350))
        self.assertEqual(self.summary_a["input"]["packed_sha256"], WAVE13.EXPECTED_INPUT_PACKED_SHA256)
        self.assertEqual(self.summary_a["output"]["packed_sha256"], WAVE13.EXPECTED_OUTPUT_PACKED_SHA256)
        self.assertEqual(self.summary_a["scope"]["changed_files"], 1)
        self.assertEqual(self.summary_a["scope"]["changed_logical_records"], 7)
        self.assertEqual(self.summary_a["scope"]["changed_ids"], list(WAVE13.candidate_ids()))
        self.assertEqual(WAVE13.sha256_bytes(self.packed_a), WAVE13.EXPECTED_OUTPUT_PACKED_SHA256)
        self.assertEqual(len(self.packed_a), WAVE13.EXPECTED_OUTPUT_PACKED_SIZE)

    def test_candidate_is_deterministic_and_candidate_only(self) -> None:
        self.assertEqual(self.packed_a, self.packed_b)
        self.assertEqual(
            json.dumps(self.summary_a, ensure_ascii=False, sort_keys=True),
            json.dumps(self.summary_b, ensure_ascii=False, sort_keys=True),
        )
        self.assertEqual(self.summary_a["output_policy"]["steam_apply_capability"], "absent")
        self.assertFalse(self.summary_a["output_policy"]["steam_game_resource_written"])
        self.assertFalse(self.summary_a["output_policy"]["git_stage_or_commit_written"])

    def test_only_seven_text_cells_change_and_opaque_header_survives(self) -> None:
        _input_packed, _header, _input_raw, before = WAVE13.load_source(WAVE13.DEFAULT_STEAM_ROOT)
        _out_header, out_raw = WAVE13.decompress_wrapper(self.packed_a)
        after = WAVE13.parse_message_table(out_raw)
        self.assertEqual(before.string_count, after.string_count)
        changed = tuple(index for index, pair in enumerate(zip(before.texts, after.texts)) if pair[0] != pair[1])
        self.assertEqual(changed, WAVE13.candidate_ids())
        for index, pair in enumerate(zip(before.texts, after.texts)):
            if index not in WAVE13.candidate_ids():
                self.assertEqual(pair[0], pair[1], index)
        self.assertEqual(WAVE13.opaque_header_digest(before), WAVE13.opaque_header_digest(after))
        self.assertTrue(self.details_a["input_opaque_header_digest"] == self.details_a["output_opaque_header_digest"])

    def test_protected_tags_opaque_text_controls_and_runtime_tokens_are_preserved(self) -> None:
        _input_packed, _header, _input_raw, before = WAVE13.load_source(WAVE13.DEFAULT_STEAM_ROOT)
        _out_header, out_raw = WAVE13.decompress_wrapper(self.packed_a)
        after = WAVE13.parse_message_table(out_raw)
        for candidate in WAVE13.CANDIDATES:
            with self.subTest(identifier=candidate.identifier):
                current = before.texts[candidate.identifier]
                target = after.texts[candidate.identifier]
                self.assertEqual(WAVE13.text_sha256(current), candidate.current_utf16le_sha256)
                self.assertEqual(WAVE13.text_sha256(target), candidate.target_utf16le_sha256)
                self.assertEqual(WAVE13.protected_profile(current), WAVE13.protected_profile(target))
                self.assertEqual(WAVE13.protected_profile(target)["esc"], [])
                self.assertEqual(WAVE13.protected_profile(target)["runtime_tokens"], [])
                self.assertEqual(WAVE13.protected_profile(target)["printf"], [])
                self.assertEqual(WAVE13.protected_profile(target)["controls"], [])
                self.assertEqual(WAVE13.protected_profile(target)["pua"], [])

    def test_manual_break_context_and_max_three_line_width_contract(self) -> None:
        expected_widths = {
            3280: [192, 840, 792],
            4066: [1008, 984, 984],
            5299: [1008, 696, 720],
            6960: [720, 744],
            7380: [912, 912, 672],
            8140: [960, 912, 216],
            8350: [888, 912, 744],
        }
        rows = {row["id"]: row for row in self.details_a["rows"]}
        self.assertEqual(set(rows), set(expected_widths))
        self.assertEqual(self.summary_a["layout_contract"]["max_target_lines"], 3)
        self.assertEqual(self.summary_a["layout_contract"]["empirical_base_event_max_line_px"], 1104)
        self.assertEqual(self.summary_a["layout_contract"]["preserved_manual_line_current_max_px"], 1104)
        for candidate in WAVE13.CANDIDATES:
            with self.subTest(identifier=candidate.identifier):
                row = rows[candidate.identifier]
                target_layout = row["layout"]["target"]
                self.assertEqual(target_layout["line_widths_px"], expected_widths[candidate.identifier])
                self.assertEqual(target_layout["line_count"], len(expected_widths[candidate.identifier]))
                self.assertLessEqual(target_layout["line_count"], WAVE13.MAX_LINES)
                self.assertLessEqual(target_layout["max_line_width_px"], WAVE13.EMPIRICAL_BASE_EVENT_MAX_LINE_PX)
                self.assertEqual(target_layout["fallback_codepoints"], [])
                self.assertTrue(row["linebreak"]["rationale"])
        for identifier in (7380, 8350):
            with self.subTest(restored_identifier=identifier):
                row = rows[identifier]
                self.assertEqual(row["linebreak"]["policy"], "restore_contextual_three_lines")
                self.assertEqual(row["linebreak"]["current_vector"], [])
                self.assertEqual(row["linebreak"]["target_vector"], ["\n", "\n"])
                self.assertEqual(row["linebreak"]["target_manual_line_count"], 3)
        for identifier in (3280, 4066, 5299, 6960, 8140):
            self.assertEqual(rows[identifier]["linebreak"]["policy"], "preserve_existing_breaks")

    def test_pristine_pc_japanese_anchor_and_switch_exclusion(self) -> None:
        evidence = WAVE13.validate_pristine_pc_japanese()
        self.assertEqual(evidence["platform"], "Steam PC")
        self.assertEqual(evidence["packed_sha256"], WAVE13.EXPECTED_PRISTINE_PC_JP_SHA256)
        self.assertFalse(evidence["switch_korean_translation_used"])
        self.assertEqual(set(evidence["coordinate_utf16le_sha256"]), {str(value) for value in WAVE13.candidate_ids()})
        self.assertNotIn("switch", str(WAVE13.PRISTINE_PC_JP_PATH).casefold())
        self.assertFalse(self.summary_a["provenance"]["switch_korean_translation_used"])
        self.assertFalse(self.summary_a["provenance"]["switch_korean_assets_read"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
