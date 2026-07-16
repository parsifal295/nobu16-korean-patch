#!/usr/bin/env python3
"""Unit tests for the source-free Steam-JP title image visual QA helper."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import visual_qa_steam_jp_title_images_v1 as qa  # noqa: E402


def rgba(width: int, height: int, visible: set[tuple[int, int]]) -> bytes:
    output = bytearray(width * height * 4)
    for x, y in visible:
        at = (y * width + x) * 4
        output[at : at + 4] = bytes((255, 255, 255, 255))
    return bytes(output)


class VisualQaTests(unittest.TestCase):
    def test_source_mapping_keeps_the_semantic_remaps(self) -> None:
        self.assertEqual(qa.source_plan(0)["source_index"], 3)
        self.assertEqual(qa.source_plan(24)["source_index"], 25)
        self.assertEqual(qa.source_plan(25)["source_index"], 24)
        self.assertEqual(qa.source_plan(38)["expected_label"], "부대 편성")
        self.assertEqual(qa.source_plan(74)["expected_label"], "공주 정보")

    def test_alpha_bbox_and_crop_are_exact(self) -> None:
        image = rgba(4, 3, {(1, 1), (3, 2)})
        self.assertEqual(qa.alpha_bbox(image, 4, 3), (1, 1, 3, 2))
        cropped, width, height = qa.crop_rgba(image, 4, 3, (1, 1, 3, 2))
        self.assertEqual((width, height), (3, 2))
        self.assertEqual(qa.alpha_bbox(cropped, width, height), (0, 0, 2, 1))

    def test_paste_reports_clipping_instead_of_silently_losing_ink(self) -> None:
        image = rgba(2, 1, {(0, 0), (1, 0)})
        pasted, clipped = qa.paste_rgba(image, 2, 1, -1, 0, target_width=2, target_height=1)
        self.assertEqual(clipped, 1)
        self.assertEqual(qa.alpha_bbox(pasted, 2, 1), (0, 0, 0, 0))

    def test_visual_metrics_detects_stray_visible_noise(self) -> None:
        expected = rgba(qa.PC_WIDTH, qa.PC_HEIGHT, {(10, 10), (11, 10)})
        actual = rgba(qa.PC_WIDTH, qa.PC_HEIGHT, {(10, 10), (11, 10), (500, 100)})
        metrics = qa.visual_metrics(expected, actual)
        self.assertEqual(metrics["candidate_only_visible_pixels"], 1)
        self.assertEqual(
            metrics["candidate_only_visible_pixels_farther_than_codec_fringe_radius"], 1
        )
        self.assertLess(metrics["visible_mask_iou"], 1.0)
        self.assertFalse(
            qa.assessment(metrics)["no_stray_visible_noise_farther_than_codec_fringe_radius"]
        )

    def test_checkerboard_and_contact_sheet_are_opaque_and_sized(self) -> None:
        image = rgba(qa.PC_WIDTH, qa.PC_HEIGHT, {(0, 0), (1, 0)})
        panel, width, height = qa.bordered_panel(image, (1, 2, 3, 255))
        self.assertEqual((width, height), (1024, 256))
        self.assertTrue(all(panel[offset + 3] == 255 for offset in range(0, len(panel), 4)))
        sheet, sheet_width, sheet_height = qa.contact_sheet(
            [{"slot": 0, "expected_rgba": image, "candidate_rgba": image}]
        )
        self.assertGreater(sheet_width, width)
        self.assertGreater(sheet_height, height)
        self.assertTrue(all(sheet[offset + 3] == 255 for offset in range(0, len(sheet), 4)))


if __name__ == "__main__":
    unittest.main()
