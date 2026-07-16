"""Unit tests for the source-free Steam-JP title-image candidate builder."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
SCRIPT = WORKSTREAM / "build_steam_jp_title_images_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_title_images_v1", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SteamJpTitleImagesV1Tests(unittest.TestCase):
    def test_jp_resource_and_slot_contract_are_exact(self) -> None:
        self.assertEqual(MODULE.TARGET_RESOURCE, "RES_JP/res_lang.bin")
        self.assertEqual(MODULE.OUTER_TITLE_INDEX, 3)
        self.assertEqual(MODULE.TARGET_COUNT, 108)
        self.assertEqual(MODULE.TAIL_INDICES, (108, 109))
        self.assertEqual(MODULE.PC_WIDTH, 512)
        self.assertEqual(MODULE.PC_HEIGHT, 128)

    def test_semantic_source_selection_is_fail_closed(self) -> None:
        self.assertEqual(MODULE.select_source(0), ("switch_v13", 3))
        self.assertEqual(MODULE.select_source(24), ("switch_v13", 25))
        self.assertEqual(MODULE.select_source(25), ("switch_v13", 24))
        self.assertEqual(MODULE.select_source(38), ("corrected", None))
        self.assertEqual(MODULE.select_source(74), ("corrected", None))
        self.assertEqual(MODULE.select_source(107), ("switch_v13", 107))
        with self.assertRaises(MODULE.TitleCandidateError):
            MODULE.select_source(-1)
        with self.assertRaises(MODULE.TitleCandidateError):
            MODULE.select_source(108)

    def test_pins_have_exact_shape(self) -> None:
        for pin in (MODULE.EXPECTED_JP_STOCK, MODULE.EXPECTED_JP_CANDIDATE):
            self.assertIsInstance(pin["size"], int)
            self.assertGreater(pin["size"], 0)
            self.assertEqual(len(pin["sha256"]), 64)
            self.assertEqual(pin["sha256"], pin["sha256"].upper())
        self.assertEqual(len(MODULE.EXPECTED_CORRECTED_PNG_SHA256), 2)
        for digest in MODULE.EXPECTED_CORRECTED_PNG_SHA256.values():
            self.assertEqual(len(digest), 64)

    def test_final_output_paths_cannot_escape_tmp(self) -> None:
        safe = MODULE.ensure_tmp_output_path(MODULE.TMP_ROOT / "title-images-test" / "x.bin")
        self.assertTrue(safe.is_relative_to(MODULE.TMP_ROOT.resolve()))
        with self.assertRaises(MODULE.TitleCandidateError):
            MODULE.ensure_tmp_output_path(MODULE.REPO / "not-tmp" / "x.bin")

    def test_alpha_crop_resize_and_paste_preserve_origin(self) -> None:
        # A tiny opaque 2x2 image at (1, 1) exercises the reusable placement
        # primitives without requiring any game or third-party input.
        rgba = bytearray(4 * 4 * 4)
        for y in (1, 2):
            for x in (1, 2):
                offset = (y * 4 + x) * 4
                rgba[offset : offset + 4] = bytes((200, 100, 50, 255))
        bbox = MODULE.alpha_bbox(bytes(rgba), 4, 4)
        self.assertEqual(bbox, (1, 1, 2, 2))
        cropped, width, height = MODULE.crop_rgba(bytes(rgba), 4, 4, bbox)
        self.assertEqual((width, height), (2, 2))
        resized = MODULE.resize_rgba_lanczos3_premultiplied(cropped, width, height, 4, 4)
        canvas, clipped = MODULE.paste_clipped(resized, 4, 4, 8, 8, 2, 3)
        self.assertEqual(clipped, 0)
        self.assertEqual(MODULE.alpha_bbox(canvas, 8, 8)[:2], (2, 3))

    def test_source_free_files_never_reference_sc_raw_route(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("RES_SC", source)
        validation = json.loads((WORKSTREAM / "validation.v1.json").read_text(encoding="utf-8"))
        self.assertTrue(validation["source_free"])
        self.assertTrue(validation["file_only"])
        self.assertFalse(validation["game_install_modified"])
        self.assertEqual(
            validation["pins"]["steam_jp_font_baseline"], MODULE.EXPECTED_JP_STOCK
        )
        self.assertEqual(
            validation["pins"]["steam_jp_title_candidate"], MODULE.EXPECTED_JP_CANDIDATE
        )
        self.assertTrue(
            validation["candidate_verification"]["tail_slots_108_109_byte_preserved"]
        )
        self.assertTrue(
            validation["candidate_verification"]["unrelated_outer_entries_byte_preserved"]
        )
        self.assertTrue(validation["constraints"]["output_paths_resolve_under_tmp"])
        rendered = json.dumps(validation, ensure_ascii=False)
        self.assertNotIn("RES_SC", rendered)
        self.assertNotIn("F:\\\\", rendered)


if __name__ == "__main__":
    unittest.main()
