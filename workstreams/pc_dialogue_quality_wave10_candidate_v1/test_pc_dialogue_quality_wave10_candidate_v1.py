#!/usr/bin/env python3
"""Deterministic contracts for the private PC-only Wave 10 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave10_candidate_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave10", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Wave 10 builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE10 = load_builder()


class Wave10CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle_a = WAVE10.prepare_candidate(
            WAVE10.WAVE9_INPUT_ROOT, WAVE10.DEFAULT_FONT_ROOT
        )
        cls.bundle_b = WAVE10.prepare_candidate(
            WAVE10.WAVE9_INPUT_ROOT, WAVE10.DEFAULT_FONT_ROOT
        )

    def test_scope_is_exactly_the_twelve_pk_records(self) -> None:
        self.assertEqual(WAVE10.PK_RECORD_IDS, tuple(range(1454, 1466)))
        self.assertEqual(WAVE10.BASE_DONOR_RECORD_IDS, tuple(range(1450, 1462)))
        self.assertEqual(len(WAVE10.PK_RECORD_IDS), 12)
        self.assertEqual(WAVE10.RESOURCE, "MSG_PK/JP/msggame.bin")
        self.assertEqual(WAVE10.CURRENT_LITERALS, ("승", "…\n가문을 위해서라면, 어쩔 수 없"))
        self.assertEqual(
            WAVE10.TARGET_LITERALS,
            ("알겠습니다", "…\n가문을 위한 일이라면, 어쩔 수 없지요."),
        )

    def test_candidate_is_deterministic_and_pinned(self) -> None:
        self.assertEqual(self.bundle_a.packed_msggame, self.bundle_b.packed_msggame)
        self.assertEqual(self.bundle_a.input_sha256, WAVE10.INPUT_SHA256)
        self.assertEqual(self.bundle_a.output_sha256, WAVE10.TARGET_SHA256)
        self.assertEqual(
            json.dumps(self.bundle_a.audit, ensure_ascii=False, sort_keys=True),
            json.dumps(self.bundle_b.audit, ensure_ascii=False, sort_keys=True),
        )
        self.assertTrue(self.bundle_a.audit["source_free"])
        self.assertFalse(self.bundle_a.audit["source_policy"]["switch_korean_used"])
        self.assertEqual(self.bundle_a.audit["steam_write_capability"], "absent")

    def test_only_contract_records_change(self) -> None:
        input_path = WAVE10.WAVE9_INPUT_ROOT / Path(WAVE10.RESOURCE)
        before = WAVE10.records_by_coordinate(input_path.read_bytes())
        after = WAVE10.records_by_coordinate(self.bundle_a.packed_msggame)
        changed = {
            coordinate
            for coordinate in before
            if before[coordinate].data != after[coordinate].data
        }
        expected = {(6, record_id) for record_id in WAVE10.PK_RECORD_IDS}
        self.assertEqual(changed, expected)
        for coordinate in sorted(expected):
            with self.subTest(coordinate=coordinate):
                self.assertEqual(
                    WAVE10.literal_texts(before[coordinate]), WAVE10.CURRENT_LITERALS
                )
                self.assertEqual(
                    WAVE10.literal_texts(after[coordinate]), WAVE10.TARGET_LITERALS
                )
                self.assertEqual(
                    tuple(item.hex().upper() for item in WAVE10.opaque_spans(before[coordinate])),
                    WAVE10.INPUT_OPAQUE_SPANS_HEX,
                )
                self.assertEqual(
                    tuple(item.hex().upper() for item in WAVE10.opaque_spans(after[coordinate])),
                    WAVE10.OUTPUT_OPAQUE_SPANS_HEX,
                )
                self.assertEqual(
                    WAVE10.marker_topology(before[coordinate]),
                    WAVE10.marker_topology(after[coordinate]),
                )
                self.assertTrue(after[coordinate].data.endswith(WAVE10.RECORD_TERMINATOR))
                self.assertEqual(WAVE10.WAVE4.opaque_commands(after[coordinate]), ())

    def test_base_direct_correction_and_pristine_pc_jp_are_pinned(self) -> None:
        evidence = WAVE10.validate_pc_direct_correction()
        self.assertEqual(len(evidence["one_to_one_pairs"]), 12)
        self.assertEqual(evidence["base_current_sha256"], WAVE10.BASE_CURRENT_SHA256)
        self.assertEqual(
            evidence["base_pristine_jp_sha256"], WAVE10.BASE_PRISTINE_JP_SHA256
        )
        self.assertEqual(evidence["pk_pristine_jp_sha256"], WAVE10.PK_PRISTINE_JP_SHA256)
        self.assertTrue(
            all(
                item["base_output_record_sha256"] == WAVE10.TARGET_RECORD_SHA256
                for item in evidence["one_to_one_pairs"]
            )
        )

    def test_target_font_layout_is_two_lines_and_within_limit(self) -> None:
        summary = self.bundle_a.audit["summary"]
        self.assertEqual(summary["manual_lines"], 2)
        self.assertEqual(summary["target_line_widths_px"], [288, 888])
        self.assertLessEqual(max(summary["target_line_widths_px"]), WAVE10.MAX_LINE_PX)
        self.assertEqual(len(self.bundle_a.audit["records"]), 12)
        for row in self.bundle_a.audit["records"]:
            with self.subTest(coordinate=row["coordinate"]):
                self.assertEqual(row["output_layout"]["line_count"], 2)
                self.assertEqual(row["output_layout"]["line_widths_px"], [288, 888])
                self.assertEqual(row["output_layout"]["wide_fallback_codepoints"], [])
                self.assertEqual(row["missing_static_glyphs"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
