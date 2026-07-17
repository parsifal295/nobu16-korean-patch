#!/usr/bin/env python3
"""Normalize twelve direct ImageGen PK detail-wheel strips to 1200x190 RGBA."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

from prepare_direct_wheel_imagegen_outputs import (
    active_vertical_band,
    chroma_alpha_only,
    foreground_bbox,
    normalize_state,
    sha256,
)


JOBS = (
    ("00_joint_battle", "공투"),
    ("01_reinforcement", "증원"),
    ("02_standby", "대기"),
    ("03_siege_battle", "공성전"),
    ("04_castle_role", "성역할"),
    ("05_edit_castle_role", "편집"),
    ("06_clear_castle_role", "해제"),
    ("07_supply_base", "보급거점"),
    ("08_clear_supply_base", "해제"),
    ("09_defense_base", "방어거점"),
    ("10_clear_defense_base", "해제"),
    ("11_edit_defense_base", "편집"),
)


def normalize_main_state(cell: Image.Image) -> tuple[Image.Image, dict[str, object]]:
    keyed = chroma_alpha_only(cell)
    bbox = foreground_bbox(keyed)
    sprite = keyed.crop(bbox)
    scale = min(200 / sprite.width, 184 / sprite.height)
    size = (max(1, int(round(sprite.width * scale))), max(1, int(round(sprite.height * scale))))
    sprite = sprite.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (204, 188), (0, 0, 0, 0))
    x = (204 - size[0]) // 2
    y = 188 - size[1] - 2
    canvas.alpha_composite(sprite, (x, y))
    return canvas, {
        "source_bbox": list(bbox),
        "source_size": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
        "resized": list(size),
        "placement": [x, y],
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
        "schema": "nobu16.kr.pk-wheel-imagegen-direct-prepared.v1",
        "foreground_policy": "split six cells; crop complete sprite; resize and center; alpha-only chroma key",
        "groups": {},
    }

    main_path = source / "pk_main_wide_area_imagegen.png"
    main_image = Image.open(main_path).convert("RGBA")
    main_top, main_bottom = active_vertical_band(main_image)
    main_band = main_image.crop((0, main_top, main_image.width, main_bottom))
    main_strip = Image.new("RGBA", (1224, 188), (0, 0, 0, 0))
    main_states = []
    for state in range(6):
        left = round(state * main_band.width / 6)
        right = round((state + 1) * main_band.width / 6)
        cell, stats = normalize_main_state(main_band.crop((left, 0, right, main_band.height)))
        main_strip.alpha_composite(cell, (state * 204, 0))
        main_states.append({"state": state + 1, **stats})
    main_alpha_path = output / "pk_main_00_alpha.png"
    main_green_path = output / "pk_main_00_green.png"
    main_strip.save(main_alpha_path, optimize=False)
    main_green = Image.new("RGBA", main_strip.size, (0, 255, 0, 255))
    main_green.alpha_composite(main_strip)
    main_green.convert("RGB").save(main_green_path, optimize=False)
    report["main_group"] = {
        "name": "wide_area",
        "ko": "광역",
        "source": {"path": str(main_path), "sha256": sha256(main_path), "dimensions": list(main_image.size)},
        "content_band": [main_top, main_bottom],
        "alpha": {"path": str(main_alpha_path), "sha256": sha256(main_alpha_path)},
        "green": {"path": str(main_green_path), "sha256": sha256(main_green_path)},
        "states": main_states,
    }
    contact = Image.new("RGB", (1200, 218 * len(JOBS)), (28, 28, 28))
    draw = ImageDraw.Draw(contact)
    for group, (name, ko) in enumerate(JOBS):
        path = source / f"{name}_imagegen.png"
        image = Image.open(path).convert("RGBA")
        top, bottom = active_vertical_band(image)
        band = image.crop((0, top, image.width, bottom))
        strip = Image.new("RGBA", (1200, 190), (0, 0, 0, 0))
        states = []
        for state in range(6):
            left = round(state * band.width / 6)
            right = round((state + 1) * band.width / 6)
            cell, stats = normalize_state(band.crop((left, 0, right, band.height)))
            strip.alpha_composite(cell, (state * 200, 0))
            states.append({"state": state + 1, **stats})
        alpha_path = output / f"pk_detail_{group:02d}_alpha.png"
        green_path = output / f"pk_detail_{group:02d}_green.png"
        strip.save(alpha_path, optimize=False)
        green = Image.new("RGBA", strip.size, (0, 255, 0, 255))
        green.alpha_composite(strip)
        green.convert("RGB").save(green_path, optimize=False)
        y = group * 218
        draw.text((6, y + 5), f"PK DETAIL {group:02d} {name}", fill=(255, 255, 255))
        contact.paste(green.convert("RGB"), (0, y + 28))
        report["groups"][f"{group:02d}"] = {
            "name": name,
            "ko": ko,
            "source": {"path": str(path), "sha256": sha256(path), "dimensions": list(image.size)},
            "content_band": [top, bottom],
            "alpha": {"path": str(alpha_path), "sha256": sha256(alpha_path)},
            "green": {"path": str(green_path), "sha256": sha256(green_path)},
            "states": states,
        }
    contact_path = output / "pk_detail_contact.png"
    contact.save(contact_path, optimize=False)
    report["contact"] = {"path": str(contact_path), "sha256": sha256(contact_path)}
    manifest = output / "manifest.json"
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "groups": len(JOBS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
