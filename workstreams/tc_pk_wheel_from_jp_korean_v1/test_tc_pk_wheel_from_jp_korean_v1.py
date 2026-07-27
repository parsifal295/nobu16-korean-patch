#!/usr/bin/env python3

from __future__ import annotations

import unittest

import build_tc_pk_wheel_from_jp_korean_v1 as target


class TcPkWheelFromJpKoreanTests(unittest.TestCase):
    def test_detail_groups_cover_all_non_main_active_records(self) -> None:
        groups = target.detail_group_records()
        self.assertEqual(len(groups), 12)
        self.assertTrue(all(len(group) == 6 for group in groups))
        flattened = [record for group in groups for record in group]
        self.assertEqual(flattened, list(range(6)) + list(range(12, 78)))

    def test_active_records_are_exactly_zero_through_seventy_seven(self) -> None:
        self.assertEqual(target.active_records(), list(range(78)))

    def test_record_rect_adds_four_pixel_guard_on_every_side(self) -> None:
        self.assertEqual(target.record_rect((100, 200, 96, 88, 0)), (96, 196, 200, 292))
        self.assertEqual(target.record_rect((4, 4, 192, 176, 0)), (0, 0, 200, 184))

    def test_invalid_active_record_is_rejected(self) -> None:
        with self.assertRaises(target.WheelTransplantError):
            target.record_rect((0, 0, 0, 0, 0))

    def test_all_labels_have_six_state_groups(self) -> None:
        self.assertEqual(len(target.DETAIL_LABELS), len(target.detail_group_records()))
        self.assertEqual(target.DETAIL_LABELS[7], "보급거점")
        self.assertEqual(target.MAIN_LABEL, "광역")


if __name__ == "__main__":
    unittest.main()
