#!/usr/bin/env python3
"""Extract the current Steam-JP system-button cells for visual review.

This is a read-only diagnostic helper.  It decodes ``RES_JP/res_lang.bin``
outer ``/5``, nested slot ``0``, texture ``1`` using the established archive
codec and writes only PNG/JSON evidence below the requested output directory.
"""

from __future__ import annotations

import argparse
from collections import deque
import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
LEGACY = REPO / "workstreams" / "steam_jp_system_buttons_v1" / "build_steam_jp_system_buttons_v1.py"


CELLS = (
    ("close", "닫기", (0, 88, 192, 176)),
    ("stop", "중지", (648, 88, 840, 176)),
    ("confirm", "결정", (576, 176, 768, 264)),
    ("reject", "거절", (0, 176, 192, 264)),
    ("back", "뒤로", (3264, 176, 3456, 264)),
    ("no", "아니오", (192, 264, 384, 352)),
    ("skip", "건너뛰기", (3648, 352, 3840, 440)),
    ("yes", "예", (384, 512, 576, 600)),
    ("release_all", "전부개방", (192, 176, 384, 264)),
    ("hime", "희", (1536, 264, 1728, 352)),
    ("command", "지휘", (2880, 264, 3072, 352)),
    ("renegotiate", "재교섭", (2112, 352, 2304, 440)),
    ("accept", "수락", (768, 352, 960, 440)),
    ("dispose", "처단", (2688, 352, 2880, 440)),
    ("recruit", "등용", (0, 440, 192, 528)),
    ("warrior", "무장", (2880, 440, 3072, 528)),
    ("next", "다음", (768, 512, 960, 600)),
    ("approve", "승인", (2688, 0, 2880, 88)),
    ("deny", "부인", (2880, 88, 3072, 176)),
)


def component_cell(atlas: Image.Image, nominal: tuple[int, int, int, int]) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Return the isolated alpha component nearest a nominal 192x88 cell.

    Some catalog records describe the engine's logical cell rather than the
    packed artwork bounds (notably ``back`` and ``next``).  Isolating the
    connected button component prevents neighbouring fragments from becoming
    ImageGen references and prevents a logical-cell crop from clipping art.
    """

    cx = (nominal[0] + nominal[2]) // 2
    cy = (nominal[1] + nominal[3]) // 2
    x0, y0 = max(0, cx - 224), max(0, cy - 112)
    x1, y1 = min(atlas.width, cx + 224), min(atlas.height, cy + 112)
    alpha = atlas.getchannel("A").crop((x0, y0, x1, y1))
    width, height = alpha.size
    values = alpha.load()
    sx, sy = cx - x0, cy - y0
    if values[sx, sy] <= 8:
        candidates = []
        for y in range(height):
            for x in range(width):
                if values[x, y] > 8:
                    candidates.append(((x - sx) ** 2 + (y - sy) ** 2, x, y))
        if not candidates:
            raise RuntimeError(f"no alpha component near {nominal}")
        _, sx, sy = min(candidates)

    queue = deque([(sx, sy)])
    seen = {(sx, sy)}
    min_x = max_x = sx
    min_y = max_y = sy
    while queue:
        x, y = queue.popleft()
        min_x, max_x = min(min_x, x), max(max_x, x)
        min_y, max_y = min(min_y, y), max(max_y, y)
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and values[nx, ny] > 8:
                seen.add((nx, ny))
                queue.append((nx, ny))

    actual = (x0 + min_x, y0 + min_y, x0 + max_x + 1, y0 + max_y + 1)
    crop = atlas.crop(actual)
    canvas = Image.new("RGBA", (192, 88), (0, 0, 0, 0))
    paste_x = (192 - crop.width) // 2
    paste_y = (88 - crop.height) // 2
    if paste_x < 0 or paste_y < 0:
        raise RuntimeError(f"component exceeds canonical cell: {nominal} -> {actual}")
    canvas.alpha_composite(crop, (paste_x, paste_y))
    return canvas, actual


def load_legacy():
    spec = importlib.util.spec_from_file_location("system_button_extract_legacy", LEGACY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {LEGACY}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    archive = args.archive.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    legacy = load_legacy()
    decoded = legacy.decode_outer_texture(archive.read_bytes(), label="current Steam JP")
    if (decoded.texture.width, decoded.texture.height) != (4096, 2048):
        raise RuntimeError("unexpected system-button atlas dimensions")
    atlas = Image.frombytes("RGBA", (4096, 2048), decoded.rgba)
    atlas.save(output / "system_buttons_atlas.png")

    scale = 2
    label_h = 24
    gap = 8
    columns = 3
    cell_w, cell_h = 192 * scale, 88 * scale
    rows = (len(CELLS) + columns - 1) // columns
    contact = Image.new("RGBA", (gap + columns * (cell_w + gap), gap + rows * (label_h + cell_h + gap)), (18, 18, 18, 255))
    draw = ImageDraw.Draw(contact)
    manifest = []
    for index, (name, label, box) in enumerate(CELLS):
        crop, actual_box = component_cell(atlas, box)
        crop_path = output / f"{index:02d}_{name}_{label}.png"
        crop.save(crop_path)
        col, row = index % columns, index // columns
        x = gap + col * (cell_w + gap)
        y = gap + row * (label_h + cell_h + gap)
        draw.text((x, y + 4), f"{index:02d} {name} / {label}", fill=(230, 230, 230, 255))
        contact.alpha_composite(crop.resize((cell_w, cell_h), Image.Resampling.NEAREST), (x, y + label_h))
        manifest.append({"index": index, "id": name, "label_ko": label, "nominal_box": list(box), "artwork_box": list(actual_box), "file": crop_path.name})
    contact.save(output / "system_button_cells_contact.png")
    (output / "manifest.json").write_text(json.dumps({"archive": str(archive), "cells": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
