#!/usr/bin/env python3
"""Normalize all generated six-state command-wheel strips to clean 1200x190 RGBA rows."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


TARGET_SIZE = (1200, 190)
CELL_SIZE = (200, 190)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def active_vertical_band(image: Image.Image) -> tuple[int, int]:
    array = np.array(image.convert("RGB"), dtype=np.int16)
    score = array[:, :, 1] - np.maximum(array[:, :, 0], array[:, :, 2])
    # Imagegen preserves the requested chroma row but pads it with large white margins.
    # Locate the continuous row where green occupies most of the width.
    counts = np.sum((score > 72) & (array[:, :, 1] > 105), axis=1)
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
        raise ValueError("no generated button row found")
    top, bottom = max(runs, key=lambda run: (run[1] - run[0], int(np.sum(counts[run[0] : run[1]]))))
    return top, bottom


def chroma_alpha(image: Image.Image) -> Image.Image:
    array = np.array(image.convert("RGBA"), dtype=np.uint8)
    rgb = array[:, :, :3].astype(np.float32)
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    score = green - np.maximum(red, blue)
    alpha = np.clip((72.0 - score) / 52.0, 0.0, 1.0)
    alpha = np.where(green < 70.0, 1.0, alpha)
    alpha = np.where((green > 115.0) & (score > 86.0), 0.0, alpha)
    visible = alpha > 0.0
    rgb[:, :, 1] = np.where(visible, np.minimum(green, np.maximum(red, blue) + 18.0), green)
    array[:, :, :3] = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
    array[:, :, 3] = np.clip(alpha * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(array, mode="RGBA")


def connected_components(mask: np.ndarray) -> list[tuple[np.ndarray, tuple[int, int, int, int]]]:
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    components: list[tuple[np.ndarray, tuple[int, int, int, int]]] = []
    for y0, x0 in zip(*np.nonzero(mask & ~seen)):
        if seen[y0, x0]:
            continue
        queue: deque[tuple[int, int]] = deque([(int(y0), int(x0))])
        seen[y0, x0] = True
        pixels: list[tuple[int, int]] = []
        min_x = max_x = int(x0)
        min_y = max_y = int(y0)
        while queue:
            y, x = queue.popleft()
            pixels.append((y, x))
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    if not seen[ny, nx] and mask[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
        coords = np.asarray(pixels, dtype=np.int16)
        components.append((coords, (min_x, min_y, max_x + 1, max_y + 1)))
    return components


def remove_thin_horizontal_spurs(mask: np.ndarray) -> np.ndarray:
    """Delete long 1-3px source-atlas rule fragments without touching the button body."""
    cleaned = mask.copy()
    height, width = mask.shape
    for y in range(height):
        row = mask[y]
        padded = np.pad(row.astype(np.int8), (1, 1))
        edges = np.diff(padded)
        starts = np.flatnonzero(edges == 1)
        ends = np.flatnonzero(edges == -1)
        for start, end in zip(starts, ends):
            if end - start < 48:
                continue
            y0 = max(0, y - 2)
            y1 = min(height, y + 3)
            support = np.sum(mask[y0:y1, start:end], axis=0)
            thin = support <= 3
            cleaned[y, start:end][thin] = False
    return cleaned


def isolate_button(cell: Image.Image) -> tuple[Image.Image, dict[str, object]]:
    array = np.array(cell.convert("RGBA"), dtype=np.uint8)
    alpha = array[:, :, 3]
    initial = alpha >= 20
    detection = remove_thin_horizontal_spurs(initial)
    components = connected_components(detection)
    if not components:
        raise ValueError("no foreground component in generated state")

    def rank(component: tuple[np.ndarray, tuple[int, int, int, int]]) -> tuple[float, int]:
        coords, bbox = component
        cy = float(np.mean(coords[:, 0]))
        cx = float(np.mean(coords[:, 1]))
        center_penalty = ((cx - 100.0) / 100.0) ** 2 + ((cy - 100.0) / 95.0) ** 2
        return (len(coords) / (1.0 + center_penalty), len(coords))

    main_coords, main_bbox = max(components, key=rank)
    keep = np.zeros_like(initial)
    keep[main_coords[:, 0], main_coords[:, 1]] = True

    # Retain sizeable nearby antialias/shadow islands belonging to the main control.
    mx0, my0, mx1, my1 = main_bbox
    for coords, bbox in components:
        if coords is main_coords or len(coords) < 12:
            continue
        x0, y0, x1, y1 = bbox
        gap_x = max(0, max(mx0 - x1, x0 - mx1))
        gap_y = max(0, max(my0 - y1, y0 - my1))
        if gap_x <= 5 and gap_y <= 5 and len(coords) >= max(12, len(main_coords) // 500):
            keep[coords[:, 0], coords[:, 1]] = True

    # Expand one pixel to retain soft edges from the original alpha, but keep obvious rules out.
    expanded = keep.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            shifted = np.zeros_like(keep)
            sy0, sy1 = max(0, -dy), min(keep.shape[0], keep.shape[0] - dy)
            sx0, sx1 = max(0, -dx), min(keep.shape[1], keep.shape[1] - dx)
            shifted[sy0 + dy : sy1 + dy, sx0 + dx : sx1 + dx] = keep[sy0:sy1, sx0:sx1]
            expanded |= shifted
    array[:, :, 3] = np.where(expanded, alpha, 0).astype(np.uint8)
    removed = int(np.count_nonzero(initial & ~expanded))
    return Image.fromarray(array, mode="RGBA"), {
        "main_bbox": list(main_bbox),
        "main_pixels": int(len(main_coords)),
        "components": len(components),
        "removed_pixels": removed,
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
        "schema": "nobu16.kr.wheel-imagegen-prepared.v2",
        "source": str(source),
        "mapping": {"path": str(mapping_path), "sha256": sha256(mapping_path)},
        "targets": {},
    }
    sheets: list[list[tuple[str, Image.Image]]] = [[] for _ in range(4)]
    for index, group in enumerate(groups):
        name = group["name"]
        path = source / f"{name}_imagegen.png"
        image = Image.open(path).convert("RGBA")
        top, bottom = active_vertical_band(image)
        normalized = image.crop((0, top, image.width, bottom)).resize(TARGET_SIZE, Image.Resampling.LANCZOS)
        keyed = chroma_alpha(normalized)
        clean = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
        states: list[dict[str, object]] = []
        for state in range(6):
            cell = keyed.crop((state * 200, 0, (state + 1) * 200, 190))
            isolated, stats = isolate_button(cell)
            clean.alpha_composite(isolated, (state * 200, 0))
            states.append(stats)
        alpha_path = output / f"{name}_physical_alpha.png"
        green_path = output / f"{name}_physical_green.png"
        clean.save(alpha_path, optimize=False)
        green = Image.new("RGBA", TARGET_SIZE, (0, 255, 0, 255))
        green.alpha_composite(clean)
        green.convert("RGB").save(green_path, optimize=False)
        report["targets"][name] = {
            "ko": group["ko"],
            "target_groups": group["targets"],
            "source": {"path": str(path), "sha256": sha256(path), "dimensions": list(image.size)},
            "content_band": [top, bottom],
            "states": states,
            "alpha": {"path": str(alpha_path), "sha256": sha256(alpha_path)},
            "green": {"path": str(green_path), "sha256": sha256(green_path)},
        }
        sheets[index // 12].append((f"{name} / {group['ko']}", clean))

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
