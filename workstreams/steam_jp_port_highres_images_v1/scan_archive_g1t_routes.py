#!/usr/bin/env python3
"""List nested G1T routes in one or more NOBU16 LINK archives."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
for candidate in (REPO / "tools", SCRIPT.parent):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_steam_jp_port_highres_images_v1 as base  # noqa: E402


def scan(path: Path) -> dict[str, object]:
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    routes: list[dict[str, object]] = []
    for outer_entry in outer.entries:
        try:
            nested = base.parse_nested_link(outer_entry.data)
        except Exception:
            continue
        for nested_entry in nested.entries:
            try:
                _header, raw = lz4.decompress_wrapper(nested_entry.data)
                g1t = atlas_codec.parse_g1t(raw)
            except Exception:
                continue
            routes.append(
                {
                    "outer": outer_entry.index,
                    "resource_id": nested.resource_id,
                    "nested": nested_entry.index,
                    "textures": [
                        {
                            "index": texture.index,
                            "format": f"0x{texture.format_code:02X}",
                            "width": texture.width,
                            "height": texture.height,
                            "mips": texture.mip_count,
                            "extra": texture.extra_version,
                            "payload_size": len(texture.payload),
                        }
                        for texture in g1t.textures
                    ],
                }
            )
    return {"archive": str(path.resolve()), "outer_entries": len(outer.entries), "routes": routes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archives", type=Path, nargs="+")
    parser.add_argument("--dimensions", help="optional WIDTHxHEIGHT texture filter")
    args = parser.parse_args()
    reports = [scan(path.resolve(strict=True)) for path in args.archives]
    if args.dimensions:
        width_text, height_text = args.dimensions.lower().split("x", 1)
        dimensions = (int(width_text), int(height_text))
        for report in reports:
            report["routes"] = [
                route
                for route in report["routes"]
                if any((texture["width"], texture["height"]) == dimensions for texture in route["textures"])
            ]
    print(json.dumps(reports, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
