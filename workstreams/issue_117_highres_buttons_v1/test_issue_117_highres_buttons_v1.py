from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_issue_117_highres_buttons_v1.py")
SPEC = importlib.util.spec_from_file_location("issue_117_highres_buttons_v1", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Issue117HighresButtonsTests(unittest.TestCase):
    def test_approve_all_cells_are_block_aligned_and_in_bounds(self) -> None:
        self.assertEqual(len(MODULE.APPROVE_ALL_CELLS), 6)
        self.assertEqual({row["style"] for row in MODULE.APPROVE_ALL_CELLS}, {"cyan", "blue", "white", "disabled"})
        for row in MODULE.APPROVE_ALL_CELLS:
            left, top, right, bottom = row["rect"]
            self.assertEqual((right - left, bottom - top), (368, 160))
            self.assertTrue(all(value % 4 == 0 for value in row["rect"]))
            self.assertTrue(0 <= left < right <= 4096)
            self.assertTrue(0 <= top < bottom <= 1024)

    def test_battle_targets_are_seven_disjoint_native_components(self) -> None:
        self.assertEqual(len(MODULE.BATTLE_TARGET_RECTS), 7)
        self.assertEqual(len(MODULE.BATTLE_SOURCE_PINS), 7)
        previous_right = 0
        for state, rect in enumerate(MODULE.BATTLE_TARGET_RECTS):
            left, top, right, bottom = rect
            self.assertGreaterEqual(left, previous_right)
            self.assertLessEqual(right, 4096)
            self.assertLessEqual(bottom, 2048)
            self.assertEqual((right - left, bottom - top), (508, 154) if state == 0 else (493, 146))
            previous_right = right

    def test_release_pins_are_uppercase_sha256(self) -> None:
        values = [MODULE.PORT1_PIN["sha256"], MODULE.PORT2_PIN["sha256"], MODULE.FONT_PIN, *MODULE.BATTLE_SOURCE_PINS]
        self.assertTrue(all(len(value) == 64 and value == value.upper() for value in values))


if __name__ == "__main__":
    unittest.main()
