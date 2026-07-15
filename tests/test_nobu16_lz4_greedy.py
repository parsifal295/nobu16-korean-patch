from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import nobu16_lz4 as lz4  # noqa: E402


class GreedyRawLZ4Tests(unittest.TestCase):
    def assert_roundtrip(self, raw: bytes) -> bytes:
        compressed = lz4.raw_lz4_compress_greedy(raw)
        self.assertEqual(lz4.raw_lz4_decompress(compressed, len(raw)), raw)
        return compressed

    def test_boundary_lengths_roundtrip(self) -> None:
        for length in range(0, 300):
            with self.subTest(length=length):
                self.assert_roundtrip(bytes((index * 37 + length) & 0xFF for index in range(length)))

    def test_repetitive_payload_is_compact(self) -> None:
        raw = (b"NOBU16-font-atlas\0" * 65536) + bytes(4096)
        compressed = self.assert_roundtrip(raw)
        self.assertLess(len(compressed), len(raw) // 20)

    def test_deterministic_random_corpus_roundtrip(self) -> None:
        rng = random.Random(0x1607)
        for length in (13, 64, 255, 4096, 65535, 131072):
            with self.subTest(length=length):
                raw = bytearray(rng.randbytes(length))
                if length >= 4096:
                    raw[length // 2 : length // 2 + 1024] = raw[128:1152]
                first = self.assert_roundtrip(bytes(raw))
                self.assertEqual(lz4.raw_lz4_compress_greedy(bytes(raw)), first)

    def test_wrapper_prefix_and_roundtrip(self) -> None:
        raw = b"ABCD" * 10000
        template = lz4.WrapperHeader(b"\x01\x01\xC4\xC1\xFA\x7F\0\0", 0, 0)
        wrapped = lz4.recompress_wrapper_greedy(raw, template)
        header, decoded = lz4.decompress_wrapper(wrapped)
        self.assertEqual(header.prefix, template.prefix)
        self.assertEqual(decoded, raw)


if __name__ == "__main__":
    unittest.main()
