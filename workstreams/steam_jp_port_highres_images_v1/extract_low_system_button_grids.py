#!/usr/bin/env python3
"""Map all low-resolution system buttons and extract the 7-state battle reference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve()
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))

from list_alpha_components import components  # noqa: E402


TARGETS = (
    ("approve", "승인", (0, 1, 2, 3, 4, 5)),
    ("stop", "중지", (6, 7, 9, 10, 11, 12)),
    ("close", "닫기", (8, 13, 14, 15, 16, 17)),
    ("deny", "부인", (18, 19, 20, 21, 22, 23)),
    ("release_all", "전부개방", (24, 26, 27, 34, 35, 36)),
    ("confirm", "결정", (28, 29, 30, 31, 32, 33)),
    ("reject", "거절", (25, 37, 38, 39, 40, 41)),
    ("back", "뒤로", (42, 43, 44, 54, 55, 56)),
    ("no", "아니오", (46, 47, 48, 49, 50, 51)),
    ("hime", "공주", (45, 52, 53, 57, 58, 59)),
    ("command", "지휘", (60, 61, 62, 63, 64, 65)),
    ("renegotiate", "재교섭", (67, 68, 69, 75, 76, 77)),
    ("accept", "수락", (66, 70, 71, 72, 73, 74)),
    ("dispose", "처단", (78, 79, 80, 81, 82, 83)),
    ("skip", "건너뛰기", (84, 85, 86, 96, 97, 98)),
    ("start", "시작", (88, 89, 90, 91, 92, 93)),
    ("recruit", "등용", (87, 94, 95, 99, 100, 101)),
    ("warrior", "무장", (102, 103, 104, 105, 106, 107)),
    ("yes", "예", (109, 110, 111, 117, 118, 119)),
    ("next", "다음", (108, 112, 113, 114, 115, 116)),
)


def background_class(sprite: Image.Image, references: list[np.ndarray]) -> int:
    rgba = np.asarray(sprite.convert("RGBA"), dtype=np.float32)
    sample = np.concatenate((rgba[8:19, 32:160, :3], rgba[60:71, 32:160, :3]), axis=0).reshape(-1)
    return int(np.argmin([np.linalg.norm(reference - sample) for reference in references]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    atlas_path = args.atlas.resolve(strict=True)
    atlas = Image.open(atlas_path).convert("RGBA")
    detected = components(np.asarray(atlas.getchannel("A"), dtype=np.uint8), 8)
    standard = [
        item for item in detected
        if 120 <= item["width"] <= 210 and 40 <= item["height"] <= 100 and item["y0"] < 700
    ]
    standard.sort(key=lambda item: (round(item["y0"] / 88), item["x0"]))
    if len(standard) != 120:
        raise ValueError(f"expected 120 standard components, found {len(standard)}")
    wide = [
        item for item in detected
        if 240 <= item["width"] <= 260 and 60 <= item["height"] <= 90 and item["y0"] < 100
    ]
    wide.sort(key=lambda item: item["x0"])
    if len(wide) != 7:
        raise ValueError(f"expected 7 battle components, found {len(wide)}")

    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    reference_vectors = []
    for item in standard[:6]:
        box = (item["x0"], item["y0"], item["x1"], item["y1"])
        rgba = np.asarray(atlas.crop(box), dtype=np.float32)
        reference_vectors.append(np.concatenate((rgba[8:19, 32:160, :3], rgba[60:71, 32:160, :3]), axis=0).reshape(-1))

    targets: dict[str, object] = {}
    used: set[int] = set()
    for name, ko, indices in TARGETS:
        records = []
        buckets: dict[int, list[tuple[int, dict[str, int]]]] = {0: [], 1: [], 2: [], 3: []}
        for index in indices:
            used.add(index)
            item = standard[index]
            box = (item["x0"], item["y0"], item["x1"], item["y1"])
            classification = background_class(atlas.crop(box), reference_vectors)
            buckets[classification].append((index, item))
        expected = {0: 1, 1: 2, 2: 1, 3: 2}
        counts = {key: len(value) for key, value in buckets.items()}
        if counts != expected:
            raise ValueError(f"unexpected visual-state counts for {name}: {counts}")
        ordered = {
            0: buckets[0][0],
            1: buckets[1][0],
            2: buckets[2][0],
            3: buckets[3][0],
            4: buckets[1][1],
            5: buckets[3][1],
        }
        for state in range(6):
            component_index, item = ordered[state]
            records.append({
                "state": state,
                "component_index": component_index,
                "artwork_box": [item["x0"], item["y0"], item["x1"], item["y1"]],
            })
        targets[name] = {"ko": ko, "states": records}
    if used != set(range(120)):
        raise ValueError(f"standard mapping mismatch: missing={sorted(set(range(120)) - used)}")

    battle_cell = (264, 88)
    battle_grid = Image.new("RGBA", (battle_cell[0] * 4, battle_cell[1] * 2), (0, 255, 32, 255))
    battle_records = []
    for state, item in enumerate(wide):
        box = (item["x0"], item["y0"], item["x1"], item["y1"])
        sprite = atlas.crop(box)
        x = (state % 4) * battle_cell[0] + (battle_cell[0] - sprite.width) // 2
        y = (state // 4) * battle_cell[1] + (battle_cell[1] - sprite.height) // 2
        battle_grid.alpha_composite(sprite, (x, y))
        battle_records.append({"state": state, "artwork_box": list(box), "artwork_size": list(sprite.size)})
    battle_path = output / "battle_start_개전_7state_reference.png"
    battle_grid.save(battle_path, optimize=False)

    contact = Image.new("RGB", (battle_grid.width, battle_grid.height + 28), (18, 18, 18))
    draw = ImageDraw.Draw(contact)
    draw.text((8, 6), "battle_start / 개전 / original Japanese 7 states", fill=(245, 245, 245))
    contact.paste(battle_grid.convert("RGB"), (0, 28))
    contact.save(output / "battle_start_reference_contact.png", optimize=False)

    manifest = {
        "schema": "nobu16.kr.system-buttons-low-original-map.v1",
        "atlas": str(atlas_path),
        "standard_cell": [192, 88],
        "targets": targets,
        "battle_start": {
            "ko": "개전",
            "cell": list(battle_cell),
            "states": battle_records,
            "reference": battle_path.name,
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"standard_targets": len(targets), "standard_states": 120, "battle_states": 7}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
