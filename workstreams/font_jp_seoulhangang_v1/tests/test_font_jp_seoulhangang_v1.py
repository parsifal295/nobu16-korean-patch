from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM.parents[1]
SPEC = importlib.util.spec_from_file_location(
    "nobu16_test_font_jp_seoulhangang_v1",
    WORKSTREAM / "build_jp_seoulhangang_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def synthetic_g1n(cells: tuple[int, int, int]) -> bytes:
    header_size = 0x20 + 4 * len(cells)
    table_offsets: list[int] = []
    cursor = header_size
    for _cell in cells:
        table_offsets.append(cursor)
        cursor += builder.MAP_SIZE + builder.RECORD_SIZE
    atlas_offset = cursor
    atlas_size = sum((cell // 2) * cell for cell in cells)
    raw = bytearray(atlas_offset + atlas_size)
    raw[:8] = builder.G1N_MAGIC
    struct.pack_into("<IIIIII", raw, 0x08, len(raw), header_size, 0, atlas_offset, 0, 3)
    for table, offset in enumerate(table_offsets):
        struct.pack_into("<I", raw, 0x20 + 4 * table, offset)
    pointer = 0
    for table, (cell, offset) in enumerate(zip(cells, table_offsets, strict=True)):
        record = offset + builder.MAP_SIZE
        raw[record : record + 8] = bytes(
            (cell, cell, 0, cell, cell, 256 - cell // 2, 0, cell)
        )
        struct.pack_into("<I", raw, record + 8, pointer)
        size = (cell // 2) * cell
        raw[atlas_offset + pointer : atlas_offset + pointer + size] = bytes([table + 1]) * size
        pointer += size
    return bytes(raw)


def synthetic_reuse_g1n(cells: tuple[int, int, int]) -> bytes:
    counts = (3, 1, 1)
    header_size = 0x20 + 4 * len(cells)
    table_offsets: list[int] = []
    cursor = header_size
    for count in counts:
        table_offsets.append(cursor)
        cursor += builder.MAP_SIZE + builder.RECORD_SIZE * count
    atlas_offset = cursor
    table_pixels: list[list[tuple[int, bytes]]] = []
    for table, cell in enumerate(cells):
        widths = [cell, cell, cell // 2] if table == 0 else [cell]
        table_pixels.append(
            [(width, bytes([0x31 + table + index]) * (width * cell // 2)) for index, width in enumerate(widths)]
        )
    atlas_size = sum(len(pixels) for rows in table_pixels for _width, pixels in rows)
    raw = bytearray(atlas_offset + atlas_size)
    raw[:8] = builder.G1N_MAGIC
    struct.pack_into("<IIIIII", raw, 0x08, len(raw), header_size, 0, atlas_offset, 0, 3)
    for table, offset in enumerate(table_offsets):
        struct.pack_into("<I", raw, 0x20 + 4 * table, offset)
    struct.pack_into("<H", raw, table_offsets[0] + 2 * 0x32A4, 1)
    struct.pack_into("<H", raw, table_offsets[0] + 2 * 0xFF65, 2)
    pointer = 0
    for table, (cell, offset) in enumerate(zip(cells, table_offsets, strict=True)):
        for ordinal, (width, pixels) in enumerate(table_pixels[table]):
            record = offset + builder.MAP_SIZE + ordinal * builder.RECORD_SIZE
            raw[record : record + 8] = bytes(
                (width, cell, 0, cell, width, 256 - width // 2, 0, cell)
            )
            struct.pack_into("<I", raw, record + 8, pointer)
            raw[atlas_offset + pointer : atlas_offset + pointer + len(pixels)] = pixels
            pointer += len(pixels)
    return bytes(raw)


def synthetic_ttf_format12(mapped: list[int]) -> bytes:
    groups = b"".join(struct.pack(">III", cp, cp, index + 1) for index, cp in enumerate(sorted(mapped)))
    subtable = struct.pack(">HHIII", 12, 0, 16 + len(groups), 0, len(mapped)) + groups
    cmap = struct.pack(">HHHHI", 0, 1, 3, 10, 12) + subtable
    table_offset = 28
    directory = (
        b"\x00\x01\x00\x00"
        + struct.pack(">HHHH", 1, 16, 0, 0)
        + b"cmap"
        + struct.pack(">III", 0, table_offset, len(cmap))
    )
    return directory + cmap


class JPFontPipelineTests(unittest.TestCase):
    def test_latest_demand_includes_pending_five(self) -> None:
        demand = builder.require_demand()
        self.assertEqual(demand["source_count"], 118)
        self.assertEqual(demand["source_entry_count"], 83_658)
        self.assertEqual(demand["hangul_syllable_count"], 1_247)
        self.assertEqual(demand["source_catalog_sha256"], builder.DEMAND_LOCK["source_catalog_sha256"])

    def test_pending_registration_is_order_stable(self) -> None:
        for resource in (
            "MSG_PK/SC/msgdata.bin",
            "MSG_PK/SC/msggame.bin",
        ):
            pending = [
                row["path"]
                for row in builder.PENDING_OVERLAYS
                if row["resource"] == resource
            ]
            absent, absent_count = builder.merge_overlay_paths(["a.json"], resource)
            present, present_count = builder.merge_overlay_paths(
                [pending[-1], "a.json", *pending[:-1]], resource
            )
            self.assertEqual(absent, present)
            self.assertEqual(absent_count, 0)
            self.assertEqual(present_count, len(pending))

    def test_real_profile_assignment_has_no_invented_small_tier(self) -> None:
        self.assertEqual(builder.PROFILE_TABLES[6], ("eb48", "eb48", "eb48"))
        self.assertEqual(builder.PROFILE_TABLES[7], ("b32", "eb48", "b32"))
        self.assertFalse(builder.SEOUL_HANGANG_M["used"])
        evidence = json.loads((WORKSTREAM / "verification.v1.json").read_text(encoding="utf-8"))
        profiles = evidence["g1n_structure"]["profiles"]
        self.assertEqual(profiles["entry_6_or_16"]["cell_hierarchy"], [48, 48, 48])
        self.assertEqual(profiles["entry_7_or_17"]["cell_hierarchy"], [32, 48, 32])
        self.assertFalse(evidence["g1n_structure"]["smaller_third_tier_present"])

    def test_mixed_cell_append_uses_b_eb_b(self) -> None:
        stock = synthetic_g1n((32, 48, 32))
        codepoint = 0xAC00
        pixels = {
            "eb48": bytes([0xE1]) * ((48 // 2) * 48),
            "b32": bytes([0xB1]) * ((32 // 2) * 32),
        }
        target, report = builder.build_g1n_append(
            stock,
            pixels,
            7,
            [codepoint],
            {0: [codepoint], 1: [codepoint], 2: [codepoint]},
            "synthetic profile 7",
        )
        self.assertEqual(report["cell_hierarchy"], [32, 48, 32])
        self.assertEqual(report["table_profiles"], ["b32", "eb48", "b32"])
        verified = builder.verify_g1n_append_without_raster(
            stock,
            target,
            7,
            {0: [codepoint], 1: [codepoint], 2: [codepoint]},
            "synthetic profile 7",
        )
        self.assertTrue(verified["complete_stock_atlas_exact_prefix"])

    def test_stock_reuse_copies_pixels_to_new_table2_tail(self) -> None:
        stock = synthetic_reuse_g1n((32, 48, 32))
        raster_cp = 0xAC00
        pixels = {
            "eb48": bytes([0xE1]) * ((48 // 2) * 48),
            "b32": bytes([0xB1]) * ((32 // 2) * 32),
        }
        table_plan = {
            0: [raster_cp],
            1: [raster_cp],
            2: [0x32A4, raster_cp, 0xFF65],
        }
        target, report = builder.build_g1n_append(
            stock, pixels, 7, [raster_cp], table_plan, "synthetic stock reuse"
        )
        copies = report["tables"][2]["stock_pixel_copies"]
        self.assertEqual([row["codepoint"] for row in copies], ["U+32A4", "U+FF65"])
        self.assertTrue(all(not row["direct_pointer_alias"] for row in copies))
        verified = builder.verify_g1n_append_without_raster(
            stock, target, 7, table_plan, "synthetic stock reuse"
        )
        self.assertTrue(verified["stock_pixel_copies_exact"])
        self.assertEqual(len(verified["stock_pixel_copies"]), 2)

    def test_cmap_parser_never_invents_fallback_coverage(self) -> None:
        font = synthetic_ttf_format12([0xAC00, 0x32A4])
        subtables = builder.parse_unicode_cmap(font, "synthetic font")
        self.assertTrue(any(builder.cmap_glyph_id(row, 0xAC00, "synthetic") for row in subtables))
        self.assertTrue(any(builder.cmap_glyph_id(row, 0x32A4, "synthetic") for row in subtables))
        self.assertFalse(any(builder.cmap_glyph_id(row, 0xFF65, "synthetic") for row in subtables))

    def test_cmap_gate_rejects_any_unreviewed_missing_character(self) -> None:
        append_union = [0x32A4, 0xAC00, 0xFF65]
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "tmp") as temporary:
            root = Path(temporary)
            good = root / "good.ttf"
            bad = root / "bad.ttf"
            good.write_bytes(synthetic_ttf_format12([0xAC00]))
            bad.write_bytes(synthetic_ttf_format12([]))
            good_paths = {
                "entry6_48px_eb": good,
                "entry7_32px_b": good,
            }
            reports = builder.validate_official_font_cmaps(good_paths, append_union)
            self.assertTrue(all(row["cmap_missing_count"] == 2 for row in reports))
            bad_paths = {
                "entry6_48px_eb": bad,
                "entry7_32px_b": bad,
            }
            with self.assertRaises(builder.JPFontBuildError):
                builder.validate_official_font_cmaps(bad_paths, append_union)

    def test_wrong_stock_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "tmp") as temporary:
            path = Path(temporary) / "wrong.bin"
            path.write_bytes(b"wrong")
            with self.assertRaises(builder.JPFontBuildError):
                builder.require_stock(path, "base")

    def test_verification_pins_private_outputs_and_both_runtime_routes(self) -> None:
        evidence = builder.strict_json(WORKSTREAM / "verification.v1.json")
        expected = builder.load_expected_outputs(WORKSTREAM / "verification.v1.json")
        self.assertEqual(
            [row["candidate_archive_sha256"] for row in expected["routes"]],
            [
                "4395B84C5F678E37D8F39BCEEFF1986F62B07A54FF7936FC1402412AF07536F2",
                "697F5034140A35A676CC0D0006CCECE4753D823109C5792500C46DE6499C9C12",
            ],
        )
        routes = evidence["pk_runtime_route_evidence"]
        self.assertFalse(routes["steam_runtime_required_combination_verified"])
        self.assertEqual(
            routes["safe_distribution_decision"],
            "include both JP base and JP PK font candidates pending Steam runtime validation",
        )
        self.assertIn("/res_lang.bin", routes["ascii_string_offsets"])
        self.assertIn("/res_lang_pk.bin", routes["ascii_string_offsets"])

    def test_expected_cmap_gate_excludes_only_two_stock_reuse_points(self) -> None:
        expected = builder.load_expected_outputs(WORKSTREAM / "verification.v1.json")
        for row in expected["font_cmap_gate"]:
            self.assertTrue(row["gdi_fallback_forbidden"])
            self.assertEqual(row["cmap_missing"], ["U+32A4", "U+FF65"])
            self.assertEqual(row["cmap_covered_count"], 1_306)

    def test_official_fonts_and_archive_are_individually_pinned(self) -> None:
        evidence = builder.strict_json(WORKSTREAM / "verification.v1.json")
        fonts = evidence["official_font_pin"]
        self.assertEqual(fonts["archive_sha256"], builder.SC_FONT.OFFICIAL_ARCHIVE_SHA256)
        self.assertEqual(
            fonts["SeoulHangangEB.ttf"]["sha256"],
            builder.SC_FONT.FONT_SOURCES["entry6_48px_eb"]["sha256"],
        )
        self.assertEqual(
            fonts["SeoulHangangB.ttf"]["sha256"],
            builder.SC_FONT.FONT_SOURCES["entry7_32px_b"]["sha256"],
        )
        self.assertEqual(fonts["SeoulHangangM.ttf"]["sha256"], builder.SEOUL_HANGANG_M["sha256"])

    def test_public_workstream_contains_no_binary_payload(self) -> None:
        forbidden_suffixes = {".bin", ".g1n", ".ttf", ".otf", ".zip", ".pixels"}
        offenders = [
            path.relative_to(WORKSTREAM).as_posix()
            for path in WORKSTREAM.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden_suffixes
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
