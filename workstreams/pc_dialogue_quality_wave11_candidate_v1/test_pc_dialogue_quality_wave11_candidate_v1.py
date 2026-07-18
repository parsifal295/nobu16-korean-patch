#!/usr/bin/env python3
"""Regression tests for the private PC-only Wave 11 terminology candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave11_candidate_v1.py"


def load_builder():
    name = "_test_pc_dialogue_quality_wave11_candidate"
    spec = importlib.util.spec_from_file_location(name, BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 11 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


WAVE11 = load_builder()


class Wave11CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = WAVE11.prepare_candidate(
            WAVE11.WAVE9_INPUT_ROOT, WAVE11.DEFAULT_FONT_ROOT
        )
        cls.input_packed = WAVE11.validate_wave9_input(WAVE11.WAVE9_INPUT_ROOT)
        cls.before = WAVE11.records_by_coordinate(cls.input_packed)
        cls.after = WAVE11.records_by_coordinate(cls.bundle.packed)

    def test_candidate_is_deterministic_and_pinned(self) -> None:
        again = WAVE11.prepare_candidate(WAVE11.WAVE9_INPUT_ROOT, WAVE11.DEFAULT_FONT_ROOT)
        self.assertEqual(WAVE11.sha256_bytes(self.bundle.packed), WAVE11.TARGET_SHA256)
        self.assertEqual(self.bundle.packed, again.packed)
        self.assertEqual(self.bundle.audit["input_sha256"], WAVE11.INPUT_SHA256)
        self.assertEqual(self.bundle.audit["output_sha256"], WAVE11.TARGET_SHA256)

    def test_exactly_eight_records_change(self) -> None:
        changed = {
            coordinate
            for coordinate in self.before
            if self.before[coordinate].data != self.after[coordinate].data
        }
        expected = {change.record_coordinate for change in WAVE11.CHANGES}
        self.assertEqual(changed, expected)
        self.assertEqual(len(expected), 8)

    def test_every_literal_and_opaque_span_is_pinned(self) -> None:
        for change in WAVE11.CHANGES:
            before = self.before[change.record_coordinate]
            after = self.after[change.record_coordinate]
            self.assertEqual(WAVE11.sha256_bytes(before.data), change.input_record_sha256)
            self.assertEqual(WAVE11.sha256_bytes(after.data), change.output_record_sha256)
            self.assertEqual(
                WAVE11.literals(before)[change.literal_id],
                change.current,
                change.label,
            )
            self.assertEqual(
                WAVE11.literals(after)[change.literal_id],
                change.target,
                change.label,
            )
            self.assertEqual(WAVE11.opaque_spans(after), WAVE11.opaque_spans(before))
            self.assertEqual(WAVE11.marker_topology(after), WAVE11.marker_topology(before))
            self.assertNotIn(b"\x01\x43", before.data)
            self.assertTrue(after.data.endswith(WAVE11.RECORD_TERMINATOR))

    def test_pristine_pc_japanese_and_pc_english_anchor_the_feature(self) -> None:
        evidence = WAVE11.validate_semantic_anchors()
        self.assertEqual(evidence["feature_anchor_count"], len(WAVE11.CHANGES))
        self.assertEqual(evidence["pristine_pk_jp_sha256"], WAVE11.PRISTINE_PK_JP_SHA256)
        self.assertEqual(evidence["pk_en_sha256"], WAVE11.PK_EN_SHA256)
        self.assertFalse(self.bundle.audit["source_policy"]["switch_korean_used"])

    def test_layout_preserves_all_manual_lines_without_fallback(self) -> None:
        advance, _font = WAVE11.WAVE10_METRIC.load_font_advance(WAVE11.DEFAULT_FONT_ROOT)
        for change in WAVE11.CHANGES:
            before_layout = WAVE11.record_layout(
                self.before[change.record_coordinate], advance
            )
            after_layout = WAVE11.record_layout(
                self.after[change.record_coordinate], advance
            )
            self.assertEqual(
                tuple(after_layout["line_widths_px"]),
                change.expected_record_line_widths_px,
                change.label,
            )
            self.assertEqual(after_layout["line_count"], before_layout["line_count"])
            self.assertTrue(
                all(
                    after_width <= before_width
                    for before_width, after_width in zip(
                        before_layout["line_widths_px"],
                        after_layout["line_widths_px"],
                    )
                ),
                change.label,
            )
            self.assertEqual(after_layout["wide_fallback_codepoints"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
