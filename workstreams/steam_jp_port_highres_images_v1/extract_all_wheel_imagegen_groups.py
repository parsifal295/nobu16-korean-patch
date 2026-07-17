#!/usr/bin/env python3
"""Prepare every six-state command-wheel group for imagegen editing.

The PC and Switch atlases use the same logical command order but different
grid pitches and row widths.  This utility walks that shared linear order,
emits native 224 px PC target strips, and emits enlarged Korean Switch strips
only as visual references.  It never writes a game archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


PC_CELL = 224
PC_ORIGIN = (110, 0)
PC_FIRST_COLUMN = 2
PC_COLUMNS = 15
PC_BODY_ORIGIN = (110, 448)
PC_BODY_COLUMNS = 18
PC_BODY_START = 2
PC_BODY_ROW_PITCH = 112

SWITCH_CELL = 80
SWITCH_ORIGIN = (34, -3)
SWITCH_FIRST_COLUMN = 2
SWITCH_COLUMNS = 23

GROUP_STATES = 6
GROUP_COUNT = 45


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_row(path: Path, image: Image.Image | None = None) -> dict[str, object]:
    opened = image if image is not None else Image.open(path)
    try:
        return {
            "path": str(path),
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "dimensions": [opened.width, opened.height],
        }
    finally:
        if image is None:
            opened.close()


def padded_crop(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    x0, y0, x1, y1 = box
    result = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    source_box = (max(0, x0), max(0, y0), min(image.width, x1), min(image.height, y1))
    if source_box[0] < source_box[2] and source_box[1] < source_box[3]:
        crop = image.crop(source_box)
        result.alpha_composite(crop, (source_box[0] - x0, source_box[1] - y0))
    return result


def sequence_cell(index: int, *, origin: tuple[int, int], first_column: int, columns: int, cell: int) -> tuple[int, int, int, int]:
    row, offset = divmod(index, columns)
    column = first_column + offset
    x0 = origin[0] + column * cell
    y0 = origin[1] + row * cell
    return x0, y0, x0 + cell, y0 + cell


def pc_group_box(group: int, state: int) -> tuple[int, int, int, int]:
    if group < 5:
        index = group * GROUP_STATES + state
        return sequence_cell(index, origin=PC_ORIGIN, first_column=PC_FIRST_COLUMN, columns=PC_COLUMNS, cell=PC_CELL)
    body_index = PC_BODY_START + (group - 5) * GROUP_STATES + state
    row, column = divmod(body_index, PC_BODY_COLUMNS)
    x0 = PC_BODY_ORIGIN[0] + column * PC_CELL
    # The detailed PC buttons are free-packed with a half-cell vertical
    # pitch.  Their transparent upper/lower lobes interleave; treating this
    # as a 224 px row pitch skips every other logical command and mixes
    # unrelated labels in the generated strips.
    y0 = PC_BODY_ORIGIN[1] + row * PC_BODY_ROW_PITCH
    return x0, y0, x0 + PC_CELL, y0 + PC_CELL


def strip(image: Image.Image, boxes: list[tuple[int, int, int, int]], *, output_cell: int) -> Image.Image:
    result = Image.new("RGBA", (output_cell * len(boxes), output_cell), (0, 0, 0, 0))
    for state, box in enumerate(boxes):
        cell = padded_crop(image, box)
        if cell.size != (output_cell, output_cell):
            cell = cell.resize((output_cell, output_cell), Image.Resampling.LANCZOS)
        result.alpha_composite(cell, (state * output_cell, 0))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pc", type=Path, required=True, help="decoded 4096x4096 PC PORT1 wheel PNG")
    parser.add_argument("--switch", type=Path, required=True, help="decoded 2048x1024 Korean Switch reference PNG")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    output.mkdir(parents=True)

    pc_path = args.pc.resolve(strict=True)
    switch_path = args.switch.resolve(strict=True)
    pc = Image.open(pc_path).convert("RGBA")
    switch = Image.open(switch_path).convert("RGBA")
    if pc.size != (4096, 4096):
        raise ValueError(f"PC atlas dimensions differ: {pc.size}")
    if switch.size != (2048, 1024):
        raise ValueError(f"Switch atlas dimensions differ: {switch.size}")

    rows: list[dict[str, object]] = []
    pc_strips: list[Image.Image] = []
    for group in range(GROUP_COUNT):
        indices = list(range(group * GROUP_STATES, (group + 1) * GROUP_STATES))
        pc_boxes = [pc_group_box(group, state) for state in range(GROUP_STATES)]
        switch_boxes = [
            sequence_cell(index, origin=SWITCH_ORIGIN, first_column=SWITCH_FIRST_COLUMN, columns=SWITCH_COLUMNS, cell=SWITCH_CELL)
            for index in indices
        ]
        pc_strip = strip(pc, pc_boxes, output_cell=PC_CELL)
        switch_strip = strip(switch, switch_boxes, output_cell=PC_CELL)
        pc_output = output / f"group_{group:02d}_pc_native.png"
        pc_green_output = output / f"group_{group:02d}_pc_green.png"
        switch_output = output / f"group_{group:02d}_ko_reference.png"
        pc_strip.save(pc_output, format="PNG", optimize=False)
        pc_green = Image.new("RGBA", pc_strip.size, (0, 255, 0, 255))
        pc_green.alpha_composite(pc_strip)
        pc_green.convert("RGB").save(pc_green_output, format="PNG", optimize=False)
        switch_strip.save(switch_output, format="PNG", optimize=False)
        pc_strips.append(pc_strip.copy())
        rows.append({
            "group": group,
            "sequence_indices": indices,
            "pc_boxes": [list(box) for box in pc_boxes],
            "switch_boxes": [list(box) for box in switch_boxes],
            "pc": file_row(pc_output, pc_strip),
            "pc_green": file_row(pc_green_output),
            "korean_reference": file_row(switch_output, switch_strip),
        })

    contacts: list[str] = []
    for start in range(5, GROUP_COUNT, 5):
        selected = pc_strips[start:min(start + 5, GROUP_COUNT)]
        contact = Image.new("RGBA", (PC_CELL * GROUP_STATES, PC_CELL * len(selected)), (0, 0, 0, 0))
        for row, image in enumerate(selected):
            contact.alpha_composite(image, (0, row * PC_CELL))
        contact_path = output / f"contact_groups_{start:02d}_{start + len(selected) - 1:02d}.png"
        contact.save(contact_path, format="PNG", optimize=False)
        contacts.append(str(contact_path))

    pairs: list[dict[str, str]] = []
    for start in range(5, GROUP_COUNT, 2):
        selected = pc_strips[start:min(start + 2, GROUP_COUNT)]
        pair = Image.new("RGBA", (PC_CELL * GROUP_STATES, PC_CELL * len(selected)), (0, 0, 0, 0))
        for row, image in enumerate(selected):
            pair.alpha_composite(image, (0, row * PC_CELL))
        pair_path = output / f"pair_groups_{start:02d}_{start + len(selected) - 1:02d}.png"
        pair.save(pair_path, format="PNG", optimize=False)
        green = Image.new("RGBA", pair.size, (0, 255, 0, 255))
        green.alpha_composite(pair)
        green_path = output / f"pair_groups_{start:02d}_{start + len(selected) - 1:02d}_green.png"
        green.convert("RGB").save(green_path, format="PNG", optimize=False)
        pairs.append({"alpha": str(pair_path), "green": str(green_path)})

    manifest = {
        "schema": "nobu16.kr.wheel-imagegen-groups.v1",
        "game_files_written": False,
        "pc_input": file_row(pc_path, pc),
        "switch_reference": file_row(switch_path, switch),
        "group_count": GROUP_COUNT,
        "states_per_group": GROUP_STATES,
        "groups": rows,
        "contacts": contacts,
        "pairs": pairs,
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "group_count": GROUP_COUNT}, ensure_ascii=False))


if __name__ == "__main__":
    main()
