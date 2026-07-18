#!/usr/bin/env python3
"""Regression contracts for the private Wave 21 static-quality candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave21_static_quality_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave21", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE21 = load_builder()


class Wave21StaticQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.predecessor_profile = WAVE21.profile_hashes(WAVE21.PREDECESSOR_CANDIDATE_ROOT)
        if cls.predecessor_profile != WAVE21.INPUT_SHA256:
            raise RuntimeError("Wave 19 candidate is not the exact pinned Wave 21 predecessor")
        cls.output_a, cls.audit_a = WAVE21.prepare_candidate(WAVE21.PREDECESSOR_CANDIDATE_ROOT)
        cls.output_b, cls.audit_b = WAVE21.prepare_candidate(WAVE21.PREDECESSOR_CANDIDATE_ROOT)
        cls.before = WAVE21.records_by_coordinate(
            (WAVE21.PREDECESSOR_CANDIDATE_ROOT / WAVE21.PK_MSGGAME).read_bytes()
        )
        cls.after = WAVE21.records_by_coordinate(cls.output_a)

    def test_unique_wave19_eleven_file_preimage_and_issue61_preservation(self) -> None:
        self.assertEqual(tuple(WAVE21.INPUT_SHA256), WAVE21.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE21.TARGET_SHA256), WAVE21.PROFILE_PATHS)
        self.assertEqual(self.predecessor_profile, WAVE21.INPUT_SHA256)
        self.assertEqual(
            WAVE21.INPUT_SHA256[WAVE21.BASE_MSGGAME],
            "C00B78165B06A5A9D2BFBE134E847E4B00EC3E5243EE9A1981BA1BB68CFA79C6",
        )
        self.assertEqual(
            WAVE21.INPUT_SHA256[WAVE21.PK_MSGGAME],
            "7D7826A575E4BA80FEE1E4FE920CBD7E16A48F0DA529D06514EDB59B11422FBC",
        )
        self.assertEqual(
            WAVE21.INPUT_SHA256["MSG/JP/strdata.bin"],
            "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
        )
        self.assertEqual(
            WAVE21.INPUT_SHA256["MSG_PK/JP/msgdata.bin"],
            "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
        )
        self.assertEqual(len(self.output_a), WAVE21.TARGET_PK_PACKED_SIZE)
        self.assertEqual(
            WAVE21.sha256_bytes(self.output_a), WAVE21.TARGET_SHA256[WAVE21.PK_MSGGAME]
        )
        for relative in WAVE21.PROFILE_PATHS:
            if relative != WAVE21.PK_MSGGAME:
                self.assertEqual(WAVE21.TARGET_SHA256[relative], WAVE21.INPUT_SHA256[relative])

    def test_exact_two_pk_literal_targets_preserve_record_structure(self) -> None:
        self.assertEqual(
            [(change.coordinate, change.literal_id) for change in WAVE21.CHANGES],
            [((2, 249), 1), ((2, 321), 1)],
        )
        for change in WAVE21.CHANGES:
            with self.subTest(change=change.coordinate_text):
                before = self.before[change.coordinate]
                after = self.after[change.coordinate]
                before_literals = WAVE21.literal_texts(before)
                after_literals = WAVE21.literal_texts(after)
                self.assertEqual(WAVE21.sha256_bytes(before.data), change.input_record_sha256)
                self.assertEqual(len(before.data), change.input_record_size)
                self.assertEqual(
                    tuple(WAVE21.text_sha256(value) for value in before_literals),
                    change.input_literal_utf16le_sha256,
                )
                self.assertEqual(
                    tuple(value.hex().upper() for value in WAVE21.opaque_spans(before)),
                    change.opaque_spans_hex,
                )
                self.assertEqual(WAVE21.sha256_bytes(after.data), change.target_record_sha256)
                self.assertEqual(len(after.data), change.target_record_size)
                self.assertEqual(
                    tuple(WAVE21.text_sha256(value) for value in after_literals),
                    change.target_literal_utf16le_sha256,
                )
                self.assertEqual(after_literals[change.literal_id], change.target_literal)
                for literal_id, value in enumerate(before_literals):
                    if literal_id != change.literal_id:
                        self.assertEqual(after_literals[literal_id], value)
                self.assertEqual(WAVE21.opaque_spans(after), WAVE21.opaque_spans(before))
                self.assertEqual(WAVE21.marker_topology(after), WAVE21.marker_topology(before))
                self.assertTrue(after.data.endswith(WAVE21.RECORD_TERMINATOR))
                self.assertEqual(
                    tuple(WAVE21.text_format_signature(value) for value in after_literals),
                    tuple(WAVE21.text_format_signature(value) for value in before_literals),
                )

    def test_only_two_pk_records_change(self) -> None:
        self.assertEqual(self.before.keys(), self.after.keys())
        changed = {
            coordinate
            for coordinate in self.before
            if self.before[coordinate].data != self.after[coordinate].data
        }
        self.assertEqual(changed, set(WAVE21.CHANGE_BY_COORDINATE))
        for coordinate, record in self.before.items():
            if coordinate not in changed:
                self.assertEqual(record.data, self.after[coordinate].data)
        WAVE21.validate_raw_roundtrip(self.output_a, "test Wave 21 candidate")

    def test_pc_jp_en_sc_tc_anchors_and_font_metrics_are_pinned(self) -> None:
        anchors = WAVE21.validate_pc_anchors()
        self.assertEqual(
            set(anchors["reference_packed_sha256"]), {"JP", "EN", "SC", "TC"}
        )
        self.assertEqual(set(anchors["records"]), {"2:249", "2:321"})
        font = self.audit_a["font_layout"]["font"]
        self.assertEqual(font["packed_sha256"], WAVE21.FONT_SHA256)
        for change in WAVE21.CHANGES:
            with self.subTest(change=change.coordinate_text):
                layout = self.audit_a["font_layout"]["records"][change.coordinate_text]
                self.assertEqual(
                    tuple(layout["current"]["line_widths_px"]), change.current_widths_px
                )
                self.assertEqual(
                    tuple(layout["target"]["line_widths_px"]), change.target_widths_px
                )
                self.assertEqual(layout["target"]["wide_fallback_codepoints"], [])
                if change.target_max_line_px is not None:
                    self.assertLessEqual(
                        layout["target"]["max_width_px"], change.target_max_line_px
                    )
                else:
                    self.assertEqual(
                        layout["current"]["line_widths_px"],
                        layout["target"]["line_widths_px"],
                    )

    def test_deterministic_candidate_and_no_steam_writer(self) -> None:
        self.assertEqual(self.output_a, self.output_b)
        self.assertEqual(
            json.dumps(self.audit_a, ensure_ascii=False, sort_keys=True),
            json.dumps(self.audit_b, ensure_ascii=False, sort_keys=True),
        )
        policy = self.audit_a["source_policy"]
        self.assertTrue(policy["wave19_full_profile_required"])
        self.assertTrue(policy["issue61_strdata_msgdata_preserved"])
        self.assertTrue(policy["pristine_pc_japanese_read"])
        self.assertTrue(policy["pc_en_sc_tc_context_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["git_operation"], "absent")
        self.assertEqual(policy["release_operation"], "absent")
        with self.assertRaises(WAVE21.Wave21Error):
            WAVE21.require_tmp(WAVE21.DEFAULT_STEAM_ROOT, "Steam path")


if __name__ == "__main__":
    unittest.main(verbosity=2)
