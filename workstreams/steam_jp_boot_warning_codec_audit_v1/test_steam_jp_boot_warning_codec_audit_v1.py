#!/usr/bin/env python3
"""Unit tests for the source-free Steam JP boot-warning codec audit."""

from __future__ import annotations

import importlib.util
import struct
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
MODULE_PATH = WORKSTREAM / "build_steam_jp_boot_warning_codec_audit_v1.py"
SPEC = importlib.util.spec_from_file_location("boot_warning_codec_audit", MODULE_PATH)
assert SPEC and SPEC.loader
codec = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = codec
SPEC.loader.exec_module(codec)


def make_format01_g1t(width: int = 2, height: int = 2, payload: bytes | None = None) -> bytes:
    if payload is None:
        payload = bytes(range(width * height * 4))
    width_log2 = width.bit_length() - 1
    height_log2 = height.bit_length() - 1
    assert width == 1 << width_log2 and height == 1 << height_log2
    assert len(payload) == width * height * 4
    texture = bytearray((0x10, 0x01, (height_log2 << 4) | width_log2, 0, 0, 0, 0, 0x10))
    texture.extend(struct.pack("<I", 12))
    texture.extend(b"\0" * 8)
    texture.extend(payload)
    raw = bytearray(codec.G1T_MAGIC)
    raw.extend(struct.pack("<4I", 0, 32, 1, codec.PC_PLATFORM))
    raw.extend(b"\0" * 8)
    raw.extend(struct.pack("<I", 4))
    raw.extend(texture)
    struct.pack_into("<I", raw, 8, len(raw))
    return bytes(raw)


def make_inner_link32() -> bytes:
    first_offset = 64
    second_offset = 96
    first = b"abc"
    second = b"defg"
    blob = bytearray(b"LINK")
    blob.extend(struct.pack("<4I", 2, 32, 6, 64))
    blob.extend(b"\0" * 12)
    blob.extend(struct.pack("<II", first_offset, len(first)))
    blob.extend(struct.pack("<II", second_offset, len(second)))
    blob.extend(b"\0" * (first_offset - len(blob)))
    blob.extend(first)
    blob.extend(b"\0" * (second_offset - len(blob)))
    blob.extend(second)
    return bytes(blob)


class BootWarningCodecAuditTests(unittest.TestCase):
    def test_format01_rgba_decode_encode_is_exact(self) -> None:
        raw = make_format01_g1t()
        parsed = codec.parse_format01_g1t(raw, "synthetic")
        self.assertEqual(parsed.width, 2)
        self.assertEqual(parsed.height, 2)
        self.assertEqual(parsed.format_code, 0x01)
        rgba = codec.decode_format01_rgba(parsed.payload, parsed.width, parsed.height)
        self.assertEqual(codec.encode_format01_rgba(rgba, parsed.width, parsed.height), parsed.payload)
        self.assertEqual(parsed.payload_offset, 56)

    def test_format01_rejects_wrong_format_or_payload_size(self) -> None:
        malformed_format = bytearray(make_format01_g1t())
        malformed_format[37] = 0x5B
        with self.assertRaises(codec.AuditError):
            codec.parse_format01_g1t(bytes(malformed_format), "wrong-format")
        with self.assertRaises(codec.AuditError):
            codec.parse_format01_g1t(make_format01_g1t()[:-1], "short-payload")

    def test_inner_link_identity_rebuild_is_byte_exact(self) -> None:
        source = make_inner_link32()
        parsed = codec.parse_inner_link32(source, "synthetic-inner")
        self.assertEqual(parsed.resource_id, 6)
        self.assertEqual(parsed.original_sha256, codec.sha256_bytes(source))
        self.assertEqual(codec.rebuild_inner_link32_identity(parsed), source)

    def test_nearest_preview_and_png_are_deterministic(self) -> None:
        rgba = bytes((12, 34, 56, 255)) * 16
        preview = codec.nearest_resize_rgba(rgba, 4, 4, 2, 2)
        self.assertEqual(preview, bytes((12, 34, 56, 255)) * 4)
        first = codec.encode_png_rgba(preview, 2, 2)
        second = codec.encode_png_rgba(preview, 2, 2)
        self.assertEqual(first, second)
        self.assertTrue(first.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_metadata_is_source_free_and_rejects_binary_keys(self) -> None:
        validation = WORKSTREAM / "validation.v1.json"
        data = __import__("json").loads(validation.read_text(encoding="utf-8"))
        codec.validate_metadata(data)
        self.assertEqual(data["provenance"]["builder_sha256"], codec.sha256_file(MODULE_PATH))
        data["slots"][0]["g1t"]["payload"] = "forbidden"
        with self.assertRaises(codec.AuditError):
            codec.validate_metadata(data)

    def test_preview_destination_cannot_escape_tmp(self) -> None:
        with self.assertRaises(codec.AuditError):
            codec.require_tmp_output(WORKSTREAM / "not_tmp")


if __name__ == "__main__":
    unittest.main()
