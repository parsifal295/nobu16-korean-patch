#!/usr/bin/env python3
"""List connected alpha-component boxes in a decoded atlas PNG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def components(alpha: np.ndarray, threshold: int) -> list[dict[str, int]]:
    parent: list[int] = []
    boxes: list[list[int]] = []
    areas: list[int] = []

    def make(x0: int, x1: int, y: int) -> int:
        index = len(parent)
        parent.append(index)
        boxes.append([x0, y, x1, y + 1])
        areas.append(x1 - x0)
        return index

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> int:
        left, right = find(left), find(right)
        if left == right:
            return left
        parent[right] = left
        boxes[left][0] = min(boxes[left][0], boxes[right][0])
        boxes[left][1] = min(boxes[left][1], boxes[right][1])
        boxes[left][2] = max(boxes[left][2], boxes[right][2])
        boxes[left][3] = max(boxes[left][3], boxes[right][3])
        areas[left] += areas[right]
        return left

    previous: list[tuple[int, int, int]] = []
    for y, row in enumerate(alpha >= threshold):
        padded = np.pad(row.astype(np.int8), (1, 1))
        changes = np.diff(padded)
        starts = np.flatnonzero(changes == 1)
        ends = np.flatnonzero(changes == -1)
        current: list[tuple[int, int, int]] = []
        prior_index = 0
        for x0, x1 in zip(starts.tolist(), ends.tolist()):
            identifier = make(x0, x1, y)
            while prior_index < len(previous) and previous[prior_index][1] < x0:
                prior_index += 1
            match = prior_index
            while match < len(previous) and previous[match][0] <= x1:
                px0, px1, pid = previous[match]
                if px1 >= x0 and px0 <= x1:
                    identifier = union(identifier, pid)
                match += 1
            root = find(identifier)
            boxes[root][0] = min(boxes[root][0], x0)
            boxes[root][2] = max(boxes[root][2], x1)
            boxes[root][3] = y + 1
            current.append((x0, x1, root))
        previous = current

    output: list[dict[str, int]] = []
    for index in range(len(parent)):
        if find(index) != index:
            continue
        x0, y0, x1, y1 = boxes[index]
        output.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "width": x1 - x0, "height": y1 - y0, "area": areas[index]})
    return sorted(output, key=lambda item: (item["y0"], item["x0"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--threshold", type=int, default=8)
    parser.add_argument("--min-width", type=int, default=0)
    parser.add_argument("--min-height", type=int, default=0)
    args = parser.parse_args()
    alpha = np.asarray(Image.open(args.image.resolve(strict=True)).convert("RGBA").getchannel("A"), dtype=np.uint8)
    rows = [item for item in components(alpha, args.threshold) if item["width"] >= args.min_width and item["height"] >= args.min_height]
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
