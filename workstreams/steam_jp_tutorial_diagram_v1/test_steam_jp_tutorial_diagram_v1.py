#!/usr/bin/env python3
"""Unit tests for the bounded Steam-JP tutorial-diagram candidate builder."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
for path in (WORKSTREAM, TOOLS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

SPEC = importlib.util.spec_from_file_location(
    "steam_jp_tutorial_diagram_v1_builder",
    WORKSTREAM / "build_steam_jp_tutorial_diagram_v1.py",
)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class TutorialDiagramBuilderTests(unittest.TestCase):
    def test_scope_explicitly_excludes_title_and_logo_entries(self) -> None:
        self.assertEqual(BUILDER.OUTER_INDEX, 16)
        self.assertEqual(BUILDER.TARGET_RESOURCE, "RES_JP/res_lang.bin")
        self.assertNotIn(3, (BUILDER.OUTER_INDEX,))
        self.assertNotIn(24, (BUILDER.OUTER_INDEX,))
        self.assertEqual([row["name"] for row in BUILDER.PANEL_MAPPINGS], ["progress_flow", "faction_hierarchy"])

    def test_tutorial_link_roundtrip_preserves_non_wrapper_bytes(self) -> None:
        fixed = b"LINK" + (1).to_bytes(4, "little") + (32).to_bytes(4, "little") + (64).to_bytes(4, "little") + (64).to_bytes(4, "little") + b"\0" * 12
        wrapper = b"old-wrapper"
        pre_slot = b"\0" * 24
        tail = b"tail"
        blob = fixed + (64).to_bytes(4, "little") + len(wrapper).to_bytes(4, "little") + pre_slot + wrapper + tail
        link = BUILDER.parse_tutorial_link(blob, label="synthetic")
        self.assertEqual(BUILDER.rebuild_tutorial_link(link, wrapper), blob)
        rebuilt = BUILDER.rebuild_tutorial_link(link, b"new")
        reparsed = BUILDER.parse_tutorial_link(rebuilt, label="synthetic rebuilt")
        self.assertEqual(reparsed.wrapper, b"new")
        self.assertEqual(reparsed.fixed_header, fixed)
        self.assertEqual(reparsed.pre_slot, pre_slot)
        self.assertEqual(reparsed.tail, tail)

    def test_changed_block_detection_is_bc3_granular(self) -> None:
        before = bytes(8 * 8 * 4)
        after = bytearray(before)
        after[(5 * 8 + 5) * 4 : (5 * 8 + 5) * 4 + 4] = b"\x10\x20\x30\x40"
        self.assertEqual(BUILDER.changed_bc3_blocks(before, bytes(after), 8, 8), {(1, 1)})

    def test_nearest_resize_is_deterministic(self) -> None:
        source = bytes((10, 0, 0, 255, 20, 0, 0, 255, 30, 0, 0, 255, 40, 0, 0, 255))
        output = BUILDER.resize_rgba_nearest(source, 2, 2, 4, 4)
        self.assertEqual(len(output), 4 * 4 * 4)
        self.assertEqual(output[:4], bytes((10, 0, 0, 255)))
        self.assertEqual(output[(3 * 4 + 3) * 4 : (3 * 4 + 3) * 4 + 4], bytes((40, 0, 0, 255)))

    def test_selected_encoder_cannot_change_unallowed_blocks(self) -> None:
        width = height = 8
        original_rgba = bytes((20, 40, 60, 255)) * (width * height)
        block = BUILDER.codec.encode_bc3_block(original_rgba[:64])
        template = block * 4
        requested = bytearray(original_rgba)
        requested[(5 * width + 5) * 4 : (5 * width + 5) * 4 + 4] = bytes((200, 10, 40, 255))
        rebuilt, preserved, encoded = BUILDER.encode_selected_bc3_blocks(bytes(requested), width, height, template, {(1, 1)})
        self.assertEqual(rebuilt[:48], template[:48])
        self.assertNotEqual(rebuilt[48:64], template[48:64])
        self.assertEqual(preserved, 3)
        self.assertEqual(encoded, 1)

    def test_tmp_lexical_escape_is_rejected_before_write(self) -> None:
        with self.assertRaises(BUILDER.TutorialDiagramError):
            BUILDER.lexical_tmp_path(REPO / "outside-tmp")


if __name__ == "__main__":
    unittest.main(verbosity=2)
