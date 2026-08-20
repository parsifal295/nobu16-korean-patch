from __future__ import annotations

import importlib.util
import struct
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parents[1]
BUILDER_PATH = WORKSTREAM / "build_font_jp_griun_polsensibility_v1.py"
SPEC = importlib.util.spec_from_file_location("font_jp_griun_polsensibility_v1", BUILDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load Griun table-1 builder")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


TARGET = 0xAC00
EXCEPTION = 0xD07F
CELL = 32
STRIDE = CELL * CELL // 2


def make_record(width: int, pointer: int, metric_width: int | None = None) -> bytes:
    if metric_width is None:
        metric_width = width
    return bytes((width, CELL, 0, CELL, metric_width, 0, 0, CELL)) + struct.pack("<I", pointer)


def make_safe_payload() -> bytes:
    payload = bytearray(STRIDE)
    for y in range(1, CELL - 1):
        for x in range(1, CELL - 1):
            index = y * (CELL // 2) + x // 2
            if x % 2 == 0:
                payload[index] |= 0xE0
            else:
                payload[index] |= 0x0E
    return bytes(payload)


def make_fixture(*, alias_table_1_to_table_0: bool = False) -> tuple[bytes, dict[tuple[int, int], tuple[int, int]]]:
    palette_count = 0
    header_size = 0x20 + 3 * 4
    record_count = 3
    table_size = BUILDER.MAP_SIZE + record_count * BUILDER.RECORD_SIZE
    table_offsets = tuple(header_size + table * table_size for table in range(3))
    atlas_offset = header_size + 3 * table_size
    atlas = bytearray(6 * STRIDE)
    spans: dict[tuple[int, int], tuple[int, int]] = {}
    body = bytearray(3 * table_size)

    for table in range(3):
        table_relative = table * table_size
        struct.pack_into("<H", body, table_relative + 2 * TARGET, 1)
        struct.pack_into("<H", body, table_relative + 2 * EXCEPTION, 2)
        target_index = table * 2
        if table == BUILDER.TARGET_TABLE and alias_table_1_to_table_0:
            target_index = 0
        target_pointer = target_index * STRIDE
        exception_pointer = (table * 2 + 1) * STRIDE
        records = (
            make_record(0, 0),
            make_record(CELL, target_pointer, CELL - 3),
            make_record(CELL, exception_pointer, CELL - 2),
        )
        records_start = table_relative + BUILDER.MAP_SIZE
        body[records_start : records_start + len(b"".join(records))] = b"".join(records)
        atlas[target_pointer : target_pointer + STRIDE] = bytes((0x10 + table,)) * STRIDE
        atlas[exception_pointer : exception_pointer + STRIDE] = bytes((0x20 + table,)) * STRIDE
        spans[(table, TARGET)] = (atlas_offset + target_pointer, atlas_offset + target_pointer + STRIDE)
        spans[(table, EXCEPTION)] = (atlas_offset + exception_pointer, atlas_offset + exception_pointer + STRIDE)

    total_size = atlas_offset + len(atlas)
    header = bytearray(header_size)
    header[:8] = BUILDER.G1N_MAGIC
    struct.pack_into("<IIIIII", header, 8, total_size, header_size, 10, atlas_offset, palette_count, 3)
    struct.pack_into("<3I", header, 0x20, *table_offsets)
    return bytes(header + body + atlas), spans


class GriunTableOneBuilderTest(unittest.TestCase):
    def test_full_cell_raster_fits_existing_width_packed_record(self) -> None:
        full = bytearray(STRIDE)
        for y in range(2, CELL - 2):
            for x in range(2, CELL - 2):
                index = y * (CELL // 2) + x // 2
                if x % 2 == 0:
                    full[index] |= 0xF0
                else:
                    full[index] |= 0x0F
        fitted, report = BUILDER.fit_glyph_to_record_width(bytes(full), CELL, 20)
        self.assertEqual(len(fitted), 20 * CELL // 2)
        self.assertEqual(report["mode"], "horizontal_scale")
        self.assertGreaterEqual(report["minimum_horizontal_margin"], 1)
        ink_x = {
            x
            for y in range(CELL)
            for x in range(20)
            if BUILDER._pixel_nibble(fitted, 20, x, y)
        }
        self.assertEqual(min(ink_x), 1)
        self.assertEqual(max(ink_x), 18)

    def test_only_table_one_target_pixels_change(self) -> None:
        source, spans = make_fixture()
        replacement = make_safe_payload()
        payloads = {CELL: replacement}
        candidate, report = BUILDER.replace_g1n_pixels(
            source,
            payloads,
            {TARGET: 0},
            {TARGET},
            {EXCEPTION},
            "fixture",
        )

        self.assertEqual(len(candidate), len(source))
        self.assertEqual(report["target_table"], 1)
        self.assertTrue(report["tables_0_and_2_exact"])
        self.assertEqual(report["target_span_count"], 1)
        for table in range(3):
            for codepoint in (TARGET, EXCEPTION):
                start, end = spans[(table, codepoint)]
                if table == 1 and codepoint == TARGET:
                    self.assertEqual(candidate[start:end], replacement)
                    self.assertNotEqual(candidate[start:end], source[start:end])
                else:
                    self.assertEqual(candidate[start:end], source[start:end])

        target_rows = [row for row in report["tables"] if row["target_table"]]
        self.assertEqual(len(target_rows), 1)
        self.assertEqual(target_rows[0]["table"], 1)
        self.assertEqual(target_rows[0]["replaced_hangul_count"], 1)
        self.assertEqual(
            [row["replaced_hangul_count"] for row in report["tables"]],
            [0, 1, 0],
        )

    def test_cross_table_pixel_alias_is_rejected(self) -> None:
        source, _spans = make_fixture(alias_table_1_to_table_0=True)
        with self.assertRaisesRegex(BUILDER.BuildError, "aliases table 0/2 pixels"):
            BUILDER.replace_g1n_pixels(
                source,
                {CELL: make_safe_payload()},
                {TARGET: 0},
                {TARGET},
                {EXCEPTION},
                "alias fixture",
            )

    def test_release_contract_targets_index_one(self) -> None:
        self.assertEqual(BUILDER.TARGET_TABLE, 1)
        self.assertEqual(BUILDER.CMAP_EXCEPTIONS, (0xCE4C, 0xD07F))
        self.assertEqual(BUILDER.DEMANDED_EXCEPTION, 0xD07F)
        self.assertEqual(
            {row["cell"] for row in BUILDER.PROFILE_BY_CELL.values()},
            {32, 48, 64, 96},
        )


if __name__ == "__main__":
    unittest.main()
