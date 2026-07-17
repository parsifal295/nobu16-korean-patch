#!/usr/bin/env python3
"""Rebuild every detailed command-wheel group from imagegen assets and native layout metadata."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from PIL import Image, ImageChops, ImageFilter


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
TITLE_WORKSTREAM = REPO / "workstreams" / "steam_jp_title_images_v1"
for candidate in (WORKSTREAM, TOOLS, TITLE_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_steam_jp_title_images_v1 as title_v1  # noqa: E402
import build_steam_jp_port_highres_images_v1 as base  # noqa: E402
from prepare_full_wheel_imagegen_outputs import connected_components  # noqa: E402


SCHEMA = "nobu16.kr.runtime-wheel-imagegen-full.v1"
EXPECTED_LOW = {
    "size": 160095868,
    "sha256": "2F8048EC34B8B86CED54C0DC9A0879522D2717953805A4E4CC5EFF05407A4A45",
}
EXPECTED_HIGH = {
    "size": 80222000,
    "sha256": "3F83482358DFCB946C5D09ADEBEDCF4CFD2858794D79257835ECAB54423AE976",
}
DETAIL_RANGES = ((18, 251), (282, 389))


class FullWheelError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FullWheelError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def file_spec(path: Path) -> dict[str, Any]:
    return {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}


def verify_pin(path: Path, expected: Mapping[str, Any], name: str) -> dict[str, Any]:
    actual = file_spec(path)
    require(actual["size"] == expected["size"], f"{name} size differs: {actual['size']}")
    require(actual["sha256"] == expected["sha256"], f"{name} SHA256 differs: {actual['sha256']}")
    return actual


def changed_blocks(before: bytes, after: bytes, width: int, height: int) -> list[tuple[int, int]]:
    require(len(before) == len(after) == width * height, "BC3 geometry differs")
    blocks_wide = width // 4
    result: list[tuple[int, int]] = []
    for index in range(len(before) // 16):
        start = index * 16
        if before[start : start + 16] != after[start : start + 16]:
            result.append((index % blocks_wide, index // blocks_wide))
    return result


def premultiplied_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    raw = title_v1.resize_rgba_lanczos3_premultiplied(
        rgba.tobytes(), rgba.width, rgba.height, size[0], size[1]
    )
    return Image.frombytes("RGBA", size, raw)


def detail_group_records() -> list[list[int]]:
    groups: list[list[int]] = []
    for start, end in DETAIL_RANGES:
        require((end - start + 1) % 6 == 0, "detail range is not divisible by six")
        groups.extend([list(range(index, index + 6)) for index in range(start, end + 1, 6)])
    require(len(groups) == 57, f"expected 57 detail groups, got {len(groups)}")
    return groups


def parse_layout(table_padding: bytes) -> list[tuple[int, int, int, int, int]]:
    require(len(table_padding) >= 32, "layout table is too short")
    layout = table_padding[24:]
    require(len(layout) % 12 == 8, f"unexpected layout byte count: {len(layout)}")
    records: list[tuple[int, int, int, int, int]] = []
    for index in range((len(layout) - 8) // 12):
        first, second, third = struct.unpack_from("<III", layout, index * 12)
        records.append((first & 0xFFFF, first >> 16, second & 0xFFFF, second >> 16, third))
    require(len(records) == 474, f"expected 474 layout records, got {len(records)}")
    return records


def centered_main_mask(cell: Image.Image, dilation: int) -> tuple[Image.Image, dict[str, Any]]:
    alpha = np.array(cell.getchannel("A"), dtype=np.uint8)
    components = connected_components(alpha >= 8)
    require(bool(components), "native detailed sprite has no foreground component")

    def rank(component: tuple[np.ndarray, tuple[int, int, int, int]]) -> tuple[float, int]:
        coords, _ = component
        cy = float(np.mean(coords[:, 0]))
        cx = float(np.mean(coords[:, 1]))
        width, height = cell.size
        center_penalty = ((cx - width / 2) / (width / 2)) ** 2 + ((cy - height * 0.52) / (height / 2)) ** 2
        return (len(coords) / (1.0 + center_penalty), len(coords))

    coords, bbox = max(components, key=rank)
    mask = np.zeros(alpha.shape, dtype=np.uint8)
    mask[coords[:, 0], coords[:, 1]] = 255
    image = Image.fromarray(mask, mode="L")
    if dilation > 1:
        image = image.filter(ImageFilter.MaxFilter(dilation))
    return image, {
        "native_component_bbox": list(bbox),
        "native_component_pixels": int(len(coords)),
        "native_components": len(components),
    }


def add_mask_blocks(
    allowed: set[tuple[int, int]], mask: Image.Image, x0: int, y0: int
) -> None:
    array = np.array(mask, dtype=np.uint8)
    ys, xs = np.nonzero(array)
    if len(xs) == 0:
        return
    block_ids = np.unique(((ys + y0) // 4).astype(np.int64) * 4096 + ((xs + x0) // 4))
    for block_id in block_ids.tolist():
        allowed.add((int(block_id % 4096), int(block_id // 4096)))


def compose_texture(
    texture: atlas_codec.Texture,
    prepared: Path,
    mapping: dict[str, Any],
    table_padding: bytes,
    *,
    scale: int,
) -> tuple[bytes, Image.Image, dict[str, Any]]:
    dimensions = (4096, 4096) if scale == 2 else (2048, 2048)
    core_size = (192, 176) if scale == 2 else (96, 88)
    cell_size = (200, 190) if scale == 2 else (100, 95)
    padding = (4, 12) if scale == 2 else (2, 6)
    dilation = 7 if scale == 2 else 3
    require(
        (texture.width, texture.height, texture.format_code) == (*dimensions, 0x5B),
        f"wheel texture contract differs: {(texture.width, texture.height, texture.format_code)}",
    )
    decoded = atlas_codec.decode_texture(texture)
    require(decoded is not None, "wheel texture cannot decode")
    atlas = Image.frombytes("RGBA", dimensions, decoded)
    records = parse_layout(table_padding)
    group_records = detail_group_records()

    by_group: dict[int, dict[str, Any]] = {}
    for item in mapping["groups"]:
        for group in item["targets"]:
            require(group not in by_group, f"detail group {group} mapped more than once")
            by_group[int(group)] = item
    require(set(by_group) == set(range(57)), f"detail mapping coverage differs: {sorted(set(range(57)) - set(by_group))}")

    strips: dict[str, Image.Image] = {}
    for item in mapping["groups"]:
        name = item["name"]
        path = prepared / f"{name}_physical_alpha.png"
        require(path.is_file(), f"missing prepared imagegen strip: {path}")
        full = Image.open(path).convert("RGBA")
        require(full.size == (1200, 190), f"prepared strip geometry differs: {name} {full.size}")
        strips[name] = full if scale == 2 else premultiplied_resize(full, (600, 95))

    operations: list[dict[str, Any]] = []
    allowed: set[tuple[int, int]] = set()
    groups_report: list[dict[str, Any]] = []
    for group in range(57):
        item = by_group[group]
        name = item["name"]
        positions: list[dict[str, Any]] = []
        for state, record_index in enumerate(group_records[group]):
            x, y, width, height, third = records[record_index]
            require((width, height, third) == (*core_size, 0), f"record {record_index} contract differs")
            rect = (x - padding[0], y - padding[1], x - padding[0] + cell_size[0], y - padding[1] + cell_size[1])
            require(
                0 <= rect[0] < rect[2] <= dimensions[0] and 0 <= rect[1] < rect[3] <= dimensions[1],
                f"record {record_index} escapes atlas: {rect}",
            )
            native = atlas.crop(rect)
            native_mask, mask_stats = centered_main_mask(native, dilation)
            generated = strips[name].crop(
                (state * cell_size[0], 0, (state + 1) * cell_size[0], cell_size[1])
            )
            clipped = generated.copy()
            clipped.putalpha(ImageChops.multiply(generated.getchannel("A"), native_mask))
            require(clipped.getbbox() is not None, f"clipped imagegen state is empty: {name} {state}")
            operations.append({"rect": rect, "mask": native_mask, "cell": clipped})
            add_mask_blocks(allowed, native_mask, rect[0], rect[1])
            positions.append({
                "state": state,
                "record": record_index,
                "atlas_xy": [x, y],
                "rect": list(rect),
                **mask_stats,
            })
        groups_report.append({
            "group": group,
            "name": name,
            "ko": item["ko"],
            "source_group": item["source_group"],
            "positions": positions,
        })

    # Clear every native detail component first. This prevents one packed sprite from
    # erasing another newly composed sprite when their padded cells overlap.
    for operation in operations:
        atlas.paste((0, 0, 0, 0), operation["rect"], operation["mask"])
    for operation in operations:
        atlas.alpha_composite(operation["cell"], (operation["rect"][0], operation["rect"][1]))

    requested = atlas.tobytes()
    payload, encoded = base.encode_selected_blocks(
        requested, texture.width, texture.height, texture.payload, allowed
    )
    actual = changed_blocks(texture.payload, payload, texture.width, texture.height)
    require(actual, "full wheel composition changed no BC3 blocks")
    return payload, atlas, {
        "dimensions": list(dimensions),
        "scale": scale,
        "method": "imagegen_all_detail_groups_at_native_layout_record_coordinates",
        "detail_groups": 57,
        "states": len(operations),
        "unique_assets": len(strips),
        "native_mask_dilation_pixels": dilation,
        "allowed_bc3_blocks": len(allowed),
        "encoded_bc3_blocks": encoded,
        "changed_bc3_blocks": len(actual),
        "changed_block_bbox": base.changed_block_bbox(actual),
        "groups": groups_report,
        "layout_record_count": len(records),
        "layout_driven": True,
        "unselected_bc3_blocks_byte_preserved": True,
    }


def rebuild_archive(
    source: Path,
    destination: Path,
    preview: Path,
    prepared: Path,
    mapping: dict[str, Any],
    *,
    outer_index: int,
    scale: int,
) -> dict[str, Any]:
    blob = source.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, "outer LINK identity failed")
    before_outer = base.outer_hashes(outer)
    nested = base.parse_nested_link(outer.entries[outer_index].data, expected_resource_id=474)
    slot, header, raw, g1t = base.g1t_wrapper_entry(nested)
    require(len(g1t.textures) > 0, "wheel G1T has no texture")
    payload, composed, composition = compose_texture(
        g1t.textures[0], prepared, mapping, nested.table_padding, scale=scale
    )
    rebuilt_raw = base.replace_g1t_payloads(raw, g1t, {0: payload})
    require(len(rebuilt_raw) == len(raw), "wheel G1T size changed")
    for index, texture in enumerate(g1t.textures):
        if index == 0:
            continue
        start = texture.payload_offset
        require(
            rebuilt_raw[start : start + len(texture.payload)] == texture.payload,
            f"unselected wheel texture {index} changed",
        )
    wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, header)
    _, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == rebuilt_raw, "wheel wrapper roundtrip failed")
    rebuilt_nested = base.rebuild_nested_link(nested, {slot: wrapper})
    reparsed_nested = base.parse_nested_link(rebuilt_nested, expected_resource_id=474)
    require(reparsed_nested.table_padding == nested.table_padding, "native layout table changed")
    for entry in nested.entries:
        if entry.index != slot:
            require(
                reparsed_nested.entries[entry.index].data == entry.data,
                f"unrelated nested entry {entry.index} changed",
            )
    candidate_blob = lz4.rebuild_link(outer, {outer_index: rebuilt_nested})
    base.atomic_write(destination, candidate_blob, forbidden=(source,))
    candidate = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(candidate) == candidate_blob, "candidate LINK identity failed")
    after_outer = base.outer_hashes(candidate)
    changed_outers = [
        index
        for index in range(len(candidate.entries))
        if before_outer[str(index)] != after_outer[str(index)]
    ]
    require(changed_outers == [outer_index], f"changed outer scope differs: {changed_outers}")
    for index in range(len(candidate.entries)):
        if index != outer_index:
            require(
                candidate.entries[index].data == outer.entries[index].data,
                f"unrelated outer entry {index} changed",
            )
    preview.parent.mkdir(parents=True, exist_ok=True)
    composed.save(preview, optimize=False)
    del raw, rebuilt_raw, composed
    gc.collect()
    return {
        "candidate": file_spec(destination),
        "preview": file_spec(preview),
        "changed_outer_entries": changed_outers,
        "resource_id": 474,
        "nested_g1t_slot": slot,
        "selected_textures": [0],
        "composition": composition,
        "native_layout_table_byte_preserved": True,
        "unrelated_outer_entries_byte_preserved": True,
        "unrelated_nested_entries_byte_preserved": True,
        "unselected_g1t_bytes_preserved": True,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    low = args.low.resolve(strict=True)
    high = args.high.resolve(strict=True)
    prepared = args.prepared.resolve(strict=True)
    mapping_path = args.mapping.resolve(strict=True)
    output = base.fresh_output(args.output.resolve())
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    require(mapping.get("schema") == "nobu16.kr.wheel-detail-groups.v1", "mapping schema differs")
    require(len(mapping.get("groups", [])) == 46, "mapping must contain 46 unique assets")
    prepared_manifest = json.loads((prepared / "manifest.json").read_text(encoding="utf-8"))
    require(prepared_manifest.get("schema") == "nobu16.kr.wheel-imagegen-prepared.v2", "prepared schema differs")
    require(len(prepared_manifest.get("targets", {})) == 46, "prepared target count differs")
    inputs = {
        "low": verify_pin(low, EXPECTED_LOW, "low clean combined base"),
        "high": verify_pin(high, EXPECTED_HIGH, "high clean combined base"),
        "prepared_manifest": file_spec(prepared / "manifest.json"),
        "mapping": file_spec(mapping_path),
    }
    print("stage=low_full_runtime_wheel", flush=True)
    low_result = rebuild_archive(
        low,
        output / "candidate" / "RES_JP" / "res_lang.bin",
        output / "preview" / "wheel_low.png",
        prepared,
        mapping,
        outer_index=8,
        scale=1,
    )
    print("stage=high_full_runtime_wheel", flush=True)
    high_result = rebuild_archive(
        high,
        output / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port1.bin",
        output / "preview" / "wheel_high.png",
        prepared,
        mapping,
        outer_index=3,
        scale=2,
    )
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": inputs,
        "mapping_coverage": {"unique_assets": 46, "detail_groups": 57, "states": 342},
        "low": low_result,
        "high": high_result,
    }
    report_path = output / "build_report.json"
    base.write_json(report_path, report, forbidden=(low, high))
    return {"report": str(report_path), "low": low_result["candidate"], "high": high_result["candidate"]}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--low", type=Path, required=True)
    result.add_argument("--high", type=Path, required=True)
    result.add_argument("--prepared", type=Path, required=True)
    result.add_argument("--mapping", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
