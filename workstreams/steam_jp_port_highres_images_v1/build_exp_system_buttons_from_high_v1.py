#!/usr/bin/env python3
"""Build the ordinary-resolution expansion button atlas from reviewed high-res art.

The runtime ordinary-resolution route is ``RES_JP/res_lang_exp.bin`` outer
``/3``, resource ``3860``, texture ``1``.  Its 4096x2048 atlas uses the same
20 six-state labels as the reviewed 4096x4096 high-resolution atlas, but packs
them into 192x88 logical cells.  This builder crops the final reviewed high-res
cells, premultiplied-alpha downsamples 376x168 to 188x84, and centers them in
the low-res cells.  No text or button art is regenerated.

The seven-state ``battle_start`` family has no counterpart in the high-res
atlas.  Those seven already-reviewed Korean sprites are copied from the
released low-res base atlas.  Every other target is sourced from the high-res
atlas, while unrelated outer entries, nested entries, textures, and BC3 blocks
remain byte-identical.
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from PIL import Image


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
for candidate in (WORKSTREAM, TOOLS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_steam_jp_port_highres_images_v1 as base  # noqa: E402
import build_current_direct_imagegen_wheel_system_candidates as current  # noqa: E402
from list_alpha_components import components  # noqa: E402


SCHEMA = "nobu16.kr.exp-system-buttons-from-reviewed-high.v1"
PINS = {
    "expansion_low": {
        "size": 13_226_270,
        "sha256": "09DDC867E0B6F5A8210332C12F180A24A52C0B94D0AEE5E00E622CEA25A06D74",
    },
    "reviewed_high": {
        "size": 83_878_438,
        "sha256": "F65383C72291D08B71EBA7E2EF504A8C674E7C4678445045868D98FCA5B0730D",
    },
    "released_low_fallback": {
        "size": 161_428_458,
        "sha256": "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7",
    },
    "reviewed_high_report": {
        "size": 1_459_914,
        "sha256": "F7887066AF1FF23092DB493DD40E75BAE16E33F5486FAD25EA46066DCAC4F5AF",
    },
}

TARGETS = (
    ("approve", (0, 1, 2, 3, 4, 5)),
    ("stop", (6, 7, 9, 10, 11, 12)),
    ("close", (8, 13, 14, 15, 16, 17)),
    ("deny", (18, 19, 20, 21, 22, 23)),
    ("release_all", (24, 26, 27, 34, 35, 36)),
    ("confirm", (28, 29, 30, 31, 32, 33)),
    ("reject", (25, 37, 38, 39, 40, 41)),
    ("back", (42, 43, 44, 54, 55, 56)),
    ("no", (46, 47, 48, 49, 50, 51)),
    ("hime", (45, 52, 53, 57, 58, 59)),
    ("command", (60, 61, 62, 63, 64, 65)),
    ("renegotiate", (67, 68, 69, 75, 76, 77)),
    ("accept", (66, 70, 71, 72, 73, 74)),
    ("dispose", (78, 79, 80, 81, 82, 83)),
    ("skip", (84, 85, 86, 96, 97, 98)),
    ("start", (88, 89, 90, 91, 92, 93)),
    ("recruit", (87, 94, 95, 99, 100, 101)),
    ("warrior", (102, 103, 104, 105, 106, 107)),
    ("yes", (109, 110, 111, 117, 118, 119)),
    ("next", (108, 112, 113, 114, 115, 116)),
)


class BuildError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def file_spec(path: Path) -> dict[str, Any]:
    return {"path": str(path), "size": path.stat().st_size, "sha256": base.sha256_file(path)}


def pin(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = file_spec(path)
    require(actual["size"] == expected["size"] and actual["sha256"] == expected["sha256"], f"{label} pin differs: {actual}")
    return actual


def archive_texture(
    path: Path,
    *,
    outer_index: int,
    resource_id: int,
    texture_index: int,
) -> tuple[lz4.LinkArchive, lz4.LinkArchive, int, lz4.WrapperHeader, bytes, atlas_codec.G1TFile, atlas_codec.Texture, Image.Image]:
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"outer LINK identity failed: {path}")
    require(outer_index < len(outer.entries), f"outer /{outer_index} is absent: {path}")
    nested = base.parse_nested_link(outer.entries[outer_index].data, expected_resource_id=resource_id)
    slot, header, raw, g1t = base.g1t_wrapper_entry(nested)
    require(texture_index < len(g1t.textures), f"texture {texture_index} is absent: {path}")
    texture = g1t.textures[texture_index]
    rgba = atlas_codec.decode_texture(texture)
    require(rgba is not None, f"texture cannot decode: {path}")
    image = Image.frombytes("RGBA", (texture.width, texture.height), rgba)
    return outer, nested, slot, header, raw, g1t, texture, image


def standard_components(atlas: Image.Image) -> list[dict[str, int]]:
    detected = components(np.asarray(atlas.getchannel("A"), dtype=np.uint8), 8)
    standard = [
        item
        for item in detected
        if 120 <= item["width"] <= 210 and 40 <= item["height"] <= 100 and item["y0"] < 700
    ]
    standard.sort(key=lambda item: (round(item["y0"] / 88), item["x0"]))
    require(len(standard) == 120, f"expected 120 ordinary-resolution components, found {len(standard)}")
    return standard


def wide_components(atlas: Image.Image, *, min_height: int = 60) -> list[dict[str, int]]:
    detected = components(np.asarray(atlas.getchannel("A"), dtype=np.uint8), 8)
    wide = [
        item
        for item in detected
        if 240 <= item["width"] <= 260 and min_height <= item["height"] <= 90 and item["y0"] < 100
    ]
    wide.sort(key=lambda item: item["x0"])
    require(len(wide) == 7, f"expected seven battle-start components, found {len(wide)}")
    return wide


def background_class(sprite: Image.Image, references: list[np.ndarray]) -> int:
    rgba = np.asarray(sprite.convert("RGBA"), dtype=np.float32)
    sample = np.concatenate((rgba[8:19, 32:160, :3], rgba[60:71, 32:160, :3]), axis=0).reshape(-1)
    return int(np.argmin([np.linalg.norm(reference - sample) for reference in references]))


def map_low_states(atlas: Image.Image) -> dict[str, list[list[int]]]:
    standard = standard_components(atlas)
    references: list[np.ndarray] = []
    for item in standard[:6]:
        box = (item["x0"], item["y0"], item["x1"], item["y1"])
        rgba = np.asarray(atlas.crop(box), dtype=np.float32)
        references.append(np.concatenate((rgba[8:19, 32:160, :3], rgba[60:71, 32:160, :3]), axis=0).reshape(-1))

    result: dict[str, list[list[int]]] = {}
    used: set[int] = set()
    for name, indices in TARGETS:
        buckets: dict[int, list[tuple[int, dict[str, int]]]] = {0: [], 1: [], 2: [], 3: []}
        for index in indices:
            used.add(index)
            item = standard[index]
            box = (item["x0"], item["y0"], item["x1"], item["y1"])
            buckets[background_class(atlas.crop(box), references)].append((index, item))
        counts = {key: len(value) for key, value in buckets.items()}
        require(counts == {0: 1, 1: 2, 2: 1, 3: 2}, f"unexpected state classes for {name}: {counts}")
        ordered = {
            0: buckets[0][0],
            1: buckets[1][0],
            2: buckets[2][0],
            3: buckets[3][0],
            4: buckets[1][1],
            5: buckets[3][1],
        }
        result[name] = [
            [item["x0"], item["y0"], item["x1"], item["y1"]]
            for _index, item in (ordered[state] for state in range(6))
        ]
    require(used == set(range(120)), "ordinary-resolution component mapping is incomplete")
    return result


def isolated_high_cells(atlas: Image.Image, report: dict[str, Any]) -> dict[tuple[str, int], Image.Image]:
    route = report["routes"]["system_buttons_high"]["composition"]
    require(route["dimensions"] == [4096, 4096], "reviewed high route dimensions differ")
    require(route["operation_count"] == 120, "reviewed high route operation count differs")
    result: dict[tuple[str, int], Image.Image] = {}
    for operation in route["operations"]:
        require(operation["family"] == "system_button_high", "unexpected operation in reviewed high route")
        rect = tuple(int(value) for value in operation["rect"])
        require((rect[2] - rect[0], rect[3] - rect[1]) == (376, 168), f"reviewed high cell geometry differs: {rect}")
        bbox = tuple(int(value) for value in operation["generated_bbox"])
        require(0 <= bbox[0] < bbox[2] <= 376 and 0 <= bbox[1] < bbox[3] <= 168, f"invalid reviewed high bbox: {bbox}")
        source = atlas.crop(rect)
        isolated = Image.new("RGBA", (376, 168), (0, 0, 0, 0))
        isolated.alpha_composite(source.crop(bbox), (bbox[0], bbox[1]))
        key = (str(operation["name"]), int(operation["state"]))
        require(key not in result, f"duplicate reviewed high operation: {key}")
        result[key] = isolated
    expected = {(name, state) for name, _indices in TARGETS for state in range(6)}
    require(set(result) == expected, f"reviewed high target coverage differs: missing={sorted(expected - set(result))}")
    return result


def build_operations(
    target_atlas: Image.Image,
    high_atlas: Image.Image,
    released_low_atlas: Image.Image,
    high_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    low_states = map_low_states(target_atlas)
    high_cells = isolated_high_cells(high_atlas, high_report)
    operations: list[dict[str, Any]] = []
    standard_rows: list[dict[str, Any]] = []

    for name, _indices in TARGETS:
        for state in range(6):
            high_cell = high_cells[(name, state)]
            half = current.premultiplied_resize(high_cell, (188, 84))
            cell = current.place_in_canvas(half, (192, 88))
            target_box = low_states[name][state]
            operations.append(
                {
                    "family": "system_button_exp_from_high",
                    "name": name,
                    "state": state,
                    "rect": current.centered_rect(target_box, cell.size),
                    "cell": cell,
                }
            )
            standard_rows.append(
                {
                    "name": name,
                    "state": state,
                    "source_cell": [376, 168],
                    "downsampled_cell": [188, 84],
                    "target_cell": [192, 88],
                    "target_native_box": target_box,
                    "resampler": "premultiplied-alpha Lanczos3",
                }
            )

    # The reviewed Korean dark-state sprites have less non-transparent vertical
    # coverage than the Japanese originals, although their logical cell is the
    # same.  Accept that intentional alpha-bound difference only for the source.
    source_wide = wide_components(released_low_atlas, min_height=50)
    target_wide = wide_components(target_atlas)
    battle_rows: list[dict[str, Any]] = []
    for state, (source_item, target_item) in enumerate(zip(source_wide, target_wide)):
        source_box = [source_item["x0"], source_item["y0"], source_item["x1"], source_item["y1"]]
        target_box = [target_item["x0"], target_item["y0"], target_item["x1"], target_item["y1"]]
        sprite = released_low_atlas.crop(tuple(source_box))
        cell = current.place_in_canvas(sprite, (264, 88))
        operations.append(
            {
                "family": "system_button_exp_battle_start_reuse",
                "name": "battle_start",
                "state": state,
                "rect": current.centered_rect(target_box, cell.size),
                "cell": cell,
            }
        )
        battle_rows.append({"state": state, "source_box": source_box, "target_native_box": target_box})

    require(len(operations) == 127, f"operation count differs: {len(operations)}")
    return operations, {
        "standard": {
            "labels": 20,
            "states": len(standard_rows),
            "source": "reviewed high-resolution atlas",
            "new_art_generated": False,
            "rows": standard_rows,
        },
        "battle_start": {
            "states": len(battle_rows),
            "source": "released Korean low-resolution base atlas (no high-resolution counterpart)",
            "new_art_generated": False,
            "rows": battle_rows,
        },
    }


def rebuild_nested(
    nested: lz4.LinkArchive,
    slot: int,
    header: lz4.WrapperHeader,
    raw: bytes,
    g1t: atlas_codec.G1TFile,
    *,
    texture_index: int,
    payload: bytes,
) -> bytes:
    rebuilt_raw = base.replace_g1t_payloads(raw, g1t, {texture_index: payload})
    require(len(rebuilt_raw) == len(raw), "G1T raw size changed")
    wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, header)
    _roundtrip_header, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == rebuilt_raw, "G1T wrapper roundtrip failed")
    rebuilt = base.rebuild_nested_link(nested, {slot: wrapper})
    reparsed = base.parse_nested_link(rebuilt, expected_resource_id=3860)
    require(reparsed.table_padding == nested.table_padding, "nested layout/table padding changed")
    for entry in nested.entries:
        if entry.index != slot:
            require(
                reparsed.entries[entry.index].data == entry.data and reparsed.entries[entry.index].gap_after == entry.gap_after,
                f"unselected nested entry changed: {entry.index}",
            )
    return rebuilt


def build(args: argparse.Namespace) -> dict[str, Any]:
    expansion = args.expansion.resolve(strict=True)
    reviewed_high = args.reviewed_high.resolve(strict=True)
    released_low = args.released_low.resolve(strict=True)
    reviewed_high_report = args.reviewed_high_report.resolve(strict=True)
    output = base.fresh_output(args.output.resolve())

    inputs = {
        "expansion_low": pin(expansion, PINS["expansion_low"], "expansion low"),
        "reviewed_high": pin(reviewed_high, PINS["reviewed_high"], "reviewed high"),
        "released_low_fallback": pin(released_low, PINS["released_low_fallback"], "released low fallback"),
        "reviewed_high_report": pin(reviewed_high_report, PINS["reviewed_high_report"], "reviewed high report"),
    }
    high_report = json.loads(reviewed_high_report.read_text(encoding="utf-8"))
    report_candidate = high_report["candidates"]["base_high"]["candidate"]
    require(
        report_candidate["size"] == inputs["reviewed_high"]["size"]
        and report_candidate["sha256"] == inputs["reviewed_high"]["sha256"],
        "reviewed high report does not describe the supplied high archive",
    )

    (
        _exp_outer,
        exp_nested,
        exp_slot,
        exp_header,
        exp_raw,
        exp_g1t,
        exp_texture,
        exp_atlas,
    ) = archive_texture(expansion, outer_index=3, resource_id=3860, texture_index=1)
    (
        _high_outer,
        _high_nested,
        _high_slot,
        _high_header,
        _high_raw,
        _high_g1t,
        high_texture,
        high_atlas,
    ) = archive_texture(reviewed_high, outer_index=2, resource_id=3860, texture_index=1)
    (
        _released_outer,
        _released_nested,
        _released_slot,
        _released_header,
        _released_raw,
        _released_g1t,
        released_texture,
        released_atlas,
    ) = archive_texture(released_low, outer_index=5, resource_id=3856, texture_index=1)
    require((exp_texture.width, exp_texture.height) == (4096, 2048), "expansion target dimensions differ")
    require((high_texture.width, high_texture.height) == (4096, 4096), "reviewed high dimensions differ")
    require((released_texture.width, released_texture.height) == (4096, 2048), "released low dimensions differ")

    operations, resize_report = build_operations(exp_atlas, high_atlas, released_atlas, high_report)
    payload, preview, composition = current.compose_operations(
        exp_texture,
        operations,
        method="reviewed_high_atlas_376x168_to_188x84_in_192x88_premultiplied_lanczos3",
    )
    rebuilt_nested = rebuild_nested(
        exp_nested,
        exp_slot,
        exp_header,
        exp_raw,
        exp_g1t,
        texture_index=1,
        payload=payload,
    )
    candidate_path = output / "candidate" / "RES_JP" / "res_lang_exp.bin"
    archive_report = current.rebuild_archive(expansion, candidate_path, {3: rebuilt_nested}, [3])
    requested_preview_path = output / "preview" / "system_buttons_exp_from_high_requested.png"
    requested_preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview.save(requested_preview_path, optimize=False)

    (
        _candidate_outer,
        _candidate_nested,
        _candidate_slot,
        _candidate_header,
        _candidate_raw,
        _candidate_g1t,
        candidate_texture,
        candidate_atlas,
    ) = archive_texture(candidate_path, outer_index=3, resource_id=3860, texture_index=1)
    require((candidate_texture.width, candidate_texture.height) == (4096, 2048), "candidate route dimensions differ")
    require(len(standard_components(candidate_atlas)) == 120, "candidate standard component coverage differs")
    require(len(wide_components(candidate_atlas, min_height=50)) == 7, "candidate battle-start component coverage differs")
    decoded_preview_path = output / "preview" / "system_buttons_exp_from_high_decoded.png"
    candidate_atlas.save(decoded_preview_path, optimize=False)

    report = {
        "schema": SCHEMA,
        "result": "PASS",
        "inputs": inputs,
        "route": {
            "archive": "RES_JP/res_lang_exp.bin",
            "outer_entry": 3,
            "resource_id": 3860,
            "texture_index": 1,
            "dimensions": [4096, 2048],
        },
        "resize": resize_report,
        "composition": composition,
        "candidate": archive_report,
        "previews": {
            "requested_rgba": file_spec(requested_preview_path),
            "candidate_bc3_decoded": file_spec(decoded_preview_path),
        },
        "candidate_decode_verification": {
            "standard_components": 120,
            "battle_start_components": 7,
            "dimensions": [4096, 2048],
        },
        "preservation": {
            "unrelated_outer_entries_byte_preserved": True,
            "unrelated_nested_entries_byte_preserved": True,
            "unselected_g1t_bytes_preserved": True,
            "unselected_bc3_blocks_byte_preserved": True,
        },
        "live_files_written": False,
    }
    report_path = output / "build_report.json"
    base.write_json(report_path, report, forbidden=(expansion, reviewed_high, released_low, reviewed_high_report))
    del exp_raw, exp_atlas, high_atlas, released_atlas, preview, candidate_atlas, _candidate_raw
    gc.collect()
    return {
        "report": str(report_path),
        "candidate": report["candidate"]["candidate"],
        "preview": report["previews"]["candidate_bc3_decoded"],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--expansion", type=Path, required=True)
    result.add_argument("--reviewed-high", type=Path, required=True)
    result.add_argument("--released-low", type=Path, required=True)
    result.add_argument("--reviewed-high-report", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
