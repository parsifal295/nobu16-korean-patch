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

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameFormatError,
    is_visible_translation_candidate,
    iter_literals,
    parse_packed_msggame,
    parse_raw_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
    rebuild_raw_with_literals,
)
from nobu16_lz4 import WrapperHeader, decompress_wrapper, recompress_wrapper  # noqa: E402


def literal(text: str) -> bytes:
    return LITERAL_START + text.encode("utf-16-le") + LITERAL_END


def block(records: list[bytes]) -> bytes:
    cursor = 4 + 4 * len(records)
    offsets: list[int] = []
    for record in records:
        offsets.append(cursor)
        cursor += len(record)
    return (
        struct.pack("<I", len(records))
        + b"".join(struct.pack("<I", offset) for offset in offsets)
        + b"".join(records)
    )


def raw_fixture() -> bytes:
    blocks = [
        block([b"\x91" + literal("Alpha") + b"\x92", b"\x01\x02\x03"]),
        block([literal(""), literal("Visible") + literal("Second")]),
    ]
    header_size = 4 + 8 * len(blocks)
    cursor = (header_size + 3) & ~3
    pairs: list[tuple[int, int]] = []
    for value in blocks:
        pairs.append((cursor, len(value)))
        cursor = (cursor + len(value) + 3) & ~3
    out = bytearray(struct.pack("<I", len(blocks)))
    out.extend(b"".join(struct.pack("<II", *pair) for pair in pairs))
    out.extend(b"\0" * (((len(out) + 3) & ~3) - len(out)))
    for value in blocks:
        out.extend(value)
        out.extend(b"\0" * (((len(out) + 3) & ~3) - len(out)))
    return bytes(out)


class MsgGameFormatTests(unittest.TestCase):
    def test_parse_and_noop_rebuild_are_byte_exact(self) -> None:
        raw = raw_fixture()
        archive = parse_raw_msggame(raw)
        self.assertEqual(len(archive.blocks), 2)
        self.assertEqual(archive.record_count, 4)
        self.assertEqual([len(block.records) for block in archive.blocks], [2, 2])
        self.assertEqual(rebuild_raw_msggame(archive), raw)

    def test_literal_coordinates_and_visibility(self) -> None:
        archive = parse_raw_msggame(raw_fixture())
        values = list(iter_literals(archive))
        self.assertEqual([value.text for value in values], ["Alpha", "", "Visible", "Second"])
        self.assertEqual(
            [(value.block_id, value.record_id, value.literal_id) for value in values],
            [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)],
        )
        self.assertEqual(
            [is_visible_translation_candidate(value.text) for value in values],
            [True, False, True, True],
        )

    def test_variable_length_literal_overlay_rebuilds_all_offsets(self) -> None:
        archive = parse_raw_msggame(raw_fixture())
        rebuilt = rebuild_raw_with_literals(
            archive,
            {
                (0, 0, 0): "한글화 길이 증가 시험",
                (1, 1, 1): "끝",
            },
        )
        self.assertNotEqual(rebuilt, raw_fixture())
        parsed = parse_raw_msggame(rebuilt)
        values = {
            (value.block_id, value.record_id, value.literal_id): value.text
            for value in iter_literals(parsed)
        }
        self.assertEqual(values[(0, 0, 0)], "한글화 길이 증가 시험")
        self.assertEqual(values[(1, 1, 1)], "끝")
        self.assertEqual(values[(1, 1, 0)], "Visible")
        self.assertEqual(rebuild_raw_msggame(parsed), rebuilt)

    def test_complete_record_replacement_can_change_length(self) -> None:
        archive = parse_raw_msggame(raw_fixture())
        replacement = b"\xAA\xBB\xCC\xDD\xEE"
        rebuilt = rebuild_raw_msggame(archive, {(0, 1): replacement})
        parsed = parse_raw_msggame(rebuilt)
        self.assertEqual(parsed.blocks[0].records[1].data, replacement)
        self.assertEqual(parsed.blocks[1].records[0].data, archive.blocks[1].records[0].data)

    def test_packed_literal_overlay_has_semantic_roundtrip(self) -> None:
        raw = raw_fixture()
        header = WrapperHeader(b"\x01\x01\xC4\xC1\xFA\x7F\x00\x00", len(raw), 0)
        packed = recompress_wrapper(raw, header)
        rebuilt = rebuild_packed_with_literals(packed, {(0, 0, 0): "한국어"})
        parsed = parse_packed_msggame(rebuilt)
        values = list(iter_literals(parsed.archive))
        self.assertEqual(values[0].text, "한국어")
        _header, rebuilt_raw = decompress_wrapper(rebuilt)
        self.assertEqual(rebuild_raw_msggame(parsed.archive), rebuilt_raw)

    def test_rejects_odd_or_unterminated_literal(self) -> None:
        archive = parse_raw_msggame(raw_fixture())
        original = archive.blocks[0].records[0]
        odd = type(original)(
            original.block_id,
            original.record_id,
            original.relative_offset,
            LITERAL_START + b"A" + LITERAL_END,
        )
        with self.assertRaises(MsgGameFormatError):
            parse_record_literals(odd)
        unterminated = type(original)(
            original.block_id,
            original.record_id,
            original.relative_offset,
            LITERAL_START + "text".encode("utf-16-le"),
        )
        with self.assertRaises(MsgGameFormatError):
            parse_record_literals(unterminated)


if __name__ == "__main__":
    unittest.main()
