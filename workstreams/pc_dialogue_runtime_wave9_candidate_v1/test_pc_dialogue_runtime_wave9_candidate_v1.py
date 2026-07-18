#!/usr/bin/env python3
"""Deterministic contract tests for the private Wave 9 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_runtime_wave9_candidate_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_runtime_wave9", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Wave 9 builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE9 = load_builder()


class Wave9CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle_a = WAVE9.prepare_candidate(
            WAVE9.WAVE8_INPUT_ROOT, WAVE9.DEFAULT_FONT_ROOT
        )
        cls.bundle_b = WAVE9.prepare_candidate(
            WAVE9.WAVE8_INPUT_ROOT, WAVE9.DEFAULT_FONT_ROOT
        )

    def test_group_sizes_and_homograph_guard(self) -> None:
        WAVE9.validate_row_definitions()
        self.assertEqual(len(WAVE9.RUNTIME_LAYOUT_ROWS), 25)
        self.assertEqual(len(WAVE9.GUSIN_TERMINOLOGY_ROWS), 8)
        self.assertEqual(len(WAVE9.ALL_ROWS), 33)
        self.assertEqual(
            {item.coordinate for item in WAVE9.GUSIN_TERMINOLOGY_ROWS},
            {
                (6, 563),
                (6, 572),
                (6, 1195),
                (6, 1396),
                (6, 1397),
                (6, 1398),
                (6, 1399),
                (6, 1472),
            },
        )
        self.assertTrue(
            all(
                WAVE9.EXCLUDED_HOMOGRAPH
                not in "".join(item.current_literals + item.output_literals)
                for item in WAVE9.ALL_ROWS
            )
        )

    def test_terminology_changes_are_restricted(self) -> None:
        for item in WAVE9.GUSIN_TERMINOLOGY_ROWS:
            exception = WAVE9.TERMINOLOGY_GRAMMAR_EXCEPTIONS.get(item.coordinate)
            if exception is None:
                expected = tuple(
                    value.replace("구신", "건의") for value in item.current_literals
                )
            else:
                expected = tuple(
                    value.replace(exception[0], exception[1])
                    for value in item.current_literals
                )
            self.assertEqual(item.output_literals, expected, item.key)
        self.assertEqual(
            set(WAVE9.TERMINOLOGY_GRAMMAR_EXCEPTIONS),
            {(6, 1195), (6, 1396), (6, 1472)},
        )

    def test_bundle_is_deterministic_and_target_pinned(self) -> None:
        self.assertEqual(self.bundle_a.packed_msggame, self.bundle_b.packed_msggame)
        self.assertEqual(
            self.bundle_a.output_profile_sha256, WAVE9.TARGET_SHA256
        )
        self.assertEqual(
            json.dumps(self.bundle_a.audit, ensure_ascii=False, sort_keys=True),
            json.dumps(self.bundle_b.audit, ensure_ascii=False, sort_keys=True),
        )
        self.assertEqual(self.bundle_a.audit["summary"]["physical_records"], 33)
        self.assertEqual(
            self.bundle_a.audit["summary"]["high_confidence_terminology_records"], 8
        )
        self.assertTrue(self.bundle_a.audit["source_free"])
        self.assertEqual(self.bundle_a.audit["steam_write_capability"], "absent")

    def test_only_contract_records_change_and_opaque_bytes_survive(self) -> None:
        input_packed = (
            WAVE9.WAVE8_INPUT_ROOT / Path(WAVE9.RESOURCE)
        ).read_bytes()
        before = WAVE9.records_by_coordinate(input_packed)
        after = WAVE9.records_by_coordinate(self.bundle_a.packed_msggame)
        changed = {
            coordinate
            for coordinate in before
            if before[coordinate].data != after[coordinate].data
        }
        expected = {item.coordinate for item in WAVE9.ALL_ROWS}
        self.assertEqual(changed, expected)
        for item in WAVE9.ALL_ROWS:
            with self.subTest(coordinate=item.key):
                self.assertEqual(
                    WAVE9.opaque_spans(before[item.coordinate]),
                    WAVE9.opaque_spans(after[item.coordinate]),
                )
                self.assertEqual(
                    WAVE9.literal_marker_topology(before[item.coordinate]),
                    WAVE9.literal_marker_topology(after[item.coordinate]),
                )
                self.assertTrue(after[item.coordinate].data.endswith(WAVE9.RECORD_TERMINATOR))

    def test_pc_terminology_reference_profile_is_pinned(self) -> None:
        self.assertEqual(
            WAVE9.validate_terminology_references(), WAVE9.PC_REFERENCE_SHA256
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
