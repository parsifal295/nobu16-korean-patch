"""Strict parser/rebuilder for the five-block base-game ``strdata.bin``.

This copy is deliberately local to the Switch-to-PK biography importer.  The
worktree's older exploratory ``strdata`` workstream is not a runtime
dependency, so this importer remains reproducible from tracked tools plus
its own source.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Sequence

from nobu16_msg_table import MessageTable, MessageTableError, parse_message_table, rebuild_message_table


OUTER_BLOCK_COUNT = 5
OUTER_HEADER_SIZE = 0x2C
INNER_HEADER_SIZE = 0x14
SYNTHETIC_BLOCK_OFFSET = 0x0C
EXPECTED_SLOT_COUNTS = (25069, 4100, 3000, 122, 20)


class StrdataContainerError(ValueError):
    """Raised when the fixed five-block container violates its layout."""


@dataclass(frozen=True)
class StrdataBlock:
    block_id: int
    offset: int
    logical_size: int
    gap_after: bytes
    inner_header: bytes
    table: MessageTable

    @property
    def texts(self) -> tuple[str, ...]:
        return self.table.texts

    @property
    def slot_count(self) -> int:
        return self.table.string_count


@dataclass(frozen=True)
class StrdataContainer:
    raw: bytes
    blocks: tuple[StrdataBlock, ...]


def _u32(blob: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(blob):
        raise StrdataContainerError(f"{label} lies outside raw data")
    return struct.unpack_from("<I", blob, offset)[0]


def _padding(logical_size: int) -> int:
    return (-(SYNTHETIC_BLOCK_OFFSET + logical_size)) % 4


def _synthetic(inner: bytes, gap_after: bytes) -> bytes:
    if gap_after != b"\0" * _padding(len(inner)):
        raise StrdataContainerError("inner table alignment padding is invalid")
    return struct.pack("<III", 1, SYNTHETIC_BLOCK_OFFSET, len(inner)) + inner + gap_after


def _descriptors(raw: bytes) -> tuple[tuple[int, int], ...]:
    if len(raw) < OUTER_HEADER_SIZE:
        raise StrdataContainerError("strdata is shorter than its outer header")
    if _u32(raw, 0, "outer block count") != OUTER_BLOCK_COUNT:
        raise StrdataContainerError("strdata outer block count differs")
    if _u32(raw, 4, "outer header size") != OUTER_HEADER_SIZE:
        raise StrdataContainerError("strdata outer header size differs")
    result = [(OUTER_HEADER_SIZE, _u32(raw, 8, "block zero size"))]
    for block_id in range(1, OUTER_BLOCK_COUNT):
        at = 12 + (block_id - 1) * 8
        result.append((_u32(raw, at, f"block {block_id} offset"), _u32(raw, at + 4, f"block {block_id} size")))
    return tuple(result)


def parse_strdata(raw: bytes) -> StrdataContainer:
    """Parse all five blocks and prove each inner offset table is canonical."""
    descriptors = _descriptors(raw)
    blocks: list[StrdataBlock] = []
    previous_end = OUTER_HEADER_SIZE
    for block_id, ((offset, logical_size), expected_slots) in enumerate(
        zip(descriptors, EXPECTED_SLOT_COUNTS, strict=True)
    ):
        next_offset = descriptors[block_id + 1][0] if block_id + 1 < len(descriptors) else len(raw)
        logical_end = offset + logical_size
        if offset != previous_end or logical_end > next_offset or next_offset > len(raw):
            raise StrdataContainerError(f"block {block_id} placement is invalid")
        inner = raw[offset:logical_end]
        if len(inner) < INNER_HEADER_SIZE or _u32(inner, 0x0C, f"block {block_id} table offset") != INNER_HEADER_SIZE:
            raise StrdataContainerError(f"block {block_id} inner header differs")
        gap_after = raw[logical_end:next_offset]
        try:
            table = parse_message_table(_synthetic(inner, gap_after))
        except MessageTableError as exc:
            raise StrdataContainerError(f"block {block_id} table is invalid: {exc}") from exc
        if table.string_count != expected_slots:
            raise StrdataContainerError(f"block {block_id} slot count differs")
        if rebuild_message_table(table, table.texts) != _synthetic(inner, gap_after):
            raise StrdataContainerError(f"block {block_id} parse/rebuild is not byte-identical")
        blocks.append(StrdataBlock(block_id, offset, logical_size, gap_after, inner[:INNER_HEADER_SIZE], table))
        previous_end = next_offset
    if previous_end != len(raw):
        raise StrdataContainerError("strdata parser did not consume raw payload")
    return StrdataContainer(raw=raw, blocks=tuple(blocks))


def rebuild_strdata(container: StrdataContainer, replacements: dict[int, Sequence[str]] | None = None) -> bytes:
    """Rebuild without changing opaque headers; used for byte-identity checks."""
    output = bytearray(container.raw[:OUTER_HEADER_SIZE])
    starts: list[int] = []
    sizes: list[int] = []
    for block in container.blocks:
        texts = block.texts if not replacements or block.block_id not in replacements else tuple(replacements[block.block_id])
        if len(texts) != block.slot_count:
            raise StrdataContainerError(f"block {block.block_id} replacement count differs")
        synthetic = rebuild_message_table(block.table, texts)
        logical_size = _u32(synthetic, 8, f"rebuilt block {block.block_id} size")
        inner = synthetic[SYNTHETIC_BLOCK_OFFSET:SYNTHETIC_BLOCK_OFFSET + logical_size]
        gap_after = synthetic[SYNTHETIC_BLOCK_OFFSET + logical_size:]
        if inner[:INNER_HEADER_SIZE] != block.inner_header or gap_after != b"\0" * _padding(logical_size):
            raise StrdataContainerError(f"block {block.block_id} rebuild altered container structure")
        starts.append(len(output))
        sizes.append(len(inner))
        output.extend(inner)
        output.extend(gap_after)
    struct.pack_into("<II", output, 0, OUTER_BLOCK_COUNT, OUTER_HEADER_SIZE)
    struct.pack_into("<I", output, 8, sizes[0])
    for block_id in range(1, OUTER_BLOCK_COUNT):
        at = 12 + (block_id - 1) * 8
        struct.pack_into("<II", output, at, starts[block_id], sizes[block_id])
    rebuilt = bytes(output)
    check = parse_strdata(rebuilt)
    for old, new in zip(container.blocks, check.blocks, strict=True):
        expected = old.texts if not replacements or old.block_id not in replacements else tuple(replacements[old.block_id])
        if new.texts != expected:
            raise StrdataContainerError(f"block {old.block_id} rebuilt texts differ")
    return rebuilt
