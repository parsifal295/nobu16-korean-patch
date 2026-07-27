from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_military_overlay_no_japanese_v2.py")
SPEC = importlib.util.spec_from_file_location("military_overlay_no_japanese_v2", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class NoJapaneseContractTests(unittest.TestCase):
    def test_contract(self) -> None:
        builder.validate_contract()

    def test_inventory_matches_all_seven_audited_groups(self) -> None:
        expected = {
            row["id"] for row in builder.v1.military.SAFE_MAPPINGS
        } | {
            row["id"] for row in builder.v1.military.AUDIT_ONLY_MAPPINGS
        }
        self.assertEqual({row["id"] for row in builder.ELEMENTS}, expected)
        self.assertEqual(len(expected), 7)

    def test_every_japanese_bbox_and_korean_target_are_cleared(self) -> None:
        for row in builder.ELEMENTS:
            self.assertTrue(builder.v1.rect_contains(row["low_clear_rect"], row["low_japanese_bbox"]))
            self.assertTrue(builder.v1.rect_contains(row["low_clear_rect"], row["low_korean_target"]))

    def test_every_high_japanese_bbox_has_full_clear_provenance(self) -> None:
        for row in builder.ELEMENTS:
            self.assertTrue(builder.v1.rect_contains(row["high_clear_provenance"], row["high_japanese_bbox"]))

    def test_every_korean_target_is_rounded_half_of_high_source(self) -> None:
        for row in builder.ELEMENTS:
            source_width, source_height = builder.v1.rect_dimensions(row["high_korean_source"])
            target_width, target_height = builder.v1.rect_dimensions(row["low_korean_target"])
            self.assertEqual(
                (target_width, target_height),
                ((source_width + 1) // 2, (source_height + 1) // 2),
            )

    def test_low_clear_rectangles_do_not_overlap(self) -> None:
        rectangles = [row["low_clear_rect"] for row in builder.ELEMENTS]
        for index, left in enumerate(rectangles):
            for right in rectangles[index + 1 :]:
                self.assertFalse(builder.v1.rectangles_overlap(left, right))

    def test_expected_hashes_are_full_sha256(self) -> None:
        for row in builder.EXPECTED_INPUTS.values():
            self.assertEqual(len(row["sha256"]), 64)
            int(row["sha256"], 16)


if __name__ == "__main__":
    unittest.main()
