"""Parse and rebuild the five-block ``MSG/*/strdata.bin`` raw container.

``strdata`` is not a normal one-block message table.  Its outer directory
contains five consecutive inner string tables.  Each inner table has the
ordinary NOBU16 offset-table layout at ``+0x14``; wrapping it with the small
synthetic one-block header understood by :mod:`nobu16_msg_table` lets the
shared strict parser validate it without duplicating UTF-16 table logic.

The two-byte gaps between several inner blocks are the synthetic wrapper's
four-byte alignment padding.  They are reconstructed from each rebuilt
logical inner size, while opaque inner-header words remain byte-preserved.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Mapping, Sequence

from nobu16_msg_table import MessageTable, MessageTableError, parse_message_table, rebuild_message_table


OUTER_BLOCK_COUNT = 5
OUTER_HEADER_SIZE = 0x2C
SYNTHETIC_BLOCK_OFFSET = 0x0C
SYNTHETIC_HEADER_SIZE = 0x0C
INNER_HEADER_SIZE = 0x14
INNER_TABLE_RELATIVE_OFFSET = 0x14
EXPECTED_SLOT_COUNTS = (25069, 4100, 3000, 122, 20)


class StrdataFormatError(ValueError):
    """Raised when a raw strdata container violates its pinned layout."""


@dataclass(frozen=True)
class StrdataBlock:
    """One inner table together with its outer placement metadata."""

    block_id: int
    offset: int
    logical_size: int
    gap_after: bytes
    inner_header: bytes
    table: MessageTable

    @property
    def slot_count(self) -> int:
        return self.table.string_count

    @property
    def texts(self) -> tuple[str, ...]:
        return self.table.texts


@dataclass(frozen=True)
class StrdataArchive:
    """Strictly parsed decompressed strdata data."""

    raw: bytes
    outer_header_size: int
    blocks: tuple[StrdataBlock, ...]

    @property
    def block_count(self) -> int:
        return len(self.blocks)

    @property
    def slot_count(self) -> int:
        return sum(block.slot_count for block in self.blocks)


def _u32(blob: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(blob):
        raise StrdataFormatError(f"{label} at 0x{offset:X} is outside raw data")
    return struct.unpack_from("<I", blob, offset)[0]


def _outer_descriptors(raw: bytes) -> tuple[tuple[int, int], ...]:
    if len(raw) < OUTER_HEADER_SIZE:
        raise StrdataFormatError("raw data is smaller than the strdata outer header")
    block_count = _u32(raw, 0, "outer block count")
    if block_count != OUTER_BLOCK_COUNT:
        raise StrdataFormatError(
            f"outer block count={block_count}, expected={OUTER_BLOCK_COUNT}"
        )
    header_size = _u32(raw, 4, "outer header size")
    if header_size != OUTER_HEADER_SIZE:
        raise StrdataFormatError(
            f"outer header size=0x{header_size:X}, expected=0x{OUTER_HEADER_SIZE:X}"
        )

    descriptors = [(header_size, _u32(raw, 8, "block 0 logical size"))]
    for block_id in range(1, OUTER_BLOCK_COUNT):
        descriptor_offset = 12 + (block_id - 1) * 8
        descriptors.append(
            (
                _u32(raw, descriptor_offset, f"block {block_id} offset"),
                _u32(raw, descriptor_offset + 4, f"block {block_id} logical size"),
            )
        )
    return tuple(descriptors)


def _expected_padding(logical_size: int) -> int:
    return (-(SYNTHETIC_HEADER_SIZE + logical_size)) % 4


def _fake_table_blob(inner: bytes, gap_after: bytes) -> bytes:
    logical_size = len(inner)
    expected_gap = _expected_padding(logical_size)
    if gap_after != b"\0" * expected_gap:
        raise StrdataFormatError(
            f"inner table padding is {gap_after.hex()}, expected {expected_gap} zero bytes"
        )
    return (
        struct.pack("<III", 1, SYNTHETIC_BLOCK_OFFSET, logical_size)
        + inner
        + gap_after
    )


def parse_raw_strdata(raw: bytes) -> StrdataArchive:
    """Strictly parse one decompressed SC, JP, or TC strdata table."""
    descriptors = _outer_descriptors(raw)
    blocks: list[StrdataBlock] = []
    previous_end = OUTER_HEADER_SIZE
    for block_id, ((offset, logical_size), expected_slots) in enumerate(
        zip(descriptors, EXPECTED_SLOT_COUNTS, strict=True)
    ):
        if offset != previous_end:
            if offset < previous_end:
                raise StrdataFormatError(
                    f"block {block_id} begins at 0x{offset:X}, before prior block end 0x{previous_end:X}"
                )
            # Gaps belong to the preceding block and are checked below.
        logical_end = offset + logical_size
        next_offset = (
            descriptors[block_id + 1][0]
            if block_id + 1 < len(descriptors)
            else len(raw)
        )
        if logical_end > next_offset or next_offset > len(raw):
            raise StrdataFormatError(
                f"block {block_id} span 0x{offset:X}..0x{logical_end:X} is invalid"
            )
        if block_id and offset != previous_end:
            raise StrdataFormatError(
                f"block {block_id} offset 0x{offset:X} does not follow prior padded end 0x{previous_end:X}"
            )
        inner = raw[offset:logical_end]
        if len(inner) < INNER_HEADER_SIZE:
            raise StrdataFormatError(f"block {block_id} is smaller than its inner header")
        table_rel = _u32(inner, 0x0C, f"block {block_id} inner table relative offset")
        if table_rel != INNER_TABLE_RELATIVE_OFFSET:
            raise StrdataFormatError(
                f"block {block_id} table offset=0x{table_rel:X}, expected=0x{INNER_TABLE_RELATIVE_OFFSET:X}"
            )
        gap_after = raw[logical_end:next_offset]
        try:
            table = parse_message_table(_fake_table_blob(inner, gap_after))
        except MessageTableError as exc:
            raise StrdataFormatError(f"block {block_id} inner table is invalid: {exc}") from exc
        if table.string_count != expected_slots:
            raise StrdataFormatError(
                f"block {block_id} slots={table.string_count}, expected={expected_slots}"
            )
        unchanged = rebuild_message_table(table, table.texts)
        if unchanged != _fake_table_blob(inner, gap_after):
            raise StrdataFormatError(
                f"block {block_id} synthetic unchanged rebuild is not byte-identical"
            )
        blocks.append(
            StrdataBlock(
                block_id=block_id,
                offset=offset,
                logical_size=logical_size,
                gap_after=gap_after,
                inner_header=inner[:INNER_HEADER_SIZE],
                table=table,
            )
        )
        previous_end = next_offset
    if previous_end != len(raw):
        raise StrdataFormatError(
            f"parsed outer data ends at 0x{previous_end:X}, raw length is 0x{len(raw):X}"
        )
    return StrdataArchive(raw=raw, outer_header_size=OUTER_HEADER_SIZE, blocks=tuple(blocks))


def _replacement_texts(
    block: StrdataBlock,
    replacements: Mapping[int, Sequence[str]] | None,
) -> Sequence[str]:
    if not replacements or block.block_id not in replacements:
        return block.texts
    texts = replacements[block.block_id]
    if len(texts) != block.slot_count:
        raise StrdataFormatError(
            f"block {block.block_id} replacement count={len(texts)}, expected={block.slot_count}"
        )
    if any(not isinstance(text, str) for text in texts):
        raise StrdataFormatError(f"block {block.block_id} contains a non-string replacement")
    return texts


def rebuild_raw_strdata(
    archive: StrdataArchive,
    replacements: Mapping[int, Sequence[str]] | None = None,
) -> bytes:
    """Rebuild raw data, recalculating outer offsets and alignment gaps only."""
    rebuilt_blocks: list[tuple[bytes, bytes]] = []
    for block in archive.blocks:
        fake_rebuilt = rebuild_message_table(
            block.table, _replacement_texts(block, replacements)
        )
        new_logical_size = _u32(fake_rebuilt, 8, f"rebuilt block {block.block_id} size")
        inner_start = SYNTHETIC_HEADER_SIZE
        inner_end = inner_start + new_logical_size
        if inner_end > len(fake_rebuilt):
            raise StrdataFormatError(f"rebuilt block {block.block_id} is truncated")
        inner = fake_rebuilt[inner_start:inner_end]
        gap_after = fake_rebuilt[inner_end:]
        if len(inner) != new_logical_size or gap_after != b"\0" * _expected_padding(new_logical_size):
            raise StrdataFormatError(
                f"rebuilt block {block.block_id} has invalid synthetic alignment padding"
            )
        if inner[:INNER_HEADER_SIZE] != block.inner_header:
            raise StrdataFormatError(
                f"rebuilt block {block.block_id} changed opaque inner header bytes"
            )
        rebuilt_blocks.append((inner, gap_after))

    output = bytearray(archive.raw[: archive.outer_header_size])
    if len(output) != OUTER_HEADER_SIZE:
        raise StrdataFormatError("outer header length changed unexpectedly")
    struct.pack_into("<II", output, 0, OUTER_BLOCK_COUNT, OUTER_HEADER_SIZE)
    starts: list[int] = []
    lengths: list[int] = []
    for inner, gap_after in rebuilt_blocks:
        starts.append(len(output))
        lengths.append(len(inner))
        output.extend(inner)
        output.extend(gap_after)
    struct.pack_into("<I", output, 8, lengths[0])
    for block_id in range(1, OUTER_BLOCK_COUNT):
        descriptor_offset = 12 + (block_id - 1) * 8
        struct.pack_into("<II", output, descriptor_offset, starts[block_id], lengths[block_id])

    rebuilt = bytes(output)
    reparsed = parse_raw_strdata(rebuilt)
    for original, check in zip(archive.blocks, reparsed.blocks, strict=True):
        expected_texts = tuple(_replacement_texts(original, replacements))
        if check.texts != expected_texts:
            raise StrdataFormatError(
                f"rebuilt block {original.block_id} text parse verification failed"
            )
    return rebuilt


def coordinate_texts(archive: StrdataArchive) -> dict[tuple[int, int], str]:
    """Return every text under deterministic ``(block_id, slot_id)`` keys."""
    return {
        (block.block_id, slot_id): text
        for block in archive.blocks
        for slot_id, text in enumerate(block.texts)
    }
