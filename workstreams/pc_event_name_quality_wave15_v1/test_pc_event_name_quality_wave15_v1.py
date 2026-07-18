#!/usr/bin/env python3
"""Regression contracts for the private Wave 15 event-name candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_name_quality_wave15_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_event_name_quality_wave15", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE15 = load_builder()


class Wave15EventNameCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = WAVE15.prepare_candidate()
        cls.current = WAVE15.load_current_steam_table()
        expected_texts = list(cls.current.table.texts)
        for change in WAVE15.CHANGES:
            expected_texts[change.entry_id] = change.target_text
        cls.candidate_raw, cls.candidate_table = WAVE15.validate_candidate(
            cls.current,
            cls.bundle.packed,
            tuple(expected_texts),
        )

    def test_pinned_profiles_and_output_are_complete(self) -> None:
        self.assertEqual(WAVE15.INPUT_SHA256, WAVE15.sha256_bytes(self.current.packed))
        self.assertEqual(WAVE15.INPUT_RAW_SHA256, WAVE15.sha256_bytes(self.current.raw))
        self.assertEqual(WAVE15.TARGET_SHA256, WAVE15.sha256_bytes(self.bundle.packed))
        self.assertEqual(WAVE15.TARGET_RAW_SHA256, WAVE15.sha256_bytes(self.bundle.raw))
        self.assertEqual(len(self.bundle.packed), WAVE15.TARGET_SIZE)
        self.assertEqual(len(self.bundle.raw), WAVE15.TARGET_RAW_SIZE)
        self.assertEqual(tuple(change.entry_id for change in WAVE15.CHANGES), (3015, 3016, 3084))
        self.assertEqual(self.bundle.audit["only_changed_ids"], [3015, 3016, 3084])

    def test_only_the_three_pinned_event_names_change(self) -> None:
        changed_ids = {
            entry_id
            for entry_id, (before, after) in enumerate(
                zip(self.current.table.texts, self.candidate_table.texts)
            )
            if before != after
        }
        self.assertEqual(changed_ids, {3015, 3016, 3084})
        for change in WAVE15.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                self.assertEqual(self.current.table.texts[change.entry_id], change.current_text)
                self.assertEqual(self.candidate_table.texts[change.entry_id], change.target_text)
                self.assertEqual(
                    WAVE15.text_hash(self.current.table.texts[change.entry_id]),
                    change.current_text_sha256,
                )
                self.assertEqual(
                    WAVE15.text_hash(self.candidate_table.texts[change.entry_id]),
                    change.target_text_sha256,
                )

    def test_pc_japanese_and_english_anchors_are_pinned_per_entry(self) -> None:
        records = {record["id"]: record for record in self.bundle.audit["records"]}
        self.assertEqual(set(records), {3015, 3016, 3084})
        for change in WAVE15.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                record = records[change.entry_id]
                anchors = record["anchors"]
                self.assertEqual(
                    WAVE15.text_hash(anchors["pristine_pc_japanese_text"]),
                    change.jp_anchor_utf16le_sha256,
                )
                self.assertEqual(
                    WAVE15.text_hash(anchors["pc_english_text"]),
                    change.en_anchor_utf16le_sha256,
                )
                self.assertEqual(
                    anchors["pristine_pc_japanese_text"],
                    change.jp_anchor_text,
                )
                self.assertEqual(anchors["pc_english_text"], change.en_anchor_text)
        anchors = self.bundle.audit["anchors"]
        self.assertEqual(anchors["pristine_pc_japanese"]["sha256"], WAVE15.PRISTINE_PC_JP_SHA256)
        self.assertEqual(anchors["pc_english"]["sha256"], WAVE15.PC_EN_SHA256)

    def test_control_token_linebreak_and_font_layout_invariants_are_fixed(self) -> None:
        records = {record["id"]: record for record in self.bundle.audit["records"]}
        self.assertEqual(self.bundle.audit["font"]["sha256"], WAVE15.EVENT_FONT_SHA256)
        self.assertEqual(self.bundle.audit["font"]["size"], WAVE15.EVENT_FONT_SIZE)
        for change in WAVE15.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                record = records[change.entry_id]
                invariant = record["format_invariants"]
                self.assertTrue(invariant["identical"])
                self.assertEqual(invariant["current"], WAVE15.EMPTY_STATIC_SIGNATURE)
                self.assertEqual(invariant["target"], WAVE15.EMPTY_STATIC_SIGNATURE)
                layout = record["layout"]
                self.assertEqual(
                    tuple(layout["current_line_widths_px"]),
                    change.current_line_widths_px,
                )
                self.assertEqual(
                    tuple(layout["target_line_widths_px"]),
                    change.target_line_widths_px,
                )
                self.assertLessEqual(max(layout["target_line_widths_px"]), WAVE15.MAX_LINE_PX)
                self.assertLessEqual(len(layout["target_line_widths_px"]), WAVE15.MAX_LINES)

    def test_source_and_write_policy_excludes_switch_and_steam_apply(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pristine_pc_japanese_anchor_read"])
        self.assertTrue(policy["pc_english_anchor_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["existing_korean_translation_artifacts_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertEqual(self.bundle.manifest["steam_apply"], "not_implemented")
        self.assertEqual(self.bundle.manifest["transaction"], "not_implemented")
        self.assertEqual(self.bundle.manifest["git_commit"], "not_implemented")

    def test_candidate_write_path_is_private_and_current_source_path_is_not_rebasable(self) -> None:
        valid = WAVE15.require_private_output(WAVE15.PRIVATE_TMP_ROOT / "unit-test-candidate")
        self.assertEqual(valid, (WAVE15.PRIVATE_TMP_ROOT / "unit-test-candidate").resolve())
        with self.assertRaises(WAVE15.Wave15Error):
            WAVE15.require_private_output(WAVE15.CURRENT_STEAM_RESOURCE)
        with self.assertRaises(WAVE15.Wave15Error):
            WAVE15.load_current_steam_table(WAVE15.PRISTINE_PC_JP_RESOURCE)

    def test_prepare_is_deterministic(self) -> None:
        again = WAVE15.prepare_candidate()
        self.assertEqual(again.packed, self.bundle.packed)
        self.assertEqual(again.raw, self.bundle.raw)
        self.assertEqual(again.audit, self.bundle.audit)
        self.assertEqual(again.manifest, self.bundle.manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
