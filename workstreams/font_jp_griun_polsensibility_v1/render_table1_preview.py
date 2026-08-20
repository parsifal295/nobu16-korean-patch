#!/usr/bin/env python3
"""Render an exact-pixel preview from the built table-1 G1N candidates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
BUILD_PATH = SCRIPT_DIR / "build_font_jp_griun_polsensibility_v1.py"
SPEC = importlib.util.spec_from_file_location("font_jp_griun_preview_builder", BUILD_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load table-1 builder")
BUILD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILD
SPEC.loader.exec_module(BUILD)


EXPECTED_BY_VARIANT = {
    "seoulhangang": {
        "RES_JP/res_lang.bin": (
            153_501_108,
            "B10EF608C4B1A4981C096A29D8B413087EF395696CB8A219B715BDF4C712D07C",
        ),
        "RES_JP_PK_PORT/res_lang_pk_port1.bin": (
            79_074_833,
            "C1B21E2128A74263DCE4598E49477B056E5C64286E156FF046F7C773D3FB56EB",
        ),
    },
    "griun": {
        "RES_JP/res_lang.bin": (
            154_082_054,
            "D68FC908C380528833895B7D9C6657101B6BABDEC65C950F5FAFA8D182DC9891",
        ),
        "RES_JP_PK_PORT/res_lang_pk_port1.bin": (
            80_311_467,
            "85880CC267E1A06CEC960995902993D97C172620DF1DA2446757302962A503C6",
        ),
    },
}
PREVIEW_TEXT = "독안룡 아즈치성 오다 노부나가"
CLI_PREVIEW_LINES = ("독안룡", "아즈치성", "오다 노부나가")


FONT_5X7 = {
    " ": ("00000",) * 7,
    "/": ("00001", "00010", "00100", "01000", "10000", "00000", "00000"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "4": ("01010", "01010", "01010", "11111", "00010", "00010", "00010"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_candidate(root: Path, relative: str, variant: str) -> bytes:
    path = root / relative
    expected_size, expected_hash = EXPECTED_BY_VARIANT[variant][relative]
    if not path.is_file() or path.stat().st_size != expected_size or sha256_file(path) != expected_hash:
        raise ValueError(f"candidate pin mismatch: {relative}")
    return path.read_bytes()


def glyph(raw: bytes, codepoint: int) -> tuple[int, int, bytes]:
    layout = BUILD.parse_g1n(raw, "preview G1N")
    table = layout.tables[BUILD.TARGET_TABLE]
    ordinal = struct.unpack_from("<H", raw, table.offset + 2 * codepoint)[0]
    if not ordinal:
        raise ValueError(f"preview codepoint is unmapped: U+{codepoint:04X}")
    record = table.offset + BUILD.MAP_SIZE + ordinal * BUILD.RECORD_SIZE
    width = raw[record]
    pointer = struct.unpack_from("<I", raw, record + 8)[0]
    size = width * table.cell // 2
    pixels = raw[layout.atlas_offset + pointer : layout.atlas_offset + pointer + size]
    if len(pixels) != size or not any(pixels):
        raise ValueError(f"invalid preview glyph: U+{codepoint:04X}")
    return width, table.cell, pixels


def put_pixel(image: bytearray, canvas_width: int, x: int, y: int, color: tuple[int, int, int]) -> None:
    canvas_height = len(image) // (canvas_width * 3)
    if x < 0 or y < 0 or x >= canvas_width or y >= canvas_height:
        return
    index = (y * canvas_width + x) * 3
    if index + 3 > len(image):
        return
    image[index : index + 3] = bytes(color)


def rectangle(image: bytearray, canvas_width: int, x: int, y: int, width: int, height: int, color: tuple[int, int, int]) -> None:
    for px in range(x, x + width):
        put_pixel(image, canvas_width, px, y, color)
        put_pixel(image, canvas_width, px, y + height - 1, color)
    for py in range(y, y + height):
        put_pixel(image, canvas_width, x, py, color)
        put_pixel(image, canvas_width, x + width - 1, py, color)


def draw_label(image: bytearray, canvas_width: int, x: int, y: int, text: str, scale: int = 3) -> None:
    for char in text:
        bitmap = FONT_5X7[char]
        for row, bits in enumerate(bitmap):
            for column, bit in enumerate(bits):
                if bit == "0":
                    continue
                for dy in range(scale):
                    for dx in range(scale):
                        put_pixel(image, canvas_width, x + column * scale + dx, y + row * scale + dy, (142, 169, 190))
        x += 6 * scale


def render_row(image: bytearray, canvas_width: int, raw: bytes, y: int, scale: int, label: str) -> dict[str, Any]:
    draw_label(image, canvas_width, 36, y + 36, label)
    x = 340
    rows: list[dict[str, Any]] = []
    for character in PREVIEW_TEXT:
        if character == " ":
            x += 24 * scale
            continue
        width, cell, pixels = glyph(raw, ord(character))
        rectangle(image, canvas_width, x - 1, y - 1, width * scale + 2, cell * scale + 2, (50, 57, 64))
        for source_y in range(cell):
            for source_x in range(width):
                value = BUILD._pixel_nibble(pixels, width, source_x, source_y)
                if not value:
                    continue
                level = value * 17
                color = (min(255, level + 10), min(255, level + 7), level)
                for dy in range(scale):
                    for dx in range(scale):
                        put_pixel(image, canvas_width, x + source_x * scale + dx, y + source_y * scale + dy, color)
        rows.append({"character": character, "codepoint": f"U+{ord(character):04X}", "width": width, "cell": cell})
        x += width * scale + 6
    return {"label": label, "scale": scale, "glyphs": rows, "display_width": x}


def render_cli_line(
    image: bytearray,
    canvas_width: int,
    raw: bytes,
    y: int,
    text: str,
) -> dict[str, Any]:
    glyphs: list[tuple[str, int, int, bytes]] = []
    display_width = 0
    for character in text:
        if character == " ":
            glyphs.append((character, 24, 96, b""))
            display_width += 24
            continue
        width, cell, pixels = glyph(raw, ord(character))
        glyphs.append((character, width, cell, pixels))
        display_width += width
    display_width += 6 * max(0, len(glyphs) - 1)
    x = max(16, (canvas_width - display_width) // 2)
    rows: list[dict[str, Any]] = []
    for character, width, cell, pixels in glyphs:
        if character == " ":
            x += width + 6
            continue
        rectangle(image, canvas_width, x - 1, y - 1, width + 2, cell + 2, (50, 57, 64))
        for source_y in range(cell):
            for source_x in range(width):
                value = BUILD._pixel_nibble(pixels, width, source_x, source_y)
                if not value:
                    continue
                level = value * 17
                put_pixel(
                    image,
                    canvas_width,
                    x + source_x,
                    y + source_y,
                    (min(255, level + 10), min(255, level + 7), level),
                )
        rows.append(
            {
                "character": character,
                "codepoint": f"U+{ord(character):04X}",
                "width": width,
                "cell": cell,
            }
        )
        x += width + 6
    return {"text": text, "glyphs": rows, "display_width": display_width}


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int, pixels: bytes) -> None:
    scanlines = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += png_chunk(b"IDAT", zlib.compress(scanlines, 9))
    png += png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument(
        "--variant",
        choices=tuple(EXPECTED_BY_VARIANT),
        default="griun",
        help="pinned G1N candidate family rendered into the preview",
    )
    parser.add_argument(
        "--layout",
        choices=("detailed", "cli"),
        default="detailed",
        help="detailed audit sheet or compact installer preview",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = read_candidate(args.candidate_root, "RES_JP/res_lang.bin", args.variant)
    port1 = read_candidate(
        args.candidate_root,
        "RES_JP_PK_PORT/res_lang_pk_port1.bin",
        args.variant,
    )
    _wrapper, base_g1n = BUILD.extract_g1n(base, 6, "base preview")
    _wrapper, port1_g1n = BUILD.extract_g1n(port1, 1, "port1 preview")

    if args.layout == "cli":
        canvas_width, canvas_height = 720, 320
        image = bytearray((18, 21, 25) * (canvas_width * canvas_height))
        rows = [
            render_cli_line(image, canvas_width, port1_g1n, 8 + index * 104, text)
            for index, text in enumerate(CLI_PREVIEW_LINES)
        ]
    else:
        canvas_width, canvas_height = 2100, 300
        image = bytearray((18, 21, 25) * (canvas_width * canvas_height))
        rows = [
            render_row(image, canvas_width, base_g1n, 36, 2, "TABLE 1 / 48PX"),
            render_row(image, canvas_width, port1_g1n, 174, 1, "TABLE 1 / 96PX"),
        ]
    write_png(args.output, canvas_width, canvas_height, bytes(image))
    manifest = {
        "schema": "nobu16.kr.font-jp-table1-choice-preview.v1",
        "variant": args.variant,
        "layout": args.layout,
        "preview_text": PREVIEW_TEXT,
        "target_table": BUILD.TARGET_TABLE,
        "output": args.output.name,
        "output_size": args.output.stat().st_size,
        "output_sha256": sha256_file(args.output),
        "rows": rows,
    }
    args.output.with_suffix(".json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
