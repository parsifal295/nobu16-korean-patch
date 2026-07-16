"""Unit checks for the bounded Steam-JP system-button workstream.

These tests intentionally use synthetic RGBA/LINK values only.  They do not
read a game installation, a Switch archive, or a private candidate.
"""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_steam_jp_system_buttons_v1.py")
MAPPING_PATH = Path(__file__).with_name("mapping.v1.json")
SPEC = importlib.util.spec_from_file_location("steam_jp_system_buttons_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MappingContractTests(unittest.TestCase):
    def test_eight_core_labels_and_eleven_disjoint_next_batch_labels(self) -> None:
        MODULE.mapping_contract()
        self.assertEqual(
            {row["label_ko"] for row in MODULE.MAPPINGS},
            {"닫기", "중지", "결정", "거부", "뒤로", "아니오", "건너뛰기", "예"},
        )
        self.assertEqual(len(MODULE.MAPPINGS), 8)
        self.assertEqual(
            {row["label_ko"] for row in MODULE.NEXT_BATCH_MAPPINGS},
            {"전부개방", "희", "지휘", "재교섭", "승낙", "처단", "등용", "무장", "다음", "승인", "부인"},
        )
        self.assertEqual(len(MODULE.NEXT_BATCH_MAPPINGS), 11)
        self.assertNotIn("다음", {row["label_ko"] for row in MODULE.MAPPINGS})
        self.assertIn("다음", {row["label_ko"] for row in MODULE.NEXT_BATCH_MAPPINGS})
        self.assertNotIn("다음", MODULE.DEFERRED_LABELS_KO)

    def test_block_expansion_is_bc3_aligned(self) -> None:
        self.assertEqual(MODULE.block_expanded((5, 9, 17, 20)), (4, 8, 20, 20))

    def test_public_mapping_metadata_matches_the_executable_contract(self) -> None:
        metadata = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "audit-only")
        self.assertFalse(MODULE.CANDIDATE_GENERATION_ENABLED)
        self.assertFalse(MODULE.GAME_INSTALL_WRITE_ENABLED)
        self.assertFalse(MODULE.GIT_OR_RELEASE_WRITE_ENABLED)
        self.assertFalse(metadata["candidate_gate"]["candidate_generation_enabled"])
        self.assertFalse(metadata["candidate_gate"]["game_install_write_allowed"])
        self.assertFalse(metadata["candidate_gate"]["git_or_release_write_allowed"])
        self.assertEqual(metadata["candidate_gate"]["strict_pc_donor_study"]["result"], "NO / defer")
        self.assertIn("뒤로", metadata["candidate_gate"]["strict_pc_donor_study"]["candidate_exclusion_until_screen_qa"])
        self.assertEqual(
            {key: metadata["target"]["baseline"][key] for key in MODULE.BASELINE},
            MODULE.BASELINE,
        )
        self.assertEqual(
            [row["label_ko"] for row in metadata["confirmed_mappings"]],
            [row["label_ko"] for row in MODULE.MAPPINGS],
        )
        self.assertEqual(
            [row["label_ko"] for row in metadata["next_batch_confirmed_mappings"]],
            [row["label_ko"] for row in MODULE.NEXT_BATCH_MAPPINGS],
        )
        self.assertEqual(
            [
                (row["label_ko"], row["state"], row["switch_source_cell"], row["pc_target_cell"], row["pc_target_has_icon"])
                for row in metadata["next_batch_confirmed_mappings"]
            ],
            [
                (row["label_ko"], row["state"], list(row["source_cell"]), list(row["target_cell"]), row["target_has_icon"])
                for row in MODULE.NEXT_BATCH_MAPPINGS
            ],
        )
        self.assertEqual(
            [
                (row["label_ko"], row["switch_source_cell"], row["pc_target_cell"], row["reason"])
                for row in metadata["invalid_or_deferred_core_mappings"]
            ],
            [
                (row["label_ko"], list(row["source_cell"]), list(row["target_cell"]), row["reason"])
                for row in MODULE.INVALID_CORE_MAPPINGS
            ],
        )
        self.assertFalse(metadata["invalid_or_deferred_core_mappings"][0]["candidate_eligible"])
        self.assertEqual(metadata["deferred"]["labels_ko"], list(MODULE.DEFERRED_LABELS_KO))

    def test_candidate_generation_is_hard_gated_before_any_input_access(self) -> None:
        with self.assertRaisesRegex(MODULE.SystemButtonsError, "candidate generation is disabled"):
            MODULE.build_candidate(
                baseline=Path("not-read.bin"),
                switch_v21_zip=Path("not-read-v21.zip"),
                switch_v22_zip=Path("not-read-v22.zip"),
                output_root=Path("KR_PATCH_WORK/tmp/never-created"),
            )


class RasterHelperTests(unittest.TestCase):
    def test_resize_mask_nearest_preserves_binary_quadrants(self) -> None:
        source = bytearray((0, 1, 1, 0))
        resized = MODULE.resize_mask_nearest(source, 2, 2, 4, 4)
        self.assertEqual(len(resized), 16)
        self.assertEqual(resized[0], 0)
        self.assertEqual(resized[3], 1)
        self.assertEqual(resized[12], 1)
        self.assertEqual(resized[15], 0)

    def test_korean_foreground_keeps_only_changed_text_like_pixels(self) -> None:
        width = height = 8
        jp = bytearray((96, 112, 128, 255) * (width * height))
        ko = bytearray(jp)
        for y in range(2, 5):
            for x in range(2, 5):
                point = (y * width + x) * 4
                ko[point : point + 4] = bytes((12, 12, 12, 255))
        foreground, active = MODULE.korean_glyph_foreground(bytes(jp), bytes(ko), width, height)
        self.assertGreaterEqual(active, 24)
        self.assertEqual(foreground[3], 0)
        self.assertGreater(foreground[((3 * width + 3) * 4) + 3], 0)

    def test_masked_inpaint_changes_only_requested_pixels(self) -> None:
        width = height = 8
        target = bytearray()
        for y in range(height):
            for x in range(width):
                target.extend((x * 17, y * 19, 80, 255))
        before = bytes(target)
        box = (1, 1, 7, 7)
        mask = bytearray(36)
        mask[(3 * 6) + 3] = 1
        glyph = ((1 + 3) * width + 1 + 3) * 4
        target[glyph : glyph + 4] = bytes((255, 0, 255, 125))
        before = bytes(target)
        changed = MODULE.inpaint_masked_pc_glyphs(target, width, box, mask)
        self.assertEqual(changed, 1)
        self.assertEqual(target[: (1 * width + 1) * 4], before[: (1 * width + 1) * 4])
        self.assertNotEqual(target[((1 + 3) * width + 1 + 3) * 4 : ((1 + 3) * width + 1 + 4) * 4], before[((1 + 3) * width + 1 + 3) * 4 : ((1 + 3) * width + 1 + 4) * 4])

    def test_draw_rect_has_four_edges(self) -> None:
        rgba = bytearray(8 * 8 * 4)
        MODULE.draw_rect(rgba, 8, 8, (2, 2, 6, 6), (1, 2, 3, 4))
        self.assertEqual(rgba[(3 * 8 + 2) * 4 : (3 * 8 + 2) * 4 + 4], bytes((1, 2, 3, 4)))
        self.assertEqual(rgba[(3 * 8 + 5) * 4 : (3 * 8 + 5) * 4 + 4], bytes((1, 2, 3, 4)))


class BundleTests(unittest.TestCase):
    def test_one_slot_system_bundle_roundtrips(self) -> None:
        wrapper = b"private-wrapper"
        tail = b"tail"
        header = b"LINK" + struct.pack("<4I", 1, 32, 3856, 64) + (b"\0" * 12)
        blob = header + struct.pack("<II", 64, len(wrapper)) + (b"\0" * 24) + wrapper + tail
        bundle = MODULE.parse_system_bundle(blob)
        self.assertEqual(bundle.wrapper, wrapper)
        self.assertEqual(MODULE.rebuild_system_bundle(bundle, wrapper), blob)


if __name__ == "__main__":
    unittest.main()
