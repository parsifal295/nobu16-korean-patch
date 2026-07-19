#!/usr/bin/env python3
"""Independent checks for the private direct-PC Batch C event candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_tag_reflow_batch_c_candidate_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("batch_c_candidate_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Batch C candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BatchCCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = load_builder()
        cls.bundle = cls.m.prepare_candidate()
        cls.current = cls.m.load_table(
            cls.m.STEAM_PC_KO_EVENT,
            cls.m.W45_INPUT_PROFILE,
            cls.m.W45_RECORD_COUNT,
            "test W45 direct-PC Korean event",
            require_packed_round_trip=True,
        )
        cls.jp = cls.m.load_table(
            cls.m.PRISTINE_PC_JP_EVENT,
            cls.m.PRISTINE_PC_JP_PROFILE,
            cls.m.PRISTINE_PC_JP_RECORD_COUNT,
            "test pristine direct-PC Japanese event",
            require_packed_round_trip=False,
        )

    def test_exact_reviewed_scope(self) -> None:
        self.assertEqual(
            tuple(change.entry_id for change in self.m.CHANGES),
            (3960, 8138, 8451, 8704, 9131, 9137, 9795, 9806, 10534, 10800, 10803),
        )
        self.assertEqual(set(self.m.PC_JP_INDEX_MAP), {change.entry_id for change in self.m.CHANGES})
        self.assertEqual(len(self.m.CHANGES), 11)

    def test_root_revised_3960_literal_and_hash(self) -> None:
        change = {item.entry_id: item for item in self.m.CHANGES}[3960]
        self.assertEqual(
            change.target,
            "교묘한 수였으나, \x1bCA모토나리\x1bCZ의\n"
            "끝까지 비정한 결단으로 \x1bCB이노우에 일파\x1bCZ의\n"
            "가문 내 영향력은 일소되었다.",
        )
        self.assertEqual(
            self.m.text_hash(change.target),
            "E73C8511A443313D01FD3623882D2A2F6BE0E50CA500AF71B95835C922FA1326",
        )

    def test_report_literals_match_all_changes(self) -> None:
        self.m.require_report_literals()

    def test_pc_jp_anchors_tags_and_event_font_layout(self) -> None:
        utility = self.m.load_width_utility()
        advance, font = utility.load_event_font()
        self.assertEqual(dict(font), self.m.FONT_EVIDENCE)
        for change in self.m.CHANGES:
            widths = self.m.validate_change(change, self.current, self.jp, utility, advance)
            self.assertGreaterEqual(len(widths), 1)
            self.assertLessEqual(len(widths), 3)
            self.assertLessEqual(max(widths), self.m.PK_MAX_LINE_PX)
            self.assertEqual(widths, change.target_line_widths_px)

    def test_lz4_and_parser_round_trip(self) -> None:
        header, raw = self.m.decompress_wrapper(self.bundle.packed)
        table = self.m.parse_message_table(raw)
        self.assertEqual(raw, self.bundle.raw)
        self.assertEqual(self.m.rebuild_message_table(table, table.texts), raw)
        self.assertEqual(self.m.recompress_wrapper(raw, header), self.bundle.packed)

    def test_exact_changed_id_scope(self) -> None:
        _, raw = self.m.decompress_wrapper(self.bundle.packed)
        table = self.m.parse_message_table(raw)
        changed = tuple(
            index
            for index, (before, after) in enumerate(zip(self.current.table.texts, table.texts))
            if before != after
        )
        self.assertEqual(changed, tuple(change.entry_id for change in self.m.CHANGES))
        for change in self.m.CHANGES:
            self.assertEqual(table.texts[change.entry_id], change.target)

    def test_pinned_output_profile(self) -> None:
        self.m.require_profile(
            self.bundle.packed,
            self.bundle.raw,
            self.m.EXPECTED_OUTPUT_PROFILE,
            "test Batch C output",
        )
        self.assertEqual(self.bundle.output_profile, self.m.EXPECTED_OUTPUT_PROFILE)

    def test_audit_manifest_integrity_and_3960_supersession(self) -> None:
        self.assertEqual(
            self.m.sha256_bytes(self.m.canonical_json(self.bundle.audit)),
            self.bundle.manifest["audit_sha256"],
        )
        self.assertEqual(self.bundle.manifest["changed_cell_count"], 11)
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])
        self.assertTrue(self.bundle.audit["candidate_only"])
        self.assertIn("supersedes", self.bundle.audit["scope_notes"]["3960"])

    def test_private_output_guard(self) -> None:
        accepted = self.m.require_private(self.m.TMP_ROOT / "candidate-test", "test private root")
        self.assertTrue(accepted.is_relative_to(self.m.TMP_ROOT.resolve(strict=False)))
        with self.assertRaises(self.m.CandidateError):
            self.m.require_private(self.m.REPO / "outside-private", "test outside root")
        with self.assertRaises(self.m.CandidateError):
            self.m.require_private(self.m.TMP_ROOT, "test tmp root itself")


if __name__ == "__main__":
    unittest.main(verbosity=2)
