from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
REPO_ROOT = TEST_PATH.parents[3]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(WORKSTREAM_ROOT))
sys.path.insert(0, str(TOOLS_ROOT))

from build_literal_overlay import (  # noqa: E402
    OVERLAY_SCHEMA,
    LiteralOverlayError,
    apply_overlay_blob,
    text_hash,
)
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    iter_literals,
    parse_packed_msggame,
    sha256,
)
from nobu16_lz4 import WrapperHeader, decompress_wrapper, recompress_wrapper  # noqa: E402


def packed_fixture() -> bytes:
    record = b"\xAA" + LITERAL_START + "Source".encode("utf-16-le") + LITERAL_END + b"\xBB"
    block = struct.pack("<II", 1, 8) + record
    raw = struct.pack("<III", 1, 12, len(block)) + block
    raw += b"\0" * ((-len(raw)) % 4)
    header = WrapperHeader(b"\x01\x01\xC4\xC1\xFA\x7F\x00\x00", len(raw), 0)
    return recompress_wrapper(raw, header)


def overlay_for(packed: bytes, source_hash: str | None = None) -> dict:
    parsed = parse_packed_msggame(packed)
    source = next(iter(iter_literals(parsed.archive)))
    _header, raw = decompress_wrapper(packed)
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "synthetic-test",
        "resource": "MSG_PK/SC/msggame.bin",
        "base_language": "SC",
        "stock_sc": {
            "packed_size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
            "record_count": parsed.archive.record_count,
            "literal_slot_count": 1,
        },
        "entries": [
            {
                "block_id": source.block_id,
                "record_id": source.record_id,
                "literal_id": source.literal_id,
                "source_sc_utf16le_sha256": source_hash or text_hash(source.text),
                "ko": "더 긴 한국어 번역문",
            }
        ],
    }


class LiteralOverlayTests(unittest.TestCase):
    def test_source_free_overlay_rebuilds_and_verifies(self) -> None:
        packed = packed_fixture()
        rebuilt, manifest = apply_overlay_blob(packed, overlay_for(packed))
        parsed = parse_packed_msggame(rebuilt)
        self.assertEqual(next(iter(iter_literals(parsed.archive))).text, "더 긴 한국어 번역문")
        self.assertEqual(manifest["entry_count"], 1)
        self.assertEqual(set(manifest["checks"].values()), {"OK"})
        self.assertFalse(manifest["installed_game_file_written"])

    def test_rejects_source_hash_mismatch(self) -> None:
        packed = packed_fixture()
        with self.assertRaises(LiteralOverlayError):
            apply_overlay_blob(packed, overlay_for(packed, "0" * 64))

    def test_rejects_duplicate_coordinate(self) -> None:
        packed = packed_fixture()
        overlay = overlay_for(packed)
        overlay["entries"].append(dict(overlay["entries"][0]))
        with self.assertRaises(LiteralOverlayError):
            apply_overlay_blob(packed, overlay)


if __name__ == "__main__":
    unittest.main()
