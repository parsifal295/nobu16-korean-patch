#!/usr/bin/env python3
"""Unit tests for the offline Steam-JP full Korean font candidate builder."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_font_advance_candidate_v1_under_test",
    ROOT / "build_steam_jp_font_advance_candidate_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CandidatePureLogicTests(unittest.TestCase):
    def test_rational_scaling_uses_nearest_even_with_wider_tie_break(self) -> None:
        self.assertEqual(MODULE.scale_to_even(18, 24, 32), 24)
        self.assertEqual(MODULE.scale_to_even(20, 24, 32), 26)
        self.assertEqual(MODULE.scale_to_even(22, 24, 32), 30)
        self.assertEqual(MODULE.scale_to_even(20, 24, 64), 54)
        self.assertEqual(MODULE.scale_to_even(22, 24, 64), 58)
        self.assertEqual(MODULE.scale_to_even(34, 48, 96), 68)

    def test_crop_window_preserves_all_nonzero_ink(self) -> None:
        rows = [
            [0, 0, 1, 2, 3, 0, 0, 0],
            [0, 0, 4, 5, 6, 0, 0, 0],
        ]
        packed, crop_key, ink_key = MODULE.pack_rows_for_target(rows, 4, {0xAC00}, "test")
        self.assertEqual(crop_key, "2")
        self.assertEqual(ink_key, "3")
        self.assertEqual(MODULE.unpack_nibbles(packed[:2]), [1, 2, 3, 0])
        self.assertEqual(MODULE.unpack_nibbles(packed[2:]), [4, 5, 6, 0])

    def test_crop_refuses_to_clip_ink(self) -> None:
        rows = [[1, 2, 3, 4, 5, 6]]
        with self.assertRaises(MODULE.CandidateError):
            MODULE.pack_rows_for_target(rows, 4, {0xAC00}, "test")

    def test_pc_ink_floor_widens_switch_metric_without_clipping(self) -> None:
        rows = [[0] * 5 + [1] * 37 + [0] * 6]
        width, evidence = MODULE.fit_width_to_pc_ink(rows, 36, 48, {0xAC00}, "test")
        self.assertEqual(width, 38)
        self.assertEqual(evidence["pc_ink_width"], 37)
        self.assertTrue(evidence["pc_ink_fit_override"])
        with self.assertRaises(MODULE.CandidateError):
            MODULE.fit_width_to_pc_ink(rows, 36, 36, {0xAC00}, "test")

    def test_blank_space_is_zero_packed_but_other_blank_glyph_fails(self) -> None:
        rows = [[0, 0, 0, 0], [0, 0, 0, 0]]
        packed, crop_key, ink_key = MODULE.pack_rows_for_target(rows, 2, {0x20}, "space")
        self.assertEqual(packed, b"\0\0")
        self.assertEqual((crop_key, ink_key), ("blank_space", "0"))
        with self.assertRaises(MODULE.CandidateError):
            MODULE.pack_rows_for_target(rows, 2, {0xAC00}, "non-space")

    def test_atlas_interval_guard_does_not_need_per_byte_offset_set(self) -> None:
        original = b"\0" * 12
        candidate = bytearray(original)
        candidate[2] = 1
        candidate[9] = 2
        MODULE.assert_atlas_changes_within_allocations(
            original, bytes(candidate), [(2, 3), (8, 10)], "test"
        )
        candidate[6] = 3
        with self.assertRaises(MODULE.CandidateError):
            MODULE.assert_atlas_changes_within_allocations(
                original, bytes(candidate), [(2, 3), (8, 10)], "test"
            )


class OutputPathSafetyTests(unittest.TestCase):
    def test_reparse_component_model_is_rejected_without_symlink_privilege(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            escaped = root / "escape" / "output"
            with mock.patch.object(
                MODULE,
                "is_reparse_point",
                side_effect=lambda path: Path(path).name == "escape",
            ):
                with self.assertRaises(MODULE.CandidateError):
                    MODULE.require_no_reparse_components(root, escaped)

    def test_reparse_component_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            safe = root / "safe"
            safe.mkdir()
            target = safe / "output"
            MODULE.require_no_reparse_components(root, target)
            link = safe / "escape"
            try:
                link.symlink_to(root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable in this Windows test environment")
            with self.assertRaises(MODULE.CandidateError):
                MODULE.require_no_reparse_components(root, link / "output")


if __name__ == "__main__":
    unittest.main()
