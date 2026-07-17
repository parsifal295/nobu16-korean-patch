from __future__ import annotations

import importlib.util
import struct
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_steam_jp_port_highres_images_v1.py")
SPEC = importlib.util.spec_from_file_location("port_highres_builder", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class NestedLinkTests(unittest.TestCase):
    @staticmethod
    def fixture() -> bytes:
        fixed = bytearray(32)
        struct.pack_into("<4s4I", fixed, 0, b"LINK", 2, 32, 77, 64)
        output = fixed + bytearray(16) + bytearray(b"P" * 16)
        first_offset = len(output)
        output.extend(b"abc")
        output.extend(b"G")
        second_offset = len(output)
        output.extend(b"defg")
        output.extend(b"TT")
        struct.pack_into("<II", output, 32, first_offset, 3)
        struct.pack_into("<II", output, 40, second_offset, 4)
        return bytes(output)

    def test_identity_and_gap_preservation(self) -> None:
        original = self.fixture()
        parsed = builder.parse_nested_link(original, expected_resource_id=77)
        self.assertEqual(builder.rebuild_nested_link(parsed), original)
        rebuilt = builder.rebuild_nested_link(parsed, {0: b"longer"})
        reparsed = builder.parse_nested_link(rebuilt, expected_resource_id=77)
        self.assertEqual(reparsed.entries[0].data, b"longer")
        self.assertEqual(reparsed.entries[0].gap_after, b"G")
        self.assertEqual(reparsed.entries[1].data, b"defg")
        self.assertEqual(reparsed.entries[1].gap_after, b"TT")


class DeltaLiftTests(unittest.TestCase):
    def texture(self, rgba: bytes, width: int, height: int, index: int = 0):
        payload, _, _ = builder.codec.encode_bc3(rgba, width, height)
        return builder.atlas_codec.Texture(index, 0x5B, width, height, 1, 0, 0, payload)

    def test_one_low_pixel_maps_to_one_high_block(self) -> None:
        low_before = bytes((0, 0, 0, 255)) * 4
        low_after = bytearray(low_before)
        low_after[0:4] = bytes((255, 255, 255, 255))
        high = bytes((180, 20, 20, 255)) * 16
        before_texture = self.texture(low_before, 2, 2)
        after_texture = self.texture(bytes(low_after), 2, 2)
        high_texture = self.texture(high, 4, 4)
        payload, report = builder.lift_bc3_delta_2x(
            low_before=before_texture,
            low_after=after_texture,
            high_template=high_texture,
        )
        self.assertEqual(len(payload), 16)
        self.assertNotEqual(payload, high_texture.payload)
        self.assertEqual(report["allowed_high_bc3_blocks"], 1)
        self.assertEqual(report["changed_high_block_bbox"], [0, 0, 1, 1])


if __name__ == "__main__":
    unittest.main()
