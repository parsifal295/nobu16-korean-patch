from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MODULE_PATH = TOOLS / "build_pc_title_images_candidate.py"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location(
    "build_pc_title_images_candidate", MODULE_PATH
)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def rgba_canvas(width: int, height: int) -> bytearray:
    return bytearray(width * height * 4)


def set_pixel(
    rgba: bytearray,
    width: int,
    x: int,
    y: int,
    value: tuple[int, int, int, int],
) -> None:
    position = (y * width + x) * 4
    rgba[position : position + 4] = bytes(value)


class PcTitleImageCandidateTests(unittest.TestCase):
    def test_semantic_source_plan_is_the_audited_108_entry_plan(self) -> None:
        self.assertEqual(builder.TARGET_COUNT, 108)
        self.assertEqual(builder.SOURCE_REMAP, {0: 3, 24: 25, 25: 24})
        self.assertEqual(
            builder.CORRECTED_LABELS,
            {38: "\ubd80\ub300 \ud3b8\uc131", 74: "\uacf5\uc8fc \uc815\ubcf4"},
        )

        plan: dict[int, tuple[str, int | None]] = {}
        for target in range(builder.TARGET_COUNT):
            if target in builder.CORRECTED_LABELS:
                plan[target] = ("corrected_render", None)
            else:
                plan[target] = (
                    "switch_v13",
                    builder.SOURCE_REMAP.get(target, target),
                )

        counts = Counter(
            "corrected"
            if source is None
            else "same_index"
            if source == target
            else "cross_index"
            for target, (_, source) in plan.items()
        )
        self.assertEqual(
            counts,
            {"same_index": 103, "cross_index": 3, "corrected": 2},
        )
        self.assertEqual(plan[0], ("switch_v13", 3))
        self.assertEqual(plan[15], ("switch_v13", 15))
        self.assertEqual(plan[24], ("switch_v13", 25))
        self.assertEqual(plan[25], ("switch_v13", 24))
        self.assertEqual(plan[37], ("switch_v13", 37))
        self.assertEqual(plan[38], ("corrected_render", None))
        self.assertEqual(plan[74], ("corrected_render", None))

    def test_alpha_bbox_and_crop_preserve_only_the_inclusive_ink_box(self) -> None:
        width, height = 5, 4
        source = rgba_canvas(width, height)
        set_pixel(source, width, 1, 1, (10, 20, 30, 255))
        set_pixel(source, width, 3, 2, (40, 50, 60, 128))

        bbox = builder.alpha_bbox(bytes(source), width, height)
        self.assertEqual(bbox, (1, 1, 3, 2))
        cropped, crop_width, crop_height = builder.crop_rgba(
            bytes(source), width, height, bbox
        )

        self.assertEqual((crop_width, crop_height), (3, 2))
        self.assertEqual(cropped[:4], bytes((10, 20, 30, 255)))
        self.assertEqual(cropped[-4:], bytes((40, 50, 60, 128)))
        self.assertEqual(builder.alpha_bbox(cropped, crop_width, crop_height), (0, 0, 2, 1))

    def test_alpha_bbox_rejects_empty_or_malformed_rgba(self) -> None:
        with self.assertRaisesRegex(builder.BatchError, "no non-transparent pixels"):
            builder.alpha_bbox(bytes(3 * 2 * 4), 3, 2)
        with self.assertRaisesRegex(builder.BatchError, "byte length"):
            builder.alpha_bbox(b"\0" * 7, 3, 2)

    def test_height_scale_and_top_left_placement_are_deterministic(self) -> None:
        source = bytes((12, 34, 56, 200)) * (2 * 2)
        first = builder.resize_rgba_lanczos3_premultiplied(source, 2, 2, 6, 4)
        second = builder.resize_rgba_lanczos3_premultiplied(source, 2, 2, 6, 4)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 6 * 4 * 4)
        self.assertEqual(
            {tuple(first[position : position + 4]) for position in range(0, len(first), 4)},
            {(12, 34, 56, 200)},
        )

        canvas, clipped = builder.paste_clipped(first, 6, 4, 12, 8, 3, 2)
        self.assertEqual(clipped, 0)
        self.assertEqual(builder.alpha_bbox(canvas, 12, 8), (3, 2, 8, 5))

    def test_paste_clipped_counts_only_nontransparent_pixels_outside_canvas(self) -> None:
        source = bytearray(bytes((1, 2, 3, 255)) * (2 * 2))
        set_pixel(source, 2, 0, 0, (99, 88, 77, 0))

        canvas, clipped = builder.paste_clipped(
            bytes(source), 2, 2, 2, 2, -1, 1
        )

        self.assertEqual(clipped, 2)
        self.assertEqual(builder.alpha_bbox(canvas, 2, 2), (0, 1, 0, 1))

    def test_output_root_is_confined_to_repository_tmp(self) -> None:
        with tempfile.TemporaryDirectory(prefix="n16_title_outside_") as temporary:
            outside = Path(temporary) / "candidate"
            with self.assertRaisesRegex(builder.BatchError, "must stay under"):
                builder.ensure_private_output_root(outside)
            self.assertFalse(outside.exists())

        builder.TMP_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="n16_title_inside_", dir=builder.TMP_ROOT
        ) as temporary:
            inside = Path(temporary) / "candidate"
            resolved = builder.ensure_private_output_root(inside)
            self.assertEqual(resolved, inside.resolve())
            self.assertTrue(resolved.is_dir())


if __name__ == "__main__":
    unittest.main()
