#!/usr/bin/env python3
"""Regression contracts for the private PC-only Wave 25 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave25_static_consistency_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave25", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE25 = load_builder()


class Wave25StaticConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        WAVE25.validate_wave24_preimage(WAVE25.PREDECESSOR_CANDIDATE_ROOT)
        cls.before_packed = (WAVE25.PREDECESSOR_CANDIDATE_ROOT / WAVE25.PK_MSGGAME).read_bytes()
        cls.before = WAVE25.records_by_coordinate(cls.before_packed)
        cls.output_a, cls.audit_a = WAVE25.prepare_candidate(WAVE25.PREDECESSOR_CANDIDATE_ROOT)
        cls.output_b, cls.audit_b = WAVE25.prepare_candidate(WAVE25.PREDECESSOR_CANDIDATE_ROOT)
        cls.after = WAVE25.records_by_coordinate(cls.output_a)

    def test_exact_wave24_eleven_file_preimage_and_evidence(self) -> None:
        hashes, sizes = WAVE25.profile(WAVE25.PREDECESSOR_CANDIDATE_ROOT)
        self.assertEqual(hashes, WAVE25.INPUT_SHA256)
        self.assertEqual(sizes, WAVE25.INPUT_SIZES)
        self.assertEqual(tuple(WAVE25.INPUT_SHA256), WAVE25.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE25.TARGET_SHA256), WAVE25.PROFILE_PATHS)
        for item in WAVE25.WAVE24_EVIDENCE.values():
            path = Path(item["path"])
            self.assertEqual(path.stat().st_size, item["size"])
            self.assertEqual(WAVE25.sha256_path(path), item["sha256"])
        self.assertEqual(
            WAVE25.INPUT_SHA256["MSG_PK/JP/msgev.bin"],
            "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F",
        )

    def test_exact_two_targets_and_record_structure(self) -> None:
        self.assertEqual(
            [(item.coordinate, item.literal_id) for item in WAVE25.CHANGES],
            [((2, 283), 0), ((13, 221), 0)],
        )
        for item in WAVE25.CHANGES:
            with self.subTest(coordinate=item.text):
                before = self.before[item.coordinate]
                after = self.after[item.coordinate]
                self.assertEqual(WAVE25.sha256_bytes(before.data), item.input_record_sha256)
                self.assertEqual(len(before.data), item.input_record_size)
                self.assertEqual(
                    WAVE25.text_sha256(WAVE25.literal_texts(before)[item.literal_id]),
                    item.input_literal_sha256,
                )
                self.assertEqual(WAVE25.sha256_bytes(after.data), item.target_record_sha256)
                self.assertEqual(len(after.data), item.target_record_size)
                self.assertEqual(WAVE25.literal_texts(after)[item.literal_id], item.target_literal)
                self.assertEqual(
                    WAVE25.text_sha256(WAVE25.literal_texts(after)[item.literal_id]),
                    item.target_literal_sha256,
                )
                self.assertEqual(WAVE25.opaque_spans(after), WAVE25.opaque_spans(before))
                self.assertEqual(WAVE25.marker_topology(after), WAVE25.marker_topology(before))
                self.assertTrue(after.data.endswith(WAVE25.RECORD_TERMINATOR))

    def test_only_two_records_change_and_target_profile_is_pinned(self) -> None:
        self.assertEqual(self.before.keys(), self.after.keys())
        changed = {
            coordinate
            for coordinate in self.before
            if self.before[coordinate].data != self.after[coordinate].data
        }
        self.assertEqual(changed, set(WAVE25.CHANGE_BY_COORDINATE))
        for coordinate in self.before:
            if coordinate not in changed:
                self.assertEqual(self.before[coordinate].data, self.after[coordinate].data)
        self.assertEqual(len(self.output_a), WAVE25.TARGET_SIZES[WAVE25.PK_MSGGAME])
        self.assertEqual(WAVE25.sha256_bytes(self.output_a), WAVE25.TARGET_SHA256[WAVE25.PK_MSGGAME])
        WAVE25.validate_raw_roundtrip(self.output_a, "test Wave 25 candidate")

    def test_pc_only_anchors_duplicates_and_font_layout(self) -> None:
        anchors = WAVE25.validate_pc_anchors()
        self.assertEqual(set(anchors["reference_packed_sha256"]), {"JP", "EN", "SC", "TC"})
        self.assertEqual(set(anchors["records"]), {"2:283", "9:3874", "13:221", "13:274"})
        duplicate = self.audit_a["duplicate_evidence"]
        self.assertTrue(duplicate["battle_duplicate_is_not_modified"])
        self.assertTrue(duplicate["battle_target_has_explicit_line1_period"])
        self.assertTrue(duplicate["role_target_equals_duplicate"])
        self.assertEqual(self.audit_a["font_layout"]["font"]["packed_sha256"], WAVE25.FONT_SHA256)
        for item in WAVE25.CHANGES:
            row = self.audit_a["font_layout"]["records"][item.text]
            self.assertEqual(tuple(row["current"]["line_widths_px"]), item.current_widths_px)
            self.assertEqual(tuple(row["target"]["line_widths_px"]), item.target_widths_px)
            self.assertLessEqual(row["target"]["max_width_px"], WAVE25.DIALOGUE_MAX_LINE_PX)
            self.assertEqual(row["target"]["wide_fallback_codepoints"], [])

    def test_seven_other_groups_are_explicitly_retained(self) -> None:
        groups = self.audit_a["retained_consistency_groups"]
        self.assertEqual(len(groups), 7)
        self.assertEqual(
            [item["reason"] for item in groups],
            ["punctuation_variation", "style_variation", "style_variation", "dynamic_fragment", "punctuation_variation", "dynamic_fragment", "dynamic_fragment"],
        )
        self.assertTrue(all(item["decision"] == "reviewed_and_retained" for item in groups))
        self.assertTrue(all(len(item["jp_group_utf16le_sha256"]) == 64 for item in groups))
        self.assertTrue(all(item["pc_coordinates"] for item in groups))
        self.assertTrue(all(item["pc_jp_source_verified"] for item in groups))

    def test_deterministic_and_no_steam_writer(self) -> None:
        self.assertEqual(self.output_a, self.output_b)
        self.assertEqual(
            json.dumps(self.audit_a, ensure_ascii=False, sort_keys=True),
            json.dumps(self.audit_b, ensure_ascii=False, sort_keys=True),
        )
        policy = self.audit_a["source_policy"]
        self.assertTrue(policy["pc_jp_en_sc_tc_anchors_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["git_operation"], "absent")
        self.assertEqual(policy["release_operation"], "absent")
        with self.assertRaises(WAVE25.Wave25Error):
            WAVE25.require_tmp(WAVE25.DEFAULT_STEAM_ROOT, "Steam path")


if __name__ == "__main__":
    unittest.main(verbosity=2)
