#!/usr/bin/env python3
"""Classify the low-resolution text-button components by visual state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


SCRIPT = Path(__file__).resolve()
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))

from list_alpha_components import components  # noqa: E402


def feature(sprite: Image.Image) -> np.ndarray:
    rgba = np.asarray(sprite.convert("RGBA"), dtype=np.float32)
    if rgba.shape[:2] != (79, 180):
        raise ValueError(f"unexpected standard button geometry: {rgba.shape[:2]}")
    # The top and bottom interior strips are untouched by every label and icon,
    # so they expose the exact six-state background templates.
    sample = np.concatenate((rgba[8:19, 32:160, :3], rgba[60:71, 32:160, :3]), axis=0)
    return sample.reshape(-1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas", type=Path, required=True)
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

    features = []
    for item in detected:
        box = (item["x0"], item["y0"], item["x1"], item["y1"])
        features.append(feature(atlas.crop(box)))
    references = np.stack(features[:6])
    rows = []
    counts = [0] * 6
    for index, vector in enumerate(features):
        distances = np.linalg.norm(references - vector, axis=1)
        state = int(np.argmin(distances))
        counts[state] += 1
        rows.append({"index": index, "state": state, "distances": [round(float(value), 3) for value in distances]})
    print(json.dumps({"counts": counts, "rows": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
