#!/usr/bin/env python3
"""Normalize five direct ImageGen main-wheel strips into six 208x208 cells."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


CORE = 208
STATES = 6
TARGET_SIZE = (CORE * STATES, CORE)
JOBS = (
    ("assessment", "군평정"),
    ("appointment", "임명"),
    ("military", "군사"),
    ("domestic", "내정"),
    ("diplomacy", "외교"),
)


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
        raise ValueError("no chroma-green main-wheel row found")
    return max(runs, key=lambda run: (run[1] - run[0], int(np.sum(counts[run[0] : run[1]]))))


def chroma_alpha_only(image: Image.Image) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    rgb = rgba[:, :, :3].astype(np.float32)
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    score = green - np.maximum(red, blue)
    alpha = np.clip((72.0 - score) / 52.0, 0.0, 1.0)
    alpha = np.where(green < 70.0, 1.0, alpha)
    alpha = np.where((green > 115.0) & (score > 86.0), 0.0, alpha)
    rgba[:, :, 3] = np.clip(alpha * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(rgba, mode="RGBA")


def normalize_cell(cell: Image.Image) -> tuple[Image.Image, dict[str, object]]:
    keyed = chroma_alpha_only(cell)
    alpha = np.asarray(keyed.getchannel("A"), dtype=np.uint8)
    ys, xs = np.nonzero(alpha >= 8)
    if not len(xs):
        raise ValueError("empty main-wheel state")
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    sprite = keyed.crop(bbox)
    scale = min(204 / sprite.width, 204 / sprite.height)
    size = (max(1, int(round(sprite.width * scale))), max(1, int(round(sprite.height * scale))))
    sprite = sprite.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (CORE, CORE), (0, 0, 0, 0))
    placement = ((CORE - sprite.width) // 2, CORE - sprite.height - 2)
    canvas.alpha_composite(sprite, placement)
    return canvas, {
        "source_bbox": list(bbox),
        "source_size": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
        "resized": list(size),
        "placement": list(placement),
        "scale": scale,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    report: dict[str, object] = {
        "schema": "nobu16.kr.mainwheel-imagegen-direct-prepared.v1",
        "foreground_policy": "split six cells; crop complete sprite; resize and center; alpha-only chroma key",
        "groups": {},
    }
    contact = Image.new("RGB", (TARGET_SIZE[0], (CORE + 24) * len(JOBS)), (28, 28, 28))
    draw = ImageDraw.Draw(contact)
    for row, (name, ko) in enumerate(JOBS):
        path = source / f"{name}_imagegen.png"
        image = Image.open(path).convert("RGBA")
        top, bottom = active_vertical_band(image)
        band = image.crop((0, top, image.width, bottom))
        strip = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
        states = []
        for state in range(STATES):
            left = round(state * band.width / STATES)
            right = round((state + 1) * band.width / STATES)
            cell, stats = normalize_cell(band.crop((left, 0, right, band.height)))
            strip.alpha_composite(cell, (state * CORE, 0))
            states.append({"state": state + 1, **stats})
        alpha_path = output / f"main_{row}_{name}_alpha.png"
        green_path = output / f"main_{row}_{name}_green.png"
        strip.save(alpha_path, optimize=False)
        green = Image.new("RGBA", TARGET_SIZE, (0, 255, 0, 255))
        green.alpha_composite(strip)
        green.convert("RGB").save(green_path, optimize=False)
        y = row * (CORE + 24)
        contact.paste(green.convert("RGB"), (0, y + 24))
        draw.text((6, y + 5), f"{row} {name}", fill=(255, 255, 255))
        report["groups"][name] = {
            "ko": ko,
            "source": {"path": str(path), "sha256": sha256(path), "dimensions": list(image.size)},
            "content_band": [top, bottom],
            "alpha": {"path": str(alpha_path), "sha256": sha256(alpha_path)},
            "green": {"path": str(green_path), "sha256": sha256(green_path)},
            "states": states,
        }
    contact_path = output / "mainwheel_contact.png"
    contact.save(contact_path, optimize=False)
    report["contact"] = {"path": str(contact_path), "sha256": sha256(contact_path)}
    manifest = output / "manifest.json"
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "groups": len(JOBS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
