#!/usr/bin/env python3
"""Extract the five six-state main-wheel groups from records 252..281."""

from __future__ import annotations

import argparse
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


NAMES = ("assessment", "appointment", "military", "domestic", "diplomacy")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--outer", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    archive_path = args.archive.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    archive = lz4.parse_link(archive_path.read_bytes())
    nested = base.parse_nested_link(archive.entries[args.outer].data, expected_resource_id=474)
    _, _, _, g1t = base.g1t_wrapper_entry(nested)
    texture = g1t.textures[0]
    if (texture.width, texture.height, texture.format_code) == (4096, 4096, 0x5B):
        scale = 2
    elif (texture.width, texture.height, texture.format_code) == (2048, 2048, 0x5B):
        scale = 1
    else:
        raise ValueError("unexpected main-wheel texture contract")
    decoded = atlas_codec.decode_texture(texture)
    if decoded is None:
        raise ValueError("main-wheel texture decode failed")
    atlas = Image.frombytes("RGBA", (texture.width, texture.height), decoded)

    layout = nested.table_padding[24:]
    count = (len(layout) - 8) // 12
    records = []
    for index in range(count):
        first, second, third = struct.unpack_from("<III", layout, index * 12)
        records.append((first & 0xFFFF, first >> 16, second & 0xFFFF, second >> 16, third))

    core = 104 * scale
    strip_width = core * 6
    label_height = 10 * scale
    row_height = core + label_height
    sheet = Image.new("RGBA", (strip_width, row_height * len(NAMES)), (0, 255, 0, 255))
    draw = ImageDraw.Draw(sheet)
    groups = []
    for group, name in enumerate(NAMES):
        strip = Image.new("RGBA", (strip_width, core), (0, 0, 0, 0))
        positions = []
        for state in range(6):
            record_index = 252 + group * 6 + state
            x, y, width, height, third = records[record_index]
            if (width, height, third) != (core, core, 0):
                raise ValueError(f"record {record_index} differs: {(width, height, third)}")
            rect = (x, y, x + width, y + height)
            strip.alpha_composite(atlas.crop(rect), (state * core, 0))
            positions.append({"record": record_index, "state": state + 1, "rect": list(rect)})
        alpha_path = output / f"main_{group}_{name}_alpha.png"
        green_path = output / f"main_{group}_{name}_green.png"
        strip.save(alpha_path, optimize=False)
        green = Image.new("RGBA", strip.size, (0, 255, 0, 255))
        green.alpha_composite(strip)
        green.convert("RGB").save(green_path, optimize=False)
        y0 = group * row_height
        sheet.alpha_composite(green, (0, y0 + label_height))
        draw.rectangle((0, y0, 120 * scale, y0 + label_height), fill=(0, 0, 0, 255))
        draw.text((4 * scale, y0 + scale), f"{group} {name}", fill=(255, 255, 0, 255))
        groups.append({"group": group, "name": name, "positions": positions, "alpha": str(alpha_path), "green": str(green_path)})
    contact = output / "mainwheel_contact.png"
    sheet.convert("RGB").save(contact, optimize=False)
    manifest = output / "manifest.json"
    manifest.write_text(json.dumps({"archive": str(archive_path), "scale": scale, "groups": groups, "contact": str(contact)}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "groups": len(groups)}))


if __name__ == "__main__":
    main()
