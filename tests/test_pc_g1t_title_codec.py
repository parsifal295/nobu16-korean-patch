from __future__ import annotations

import importlib.util
import struct
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "pc_g1t_title_codec.py"
SPEC = importlib.util.spec_from_file_location("pc_g1t_title_codec", MODULE_PATH)
assert SPEC and SPEC.loader
codec = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = codec
SPEC.loader.exec_module(codec)


def make_g1t(bc3: bytes) -> bytes:
    texture_header = bytes.fromhex(
        "10 5B 79 00 11 11 01 10 0C 00 00 00 00 00 00 00 00 00 01 00"
    )
    raw = (
        codec.G1T_MAGIC_VERSION
        + b"\0" * 24
        + struct.pack("<I", 4)
        + texture_header
        + bc3
    )
    mutable = bytearray(raw)
    struct.pack_into("<4I", mutable, 8, len(raw), 0x20, 1, 0x0A)
    return bytes(mutable)


def make_inner(entries: list[bytes]) -> bytes:
    count = len(entries)
    table_end = 0x20 + count * 8
    first_offset = codec.align_up(table_end, 0x20)
    output = bytearray(
        b"LINK"
        + struct.pack("<4I", count, 0x20, count, codec.align_up(table_end, 0x20))
        + b"\0" * 12
        + b"\0" * (count * 8)
        + b"\0" * (first_offset - table_end)
    )
    pairs = []
    for index, entry in enumerate(entries):
        pairs.append((len(output), len(entry)))
        output.extend(entry)
        if index + 1 < count:
            output.extend(b"\0" * (codec.align_up(len(output), 0x20) - len(output)))
    for index, pair in enumerate(pairs):
        struct.pack_into("<II", output, 0x20 + index * 8, *pair)
    return bytes(output)


def make_outer(title_inner: bytes) -> bytes:
    entries = [b"zero", b"one", b"two", title_inner]
    count = len(entries)
    output = bytearray(b"LINK" + struct.pack("<III", count, 1, 0) + b"\0" * (count * 8))
    pairs = []
    for entry in entries:
        pairs.append((len(output), len(entry)))
        output.extend(entry)
        output.extend(codec.LZ4.LINK_ENTRY_TRAILER)
    for index, pair in enumerate(pairs):
        struct.pack_into("<II", output, 16 + index * 8, *pair)
    return bytes(output)


class PcG1tTitleCodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.block = bytes((255, 255)) + b"\0" * 6 + struct.pack("<HHI", 0xF800, 0xF800, 0)
        cls.bc3 = cls.block * (codec.EXPECTED_WIDTH // 4) * (codec.EXPECTED_HEIGHT // 4)
        cls.g1t = make_g1t(cls.bc3)
        cls.wrapper = codec.LZ4.recompress_wrapper(
            cls.g1t,
            codec.LZ4.WrapperHeader(b"\x01\x01\xAA\xBB\xCC\xDD\0\0", 0, 0),
        )
        cls.inner = make_inner([cls.wrapper, b"second-entry"])
        cls.outer = make_outer(cls.inner)

    def test_png_rgba_roundtrip_is_deterministic(self) -> None:
        rgba = bytes((10, 20, 30, 40)) * 35
        png_a = codec.encode_rgba_png(rgba, 7, 5)
        png_b = codec.encode_rgba_png(rgba, 7, 5)
        self.assertEqual(png_a, png_b)
        decoded, width, height = codec.decode_png(png_a)
        self.assertEqual((width, height), (7, 5))
        self.assertEqual(decoded, rgba)

    def test_bc3_decode_and_template_identity(self) -> None:
        rgba = codec.decode_bc3(self.bc3, codec.EXPECTED_WIDTH, codec.EXPECTED_HEIGHT)
        self.assertEqual(rgba[:4], bytes((255, 0, 0, 255)))
        encoded, preserved, changed = codec.encode_bc3(
            rgba,
            codec.EXPECTED_WIDTH,
            codec.EXPECTED_HEIGHT,
            template_bc3=self.bc3,
        )
        self.assertEqual(encoded, self.bc3)
        self.assertEqual(preserved, 4096)
        self.assertEqual(changed, 0)

    def test_g1t_exact_layout_is_parsed_and_rebuilt(self) -> None:
        texture = codec.parse_pc_title_g1t(self.g1t)
        self.assertEqual(texture.format_code, 0x5B)
        self.assertEqual((texture.width, texture.height), (512, 128))
        self.assertEqual(texture.payload_offset, 56)
        self.assertEqual(texture.bc3, self.bc3)
        self.assertEqual(codec.replace_g1t_bc3(texture, self.bc3), self.g1t)
        malformed = bytearray(self.g1t)
        malformed[texture.texture_offset + 1] = 0x5A
        with self.assertRaisesRegex(codec.CodecError, "expected 0x5B"):
            codec.parse_pc_title_g1t(bytes(malformed))

    def test_inner_link32_identity_and_growth_keep_alignment(self) -> None:
        parsed = codec.parse_inner_link32(self.inner)
        self.assertEqual(codec.rebuild_inner_link32(parsed), self.inner)
        grown = codec.rebuild_inner_link32(parsed, {0: parsed.entries[0].data + b"growth"})
        reparsed = codec.parse_inner_link32(grown)
        self.assertEqual(reparsed.entries[0].data, parsed.entries[0].data + b"growth")
        self.assertEqual(reparsed.entries[1].data, b"second-entry")
        self.assertEqual(reparsed.entries[1].offset % 0x20, 0)

    def test_full_chain_unchanged_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="n16_pc_g1t_test_") as temporary:
            path = Path(temporary) / "res_lang.bin"
            path.write_bytes(self.outer)
            before = codec.sha256_file(path)
            chain = codec.load_texture_chain(path, 0)
            rgba = codec.decode_bc3(chain.g1t.bc3, chain.g1t.width, chain.g1t.height)
            candidate, report = codec.rebuild_texture_chain(chain, rgba)
            self.assertEqual(candidate, self.outer)
            self.assertTrue(report["outer_archive_exact"])
            self.assertEqual(report["preserved_template_blocks"], 4096)
            self.assertEqual(report["deterministically_encoded_blocks"], 0)
            self.assertEqual(codec.sha256_file(path), before)

    def test_one_changed_block_is_deterministic_and_reextracts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="n16_pc_g1t_test_") as temporary:
            path = Path(temporary) / "res_lang.bin"
            path.write_bytes(self.outer)
            chain = codec.load_texture_chain(path, 0)
            rgba = bytearray(
                codec.decode_bc3(chain.g1t.bc3, chain.g1t.width, chain.g1t.height)
            )
            rgba[0:4] = bytes((0, 255, 0, 255))
            first, report_a = codec.rebuild_texture_chain(chain, bytes(rgba))
            second, report_b = codec.rebuild_texture_chain(chain, bytes(rgba))
            self.assertEqual(first, second)
            self.assertEqual(report_a, report_b)
            self.assertEqual(report_a["preserved_template_blocks"], 4095)
            self.assertEqual(report_a["deterministically_encoded_blocks"], 1)
            candidate_path = Path(temporary) / "candidate.bin"
            candidate_path.write_bytes(first)
            reparsed = codec.load_texture_chain(candidate_path, 0)
            self.assertNotEqual(reparsed.g1t.bc3, chain.g1t.bc3)
            for index in range(3):
                self.assertEqual(reparsed.outer.entries[index].data, chain.outer.entries[index].data)


if __name__ == "__main__":
    unittest.main()
