#!/usr/bin/env python3
"""Regression contracts for the private Wave 17 static-quality candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave17_static_quality_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave17", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE17 = load_builder()


class Wave17StaticQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live_profile = WAVE17.profile_hashes(WAVE17.DEFAULT_STEAM_ROOT)
        if cls.live_profile != WAVE17.INPUT_SHA256:
            raise RuntimeError(
                "Steam profile is not the unique Wave 15+16 plus Issue 61 input for Wave 17"
            )
        cls.output_a, cls.audit_a = WAVE17.prepare_candidate(WAVE17.DEFAULT_STEAM_ROOT)
        cls.output_b, cls.audit_b = WAVE17.prepare_candidate(WAVE17.DEFAULT_STEAM_ROOT)
        cls.before = WAVE17.records_by_coordinate(
            (WAVE17.DEFAULT_STEAM_ROOT / WAVE17.BASE_MSGGAME).read_bytes()
        )
        cls.after = WAVE17.records_by_coordinate(cls.output_a)

    def test_unique_wave15_plus_wave16_issue61_eleven_file_preimage(self) -> None:
        self.assertEqual(tuple(WAVE17.INPUT_SHA256), WAVE17.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE17.TARGET_SHA256), WAVE17.PROFILE_PATHS)
        self.assertEqual(self.live_profile, WAVE17.INPUT_SHA256)
        self.assertEqual(
            WAVE17.INPUT_SHA256[WAVE17.BASE_MSGGAME],
            "EEA622999F38C72F2088467E04D4A885B684D3FD3CF99FB72879A72079CF9351",
        )
        self.assertEqual(
            WAVE17.INPUT_SHA256[WAVE17.PK_MSGEV],
            "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3",
        )
        self.assertEqual(
            WAVE17.INPUT_SHA256[WAVE17.PK_MSGGAME],
            "9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC",
        )
        self.assertEqual(
            WAVE17.INPUT_SHA256["MSG/JP/strdata.bin"],
            "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
        )
        self.assertEqual(
            WAVE17.INPUT_SHA256["MSG_PK/JP/msgdata.bin"],
            "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
        )
        self.assertEqual(len(self.output_a), WAVE17.TARGET_BASE_PACKED_SIZE)
        self.assertEqual(
            WAVE17.sha256_bytes(self.output_a), WAVE17.TARGET_SHA256[WAVE17.BASE_MSGGAME]
        )

    def test_exact_three_static_literal_targets(self) -> None:
        self.assertEqual(
            [(change.coordinate, change.literal_id) for change in WAVE17.CHANGES],
            [((2, 489), 1), ((2, 519), 0), ((13, 328), 0)],
        )
        for change in WAVE17.CHANGES:
            with self.subTest(change=change.coordinate_text):
                before = self.before[change.coordinate]
                after = self.after[change.coordinate]
                self.assertEqual(
                    WAVE17.sha256_bytes(before.data), change.input_record_sha256
                )
                self.assertEqual(len(before.data), change.input_record_size)
                self.assertEqual(
                    tuple(WAVE17.text_sha256(value) for value in WAVE17.literal_texts(before)),
                    change.input_literal_utf16le_sha256,
                )
                self.assertEqual(
                    tuple(value.hex().upper() for value in WAVE17.opaque_spans(before)),
                    change.opaque_spans_hex,
                )
                self.assertEqual(
                    WAVE17.sha256_bytes(after.data), change.target_record_sha256
                )
                self.assertEqual(len(after.data), change.target_record_size)
                self.assertEqual(
                    tuple(WAVE17.text_sha256(value) for value in WAVE17.literal_texts(after)),
                    change.target_literal_utf16le_sha256,
                )
                self.assertEqual(WAVE17.opaque_spans(after), WAVE17.opaque_spans(before))
                self.assertEqual(WAVE17.marker_topology(after), WAVE17.marker_topology(before))
                self.assertTrue(after.data.endswith(WAVE17.RECORD_TERMINATOR))
                self.assertEqual(
                    "".join(WAVE17.literal_texts(after)).count("\n"),
                    "".join(WAVE17.literal_texts(before)).count("\n"),
                )

    def test_only_the_three_base_records_change(self) -> None:
        self.assertEqual(self.before.keys(), self.after.keys())
        changed = {
            coordinate
            for coordinate in self.before
            if self.before[coordinate].data != self.after[coordinate].data
        }
        self.assertEqual(changed, set(WAVE17.CHANGE_BY_COORDINATE))
        for coordinate, record in self.before.items():
            if coordinate not in changed:
                self.assertEqual(record.data, self.after[coordinate].data)
        WAVE17.validate_raw_roundtrip(self.output_a, "test Wave 17 candidate")

    def test_pc_anchors_and_font_metrics_are_pinned(self) -> None:
        anchors = WAVE17.validate_pc_anchors()
        self.assertEqual(set(anchors["reference_packed_sha256"]), {"JP", "SC", "TC"})
        self.assertEqual(set(anchors["records"]), {"2:489", "2:519", "13:328"})
        font = self.audit_a["font_layout"]["font"]
        self.assertEqual(font["packed_sha256"], WAVE17.FONT_SHA256)
        for change in WAVE17.CHANGES:
            with self.subTest(change=change.coordinate_text):
                layout = self.audit_a["font_layout"]["records"][change.coordinate_text]
                self.assertEqual(
                    tuple(layout["current"]["line_widths_px"]),
                    change.layout.current_widths_px,
                )
                self.assertEqual(
                    tuple(layout["target"]["line_widths_px"]),
                    change.layout.target_widths_px,
                )
                self.assertEqual(layout["target"]["wide_fallback_codepoints"], [])
                if change.layout.dialogue_limit_px is not None:
                    self.assertLessEqual(
                        layout["target"]["max_width_px"], change.layout.dialogue_limit_px
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
        self.assertTrue(policy["wave15_plus_wave16_issue61_successor_profile_required"])
        self.assertTrue(policy["pristine_pc_japanese_read"])
        self.assertTrue(policy["pc_sc_tc_context_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["git_operation"], "absent")
        self.assertEqual(policy["release_operation"], "absent")
        with self.assertRaises(WAVE17.Wave17Error):
            WAVE17.require_tmp(WAVE17.DEFAULT_STEAM_ROOT, "Steam path")


if __name__ == "__main__":
    unittest.main(verbosity=2)
