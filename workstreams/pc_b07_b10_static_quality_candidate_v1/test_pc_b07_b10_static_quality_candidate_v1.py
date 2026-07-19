#!/usr/bin/env python3
"""Unit tests for the private PC B07–B10 six-literal candidate recipe."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_pc_b07_b10_static_quality_candidate_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_b07_b10_static_quality_candidate_v1", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PcB07B10StaticQualityCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate_existed_before_prepare = MODULE.CANDIDATE_ROOT.exists()
        cls.prepared = MODULE.prepare_all()
        cls.candidate_exists_after_prepare = MODULE.CANDIDATE_ROOT.exists()

    def test_recipe_has_exactly_six_distinct_literal_coordinates(self) -> None:
        coordinates = [
            change.coordinate
            for resource in MODULE.RESOURCES
            for change in resource.changes
        ]
        self.assertEqual(6, len(coordinates))
        self.assertEqual(6, len(set(coordinates)))
        self.assertEqual(
            {(9, 3640, 0), (9, 3776, 0), (9, 3796, 0), (9, 4094, 0), (9, 4113, 0), (9, 4114, 0)},
            set(coordinates),
        )

    def test_pinned_utf16le_preimages_and_targets_are_valid(self) -> None:
        for resource in MODULE.RESOURCES:
            for change in resource.changes:
                self.assertEqual(change.before_utf16le_sha256, MODULE.utf16le_sha256(change.before))
                self.assertEqual(change.after_utf16le_sha256, MODULE.utf16le_sha256(change.after))
                self.assertEqual(
                    MODULE.line_ending_signature(change.before),
                    MODULE.line_ending_signature(change.after),
                )
                self.assertEqual(MODULE.control_signature(change.before), MODULE.control_signature(change.after))

    def test_candidate_profiles_are_pinned(self) -> None:
        for prepared in self.prepared:
            self.assertEqual(prepared.spec.candidate_raw, MODULE.profile_of(prepared.candidate_raw))
            self.assertEqual(prepared.spec.candidate_packed, MODULE.profile_of(prepared.candidate_packed))
            self.assertEqual(prepared.candidate_raw, MODULE.rebuild_raw_msggame(prepared.candidate_archive))

    def test_changed_record_and_literal_scope_is_exact(self) -> None:
        for prepared in self.prepared:
            MODULE.validate_candidate_scope(prepared)
            source_literals = MODULE.literal_text_map(prepared.source_archive)
            candidate_literals = MODULE.literal_text_map(prepared.candidate_archive)
            actual = {
                coordinate
                for coordinate, source_text in source_literals.items()
                if source_text != candidate_literals[coordinate]
            }
            self.assertEqual({change.coordinate for change in prepared.spec.changes}, actual)

    def test_private_path_guard_rejects_game_input(self) -> None:
        self.assertEqual(
            MODULE.CANDIDATE_ROOT.resolve(),
            MODULE.require_candidate_path(MODULE.CANDIDATE_ROOT),
        )
        with self.assertRaises(MODULE.CandidateError):
            MODULE.require_candidate_path(MODULE.RESOURCES[0].source_path)

    def test_in_memory_preparation_does_not_write_a_private_candidate(self) -> None:
        self.assertEqual(self.candidate_existed_before_prepare, self.candidate_exists_after_prepare)


if __name__ == "__main__":
    unittest.main(verbosity=2)
