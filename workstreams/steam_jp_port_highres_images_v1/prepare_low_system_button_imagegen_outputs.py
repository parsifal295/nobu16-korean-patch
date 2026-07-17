#!/usr/bin/env python3
"""Prepare complete low-resolution system-button assets from direct ImageGen outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve()
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))

from prepare_direct_wheel_imagegen_outputs import active_vertical_band, chroma_alpha_only, foreground_bbox  # noqa: E402
from list_alpha_components import components  # noqa: E402


STANDARD_CELL = (192, 88)
STANDARD_CONTENT = (180, 79)
BATTLE_CELL = (264, 88)
BATTLE_CONTENT = (252, 74)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def normalize(sprite_source: Image.Image, cell: tuple[int, int], content: tuple[int, int], chroma: bool = False) -> tuple[Image.Image, dict[str, object]]:
    sprite_source = chroma_alpha_only(sprite_source) if chroma else sprite_source.convert("RGBA")
    detected = components(np.asarray(sprite_source.getchannel("A"), dtype=np.uint8), 8)
    if not detected:
        raise ValueError("no generated component found")
    main = max(detected, key=lambda item: item["area"])
    bbox = (main["x0"], main["y0"], main["x1"], main["y1"])
    sprite = sprite_source.crop(bbox)
    scale = min(content[0] / sprite.width, content[1] / sprite.height)
    width = max(1, int(round(sprite.width * scale)))
    height = max(1, int(round(sprite.height * scale)))
    sprite = sprite.resize((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", cell, (0, 0, 0, 0))
    x = (cell[0] - width) // 2
    y = (cell[1] - height) // 2
    canvas.alpha_composite(sprite, (x, y))
    return canvas, {
        "source_bbox": list(bbox),
        "source_size": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
        "scale": scale,
        "placed_bbox": [x, y, x + width, y + height],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--high-prepared-manifest", type=Path, required=True)
    parser.add_argument("--low-reference-manifest", type=Path, required=True)
    parser.add_argument("--battle-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    high_manifest_path = args.high_prepared_manifest.resolve(strict=True)
    low_manifest_path = args.low_reference_manifest.resolve(strict=True)
    battle_source_path = args.battle_source.resolve(strict=True)
    high = json.loads(high_manifest_path.read_text(encoding="utf-8"))
    low = json.loads(low_manifest_path.read_text(encoding="utf-8"))
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    report: dict[str, object] = {
        "schema": "nobu16.kr.system-buttons-low-imagegen-direct-prepared.v1",
        "policy": "all 20 standard labels derived from direct high-resolution ImageGen six-state grids; battle-start uses its own direct seven-state ImageGen edit; complete-sprite uniform fit only",
        "high_prepared_manifest": {"path": str(high_manifest_path), "sha256": sha256(high_manifest_path)},
        "low_reference_manifest": {"path": str(low_manifest_path), "sha256": sha256(low_manifest_path)},
        "targets": {},
    }
    contact_rows: list[tuple[str, Image.Image]] = []
    for target_index, (name, mapping) in enumerate(low["targets"].items()):
        if name not in high["targets"]:
            raise ValueError(f"missing high-resolution ImageGen target: {name}")
        strip = Image.new("RGBA", (STANDARD_CELL[0] * 6, STANDARD_CELL[1]), (0, 0, 0, 0))
        states = []
        high_states = high["targets"][name]["states"]
        for state in range(6):
            source_path = Path(high_states[state]["alpha"]["path"]).resolve(strict=True)
            normalized, stats = normalize(Image.open(source_path), STANDARD_CELL, STANDARD_CONTENT)
            state_path = output / f"{target_index:02d}_{name}_state{state}_alpha.png"
            normalized.save(state_path, optimize=False)
            strip.alpha_composite(normalized, (state * STANDARD_CELL[0], 0))
            states.append({
                "state": state,
                "artwork_box": mapping["states"][state]["artwork_box"],
                "component_index": mapping["states"][state]["component_index"],
                "normalization": stats,
                "alpha": {"path": str(state_path), "sha256": sha256(state_path)},
            })
        strip_path = output / f"{target_index:02d}_{name}_strip_alpha.png"
        strip.save(strip_path, optimize=False)
        report["targets"][name] = {"ko": mapping["ko"], "states": states, "strip": {"path": str(strip_path), "sha256": sha256(strip_path)}}
        contact_rows.append((f"{target_index:02d} {name} / {mapping['ko']}", strip))

    battle_source = Image.open(battle_source_path).convert("RGBA")
    top, bottom = active_vertical_band(battle_source)
    battle_band = battle_source.crop((0, top, battle_source.width, bottom))
    battle_strip = Image.new("RGBA", (BATTLE_CELL[0] * 7, BATTLE_CELL[1]), (0, 0, 0, 0))
    battle_states = []
    for state in range(7):
        column, row = state % 4, state // 4
        left = round(column * battle_band.width / 4)
        right = round((column + 1) * battle_band.width / 4)
        upper = round(row * battle_band.height / 2)
        lower = round((row + 1) * battle_band.height / 2)
        normalized, stats = normalize(battle_band.crop((left, upper, right, lower)), BATTLE_CELL, BATTLE_CONTENT, chroma=True)
        state_path = output / f"battle_start_state{state}_alpha.png"
        normalized.save(state_path, optimize=False)
        battle_strip.alpha_composite(normalized, (state * BATTLE_CELL[0], 0))
        battle_states.append({
            "state": state,
            "artwork_box": low["battle_start"]["states"][state]["artwork_box"],
            "normalization": stats,
            "alpha": {"path": str(state_path), "sha256": sha256(state_path)},
        })
    battle_strip_path = output / "battle_start_strip_alpha.png"
    battle_strip.save(battle_strip_path, optimize=False)
    report["battle_start"] = {
        "ko": "개전",
        "source": {"path": str(battle_source_path), "sha256": sha256(battle_source_path), "dimensions": list(battle_source.size), "active_vertical_band": [top, bottom]},
        "states": battle_states,
        "strip": {"path": str(battle_strip_path), "sha256": sha256(battle_strip_path)},
    }

    tile_h = STANDARD_CELL[1] + 28
    contact = Image.new("RGB", (STANDARD_CELL[0] * 6, tile_h * 20 + BATTLE_CELL[1] + 28), (18, 18, 18))
    draw = ImageDraw.Draw(contact)
    for row, (label, strip) in enumerate(contact_rows):
        y = row * tile_h
        draw.text((8, y + 6), label, fill=(245, 245, 245))
        green = Image.new("RGBA", strip.size, (0, 255, 32, 255))
        green.alpha_composite(strip)
        contact.paste(green.convert("RGB"), (0, y + 28))
    y = tile_h * 20
    draw.text((8, y + 6), "battle_start / 개전 / 7 states", fill=(245, 245, 245))
    battle_green = Image.new("RGBA", battle_strip.size, (0, 255, 32, 255))
    battle_green.alpha_composite(battle_strip)
    contact.paste(battle_green.convert("RGB"), (0, y + 28))
    contact_path = output / "low_system_buttons_imagegen_contact.png"
    contact.save(contact_path, optimize=False)
    report["contact"] = {"path": str(contact_path), "sha256": sha256(contact_path), "standard_states": 120, "battle_states": 7}

    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "standard_states": 120, "battle_states": 7}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
