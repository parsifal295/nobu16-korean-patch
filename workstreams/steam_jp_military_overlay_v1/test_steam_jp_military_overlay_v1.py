#!/usr/bin/env python3
"""Small deterministic tests for the private /12 military-overlay builder."""

from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_steam_jp_military_overlay_v1 as builder  # noqa: E402


class MappingContractTests(unittest.TestCase):
    def test_safe_mapping_contract(self) -> None:
        builder.validate_mapping_contract()
        self.assertEqual(len(builder.SAFE_MAPPINGS), 4)
        self.assertEqual(len(builder.AUDIT_ONLY_MAPPINGS), 3)

    def test_safe_targets_are_disjoint_and_bc3_aligned(self) -> None:
        targets = [tuple(item["pc_target_rect"]) for item in builder.SAFE_MAPPINGS]
        for target in targets:
            self.assertTrue(all(value % 4 == 0 for value in target))
        for position, target in enumerate(targets):
            for other in targets[position + 1:]:
                self.assertFalse(builder.rectangles_overlap(target, other))

    def test_forbidden_title_logo_outer_entries_are_not_targets(self) -> None:
        self.assertNotIn(builder.OUTER_INDEX, {3, 24})
        for row in builder.SAFE_MAPPINGS:
            self.assertNotIn("logo", row["id"].lower())
            self.assertNotIn("title_art", row["id"].lower())

    def test_audit_only_rank_rows_have_no_pc_write_rectangle(self) -> None:
        for row in builder.AUDIT_ONLY_MAPPINGS:
            self.assertNotIn("pc_target_rect", row)
            self.assertIn("background", row["reason"])


class ContainerAndPixelTests(unittest.TestCase):
    def test_nested_link_identity_and_replacement(self) -> None:
        fixed = b"LINK" + struct.pack("<4I", 1, 32, 58, 64) + b"\0" * 12
        original = fixed + struct.pack("<II", 64, 4) + b"\0" * 24 + b"abcd"
        parsed = builder.parse_inner_link(original, "synthetic")
        self.assertEqual(builder.rebuild_inner_link(parsed), original)
        replacement = builder.rebuild_inner_link(parsed, {0: b"abcdef"})
        reparsed = builder.parse_inner_link(replacement, "synthetic replacement")
        self.assertEqual(reparsed.entries[0].data, b"abcdef")
        self.assertEqual(reparsed.resource_id, 58)

    def test_change_escape_gate(self) -> None:
        before = bytes(8 * 8 * 4)
        after = bytearray(before)
        after[(2 * 8 + 2) * 4:(2 * 8 + 2) * 4 + 4] = b"\xFF\x00\x00\xFF"
        after[(6 * 8 + 6) * 4:(6 * 8 + 6) * 4 + 4] = b"\xFF\x00\x00\xFF"
        self.assertEqual(builder.changed_pixels_escape_rectangles(before, bytes(after), 8, 8, [(0, 0, 4, 4)]), 1)
        self.assertEqual(builder.changed_pixel_count(before, bytes(after), 8, 8, within=(0, 0, 4, 4)), 1)

    def test_clear_then_paste_is_bounded(self) -> None:
        canvas = bytearray(b"\xAA" * (8 * 8 * 4))
        builder.clear_rect_rgba(canvas, 8, 8, (4, 4, 8, 8))
        source = b"\x10\x20\x30\x40" * 16
        builder.paste_rgba(canvas, 8, 4, 4, source, 4, 4)
        self.assertEqual(canvas[:4], b"\xAA" * 4)
        self.assertEqual(canvas[(4 * 8 + 4) * 4:(4 * 8 + 4) * 4 + 4], b"\x10\x20\x30\x40")

    def test_lexical_tmp_rejects_escape_without_creating_output(self) -> None:
        with self.assertRaises(builder.OverlayError):
            builder.lexical_tmp_path(Path(r"C:\outside-of-project\candidate.bin"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
