#!/usr/bin/env python3
"""Locate duplicate Japanese supply-base wheel sprites in live JP archives."""

from __future__ import annotations

import argparse
import heapq
import json
import struct
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
IMAGE_WORKSTREAM = REPO / "workstreams" / "steam_jp_port_highres_images_v1"
for candidate in (TOOLS, IMAGE_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_steam_jp_port_highres_images_v1 as base  # noqa: E402


CELL_GEOMETRIES = {
    (96, 88),
    (192, 176),
    (196, 180),
}
CONTACT_BACKGROUND = (28, 92, 132, 255)


def parse_layout(table_padding: bytes) -> list[tuple[int, int, int, int, int]]:
    if len(table_padding) < 32:
        return []
    layout = table_padding[24:]
    if len(layout) % 12 != 8:
        return []
    records = []
    for index in range((len(layout) - 8) // 12):
        first, second, third = struct.unpack_from("<III", layout, index * 12)
        records.append(
            (first & 0xFFFF, first >> 16, second & 0xFFFF, second >> 16, third)
        )
    return records


def padded_crop(
    atlas: Image.Image, rect: tuple[int, int, int, int]
) -> Image.Image:
    left, top, right, bottom = rect
    result = Image.new("RGBA", (right - left, bottom - top), (0, 0, 0, 0))
    clipped = (
        max(0, left),
        max(0, top),
        min(atlas.width, right),
        min(atlas.height, bottom),
    )
    if clipped[0] < clipped[2] and clipped[1] < clipped[3]:
        result.paste(
            atlas.crop(clipped),
            (clipped[0] - left, clipped[1] - top),
        )
    return result


def normalized_cell(
    atlas: Image.Image,
    record: tuple[int, int, int, int, int],
    mode: str,
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    x, y, width, height, _third = record
    if mode == "tight":
        rect = (x - 4, y - 4, x + width + 4, y + height + 4)
    elif mode == "base":
        scale = 2 if width >= 168 else 1
        cell_size = (200, 190) if scale == 2 else (100, 95)
        padding = (4, 12) if scale == 2 else (2, 6)
        rect = (
            x - padding[0],
            y - padding[1],
            x - padding[0] + cell_size[0],
            y - padding[1] + cell_size[1],
        )
    else:
        raise ValueError(f"unknown crop mode: {mode}")
    cell = padded_crop(atlas, rect)
    if cell.size != (200, 184):
        cell = cell.resize((200, 184), Image.Resampling.LANCZOS)
    return cell, rect


def features(image: Image.Image) -> np.ndarray:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.float32)
    background = np.empty_like(rgba)
    background[:, :, :] = CONTACT_BACKGROUND
    alpha = rgba[:, :, 3:4] / 255.0
    composite = rgba[:, :, :3] * alpha + background[:, :, :3] * (1.0 - alpha)
    gray = (
        composite[:, :, 0] * 0.299
        + composite[:, :, 1] * 0.587
        + composite[:, :, 2] * 0.114
    )
    gx = np.diff(gray, axis=1, append=gray[:, -1:])
    gy = np.diff(gray, axis=0, append=gray[-1:, :])
    return np.stack((gray / 255.0, gx / 255.0, gy / 255.0), axis=2)


def score(reference: np.ndarray, candidate: Image.Image) -> float:
    delta = reference - features(candidate)
    return float(np.mean(delta * delta))


def iter_routes(archive_path: Path):
    blob = archive_path.read_bytes()
    outer = lz4.parse_link(blob)
    for outer_entry in outer.entries:
        try:
            nested = base.parse_nested_link(outer_entry.data)
        except Exception:
            continue
        records = parse_layout(nested.table_padding)
        if not records:
            continue
        candidate_records = [
            index
            for index, (_x, _y, width, height, third) in enumerate(records)
            if (width, height) in CELL_GEOMETRIES and third == 0
        ]
        if not candidate_records:
            continue
        for nested_entry in nested.entries:
            try:
                _header, raw = lz4.decompress_wrapper(nested_entry.data)
                g1t = atlas_codec.parse_g1t(raw)
            except Exception:
                continue
            for texture in g1t.textures:
                if texture.format_code != 0x5B:
                    continue
                yield (
                    outer_entry.index,
                    nested.resource_id,
                    nested_entry.index,
                    texture,
                    records,
                    candidate_records,
                )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", action="append", type=Path, required=True)
    parser.add_argument("--template-strip", type=Path, required=True)
    parser.add_argument("--state", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--keep", type=int, default=80)
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    strip = Image.open(args.template_strip.resolve(strict=True)).convert("RGBA")
    if strip.width % 6 != 0:
        raise ValueError(f"template strip does not have six states: {strip.size}")
    state_width = strip.width // 6
    state_index = args.state - 1
    if not 0 <= state_index < 6:
        raise ValueError(f"template state is outside 1..6: {args.state}")
    template = strip.crop(
        (state_index * state_width, 0, (state_index + 1) * state_width, strip.height)
    )
    if template.size != (200, 184):
        template = template.resize((200, 184), Image.Resampling.LANCZOS)
    reference = features(template)

    heap: list[tuple[float, int, dict[str, Any], Image.Image]] = []
    serial = 0
    route_count = 0
    record_count = 0
    for archive_arg in args.archive:
        archive = archive_arg.resolve(strict=True)
        for (
            outer,
            resource_id,
            nested_slot,
            texture,
            records,
            candidate_records,
        ) in iter_routes(archive):
            route_count += 1
            decoded = atlas_codec.decode_texture(texture)
            if decoded is None:
                continue
            atlas = Image.frombytes(
                "RGBA", (texture.width, texture.height), decoded
            )
            for record_index in candidate_records:
                record = records[record_index]
                for mode in ("tight", "base"):
                    cell, rect = normalized_cell(atlas, record, mode)
                    value = score(reference, cell)
                    row = {
                        "archive": str(archive),
                        "outer": outer,
                        "resource_id": resource_id,
                        "nested_slot": nested_slot,
                        "texture_index": texture.index,
                        "texture_dimensions": [texture.width, texture.height],
                        "layout_record_count": len(records),
                        "record": record_index,
                        "record_geometry": list(record),
                        "crop_mode": mode,
                        "rect": list(rect),
                        "score": value,
                    }
                    item = (-value, serial, row, cell)
                    serial += 1
                    if len(heap) < args.keep:
                        heapq.heappush(heap, item)
                    elif item > heap[0]:
                        heapq.heapreplace(heap, item)
                    record_count += 1

    ranked = sorted(
        [(-negative, serial_number, row, cell) for negative, serial_number, row, cell in heap],
        key=lambda item: (item[0], item[1]),
    )
    rows = []
    contact = Image.new(
        "RGB",
        (200 * 5, (184 + 36) * ((len(ranked) + 4) // 5)),
        (24, 24, 24),
    )
    draw = ImageDraw.Draw(contact)
    for rank, (value, _serial, row, cell) in enumerate(ranked):
        row["rank"] = rank + 1
        rows.append(row)
        column = rank % 5
        contact_row = rank // 5
        x = column * 200
        y = contact_row * (184 + 36)
        draw.text(
            (x + 3, y + 3),
            f"{rank + 1} r{row['resource_id']} o{row['outer']} rec{row['record']} {row['crop_mode']}",
            fill=(255, 255, 255),
        )
        draw.text(
            (x + 3, y + 17),
            f"score={value:.6f}",
            fill=(255, 255, 255),
        )
        green = Image.new("RGBA", cell.size, CONTACT_BACKGROUND)
        green.alpha_composite(cell)
        contact.paste(green.convert("RGB"), (x, y + 36))

    contact_path = output / "top_matches.png"
    contact.save(contact_path, optimize=False)
    report_path = output / "matches.json"
    report_path.write_text(
        json.dumps(
            {
                "template": str(args.template_strip.resolve(strict=True)),
                "template_state": args.state,
                "archives": [str(path.resolve(strict=True)) for path in args.archive],
                "routes_scanned": route_count,
                "record_crop_candidates_scored": record_count,
                "matches": rows,
                "contact": str(contact_path),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "report": str(report_path),
                "routes_scanned": route_count,
                "record_crop_candidates_scored": record_count,
                "best": rows[0] if rows else None,
            }
        )
    )


if __name__ == "__main__":
    main()
