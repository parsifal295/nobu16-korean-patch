#!/usr/bin/env python3
"""Create indexed contact sheets from existing six-state wheel group strips."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--suffix", default="ko_reference")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--groups", type=int, default=45)
    parser.add_argument("--per-sheet", type=int, default=10)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 28)
    for start in range(0, args.groups, args.per_sheet):
        selected: list[tuple[int, Image.Image]] = []
        for group in range(start, min(start + args.per_sheet, args.groups)):
            path = source / f"group_{group:02d}_{args.suffix}.png"
            selected.append((group, Image.open(path).convert("RGBA")))
        width = max(image.width for _, image in selected)
        row_height = max(image.height for _, image in selected) + 40
        contact = Image.new("RGBA", (width, row_height * len(selected)), (0, 255, 0, 255))
        draw = ImageDraw.Draw(contact)
        for row, (group, image) in enumerate(selected):
            y = row * row_height
            contact.alpha_composite(image, (0, y + 40))
            draw.rectangle((0, y, 160, y + 40), fill=(0, 0, 0, 255))
            draw.text((8, y + 4), f"GROUP {group:02d}", font=font, fill=(255, 255, 0, 255))
        path = output / f"groups_{start:02d}_{start + len(selected) - 1:02d}_{args.suffix}.png"
        contact.convert("RGB").save(path, optimize=False)
        print(path)


if __name__ == "__main__":
    main()
