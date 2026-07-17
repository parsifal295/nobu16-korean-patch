#!/usr/bin/env python3
"""Normalize direct ImageGen wheel strips without altering generated foreground pixels."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


TARGET_SIZE = (1200, 190)
CELL_SIZE = (200, 190)
CELL_CONTENT_LIMIT = (196, 186)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def active_vertical_band(image: Image.Image) -> tuple[int, int]:
    rgb = np.asarray(image.convert("RGB"), dtype=np.int16)
    score = rgb[:, :, 1] - np.maximum(rgb[:, :, 0], rgb[:, :, 2])
    counts = np.sum((score > 72) & (rgb[:, :, 1] > 105), axis=1)
    active = counts > max(24, int(image.width * 0.01))
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for y, flag in enumerate(active.tolist() + [False]):
        if flag and start is None:
            start = y
        elif not flag and start is not None:
            runs.append((start, y))
            start = None
    if not runs:
        raise ValueError("no chroma-green sprite row found")
    return max(runs, key=lambda run: (run[1] - run[0], int(np.sum(counts[run[0] : run[1]]))))


def chroma_alpha_only(image: Image.Image) -> Image.Image:
    """Derive alpha from green while leaving every generated RGB value untouched."""
    array = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    rgb = array[:, :, :3].astype(np.float32)
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    score = green - np.maximum(red, blue)
    alpha = np.clip((72.0 - score) / 52.0, 0.0, 1.0)
    alpha = np.where(green < 70.0, 1.0, alpha)
    alpha = np.where((green > 115.0) & (score > 86.0), 0.0, alpha)
    array[:, :, 3] = np.clip(alpha * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(array, mode="RGBA")


def foreground_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    ys, xs = np.nonzero(alpha >= 8)
    if not len(xs):
        raise ValueError("no generated foreground found in state cell")
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def normalize_state(cell: Image.Image) -> tuple[Image.Image, dict[str, object]]:
    keyed = chroma_alpha_only(cell)
    bbox = foreground_bbox(keyed)
    sprite = keyed.crop(bbox)
    limit_w, limit_h = CELL_CONTENT_LIMIT
    scale = min(limit_w / sprite.width, limit_h / sprite.height)
    width = max(1, int(round(sprite.width * scale)))
    height = max(1, int(round(sprite.height * scale)))
    sprite = sprite.resize((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", CELL_SIZE, (0, 0, 0, 0))
    x = (CELL_SIZE[0] - width) // 2
    y = CELL_SIZE[1] - height - 2
    canvas.alpha_composite(sprite, (x, y))
    return canvas, {
        "source_bbox": list(bbox),
        "source_size": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
        "placed_bbox": [x, y, x + width, y + height],
        "scale": scale,
    }


def contact_sheet(items: list[tuple[str, Image.Image]], path: Path) -> None:
    columns = 2
    tile_w, tile_h = 1200, 220
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * tile_w, rows * tile_h), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)
    for index, (name, image) in enumerate(items):
        col, row = index % columns, index // columns
        x, y = col * tile_w, row * tile_h
        green = Image.new("RGBA", TARGET_SIZE, (0, 255, 0, 255))
        green.alpha_composite(image)
        canvas.paste(green.convert("RGB"), (x, y + 28))
        draw.text((x + 8, y + 6), name, fill=(255, 255, 255))
    canvas.save(path, optimize=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    mapping_path = args.mapping.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    groups = mapping["groups"]
    names = [group["name"] for group in groups]
    if len(names) != 46 or len(set(names)) != 46:
        raise ValueError(f"expected 46 unique generated assets, got {len(names)}")

    report: dict[str, object] = {
        "schema": "nobu16.kr.wheel-imagegen-direct-prepared.v1",
        "source": str(source),
        "mapping": {"path": str(mapping_path), "sha256": sha256(mapping_path)},
        "foreground_policy": "crop active green band; resize whole strip; derive alpha only; preserve RGB",
        "targets": {},
    }
    sheets: list[list[tuple[str, Image.Image]]] = [[] for _ in range(4)]
    for index, group in enumerate(groups):
        name = group["name"]
        path = source / f"{name}_imagegen.png"
        image = Image.open(path).convert("RGBA")
        top, bottom = active_vertical_band(image)
        band = image.crop((0, top, image.width, bottom))
        keyed = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
        state_stats: list[dict[str, object]] = []
        for state in range(6):
            left = round(state * band.width / 6)
            right = round((state + 1) * band.width / 6)
            normalized_state, stats = normalize_state(band.crop((left, 0, right, band.height)))
            keyed.alpha_composite(normalized_state, (state * CELL_SIZE[0], 0))
            state_stats.append(stats)
        alpha_path = output / f"{name}_physical_alpha.png"
        green_path = output / f"{name}_physical_green.png"
        keyed.save(alpha_path, optimize=False)
        green = Image.new("RGBA", TARGET_SIZE, (0, 255, 0, 255))
        green.alpha_composite(keyed)
        green.convert("RGB").save(green_path, optimize=False)
        report["targets"][name] = {
            "ko": group["ko"],
            "target_groups": group["targets"],
            "source": {"path": str(path), "sha256": sha256(path), "dimensions": list(image.size)},
            "content_band": [top, bottom],
            "states": state_stats,
            "alpha": {"path": str(alpha_path), "sha256": sha256(alpha_path)},
            "green": {"path": str(green_path), "sha256": sha256(green_path)},
        }
        sheets[index // 12].append((f"{name} / {group['ko']}", keyed))

    contacts: list[dict[str, object]] = []
    for index, items in enumerate(sheets, start=1):
        if not items:
            continue
        path = output / f"contact_{index:02d}.png"
        contact_sheet(items, path)
        contacts.append({"path": str(path), "sha256": sha256(path), "items": len(items)})
    report["contacts"] = contacts
    manifest = output / "manifest.json"
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "targets": len(names), "contacts": len(contacts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
