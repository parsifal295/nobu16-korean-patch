#!/usr/bin/env python3
"""Regression contracts for the private Wave 18 static-label candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_static_labels_wave18_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_event_static_labels_wave18", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE18 = load_builder()


class Wave18StaticLabelCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = WAVE18.prepare_candidate()
        cls.current = WAVE18.load_current_steam_table()
        expected_texts = list(cls.current.table.texts)
        for change in WAVE18.CHANGES:
            expected_texts[change.entry_id] = change.target_text
        cls.candidate_raw, cls.candidate_table = WAVE18.validate_candidate(
            cls.current,
            cls.bundle.packed,
            tuple(expected_texts),
        )

    def test_pinned_profiles_and_output_are_complete(self) -> None:
        self.assertEqual(WAVE18.INPUT_SHA256, WAVE18.sha256_bytes(self.current.packed))
        self.assertEqual(WAVE18.INPUT_RAW_SHA256, WAVE18.sha256_bytes(self.current.raw))
        self.assertEqual(WAVE18.TARGET_SHA256, WAVE18.sha256_bytes(self.bundle.packed))
        self.assertEqual(WAVE18.TARGET_RAW_SHA256, WAVE18.sha256_bytes(self.bundle.raw))
        self.assertEqual(len(self.bundle.packed), WAVE18.TARGET_SIZE)
        self.assertEqual(len(self.bundle.raw), WAVE18.TARGET_RAW_SIZE)
        self.assertEqual(
            tuple(change.entry_id for change in WAVE18.CHANGES),
            (11007, 14040, 14386, 14391, 14403, 14623, 14648, 14651),
        )
        self.assertEqual(
            self.bundle.audit["only_changed_ids"],
            [11007, 14040, 14386, 14391, 14403, 14623, 14648, 14651],
        )

    def test_only_the_eight_pinned_static_labels_change(self) -> None:
        changed_ids = {
            entry_id
            for entry_id, (before, after) in enumerate(
                zip(self.current.table.texts, self.candidate_table.texts)
            )
            if before != after
        }
        self.assertEqual(changed_ids, set(WAVE18.CHANGE_BY_ID))
        for change in WAVE18.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                self.assertEqual(self.current.table.texts[change.entry_id], change.current_text)
                self.assertEqual(self.candidate_table.texts[change.entry_id], change.target_text)
                self.assertEqual(
                    WAVE18.text_hash(self.current.table.texts[change.entry_id]),
                    change.current_text_sha256,
                )
                self.assertEqual(
                    WAVE18.text_hash(self.candidate_table.texts[change.entry_id]),
                    change.target_text_sha256,
                )

    def test_pc_jp_en_sc_tc_anchors_are_pinned_per_entry(self) -> None:
        records = {record["id"]: record for record in self.bundle.audit["records"]}
        self.assertEqual(set(records), set(WAVE18.CHANGE_BY_ID))
        for change in WAVE18.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                record = records[change.entry_id]
                declared = WAVE18.source_anchor_map(change)
                self.assertEqual(set(record["anchors"]), {"JP", "EN", "SC", "TC"})
                for language, anchor in declared.items():
                    observed = record["anchors"][language]
                    self.assertEqual(observed["text"], anchor.text)
                    self.assertEqual(observed["utf16le_sha256"], anchor.utf16le_sha256)
                    self.assertEqual(WAVE18.text_hash(observed["text"]), anchor.utf16le_sha256)
        self.assertEqual(
            self.bundle.audit["source_resources"]["JP"]["sha256"],
            WAVE18.PRISTINE_PC_JP_SHA256,
        )
        self.assertEqual(self.bundle.audit["source_resources"]["EN"]["sha256"], WAVE18.PC_EN_SHA256)
        self.assertEqual(self.bundle.audit["source_resources"]["SC"]["sha256"], WAVE18.PC_SC_SHA256)
        self.assertEqual(self.bundle.audit["source_resources"]["TC"]["sha256"], WAVE18.PC_TC_SHA256)

    def test_duplicate_and_era_format_anchors_are_hash_pinned(self) -> None:
        records = {record["id"]: record for record in self.bundle.audit["records"]}
        for change in WAVE18.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                reported = {anchor["id"]: anchor for anchor in records[change.entry_id]["duplicate_anchors"]}
                self.assertEqual(
                    set(reported),
                    {anchor.entry_id for anchor in change.duplicate_anchors},
                )
                for anchor in change.duplicate_anchors:
                    observed = reported[anchor.entry_id]
                    self.assertEqual(observed["jp_text"], anchor.jp_text)
                    self.assertEqual(
                        observed["jp_utf16le_sha256"],
                        anchor.jp_utf16le_sha256,
                    )
                    self.assertEqual(observed["current_ko_text"], anchor.current_ko_text)
                    self.assertEqual(
                        observed["current_ko_utf16le_sha256"],
                        anchor.current_ko_utf16le_sha256,
                    )
                    self.assertEqual(observed["matches_target"], anchor.matches_target)
        self.assertEqual(
            [anchor["id"] for anchor in self.bundle.audit["era_format_anchors"]],
            [14642, 14643],
        )
        for expected, observed in zip(
            WAVE18.ERA_FORMAT_ANCHORS,
            self.bundle.audit["era_format_anchors"],
            strict=True,
        ):
            self.assertEqual(observed["jp_utf16le_sha256"], expected.jp_utf16le_sha256)
            self.assertEqual(
                observed["current_ko_utf16le_sha256"],
                expected.current_ko_utf16le_sha256,
            )
            self.assertTrue(observed["current_ko_text"].startswith("시대 개요("))
            self.assertTrue(observed["current_ko_text"].endswith(")"))

    def test_control_token_linebreak_and_font_layout_invariants_are_fixed(self) -> None:
        records = {record["id"]: record for record in self.bundle.audit["records"]}
        self.assertEqual(self.bundle.audit["font"]["sha256"], WAVE18.EVENT_FONT_SHA256)
        self.assertEqual(self.bundle.audit["font"]["size"], WAVE18.EVENT_FONT_SIZE)
        for change in WAVE18.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                record = records[change.entry_id]
                invariant = record["format_invariants"]
                self.assertTrue(invariant["identical"])
                self.assertEqual(invariant["current"], WAVE18.EMPTY_STATIC_SIGNATURE)
                self.assertEqual(invariant["target"], WAVE18.EMPTY_STATIC_SIGNATURE)
                layout = record["layout"]
                self.assertEqual(
                    tuple(layout["current_line_widths_px"]),
                    change.current_line_widths_px,
                )
                self.assertEqual(
                    tuple(layout["target_line_widths_px"]),
                    change.target_line_widths_px,
                )
                self.assertLessEqual(max(layout["target_line_widths_px"]), WAVE18.MAX_LINE_PX)
                self.assertLessEqual(len(layout["target_line_widths_px"]), WAVE18.MAX_LINES)

    def test_source_and_write_policy_excludes_switch_and_steam_apply(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pristine_pc_japanese_anchor_read"])
        self.assertTrue(policy["pc_english_anchor_read"])
        self.assertTrue(policy["pc_simplified_chinese_anchor_read"])
        self.assertTrue(policy["pc_traditional_chinese_anchor_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["existing_korean_translation_artifacts_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertEqual(self.bundle.manifest["steam_apply"], "not_implemented")
        self.assertEqual(self.bundle.manifest["transaction"], "not_implemented")
        self.assertEqual(self.bundle.manifest["git_commit"], "not_implemented")

    def test_candidate_write_path_is_private_and_current_source_path_is_not_rebasable(self) -> None:
        valid = WAVE18.require_private_output(WAVE18.PRIVATE_TMP_ROOT / "unit-test-candidate")
        self.assertEqual(valid, (WAVE18.PRIVATE_TMP_ROOT / "unit-test-candidate").resolve())
        with self.assertRaises(WAVE18.Wave18Error):
            WAVE18.require_private_output(WAVE18.CURRENT_STEAM_RESOURCE)
        with self.assertRaises(WAVE18.Wave18Error):
            WAVE18.load_current_steam_table(WAVE18.PRISTINE_PC_JP_RESOURCE)

    def test_prepare_is_deterministic(self) -> None:
        again = WAVE18.prepare_candidate()
        self.assertEqual(again.packed, self.bundle.packed)
        self.assertEqual(again.raw, self.bundle.raw)
        self.assertEqual(again.audit, self.bundle.audit)
        self.assertEqual(again.manifest, self.bundle.manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
