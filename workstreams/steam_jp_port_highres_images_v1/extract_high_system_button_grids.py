#!/usr/bin/env python3
"""Extract the 20 six-state high-resolution system-button reference grids."""

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


CELL = (376, 168)
GREEN = (0, 255, 32, 255)
TARGETS = (
    ("approve", "承認", "승인"),
    ("stop", "中止", "중지"),
    ("close", "閉じる", "닫기"),
    ("deny", "否認", "부인"),
    ("release_all", "全解放", "전부개방"),
    ("confirm", "決定", "결정"),
    ("reject", "拒否", "거절"),
    ("back", "戻る", "뒤로"),
    ("no", "いいえ", "아니오"),
    ("hime", "姫", "공주"),
    ("command", "采配する", "지휘"),
    ("renegotiate", "再交渉", "재교섭"),
    ("accept", "承諾", "수락"),
    ("dispose", "処断", "처단"),
    ("skip", "スキップ", "건너뛰기"),
    ("start", "開始", "시작"),
    ("recruit", "登用", "등용"),
    ("warrior", "武将", "무장"),
    ("yes", "はい", "예"),
    ("next", "次へ", "다음"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    atlas_path = args.atlas.resolve(strict=True)
    atlas = Image.open(atlas_path).convert("RGBA")
    if atlas.size != (4096, 4096):
        raise ValueError(f"unexpected atlas geometry: {atlas.size}")
    detected = [
        item
        for item in components(np.asarray(atlas.getchannel("A"), dtype=np.uint8), 8)
        if 240 <= item["width"] <= 400 and 60 <= item["height"] <= 200 and item["y0"] < 2300
    ]
    if len(detected) != len(TARGETS) * 6:
        raise ValueError(f"expected 120 text-button components, found {len(detected)}")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {"atlas": str(atlas_path), "cell": list(CELL), "targets": {}}
    contacts = Image.new("RGBA", (CELL[0] * 3, CELL[1] * 2 * len(TARGETS)), (20, 20, 20, 255))
    for target_index, (name, jp, ko) in enumerate(TARGETS):
        states = detected[target_index * 6 : (target_index + 1) * 6]
        grid = Image.new("RGBA", (CELL[0] * 3, CELL[1] * 2), GREEN)
        state_records = []
        for state_index, item in enumerate(states):
            box = (item["x0"], item["y0"], item["x1"], item["y1"])
            sprite = atlas.crop(box)
            cell_x = (state_index % 3) * CELL[0] + (CELL[0] - sprite.width) // 2
            cell_y = (state_index // 3) * CELL[1] + (CELL[1] - sprite.height) // 2
            grid.alpha_composite(sprite, (cell_x, cell_y))
            state_records.append({"state": state_index, "artwork_box": list(box), "artwork_size": list(sprite.size)})
        path = output / f"{target_index:02d}_{name}_{ko}_reference.png"
        grid.save(path, optimize=False)
        contacts.alpha_composite(grid, (0, target_index * CELL[1] * 2))
        manifest["targets"][name] = {"jp": jp, "ko": ko, "states": state_records, "reference": path.name}
    contacts.save(output / "high_system_button_reference_contact.png", optimize=False)
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
