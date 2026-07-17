#!/usr/bin/env python3
"""Create an indexed contact sheet for the low-resolution text buttons."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve()
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))

from list_alpha_components import components  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    atlas = Image.open(args.atlas.resolve(strict=True)).convert("RGBA")
    detected = [
        item
        for item in components(np.asarray(atlas.getchannel("A"), dtype=np.uint8), 8)
        if 120 <= item["width"] <= 210 and 40 <= item["height"] <= 100 and item["y0"] < 700
    ]
    detected.sort(key=lambda item: (round(item["y0"] / 88), item["x0"]))
    if len(detected) != 120:
        raise ValueError(f"expected 120 components, found {len(detected)}")

    columns = 6
    tile_w, tile_h = 384, 204
    contact = Image.new("RGB", (columns * tile_w, 20 * tile_h), (18, 18, 18))
    draw = ImageDraw.Draw(contact)
    for index, item in enumerate(detected):
        box = (item["x0"], item["y0"], item["x1"], item["y1"])
        sprite = atlas.crop(box)
        green = Image.new("RGBA", (192, 88), (0, 255, 32, 255))
        green.alpha_composite(sprite, ((192 - sprite.width) // 2, (88 - sprite.height) // 2))
        green = green.resize((384, 176), Image.Resampling.NEAREST)
        x = (index % columns) * tile_w
        y = (index // columns) * tile_h
        draw.text((x + 8, y + 5), f"{index:03d}  box={box}", fill=(245, 245, 245))
        contact.paste(green.convert("RGB"), (x, y + 28))
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    contact.save(args.output.resolve(), optimize=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
