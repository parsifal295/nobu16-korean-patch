from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_battle_merit_badges_native_repair_v1.py")
SPEC = importlib.util.spec_from_file_location("battle_merit_badges_native_repair_v1", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class MappingContractTests(unittest.TestCase):
    def test_contract(self) -> None:
        builder.validate_mapping_contract()

    def test_each_low_target_is_exact_half_of_high_target(self) -> None:
        for row in builder.BADGES:
            high_width, high_height = builder.rect_dimensions(row["high_target_rect"])
            low_width, low_height = builder.rect_dimensions(row["low_target_rect"])
            self.assertEqual((high_width, high_height), (low_width * 2, low_height * 2))

    def test_high_repair_unions_do_not_overlap(self) -> None:
        unions = [
            builder.rect_union(row["high_source_rect"], row["high_target_rect"])
            for row in builder.BADGES
        ]
        for index, left in enumerate(unions):
            for right in unions[index + 1 :]:
                self.assertFalse(builder.rectangles_overlap(left, right))

    def test_low_targets_do_not_overlap(self) -> None:
        targets = [row["low_target_rect"] for row in builder.BADGES]
        for index, left in enumerate(targets):
            for right in targets[index + 1 :]:
                self.assertFalse(builder.rectangles_overlap(left, right))

    def test_rect_contains(self) -> None:
        self.assertTrue(builder.rect_contains((0, 0, 10, 10), (1, 2, 9, 8)))
        self.assertFalse(builder.rect_contains((0, 0, 10, 10), (-1, 2, 9, 8)))

    def test_expected_input_hashes_are_full_sha256(self) -> None:
        for row in builder.EXPECTED_INPUTS.values():
            self.assertEqual(len(row["sha256"]), 64)
            int(row["sha256"], 16)

    def test_routes_are_fixed(self) -> None:
        self.assertEqual(builder.HIGH_OUTER, 17)
        self.assertEqual(builder.LOW_OUTER, 12)
        self.assertEqual(builder.RESOURCE_ID, 58)
        self.assertEqual(builder.HIGH_GEOMETRY, (4096, 1024))
        self.assertEqual(builder.LOW_GEOMETRY, (2048, 512))


if __name__ == "__main__":
    unittest.main()
