#!/usr/bin/env python3
"""Pure LINK-contract tests for the private non-logo text-fit compositor."""

from __future__ import annotations

import importlib.util
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_nonlogo_textfit_composite_v1_under_test",
    ROOT / "build_steam_jp_nonlogo_textfit_composite_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def synthetic_link(count: int = 25) -> bytes:
    fixed = b"LINK" + struct.pack("<III", count, 1, 0)
    table = bytearray(count * 8)
    body = bytearray()
    offset = len(fixed) + len(table)
    for index in range(count):
        data = f"outer-{index}".encode("ascii")
        gap = bytes((0x90 + (index % 8),))
        struct.pack_into("<II", table, index * 8, offset, len(data))
        body.extend(data)
        body.extend(gap)
        offset += len(data) + len(gap)
    return fixed + bytes(table) + bytes(body)


def replace(blob: bytes, replacements: dict[int, bytes]) -> bytes:
    archive = MODULE.parse_link(blob)
    return MODULE.rebuild_link(archive, replacements)


class NonLogoTextfitCompositeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = synthetic_link()
        self.image = replace(
            self.baseline,
            {
                3: b"existing-title-image",
                8: b"existing-wheel-image",
                12: b"existing-military-image",
                13: b"existing-banner-image",
                16: b"existing-tutorial-image",
                24: b"existing-logo-image",
            },
        )
        self.font = replace(self.baseline, {6: b"font-tier-6-compact", 7: b"font-tier-7-compact"})

    def test_only_font_outers_change_and_protected_pairs_are_preserved(self) -> None:
        result, report = MODULE.compose_res_jp_font(self.image, self.baseline, self.font)
        before = MODULE.parse_link(self.image)
        after = MODULE.parse_link(result)
        self.assertEqual(MODULE._changed_entries(before, after), {6, 7})
        self.assertEqual(report["changed_outer_entries"], [6, 7])
        for outer in (3, 8, 12, 13, 16, 24):
            self.assertEqual(MODULE._entry_pair(after, outer), MODULE._entry_pair(before, outer))

    def test_image_font_preimage_drift_is_rejected(self) -> None:
        drifted_image = replace(self.image, {6: b"unreviewed-image-font"})
        with self.assertRaises(MODULE.CompositeError):
            MODULE.compose_res_jp_font(drifted_image, self.baseline, self.font)

    def test_font_candidate_nonfont_change_is_rejected(self) -> None:
        unsafe_font = replace(self.font, {24: b"must-never-be-a-font-replacement"})
        with self.assertRaises(MODULE.CompositeError):
            MODULE.compose_res_jp_font(self.image, self.baseline, unsafe_font)

    def test_title_and_logo_are_disjoint_from_font_targets(self) -> None:
        self.assertTrue(
            set(MODULE.PROTECTED_LOGO_TITLE_OUTERS).isdisjoint(MODULE.IMAGE_FONT_OUTERS)
        )
        self.assertEqual(MODULE.PROTECTED_LOGO_TITLE_OUTERS, (3, 24))
        self.assertEqual(MODULE.IMAGE_FONT_OUTERS, (6, 7))


if __name__ == "__main__":
    unittest.main()
