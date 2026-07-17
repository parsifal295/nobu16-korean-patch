#!/usr/bin/env python3
"""Prepare 20 direct-ImageGen six-state high-resolution system-button grids."""

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

from prepare_direct_wheel_imagegen_outputs import chroma_alpha_only, foreground_bbox  # noqa: E402
from list_alpha_components import components  # noqa: E402


CELL = (376, 168)
CONTENT = (360, 158)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def normalize(cell: Image.Image) -> tuple[Image.Image, dict[str, object]]:
    keyed = chroma_alpha_only(cell)
    detected = components(np.asarray(keyed.getchannel("A"), dtype=np.uint8), 8)
    if not detected:
        raise ValueError("no generated component found")
    main = max(detected, key=lambda item: item["area"])
    bbox = (main["x0"], main["y0"], main["x1"], main["y1"])
    sprite = keyed.crop(bbox)
    scale = min(CONTENT[0] / sprite.width, CONTENT[1] / sprite.height)
    width = max(1, int(round(sprite.width * scale)))
    height = max(1, int(round(sprite.height * scale)))
    sprite = sprite.resize((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", CELL, (0, 0, 0, 0))
    x = (CELL[0] - width) // 2
    y = (CELL[1] - height) // 2
    canvas.alpha_composite(sprite, (x, y))
    return canvas, {"source_bbox": list(bbox), "source_size": [bbox[2] - bbox[0], bbox[3] - bbox[1]], "scale": scale, "placed_bbox": [x, y, x + width, y + height]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--reference-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    reference_manifest_path = args.reference_manifest.resolve(strict=True)
    references = json.loads(reference_manifest_path.read_text(encoding="utf-8"))
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    report: dict[str, object] = {
        "schema": "nobu16.kr.system-buttons-high-imagegen-direct-prepared.v1",
        "source": str(source),
        "reference_manifest": {"path": str(reference_manifest_path), "sha256": sha256(reference_manifest_path)},
        "policy": "direct ImageGen six-state grids; alpha-only chroma removal; complete-sprite uniform fit; no glyph rendering or native-mask clipping",
        "cell": list(CELL),
        "targets": {},
    }
    contact_rows = []
    for target_index, (name, reference) in enumerate(references["targets"].items()):
        path = source / f"{target_index:02d}_{name}_imagegen.png"
        image = Image.open(path).convert("RGBA")
        states = []
        strip = Image.new("RGBA", (CELL[0] * 6, CELL[1]), (0, 0, 0, 0))
        for state in range(6):
            left = round((state % 3) * image.width / 3)
            right = round(((state % 3) + 1) * image.width / 3)
            top = round((state // 3) * image.height / 2)
            bottom = round(((state // 3) + 1) * image.height / 2)
            normalized, stats = normalize(image.crop((left, top, right, bottom)))
            state_path = output / f"{target_index:02d}_{name}_state{state}_alpha.png"
            normalized.save(state_path, optimize=False)
            strip.alpha_composite(normalized, (state * CELL[0], 0))
            states.append({"state": state, "artwork_box": reference["states"][state]["artwork_box"], "source_cell": [left, top, right, bottom], "normalization": stats, "alpha": {"path": str(state_path), "sha256": sha256(state_path)}})
        strip_path = output / f"{target_index:02d}_{name}_strip_alpha.png"
        strip.save(strip_path, optimize=False)
        report["targets"][name] = {"jp": reference["jp"], "ko": reference["ko"], "source": {"path": str(path), "sha256": sha256(path), "dimensions": list(image.size)}, "states": states, "strip": {"path": str(strip_path), "sha256": sha256(strip_path)}}
        contact_rows.append((f"{target_index:02d} {name} / {reference['ko']}", strip))

    tile_h = CELL[1] + 28
    contact = Image.new("RGB", (CELL[0] * 6, tile_h * len(contact_rows)), (18, 18, 18))
    draw = ImageDraw.Draw(contact)
    for row, (label, strip) in enumerate(contact_rows):
        y = row * tile_h
        draw.text((8, y + 6), label, fill=(245, 245, 245))
        green = Image.new("RGBA", strip.size, (0, 255, 32, 255))
        green.alpha_composite(strip)
        contact.paste(green.convert("RGB"), (0, y + 28))
    contact_path = output / "high_system_buttons_imagegen_contact.png"
    contact.save(contact_path, optimize=False)
    report["contact"] = {"path": str(contact_path), "sha256": sha256(contact_path), "targets": len(contact_rows), "states": len(contact_rows) * 6}
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "targets": len(contact_rows), "states": len(contact_rows) * 6}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
