#!/usr/bin/env python3
"""Extract the twelve six-state PK detail-wheel groups from resource 81."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
for candidate in (WORKSTREAM, TOOLS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_steam_jp_port_highres_images_v1 as base  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--outer", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    archive_path = args.archive.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    archive = lz4.parse_link(archive_path.read_bytes())
    nested = base.parse_nested_link(archive.entries[args.outer].data, expected_resource_id=81)
    _, _, _, g1t = base.g1t_wrapper_entry(nested)
    texture = g1t.textures[0]
    if texture.format_code != 0x5B or (texture.width, texture.height) not in {(2048, 2048), (1024, 1024)}:
        raise ValueError(f"unexpected PK wheel texture: {(texture.width, texture.height, texture.format_code)}")
    scale = 2 if texture.width == 2048 else 1
    decoded = atlas_codec.decode_texture(texture)
    if decoded is None:
        raise ValueError("PK wheel texture decode failed")
    atlas = Image.frombytes("RGBA", (texture.width, texture.height), decoded)

    layout = nested.table_padding[24:]
    count = (len(layout) - 8) // 12
    records = []
    for index in range(count):
        first, second, third = struct.unpack_from("<III", layout, index * 12)
        records.append((first & 0xFFFF, first >> 16, second & 0xFFFF, second >> 16, third))
    group_indices = [list(range(0, 6))] + [list(range(index, index + 6)) for index in range(12, 78, 6)]
    if len(group_indices) != 12:
        raise ValueError("PK detail group count differs")

    groups = []
    strips = []

    main_cell = (204, 188) if scale == 2 else (104, 96)
    main_strip = Image.new("RGBA", (main_cell[0] * 6, main_cell[1]), (0, 0, 0, 0))
    main_positions = []
    for state, index in enumerate(range(6, 12)):
        x, y, width, height, third = records[index]
        expected = (196, 180, 0) if scale == 2 else (96, 88, 0)
        if (width, height, third) != expected:
            raise ValueError(f"record {index} is not the PK main state: {(width, height, third)}")
        rect = (x - 4, y - 4, x - 4 + main_cell[0], y - 4 + main_cell[1])
        main_strip.alpha_composite(atlas.crop(rect), (state * main_cell[0], 0))
        main_positions.append({"state": state + 1, "record": index, "rect": list(rect)})
    main_alpha_path = output / "pk_main_00_alpha.png"
    main_green_path = output / "pk_main_00_green.png"
    main_strip.save(main_alpha_path, optimize=False)
    main_green = Image.new("RGBA", main_strip.size, (0, 255, 0, 255))
    main_green.alpha_composite(main_strip)
    main_green.convert("RGB").save(main_green_path, optimize=False)
    for group, indices in enumerate(group_indices):
        detail_cell = (200, 184) if scale == 2 else (104, 96)
        strip = Image.new("RGBA", (detail_cell[0] * 6, detail_cell[1]), (0, 0, 0, 0))
        positions = []
        for state, index in enumerate(indices):
            x, y, width, height, third = records[index]
            expected = (192, 176, 0) if scale == 2 else (96, 88, 0)
            if (width, height, third) != expected:
                raise ValueError(f"record {index} is not a PK detail state: {(width, height, third)}")
            rect = (x - 4, y - 4, x - 4 + detail_cell[0], y - 4 + detail_cell[1])
            strip.alpha_composite(atlas.crop(rect), (state * detail_cell[0], 0))
            positions.append({"state": state + 1, "record": index, "rect": list(rect)})
        alpha_path = output / f"pk_detail_{group:02d}_alpha.png"
        green_path = output / f"pk_detail_{group:02d}_green.png"
        strip.save(alpha_path, optimize=False)
        green = Image.new("RGBA", strip.size, (0, 255, 0, 255))
        green.alpha_composite(strip)
        green.convert("RGB").save(green_path, optimize=False)
        strips.append(green.convert("RGB"))
        groups.append({"group": group, "indices": indices, "positions": positions, "alpha": str(alpha_path), "green": str(green_path)})

    contact_width = strips[0].width
    row_height = strips[0].height + 28
    contact = Image.new("RGB", (contact_width, row_height * len(strips)), (28, 28, 28))
    draw = ImageDraw.Draw(contact)
    for row, strip in enumerate(strips):
        y = row * row_height
        draw.text((6, y + 5), f"PK DETAIL {row:02d}", fill=(255, 255, 255))
        contact.paste(strip, (0, y + 28))
    contact_path = output / "pk_detail_contact.png"
    contact.save(contact_path, optimize=False)
    atlas_path = output / "pk_wheel_atlas.png"
    atlas.save(atlas_path, optimize=False)
    manifest = output / "manifest.json"
    manifest.write_text(json.dumps({
        "schema": "nobu16.kr.pk-wheel-groups.v1",
        "archive": {"path": str(archive_path), "sha256": sha256(archive_path)},
        "scale": scale,
        "groups": groups,
        "main_group": {
            "group": 0,
            "indices": list(range(6, 12)),
            "positions": main_positions,
            "alpha": str(main_alpha_path),
            "green": str(main_green_path),
        },
        "contact": str(contact_path),
        "atlas": str(atlas_path),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "groups": len(groups)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
